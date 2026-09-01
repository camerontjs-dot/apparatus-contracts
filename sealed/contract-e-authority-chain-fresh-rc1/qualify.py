from __future__ import annotations

import json
from collections import Counter
from copy import deepcopy
from pathlib import Path

from evaluate_fresh import _score_output
from reference import evaluate as reference_evaluate
from sealed_cases import CASES


def _status_flag_control(case):
    idx = {r["id"]: r for r in case.get("receipts", [])}
    req = case["request"]
    deps = [idx.get(rid) for rid in req.get("dependencies", [])]
    if req.get("authority_kind") == "observation":
        return req.get("status") == "established"
    return bool(deps) and all(d and d.get("status") == "established" for d in deps) and (
        req.get("authority_kind") == "comparison" or bool(req.get("basis"))
    )


def _any_basis_control(case):
    req = case["request"]
    basis = req.get("basis", {})
    required = {"subject", "domain", "operation", "scope", "target_class", "current", "valid"}
    return required.issubset(basis) and basis.get("current") is True and basis.get("valid") is True


def _bare_resolution_control(case):
    req = case["request"]
    resolved = set(req.get("resolved_residue_ids", [])) | set(req.get("resolved_conflict_ids", []))
    blocking_residue = any(
        r.get("relevant", True) and r.get("status") in {"unresolved", "contested"} and r["id"] not in resolved
        for r in case.get("residues", [])
    )
    blocking_conflict = any(
        c.get("relevant", True) and c.get("status") in {"unresolved", "contested"} and c["id"] not in resolved
        for c in case.get("conflicts", [])
    )
    if req.get("authority_kind") in {"semantic", "composition", "decision", "action", "verification"} and (blocking_residue or blocking_conflict):
        return False
    idx = {r["id"]: r for r in case.get("receipts", [])}
    deps = [idx.get(rid) for rid in req.get("dependencies", [])]
    return bool(req.get("basis")) and (not deps or all(d and d.get("status") == "established" for d in deps))


def _control_false_permits(control, tag):
    ids = []
    for case in CASES:
        if tag not in case.get("tags", []):
            continue
        if case["expected"]["allowed"] is False and control(case) is True:
            ids.append(case["id"])
    return ids


def qualify(output_dir: Path):
    failures = []
    reference_rows = []
    for case in CASES:
        input_case = deepcopy({k: v for k, v in case.items() if k != "expected"})
        out = reference_evaluate(input_case)
        row = _score_output(case, out)
        reference_rows.append(row)
        if not row["exact_contract_match"]:
            failures.append(f"reference_mismatch:{case['id']}")

    # Evaluator self-controls.
    negative_case = next(case for case in CASES if case["expected"]["allowed"] is False)
    positive_case = next(case for case in CASES if case["expected"]["allowed"] is True)

    neg_ref = reference_evaluate(deepcopy({k: v for k, v in negative_case.items() if k != "expected"}))
    unsafe = deepcopy(neg_ref)
    unsafe["allowed"] = True
    unsafe["status"] = "established"
    unsafe["authority_kind"] = negative_case["request"].get("authority_kind")
    unsafe_row = _score_output(negative_case, unsafe)
    if not unsafe_row["false_permit"]:
        failures.append("self_control_false_permit_not_detected")

    pos_ref = reference_evaluate(deepcopy({k: v for k, v in positive_case.items() if k != "expected"}))
    reject = deepcopy(pos_ref)
    reject["allowed"] = False
    reject["status"] = "insufficient_authority"
    reject["authority_kind"] = None
    reject_row = _score_output(positive_case, reject)
    if not reject_row["false_reject"]:
        failures.append("self_control_false_reject_not_detected")

    damaged = deepcopy(pos_ref)
    damaged["raw_source"] = {"tampered": True}
    damaged_row = _score_output(positive_case, damaged)
    if "raw_source" not in damaged_row["preservation_failures"]:
        failures.append("self_control_preservation_not_detected")

    status_fp = _control_false_permits(_status_flag_control, "status_forge")
    basis_fp = _control_false_permits(_any_basis_control, "nonconferring_basis_attack")
    bare_fp = _control_false_permits(_bare_resolution_control, "unauthorized_resolution_attack")
    if not status_fp:
        failures.append("status_flag_control_not_discriminated")
    if not basis_fp:
        failures.append("any_basis_control_not_discriminated")
    if not bare_fp:
        failures.append("bare_resolution_control_not_discriminated")

    # Coverage and pair integrity.
    kinds = Counter(case["request"].get("authority_kind") for case in CASES)
    positive_kinds = Counter(case["request"].get("authority_kind") for case in CASES if case["expected"]["allowed"] is True)
    negative_kinds = Counter(case["request"].get("authority_kind") for case in CASES if case["expected"]["allowed"] is False)
    for kind in ["observation", "measurement", "semantic", "comparison", "resolution", "composition", "decision", "action", "verification"]:
        if positive_kinds[kind] == 0 or negative_kinds[kind] == 0:
            failures.append(f"coverage_missing_positive_or_negative:{kind}")

    pair_groups = {}
    for case in CASES:
        pair = case.get("pair")
        if pair:
            pair_groups.setdefault(pair["id"], []).append(case)
    for pair_id, members in pair_groups.items():
        if len(members) != 2:
            failures.append(f"pair_cardinality:{pair_id}")
            continue
        expectation = members[0]["pair"]["expect"]
        vals = [m["expected"]["allowed"] for m in members]
        if expectation == "same" and vals[0] != vals[1]:
            failures.append(f"pair_expected_same_invalid:{pair_id}")
        if expectation == "flip" and vals[0] == vals[1]:
            failures.append(f"pair_expected_flip_invalid:{pair_id}")

    result = {
        "schema": "contract-e-authority-chain-fresh-rc1-sealed-evaluator-qualification-v1",
        "case_count": len(CASES),
        "reference_exact_matches": sum(row["exact_contract_match"] for row in reference_rows),
        "expected_positive": sum(case["expected"]["allowed"] is True for case in CASES),
        "expected_negative": sum(case["expected"]["allowed"] is False for case in CASES),
        "request_kind_counts": dict(kinds),
        "status_flag_control_false_permits": status_fp,
        "any_basis_control_false_permits": basis_fp,
        "bare_resolution_control_false_permits": bare_fp,
        "pair_count": len(pair_groups),
        "failures": failures,
        "qualified": not failures,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "QUALIFICATION.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    if failures:
        raise SystemExit("sealed evaluator qualification failed: " + "; ".join(failures))
    print(json.dumps(result, sort_keys=True))
    return result


if __name__ == "__main__":
    qualify(Path("sealed/contract-e-authority-chain-fresh-rc1/qualification"))
