from __future__ import annotations

import json
import math
from typing import Any

from contract_d_core import (
    ContractDError,
    SAFE_INTEGER_MAX,
    SAFE_INTEGER_MIN,
    canonical_json_bytes,
    validate_decision,
)


def _reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        if key in out:
            raise ContractDError("duplicate_json_key", "$", key)
        out[key] = value
    return out


def _reject_constant(value: str) -> None:
    raise ContractDError("non_finite_number", "$", value)


def _parse_integer_token(token: str) -> int | float:
    """Parse JSON integer syntax without precision loss.

    Safe-range integers remain host ints. Outside that range, accept only values
    exactly representable as IEEE-754 binary64 and materialize them as floats.
    This permits JCS canonical output of accepted binary64 values such as 1e20
    to round-trip while rejecting precision-losing integer tokens such as
    9007199254740993.
    """
    value = int(token)
    if SAFE_INTEGER_MIN <= value <= SAFE_INTEGER_MAX:
        return value
    try:
        binary64 = float(value)
    except OverflowError as exc:
        raise ContractDError("non_interoperable_integer", "$", token) from exc
    if not math.isfinite(binary64) or int(binary64) != value:
        raise ContractDError("non_interoperable_integer", "$", token)
    return binary64


def parse_json_bytes(data: bytes) -> dict[str, Any]:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ContractDError("invalid_utf8", "$") from exc
    try:
        value = json.loads(
            text,
            object_pairs_hook=_reject_duplicate_pairs,
            parse_constant=_reject_constant,
            parse_int=_parse_integer_token,
        )
    except ContractDError:
        raise
    except RecursionError as exc:
        raise ContractDError("resource_limit", "$", "json_parse_recursion") from exc
    except Exception as exc:
        raise ContractDError("invalid_json", "$") from exc
    validate_decision(value)
    return value


def require_canonical_bytes(data: bytes) -> dict[str, Any]:
    value = parse_json_bytes(data)
    try:
        expected = canonical_json_bytes(value)
    except ContractDError:
        raise
    except Exception as exc:
        raise ContractDError("canonicalization_failure", "$", type(exc).__name__) from exc
    if data != expected:
        raise ContractDError("noncanonical_json", "$")
    return value


def validate(value: Any) -> dict[str, Any]:
    return validate_decision(value)
