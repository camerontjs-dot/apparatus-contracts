"""Portable controls for exact single-item MainFrame intake RC1."""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from typing import Any

from adapters.base import LLMAdapter
import harness.backlog_single_item_intake as single


def tagged(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


class CountingAdapter(LLMAdapter):
    def __init__(self) -> None:
        self.generate_calls = 0

    def health_check(self) -> bool:
        return True

    def generate(
        self,
        prompt: str,
        *,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        json_mode: bool = False,
    ) -> str:
        self.generate_calls += 1
        return json.dumps(
            {
                "claims": [
                    {
                        "text": "The current implementation preserves exact decision identity across the tested handoff.",
                        "origin_relation": "explicit",
                        "origin_refs": ["paragraph[1]"],
                        "lineage_refs": [],
                    }
                ]
            }
        )

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [[0.0] for _ in texts]

    @property
    def model_name(self) -> str:
        return "fake-single-item"

    @property
    def adapter_name(self) -> str:
        return "fake"


class SingleItemIntakeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.mainframe = self.base / "MainFrame"
        self.knowledge = self.mainframe / "10_knowledge" / "demo"
        self.raw = self.mainframe / "10_knowledge" / "demo" / "raw"
        self.project = self.mainframe / "30_projects" / "demo"
        self.knowledge.mkdir(parents=True)
        self.raw.mkdir(parents=True)
        self.project.mkdir(parents=True)

        (self.raw / "capture.md").write_text(
            "---\ntype: raw\nstatus: queued\n---\n\nRaw source body.\n",
            encoding="utf-8",
        )
        (self.project / "README.md").write_text(
            "---\ntype: note\nsource: 10_knowledge/demo/raw/capture.md\n---\n\nProject synthesis.\n",
            encoding="utf-8",
        )
        self.selected = self.knowledge / "selected.md"
        self.selected.write_text(
            "---\ntype: note\nstatus: synthesized\nsource: 30_projects/demo/README.md\n---\n\n"
            "The current implementation preserves exact decision identity across the tested handoff.\n",
            encoding="utf-8",
        )
        self.other = self.knowledge / "other.md"
        self.other.write_text(
            "---\ntype: note\nstatus: synthesized\n---\n\n"
            "THIS DOCUMENT MUST NOT BE READ BY STRICT SINGLE-ITEM INTAKE.\n",
            encoding="utf-8",
        )
        self.adapter = CountingAdapter()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _allowlist(self, items: list[dict[str, str]] | None = None) -> Path:
        if items is None:
            items = [
                {
                    "knowledge_path": "10_knowledge/demo/selected.md",
                    "document_identity": tagged(self.selected.read_bytes()),
                }
            ]
        path = self.base / "allowlist.json"
        path.write_text(
            json.dumps({"schema": single.ALLOWLIST_SCHEMA, "items": items}),
            encoding="utf-8",
        )
        return path

    def test_reads_only_admitted_document_plus_explicit_provenance(self) -> None:
        allowlist = self._allowlist()
        out = self.base / "out"
        original = Path.read_bytes
        reads: list[Path] = []

        def tracked(path: Path) -> bytes:
            resolved = path.resolve(strict=True)
            reads.append(resolved)
            if resolved == self.other.resolve(strict=True):
                raise AssertionError("non-admitted sibling document was read")
            return original(path)

        with patch.object(Path, "read_bytes", tracked):
            single.run_single_item_intake(
                self.mainframe,
                self.adapter,
                allowlist_path=allowlist,
                output_dir=out,
            )

        self.assertEqual(self.adapter.generate_calls, 1)
        self.assertNotIn(self.other.resolve(strict=True), reads)
        inv = json.loads((out / "inventory.json").read_text(encoding="utf-8"))
        self.assertEqual(inv["schema"], single.INVENTORY_SCHEMA)
        self.assertEqual(inv["mode"], "exact_single_item")
        self.assertEqual(inv["knowledge_path"], "10_knowledge/demo/selected.md")
        self.assertEqual(len(inv["documents"]), 1)
        raw_ids = inv["documents"][0]["claims"][0]["resolved_raw_source_ref_ids"]
        self.assertEqual(len(raw_ids), 1)

    def test_zero_item_admission_rejects_before_generation(self) -> None:
        with self.assertRaises(single.SingleItemIntakeError):
            single.run_single_item_intake(
                self.mainframe,
                self.adapter,
                allowlist_path=self._allowlist([]),
                output_dir=self.base / "out-zero",
            )
        self.assertEqual(self.adapter.generate_calls, 0)

    def test_duplicate_and_multi_item_admission_reject_before_generation(self) -> None:
        item = {
            "knowledge_path": "10_knowledge/demo/selected.md",
            "document_identity": tagged(self.selected.read_bytes()),
        }
        with self.assertRaises(single.SingleItemIntakeError):
            single.run_single_item_intake(
                self.mainframe,
                self.adapter,
                allowlist_path=self._allowlist([item, dict(item)]),
                output_dir=self.base / "out-dup",
            )
        self.assertEqual(self.adapter.generate_calls, 0)

        other = {
            "knowledge_path": "10_knowledge/demo/other.md",
            "document_identity": tagged(self.other.read_bytes()),
        }
        with self.assertRaises(single.SingleItemIntakeError):
            single.run_single_item_intake(
                self.mainframe,
                self.adapter,
                allowlist_path=self._allowlist([item, other]),
                output_dir=self.base / "out-multi",
            )
        self.assertEqual(self.adapter.generate_calls, 0)

    def test_traversal_and_absent_path_reject_before_generation(self) -> None:
        for raw in (
            "../outside.md",
            "10_knowledge/demo/../other.md",
            "10_knowledge/demo/absent.md",
        ):
            with self.subTest(raw=raw):
                allowlist = self._allowlist(
                    [{"knowledge_path": raw, "document_identity": "sha256:" + "0" * 64}]
                )
                with self.assertRaises(single.SingleItemIntakeError):
                    single.run_single_item_intake(
                        self.mainframe,
                        self.adapter,
                        allowlist_path=allowlist,
                        output_dir=self.base / ("out-" + hashlib.sha256(raw.encode()).hexdigest()[:8]),
                    )
                self.assertEqual(self.adapter.generate_calls, 0)

    def test_symlink_escape_rejects_before_generation(self) -> None:
        outside = self.base / "outside.md"
        outside.write_text(
            "---\ntype: note\nstatus: synthesized\n---\n\nOutside.\n",
            encoding="utf-8",
        )
        link = self.knowledge / "escape.md"
        try:
            link.symlink_to(outside)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        allowlist = self._allowlist(
            [
                {
                    "knowledge_path": "10_knowledge/demo/escape.md",
                    "document_identity": tagged(outside.read_bytes()),
                }
            ]
        )
        with self.assertRaises(single.SingleItemIntakeError):
            single.run_single_item_intake(
                self.mainframe,
                self.adapter,
                allowlist_path=allowlist,
                output_dir=self.base / "out-escape",
            )
        self.assertEqual(self.adapter.generate_calls, 0)

    def test_document_identity_mismatch_rejects_before_generation(self) -> None:
        allowlist = self._allowlist(
            [
                {
                    "knowledge_path": "10_knowledge/demo/selected.md",
                    "document_identity": "sha256:" + "0" * 64,
                }
            ]
        )
        with self.assertRaises(single.SingleItemIntakeError):
            single.run_single_item_intake(
                self.mainframe,
                self.adapter,
                allowlist_path=allowlist,
                output_dir=self.base / "out-hash",
            )
        self.assertEqual(self.adapter.generate_calls, 0)

    def test_provenance_identity_mismatch_rejects_before_generation(self) -> None:
        allowlist = self._allowlist()
        bad_entries = [
            {
                "source_ref_id": "source-ref:bad",
                "raw_ref": "30_projects/demo/README.md",
                "resolution_status": "resolved_local",
                "semantic_status": "UNASSESSED",
                "content_identity": "sha256:" + "a" * 64,
                "resolved_mainframe_path": "30_projects/demo/README.md",
            }
        ]
        bad_bytes = {"sha256:" + "a" * 64: b"different bytes"}
        with patch.object(
            single,
            "collect_source_refs",
            return_value=(bad_entries, {}, ["source-ref:bad"], bad_bytes),
        ), patch.object(single, "trace_explicit_lineage", return_value=[]):
            with self.assertRaises(single.SingleItemIntakeError):
                single.run_single_item_intake(
                    self.mainframe,
                    self.adapter,
                    allowlist_path=allowlist,
                    output_dir=self.base / "out-prov-mismatch",
                )
        self.assertEqual(self.adapter.generate_calls, 0)

    def test_source_path_escape_rejects_before_generation(self) -> None:
        outside = self.base / "external.txt"
        outside.write_text("outside", encoding="utf-8")
        self.selected.write_text(
            "---\ntype: note\nstatus: synthesized\n---\n\n"
            "The current implementation preserves exact decision identity across the tested handoff. "
            "[outside](../../../external.txt)\n",
            encoding="utf-8",
        )
        allowlist = self._allowlist()
        with self.assertRaises(single.SingleItemIntakeError):
            single.run_single_item_intake(
                self.mainframe,
                self.adapter,
                allowlist_path=allowlist,
                output_dir=self.base / "out-source-escape",
            )
        self.assertEqual(self.adapter.generate_calls, 0)

    def test_missing_raw_provenance_is_preserved_as_stopped_without_generation(self) -> None:
        self.selected.write_text(
            "---\ntype: note\nstatus: synthesized\n---\n\n"
            "The current implementation preserves exact decision identity across the tested handoff.\n",
            encoding="utf-8",
        )
        out = self.base / "out-stopped"
        single.run_single_item_intake(
            self.mainframe,
            self.adapter,
            allowlist_path=self._allowlist(),
            output_dir=out,
        )
        self.assertEqual(self.adapter.generate_calls, 0)
        stopped = json.loads((out / "STOPPED.json").read_text(encoding="utf-8"))
        self.assertEqual(stopped["terminal_state"], "STOPPED")
        self.assertEqual(stopped["stop_code"], "NO_RESOLVED_RAW_PROVENANCE")
        self.assertEqual(stopped["model_generation_calls"], 0)

    def test_legacy_backlog_intake_source_is_not_modified_by_successor(self) -> None:
        legacy = Path(__file__).parent / "backlog_intake.py"
        self.assertTrue(legacy.exists())
        # Exact Git-blob preservation is also pinned by the successor qualification workflow.
        self.assertIn("def _scan_paths(", legacy.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
