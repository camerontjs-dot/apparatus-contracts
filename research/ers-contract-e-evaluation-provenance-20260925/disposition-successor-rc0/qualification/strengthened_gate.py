#!/usr/bin/env python3
"""OS-contained runtime and pre-scientific discrimination gate for ERS 05."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import bootstrap_pre_matrix as bootstrap
ORIGINAL_CLASSIFY = bootstrap.classify

PROFILE_SHA256 = "ac0025ad01d00d87661e34bb83362c4094479c2ff619c3fdbfb5cfd9287c12ce"
RUNNER_PATH = bootstrap.SUCCESSOR_RUNNER
PR148_COMMIT = "b673b2b06804e94042ad35d4621f4a4ca5ee4851"
PR149_COMMIT = "4bd5b030726ed064d410cb8c99e79c23a0426c8a"
PREREG_COMMIT = "e54330db4de2090e8a238823459546d3153a42e3"
REQUIRED_SETUP_CHECKS = {
    "wrong_frozen_decision", "dirty_frozen_decision",
    "wrong_frozen_contract_e", "dirty_frozen_contract_e",
    "wrong_frozen_contract_d", "dirty_frozen_contract_d",
    "wrong_frozen_contract_c_consumer", "dirty_frozen_contract_c_consumer",
    "ers_rc5_not_ancestor", "ers_rc4_not_ancestor",
    "preregistration_not_ancestor", "receipt_contract_preregistration_not_ancestor",
    "cal_v3_object_missing", "wrong_provenance_profile", "dirty_provenance_profile",
    "dirty_frozen_ers_candidate", "frozen_transcript_schema_missing", "transcript_schema_blob_mismatch",
    "noncanonical_ers_source_commit_alias", "ers_source_commit_freeze_mismatch",
    "ers_source_tree_freeze_mismatch", "ers_receipt_preregistration_mismatch",
    "ers_receipt_transcript_schema_mismatch", "ers_source_not_ancestor",
    "apparatus_source_commit_freeze_mismatch", "apparatus_ers_source_commit_mismatch",
    "apparatus_ers_source_tree_mismatch", "apparatus_preregistration_mismatch",
    "apparatus_transcript_schema_mismatch", "receipt_issuer_key_mismatch",
    "frozen_issuer_key_id_changed", "ers_freeze_receipt_commit_mismatch",
    "ers_freeze_receipt_blob_mismatch", "preflight_receipt_schema_mismatch",
    "receipt_consistency_preflight_not_pass", "preflight_experiment_id_mismatch",
    "preflight_ers_freeze_commit_mismatch", "preflight_ers_freeze_blob_mismatch",
    "preflight_apparatus_source_commit_mismatch", "preflight_apparatus_receipt_blob_mismatch",
    "preflight_apparatus_receipt_sha256_mismatch", "preflight_compared_values_missing",
    "preflight_contains_failed_comparison", "contract_e_called_during_preflight",
    "supervisor_started_during_preflight", "candidate_runtime_imported_during_preflight",
    "network_used_during_preflight", "apparatus_freeze_receipt_not_in_frozen_head",
    "preflight_pass_not_in_frozen_head", "contract_e_variable_length_intent_probe_failed",
    "PIPE01:supported_decision_behavior_changed", "PIPE02:supported_decision_behavior_changed",
    "PIPE03:supported_decision_behavior_changed", "PIPE01:supported_contract_d_bytes_changed",
    "PIPE02:supported_contract_d_bytes_changed", "PIPE03:supported_contract_d_bytes_changed",
    "PIPE01:released_d_rejection_changed", "PIPE02:released_d_rejection_changed",
    "PIPE03:released_d_rejection_changed", "pipe01_native_decision_identity_changed",
    "pipe01_claim_content_identity_changed", "pipe01_native_ers_decision_changed",
    "PIPE02:hold_behavior_changed", "PIPE03:hold_behavior_changed",
    "frozen_issuer_key_id_changed", "pinned_public_key_identity_mismatch",
    "independent_render_disagreement", "independent_render_packet_identity_mismatch",
    "independent_payload_identity_mismatch", "payload_terminal_newline_changed",
    "pipe01_fixture_missing", "sandbox_not_empty_before_decisive_run",
    "five_inherited_input_identities_changed", "frozen_contract_e_intent_identity_disagrees",
    "independent_execution_intent_identity_mismatch", "authority_state_fixture_identity_mismatch",
}


def git_text(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def require_head(root: Path, expected: str, label: str, clean: bool = True) -> None:
    if git_text(root, "rev-parse", "HEAD") != expected:
        raise RuntimeError(f"{label}_head_changed")
    if clean and git_text(root, "status", "--porcelain=v1", "--untracked-files=all"):
        raise RuntimeError(f"{label}_checkout_dirty")


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def file_sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def tree_snapshot(root: Path, hash_contents: bool = True) -> dict:
    root = root.resolve()
    if not root.exists():
        raise RuntimeError(f"protected_root_missing:{root.name}")
    digest = hashlib.sha256()
    count = 0
    total_bytes = 0

    def fail(error: OSError) -> None:
        raise error

    for current, dirs, files in os.walk(root, topdown=True, followlinks=False, onerror=fail):
        dirs.sort()
        files.sort()
        current_path = Path(current)
        names = sorted(dirs + files)
        if current_path == root:
            names.append(".")
        for name in names:
            path = current_path if name == "." else current_path / name
            rel = "." if name == "." else path.relative_to(root).as_posix()
            st = path.lstat()
            if path.is_symlink():
                kind = "symlink"
                extra = os.readlink(path)
            elif path.is_dir():
                kind = "directory"
                extra = ""
            elif path.is_file():
                kind = "file"
                extra = ""
                total_bytes += st.st_size
            else:
                kind = "other"
                extra = ""
            content_id = ""
            if hash_contents and kind == "file":
                content_id = file_sha(path)
            row = "\0".join((
                rel, kind, str(st.st_mode), str(st.st_size), str(st.st_mtime_ns),
                str(st.st_ctime_ns), str(st.st_ino), extra, content_id,
            )).encode("utf-8", "surrogateescape")
            digest.update(len(row).to_bytes(8, "big"))
            digest.update(row)
            count += 1
    return {
        "entries": count,
        "file_bytes": total_bytes,
        "sha256": digest.hexdigest(),
        "algorithm": "sorted-lstat-tree-sha256" if hash_contents else "sorted-lstat-metadata-tree-sha256",
    }


def mainframe_git_state(root: Path) -> dict:
    commands = {
        "head": ["git", "-C", str(root), "rev-parse", "HEAD"],
        "status": ["git", "-C", str(root), "status", "--porcelain=v1", "--untracked-files=all"],
    }
    outputs = {}
    env = os.environ.copy()
    env["GIT_OPTIONAL_LOCKS"] = "0"
    for name, command in commands.items():
        result = subprocess.run(command, env=env, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode:
            raise RuntimeError(f"mainframe_git_snapshot_failed:{name}:{result.returncode}")
        outputs[name] = result.stdout
    git_dir = subprocess.check_output(["git", "-C", str(root), "rev-parse", "--git-dir"], env=env, text=True).strip()
    index = (root / git_dir / "index").resolve()
    return {
        "head": outputs["head"].decode().strip(),
        "status_sha256": sha(outputs["status"]),
        "status_entries": len(outputs["status"].splitlines()),
        "index_sha256": file_sha(index) if index.is_file() else None,
    }


def containment_probe(canary: Path) -> dict:
    if not canary.is_dir() or any(canary.iterdir()):
        raise RuntimeError("protected_canary_not_empty")
    before = tree_snapshot(canary)
    attempts = []
    open_target = canary / "ordinary-open.bin"
    try:
        with open(open_target, "wb") as stream:
            stream.write(b"negative-control")
        attempts.append({"api": "open(..., wb)", "result": "WRITE_SUCCEEDED"})
    except OSError as exc:
        attempts.append({"api": "open(..., wb)", "result": "DENIED", "error_type": type(exc).__name__, "errno": exc.errno})

    pathlib_target = canary / "path-write-bytes.bin"
    try:
        pathlib_target.write_bytes(b"negative-control")
        attempts.append({"api": "Path.write_bytes", "result": "WRITE_SUCCEEDED"})
    except OSError as exc:
        attempts.append({"api": "Path.write_bytes", "result": "DENIED", "error_type": type(exc).__name__, "errno": exc.errno})
    after = tree_snapshot(canary)
    passed = all(item["result"] == "DENIED" and item.get("error_type") == "PermissionError" for item in attempts) and before == after
    return {
        "canary_alias": "protected_controls:write_canary",
        "attempts": attempts,
        "before": before,
        "after": after,
        "unchanged": before == after,
        "passed": passed,
    }


def classify(error: str, boundary: bool, counters: dict) -> str:
    if "pipe01_native_ers_decision_changed" in error:
        return "pipe01_disposition_expectation_defect"
    return ORIGINAL_CLASSIFY(error, boundary, counters)


def clean_case(case: dict, alias_roots: list[tuple[str, Path]]) -> dict:
    def clean(value):
        if isinstance(value, str):
            for alias, path in sorted(alias_roots, key=lambda item: len(str(item[1])), reverse=True):
                value = value.replace(str(path.resolve()), f"${alias}")
            return value
        if isinstance(value, list):
            return [clean(item) for item in value]
        if isinstance(value, dict):
            return {key: clean(item) for key, item in value.items()}
        return value
    return clean(case)


def run_child(script: Path, args: list[str], env: dict[str, str]) -> dict:
    completed = subprocess.run(
        [sys.executable, str(script), *args], env=env, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False,
    )
    if completed.returncode:
        raise RuntimeError(f"qualification_substep_failed:{script.name}:{completed.returncode}:{completed.stdout[-2000:]}")
    return {"status": "COMPLETED", "stdout_tail": completed.stdout.splitlines()[-8:]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--pr148-root", required=True, type=Path)
    parser.add_argument("--pr149-root", required=True, type=Path)
    parser.add_argument("--wrong-root", required=True, type=Path)
    parser.add_argument("--wrong-disposition", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--temp-root", required=True, type=Path)
    parser.add_argument("--control-root", required=True, type=Path)
    parser.add_argument("--mainframe-root", required=True, type=Path)
    parser.add_argument("--apparatus-workbench", required=True, type=Path)
    parser.add_argument("--frozen-checkouts", required=True, type=Path)
    parser.add_argument("--fixtures-root", required=True, type=Path)
    parser.add_argument("--sandbox-root", required=True, type=Path)
    parser.add_argument("--runtime-root", required=True, type=Path)
    parser.add_argument("--canary-root", required=True, type=Path)
    parser.add_argument("--profile", required=True, type=Path)
    parser.add_argument("--result", required=True, type=Path)
    args = parser.parse_args()

    repo = args.repo.resolve()
    output_root = args.output_root.resolve()
    temp_root = args.temp_root.resolve()
    control_root = args.control_root.resolve()
    profile_path = args.profile.resolve()
    canary = args.canary_root.resolve()
    if not output_root.is_dir() or not temp_root.is_dir() or not control_root.is_dir():
        raise RuntimeError("qualification_roots_must_be_precreated")
    profile_bytes = profile_path.read_bytes()
    profile_sha = sha(profile_bytes)
    if profile_sha != PROFILE_SHA256:
        raise RuntimeError("write_profile_sha256_mismatch")
    actual_source = git_text(repo, "rev-parse", "HEAD")
    if actual_source != args.source_commit:
        raise RuntimeError("source_commit_changed_before_bootstrap")
    require_head(repo, actual_source, "successor")
    require_head(args.pr148_root, PR148_COMMIT, "pr148")
    require_head(args.pr149_root, PR149_COMMIT, "pr149")
    require_head(args.wrong_root, actual_source, "wrong_root_control", clean=False)
    require_head(args.wrong_disposition, actual_source, "wrong_disposition_control", clean=False)
    committed_runner_blob = git_text(repo, "rev-parse", f"{actual_source}:{RUNNER_PATH}")
    if bootstrap.blob_oid((repo / RUNNER_PATH).read_bytes()) != committed_runner_blob:
        raise RuntimeError("successor_runner_worktree_blob_changed")
    if git_text(args.pr148_root, "rev-parse", f"HEAD:{RUNNER_PATH}") != bootstrap.PREDECESSOR_BLOB:
        raise RuntimeError("pr148_runner_blob_changed")
    if git_text(args.pr149_root, "rev-parse", f"HEAD:{RUNNER_PATH}") != "6c20a20831a34cf83eb38f0b86ae6965a15a7990":
        raise RuntimeError("pr149_runner_blob_changed")
    wrong_root_text = (args.wrong_root / RUNNER_PATH).read_text()
    wrong_disposition_text = (args.wrong_disposition / RUNNER_PATH).read_text()
    if "ROOT = HERE.parents[1]" not in wrong_root_text or 'disposition"] == "pending_review"' in wrong_root_text:
        raise RuntimeError("wrong_root_control_identity_changed")
    if 'disposition"] == "pending_review"' not in wrong_disposition_text or "ROOT = HERE.parents[2]" not in wrong_disposition_text:
        raise RuntimeError("wrong_disposition_control_identity_changed")
    source_parent = git_text(repo, "rev-parse", f"{actual_source}^1")
    preregistration_ancestor = subprocess.run(
        ["git", "-C", str(repo), "merge-base", "--is-ancestor", PREREG_COMMIT, actual_source],
        check=False,
    )
    if preregistration_ancestor.returncode != 0:
        raise RuntimeError("preregistration_not_source_ancestor")

    root_specs = [
        ("mainframe_repo", args.mainframe_root, False),
        ("apparatus_workbench", args.apparatus_workbench, True),
        ("pr148_checkout", args.pr148_root, True),
        ("pr149_checkout", args.pr149_root, True),
        ("successor_checkout", repo, True),
        ("controlled_worktrees", control_root, True),
        ("frozen_checkouts", args.frozen_checkouts, True),
        ("frozen_fixtures", args.fixtures_root, True),
        ("scientific_sandbox", args.sandbox_root, True),
        ("frozen_runtime", args.runtime_root, True),
        ("protected_canary", canary, True),
    ]
    before = {name: tree_snapshot(path, strong) for name, path, strong in root_specs}
    before["mainframe_git_state"] = mainframe_git_state(args.mainframe_root)
    canary_result = containment_probe(canary)
    if not canary_result["passed"]:
        raise RuntimeError("os_write_containment_negative_control_failed")

    env = os.environ.copy()
    env.update({
        "ERS05_ERS_ROOT": str(args.frozen_checkouts / "ers-root"),
        "ERS05_DECISION_ROOT": str(args.frozen_checkouts / "decision-root"),
        "ERS05_CONTRACT_E_ROOT": str(args.frozen_checkouts / "contract-e-root"),
        "ERS05_CONTRACT_D_ROOT": str(args.frozen_checkouts / "contract-d-root"),
        "ERS05_CONSUMER_ROOT": str(args.frozen_checkouts / "consumer-root"),
        "ERS05_PROVENANCE_PROFILE": str(
            args.frozen_checkouts / "provenance-root" / bootstrap.PROFILE
        ),
        "ERS05_FIXTURES": str(args.fixtures_root),
        "MAINFRAME_ROOT": str(args.mainframe_root),
        "ERS05_PROTECTED_PATHS": os.pathsep.join(str(path.resolve()) for _, path, _ in root_specs),
        "TMPDIR": str(temp_root),
        "GIT_OPTIONAL_LOCKS": "0",
        "PYTHONDONTWRITEBYTECODE": "1",
    })
    os.environ.update(env)

    run_child(HERE / "source_delta_proof.py", [
        "--repo", str(repo), "--source-commit", actual_source,
        "--output", str(output_root / "SOURCE_DELTA.json"),
    ], env)
    source_delta = json.loads((output_root / "SOURCE_DELTA.json").read_text())
    run_child(HERE / "runtime_reverify.py", [
        "--runtime-root", str(args.runtime_root), "--output-root", str(output_root),
        "--temp-root", str(temp_root), "--output", str(output_root / "RUNTIME_REUSE.json"),
    ], env)
    runtime = json.loads((output_root / "RUNTIME_REUSE.json").read_text())

    alias_roots = [
        ("MAINFRAME_ROOT", args.mainframe_root),
        ("APPARATUS_WORKBENCH", args.apparatus_workbench),
        ("PR148_ROOT", args.pr148_root),
        ("PR149_ROOT", args.pr149_root),
        ("SUCCESSOR_ROOT", repo),
        ("CONTROL_ROOT", control_root),
        ("FROZEN_CHECKOUTS", args.frozen_checkouts),
        ("FROZEN_FIXTURES", args.fixtures_root),
        ("SCIENTIFIC_SANDBOX", args.sandbox_root),
        ("FROZEN_RUNTIME", args.runtime_root),
        ("QUALIFICATION_OUTPUT", output_root),
        ("QUALIFICATION_TEMP", temp_root),
        ("PROTECTED_CANARY", canary),
    ]
    bootstrap.classify = classify
    cases = [
        ("frozen_pr148", args.pr148_root, "repository_root_path_defect"),
        ("frozen_pr149", args.pr149_root, "pipe01_disposition_expectation_defect"),
        ("new_successor", repo, "bootstrap_pass"),
        ("wrong_root_control", args.wrong_root, "repository_root_path_defect"),
        ("wrong_disposition_control", args.wrong_disposition, "pipe01_disposition_expectation_defect"),
        ("wrong_receipt_path_control", repo, "receipt_path_outside_repository"),
    ]
    outside_receipt = output_root / "wrong-receipt-path" / "FREEZE_RECEIPT.json"
    outside_receipt.parent.mkdir(parents=True, exist_ok=True)
    outside_receipt.write_bytes((repo / bootstrap.RECEIPT).read_bytes())
    case_reports = []
    for name, apparatus, expected in cases:
        runner_root = repo if name in ("new_successor", "wrong_receipt_path_control") else apparatus
        runner = runner_root / RUNNER_PATH
        receipt = apparatus / bootstrap.RECEIPT
        if name == "wrong_receipt_path_control":
            receipt = output_root / "wrong-receipt-path" / "FREEZE_RECEIPT.json"
        run_output = output_root / name / "runner-output"
        run_output.parent.mkdir(parents=True, exist_ok=True)
        report = bootstrap.execute(runner, apparatus, run_output, receipt, args.sandbox_root)
        normalized = clean_case(report, alias_roots)
        checks = report.get("checks", [])
        case_reports.append({
            "name": name,
            "expected": expected,
            "observed": report["outcome"],
            "matched": report["outcome"] == expected,
            "runner_blob": report["runner_blob"],
            "boundary_reached": report["boundary_reached"],
            "error_type": report["error_type"],
            "error": normalized["error"],
            "stages": report["stages"],
            "check_count": len(checks),
            "failed_checks": [item for item in checks if not item["passed"]],
            "checks": checks,
            "cli_flags": report["cli_flags"],
            "counters": report["counters"],
            "sandbox_entries_after": report["sandbox_entries_after"],
            "runner_output_files": report["runner_output_files"],
            "issuer_public_identity_checked_before_runner": report["issuer_public_identity_checked_before_runner"],
            "private_key_material_retained": report["private_key_material_retained"],
        })
        (output_root / f"{name}.json").write_text(json.dumps(normalized, indent=2, sort_keys=True) + "\n")

    after = {name: tree_snapshot(path, strong) for name, path, strong in root_specs}
    after["mainframe_git_state"] = mainframe_git_state(args.mainframe_root)
    unchanged = before == after
    per_case_zero = all(
        all(report["counters"].get(counter, 0) == 0 for counter in (
            "contract_e_evaluations", "supervisor_launches", "scientific_pipe_cases",
            "scientific_mutations", "scientific_sandbox_creations", "network_attempts",
            "mainframe_write_attempts", "protected_write_attempts",
            "provenance_scientific_captures", "scientific_sandbox_mutations",
            "protected_filesystem_mutations",
        ))
        for report in case_reports
    )
    case_match = all(item["matched"] for item in case_reports)
    successor = next(item for item in case_reports if item["name"] == "new_successor")
    passed_labels = {item["label"] for item in successor["checks"] if item["passed"]}
    missing_required_checks = sorted(REQUIRED_SETUP_CHECKS - passed_labels)
    successor_checks_ok = successor["check_count"] > 0 and not successor["failed_checks"] and not missing_required_checks
    passed = bool(source_delta.get("status") == "PASS" and runtime.get("status") == "PASS" and
                  canary_result["passed"] and unchanged and per_case_zero and case_match and
                  successor["boundary_reached"] and successor_checks_ok)

    profile_parameters = {
        "ERS05_ALLOWED_OUTPUT": str(output_root),
        "ERS05_ALLOWED_TEMP": str(temp_root),
        "ERS05_MAINFRAME_ROOT": str(args.mainframe_root.resolve()),
        "ERS05_APPARATUS_ROOT": str(repo),
        "ERS05_APPARATUS_WORKBENCH": str(args.apparatus_workbench.resolve()),
        "ERS05_PR148_ROOT": str(args.pr148_root.resolve()),
        "ERS05_PR149_ROOT": str(args.pr149_root.resolve()),
        "ERS05_CONTROL_ROOT": str(control_root),
        "ERS05_FROZEN_CHECKOUTS_ROOT": str(args.frozen_checkouts.resolve()),
        "ERS05_FIXTURES_ROOT": str(args.fixtures_root.resolve()),
        "ERS05_SCIENTIFIC_SANDBOX": str(args.sandbox_root.resolve()),
        "ERS05_RUNTIME_ROOT": str(args.runtime_root.resolve()),
        "ERS05_CANARY_ROOT": str(canary),
    }
    effective_profile_hash = sha(profile_bytes + json.dumps(profile_parameters, sort_keys=True, separators=(",", ":")).encode())
    report = {
        "schema": "ers05-strengthened-pre-matrix-qualification/1",
        "status": "PASS" if passed else "INCONCLUSIVE",
        "source_commit": actual_source,
        "source_parent_commit": source_parent,
        "preregistration_ancestor_commit": PREREG_COMMIT,
        "bootstrap_gate_blob": git_text(repo, "rev-parse", f"{actual_source}:research/ers-contract-e-evaluation-provenance-20260925/disposition-successor-rc0/qualification/strengthened_gate.py"),
        "bootstrap_boundary_gate_blob": git_text(repo, "rev-parse", f"{actual_source}:research/ers-contract-e-evaluation-provenance-20260925/disposition-successor-rc0/qualification/bootstrap_pre_matrix.py"),
        "write_profile_git_blob": git_text(repo, "rev-parse", f"{actual_source}:research/ers-contract-e-evaluation-provenance-20260925/disposition-successor-rc0/qualification/write-deny-profile.sb"),
        "missing_required_setup_checks": missing_required_checks,
        "predecessor_pr148_commit": PR148_COMMIT,
        "predecessor_pr149_commit": PR149_COMMIT,
        "scientific_authority_pr130_commit": "dcdd10355e2f885273d843eef6e345bafca95faa",
        "decision_identity": "decision:sha256:3427c5cb6692bf7358c13e47628ef7a91a0c53e78affc58f2ae60173daffcc15",
        "decision_disposition": "clear",
        "containment": {
            "mechanism": "macOS sandbox-exec deny-default profile",
            "profile_path": "qualification/write-deny-profile.sb",
            "profile_sha256": profile_sha,
            "effective_profile_binding_sha256": effective_profile_hash,
            "allowed_write_aliases": ["$QUALIFICATION_OUTPUT", "$QUALIFICATION_TEMP"],
            "protected_aliases": [name for name, _, _ in root_specs],
            "network_rule": "deny network*",
            "negative_control": canary_result,
        },
        "source_delta": source_delta,
        "runtime": runtime,
        "cases": case_reports,
        "protected_filesystem": {
            "before": before,
            "after": after,
            "unchanged": unchanged,
            "snapshot_scope": [name for name, _, _ in root_specs] + ["mainframe_git_state"],
        },
        "scientific_counters": {
            "contract_e_evaluations": 0,
            "supervisor_launches": 0,
            "scientific_pipe_executions": 0,
            "scientific_mutations": 0,
            "scientific_sandbox_mutations": 0,
            "provenance_scientific_captures": 0,
            "unauthorized_network_attempts": 0,
            "protected_filesystem_mutations": 0,
            "per_case_zero_counter_check": per_case_zero,
        },
        "passed": passed,
    }
    args.result.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "status": report["status"],
        "case_outcomes": {item["name"]: item["observed"] for item in case_reports},
        "canary_passed": canary_result["passed"],
        "protected_filesystem_unchanged": unchanged,
        "scientific_counters_zero": per_case_zero,
    }, sort_keys=True))
    return 0 if passed else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"status": "INCONCLUSIVE", "error_type": type(exc).__name__, "error": str(exc)}, sort_keys=True))
        raise SystemExit(2)
