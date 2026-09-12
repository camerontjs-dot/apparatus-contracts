"""Synthesize the RC0 result while preserving the first evaluator deviation."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from validators import contract_c as released_c

SCHEMA = "contract-c-surface-necessity-rc0-final-v1"
KNOWN_INVALID_FIRST_EVALUATOR_CHECKS = {
    "attacker_chosen_new_digest_is_not_authority",
    "internal_receipt_cannot_authorize_coherent_tamper",
}


def execute(out: Path) -> dict[str, object]:
    first = json.loads((out / "EVALUATION.json").read_text(encoding="utf-8"))
    discriminator = json.loads(
        (out / "BINDING_DISCRIMINATOR.json").read_text(encoding="utf-8")
    )

    first_failures = set(first["core_failures"])
    unexpected_first_failures = sorted(first_failures - KNOWN_INVALID_FIRST_EVALUATOR_CHECKS)
    missing_expected_deviation = sorted(KNOWN_INVALID_FIRST_EVALUATOR_CHECKS - first_failures)

    corrected_binding_pass = bool(discriminator["passed"])
    scientific_checks_except_invalid_mutation = {
        key: value
        for key, value in first["checks"].items()
        if key not in KNOWN_INVALID_FIRST_EVALUATOR_CHECKS
    }
    remaining_checks_pass = all(scientific_checks_except_invalid_mutation.values())

    supported = (
        not unexpected_first_failures
        and not missing_expected_deviation
        and remaining_checks_pass
        and corrected_binding_pass
    )

    result: dict[str, object] = {
        "schema": SCHEMA,
        "research_disposition": (
            "SUPPORTED_MINIMAL_IN_BAND_INVARIANTS_WITH_SIDECAR_RESEARCH_VESSEL"
            if supported
            else "INCONCLUSIVE_SURFACE_NECESSITY"
        ),
        "preserved_deviation": {
            "run_id": "34695162889",
            "job_id": "103557287278",
            "classification": "EVALUATOR_CONSTRUCTION_INVALID",
            "detail": (
                "The first external-authority mutation changed one causal member to residual "
                "while retaining independent_sufficient_alternatives, creating an invalid "
                "one-causal-member shape. The internal verifier therefore rejected semantic "
                "invalidity before the intended external-authority discriminator was reached."
            ),
            "observed_failed_checks": sorted(first_failures),
            "unexpected_failed_checks": unexpected_first_failures,
        },
        "corrected_discriminator": {
            "passed": corrected_binding_pass,
            "checks": discriminator["checks"],
            "interpretation": discriminator["interpretation"],
        },
        "all_other_first_evaluator_checks_pass": remaining_checks_pass,
        "classification": first["classification"],
        "preregistered_expectation_falsifications": first[
            "preregistered_expectation_falsifications"
        ],
        "positive_shape_validation": first["positive_shape_validation"],
        "in_band_reference": first["in_band_reference"],
        "important_observations": first["important_observations"],
        "interpretation": {
            **first["interpretation"],
            "research_vessel_supported": supported,
            "sidecar_is_useful_as_research_vessel": supported,
            "first_evaluator_failure_is_scientific_falsification": False,
            "member_id_preregistered_integrity_expectation_survived": False,
            "member_id_observed_classification": first["classification"]["member_id"],
            "external_object_authority_requires_independent_expected_binding": True,
            "released_contract_c_1_0_mutated": False,
            "contract_c_successor_version_selected": False,
            "promotion_authorized": False,
        },
    }
    (out / "FINAL_EVALUATION.json").write_bytes(released_c.canonical_bytes(result))
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = execute(args.out)
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["research_disposition"] != (
        "SUPPORTED_MINIMAL_IN_BAND_INVARIANTS_WITH_SIDECAR_RESEARCH_VESSEL"
    ):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
