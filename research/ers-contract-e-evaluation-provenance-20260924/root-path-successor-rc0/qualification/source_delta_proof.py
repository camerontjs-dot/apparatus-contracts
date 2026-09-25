#!/usr/bin/env python3
"""Prove the successor runner differs from PR #148 by one root-index constant."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import subprocess
from pathlib import Path

PREDECESSOR_COMMIT = "b673b2b06804e94042ad35d4621f4a4ca5ee4851"
PREDECESSOR_BLOB = "79a347c9698610a1c743074e426a79590cb32ba4"
RUNNER = (
    "research/ers-contract-e-evaluation-provenance-20260921/"
    "fixture-bound-identity-successor-rc0/reproduce_rc6_fixture_bound.py"
)


class ProofError(RuntimeError):
    pass


def git_bytes(root: Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode:
        raise ProofError(result.stderr.decode("utf-8", "replace").strip())
    return result.stdout


def blob_oid(raw: bytes) -> str:
    header = b"blob " + str(len(raw)).encode("ascii") + b"\0"
    return hashlib.sha1(header + raw).hexdigest()


def root_index(tree: ast.AST) -> int:
    found = []
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == "ROOT" for target in node.targets):
            continue
        value = node.value
        if (
            isinstance(value, ast.Subscript)
            and isinstance(value.value, ast.Attribute)
            and isinstance(value.value.value, ast.Name)
            and value.value.value.id == "HERE"
            and value.value.attr == "parents"
            and isinstance(value.slice, ast.Constant)
            and isinstance(value.slice.value, int)
        ):
            found.append((node, value.slice.value))
    if len(found) != 1:
        raise ProofError(f"root_assignment_count:{len(found)}")
    return found[0][1]


def normalized_dump(source: str, index: int) -> str:
    tree = ast.parse(source)
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if any(isinstance(target, ast.Name) and target.id == "ROOT" for target in node.targets):
            node.value.slice.value = index
    return ast.dump(tree, include_attributes=False)


def function_dumps(source: str) -> dict[str, str]:
    tree = ast.parse(source)
    return {
        node.name: ast.dump(node, include_attributes=False)
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    repo = args.repo.resolve()
    predecessor = git_bytes(repo, "cat-file", "-p", PREDECESSOR_BLOB)
    successor = (repo / RUNNER).read_bytes()
    if blob_oid(predecessor) != PREDECESSOR_BLOB:
        raise ProofError("predecessor_blob_identity")
    successor_blob = blob_oid(successor)
    predecessor_text = predecessor.decode("utf-8")
    successor_text = successor.decode("utf-8")
    old_lines = predecessor_text.splitlines()
    new_lines = successor_text.splitlines()
    if len(old_lines) != len(new_lines):
        raise ProofError("line_count_changed")
    changed = [
        (index + 1, old, new)
        for index, (old, new) in enumerate(zip(old_lines, new_lines))
        if old != new
    ]
    if changed != [(29, "ROOT = HERE.parents[1]", "ROOT = HERE.parents[2]")]:
        raise ProofError("unexpected_line_delta:" + json.dumps(changed))
    if root_index(ast.parse(predecessor_text)) != 1 or root_index(ast.parse(successor_text)) != 2:
        raise ProofError("root_index_mismatch")
    if normalized_dump(predecessor_text, 0) != normalized_dump(successor_text, 0):
        raise ProofError("ast_not_equivalent_after_root_normalization")
    if function_dumps(predecessor_text) != function_dumps(successor_text):
        raise ProofError("function_or_class_body_changed")
    protected = (
        "matrix_rejection",
        "start_supervisor",
        "run_matrix",
        "build_and_validate_sidecars",
        "main",
    )
    bodies = function_dumps(successor_text)
    if any(name not in bodies for name in protected):
        raise ProofError("protected_function_missing")
    report = {
        "schema": "ers-05-root-path-source-delta/1",
        "predecessor_commit": PREDECESSOR_COMMIT,
        "predecessor_runner_blob": PREDECESSOR_BLOB,
        "successor_runner_blob": successor_blob,
        "changed_lines": [
            {"line": 29, "predecessor": "ROOT = HERE.parents[1]", "successor": "ROOT = HERE.parents[2]"}
        ],
        "ast_equivalent_after_normalizing_root_index": True,
        "function_and_class_bodies_identical": True,
        "protected_functions_present": list(protected),
        "scientific_matrix_mutation_supervisor_transcript_contract_bodies_unchanged": True,
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
