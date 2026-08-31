from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from contract_d_core import ContractDError, semantic_identity, validate_decision, validate_effect


@dataclass(frozen=True)
class ApplicabilityExpectation:
    input_authority: dict[str, str]
    policy: dict[str, str]
    target: dict[str, str]
    requested_operation: str
    effect_params: dict[str, Any] | None = None


def _same_exact(actual: dict[str, Any], expected: dict[str, Any], keys: tuple[str, ...]) -> bool:
    return all(actual.get(key) == expected.get(key) for key in keys)


def _exact_string_mapping(value: Any, keys: set[str]) -> bool:
    return (
        isinstance(value, dict)
        and set(value) == keys
        and all(isinstance(value[key], str) and value[key] for key in keys)
    )


def _valid_expectation(expected: Any) -> bool:
    if not isinstance(expected, ApplicabilityExpectation):
        return False
    if not _exact_string_mapping(expected.input_authority, {"kind", "id", "immutable_id"}):
        return False
    if not _exact_string_mapping(expected.policy, {"id", "version"}):
        return False
    if not _exact_string_mapping(expected.target, {"kind", "id", "content_sha256"}):
        return False
    if not isinstance(expected.requested_operation, str) or not expected.requested_operation:
        return False
    if expected.effect_params is not None:
        if not isinstance(expected.effect_params, dict):
            return False
        if not all(isinstance(key, str) for key in expected.effect_params):
            return False
    return True


def consume(decision: Any, expected: ApplicabilityExpectation) -> dict[str, Any]:
    try:
        validate_decision(decision)
        identity = semantic_identity(decision)
    except ContractDError as exc:
        return {"outcome": "cannot_establish", "reason": exc.code}
    except Exception:
        return {"outcome": "cannot_establish", "reason": "controlled_runtime_failure"}

    if not _valid_expectation(expected):
        return {
            "outcome": "cannot_establish",
            "reason": "invalid_expectation",
            "decision_identity": identity,
        }

    if not _same_exact(
        decision["input_authority"],
        expected.input_authority,
        ("kind", "id", "immutable_id"),
    ):
        return {
            "outcome": "not_applicable",
            "reason": "input_authority_mismatch",
            "decision_identity": identity,
        }
    if not _same_exact(decision["policy"], expected.policy, ("id", "version")):
        return {
            "outcome": "not_applicable",
            "reason": "policy_mismatch",
            "decision_identity": identity,
        }
    if not _same_exact(
        decision["target"],
        expected.target,
        ("kind", "id", "content_sha256"),
    ):
        return {
            "outcome": "not_applicable",
            "reason": "target_mismatch",
            "decision_identity": identity,
        }

    evaluation = decision["evaluation"]
    if evaluation["state"] == "failed":
        return {"outcome": "evaluation_failed", "decision_identity": identity}

    try:
        effect = validate_effect(decision["effect"])
    except ContractDError as exc:
        return {
            "outcome": "cannot_establish",
            "reason": exc.code,
            "decision_identity": identity,
        }

    if effect["type"] != expected.requested_operation:
        return {
            "outcome": "not_applicable",
            "reason": "requested_operation_mismatch",
            "decision_identity": identity,
        }

    requested = {} if expected.effect_params is None else expected.effect_params
    if any(
        key not in effect["params"] or effect["params"][key] != value
        for key, value in requested.items()
    ):
        return {
            "outcome": "not_applicable",
            "reason": "requested_effect_parameter_mismatch",
            "decision_identity": identity,
        }

    if evaluation["disposition"] == "hold":
        return {"outcome": "hold", "decision_identity": identity}
    return {"outcome": "candidate_for_authorization", "decision_identity": identity}
