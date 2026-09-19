from __future__ import annotations

import importlib.util
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
SUCCESSOR_DIR = REPO / "docs/research/contract-e/v1-rc3-target-reference-cardinality-successor-20260903/candidate"
PREDECESSOR_PROFILE_PATH = REPO / "docs/research/contract-e/v1-rc3-exact-currentness-jcs-20260902/integration_profile.py"

ERS_REPOSITORY = "camerontjs-dot/epistemic-research-system"
ERS_BASELINE_COMMIT = "0038ae3f16894e96f9aaf45ffe3bc93a6059da2c"
ERS_PRINCIPAL = "agent:epistemic-auditor"
ERS_EFFECT_TYPE = "epistemic_audit.stage_pending_review"
ERS_EFFECT_VERSION = "1"
ERS_SCOPE = "claim"
ERS_TARGET_CLASS = "execution_intent"
PENDING_REVIEW_ROOT = "20_live/epistemic-audit/pending-review"

_ref_spec = importlib.util.spec_from_file_location("contract_e_rc3_target_cardinality_reference", SUCCESSOR_DIR / "reference.py")
if _ref_spec is None or _ref_spec.loader is None:
    raise RuntimeError("cannot load Contract E RC3 target-cardinality reference")
successor_reference = importlib.util.module_from_spec(_ref_spec)
sys.modules[_ref_spec.name] = successor_reference
_ref_spec.loader.exec_module(successor_reference)

_profile_spec = importlib.util.spec_from_file_location("contract_e_rc3_integration_profile", PREDECESSOR_PROFILE_PATH)
if _profile_spec is None or _profile_spec.loader is None:
    raise RuntimeError("cannot load Contract E RC3 integration profile")
integration_profile = importlib.util.module_from_spec(_profile_spec)
sys.modules[_profile_spec.name] = integration_profile
_profile_spec.loader.exec_module(integration_profile)

for _name in ("REQUEST_SCHEMA", "authority_state_identity", "evaluate", "reference_identity", "sha256_identity"):
    setattr(integration_profile, _name, getattr(successor_reference, _name))


def install_research_effect_profile(contract_d_root: Path) -> tuple[Any, Any]:
    core, consume_mod = integration_profile.load_contract_d(str(contract_d_root))
    registry = deepcopy(core.REGISTRY)
    effects = registry.setdefault("effects", {})
    if ERS_EFFECT_TYPE in effects:
        raise RuntimeError("ERS effect unexpectedly present in released Contract D registry")
    effects[ERS_EFFECT_TYPE] = {ERS_EFFECT_VERSION: {"params": {}}}
    core.REGISTRY = registry
    return core, consume_mod


def make_pending_review_decision(contract_d_root: Path) -> dict[str, Any]:
    fixtures = json.loads((contract_d_root / "fixtures/contract-d/1.0.0/valid.json").read_text(encoding="utf-8"))["fixtures"]
    decision = deepcopy(fixtures["source-audit-clear.json"])
    decision["policy"] = {"id": "mainframe.epistemic-audit.pending-review", "version": "rc1"}
    decision["target"] = {
        "kind": "epistemic_claim",
        "id": "claim:fixture-1",
        "content_sha256": "sha256:" + "1" * 64,
    }
    decision["effect"] = {"type": ERS_EFFECT_TYPE, "version": ERS_EFFECT_VERSION, "params": {}}
    return decision


def released_contract_d_rejects_ers_effect(contract_d_root: Path) -> str:
    core, _ = integration_profile.load_contract_d(str(contract_d_root))
    decision = make_pending_review_decision(contract_d_root)
    try:
        core.validate_decision(decision)
    except core.ContractDError as exc:
        return exc.code
    return "accepted"


def expectation_for(decision: dict[str, Any], core: Any, consume_mod: Any) -> Any:
    effect = core.validate_effect(decision["effect"])
    return consume_mod.ApplicabilityExpectation(
        input_authority=deepcopy(decision["input_authority"]),
        policy=deepcopy(decision["policy"]),
        target=deepcopy(decision["target"]),
        requested_operation=effect["type"],
        effect_params=deepcopy(effect["params"]),
    )



def project_contract_d_decision_identity_for_ers(decision_identity: str) -> str:
    prefix = "decision:sha256:"
    if not isinstance(decision_identity, str) or not decision_identity.startswith(prefix):
        raise ValueError("unsupported_contract_d_decision_identity")
    digest = decision_identity[len("decision:"):]
    if len(digest) != 71:
        raise ValueError("invalid_contract_d_decision_identity")
    return digest

def make_execution_intent(decision_identity: str, *, claim_id: str, claim_content_sha256: str, pre_state_sha256: str) -> dict[str, Any]:
    executable_material = f"{ERS_REPOSITORY}@{ERS_BASELINE_COMMIT}:shadow_pending_review_consumer"
    executable_sha256 = integration_profile.sha256_identity(executable_material)
    return {
        "schema": "execution-intent-candidate-v1",
        "executable_sha256": executable_sha256,
        "entry_point": "ers.contract_e.shadow_stage_pending_review",
        "arguments": ["--claim-id", claim_id, "--shadow"],
        "input_identities": [decision_identity, claim_content_sha256, pre_state_sha256],
        "environment_constraints": {
            "mode": "shadow",
            "network": "disabled",
            "repository": ERS_REPOSITORY,
            "baseline_commit": ERS_BASELINE_COMMIT,
        },
        "side_effect_targets": [f"{PENDING_REVIEW_ROOT}/{claim_id.replace(':', '_')}.md"],
    }


def target_reference_for_intent(intent: dict[str, Any]) -> dict[str, Any]:
    intent_id = integration_profile.execution_intent_identity(intent)
    return integration_profile.immutable_ref("TARGET", ERS_TARGET_CLASS, "1", intent_id)


def make_authority_state(target_reference: dict[str, Any], *, subject_id: str = ERS_PRINCIPAL, valid_from: str = "2026-09-18T00:00:00Z", valid_until: str | None = "2026-09-20T00:00:00Z", revoked_at: str | None = None) -> dict[str, Any]:
    state = {
        "schema": successor_reference.STATE_SCHEMA,
        "authority_state_id": "sha256:" + "0" * 64,
        "records": [{
            "id": "auth:ers-pending-review-rc0",
            "basis_type": "policy",
            "subject_id": subject_id,
            "domain": "epistemic_audit",
            "operation": ERS_EFFECT_TYPE,
            "scope": ERS_SCOPE,
            "target_class": ERS_TARGET_CLASS,
            "target_ref": target_reference["identity_sha256"],
            "valid_from": valid_from,
            "valid_until": valid_until,
            "revoked_at": revoked_at,
            "parent_id": None,
            "delegated_by": None,
        }],
    }
    state["authority_state_id"] = successor_reference.authority_state_identity(state)
    return state


def shadow_gate(*, contract_d_root: Path, decision: dict[str, Any], expected: Any, authority_state: dict[str, Any], execution_intent: dict[str, Any], subject_id: str = ERS_PRINCIPAL, evaluation_time: str = "2026-09-19T00:00:00Z", target_reference: dict[str, Any] | None = None, trusted_decision_identity: str | None = None) -> dict[str, Any]:
    core, _ = integration_profile.load_contract_d(str(contract_d_root))
    decision_identity = core.semantic_identity(decision)
    trusted = integration_profile.TrustedBindings(
        trusted_decision_identity or decision_identity,
        successor_reference.authority_state_identity(authority_state),
    )
    target_reference = target_reference or target_reference_for_intent(execution_intent)
    jurisdiction = {
        "domain": "epistemic_audit",
        "operation": ERS_EFFECT_TYPE,
        "scope": ERS_SCOPE,
        "target_class": ERS_TARGET_CLASS,
        "target_ref": target_reference["identity_sha256"],
    }
    return integration_profile.machine_gate(
        execution_intent=execution_intent,
        decision=decision,
        expected=expected,
        trusted=trusted,
        contract_d_root=str(contract_d_root),
        authority_state=authority_state,
        subject_id=subject_id,
        evaluation_time=evaluation_time,
        jurisdiction=jurisdiction,
        target_reference=target_reference,
    )
