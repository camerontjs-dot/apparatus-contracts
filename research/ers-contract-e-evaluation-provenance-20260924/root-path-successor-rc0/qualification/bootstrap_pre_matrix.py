#!/usr/bin/env python3
"""Pre-matrix bootstrap gate for the ERS 05 repository-root successor.

Invokes a runner with the frozen scientific argument shape and stops at the
hold-case boundary, before supervisor launch or Contract E. One process runs
one runner. Discrimination mode reinvokes this file.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import linecache
from pathlib import Path

PREDECESSOR_BLOB = "79a347c9698610a1c743074e426a79590cb32ba4"
SUCCESSOR_RUNNER = (
    "research/ers-contract-e-evaluation-provenance-20260921/"
    "fixture-bound-identity-successor-rc0/reproduce_rc6_fixture_bound.py"
)
RECEIPT = (
    "research/ers-contract-e-evaluation-provenance-20260921/"
    "fixture-bound-receipt-contract-successor-rc0/FREEZE_RECEIPT.json"
)
PREFLIGHT = (
    "research/ers-contract-e-evaluation-provenance-20260921/"
    "fixture-bound-receipt-contract-successor-rc0/qualification-20260923/POSITIVE.json"
)
SCHEMA = (
    "research/ers-contract-e-evaluation-provenance-20260921/"
    "schemas/contract-e-evaluation-transcript.rc0.schema.json"
)
PROFILE = "research/provenance-link-explicit-rc0/validator.py"
ISSUER_PUBLIC = "sha256:e7f4581c2d58eecd0279f895cf3dd49df3098d092fa1e083731d802fcd1db259"
KEYCHAIN_SERVICE = "CAL Pipeline ERS-EVAL-TIME-PROV-05 issuer"
BOUNDARY_TEXT = "hold_cases: dict[str, Any] = {}"
FAILING_HEAD = (
    "HEAD:ers-contract-e-evaluation-provenance-20260921/"
    "fixture-bound-receipt-contract-successor-rc0/FREEZE_RECEIPT.json"
)
STAGE_MARKERS = (
    ("cli_entered_run_matrix", "def run_matrix"),
    ("root_pins", "expected_pins = {"),
    ("ancestry_and_cal_v3", "cal_v3_object_missing"),
    ("transcript_schema", "transcript_schema_blob_mismatch"),
    ("ers_freeze_receipt", "ers_source_commit_freeze_mismatch"),
    ("apparatus_freeze_receipt", "apparatus_source_commit_freeze_mismatch"),
    ("preflight_receipt", "receipt_consistency_preflight_not_pass"),
    ("repository_relative_conversion", "relative_to(ROOT)"),
    ("head_path_resolution", "apparatus_freeze_receipt_not_in_frozen_head"),
    ("contract_e_profile_module", "contract_e_profile.py"),
    ("render_bound_module", "ers-render-bound-shadow-composition"),
    ("issuer_public_key", "pinned_public_key_identity_mismatch"),
    ("fixture_location", "pipe01_fixture_missing"),
    ("sandbox_read", "sandbox_not_empty_before_decisive_run"),
    ("execution_intent_identity", "five_inherited_input_identities_changed"),
)
PASS_STAGES = (
    "head_path_resolution",
    "issuer_public_key",
    "fixture_location",
    "sandbox_read",
    "execution_intent_identity",
)


class BootstrapBoundary(BaseException):
    """Stop before the first scientific statement. Not an Exception, so the runner's failure writer does not relabel it."""


class ScientificForbidden(BaseException):
    def __init__(self, kind: str) -> None:
        self.kind = kind
        super().__init__(kind)


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def blob_oid(raw: bytes) -> str:
    header = b"blob " + str(len(raw)).encode("ascii") + b"\0"
    return hashlib.sha1(header + raw).hexdigest()


def public_identity(pem: bytes) -> str:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    key = serialization.load_pem_private_key(pem, password=None)
    if not isinstance(key, Ed25519PrivateKey):
        raise RuntimeError("issuer_key_not_ed25519")
    public = key.public_key().public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return "sha256:" + sha256(public)


def materialize_key(directory: Path) -> Path:
    raw = subprocess.check_output(
        [
            "security", "find-generic-password",
            "-s", KEYCHAIN_SERVICE,
            "-a", ISSUER_PUBLIC,
            "-w",
        ]
    )
    pem = bytes.fromhex(raw.decode().strip())
    if public_identity(pem) != ISSUER_PUBLIC:
        raise RuntimeError("issuer_public_identity_mismatch")
    path = directory / "issuer.pem"
    path.write_bytes(pem)
    path.chmod(0o600)
    return path


def discover_mainframe(start: Path) -> Path | None:
    supplied = os.environ.get("MAINFRAME_ROOT")
    if supplied:
        candidate = Path(supplied)
        if (candidate / "HARNESS.md").is_file():
            return candidate.resolve()
    for parent in [start, *start.parents]:
        if parent.name == "MainFrame" and (parent / "HARNESS.md").is_file():
            return parent.resolve()
    return None


def classify(error: str, boundary: bool, counters: dict) -> str:
    scientific = any(counters[name] for name in (
        "contract_e_evaluations", "supervisor_launches", "scientific_pipe_cases",
        "scientific_mutations", "scientific_sandbox_creations", "mainframe_write_attempts",
    ))
    if scientific:
        return "scientific_execution_attempted"
    if boundary and all(stage in counters["stages"] for stage in PASS_STAGES):
        return "bootstrap_pass"
    if (
        FAILING_HEAD in error
        and "HEAD:research/ers-contract-e-evaluation-provenance-20260921/" not in error
        and "/research', 'rev-parse'" in error
    ):
        return "repository_root_path_defect"
    if "is not in the subpath" in error:
        return "receipt_path_outside_repository"
    return "incidental_failure"


def execute(runner: Path, apparatus: Path, output: Path, receipt_path: Path, sandbox: Path) -> dict:
    runner = runner.resolve()
    apparatus = apparatus.resolve()
    output = output.resolve()
    sandbox = sandbox.resolve()
    if output.exists():
        raise RuntimeError("output_exists")
    if not sandbox.is_dir() or any(sandbox.iterdir()):
        raise RuntimeError("sandbox_not_empty_directory")
    counters = {
        "contract_e_evaluations": 0,
        "supervisor_launches": 0,
        "scientific_pipe_cases": 0,
        "scientific_mutations": 0,
        "scientific_sandbox_creations": 0,
        "network_attempts": 0,
        "mainframe_write_attempts": 0,
        "non_git_processes": [],
        "stages": [],
    }
    key_dir = Path(tempfile.mkdtemp(prefix="ers05-issuer-"))
    key_path = materialize_key(key_dir)
    mainframe = discover_mainframe(apparatus)
    original_popen = subprocess.Popen
    original_connect = socket.socket.connect
    original_create_connection = socket.create_connection
    original_mkdir = Path.mkdir
    original_open = open
    original_tempdir = tempfile.TemporaryDirectory

    def record_stage(line: str) -> None:
        for name, marker in STAGE_MARKERS:
            if marker in line and name not in counters["stages"]:
                counters["stages"].append(name)

    def traced(frame, event, arg):
        if event == "line" and frame.f_code.co_name == "run_matrix" and frame.f_code.co_filename == str(runner):
            line = linecache.getline(frame.f_code.co_filename, frame.f_lineno)
            record_stage(line)
            if BOUNDARY_TEXT in line:
                raise BootstrapBoundary()
        return traced

    def guarded_popen(command, *args, **kwargs):
        rendered = command if isinstance(command, str) else " ".join(str(part) for part in command)
        if "qualification_supervisor.py" in rendered:
            counters["supervisor_launches"] += 1
            raise ScientificForbidden("supervisor")
        executable = command[0] if isinstance(command, (list, tuple)) and command else rendered
        if Path(str(executable)).name != "git":
            counters["non_git_processes"].append(rendered[:240])
        return original_popen(command, *args, **kwargs)

    def guarded_connect(self, address):
        counters["network_attempts"] += 1
        raise ScientificForbidden("network")

    def guarded_create_connection(*args, **kwargs):
        counters["network_attempts"] += 1
        raise ScientificForbidden("network")

    def guarded_mkdir(self, mode=0o777, parents=False, exist_ok=False):
        if self.resolve() == sandbox and not self.exists():
            counters["scientific_sandbox_creations"] += 1
            raise ScientificForbidden("sandbox_creation")
        return original_mkdir(self, mode, parents, exist_ok)

    def guarded_tempdir(*args, **kwargs):
        if kwargs.get("prefix") == "ers-rc6-supervisor-":
            counters["scientific_sandbox_creations"] += 1
            raise ScientificForbidden("supervisor_runtime_directory")
        return original_tempdir(*args, **kwargs)

    def guarded_open(file, mode="r", *args, **kwargs):
        writing = any(flag in mode for flag in ("w", "a", "x", "+"))
        if writing and mainframe is not None:
            try:
                target = Path(file).resolve()
            except OSError:
                target = None
            if target is not None and (target == mainframe or mainframe in target.parents):
                counters["mainframe_write_attempts"] += 1
                raise ScientificForbidden("mainframe_write")
        return original_open(file, mode, *args, **kwargs)

    spec = importlib.util.spec_from_file_location("ers05_bootstrap_runner", runner)
    if spec is None or spec.loader is None:
        raise RuntimeError("runner_import_spec_failed")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    original_load = module.load_module
    original_start = module.start_supervisor

    def guarded_load(name, path):
        loaded = original_load(name, path)
        profile = getattr(loaded, "integration_profile", None)
        if profile is not None and hasattr(profile, "evaluate"):
            def forbidden_evaluate(*args, **kwargs):
                counters["contract_e_evaluations"] += 1
                raise ScientificForbidden("contract_e")
            profile.evaluate = forbidden_evaluate
        if hasattr(loaded, "shadow_gate"):
            def forbidden_shadow(*args, **kwargs):
                counters["scientific_pipe_cases"] += 1
                raise ScientificForbidden("shadow_gate")
            loaded.shadow_gate = forbidden_shadow
        return loaded

    def guarded_start(*args, **kwargs):
        counters["supervisor_launches"] += 1
        raise ScientificForbidden("supervisor")

    module.load_module = guarded_load
    module.start_supervisor = guarded_start
    subprocess.Popen = guarded_popen
    socket.socket.connect = guarded_connect
    socket.create_connection = guarded_create_connection
    Path.mkdir = guarded_mkdir
    tempfile.TemporaryDirectory = guarded_tempdir
    builtins_open = guarded_open
    import builtins
    builtins.open = builtins_open

    argv = [
        str(runner),
        "--ers-root", os.environ["ERS05_ERS_ROOT"],
        "--ers-source-commit", "65f47d029fb734be1d5d506a135cbeba813f6be8",
        "--apparatus-source-commit", "b868e66523ed622dbc6615d22d5f73f81cbda94f",
        "--apparatus-freeze-receipt", str(receipt_path),
        "--preflight-pass-receipt", str(apparatus / PREFLIGHT),
        "--decision-root", os.environ["ERS05_DECISION_ROOT"],
        "--contract-e-root", os.environ["ERS05_CONTRACT_E_ROOT"],
        "--contract-d-root", os.environ["ERS05_CONTRACT_D_ROOT"],
        "--consumer-root", os.environ["ERS05_CONSUMER_ROOT"],
        "--fixtures", os.environ["ERS05_FIXTURES"],
        "--sandbox-root", str(sandbox),
        "--transcript-schema", str(apparatus / SCHEMA),
        "--provenance-profile", os.environ["ERS05_PROVENANCE_PROFILE"],
        "--issuer-private-key", str(key_path),
        "--output", str(output),
    ]
    previous_argv = sys.argv
    previous_trace = sys.gettrace()
    boundary = False
    error = ""
    error_type = ""
    exit_code = None
    try:
        sys.argv = argv
        sys.settrace(traced)
        try:
            exit_code = module.main()
        except BootstrapBoundary:
            boundary = True
        except ScientificForbidden as exc:
            error_type = "ScientificForbidden"
            error = exc.kind
    except Exception as exc:
        error_type = type(exc).__name__
        error = str(exc)
    finally:
        sys.settrace(previous_trace)
        sys.argv = previous_argv
        subprocess.Popen = original_popen
        socket.socket.connect = original_connect
        socket.create_connection = original_create_connection
        Path.mkdir = original_mkdir
        tempfile.TemporaryDirectory = original_tempdir
        builtins.open = original_open
        key_path.unlink(missing_ok=True)
        key_dir.rmdir()
    if output.is_dir() and (output / "FAILURE.json").is_file() and not error:
        failure = json.loads((output / "FAILURE.json").read_text(encoding="utf-8"))
        error_type = failure.get("error_type", "")
        error = failure.get("error", "")
    sandbox_entries = sorted(path.name for path in sandbox.iterdir())
    outcome = classify(error, boundary, counters)
    return {
        "schema": "ers-05-bootstrap-pre-matrix/1",
        "runner": str(runner),
        "runner_blob": blob_oid(runner.read_bytes()),
        "apparatus_head": subprocess.check_output(["git", "-C", str(apparatus), "rev-parse", "HEAD"], text=True).strip(),
        "outcome": outcome,
        "boundary_reached": boundary,
        "exit_code": exit_code,
        "error_type": error_type,
        "error": error,
        "stages": counters["stages"],
        "counters": {
            "contract_e_evaluations": counters["contract_e_evaluations"],
            "supervisor_launches": counters["supervisor_launches"],
            "scientific_pipe_cases": counters["scientific_pipe_cases"],
            "scientific_mutations": counters["scientific_mutations"],
            "scientific_sandbox_creations": counters["scientific_sandbox_creations"],
            "network_attempts": counters["network_attempts"],
            "mainframe_write_attempts": counters["mainframe_write_attempts"],
            "non_git_processes": counters["non_git_processes"],
        },
        "sandbox_entries_after": sandbox_entries,
        "runner_output_files": sorted(path.name for path in output.iterdir()) if output.is_dir() else [],
        "issuer_public_identity_checked_before_runner": True,
        "private_key_material_retained": False,
    }


def prepare_case(root: Path, name: str) -> tuple[Path, Path]:
    output = root / name / "runner-output"
    sandbox = root / name / "sandbox"
    output.parent.mkdir(parents=True, exist_ok=True)
    sandbox.mkdir()
    return output, sandbox


def write_receipt(path: Path, report: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("execute", "discriminate"), required=True)
    parser.add_argument("--runner", type=Path)
    parser.add_argument("--apparatus", type=Path)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--work-root", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--successor-repo", type=Path)
    args = parser.parse_args()
    if args.mode == "execute":
        missing = [name for name in ("runner", "apparatus", "receipt", "output") if getattr(args, name) is None]
        if missing:
            raise SystemExit("missing:" + ",".join(missing))
        output, sandbox = prepare_case(args.work_root, args.output.stem)
        # `prepare_case` creates a fresh sandbox. The caller-selected output
        # directory is the receipt, while the runner output lives beside it.
        runner_output = args.work_root / args.output.stem / "runner-output"
        if runner_output.exists():
            shutil.rmtree(runner_output)
        sandbox = args.work_root / args.output.stem / "sandbox"
        if sandbox.exists():
            shutil.rmtree(sandbox)
        sandbox.mkdir(parents=True)
        report = execute(args.runner, args.apparatus, runner_output, args.receipt, sandbox)
        write_receipt(args.output, report)
        print(json.dumps({"outcome": report["outcome"], "stages": report["stages"], "counters": report["counters"]}, sort_keys=True))
        return 0 if report["outcome"] in {
            "bootstrap_pass", "repository_root_path_defect", "receipt_path_outside_repository"
        } else 1

    repo = args.successor_repo.resolve()
    predecessor = Path(os.environ["ERS05_PREDECESSOR_RUNNER"])
    cases = []
    successor_runner = repo / SUCCESSOR_RUNNER
    successor_receipt = repo / RECEIPT
    # Predecessor frozen file, unchanged checkout.
    cases.append(("predecessor", predecessor, Path(os.environ["ERS05_PREDECESSOR_APPARATUS"]), Path(os.environ["ERS05_PREDECESSOR_APPARATUS"]) / RECEIPT, "repository_root_path_defect"))
    cases.append(("successor", successor_runner, repo, successor_receipt, "bootstrap_pass"))
    wrong_root = Path(tempfile.mkdtemp(prefix="ers05-wrong-root-"))
    subprocess.check_call(["git", "-C", str(repo), "worktree", "add", "--detach", str(wrong_root), "HEAD"])
    wrong_runner = wrong_root / SUCCESSOR_RUNNER
    text = wrong_runner.read_text(encoding="utf-8")
    replaced = text.replace("ROOT = HERE.parents[2]", "ROOT = HERE.parents[1]", 1)
    if replaced == text:
        raise SystemExit("wrong_root_replacement_failed")
    wrong_runner.write_text(replaced, encoding="utf-8")
    cases.append(("wrong_root", wrong_runner, wrong_root, wrong_root / RECEIPT, "repository_root_path_defect"))
    outside = args.work_root / "outside-receipt"
    outside.mkdir(parents=True, exist_ok=True)
    outside_receipt = outside / "FREEZE_RECEIPT.json"
    shutil.copyfile(successor_receipt, outside_receipt)
    cases.append(("wrong_receipt_path", successor_runner, repo, outside_receipt, "receipt_path_outside_repository"))

    results = []
    for name, runner, apparatus, receipt, expected in cases:
        receipt_path = args.work_root / f"{name}.json"
        command = [
            sys.executable, str(Path(__file__).resolve()),
            "--mode", "execute",
            "--runner", str(runner),
            "--apparatus", str(apparatus),
            "--receipt", str(receipt),
            "--work-root", str(args.work_root),
            "--output", str(receipt_path),
        ]
        completed = subprocess.run(command, text=True, capture_output=True)
        report = json.loads(receipt_path.read_text(encoding="utf-8")) if receipt_path.is_file() else {
            "outcome": "incidental_failure",
            "error": completed.stderr[-1000:],
        }
        results.append({
            "name": name,
            "expected": expected,
            "outcome": report.get("outcome"),
            "matched": report.get("outcome") == expected,
            "runner_blob": report.get("runner_blob"),
            "stages": report.get("stages", []),
            "counters": report.get("counters", {}),
            "error_type": report.get("error_type"),
            "error": report.get("error"),
            "process_exit": completed.returncode,
        })
    summary = {
        "schema": "ers-05-bootstrap-discrimination/1",
        "cases": results,
        "passed": all(item["matched"] for item in results) and results[1]["outcome"] == "bootstrap_pass",
    }
    if args.output:
        write_receipt(args.output, summary)
    print(json.dumps({item["name"]: item["outcome"] for item in results}, sort_keys=True))
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
