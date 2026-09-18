"""Independent verifier for frozen CAL composition portable vectors RC0."""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any

PROFILE = "CAL-CANONICAL-JSON-BOUNDED-1"
RELATIONS = frozenset({"SUPPORTS", "REFUTES", "UNRESOLVED"})
BOUND_RECEIPT_FIELDS = (
    "module_id",
    "relation",
    "input_authority_ids",
    "semantic_input_sha256",
    "modifier_state_sha256",
    "query_sha256",
    "receipt_id",
)


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def sha256_value(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def expected_material(request: dict[str, Any]) -> dict[str, Any]:
    relation = request.get("relation")
    if relation not in RELATIONS:
        raise ValueError("unsupported relation")
    authority_ids = request.get("input_authority_ids")
    if not isinstance(authority_ids, list) or not authority_ids:
        raise ValueError("input_authority_ids must be a non-empty list")
    if any(not isinstance(item, str) or not item for item in authority_ids):
        raise ValueError("invalid authority identity")
    module_id = request.get("module_id")
    if not isinstance(module_id, str) or not module_id:
        raise ValueError("module_id must be non-empty")
    for key in ("semantic_input", "modifier_state", "query"):
        if not isinstance(request.get(key), dict):
            raise ValueError(f"{key} must be an object")
    return {
        "module_id": module_id,
        "relation": relation,
        "input_authority_ids": authority_ids,
        "semantic_input_sha256": sha256_value(request["semantic_input"]),
        "modifier_state_sha256": sha256_value(request["modifier_state"]),
        "query_sha256": sha256_value(request["query"]),
    }


def expected_receipt(request: dict[str, Any]) -> dict[str, Any]:
    material = expected_material(request)
    return {
        **material,
        "receipt_id": sha256_value(material),
    }


def verify_vector(vector: dict[str, Any]) -> bool:
    request = vector.get("request")
    receipt = vector.get("expected_receipt")
    if not isinstance(request, dict) or not isinstance(receipt, dict):
        return False
    try:
        expected = expected_receipt(request)
    except (TypeError, ValueError):
        return False
    return receipt == expected


def mutated_receipts(receipt: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    mutations: list[dict[str, Any]] = []
    replacements: dict[str, Any] = {
        "module_id": f"{receipt['module_id']}-mutated",
        "relation": "REFUTES" if receipt["relation"] == "SUPPORTS" else "SUPPORTS",
        "input_authority_ids": [*receipt["input_authority_ids"], "extra-authority"],
        "semantic_input_sha256": "0" * 64,
        "modifier_state_sha256": "1" * 64,
        "query_sha256": "2" * 64,
        "receipt_id": "3" * 64,
    }
    for field in BOUND_RECEIPT_FIELDS:
        mutated = deepcopy(receipt)
        mutated[field] = replacements[field]
        mutations.append(mutated)
    return tuple(mutations)


def verify_payload(payload: dict[str, Any]) -> None:
    if payload.get("schema") != "cal-composition-portable-vectors-rc0":
        raise ValueError("unexpected vector schema")
    canonicalization = payload.get("canonicalization")
    if not isinstance(canonicalization, dict):
        raise ValueError("missing canonicalization profile")
    expected_profile = {
        "profile": PROFILE,
        "encoding": "UTF-8",
        "object_member_order": "lexicographic_by_key",
        "insignificant_whitespace": "none",
        "array_order": "preserved",
        "separators": {"item": ",", "key_value": ":"},
        "unicode_note": (
            "vectors are ASCII-only; non-ASCII canonicalization is not qualified by RC0"
        ),
        "value_domain": ["object", "array", "string", "boolean", "integer"],
    }
    if canonicalization != expected_profile:
        raise ValueError("canonicalization profile mismatch")
    vectors = payload.get("vectors")
    if not isinstance(vectors, list) or len(vectors) != 6:
        raise ValueError("expected exactly six portable vectors")
    vector_ids = [vector.get("vector_id") for vector in vectors if isinstance(vector, dict)]
    if vector_ids != ["CPV01", "CPV02", "CPV03", "CPV04", "CPV05", "CPV06"]:
        raise ValueError("vector identity/order mismatch")
    for vector in vectors:
        if not isinstance(vector, dict) or not verify_vector(vector):
            raise ValueError(f"vector verification failed: {vector!r}")


__all__ = [
    "BOUND_RECEIPT_FIELDS",
    "canonical_bytes",
    "expected_material",
    "expected_receipt",
    "mutated_receipts",
    "sha256_value",
    "verify_payload",
    "verify_vector",
]
