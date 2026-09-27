#!/usr/bin/env python3
"""Verify frozen target files and documented independent review without judging semantics."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ACTIVE = {"strict_comparison", "direct_event_order"}


def sha(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def resolve(raw: str, anchor: Path) -> Path:
    path = Path(raw)
    if not path.is_absolute():
        path = anchor / path
    return path.resolve(strict=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", required=True, type=Path)
    ap.add_argument("--contract-a", required=True, type=Path)
    args = ap.parse_args()
    args.review = args.review.resolve(strict=True)
    args.contract_a = args.contract_a.resolve(strict=True)

    review = json.loads(args.review.read_text(encoding="utf-8"))
    contract_a = json.loads(args.contract_a.read_text(encoding="utf-8"))
    if review.get("schema") != "cal-pipeline-trusted-target-review-v1":
        raise SystemExit("target review schema mismatch")
    if review.get("contract_a_handoff_sha256") != contract_a.get("handoff_sha256"):
        raise SystemExit("target review does not bind this Contract A handoff")
    if review.get("contract_a_file_sha256") != sha(args.contract_a):
        raise SystemExit("target review does not bind these exact Contract A bytes")

    children = contract_a.get("decomposition", {}).get("children", [])
    expected = {row["proposition_id"]: row for row in children}
    targets = review.get("targets")
    if not isinstance(targets, list) or {row.get("proposition_id") for row in targets} != set(expected):
        raise SystemExit("reviewed target ids must exactly equal Contract A child ids")

    for row in targets:
        pid = row["proposition_id"]
        if row.get("independent_review") is not True or row.get("semantic_fidelity_attested") is not True:
            raise SystemExit(f"target {pid} lacks independent semantic-fidelity review")
        author = row.get("target_author_context")
        reviewer = row.get("reviewer_context")
        if not author or not reviewer or author == reviewer:
            raise SystemExit("target author and independent reviewer contexts must be distinct")
        path = resolve(str(row.get("target_path") or ""), args.review.parent)
        if sha(path) != row.get("target_sha256"):
            raise SystemExit(f"target file hash mismatch: {path}")
        target = json.loads(path.read_text(encoding="utf-8"))
        proposition = target.get("proposition", {})
        if target.get("claim_id") != pid or proposition.get("proposition_id") != pid:
            raise SystemExit("target identity mismatch")
        expected_hash = str(expected[pid]["text_sha256"]).removeprefix("sha256:")
        if proposition.get("text_sha256") != expected_hash:
            raise SystemExit("target text_sha256 does not bind exact Contract A child text")
        if proposition.get("semantic_family") not in ACTIVE:
            raise SystemExit("target semantic family is outside the qualified CAL #183 active set")
    print("TARGET_REVIEW_VERIFIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
