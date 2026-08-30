from __future__ import annotations
import json
from typing import Any
from contract_d_core import ContractDError, canonical_json_bytes, validate_decision

def _reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise ContractDError("duplicate_json_key", "$", key)
        out[key] = value
    return out

def _reject_constant(value: str) -> None:
    raise ContractDError("non_finite_number", "$", value)

def parse_json_bytes(data: bytes) -> dict[str, Any]:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ContractDError("invalid_utf8", "$") from exc
    try:
        value = json.loads(text, object_pairs_hook=_reject_duplicate_pairs, parse_constant=_reject_constant)
    except ContractDError:
        raise
    except Exception as exc:
        raise ContractDError("invalid_json", "$") from exc
    validate_decision(value)
    return value

def require_canonical_bytes(data: bytes) -> dict[str, Any]:
    value = parse_json_bytes(data)
    if data != canonical_json_bytes(value):
        raise ContractDError("noncanonical_json", "$")
    return value

def validate(value: Any) -> dict[str, Any]:
    return validate_decision(value)
