#!/usr/bin/env python3
"""Prove the runner's source and full-AST delta is exactly the preregistered pair."""
from __future__ import annotations

import argparse
import ast
import copy
import difflib
import hashlib
import json
import subprocess
import sys
from pathlib import Path

PREDECESSOR_BLOB = "d0f3b69949bdeedea87fe0ac82b6d3407eac1a67"
RUNNER_PATH = (
    "research/ers-contract-e-evaluation-provenance-20260921/"
    "fixture-bound-identity-successor-rc0/reproduce_rc6_fixture_bound.py"
)
OLD_RECEIPT_PATH = (
    "research/ers-contract-e-evaluation-transcript-rc6-exec-identity-successor-20260922/"
    "FREEZE_RECEIPT.json"
)
NEW_RECEIPT_PATH = (
    "research/ers-contract-e-evaluation-transcript-rc6-receipt-contract-successor-20260923/"
    "FREEZE_RECEIPT.json"
)
OLD_KEYS = ("apparatus", "preregistration_head")
NEW_KEYS = ("apparatus", "scientific_preregistration", "commit")


class ProofError(RuntimeError):
    def __init__(self, code: str, detail: str = "") -> None:
        self.code = code
        super().__init__(code + (":" + detail if detail else ""))


def git(root: Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode:
        raise ProofError("git_object_read_failed", result.stderr.decode("utf-8", "replace"))
    return result.stdout


def blob_oid(raw: bytes) -> str:
    header = b"blob " + str(len(raw)).encode("ascii") + b"\0"
    return hashlib.sha1(header + raw).hexdigest()


def path_assignment(tree: ast.AST) -> ast.Assign:
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if any(isinstance(target, ast.Name) and target.id == "ERS_RECEIPT_RELATIVE_PATH"
               for target in node.targets):
            found.append(node)
    if len(found) != 1:
        raise ProofError("receipt_path_assignment_count", str(len(found)))
    node = found[0]
    value = node.value
    if not isinstance(value, ast.Call) or not isinstance(value.func, ast.Name) or value.func.id != "Path":
        raise ProofError("receipt_path_expression_shape")
    if len(value.args) != 1 or not isinstance(value.args[0], ast.Constant) or not isinstance(value.args[0].value, str):
        raise ProofError("receipt_path_literal_shape")
    return node


def subscript_chain(node: ast.AST) -> tuple[str, tuple[str, ...]] | None:
    keys: list[str] = []
    value = node
    while isinstance(value, ast.Subscript):
        index = value.slice
        if not isinstance(index, ast.Constant) or not isinstance(index.value, str):
            return None
        keys.append(index.value)
        value = value.value
    if not isinstance(value, ast.Name):
        return None
    return value.id, tuple(reversed(keys))


def matching_subscripts(tree: ast.AST, root_name: str, keys: tuple[str, ...]) -> list[ast.Subscript]:
    return [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Subscript) and subscript_chain(node) == (root_name, keys)
    ]


def source_changes(old: bytes, new: bytes) -> tuple[list[str], list[str]]:
    old_lines = old.decode("utf-8").splitlines(keepends=True)
    new_lines = new.decode("utf-8").splitlines(keepends=True)
    diff = difflib.unified_diff(old_lines, new_lines, fromfile="predecessor", tofile="successor", n=0)
    removed: list[str] = []
    added: list[str] = []
    for line in diff:
        if line.startswith("---") or line.startswith("+++"):
            continue
        if line.startswith("-"):
            removed.append(line[1:])
        elif line.startswith("+"):
            added.append(line[1:])
    expected_removed = [
        f'    "{OLD_RECEIPT_PATH}"\n',
        '    check(freeze_receipt["apparatus"]["preregistration_head"] == APPARATUS_PREREG, "ers_receipt_preregistration_mismatch")\n',
    ]
    expected_added = [
        f'    "{NEW_RECEIPT_PATH}"\n',
        '    check(freeze_receipt["apparatus"]["scientific_preregistration"]["commit"] == APPARATUS_PREREG, "ers_receipt_preregistration_mismatch")\n',
    ]
    if removed != expected_removed or added != expected_added:
        raise ProofError("source_delta_not_exact", json.dumps({"removed": removed, "added": added}))
    return removed, added


class ReplaceAuthorizedLookup(ast.NodeTransformer):
    def __init__(self, predecessor: ast.Subscript) -> None:
        self.predecessor = predecessor
        self.replacements = 0

    def visit_Subscript(self, node: ast.Subscript) -> ast.AST:
        if subscript_chain(node) == ("freeze_receipt", NEW_KEYS):
            self.replacements += 1
            return copy.deepcopy(self.predecessor)
        return self.generic_visit(node)


def prove(repo_root: Path, candidate_path: Path) -> dict[str, object]:
    predecessor = git(repo_root, "cat-file", "blob", PREDECESSOR_BLOB)
    if blob_oid(predecessor) != PREDECESSOR_BLOB:
        raise ProofError("predecessor_blob_identity_mismatch")
    successor = candidate_path.read_bytes()
    try:
        old_tree = ast.parse(predecessor.decode("utf-8"), filename="predecessor.py")
        new_tree = ast.parse(successor.decode("utf-8"), filename=str(candidate_path))
    except (SyntaxError, UnicodeError) as exc:
        raise ProofError("runner_ast_parse_failed", str(exc)) from exc

    old_path_assignment = path_assignment(old_tree)
    new_path_assignment = path_assignment(new_tree)
    old_path = old_path_assignment.value.args[0].value
    new_path = new_path_assignment.value.args[0].value
    if old_path != OLD_RECEIPT_PATH or new_path != NEW_RECEIPT_PATH:
        raise ProofError("receipt_path_value_mismatch", json.dumps({"old": old_path, "new": new_path}))

    old_lookup = matching_subscripts(old_tree, "freeze_receipt", OLD_KEYS)
    new_lookup = matching_subscripts(new_tree, "freeze_receipt", NEW_KEYS)
    if len(old_lookup) != 1 or len(new_lookup) != 1:
        raise ProofError("pr130_lookup_count", json.dumps({"old": len(old_lookup), "new": len(new_lookup)}))

    removed, added = source_changes(predecessor, successor)

    normalized = copy.deepcopy(new_tree)
    normalized_path = path_assignment(normalized)
    normalized_path.value.args[0].value = old_path
    replacer = ReplaceAuthorizedLookup(old_lookup[0])
    normalized = replacer.visit(normalized)
    if replacer.replacements != 1:
        raise ProofError("ast_lookup_normalization_count", str(replacer.replacements))
    if ast.dump(old_tree, include_attributes=False) != ast.dump(normalized, include_attributes=False):
        raise ProofError("runner_ast_delta_not_exact")

    return {
        "schema": "ers-05-runner-source-delta-proof/1",
        "status": "PASS",
        "predecessor_blob": PREDECESSOR_BLOB,
        "successor_blob": blob_oid(successor),
        "receipt_path_old": old_path,
        "receipt_path_new": new_path,
        "pr130_lookup_old": list(OLD_KEYS),
        "pr130_lookup_new": list(NEW_KEYS),
        "removed_source_lines": [line.rstrip("\n") for line in removed],
        "added_source_lines": [line.rstrip("\n") for line in added],
        "whole_ast_equal_after_authorized_normalization": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--candidate-source", type=Path)
    args = parser.parse_args()
    candidate = args.candidate_source or (args.repo_root / RUNNER_PATH)
    try:
        result = prove(args.repo_root.resolve(), candidate.resolve())
    except ProofError as exc:
        print(json.dumps({"schema": "ers-05-runner-source-delta-proof/1", "status": "FAIL",
                          "error_code": exc.code, "error": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
