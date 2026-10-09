"""Synthetic development checks only; do not infer Docker or actor isolation."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path

from prepare_packet import PacketError, SCHEMA, prepare, read_manifest, verify


class PacketTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.root = self.base / "source"
        self.root.mkdir()
        (self.root / "spec").mkdir()
        (self.root / "spec" / "instructions.txt").write_bytes(b"Only allowed text\n")
        (self.root / "data.txt").write_bytes(b"allowed\n")
        (self.root / "private_gold.txt").write_bytes(b"SECRET-DO-NOT-COPY")
        self.manifest = self.base / "MANIFEST.json"
        self.out = self.base / "packet"
        self.write_manifest()

    def entries(self):
        return [{"path": p, "sha256": hashlib.sha256((self.root / p).read_bytes()).hexdigest()} for p in ("data.txt", "spec/instructions.txt")]

    def write_manifest(self, files=None):
        self.manifest.write_text(json.dumps({"schema": SCHEMA, "experiment_id": "synthetic-unit-1", "files": self.entries() if files is None else files}, sort_keys=True), encoding="utf-8")

    def test_pack_and_verify_withheld_not_exported(self):
        receipt = prepare(self.manifest, self.root, self.out)
        self.assertEqual(receipt["claim"], "STAGED_BYTES_ONLY_NOT_AN_EXECUTION_OR_ISOLATION_QUALIFICATION")
        self.assertEqual(verify(self.manifest, self.out)["files"], 2)
        self.assertFalse((self.out / "world" / "private_gold.txt").exists())
        self.assertEqual((self.root / "private_gold.txt").read_bytes(), b"SECRET-DO-NOT-COPY")

    def test_source_digest_mismatch(self):
        (self.root / "data.txt").write_bytes(b"changed")
        with self.assertRaisesRegex(PacketError, "digest mismatch"):
            prepare(self.manifest, self.root, self.out)
        self.assertFalse(self.out.exists())

    def test_missing_source(self):
        (self.root / "data.txt").unlink()
        with self.assertRaisesRegex(PacketError, "missing or unsafe"):
            prepare(self.manifest, self.root, self.out)

    def test_source_symlink_refused(self):
        (self.root / "data.txt").unlink()
        (self.root / "data.txt").symlink_to("private_gold.txt")
        with self.assertRaises(PacketError):
            prepare(self.manifest, self.root, self.out)

    def test_source_parent_symlink_refused(self):
        (self.root / "spec").rename(self.root / "real")
        (self.root / "spec").symlink_to("real")
        with self.assertRaises(PacketError):
            prepare(self.manifest, self.root, self.out)

    def test_source_hardlink_refused(self):
        os.link(self.root / "data.txt", self.root / "extra_link.txt")
        with self.assertRaisesRegex(PacketError, "hardlinked"):
            prepare(self.manifest, self.root, self.out)

    def test_reject_unsafe_paths(self):
        for rel in ("../private_gold.txt", "/etc/passwd", "a//b", "a/./b", "a/../b", ".git/config", "config/.env", "a\\b", "name\nmalicious", ".ssh/key", ".codex/auth"):
            with self.subTest(rel=rel):
                self.write_manifest([{"path": rel, "sha256": "0" * 64}])
                with self.assertRaises(PacketError):
                    read_manifest(self.manifest)

    def test_duplicate_path(self):
        files = [self.entries()[0]] * 2
        self.write_manifest(files)
        with self.assertRaisesRegex(PacketError, "duplicate allowed"):
            read_manifest(self.manifest)

    def test_unsorted_files(self):
        self.write_manifest(list(reversed(self.entries())))
        with self.assertRaisesRegex(PacketError, "sorted"):
            read_manifest(self.manifest)

    def test_duplicate_json_keys(self):
        self.manifest.write_text('{"schema":"cal-context-free-packet-rc0","schema":"x","experiment_id":"x","files":[]}')
        with self.assertRaisesRegex(PacketError, "duplicate JSON key"):
            read_manifest(self.manifest)

    def test_existing_output_refused(self):
        self.out.mkdir()
        with self.assertRaisesRegex(PacketError, "already exists"):
            prepare(self.manifest, self.root, self.out)

    def test_overlapping_paths_refused(self):
        with self.assertRaisesRegex(PacketError, "disjoint"):
            prepare(self.manifest, self.root, self.root / "packet")

    def test_modified_world_rejected(self):
        prepare(self.manifest, self.root, self.out)
        target = self.out / "world" / "data.txt"
        target.chmod(0o644)
        target.write_bytes(b"tampered")
        with self.assertRaisesRegex(PacketError, "digest mismatch"):
            verify(self.manifest, self.out)

    def test_added_world_file_rejected(self):
        prepare(self.manifest, self.root, self.out)
        world = self.out / "world"
        world.chmod(0o755)
        (world / "extra.txt").write_bytes(b"extra")
        with self.assertRaisesRegex(PacketError, "extra"):
            verify(self.manifest, self.out)

    def test_extra_empty_directory_rejected(self):
        prepare(self.manifest, self.root, self.out)
        world = self.out / "world"
        world.chmod(0o755)
        (world / "empty-extra").mkdir()
        with self.assertRaisesRegex(PacketError, "unexpected directory"):
            verify(self.manifest, self.out)

    def test_weak_copy_all_baseline_detected(self):
        # A deliberately weak packager would include a private sibling file.
        prepare(self.manifest, self.root, self.out)
        world = self.out / "world"
        world.chmod(0o755)
        (world / "private_gold.txt").write_bytes(b"SECRET-DO-NOT-COPY")
        with self.assertRaisesRegex(PacketError, "extra"):
            verify(self.manifest, self.out)

    def test_world_symlink_rejected(self):
        prepare(self.manifest, self.root, self.out)
        target = self.out / "world" / "data.txt"
        target.chmod(0o644)
        target.unlink()
        target.symlink_to(self.root / "private_gold.txt")
        with self.assertRaises(PacketError):
            verify(self.manifest, self.out)

    def test_manifest_mutation_breaks_receipt_identity(self):
        prepare(self.manifest, self.root, self.out)
        # Semantically identical JSON with different wire identity does not match receipt.
        self.manifest.write_text(self.manifest.read_text() + "\n")
        with self.assertRaisesRegex(PacketError, "receipt identity"):
            verify(self.manifest, self.out)

    def test_deterministic_prepare_receipts(self):
        r1 = prepare(self.manifest, self.root, self.out)
        out2 = self.base / "packet2"
        r2 = prepare(self.manifest, self.root, out2)
        self.assertEqual(r1, r2)
        self.assertEqual((self.out / "controller-receipts" / "PREPARE.json").read_bytes(), (out2 / "controller-receipts" / "PREPARE.json").read_bytes())


if __name__ == "__main__":
    unittest.main()
