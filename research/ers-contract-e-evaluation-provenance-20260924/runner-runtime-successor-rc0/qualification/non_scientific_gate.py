#!/usr/bin/env python3
"""Receipt, source, runtime, and negative-boundary checks for the frozen 05 successor."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from zipfile import ZipFile

EXPERIMENT_ID = "ERS-EVAL-TIME-PROV-20260922-05"
PR147_HEAD = "c054d2fb0822e61833cb9e8a5acb7072dbce6531"
PR147_BASE_BRANCH = "research/ers-contract-e-evaluation-provenance-05-receipt-contract-prereg-20260923"
PR147_HEAD_BRANCH = "research/ers-contract-e-evaluation-provenance-05-scientific-execution-blocked-20260923"
PR147_BASE = "cd465d798220daa3f45261d3e6f385cf67224a46"
PR146_HEAD = "cd465d798220daa3f45261d3e6f385cf67224a46"
PR146_HEAD_BRANCH = "research/ers-contract-e-evaluation-provenance-05-receipt-contract-prereg-20260923"
APP146_FREEZE_RECEIPT_PATH = (
    "research/ers-contract-e-evaluation-provenance-20260921/"
    "fixture-bound-receipt-contract-successor-rc0/FREEZE_RECEIPT.json"
)
APP146_FREEZE_RECEIPT_BLOB = "bc7d3938be9146dd6455ab5f9fda896f22a70274"
PR130_HEAD = "dcdd10355e2f885273d843eef6e345bafca95faa"
PR131_HEAD = "077ccf6d386526bda258b3e90bd43e153c4c04c5"
PR131_CONTRACT_BLOB = "92b029e6fb5e1a7c11a661911647e618594cd797"
PR131_CONTRACT_PATH = (
    "research/ers-contract-e-evaluation-provenance-20260921/"
    "successor-receipt-contract-rc0/FREEZE_RECEIPT_CONTRACT.json"
)
PREREG_COMMIT = "e0be5131d2b906f01d3d2461941af048e0f16920"
SUCCESSOR_BRANCH = "research/ers-contract-e-evaluation-provenance-05-runner-runtime-successor-20260924"
PREREG_TREE = "2ce8a4093ed098c23f2b124226ccdfa9ff2d6a09"
PREREG_BLOB = "4308549db59e7c358d26abdada166891df8f248d"
ERS_FREEZE_COMMIT = "aa214666c9a68871c0d878a70b7f3833d49dbe9b"
ERS_PR14_BRANCH = "research/ers-contract-e-evaluation-provenance-05-receipt-contract-successor-20260923"
ERS_FREEZE_TREE = "1ad0bb7df9a6d836a5fdca7157173c60429619a3"
ERS_RECEIPT_BLOB = "50c9493d3f0584de74399118da01b7b603c813e0"
ERS_IMPLEMENTATION_COMMIT = "65f47d029fb734be1d5d506a135cbeba813f6be8"
ERS_IMPLEMENTATION_TREE = "405bb622e0d7d0f69f3da7506a15fa0b2390e191"
PREFLIGHT_COMMIT = "9f75ee325f31971ca8f0d4e1ddf9a7c04c98e940"
PREFLIGHT_TREE = "53e4d53f5f62112d28d080da0a732475c3c51df5"
PREFLIGHT_BLOB = "3314048d5904fa59fdb00e67a1ee108c167097aa"
PYPROJECT_BLOB = "94396e082c521996c9ed6e39546b3dbb0be60772"
PREDECESSOR_RUNNER_BLOB = "d0f3b69949bdeedea87fe0ac82b6d3407eac1a67"
FIXTURE_SUBJECT = "sha256:bebbb1b7973a962d59c92061e8e70283a2fb4b2b8c388705b8d80ce13000c7ad"
ERS_RECEIPT_PATH = (
    "research/ers-contract-e-evaluation-transcript-rc6-receipt-contract-successor-20260923/"
    "FREEZE_RECEIPT.json"
)
PREDECESSOR_ERS_RECEIPT_PATH = (
    "research/ers-contract-e-evaluation-transcript-rc6-exec-identity-successor-20260922/"
    "FREEZE_RECEIPT.json"
)
RUNNER_PATH = (
    "research/ers-contract-e-evaluation-provenance-20260921/"
    "fixture-bound-identity-successor-rc0/reproduce_rc6_fixture_bound.py"
)
PRE_REG_PATH = (
    "research/ers-contract-e-evaluation-provenance-20260924/"
    "runner-runtime-successor-rc0/PREREGISTRATION.md"
)
FREEZE_RECEIPT_PATH = (
    "research/ers-contract-e-evaluation-provenance-20260924/"
    "runner-runtime-successor-rc0/FREEZE_RECEIPT.json"
)
RUNTIME_DIR = (
    "research/ers-contract-e-evaluation-provenance-20260924/"
    "runner-runtime-successor-rc0/runtime"
)
EXPECTED_PINS = {"rfc8785": "0.1.4", "jsonschema": "4.26.0", "cryptography": "50.0.1"}
FROZEN_DEPENDENCIES = {
    "contract_e": "b153dcc4434cbe8a98616a9e410c6125378144c7",
    "contract_d": "298a1a0f7b7b6d7712e11200d04faec3e1ca169b",
    "decision": "816374379ba7eb23f5bfdadaf203b7e287c052db",
    "cal_pipeline_v3": "ffc43d4e89f5b1f7748e9cde0fa1efc7db47b463",
    "contract_c_consumer": "12e7e640b229619501960b1b89cf4716d8d985b3",
    "render_bound_ers_rc4": "022fcb58e14864aa173f447fa0c18dd2362b41b0",
    "ers_rc5_base": "099f84700f28e118734f1ca74feb977da1c4cf17",
    "ers_rc6_predecessor_freeze": "66a82e8ac28c380ddc7eb4388bdc3daf289c1db9",
    "provenance_profile": "3934423b1a97ad1b099057c40fe8014e5dd08c97",
    "provenance_root_freeze": "8f762f0d02d2f5a32d85c6b1c721782198422239",
}
GATE_PATH = (
    "research/ers-contract-e-evaluation-provenance-20260924/"
    "runner-runtime-successor-rc0/qualification/non_scientific_gate.py"
)
DEPENDENCY_SMOKE_PATH = (
    "research/ers-contract-e-evaluation-provenance-20260924/"
    "runner-runtime-successor-rc0/qualification/dependency_smoke.py"
)
STARTUP_GUARD_PATH = (
    "research/ers-contract-e-evaluation-provenance-20260924/"
    "runner-runtime-successor-rc0/qualification/sitecustomize.py"
)
DELTA_PROOF_PATH = (
    "research/ers-contract-e-evaluation-provenance-20260924/"
    "runner-runtime-successor-rc0/qualification/source_delta_proof.py"
)


class GateError(RuntimeError):
    def __init__(self, code: str, detail: str = "") -> None:
        self.code = code
        super().__init__(code + (":" + detail if detail else ""))


def require(condition: bool, code: str, detail: str = "") -> None:
    if not condition:
        raise GateError(code, detail)


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args], check=False,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    if result.returncode:
        raise GateError("git_command_failed", " ".join(args) + ":" + result.stderr.strip())
    return result.stdout.strip()


def git_bytes(root: Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(root), *args], check=False,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if result.returncode:
        raise GateError("git_command_failed", " ".join(args) + ":" + result.stderr.decode("utf-8", "replace").strip())
    return result.stdout


def git_blob_sha1(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def load_json(path: Path, label: str) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise GateError("invalid_json:" + label, str(exc)) from exc
    require(isinstance(value, dict), "json_root_not_object:" + label)
    return value


def validate_ers_path(path: str) -> None:
    require(path == ERS_RECEIPT_PATH, "ers_receipt_path_mismatch", path)


def validate_ers_document(document: dict) -> None:
    apparatus = document.get("apparatus")
    require(isinstance(apparatus, dict), "ers_apparatus_missing")
    scientific = apparatus.get("scientific_preregistration")
    require(isinstance(scientific, dict) and "commit" in scientific,
            "ers_pr130_canonical_missing")
    require("preregistration_head" not in apparatus, "ers_obsolete_pr130_alias_present")
    require(scientific["commit"] == PR130_HEAD, "wrong_pr130_commit", str(scientific["commit"]))


def validate_exact_blob(actual: str, expected: str, code: str) -> None:
    require(actual == expected, code, "expected=" + expected + ";actual=" + actual)


def validate_runner_pair(source: bytes, document: dict) -> None:
    try:
        tree = ast.parse(source.decode("utf-8"))
    except (SyntaxError, UnicodeError) as exc:
        raise GateError("runner_pair_ast_invalid", str(exc)) from exc
    values = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "ERS_RECEIPT_RELATIVE_PATH" for t in node.targets
        ):
            if isinstance(node.value, ast.Call) and len(node.value.args) == 1:
                arg = node.value.args[0]
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    values.append(arg.value)
    require(len(values) == 1, "runner_receipt_path_assignment_invalid")
    require(values[0] == ERS_RECEIPT_PATH, "runner_receipt_path_pair_mismatch", values[0])
    wanted = ("apparatus", "scientific_preregistration", "commit")
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Subscript):
            continue
        keys = []
        current = node
        while isinstance(current, ast.Subscript):
            if not isinstance(current.slice, ast.Constant) or not isinstance(current.slice.value, str):
                break
            keys.append(current.slice.value)
            current = current.value
        if isinstance(current, ast.Name) and current.id == "freeze_receipt":
            chain = tuple(reversed(keys))
            if chain == wanted:
                found.append(chain)
    require(len(found) == 1, "runner_pr130_lookup_pair_mismatch")
    validate_ers_document(document)


def validate_runner_blob(actual: str, expected: str) -> None:
    validate_exact_blob(actual, expected, "runner_blob_mismatch")


def validate_runtime_lock_hash(actual: str, expected: str) -> None:
    validate_exact_blob(actual, expected, "runtime_lock_hash_mismatch")


def validate_direct_pins(pins: dict) -> None:
    for name, version in EXPECTED_PINS.items():
        require(pins.get(name) == version, "direct_package_version_mismatch:" + name,
                str(pins.get(name)))


def validate_installed_versions(actual: dict[str, str], expected: list[dict]) -> None:
    for item in expected:
        name, version = item["name"], item["version"]
        require(name in actual, "missing_required_package:" + name)
        require(actual[name] == version, "installed_package_version_mismatch:" + name,
                str(actual[name]))


def validate_artifact_hash(actual: str, expected: str, label: str) -> None:
    validate_exact_blob(actual, expected, "artifact_hash_mismatch:" + label)


def runner_delta(repo_root: Path, source_path: Path) -> dict:
    script = repo_root / (RUNTIME_DIR + "/../qualification/source_delta_proof.py")
    result = subprocess.run(
        [sys.executable, str(script), "--repo-root", str(repo_root),
         "--candidate-source", str(source_path)],
        check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise GateError("source_delta_proof_output_invalid", result.stderr) from exc
    require(result.returncode == 0 and payload.get("status") == "PASS",
            "runner_delta_proof_failed", json.dumps(payload, sort_keys=True))
    return payload


def expected_error(label: str, code: str, function) -> dict:
    try:
        function()
    except GateError as exc:
        if exc.code != code:
            raise GateError("negative_wrong_rejection_boundary:" + label,
                            "expected=" + code + ";actual=" + exc.code) from exc
        return {"control": label, "status": "PASS", "rejection_boundary": exc.code,
                "error": str(exc)}
    raise GateError("negative_not_rejected:" + label, code)


def run_negative_controls(repo_root: Path, runner_source: bytes, freeze: dict,
                          manifest: dict, lock_raw: bytes, wheel_path: Path,
                          receipt_doc: dict) -> list[dict]:
    controls = []
    controls.append(expected_error(
        "predecessor_ers_receipt_path", "ers_receipt_path_mismatch",
        lambda: validate_ers_path(PREDECESSOR_ERS_RECEIPT_PATH),
    ))
    controls.append(expected_error(
        "obsolete_only_pr130_alias", "ers_pr130_canonical_missing",
        lambda: validate_ers_document({"apparatus": {"preregistration_head": PR130_HEAD}}),
    ))
    controls.append(expected_error(
        "wrong_pr130_value", "wrong_pr130_commit",
        lambda: validate_ers_document({"apparatus": {
            "scientific_preregistration": {"commit": "0" * 40}
        }}),
    ))
    controls.append(expected_error(
        "wrong_ers_receipt_blob", "ers_receipt_blob_mismatch",
        lambda: validate_exact_blob("0" * 40, ERS_RECEIPT_BLOB, "ers_receipt_blob_mismatch"),
    ))
    expected_runner_blob = freeze["runner"]["source_blob"]
    controls.append(expected_error(
        "wrong_runner_blob", "runner_blob_mismatch",
        lambda: validate_runner_blob(PREDECESSOR_RUNNER_BLOB, expected_runner_blob),
    ))
    with tempfile.TemporaryDirectory(prefix="ers05-runner-delta-negative-") as temp:
        altered = Path(temp) / "altered_runner.py"
        altered.write_bytes(runner_source + b"\n# unauthorized change\n")
        controls.append(expected_error(
            "runner_modified_beyond_preregistered_delta", "runner_delta_proof_failed",
            lambda: runner_delta(repo_root, altered),
        ))
    expected_lock_hash = freeze["runtime"]["requirements_lock_sha256"]
    controls.append(expected_error(
        "wrong_runtime_lock_hash", "runtime_lock_hash_mismatch",
        lambda: validate_runtime_lock_hash(sha256(lock_raw + b"\n# wrong lock\n"), expected_lock_hash),
    ))
    wrong_pins = dict(manifest["direct_pins"])
    wrong_pins["jsonschema"] = "4.26.1"
    controls.append(expected_error(
        "wrong_direct_dependency_version", "direct_package_version_mismatch:jsonschema",
        lambda: validate_direct_pins(wrong_pins),
    ))
    expected_graph = manifest["dependency_graph"]
    installed = {item["name"]: item["version"] for item in expected_graph}
    installed.pop("cryptography", None)
    controls.append(expected_error(
        "missing_required_package", "missing_required_package:cryptography",
        lambda: validate_installed_versions(installed, expected_graph),
    ))
    with ZipFile(wheel_path) as archive:
        wheel_name = sorted(archive.namelist())[0]
        wheel_raw = archive.read(wheel_name)
    altered_wheel = bytearray(wheel_raw)
    altered_wheel[-1] ^= 1
    expected_wheel = next(item for item in manifest["archive_format"]["wheels"]
                          if item["filename"] == wheel_name)
    controls.append(expected_error(
        "altered_package_artifact_hash", "artifact_hash_mismatch:" + wheel_name,
        lambda: validate_artifact_hash(sha256(bytes(altered_wheel)),
                                      expected_wheel["sha256"], wheel_name),
    ))
    predecessor = git_bytes(repo_root, "cat-file", "blob", PREDECESSOR_RUNNER_BLOB)
    controls.append(expected_error(
        "old_runner_paired_with_new_05_receipt", "runner_receipt_path_pair_mismatch",
        lambda: validate_runner_pair(predecessor, receipt_doc),
    ))
    return controls


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apparatus-root", required=True, type=Path)
    parser.add_argument("--ers-root", required=True, type=Path)
    parser.add_argument("--preflight-output", required=True, type=Path)
    parser.add_argument("--freeze-commit", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    app = args.apparatus_root.resolve()
    ers = args.ers_root.resolve()
    output = args.output.resolve() if args.output else None
    try:
        require(git(app, "rev-parse", "HEAD") == args.freeze_commit,
                "apparatus_freeze_checkout_mismatch")
        require(git(app, "status", "--porcelain") == "", "apparatus_checkout_dirty")
        freeze_path = app / FREEZE_RECEIPT_PATH
        freeze = load_json(freeze_path, "apparatus_freeze")
        require(freeze.get("schema") == "ers-eval-time-prov-05-runner-runtime-successor-freeze/1",
                "apparatus_freeze_schema_mismatch")
        require(freeze.get("experiment_id") == EXPERIMENT_ID, "experiment_id_mismatch")
        require(git(app, "rev-parse", f"{args.freeze_commit}:{FREEZE_RECEIPT_PATH}") ==
                git(app, "hash-object", str(freeze_path)), "apparatus_freeze_receipt_blob_mismatch")
        source_commit_from_runner = freeze["runner"]["source_commit"]
        require(git(app, "rev-parse", f"{args.freeze_commit}^") == source_commit_from_runner,
                "freeze_receipt_not_direct_source_successor")
        require(git(app, "rev-parse", f"{source_commit_from_runner}^") == PREREG_COMMIT,
                "candidate_source_not_direct_prereg_successor")
        require(git(app, "rev-parse", f"{PREREG_COMMIT}^") == PR147_HEAD,
                "preregistration_not_based_on_exact_pr147_head")

        preserved_pr147 = freeze["authorities"]["preserved_pr147"]
        require(preserved_pr147["head"] == PR147_HEAD and
                preserved_pr147["base"] == PR147_BASE and
                preserved_pr147["head_branch"] == PR147_HEAD_BRANCH and
                preserved_pr147["base_branch"] == PR147_BASE_BRANCH and
                preserved_pr147["disposition"] == "BLOCKED_BEFORE_SCIENTIFIC_MATRIX",
                "pr147_identity_mismatch")
        qualified_pr146 = freeze["authorities"]["qualified_pr146"]
        require(qualified_pr146["head"] == PR146_HEAD and
                qualified_pr146["head_branch"] == PR146_HEAD_BRANCH and
                qualified_pr146["receipt_path"] == APP146_FREEZE_RECEIPT_PATH and
                qualified_pr146["receipt_blob"] == APP146_FREEZE_RECEIPT_BLOB,
                "pr146_identity_mismatch")
        require(git(app, "rev-parse", f"{PR146_HEAD}:{APP146_FREEZE_RECEIPT_PATH}") ==
                APP146_FREEZE_RECEIPT_BLOB, "pr146_freeze_receipt_blob_mismatch")
        require(freeze["scientific_preregistration"]["commit"] == PR130_HEAD and
                freeze["scientific_preregistration"]["pull_request"] == 130 and
                git(app, "cat-file", "-t", PR130_HEAD) == "commit",
                "pr130_identity_mismatch")
        require(freeze["receipt_contract_preregistration"]["commit"] == PR131_HEAD and
                freeze["receipt_contract_preregistration"]["contract_blob"] == PR131_CONTRACT_BLOB and
                freeze["receipt_contract_preregistration"]["contract_path"] == PR131_CONTRACT_PATH,
                "pr131_identity_mismatch")
        require(git(app, "rev-parse", f"{PR131_HEAD}:{PR131_CONTRACT_PATH}") ==
                PR131_CONTRACT_BLOB, "pr131_contract_blob_mismatch")
        prereg = freeze["successor_preregistration"]
        require(prereg["commit"] == PREREG_COMMIT and prereg["tree"] == PREREG_TREE and
                prereg["blob"] == PREREG_BLOB and prereg["path"] == PRE_REG_PATH and
                prereg["branch"] == SUCCESSOR_BRANCH,
                "successor_preregistration_identity_mismatch")
        require(git(app, "rev-parse", f"{PREREG_COMMIT}:{PRE_REG_PATH}") == PREREG_BLOB,
                "successor_preregistration_git_blob_mismatch")
        require(freeze.get("frozen_dependencies") == FROZEN_DEPENDENCIES,
                "frozen_dependency_identity_mismatch")
        require(freeze["ers_receipt"]["commit"] == ERS_FREEZE_COMMIT and
                freeze["ers_receipt"]["branch"] == ERS_PR14_BRANCH and
                freeze["ers_receipt"]["tree"] == ERS_FREEZE_TREE and
                freeze["ers_receipt"]["blob"] == ERS_RECEIPT_BLOB and
                freeze["ers_receipt"]["path"] == ERS_RECEIPT_PATH,
                "ers_receipt_freeze_identity_mismatch")
        require(git(ers, "rev-parse", "HEAD") == ERS_FREEZE_COMMIT and
                git(ers, "rev-parse", "HEAD^{tree}") == ERS_FREEZE_TREE and
                git(ers, "status", "--porcelain") == "",
                "ers_checkout_identity_mismatch")
        validate_ers_path(freeze["ers_receipt"]["path"])
        ers_receipt = ers / ERS_RECEIPT_PATH
        receipt_raw = ers_receipt.read_bytes()
        validate_exact_blob(git_blob_sha1(receipt_raw), ERS_RECEIPT_BLOB,
                            "ers_receipt_blob_mismatch")
        receipt_doc = load_json(ers_receipt, "ers_receipt")
        validate_ers_document(receipt_doc)
        require(receipt_doc["implementation"]["source_commit"] == ERS_IMPLEMENTATION_COMMIT and
                receipt_doc["implementation"]["source_tree"] == ERS_IMPLEMENTATION_TREE,
                "ers_implementation_identity_mismatch")
        require(git(ers, "rev-parse", f"{ERS_IMPLEMENTATION_COMMIT}^{{tree}}") ==
                ERS_IMPLEMENTATION_TREE, "ers_implementation_tree_mismatch")
        runner = freeze["runner"]
        require(runner["path"] == RUNNER_PATH and
                runner["branch"] == SUCCESSOR_BRANCH and
                runner["predecessor_blob"] == PREDECESSOR_RUNNER_BLOB,
                "runner_preregistration_identity_mismatch")
        source_commit = runner["source_commit"]
        require(git(app, "rev-parse", f"{source_commit}^{{tree}}") == runner["source_tree"],
                "runner_source_tree_mismatch")
        require(git(app, "merge-base", "--is-ancestor", PR130_HEAD, source_commit) == "",
                "pr130_not_ancestor_of_candidate_source")
        require(git(app, "merge-base", "--is-ancestor", PR131_HEAD, source_commit) == "",
                "pr131_not_ancestor_of_candidate_source")
        require(git(app, "merge-base", "--is-ancestor", source_commit, args.freeze_commit) == "",
                "runner_source_not_ancestor_of_freeze")
        changed_paths = git(app, "diff", "--name-only", PR147_HEAD, source_commit).splitlines()
        successor_prefix = RUNTIME_DIR.rsplit("/", 1)[0] + "/"
        unexpected_paths = [path for path in changed_paths
                            if path != RUNNER_PATH and not path.startswith(successor_prefix)]
        require(not unexpected_paths, "protected_surface_changed", ",".join(unexpected_paths))
        runner_blob = git(app, "rev-parse", f"{source_commit}:{RUNNER_PATH}")
        validate_runner_blob(runner_blob, runner["source_blob"])
        runner_raw = (app / RUNNER_PATH).read_bytes()
        validate_runner_blob(git_blob_sha1(runner_raw), runner["source_blob"])
        validate_runner_pair(runner_raw, receipt_doc)
        delta = runner_delta(app, app / RUNNER_PATH)
        require(delta["predecessor_blob"] == PREDECESSOR_RUNNER_BLOB and
                delta["successor_blob"] == runner["source_blob"] and
                delta["whole_ast_equal_after_authorized_normalization"] is True,
                "runner_delta_receipt_mismatch")
        delta_path = runner["source_delta_proof_path"]
        require(git(app, "rev-parse", f"{source_commit}:{delta_path}") ==
                runner["source_delta_proof_blob"], "source_delta_proof_blob_mismatch")
        for label, tool in freeze["qualification_tools"].items():
            require(git(app, "rev-parse", f"{source_commit}:{tool['path']}") == tool["blob"],
                    "qualification_tool_blob_mismatch:" + label)
        required_tools = {
            "non_scientific_gate": GATE_PATH,
            "dependency_smoke": DEPENDENCY_SMOKE_PATH,
            "startup_guard": STARTUP_GUARD_PATH,
            "source_delta_proof": DELTA_PROOF_PATH,
        }
        require(set(freeze["qualification_tools"]) == set(required_tools),
                "qualification_tool_set_mismatch")
        for label, expected_path in required_tools.items():
            require(freeze["qualification_tools"][label]["path"] == expected_path,
                    "qualification_tool_path_mismatch:" + label)

        runtime = freeze["runtime"]
        manifest_path = app / runtime["manifest_path"]
        manifest = load_json(manifest_path, "runtime_manifest")
        require(sha256(manifest_path.read_bytes()) == runtime["manifest_sha256"],
                "runtime_manifest_sha256_mismatch")
        validate_runtime_lock_hash(
            sha256((app / runtime["requirements_lock_path"]).read_bytes()),
            runtime["requirements_lock_sha256"],
        )
        validate_artifact_hash(
            sha256((app / runtime["wheelhouse_path"]).read_bytes()),
            runtime["wheelhouse_sha256"], "wheelhouse.zip",
        )
        validate_direct_pins(manifest["direct_pins"])
        require(manifest["direct_pin_authority"]["rfc8785"]["git_blob"] == PYPROJECT_BLOB,
                "rfc8785_pin_authority_blob_mismatch")
        require(git(app, "rev-parse", f"{source_commit}:pyproject.toml") == PYPROJECT_BLOB,
                "pyproject_pin_authority_blob_mismatch")
        require(git(app, "rev-parse", f"{source_commit}:{runtime['requirements_lock_path']}") ==
                runtime["requirements_lock_blob"], "runtime_lock_blob_mismatch")
        require(git(app, "rev-parse", f"{source_commit}:{runtime['manifest_path']}") ==
                runtime["manifest_blob"], "runtime_manifest_blob_mismatch")
        require(git(app, "rev-parse", f"{source_commit}:{runtime['wheelhouse_path']}") ==
                runtime["wheelhouse_blob"], "runtime_wheelhouse_blob_mismatch")
        require(freeze["fixture_subject"] == FIXTURE_SUBJECT, "fixture_subject_mismatch")

        preflight = freeze["qualified_preflight"]
        require(preflight["source_blob"] == PREFLIGHT_BLOB and
                preflight["source_commit"] == PREFLIGHT_COMMIT and
                preflight["source_tree"] == PREFLIGHT_TREE,
                "preflight_source_identity_mismatch")
        require(git(app, "rev-parse", f"{PREFLIGHT_COMMIT}:{preflight['source_path']}") ==
                PREFLIGHT_BLOB, "preflight_git_blob_mismatch")
        preflight_result = load_json(args.preflight_output.resolve(), "preflight_output")
        require(preflight_result.get("status") == "PASS", "qualified_receipt_source_preflight_not_pass")
        require(preflight_result.get("input_receipts", {}).get("ers", {}).get("git_blob") ==
                ERS_RECEIPT_BLOB, "preflight_ers_receipt_blob_mismatch")
        require(preflight_result.get("input_receipts", {}).get("ers", {}).get("path") ==
                ERS_RECEIPT_PATH, "preflight_ers_receipt_path_mismatch")
        require(preflight_result.get("input_receipts", {}).get("apparatus", {}).get("git_blob") ==
                APP146_FREEZE_RECEIPT_BLOB, "preflight_apparatus_receipt_blob_mismatch")
        require(preflight_result.get("scientific_preregistration", {}).get("commit") ==
                PR130_HEAD, "preflight_pr130_mismatch")
        instrumentation = preflight_result.get("instrumentation", {})
        require(instrumentation.get("candidate_runtime_imports") == [],
                "preflight_candidate_import_observed")
        require(instrumentation.get("network_attempts") == 0,
                "preflight_network_attempt_observed")
        require(instrumentation.get("contract_e_evaluation_calls") == 0,
                "preflight_contract_e_evaluation_observed")
        require(instrumentation.get("supervisor_process_launches") == 0 and
                instrumentation.get("non_git_processes") == [],
                "preflight_non_git_process_observed")

        wheelhouse = app / runtime["wheelhouse_path"]
        if output:
            output.parent.mkdir(parents=True, exist_ok=True)
        controls = run_negative_controls(app, runner_raw, freeze, manifest,
                                         (app / runtime["requirements_lock_path"]).read_bytes(),
                                         wheelhouse, receipt_doc)
        result = {
            "schema": "ers-05-runner-runtime-non-scientific-qualification/1",
            "status": "PASS",
            "apparatus_freeze_commit": args.freeze_commit,
            "apparatus_freeze_tree": git(app, "rev-parse", "HEAD^{tree}"),
            "ers_receipt_commit": ERS_FREEZE_COMMIT,
            "ers_receipt_tree": ERS_FREEZE_TREE,
            "runner_source_blob": runner_blob,
            "runner_source_delta": delta,
            "runtime_lock_sha256": runtime["requirements_lock_sha256"],
            "wheelhouse_sha256": runtime["wheelhouse_sha256"],
            "preflight_status": "PASS",
            "negative_controls": controls,
            "execution_counters": {
                "contract_e_evaluations": 0,
                "supervisor_launches": 0,
                "pipe_matrix_cases": 0,
                "scientific_mutations": 0,
                "sandbox_creations": 0,
                "candidate_runtime_imports": 0,
                "network_calls": 0
            }
        }
        encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
        if output:
            output.write_text(encoded, encoding="utf-8")
        print(encoded, end="")
        return 0
    except (GateError, OSError, KeyError, TypeError, ValueError) as exc:
        payload = {"schema": "ers-05-runner-runtime-non-scientific-qualification/1",
                   "status": "FAIL",
                   "error_code": getattr(exc, "code", type(exc).__name__),
                   "error": str(exc)}
        encoded = json.dumps(payload, indent=2, sort_keys=True) + "\n"
        if output:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(encoded, encoding="utf-8")
        print(encoded, file=sys.stderr, end="")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
