from __future__ import annotations

import importlib
import sys
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

CANDIDATE_DIR = Path(__file__).resolve().parent / "candidate"
if str(CANDIDATE_DIR) not in sys.path:
    sys.path.insert(0, str(CANDIDATE_DIR))

from reference import (  # noqa: E402
    REQUEST_SCHEMA,
    authority_state_identity,
    evaluate,
    reference_identity,
    sha256_identity,
)


class ProfileError(ValueError):
    pass


@dataclass(frozen=True)
class TrustedBindings:
    decision_identity: str
    authority_state_identity: str


EXECUTION_INTENT_KEYS = {
    "schema",
    "executable_sha256",
    "entry_point",
    "arguments",
    "input_identities",
    "environment_constraints",
    "side_effect_targets",
}


def load_contract_d(contract_d_root: str):
    root = str(Path(contract_d_root).resolve())
    if root not in sys.path:
        sys.path.insert(0, root)
    core = importlib.import_module("validators.contract_d_core")
    consume_mod = importlib.import_module("validators.contract_d_consume")
    return core, consume_mod


def execution_intent_identity(intent: dict[str, Any]) -> str:
    if not isinstance(intent, dict) or set(intent) != EXECUTION_INTENT_KEYS:
        raise ProfileError("invalid_execution_intent_shape")
    if intent["schema"] != "execution-intent-candidate-v1":
        raise ProfileError("invalid_execution_intent_schema")
    if not isinstance(intent["executable_sha256"], str) or not intent["executable_sha256"].startswith("sha256:"):
        raise ProfileError("invalid_executable_identity")
    if not isinstance(intent["entry_point"], str) or not intent["entry_point"]:
        raise ProfileError("invalid_entry_point")
    if not isinstance(intent["arguments"], list):
        raise ProfileError("invalid_arguments")
    if not isinstance(intent["input_identities"], list) or not all(isinstance(x, str) and x for x in intent["input_identities"]):
        raise ProfileError("invalid_input_identities")
    if not isinstance(intent["environment_constraints"], dict):
        raise ProfileError("invalid_environment_constraints")
    if not isinstance(intent["side_effect_targets"], list) or not all(isinstance(x, str) and x for x in intent["side_effect_targets"]):
        raise ProfileError("invalid_side_effect_targets")
    return sha256_identity(intent)


def immutable_ref(ref_id: str, kind: str, version: str | None, immutable_id: str) -> dict[str, Any]:
    return {
        "ref_id": ref_id,
        "kind": kind,
        "version": version,
        "immutable_id": immutable_id,
        "identity_sha256": reference_identity(kind, version, immutable_id),
    }


def decision_support_reference(decision_identity: str) -> dict[str, Any]:
    return immutable_ref("D", "contract_d_decision", "1.0.0", decision_identity)


def _check_trusted_authority_state(authority_state: dict[str, Any], trusted: TrustedBindings) -> str:
    try:
        recomputed = authority_state_identity(authority_state)
    except Exception as exc:
        raise ProfileError("authority_state_not_canonicalizable") from exc
    if recomputed != trusted.authority_state_identity:
        raise ProfileError("untrusted_authority_state_identity")
    return recomputed


def _check_decision(
    decision: dict[str, Any],
    expected: Any,
    trusted: TrustedBindings,
    contract_d_root: str,
) -> tuple[str, dict[str, Any]]:
    core, consume_mod = load_contract_d(contract_d_root)
    try:
        core.validate_decision(decision)
        identity = core.semantic_identity(decision)
    except core.ContractDError as exc:
        raise ProfileError(f"invalid_contract_d:{exc.code}") from exc
    if identity != trusted.decision_identity:
        raise ProfileError("untrusted_decision_identity")
    outcome = consume_mod.consume(decision, expected)
    if outcome.get("outcome") != "candidate_for_authorization":
        raise ProfileError(f"decision_not_candidate:{outcome.get('outcome')}")
    if outcome.get("decision_identity") != identity:
        raise ProfileError("decision_identity_consumer_disagreement")
    return identity, outcome


def _bind_decision_operation(expected: Any, jurisdiction: dict[str, str]) -> None:
    requested_operation = getattr(expected, "requested_operation", None)
    if not isinstance(requested_operation, str) or not requested_operation:
        raise ProfileError("invalid_requested_operation_binding")
    if jurisdiction.get("operation") != requested_operation:
        raise ProfileError("decision_operation_authorization_mismatch")


def build_authorization_request(
    *,
    authority_state: dict[str, Any],
    decision_identity: str,
    subject_id: str,
    evaluation_time: str,
    jurisdiction: dict[str, str],
    target_reference: dict[str, Any],
    conflicts: list[dict[str, Any]] | None = None,
    residues: list[dict[str, Any]] | None = None,
    prior_receipts: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    references = [deepcopy(target_reference), decision_support_reference(decision_identity)]
    supporting = [
        {
            "id": "support:decision",
            "artifact_type": "contract_d_candidate_for_authorization",
            "ref_id": "D",
        }
    ]
    for index, prior in enumerate(prior_receipts or []):
        prior_id = prior.get("receipt_id") if isinstance(prior, dict) else None
        if not isinstance(prior_id, str) or not prior_id:
            raise ProfileError("invalid_prior_receipt_reference")
        local_id = f"R{index}"
        references.append(immutable_ref(local_id, "authorization_receipt", None, prior_id))
        supporting.append(
            {
                "id": f"support:prior-receipt:{index}",
                "artifact_type": "prior_authorization_receipt",
                "ref_id": local_id,
            }
        )

    return {
        "schema": REQUEST_SCHEMA,
        "request_id": f"request:{decision_identity}:{subject_id}:{evaluation_time}",
        "authority_state_id": authority_state["authority_state_id"],
        "evaluation_time": evaluation_time,
        "subject_id": subject_id,
        "jurisdiction": deepcopy(jurisdiction),
        "references": references,
        "supporting_artifacts": supporting,
        "conflicts": deepcopy(conflicts or []),
        "residues": deepcopy(residues or []),
    }


def authorize_at_point_of_use(
    *,
    decision: dict[str, Any],
    expected: Any,
    trusted: TrustedBindings,
    contract_d_root: str,
    authority_state: dict[str, Any],
    subject_id: str,
    evaluation_time: str,
    jurisdiction: dict[str, str],
    target_reference: dict[str, Any],
    conflicts: list[dict[str, Any]] | None = None,
    residues: list[dict[str, Any]] | None = None,
    prior_receipts: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    decision_identity, d_outcome = _check_decision(decision, expected, trusted, contract_d_root)
    _bind_decision_operation(expected, jurisdiction)
    _check_trusted_authority_state(authority_state, trusted)
    request = build_authorization_request(
        authority_state=authority_state,
        decision_identity=decision_identity,
        subject_id=subject_id,
        evaluation_time=evaluation_time,
        jurisdiction=jurisdiction,
        target_reference=target_reference,
        conflicts=conflicts,
        residues=residues,
        prior_receipts=prior_receipts,
    )
    receipt = evaluate(authority_state, request)
    return {
        "permitted": bool(receipt.get("authorized")),
        "decision_identity": decision_identity,
        "decision_outcome": d_outcome["outcome"],
        "request": request,
        "receipt": receipt,
    }


def human_handoff(**kwargs) -> dict[str, Any]:
    result = authorize_at_point_of_use(**kwargs)
    if not result["permitted"]:
        return {"handoff_created": False, "authorization": result}
    request = result["request"]
    return {
        "handoff_created": True,
        "authority_conferring": False,
        "subject_id": request["subject_id"],
        "jurisdiction": deepcopy(request["jurisdiction"]),
        "decision_identity": result["decision_identity"],
        "authorization_receipt_id": result["receipt"]["receipt_id"],
        "authorization": result,
    }


def machine_gate(*, execution_intent: dict[str, Any], **kwargs) -> dict[str, Any]:
    intent_id = execution_intent_identity(execution_intent)
    expected_target = immutable_ref("TARGET", "execution_intent", "1", intent_id)
    if kwargs.get("target_reference") != expected_target:
        return {
            "execution_permitted": False,
            "reason": "execution_intent_target_binding_mismatch",
            "execution_intent_identity": intent_id,
        }
    result = authorize_at_point_of_use(**kwargs)
    return {
        "execution_permitted": bool(result["permitted"]),
        "execution_occurred": False,
        "execution_intent_identity": intent_id,
        "authorization": result,
    }
