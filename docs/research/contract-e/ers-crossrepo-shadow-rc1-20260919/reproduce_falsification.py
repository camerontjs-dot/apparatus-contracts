from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path
from copy import deepcopy

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ERS_EXPECTED = "0038ae3f16894e96f9aaf45ffe3bc93a6059da2c"
CONTRACT_E_SUBJECT = "a678c73a661853a3a704666fc6bbf29fa378948f"

sys.path.insert(0, str(HERE))
import contract_e_profile as profile  # noqa: E402


def check(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(label)


def git_head(path: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(path), "rev-parse", "HEAD"], text=True
    ).strip()


def load_ers(ers_root: Path):
    check(git_head(ers_root) == ERS_EXPECTED, "non_exact_ers_consumer_commit")
    sys.path.insert(0, str(ers_root))
    from harness import contract_e_shadow as ers  # type: ignore

    return ers


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ers-root", required=True)
    args = parser.parse_args()
    ers_root = Path(args.ers_root).resolve()
    ers = load_ers(ers_root)

    ancestry = subprocess.run(
        ["git", "-C", str(ROOT), "merge-base", "--is-ancestor", CONTRACT_E_SUBJECT, "HEAD"],
        check=False,
    )
    check(ancestry.returncode == 0, "contract_e_subject_not_ancestor")

    check(
        profile.released_contract_d_rejects_ers_effect(ROOT) == "unknown_effect_type",
        "released_contract_d_counterexample_lost",
    )

    core, consume = profile.install_research_effect_profile(ROOT)
    decision = profile.make_pending_review_decision(ROOT)
    decision["target"]["id"] = "claim-fixture-1"
    core.validate_decision(decision)
    expected = profile.expectation_for(decision, core, consume)
    consumed = consume.consume(decision, expected)
    check(
        consumed["outcome"] == "candidate_for_authorization",
        "research_effect_did_not_reach_authorization_boundary",
    )

    typed_decision_id = core.semantic_identity(decision)
    projected_decision_id = profile.project_contract_d_decision_identity_for_ers(
        typed_decision_id
    )
    check(
        typed_decision_id == "decision:" + projected_decision_id,
        "decision_identity_projection_not_reversible",
    )

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        rel = ers.pending_review_relative_path(
            run_id="run-rc1",
            claim_id=decision["target"]["id"],
            text="Bounded cross repository claim",
            project_tag="cal",
        )
        pre = ers.observe_pre_state(root, rel)
        executable_sha256 = "sha256:" + hashlib.sha256(
            (ers_root / "harness/contract_e_shadow.py").read_bytes()
        ).hexdigest()
        intent = ers.build_execution_intent(
            decision_identity=projected_decision_id,
            executable_sha256=executable_sha256,
            claim_id=decision["target"]["id"],
            claim_content_sha256=decision["target"]["content_sha256"],
            pre_state=pre,
            relative_path=rel,
        )
        target_ref = profile.target_reference_for_intent(intent)
        fresh_state = profile.make_authority_state(target_ref)

        exact = profile.shadow_gate(
            contract_d_root=ROOT,
            decision=decision,
            expected=expected,
            authority_state=fresh_state,
            execution_intent=intent,
        )
        check(exact["execution_permitted"] is True, "exact_contract_e_case_denied")
        check(exact["execution_occurred"] is False, "exact_case_claimed_execution")
        check(
            ers.consume_shadow_authorization(
                exact, intent, expected_relative_path=rel
            )["shadow_ready"]
            is True,
            "exact_ers_consume_failed",
        )

        wrong_principal = profile.shadow_gate(
            contract_d_root=ROOT,
            decision=decision,
            expected=expected,
            authority_state=fresh_state,
            execution_intent=intent,
            subject_id="agent:other",
        )
        check(
            wrong_principal["execution_permitted"] is False,
            "wrong_principal_was_permitted",
        )

        other_rel = ers.pending_review_relative_path(
            run_id="run-other",
            claim_id=decision["target"]["id"],
            text="other",
            project_tag="cal",
        )
        wrong_target_intent = deepcopy(intent)
        wrong_target_intent["arguments"][5] = other_rel
        wrong_target_intent["side_effect_targets"] = [other_rel]
        wrong_target_ref = profile.target_reference_for_intent(wrong_target_intent)
        wrong_target = profile.shadow_gate(
            contract_d_root=ROOT,
            decision=decision,
            expected=expected,
            authority_state=fresh_state,
            execution_intent=wrong_target_intent,
            target_reference=wrong_target_ref,
        )
        check(
            wrong_target["execution_permitted"] is False,
            "wrong_target_was_permitted",
        )

        revoked_state = profile.make_authority_state(
            target_ref, revoked_at="2026-09-18T23:59:59Z"
        )
        fresh_revoked = profile.shadow_gate(
            contract_d_root=ROOT,
            decision=decision,
            expected=expected,
            authority_state=revoked_state,
            execution_intent=intent,
        )
        check(
            fresh_revoked["execution_permitted"] is False,
            "fresh_revoked_contract_e_case_was_permitted",
        )

        replay_after_revocation = ers.consume_shadow_authorization(
            exact, intent, expected_relative_path=rel
        )
        check(
            replay_after_revocation["shadow_ready"] is True,
            "counterexample_changed: old_result_not_accepted_after_revocation",
        )

        target = root.joinpath(*Path(rel).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("changed-after-authorization", encoding="utf-8")
        changed_pre = ers.observe_pre_state(root, rel)
        check(
            changed_pre["state_sha256"] != pre["state_sha256"],
            "target_change_not_observed",
        )
        replay_after_target_change = ers.consume_shadow_authorization(
            exact, intent, expected_relative_path=rel
        )
        check(
            replay_after_target_change["shadow_ready"] is True,
            "counterexample_changed: old_result_not_accepted_after_target_change",
        )

        swapped_intent = ers.build_execution_intent(
            decision_identity="sha256:" + "9" * 64,
            executable_sha256=executable_sha256,
            claim_id=decision["target"]["id"],
            claim_content_sha256=decision["target"]["content_sha256"],
            pre_state=pre,
            relative_path=rel,
        )
        swapped_ref = profile.target_reference_for_intent(swapped_intent)
        swapped_state = profile.make_authority_state(swapped_ref)
        swapped = profile.shadow_gate(
            contract_d_root=ROOT,
            decision=decision,
            expected=expected,
            authority_state=swapped_state,
            execution_intent=swapped_intent,
        )
        check(
            swapped["execution_permitted"] is True,
            "counterexample_changed: swapped_decision_input_denied_by_contract_e",
        )
        check(
            ers.consume_shadow_authorization(
                swapped, swapped_intent, expected_relative_path=rel
            )["shadow_ready"]
            is True,
            "counterexample_changed: swapped_decision_input_rejected_by_ers",
        )

        generic = deepcopy(exact)
        generic["authorization"]["request"]["jurisdiction"][
            "operation"
        ] = "knowledge.add_verified_tag"
        try:
            ers.consume_shadow_authorization(
                generic, intent, expected_relative_path=rel
            )
        except Exception:
            pass
        else:
            raise AssertionError("generic_operation_receipt_was_accepted")

        mismatch = deepcopy(exact)
        mismatch["execution_intent_identity"] = "sha256:" + "8" * 64
        try:
            ers.consume_shadow_authorization(
                mismatch, intent, expected_relative_path=rel
            )
        except Exception:
            pass
        else:
            raise AssertionError("mismatched_intent_identity_was_accepted")

    print("CONTRACT_E_ERS_CROSSREPO_RC1: FALSIFIED")
    print("exact_case: permitted_shadow_only")
    print("wrong_principal: rejected")
    print("wrong_target: rejected")
    print("fresh_revoked_authority: rejected")
    print("replay_old_authorization_after_revocation: ACCEPTED_COUNTEREXAMPLE")
    print("old_authorization_after_target_change: ACCEPTED_COUNTEREXAMPLE")
    print("swapped_decision_input_identity: ACCEPTED_COUNTEREXAMPLE")
    print("generic_operation_receipt: rejected_by_ers")
    print("mismatched_execution_intent_receipt: rejected_by_ers")
    print("execution_occurred: false")


if __name__ == "__main__":
    main()
