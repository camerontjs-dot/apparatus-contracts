from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
import tempfile
from copy import deepcopy
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ERS_EXPECTED = "73a47dc0ce2e3ae6c7aa6e55c4183e223797724b"
CONTRACT_E_SUBJECT = "a678c73a661853a3a704666fc6bbf29fa378948f"
EVALUATION_TIME = "2026-09-19T00:00:00Z"

sys.path.insert(0, str(HERE))
import contract_e_profile as profile  # noqa: E402


def check(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(label)


def git_head(path: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(path), "rev-parse", "HEAD"], text=True
    ).strip()


def git_status(path: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(path), "status", "--porcelain"], text=True
    )


def file_sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(root: Path) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for path in sorted(root.rglob("*")):
        rel = str(path.relative_to(root))
        if path.is_file():
            rows.append((rel, file_sha256(path)))
        else:
            rows.append((rel + "/", "dir"))
    return rows


def expect_error(fn, code: str, label: str) -> None:
    try:
        fn()
    except Exception as exc:
        if str(exc) != code:
            raise AssertionError(f"{label}: wrong error {exc!s}") from exc
        return
    raise AssertionError(f"{label}: accepted counterexample")


def load_ers(ers_root: Path):
    check(git_head(ers_root) == ERS_EXPECTED, "non_exact_ers_consumer_commit")
    check(git_status(ers_root) == "", "dirty_ers_consumer_checkout")
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
        [
            "git",
            "-C",
            str(ROOT),
            "merge-base",
            "--is-ancestor",
            CONTRACT_E_SUBJECT,
            "HEAD",
        ],
        check=False,
    )
    check(ancestry.returncode == 0, "contract_e_subject_not_ancestor")

    check(
        profile.released_contract_d_rejects_ers_effect(ROOT)
        == "unknown_effect_type",
        "released_contract_d_counterexample_lost",
    )

    core, consume_mod = profile.install_research_effect_profile(ROOT)
    decision = profile.make_pending_review_decision(ROOT)
    decision["target"]["id"] = "claim-fixture-1"
    core.validate_decision(decision)
    expected = profile.expectation_for(decision, core, consume_mod)
    consumed = consume_mod.consume(decision, expected)
    check(
        consumed["outcome"] == "candidate_for_authorization",
        "research_contract_d_did_not_reach_authorization_boundary",
    )
    decision_id = core.semantic_identity(decision)
    check(
        isinstance(decision_id, str)
        and decision_id.startswith("decision:sha256:")
        and len(decision_id) == 80,
        "contract_d_decision_identity_not_typed",
    )

    module_path = ers_root / "harness" / "contract_e_shadow.py"
    executable_id = file_sha256(module_path)
    module_before = executable_id

    with tempfile.TemporaryDirectory() as td:
        point_root = Path(td)
        rel = ers.pending_review_relative_path(
            run_id="run-rc2",
            claim_id=decision["target"]["id"],
            text="Bounded cross repository point of use claim",
            project_tag="cal",
        )
        pre = ers.observe_pre_state(point_root, rel)
        intent = ers.build_execution_intent(
            decision_identity=decision_id,
            executable_sha256=executable_id,
            claim_id=decision["target"]["id"],
            claim_content_sha256=decision["target"]["content_sha256"],
            pre_state=pre,
            relative_path=rel,
        )
        check(
            intent["input_identities"][0] == decision_id,
            "typed_decision_identity_not_preserved",
        )
        check(
            ers.execution_intent_identity(intent)
            == profile.integration_profile.execution_intent_identity(intent),
            "execution_intent_identity_disagreement",
        )

        target_ref = profile.target_reference_for_intent(intent)
        check(
            ers.target_reference_identity(intent) == target_ref["identity_sha256"],
            "target_reference_identity_disagreement",
        )
        state = profile.make_authority_state(target_ref)
        state_id = profile.successor_reference.authority_state_identity(state)

        before_exact = snapshot(point_root)
        exact = profile.shadow_gate(
            contract_d_root=ROOT,
            decision=decision,
            expected=expected,
            authority_state=state,
            execution_intent=intent,
            evaluation_time=EVALUATION_TIME,
        )
        check(exact["execution_permitted"] is True, "exact_contract_e_denied")
        check(exact["execution_occurred"] is False, "exact_claimed_execution")
        exact_consumed = ers.consume_shadow_authorization(
            exact,
            intent,
            expected_relative_path=rel,
            mainframe_root=point_root,
            current_authority_state_id=state_id,
            current_evaluation_time=EVALUATION_TIME,
        )
        check(exact_consumed["shadow_ready"] is True, "exact_ers_rejected")
        check(
            exact_consumed["decision_identity"] == decision_id,
            "exact_decision_binding_lost",
        )
        check(
            before_exact == snapshot(point_root),
            "exact_shadow_case_mutated_target",
        )

        wrong_principal = profile.shadow_gate(
            contract_d_root=ROOT,
            decision=decision,
            expected=expected,
            authority_state=state,
            execution_intent=intent,
            subject_id="agent:other",
            evaluation_time=EVALUATION_TIME,
        )
        check(
            wrong_principal["execution_permitted"] is False,
            "wrong_principal_permitted",
        )

        wrong_rel = ers.pending_review_relative_path(
            run_id="run-wrong-target",
            claim_id=decision["target"]["id"],
            text="wrong target",
            project_tag="cal",
        )
        wrong_intent = deepcopy(intent)
        wrong_intent["arguments"][5] = wrong_rel
        wrong_intent["side_effect_targets"] = [wrong_rel]
        wrong_target = profile.shadow_gate(
            contract_d_root=ROOT,
            decision=decision,
            expected=expected,
            authority_state=state,
            execution_intent=wrong_intent,
            evaluation_time=EVALUATION_TIME,
        )
        check(
            wrong_target["execution_permitted"] is False,
            "wrong_target_permitted",
        )

        revoked = profile.make_authority_state(
            target_ref, revoked_at="2026-09-18T23:59:59Z"
        )
        revoked_id = profile.successor_reference.authority_state_identity(
            revoked
        )
        fresh_revoked = profile.shadow_gate(
            contract_d_root=ROOT,
            decision=decision,
            expected=expected,
            authority_state=revoked,
            execution_intent=intent,
            evaluation_time=EVALUATION_TIME,
        )
        check(
            fresh_revoked["execution_permitted"] is False,
            "fresh_revoked_authority_permitted",
        )

        expect_error(
            lambda: ers.consume_shadow_authorization(
                exact,
                intent,
                expected_relative_path=rel,
                mainframe_root=point_root,
                current_authority_state_id=revoked_id,
                current_evaluation_time=EVALUATION_TIME,
            ),
            "stale_authority_state",
            "replay_after_revocation",
        )
        expect_error(
            lambda: ers.consume_shadow_authorization(
                exact,
                intent,
                expected_relative_path=rel,
                mainframe_root=point_root,
                current_authority_state_id=state_id,
                current_evaluation_time="2026-09-19T00:00:01Z",
            ),
            "stale_evaluation_time",
            "replay_at_newer_time",
        )

        swapped = deepcopy(intent)
        swapped["input_identities"][0] = "decision:sha256:" + "4" * 64
        swapped_ref = profile.target_reference_for_intent(swapped)
        swapped_state = profile.make_authority_state(swapped_ref)
        swapped_state_id = (
            profile.successor_reference.authority_state_identity(swapped_state)
        )
        swapped_out = profile.shadow_gate(
            contract_d_root=ROOT,
            decision=decision,
            expected=expected,
            authority_state=swapped_state,
            execution_intent=swapped,
            evaluation_time=EVALUATION_TIME,
        )
        check(
            swapped_out["execution_permitted"] is True,
            "swapped_decision_control_did_not_reach_consumer",
        )
        expect_error(
            lambda: ers.consume_shadow_authorization(
                swapped_out,
                swapped,
                expected_relative_path=rel,
                mainframe_root=point_root,
                current_authority_state_id=swapped_state_id,
                current_evaluation_time=EVALUATION_TIME,
            ),
            "decision_identity_binding_mismatch",
            "swapped_typed_decision_identity",
        )

        generic = deepcopy(exact)
        generic["authorization"]["request"]["jurisdiction"][
            "operation"
        ] = "knowledge.add_verified_tag"
        expect_error(
            lambda: ers.consume_shadow_authorization(
                generic,
                intent,
                expected_relative_path=rel,
                mainframe_root=point_root,
                current_authority_state_id=state_id,
                current_evaluation_time=EVALUATION_TIME,
            ),
            "wrong_jurisdiction",
            "generic_operation_receipt",
        )

        mismatch = deepcopy(exact)
        mismatch["execution_intent_identity"] = "sha256:" + "8" * 64
        expect_error(
            lambda: ers.consume_shadow_authorization(
                mismatch,
                intent,
                expected_relative_path=rel,
                mainframe_root=point_root,
                current_authority_state_id=state_id,
                current_evaluation_time=EVALUATION_TIME,
            ),
            "execution_intent_identity_mismatch",
            "mismatched_execution_intent_receipt",
        )

        executed = deepcopy(exact)
        executed["execution_occurred"] = True
        expect_error(
            lambda: ers.consume_shadow_authorization(
                executed,
                intent,
                expected_relative_path=rel,
                mainframe_root=point_root,
                current_authority_state_id=state_id,
                current_evaluation_time=EVALUATION_TIME,
            ),
            "execution_occurred_not_false",
            "already_executed_result",
        )

        target = point_root.joinpath(*Path(rel).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("changed-after-authorization", encoding="utf-8")
        expect_error(
            lambda: ers.consume_shadow_authorization(
                exact,
                intent,
                expected_relative_path=rel,
                mainframe_root=point_root,
                current_authority_state_id=state_id,
                current_evaluation_time=EVALUATION_TIME,
            ),
            "point_of_use_pre_state_mismatch",
            "target_changed_after_authorization",
        )

    check(file_sha256(module_path) == module_before, "ers_module_changed")
    check(git_status(ers_root) == "", "ers_checkout_changed")

    print("CONTRACT_E_ERS_POINT_OF_USE_RC2: PASS")
    print("exact_case: permitted_shadow_only")
    print("typed_decision_identity: preserved_without_projection")
    print("intent_identity: exact_match")
    print("target_reference_identity: exact_match")
    print("wrong_principal: rejected")
    print("wrong_target: rejected")
    print("fresh_revoked_authority: rejected")
    print("replay_after_revocation: rejected")
    print("replay_at_newer_time: rejected")
    print("target_change_after_authorization: rejected")
    print("swapped_typed_decision_identity: rejected_by_ers")
    print("generic_operation_receipt: rejected_by_ers")
    print("mismatched_execution_intent_receipt: rejected_by_ers")
    print("already_executed_result: rejected_by_ers")
    print("execution_occurred: false")


if __name__ == "__main__":
    main()
