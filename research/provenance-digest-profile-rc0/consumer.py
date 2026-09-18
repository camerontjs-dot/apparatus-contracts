#!/usr/bin/env python3
"""Independent bounded consumer for CAL provenance digest-profile vectors."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

PROFILE = "cal-provenance-canonical-json-bounded-1"


def reject_numbers(value: Any) -> None:
    if isinstance(value, bool) or value is None or isinstance(value, str):
        return
    if isinstance(value, list):
        for item in value:
            reject_numbers(item)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("object key is not a string")
            reject_numbers(item)
        return
    raise ValueError(f"numeric or unsupported JSON value: {type(value).__name__}")


def canonical_bytes(value: Any) -> bytes:
    reject_numbers(value)
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def preimage(kind: str, value: dict[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(value)
    if kind == "attestation":
        out.pop("attestation_id", None)
        out.pop("attestation_sha256", None)
    elif kind == "manifest":
        out.pop("manifest_id", None)
        out.pop("manifest_sha256", None)
    else:
        raise ValueError(f"unsupported vector kind: {kind}")
    return out


def derived_id(kind: str, digest: str) -> str:
    if kind == "attestation":
        return f"attestation:sha256:{digest}"
    if kind == "manifest":
        return f"run-manifest:sha256:{digest}"
    raise ValueError(kind)


def main() -> int:
    vectors_path = Path(__file__).with_name("DIGEST-VECTORS.json")
    doc = json.loads(vectors_path.read_text(encoding="utf-8"))
    assert doc["profile"] == PROFILE

    results = []
    for row in doc["vectors"]:
        kind = row["kind"]
        base = preimage(kind, row["unsealed"])
        actual_bytes = canonical_bytes(base)
        actual_digest = sha256(actual_bytes)

        assert "sha256:" + actual_digest == row["expected_digest_sha256"]
        assert derived_id(kind, actual_digest) == row["expected_id"]

        no_lf = actual_bytes[:-1]
        assert actual_bytes.endswith(b"\n")
        assert sha256(no_lf) != actual_digest

        sealed = copy.deepcopy(base)
        if kind == "attestation":
            sealed["attestation_id"] = row["expected_id"]
            sealed["attestation_sha256"] = row["expected_digest_sha256"]
        else:
            sealed["manifest_id"] = row["expected_id"]
            sealed["manifest_sha256"] = row["expected_digest_sha256"]
        assert sha256(canonical_bytes(sealed)) != actual_digest

        ascii_bytes = (
            json.dumps(base, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
            + "\n"
        ).encode("utf-8")
        assert ascii_bytes != actual_bytes
        assert sha256(ascii_bytes) != actual_digest

        mutated = copy.deepcopy(base)
        if kind == "attestation":
            mutated["run"]["work_id"] += "-mutated"
        else:
            mutated["work_id"] += "-mutated"
        assert sha256(canonical_bytes(mutated)) != actual_digest

        results.append({
            "name": row["name"],
            "kind": kind,
            "digest": "sha256:" + actual_digest,
            "id": derived_id(kind, actual_digest),
            "mutations_rejected": 4,
        })

    print(json.dumps({"profile": PROFILE, "vectors": results}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
