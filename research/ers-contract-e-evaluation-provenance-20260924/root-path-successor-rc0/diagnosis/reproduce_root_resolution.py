#!/usr/bin/env python3
"""Reproduce the frozen PR #148 runner repository-root defect without importing it."""

from __future__ import annotations

import ast
import hashlib
import json
import subprocess
from pathlib import Path

FROZEN_COMMIT = "b673b2b06804e94042ad35d4621f4a4ca5ee4851"
RUNNER_BLOB = "79a347c9698610a1c743074e426a79590cb32ba4"
RUNNER_RELATIVE = (
    "research/ers-contract-e-evaluation-provenance-20260921/"
    "fixture-bound-identity-successor-rc0/reproduce_rc6_fixture_bound.py"
)
RECEIPT_RELATIVE = (
    "research/ers-contract-e-evaluation-provenance-20260921/"
    "fixture-bound-receipt-contract-successor-rc0/FREEZE_RECEIPT.json"
)
PREFLIGHT_RELATIVE = (
    "research/ers-contract-e-evaluation-provenance-20260921/"
    "fixture-bound-receipt-contract-successor-rc0/qualification-20260923/POSITIVE.json"
)
RENDER_JOIN = "research/ers-render-bound-shadow-composition-20260921/reproduce.py"
OBSERVED_FAILURE = Path(
    "/private/tmp/ers-eval-matrix-20260924/outputs/matrix-run/FAILURE.json"
)
OBSERVED_FAILURE_SHA256 = (
    "d169327a4958e203e087489a71a000460de5b36ad33583559d86619f2057f3d0"
)


def git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(cwd), *args],
        text=True,
        capture_output=True,
        check=False,
    )


def show_toplevel(path: Path) -> str | None:
    result = git(path, "rev-parse", "--show-toplevel")
    if result.returncode:
        return None
    return result.stdout.strip()


def classify_root_use(line: str) -> str:
    if line.startswith("ROOT ="):
        return "assignment"
    if "relative_to(ROOT)" in line:
        return "repository_relative_conversion"
    if 'ROOT / "research/' in line:
        return "repository_relative_join"
    if "git(ROOT" in line:
        return "git_cwd"
    return "other_root_value"


def main() -> None:
    repo = Path(__file__).resolve().parent
    while repo != repo.parent:
        toplevel = show_toplevel(repo)
        head = git(repo, "rev-parse", "HEAD")
        if (
            toplevel is not None
            and Path(toplevel).resolve() == repo.resolve()
            and head.returncode == 0
            and head.stdout.strip() == FROZEN_COMMIT
        ):
            break
        repo = repo.parent
    else:
        raise SystemExit("frozen_worktree_not_found")

    runner = repo / RUNNER_RELATIVE
    blob = git(repo, "rev-parse", f"HEAD:{RUNNER_RELATIVE}")
    if blob.returncode or blob.stdout.strip() != RUNNER_BLOB:
        raise SystemExit("frozen_runner_blob_mismatch")
    here = runner.resolve().parent
    candidates = []
    for index, path in enumerate([here, *list(here.parents[:4])]):
        name = "HERE" if index == 0 else f"parents[{index - 1}]"
        toplevel = show_toplevel(path)
        candidates.append({
            "name": name,
            "basename": path.name,
            "contains_git_metadata": (path / ".git").exists(),
            "show_toplevel": toplevel,
            "path_equals_show_toplevel": toplevel is not None and path.resolve() == Path(toplevel).resolve(),
            "is_repository_root": path.resolve() == repo.resolve(),
        })

    receipt = (repo / RECEIPT_RELATIVE).resolve()
    preflight = (repo / PREFLIGHT_RELATIVE).resolve()
    transforms = {}
    for label, root in (("parents[1]", here.parents[1]), ("parents[2]", here.parents[2])):
        receipt_relative = receipt.relative_to(root).as_posix()
        preflight_relative = preflight.relative_to(root).as_posix()
        head_spec = f"HEAD:{receipt_relative}"
        parsed = git(root, "rev-parse", head_spec)
        joined = root / RENDER_JOIN
        transforms[label] = {
            "basename": root.name,
            "path_equals_show_toplevel": show_toplevel(root) == str(root.resolve()),
            "receipt_relative": receipt_relative,
            "preflight_relative": preflight_relative,
            "head_spec": head_spec,
            "rev_parse_exit": parsed.returncode,
            "rev_parse_stdout": parsed.stdout.strip(),
            "rev_parse_stderr": parsed.stderr.strip(),
            "render_join_exists": joined.is_file(),
        }

    source = runner.read_text(encoding="utf-8")
    tree = ast.parse(source)
    lines = source.splitlines()
    uses = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id == "ROOT":
            text = lines[node.lineno - 1].strip()
            uses.append({
                "line": node.lineno,
                "context": type(node.ctx).__name__,
                "kind": classify_root_use(text),
                "text": text,
            })
    uses.sort(key=lambda item: (item["line"], item["text"]))

    failure_raw = OBSERVED_FAILURE.read_bytes()
    failure_sha = hashlib.sha256(failure_raw).hexdigest()
    if failure_sha != OBSERVED_FAILURE_SHA256:
        raise SystemExit("observed_failure_bytes_changed")
    failure = json.loads(failure_raw)
    parents1 = transforms["parents[1]"]
    parents2 = transforms["parents[2]"]
    minimal = (
        parents1["rev_parse_exit"] != 0
        and parents1["head_spec"] in failure["error"]
        and "/research" in failure["error"]
        and parents2["rev_parse_exit"] == 0
        and parents2["rev_parse_stdout"] == "bc7d3938be9146dd6455ab5f9fda896f22a70274"
        and parents2["render_join_exists"]
        and not parents1["render_join_exists"]
        and next(item["is_repository_root"] for item in candidates if item["name"] == "parents[2]")
        and not next(item["is_repository_root"] for item in candidates if item["name"] == "parents[1]")
    )
    report = {
        "schema": "ers-05-root-path-diagnosis/1",
        "frozen_commit": FROZEN_COMMIT,
        "runner_blob": RUNNER_BLOB,
        "runner_relative": RUNNER_RELATIVE,
        "assignment": "ROOT = HERE.parents[1]",
        "candidates": candidates,
        "transforms": transforms,
        "root_name_uses": uses,
        "observed_failure": {
            "path": str(OBSERVED_FAILURE),
            "sha256": failure_sha,
            "disposition": failure["disposition"],
            "error": failure["error"],
            "matrix_progress": failure["matrix_progress"],
        },
        "minimal_correction": "ROOT = HERE.parents[2]" if minimal else None,
        "later_join_affected": True,
        "scientific_boundary_reached_in_observed_failure": False,
    }
    destination = Path(__file__).resolve().parent / "DIAGNOSIS.json"
    destination.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "minimal_correction": report["minimal_correction"],
        "parents1_head_spec": parents1["head_spec"],
        "parents1_exit": parents1["rev_parse_exit"],
        "parents2_head_spec": parents2["head_spec"],
        "parents2_blob": parents2["rev_parse_stdout"],
        "render_join_parents1": parents1["render_join_exists"],
        "render_join_parents2": parents2["render_join_exists"],
        "root_uses": len(uses),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
