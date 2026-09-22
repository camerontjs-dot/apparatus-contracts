from __future__ import annotations

import argparse
import atexit
import base64
import copy
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import rfc8785
from cryptography.hazmat.primitives import serialization


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ERS_PREREG = "907a10dae0d3d1fc78acbfda3c26a164f3a4693b"
ERS_RC5 = "099f84700f28e118734f1ca74feb977da1c4cf17"
ERS_RC4 = "022fcb58e14864aa173f447fa0c18dd2362b41b0"
ERS_RC3 = "319e325cdf678673fae645a70e3e34afb7dddef0"
DECISION = "816374379ba7eb23f5bfdadaf203b7e287c052db"
CAL_V3 = "ffc43d4e89f5b1f7748e9cde0fa1efc7db47b463"
CONTRACT_D = "298a1a0f7b7b6d7712e11200d04faec3e1ca169b"
CONTRACT_E = "b153dcc4434cbe8a98616a9e410c6125378144c7"
CONTRACT_C_CONSUMER = "12e7e640b229619501960b1b89cf4716d8d985b3"
APPARATUS_PR127 = "bb8ff5c5d9fd3e221b0dea76e4748fe85be30796"
APPARATUS_PR128 = "5fefe7ac3725ccf3a68ff1fa5991ebc14add6856"
CLAIM_CONTENT_ID = "sha256:fe9a393b0c31f7e2f200cbefc08d9293e364f8a0810865a73003ec3502c387d0"
PIPE01_DECISION_ID = "decision:sha256:3427c5cb6692bf7358c13e47628ef7a91a0c53e78affc58f2ae60173daffcc15"
ISSUER_KEY_ID = "sha256:9b97a2a3f588c60b899f93c5dbbd010c41e8bd93f5790d6ba11fb8c381d4da17"
ISSUER_PUBLIC_KEY_PEM = b"""-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEAgab+xTwumW5B0aC2kT7ZdF3H0Wn5nmyaltI3qJoXd1U=
-----END PUBLIC KEY-----
"""
AUTHORITY_STATE_SOURCE_ID = "qualification-authority-state-fixture-v1"
EVALUATION_TIME_SOURCE_ID = "contract-e-authorization-request.evaluation_time"
OBSERVER_CLOCK_SOURCE_ID = "qualification-supervisor-process.os-clock-utc-v1"


def check(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(label)


def sha256_identity(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def canonical_json(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
        + b"\n"
    )


def independent_identity(value: Any) -> str:
    return sha256_identity(canonical_json(value))


def git(path: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(path), *args], text=True).strip()


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("module_load_failed")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def utc_text(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace(
        "+00:00", "Z"
    )


def verify_receipt_independently(receipt: dict[str, Any]) -> tuple[str, str]:
    body = receipt["body"]
    canonical = canonical_json(body)
    public_key = serialization.load_pem_public_key(ISSUER_PUBLIC_KEY_PEM)
    public_key.verify(
        base64.b64decode(receipt["signature"]["value"], validate=True), canonical
    )
    key_id = "sha256:" + hashlib.sha256(
        public_key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    ).hexdigest()
    check(key_id == ISSUER_KEY_ID, "independent_issuer_key_id_mismatch")
    return sha256_identity(canonical), key_id


def wait_for_socket(process: subprocess.Popen[str], socket_path: Path) -> None:
    deadline = time.monotonic() + 3.0
    while time.monotonic() < deadline:
        if socket_path.exists():
            return
        if process.poll() is not None:
            detail = process.stderr.read() if process.stderr else ""
            raise RuntimeError("observer_start_failed:" + detail[-500:])
        time.sleep(0.01)
    raise RuntimeError("observer_socket_not_ready")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ers-root", required=True, type=Path)
    parser.add_argument("--decision-root", required=True, type=Path)
    parser.add_argument("--contract-e-root", required=True, type=Path)
    parser.add_argument("--contract-d-root", required=True, type=Path)
    parser.add_argument("--consumer-root", required=True, type=Path)
    parser.add_argument("--fixtures", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    ers_root = args.ers_root.resolve()
    decision_root = args.decision_root.resolve()
    contract_e_root = args.contract_e_root.resolve()
    contract_d_root = args.contract_d_root.resolve()
    consumer_root = args.consumer_root.resolve()
    fixtures = args.fixtures.resolve()
    private_key = os.environ.get("ERS_CONTEXT_OBSERVER_PRIVATE_KEY")
    check(bool(private_key), "observer_key_path_missing")

    check(git(ers_root, "rev-parse", "HEAD") == ERS_RC5, "wrong_frozen_ers_rc5")
    check(git(ers_root, "rev-parse", "HEAD^" ) == ERS_PREREG, "wrong_ers_prereg_parent")
    check(git(decision_root, "rev-parse", "HEAD") == DECISION, "wrong_decision_successor")
    check(git(contract_e_root, "rev-parse", "HEAD") == CONTRACT_E, "wrong_contract_e_profile")
    check(git(contract_d_root, "rev-parse", "HEAD") == CONTRACT_D, "wrong_released_contract_d")
    check(git(consumer_root, "rev-parse", "HEAD") == CONTRACT_C_CONSUMER, "wrong_contract_c_consumer")
    check(git(ROOT, "rev-parse", APPARATUS_PR128) == APPARATUS_PR128, "wrong_apparatus_pr128_base")
    check(git(ROOT, "cat-file", "-t", CAL_V3) == "commit", "frozen_cal_v3_object_missing")
    check(
        subprocess.run(
            ["git", "-C", str(ers_root), "diff", "--quiet", ERS_RC4, "--", "pipeline_slices/contract-e-shadow-rc3", "pipeline_slices/contract-e-shadow-rc4-render-bound"],
            check=False,
        ).returncode
        == 0,
        "frozen_ers_slices_changed",
    )

    baseline = load_module(
        "ers_render_bound_base_reproduction",
        ROOT / "research/ers-render-bound-shadow-composition-20260921/reproduce.py",
    )
    profile_path = contract_e_root / "docs/research/contract-e/ers-point-of-use-crossrepo-rc2-20260919/contract_e_profile.py"
    profile = load_module("ers_context_contract_e_profile", profile_path)
    compatibility_probe = {
        "schema": "execution-intent-candidate-v1",
        "executable_sha256": "sha256:" + "1" * 64,
        "entry_point": "harness.context_bound_shadow:stage_pending_review",
        "arguments": ["--mode", "shadow-render-bound"],
        "input_identities": ["decision:sha256:" + "2" * 64] + ["sha256:" + str(i) * 64 for i in range(3, 7)],
        "environment_constraints": {"mutation": "forbidden"},
        "side_effect_targets": ["20_live/epistemic-audit/pending-review/example.md"],
    }
    compatibility_identity = profile.integration_profile.execution_intent_identity(compatibility_probe)

    slice_root = ers_root / "pipeline_slices/contract-e-shadow-rc5-context-receipt"
    sys.path.insert(0, str(slice_root))
    sys.path.insert(1, str(ers_root))
    from harness import context_bound_shadow as ers  # noqa: E402
    from harness import context_observer, render_packet  # noqa: E402

    decision_result = baseline.run_decision_successor(
        decision_root=decision_root,
        fixtures=fixtures,
        consumer_root=consumer_root,
        contract_d_root=contract_d_root,
    )
    core, consume_mod = profile.install_research_effect_profile(contract_d_root)
    supported_cases: dict[str, Any] = {}
    for case_id in ("PIPE01", "PIPE02", "PIPE03"):
        node_case = decision_result["cases"][case_id]
        stored_d = (fixtures / case_id / "contract-d.json").read_bytes()
        supported_canonical = base64.b64decode(node_case["supported_canonical_b64"])
        check(node_case["supported_equals_frozen"], case_id + ":supported_policy_changed")
        check(supported_canonical == stored_d, case_id + ":supported_contract_d_not_byte_compatible")
        check(node_case["released_ers_contract_d"]["accepted"] is False, case_id + ":released_d_accepted_ers")
        check("unknown_effect_type" in node_case["released_ers_contract_d"]["message"], case_id + ":released_d_rejection_changed")
        supported_cases[case_id] = {
            "contract_c_identity": sha256_identity((fixtures / case_id / "cal/contract-c.json").read_bytes()),
            "supported_contract_d_identity": sha256_identity(stored_d),
            "supported_matches_frozen_v3": True,
            "ers_decision_identity": core.semantic_identity(node_case["ers"]),
            "released_contract_d_rejection": node_case["released_ers_contract_d"]["message"],
        }

    pipe01 = decision_result["cases"]["PIPE01"]
    decision_id = core.semantic_identity(pipe01["ers"])
    check(decision_id == PIPE01_DECISION_ID, "pipe01_decision_identity_changed")
    check(pipe01["target"]["content_sha256"] == CLAIM_CONTENT_ID, "pipe01_claim_content_changed")

    packet = render_packet.freeze_render_packet(baseline.fixture_snapshot())
    payload = render_packet.render_pending_review(packet)
    packet_id = render_packet.render_packet_identity(packet)
    payload_id = render_packet.rendered_payload_identity(packet)
    check(payload == baseline.independent_render(packet), "independent_renderer_mismatch")
    check(packet_id == baseline.independent_object_identity(packet), "independent_packet_identity_mismatch")
    check(payload_id == sha256_identity(payload), "independent_payload_identity_mismatch")
    check(packet_id == "sha256:fc3ae075b85ebeb4a8d329453505b9a9cd3bb0ee5658e04f5f77b853cc2b2512", "frozen_packet_identity_changed")
    check(payload_id == "sha256:f8d3a15fbf385a5846311b73a3e121bae92f7842d92dafb9ffc79612fd68f221", "frozen_payload_identity_changed")

    evaluation_time = utc_text(datetime.now(timezone.utc))
    evaluation_dt = datetime.fromisoformat(evaluation_time[:-1] + "+00:00")
    authority_valid_until = utc_text(evaluation_dt + timedelta(days=1))
    packet_target = packet["render"]["target_relative_path"]
    tmp = tempfile.TemporaryDirectory(prefix="ers-context-composition-", dir="/private/tmp")
    atexit.register(tmp.cleanup)
    temp_root = Path(tmp.name)
    sandbox = temp_root / "sandbox"
    sandbox.mkdir()
    state_path = temp_root / "authority-state.json"
    socket_path = temp_root / "observer.sock"
    sandbox_before = sorted(str(item.relative_to(sandbox)) for item in sandbox.rglob("*"))
    pre_state = ers._render_bound._base.observe_pre_state(sandbox, packet_target)
    executable_id = sha256_identity((slice_root / "harness/context_bound_shadow.py").read_bytes())
    intent = ers._render_bound.build_execution_intent(
        decision_identity=decision_id,
        executable_sha256=executable_id,
        claim_id="ROOT",
        claim_content_sha256=CLAIM_CONTENT_ID,
        pre_state=pre_state,
        relative_path=packet_target,
        render_packet=packet,
    )
    check(len(intent["input_identities"]) == 5, "intent_input_identity_count_changed")
    check(intent["input_identities"][:3] == [decision_id, CLAIM_CONTENT_ID, pre_state["state_sha256"]], "inherited_intent_bindings_changed")
    check(profile.integration_profile.execution_intent_identity(intent) == ers._render_bound.execution_intent_identity(intent), "whole_intent_identity_disagreement")

    target_reference = profile.target_reference_for_intent(intent)
    authority_state = profile.make_authority_state(
        target_reference,
        valid_from="2026-01-01T00:00:00Z",
        valid_until=authority_valid_until,
    )
    expected = profile.expectation_for(pipe01["ers"], core, consume_mod)
    contract_e_result = profile.shadow_gate(
        contract_d_root=contract_d_root,
        decision=pipe01["ers"],
        expected=expected,
        authority_state=authority_state,
        execution_intent=intent,
        evaluation_time=evaluation_time,
    )
    check(contract_e_result["execution_permitted"] is True, "contract_e_did_not_permit_pipe01")
    check(contract_e_result["execution_occurred"] is False, "contract_e_execution_occurred")
    contract_e_result_identity = profile.integration_profile.sha256_identity(contract_e_result)
    check(context_observer.authority_state_identity(authority_state) == authority_state["authority_state_id"], "observer_and_contract_e_state_identity_disagree")
    state_path.write_bytes(rfc8785.dumps(authority_state) + b"\n")
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join([str(slice_root), str(ers_root), env.get("PYTHONPATH", "")])
    observer = subprocess.Popen(
        [
            sys.executable,
            str(slice_root / "harness/context_observer.py"),
            "--socket-path", str(socket_path),
            "--authority-state-source", str(state_path),
            "--private-key-file", private_key,
        ],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        wait_for_socket(observer, socket_path)
        positive = ers.stage_pending_review(
            contract_e_result,
            intent,
            expected_relative_path=packet_target,
            mainframe_root=str(sandbox),
            expected_executable_sha256=executable_id,
            render_packet=packet,
            payload=payload,
            observer_socket=str(socket_path),
        )
        receipt = positive["point_of_use_context_receipt"]
        receipt_id, independent_key_id = verify_receipt_independently(receipt)
        body = receipt["body"]
        check(positive["shadow_ready"] is True, "pipe01_not_shadow_ready")
        check(positive["execution_occurred"] is False, "pipe01_execution_occurred")
        check(body["execution_intent_identity"] == ers._render_bound.execution_intent_identity(intent), "receipt_intent_mismatch")
        check(body["authority_state_identity"] == contract_e_result["authorization"]["request"]["authority_state_id"], "receipt_authority_state_mismatch")
        check(body["evaluation_time"] == evaluation_time, "receipt_evaluation_time_mismatch")
        check(body["observations"]["authority_state_source_id"] == AUTHORITY_STATE_SOURCE_ID, "wrong_state_source_recorded")
        check(body["observations"]["evaluation_time_source_id"] == EVALUATION_TIME_SOURCE_ID, "wrong_evaluation_source_recorded")
        check(body["observations"]["observer_clock_source_id"] == OBSERVER_CLOCK_SOURCE_ID, "wrong_clock_source_recorded")
        check(positive["context_receipt_identity"] == receipt_id, "receipt_identity_independent_mismatch")
        observed_at = datetime.fromisoformat(body["observations"]["observed_at"][:-1] + "+00:00")
        age_seconds = (observed_at - evaluation_dt).total_seconds()
        check(0 <= age_seconds <= 30, "receipt_evaluation_time_not_fresh")

        # Supplemental source-provenance falsifier: mutate only the E result's
        # request timestamp after the genuine E evaluation. RC5 asks the
        # observer to attest that supplied field without a binding to the
        # original E result identity.
        forged_result = copy.deepcopy(contract_e_result)
        forged_time = utc_text(evaluation_dt - timedelta(seconds=1))
        forged_result["authorization"]["request"]["evaluation_time"] = forged_time
        forged_result_identity = profile.integration_profile.sha256_identity(forged_result)
        try:
            forged_context = ers.stage_pending_review(
                forged_result,
                intent,
                expected_relative_path=packet_target,
                mainframe_root=str(sandbox),
                expected_executable_sha256=executable_id,
                render_packet=packet,
                payload=payload,
                observer_socket=str(socket_path),
            )
            forged_receipt = forged_context["point_of_use_context_receipt"]
            forged_receipt_id, forged_receipt_key_id = verify_receipt_independently(forged_receipt)
            check(forged_receipt["body"]["evaluation_time"] == forged_time, "observer_did_not_bind_mutated_time")
            forged_time_probe = {
                "request_mutated_after_contract_e": True,
                "contract_e_original_result_identity": contract_e_result_identity,
                "mutated_result_identity": forged_result_identity,
                "mutated_result_identity_differs": forged_result_identity != contract_e_result_identity,
                "original_contract_e_evaluation_time": evaluation_time,
                "mutated_evaluation_time": forged_time,
                "observer_receipt_signature_valid": True,
                "observer_receipt_identity": forged_receipt_id,
                "observer_receipt_key_id": forged_receipt_key_id,
                "accepted": True,
                "shadow_ready": forged_context["shadow_ready"],
                "execution_occurred": forged_context["execution_occurred"],
            }
        except Exception as exc:  # noqa: BLE001 - preserve the exact boundary code
            forged_time_probe = {
                "request_mutated_after_contract_e": True,
                "contract_e_original_result_identity": contract_e_result_identity,
                "mutated_result_identity": forged_result_identity,
                "mutated_result_identity_differs": forged_result_identity != contract_e_result_identity,
                "original_contract_e_evaluation_time": evaluation_time,
                "mutated_evaluation_time": forged_time,
                "accepted": False,
                "error": getattr(exc, "code", str(exc)),
            }
        sandbox_after = sorted(str(item.relative_to(sandbox)) for item in sandbox.rglob("*"))
        check(sandbox_before == [], "sandbox_not_empty_before")
        check(sandbox_after == [], "sandbox_mutated_after")

        hold_cases = {}
        evaluation_calls: list[Any] = []
        original_evaluate = profile.integration_profile.evaluate

        def counted_evaluate(*call_args: Any, **call_kwargs: Any):
            evaluation_calls.append(True)
            return original_evaluate(*call_args, **call_kwargs)

        profile.integration_profile.evaluate = counted_evaluate
        try:
            for case_id in ("PIPE02", "PIPE03"):
                node_case = decision_result["cases"][case_id]
                hold_expected = profile.expectation_for(node_case["ers"], core, consume_mod)
                try:
                    profile.shadow_gate(
                        contract_d_root=contract_d_root,
                        decision=node_case["ers"],
                        expected=hold_expected,
                        authority_state=authority_state,
                        execution_intent=intent,
                        evaluation_time=evaluation_time,
                    )
                except Exception as exc:  # noqa: BLE001 - record exact HOLD result
                    hold_cases[case_id] = getattr(exc, "code", str(exc))
                else:
                    raise AssertionError(case_id + ":hold_reached_contract_e")
        finally:
            profile.integration_profile.evaluate = original_evaluate
        check(all(code == "decision_not_candidate:hold" for code in hold_cases.values()), "pipe02_pipe03_hold_changed")
        check(evaluation_calls == [], "held_case_reached_contract_e_evaluator")

        disposition = (
            "FALSIFIED_POINT_OF_USE_CONTEXT_EVALUATION_TIME_PROVENANCE"
            if forged_time_probe["accepted"]
            else "SUPPORTED_FOR_CONTROLLED_LOCAL_CONTEXT_RECEIPT_COMPOSITION"
        )
        receipt_out = {
            "schema": "ers-point-of-use-context-provenance-composition-receipt/1",
            "experiment_id": "ERS-POU-CTX-20260921-01",
            "disposition": disposition,
            "subjects": {
                "apparatus_pr127_base": APPARATUS_PR127,
                "apparatus_pr128_base": APPARATUS_PR128,
                "decision_successor": DECISION,
                "cal_pipeline_v3": CAL_V3,
                "contract_d": CONTRACT_D,
                "contract_e_profile": CONTRACT_E,
                "contract_c_consumer": CONTRACT_C_CONSUMER,
                "ers_rc3_preserved": ERS_RC3,
                "ers_render_bound_successor": ERS_RC4,
                "ers_preregistration": ERS_PREREG,
                "ers_rc5_frozen_successor": ERS_RC5,
                "ers_rc5_tree": git(ers_root, "rev-parse", "HEAD^{tree}"),
            },
            "contract_e_compatibility": {
                "schema": compatibility_probe["schema"],
                "input_identity_count": len(compatibility_probe["input_identities"]),
                "variable_length_intent_accepted": True,
                "intent_identity": compatibility_identity,
                "contract_e_source_changed": False,
            },
            "pipe01": {
                "decision_semantic_identity": decision_id,
                "claim_content_sha256": CLAIM_CONTENT_ID,
                "render_packet_schema": packet["schema"],
                "render_packet_identity": packet_id,
                "payload_identity": payload_id,
                "pre_state_identity": pre_state["state_sha256"],
                "executable_identity": executable_id,
                "execution_intent_identity": ers._render_bound.execution_intent_identity(intent),
                "execution_intent_input_identities": intent["input_identities"],
                "contract_e_result_identity": contract_e_result_identity,
                "ers_shadow_result_identity": ers._render_bound._base.sha256_identity(positive),
                "shadow_ready": positive["shadow_ready"],
                "execution_occurred": positive["execution_occurred"],
                "sandbox_before": sandbox_before,
                "sandbox_after": sandbox_after,
            },
            "context_receipt": {
                "schema": body["schema"],
                "identity": receipt_id,
                "issuer_id": body["issuer_id"],
                "issuer_key_id": independent_key_id,
                "signature_independently_verified": True,
                "body_identity_independently_recomputed": True,
                "evaluation_time_source_id": body["observations"]["evaluation_time_source_id"],
                "authority_state_source_id": body["observations"]["authority_state_source_id"],
                "observer_clock_source_id": body["observations"]["observer_clock_source_id"],
                "authority_state_identity": body["authority_state_identity"],
                "evaluation_time": body["evaluation_time"],
                "observed_at": body["observations"]["observed_at"],
                "freshness_age_seconds": age_seconds,
                "signed_receipt": receipt,
            },
            "caller_selected_time_falsifier": forged_time_probe,
            "held_cases": {
                case_id: {"decision": hold_cases[case_id], "contract_e_evaluate_calls": 0}
                for case_id in ("PIPE02", "PIPE03")
            },
            "supported_claim_and_contract_d": {
                "cases": supported_cases,
                "supported_policy_byte_behavior_compatible": True,
                "released_contract_d_still_rejects_ers_as_unknown_effect_type": True,
            },
            "upstream_bytes_changed": {
                "decision": False,
                "cal_pipeline_v3": False,
                "released_contract_d": False,
                "contract_e_profile": False,
                "frozen_ers_rc3": False,
                "render_bound_ers_rc4": False,
            },
            "execution_and_mutation": {
                "executor_included": False,
                "executor_invoked": False,
                "pending_review_write": False,
                "real_mainframe_mutation": False,
                "contract_d_effect_registration": False,
                "release_or_promotion": False,
            },
            "open_blockers": [
                "trusted point-of-use authority-state provenance",
                "trusted evaluation-time provenance",
                "released Contract D ERS effect registration",
                "Contract E production authorization",
                "real executor behavior",
                "filesystem write atomicity and recovery semantics",
            ],
        }
        if args.output:
            args.output.write_text(json.dumps(receipt_out, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(receipt_out, indent=2))
    finally:
        observer.terminate()
        try:
            observer.wait(timeout=2)
        except subprocess.TimeoutExpired:
            observer.kill()
            observer.wait(timeout=2)
        tmp.cleanup()


if __name__ == "__main__":
    main()
