from __future__ import annotations

import argparse
import hashlib
import importlib.util
import inspect
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RC2_DIR = ROOT / "docs/research/contract-e/ers-point-of-use-crossrepo-rc2-20260919"
RC2_HEAD = "b153dcc4434cbe8a98616a9e410c6125378144c7"
ERS_HEAD = "73a47dc0ce2e3ae6c7aa6e55c4183e223797724b"


def check(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(label)


def git_head(path: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(path), "rev-parse", "HEAD"], text=True
    ).strip()


def load_profile():
    spec = importlib.util.spec_from_file_location(
        "ers_point_of_use_rc2_profile", RC2_DIR / "contract_e_profile.py"
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot_load_rc2_profile")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ers-root", required=True)
    args = parser.parse_args()

    ers_root = Path(args.ers_root).resolve()
    check(git_head(ROOT) == RC2_HEAD, "non_exact_apparatus_rc2_commit")
    check(git_head(ers_root) == ERS_HEAD, "non_exact_ers_consumer_commit")

    sys.path.insert(0, str(ers_root))
    from harness import contract_e_shadow as ers

    profile = load_profile()
    core, consume = profile.install_research_effect_profile(ROOT)
    decision = profile.make_pending_review_decision(ROOT)
    decision["target"]["id"] = "claim-fixture-1"
    core.validate_decision(decision)
    expected = profile.expectation_for(decision, core, consume)
    consume.consume(decision, expected)
    decision_id = core.semantic_identity(decision)

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        rel = ers.pending_review_relative_path(
            run_id="run-payload-binding",
            claim_id=decision["target"]["id"],
            text="Bounded output binding claim",
            project_tag="cal",
        )
        pre = ers.observe_pre_state(root, rel)
        executable_sha256 = "sha256:" + hashlib.sha256(
            (ers_root / "harness/contract_e_shadow.py").read_bytes()
        ).hexdigest()
        intent = ers.build_execution_intent(
            decision_identity=decision_id,
            executable_sha256=executable_sha256,
            claim_id=decision["target"]["id"],
            claim_content_sha256=decision["target"]["content_sha256"],
            pre_state=pre,
            relative_path=rel,
        )
        target_ref = profile.target_reference_for_intent(intent)
        state = profile.make_authority_state(target_ref)
        result = profile.shadow_gate(
            contract_d_root=ROOT,
            decision=decision,
            expected=expected,
            authority_state=state,
            execution_intent=intent,
        )
        accepted = ers.consume_shadow_authorization(
            result,
            intent,
            expected_relative_path=rel,
            mainframe_root=root,
            current_authority_state_id=state["authority_state_id"],
            current_evaluation_time="2026-09-19T00:00:00Z",
        )
        check(accepted["shadow_ready"] is True, "exact_rc2_not_shadow_ready")

        payload_a = (
            b"---\nstatus: active\n---\nExpected pending review body\n"
        )
        payload_b = (
            b"---\nstatus: active\n---\nDIFFERENT CONTENT WITH SAME AUTHORIZATION\n"
        )
        payload_a_id = "sha256:" + hashlib.sha256(payload_a).hexdigest()
        payload_b_id = "sha256:" + hashlib.sha256(payload_b).hexdigest()
        check(payload_a_id != payload_b_id, "payloads_not_distinct")

        authorized_material = repr(intent) + repr(result)
        check(payload_a_id not in authorized_material, "payload_a_unexpectedly_bound")
        check(payload_b_id not in authorized_material, "payload_b_unexpectedly_bound")

        parameters = inspect.signature(ers.consume_shadow_authorization).parameters
        payload_parameter_names = {
            name
            for name in parameters
            if "payload" in name.lower() or "output" in name.lower()
        }
        check(not payload_parameter_names, "consumer_has_payload_binding_parameter")

        print("ERS_OUTPUT_PAYLOAD_BINDING: FALSIFIED")
        print("exact_rc2_consumer: accepted")
        print(f"payload_a: {payload_a_id}")
        print(f"payload_b: {payload_b_id}")
        print("payloads_differ: true")
        print("payload_a_bound: false")
        print("payload_b_bound: false")
        print("consumer_payload_parameter: absent")
        print(f"intent_input_identities: {intent['input_identities']}")
        print("disposition: FALSIFIED_EXECUTION_PAYLOAD_UNBOUND")


if __name__ == "__main__":
    main()
