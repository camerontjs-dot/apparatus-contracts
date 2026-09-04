from __future__ import annotations

import argparse
import importlib.util
import json
from copy import deepcopy
from pathlib import Path

from target_cardinality_cases import extra_cases as target_cardinality_cases

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
REFERENCE_PATH = (
    REPO
    / "docs/research/contract-e/v1-rc3-target-reference-cardinality-successor-20260903/candidate/reference.py"
)
PREDECESSOR_REFERENCE_PATH = (
    REPO
    / "docs/research/contract-e/v1-rc3-exact-currentness-jcs-20260902/candidate/reference.py"
)
PREDECESSOR_HIDDEN_PATH = REPO / "sealed/contract-e-v1-rc3-fresh/hidden_cases.py"
PREDECESSOR_HIDDEN_EXTENSION_PATH = (
    REPO / "sealed/contract-e-v1-rc3-fresh/hidden_cases_reference_identity_extension.py"
)

NORMATIVE_FIELDS = [
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
]


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def projection(value):
    if not isinstance(value, dict):
        return None
    return {key: deepcopy(value.get(key)) for key in NORMATIVE_FIELDS}


def predecessor_hidden_cases(reference) -> list[dict]:
    hidden = load_module(PREDECESSOR_HIDDEN_PATH, "contract_e_rc3_predecessor_hidden")
    extension = load_module(
        PREDECESSOR_HIDDEN_EXTENSION_PATH,
        "contract_e_rc3_predecessor_hidden_extension",
    )
    return hidden.cases(reference) + extension.extra_cases(reference)


def all_hidden_cases(reference) -> list[dict]:
    return predecessor_hidden_cases(reference) + target_cardinality_cases(reference)


def compare(implementation_path: Path) -> dict:
    reference = load_module(REFERENCE_PATH, "contract_e_v1_rc3_target_cardinality_reference")
    implementation = load_module(
        implementation_path, "contract_e_v1_rc3_target_cardinality_fresh_impl"
    )
    if not callable(getattr(implementation, "evaluate", None)):
        raise RuntimeError(
            "fresh implementation must expose evaluate(authority_state: dict, request: dict) -> dict"
        )

    records = []
    false_permits = []
    false_rejects = []
    exceptions = []
    preservation_failures = []
    normative_mismatches = []
    diagnostic_shape_failures = []
    fractional_failures = []
    canonicalization_failures = []
    dual_identity_failures = []
    target_cardinality_failures = []

    hidden = all_hidden_cases(reference)
    for item in hidden:
        expected = reference.evaluate(item["state"], item["request"])
        error = None
        try:
            observed = implementation.evaluate(item["state"], item["request"])
        except Exception as exc:  # noqa: BLE001
            observed = None
            error = f"{type(exc).__name__}: {exc}"
            exceptions.append(item["id"])

        expected_projection = projection(expected)
        observed_projection = projection(observed)
        normative_match = observed_projection == expected_projection
        if not normative_match:
            normative_mismatches.append(item["id"])
            if item["family"] == "fractional-currentness":
                fractional_failures.append(item["id"])
            if item["family"] == "canonicalization":
                canonicalization_failures.append(item["id"])
            if item["family"] == "target-reference-cardinality":
                target_cardinality_failures.append(item["id"])
            if "dual-identity" in item["tags"]:
                dual_identity_failures.append(item["id"])

        expected_allowed = expected.get("authorized") is True
        observed_allowed = isinstance(observed, dict) and observed.get("authorized") is True
        if observed_allowed and not expected_allowed:
            false_permits.append(item["id"])
        if expected_allowed and not observed_allowed:
            false_rejects.append(item["id"])

        preservation_ok = (
            isinstance(observed, dict)
            and observed.get("preserved") == expected.get("preserved")
        )
        if not preservation_ok:
            preservation_failures.append(item["id"])

        diagnostic_shape_ok = (
            isinstance(observed, dict)
            and isinstance(observed.get("diagnostics"), list)
            and all(isinstance(x, str) for x in observed.get("diagnostics", []))
        )
        if not diagnostic_shape_ok:
            diagnostic_shape_failures.append(item["id"])

        records.append(
            {
                "id": item["id"],
                "family": item["family"],
                "tags": item["tags"],
                "expected_authorized": expected_allowed,
                "observed_authorized": observed_allowed,
                "normative_match": normative_match,
                "preservation_ok": preservation_ok,
                "diagnostic_shape_ok": diagnostic_shape_ok,
                "exception": error,
            }
        )

    count = len(records)
    exact = count - len(normative_mismatches)
    supported = not (
        normative_mismatches
        or false_permits
        or false_rejects
        or exceptions
        or preservation_failures
        or diagnostic_shape_failures
    )
    return {
        "schema": "contract-e-v1-rc3-target-cardinality-fresh-comparison-v1",
        "case_count": count,
        "predecessor_case_count": count - len(target_cardinality_cases(reference)),
        "target_cardinality_case_count": len(target_cardinality_cases(reference)),
        "normative_exact_matches": exact,
        "normative_mismatch_ids": normative_mismatches,
        "false_permit_ids": false_permits,
        "false_reject_ids": false_rejects,
        "exception_ids": exceptions,
        "preservation_failure_ids": preservation_failures,
        "diagnostic_shape_failure_ids": diagnostic_shape_failures,
        "fractional_currentness_failure_ids": fractional_failures,
        "canonicalization_failure_ids": canonicalization_failures,
        "dual_identity_failure_ids": dual_identity_failures,
        "target_cardinality_failure_ids": target_cardinality_failures,
        "diagnostic_content_is_normative": False,
        "records": records,
        "scientific_state": "SUPPORTED" if supported else "FALSIFIED",
    }


def predecessor_reference_regression() -> dict:
    predecessor = load_module(
        PREDECESSOR_REFERENCE_PATH, "contract_e_v1_rc3_predecessor_reference_regression"
    )
    successor = load_module(
        REFERENCE_PATH, "contract_e_v1_rc3_successor_reference_regression"
    )
    cases = predecessor_hidden_cases(successor)
    mismatch_ids = []
    for item in cases:
        before = projection(predecessor.evaluate(item["state"], item["request"]))
        after = projection(successor.evaluate(item["state"], item["request"]))
        if before != after:
            mismatch_ids.append(item["id"])
    return {
        "case_count": len(cases),
        "normative_exact_matches": len(cases) - len(mismatch_ids),
        "normative_mismatch_ids": mismatch_ids,
        "state": "PASS" if not mismatch_ids else "FAIL",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--implementation", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    result = compare(Path(args.implementation).resolve())
    regression = predecessor_reference_regression()
    payload = {"comparison": result, "predecessor_reference_regression": regression}
    (out / "RESULTS.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "comparison": {k: v for k, v in result.items() if k != "records"},
                "predecessor_reference_regression": regression,
            },
            indent=2,
            sort_keys=True,
        )
    )
    if result["scientific_state"] != "SUPPORTED" or regression["state"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
