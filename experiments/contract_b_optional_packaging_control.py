"""Research-only packaging control for an optional Contract-B factual-context ledger.

This does not change canonical Contract B. It probes whether the current locked
artifact verifier can carry an additive companion file without reinterpreting
canonical payloads, and whether the existing SHA256SUMS mechanism can bind that
companion strongly enough to detect tampering.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EB_ROOT = Path(os.environ["EB_ROOT"]).resolve()
CAL_ROOT = Path(os.environ["CAL_ROOT"]).resolve()
RESULTS_DIR = Path(os.environ.get("RESULTS_DIR", ROOT / "experiment-results"))
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(EB_ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from evidence_bundler.experiments.contract_b_seam_probe import (  # noqa: E402
    build_handoff_variant,
    load_fixture,
)
from contract_b_optional_extension_minimality import (  # noqa: E402
    build_extension_ref,
    extract_capability_ledger,
    validate_extension_ref,
)
from validators.verify_contract_integrity import verify  # noqa: E402

FIXTURE_PATH = EB_ROOT / "examples" / "contract-b-seam" / "tri-repo-fixture.yaml"
LEGACY_CB_PATH = CAL_ROOT / "tests" / "fixtures" / "cb" / "evidence-bundle-minimal"
EXTENSION_REL = Path("extensions") / "contract-b-factual-context-research-v1.json"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_snapshot(path: Path) -> dict[str, str]:
    """Hash canonical C-B payload files, excluding the integrity index itself."""
    rels: list[Path] = [
        Path("CONTRACT_VERSION"),
        Path("bundle_manifest.yaml"),
        Path("audit_config.yaml"),
        Path("validation_set_ref.yaml"),
    ]
    rels.extend(sorted(Path("claims") / p.name for p in (path / "claims").glob("*.yaml")))
    for source in sorted(p for p in (path / "evidence").iterdir() if p.is_dir()):
        profile = source / "source_profile.yaml"
        if profile.exists():
            rels.append(profile.relative_to(path))
        passages = source / "passages"
        if passages.is_dir():
            rels.extend(sorted(p.relative_to(path) for p in passages.glob("*.yaml")))
    return {rel.as_posix(): sha256_file(path / rel) for rel in rels if (path / rel).exists()}


def add_extension(path: Path, payload: dict[str, Any], *, bind: bool) -> None:
    target = path / EXTENSION_REL
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if bind:
        sums = path / "SHA256SUMS"
        existing = sums.read_text(encoding="utf-8")
        if existing and not existing.endswith("\n"):
            existing += "\n"
        existing += f"{sha256_file(target)}  {EXTENSION_REL.as_posix()}\n"
        sums.write_text(existing, encoding="utf-8")


def report_dict(report: Any) -> dict[str, Any]:
    return {
        "passed": bool(report.passed),
        "errors": list(report.errors),
        "checked_files": list(report.checked_files),
    }


def main() -> int:
    fixture = load_fixture(FIXTURE_PATH)
    v1 = build_handoff_variant(fixture, "minimal_context")
    ledger = extract_capability_ledger(v1)
    ref = build_extension_ref(ledger)
    payload = {
        "research_status": "noncanonical",
        "binding": ref,
        "capabilities": ledger,
    }
    extension_errors = validate_extension_ref(ref, ledger)

    baseline_snapshot = canonical_snapshot(LEGACY_CB_PATH)
    baseline_report = verify(LEGACY_CB_PATH)
    contract_version = (LEGACY_CB_PATH / "CONTRACT_VERSION").read_text(encoding="utf-8").strip()

    with tempfile.TemporaryDirectory(prefix="cb-optional-extension-") as tmp_raw:
        tmp = Path(tmp_raw)

        unbound = tmp / "unbound"
        shutil.copytree(LEGACY_CB_PATH, unbound)
        add_extension(unbound, payload, bind=False)
        unbound_report = verify(unbound)
        unbound_snapshot = canonical_snapshot(unbound)

        bound = tmp / "bound"
        shutil.copytree(LEGACY_CB_PATH, bound)
        add_extension(bound, payload, bind=True)
        bound_report = verify(bound)
        bound_snapshot = canonical_snapshot(bound)
        bound_extension_hash = sha256_file(bound / EXTENSION_REL)

        tampered = tmp / "tampered"
        shutil.copytree(bound, tampered)
        target = tampered / EXTENSION_REL
        original = target.read_text(encoding="utf-8")
        target.write_text(original + "\n", encoding="utf-8")
        tampered_report = verify(tampered)

        tamper_detected_for_extension = any(
            EXTENSION_REL.as_posix() in error and "hash mismatch" in error
            for error in tampered_report.errors
        )

        result = {
            "experiment": "Contract B optional companion packaging control",
            "status": "research_only",
            "legacy_contract_version": contract_version,
            "extension_validation_errors": extension_errors,
            "baseline": report_dict(baseline_report),
            "unbound_companion": {
                **report_dict(unbound_report),
                "canonical_payload_unchanged": unbound_snapshot == baseline_snapshot,
                "observation": (
                    "Existing verifier accepts an unlisted extra companion, so mere colocated "
                    "presence is not an integrity binding."
                ),
            },
            "bound_companion": {
                **report_dict(bound_report),
                "canonical_payload_unchanged": bound_snapshot == baseline_snapshot,
                "extension_sha256": bound_extension_hash,
                "sha256sums_lists_extension": EXTENSION_REL.as_posix()
                in (bound / "SHA256SUMS").read_text(encoding="utf-8"),
                "observation": (
                    "Existing verifier accepts the additive companion when checksum-bound, "
                    "without schema reinterpretation of canonical payloads."
                ),
            },
            "tampered_bound_companion": {
                **report_dict(tampered_report),
                "tamper_detected_for_extension": tamper_detected_for_extension,
                "observation": (
                    "Changing the bound companion without updating SHA256SUMS is detected "
                    "by the existing artifact integrity protocol."
                ),
            },
            "interpretive_limits": [
                "This is a packaging compatibility control, not a production extension schema.",
                "The old verifier does not understand extension semantics; it only demonstrates additive carriage and integrity binding.",
                "A future extension-aware consumer still needs explicit discovery and fail-closed absence semantics.",
                "Keeping the legacy numeric CONTRACT_VERSION in this research copy is not a versioning recommendation.",
            ],
        }

    passes = (
        baseline_report.passed
        and not extension_errors
        and result["unbound_companion"]["passed"]
        and result["unbound_companion"]["canonical_payload_unchanged"]
        and result["bound_companion"]["passed"]
        and result["bound_companion"]["canonical_payload_unchanged"]
        and result["bound_companion"]["sha256sums_lists_extension"]
        and not result["tampered_bound_companion"]["passed"]
        and result["tampered_bound_companion"]["tamper_detected_for_extension"]
    )
    result["passes"] = passes

    out = RESULTS_DIR / "packaging-control.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if passes else 1


if __name__ == "__main__":
    raise SystemExit(main())
