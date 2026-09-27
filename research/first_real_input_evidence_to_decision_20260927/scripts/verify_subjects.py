#!/usr/bin/env python3
"""Verify exact source checkouts and executable blobs without network access."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def git(root: Path, *args: str) -> str:
    cp = subprocess.run(["git", "-C", str(root), *args], text=True, capture_output=True, check=False)
    if cp.returncode:
        raise SystemExit(f"git verification failed at {root}: {cp.stderr.strip()}")
    return cp.stdout.strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--subjects", required=True, type=Path)
    ap.add_argument(
        "--root",
        action="append",
        default=[],
        metavar="ROLE=CHECKOUT",
        help="Repeat for each checkout_required subject.",
    )
    args = ap.parse_args()
    roots = {}
    for item in args.root:
        if "=" not in item:
            raise SystemExit("--root must be ROLE=CHECKOUT")
        role, value = item.split("=", 1)
        roots[role] = Path(value).resolve()

    data = json.loads(args.subjects.read_text(encoding="utf-8"))
    failures = []
    checked = []
    for role, subject in data["subjects"].items():
        if not subject.get("checkout_required"):
            continue
        root = roots.get(role)
        if root is None:
            failures.append(f"missing --root for {role}")
            continue
        expected = subject["commit"]
        observed = git(root, "rev-parse", "HEAD")
        if observed != expected:
            failures.append(f"{role}: HEAD {observed} != {expected}")
            continue
        if git(root, "status", "--porcelain"):
            failures.append(f"{role}: checkout is dirty")
        expected_tree = subject.get("tree")
        if expected_tree and git(root, "rev-parse", "HEAD^{tree}") != expected_tree:
            failures.append(f"{role}: tree identity mismatch")
        tag = subject.get("tag")
        if tag:
            deref = git(root, "rev-parse", f"refs/tags/{tag}^{{}}")
            if deref != expected:
                failures.append(f"{role}: tag {tag} does not dereference to expected commit")
        for path, blob in subject.get("files", {}).items():
            observed_blob = git(root, "rev-parse", f"HEAD:{path}")
            if observed_blob != blob:
                failures.append(f"{role}: blob mismatch {path}: {observed_blob} != {blob}")
        checked.append(role)

    if failures:
        for line in failures:
            print("FAIL", line)
        return 2
    print(json.dumps({"status": "verified", "roles": checked}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
