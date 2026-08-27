#!/usr/bin/env python3
"""Bounded baseline-only reproducibility runner for Contract B RC1."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

APPARATUS_PARENT = "40349629c289a340c95735510cf04b1926d200d0"
EB_SHA = "b4ca9111f5957ef7e7955e2c5024f2280ee19eb5"
CAL_SHA = "6acc3462dad73959ccec6bccf8407215f5274cf6"
EXPECTED_V1 = "sha256:a861eeafe9a360e9280e2d2c092bd2bbcdee6661c55412802be6fecbf8c7b2d7"
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
        for k, v in value.items():
            if k in PROHIBITED:
                found.add(k)
            found |= find_prohibited(v)
    elif isinstance(value, list):
        for item in value:
            found |= find_prohibited(item)
    return found


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--eb-root", type=Path, required=True)
    p.add_argument("--cal-root", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    sys.path.insert(0, str((args.eb_root / "src").resolve()))
    from evidence_bundler.experiments.contract_b_seam_probe import (  # noqa: PLC0415
        build_handoff_variant, canonical_hash, load_fixture,
    )

    fixture = load_fixture(args.eb_root / "examples/contract-b-seam/tri-repo-fixture.yaml")
    v1 = build_handoff_variant(fixture, "minimal_context")
    v1_hash = canonical_hash(v1)
    if v1_hash != EXPECTED_V1:
        raise SystemExit(f"frozen V1 drift: {v1_hash}")
    input_path = args.out / "frozen_v1.json"
    input_path.write_bytes(canonical_bytes(v1) + b"\n")

    here = Path(__file__).resolve().parent
    a = subprocess.run([
        sys.executable, str(here / "contract_b_rc1_consumer_a.py"),
        "--input", str(input_path), "--eb-root", str(args.eb_root), "--out", str(args.out),
    ], text=True, capture_output=True)
    b = subprocess.run([
        "node", str(here / "contract_b_rc1_consumer_b.mjs"),
        "--input", str(input_path), "--out", str(args.out),
    ], text=True, capture_output=True)

    result: dict[str, Any] = {
        "experiment": "contract-b-rc1-independent-consumer-baseline",
        "status": "research_only",
        "scope": "baseline equivalence only; no metamorphic tests; no Contract C",
        "pins": {
            "apparatus_parent": APPARATUS_PARENT,
            "evidence_bundler": EB_SHA,
            "claim_audit_lab": CAL_SHA,
        },
        "frozen_v1_sha256": v1_hash,
        "consumer_a": {"returncode": a.returncode, "stdout": a.stdout, "stderr": a.stderr},
        "consumer_b": {"returncode": b.returncode, "stdout": b.stdout, "stderr": b.stderr},
        "independence": {
            "consumer_a_language": "python",
            "consumer_a_semantic_dependency": "pinned EB build_cal_measurement_view only",
            "consumer_b_language": "javascript/node",
            "consumer_b_implementation_dependencies": "standard library only; no EB/CAL imports",
            "shared_normalization_module": False,
            "same_orchestrating_reviewer_authored_both": True,
            "separate_agent_runtime_available": False,
        },
    }

    if a.returncode != 0 or b.returncode != 0:
        result["disposition"] = "BASELINE_EXECUTION_FAILED"
        (args.out / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, indent=2))
        return 1

    a_ledger_raw = (args.out / "consumer_a_ledger.json").read_bytes().rstrip(b"\n")
    b_ledger_raw = (args.out / "consumer_b_ledger.json").read_bytes().rstrip(b"\n")
    a_sem_raw = (args.out / "consumer_a_semantic.json").read_bytes().rstrip(b"\n")
    b_sem_raw = (args.out / "consumer_b_semantic.json").read_bytes().rstrip(b"\n")
    a_ledger = json.loads(a_ledger_raw)
    b_ledger = json.loads(b_ledger_raw)
    a_sem = json.loads(a_sem_raw)
    b_sem = json.loads(b_sem_raw)
    ar = json.loads((args.out / "consumer_a_result.json").read_text())
    br = json.loads((args.out / "consumer_b_result.json").read_text())

    checks = {
        "input_hash_equal": ar["input_sha256"] == br["input_sha256"] == EXPECTED_V1,
        "ledger_bytes_equal": a_ledger_raw == b_ledger_raw,
        "ledger_hash_equal": ar["ledger_sha256"] == br["ledger_sha256"] == digest(a_ledger) == digest(b_ledger),
        "semantic_bytes_equal": a_sem_raw == b_sem_raw,
        "semantic_hash_equal": ar["semantic_sha256"] == br["semantic_sha256"] == digest(a_sem) == digest(b_sem),
        "no_prohibited_cal_judgments_a": not find_prohibited(a_ledger),
        "no_prohibited_cal_judgments_b": not find_prohibited(b_ledger),
        "stored_coverage_counts_not_canonicalized_a": not any(k in json.dumps(a_ledger) for k in ["candidate_count", "reviewed_count", "admitted_count"]),
        "stored_coverage_counts_not_canonicalized_b": not any(k in json.dumps(b_ledger) for k in ["candidate_count", "reviewed_count", "admitted_count"]),
    }
    result["consumer_a_result"] = ar
    result["consumer_b_result"] = br
    result["checks"] = checks
    result["ledger_sha256"] = ar["ledger_sha256"]
    result["semantic_sha256"] = ar["semantic_sha256"]
    passed = all(checks.values())
    result["disposition"] = "BASELINE_REPRODUCIBLE" if passed else "BASELINE_NOT_REPRODUCIBLE"

    (args.out / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
