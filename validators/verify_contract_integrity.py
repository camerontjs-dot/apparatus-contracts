"""Artifact-tree integrity verifier for C-A and C-B handoff artifacts."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from . import SUPPORTED_CONTRACT_VERSIONS
from ._hashing import verify_sha256sums
from ._models import (
    AuditConfig,
    BundleManifest,
    ClaimAuditUnit,
    ClaimsRegistry,
    PassageRecord,
    PassagesFile,
    ScaffoldRun,
    SourceMetadata,
)
from .contract_b_factual_context import (
    EXTENSION_PATH,
    FactualContextValidationError,
    load_extension,
)


@dataclass
class IntegrityReport:
    artifact_path: Path
    artifact_type: str
    errors: list[str] = field(default_factory=list)
    checked_files: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.errors

    def add(self, message: str) -> None:
        self.errors.append(message)


def _load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _validate(model_cls: Any, path: Path, report: IntegrityReport) -> None:
    report.checked_files.append(str(path.relative_to(report.artifact_path)))
    try:
        data = _load_yaml(path)
    except yaml.YAMLError as exc:
        report.add(f"{path.relative_to(report.artifact_path)}: YAML parse error: {exc}")
        return
    if not isinstance(data, dict):
        report.add(
            f"{path.relative_to(report.artifact_path)}: expected mapping at root, "
            f"got {type(data).__name__}"
        )
        return
    try:
        model_cls.model_validate(data)
    except ValidationError as exc:
        rel = path.relative_to(report.artifact_path)
        for err in exc.errors():
            loc = ".".join(str(p) for p in err["loc"])
            report.add(f"{rel}: {loc}: {err['msg']}")


def _detect_type(path: Path) -> str:
    if (path / "scaffold_run.yaml").exists():
        return "C-A"
    if (path / "bundle_manifest.yaml").exists():
        return "C-B"
    return "unknown"


def _contract_version(path: Path) -> str | None:
    version_path = path / "CONTRACT_VERSION"
    if not version_path.exists():
        return None
    return version_path.read_text(encoding="utf-8").strip()


def _check_contract_version(path: Path, report: IntegrityReport, against_pin: str | None) -> None:
    version = _contract_version(path)
    if version is None:
        report.add("CONTRACT_VERSION file missing")
        return
    if version not in SUPPORTED_CONTRACT_VERSIONS:
        report.add(
            f"CONTRACT_VERSION is {version!r}, expected one of "
            f"{sorted(SUPPORTED_CONTRACT_VERSIONS)!r}"
        )
    if against_pin is not None and version != against_pin:
        report.add(f"CONTRACT_VERSION is {version!r} but --against-pin requires {against_pin!r}")


def _check_sha256sums(path: Path, report: IntegrityReport) -> None:
    sums_path = path / "SHA256SUMS"
    if not sums_path.exists():
        report.add("SHA256SUMS file missing")
        return
    mismatches = verify_sha256sums(sums_path, path)
    for mismatch in mismatches:
        if mismatch.actual is None:
            report.add(f"{mismatch.relative_path}: listed in SHA256SUMS but missing on disk")
        else:
            report.add(
                f"{mismatch.relative_path}: hash mismatch "
                f"(expected {mismatch.expected}, got {mismatch.actual})"
            )


def _check_ca(path: Path, report: IntegrityReport) -> None:
    _validate(ScaffoldRun, path / "scaffold_run.yaml", report)
    _validate(ClaimsRegistry, path / "claims.yaml", report)
    corpus_dir = path / "corpus"
    if not corpus_dir.is_dir():
        report.add("corpus/ directory missing")
        return
    for source_dir in sorted(p for p in corpus_dir.iterdir() if p.is_dir()):
        metadata_path = source_dir / "metadata.yaml"
        passages_path = source_dir / "passages.yaml"
        if metadata_path.exists():
            _validate(SourceMetadata, metadata_path, report)
        else:
            report.add(f"corpus/{source_dir.name}/metadata.yaml missing")
        if passages_path.exists():
            _validate(PassagesFile, passages_path, report)
        else:
            report.add(f"corpus/{source_dir.name}/passages.yaml missing")


def _cb_identity_sets(path: Path) -> tuple[set[str], set[str], set[str]]:
    claim_ids: set[str] = set()
    source_ids: set[str] = set()
    passage_ids: set[str] = set()
    claims_dir = path / "claims"
    if claims_dir.is_dir():
        for claim_path in claims_dir.glob("*.yaml"):
            data = _load_yaml(claim_path)
            if isinstance(data, dict) and isinstance(data.get("claim_id"), str):
                claim_ids.add(data["claim_id"])
    evidence_dir = path / "evidence"
    if evidence_dir.is_dir():
        for source_dir in (item for item in evidence_dir.iterdir() if item.is_dir()):
            source_ids.add(source_dir.name)
            passages_dir = source_dir / "passages"
            if passages_dir.is_dir():
                for passage_path in passages_dir.glob("*.yaml"):
                    data = _load_yaml(passage_path)
                    if isinstance(data, dict) and isinstance(data.get("passage_id"), str):
                        passage_ids.add(data["passage_id"])
    return claim_ids, source_ids, passage_ids


def _check_factual_context_extension(path: Path, report: IntegrityReport) -> None:
    extension_path = path / EXTENSION_PATH
    if not extension_path.exists():
        return
    version = _contract_version(path)
    if version != "1.2.0":
        report.add(
            f"{EXTENSION_PATH.as_posix()}: extension requires CONTRACT_VERSION '1.2.0', got {version!r}"
        )
        return
    sums_path = path / "SHA256SUMS"
    if not sums_path.exists():
        return
    listed_paths: set[str] = set()
    for line in sums_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        parts = line.split(maxsplit=1)
        if len(parts) == 2:
            listed_paths.add(parts[1])
    if EXTENSION_PATH.as_posix() not in listed_paths:
        report.add(f"{EXTENSION_PATH.as_posix()}: present extension is not integrity-bound in SHA256SUMS")
        return
    claim_ids, source_ids, passage_ids = _cb_identity_sets(path)
    try:
        load_extension(
            extension_path,
            claim_ids=claim_ids,
            source_ids=source_ids,
            passage_ids=passage_ids,
        )
    except (FactualContextValidationError, OSError) as exc:
        report.add(f"{EXTENSION_PATH.as_posix()}: {exc}")
        return
    report.checked_files.append(EXTENSION_PATH.as_posix())


def _check_cb(path: Path, report: IntegrityReport) -> None:
    _validate(BundleManifest, path / "bundle_manifest.yaml", report)
    audit_config_path = path / "audit_config.yaml"
    if audit_config_path.exists():
        _validate(AuditConfig, audit_config_path, report)
    else:
        report.add("audit_config.yaml missing")

    claims_dir = path / "claims"
    if not claims_dir.is_dir():
        report.add("claims/ directory missing")
    else:
        for claim_yaml in sorted(claims_dir.glob("*.yaml")):
            _validate(ClaimAuditUnit, claim_yaml, report)

    evidence_dir = path / "evidence"
    if evidence_dir.is_dir():
        for source_dir in sorted(p for p in evidence_dir.iterdir() if p.is_dir()):
            passages_dir = source_dir / "passages"
            if passages_dir.is_dir():
                for passage_yaml in sorted(passages_dir.glob("*.yaml")):
                    _validate(PassageRecord, passage_yaml, report)
    else:
        report.add("evidence/ directory missing")

    _check_factual_context_extension(path, report)


def verify(path: Path, *, against_pin: str | None = None) -> IntegrityReport:
    artifact_type = _detect_type(path)
    report = IntegrityReport(artifact_path=path, artifact_type=artifact_type)
    if artifact_type == "unknown":
        report.add(
            "could not detect artifact type: neither scaffold_run.yaml (C-A) "
            "nor bundle_manifest.yaml (C-B) found at the tree root"
        )
        return report
    _check_contract_version(path, report, against_pin)
    _check_sha256sums(path, report)
    if artifact_type == "C-A":
        _check_ca(path, report)
    else:
        _check_cb(path, report)
    return report


def _print_report(report: IntegrityReport) -> None:
    print(f"{report.artifact_type} artifact: {report.artifact_path}")
    print(f"  files checked: {len(report.checked_files)}")
    if report.passed:
        print("  result: OK")
        return
    print(f"  result: FAIL ({len(report.errors)} error{'s' if len(report.errors) != 1 else ''})")
    for error in report.errors:
        print(f"    - {error}")


def run(path: Path, *, against_pin: str | None = None) -> int:
    if not path.exists():
        print(f"FAIL: artifact path does not exist: {path}")
        return 1
    if not path.is_dir():
        print(f"FAIL: artifact path is not a directory: {path}")
        return 1
    report = verify(path.resolve(), against_pin=against_pin)
    _print_report(report)
    return 0 if report.passed else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="verify-contract-integrity",
        description="Validate a C-A scaffold-run or C-B evidence-bundle artifact tree.",
    )
    parser.add_argument("artifact", type=Path, help="Path to the artifact directory")
    parser.add_argument("--against-pin", type=str, default=None)
    args = parser.parse_args(argv)
    return run(args.artifact, against_pin=args.against_pin)


if __name__ == "__main__":
    sys.exit(main())
