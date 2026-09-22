"""Independent non-evaluating fixture-binding gate.

This evaluator binds the actual fixture root to the frozen PR #139
fixture-authority record. It reads bytes, paths, Git object identities, and
that frozen record only. It does not import or execute the scientific runner,
Contract E, ERS, or any candidate runtime.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


EXPERIMENT_ID = "ERS-EVAL-TIME-PROV-20260922-05"
PREREGISTRATION_COMMIT = "aca99bfc1bc6f06269894087942fb590f4388697"
FIXTURE_AUTHORITY_BLOB = "7d69167bc17d380f9ccf5c6be0473fbdf4338215"
RUNNER_BLOB = "35bf0e98d7575b9db7ffe2f6906aff757e865e72"
RECEIPT_PREFLIGHT_BLOB = "e7e94523bff84792d355ef2a6da805a91919e076"

AUTHORITY_RELATIVE_PATH = (
    "research/ers-contract-e-evaluation-provenance-20260921/"
    "fixture-bound-successor-rc0/FIXTURE_AUTHORITY.json"
)
RUNNER_RELATIVE_PATH = (
    "research/ers-contract-e-evaluation-provenance-20260921/reproduce_rc6.py"
)
RECEIPT_PREFLIGHT_RELATIVE_PATH = (
    "research/ers-contract-e-evaluation-provenance-20260921/receipt_preflight.py"
)

REQUIRED_CASES = ("PIPE01", "PIPE02", "PIPE03")
REQUIRED_RELATIVE_FILES = (
    "cal/contract-c.json",
    "consumer-inputs.json",
    "decision-target.json",
    "contract-d.json",
)
ALLOWED_FIXTURE_ROOT_NAMES = set(REQUIRED_CASES) | {"FIXTURE_MANIFEST.json"}
REQUIRED_PROVENANCE = {
    "cal/contract-c.json": "byte_matched_to_surviving_historical_artifact",
    "contract-d.json": "byte_matched_to_surviving_historical_artifact",
    "consumer-inputs.json": (
        "deterministically_reconstructed_without_preserved_historical_reference"
    ),
    "decision-target.json": (
        "deterministically_reconstructed_without_preserved_historical_reference"
    ),
}

ALLOWED_SUBPROCESS_PROGRAMS = {"git", "shasum", "openssl"}
FORBIDDEN_IMPORT_TOKENS = (
    "reproduce_rc6",
    "receipt_preflight",
    "qualification_supervisor",
    "contract_e_profile",
    "integration_profile",
    "context_bound_shadow",
    "render_bound_shadow",
    "evaluation_transcript",
    "epistemic-research-system",
    "epistemic_research_system",
    "urllib",
    "requests",
    "http.client",
    "httpx",
    "aiohttp",
)
FORBIDDEN_MODULE_TOKENS = (
    "reproduce_rc6",
    "receipt_preflight",
    "qualification_supervisor",
    "contract_e_profile",
    "context_bound_shadow",
    "render_bound_shadow",
    "evaluation_transcript",
)

PASS_DISPOSITION = "QUALIFIED_FIXTURE_BOUND_SCIENTIFIC_SUBJECT"
SCHEMA = "ers-evaluation-provenance-fixture-binding-preflight/1"


class PreflightError(RuntimeError):
    """A fixture-binding check failed closed."""


class RuntimeGuard:
    """Block scientific execution, candidate imports, and network recovery."""

    def __init__(self) -> None:
        self.git_processes = 0
        self.independent_digest_processes = 0
        self.non_allowed_processes: list[str] = []
        self.candidate_imports: list[str] = []
        self.network_attempts = 0
        self.contract_e_evaluation_calls = 0
        self.supervisor_process_launches = 0
        self.scientific_runner_imports = 0
        self.ers_candidate_runtime_imports = 0

    def audit(self, event: str, args: tuple[Any, ...]) -> None:
        if event == "import":
            name = str(args[0]) if args else ""
            origin = str(args[1]) if len(args) > 1 and args[1] else ""
            lowered = (name + " " + origin).lower()
            if any(token in lowered for token in FORBIDDEN_IMPORT_TOKENS):
                self.candidate_imports.append(name or origin)
                if "reproduce_rc6" in lowered:
                    self.scientific_runner_imports += 1
                if any(
                    token in lowered
                    for token in (
                        "qualification_supervisor",
                        "contract_e_profile",
                        "context_bound_shadow",
                        "render_bound_shadow",
                        "evaluation_transcript",
                        "epistemic",
                    )
                ):
                    self.ers_candidate_runtime_imports += 1
                raise PreflightError("candidate_runtime_import_blocked:" + (name or origin))
        elif event == "subprocess.Popen":
            program = _subprocess_program(args)
            if program == "git":
                self.git_processes += 1
                return
            if program in {"shasum", "openssl"}:
                self.independent_digest_processes += 1
                return
            self.non_allowed_processes.append(program)
            if "supervisor" in program or program.startswith("python"):
                self.supervisor_process_launches += 1
            raise PreflightError("non_allowed_subprocess_blocked:" + program)
        elif event in {"socket.connect", "socket.getaddrinfo", "http.client.connect"}:
            self.network_attempts += 1
            raise PreflightError("network_access_blocked")

    def profile(self, frame: Any, event: str, _arg: Any) -> None:
        if event != "call":
            return
        module = str(frame.f_globals.get("__name__", "")).lower()
        filename = str(frame.f_code.co_filename).lower()
        function = frame.f_code.co_name
        if function == "evaluate" and (
            "contract_e" in module or "integration_profile" in module or "contract-e" in filename
        ):
            self.contract_e_evaluation_calls += 1
            raise PreflightError("contract_e_evaluation_during_fixture_binding")
        if function == "evaluate_and_attest" and "qualification_supervisor" in module:
            self.contract_e_evaluation_calls += 1
            self.supervisor_process_launches += 1
            raise PreflightError("supervisor_launch_during_fixture_binding")

    def summary(self) -> dict[str, Any]:
        return {
            "contract_e_evaluation_calls": self.contract_e_evaluation_calls,
            "supervisor_process_launches": self.supervisor_process_launches,
            "scientific_runner_imports": self.scientific_runner_imports,
            "ers_candidate_runtime_imports": self.ers_candidate_runtime_imports,
            "candidate_runtime_imports": list(self.candidate_imports),
            "non_allowed_processes": list(self.non_allowed_processes),
            "git_processes": self.git_processes,
            "independent_digest_processes": self.independent_digest_processes,
            "network_attempts": self.network_attempts,
            "loaded_forbidden_modules": loaded_forbidden_modules(),
        }


def _subprocess_program(args: tuple[Any, ...]) -> str:
    executable = str(args[0] or "") if args else ""
    argv = args[1] if len(args) > 1 else []
    first = str(argv[0]) if isinstance(argv, (list, tuple)) and argv else executable
    return Path(first).name


def loaded_forbidden_modules() -> list[str]:
    hits: list[str] = []
    for name in sys.modules:
        lowered = name.lower()
        if any(token in lowered for token in FORBIDDEN_MODULE_TOKENS):
            hits.append(name)
    return sorted(hits)


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def sha256_bytes(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def read_bytes(path: Path) -> bytes:
    with path.open("rb") as handle:
        return handle.read()


def git_bytes(root: Path, *args: str) -> bytes:
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise PreflightError("git_object_check_failed:" + detail[:240])
    return completed.stdout


def git_text(root: Path, *args: str) -> str:
    return git_bytes(root, *args).decode("utf-8").strip()


def resolve_independent_digest_tool() -> list[str]:
    candidates = (
        ["/usr/bin/shasum", "-a", "256"],
        ["shasum", "-a", "256"],
        ["/usr/bin/openssl", "dgst", "-sha256"],
        ["openssl", "dgst", "-sha256"],
    )
    for command in candidates:
        executable = command[0]
        if os.path.isfile(executable) and os.access(executable, os.X_OK):
            return command
        resolved = shutil.which(executable)
        if resolved:
            return [resolved, *command[1:]]
    raise PreflightError("independent_digest_tool_unavailable")


def parse_independent_digest(output: str) -> str:
    text = output.strip()
    if not text:
        raise PreflightError("independent_digest_empty")
    if "SHA256(" in text and "=" in text:
        digest = text.split("=", 1)[1].strip()
    else:
        digest = text.split()[0].strip()
    digest = digest.lower()
    if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
        raise PreflightError("independent_digest_parse_failed:" + text[:120])
    return "sha256:" + digest


def independent_sha256(path: Path, tool: list[str]) -> str:
    completed = subprocess.run(
        [*tool, str(path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise PreflightError("independent_digest_failed:" + detail[:240])
    return parse_independent_digest(completed.stdout.decode("utf-8", errors="replace"))


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


def _load_json(path: Path) -> dict[str, Any]:
    raw = read_bytes(path)
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PreflightError("json_parse_failed:" + path.as_posix()) from exc
    if not isinstance(value, dict):
        raise PreflightError("json_object_required:" + path.as_posix())
    return value


def _case_file_map(root: Path, case_id: str) -> dict[str, Path]:
    case_dir = root / case_id
    found: dict[str, Path] = {}
    if not case_dir.is_dir():
        return found
    for path in sorted(case_dir.rglob("*")):
        if path.is_file():
            found[path.relative_to(case_dir).as_posix()] = path
    return found


def snapshot_fixture_bytes(fixture_root: Path) -> dict[str, str]:
    snapshot: dict[str, str] = {}
    for path in sorted(fixture_root.rglob("*")):
        if path.is_file():
            snapshot[path.relative_to(fixture_root).as_posix()] = sha256_bytes(read_bytes(path))
    return snapshot


def build_preflight(
    *,
    apparatus_root: Path,
    apparatus_source_commit: str,
    fixture_root: Path,
    recovery_manifest: Path,
    verification_receipt: Path,
    composition_results: list[Path],
    guard: RuntimeGuard,
    independent_digest_tool: list[str] | None = None,
) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    fixture_root = fixture_root.resolve()
    apparatus_root = apparatus_root.resolve()
    recovery_manifest = recovery_manifest.resolve()
    verification_receipt = verification_receipt.resolve()
    composition_results = [path.resolve() for path in composition_results]
    before_snapshot = snapshot_fixture_bytes(fixture_root)
    digest_tool = independent_digest_tool or resolve_independent_digest_tool()

    observed_head = git_text(apparatus_root, "rev-parse", "HEAD")
    _record(checks, "apparatus_head_equals_source_commit", observed_head, apparatus_source_commit)

    ancestor = subprocess.run(
        [
            "git",
            "-C",
            str(apparatus_root),
            "merge-base",
            "--is-ancestor",
            PREREGISTRATION_COMMIT,
            apparatus_source_commit,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    _record(
        checks,
        "preregistration_is_ancestor",
        ancestor.returncode,
        0,
        passed=ancestor.returncode == 0,
    )
    if ancestor.returncode != 0:
        raise PreflightError("preregistration_not_ancestor")

    authority_path = apparatus_root / AUTHORITY_RELATIVE_PATH
    runner_path = apparatus_root / RUNNER_RELATIVE_PATH
    preflight_path = apparatus_root / RECEIPT_PREFLIGHT_RELATIVE_PATH
    for path, label in (
        (authority_path, "fixture_authority"),
        (runner_path, "scientific_runner"),
        (preflight_path, "receipt_preflight"),
    ):
        _record(checks, label + "_present", path.is_file(), True)

    prereg_authority_blob = git_text(
        apparatus_root, "rev-parse", f"{PREREGISTRATION_COMMIT}:{AUTHORITY_RELATIVE_PATH}"
    )
    source_authority_blob = git_text(
        apparatus_root, "rev-parse", f"{apparatus_source_commit}:{AUTHORITY_RELATIVE_PATH}"
    )
    worktree_authority_blob = git_text(apparatus_root, "hash-object", str(authority_path))
    authority_bytes = read_bytes(authority_path)
    _record(checks, "fixture_authority_preregistration_blob", prereg_authority_blob, FIXTURE_AUTHORITY_BLOB)
    _record(checks, "fixture_authority_source_blob", source_authority_blob, FIXTURE_AUTHORITY_BLOB)
    _record(checks, "fixture_authority_worktree_blob", worktree_authority_blob, FIXTURE_AUTHORITY_BLOB)
    _record(checks, "fixture_authority_byte_sha256_present", sha256_bytes(authority_bytes).startswith("sha256:"), True)

    runner_source_blob = git_text(
        apparatus_root, "rev-parse", f"{apparatus_source_commit}:{RUNNER_RELATIVE_PATH}"
    )
    runner_worktree_blob = git_text(apparatus_root, "hash-object", str(runner_path))
    preflight_source_blob = git_text(
        apparatus_root, "rev-parse", f"{apparatus_source_commit}:{RECEIPT_PREFLIGHT_RELATIVE_PATH}"
    )
    preflight_worktree_blob = git_text(apparatus_root, "hash-object", str(preflight_path))
    _record(checks, "scientific_runner_source_blob", runner_source_blob, RUNNER_BLOB)
    _record(checks, "scientific_runner_worktree_blob", runner_worktree_blob, RUNNER_BLOB)
    _record(checks, "receipt_preflight_source_blob", preflight_source_blob, RECEIPT_PREFLIGHT_BLOB)
    _record(checks, "receipt_preflight_worktree_blob", preflight_worktree_blob, RECEIPT_PREFLIGHT_BLOB)

    authority = json.loads(authority_bytes.decode("utf-8"))
    if not isinstance(authority, dict):
        raise PreflightError("fixture_authority_not_object")
    _record(checks, "authority_experiment_id", authority.get("experiment_id"), EXPERIMENT_ID)
    _record(
        checks,
        "authority_runner_blob_pin",
        authority.get("predecessor", {}).get("runner_blob"),
        RUNNER_BLOB,
    )
    _record(
        checks,
        "authority_receipt_preflight_blob_pin",
        authority.get("predecessor", {}).get("receipt_preflight_blob"),
        RECEIPT_PREFLIGHT_BLOB,
    )

    frozen_files = authority.get("fixture_files")
    if not isinstance(frozen_files, dict):
        raise PreflightError("fixture_authority_files_missing")
    frozen_recovery = authority.get("fixture_recovery")
    if not isinstance(frozen_recovery, dict):
        raise PreflightError("fixture_recovery_record_missing")
    expected_manifest_sha256 = frozen_recovery.get("manifest_sha256")
    expected_verification_sha256 = frozen_recovery.get("verification_json_sha256")
    expected_composition_sha256 = frozen_recovery.get("composition_result_sha256")

    root_names = {entry.name for entry in fixture_root.iterdir()}
    _record(checks, "fixture_root_entries", sorted(root_names), sorted(ALLOWED_FIXTURE_ROOT_NAMES))
    extra_root = sorted(root_names - ALLOWED_FIXTURE_ROOT_NAMES)
    _record(checks, "fixture_root_has_no_unexpected_entries", extra_root, [])

    observed_files: dict[str, dict[str, dict[str, str]]] = {}
    independent_files: dict[str, dict[str, str]] = {}
    for case_id in REQUIRED_CASES:
        _record(checks, case_id + "_directory_present", (fixture_root / case_id).is_dir(), True)
        found = _case_file_map(fixture_root, case_id)
        _record(checks, case_id + "_exact_runner_read_files", sorted(found), sorted(REQUIRED_RELATIVE_FILES))
        extra_files = sorted(set(found) - set(REQUIRED_RELATIVE_FILES))
        missing_files = sorted(set(REQUIRED_RELATIVE_FILES) - set(found))
        _record(checks, case_id + "_missing_required_files", missing_files, [])
        _record(checks, case_id + "_unexpected_runner_read_files", extra_files, [])
        observed_files[case_id] = {}
        independent_files[case_id] = {}
        frozen_case = frozen_files.get(case_id)
        if not isinstance(frozen_case, dict):
            raise PreflightError("frozen_case_missing:" + case_id)
        for relative in REQUIRED_RELATIVE_FILES:
            path = found.get(relative)
            frozen_entry = frozen_case.get(relative)
            if not isinstance(frozen_entry, dict):
                raise PreflightError("frozen_file_missing:" + case_id + "/" + relative)
            expected_sha256 = frozen_entry.get("sha256")
            expected_provenance = frozen_entry.get("provenance")
            required_provenance = REQUIRED_PROVENANCE[relative]
            _record(
                checks,
                f"{case_id}/{relative}/frozen_provenance",
                expected_provenance,
                required_provenance,
            )
            if path is None:
                _record(checks, f"{case_id}/{relative}/present", False, True)
                continue
            raw = read_bytes(path)
            observed_sha256 = sha256_bytes(raw)
            independent = independent_sha256(path, digest_tool)
            observed_files[case_id][relative] = {
                "sha256": observed_sha256,
                "provenance": required_provenance,
                "bytes": str(len(raw)),
            }
            independent_files[case_id][relative] = independent
            _record(checks, f"{case_id}/{relative}/sha256", observed_sha256, expected_sha256)
            _record(
                checks,
                f"{case_id}/{relative}/independent_sha256",
                independent,
                expected_sha256,
            )
            _record(
                checks,
                f"{case_id}/{relative}/hashlib_matches_independent",
                independent,
                observed_sha256,
            )

    if not recovery_manifest.is_file():
        raise PreflightError("recovery_manifest_missing")
    if not verification_receipt.is_file():
        raise PreflightError("verification_receipt_missing")
    manifest_bytes = read_bytes(recovery_manifest)
    verification_bytes = read_bytes(verification_receipt)
    manifest_sha256 = sha256_bytes(manifest_bytes)
    verification_sha256 = sha256_bytes(verification_bytes)
    manifest_independent = independent_sha256(recovery_manifest, digest_tool)
    verification_independent = independent_sha256(verification_receipt, digest_tool)
    _record(checks, "recovery_manifest_sha256", manifest_sha256, expected_manifest_sha256)
    _record(checks, "recovery_manifest_independent_sha256", manifest_independent, expected_manifest_sha256)
    _record(checks, "verification_receipt_sha256", verification_sha256, expected_verification_sha256)
    _record(
        checks,
        "verification_receipt_independent_sha256",
        verification_independent,
        expected_verification_sha256,
    )

    manifest = json.loads(manifest_bytes.decode("utf-8"))
    verification = json.loads(verification_bytes.decode("utf-8"))
    if not isinstance(manifest, dict) or not isinstance(verification, dict):
        raise PreflightError("recovery_documents_not_objects")

    for document_name, document in (("manifest", manifest), ("verification", verification)):
        cases = document.get("cases")
        if not isinstance(cases, dict):
            raise PreflightError(document_name + "_cases_missing")
        for case_id in REQUIRED_CASES:
            case_entry = cases.get(case_id)
            if not isinstance(case_entry, dict):
                raise PreflightError(document_name + "_case_missing:" + case_id)
            for relative in REQUIRED_RELATIVE_FILES:
                file_entry = case_entry.get(relative)
                if not isinstance(file_entry, dict):
                    raise PreflightError(document_name + "_file_missing:" + case_id + "/" + relative)
                recorded_sha256 = file_entry.get("sha256")
                recorded_provenance = file_entry.get("provenance_classification")
                frozen_entry = frozen_files[case_id][relative]
                _record(
                    checks,
                    f"{document_name}/{case_id}/{relative}/recorded_sha256",
                    recorded_sha256,
                    frozen_entry["sha256"],
                )
                _record(
                    checks,
                    f"{document_name}/{case_id}/{relative}/provenance_classification",
                    recorded_provenance,
                    REQUIRED_PROVENANCE[relative],
                )
                _record(
                    checks,
                    f"{document_name}/{case_id}/{relative}/provenance_matches_frozen_authority",
                    recorded_provenance,
                    frozen_entry["provenance"],
                )
        recorded_composition = document.get("historical_run", {}).get("composition_result_sha256")
        _record(
            checks,
            document_name + "_recorded_composition_result_sha256",
            recorded_composition,
            expected_composition_sha256,
        )

    composition_observed: list[dict[str, str]] = []
    for composition_path in composition_results:
        if not composition_path.is_file():
            raise PreflightError("composition_result_missing:" + composition_path.as_posix())
        raw = read_bytes(composition_path)
        observed = sha256_bytes(raw)
        independent = independent_sha256(composition_path, digest_tool)
        composition_observed.append(
            {
                "path": str(composition_path),
                "sha256": observed,
                "independent_sha256": independent,
            }
        )
        _record(checks, "composition_result_sha256:" + composition_path.name, observed, expected_composition_sha256)
        _record(
            checks,
            "composition_result_independent_sha256:" + composition_path.name,
            independent,
            expected_composition_sha256,
        )

    after_snapshot = snapshot_fixture_bytes(fixture_root)
    _record(checks, "fixture_bytes_unmodified", after_snapshot, before_snapshot)
    _record(checks, "loaded_forbidden_modules", loaded_forbidden_modules(), [])
    _record(checks, "contract_e_evaluation_calls", guard.contract_e_evaluation_calls, 0)
    _record(checks, "supervisor_process_launches", guard.supervisor_process_launches, 0)
    _record(checks, "scientific_runner_imports", guard.scientific_runner_imports, 0)
    _record(checks, "ers_candidate_runtime_imports", guard.ers_candidate_runtime_imports, 0)
    _record(checks, "network_attempts", guard.network_attempts, 0)

    failures = [item for item in checks if item.get("passed") is not True]
    if failures:
        raise PreflightError(json.dumps({"failures": failures}, sort_keys=True))

    subject = {
        "experiment_id": EXPERIMENT_ID,
        "preregistration_commit": PREREGISTRATION_COMMIT,
        "fixture_authority_blob": FIXTURE_AUTHORITY_BLOB,
        "runner_blob": RUNNER_BLOB,
        "receipt_preflight_blob": RECEIPT_PREFLIGHT_BLOB,
        "fixture_files": {
            case_id: {
                relative: {
                    "sha256": observed_files[case_id][relative]["sha256"],
                    "provenance": observed_files[case_id][relative]["provenance"],
                }
                for relative in REQUIRED_RELATIVE_FILES
            }
            for case_id in REQUIRED_CASES
        },
        "manifest_sha256": manifest_sha256,
        "verification_json_sha256": verification_sha256,
        "composition_result_sha256": expected_composition_sha256,
    }
    return {
        "schema": SCHEMA,
        "status": "PASS",
        "disposition": PASS_DISPOSITION,
        "experiment_id": EXPERIMENT_ID,
        "scientific_hypothesis_result": "NOT_RUN",
        "scientific_matrix_authorized": False,
        "historical_authority_claim_for_reconstructed_inputs": False,
        "executor_authorized": False,
        "mainframe_write_authorized": False,
        "preregistration": {
            "repository": "camerontjs-dot/apparatus-contracts",
            "pull_request": 139,
            "commit": PREREGISTRATION_COMMIT,
            "fixture_authority_path": AUTHORITY_RELATIVE_PATH,
            "fixture_authority_blob": FIXTURE_AUTHORITY_BLOB,
            "fixture_authority_sha256": sha256_bytes(authority_bytes),
        },
        "apparatus_source": {
            "commit": apparatus_source_commit,
            "head": observed_head,
            "runner_path": RUNNER_RELATIVE_PATH,
            "runner_blob": runner_worktree_blob,
            "receipt_preflight_path": RECEIPT_PREFLIGHT_RELATIVE_PATH,
            "receipt_preflight_blob": preflight_worktree_blob,
        },
        "fixture_root": {
            "path": str(fixture_root),
            "path_identity_preregistered": False,
            "entries": sorted(root_names),
        },
        "observed_fixture_files": observed_files,
        "independent_digest": {
            "tool": digest_tool,
            "fixture_files": independent_files,
            "manifest_sha256": manifest_independent,
            "verification_json_sha256": verification_independent,
            "composition_results": composition_observed,
        },
        "recovery_identities": {
            "manifest_path": str(recovery_manifest),
            "manifest_sha256": manifest_sha256,
            "verification_receipt_path": str(verification_receipt),
            "verification_json_sha256": verification_sha256,
            "composition_result_sha256": expected_composition_sha256,
            "composition_result_files": composition_observed,
        },
        "subject_identity": sha256_bytes(canonical_json_bytes(subject)),
        "subject": subject,
        "compared_values": checks,
        "instrumentation": guard.summary(),
        "nonclaims": [
            "This gate passing means only QUALIFIED_FIXTURE_BOUND_SCIENTIFIC_SUBJECT.",
            "It does not mean the evaluation-time provenance hypothesis passed.",
            "It does not turn reconstructed consumer-inputs.json or decision-target.json into historical bytes.",
            "It does not authorize an executor, ERS write, production promotion, or MainFrame mutation.",
            "It does not authorize the PR #130 decisive matrix.",
        ],
    }


def _failure_receipt(exc: BaseException, guard: RuntimeGuard) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "status": "FAIL",
        "disposition": "FIXTURE_BINDING_FAILED",
        "experiment_id": EXPERIMENT_ID,
        "scientific_hypothesis_result": "NOT_RUN",
        "scientific_matrix_authorized": False,
        "error_type": type(exc).__name__,
        "error": str(exc),
        "instrumentation": guard.summary(),
        "nonclaims": [
            "A failed fixture-binding gate is not a scientific result about evaluation-time provenance.",
            "No Contract E evaluation or PR #130 matrix ran.",
        ],
    }


def run_preflight(
    *,
    apparatus_root: Path,
    apparatus_source_commit: str,
    fixture_root: Path,
    recovery_manifest: Path,
    verification_receipt: Path,
    composition_results: list[Path],
    output_path: Path | None = None,
    independent_digest_tool: list[str] | None = None,
) -> dict[str, Any]:
    if output_path is not None:
        output_path = output_path.resolve()
        if not output_path.parent.is_dir():
            raise SystemExit("preflight_output_parent_missing")
        if output_path.exists():
            raise SystemExit("preflight_output_path_exists")
    guard = RuntimeGuard()
    sys.addaudithook(guard.audit)
    sys.setprofile(guard.profile)
    try:
        result = build_preflight(
            apparatus_root=apparatus_root,
            apparatus_source_commit=apparatus_source_commit,
            fixture_root=fixture_root,
            recovery_manifest=recovery_manifest,
            verification_receipt=verification_receipt,
            composition_results=composition_results,
            guard=guard,
            independent_digest_tool=independent_digest_tool,
        )
    except Exception as exc:
        result = _failure_receipt(exc, guard)
        if output_path is not None:
            output_path.write_bytes(canonical_json_bytes(result))
        return result
    finally:
        sys.setprofile(None)
    if output_path is not None:
        output_path.write_bytes(canonical_json_bytes(result))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apparatus-root", required=True, type=Path)
    parser.add_argument("--apparatus-source-commit", required=True)
    parser.add_argument("--fixture-root", required=True, type=Path)
    parser.add_argument("--recovery-manifest", required=True, type=Path)
    parser.add_argument("--verification-receipt", required=True, type=Path)
    parser.add_argument("--composition-result", action="append", default=[], type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = run_preflight(
        apparatus_root=args.apparatus_root,
        apparatus_source_commit=args.apparatus_source_commit,
        fixture_root=args.fixture_root,
        recovery_manifest=args.recovery_manifest,
        verification_receipt=args.verification_receipt,
        composition_results=list(args.composition_result),
        output_path=args.output,
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
