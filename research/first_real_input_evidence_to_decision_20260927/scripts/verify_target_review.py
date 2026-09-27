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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", required=True, type=Path)
    args = ap.parse_args()
    review = json.loads(args.review.read_text(encoding="utf-8"))
    if review.get("schema") != "cal-pipeline-trusted-target-review-v1":
        raise SystemExit("target review schema mismatch")
    targets = review.get("targets")
    if not isinstance(targets, list) or not targets:
        raise SystemExit("target review has no child targets")
    for row in targets:
        if row.get("independent_review") is not True or row.get("semantic_fidelity_attested") is not True:
            raise SystemExit(f"target {row.get('proposition_id')} lacks independent semantic-fidelity review")
        if not row.get("target_author_context") or not row.get("reviewer_context"):
            raise SystemExit("target author/reviewer context identities are required")
        if row["target_author_context"] == row["reviewer_context"]:
            raise SystemExit("target author and independent reviewer contexts must be distinct")
        path = Path(row["target_path"]).resolve(strict=True)
        if sha(path) != row.get("target_sha256"):
            raise SystemExit(f"target file hash mismatch: {path}")
        target = json.loads(path.read_text(encoding="utf-8"))
        proposition = target.get("proposition", {})
        if target.get("claim_id") != row["proposition_id"]:
            raise SystemExit("target claim_id mismatch")
        if proposition.get("proposition_id") != row["proposition_id"]:
            raise SystemExit("target proposition id mismatch")
        if proposition.get("text_sha256") != row["claim_text_sha256_cal"]:
            raise SystemExit("target text_sha256 does not bind exact Contract A child text")
        if proposition.get("semantic_family") not in ACTIVE:
            raise SystemExit("target semantic family is outside the qualified CAL #183 active set")
    print("TARGET_REVIEW_VERIFIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
