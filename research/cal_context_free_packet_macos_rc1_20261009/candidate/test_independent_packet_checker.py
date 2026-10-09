"""macOS successor controls, public synthetic data, no model/host integrations.

Independent checker imports no target verifier; still authored by same controller.
Preserve first failure in separate original RC0 evidence, do not rewrite it.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from independent_packet_checker import check, CheckFailure
from prepare_packet import prepare, read_manifest, PacketError, SCHEMA


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class PacketMacControls(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.source = self.base / "source"
        (self.source / "data").mkdir(parents=True)
        (self.source / "instructions").mkdir()
        (self.source / "data" / "marker.txt").write_bytes(b"PUBLIC-ALLOW-MARKER\n")
        (self.source / "instructions" / "request.txt").write_bytes(b"Read marker and write a short answer.\n")
        (self.source / "private_gold.txt").write_bytes(b"SYNTHETIC-HIDDEN-GOLD\n")
        self.manifest = self.base / "MANIFEST.json"
        self.packet = self.base / "packet"
        self.entries = [
            {"path": "data/marker.txt", "sha256": sha(b"PUBLIC-ALLOW-MARKER\n")},
            {"path": "instructions/request.txt", "sha256": sha(b"Read marker and write a short answer.\n")},
        ]
        self.write_manifest(self.entries)

    def write_manifest(self, entries):
        obj = {"schema": SCHEMA, "experiment_id": "macos-control-rc1",
               "files": sorted(entries, key=lambda x: x["path"])}
        self.manifest.write_bytes((json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n").encode())

    def fresh(self):
        prepare(self.manifest, self.source, self.packet)

    def must_reject(self, reason):
        with self.assertRaises(CheckFailure) as caught:
            check(self.manifest, self.source, self.packet)
        self.assertEqual(caught.exception.reason, reason)

    def test_01_world_and_input_identity_positive(self):
        self.fresh()
        result = check(self.manifest, self.source, self.packet)
        self.assertEqual(result["status"], "STAGED_BYTES_CODE_ISOLATED_CHECK")
        self.assertEqual(result["paths"], [e["path"] for e in self.entries])
        self.assertTrue((self.source / "private_gold.txt").is_file())
        self.assertFalse((self.packet / "world" / "private_gold.txt").exists())

    def test_02_true_copy_all_weak_baseline_rejected_for_extra_file(self):
        self.fresh()
        weak = self.base / "weak-copier-output"
        weak.mkdir()
        shutil.copytree(self.source, weak / "world")
        (weak / "scratch").mkdir()
        shutil.copytree(self.packet / "controller-receipts", weak / "controller-receipts")
        self.assertEqual((weak / "world" / "private_gold.txt").read_bytes(), b"SYNTHETIC-HIDDEN-GOLD\n")
        with self.assertRaises(CheckFailure) as caught:
            check(self.manifest, self.source, weak)
        self.assertEqual(caught.exception.reason, "EXTRA_FILE")

    def test_03_unexpected_world_file_rejected(self):
        self.fresh()
        world = self.packet / "world"
        world.chmod(0o755)
        (world / "extra.txt").write_bytes(b"unapproved\n")
        self.must_reject("EXTRA_FILE")

    def test_04_mutated_allowed_bytes_rejected(self):
        self.fresh()
        file = self.packet / "world" / "data" / "marker.txt"
        file.chmod(0o644)
        file.write_bytes(b"TAMPERED\n")
        self.must_reject("DIGEST_MISMATCH")

    def test_05_symlink_to_outside_world_rejected_after_real_insertion(self):
        self.fresh()
        world = self.packet / "world"
        (world / "data").chmod(0o755)
        file = world / "data" / "marker.txt"
        file.unlink()
        file.symlink_to(self.source / "private_gold.txt")
        self.assertTrue(file.is_symlink())
        self.must_reject("WORLD_SYMLINK")

    def test_06_fifo_nonregular_rejected(self):
        self.fresh()
        world = self.packet / "world"
        world.chmod(0o755)
        fifo = world / "pipe"
        os.mkfifo(fifo)
        self.assertTrue(fifo.exists())
        self.must_reject("WORLD_NONREGULAR")

    def test_07_hardlinked_allowed_file_rejected(self):
        self.fresh()
        data = self.packet / "world" / "data"
        data.chmod(0o755)
        target = data / "marker.txt"
        target.unlink()
        os.link(self.source / "private_gold.txt", target)
        self.assertGreater(target.stat().st_nlink, 1)
        self.must_reject("HARDLINK")

    def test_08_unexpected_empty_directory_rejected(self):
        self.fresh()
        world = self.packet / "world"
        world.chmod(0o755)
        (world / "invisible-empty").mkdir()
        self.must_reject("EXTRA_DIRECTORY")

    def test_09_scratch_not_empty_rejected(self):
        self.fresh()
        (self.packet / "scratch" / "old_answer.txt").write_bytes(b"stale")
        self.must_reject("SCRATCH_NOT_EMPTY")

    def test_10_modified_receipt_rejected(self):
        self.fresh()
        receipt = self.packet / "controller-receipts" / "PREPARE.json"
        obj = json.loads(receipt.read_text())
        obj["manifest_sha256"] = "0" * 64
        receipt.write_text(json.dumps(obj))
        self.must_reject("RECEIPT_IDENTITY")

    def test_11_casefold_ambient_stores_blocked(self):
        for denied in (".GIT/config", ".Env", ".SsH/id_key", ".CODEX/auth", ".NeTrC", ".CLAUDE/preferences"):
            with self.subTest(path=denied):
                self.write_manifest([{"path": denied, "sha256": "0" * 64}])
                with self.assertRaisesRegex(PacketError, "unsafe relative"):
                    read_manifest(self.manifest)

    def test_12_casefold_file_alias_blocked_before_io(self):
        self.write_manifest([
            {"path": "data/MARKER.TXT", "sha256": "0" * 64},
            {"path": "data/marker.txt", "sha256": "0" * 64}
        ])
        with self.assertRaisesRegex(PacketError, "casefold path alias"):
            read_manifest(self.manifest)

    def test_13_casefold_parent_alias_blocked_before_io(self):
        self.write_manifest([
            {"path": "Data/alpha.txt", "sha256": "0" * 64},
            {"path": "data/zeta.txt", "sha256": "0" * 64}
        ])
        with self.assertRaisesRegex(PacketError, "casefold path alias"):
            read_manifest(self.manifest)

    def test_14_prohibited_manifest_symlink_refused(self):
        self.manifest.unlink()
        self.manifest.symlink_to(self.source / "data" / "marker.txt")
        with self.assertRaises(PacketError):
            read_manifest(self.manifest)

    def test_15_checker_has_no_target_verifier_import(self):
        source = Path(__file__).with_name("independent_packet_checker.py").read_text()
        self.assertNotIn("from prepare_packet", source)
        self.assertNotIn("import prepare_packet", source)
        self.assertNotIn("verify(", source)


if __name__ == "__main__":
    unittest.main()
