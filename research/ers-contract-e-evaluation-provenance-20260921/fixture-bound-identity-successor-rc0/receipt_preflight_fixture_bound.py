"""Non-evaluating consistency preflight for the RC6 receipt-contract successor.

This module reads only receipts, Git objects, and source text. It never imports
the ERS candidate, Contract E profile, or qualification supervisor.
"""

from __future__ import annotations

import argparse
import ast
import base64
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


EXPERIMENT_ID = "ERS-EVAL-TIME-PROV-20260922-05"
PR130_HEAD = "dcdd10355e2f885273d843eef6e345bafca95faa"
PR131_HEAD = "077ccf6d386526bda258b3e90bd43e153c4c04c5"
TRANSCRIPT_SCHEMA_BLOB = "b85b38ce95263e348d2ebd1293f76ffc87adcf6d"
ERS_REPOSITORY = "camerontjs-dot/epistemic-research-system"
APPARATUS_REPOSITORY = "camerontjs-dot/apparatus-contracts"
ERS_RECEIPT_RELATIVE_PATH = Path(
    "research/ers-contract-e-evaluation-transcript-rc6-exec-identity-successor-20260922/FREEZE_RECEIPT.json"
)
APP_RECEIPT_RELATIVE_PATH = Path(
    "research/ers-contract-e-evaluation-provenance-20260921/successor-executable-source-identity-rc0/FREEZE_RECEIPT.json"
)
TRANSCRIPT_SCHEMA_PATH = (
    "research/ers-contract-e-evaluation-provenance-20260921/"
    "schemas/contract-e-evaluation-transcript.rc0.schema.json"
)
EXPECTED_ISSUER_ID = re.compile(r"^sha256:[0-9a-f]{64}$")

EXPECTED_CLIENT_SIGNATURE = (
    "evaluate_and_attest(socket_path, *, decision, execution_intent, "
    "authority_state, challenge) -> dict[str, bytes]"
)
EXPECTED_CONSUMER_SIGNATURE = (
    "stage_pending_review(decision, execution_intent, authority_state, *, "
    "expected_relative_path, mainframe_root, expected_executable_sha256, "
    "render_packet_value, payload, supervisor_socket)"
)
EXPECTED_WIRE_KEYS = [
    "schema",
    "decision",
    "execution_intent",
    "authority_state",
    "challenge",
]
FORBIDDEN_SUPERVISOR_INPUTS = {
    "evaluation_time",
    "contract_e_result",
    "result",
    "result_bytes",
    "transcript_body",
}
EXPECTED_FORBIDDEN_INPUTS = [
    "evaluation_time",
    "contract_e_result",
    "result_bytes",
    "precomputed transcript body",
]


class PreflightError(RuntimeError):
    """A receipt or static source consistency check failed."""


class RuntimeGuard:
    """Observe and block any non-Git execution or candidate-runtime import."""

    def __init__(self, output_path: Path):
        self.output_path = output_path.resolve()
        self.git_processes = 0
        self.non_git_processes: list[str] = []
        self.candidate_imports: list[str] = []
        self.network_attempts = 0
        self.contract_e_evaluation_calls = 0
        self.supervisor_process_launches = 0

    def audit(self, event: str, args: tuple[Any, ...]) -> None:
        if event == "import":
            name = str(args[0]) if args else ""
            origin = str(args[1]) if len(args) > 1 and args[1] else ""
            lowered = (name + " " + origin).lower()
            if any(
                token in lowered
                for token in (
                    "qualification_supervisor",
                    "contract_e_profile",
                    "apparatus-contracts",
                    "epistemic-research-system",
                )
            ):
                self.candidate_imports.append(name or origin)
                raise PreflightError("candidate_runtime_import_blocked")
        elif event == "subprocess.Popen":
            executable = str(args[0] or "") if args else ""
            argv = args[1] if len(args) > 1 else []
            first = str(argv[0]) if isinstance(argv, (list, tuple)) and argv else executable
            program = Path(first).name
            if program == "git":
                self.git_processes += 1
                return
            self.non_git_processes.append(program)
            if "supervisor" in program or "python" in program:
                self.supervisor_process_launches += 1
            raise PreflightError("non_git_subprocess_blocked")
        elif event in {"socket.connect", "socket.getaddrinfo", "http.client.connect"}:
            self.network_attempts += 1
            raise PreflightError("network_access_blocked")

    def profile(self, frame: Any, event: str, _arg: Any) -> None:
        if event != "call":
            return
        module = str(frame.f_globals.get("__name__", "")).lower()
        filename = str(frame.f_code.co_filename).lower()
        function = frame.f_code.co_name
        candidate_evaluation = (
            function == "evaluate"
            and ("contract_e" in module or "integration_profile" in module or "contract-e" in filename)
        ) or (
            function == "evaluate_and_attest"
            and "qualification_supervisor" in module
        )
        if candidate_evaluation:
            self.contract_e_evaluation_calls += 1
            raise PreflightError("contract_e_evaluation_during_preflight")

    def summary(self) -> dict[str, Any]:
        return {
            "contract_e_evaluation_calls": self.contract_e_evaluation_calls,
            "supervisor_process_launches": self.supervisor_process_launches,
            "candidate_runtime_imports": list(self.candidate_imports),
            "non_git_processes": list(self.non_git_processes),
            "git_processes": self.git_processes,
            "network_attempts": self.network_attempts,
        }


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def sha256(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def git_bytes(root: Path, *args: str, input_bytes: bytes | None = None) -> bytes:
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        input=input_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise PreflightError("git_object_check_failed:" + detail[:240])
    return completed.stdout


def git_text(root: Path, *args: str, input_bytes: bytes | None = None) -> str:
    return git_bytes(root, *args, input_bytes=input_bytes).decode("utf-8").strip()


def get_path(value: Any, dotted_path: str) -> Any:
    current = value
    for component in dotted_path.split("."):
        if not isinstance(current, dict) or component not in current:
            return None
        current = current[component]
    return current


def _record(
    checks: list[dict[str, Any]],
    name: str,
    actual: Any,
    expected: Any,
    passed: bool | None = None,
) -> None:
    checks.append(
        {
            "check": name,
            "actual": actual,
            "expected": expected,
            "passed": actual == expected if passed is None else passed,
        }
    )


def _function(tree: ast.AST, name: str) -> ast.FunctionDef:
    matches = [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name
    ]
    if len(matches) != 1 or not isinstance(matches[0], ast.FunctionDef):
        raise PreflightError("public_api_function_missing_or_ambiguous:" + name)
    return matches[0]


def _assignment(tree: ast.AST, name: str) -> Any:
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == name for target in node.targets
        ):
            return ast.literal_eval(node.value)
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == name:
            return ast.literal_eval(node.value)
    raise PreflightError("source_constant_missing:" + name)


def _argument_shape(node: ast.FunctionDef) -> dict[str, Any]:
    arguments = node.args
    if arguments.vararg is not None or arguments.kwarg is not None:
        raise PreflightError("public_api_variadic_parameters_forbidden:" + node.name)
    if any(value is not None for value in arguments.kw_defaults):
        raise PreflightError("public_api_defaulted_keyword_parameter:" + node.name)
    return {
        "positional": [value.arg for value in arguments.posonlyargs + arguments.args],
        "keyword_only": [value.arg for value in arguments.kwonlyargs],
        "return": ast.unparse(node.returns) if node.returns is not None else None,
    }


def inspect_supervisor_api(
    client_source: bytes,
    server_source: bytes,
    transcript_source: bytes,
) -> dict[str, Any]:
    client_tree = ast.parse(client_source.decode("utf-8"))
    server_tree = ast.parse(server_source.decode("utf-8"))
    transcript_tree = ast.parse(transcript_source.decode("utf-8"))

    client_function = _function(client_tree, "evaluate_and_attest")
    client_shape = _argument_shape(client_function)
    expected_client_shape = {
        "positional": ["socket_path"],
        "keyword_only": ["decision", "execution_intent", "authority_state", "challenge"],
        "return": "dict[str, bytes]",
    }
    if client_shape != expected_client_shape:
        raise PreflightError("public_supervisor_api_shape_mismatch")
    names = set(client_shape["positional"] + client_shape["keyword_only"])
    if names.intersection(FORBIDDEN_SUPERVISOR_INPUTS):
        raise PreflightError("forbidden_supervisor_api_parameter")

    make_request = _function(client_tree, "make_request")
    returned_dicts = [
        node.value
        for node in ast.walk(make_request)
        if isinstance(node, ast.Return) and isinstance(node.value, ast.Dict)
    ]
    if len(returned_dicts) != 1:
        raise PreflightError("supervisor_wire_request_shape_unprovable")
    wire_keys = [ast.literal_eval(key) for key in returned_dicts[0].keys]
    server_keys = _assignment(server_tree, "_REQUEST_KEYS")
    if wire_keys != EXPECTED_WIRE_KEYS or set(server_keys) != set(EXPECTED_WIRE_KEYS):
        raise PreflightError("supervisor_wire_keys_changed")
    server_evaluator = _function(server_tree, "evaluate_and_attest")
    server_shape = _argument_shape(server_evaluator)
    if server_shape["positional"] != ["self", "request"] or server_shape["keyword_only"]:
        raise PreflightError("supervisor_server_api_shape_mismatch")

    pem = _assignment(transcript_tree, "ISSUER_PUBLIC_KEY_PEM")
    issuer_key_id = _assignment(transcript_tree, "ISSUER_KEY_ID")
    if not isinstance(pem, bytes) or not isinstance(issuer_key_id, str):
        raise PreflightError("issuer_pin_type_invalid")
    encoded_der = b"".join(
        line.strip()
        for line in pem.splitlines()
        if line and not line.startswith(b"-----")
    )
    try:
        der = base64.b64decode(encoded_der, validate=True)
    except ValueError as exc:
        raise PreflightError("issuer_public_key_pem_invalid") from exc
    actual_key_id = sha256(der)
    if actual_key_id != issuer_key_id:
        raise PreflightError("issuer_public_key_identity_mismatch")

    return {
        "client_signature": EXPECTED_CLIENT_SIGNATURE,
        "client_shape": client_shape,
        "wire_keys": wire_keys,
        "server_request_keys": sorted(server_keys),
        "server_evaluator_shape": server_shape,
        "forbidden_inputs_absent": sorted(FORBIDDEN_SUPERVISOR_INPUTS),
        "issuer_public_key_identity": actual_key_id,
    }


def _load_json(raw: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise PreflightError("invalid_json_receipt:" + label) from exc
    if not isinstance(value, dict):
        raise PreflightError("receipt_root_not_object:" + label)
    return value


def build_preflight(
    *,
    apparatus_root: Path,
    apparatus_source_commit: str,
    ers_root: Path,
    ers_source_commit: str,
    ers_freeze_commit: str,
    apparatus_freeze_receipt: Path,
    guard: RuntimeGuard,
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    if apparatus_freeze_receipt.resolve() != (apparatus_root / APP_RECEIPT_RELATIVE_PATH).resolve():
        raise PreflightError("apparatus_freeze_receipt_path_not_canonical")
    ers_receipt_git_blob = git_text(
        ers_root,
        "rev-parse",
        f"{ers_freeze_commit}:{ERS_RECEIPT_RELATIVE_PATH.as_posix()}",
    )
    ers_receipt_bytes = git_bytes(
        ers_root,
        "show",
        f"{ers_freeze_commit}:{ERS_RECEIPT_RELATIVE_PATH.as_posix()}",
    )
    app_receipt_bytes = apparatus_freeze_receipt.read_bytes()
    app_receipt_git_blob = git_text(
        apparatus_root,
        "hash-object",
        "--stdin",
        input_bytes=app_receipt_bytes,
    )
    ers_receipt = _load_json(ers_receipt_bytes, "ers")
    app_receipt = _load_json(app_receipt_bytes, "apparatus")

    expected_ers_schema = "ers-contract-e-evaluation-transcript-freeze/1"
    expected_app_schema = "ers-contract-e-evaluation-provenance-apparatus-freeze/1"
    _record(checks, "ers_receipt_schema", ers_receipt.get("schema"), expected_ers_schema)
    _record(checks, "apparatus_receipt_schema", app_receipt.get("schema"), expected_app_schema)
    _record(checks, "ers_experiment_id", ers_receipt.get("experiment_id"), EXPERIMENT_ID)
    _record(checks, "apparatus_experiment_id", app_receipt.get("experiment_id"), EXPERIMENT_ID)
    _record(
        checks,
        "matching_experiment_identity",
        (ers_receipt.get("experiment_id"), app_receipt.get("experiment_id")),
        (EXPERIMENT_ID, EXPERIMENT_ID),
    )

    ers_source = get_path(ers_receipt, "implementation.source_commit")
    app_ers_source = get_path(app_receipt, "ers_candidate.source_commit")
    ers_tree = get_path(ers_receipt, "implementation.source_tree")
    app_ers_tree = get_path(app_receipt, "ers_candidate.source_tree")
    _record(checks, "ers_source_commit_equals_apparatus_binding", ers_source, app_ers_source)
    _record(checks, "ers_source_tree_equals_apparatus_binding", ers_tree, app_ers_tree)
    ers_apparatus_source = get_path(ers_receipt, "apparatus.candidate_source_commit")
    ers_apparatus_tree = get_path(ers_receipt, "apparatus.candidate_source_tree")
    _record(checks, "ers_receipt_binds_apparatus_source_commit", ers_apparatus_source, apparatus_source_commit)
    _record(checks, "ers_receipt_binds_apparatus_source_tree", ers_apparatus_tree, get_path(app_receipt, "apparatus_candidate_source_tree"))
    _record(checks, "cli_ers_source_commit_matches_ers_receipt", ers_source, ers_source_commit)
    _record(checks, "cli_ers_source_commit_matches_apparatus_receipt", app_ers_source, ers_source_commit)
    _record(checks, "cli_apparatus_source_commit_matches_receipt", app_receipt.get("apparatus_candidate_source_commit"), apparatus_source_commit)

    ers_pr130 = get_path(ers_receipt, "apparatus.preregistration_head")
    app_pr130 = get_path(app_receipt, "preregistration.frozen_head")
    _record(checks, "ers_pr130_head", ers_pr130, PR130_HEAD)
    _record(checks, "apparatus_pr130_head", app_pr130, PR130_HEAD)
    _record(checks, "matching_pr130_head", (ers_pr130, app_pr130), (PR130_HEAD, PR130_HEAD))
    ers_pr131 = get_path(ers_receipt, "apparatus.receipt_contract_preregistration.commit")
    app_pr131 = get_path(app_receipt, "receipt_contract_preregistration.frozen_head")
    _record(checks, "ers_pr131_head", ers_pr131, PR131_HEAD)
    _record(checks, "apparatus_pr131_head", app_pr131, PR131_HEAD)

    ers_schema_blob = get_path(ers_receipt, "apparatus.transcript_schema_blob")
    app_schema_blob = get_path(app_receipt, "preregistration.transcript_schema_blob")
    _record(checks, "ers_transcript_schema_blob", ers_schema_blob, TRANSCRIPT_SCHEMA_BLOB)
    _record(checks, "apparatus_transcript_schema_blob", app_schema_blob, TRANSCRIPT_SCHEMA_BLOB)
    _record(checks, "matching_transcript_schema_blob", (ers_schema_blob, app_schema_blob), (TRANSCRIPT_SCHEMA_BLOB, TRANSCRIPT_SCHEMA_BLOB))

    ers_issuer = get_path(ers_receipt, "issuer.public_key_identity")
    app_issuer = get_path(app_receipt, "issuer.public_key_identity")
    _record(checks, "ers_issuer_key_identity_format", bool(EXPECTED_ISSUER_ID.fullmatch(str(ers_issuer))), True)
    _record(checks, "matching_issuer_key_identity", ers_issuer, app_issuer)
    _record(checks, "apparatus_issuer_key_identity_format", bool(EXPECTED_ISSUER_ID.fullmatch(str(app_issuer))), True)

    app_ers_freeze_commit = get_path(app_receipt, "ers_candidate.freeze_receipt_commit")
    app_ers_freeze_blob = get_path(app_receipt, "ers_candidate.freeze_receipt_blob")
    app_ers_freeze_tree = get_path(app_receipt, "ers_candidate.freeze_receipt_tree")
    actual_ers_freeze_tree = git_text(ers_root, "rev-parse", f"{ers_freeze_commit}^{{tree}}")
    _record(checks, "apparatus_points_to_read_ers_freeze_commit", app_ers_freeze_commit, ers_freeze_commit)
    _record(checks, "apparatus_points_to_read_ers_freeze_blob", app_ers_freeze_blob, ers_receipt_git_blob)
    _record(checks, "apparatus_ers_freeze_tree", app_ers_freeze_tree, actual_ers_freeze_tree)
    _record(checks, "ers_freeze_commit_is_head", git_text(ers_root, "rev-parse", "HEAD"), ers_freeze_commit)
    _record(checks, "apparatus_source_commit_is_head_before_freeze", git_text(apparatus_root, "rev-parse", "HEAD"), apparatus_source_commit)

    resolved_objects: list[dict[str, Any]] = []
    for label, root, commit, expected_tree in (
        ("ers_source", ers_root, ers_source_commit, ers_tree),
        ("apparatus_source", apparatus_root, apparatus_source_commit, get_path(app_receipt, "apparatus_candidate_source_tree")),
        ("ers_freeze", ers_root, ers_freeze_commit, actual_ers_freeze_tree),
    ):
        resolved_commit = git_text(root, "rev-parse", f"{commit}^{{commit}}")
        resolved_tree = git_text(root, "rev-parse", f"{commit}^{{tree}}")
        _record(checks, label + "_commit_resolves", resolved_commit, commit)
        _record(checks, label + "_tree_resolves", resolved_tree, expected_tree)
        resolved_objects.append({"label": label, "commit": resolved_commit, "tree": resolved_tree})

    _record(checks, "ers_source_tree_matches_resolved_git_tree", ers_tree, git_text(ers_root, "rev-parse", f"{ers_source_commit}^{{tree}}"))
    _record(checks, "apparatus_source_tree_matches_resolved_git_tree", get_path(app_receipt, "apparatus_candidate_source_tree"), git_text(apparatus_root, "rev-parse", f"{apparatus_source_commit}^{{tree}}"))
    _record(checks, "ers_source_commit_is_ancestor_of_freeze", git_text(ers_root, "merge-base", "--is-ancestor", ers_source_commit, ers_freeze_commit), "")
    _record(checks, "pr130_is_ancestor_of_apparatus_source", git_text(apparatus_root, "merge-base", "--is-ancestor", PR130_HEAD, apparatus_source_commit), "")
    _record(checks, "pr131_is_ancestor_of_apparatus_source", git_text(apparatus_root, "merge-base", "--is-ancestor", PR131_HEAD, apparatus_source_commit), "")

    schema_at_pr130 = git_text(apparatus_root, "rev-parse", f"{PR130_HEAD}:{TRANSCRIPT_SCHEMA_PATH}")
    _record(checks, "pr130_transcript_schema_object", schema_at_pr130, TRANSCRIPT_SCHEMA_BLOB)

    app_source_path = get_path(app_receipt, "apparatus_candidate_source_path")
    app_source_blob_expected = get_path(app_receipt, "apparatus_candidate_source_blob")
    app_source_blob_actual = git_text(apparatus_root, "rev-parse", f"{apparatus_source_commit}:{app_source_path}")
    _record(checks, "apparatus_runner_source_blob", app_source_blob_actual, app_source_blob_expected)
    preflight_source_blob = get_path(app_receipt, "preflight_source_blob")
    preflight_source_path = get_path(app_receipt, "preflight_source_path")
    preflight_blob_actual = git_text(apparatus_root, "rev-parse", f"{apparatus_source_commit}:{preflight_source_path}")
    _record(checks, "preflight_source_blob", preflight_blob_actual, preflight_source_blob)

    expected_decisive_before_freeze = False
    _record(checks, "ers_no_decisive_result_before_freeze", ers_receipt.get("decisive_rc6_matrix_observed_before_freeze"), expected_decisive_before_freeze)
    _record(checks, "apparatus_no_decisive_result_before_freeze", app_receipt.get("decisive_rc6_matrix_observed_before_freeze"), expected_decisive_before_freeze)
    _record(checks, "ers_no_top_level_source_alias", "implementation_source_commit" in ers_receipt, False)

    api = get_path(ers_receipt, "public_api")
    app_api = get_path(app_receipt, "public_supervisor_api")
    expected_ers_wire = {
        "supervisor_client": EXPECTED_CLIENT_SIGNATURE,
        "supervisor_wire_keys": EXPECTED_WIRE_KEYS,
        "forbidden_supervisor_inputs": EXPECTED_FORBIDDEN_INPUTS,
        "ers_consumer": EXPECTED_CONSUMER_SIGNATURE,
        "challenge_generation": "ERS consumer generates a fresh secrets.token_urlsafe(32) challenge",
        "transcript_freshness_seconds": 30,
    }
    expected_app_api = {
        "signature": EXPECTED_CLIENT_SIGNATURE,
        "wire_keys": EXPECTED_WIRE_KEYS,
        "caller_time_parameter": False,
        "caller_contract_e_result_parameter": False,
        "caller_precomputed_transcript_signing_parameter": False,
        "normal_api_shape_tests": "4 passed",
    }
    _record(checks, "ers_public_api_receipt", api, expected_ers_wire)
    _record(checks, "apparatus_public_api_receipt", app_api, expected_app_api)
    _record(checks, "ers_source_not_legacy_top_level_alias", "implementation_source_commit" in ers_receipt, False)
    _record(checks, "apparatus_source_not_legacy_top_level_alias", "implementation_source_commit" in app_receipt, False)

    source_slice = get_path(ers_receipt, "implementation.slice")
    client_source = git_bytes(ers_root, "show", f"{ers_source_commit}:{source_slice}/harness/supervisor_client.py")
    server_source = git_bytes(ers_root, "show", f"{ers_source_commit}:{source_slice}/harness/qualification_supervisor.py")
    transcript_source = git_bytes(ers_root, "show", f"{ers_source_commit}:{source_slice}/harness/evaluation_transcript.py")
    api_details = inspect_supervisor_api(client_source, server_source, transcript_source)
    _record(checks, "source_supervisor_api_signature", api_details["client_signature"], EXPECTED_CLIENT_SIGNATURE)
    _record(checks, "source_supervisor_wire_keys", api_details["wire_keys"], EXPECTED_WIRE_KEYS)
    _record(checks, "source_server_request_keys", api_details["server_request_keys"], sorted(EXPECTED_WIRE_KEYS))
    _record(checks, "source_issuer_key_matches_receipts", api_details["issuer_public_key_identity"], ers_issuer)
    _record(checks, "source_issuer_key_matches_apparatus_receipt", api_details["issuer_public_key_identity"], app_issuer)

    failures = [check for check in checks if not check["passed"]]
    if guard.contract_e_evaluation_calls != 0 or guard.supervisor_process_launches != 0 or guard.candidate_imports or guard.network_attempts:
        failures.append(
            {
                "check": "non_evaluating_runtime_guard",
                "actual": guard.summary(),
                "expected": {
                    "contract_e_evaluation_calls": 0,
                    "supervisor_process_launches": 0,
                    "candidate_runtime_imports": [],
                    "network_attempts": 0,
                },
                "passed": False,
            }
        )
    if failures:
        raise PreflightError(json.dumps({"checks": checks, "failures": failures}, sort_keys=True))

    return {
        "schema": "ers-evaluation-provenance-receipt-consistency-preflight/1",
        "status": "PASS",
        "experiment_id": EXPERIMENT_ID,
        "scientific_preregistration": {
            "repository": APPARATUS_REPOSITORY,
            "pull_request": 130,
            "commit": PR130_HEAD,
        },
        "receipt_contract_preregistration": {
            "repository": APPARATUS_REPOSITORY,
            "pull_request": 131,
            "commit": PR131_HEAD,
        },
        "input_receipts": {
            "ers": {
                "repository": ERS_REPOSITORY,
                "freeze_receipt_commit": ers_freeze_commit,
                "freeze_receipt_tree": actual_ers_freeze_tree,
                "path": ERS_RECEIPT_RELATIVE_PATH.as_posix(),
                "git_blob": ers_receipt_git_blob,
                "sha256_bytes": sha256(ers_receipt_bytes),
            },
            "apparatus": {
                "repository": APPARATUS_REPOSITORY,
                "source_commit": apparatus_source_commit,
                "path": APP_RECEIPT_RELATIVE_PATH.as_posix(),
                "git_blob": app_receipt_git_blob,
                "sha256_bytes": sha256(app_receipt_bytes),
            },
        },
        "compared_values": checks,
        "resolved_git_objects": resolved_objects,
        "public_supervisor_api": api_details,
        "instrumentation": guard.summary(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apparatus-root", required=True, type=Path)
    parser.add_argument("--apparatus-source-commit", required=True)
    parser.add_argument("--ers-root", required=True, type=Path)
    parser.add_argument("--ers-source-commit", required=True)
    parser.add_argument("--ers-freeze-commit", required=True)
    parser.add_argument("--apparatus-freeze-receipt", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    apparatus_root = args.apparatus_root.resolve()
    ers_root = args.ers_root.resolve()
    receipt_path = (args.apparatus_freeze_receipt or (apparatus_root / APP_RECEIPT_RELATIVE_PATH)).resolve()
    output_path = args.output.resolve()
    if not receipt_path.is_file():
        raise SystemExit("apparatus_freeze_receipt_missing")
    if not output_path.parent.is_dir():
        raise SystemExit("preflight_output_parent_missing")
    if output_path.exists():
        raise SystemExit("preflight_output_path_exists")

    guard = RuntimeGuard(output_path)
    sys.addaudithook(guard.audit)
    sys.setprofile(guard.profile)
    try:
        result = build_preflight(
            apparatus_root=apparatus_root,
            apparatus_source_commit=args.apparatus_source_commit,
            ers_root=ers_root,
            ers_source_commit=args.ers_source_commit,
            ers_freeze_commit=args.ers_freeze_commit,
            apparatus_freeze_receipt=receipt_path,
            guard=guard,
        )
    except Exception as exc:
        failure = {
            "schema": "ers-evaluation-provenance-receipt-consistency-preflight/1",
            "status": "FAIL",
            "experiment_id": EXPERIMENT_ID,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "instrumentation": guard.summary(),
        }
        output_path.write_bytes(canonical_json_bytes(failure))
        print(json.dumps(failure, ensure_ascii=False, sort_keys=True, indent=2), file=sys.stderr)
        return 1
    finally:
        sys.setprofile(None)

    output_path.write_bytes(canonical_json_bytes(result))
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
