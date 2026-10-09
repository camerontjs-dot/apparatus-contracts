#!/usr/bin/env python3
"""Independent-from-target-code packet checker; controller only.

This checker does NOT import the candidate prepare/verify module. It checks
a controller-frozen manifest, copied bytes, identities, and unexpected entries.
It is code-isolated, not independently authored, and is not an agent sandbox.
"""
from __future__ import annotations

import hashlib
import json
import os
import stat
from pathlib import Path

EXPECTED_CLAIM = "STAGED_BYTES_ONLY_NOT_AN_EXECUTION_OR_ISOLATION_QUALIFICATION"


class CheckFailure(Exception):
    def __init__(self, reason: str, detail: str = ""):
        super().__init__(f"{reason}: {detail}")
        self.reason = reason


def _unique(pairs):
    obj = {}
    for key, val in pairs:
        if key in obj:
            raise CheckFailure("DUPLICATE_KEY", key)
        obj[key] = val
    return obj


def _object(raw: bytes):
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=_unique)
    except (UnicodeError, ValueError) as error:
        raise CheckFailure("INVALID_JSON", str(error)) from error


def _actual_regular(path: Path):
    try:
        st = path.lstat()
    except FileNotFoundError as error:
        raise CheckFailure("MISSING", str(path.name)) from error
    if not stat.S_ISREG(st.st_mode):
        raise CheckFailure("NONREGULAR", path.name)
    if st.st_nlink != 1:
        raise CheckFailure("HARDLINK", path.name)
    return st


def check(manifest_path: Path, source: Path, packet: Path) -> dict:
    """Check candidate output using only controller-frozen inputs and stdlib."""
    manifest_path, source, packet = map(Path, (manifest_path, source, packet))
    manifest_raw = manifest_path.read_bytes()
    manifest = _object(manifest_raw)
    if not isinstance(manifest, dict) or set(manifest) != {"schema", "experiment_id", "files"}:
        raise CheckFailure("MANIFEST_SHAPE")
    if manifest["schema"] != "cal-context-free-packet-rc0":
        raise CheckFailure("MANIFEST_SCHEMA")
    entries = manifest["files"]
    if not isinstance(entries, list) or not entries:
        raise CheckFailure("MANIFEST_ENTRIES")
    if any(not isinstance(e, dict) or set(e) != {"path", "sha256"} for e in entries):
        raise CheckFailure("MANIFEST_ENTRY_SHAPE")
    paths = [e["path"] for e in entries]
    if not all(isinstance(p, str) and p and not p.startswith("/") and
               all(x not in ("", ".", "..") for x in p.split("/")) for p in paths):
        raise CheckFailure("MANIFEST_PATH")
    if paths != sorted(set(paths)):
        raise CheckFailure("MANIFEST_ORDER_OR_DUPLICATE")
    expected = {e["path"]: e["sha256"] for e in entries}
    dirs = {"/".join(p.split("/")[:i]) for p in paths for i in range(1, len(p.split("/")))}

    if packet.is_symlink() or not packet.is_dir():
        raise CheckFailure("PACKET_ROOT")
    root_names = {x.name for x in packet.iterdir()}
    if root_names != {"world", "scratch", "controller-receipts"}:
        raise CheckFailure("PACKET_LAYOUT", repr(sorted(root_names)))
    world = packet / "world"
    scratch = packet / "scratch"
    receipts = packet / "controller-receipts"
    if world.is_symlink() or scratch.is_symlink() or receipts.is_symlink():
        raise CheckFailure("PACKET_SYMLINK")
    if not all(x.is_dir() for x in (world, scratch, receipts)):
        raise CheckFailure("PACKET_DIRECTORY")
    if list(scratch.iterdir()):
        raise CheckFailure("SCRATCH_NOT_EMPTY")
    if {x.name for x in receipts.iterdir()} != {"PREPARE.json"}:
        raise CheckFailure("RECEIPT_LAYOUT")
    receipt_file = receipts / "PREPARE.json"
    _actual_regular(receipt_file)
    receipt = _object(receipt_file.read_bytes())
    if receipt.get("manifest_sha256") != hashlib.sha256(manifest_raw).hexdigest():
        raise CheckFailure("RECEIPT_IDENTITY")
    if receipt.get("claim") != EXPECTED_CLAIM or receipt.get("experiment_id") != manifest["experiment_id"]:
        raise CheckFailure("RECEIPT_CLAIM")

    found = {}

    def visit(directory: Path, prefix: str):
        with os.scandir(directory) as handle:
            children = sorted(handle, key=lambda entry: entry.name)
        for child in children:
            rel = f"{prefix}/{child.name}" if prefix else child.name
            full = Path(child.path)
            mode = child.stat(follow_symlinks=False).st_mode
            if stat.S_ISLNK(mode):
                raise CheckFailure("WORLD_SYMLINK", rel)
            if stat.S_ISDIR(mode):
                if rel not in dirs:
                    raise CheckFailure("EXTRA_DIRECTORY", rel)
                visit(full, rel)
            elif stat.S_ISREG(mode):
                if rel not in expected:
                    raise CheckFailure("EXTRA_FILE", rel)
                st = _actual_regular(full)
                source_file = source / rel
                src_st = _actual_regular(source_file)
                data = full.read_bytes()
                digest = hashlib.sha256(data).hexdigest()
                if digest != expected[rel] or hashlib.sha256(source_file.read_bytes()).hexdigest() != expected[rel]:
                    raise CheckFailure("DIGEST_MISMATCH", rel)
                if st.st_dev == src_st.st_dev and st.st_ino == src_st.st_ino:
                    raise CheckFailure("SOURCE_HARDLINK", rel)
                found[rel] = {"sha256": digest, "bytes": len(data)}
            else:
                raise CheckFailure("WORLD_NONREGULAR", rel)

    visit(world, "")
    if set(found) != set(expected):
        raise CheckFailure("MISSING_WORLD_FILES", repr(sorted(set(expected) - set(found))))
    return {"status": "STAGED_BYTES_CODE_ISOLATED_CHECK", "file_count": len(found),
            "manifest_sha256": hashlib.sha256(manifest_raw).hexdigest(),
            "paths": sorted(found)}
