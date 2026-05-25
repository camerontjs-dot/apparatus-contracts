"""SHA-256 helpers for canonical-vocabulary drift detection and SHA256SUMS verification.

All hashes are computed with the standard library ``hashlib.sha256`` and reported
as lowercase hex digests, optionally prefixed with ``sha256:`` to match the
contract's manifest field conventions.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Iterable, NamedTuple

_CHUNK_SIZE = 65536


class Sha256SumEntry(NamedTuple):
    """One entry from a SHA256SUMS file."""

    digest: str
    relative_path: str


def hash_file(path: Path) -> str:
    """Return the lowercase hex SHA-256 digest of ``path``'s bytes."""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            chunk = fh.read(_CHUNK_SIZE)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def hash_bytes(payload: bytes) -> str:
    """Return the lowercase hex SHA-256 digest of an in-memory bytes payload."""
    return hashlib.sha256(payload).hexdigest()


def parse_sha256sums(path: Path) -> list[Sha256SumEntry]:
    """Parse a ``SHA256SUMS`` file into entries.

    The format is the GNU ``sha256sum`` convention: one entry per line,
    ``<hexdigest><space><space><relative-path>``. Lines that are blank or start
    with ``#`` are skipped.
    """
    entries: list[Sha256SumEntry] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        # Accept either "<digest>  <path>" (two spaces, GNU) or "<digest> <path>".
        if "  " in line:
            digest, _, relpath = line.partition("  ")
        else:
            digest, _, relpath = line.partition(" ")
        digest = digest.strip()
        relpath = relpath.strip()
        if not digest or not relpath:
            continue
        # Drop the optional leading "*" used by sha256sum binary mode.
        if relpath.startswith("*"):
            relpath = relpath[1:]
        entries.append(Sha256SumEntry(digest=digest, relative_path=relpath))
    return entries


class Sha256SumsMismatch(NamedTuple):
    """One file whose recomputed hash did not match its SHA256SUMS entry."""

    relative_path: str
    expected: str
    actual: str | None  # None means the file is missing on disk.


def verify_sha256sums(
    sums_path: Path,
    root: Path,
    *,
    exclude: Iterable[str] = ("SHA256SUMS",),
) -> list[Sha256SumsMismatch]:
    """Recompute hashes of files listed in ``sums_path`` and return mismatches.

    Files in ``exclude`` are skipped (by default the SHA256SUMS file itself is
    not listed in its own contents). Missing files are reported with
    ``actual=None``.
    """
    excluded = set(exclude)
    mismatches: list[Sha256SumsMismatch] = []
    for entry in parse_sha256sums(sums_path):
        if entry.relative_path in excluded:
            continue
        file_path = root / entry.relative_path
        if not file_path.exists():
            mismatches.append(
                Sha256SumsMismatch(
                    relative_path=entry.relative_path,
                    expected=entry.digest,
                    actual=None,
                )
            )
            continue
        actual = hash_file(file_path)
        if actual.lower() != entry.digest.lower():
            mismatches.append(
                Sha256SumsMismatch(
                    relative_path=entry.relative_path,
                    expected=entry.digest,
                    actual=actual,
                )
            )
    return mismatches
