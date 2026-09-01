from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _self_controls():
    failures = []
    fake = [{"expected_allowed": False, "allowed": True}]
    if sum(r["allowed"] and not r["expected_allowed"] for r in fake) != 1:
        failures.append("false_permit_count")
    fake = [{"expected_allowed": True, "allowed": False}]
    if sum(r["allowed"] and not r["expected_allowed"] for r in fake) != 0:
        failures.append("false_reject_safety")
    if {"raw_source": "a", "proposals": [1]} == {"raw_source": "b", "proposals": [1]}:
        failures.append("preservation_detection")
    if not (True == True and True != False):
        failures.append("pair_logic")
    tagged = [{"expected_allowed": False, "allowed": False, "tags": ["x"]}, {"expected_allowed": False, "allowed": True, "tags": []}]
    denom = [r for r in tagged if "x" in r["tags"] and not r["expected_allowed"]]
    if sum(not r["allowed"] for r in denom) / len(denom) != 1.0:
        failures.append("tag_rate_logic")
    return failures


def _row(case, got):
    return {
        "id": case["id"],
        "family": case["family"],
        "tags": list(case.get("tags", [])),
        "expected_allowed": bool(case["expected_allowed"]),
        "allowed": bool(got["allowed"]),
        "reason": got.get("reason"),
        "pair_id": case.get("pair_id"),
        "pair_expectation": case.get("pair_expectation"),
        "raw_source_preserved": got.get("raw_source") == case.get("raw_source"),
        "proposals_preserved": got.get("proposals") == case.get("proposals", []),
        "conflicts_preserved": got.get("conflicts") == case.get("conflicts", []),
        "residues_preserved": got.get("residues") == case.get("residues", []),
        "comparisons_preserved": got.get("comparison_receipts") == case.get("comparison_receipts", []),
    }


def _rate(rows, tag, want_allowed):
    xs = [r for r in rows if tag in r["tags"] and r["expected_allowed"] is want_allowed]
    if not xs:
        return None
    if want_allowed:
        return sum(r["allowed"] for r in xs) / len(xs)
    return sum(not r["allowed"] for r in xs) / len(xs)


def _aggregate(rows):
    positives = [r for r in rows if r["expected_allowed"]]
    fps = [r for r in rows if r["allowed"] and not r["expected_allowed"]]
    fns = [r for r in rows if not r["allowed"] and r["expected_allowed"]]
    preservation = {
        k: sum(r[k] for r in rows) / len(rows)
        for k in ("raw_source_preserved", "proposals_preserved", "conflicts_preserved", "residues_preserved", "comparisons_preserved")
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
        exp = prs[0].get("pair_expectation")
        outs = [p["allowed"] for p in prs]
        passed = outs[0] == outs[1] if exp == "same" else outs[0] != outs[1]
        if exp == "same":
            same_total += 1; same_pass += int(passed)
        elif exp == "flip":
            flip_total += 1; flip_pass += int(passed)
        pair_rows.append({"pair_id": pid, "expectation": exp, "outcomes": outs, "passed": passed})
    return {
        "cases": len(rows),
        "expected_positive": len(positives),
        "true_permits": sum(r["allowed"] for r in positives),
        "false_permits": len(fps),
        "false_rejects": len(fns),
        "false_permit_ids": [r["id"] for r in fps],
        "false_reject_ids": [r["id"] for r in fns],
        "valid_authority_grant_recall": sum(r["allowed"] for r in positives) / len(positives) if positives else 1.0,
        "preservation": preservation,
        "recursive_lineage_attack_rejection": _rate(rows, "recursive_lineage_attack", False),
        "cycle_attack_rejection": _rate(rows, "cycle_attack", False),
        "nonconferring_basis_rejection": _rate(rows, "nonconferring_basis_attack", False),
        "unauthorized_resolution_rejection": _rate(rows, "unauthorized_resolution_attack", False),
        "valid_resolution_acceptance": _rate(rows, "valid_resolution", True),
        "rc0_safety_regression_rejection": _rate(rows, "rc0_safety_regression", False),
        "metamorphic_same_rate": same_pass / same_total if same_total else 1.0,
        "authority_sensitive_flip_rate": flip_pass / flip_total if flip_total else 1.0,
        "pair_rows": pair_rows,
    }


def main():
    out = Path(os.environ.get("OUT_DIR", ROOT / "results")); out.mkdir(parents=True, exist_ok=True)
    failures = _self_controls()
    proto = _load("authority_chain", ROOT / "authority_chain.py")
    cohort = _load("heldout_cases", ROOT / "heldout_cases.py")
    cases = list(cohort.CASES)
    if not cases or len({c["id"] for c in cases}) != len(cases):
        failures.append("case_identity")

    runners = {
        "candidate": proto.evaluate,
        "STATUS_FLAG_CONTROL": proto.status_flag_control,
        "BARE_RESOLUTION_ID_CONTROL": proto.bare_resolution_id_control,
        "ANY_BASIS_CONTROL": proto.any_basis_control,
    }
    rows_by = {}
    metrics = {}
    for name, fn in runners.items():
        rows = []
        for c in cases:
            before = deepcopy(c)
            got = fn(c)
            if c != before:
                failures.append(f"case_mutation:{name}:{c['id']}")
            rows.append(_row(c, got))
        rows_by[name] = rows
        metrics[name] = _aggregate(rows)

    cand = metrics["candidate"]
    controls_ok = (
        any(r["allowed"] and not r["expected_allowed"] and "recursive_lineage_attack" in r["tags"] for r in rows_by["STATUS_FLAG_CONTROL"])
        and any(r["allowed"] and not r["expected_allowed"] and "unauthorized_resolution_attack" in r["tags"] for r in rows_by["BARE_RESOLUTION_ID_CONTROL"])
        and any(r["allowed"] and not r["expected_allowed"] and "nonconferring_basis_attack" in r["tags"] for r in rows_by["ANY_BASIS_CONTROL"])
    )
    preservation_min = min(cand["preservation"].values())
    required_rates = [
        cand["recursive_lineage_attack_rejection"], cand["cycle_attack_rejection"],
        cand["nonconferring_basis_rejection"], cand["unauthorized_resolution_rejection"],
        cand["rc0_safety_regression_rejection"],
    ]
    terminal = "AUTHORITY_CHAIN_PROTOCOL_INCONCLUSIVE"
    if failures:
        terminal = "AUTHORITY_CHAIN_PROTOCOL_APPARATUS_INVALID"
    elif cand["false_permits"] > 0:
        terminal = "AUTHORITY_CHAIN_PROTOCOL_LAUNDERS"
    elif cand["valid_authority_grant_recall"] < 0.95 or (cand["valid_resolution_acceptance"] is not None and cand["valid_resolution_acceptance"] < 0.95):
        terminal = "AUTHORITY_CHAIN_PROTOCOL_OVERBLOCKS"
    elif (
        preservation_min == 1.0 and all(x == 1.0 for x in required_rates if x is not None)
        and cand["valid_resolution_acceptance"] is not None and cand["valid_resolution_acceptance"] >= 0.95
        and cand["metamorphic_same_rate"] >= 0.95 and cand["authority_sensitive_flip_rate"] >= 0.95
        and controls_ok
    ):
        terminal = "AUTHORITY_CHAIN_PROTOCOL_SUPPORTED_WITH_BOUNDS"

    result = {
        "schema": "contract-e-epistemic-authority-propagation-rc0b-results-v1",
        "terminal_state": terminal,
        "candidate_freeze": "7146b946989fab8c4eaef48ef9c6c7d39e21ada2",
        "self_control_failures": failures,
        "targeted_negative_controls_ok": controls_ok,
        "candidate": cand,
        "controls": {k:v for k,v in metrics.items() if k != "candidate"},
    }
    (out/"RESULTS.json").write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    (out/"ROWS.json").write_text(json.dumps(rows_by, indent=2, sort_keys=True)+"\n")
    lines = [
        "# Contract E Epistemic Authority Propagation RC0B — Results", "",
        f"Terminal state: **{terminal}**", "",
        f"Cases: {cand['cases']}",
        f"Valid authority recall: {cand['valid_authority_grant_recall']:.6f}",
        f"Unsafe authority promotions: {cand['false_permits']}",
        f"False rejects: {cand['false_rejects']}",
        f"Recursive-lineage rejection: {cand['recursive_lineage_attack_rejection']}",
        f"Cycle rejection: {cand['cycle_attack_rejection']}",
        f"Non-conferring-basis rejection: {cand['nonconferring_basis_rejection']}",
        f"Unauthorized-resolution rejection: {cand['unauthorized_resolution_rejection']}",
        f"Valid-resolution acceptance: {cand['valid_resolution_acceptance']}",
        f"RC0 safety regression rejection: {cand['rc0_safety_regression_rejection']}",
        f"Preservation minimum: {preservation_min:.6f}",
        f"Metamorphic same: {cand['metamorphic_same_rate']:.6f}",
        f"Authority flip: {cand['authority_sensitive_flip_rate']:.6f}",
        f"Targeted negative controls unsafe as intended: {controls_ok}", "",
        "False permits:", *[f"- {x}" for x in cand["false_permit_ids"]], "",
        "False rejects:", *[f"- {x}" for x in cand["false_reject_ids"]],
    ]
    (out/"REPORT.md").write_text("\n".join(lines)+"\n")
    for f in ("RESULTS.json","ROWS.json","REPORT.md"):
        p=out/f; print(f, hashlib.sha256(p.read_bytes()).hexdigest())
    print(json.dumps({"terminal_state":terminal,"cases":cand["cases"]}, sort_keys=True))

if __name__ == "__main__":
    main()
