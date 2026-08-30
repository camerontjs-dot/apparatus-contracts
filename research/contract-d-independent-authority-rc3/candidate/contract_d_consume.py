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

def consume(decision: Any, expected: ApplicabilityExpectation) -> dict[str, Any]:
    try:
        validate_decision(decision)
    except ContractDError as exc:
        return {"outcome": "cannot_establish", "reason": exc.code}
    identity = semantic_identity(decision)
    if not _same_exact(decision["input_authority"], expected.input_authority, ("kind", "id", "immutable_id")):
        return {"outcome": "not_applicable", "reason": "input_authority_mismatch", "decision_identity": identity}
    if not _same_exact(decision["policy"], expected.policy, ("id", "version")):
        return {"outcome": "not_applicable", "reason": "policy_mismatch", "decision_identity": identity}
    if not _same_exact(decision["target"], expected.target, ("kind", "id", "content_sha256")):
        return {"outcome": "not_applicable", "reason": "target_mismatch", "decision_identity": identity}
    evaluation = decision["evaluation"]
    if evaluation["state"] == "failed":
        return {"outcome": "evaluation_failed", "decision_identity": identity}
    if evaluation["disposition"] == "hold":
        return {"outcome": "hold", "decision_identity": identity}
    effect = validate_effect(decision["effect"])
    if effect["type"] != expected.requested_operation:
        return {"outcome": "not_applicable", "reason": "requested_operation_mismatch", "decision_identity": identity}
    requested_params = expected.effect_params or {}
    unknown_requested = set(requested_params) - set(effect["params"])
    if unknown_requested:
        return {"outcome": "not_applicable", "reason": "requested_effect_parameter_mismatch", "decision_identity": identity}
    for key, value in requested_params.items():
        if effect["params"].get(key) != value:
            return {"outcome": "not_applicable", "reason": "requested_effect_parameter_mismatch", "decision_identity": identity}
    return {"outcome": "candidate_for_authorization", "decision_identity": identity}
