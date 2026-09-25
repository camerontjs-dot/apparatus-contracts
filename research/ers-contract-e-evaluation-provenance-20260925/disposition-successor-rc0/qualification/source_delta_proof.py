#!/usr/bin/env python3
"""Mechanically compare the successor runner with immutable PR #149."""
from __future__ import annotations

import argparse
import ast
import difflib
import hashlib
import json
import subprocess
from pathlib import Path

BASE_COMMIT = "4bd5b030726ed064d410cb8c99e79c23a0426c8a"
PR148_COMMIT = "b673b2b06804e94042ad35d4621f4a4ca5ee4851"
BASE_TREE = "6aff39c21f777912472ae62324b94619ef4956de"
PREREG_COMMIT = "e54330db4de2090e8a238823459546d3153a42e3"
PR130_COMMIT = "dcdd10355e2f885273d843eef6e345bafca95faa"
PR130_EXPERIMENT = "research/ers-contract-e-evaluation-provenance-20260921/EXPERIMENT.json"
PR130_PREREG = "research/ers-contract-e-evaluation-provenance-20260921/PREREGISTRATION.md"
PR149_DELTA_PATH = "research/ers-contract-e-evaluation-provenance-20260924/root-path-successor-rc0/qualification/20260924/SOURCE_DELTA.json"
PREREG_RECONCILIATION = "research/ers-contract-e-evaluation-provenance-20260925/disposition-successor-rc0/decision-reconciliation/RECONCILIATION.json"
RUNNER = (
    "research/ers-contract-e-evaluation-provenance-20260921/"
    "fixture-bound-identity-successor-rc0/reproduce_rc6_fixture_bound.py"
)
BASE_RUNNER = "6c20a20831a34cf83eb38f0b86ae6965a15a7990"
EXPECTED_PR149_DELTA_BLOB = "3a11e56f95ccdd8418664e52e46867ab1c080d16"
EXPECTED_PR130_BLOBS = {
    PR130_EXPERIMENT: "7b0515c186b70b081aad4774821045b2b8202774",
    PR130_PREREG: "7c8904bf1237b8cf381e7d69f7b217286363b9ac",
}
AUTHORIZED_CHECK = "pipe01_native_ers_decision_changed"


class ProofError(RuntimeError):
    pass


def git(root: Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(root), *args], check=False,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if result.returncode:
        raise ProofError(result.stderr.decode("utf-8", "replace").strip())
    return result.stdout


def blob_oid(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def normalize_disposition(source: str) -> tuple[str, str]:
    tree = ast.parse(source)
    matches = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name) or node.func.id != "check":
            continue
        if len(node.args) != 2 or not isinstance(node.args[1], ast.Constant) or node.args[1].value != AUTHORIZED_CHECK:
            continue
        compare = node.args[0]
        if not isinstance(compare, ast.Compare) or len(compare.ops) != 1 or not isinstance(compare.ops[0], ast.Eq):
            raise ProofError("authorized_check_shape_changed")
        if not isinstance(compare.comparators[0], ast.Constant) or not isinstance(compare.comparators[0].value, str):
            raise ProofError("authorized_disposition_constant_missing")
        actual = compare.comparators[0].value
        left = compare.left
        if not isinstance(left, ast.Subscript) or not isinstance(left.slice, ast.Constant) or left.slice.value != "disposition":
            raise ProofError("authorized_disposition_expression_changed")
        matches.append((compare.comparators[0], actual))
    if len(matches) != 1:
        raise ProofError(f"authorized_check_count:{len(matches)}")
    constant, actual = matches[0]
    if actual not in ("pending_review", "clear"):
        raise ProofError(f"unexpected_disposition:{actual}")
    constant.value = "AUTHORIZED_PIPE01_DISPOSITION"
    return ast.dump(tree, include_attributes=False), actual


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    repo = args.repo.resolve()

    base_tree = git(repo, "rev-parse", f"{BASE_COMMIT}^{{tree}}").decode().strip()
    if base_tree != BASE_TREE:
        raise ProofError("pr149_tree_identity_changed")
    parent = git(repo, "rev-parse", f"{args.source_commit}^1").decode().strip()
    if parent != PREREG_COMMIT:
        raise ProofError("source_commit_not_child_of_preregistration")

    predecessor = git(repo, "cat-file", "blob", f"{BASE_COMMIT}:{RUNNER}")
    successor = git(repo, "cat-file", "blob", f"{args.source_commit}:{RUNNER}")
    base_runner_blob = blob_oid(predecessor)
    successor_blob = blob_oid(successor)
    if base_runner_blob != BASE_RUNNER:
        raise ProofError("pr149_runner_blob_changed")
    successor_text = successor.decode("utf-8")
    retained_checks = {
        "pr148_ers_receipt_path": '"research/ers-contract-e-evaluation-transcript-rc6-receipt-contract-successor-20260923/FREEZE_RECEIPT.json"' in successor_text,
        "pr148_apparatus_scientific_preregistration_commit": 'freeze_receipt["apparatus"]["scientific_preregistration"]["commit"] == APPARATUS_PREREG' in successor_text,
        "pr149_repository_root_correction": "ROOT = HERE.parents[2]" in successor_text,
    }
    if not all(retained_checks.values()):
        raise ProofError("cumulative_runner_correction_missing:" + json.dumps(retained_checks))
    pr149_delta_raw = git(repo, "cat-file", "blob", f"{BASE_COMMIT}:{PR149_DELTA_PATH}")
    pr149_delta_blob = blob_oid(pr149_delta_raw)
    if pr149_delta_blob != EXPECTED_PR149_DELTA_BLOB:
        raise ProofError("pr149_delta_receipt_blob_changed")
    pr149_delta = json.loads(pr149_delta_raw)
    if not pr149_delta.get("ast_equivalent_after_normalizing_root_index") or pr149_delta.get("successor_runner_blob") != BASE_RUNNER:
        raise ProofError("pr149_root_delta_receipt_not_reconciled")
    reconciliation_raw = git(repo, "cat-file", "blob", f"{PREREG_COMMIT}:{PREREG_RECONCILIATION}")
    reconciliation = json.loads(reconciliation_raw)
    fixture_identities = reconciliation["frozen_pipe01_inputs"]

    old_lines = predecessor.decode().splitlines()
    new_lines = successor.decode().splitlines()
    changed = [(i + 1, old, new) for i, (old, new) in enumerate(zip(old_lines, new_lines)) if old != new]
    if len(old_lines) != len(new_lines) or changed != [(
        391,
        '    check(decision["evaluation"]["disposition"] == "pending_review", "pipe01_native_ers_decision_changed")',
        '    check(decision["evaluation"]["disposition"] == "clear", "pipe01_native_ers_decision_changed")',
    )]:
        raise ProofError("unexpected_runner_line_delta:" + json.dumps(changed))

    normalized_predecessor, predecessor_disposition = normalize_disposition(predecessor.decode())
    normalized_successor, successor_disposition = normalize_disposition(successor.decode())
    if normalized_predecessor != normalized_successor:
        raise ProofError("runner_ast_diff_after_disposition_normalization")
    if (predecessor_disposition, successor_disposition) != ("pending_review", "clear"):
        raise ProofError("wrong_authorized_disposition_delta")

    pr130_blobs = {}
    for path, expected in EXPECTED_PR130_BLOBS.items():
        actual = git(repo, "rev-parse", f"{PR130_COMMIT}:{path}").decode().strip()
        if actual != expected:
            raise ProofError(f"pr130_authority_blob_changed:{path}:{actual}")
        pr130_blobs[path] = actual

    changed_paths = git(repo, "diff", "--name-only", BASE_COMMIT, args.source_commit).decode().splitlines()
    outside_successor = [
        path for path in changed_paths
        if path != RUNNER and not path.startswith("research/ers-contract-e-evaluation-provenance-20260925/disposition-successor-rc0/")
    ]
    if outside_successor:
        raise ProofError("out_of_scope_source_paths:" + json.dumps(outside_successor))

    report = {
        "schema": "ers05-runner-source-delta/1",
        "predecessor": {
            "pull_request": 149,
            "commit": BASE_COMMIT,
            "tree": BASE_TREE,
            "runner_path": RUNNER,
            "runner_blob": base_runner_blob,
        },
        "preregistration": {"commit": PREREG_COMMIT},
        "source": {
            "commit": args.source_commit,
            "tree": git(repo, "rev-parse", f"{args.source_commit}^{{tree}}").decode().strip(),
            "runner_path": RUNNER,
            "runner_blob": successor_blob,
        },
        "changed_line": {
            "line": 391,
            "predecessor": 'decision["evaluation"]["disposition"] == "pending_review"',
            "successor": 'decision["evaluation"]["disposition"] == "clear"',
        },
        "ast_equal_after_normalizing_authorized_disposition_constant": True,
        "cumulative_runner_lineage": [
            {"pull_request": 148, "commit": PR148_COMMIT, "runner_blob": "79a347c9698610a1c743074e426a79590cb32ba4", "receipt_path_and_apparatus_commit_corrections_retained": True},
            {"pull_request": 149, "commit": BASE_COMMIT, "runner_blob": BASE_RUNNER, "source_delta_path": PR149_DELTA_PATH, "source_delta_blob": pr149_delta_blob, "root_correction_retained": True},
            {"successor_preregistration_commit": PREREG_COMMIT},
        ],
        "retained_pr148_corrections": retained_checks,
        "pipe01_fixture_identities": fixture_identities,
        "pr130": {"commit": PR130_COMMIT, "blobs": pr130_blobs},
        "unchanged_surfaces": {
            "matrix_cases": True,
            "scientific_mutations": True,
            "supervisor_api": True,
            "transcript_schema_and_signing": True,
            "ers_and_contract_e_semantics": True,
            "fixtures": True,
            "expected_scientific_outcomes": True,
        },
        "changed_paths_outside_successor_dir": [RUNNER],
        "status": "PASS",
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ProofError as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc)}, sort_keys=True))
        raise SystemExit(1)
