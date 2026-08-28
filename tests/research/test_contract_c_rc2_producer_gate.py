from __future__ import annotations

import copy

from research_contract_c_rc2.producer_gate import (
    ALLOWED_CAUSAL_FORMS,
    CAL_PRODUCTION_SHA,
    EXPECTED_POLICY_SHA256,
    GENERIC_ASSESSMENTS,
    PROFILE_ID,
    canonical_bytes,
    rebuild_result_set_id,
    sha256_bytes,
    stable_id,
    targeted_ablation_matrix,
    validate_candidate,
    weak_candidate_controls,
)


def _policy() -> dict[str, object]:
    return {
        "candidate_admission": 0.4,
        "config_id": "cal-rules-v1.2.0",
        "counterevidence_weight": 0.3,
        "false_caution_detection": True,
        "false_caution_threshold": 0.85,
        "needs_source_detection": True,
        "overstated_detection": True,
        "partial_support": 0.55,
        "require_passage_level_match": True,
        "sourced_support": 0.8,
    }


def _candidate() -> dict[str, object]:
    policy = _policy()
    assert sha256_bytes(canonical_bytes(policy)) == EXPECTED_POLICY_SHA256
    ref = {
        "source_id": "src-a",
        "passage_id": "passage-a",
        "passage_sha256": "sha256:passage-a",
    }
    cid = stable_id(
        "contribution",
        {
            "proposition_id": "claim-a",
            "channel": "support",
            "evidence_ref": ref,
        },
    )
    body = {
        "candidate_profile": PROFILE_ID,
        "input": {
            "contract_b": {
                "contract_version": "1.2.0",
                "bundle_id": "bundle-a",
                "bundle_hash": "sha256:bundle-a",
                "artifact_sha256": "sha256:artifact-a",
                "sha256sums_sha256": "sha256:sums-a",
            }
        },
        "producer": {
            "name": "claim-audit-lab",
            "production_semantic_sha": CAL_PRODUCTION_SHA,
            "engine": "v0.2-lexical",
            "policy": {
                "config_id": "cal-rules-v1.2.0",
                "canonical": policy,
                "sha256": EXPECTED_POLICY_SHA256,
            },
        },
        "execution": {
            "state": "completed",
            "execution_id": "execution:test",
        },
        "propositions": [
            {
                "proposition": {
                    "proposition_id": "claim-a",
                    "text_sha256": "sha256:claim-a",
                },
                "contributions": [
                    {
                        "contribution_id": cid,
                        "channel": "support",
                        "evidence_ref": ref,
                        "terminal_role": "necessary",
                        "measurement_role": "co_maximal",
                    }
                ],
                "measurement": {
                    "kind": "cal_v0_2_aggregate_support_signal",
                    "value": 0.8,
                    "basis_contribution_ids": [cid],
                },
                "generic_assessments": {
                    name: {"state": "not_performed"} for name in GENERIC_ASSESSMENTS
                },
                "conclusion": {
                    "reported_verdict": "supported",
                    "terminal_branch": "supported_score_branch",
                    "causal_form": "single_necessary",
                    "terminal_necessary_contribution_ids": [cid],
                    "terminal_residual_contribution_ids": [],
                    "rule_roles": [],
                },
                "execution": {"state": "completed"},
                "reassessment": {"relation": "original", "prior_result_id": None},
            }
        ],
    }
    return rebuild_result_set_id(body)


def test_reference_candidate_validates() -> None:
    assert validate_candidate(_candidate()) == []


def test_validator_rejects_all_weak_controls() -> None:
    controls = weak_candidate_controls(_candidate())
    assert controls
    assert all(errors for errors in controls.values())


def test_targeted_missing_state_ablation_fails_closed() -> None:
    rows = targeted_ablation_matrix(_candidate())
    assert rows
    assert all(row["validator_rejects"] for row in rows)
    assert all("enforcement only" in row["evidence_rule"] for row in rows)


def test_not_performed_cannot_be_laundered_into_assessment() -> None:
    candidate = copy.deepcopy(_candidate())
    candidate["propositions"][0]["generic_assessments"]["eligibility"] = {
        "state": "performed",
        "value": "eligible",
    }
    candidate = rebuild_result_set_id(candidate)
    errors = validate_candidate(candidate)
    assert any("must remain not_performed" in error for error in errors)


def test_policy_config_name_alone_is_not_identity() -> None:
    candidate = copy.deepcopy(_candidate())
    candidate["producer"]["policy"] = {"config_id": "cal-rules-v1.2.0"}
    candidate = rebuild_result_set_id(candidate)
    errors = validate_candidate(candidate)
    assert any("canonical policy state missing" in error for error in errors)


def test_destination_policy_and_telemetry_are_rejected() -> None:
    authority = copy.deepcopy(_candidate())
    authority["authority_profile"] = "auto"
    authority = rebuild_result_set_id(authority)
    assert any("destination-policy leakage" in error for error in validate_candidate(authority))

    telemetry = copy.deepcopy(_candidate())
    telemetry["propositions"][0]["explanation"] = "debug prose"
    telemetry = rebuild_result_set_id(telemetry)
    assert any("telemetry leakage" in error for error in validate_candidate(telemetry))


def test_causal_form_vocabulary_preserves_multiplicity_classes() -> None:
    assert {
        "single_necessary",
        "independent_sufficient_alternatives",
        "jointly_sufficient",
        "redundant_non_deciding",
    } == ALLOWED_CAUSAL_FORMS


def test_result_set_identity_detects_mutation() -> None:
    candidate = _candidate()
    candidate["propositions"][0]["conclusion"]["reported_verdict"] = "unsupported"
    errors = validate_candidate(candidate)
    assert "result-set identity mismatch" in errors
