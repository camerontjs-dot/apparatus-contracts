"""Deterministic tests for MainFrame backlog intake RC0."""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from typing import Any

from adapters.base import LLMAdapter
from harness.backlog_intake import run_backlog_intake


class FakeAdapter(LLMAdapter):
    def __init__(self, payload: dict[str, Any]) -> None:
        self.payload = payload

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
        return json.dumps(self.payload)

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [[0.0] for _ in texts]

    @property
    def model_name(self) -> str:
        return "fake-model-v1"

    @property
    def adapter_name(self) -> str:
        return "fake"


def snapshot_tree(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        result[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


class BacklogIntakeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.mainframe = self.base / "MainFrame"
        self.project = self.mainframe / "10_knowledge" / "demo"
        self.raw = self.mainframe / "30_projects" / "demo" / "raw-materials"
        self.project_dir = self.mainframe / "30_projects" / "demo"
        self.capture_dir = self.mainframe / "10_knowledge" / "demo" / "raw"
        self.project.mkdir(parents=True)
        self.raw.mkdir(parents=True)
        self.capture_dir.mkdir(parents=True)
        (self.raw / "report.txt").write_text("RAW SOURCE BYTES\n", encoding="utf-8")
        (self.capture_dir / "capture.md").write_text(
            "---\ntype: raw\nstatus: queued\nurl: https://example.org/raw\n---\n\nRaw capture body.\n",
            encoding="utf-8",
        )
        (self.project_dir / "README.md").write_text(
            "---\ntype: note\nsource: 10_knowledge/demo/raw/capture.md\n---\n\nProject synthesis.\n",
            encoding="utf-8",
        )
        self.note = self.project / "synthesis.md"
        self.note.write_text(
            "---\ntype: note\nstatus: synthesized\nsource: 30_projects/demo/README.md\n---\n\n"
            "The current implementation preserves exact decision identity across the tested handoff. "
            "[raw report](../../30_projects/demo/raw-materials/report.txt)\n\n"
            "The note also links to [external documentation](https://example.com/spec) for background.\n",
            encoding="utf-8",
        )
        self.adapter = FakeAdapter(
            {
                "claims": [
                    {
                        "text": "The current implementation preserves exact decision identity across the tested handoff.",
                        "origin_relation": "explicit",
                        "origin_refs": ["paragraph[1]"],
                        "lineage_refs": ["paragraph[2]"],
                    }
                ]
            }
        )

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _load(self, output: Path) -> dict[str, Any]:
        return json.loads((output / "inventory.json").read_text(encoding="utf-8"))

    def test_recovers_only_explicit_source_refs_and_copies_local_bytes(self) -> None:
        out = self.base / "out"
        run_backlog_intake(self.mainframe, self.adapter, project_tag="demo", output_dir=out)
        inv = self._load(out)
        doc = inv["documents"][0]
        claim = doc["claims"][0]

        self.assertEqual(claim["source_semantics"], "UNASSESSED")
        self.assertNotIn("support_status", claim)
        self.assertEqual(len(claim["candidate_source_ref_ids"]), 3)
        self.assertEqual(len(claim["resolved_raw_source_ref_ids"]), 1)
        self.assertEqual(claim["lineage_status"], "resolved_raw_lineage")
        self.assertTrue(doc["source_lineage_edges"])

        refs = {r["raw_ref"]: r for r in doc["source_refs"]}
        local = refs["../../30_projects/demo/raw-materials/report.txt"]
        external = refs["https://example.com/spec"]
        self.assertEqual(local["resolution_status"], "resolved_local")
        self.assertEqual(external["resolution_status"], "external_unfetched")
        copied = out / local["packet_path"]
        self.assertEqual(copied.read_bytes(), b"RAW SOURCE BYTES\n")

        raw_id = claim["resolved_raw_source_ref_ids"][0]
        raw_entry = next(r for r in doc["source_refs"] if r["source_ref_id"] == raw_id)
        self.assertEqual(raw_entry["lineage_terminal_kind"], "raw_local")
        self.assertIn("packet_path", raw_entry)
        self.assertIn(b"Raw capture body.", (out / raw_entry["packet_path"]).read_bytes())

    def test_raw_path_convention_is_preserved_without_type_field(self) -> None:
        capture = self.capture_dir / "legacy.md"
        capture.write_text("Legacy raw capture body.\n", encoding="utf-8")
        (self.project_dir / "README.md").write_text(
            "---\ntype: note\nsource: 10_knowledge/demo/raw/legacy.md\n---\n\nProject synthesis.\n",
            encoding="utf-8",
        )
        out = self.base / "out-legacy-raw"
        run_backlog_intake(self.mainframe, self.adapter, project_tag="demo", output_dir=out)
        claim = self._load(out)["documents"][0]["claims"][0]
        self.assertEqual(len(claim["resolved_raw_source_ref_ids"]), 1)
        raw_id = claim["resolved_raw_source_ref_ids"][0]
        raw_entry = next(
            r for r in self._load(out)["documents"][0]["source_refs"]
            if r["source_ref_id"] == raw_id
        )
        self.assertEqual(raw_entry["raw_classification_basis"], "mainframe_raw_path_convention")

    def test_model_cannot_inject_source_reference(self) -> None:
        adapter = FakeAdapter(
            {
                "claims": [
                    {
                        "text": "The current implementation preserves exact decision identity across the tested handoff.",
                        "origin_relation": "explicit",
                        "origin_refs": ["paragraph[1]", "https://attacker.invalid/source"],
                        "lineage_refs": ["paragraph[999]"],
                    }
                ]
            }
        )
        out = self.base / "out-injection"
        run_backlog_intake(self.mainframe, adapter, project_tag="demo", output_dir=out)
        claim = self._load(out)["documents"][0]["claims"][0]
        self.assertEqual(len(claim["candidate_source_ref_ids"]), 2)
        self.assertTrue(claim["lineage_validation_errors"])
        self.assertFalse(
            any("attacker.invalid" in r["raw_ref"] for r in self._load(out)["documents"][0]["source_refs"])
        )

    def test_path_escape_is_blocked(self) -> None:
        outside = self.base / "outside.txt"
        outside.write_text("SECRET", encoding="utf-8")
        self.note.write_text(
            "---\ntype: note\nstatus: synthesized\n---\n\n"
            "The current implementation preserves exact decision identity across the tested handoff. "
            "[outside](../../../outside.txt)\n",
            encoding="utf-8",
        )
        adapter = FakeAdapter(
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
        out = self.base / "out-escape"
        run_backlog_intake(self.mainframe, adapter, project_tag="demo", output_dir=out)
        ref = self._load(out)["documents"][0]["source_refs"][0]
        self.assertEqual(ref["resolution_status"], "blocked_path_escape")
        self.assertNotIn("packet_path", ref)

    def test_static_symlink_escape_is_blocked(self) -> None:
        outside = self.base / "outside-source.txt"
        outside.write_text("SECRET", encoding="utf-8")
        link = self.raw / "linked.txt"
        try:
            link.symlink_to(outside)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        self.note.write_text(
            "---\ntype: note\nstatus: synthesized\n---\n\n"
            "The current implementation preserves exact decision identity across the tested handoff. "
            "[linked](../../30_projects/demo/raw-materials/linked.txt)\n",
            encoding="utf-8",
        )
        out = self.base / "out-symlink"
        run_backlog_intake(self.mainframe, self.adapter, project_tag="demo", output_dir=out)
        ref = self._load(out)["documents"][0]["source_refs"][0]
        self.assertEqual(ref["resolution_status"], "blocked_path_escape")

    def test_mainframe_is_not_mutated(self) -> None:
        before = snapshot_tree(self.mainframe)
        out = self.base / "out-nondestructive"
        run_backlog_intake(self.mainframe, self.adapter, project_tag="demo", output_dir=out)
        after = snapshot_tree(self.mainframe)
        self.assertEqual(before, after)

    def test_claim_and_inventory_identities_are_stable(self) -> None:
        out1 = self.base / "out1"
        out2 = self.base / "out2"
        run_backlog_intake(
            self.mainframe, self.adapter, project_tag="demo", output_dir=out1, run_id="one"
        )
        run_backlog_intake(
            self.mainframe, self.adapter, project_tag="demo", output_dir=out2, run_id="two"
        )
        inv1 = self._load(out1)
        inv2 = self._load(out2)
        self.assertEqual(inv1["inventory_id"], inv2["inventory_id"])
        self.assertEqual(
            inv1["documents"][0]["claims"][0]["claim_id"],
            inv2["documents"][0]["claims"][0]["claim_id"],
        )


if __name__ == "__main__":
    unittest.main()
