from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

from hidden_cases import cases

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
REFERENCE_PATH = REPO / "docs/research/contract-e/v1-rc2-dual-state-identity-20260902/candidate/reference.py"

NORMATIVE_FIELDS = [
    "schema",
    "receipt_id",
    "authority_conferring",
    "authorized",
    "request_id",
    "request_sha256",
    "authority_state_claimed_id",
    "authority_state_computed_id",
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
    return {key: value.get(key) for key in NORMATIVE_FIELDS}


def compare(implementation_path: Path):
    reference = load_module(REFERENCE_PATH, "contract_e_v1_rc2_reference")
    implementation = load_module(implementation_path, "contract_e_v1_rc2_fresh_impl")
    if not callable(getattr(implementation, "evaluate", None)):
        raise RuntimeError("fresh implementation must expose evaluate(authority_state: dict, request: dict) -> dict")

    records = []
    false_permits = []
    false_rejects = []
    exceptions = []
    preservation_failures = []
    normative_mismatches = []
    diagnostic_shape_failures = []

    for item in cases():
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

        expected_allowed = expected.get("authorized") is True
        observed_allowed = isinstance(observed, dict) and observed.get("authorized") is True
        if observed_allowed and not expected_allowed:
            false_permits.append(item["id"])
        if expected_allowed and not observed_allowed:
            false_rejects.append(item["id"])

        preservation_ok = isinstance(observed, dict) and observed.get("preserved") == expected.get("preserved")
        if not preservation_ok:
            preservation_failures.append(item["id"])

        diagnostic_shape_ok = (
            isinstance(observed, dict)
            and isinstance(observed.get("diagnostics"), list)
            and all(isinstance(x, str) for x in observed.get("diagnostics", []))
        )
        if not diagnostic_shape_ok:
            diagnostic_shape_failures.append(item["id"])

        records.append({
            "id": item["id"],
            "family": item["family"],
            "tags": item["tags"],
            "expected_authorized": expected_allowed,
            "observed_authorized": observed_allowed,
            "normative_match": normative_match,
            "preservation_ok": preservation_ok,
            "diagnostic_shape_ok": diagnostic_shape_ok,
            "exception": error,
        })

    count = len(records)
    exact = count - len(normative_mismatches)
    result = {
        "schema": "contract-e-v1-rc2-fresh-comparison-v1",
        "case_count": count,
        "normative_exact_matches": exact,
        "normative_mismatch_ids": normative_mismatches,
        "false_permit_ids": false_permits,
        "false_reject_ids": false_rejects,
        "exception_ids": exceptions,
        "preservation_failure_ids": preservation_failures,
        "diagnostic_shape_failure_ids": diagnostic_shape_failures,
        "diagnostic_content_is_normative": False,
        "records": records,
        "scientific_state": (
            "SUPPORTED"
            if not normative_mismatches
            and not exceptions
            and not preservation_failures
            and not diagnostic_shape_failures
            else "FALSIFIED"
        ),
    }
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--implementation", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    result = compare(Path(args.implementation).resolve())
    (out / "RESULTS.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "records"}, indent=2, sort_keys=True))
    if result["scientific_state"] != "SUPPORTED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
