from __future__ import annotations

import argparse
import importlib.util
import json
from copy import deepcopy
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
REFERENCE_PATH = REPO / "docs/research/contract-e/v1-closure-20260902/successor-rc2/candidate/reference.py"
EVALUATOR_PATH = HERE / "evaluate_fresh.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def rehash(reference, receipt):
    out = deepcopy(receipt)
    projection = {k: deepcopy(v) for k, v in out.items() if k not in {"receipt_id", "diagnostics"}}
    out["receipt_id"] = reference.sha256_identity(projection)
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile-results", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    reference = load_module(REFERENCE_PATH, "contract_e_rc2_reference_qualification")
    evaluator = load_module(EVALUATOR_PATH, "contract_e_rc2_evaluator_qualification")

    reference_result = evaluator.compare_callable(reference.evaluate, reference.evaluate)
    reference_ok = (
        reference_result["scientific_state"] == "SUPPORTED"
        and reference_result["normative_exact_matches"] == reference_result["case_count"]
        and not reference_result["false_permit_ids"]
        and not reference_result["false_reject_ids"]
        and not reference_result["exception_ids"]
        and not reference_result["preservation_failure_ids"]
        and not reference_result["diagnostic_shape_failure_ids"]
        and not reference_result["dual_identity_failure_ids"]
    )
    if not reference_ok:
        raise AssertionError("reference does not exactly satisfy evaluator")

    def claimed_only(state, request):
        receipt = reference.evaluate(state, request)
        receipt["recomputed_authority_state_id"] = receipt.get("claimed_authority_state_id")
        return rehash(reference, receipt)

    def recomputed_only(state, request):
        receipt = reference.evaluate(state, request)
        receipt["claimed_authority_state_id"] = receipt.get("recomputed_authority_state_id")
        return rehash(reference, receipt)

    def supporting_confers(state, request):
        receipt = reference.evaluate(state, request)
        if (
            not receipt.get("authorized")
            and isinstance(request, dict)
            and request.get("supporting_artifacts")
        ):
            receipt["authorized"] = True
            receipt["authority_basis_id"] = "weak:supporting-artifact"
        return rehash(reference, receipt)

    def currentness_bypass(state, request):
        receipt = reference.evaluate(state, request)
        if "authority_not_current" in receipt.get("diagnostics", []):
            receipt["authorized"] = True
            receipt["authority_basis_id"] = "weak:historical-authority"
        return rehash(reference, receipt)

    core_controls = {
        "claimed-only-identity-collapse": claimed_only,
        "recomputed-only-identity-collapse": recomputed_only,
        "supporting-artifact-conferral": supporting_confers,
        "currentness-bypass": currentness_bypass,
    }

    core_control_results = {}
    for name, fn in core_controls.items():
        result = evaluator.compare_callable(fn, reference.evaluate)
        caught = (
            result["scientific_state"] == "FALSIFIED"
            and bool(result["normative_mismatch_ids"] or result["false_permit_ids"] or result["dual_identity_failure_ids"])
        )
        core_control_results[name] = {
            "caught": caught,
            "normative_mismatch_ids": result["normative_mismatch_ids"],
            "false_permit_ids": result["false_permit_ids"],
            "dual_identity_failure_ids": result["dual_identity_failure_ids"],
        }
        if not caught:
            raise AssertionError(f"weak core control not caught: {name}")

    # Diagnostic content must remain non-authoritative.
    diagnostic_identity_checks = 0
    for item in evaluator.cases():
        receipt = reference.evaluate(deepcopy(item["state"]), deepcopy(item["request"]))
        mutated = deepcopy(receipt)
        mutated["diagnostics"] = ["qualification-only-diagnostic", item["id"]]
        projection = {k: deepcopy(v) for k, v in mutated.items() if k not in {"receipt_id", "diagnostics"}}
        if reference.sha256_identity(projection) != receipt["receipt_id"]:
            raise AssertionError(f"diagnostic content changed receipt identity: {item['id']}")
        diagnostic_identity_checks += 1

    profile = json.loads(Path(args.profile_results).read_text(encoding="utf-8"))
    if profile.get("status") != "PASS" or profile.get("failed_ids"):
        raise AssertionError("trusted-origin pressure profile is not clean")
    by_id = {row["id"]: row for row in profile["rows"]}

    profile_controls = {
        "self-derived-decision-trust": (
            by_id["O04-weak-derived-decision-anchor-is-fooled"]["observed"] is True
            and by_id["O03-forged-d-rejected-by-external-anchor"]["observed"] is False
        ),
        "self-derived-authority-state-trust": (
            by_id["A04-weak-derived-state-anchor-is-fooled"]["observed"] is True
            and by_id["A03-forged-root-rejected-by-external-anchor"]["observed"] is False
        ),
        "receipt-only-permission": (
            by_id["R01-forged-receipt-fools-receipt-only"]["observed"] is True
            and by_id["R02-fresh-point-of-use-ignores-forged-receipt"]["observed"] is False
        ),
        "historical-receipt-currentness": (
            by_id["M39-old-receipt-was-authorized"]["observed"] is True
            and by_id["M40-fresh-revocation-blocks"]["observed"] is False
        ),
        "execution-intent-substitution": (
            by_id["M26-target-1"]["observed"] is False
        ),
    }
    if not all(profile_controls.values()):
        raise AssertionError(f"trusted-origin weak controls not discriminated: {profile_controls}")

    weak_controls_caught = {
        "claimed-only-identity-collapse": core_control_results["claimed-only-identity-collapse"]["caught"],
        "recomputed-only-identity-collapse": core_control_results["recomputed-only-identity-collapse"]["caught"],
        "supporting-artifact-conferral": core_control_results["supporting-artifact-conferral"]["caught"],
        "self-derived-decision-trust": profile_controls["self-derived-decision-trust"],
        "self-derived-authority-state-trust": profile_controls["self-derived-authority-state-trust"],
        "receipt-only-permission": profile_controls["receipt-only-permission"],
        "historical-receipt-currentness": profile_controls["historical-receipt-currentness"],
        "execution-intent-substitution": profile_controls["execution-intent-substitution"],
    }

    result = {
        "status": "QUALIFIED",
        "fresh_independent_implementation_existed": False,
        "hidden_case_count": reference_result["case_count"],
        "reference_normative_exact_matches": reference_result["normative_exact_matches"],
        "reference_false_permits": reference_result["false_permit_ids"],
        "reference_false_rejects": reference_result["false_reject_ids"],
        "reference_exceptions": reference_result["exception_ids"],
        "reference_preservation_failures": reference_result["preservation_failure_ids"],
        "reference_diagnostic_shape_failures": reference_result["diagnostic_shape_failure_ids"],
        "reference_dual_identity_failures": reference_result["dual_identity_failure_ids"],
        "diagnostic_identity_checks": diagnostic_identity_checks,
        "core_control_details": core_control_results,
        "profile_case_count": profile["case_count"],
        "profile_controls": profile_controls,
        "weak_controls_caught": weak_controls_caught,
        "weak_control_count": len(weak_controls_caught),
    }
    if not all(weak_controls_caught.values()):
        raise AssertionError("one or more required weak controls escaped")

    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
