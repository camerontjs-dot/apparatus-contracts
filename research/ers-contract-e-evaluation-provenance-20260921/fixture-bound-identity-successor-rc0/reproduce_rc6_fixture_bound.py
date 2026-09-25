from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import importlib.util
import json
import os
import platform
import secrets
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

import jsonschema
import rfc8785
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EXPERIMENT_ID = "ERS-EVAL-TIME-PROV-20260922-05"
APPARATUS_PREREG = "dcdd10355e2f885273d843eef6e345bafca95faa"
RECEIPT_CONTRACT_PREREG = "077ccf6d386526bda258b3e90bd43e153c4c04c5"
CONTRACT_E = "b153dcc4434cbe8a98616a9e410c6125378144c7"
CONTRACT_D = "298a1a0f7b7b6d7712e11200d04faec3e1ca169b"
DECISION = "816374379ba7eb23f5bfdadaf203b7e287c052db"
CAL_V3 = "ffc43d4e89f5b1f7748e9cde0fa1efc7db47b463"
CONTRACT_C_CONSUMER = "12e7e640b229619501960b1b89cf4716d8d985b3"
ERS_RC5 = "099f84700f28e118734f1ca74feb977da1c4cf17"
ERS_RC4 = "022fcb58e14864aa173f447fa0c18dd2362b41b0"
ERS_RC3 = "319e325cdf678673fae645a70e3e34afb7dddef0"
PROVENANCE_PROFILE = "3934423b1a97ad1b099057c40fe8014e5dd08c97"
TRANSCRIPT_SCHEMA_BLOB = "b85b38ce95263e348d2ebd1293f76ffc87adcf6d"
ERS_RECEIPT_RELATIVE_PATH = Path(
    "research/ers-contract-e-evaluation-transcript-rc6-receipt-contract-successor-20260923/FREEZE_RECEIPT.json"
)
CLAIM_CONTENT_ID = "sha256:fe9a393b0c31f7e2f200cbefc08d9293e364f8a0810865a73003ec3502c387d0"
PIPE01_DECISION_ID = "decision:sha256:3427c5cb6692bf7358c13e47628ef7a91a0c53e78affc58f2ae60173daffcc15"
ISSUER_KEY_ID = "sha256:e7f4581c2d58eecd0279f895cf3dd49df3098d092fa1e083731d802fcd1db259"
ISSUER_PUBLIC_KEY_PEM = b"""-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEAKlHbYp+oTHO3iaBSwhqyYW+ybobI/iFP4iDXESQm0Tg=
-----END PUBLIC KEY-----
"""
ACTIVE_MATRIX_PATH: Path | None = None


class QualificationError(RuntimeError):
    pass


def check(condition: bool, label: str) -> None:
    if not condition:
        raise QualificationError(label)


def sha256_identity(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return rfc8785.dumps(value) + b"\n"


def independent_identity(value: Any) -> str:
    return sha256_identity(canonical_bytes(value))


def git(path: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(path), *args], text=True).strip()


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise QualificationError("module_load_failed:" + str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def utc_text(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace(
        "+00:00", "Z"
    )


def sandbox_snapshot(root: Path) -> dict[str, Any]:
    if not root.is_dir():
        raise QualificationError("sandbox_root_missing_or_not_directory")
    stat_value = root.stat()
    entries = []
    for child in sorted(root.rglob("*"), key=lambda value: value.as_posix()):
        relative = child.relative_to(root).as_posix()
        if child.is_symlink():
            entries.append({"path": relative, "kind": "symlink", "target": os.readlink(child)})
        elif child.is_file():
            raw = child.read_bytes()
            entries.append({"path": relative, "kind": "file", "bytes": len(raw), "sha256": sha256_identity(raw)})
        elif child.is_dir():
            entries.append({"path": relative, "kind": "directory"})
        else:
            entries.append({"path": relative, "kind": "other"})
    return {
        "path": str(root.resolve()),
        "device": stat_value.st_dev,
        "inode": stat_value.st_ino,
        "mode": stat_value.st_mode,
        # RFC 8785 intentionally rejects integers outside the IEEE-754 safe
        # range; preserve exact nanoseconds as a decimal string in receipts.
        "mtime_ns": str(stat_value.st_mtime_ns),
        "entries": entries,
    }


def independent_verify_response(response: dict[str, bytes], expected_key_id: str) -> dict[str, Any]:
    request_raw = response["request_bytes"]
    result_raw = response["result_bytes"]
    transcript_raw = response["transcript_bytes"]
    request = json.loads(request_raw.decode("utf-8"))
    result = json.loads(result_raw.decode("utf-8"))
    transcript = json.loads(transcript_raw.decode("utf-8"))
    check(canonical_bytes(request) == request_raw, "independent_request_not_canonical")
    check(canonical_bytes(result) == result_raw, "independent_result_not_canonical")
    check(canonical_bytes(transcript) == transcript_raw, "independent_transcript_not_canonical")
    body = transcript["body"]
    check(body["contract_e_request_sha256"] == sha256_identity(request_raw), "independent_request_digest_mismatch")
    check(body["contract_e_result_sha256"] == sha256_identity(result_raw), "independent_result_digest_mismatch")
    check(result["authorization"]["request"] == request, "independent_request_result_mismatch")
    public_key = serialization.load_pem_public_key(ISSUER_PUBLIC_KEY_PEM)
    public_key.verify(
        base64.b64decode(transcript["signature"]["value"], validate=True),
        canonical_bytes(body),
    )
    actual_key_id = sha256_identity(
        public_key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )
    check(actual_key_id == expected_key_id == ISSUER_KEY_ID, "independent_issuer_identity_mismatch")
    return {
        "request": request,
        "result": result,
        "transcript": transcript,
        "request_sha256": sha256_identity(request_raw),
        "result_sha256": sha256_identity(result_raw),
        "transcript_sha256": sha256_identity(transcript_raw),
        "issuer_key_id": actual_key_id,
    }


def response_from_shadow_result(value: dict[str, Any]) -> dict[str, bytes]:
    return {
        "request_bytes": base64.b64decode(value["contract_e_request_bytes_base64"], validate=True),
        "result_bytes": base64.b64decode(value["contract_e_result_bytes_base64"], validate=True),
        "transcript_bytes": base64.b64decode(value["contract_e_transcript_bytes_base64"], validate=True),
    }


def matrix_rejection(
    label: str,
    attempt: Callable[[], Any],
    matrix: dict[str, Any],
    *,
    expected_error: str,
) -> bool:
    try:
        value = attempt()
    except Exception as exc:  # capture exact fail-closed boundary
        error = getattr(exc, "code", None)
        matched = error == expected_error
        matrix[label] = {
            "rejected_before_shadow_ready": matched,
            "error": error if isinstance(error, str) else str(exc),
            "expected_error": expected_error,
            "error_type": type(exc).__name__,
        }
        if ACTIVE_MATRIX_PATH is not None:
            ACTIVE_MATRIX_PATH.write_bytes(canonical_bytes(matrix))
        if not matched:
            raise QualificationError(
                f"unexpected_rejection_boundary:{label}:expected={expected_error}:actual={error}"
            ) from exc
        return True
    matrix[label] = {
        "rejected_before_shadow_ready": False,
        "unexpected_value_type": type(value).__name__,
        "unexpected_shadow_ready": value.get("shadow_ready") if isinstance(value, dict) else None,
    }
    if ACTIVE_MATRIX_PATH is not None:
        ACTIVE_MATRIX_PATH.write_bytes(canonical_bytes(matrix))
    return False


def run_raw_supervisor_request(socket_path: Path, request: dict[str, Any]) -> dict[str, Any]:
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
        connection.settimeout(10.0)
        connection.connect(str(socket_path))
        connection.sendall(canonical_bytes(request))
        raw = connection.makefile("rb").readline(4_194_305)
    if len(raw) > 4_194_304 or not raw.endswith(b"\n"):
        raise QualificationError("invalid_raw_supervisor_response")
    return json.loads(raw.decode("utf-8"))


def start_supervisor(
    *,
    ers_root: Path,
    contract_e_root: Path,
    contract_d_root: Path,
    private_key: Path,
    socket_path: Path,
) -> subprocess.Popen[str]:
    rc6_slice = ers_root / "pipeline_slices/contract-e-shadow-rc6-evaluation-transcript"
    rc5_slice = ers_root / "pipeline_slices/contract-e-shadow-rc5-context-receipt"
    env = os.environ.copy()
    env["PYTHONPATH"] = os.pathsep.join(
        [str(rc6_slice), str(rc5_slice), str(ers_root), env.get("PYTHONPATH", "")]
    )
    return subprocess.Popen(
        [
            sys.executable,
            str(rc6_slice / "harness/qualification_supervisor.py"),
            "--socket-path", str(socket_path),
            "--contract-e-root", str(contract_e_root),
            "--contract-d-root", str(contract_d_root),
            "--private-key-file", str(private_key),
        ],
        cwd=str(ers_root),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )


def wait_for_socket(process: subprocess.Popen[str], socket_path: Path) -> None:
    deadline = time.monotonic() + 5.0
    while time.monotonic() < deadline:
        if socket_path.exists():
            return
        if process.poll() is not None:
            detail = process.stderr.read() if process.stderr else ""
            raise QualificationError("supervisor_start_failed:" + detail[-600:])
        time.sleep(0.01)
    raise QualificationError("supervisor_socket_not_ready")


def file_digest(path: Path) -> str:
    return sha256_identity(path.read_bytes())


def run_matrix(args: argparse.Namespace, output_root: Path) -> dict[str, Any]:
    global ACTIVE_MATRIX_PATH
    ACTIVE_MATRIX_PATH = output_root / "MATRIX_PROGRESS.json"
    ers_root = args.ers_root.resolve()
    decision_root = args.decision_root.resolve()
    contract_e_root = args.contract_e_root.resolve()
    contract_d_root = args.contract_d_root.resolve()
    consumer_root = args.consumer_root.resolve()
    fixtures = args.fixtures.resolve()
    sandbox = args.sandbox_root.resolve()
    schema_path = args.transcript_schema.resolve()
    provenance_profile = args.provenance_profile.resolve()
    private_key = args.issuer_private_key.resolve()

    expected_pins = {
        "decision": (decision_root, DECISION),
        "contract_e": (contract_e_root, CONTRACT_E),
        "contract_d": (contract_d_root, CONTRACT_D),
        "contract_c_consumer": (consumer_root, CONTRACT_C_CONSUMER),
    }
    for label, (path, expected) in expected_pins.items():
        check(git(path, "rev-parse", "HEAD") == expected, "wrong_frozen_" + label)
        check(not git(path, "status", "--porcelain"), "dirty_frozen_" + label)
    check(git(ers_root, "merge-base", "--is-ancestor", ERS_RC5, "HEAD") == "", "ers_rc5_not_ancestor")
    check(git(ers_root, "merge-base", "--is-ancestor", ERS_RC4, "HEAD") == "", "ers_rc4_not_ancestor")
    check(git(ROOT, "merge-base", "--is-ancestor", APPARATUS_PREREG, "HEAD") == "", "preregistration_not_ancestor")
    check(git(ROOT, "merge-base", "--is-ancestor", RECEIPT_CONTRACT_PREREG, "HEAD") == "", "receipt_contract_preregistration_not_ancestor")
    check(git(ROOT, "cat-file", "-t", CAL_V3) == "commit", "cal_v3_object_missing")
    check(git(provenance_profile.parents[1], "rev-parse", "HEAD") == PROVENANCE_PROFILE, "wrong_provenance_profile")
    check(not git(provenance_profile.parents[1], "status", "--porcelain"), "dirty_provenance_profile")
    check(git(ers_root, "status", "--porcelain") == "", "dirty_frozen_ers_candidate")
    check(schema_path.is_file(), "frozen_transcript_schema_missing")
    check(git(ROOT, "hash-object", str(schema_path)) == TRANSCRIPT_SCHEMA_BLOB, "transcript_schema_blob_mismatch")

    freeze_receipt_path = ers_root / ERS_RECEIPT_RELATIVE_PATH
    freeze_receipt = json.loads(freeze_receipt_path.read_text(encoding="utf-8"))
    check("implementation_source_commit" not in freeze_receipt, "noncanonical_ers_source_commit_alias")
    check(freeze_receipt["implementation"]["source_commit"] == args.ers_source_commit, "ers_source_commit_freeze_mismatch")
    ers_source_tree = git(ers_root, "rev-parse", f"{args.ers_source_commit}^{{tree}}")
    check(freeze_receipt["implementation"]["source_tree"] == ers_source_tree, "ers_source_tree_freeze_mismatch")
    check(freeze_receipt["apparatus"]["scientific_preregistration"]["commit"] == APPARATUS_PREREG, "ers_receipt_preregistration_mismatch")
    check(freeze_receipt["apparatus"]["transcript_schema_blob"] == TRANSCRIPT_SCHEMA_BLOB, "ers_receipt_transcript_schema_mismatch")
    check(git(ers_root, "merge-base", "--is-ancestor", args.ers_source_commit, "HEAD") == "", "ers_source_not_ancestor")
    app_freeze = json.loads(args.apparatus_freeze_receipt.read_text(encoding="utf-8"))
    check(app_freeze["apparatus_candidate_source_commit"] == args.apparatus_source_commit, "apparatus_source_commit_freeze_mismatch")
    check("implementation_source_commit" not in app_freeze, "noncanonical_ers_source_commit_alias")
    check(app_freeze["ers_candidate"]["source_commit"] == args.ers_source_commit, "apparatus_ers_source_commit_mismatch")
    check(app_freeze["ers_candidate"]["source_tree"] == ers_source_tree, "apparatus_ers_source_tree_mismatch")
    check(app_freeze["preregistration"]["frozen_head"] == APPARATUS_PREREG, "apparatus_preregistration_mismatch")
    check(app_freeze["preregistration"]["transcript_schema_blob"] == TRANSCRIPT_SCHEMA_BLOB, "apparatus_transcript_schema_mismatch")
    check(freeze_receipt["issuer"]["public_key_identity"] == app_freeze["issuer"]["public_key_identity"], "receipt_issuer_key_mismatch")
    check(freeze_receipt["issuer"]["public_key_identity"] == ISSUER_KEY_ID, "frozen_issuer_key_id_changed")
    ers_freeze_commit = app_freeze["ers_candidate"]["freeze_receipt_commit"]
    ers_freeze_blob = app_freeze["ers_candidate"]["freeze_receipt_blob"]
    check(git(ers_root, "rev-parse", "HEAD") == ers_freeze_commit, "ers_freeze_receipt_commit_mismatch")
    check(git(ers_root, "rev-parse", f"{ers_freeze_commit}:{ERS_RECEIPT_RELATIVE_PATH.as_posix()}") == ers_freeze_blob, "ers_freeze_receipt_blob_mismatch")

    preflight_path = args.preflight_pass_receipt.resolve()
    preflight_raw = preflight_path.read_bytes()
    preflight = json.loads(preflight_raw.decode("utf-8"))
    check(preflight.get("schema") == "ers-evaluation-provenance-receipt-consistency-preflight/1", "preflight_receipt_schema_mismatch")
    check(preflight.get("status") == "PASS", "receipt_consistency_preflight_not_pass")
    check(preflight.get("experiment_id") == EXPERIMENT_ID, "preflight_experiment_id_mismatch")
    check(preflight.get("input_receipts", {}).get("ers", {}).get("freeze_receipt_commit") == ers_freeze_commit, "preflight_ers_freeze_commit_mismatch")
    check(preflight.get("input_receipts", {}).get("ers", {}).get("git_blob") == ers_freeze_blob, "preflight_ers_freeze_blob_mismatch")
    app_preflight_input = preflight.get("input_receipts", {}).get("apparatus", {})
    check(app_preflight_input.get("source_commit") == args.apparatus_source_commit, "preflight_apparatus_source_commit_mismatch")
    check(app_preflight_input.get("git_blob") == git(ROOT, "hash-object", str(args.apparatus_freeze_receipt)), "preflight_apparatus_receipt_blob_mismatch")
    check(app_preflight_input.get("sha256_bytes") == sha256_identity(args.apparatus_freeze_receipt.read_bytes()), "preflight_apparatus_receipt_sha256_mismatch")
    preflight_checks = preflight.get("compared_values")
    check(isinstance(preflight_checks, list) and bool(preflight_checks), "preflight_compared_values_missing")
    check(all(isinstance(item, dict) and item.get("passed") is True for item in preflight_checks), "preflight_contains_failed_comparison")
    instrumentation = preflight.get("instrumentation", {})
    check(instrumentation.get("contract_e_evaluation_calls") == 0, "contract_e_called_during_preflight")
    check(instrumentation.get("supervisor_process_launches") == 0, "supervisor_started_during_preflight")
    check(instrumentation.get("candidate_runtime_imports") == [], "candidate_runtime_imported_during_preflight")
    check(instrumentation.get("network_attempts") == 0, "network_used_during_preflight")
    app_receipt_relative = args.apparatus_freeze_receipt.resolve().relative_to(ROOT).as_posix()
    preflight_relative = preflight_path.relative_to(ROOT).as_posix()
    check(git(ROOT, "rev-parse", f"HEAD:{app_receipt_relative}") == git(ROOT, "hash-object", str(args.apparatus_freeze_receipt)), "apparatus_freeze_receipt_not_in_frozen_head")
    check(git(ROOT, "rev-parse", f"HEAD:{preflight_relative}") == git(ROOT, "hash-object", str(preflight_path)), "preflight_pass_not_in_frozen_head")

    compatibility_profile_path = contract_e_root / "docs/research/contract-e/ers-point-of-use-crossrepo-rc2-20260919/contract_e_profile.py"
    profile = load_module("ers_rc6_run_contract_e_profile", compatibility_profile_path)
    compatibility = {}
    for count in (5, 7):
        probe = {
            "schema": "execution-intent-candidate-v1",
            "executable_sha256": "sha256:" + "1" * 64,
            "entry_point": "harness.context_bound_shadow:stage_pending_review",
            "arguments": [],
            "input_identities": ["sha256:" + f"{index:064x}" for index in range(1, count + 1)],
            "environment_constraints": {},
            "side_effect_targets": ["20_live/epistemic-audit/pending-review/probe.md"],
        }
        compatibility[str(count)] = profile.integration_profile.execution_intent_identity(probe)
    check(len(compatibility) == 2, "contract_e_variable_length_intent_probe_failed")

    baseline = load_module(
        "ers_rc6_frozen_render_bound_reproduction",
        ROOT / "research/ers-render-bound-shadow-composition-20260921/reproduce.py",
    )
    decision_result = baseline.run_decision_successor(
        decision_root=decision_root,
        fixtures=fixtures,
        consumer_root=consumer_root,
        contract_d_root=contract_d_root,
    )
    core, consume_mod = profile.install_research_effect_profile(contract_d_root)
    supported_cases = {}
    for case_id in ("PIPE01", "PIPE02", "PIPE03"):
        node_case = decision_result["cases"][case_id]
        stored_d = (fixtures / case_id / "contract-d.json").read_bytes()
        supported = base64.b64decode(node_case["supported_canonical_b64"])
        check(node_case["supported_equals_frozen"], case_id + ":supported_decision_behavior_changed")
        check(stored_d == supported, case_id + ":supported_contract_d_bytes_changed")
        released = node_case["released_ers_contract_d"]
        check(released["accepted"] is False and "unknown_effect_type" in released["message"], case_id + ":released_d_rejection_changed")
        supported_cases[case_id] = {
            "supported_contract_d_sha256": sha256_identity(supported),
            "matches_frozen_behavior": True,
            "released_contract_d_rejection": "unknown_effect_type",
        }
    pipe01 = decision_result["cases"]["PIPE01"]
    decision = pipe01["ers"]
    decision_identity = core.semantic_identity(decision)
    check(decision_identity == PIPE01_DECISION_ID, "pipe01_native_decision_identity_changed")
    check(pipe01["target"]["content_sha256"] == CLAIM_CONTENT_ID, "pipe01_claim_content_identity_changed")
    check(decision["evaluation"]["disposition"] == "clear", "pipe01_native_ers_decision_changed")
    for case_id in ("PIPE02", "PIPE03"):
        check(decision_result["cases"][case_id]["ers"]["evaluation"]["disposition"] == "hold", case_id + ":hold_behavior_changed")

    rc6_slice = ers_root / "pipeline_slices/contract-e-shadow-rc6-evaluation-transcript"
    rc5_slice = ers_root / "pipeline_slices/contract-e-shadow-rc5-context-receipt"
    for path in reversed((rc6_slice, rc5_slice, ers_root)):
        sys.path.insert(0, str(path))
    from harness import context_bound_shadow as ers  # noqa: E402
    from harness import evaluation_transcript, render_bound_shadow, render_packet, supervisor_client  # noqa: E402

    check(evaluation_transcript.ISSUER_KEY_ID == ISSUER_KEY_ID, "frozen_issuer_key_id_changed")
    public_key = serialization.load_pem_public_key(evaluation_transcript.ISSUER_PUBLIC_KEY_PEM)
    actual_issuer_key_id = sha256_identity(
        public_key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )
    check(actual_issuer_key_id == ISSUER_KEY_ID, "pinned_public_key_identity_mismatch")

    packet = render_packet.freeze_render_packet(baseline.fixture_snapshot())
    payload = render_packet.render_pending_review(packet)
    packet_identity = render_packet.render_packet_identity(packet)
    payload_identity = render_packet.rendered_payload_identity(packet)
    check(payload == baseline.independent_render(packet), "independent_render_disagreement")
    check(packet_identity == independent_identity(packet), "independent_render_packet_identity_mismatch")
    check(payload_identity == sha256_identity(payload), "independent_payload_identity_mismatch")
    check(payload.endswith(b"\n"), "payload_terminal_newline_changed")
    check((fixtures / "PIPE01").is_dir(), "pipe01_fixture_missing")

    sandbox_before = sandbox_snapshot(sandbox)
    check(sandbox_before["entries"] == [], "sandbox_not_empty_before_decisive_run")
    target_relative_path = packet["render"]["target_relative_path"]
    pre_state = render_bound_shadow._base.observe_pre_state(sandbox, target_relative_path)
    executable_sha256 = sha256_identity((rc6_slice / "harness/context_bound_shadow.py").read_bytes())
    intent = render_bound_shadow.build_execution_intent(
        decision_identity=decision_identity,
        executable_sha256=executable_sha256,
        claim_id="ROOT",
        claim_content_sha256=CLAIM_CONTENT_ID,
        pre_state=pre_state,
        relative_path=target_relative_path,
        render_packet=packet,
    )
    expected_five = [decision_identity, CLAIM_CONTENT_ID, pre_state["state_sha256"], packet_identity, payload_identity]
    check(intent["input_identities"] == expected_five, "five_inherited_input_identities_changed")
    check(profile.integration_profile.execution_intent_identity(intent) == render_bound_shadow.execution_intent_identity(intent), "frozen_contract_e_intent_identity_disagrees")
    intent_identity = independent_identity(intent)
    check(intent_identity == render_bound_shadow.execution_intent_identity(intent), "independent_execution_intent_identity_mismatch")
    authority_state = profile.make_authority_state(
        profile.target_reference_for_intent(intent),
        valid_from="2026-09-20T00:00:00Z",
        valid_until="2027-01-01T00:00:00Z",
    )
    authority_state_identity = profile.integration_profile.authority_state_identity(authority_state)
    check(authority_state_identity == authority_state["authority_state_id"], "authority_state_fixture_identity_mismatch")

    # Reassert that native HOLD cases stop before Contract E is invoked. The
    # temporary counter observes only the frozen evaluator entry point.
    hold_cases: dict[str, Any] = {}
    hold_evaluations: list[dict[str, Any]] = []
    original_evaluate = profile.integration_profile.evaluate

    def count_hold_evaluation(state_arg: dict[str, Any], request_arg: dict[str, Any]) -> dict[str, Any]:
        hold_evaluations.append({"state": state_arg, "request": request_arg})
        return original_evaluate(state_arg, request_arg)

    profile.integration_profile.evaluate = count_hold_evaluation
    try:
        for case_id in ("PIPE02", "PIPE03"):
            held_decision = decision_result["cases"][case_id]["ers"]
            held_intent = render_bound_shadow.build_execution_intent(
                decision_identity=core.semantic_identity(held_decision),
                executable_sha256=executable_sha256,
                claim_id="ROOT",
                claim_content_sha256=CLAIM_CONTENT_ID,
                pre_state=pre_state,
                relative_path=target_relative_path,
                render_packet=packet,
            )
            held_state = profile.make_authority_state(
                profile.target_reference_for_intent(held_intent),
                valid_from="2026-09-20T00:00:00Z",
                valid_until="2027-01-01T00:00:00Z",
            )
            held_expected = profile.expectation_for(
                held_decision, core, consume_mod
            )
            try:
                profile.shadow_gate(
                    contract_d_root=contract_d_root,
                    decision=held_decision,
                    expected=held_expected,
                    authority_state=held_state,
                    execution_intent=held_intent,
                    evaluation_time="2026-09-21T00:00:00Z",
                    target_reference=profile.target_reference_for_intent(held_intent),
                    trusted_decision_identity=core.semantic_identity(held_decision),
                )
            except Exception as exc:
                error = getattr(exc, "code", str(exc))
                if error != "decision_not_candidate:hold":
                    raise QualificationError(
                        f"{case_id}:unexpected_hold_boundary:{error}"
                    ) from exc
            else:
                raise QualificationError(f"{case_id}:hold_reached_shadow_gate_return")
            hold_cases[case_id] = {
                "decision_disposition": "hold",
                "gate_error": "decision_not_candidate:hold",
                "contract_evaluation_calls": len(hold_evaluations),
            }
            check(not hold_evaluations, case_id + ":hold_reached_contract_e")
    finally:
        profile.integration_profile.evaluate = original_evaluate

    matrix: dict[str, Any] = {}
    temp_runtime = tempfile.TemporaryDirectory(prefix="ers-rc6-supervisor-", dir="/private/tmp")
    runtime_root = Path(temp_runtime.name)
    socket_path = runtime_root / "qualification-supervisor.sock"
    process = start_supervisor(
        ers_root=ers_root,
        contract_e_root=contract_e_root,
        contract_d_root=contract_d_root,
        private_key=private_key,
        socket_path=socket_path,
    )
    matrix_started_at = utc_text(datetime.now(timezone.utc))
    try:
        wait_for_socket(process, socket_path)
        shadow = ers.stage_pending_review(
            decision,
            intent,
            authority_state,
            expected_relative_path=target_relative_path,
            mainframe_root=str(sandbox),
            expected_executable_sha256=executable_sha256,
            render_packet_value=packet,
            payload=payload,
            supervisor_socket=str(socket_path),
        )
        check(shadow.get("shadow_ready") is True, "authentic_pipe01_not_shadow_ready")
        check(shadow.get("execution_occurred") is False, "authentic_pipe01_execution_occurred")
        response_a = response_from_shadow_result(shadow)
        challenge_a = shadow["contract_e_challenge"]
        verified_a = evaluation_transcript.verify_evaluation_response(
            response_a,
            execution_intent=intent,
            expected_authority_state=authority_state,
            expected_challenge=challenge_a,
        )
        independent_a = independent_verify_response(response_a, ISSUER_KEY_ID)
        jsonschema.validate(
            verified_a["transcript"],
            json.loads(schema_path.read_text(encoding="utf-8")),
        )
        check(independent_a["request_sha256"] == verified_a["contract_e_request_sha256"], "independent_e_request_identity_disagreement")
        check(independent_a["result_sha256"] == verified_a["contract_e_result_sha256"], "independent_e_result_identity_disagreement")
        check(independent_a["transcript_sha256"] == verified_a["transcript_identity"], "independent_transcript_identity_disagreement")
        check(verified_a["execution_intent_identity"] == intent_identity, "transcript_intent_identity_changed")
        check(verified_a["authority_state_identity"] == authority_state_identity, "transcript_authority_state_identity_changed")
        matrix["authentic_pipe01"] = {
            "shadow_ready": True,
            "execution_occurred": False,
            "accepted": True,
            "frozen_transcript_schema_valid": True,
            "execution_intent_identity": intent_identity,
            "five_inherited_input_identities": expected_five,
        }
        matrix["control_metadata"] = {"first_evaluation_challenge": challenge_a}
        ACTIVE_MATRIX_PATH.write_bytes(canonical_bytes(matrix))

        def verify_then_shadow(
            candidate_response: dict[str, bytes],
            candidate_intent: dict[str, Any],
            candidate_state: dict[str, Any],
            candidate_challenge: str,
        ) -> dict[str, Any]:
            verified = evaluation_transcript.verify_evaluation_response(
                candidate_response,
                execution_intent=candidate_intent,
                expected_authority_state=candidate_state,
                expected_challenge=candidate_challenge,
            )
            return render_bound_shadow.stage_pending_review(
                verified["result"],
                candidate_intent,
                expected_relative_path=target_relative_path,
                mainframe_root=str(sandbox),
                current_authority_state_id=verified["authority_state_identity"],
                current_evaluation_time=verified["evaluation_time"],
                expected_executable_sha256=candidate_intent["executable_sha256"],
                render_packet=packet,
                payload=payload,
            )

        # RC5 falsifier: alter only result.request.evaluation_time by exactly +1s.
        mutated_time_result = json.loads(response_a["result_bytes"].decode("utf-8"))
        old_time = mutated_time_result["authorization"]["request"]["evaluation_time"]
        old_dt = datetime.fromisoformat(old_time[:-1] + "+00:00")
        new_time = utc_text(old_dt + timedelta(seconds=1))
        mutated_time_result["authorization"]["request"]["evaluation_time"] = new_time
        response_time_plus_one = dict(response_a)
        response_time_plus_one["result_bytes"] = canonical_bytes(mutated_time_result)
        matrix["control_metadata"]["rc5_time_substitution"] = {
            "old_evaluation_time": old_time,
            "mutated_evaluation_time": new_time,
            "contract_e_rerun": False,
        }
        check(
            matrix_rejection(
                "rc5_result_time_plus_one_second_without_rerun",
                lambda: verify_then_shadow(
                    response_time_plus_one,
                    intent,
                    authority_state,
                    challenge_a,
                ),
                matrix,
                expected_error="contract_e_result_sha256_mismatch",
            ),
            "rc6_falsified_by_time_substitution",
        )

        time.sleep(0.02)
        challenge_b = secrets.token_urlsafe(32)
        response_b = supervisor_client.evaluate_and_attest(
            str(socket_path),
            decision=decision,
            execution_intent=intent,
            authority_state=authority_state,
            challenge=challenge_b,
        )
        verified_b = evaluation_transcript.verify_evaluation_response(
            response_b,
            execution_intent=intent,
            expected_authority_state=authority_state,
            expected_challenge=challenge_b,
        )
        check(verified_b["evaluation_time"] > verified_a["evaluation_time"], "second_authentic_evaluation_not_later")
        matrix["control_metadata"]["authentic_evaluations_for_cross_pair"] = 2
        check(
            matrix_rejection(
                "cross_pair_result_a_transcript_b",
                lambda: verify_then_shadow(
                    {"request_bytes": response_b["request_bytes"], "result_bytes": response_a["result_bytes"], "transcript_bytes": response_b["transcript_bytes"]},
                    intent,
                    authority_state,
                    challenge_b,
                ),
                matrix,
                expected_error="contract_e_result_sha256_mismatch",
            ),
            "rc6_falsified_by_cross_pair_a_b",
        )
        check(
            matrix_rejection(
                "cross_pair_result_b_transcript_a",
                lambda: verify_then_shadow(
                    {"request_bytes": response_a["request_bytes"], "result_bytes": response_b["result_bytes"], "transcript_bytes": response_a["transcript_bytes"]},
                    intent,
                    authority_state,
                    challenge_a,
                ),
                matrix,
                expected_error="contract_e_result_sha256_mismatch",
            ),
            "rc6_falsified_by_cross_pair_b_a",
        )

        # Mutate one ASCII byte inside the result's intent identity; JSON remains valid.
        result_one_byte = bytearray(response_a["result_bytes"])
        marker = b'"execution_intent_identity":"sha256:'
        offset = response_a["result_bytes"].find(marker)
        check(offset >= 0, "result_intent_identity_marker_missing")
        digest_offset = offset + len(marker)
        original_byte = result_one_byte[digest_offset]
        result_one_byte[digest_offset] = ord("0") if original_byte != ord("0") else ord("1")
        response_one_byte = dict(response_a)
        response_one_byte["result_bytes"] = bytes(result_one_byte)
        check(
            matrix_rejection(
                "one_byte_contract_e_result_mutation",
                lambda: verify_then_shadow(
                    response_one_byte,
                    intent,
                    authority_state,
                    challenge_a,
                ),
                matrix,
                expected_error="contract_e_result_sha256_mismatch",
            ),
            "rc6_falsified_by_one_byte_result_mutation",
        )

        intent_b = copy.deepcopy(intent)
        intent_b["executable_sha256"] = "sha256:" + "e" * 64
        intent_b_identity = render_bound_shadow.execution_intent_identity(intent_b)
        authority_state_b = profile.make_authority_state(
            profile.target_reference_for_intent(intent_b),
            valid_from="2026-09-20T00:00:00Z",
            valid_until="2027-01-01T00:00:00Z",
        )
        challenge_c = secrets.token_urlsafe(32)
        response_c = supervisor_client.evaluate_and_attest(
            str(socket_path),
            decision=decision,
            execution_intent=intent_b,
            authority_state=authority_state_b,
            challenge=challenge_c,
        )
        verified_c = evaluation_transcript.verify_evaluation_response(
            response_c,
            execution_intent=intent_b,
            expected_authority_state=authority_state_b,
            expected_challenge=challenge_c,
        )
        check(verified_c["execution_intent_identity"] == intent_b_identity, "alternate_valid_intent_transcript_invalid")
        check(
            matrix_rejection(
                "wrong_execution_intent_transcript",
                lambda: verify_then_shadow(
                    response_c,
                    intent,
                    authority_state_b,
                    challenge_c,
                ),
                matrix,
                expected_error="transcript_intent_mismatch",
            ),
            "rc6_falsified_by_wrong_intent_transcript",
        )
        check(
            matrix_rejection(
                "wrong_authority_state_transcript",
                lambda: verify_then_shadow(
                    response_c,
                    intent_b,
                    authority_state,
                    challenge_c,
                ),
                matrix,
                expected_error="transcript_authority_state_mismatch",
            ),
            "rc6_falsified_by_wrong_authority_state_transcript",
        )

        # A fresh non-pinned key signs a schema-shaped transcript over the same exact body.
        wrong_key = Ed25519PrivateKey.generate()
        wrong_key_id = sha256_identity(
            wrong_key.public_key().public_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )
        wrong_issuer_transcript = json.loads(response_a["transcript_bytes"].decode("utf-8"))
        wrong_issuer_transcript["body"]["issuer_id"] = "ers-nonpinned-test-issuer"
        wrong_issuer_transcript["body"]["issuer_key_id"] = wrong_key_id
        wrong_issuer_transcript["signature"]["key_id"] = wrong_key_id
        wrong_issuer_transcript["signature"]["value"] = base64.b64encode(
            wrong_key.sign(canonical_bytes(wrong_issuer_transcript["body"]))
        ).decode("ascii")
        jsonschema.validate(wrong_issuer_transcript, json.loads(schema_path.read_text(encoding="utf-8")))
        response_wrong_issuer = dict(response_a)
        response_wrong_issuer["transcript_bytes"] = canonical_bytes(wrong_issuer_transcript)
        check(
            matrix_rejection(
                "correctly_shaped_wrong_ed25519_issuer",
                lambda: verify_then_shadow(
                    response_wrong_issuer,
                    intent,
                    authority_state,
                    challenge_a,
                ),
                matrix,
                expected_error="wrong_transcript_issuer",
            ),
            "rc6_falsified_by_wrong_issuer",
        )

        # Wait past the frozen 30-second bound; this is an authentic signed transcript.
        time.sleep(31.0)
        check(
            matrix_rejection(
                "stale_authentic_transcript",
                lambda: verify_then_shadow(
                    response_a,
                    intent,
                    authority_state,
                    challenge_a,
                ),
                matrix,
                expected_error="stale_transcript",
            ),
            "rc6_falsified_by_stale_transcript",
        )

        # Replaying a used challenge is rejected by the supervisor before another E call.
        replay_error = None
        try:
            supervisor_client.evaluate_and_attest(
                str(socket_path),
                decision=decision,
                execution_intent=intent,
                authority_state=authority_state,
                challenge=challenge_a,
            )
        except Exception as exc:
            replay_error = getattr(exc, "code", str(exc))
        matrix["replayed_challenge"] = {
            "rejected_before_contract_e": replay_error == "replayed_challenge",
            "error": replay_error,
        }
        ACTIVE_MATRIX_PATH.write_bytes(canonical_bytes(matrix))
        check(matrix["replayed_challenge"]["rejected_before_contract_e"], "replayed_challenge_not_rejected")

        # Also test the closed wire boundary with forbidden caller-supplied values.
        forbidden_request = supervisor_client.make_request(
            decision=decision,
            execution_intent=intent,
            authority_state=authority_state,
            challenge=secrets.token_urlsafe(32),
        )
        forbidden_request["evaluation_time"] = "2000-01-01T00:00:00Z"
        forbidden_request["contract_e_result"] = {"caller": "substituted"}
        forbidden_response = run_raw_supervisor_request(socket_path, forbidden_request)
        signature_parameters = set(__import__("inspect").signature(supervisor_client.evaluate_and_attest).parameters)
        api_shape_ok = (
            "evaluation_time" not in signature_parameters
            and "contract_e_result" not in signature_parameters
            and forbidden_response.get("ok") is False
            and forbidden_response.get("error") == "invalid_supervisor_request_shape"
        )
        matrix["caller_time_or_result_signing_path"] = {
            "normal_api_parameters": sorted(signature_parameters),
            "forbidden_wire_request_rejected": forbidden_response.get("error") == "invalid_supervisor_request_shape",
            "result": "NO_CALLER_CONTROLLED_TIME_OR_RESULT_PATH" if api_shape_ok else "FALSIFIED",
        }
        ACTIVE_MATRIX_PATH.write_bytes(canonical_bytes(matrix))
        check(api_shape_ok, "supervisor_api_exposes_caller_controlled_time_or_result")
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=3)
        if socket_path.exists():
            socket_path.unlink()
        temp_runtime.cleanup()

    sandbox_after = sandbox_snapshot(sandbox)
    check(sandbox_after == sandbox_before, "sandbox_changed_during_qualification")
    target_path = sandbox / target_relative_path
    check(not target_path.exists(), "pending_review_target_created_in_sandbox")

    matrix_complete = all(
        value.get("rejected_before_shadow_ready") is True
        for key, value in matrix.items()
        if key not in {"authentic_pipe01", "replayed_challenge", "caller_time_or_result_signing_path", "control_metadata"}
    )
    matrix_complete = matrix_complete and matrix["replayed_challenge"]["rejected_before_contract_e"]
    matrix_complete = matrix_complete and matrix["caller_time_or_result_signing_path"]["result"] == "NO_CALLER_CONTROLLED_TIME_OR_RESULT_PATH"
    disposition = (
        "SUPPORTED_FOR_CONTROLLED_LOCAL_ERS_EVALUATION_TRANSCRIPT_SHADOW_COMPOSITION"
        if matrix_complete and shadow["shadow_ready"] is True and shadow["execution_occurred"] is False
        else "FALSIFIED"
    )

    report = {
        "schema": "ers-contract-e-evaluation-provenance-result/1",
        "experiment_id": EXPERIMENT_ID,
        "disposition": disposition,
        "subjects": {
            "apparatus_preregistration": APPARATUS_PREREG,
            "receipt_contract_preregistration": RECEIPT_CONTRACT_PREREG,
            "apparatus_candidate_source_commit": args.apparatus_source_commit,
            "ers_rc5_base": ERS_RC5,
            "ers_candidate_source_commit": args.ers_source_commit,
            "contract_e": CONTRACT_E,
            "contract_d": CONTRACT_D,
            "decision": DECISION,
            "cal_pipeline_v3": CAL_V3,
            "contract_c_consumer": CONTRACT_C_CONSUMER,
            "provenance_profile": PROVENANCE_PROFILE,
            "transcript_schema_git_blob": TRANSCRIPT_SCHEMA_BLOB,
            "receipt_preflight": {
                "path": preflight_path.relative_to(ROOT).as_posix(),
                "git_blob": git(ROOT, "hash-object", str(preflight_path)),
                "sha256_bytes": sha256_identity(preflight_raw),
                "compared_value_count": len(preflight_checks),
                "contract_e_evaluation_calls": instrumentation["contract_e_evaluation_calls"],
            },
        },
        "pipe01": {
            "decision_identity": decision_identity,
            "claim_content_identity": CLAIM_CONTENT_ID,
            "execution_intent_identity": intent_identity,
            "execution_intent_input_identities": expected_five,
            "render_packet_identity": packet_identity,
            "rendered_payload_identity": payload_identity,
            "pre_state_identity": pre_state["state_sha256"],
            "shadow_ready": shadow["shadow_ready"],
            "execution_occurred": shadow["execution_occurred"],
        },
        "contract_e_evaluation": {
            "request_sha256": independent_a["request_sha256"],
            "result_sha256": independent_a["result_sha256"],
            "result_identity": verified_a["contract_e_result_identity"],
            "evaluation_time": verified_a["evaluation_time"],
            "transcript_sha256": independent_a["transcript_sha256"],
            "issuer_key_id": actual_issuer_key_id,
            "second_authentic_request_sha256": verified_b["contract_e_request_sha256"],
            "second_authentic_result_sha256": verified_b["contract_e_result_sha256"],
            "second_authentic_transcript_sha256": verified_b["transcript_identity"],
        },
        "pipe_hold_cases": hold_cases,
        "supported_claim_compatibility": supported_cases,
        "decisive_matrix": matrix,
        "sandbox": {"before": sandbox_before, "after": sandbox_after, "unchanged": True},
        "provenance_sidecars": {"status": "pending_generation"},
        "limitations": [
            "qualification-only local issuer and private-key custody",
            "same-user host compromise resistance not established",
            "OS clock correctness not established",
            "authority-state provenance not established",
            "Contract E production authorization not established",
            "released Contract D ERS effect registration not established",
            "no executor, pending-review write, filesystem atomicity, or recovery semantics",
            "no production mutation, release, merge, effect registration, or promotion",
            "provenance profile independent reconstruction remains separate",
        ],
        "matrix_started_at": matrix_started_at,
        "python_version": platform.python_version(),
        "rfc8785_version": rfc8785.__version__,
        "cryptography_version": __import__("cryptography").__version__,
        "jsonschema_version": jsonschema.__version__,
    }
    report["_sidecar_inputs"] = {
        "decision": decision,
        "execution_intent": intent,
        "authority_state": authority_state,
        "render_packet": packet,
        "payload": payload,
        "shadow_result": shadow,
        "response": response_a,
        "decision_identity": decision_identity,
        "intent_identity": intent_identity,
        "authority_state_identity": authority_state_identity,
        "packet_identity": packet_identity,
        "payload_identity": payload_identity,
        "pre_state_identity": pre_state["state_sha256"],
        "profile": profile,
        "core": core,
        "consumer_root": consumer_root,
        "ers_root": ers_root,
        "ers_source_commit": args.ers_source_commit,
        "app_source_commit": args.apparatus_source_commit,
        "contract_e_root": contract_e_root,
        "contract_d_root": contract_d_root,
        "decision_root": decision_root,
        "schema_path": schema_path,
        "provenance_profile": provenance_profile,
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ers-root", required=True, type=Path)
    parser.add_argument("--ers-source-commit", required=True)
    parser.add_argument("--apparatus-source-commit", required=True)
    parser.add_argument("--apparatus-freeze-receipt", required=True, type=Path)
    parser.add_argument("--preflight-pass-receipt", required=True, type=Path)
    parser.add_argument("--decision-root", required=True, type=Path)
    parser.add_argument("--contract-e-root", required=True, type=Path)
    parser.add_argument("--contract-d-root", required=True, type=Path)
    parser.add_argument("--consumer-root", required=True, type=Path)
    parser.add_argument("--fixtures", required=True, type=Path)
    parser.add_argument("--sandbox-root", required=True, type=Path)
    parser.add_argument("--transcript-schema", required=True, type=Path)
    parser.add_argument("--provenance-profile", required=True, type=Path)
    parser.add_argument("--issuer-private-key", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    output_root = args.output.resolve()
    if output_root.exists():
        raise SystemExit("output_path_must_not_exist")
    output_root.mkdir(parents=True)
    running = {
        "schema": "ers-contract-e-evaluation-provenance-run-state/1",
        "experiment_id": EXPERIMENT_ID,
        "state": "active",
        "decisive_result_observed_before_freeze": False,
        "output_path": str(output_root),
    }
    (output_root / "RUNNING.json").write_bytes(canonical_bytes(running))
    try:
        report = run_matrix(args, output_root)
        sidecars = build_and_validate_sidecars(report, report.pop("_sidecar_inputs"), output_root)
        report["provenance_sidecars"] = sidecars
        (output_root / "RESULT.json").write_bytes(canonical_bytes(report))
        (output_root / "RUNNING.json").unlink()
        print(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2))
        return 0 if report["disposition"].startswith("SUPPORTED_") else 2
    except Exception as exc:
        progress_path = output_root / "MATRIX_PROGRESS.json"
        progress = {}
        if progress_path.is_file():
            try:
                progress = json.loads(progress_path.read_text(encoding="utf-8"))
            except Exception:
                progress = {"unreadable_progress_file": True}
        falsified = any(
            isinstance(value, dict) and value.get("unexpected_shadow_ready") is True
            for value in progress.values()
        )
        block_markers = (
            "wrong_frozen_", "dirty_frozen_", "wrong_provenance_profile",
            "transcript_schema_blob_mismatch", "frozen_ers_candidate",
            "preregistration_not_ancestor", "ers_rc5_not_ancestor",
            "ers_rc4_not_ancestor", "sandbox_root_missing", "sandbox_not_empty",
            "private_key", "missing", "unavailable", "not_found",
        )
        blocked = isinstance(exc, (FileNotFoundError, ModuleNotFoundError, PermissionError)) or any(
            marker in str(exc) for marker in block_markers
        )
        failure = {
            "schema": "ers-contract-e-evaluation-provenance-failure/1",
            "experiment_id": EXPERIMENT_ID,
            "disposition": "FALSIFIED" if falsified else ("BLOCKED" if blocked else "INCONCLUSIVE"),
            "error_type": type(exc).__name__,
            "error": str(exc),
            "output_path": str(output_root),
            "decisive_result_observed_before_freeze": False,
            "matrix_progress": progress,
        }
        (output_root / "FAILURE.json").write_bytes(canonical_bytes(failure))
        print(json.dumps(failure, ensure_ascii=False, sort_keys=True, indent=2), file=sys.stderr)
        return 3


def build_and_validate_sidecars(report: dict[str, Any], inputs: dict[str, Any], output_root: Path) -> dict[str, Any]:
    """Emit exact run artifacts and the two required profile-linked attestations."""

    profile_root: Path = inputs["provenance_profile"]
    case = output_root / "sidecars" / "ers-evaluation-transcript-rc6"
    artifacts_dir = case / "artifacts"
    attestations_dir = case / "attestations"
    artifacts_dir.mkdir(parents=True)
    attestations_dir.mkdir()
    response = inputs["response"]
    shadow = inputs["shadow_result"]
    material = {
        "execution-intent": canonical_bytes(inputs["execution_intent"]),
        "authority-state": canonical_bytes(inputs["authority_state"]),
        "contract-e-request": response["request_bytes"],
        "contract-e-result": response["result_bytes"],
        "evaluation-transcript": response["transcript_bytes"],
        "render-packet": canonical_bytes(inputs["render_packet"]),
        "rendered-payload": inputs["payload"],
        "ers-shadow-result": canonical_bytes(shadow),
    }
    artifact_entries = []
    for artifact_id, raw in material.items():
        filename = artifact_id + (".bin" if artifact_id == "rendered-payload" else ".json")
        (artifacts_dir / filename).write_bytes(raw)
        commitment = {"scheme": "sha256-bytes", "value": sha256_identity(raw)}
        artifact_entries.append({
            "artifact_id": artifact_id,
            "kind": "research-run-artifact",
            "logical_id": artifact_id,
            "commitments": [commitment],
            "retention": {"state": "retained_verified", "locators": [{"kind": "filesystem", "value": "artifacts/" + filename}]},
            "required_for_reconstruction": True,
        })

    source_commits = [
        ("apparatus-preregistration", "camerontjs-dot/apparatus-contracts", APPARATUS_PREREG, ROOT),
        ("contract-e-profile", "camerontjs-dot/apparatus-contracts", CONTRACT_E, inputs["contract_e_root"]),
        ("contract-d-release", "camerontjs-dot/apparatus-contracts", CONTRACT_D, inputs["contract_d_root"]),
        ("decision-engine", "camerontjs-dot/decision-engine", DECISION, inputs["decision_root"]),
        ("contract-c-consumer", "camerontjs-dot/research-scaffold-harness", CONTRACT_C_CONSUMER, inputs["consumer_root"]),
        ("ers-rc6-implementation", "camerontjs-dot/epistemic-research-system", inputs["ers_source_commit"], inputs["ers_root"]),
        ("provenance-profile", "camerontjs-dot/apparatus-contracts", PROVENANCE_PROFILE, profile_root.parents[1]),
    ]
    config_entries = []
    config_records = []
    for logical_id, repository, commit, repo_path in source_commits:
        tree = git(repo_path, "rev-parse", f"{commit}^{{tree}}")
        artifact_id = "config-" + logical_id
        commits = [
            {"scheme": "git-commit", "value": commit},
            {"scheme": "git-tree", "value": tree},
        ]
        artifact_entries.append({
            "artifact_id": artifact_id,
            "kind": "configuration-source",
            "logical_id": logical_id,
            "commitments": commits,
            "retention": {"state": "retained_verified", "locators": [{"kind": "git_object", "value": repository + "@" + commit}]},
            "required_for_reconstruction": True,
        })
        config_entries.append({
            "artifact_id": artifact_id,
            "kind": "configuration-source",
            "logical_id": logical_id,
            "commitments": commits,
            "resolution": {"type": "retained", "artifact_id": artifact_id},
        })
        config_records.append({
            "kind": "configuration-source",
            "logical_id": logical_id,
            "commitments": commits,
            "behaviorally_relevant": True,
            "resolution": {"type": "retained", "artifact_id": artifact_id},
        })
    schema_raw = inputs["schema_path"].read_bytes()
    schema_artifact_id = "config-frozen-transcript-schema"
    schema_entry = {
        "artifact_id": schema_artifact_id,
        "kind": "research-schema",
        "logical_id": "contract-e-evaluation-transcript-rc0",
        "commitments": [
            {"scheme": "sha256-bytes", "value": sha256_identity(schema_raw)},
            {"scheme": "git-commit", "value": APPARATUS_PREREG},
        ],
        "retention": {"state": "retained_verified", "locators": [{"kind": "git_object", "value": "camerontjs-dot/apparatus-contracts@" + APPARATUS_PREREG + ":research/ers-contract-e-evaluation-provenance-20260921/schemas/contract-e-evaluation-transcript.rc0.schema.json"}]},
        "required_for_reconstruction": True,
    }
    artifact_entries.append(schema_entry)
    config_entries.append({
        "artifact_id": schema_artifact_id,
        "kind": schema_entry["kind"],
        "logical_id": schema_entry["logical_id"],
        "commitments": schema_entry["commitments"],
        "resolution": {"type": "retained", "artifact_id": schema_artifact_id},
    })
    config_records.append({
        "kind": schema_entry["kind"],
        "logical_id": schema_entry["logical_id"],
        "commitments": schema_entry["commitments"],
        "behaviorally_relevant": True,
        "resolution": {"type": "retained", "artifact_id": schema_artifact_id},
    })

    artifacts_by_id = {entry["artifact_id"]: entry for entry in artifact_entries}

    def artifact_ref(artifact_id: str) -> dict[str, Any]:
        entry = artifacts_by_id[artifact_id]
        return {
            "artifact_id": artifact_id,
            "kind": entry["kind"],
            "logical_id": entry["logical_id"],
            "commitments": entry["commitments"],
        }

    def seal(value: dict[str, Any], id_field: str, sha_field: str, prefix: str) -> dict[str, Any]:
        payload = {key: child for key, child in value.items() if key not in {id_field, sha_field}}
        digest = sha256_identity(canonical_bytes(payload))
        value[id_field] = prefix + digest
        value[sha_field] = digest
        return value

    authority_refs = [
        {"kind": "git-commit", "id": repository + "@" + commit, "immutable_id": commit}
        for _, repository, commit, _ in source_commits
    ]
    e_attestation = {
        "attestation_schema": "cal-pipeline-apparatus-attestation-v1-explicit-link-rc0",
        "attestation_id": "",
        "stage": {"id": "contract_e_evaluation", "kind": "other"},
        "producer": {"system_id": "apparatus-contracts-contract-e-profile", "implementation": {"kind": "git", "repository": "camerontjs-dot/apparatus-contracts", "commit_sha": CONTRACT_E}},
        "run": {"run_id": EXPERIMENT_ID, "work_id": "ers-contract-e-evaluation-transcript"},
        "inputs": [
            {"role": "causal_input", "artifact": artifact_ref("execution-intent")},
            {"role": "authority_input", "artifact": artifact_ref("authority-state")},
        ],
        "authorities": authority_refs,
        "configuration": {"identities": config_entries},
        "operation": {"name": "contract_e_supervised_evaluation", "version": "rc0"},
        "outputs": [artifact_ref("contract-e-request"), artifact_ref("contract-e-result"), artifact_ref("evaluation-transcript")],
        "execution": {"state": "completed", "reason_code": None},
        "attestation_sha256": "",
    }
    ers_attestation = {
        "attestation_schema": "cal-pipeline-apparatus-attestation-v1-explicit-link-rc0",
        "attestation_id": "",
        "stage": {"id": "ers_write_free_shadow", "kind": "other"},
        "producer": {"system_id": "epistemic-research-system", "implementation": {"kind": "git", "repository": "camerontjs-dot/epistemic-research-system", "commit_sha": inputs["ers_source_commit"]}},
        "run": {"run_id": EXPERIMENT_ID, "work_id": "ers-contract-e-evaluation-transcript"},
        "inputs": [
            {"role": "causal_input", "artifact": artifact_ref("execution-intent")},
            {"role": "authority_input", "artifact": artifact_ref("authority-state")},
            {"role": "observed_context", "artifact": artifact_ref("evaluation-transcript")},
            {"role": "causal_input", "artifact": artifact_ref("render-packet")},
            {"role": "causal_input", "artifact": artifact_ref("rendered-payload")},
        ],
        "authorities": authority_refs,
        "configuration": {"identities": config_entries},
        "operation": {"name": "ers_contract_e_shadow_transcript_consumer", "version": "rc6"},
        "outputs": [artifact_ref("ers-shadow-result")],
        "execution": {"state": "completed", "reason_code": None},
        "attestation_sha256": "",
    }
    seal(e_attestation, "attestation_id", "attestation_sha256", "attestation:")
    seal(ers_attestation, "attestation_id", "attestation_sha256", "attestation:")
    e_attestation_bytes = canonical_bytes(e_attestation)
    ers_attestation_bytes = canonical_bytes(ers_attestation)
    (attestations_dir / "contract-e.explicit.json").write_bytes(e_attestation_bytes)
    (attestations_dir / "ers.explicit.json").write_bytes(ers_attestation_bytes)
    for artifact_id, filename, raw in (
        ("contract-e-attestation", "contract-e.explicit.json", e_attestation_bytes),
        ("ers-attestation", "ers.explicit.json", ers_attestation_bytes),
    ):
        entry = {
            "artifact_id": artifact_id,
            "kind": "apparatus-attestation",
            "logical_id": artifact_id,
            "commitments": [{"scheme": "sha256-bytes", "value": sha256_identity(raw)}],
            "retention": {
                "state": "retained_verified",
                "locators": [{"kind": "filesystem", "value": "attestations/" + filename}],
            },
            "required_for_reconstruction": True,
        }
        artifact_entries.append(entry)
        artifacts_by_id[artifact_id] = entry

    manifest = {
        "manifest_schema": "cal-pipeline-run-manifest-v1-explicit-link-rc0",
        "manifest_id": "",
        "run_id": EXPERIMENT_ID,
        "work_id": "ers-contract-e-evaluation-transcript",
        "root_inputs": ["execution-intent", "authority-state"],
        "artifacts": artifact_entries,
        "stages": [
            {"stage_id": "contract_e_evaluation", "stage_kind": "other", "state": "completed", "attestation_artifact_id": "contract-e-attestation"},
            {"stage_id": "ers_write_free_shadow", "stage_kind": "other", "state": "completed", "attestation_artifact_id": "ers-attestation"},
        ],
        "authorities": authority_refs,
        "reconstruction": {
            "required_artifact_ids": sorted(artifacts_by_id),
            "status": "not_evaluated",
            "missing_or_unresolved": [],
            "notes": ["Explicit-link sidecar validation is evidence capture only; this manifest does not claim independent pipeline reconstruction."],
        },
        "manifest_sha256": "",
        "link_profile": "cal-provenance-explicit-link-1",
    }
    seal(manifest, "manifest_id", "manifest_sha256", "run-manifest:")
    (case / "manifest.explicit.json").write_bytes(canonical_bytes(manifest))
    config_resolution = {"configurations": config_records}
    (case / "config-resolution.json").write_bytes(canonical_bytes(config_resolution))

    # Invoke the exact pinned validator code with only its read root redirected to
    # this disposable sidecar copy; source/schema bytes remain those at 3934423.
    with tempfile.TemporaryDirectory(prefix="ers-rc6-provenance-profile-") as td:
        validation_root = Path(td)
        shutil.copytree(profile_root / "schemas", validation_root / "schemas")
        shutil.copytree(case.parent, validation_root / "sidecars")
        validator = load_module("ers_rc6_pinned_provenance_validator", profile_root / "validator.py")
        validator.ROOT = validation_root
        validator.VECTORS_PATH = validation_root / "LINK-VECTORS.json"
        validator.SCHEMAS_DIR = validation_root / "schemas"
        validator.MANIFEST_SCHEMA_PATH = validator.SCHEMAS_DIR / "run-manifest.explicit-link-rc0.schema.json"
        validator.ATTESTATION_SCHEMA_PATH = validator.SCHEMAS_DIR / "apparatus-attestation.explicit-link-rc0.schema.json"
        sidecar_validation = validator.validate_sidecars()
    return {
        "profile_commit": PROVENANCE_PROFILE,
        "manifest_id": manifest["manifest_id"],
        "manifest_sha256": manifest["manifest_sha256"],
        "contract_e_attestation_id": e_attestation["attestation_id"],
        "contract_e_attestation_sha256": e_attestation["attestation_sha256"],
        "ers_attestation_id": ers_attestation["attestation_id"],
        "ers_attestation_sha256": ers_attestation["attestation_sha256"],
        "artifact_ids": sorted(artifacts_by_id),
        "validation": sidecar_validation,
        "status": "PASS" if sidecar_validation and all(row[1] for row in sidecar_validation) else "FAIL",
        "profile_vectors_run": False,
    }


if __name__ == "__main__":
    raise SystemExit(main())
