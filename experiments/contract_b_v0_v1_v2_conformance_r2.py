"""Run 2 of the Contract B V0/V1/V2 conformance experiment.

This is a research-only correction to the experimental harness after run 1
revealed runner/orchestration defects. Product and canonical contract code are
not modified.
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
RESULTS_DIR = Path(os.environ.get("RESULTS_DIR", ROOT / "experiment-results/contract-b-v0-v1-v2-r2")).resolve()
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

PINS = {
    "evidence_bundler": "b4ca9111f5957ef7e7955e2c5024f2280ee19eb5",
    "claim_audit_lab": "6acc3462dad73959ccec6bccf8407215f5274cf6",
    "apparatus_contracts_preregistered_base": "63e8506396132a44ebc0e6c2312047e99b1125eb",
    "decision_engine_downstream_context": "55f108c196ead020b5965c7d4d737464c92bc4a0",
}
FIXTURE_PATH = EB_ROOT / "examples/contract-b-seam/tri-repo-fixture.yaml"


def h(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def semantic_payload(view: dict[str, Any]) -> dict[str, Any]:
    return {
        "claim_id": view["claim"]["claim_id"],
        "claim_text": view["claim"]["claim_text"],
        "passages": [
            {"passage_id": p["passage_id"], "text": p["text"]}
            for p in view["admitted_passages"]
        ],
    }


def deep_diff(a: Any, b: Any, path: str = "$") -> list[dict[str, Any]]:
    if type(a) is not type(b):
        return [{"path": path, "before": a, "after": b}]
    if isinstance(a, dict):
        out: list[dict[str, Any]] = []
        for key in sorted(set(a) | set(b)):
            child = f"{path}.{key}"
            if key not in a:
                out.append({"path": child, "before": "<missing>", "after": b[key]})
            elif key not in b:
                out.append({"path": child, "before": a[key], "after": "<missing>"})
            else:
                out.extend(deep_diff(a[key], b[key], child))
        return out
    if isinstance(a, list):
        if len(a) != len(b):
            return [{"path": path + ".length", "before": len(a), "after": len(b)}]
        out: list[dict[str, Any]] = []
        for idx, (left, right) in enumerate(zip(a, b, strict=True)):
            out.extend(deep_diff(left, right, f"{path}[{idx}]"))
        return out
    return [] if a == b else [{"path": path, "before": a, "after": b}]


def result_artifact(b_hash: str, semantic_hash: str, policy: str, state: str) -> dict[str, Any]:
    body = {
        "artifact_kind": "cal-result-research-candidate",
        "contract_b_hash": b_hash,
        "semantic_measurement_hash": semantic_hash,
        "cal_policy_id": policy,
        "assessment_state": state,
    }
    return {**body, "result_hash": h(body)}


def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    fixture_bytes = FIXTURE_PATH.read_bytes()
    fixture = load_fixture(FIXTURE_PATH)
    v0 = build_handoff_variant(fixture, "current_cb")
    v1 = build_handoff_variant(fixture, "minimal_context")
    v2 = build_handoff_variant(fixture, "full_sidecar")
    view1 = build_cal_measurement_view(v1)
    view2 = build_cal_measurement_view(v2)
    records: list[dict[str, Any]] = []
    deviations: list[dict[str, Any]] = [
        {
            "run": 1,
            "type": "harness_failure",
            "detail": "Run 1 used incorrect fixture keys and incorrect pytest scoping/import paths; preserved separately and not counted as seam evidence.",
        }
    ]

    def run(test_id: str, title: str, fn: Callable[[], dict[str, Any]]) -> None:
        try:
            records.append({"test_id": test_id, "title": title, "status": "PASS", "evidence": fn()})
        except Exception as exc:
            records.append({"test_id": test_id, "title": title, "status": "FAIL", "error_type": type(exc).__name__, "error": str(exc)})

    def t1() -> dict[str, Any]:
        validate_fixture(fixture)
        bad = copy.deepcopy(fixture)
        bad["coverage"]["admitted_count"] += 1
        try:
            validate_fixture(bad)
        except SeamProbeError as exc:
            rejection = str(exc)
        else:
            raise AssertionError("coverage tamper not rejected")
        return {
            "fixture_file_hash": "sha256:" + hashlib.sha256(fixture_bytes).hexdigest(),
            "v0_hash": h(v0), "v1_hash": h(v1), "v2_hash": h(v2),
            "tamper_rejection": rejection,
        }

    def t2() -> dict[str, Any]:
        try:
            build_cal_measurement_view(v0)
        except SeamProbeError as exc:
            return {"typed_failure": str(exc), "default_fabricated": False}
        raise AssertionError("V0 unexpectedly constructed a measurement view")

    def t3() -> dict[str, Any]:
        again = build_handoff_variant(fixture, "minimal_context")
        assert canonical_hash(again) == canonical_hash(v1)
        required = set(fixture["required_mechanical_fact_ids"])
        present = collect_fact_ids(v1)
        assert required <= present
        judgments = sorted(find_audit_judgment_keys(v1))
        assert judgments == []
        assert v1["claim"]["claim_text"] == fixture["claim"]["claim_text"]
        assert {p["passage_id"]: p["text"] for p in v1["passages"]} == {
            p["passage_id"]: p["text"] for p in fixture["passages"]
        }
        return {
            "ledger_hash": canonical_hash(v1),
            "required_fact_ids": sorted(required),
            "link_history_count": len(v1["links"]),
            "coverage": v1["coverage"],
            "cal_judgment_keys": judgments,
        }

    def t4() -> dict[str, Any]:
        assert canonical_hash(view1) == canonical_hash(view2)
        assert h(semantic_payload(view1)) == h(semantic_payload(view2))
        return {"measurement_view_hash": canonical_hash(view1), "semantic_payload_hash": h(semantic_payload(view1))}

    def t5() -> dict[str, Any]:
        hostile = mutate_downstream_assessments(fixture)
        hostile_v2 = build_handoff_variant(hostile, "full_sidecar")
        diffs = deep_diff(v2["cal_research_sidecar"], hostile_v2["cal_research_sidecar"])
        assert diffs
        hostile_view = build_cal_measurement_view(hostile_v2)
        assert canonical_hash(hostile_view) == canonical_hash(view1)
        return {"hostile_mutation_count": len(diffs), "sample": diffs[:8], "blinded_view_hash": canonical_hash(hostile_view)}

    def t6() -> dict[str, Any]:
        mutated = mutate_nomination_metadata(fixture)
        mv1 = build_handoff_variant(mutated, "minimal_context")
        mview = build_cal_measurement_view(mv1)
        assert handoff_hash(mutated) != handoff_hash(fixture)
        assert canonical_hash(mview) == canonical_hash(view1)
        return {
            "baseline_handoff_hash": handoff_hash(fixture),
            "mutated_handoff_hash": handoff_hash(mutated),
            "semantic_view_hash": canonical_hash(view1),
        }

    def t7() -> dict[str, Any]:
        mutated = copy.deepcopy(fixture)
        mutated["coverage"]["search_scope"]["closed_world"] = not mutated["coverage"]["search_scope"]["closed_world"]
        validate_fixture(mutated)
        diffs = deep_diff(fixture, mutated)
        assert diffs == [{"path": "$.coverage.search_scope.closed_world", "before": True, "after": False}]
        mview = build_cal_measurement_view(build_handoff_variant(mutated, "minimal_context"))
        assert canonical_hash(mview) != canonical_hash(view1)
        assert h(semantic_payload(mview)) == h(semantic_payload(view1))
        deviations.append({
            "test_id": "T7", "type": "control_redesign",
            "detail": "Used coverage.search_scope.closed_world instead of changing a version/date fact, because the latter would contradict unchanged passage content and confound the control.",
        })
        return {
            "single_diff": diffs[0],
            "baseline_context_hash": canonical_hash(view1),
            "mutated_context_hash": canonical_hash(mview),
            "semantic_payload_hash": h(semantic_payload(view1)),
        }

    def t8() -> dict[str, Any]:
        mutated = copy.deepcopy(fixture)
        incident = next(s for s in mutated["sources"] if s["source_id"] == "src-incident")
        incident["source_trust_level"] = "secondary"
        validate_fixture(mutated)
        diffs = deep_diff(fixture, mutated)
        assert diffs == [{"path": "$.sources[1].source_trust_level", "before": "primary", "after": "secondary"}]
        mview = build_cal_measurement_view(build_handoff_variant(mutated, "minimal_context"))
        assert canonical_hash(mview) == canonical_hash(view1)
        return {
            "single_diff": diffs[0],
            "semantic_view_hash_unchanged": canonical_hash(view1),
            "policy_layer_control": "Pinned CAL Rung-05 H05_2/H05_3 executed separately by workflow",
        }

    def t9() -> dict[str, Any]:
        serialized = json.dumps(view1, sort_keys=True)
        assert "completeness_conclusion" not in serialized
        assert "sufficient_for_fixture_only" not in serialized
        aperture = v2["cal_research_sidecar"]["aperture_assessment"]
        assert aperture["completeness_conclusion"] == "sufficient_for_fixture_only"
        return {
            "coverage_facts": view1["coverage"],
            "v1_completeness_judgment": None,
            "v2_sidecar_completeness_judgment": aperture["completeness_conclusion"],
        }

    def t10() -> dict[str, Any]:
        upstream = {p["passage_id"] for p in v1["passages"]}
        admitted = {p["passage_id"] for p in view1["admitted_passages"]}
        for pid in ("psg-validation-old", "psg-incident"):
            assessment = next(a for a in v2["cal_research_sidecar"]["assessments"] if a["passage_id"] == pid)
            assert assessment["decision_participation"] is False
            assert pid in upstream and pid in admitted
        assert "psg-marketing" in upstream and "psg-marketing" not in admitted
        assert collect_fact_ids(v1) == set(fixture["required_mechanical_fact_ids"])
        return {
            "upstream_passage_ids": sorted(upstream),
            "admitted_passage_ids": sorted(admitted),
            "non_deciding_but_preserved": ["psg-validation-old", "psg-incident"],
            "rejected_but_recoverable": "psg-marketing",
        }

    def t11() -> dict[str, Any]:
        b_hash = canonical_hash(v1)
        s_hash = h(semantic_payload(view1))
        first = result_artifact(b_hash, s_hash, "cal-policy-A", "initial")
        frozen = json.dumps(first, sort_keys=True)
        second = result_artifact(b_hash, s_hash, "cal-policy-B", "re-audit")
        assert first["contract_b_hash"] == second["contract_b_hash"]
        assert first["result_hash"] != second["result_hash"]
        assert json.dumps(first, sort_keys=True) == frozen
        return {"bound_contract_b_hash": b_hash, "first": first, "second": second, "prior_result_unchanged": True}

    def t12() -> dict[str, Any]:
        source = (CAL_ROOT / "src/claim_audit_lab/v1/cb_writeback.py").read_text(encoding="utf-8")
        for marker in ("shutil.copytree(source_bundle_dir, out_dir)", "reseal_bundle(out_dir)", ".audit-trace.json"):
            assert marker in source
        separate = result_artifact(canonical_hash(v1), h(semantic_payload(view1)), "cal-policy-A", "initial")
        assert not any(k in separate for k in ("claim", "sources", "passages", "links", "coverage"))
        deviations.append({
            "test_id": "T12", "type": "feasibility_limit",
            "detail": "The pinned resealed-C-B writer consumes canonical on-disk C-B rather than the V1 research projection. Its mechanism was executed on CAL's existing fixture; no synthetic V1-to-canonical conversion was invented.",
        })
        return {
            "comparison_scope": "mechanism comparison; not same-world byte-for-byte packaging",
            "resealed_derivative": {
                "copies_full_input_bundle": True,
                "reseals_output": True,
                "self_contained": True,
                "adds_downstream_judgment_inside_C_B_shaped_derivative": True,
            },
            "separate_result": {
                "binds_immutable_B_by_hash": separate["contract_b_hash"],
                "duplicates_upstream_evidence_payload": False,
                "self_contained_without_bound_B": False,
                "downstream_ownership_explicit": True,
            },
            "same_world_execution": False,
        }

    tests = [
        ("T1", "Input/hash/integrity validation", t1),
        ("T2", "V0 fail-closed behavior", t2),
        ("T3", "Deterministic V1 pre-assessment ledger", t3),
        ("T4", "V1/V2 semantic-measurement equivalence", t4),
        ("T5", "Hostile V2 sidecar mutation/blinding", t5),
        ("T6", "Nomination role/rank/score invariance", t6),
        ("T7", "Single-variable mechanical-context sensitivity", t7),
        ("T8", "Trust versus CAL-policy separation", t8),
        ("T9", "Coverage facts versus completeness judgment", t9),
        ("T10", "Non-destructive preservation", t10),
        ("T11", "Re-audit/result immutability", t11),
        ("T12", "Result packaging comparison", t12),
    ]
    for args in tests:
        run(*args)

    failures = [r for r in records if r["status"] == "FAIL"]
    payload = {
        "experiment": "Contract B V0/V1/V2 conformance run 2",
        "research_only": True,
        "pinned_heads": PINS,
        "fixture": "examples/contract-b-seam/tri-repo-fixture.yaml",
        "tests": records,
        "deviations": deviations,
        "failure_count": len(failures),
    }
    (RESULTS_DIR / "custom-run-r2.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Contract B V0/V1/V2 conformance run 2", "",
        "Research-only execution record. Run 1 harness failures are preserved separately.", "",
        "| Test | Status | Title |", "|---|---|---|",
        *[f"| {r['test_id']} | {r['status']} | {r['title']} |" for r in records],
        "", "## Deviations", "",
        *[f"- {d.get('test_id', 'RUN1')}: {d['type']} — {d['detail']}" for d in deviations],
        "", f"Failures: **{len(failures)}**", "",
    ]
    (RESULTS_DIR / "custom-run-r2.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
