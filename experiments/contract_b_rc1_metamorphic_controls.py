#!/usr/bin/env python3
"""Preregistered metamorphic controls for the frozen Contract B RC1 consumers.

The existing Consumer A/B normalization code is not modified. For mutations where
integrity is not the variable under test, this harness substitutes only the expected
input SHA constant at execution time. M4 deliberately retains the frozen hash.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

EB_SHA = "b4ca9111f5957ef7e7955e2c5024f2280ee19eb5"
CAL_SHA = "6acc3462dad73959ccec6bccf8407215f5274cf6"
RC1_BASE = "aa016bcebd57dd09870a9cd4cc129ea7f7f5fc43"
BASELINE_HASH = "sha256:a861eeafe9a360e9280e2d2c092bd2bbcdee6661c55412802be6fecbf8c7b2d7"
BASELINE_LEDGER = "sha256:5e168cf01e3e187280a3ea3cca9fe8b88741e3e015616aca50f6043a4a310c57"
BASELINE_SEMANTIC = "sha256:814d5966f876a26bca40e2fc189134ea3921736b5a92e8bd6ec30a3a392b54dc"
PROHIBITED = {
    "proposition_specific_relation", "semantic_validity", "temporal_applicability",
    "authority_applicability", "decision_participation", "completeness_conclusion",
    "verdict", "abstention",
}


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def find_prohibited(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            if key in PROHIBITED:
                found.add(key)
            found |= find_prohibited(child)
    elif isinstance(value, list):
        for child in value:
            found |= find_prohibited(child)
    return found


def masked_ledger_bytes(value: dict[str, Any]) -> bytes:
    masked = copy.deepcopy(value)
    masked["input_identity"]["input_sha256"] = "<masked-input-sha>"
    return canonical_bytes(masked)


def run_a(a_path: Path, input_path: Path, eb_root: Path, out_dir: Path, expected: str) -> subprocess.CompletedProcess[str]:
    code = r'''import importlib.util, sys
expected, script, input_path, eb_root, out_dir = sys.argv[1:6]
spec = importlib.util.spec_from_file_location("rc1_consumer_a_control", script)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)
module.EXPECTED_INPUT = expected
sys.argv = [script, "--input", input_path, "--eb-root", eb_root, "--out", out_dir]
raise SystemExit(module.main())
'''
    return subprocess.run(
        [sys.executable, "-c", code, expected, str(a_path), str(input_path), str(eb_root), str(out_dir)],
        text=True, capture_output=True,
    )


def run_b(b_path: Path, input_path: Path, out_dir: Path, expected: str, scratch_dir: Path) -> subprocess.CompletedProcess[str]:
    source = b_path.read_text(encoding="utf-8")
    if source.count(BASELINE_HASH) != 1:
        raise RuntimeError("Consumer B expected-hash constant is not uniquely replaceable")
    controlled = source.replace(BASELINE_HASH, expected, 1)
    temp = scratch_dir / "consumer_b_control.mjs"
    temp.write_text(controlled, encoding="utf-8")
    return subprocess.run(
        ["node", str(temp), "--input", str(input_path), "--out", str(out_dir)],
        text=True, capture_output=True,
    )


def run_success_case(
    name: str,
    value: dict[str, Any],
    expected: str,
    *,
    root: Path,
    eb_root: Path,
    a_path: Path,
    b_path: Path,
) -> dict[str, Any]:
    case = root / name
    a_out, b_out = case / "a", case / "b"
    case.mkdir(parents=True, exist_ok=True)
    input_path = case / "input.json"
    input_path.write_bytes(canonical_bytes(value) + b"\n")
    a = run_a(a_path, input_path, eb_root, a_out, expected)
    b = run_b(b_path, input_path, b_out, expected, case)
    observed = {
        "input_sha256": digest(value),
        "expected_sha256": expected,
        "a_returncode": a.returncode,
        "b_returncode": b.returncode,
        "a_stdout": a.stdout,
        "a_stderr": a.stderr,
        "b_stdout": b.stdout,
        "b_stderr": b.stderr,
    }
    if a.returncode != 0 or b.returncode != 0:
        observed["execution_ok"] = False
        return observed
    a_ledger_raw = (a_out / "consumer_a_ledger.json").read_bytes().rstrip(b"\n")
    b_ledger_raw = (b_out / "consumer_b_ledger.json").read_bytes().rstrip(b"\n")
    a_sem_raw = (a_out / "consumer_a_semantic.json").read_bytes().rstrip(b"\n")
    b_sem_raw = (b_out / "consumer_b_semantic.json").read_bytes().rstrip(b"\n")
    a_ledger, b_ledger = json.loads(a_ledger_raw), json.loads(b_ledger_raw)
    a_sem, b_sem = json.loads(a_sem_raw), json.loads(b_sem_raw)
    observed.update({
        "execution_ok": True,
        "cross_consumer_ledger_bytes_equal": a_ledger_raw == b_ledger_raw,
        "cross_consumer_semantic_bytes_equal": a_sem_raw == b_sem_raw,
        "a_ledger_hash": digest(a_ledger),
        "b_ledger_hash": digest(b_ledger),
        "a_semantic_hash": digest(a_sem),
        "b_semantic_hash": digest(b_sem),
        "a_ledger": a_ledger,
        "b_ledger": b_ledger,
        "a_semantic": a_sem,
        "b_semantic": b_sem,
        "a_ledger_raw": a_ledger_raw.decode("utf-8"),
        "a_semantic_raw": a_sem_raw.decode("utf-8"),
        "masked_ledger": masked_ledger_bytes(a_ledger).decode("utf-8"),
    })
    return observed


def run_failure_case(
    name: str,
    value: dict[str, Any],
    expected: str,
    *,
    root: Path,
    eb_root: Path,
    a_path: Path,
    b_path: Path,
) -> dict[str, Any]:
    case = root / name
    a_out, b_out = case / "a", case / "b"
    case.mkdir(parents=True, exist_ok=True)
    input_path = case / "input.json"
    input_path.write_bytes(canonical_bytes(value) + b"\n")
    a = run_a(a_path, input_path, eb_root, a_out, expected)
    b = run_b(b_path, input_path, b_out, expected, case)
    return {
        "input_sha256": digest(value),
        "expected_sha256": expected,
        "a_returncode": a.returncode,
        "b_returncode": b.returncode,
        "a_stdout": a.stdout,
        "a_stderr": a.stderr,
        "b_stdout": b.stdout,
        "b_stderr": b.stderr,
        "a_outputs_absent": not (a_out / "consumer_a_ledger.json").exists() and not (a_out / "consumer_a_semantic.json").exists(),
        "b_outputs_absent": not (b_out / "consumer_b_ledger.json").exists() and not (b_out / "consumer_b_semantic.json").exists(),
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--eb-root", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    sys.path.insert(0, str((args.eb_root / "src").resolve()))
    from evidence_bundler.experiments.contract_b_seam_probe import build_handoff_variant, load_fixture  # noqa: PLC0415

    fixture = load_fixture(args.eb_root / "examples/contract-b-seam/tri-repo-fixture.yaml")
    baseline_v1 = build_handoff_variant(fixture, "minimal_context")
    if digest(baseline_v1) != BASELINE_HASH:
        raise SystemExit(f"frozen V1 drift: {digest(baseline_v1)}")

    here = Path(__file__).resolve().parent
    a_path = here / "contract_b_rc1_consumer_a.py"
    b_path = here / "contract_b_rc1_consumer_b.mjs"
    cases: dict[str, Any] = {}
    checks: dict[str, bool] = {}

    baseline = run_success_case("baseline", baseline_v1, BASELINE_HASH, root=args.out, eb_root=args.eb_root, a_path=a_path, b_path=b_path)
    cases["baseline"] = {k: v for k, v in baseline.items() if k not in {"a_ledger", "b_ledger", "a_semantic", "b_semantic", "a_ledger_raw", "a_semantic_raw", "masked_ledger"}}
    checks.update({
        "baseline_execution": baseline.get("execution_ok") is True,
        "baseline_cross_consumer_ledger": baseline.get("cross_consumer_ledger_bytes_equal") is True,
        "baseline_cross_consumer_semantic": baseline.get("cross_consumer_semantic_bytes_equal") is True,
        "baseline_ledger_hash_preserved": baseline.get("a_ledger_hash") == BASELINE_LEDGER,
        "baseline_semantic_hash_preserved": baseline.get("a_semantic_hash") == BASELINE_SEMANTIC,
    })
    if not all(checks.values()):
        raise SystemExit("baseline repeat failed before metamorphic controls")

    # M1: mutate preparation metadata that must be audit-visible but semantic-blind.
    m1 = copy.deepcopy(baseline_v1)
    target = next(link for link in m1["links"] if link["review"]["decision"] == "accepted")
    target["nomination"]["rank"] = 99
    target["nomination"]["scores"] = {"fusion": 0.01}
    target["nomination"]["hypothesized_role"] = "counter_candidate"
    m1r = run_success_case("m1_nomination_mutation", m1, digest(m1), root=args.out, eb_root=args.eb_root, a_path=a_path, b_path=b_path)
    cases["M1"] = {k: v for k, v in m1r.items() if k not in {"a_ledger", "b_ledger", "a_semantic", "b_semantic", "a_ledger_raw", "a_semantic_raw", "masked_ledger"}}
    checks.update({
        "m1_execution": m1r.get("execution_ok") is True,
        "m1_cross_consumer_ledger": m1r.get("cross_consumer_ledger_bytes_equal") is True,
        "m1_cross_consumer_semantic": m1r.get("cross_consumer_semantic_bytes_equal") is True,
        "m1_semantic_invariant": m1r.get("a_semantic_raw") == baseline.get("a_semantic_raw"),
        "m1_history_changes_ledger": m1r.get("masked_ledger") != baseline.get("masked_ledger"),
    })

    # M2: hostile CAL-only judgments must not cross the normalized Contract-B boundary.
    m2 = copy.deepcopy(baseline_v1)
    m2["cal_research_sidecar"] = {
        "verdict": "hostile_injection",
        "assessments": [{
            "passage_id": "psg-validation-current",
            "semantic_validity": "valid",
            "temporal_applicability": "current",
            "decision_participation": True,
        }],
    }
    m2r = run_success_case("m2_downstream_injection", m2, digest(m2), root=args.out, eb_root=args.eb_root, a_path=a_path, b_path=b_path)
    cases["M2"] = {k: v for k, v in m2r.items() if k not in {"a_ledger", "b_ledger", "a_semantic", "b_semantic", "a_ledger_raw", "a_semantic_raw", "masked_ledger"}}
    checks.update({
        "m2_execution": m2r.get("execution_ok") is True,
        "m2_cross_consumer_ledger": m2r.get("cross_consumer_ledger_bytes_equal") is True,
        "m2_cross_consumer_semantic": m2r.get("cross_consumer_semantic_bytes_equal") is True,
        "m2_semantic_invariant": m2r.get("a_semantic_raw") == baseline.get("a_semantic_raw"),
        "m2_ledger_invariant_except_input_hash": m2r.get("masked_ledger") == baseline.get("masked_ledger"),
        "m2_no_prohibited_ledger": not find_prohibited(m2r.get("a_ledger", {})),
        "m2_no_prohibited_semantic": not find_prohibited(m2r.get("a_semantic", {})),
    })

    # M3: missing and explicit null are the same extension-aware unknown state.
    m3a = copy.deepcopy(baseline_v1)
    m3a["claim"].pop("atomicity", None)
    m3n = copy.deepcopy(baseline_v1)
    m3n["claim"]["atomicity"] = None
    m3ar = run_success_case("m3_atomicity_absent", m3a, digest(m3a), root=args.out, eb_root=args.eb_root, a_path=a_path, b_path=b_path)
    m3nr = run_success_case("m3_atomicity_null", m3n, digest(m3n), root=args.out, eb_root=args.eb_root, a_path=a_path, b_path=b_path)
    cases["M3_absent"] = {k: v for k, v in m3ar.items() if k not in {"a_ledger", "b_ledger", "a_semantic", "b_semantic", "a_ledger_raw", "a_semantic_raw", "masked_ledger"}}
    cases["M3_null"] = {k: v for k, v in m3nr.items() if k not in {"a_ledger", "b_ledger", "a_semantic", "b_semantic", "a_ledger_raw", "a_semantic_raw", "masked_ledger"}}
    unknown = {"state": "unknown", "value": None}
    checks.update({
        "m3_absent_execution": m3ar.get("execution_ok") is True,
        "m3_null_execution": m3nr.get("execution_ok") is True,
        "m3_cross_consumer_absent": m3ar.get("cross_consumer_ledger_bytes_equal") is True,
        "m3_cross_consumer_null": m3nr.get("cross_consumer_ledger_bytes_equal") is True,
        "m3_absent_normalizes_unknown": m3ar.get("a_ledger", {}).get("claim", {}).get("atomicity") == unknown,
        "m3_null_normalizes_unknown": m3nr.get("a_ledger", {}).get("claim", {}).get("atomicity") == unknown,
        "m3_absent_null_equivalent_except_input_hash": m3ar.get("masked_ledger") == m3nr.get("masked_ledger"),
        "m3_semantic_absent_invariant": m3ar.get("a_semantic_raw") == baseline.get("a_semantic_raw"),
        "m3_semantic_null_invariant": m3nr.get("a_semantic_raw") == baseline.get("a_semantic_raw"),
    })

    # M4: corrupted bytes must fail against the original frozen hash.
    m4 = copy.deepcopy(baseline_v1)
    m4["links"][0]["nomination"]["rank"] = 777
    m4r = run_failure_case("m4_integrity_corruption", m4, BASELINE_HASH, root=args.out, eb_root=args.eb_root, a_path=a_path, b_path=b_path)
    cases["M4"] = m4r
    checks.update({
        "m4_a_rejects": m4r["a_returncode"] != 0,
        "m4_b_rejects": m4r["b_returncode"] != 0,
        "m4_a_no_outputs": m4r["a_outputs_absent"],
        "m4_b_no_outputs": m4r["b_outputs_absent"],
    })

    # M5: permute only collections explicitly normalized by RC1.
    m5 = copy.deepcopy(baseline_v1)
    m5["sources"].reverse()
    m5["passages"].reverse()
    m5["links"].reverse()
    for source in m5["sources"]:
        source["context_facts"] = list(reversed(source.get("context_facts", [])))
    for passage in m5["passages"]:
        passage["anchors"] = list(reversed(passage.get("anchors", [])))
    m5["coverage"]["limitations"] = list(reversed(m5["coverage"].get("limitations", [])))
    m5r = run_success_case("m5_ordering_invariance", m5, digest(m5), root=args.out, eb_root=args.eb_root, a_path=a_path, b_path=b_path)
    cases["M5"] = {k: v for k, v in m5r.items() if k not in {"a_ledger", "b_ledger", "a_semantic", "b_semantic", "a_ledger_raw", "a_semantic_raw", "masked_ledger"}}
    checks.update({
        "m5_execution": m5r.get("execution_ok") is True,
        "m5_cross_consumer_ledger": m5r.get("cross_consumer_ledger_bytes_equal") is True,
        "m5_cross_consumer_semantic": m5r.get("cross_consumer_semantic_bytes_equal") is True,
        "m5_semantic_invariant": m5r.get("a_semantic_raw") == baseline.get("a_semantic_raw"),
        "m5_ledger_invariant_except_input_hash": m5r.get("masked_ledger") == baseline.get("masked_ledger"),
    })

    # M6: redundant stored counts are verification inputs, not independent canonical facts.
    m6 = copy.deepcopy(baseline_v1)
    m6["coverage"]["candidate_count"] += 1
    m6r = run_failure_case("m6_stored_count_corruption", m6, digest(m6), root=args.out, eb_root=args.eb_root, a_path=a_path, b_path=b_path)
    cases["M6"] = m6r
    checks.update({
        "m6_a_rejects": m6r["a_returncode"] != 0,
        "m6_b_rejects": m6r["b_returncode"] != 0,
        "m6_a_no_outputs": m6r["a_outputs_absent"],
        "m6_b_no_outputs": m6r["b_outputs_absent"],
    })

    passed = all(checks.values())
    result = {
        "experiment": "contract-b-rc1-metamorphic-controls",
        "status": "research_only",
        "pins": {"rc1_base": RC1_BASE, "evidence_bundler": EB_SHA, "claim_audit_lab": CAL_SHA},
        "baseline_hash": BASELINE_HASH,
        "independence_claim": "none_new; reuses frozen A/B and changes only expected test-input hash when preregistered",
        "checks": checks,
        "cases": cases,
        "suite_result": "ALL_PREREGISTERED_CONTROLS_PASS" if passed else "ONE_OR_MORE_CONTROLS_FAILED",
        "contract_b_promoted": False,
        "contract_c_touched": False,
    }
    (args.out / "metamorphic_result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
