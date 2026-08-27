"""Contract B V0/V1/V2 conformance experiment.

Research only. This runner consumes the pinned Evidence Bundler research fixture
and helpers directly. It does not define a canonical handoff model, mutate CAL
production behavior, or assign a schema version.
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
EB_ROOT = Path(os.environ.get("EB_ROOT", ROOT / "_deps/evidence-bundler")).resolve()
CAL_ROOT = Path(os.environ.get("CAL_ROOT", ROOT / "_deps/claim-audit-lab")).resolve()
RESULTS_DIR = Path(os.environ.get("RESULTS_DIR", ROOT / "experiment-results/contract-b-v0-v1-v2")).resolve()

sys.path.insert(0, str(EB_ROOT / "src"))

from evidence_bundler.experiments.contract_b_seam_probe import (  # noqa: E402
    SeamProbeError,
    build_cal_measurement_view,
    build_handoff_variant,
    canonical_hash,
    collect_fact_ids,
    find_audit_judgment_keys,
    handoff_hash,
    load_fixture,
    mutate_downstream_assessments,
    mutate_nomination_metadata,
    validate_fixture,
)

EB_SHA = "b4ca9111f5957ef7e7955e2c5024f2280ee19eb5"
CAL_SHA = "6acc3462dad73959ccec6bccf8407215f5274cf6"
APPARATUS_SHA = "63e8506396132a44ebc0e6c2312047e99b1125eb"
DECISION_ENGINE_SHA = "55f108c196ead020b5965c7d4d737464c92bc4a0"
FIXTURE_PATH = EB_ROOT / "examples/contract-b-seam/tri-repo-fixture.yaml"


class CheckFailure(AssertionError):
    pass


def _sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _hash_obj(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return _sha256_bytes(payload.encode("utf-8"))


def _semantic_payload(view: dict[str, Any]) -> dict[str, Any]:
    """Only proposition/passage content, excluding provenance/context/policy."""
    claim = view["claim"]
    return {
        "claim_id": claim["claim_id"],
        "claim_text": claim["text"],
        "passages": [
            {
                "passage_id": p["passage_id"],
                "text": p["text"],
            }
            for p in view["admitted_passages"]
        ],
    }


def _deep_diff(a: Any, b: Any, path: str = "$") -> list[dict[str, Any]]:
    if type(a) is not type(b):
        return [{"path": path, "before": a, "after": b}]
    if isinstance(a, dict):
        diffs: list[dict[str, Any]] = []
        keys = sorted(set(a) | set(b))
        for key in keys:
            child = f"{path}.{key}"
            if key not in a:
                diffs.append({"path": child, "before": "<missing>", "after": b[key]})
            elif key not in b:
                diffs.append({"path": child, "before": a[key], "after": "<missing>"})
            else:
                diffs.extend(_deep_diff(a[key], b[key], child))
        return diffs
    if isinstance(a, list):
        if len(a) != len(b):
            return [{"path": path + ".length", "before": len(a), "after": len(b)}]
        diffs: list[dict[str, Any]] = []
        for i, (left, right) in enumerate(zip(a, b, strict=True)):
            diffs.extend(_deep_diff(left, right, f"{path}[{i}]"))
        return diffs
    if a != b:
        return [{"path": path, "before": a, "after": b}]
    return []


def _source(handoff: dict[str, Any], source_id: str) -> dict[str, Any]:
    return next(s for s in handoff["sources"] if s["source_id"] == source_id)


def _passage_ids(view: dict[str, Any]) -> set[str]:
    return {p["passage_id"] for p in view["admitted_passages"]}


def _make_result_artifact(
    *,
    contract_b_hash: str,
    semantic_measurement_hash: str,
    cal_policy_id: str,
    assessment_state: str,
) -> dict[str, Any]:
    body = {
        "artifact_kind": "cal-result-research-candidate",
        "contract_b_hash": contract_b_hash,
        "semantic_measurement_hash": semantic_measurement_hash,
        "cal_policy_id": cal_policy_id,
        "assessment_state": assessment_state,
    }
    return {**body, "result_hash": _hash_obj(body)}


def _record(
    records: list[dict[str, Any]],
    test_id: str,
    title: str,
    fn: Callable[[], dict[str, Any]],
) -> None:
    try:
        evidence = fn()
        records.append({"test_id": test_id, "title": title, "status": "PASS", "evidence": evidence})
    except Exception as exc:  # preserve counterexamples instead of aborting later tests
        records.append(
            {
                "test_id": test_id,
                "title": title,
                "status": "FAIL",
                "error_type": type(exc).__name__,
                "error": str(exc),
            }
        )


def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    fixture_bytes = FIXTURE_PATH.read_bytes()
    fixture = load_fixture(FIXTURE_PATH)

    v0 = build_handoff_variant(fixture, "current_cb")
    v1 = build_handoff_variant(fixture, "minimal_context")
    v2 = build_handoff_variant(fixture, "full_sidecar")
    v1_view = build_cal_measurement_view(v1)
    v2_view = build_cal_measurement_view(v2)

    records: list[dict[str, Any]] = []
    deviations: list[dict[str, Any]] = []

    def t1() -> dict[str, Any]:
        validate_fixture(fixture)
        tampered = copy.deepcopy(fixture)
        tampered["coverage"]["admitted_count"] += 1
        caught = None
        try:
            validate_fixture(tampered)
        except SeamProbeError as exc:
            caught = str(exc)
        if caught is None:
            raise CheckFailure("coverage-count tamper was not rejected")
        if _hash_obj(fixture) == _hash_obj(tampered):
            raise CheckFailure("tampered fixture retained the same canonical object hash")
        return {
            "fixture_file_hash": _sha256_bytes(fixture_bytes),
            "fixture_object_hash": _hash_obj(fixture),
            "v0_hash": _hash_obj(v0),
            "v1_hash": _hash_obj(v1),
            "v2_hash": _hash_obj(v2),
            "negative_control": caught,
        }

    def t2() -> dict[str, Any]:
        error = None
        try:
            build_cal_measurement_view(v0)
        except SeamProbeError as exc:
            error = str(exc)
        if error is None:
            raise CheckFailure("V0 unexpectedly produced a CAL measurement view")
        return {
            "typed_failure": error,
            "invented_default_view": False,
            "v0_fields": sorted(v0),
        }

    def t3() -> dict[str, Any]:
        v1_again = build_handoff_variant(fixture, "minimal_context")
        if canonical_hash(v1_again) != canonical_hash(v1):
            raise CheckFailure("V1 construction is not deterministic")
        required = set(fixture["required_mechanical_fact_ids"])
        present = collect_fact_ids(v1)
        missing = sorted(required - present)
        if missing:
            raise CheckFailure(f"V1 missing required factual context: {missing}")
        judgments = sorted(find_audit_judgment_keys(v1))
        if judgments:
            raise CheckFailure(f"V1 contains CAL-owned judgment keys: {judgments}")
        if v1["claim"]["text"] != fixture["claim"]["text"]:
            raise CheckFailure("claim text changed in V1")
        fixture_passages = {p["passage_id"]: p["text"] for p in fixture["passages"]}
        v1_passages = {p["passage_id"]: p["text"] for p in v1["passages"]}
        if fixture_passages != v1_passages:
            raise CheckFailure("passage content changed in V1")
        return {
            "deterministic_hash": canonical_hash(v1),
            "required_fact_count": len(required),
            "present_fact_count": len(present),
            "link_history_count": len(v1["links"]),
            "coverage_present": True,
            "cal_judgment_keys": judgments,
        }

    def t4() -> dict[str, Any]:
        left = canonical_hash(v1_view)
        right = canonical_hash(v2_view)
        if left != right:
            raise CheckFailure("V1 and V2 pre-assessment semantic views differ")
        return {
            "v1_measurement_view_hash": left,
            "v2_measurement_view_hash": right,
            "semantic_payload_hash": _hash_obj(_semantic_payload(v1_view)),
        }

    def t5() -> dict[str, Any]:
        hostile_fixture = mutate_downstream_assessments(fixture)
        hostile_v2 = build_handoff_variant(hostile_fixture, "full_sidecar")
        hostile_view = build_cal_measurement_view(hostile_v2)
        sidecar_diff = _deep_diff(v2["cal_research_sidecar"], hostile_v2["cal_research_sidecar"])
        if not sidecar_diff:
            raise CheckFailure("hostile sidecar mutation changed nothing")
        if canonical_hash(hostile_view) != canonical_hash(v1_view):
            raise CheckFailure("hostile V2 sidecar changed the blinded CAL measurement view")
        return {
            "hostile_sidecar_diff_count": len(sidecar_diff),
            "sample_mutations": sidecar_diff[:8],
            "blinded_measurement_view_hash": canonical_hash(hostile_view),
            "baseline_measurement_view_hash": canonical_hash(v1_view),
        }

    def t6() -> dict[str, Any]:
        mutated_fixture = mutate_nomination_metadata(fixture)
        mutated_v1 = build_handoff_variant(mutated_fixture, "minimal_context")
        mutated_view = build_cal_measurement_view(mutated_v1)
        if handoff_hash(mutated_fixture) == handoff_hash(fixture):
            raise CheckFailure("nomination mutation did not change the auditable handoff")
        if canonical_hash(mutated_view) != canonical_hash(v1_view):
            raise CheckFailure("nomination metadata changed CAL semantic measurement input")
        return {
            "baseline_handoff_hash": handoff_hash(fixture),
            "mutated_handoff_hash": handoff_hash(mutated_fixture),
            "measurement_view_hash": canonical_hash(v1_view),
            "mutated_measurement_view_hash": canonical_hash(mutated_view),
        }

    def t7() -> dict[str, Any]:
        # The preregistration's version/date examples can contradict passage text.
        # Use a fixture-only search-scope fact that can vary independently of passage semantics.
        mutated = copy.deepcopy(fixture)
        before = mutated["coverage"]["search_scope"]["closed_world"]
        mutated["coverage"]["search_scope"]["closed_world"] = not before
        validate_fixture(mutated)
        diffs = _deep_diff(fixture, mutated)
        expected_path = "$.coverage.search_scope.closed_world"
        if len(diffs) != 1 or diffs[0]["path"] != expected_path:
            raise CheckFailure(f"mechanical control was not single-variable: {diffs}")
        mutated_v1 = build_handoff_variant(mutated, "minimal_context")
        mutated_view = build_cal_measurement_view(mutated_v1)
        if canonical_hash(mutated_view) == canonical_hash(v1_view):
            raise CheckFailure("mechanical context change did not change CAL context input")
        if _hash_obj(_semantic_payload(mutated_view)) != _hash_obj(_semantic_payload(v1_view)):
            raise CheckFailure("mechanical context control changed proposition/passage semantics")
        deviations.append(
            {
                "test_id": "T7",
                "type": "control_redesign",
                "reason": "version/effective-date mutation could create an internally inconsistent evidence world",
                "replacement": expected_path,
            }
        )
        return {
            "single_diff": diffs[0],
            "baseline_context_view_hash": canonical_hash(v1_view),
            "mutated_context_view_hash": canonical_hash(mutated_view),
            "semantic_payload_hash_unchanged": _hash_obj(_semantic_payload(v1_view)),
        }

    def t8() -> dict[str, Any]:
        # Cross-repo execution of CAL's current policy is delegated to pinned Rung-05 tests.
        # Here we establish the EB-side structural isolation on the same tri-repo evidence world.
        mutated = copy.deepcopy(fixture)
        src = next(s for s in mutated["sources"] if s["source_id"] == "src-incident")
        before = src["source_trust_level"]
        src["source_trust_level"] = "secondary" if before == "primary" else "primary"
        validate_fixture(mutated)
        diffs = _deep_diff(fixture, mutated)
        if len(diffs) != 1 or diffs[0]["path"] != "$.sources[1].source_trust_level":
            raise CheckFailure(f"trust control was not single-variable: {diffs}")
        mutated_v1 = build_handoff_variant(mutated, "minimal_context")
        mutated_view = build_cal_measurement_view(mutated_v1)
        if canonical_hash(mutated_view) != canonical_hash(v1_view):
            raise CheckFailure("trust level leaked into EB research semantic measurement view")
        return {
            "single_diff": diffs[0],
            "semantic_measurement_view_hash_unchanged": canonical_hash(v1_view),
            "cal_policy_execution": "see pinned CAL Rung-05 H05_2/H05_3 workflow evidence",
        }

    def t9() -> dict[str, Any]:
        coverage = v1_view["coverage"]
        serialized = json.dumps(v1_view, sort_keys=True)
        if "completeness_conclusion" in serialized or "sufficient_for_fixture_only" in serialized:
            raise CheckFailure("CAL completeness judgment leaked into V1 measurement view")
        sidecar_aperture = v2["cal_research_sidecar"]["aperture"]
        if "completeness_conclusion" not in sidecar_aperture:
            raise CheckFailure("V2 upper-bound sidecar lacks the intended completeness judgment control")
        return {
            "coverage": coverage,
            "v1_has_completeness_judgment": False,
            "v2_sidecar_completeness_judgment": sidecar_aperture["completeness_conclusion"],
        }

    def t10() -> dict[str, Any]:
        all_passage_ids = {p["passage_id"] for p in v1["passages"]}
        admitted = _passage_ids(v1_view)
        old = next(a for a in v2["cal_research_sidecar"]["assessments"] if a["passage_id"] == "psg-validation-old")
        incident = next(a for a in v2["cal_research_sidecar"]["assessments"] if a["passage_id"] == "psg-incident")
        if old["decision_participation"] is not False or incident["decision_participation"] is not False:
            raise CheckFailure("fixture no longer contains intended non-deciding controls")
        for pid in ("psg-validation-old", "psg-incident"):
            if pid not in all_passage_ids or pid not in admitted:
                raise CheckFailure(f"non-deciding admitted evidence was erased: {pid}")
        if "psg-marketing" not in all_passage_ids or "psg-marketing" in admitted:
            raise CheckFailure("rejected candidate preservation/admission boundary is wrong")
        if collect_fact_ids(v1) != set(fixture["required_mechanical_fact_ids"]):
            raise CheckFailure("upstream context facts are not fully reconstructable")
        return {
            "all_upstream_passage_ids": sorted(all_passage_ids),
            "admitted_semantic_passage_ids": sorted(admitted),
            "non_deciding_but_preserved": ["psg-validation-old", "psg-incident"],
            "rejected_but_recoverable": "psg-marketing",
            "preserved_fact_ids": sorted(collect_fact_ids(v1)),
        }

    def t11() -> dict[str, Any]:
        b_hash = canonical_hash(v1)
        semantic_hash = _hash_obj(_semantic_payload(v1_view))
        first = _make_result_artifact(
            contract_b_hash=b_hash,
            semantic_measurement_hash=semantic_hash,
            cal_policy_id="cal-policy-A",
            assessment_state="initial",
        )
        first_bytes = json.dumps(first, sort_keys=True).encode("utf-8")
        second = _make_result_artifact(
            contract_b_hash=b_hash,
            semantic_measurement_hash=semantic_hash,
            cal_policy_id="cal-policy-B",
            assessment_state="re-audit",
        )
        if first["contract_b_hash"] != second["contract_b_hash"]:
            raise CheckFailure("re-audit no longer binds the same immutable B input")
        if first["result_hash"] == second["result_hash"]:
            raise CheckFailure("policy/state change did not create a distinct result artifact")
        if json.dumps(first, sort_keys=True).encode("utf-8") != first_bytes:
            raise CheckFailure("first result artifact mutated during re-audit construction")
        return {
            "contract_b_hash": b_hash,
            "first_result": first,
            "second_result": second,
            "prior_result_unchanged": True,
        }

    def t12() -> dict[str, Any]:
        writeback_path = CAL_ROOT / "src/claim_audit_lab/v1/cb_writeback.py"
        text = writeback_path.read_text(encoding="utf-8")
        required_markers = [
            "shutil.copytree(source_bundle_dir, out_dir)",
            "reseal_bundle(out_dir)",
            ".audit-trace.json",
        ]
        missing = [marker for marker in required_markers if marker not in text]
        if missing:
            raise CheckFailure(f"pinned CAL writeback mechanism changed; missing {missing}")
        result = _make_result_artifact(
            contract_b_hash=canonical_hash(v1),
            semantic_measurement_hash=_hash_obj(_semantic_payload(v1_view)),
            cal_policy_id="cal-policy-A",
            assessment_state="initial",
        )
        if any(key in result for key in ("sources", "passages", "links", "coverage", "claim")):
            raise CheckFailure("separate result artifact duplicated upstream evidence-world payload")
        deviations.append(
            {
                "test_id": "T12",
                "type": "feasibility_limit",
                "reason": "current CAL resealed-C-B writer consumes canonical on-disk C-B, not the V1 research projection; no synthetic conversion was introduced",
                "mechanism_control": "pinned CAL test_cb_writeback.py executed separately in workflow",
            }
        )
        return {
            "status_detail": "PARTIAL_MECHANISM_COMPARISON",
            "resealed_derivative": {
                "upstream_copy": "full source bundle copied before audit material is added",
                "resealed": True,
                "self_contained": True,
                "changes_bundle_hash": True,
                "compatibility": "preserves current C-B-shaped audited derivative",
            },
            "separate_result": {
                "binds_contract_b_hash": result["contract_b_hash"],
                "duplicates_upstream_payload": False,
                "self_contained_without_bound_B": False,
                "result_hash": result["result_hash"],
                "ownership": "CAL result fields remain downstream-owned",
            },
            "same_world_execution": False,
            "reason": "not feasible without adding an unpreregistered V1-to-canonical-C-B transformation",
        }

    for test_id, title, fn in [
        ("T1", "Input/hash/integrity validation", t1),
        ("T2", "V0 fail-closed with no invented defaults", t2),
        ("T3", "Deterministic V1 pre-assessment ledger", t3),
        ("T4", "V1/V2 pre-assessment semantic-measurement equivalence", t4),
        ("T5", "Hostile V2-sidecar mutation/blinding", t5),
        ("T6", "EB nomination role/rank/score invariance", t6),
        ("T7", "Single-variable mechanical-context sensitivity", t7),
        ("T8", "Trust-level versus CAL-policy separation", t8),
        ("T9", "Coverage facts versus CAL completeness judgment", t9),
        ("T10", "Non-destructive evidence/context preservation", t10),
        ("T11", "Re-audit/result immutability", t11),
        ("T12", "Resealed C-B versus immutable-B-bound result packaging", t12),
    ]:
        _record(records, test_id, title, fn)

    failures = [r for r in records if r["status"] == "FAIL"]
    payload = {
        "experiment": "Contract B V0/V1/V2 conformance",
        "research_only": True,
        "pinned_heads": {
            "evidence_bundler": EB_SHA,
            "claim_audit_lab": CAL_SHA,
            "apparatus_contracts_preregistered_base": APPARATUS_SHA,
            "decision_engine_downstream_context": DECISION_ENGINE_SHA,
        },
        "fixture": str(FIXTURE_PATH.relative_to(EB_ROOT)),
        "claim_under_review": "The V1 minimal factual-context Contract B handoff contains enough upstream evidence-world state for CAL to construct its pre-assessment measurement view without inventing defaults or accepting upstream proposition-specific semantic judgments.",
        "tests": records,
        "deviations": deviations,
        "custom_runner_failures": len(failures),
        "note": "Pinned CAL Rung-04/Rung-05 and writeback tests are executed by the workflow and reported separately; green CI is not treated as architectural confirmation.",
    }
    (RESULTS_DIR / "custom-run.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Contract B V0/V1/V2 custom conformance run",
        "",
        "Research-only execution record. This file is an observation artifact, not a schema decision.",
        "",
        "## Pins",
        "",
        *[f"- `{name}`: `{sha}`" for name, sha in payload["pinned_heads"].items()],
        "",
        "## Checks",
        "",
        "| Test | Status | Title |",
        "|---|---|---|",
        *[f"| {r['test_id']} | {r['status']} | {r['title']} |" for r in records],
        "",
        "## Deviations and feasibility limits",
        "",
    ]
    for deviation in deviations:
        lines.append(f"- **{deviation['test_id']} / {deviation['type']}**: {deviation['reason']}")
    if not deviations:
        lines.append("- None recorded.")
    lines.extend(["", f"Custom runner failures: **{len(failures)}**", ""])
    (RESULTS_DIR / "custom-run.md").write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
