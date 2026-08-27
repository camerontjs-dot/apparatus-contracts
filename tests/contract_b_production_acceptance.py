"""Cross-repository production acceptance gate for Contract B 1.2.0 promotion.

This is intentionally a production-path test: it builds a fresh Evidence Bundler
BM25 retrieval bundle, attaches the optional factual-context extension through the
production EB package, validates it with Apparatus, and consumes it through CAL's
production Contract-B intake path. The checked-in CAL 1.0.0 fixture is used
untouched for the legacy compatibility assertions.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Callable

import yaml

from validators.verify_contract_integrity import verify as apparatus_verify

from evidence_bundler.contracts import factual_context as eb_fc
from evidence_bundler.contracts.factual_context import (
    ContractBFactualContext as EBFactualContext,
    attach_factual_context,
    canonical_bytes as eb_canonical_bytes,
)
from evidence_bundler.contracts.writer import build_retrieval_bundle, validate_bundle_tree
from evidence_bundler.models.retrieval import RetrievalConfig

from claim_audit_lab.contracts.bundle_loader import BundleIntegrityError, load_bundle
from claim_audit_lab.contracts.factual_context import (
    FactualContextIntakeError,
    canonical_bytes as cal_canonical_bytes,
    load_contract_b_intake,
)

ROOT = Path(__file__).resolve().parents[1]
EB_ROOT = ROOT / "_deps" / "evidence-bundler"
CAL_ROOT = ROOT / "_deps" / "claim-audit-lab"
OUT = ROOT / "production-acceptance"
EXT_REL = Path("extensions/contract-b-factual-context-v1.json")


def _git_sha(path: Path) -> str:
    return subprocess.check_output(["git", "-C", str(path), "rev-parse", "HEAD"], text=True).strip()


def _tree_digest(path: Path) -> str:
    h = hashlib.sha256()
    for file_path in sorted(p for p in path.rglob("*") if p.is_file()):
        rel = file_path.relative_to(path).as_posix()
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(hashlib.sha256(file_path.read_bytes()).digest())
        h.update(b"\n")
    return h.hexdigest()


def _yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), path
    return data


def _bundle_ids(bundle_dir: Path) -> tuple[list[str], dict[str, str], dict[str, dict[str, Any]]]:
    claim_ids: list[str] = []
    claim_docs: dict[str, dict[str, Any]] = {}
    for path in sorted((bundle_dir / "claims").glob("*.yaml")):
        row = _yaml(path)
        claim_id = str(row["claim_id"])
        claim_ids.append(claim_id)
        claim_docs[claim_id] = row
    passage_source: dict[str, str] = {}
    for path in sorted((bundle_dir / "evidence").glob("*/passages/*.yaml")):
        row = _yaml(path)
        passage_source[str(row["passage_id"])] = str(row["source_id"])
    return claim_ids, passage_source, claim_docs


def _claim_nominees(claim_doc: dict[str, Any]) -> list[str]:
    values: list[str] = []
    for field in ("evidence_passages", "counterevidence_passages"):
        rows = claim_doc.get(field, [])
        if isinstance(rows, list):
            for row in rows:
                if isinstance(row, dict) and isinstance(row.get("passage_id"), str):
                    values.append(row["passage_id"])
    return list(dict.fromkeys(values))


def _extension_dict(
    *,
    claim_id: str,
    accepted_passage: str,
    rejected_passage: str,
    accepted_source: str,
    nomination_variant: str = "baseline",
) -> dict[str, Any]:
    return {
        "schema": "contract-b-factual-context-v1",
        "history_complete": True,
        "claims": [
            {
                "claim_id": claim_id,
                "origin": {"state": "known", "value": {"surface": "fresh-production-bundle"}},
                "atomicity": {"state": "unknown", "value": None},
            }
        ],
        "sources": [
            {
                "source_id": accepted_source,
                "context_facts": [
                    {
                        "fact_id": "fact-effective-date-001",
                        "predicate": "effective_date",
                        "value": "2026-01-15",
                        "assertion_mode": "source_declared",
                        "provenance_passage_id": accepted_passage,
                    }
                ],
            }
        ],
        "passages": [
            {
                "passage_id": accepted_passage,
                "anchors": [{"type": "character_range", "value": {"start": 0, "end": 16}}],
            },
            {
                "passage_id": rejected_passage,
                "anchors": [{"type": "character_range", "value": {"start": 0, "end": 8}}],
            },
        ],
        "history": [
            {
                "link_id": "history-accepted-001",
                "claim_id": claim_id,
                "passage_id": accepted_passage,
                "nomination": {
                    "method": "bm25",
                    "rank": 1,
                    "variant": nomination_variant,
                },
                "review": {"decision": "accepted", "reviewer": "production-acceptance-gate"},
            },
            {
                "link_id": "history-rejected-001",
                "claim_id": claim_id,
                "passage_id": rejected_passage,
                "nomination": {
                    "method": "bm25",
                    "rank": 2,
                    "variant": nomination_variant,
                },
                "review": {"decision": "rejected", "reviewer": "production-acceptance-gate"},
            },
        ],
        "history_count_checks": [
            {"claim_id": claim_id, "candidate": 2, "reviewed": 2, "admitted": 1}
        ],
        "aperture": [
            {
                "claim_id": claim_id,
                "search_scope": {"retrieval_method": "bm25", "top_k": 5},
                "outcome": {"state": "unknown", "value": None},
                "limitations": ["No proposition-specific completeness conclusion is asserted."],
            }
        ],
    }


def _write_raw_extension_and_reseal(bundle_dir: Path, raw: dict[str, Any]) -> None:
    target = bundle_dir / EXT_REL
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(raw, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
        + "\n",
        encoding="utf-8",
    )
    eb_fc._reseal(bundle_dir)  # mutation controls deliberately bypass producer schema validation


def _contains_key(value: Any, key: str) -> bool:
    if isinstance(value, dict):
        return key in value or any(_contains_key(child, key) for child in value.values())
    if isinstance(value, list):
        return any(_contains_key(child, key) for child in value)
    return False


def _expect_raises(fn: Callable[[], Any], accepted: tuple[type[BaseException], ...]) -> None:
    try:
        fn()
    except accepted:
        return
    raise AssertionError(f"expected one of {[cls.__name__ for cls in accepted]}")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []

    def gate(number: int, name: str, fn: Callable[[], None]) -> None:
        try:
            fn()
        except Exception as exc:  # noqa: BLE001 - preserve all gate failures in one receipt
            results.append({"number": number, "name": name, "result": "FAIL", "detail": repr(exc)})
            print(f"FAIL {number:02d} {name}: {exc}")
        else:
            results.append({"number": number, "name": name, "result": "PASS", "detail": ""})
            print(f"PASS {number:02d} {name}")

    with tempfile.TemporaryDirectory(prefix="contract-b-prod-") as tmp_raw:
        tmp = Path(tmp_raw)
        legacy = CAL_ROOT / "tests" / "fixtures" / "cb" / "evidence-bundle-minimal"
        legacy_before = _tree_digest(legacy)

        fresh_absent = tmp / "fresh-1.2-absent"
        build_retrieval_bundle(
            EB_ROOT / "examples" / "handoff-demo" / "scaffold-run-bm25-handoff-demo",
            fresh_absent,
            config=RetrievalConfig(retrieval_method="bm25", top_k=5, lexical_score_floor=0.0),
        )
        assert not validate_bundle_tree(fresh_absent), validate_bundle_tree(fresh_absent)
        absent_bundle_hash = _yaml(fresh_absent / "bundle_manifest.yaml")["bundle"]["bundle_hash"]

        claim_ids, passage_source, claim_docs = _bundle_ids(fresh_absent)
        assert claim_ids, "fresh production bundle contains no claims"
        claim_id = claim_ids[0]
        nominees = _claim_nominees(claim_docs[claim_id])
        all_passages = list(passage_source)
        if len(nominees) < 2:
            nominees.extend(pid for pid in all_passages if pid not in nominees)
        nominees = list(dict.fromkeys(nominees))
        assert len(nominees) >= 2, "need at least two canonical passages for accepted/rejected control"
        accepted_passage, rejected_passage = nominees[:2]
        accepted_source = passage_source[accepted_passage]

        ext_raw = _extension_dict(
            claim_id=claim_id,
            accepted_passage=accepted_passage,
            rejected_passage=rejected_passage,
            accepted_source=accepted_source,
        )
        extension = EBFactualContext.model_validate(ext_raw)

        promoted = tmp / "fresh-1.2-promoted"
        shutil.copytree(fresh_absent, promoted)
        attach_factual_context(promoted, extension)
        promoted_bundle_hash = _yaml(promoted / "bundle_manifest.yaml")["bundle"]["bundle_hash"]
        promoted_intake = load_contract_b_intake(promoted)

        def g1() -> None:
            report = apparatus_verify(legacy)
            assert report.passed, report.errors
            assert _tree_digest(legacy) == legacy_before

        gate(1, "untouched legacy Contract-B artifact still validates", g1)

        def g2() -> None:
            old = load_bundle(legacy)
            intake = load_contract_b_intake(legacy)
            assert intake.extension_state == "legacy_absent"
            assert intake.intake_ledger is None and intake.semantic_context is None
            assert intake.bundle == old

        gate(2, "legacy behavior unchanged with extension absent", g2)

        def g3() -> None:
            assert (promoted / EXT_REL).is_file()
            assert not validate_bundle_tree(promoted), validate_bundle_tree(promoted)
            assert (promoted / "CONTRACT_VERSION").read_text().strip() == "1.2.0"

        gate(3, "actual EB production retrieval producer plus attach emits valid extension-aware artifact", g3)

        def g4() -> None:
            report = apparatus_verify(promoted, against_pin="1.2.0")
            assert report.passed, report.errors

        gate(4, "Apparatus validates promoted artifact", g4)

        gate(5, "actual CAL production consumer accepts promoted artifact", lambda: (
            None if promoted_intake.extension_state == "present" else (_ for _ in ()).throw(AssertionError(promoted_intake.extension_state))
        ))

        def g6() -> None:
            intake = load_contract_b_intake(fresh_absent)
            assert intake.extension_state == "absent"
            assert intake.intake_ledger is None and intake.semantic_context is None

        gate(6, "CAL does not invent extension state when absent", g6)

        def g7() -> None:
            assert promoted_intake.semantic_context is not None
            row = next(row for row in promoted_intake.semantic_context["claims"] if row["claim_id"] == claim_id)
            assert row["atomicity"] == {"state": "unknown", "value": None}

        gate(7, "explicit unknown remains unknown", g7)

        def g8() -> None:
            sums = (promoted / "SHA256SUMS").read_text(encoding="utf-8")
            assert EXT_REL.as_posix() in sums
            assert promoted_bundle_hash != absent_bundle_hash
            assert not validate_bundle_tree(promoted)

        gate(8, "extension is included in integrity binding", g8)

        def g9() -> None:
            tampered = tmp / "tampered-extension"
            shutil.copytree(promoted, tampered)
            target = tampered / EXT_REL
            raw = bytearray(target.read_bytes())
            raw[-2] = ord(" ") if raw[-2] != ord(" ") else ord("x")
            target.write_bytes(bytes(raw))
            assert not apparatus_verify(tampered).passed
            _expect_raises(lambda: load_contract_b_intake(tampered), (BundleIntegrityError, FactualContextIntakeError))

        gate(9, "extension tampering fails closed", g9)

        def g10() -> None:
            unbound = tmp / "unbound-extension"
            shutil.copytree(fresh_absent, unbound)
            target = unbound / EXT_REL
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(eb_canonical_bytes(extension))
            assert not apparatus_verify(unbound).passed
            _expect_raises(lambda: load_contract_b_intake(unbound), (BundleIntegrityError, FactualContextIntakeError))

        gate(10, "unbound extension sidecar fails closed", g10)

        def g11() -> None:
            inconsistent = tmp / "inconsistent-counts"
            shutil.copytree(promoted, inconsistent)
            raw = json.loads((inconsistent / EXT_REL).read_text(encoding="utf-8"))
            raw["history_count_checks"][0]["candidate"] = 99
            _write_raw_extension_and_reseal(inconsistent, raw)
            assert not apparatus_verify(inconsistent).passed
            _expect_raises(lambda: load_contract_b_intake(inconsistent), (FactualContextIntakeError, BundleIntegrityError))

        gate(11, "inconsistent complete-history count check fails closed", g11)

        def g12() -> None:
            assert promoted_intake.intake_ledger is not None
            rejected = [
                row for row in promoted_intake.intake_ledger["history"]
                if row["review"]["decision"] == "rejected"
            ]
            assert any(row["passage_id"] == rejected_passage for row in rejected)
            resolved = list((promoted / "evidence").glob(f"*/passages/{rejected_passage}.yaml"))
            assert len(resolved) == 1
            assert promoted_intake.semantic_context is not None
            semantic_text = json.dumps(promoted_intake.semantic_context, sort_keys=True)
            assert rejected_passage not in semantic_text

        gate(12, "complete history preserves rejected-candidate recoverability", g12)

        def g13() -> None:
            variant = tmp / "nomination-metadata-variant"
            shutil.copytree(fresh_absent, variant)
            variant_ext = EBFactualContext.model_validate(
                _extension_dict(
                    claim_id=claim_id,
                    accepted_passage=accepted_passage,
                    rejected_passage=rejected_passage,
                    accepted_source=accepted_source,
                    nomination_variant="metadata-only-change",
                )
            )
            attach_factual_context(variant, variant_ext)
            variant_intake = load_contract_b_intake(variant)
            assert variant_intake.intake_ledger != promoted_intake.intake_ledger
            assert variant_intake.semantic_context == promoted_intake.semantic_context

        gate(13, "nomination metadata stays audit-visible but semantic-view invariant", g13)

        def g14() -> None:
            hostile = tmp / "hostile-judgment-field"
            shutil.copytree(promoted, hostile)
            raw = json.loads((hostile / EXT_REL).read_text(encoding="utf-8"))
            raw["history"][0]["nomination"]["verdict"] = "supported"
            _write_raw_extension_and_reseal(hostile, raw)
            assert not apparatus_verify(hostile).passed
            _expect_raises(lambda: load_contract_b_intake(hostile), (FactualContextIntakeError, BundleIntegrityError))

        gate(14, "hostile upstream CAL judgment fields cannot enter Contract B", g14)

        def g15() -> None:
            assert promoted_intake.semantic_context is not None
            row = next(row for row in promoted_intake.semantic_context["claims"] if row["claim_id"] == claim_id)
            admitted = next(p for p in row["admitted_passages"] if p["passage_id"] == accepted_passage)
            facts = admitted["context_facts"]
            assert any(
                fact["predicate"] == "effective_date"
                and fact["value"] == "2026-01-15"
                and fact["provenance_passage_id"] == accepted_passage
                for fact in facts
            )

        gate(15, "provenance-bound version/effective-date/context facts survive intake as facts", g15)

        def g16() -> None:
            assert promoted_intake.intake_ledger is not None
            assert promoted_intake.semantic_context is not None
            assert not _contains_key(promoted_intake.intake_ledger, "temporal_applicability")
            assert not _contains_key(promoted_intake.semantic_context, "temporal_applicability")
            assert not _contains_key(promoted_intake.semantic_context, "authority_applicability")
            assert not _contains_key(promoted_intake.semantic_context, "supplier_applicability")

        gate(16, "temporal/version facts do not become applicability judgments upstream", g16)

        def g17() -> None:
            permuted = json.loads(json.dumps(ext_raw))
            for key in ("claims", "sources", "passages", "history", "history_count_checks", "aperture"):
                permuted[key] = list(reversed(permuted[key]))
            for source in permuted["sources"]:
                source["context_facts"] = list(reversed(source["context_facts"]))
            for passage in permuted["passages"]:
                passage["anchors"] = list(reversed(passage["anchors"]))
            for aperture in permuted["aperture"]:
                aperture["limitations"] = list(reversed(aperture["limitations"]))
            permuted_ext = EBFactualContext.model_validate(permuted)
            eb_bytes = eb_canonical_bytes(extension)
            assert eb_canonical_bytes(permuted_ext) == eb_bytes
            cal_model = __import__(
                "claim_audit_lab.contracts.factual_context", fromlist=["ContractBFactualContext"]
            ).ContractBFactualContext.model_validate(ext_raw)
            assert cal_canonical_bytes(cal_model) == eb_bytes
            assert (promoted / EXT_REL).read_bytes() == eb_bytes

        gate(17, "canonical ordering and permutation behavior are deterministic cross-repo", g17)

        artifact = {
            "schema": "contract-b-production-acceptance-v1",
            "apparatus_sha": _git_sha(ROOT),
            "evidence_bundler_sha": _git_sha(EB_ROOT),
            "claim_audit_lab_sha": _git_sha(CAL_ROOT),
            "contract_b_version": "1.2.0",
            "legacy_fixture_contract_version": (legacy / "CONTRACT_VERSION").read_text().strip(),
            "legacy_fixture_tree_digest_sha256": legacy_before,
            "fresh_absent_bundle_hash": absent_bundle_hash,
            "promoted_bundle_hash": promoted_bundle_hash,
            "extension_sha256": hashlib.sha256((promoted / EXT_REL).read_bytes()).hexdigest(),
            "gates": results,
            "pass_count": sum(row["result"] == "PASS" for row in results),
            "fail_count": sum(row["result"] == "FAIL" for row in results),
        }
        (OUT / "cross-repo-gates.json").write_text(
            json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        shutil.copy2(promoted / EXT_REL, OUT / "promoted-extension.json")
        (OUT / "promoted-SHA256SUMS.txt").write_text(
            (promoted / "SHA256SUMS").read_text(encoding="utf-8"), encoding="utf-8"
        )

    failures = [row for row in results if row["result"] != "PASS"]
    print(f"\nCross-repo production gates: {len(results) - len(failures)} passed, {len(failures)} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
