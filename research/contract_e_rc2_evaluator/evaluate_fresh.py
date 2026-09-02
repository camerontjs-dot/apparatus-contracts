from __future__ import annotations

import argparse
import importlib.util
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

REQUIRED_KEYS = {
    "schema",
    "receipt_id",
    "authority_conferring",
    "authorized",
    "request_id",
    "request_sha256",
    "claimed_authority_state_id",
    "recomputed_authority_state_id",
    "evaluation_time",
    "subject_id",
    "jurisdiction",
    "authority_basis_id",
    "preserved",
    "diagnostics",
}


def load_module(path: str, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def normative(receipt: dict[str, Any]) -> dict[str, Any]:
    return {k: deepcopy(v) for k, v in receipt.items() if k != "diagnostics"}


def diagnostic_shape_ok(receipt: Any) -> bool:
    if not isinstance(receipt, dict) or set(receipt) != REQUIRED_KEYS:
        return False
    diagnostics = receipt.get("diagnostics")
    return (
        isinstance(diagnostics, list)
        and all(isinstance(x, str) for x in diagnostics)
        and len(diagnostics) == len(set(diagnostics))
    )


def evaluate_module(candidate_path: str, reference_path: str, hidden_cases_path: str) -> dict[str, Any]:
    candidate = load_module(candidate_path, "rc2_candidate_under_test")
    reference = load_module(reference_path, "rc2_frozen_reference")
    hidden = load_module(hidden_cases_path, "rc2_hidden_cases")
    if not callable(getattr(candidate, "evaluate", None)):
        raise RuntimeError("candidate must expose evaluate(authority_state, request)")
    if not callable(getattr(reference, "evaluate", None)):
        raise RuntimeError("reference missing evaluate")

    records = []
    false_permits = []
    false_rejects = []
    normative_mismatches = []
    exceptions = []
    diagnostic_shape_failures = []
    preservation_failures = []
    outputs = {}

    for case in hidden.cases():
        case_id = case["id"]
        try:
            expected = reference.evaluate(deepcopy(case["state"]), deepcopy(case["request"]))
            observed = candidate.evaluate(deepcopy(case["state"]), deepcopy(case["request"]))
        except Exception as exc:
            exceptions.append(case_id)
            records.append({
                "id": case_id,
                "family": case["family"],
                "tags": case.get("tags", []),
                "exception": f"{type(exc).__name__}: {exc}",
                "normative_match": False,
                "diagnostic_shape_ok": False,
                "preservation_ok": False,
            })
            continue

        expected_auth = bool(expected.get("authorized"))
        observed_auth = bool(observed.get("authorized"))
        if observed_auth and not expected_auth:
            false_permits.append(case_id)
        if expected_auth and not observed_auth:
            false_rejects.append(case_id)

        nmatch = normative(observed) == normative(expected)
        if not nmatch:
            normative_mismatches.append(case_id)

        dshape = diagnostic_shape_ok(observed)
        if not dshape:
            diagnostic_shape_failures.append(case_id)

        preserve_ok = (
            isinstance(observed, dict)
            and observed.get("preserved") == expected.get("preserved")
        )
        if not preserve_ok:
            preservation_failures.append(case_id)

        outputs[case_id] = {
            "expected": expected,
            "observed": observed,
        }
        records.append({
            "id": case_id,
            "family": case["family"],
            "tags": case.get("tags", []),
            "expected_authorized": expected_auth,
            "observed_authorized": observed_auth,
            "normative_match": nmatch,
            "diagnostic_shape_ok": dshape,
            "preservation_ok": preserve_ok,
            "exception": None,
        })

    # Cross-case RC2 invariant: same canonical invalid state with two different
    # claimed IDs must preserve the same recomputed identity but different
    # claimed identities and therefore different receipt IDs.
    a = outputs.get("NEG-FORGED-CLAIM-A", {}).get("observed")
    b = outputs.get("NEG-FORGED-CLAIM-B", {}).get("observed")
    cross_case_dual_identity_ok = bool(
        a
        and b
        and a.get("authorized") is False
        and b.get("authorized") is False
        and a.get("claimed_authority_state_id") != b.get("claimed_authority_state_id")
        and a.get("recomputed_authority_state_id") == b.get("recomputed_authority_state_id")
        and a.get("receipt_id") != b.get("receipt_id")
    )

    state = "SUPPORTED" if not (
        false_permits
        or false_rejects
        or normative_mismatches
        or exceptions
        or diagnostic_shape_failures
        or preservation_failures
        or not cross_case_dual_identity_ok
    ) else "FALSIFIED"

    return {
        "scientific_state": state,
        "case_count": len(records),
        "normative_exact_matches": len(records) - len(set(normative_mismatches + exceptions)),
        "normative_mismatch_ids": normative_mismatches,
        "false_permit_ids": false_permits,
        "false_reject_ids": false_rejects,
        "exception_ids": exceptions,
        "diagnostic_shape_failure_ids": diagnostic_shape_failures,
        "preservation_failure_ids": preservation_failures,
        "cross_case_dual_identity_ok": cross_case_dual_identity_ok,
        "records": records,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--reference", required=True)
    parser.add_argument("--hidden-cases", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = evaluate_module(args.candidate, args.reference, args.hidden_cases)
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "records"}, sort_keys=True))
    return 0 if result["scientific_state"] == "SUPPORTED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
