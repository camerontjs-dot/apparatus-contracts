#!/usr/bin/env python3
"""Research-only offline builder for an exact CAL context-free file world.

This copies allowlisted bytes from a controller-owned snapshot into a fresh directory.
It does NOT launch an agent, container, or sandbox, or establish confinement.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import tempfile
import unicodedata
from pathlib import Path

SCHEMA = "cal-context-free-packet-rc0"
MAX_FILES = 256
MAX_FILE_BYTES = 20 * 1024 * 1024
MAX_TOTAL_BYTES = 100 * 1024 * 1024
SHA_RE = re.compile(r"^[a-f0-9]{64}$")
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,95}$")
# Refuse ambient tool/config stores even if accidentally placed on the allowlist.
DENIED_PARTS = frozenset({".git", ".ssh", ".aws", ".codex", ".claude", ".config", "__pycache__"})
DENIED_LEAVES = frozenset({".env", ".gitmodules", ".netrc", "id_rsa", "id_ed25519"})


class PacketError(ValueError):
    """An explicit preparation or verification failure."""


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def no_duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for k, v in pairs:
        if k in result:
            raise PacketError(f"duplicate JSON key: {k}")
        result[k] = v
    return result


def read_manifest(path: Path) -> tuple[dict, bytes]:
    if path.is_symlink() or not path.is_file():
        raise PacketError("manifest must be a regular file, not a symlink")
    raw = path.read_bytes()
    try:
        obj = json.loads(raw, object_pairs_hook=no_duplicate_keys)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PacketError("invalid JSON manifest") from exc
    if not isinstance(obj, dict) or set(obj) != {"schema", "experiment_id", "files"}:
        raise PacketError("manifest must have exactly schema, experiment_id, files")
    if obj["schema"] != SCHEMA or not isinstance(obj["experiment_id"], str) or not ID_RE.fullmatch(obj["experiment_id"]):
        raise PacketError("bad schema or experiment_id")
    files = obj["files"]
    if not isinstance(files, list) or not 1 <= len(files) <= MAX_FILES:
        raise PacketError("file count outside bound")
    seen = set()
    # Case-insensitive filesystems must not silently alias manifest paths.
    portable_names = {}
    for entry in files:
        if not isinstance(entry, dict) or set(entry) != {"path", "sha256"}:
            raise PacketError("each entry must have exactly path and sha256")
        rel = entry["path"]
        if not isinstance(rel, str) or not valid_relative(rel):
            raise PacketError(f"unsafe relative path: {rel!r}")
        if rel in seen:
            raise PacketError(f"duplicate allowed path: {rel}")
        seen.add(rel)
        parts = rel.split("/")
        for n in range(1, len(parts) + 1):
            prefix = tuple(parts[:n])
            folded = tuple(x.casefold() for x in prefix)
            if folded in portable_names and portable_names[folded] != prefix:
                raise PacketError(f"casefold path alias: {rel}")
            portable_names[folded] = prefix
        if not isinstance(entry["sha256"], str) or not SHA_RE.fullmatch(entry["sha256"]):
            raise PacketError(f"invalid SHA-256 for {rel}")
    if files != sorted(files, key=lambda x: x["path"]):
        raise PacketError("files must be sorted by path before freezing")
    return obj, hashlib.sha256(raw).digest()


def valid_relative(rel: str) -> bool:
    if len(rel) > 500 or not rel or "\\" in rel or "\x00" in rel or rel.startswith("/"):
        return False
    if unicodedata.normalize("NFC", rel) != rel or any(ord(ch) < 32 or ord(ch) == 127 for ch in rel):
        return False
    parts = rel.split("/")
    return not any(part in {"", ".", ".."} or part.casefold() in DENIED_PARTS for part in parts) and parts[-1].casefold() not in DENIED_LEAVES


def confined_read(root: Path, rel: str) -> bytes:
    """Read a relative regular file without following symlinks at any path step.

    Controller-owned source is required; this is not an adversarial race-proof
    filesystem snapshot across a hostile concurrent writer.
    """
    flags = os.O_RDONLY | os.O_NOFOLLOW
    dirflags = flags | os.O_DIRECTORY
    parts = rel.split("/")
    fd = os.open(root, dirflags)
    try:
        for part in parts[:-1]:
            nxt = os.open(part, dirflags, dir_fd=fd)
            os.close(fd)
            fd = nxt
        child = os.open(parts[-1], flags, dir_fd=fd)
        try:
            before = os.fstat(child)
            if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or before.st_size > MAX_FILE_BYTES:
                raise PacketError(f"non-regular/hardlinked/oversized file: {rel}")
            chunks = []
            remaining = MAX_FILE_BYTES + 1
            while remaining:
                piece = os.read(child, min(1024 * 1024, remaining))
                if not piece:
                    break
                remaining -= len(piece)
                chunks.append(piece)
            data = b"".join(chunks)
            after = os.fstat(child)
            if len(data) > MAX_FILE_BYTES or before.st_size != len(data) or (before.st_dev, before.st_ino, before.st_mtime_ns, before.st_size) != (after.st_dev, after.st_ino, after.st_mtime_ns, after.st_size):
                raise PacketError(f"source changed or exceeded bound: {rel}")
            return data
        finally:
            os.close(child)
    finally:
        os.close(fd)


def collect_files(world: Path, expected: set[str]) -> dict[str, bytes]:
    if world.is_symlink() or not world.is_dir():
        raise PacketError("world is absent or is symlink")
    found = {}
    expected_dirs = {"/".join(rel.split("/")[:i]) for rel in expected for i in range(1, len(rel.split("/")))}
    for dirpath, dirs, files in os.walk(world, topdown=True, followlinks=False):
        for name in dirs:
            subdir = Path(dirpath) / name
            if subdir.is_symlink() or subdir.relative_to(world).as_posix() not in expected_dirs:
                raise PacketError("unexpected directory or symlink in world")
        for name in files:
            p = Path(dirpath) / name
            if p.is_symlink() or not p.is_file():
                raise PacketError("unexpected nonregular world entry")
            rel = p.relative_to(world).as_posix()
            if not valid_relative(rel):
                raise PacketError("unsafe world file path")
            found[rel] = confined_read(world, rel)
    return found


def prepare(manifest_file: Path, source_root: Path, output: Path) -> dict:
    manifest, raw_sha = read_manifest(manifest_file)
    if source_root.is_symlink() or not source_root.is_dir():
        raise PacketError("source root must be a real directory")
    if output.exists() or output.is_symlink():
        raise PacketError("output already exists; refusing overwrite")
    # Don't let generated files enter the input tree, even if not explicitly copied.
    src = source_root.resolve(strict=True)
    dest = output.resolve(strict=False)
    if src == dest or src in dest.parents or dest in src.parents:
        raise PacketError("source and output paths must be disjoint")
    if not output.parent.is_dir() or output.parent.is_symlink():
        raise PacketError("output parent must already exist and not be a symlink")
    files = {}
    total = 0
    for entry in manifest["files"]:
        rel = entry["path"]
        try:
            data = confined_read(src, rel)
        except (FileNotFoundError, OSError) as exc:
            raise PacketError(f"missing or unsafe source path: {rel}") from exc
        digest = hashlib.sha256(data).hexdigest()
        if digest != entry["sha256"]:
            raise PacketError(f"source digest mismatch: {rel}")
        total += len(data)
        if total > MAX_TOTAL_BYTES:
            raise PacketError("combined byte bound exceeded")
        files[rel] = data
    stage = Path(tempfile.mkdtemp(prefix=".cal-world-", dir=output.parent))
    try:
        world = stage / "world"
        world.mkdir(mode=0o700)
        for rel, data in files.items():
            target = world / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as stream:
                stream.write(data)
            target.chmod(0o444)
        (stage / "scratch").mkdir(mode=0o700)
        receipts = stage / "controller-receipts"
        receipts.mkdir(mode=0o700)
        receipt = {
            "schema": SCHEMA,
            "claim": "STAGED_BYTES_ONLY_NOT_AN_EXECUTION_OR_ISOLATION_QUALIFICATION",
            "experiment_id": manifest["experiment_id"],
            "manifest_sha256": raw_sha.hex(),
            "allowlisted": [{"path": rel, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)} for rel, data in files.items()],
            "total_bytes": total,
            "not_assessed": ["model_context", "agent_tools", "host_mcp", "network", "sandbox_confinement", "independent_evaluation"],
        }
        (receipts / "PREPARE.json").write_bytes(canonical(receipt))
        for dirpath, dirs, _files in os.walk(world):
            for name in dirs:
                (Path(dirpath) / name).chmod(0o555)
        world.chmod(0o555)
        stage.rename(output)
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise
    return receipt


def verify(manifest_file: Path, packet_dir: Path) -> dict:
    manifest, raw_sha = read_manifest(manifest_file)
    rp = packet_dir / "controller-receipts" / "PREPARE.json"
    if rp.is_symlink() or not rp.is_file():
        raise PacketError("missing controller receipt")
    receipt, _ = read_receipt(rp)
    if receipt.get("schema") != SCHEMA or receipt.get("experiment_id") != manifest["experiment_id"] or receipt.get("manifest_sha256") != raw_sha.hex() or receipt.get("claim") != "STAGED_BYTES_ONLY_NOT_AN_EXECUTION_OR_ISOLATION_QUALIFICATION":
        raise PacketError("receipt identity or claim mismatch")
    expected = {x["path"]: x["sha256"] for x in manifest["files"]}
    observed = collect_files(packet_dir / "world", set(expected))
    if set(expected) != set(observed):
        raise PacketError("world has missing or extra files")
    sizes = []
    for rel, data in observed.items():
        digest = hashlib.sha256(data).hexdigest()
        if digest != expected[rel]:
            raise PacketError(f"world digest mismatch: {rel}")
        sizes.append(len(data))
    if receipt.get("total_bytes") != sum(sizes) or receipt.get("allowlisted") != [{"path": p, "sha256": expected[p], "bytes": len(observed[p])} for p in sorted(expected)]:
        raise PacketError("receipt contents do not match staged bytes")
    return {"verified": True, "claim": receipt["claim"], "files": len(observed)}


def read_receipt(path: Path) -> tuple[dict, bytes]:
    raw = path.read_bytes()
    try:
        obj = json.loads(raw, object_pairs_hook=no_duplicate_keys)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PacketError("bad receipt") from exc
    if not isinstance(obj, dict):
        raise PacketError("bad receipt shape")
    return obj, raw


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    actions = ap.add_subparsers(dest="action", required=True)
    pack = actions.add_parser("prepare")
    pack.add_argument("--manifest", type=Path, required=True)
    pack.add_argument("--source-root", type=Path, required=True)
    pack.add_argument("--output", type=Path, required=True)
    check = actions.add_parser("verify")
    check.add_argument("--manifest", type=Path, required=True)
    check.add_argument("--packet", type=Path, required=True)
    args = ap.parse_args()
    try:
        if args.action == "prepare":
            result = prepare(args.manifest, args.source_root, args.output)
        else:
            result = verify(args.manifest, args.packet)
    except (PacketError, OSError) as exc:
        ap.exit(2, f"PACKET_ERROR: {exc}\n")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
