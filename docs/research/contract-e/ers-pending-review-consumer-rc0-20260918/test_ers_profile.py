from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import ers_profile as ers

ROOT = Path(__file__).resolve().parents[4]


def check(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(label)


def main() -> None:
    check(
        ers.released_contract_d_rejects_ers_effect(ROOT) == "unknown_effect_type",
        "released Contract D unexpectedly accepted ERS pending-review effect",
    )

    core, consume_mod = ers.install_research_effect_profile(ROOT)
    decision = ers.make_pending_review_decision(ROOT)
    core.validate_decision(decision)
    expected = ers.expectation_for(decision, core, consume_mod)
    consumed = consume_mod.consume(decision, expected)
    check(
        consumed["outcome"] == "candidate_for_authorization",
        f"research Contract D profile did not reach authorization boundary: {consumed}",
    )

    decision_id = core.semantic_identity(decision)
    intent = ers.make_execution_intent(
        decision_id,
        claim_id=decision["target"]["id"],
        claim_content_sha256=decision["target"]["content_sha256"],
        pre_state_sha256="sha256:" + "2" * 64,
    )
    target_ref = ers.target_reference_for_intent(intent)
    state = ers.make_authority_state(target_ref)

    exact = ers.shadow_gate(
        contract_d_root=ROOT,
        decision=decision,
        expected=expected,
        authority_state=state,
        execution_intent=intent,
    )
    check(exact["execution_permitted"] is True, f"exact case denied: {exact}")
    check(exact["execution_occurred"] is False, "shadow profile claimed execution")

    wrong_principal = ers.shadow_gate(
        contract_d_root=ROOT,
        decision=decision,
        expected=expected,
        authority_state=state,
        execution_intent=intent,
        subject_id="agent:other",
    )
    check(wrong_principal["execution_permitted"] is False, "wrong principal permitted")

    wrong_target = deepcopy(target_ref)
    wrong_target["immutable_id"] = "sha256:" + "3" * 64
    wrong_target["identity_sha256"] = ers.successor_reference.reference_identity(
        wrong_target["kind"], wrong_target["version"], wrong_target["immutable_id"]
    )
    wrong_target_result = ers.shadow_gate(
        contract_d_root=ROOT,
        decision=decision,
        expected=expected,
        authority_state=state,
        execution_intent=intent,
        target_reference=wrong_target,
    )
    check(
        wrong_target_result["execution_permitted"] is False
        and wrong_target_result["reason"] == "execution_intent_target_binding_mismatch",
        f"wrong target not discriminated: {wrong_target_result}",
    )

    swapped = deepcopy(decision)
    swapped["target"]["content_sha256"] = "sha256:" + "4" * 64
    try:
        ers.shadow_gate(
            contract_d_root=ROOT,
            decision=swapped,
            expected=expected,
            authority_state=state,
            execution_intent=intent,
            trusted_decision_identity=decision_id,
        )
    except ers.integration_profile.ProfileError as exc:
        check(
            str(exc) == "untrusted_decision_identity",
            f"swapped decision failed for unexpected reason: {exc}",
        )
    else:
        raise AssertionError("swapped Contract D decision permitted")

    stale = ers.shadow_gate(
        contract_d_root=ROOT,
        decision=decision,
        expected=expected,
        authority_state=state,
        execution_intent=intent,
        evaluation_time="2026-09-21T00:00:00Z",
    )
    check(stale["execution_permitted"] is False, "stale authority permitted")

    revoked_state = ers.make_authority_state(
        target_ref,
        revoked_at="2026-09-18T12:00:00Z",
    )
    revoked = ers.shadow_gate(
        contract_d_root=ROOT,
        decision=decision,
        expected=expected,
        authority_state=revoked_state,
        execution_intent=intent,
    )
    check(revoked["execution_permitted"] is False, "revoked authority permitted")

    check(exact["execution_permitted"] is True, "precondition: prior permit missing")
    replay = ers.shadow_gate(
        contract_d_root=ROOT,
        decision=decision,
        expected=expected,
        authority_state=revoked_state,
        execution_intent=intent,
    )
    check(replay["execution_permitted"] is False, "prior permit conferred authority")

    changed_intent = ers.make_execution_intent(
        decision_id,
        claim_id=decision["target"]["id"],
        claim_content_sha256=decision["target"]["content_sha256"],
        pre_state_sha256="sha256:" + "5" * 64,
    )
    changed_pre_state = ers.shadow_gate(
        contract_d_root=ROOT,
        decision=decision,
        expected=expected,
        authority_state=state,
        execution_intent=changed_intent,
        target_reference=target_ref,
    )
    check(
        changed_pre_state["execution_permitted"] is False
        and changed_pre_state["reason"] == "execution_intent_target_binding_mismatch",
        f"changed pre-state not discriminated: {changed_pre_state}",
    )

    wrong_operation_state = deepcopy(state)
    wrong_operation_state["records"][0]["operation"] = "knowledge.add_verified_tag"
    wrong_operation_state["authority_state_id"] = ers.successor_reference.authority_state_identity(
        wrong_operation_state
    )
    wrong_operation = ers.shadow_gate(
        contract_d_root=ROOT,
        decision=decision,
        expected=expected,
        authority_state=wrong_operation_state,
        execution_intent=intent,
    )
    check(
        wrong_operation["execution_permitted"] is False,
        "generic knowledge mutation authority accepted",
    )

    print("ERS_CONTRACT_E_SHADOW_RC0: PASS")
    print("cases=9")
    print("execution_occurred=false")


if __name__ == "__main__":
    main()
