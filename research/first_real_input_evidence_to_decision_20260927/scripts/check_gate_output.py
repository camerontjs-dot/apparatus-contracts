#!/usr/bin/env python3
"""Bind Gate Contract A to the selected ERS claim.

For the first-input successor, a non-declared-all_of Gate result is a preserved stop.
It is never an instruction to reroll another claim.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def tagged_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def write_stop(path: Path, *, code: str, detail: str, contract_a: Path) -> None:
    value = {
        "schema": "cal-pipeline-first-real-input-stop-v1",
        "terminal_state": "STOPPED",
        "stop_code": code,
        "detail": detail,
        "contract_a_file_sha256": sha_file(contract_a),
        "reroll_authorized": False,
    }
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract-a", required=True, type=Path)
    ap.add_argument("--adapter-receipt", required=True, type=Path)
    ap.add_argument("--out-target-review", required=True, type=Path)
    ap.add_argument("--stop-receipt", required=True, type=Path)
    args = ap.parse_args()

    a = json.loads(args.contract_a.read_text(encoding="utf-8"))
    receipt = json.loads(args.adapter_receipt.read_text(encoding="utf-8"))
    root = a.get("root_proposition", {})
    if root.get("proposition_id") != receipt.get("claim_id"):
        raise SystemExit("Contract A root proposition id does not match ERS-selected claim")
    if root.get("text_sha256") != receipt.get("claim_text_sha256"):
        raise SystemExit("Contract A root text hash does not match ERS-selected claim")

    expected_sources = {
        row["source_ref_id"]: row["ers_content_identity"]
        for row in receipt["source_bindings"]
    }
    observed_sources = {
        row["source_id"]: row["content_sha256"] for row in a.get("sources", [])
    }
    if observed_sources != expected_sources:
        raise SystemExit("Contract A source identities differ from ERS raw-source bindings")

    decomp = a.get("decomposition", {})
    if decomp.get("state") != "declared" or decomp.get("operator") != "all_of":
        write_stop(
            args.stop_receipt,
            code="CONTRACT_A_NOT_DECLARED_ALL_OF",
            detail=(
                "First admitted case is outside CAL #183 parent-bound shape. "
                "Preserve this result and stop; selecting another claim to obtain all_of "
                "would be result-chasing."
            ),
            contract_a=args.contract_a,
        )
        print("STOPPED_CONTRACT_A_NOT_DECLARED_ALL_OF")
        return 3

    children = decomp.get("children")
    if not isinstance(children, list) or not children:
        write_stop(
            args.stop_receipt,
            code="CONTRACT_A_DECLARED_ALL_OF_WITHOUT_CHILDREN",
            detail="Declared all_of contains no children; preserve and stop.",
            contract_a=args.contract_a,
        )
        print("STOPPED_CONTRACT_A_DECLARED_ALL_OF_WITHOUT_CHILDREN")
        return 3

    targets = []
    for index, child in enumerate(children, start=1):
        text = child.get("text")
        if child.get("sequence") != index:
            raise SystemExit("Contract A child sequence is not contiguous")
        if not isinstance(text, str) or child.get("text_sha256") != tagged_text(text):
            raise SystemExit("Contract A child text hash mismatch")
        targets.append(
            {
                "proposition_id": child["proposition_id"],
                "claim_text": text,
                "claim_text_sha256_tagged": child["text_sha256"],
                "claim_text_sha256_cal": child["text_sha256"].removeprefix("sha256:"),
                "target_path": None,
                "target_sha256": None,
                "target_author_context": None,
                "reviewer_context": None,
                "independent_review": False,
                "semantic_fidelity_attested": False,
            }
        )

    out = {
        "schema": "cal-pipeline-trusted-target-review-v1",
        "contract_a_handoff_sha256": a["handoff_sha256"],
        "contract_a_file_sha256": sha_file(args.contract_a),
        "review_scope": "exact Contract A child text versus typed CAL target fields",
        "targets": targets,
    }
    args.out_target_review.write_text(
        json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    if args.stop_receipt.exists():
        raise SystemExit("unexpected pre-existing stop receipt")
    print("TARGET_REVIEW_REQUIRED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
