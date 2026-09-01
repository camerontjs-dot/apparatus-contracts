from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path

from sealed_cases import CASES

REQUIRED_OUTPUT_FIELDS = [
    "allowed", "status", "reason", "authority_kind",
    "raw_source", "proposals", "conflicts", "residues", "comparison_receipts",
]
PRESERVED_FIELDS = ["raw_source", "proposals", "conflicts", "residues", "comparison_receipts"]


def _load_impl(path: Path):
    spec = importlib.util.spec_from_file_location("fresh_authority_chain_impl", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import implementation: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    fn = getattr(module, "evaluate", None)
    if not callable(fn):
        raise RuntimeError("implementation does not expose callable evaluate(case: dict)")
    return fn


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _score_output(case, output):
    expected = case["expected"]
    row = {
        "id": case["id"],
        "family": case.get("family"),
        "tags": case.get("tags", []),
        "expected": expected,
        "observed": None,
        "exception": None,
        "missing_fields": [],
        "preservation_failures": [],
        "authority_match": False,
        "exact_contract_match": False,
        "false_permit": False,
        "false_reject": False,
    }
    if not isinstance(output, dict):
        row["exception"] = f"non_dict_output:{type(output).__name__}"
        return row

    row["missing_fields"] = [field for field in REQUIRED_OUTPUT_FIELDS if field not in output]
    row["observed"] = {field: output.get(field) for field in ["allowed", "status", "reason", "authority_kind"]}
    for field in PRESERVED_FIELDS:
        if output.get(field) != case.get(field):
            row["preservation_failures"].append(field)

    row["authority_match"] = all(output.get(field) == expected.get(field) for field in ["allowed", "status", "reason", "authority_kind"])
    row["false_permit"] = expected["allowed"] is False and output.get("allowed") is True
    row["false_reject"] = expected["allowed"] is True and output.get("allowed") is False
    row["exact_contract_match"] = (
        not row["missing_fields"]
        and not row["preservation_failures"]
        and row["authority_match"]
    )
    return row


def _pair_results(rows_by_id):
    groups = defaultdict(list)
    for case in CASES:
        pair = case.get("pair")
        if pair:
            groups[pair["id"]].append((pair, case["id"]))
    results = []
    for pair_id, members in sorted(groups.items()):
        expectation = members[0][0]["expect"]
        observed = [rows_by_id[cid].get("observed", {}).get("allowed") if rows_by_id[cid].get("observed") else None for _, cid in members]
        if len(observed) != 2:
            passed = False
        elif expectation == "same":
            passed = observed[0] is not None and observed[0] == observed[1]
        elif expectation == "flip":
            passed = observed[0] is not None and observed[1] is not None and observed[0] != observed[1]
        else:
            passed = False
        results.append({"pair_id": pair_id, "expectation": expectation, "case_ids": [cid for _, cid in members], "observed_allowed": observed, "passed": passed})
    return results


def evaluate_implementation(implementation: Path, output_dir: Path):
    evaluate = _load_impl(implementation)
    rows = []
    for case in CASES:
        try:
            out = evaluate(deepcopy({k: v for k, v in case.items() if k != "expected"}))
            row = _score_output(case, out)
        except Exception as exc:  # preserve implementation failures as evidence
            row = _score_output(case, None)
            row["exception"] = f"{type(exc).__name__}: {exc}"
        rows.append(row)

    rows_by_id = {row["id"]: row for row in rows}
    pairs = _pair_results(rows_by_id)

    total = len(rows)
    exact = sum(row["exact_contract_match"] for row in rows)
    authority = sum(row["authority_match"] for row in rows)
    false_permits = [row["id"] for row in rows if row["false_permit"]]
    false_rejects = [row["id"] for row in rows if row["false_reject"]]
    exception_ids = [row["id"] for row in rows if row["exception"]]
    preservation_failures = [row["id"] for row in rows if row["preservation_failures"]]
    reason_matches = sum((row.get("observed") or {}).get("reason") == row["expected"]["reason"] for row in rows)
    outcome_matches = sum((row.get("observed") or {}).get("allowed") == row["expected"]["allowed"] for row in rows)
    status_matches = sum((row.get("observed") or {}).get("status") == row["expected"]["status"] for row in rows)
    kind_matches = sum((row.get("observed") or {}).get("authority_kind") == row["expected"]["authority_kind"] for row in rows)
    pair_passes = sum(p["passed"] for p in pairs)

    supported = (
        exact == total
        and authority == total
        and not false_permits
        and not false_rejects
        and not exception_ids
        and not preservation_failures
        and pair_passes == len(pairs)
    )
    scientific_state = "INDEPENDENT_RECOVERABILITY_SUPPORTED" if supported else "INDEPENDENT_RECOVERABILITY_FALSIFIED"
    disposition = "SUPPORTED_FOR_PROMOTION" if supported else "FALSIFIED"

    results = {
        "schema": "contract-e-authority-chain-fresh-rc1-comparison-v1",
        "case_count": total,
        "implementation_path": str(implementation),
        "implementation_sha256": _sha256(implementation),
        "scientific_state": scientific_state,
        "primary_research_disposition": disposition,
        "production_authorization": False,
        "metrics": {
            "exact_contract_match": exact / total,
            "authority_tuple_match": authority / total,
            "allowed_outcome_match": outcome_matches / total,
            "status_match": status_matches / total,
            "authority_kind_match": kind_matches / total,
            "canonical_reason_match": reason_matches / total,
            "preservation_rate": (total - len(preservation_failures)) / total,
            "false_permits": len(false_permits),
            "false_rejects": len(false_rejects),
            "exceptions": len(exception_ids),
            "metamorphic_pairs_passed": pair_passes,
            "metamorphic_pairs_total": len(pairs),
        },
        "false_permit_ids": false_permits,
        "false_reject_ids": false_rejects,
        "exception_ids": exception_ids,
        "preservation_failure_ids": preservation_failures,
        "mismatch_ids": [row["id"] for row in rows if not row["exact_contract_match"]],
        "family_counts": dict(Counter(case.get("family") for case in CASES)),
        "pair_results": pairs,
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "ROWS.json").write_text(json.dumps(rows, indent=2, sort_keys=True) + "\n")
    (output_dir / "RESULTS.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
    report = [
        "# Contract E Authority-Chain Fresh Independent Reproduction RC1 — Comparison",
        "",
        f"Scientific state: **{scientific_state}**",
        f"Primary research disposition: **{disposition}**",
        "",
        f"Cases: {total}",
        f"Exact contract matches: {exact}/{total}",
        f"False permits: {len(false_permits)}",
        f"False rejects: {len(false_rejects)}",
        f"Exceptions: {len(exception_ids)}",
        f"Preservation failures: {len(preservation_failures)}",
        f"Metamorphic pairs: {pair_passes}/{len(pairs)}",
        "",
        "This is a bounded research disposition only. It does not authorize Contract E 1.0.0, production integration, merge, release, Authorization, or execution.",
    ]
    (output_dir / "REPORT.md").write_text("\n".join(report) + "\n")
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--implementation", required=True, type=Path)
    ap.add_argument("--output-dir", required=True, type=Path)
    args = ap.parse_args()
    results = evaluate_implementation(args.implementation, args.output_dir)
    print(json.dumps(results, sort_keys=True))


if __name__ == "__main__":
    main()
