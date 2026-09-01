#!/usr/bin/env python3
"""Strict validator for the Contract A wire candidate RC2 research authority.

This file is public candidate authority, not the hidden/reference consumer used for
later independent-agreement comparison.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

SCHEMA_TOKEN = "contract-a-wire-candidate-rc2"
HASH_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
MEDIA_TYPES = {"text/plain; charset=utf-8", "text/markdown; charset=utf-8"}
DECOMPOSITION_STATES = {"not_decomposed", "failed", "unknown", "declared"}


class CandidateValidationError(ValueError):
    """Raised when candidate bytes do not satisfy the RC2 authority."""


def _sha256_text(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def _canonical_payload_bytes(value: dict[str, Any]) -> bytes:
    payload = dict(value)
    payload.pop("handoff_sha256", None)
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def compute_handoff_sha256(value: dict[str, Any]) -> str:
    """Return the RC2 whole-object binding defined in SPEC.md."""
    return "sha256:" + hashlib.sha256(_canonical_payload_bytes(value)).hexdigest()


def _object(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise CandidateValidationError(f"{path} must be an object")
    return value


def _array(value: Any, path: str) -> list[Any]:
    if not isinstance(value, list):
        raise CandidateValidationError(f"{path} must be an array")
    return value


def _exact_keys(value: dict[str, Any], allowed: set[str], required: set[str], path: str) -> None:
    extras = sorted(set(value) - allowed)
    missing = sorted(required - set(value))
    if extras:
        raise CandidateValidationError(f"{path} has forbidden/unknown fields: {', '.join(extras)}")
    if missing:
        raise CandidateValidationError(f"{path} is missing required fields: {', '.join(missing)}")


def _nonblank(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise CandidateValidationError(f"{path} must be a non-blank string")
    return value


def _hash(value: Any, path: str) -> str:
    if not isinstance(value, str) or not HASH_RE.fullmatch(value):
        raise CandidateValidationError(f"{path} must be lowercase sha256:<64 hex>")
    return value


def _validate_proposition(value: Any, path: str) -> dict[str, Any]:
    row = _object(value, path)
    keys = {"proposition_id", "text", "text_sha256"}
    _exact_keys(row, keys, keys, path)
    _nonblank(row["proposition_id"], f"{path}.proposition_id")
    text = _nonblank(row["text"], f"{path}.text")
    supplied = _hash(row["text_sha256"], f"{path}.text_sha256")
    expected = _sha256_text(text)
    if supplied != expected:
        raise CandidateValidationError(
            f"{path}.text_sha256 mismatch: supplied={supplied}, expected={expected}"
        )
    return row


def _validate_decomposition(value: Any, root_id: str) -> None:
    row = _object(value, "$.decomposition")
    state = row.get("state")
    if state not in DECOMPOSITION_STATES:
        raise CandidateValidationError(
            "$.decomposition.state must be one of declared, failed, not_decomposed, unknown"
        )
    if state != "declared":
        _exact_keys(row, {"state"}, {"state"}, "$.decomposition")
        return

    allowed = {"state", "decomposition_id", "operator", "children"}
    _exact_keys(row, allowed, allowed, "$.decomposition")
    _nonblank(row["decomposition_id"], "$.decomposition.decomposition_id")
    if row["operator"] != "all_of":
        raise CandidateValidationError("$.decomposition.operator must equal 'all_of'")
    children = _array(row["children"], "$.decomposition.children")
    if len(children) < 2:
        raise CandidateValidationError("declared all_of decomposition requires at least two children")

    ids: list[str] = []
    texts: list[str] = []
    sequences: list[int] = []
    for index, child_value in enumerate(children):
        path = f"$.decomposition.children[{index}]"
        child = _object(child_value, path)
        keys = {"proposition_id", "text", "text_sha256", "sequence"}
        _exact_keys(child, keys, keys, path)
        _validate_proposition(
            {
                "proposition_id": child["proposition_id"],
                "text": child["text"],
                "text_sha256": child["text_sha256"],
            },
            path,
        )
        sequence = child["sequence"]
        if isinstance(sequence, bool) or not isinstance(sequence, int) or sequence < 1:
            raise CandidateValidationError(f"{path}.sequence must be an integer >= 1")
        ids.append(child["proposition_id"])
        texts.append(child["text"])
        sequences.append(sequence)

    if root_id in ids:
        raise CandidateValidationError("a declared child proposition_id cannot equal the root proposition_id")
    if len(ids) != len(set(ids)):
        raise CandidateValidationError("declared child proposition_id values must be unique")
    if len(texts) != len(set(texts)):
        raise CandidateValidationError("declared child text values must be unique")
    if len(sequences) != len(set(sequences)):
        raise CandidateValidationError("declared child sequence values must be unique")
    expected_sequences = list(range(1, len(children) + 1))
    if sequences != expected_sequences:
        raise CandidateValidationError(
            f"declared children must be ordered by contiguous sequence 1..N; got {sequences}"
        )


def _validate_sources(value: Any) -> None:
    rows = _array(value, "$.sources")
    source_ids: list[str] = []
    for index, source_value in enumerate(rows):
        path = f"$.sources[{index}]"
        source = _object(source_value, path)
        keys = {"source_id", "media_type", "content", "content_sha256"}
        _exact_keys(source, keys, keys, path)
        source_id = _nonblank(source["source_id"], f"{path}.source_id")
        media_type = source["media_type"]
        if media_type not in MEDIA_TYPES:
            raise CandidateValidationError(
                f"{path}.media_type must be one of {sorted(MEDIA_TYPES)!r}"
            )
        content = source["content"]
        if not isinstance(content, str):
            raise CandidateValidationError(f"{path}.content must be a string")
        supplied = _hash(source["content_sha256"], f"{path}.content_sha256")
        expected = _sha256_text(content)
        if supplied != expected:
            raise CandidateValidationError(
                f"{path}.content_sha256 mismatch: supplied={supplied}, expected={expected}"
            )
        source_ids.append(source_id)
    if len(source_ids) != len(set(source_ids)):
        raise CandidateValidationError("source_id values must be unique")


def validate_candidate(value: Any) -> dict[str, Any]:
    """Validate one parsed RC2 candidate and return it unchanged."""
    root = _object(value, "$")
    top = {
        "schema",
        "handoff_id",
        "producer",
        "work",
        "root_proposition",
        "decomposition",
        "sources",
        "handoff_sha256",
    }
    _exact_keys(root, top, top, "$")
    if root["schema"] != SCHEMA_TOKEN:
        raise CandidateValidationError(f"$.schema must equal {SCHEMA_TOKEN!r}")
    _nonblank(root["handoff_id"], "$.handoff_id")

    producer = _object(root["producer"], "$.producer")
    producer_keys = {"producer_id", "producer_version"}
    _exact_keys(producer, producer_keys, producer_keys, "$.producer")
    _nonblank(producer["producer_id"], "$.producer.producer_id")
    _nonblank(producer["producer_version"], "$.producer.producer_version")

    work = _object(root["work"], "$.work")
    _exact_keys(work, {"work_id"}, {"work_id"}, "$.work")
    _nonblank(work["work_id"], "$.work.work_id")

    proposition = _validate_proposition(root["root_proposition"], "$.root_proposition")
    _validate_decomposition(root["decomposition"], proposition["proposition_id"])
    _validate_sources(root["sources"])

    supplied = _hash(root["handoff_sha256"], "$.handoff_sha256")
    expected = compute_handoff_sha256(root)
    if supplied != expected:
        raise CandidateValidationError(
            f"$.handoff_sha256 mismatch: supplied={supplied}, expected={expected}"
        )
    return root


def load_candidate(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            parse_constant=lambda token: (_ for _ in ()).throw(
                CandidateValidationError(f"non-finite JSON value is forbidden: {token}")
            ),
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CandidateValidationError(f"invalid UTF-8 JSON: {exc}") from exc
    return validate_candidate(value)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate.py <candidate.json>", file=sys.stderr)
        return 2
    path = Path(argv[1])
    try:
        load_candidate(path)
    except (OSError, CandidateValidationError, ValueError) as exc:
        print(f"INVALID {path}: {exc}", file=sys.stderr)
        return 1
    print(f"VALID {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
