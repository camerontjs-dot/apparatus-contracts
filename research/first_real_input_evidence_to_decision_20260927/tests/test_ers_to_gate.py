from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "ers_to_gate.py"
spec = importlib.util.spec_from_file_location("ers_to_gate", SCRIPT)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


def tagged(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


class AdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "sources").mkdir()
        self.source = self.root / "sources" / "raw.md"
        self.source.write_text("Exact raw source bytes.\n", encoding="utf-8")
        identity = tagged(self.source.read_bytes())
        self.inventory = {
            "schema": "ers.mainframe_backlog_intake.rc0",
            "inventory_id": "backlog-inventory:sha256:" + "1" * 64,
            "mainframe_read_only": True,
            "source_semantics": "UNASSESSED",
            "documents": [
                {
                    "knowledge_path": "10_knowledge/demo/item.md",
                    "document_identity": "sha256:" + "2" * 64,
                    "claims": [
                        {
                            "claim_id": "claim:sha256:" + "3" * 64,
                            "text": "Alpha had a higher rate than Beta.",
                            "source_semantics": "UNASSESSED",
                            "resolved_raw_source_ref_ids": ["source-ref:raw"],
                        }
                    ],
                    "source_refs": [
                        {
                            "source_ref_id": "source-ref:raw",
                            "resolution_status": "resolved_local",
                            "semantic_status": "UNASSESSED",
                            "content_identity": identity,
                            "packet_path": "sources/raw.md",
                        }
                    ],
                }
            ],
        }
        (self.root / "inventory.json").write_text(json.dumps(self.inventory), encoding="utf-8")
        self.selection = self.root / "selection.json"
        self.selection.write_text(
            json.dumps(
                {
                    "schema": "cal-pipeline-real-input-selection-v1",
                    "knowledge_path": "10_knowledge/demo/item.md",
                    "document_identity": "sha256:" + "2" * 64,
                    "claim_id": "claim:sha256:" + "3" * 64,
                }
            ),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_copies_identity_text_and_bytes_without_semantic_metadata(self) -> None:
        packet, receipt = mod.build(self.root, self.selection)
        self.assertEqual(packet["request"]["root_text"], "Alpha had a higher rate than Beta.")
        self.assertEqual(packet["request"]["sources"][0]["content"], "Exact raw source bytes.\n")
        self.assertEqual(packet["source_metadata"], [])
        self.assertEqual(packet["evidence_task"], {})
        self.assertEqual(receipt["source_semantics"], "UNASSESSED")
        self.assertFalse(receipt["semantic_inference_performed"])

    def test_source_byte_substitution_is_rejected(self) -> None:
        self.source.write_text("Changed bytes.\n", encoding="utf-8")
        with self.assertRaises(mod.AdapterError):
            mod.build(self.root, self.selection)

    def test_semantic_status_drift_is_rejected(self) -> None:
        self.inventory["documents"][0]["source_refs"][0]["semantic_status"] = "SUPPORTED"
        (self.root / "inventory.json").write_text(json.dumps(self.inventory), encoding="utf-8")
        with self.assertRaises(mod.AdapterError):
            mod.build(self.root, self.selection)

    def test_unsupported_representation_is_rejected(self) -> None:
        binary = self.root / "sources" / "raw.pdf"
        binary.write_bytes(b"%PDF fake")
        row = self.inventory["documents"][0]["source_refs"][0]
        row["packet_path"] = "sources/raw.pdf"
        row["content_identity"] = tagged(binary.read_bytes())
        (self.root / "inventory.json").write_text(json.dumps(self.inventory), encoding="utf-8")
        with self.assertRaises(mod.AdapterError):
            mod.build(self.root, self.selection)


if __name__ == "__main__":
    unittest.main()
