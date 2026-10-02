"""Transport existing evidence without changing native filenames or bytes.

Scope: this experiment's receipts and emitted artifacts. No engine invocation.
Check: every archived member is re-read and matched to its source SHA-256.
Escape: fail before upload on missing receipt, unexpected member, or byte drift.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import tarfile
from pathlib import Path


def sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def package(root: Path, archive: Path) -> None:
    root = root.resolve(strict=True)
    archive = archive.resolve()
    if archive.is_relative_to(root) or archive.exists():
        raise ValueError("archive must be a new file outside the evidence root")
    if not (root / "receipt.json").is_file():
        raise ValueError("actual run receipt is required")
    files: set[Path] = set()
    for pattern in (
        "receipt.json",
        "result.json",
        "paired-comparisons.json",
        "first-failure.txt",
        "installed-inspect-*.json",
        "dependency-versions-*.json",
        "dependencies-*.txt",
    ):
        files.update(root.glob(pattern))
    for directory in ("commands", "worlds", "negative-controls", "dist-A", "dist-B"):
        files.update(path for path in (root / directory).rglob("*") if path.is_file())
    ordered = sorted(files, key=lambda path: path.relative_to(root).as_posix())
    if any(path.is_symlink() or not path.is_file() for path in ordered):
        raise ValueError("only regular emitted files may be transported")
    expected = {
        path.relative_to(root).as_posix(): {
            "bytes": path.stat().st_size,
            "sha256": sha256(path.read_bytes()),
        }
        for path in ordered
    }
    archive.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, "x:gz") as bundle:
        for path in ordered:
            bundle.add(path, arcname=path.relative_to(root).as_posix(), recursive=False)
    with tarfile.open(archive, "r:gz") as bundle:
        members = bundle.getmembers()
        if [member.name for member in members] != list(expected):
            raise ValueError("archive member set or ordering changed")
        for member in members:
            stream = bundle.extractfile(member)
            if not member.isfile() or stream is None:
                raise ValueError("archive member is not a regular file")
            data = stream.read()
            if {"bytes": len(data), "sha256": sha256(data)} != expected[member.name]:
                raise ValueError("archive member bytes changed")
    manifest = {
        "schema": "cal-convergence-evidence-transport-v1",
        "archive": archive.name,
        "archive_sha256": sha256(archive.read_bytes()),
        "native_paths_unchanged": True,
        "member_count": len(expected),
        "members": expected,
    }
    manifest_path = archive.with_suffix(archive.suffix + ".manifest.json")
    with manifest_path.open("x") as output:
        output.write(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps({key: value for key, value in manifest.items() if key != "members"})
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    arguments = parser.parse_args()
    package(arguments.run_root, arguments.archive)
