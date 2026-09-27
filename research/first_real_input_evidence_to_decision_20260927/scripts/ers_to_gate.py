#!/usr/bin/env python3
"""Deterministic ERS backlog-intake -> Gate packet adapter.

This adapter copies claim identity/text and exact ERS-resolved raw source bytes.
It does not decide support, refutation, source authority, applicability, or completeness.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

SCHEMA = "cal-pipeline-ers-to-gate-adapter-receipt-v1"


class AdapterError(ValueError):
    pass


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def _media_type(packet_path: str) -> str:
    suffix = Path(packet_path).suffix.lower()
    if suffix == ".md":
        return "text/markdown; charset=utf-8"
    if suffix in {".txt", ".text"}:
        return "text/plain; charset=utf-8"
    raise AdapterError(
        f"resolved source representation is outside Gate/Contract-A controlled text vocabulary: {packet_path}"
    )


def _within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def build(intake_dir: Path, selection_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    root = intake_dir.resolve(strict=True)
    inventory = json.loads((root / "inventory.json").read_text(encoding="utf-8"))
    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    if selection.get("schema") != "cal-pipeline-real-input-selection-v1":
        raise AdapterError("selection schema mismatch")
    if inventory.get("schema") != "ers.mainframe_backlog_intake.rc0":
        raise AdapterError("ERS inventory schema mismatch")
    if inventory.get("source_semantics") != "UNASSESSED":
        raise AdapterError("ERS inventory must preserve source_semantics=UNASSESSED")
    if inventory.get("mainframe_read_only") is not True:
        raise AdapterError("ERS inventory does not declare read-only MainFrame intake")

    docs = [
        row for row in inventory.get("documents", [])
        if row.get("knowledge_path") == selection.get("knowledge_path")
        and row.get("document_identity") == selection.get("document_identity")
    ]
    if len(docs) != 1:
        raise AdapterError("selection must bind exactly one ERS knowledge document identity")
    doc = docs[0]
    claims = [row for row in doc.get("claims", []) if row.get("claim_id") == selection.get("claim_id")]
    if len(claims) != 1:
        raise AdapterError("selection must bind exactly one ERS claim")
    claim = claims[0]
    if claim.get("source_semantics") != "UNASSESSED":
        raise AdapterError("selected ERS claim must retain source_semantics=UNASSESSED")

    raw_ids = list(claim.get("resolved_raw_source_ref_ids") or [])
    if not raw_ids:
        raise AdapterError("selected claim has no recoverable raw local source bytes")
    by_id = {row.get("source_ref_id"): row for row in doc.get("source_refs", [])}

    gate_sources = []
    bindings = []
    for source_ref_id in sorted(raw_ids):
        row = by_id.get(source_ref_id)
        if not isinstance(row, dict):
            raise AdapterError(f"missing ERS source record: {source_ref_id}")
        if row.get("resolution_status") != "resolved_local":
            raise AdapterError(f"ERS source is not resolved_local: {source_ref_id}")
        if row.get("semantic_status") != "UNASSESSED":
            raise AdapterError(f"ERS source semantic status drifted: {source_ref_id}")
        packet_rel = row.get("packet_path")
        identity = row.get("content_identity")
        if not isinstance(packet_rel, str) or not isinstance(identity, str):
            raise AdapterError(f"ERS source packet identity is incomplete: {source_ref_id}")
        packet_path = (root / packet_rel).resolve(strict=True)
        if not _within(packet_path, root):
            raise AdapterError("ERS packet path escapes intake directory")
        data = packet_path.read_bytes()
        observed = sha256_bytes(data)
        if observed != identity:
            raise AdapterError(
                f"ERS source byte identity mismatch for {source_ref_id}: expected {identity}, observed {observed}"
            )
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise AdapterError(f"source is not UTF-8 text: {source_ref_id}") from exc
        gate_sources.append(
            {
                "source_id": source_ref_id,
                "media_type": _media_type(packet_rel),
                "content": text,
            }
        )
        bindings.append(
            {
                "source_ref_id": source_ref_id,
                "ers_content_identity": identity,
                "packet_path": packet_rel,
                "media_type": gate_sources[-1]["media_type"],
            }
        )

    packet = {
        "request": {
            "handoff_id": f"ers-intake:{inventory['inventory_id']}:{claim['claim_id']}",
            "producer_id": "camerontjs-dot/epistemic-research-system:backlog-intake-rc0",
            "producer_version": "5c22d846174154f00649efc6b312f5409c6d1a3d",
            "work_id": inventory["inventory_id"],
            "root_id": claim["claim_id"],
            "root_text": claim["text"],
            "sources": gate_sources,
            "context_source_id": None,
        },
        "evidence_task": {},
        "source_metadata": [],
    }
    packet_bytes = canonical_bytes(packet)
    receipt = {
        "schema": SCHEMA,
        "inventory_id": inventory["inventory_id"],
        "knowledge_path": doc["knowledge_path"],
        "document_identity": doc["document_identity"],
        "claim_id": claim["claim_id"],
        "claim_text_sha256": sha256_bytes(claim["text"].encode("utf-8")),
        "source_semantics": "UNASSESSED",
        "source_bindings": bindings,
        "gate_packet_sha256": sha256_bytes(packet_bytes),
        "semantic_inference_performed": False,
    }
    return packet, receipt


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--intake-dir", required=True, type=Path)
    ap.add_argument("--selection", required=True, type=Path)
    ap.add_argument("--gate-packet", required=True, type=Path)
    ap.add_argument("--receipt", required=True, type=Path)
    args = ap.parse_args()
    packet, receipt = build(args.intake_dir, args.selection)
    args.gate_packet.parent.mkdir(parents=True, exist_ok=True)
    args.gate_packet.write_bytes(canonical_bytes(packet))
    args.receipt.write_bytes(canonical_bytes(receipt))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
