from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _self_controls() -> list[str]:
    failures = []

    # False permit counting.
    fake = [{"expected_allowed": False, "got": {"allowed": True}}]
    if sum(1 for r in fake if r["got"]["allowed"] and not r["expected_allowed"]) != 1:
        failures.append("false_permit_control")

    # Safe false reject affects recall but not unsafe permits.
    fake = [{"expected_allowed": True, "got": {"allowed": False}}]
    unsafe = sum(1 for r in fake if r["got"]["allowed"] and not r["expected_allowed"])
    tp = sum(1 for r in fake if r["got"]["allowed"] and r["expected_allowed"])
    if unsafe != 0 or tp != 0:
        failures.append("safe_incomplete_control")

    # Preservation mutation must be detectable.
    original = {"raw_source": "x", "proposals": [{"id": "p"}]}
    altered = {"raw_source": "y", "proposals": [{"id": "p"}]}
    if original["raw_source"] == altered["raw_source"]:
        failures.append("preservation_control")

    # Metamorphic control logic.
    if not (True == True):
        failures.append("same_pair_control")
    if not (True != False):
        failures.append("flip_pair_control")
    return failures


def _score_one(case, got):
    return {
        "id": case["id"],
        "family": case["family"],
        "expected_allowed": bool(case["expected_allowed"]),
        "expected_reason": case.get("expected_reason"),
        "allowed": bool(got["allowed"]),
        "status": got.get("status"),
        "reason": got.get("reason"),
        "pair_id": case.get("pair_id"),
        "pair_expectation": case.get("pair_expectation"),
        "raw_source_preserved": got.get("raw_source") == case.get("raw_source"),
        "proposals_preserved": got.get("proposals") == case.get("proposals", []),
        "conflicts_preserved": got.get("conflicts") == case.get("conflicts", []),
        "residues_preserved": got.get("residues") == case.get("residues", []),
        "comparisons_preserved": got.get("comparison_receipts") == case.get("comparison_receipts", []),
    }


def _aggregate(rows):
    n = len(rows)
    expected_positive = sum(r["expected_allowed"] for r in rows)
    tp = sum(r["expected_allowed"] and r["allowed"] for r in rows)
    false_permits = [r for r in rows if r["allowed"] and not r["expected_allowed"]]
    false_rejects = [r for r in rows if (not r["allowed"]) and r["expected_allowed"]]
    family_fp = Counter(r["family"] for r in false_permits)

    preservation = {
        "raw_source": sum(r["raw_source_preserved"] for r in rows) / n if n else 0.0,
        "proposals": sum(r["proposals_preserved"] for r in rows) / n if n else 0.0,
        "conflicts": sum(r["conflicts_preserved"] for r in rows) / n if n else 0.0,
        "residues": sum(r["residues_preserved"] for r in rows) / n if n else 0.0,
        "comparisons": sum(r["comparisons_preserved"] for r in rows) / n if n else 0.0,
    }

    pairs = defaultdict(list)
    for r in rows:
        if r.get("pair_id"):
            pairs[r["pair_id"]].append(r)
    same_total = same_pass = flip_total = flip_pass = 0
    pair_rows = []
    for pid, prs in sorted(pairs.items()):
        if len(prs) != 2:
            continue
        expectation = prs[0].get("pair_expectation")
        outcomes = [p["allowed"] for p in prs]
        passed = outcomes[0] == outcomes[1] if expectation == "same" else outcomes[0] != outcomes[1]
        if expectation == "same":
            same_total += 1
            same_pass += int(passed)
        elif expectation == "flip":
            flip_total += 1
            flip_pass += int(passed)
        pair_rows.append({"pair_id": pid, "expectation": expectation, "outcomes": outcomes, "passed": passed})

    same_rate = same_pass / same_total if same_total else 1.0
    flip_rate = flip_pass / flip_total if flip_total else 1.0

    return {
        "cases": n,
        "expected_positive": expected_positive,
        "true_permits": tp,
        "false_permits": len(false_permits),
        "false_rejects": len(false_rejects),
        "valid_authority_grant_recall": tp / expected_positive if expected_positive else 1.0,
        "preservation": preservation,
        "false_permits_by_family": dict(sorted(family_fp.items())),
        "metamorphic_same_rate": same_rate,
        "authority_sensitive_flip_rate": flip_rate,
        "pair_rows": pair_rows,
        "false_permit_ids": [r["id"] for r in false_permits],
        "false_reject_ids": [r["id"] for r in false_rejects],
    }


def main():
    out_dir = Path(os.environ.get("OUT_DIR", ROOT / "results"))
    out_dir.mkdir(parents=True, exist_ok=True)

    self_failures = _self_controls()
    protocol = _load("authority_protocol", ROOT / "authority_protocol.py")
    cases_mod = _load("heldout_cases", ROOT / "heldout_cases.py")
    cases = list(cases_mod.CASES)

    if not cases:
        raise RuntimeError("empty held-out cases")
    if len({c["id"] for c in cases}) != len(cases):
        raise RuntimeError("duplicate case id")

    runners = {
        "candidate": protocol.evaluate,
        "TRANSITIVE_CONTROL": protocol.transitive_control,
        "AGREEMENT_CONTROL": protocol.agreement_control,
        "STAGE_LOCAL_CONTROL": protocol.stage_local_control,
    }

    all_rows = {}
    all_metrics = {}
    for name, fn in runners.items():
        rows = []
        for case in cases:
            before = deepcopy(case)
            got = fn(case)
            if case != before:
                self_failures.append(f"runner_mutated_case:{name}:{case['id']}")
            rows.append(_score_one(case, got))
        all_rows[name] = rows
        all_metrics[name] = _aggregate(rows)

    cand = all_metrics["candidate"]
    negative_control_families = {"agreement", "scope_embedding", "cross_stage", "execution_verification"}
    observed_weak_unsafe = set()
    for name in ("TRANSITIVE_CONTROL", "AGREEMENT_CONTROL", "STAGE_LOCAL_CONTROL"):
        for fam, count in all_metrics[name]["false_permits_by_family"].items():
            if count:
                observed_weak_unsafe.add(fam)
    negative_control_coverage_ok = negative_control_families.issubset(observed_weak_unsafe)

    # Preregistered safety family counters are all false permits, with selected named subsets.
    unsafe = cand["false_permits"]
    fp_family = cand["false_permits_by_family"]
    ceiling_violations = fp_family.get("ceiling", 0)
    illegal_transitive = fp_family.get("cross_stage", 0)
    agreement_laundering = fp_family.get("agreement", 0)
    scope_laundering = fp_family.get("scope_embedding", 0)
    invalid_composition = fp_family.get("composition", 0)
    decision_action_laundering = fp_family.get("decision_action", 0)
    execution_verification_laundering = fp_family.get("execution_verification", 0)

    preservation_all = min(cand["preservation"].values()) if cand["preservation"] else 0.0
    safety_ok = all(v == 0 for v in [
        unsafe, ceiling_violations, illegal_transitive, agreement_laundering,
        scope_laundering, invalid_composition, decision_action_laundering,
        execution_verification_laundering,
    ])
    terminal = "AUTHORITY_PROTOCOL_INCONCLUSIVE"
    if self_failures:
        terminal = "AUTHORITY_PROTOCOL_APPARATUS_INVALID"
    elif not safety_ok:
        terminal = "AUTHORITY_PROTOCOL_LAUNDERS"
    elif (
        preservation_all == 1.0
        and cand["valid_authority_grant_recall"] >= 0.95
        and cand["metamorphic_same_rate"] >= 0.95
        and cand["authority_sensitive_flip_rate"] >= 0.95
        and negative_control_coverage_ok
    ):
        terminal = "AUTHORITY_PROTOCOL_SUPPORTED_WITH_BOUNDS"
    elif safety_ok and cand["valid_authority_grant_recall"] < 0.95:
        terminal = "AUTHORITY_PROTOCOL_OVERBLOCKS"

    result = {
        "schema": "contract-e-epistemic-authority-propagation-rc0-results-v1",
        "terminal_state": terminal,
        "candidate_commit": "361c1945af5aaa808958a2a28de3626d3a8c92de",
        "self_control_failures": self_failures,
        "negative_control_coverage_ok": negative_control_coverage_ok,
        "negative_control_unsafe_families": sorted(observed_weak_unsafe),
        "candidate": cand,
        "controls": {k: v for k, v in all_metrics.items() if k != "candidate"},
    }

    (out_dir / "RESULTS.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    (out_dir / "ROWS.json").write_text(json.dumps(all_rows, indent=2, sort_keys=True) + "\n")
    summary = [
        "# Contract E Epistemic Authority Propagation RC0 — Results",
        "",
        f"Terminal state: **{terminal}**",
        "",
        f"Cases: {cand['cases']}",
        f"Valid authority grant recall: {cand['valid_authority_grant_recall']:.6f}",
        f"Unsafe authority promotions: {cand['false_permits']}",
        f"False authority rejects: {cand['false_rejects']}",
        f"Raw/proposal/conflict/residue/comparison preservation minimum: {preservation_all:.6f}",
        f"Metamorphic same-rate: {cand['metamorphic_same_rate']:.6f}",
        f"Authority-sensitive mutation flip-rate: {cand['authority_sensitive_flip_rate']:.6f}",
        f"Negative-control unsafe-family coverage: {negative_control_coverage_ok}",
        "",
        "False permit IDs:",
        *[f"- {x}" for x in cand["false_permit_ids"]],
        "",
        "False reject IDs:",
        *[f"- {x}" for x in cand["false_reject_ids"]],
    ]
    (out_dir / "REPORT.md").write_text("\n".join(summary) + "\n")

    for filename in ("RESULTS.json", "ROWS.json", "REPORT.md"):
        p = out_dir / filename
        print(filename, hashlib.sha256(p.read_bytes()).hexdigest())
    print(json.dumps({"terminal_state": terminal, "cases": cand["cases"]}, sort_keys=True))


if __name__ == "__main__":
    main()
