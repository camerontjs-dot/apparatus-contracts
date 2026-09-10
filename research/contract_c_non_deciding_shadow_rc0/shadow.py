"""Research-only two-leaf Contract C non-deciding shadow.

This module intentionally delegates all unchanged semantics to the released
Contract C 1.0 validator. It is not a production validator or version proposal.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from validators import contract_c as released

SHADOW_VERSION = "research-non-deciding-rc0"
ALLOWED_CHANNELS = {"support", "counterevidence", "non_deciding"}


def build_shadow_schema(released_schema: dict[str, Any]) -> dict[str, Any]:
    schema = copy.deepcopy(released_schema)
    schema["title"] = "Apparatus Contract C research non-deciding shadow RC0"
    schema["$id"] = "urn:apparatus:research:contract-c:non-deciding:rc0"
    schema["properties"]["contract_c_version"]["const"] = SHADOW_VERSION
    schema["$defs"]["contribution"]["properties"]["channel"]["enum"] = [
        "support",
        "counterevidence",
        "non_deciding",
    ]
    return schema


def semantic_schema_delta(released_schema: dict[str, Any], shadow_schema: dict[str, Any]) -> list[str]:
    """Return changed semantic leaf paths, excluding research-only title/id metadata."""
    left = copy.deepcopy(released_schema)
    right = copy.deepcopy(shadow_schema)
    for obj in (left, right):
        obj.pop("title", None)
        obj.pop("$id", None)

    diffs: list[str] = []

    def walk(a: Any, b: Any, path: str) -> None:
        if type(a) is not type(b):
            diffs.append(path)
            return
        if isinstance(a, dict):
            keys = sorted(set(a) | set(b))
            for key in keys:
                child = f"{path}.{key}" if path else key
                if key not in a or key not in b:
                    diffs.append(child)
                else:
                    walk(a[key], b[key], child)
            return
        if isinstance(a, list):
            if a != b:
                diffs.append(path)
            return
        if a != b:
            diffs.append(path)

    walk(left, right, "")
    return sorted(diffs)


def expected_semantic_delta() -> list[str]:
    return sorted(
        [
            "properties.contract_c_version.const",
            "$defs.contribution.properties.channel.enum",
        ]
    )


def _compatibility_projection(value: dict[str, Any]) -> dict[str, Any]:
    """Map only the research wire additions to released 1.0 for invariant reuse."""
    compat = copy.deepcopy(value)
    compat["contract_c_version"] = released.CONTRACT_C_VERSION
    for proposition in compat.get("propositions", []):
        for contribution in proposition.get("contributions", []):
            if contribution.get("channel") == "non_deciding":
                contribution["channel"] = "support"
    compat["result_set_id"] = released.result_set_identity(compat)
    return compat


def validate_shadow_object(
    value: dict[str, Any],
    *,
    contract_b_index: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    if value.get("contract_c_version") != SHADOW_VERSION:
        errors.append(f"shadow contract_c_version must equal {SHADOW_VERSION}")
        return errors

    channels: list[str] = []
    try:
        propositions = value["propositions"]
        if not isinstance(propositions, list):
            raise TypeError
        for proposition in propositions:
            for contribution in proposition.get("contributions", []):
                channel = contribution.get("channel")
                if channel not in ALLOWED_CHANNELS:
                    errors.append(f"unknown shadow contribution channel: {channel}")
                elif isinstance(channel, str):
                    channels.append(channel)
    except (KeyError, TypeError, AttributeError):
        pass

    if "non_deciding" not in channels:
        errors.append("shadow object must exercise at least one non_deciding contribution")
    if errors:
        return errors

    expected_result_id = released.result_set_identity(value)
    if value.get("result_set_id") != expected_result_id:
        errors.append(
            f"result_set_id mismatch: expected {expected_result_id}, got {value.get('result_set_id')}"
        )

    compat = _compatibility_projection(value)
    errors.extend(released.validate_internal_structure(compat, contract_b_index=contract_b_index))
    return errors


def validate_shadow_bytes(
    raw: bytes,
    *,
    expected_sha256: str | None = None,
    contract_b_index: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    if expected_sha256 is not None:
        errors.extend(released.validate_whole_object_hash(raw, expected_sha256))
    try:
        value = released.parse_json_bytes(raw)
    except ValueError as exc:
        return errors + [str(exc)]
    if raw != released.canonical_bytes(value):
        errors.append("non-canonical shadow Contract-C bytes")
    errors.extend(validate_shadow_object(value, contract_b_index=contract_b_index))
    return errors


def canonical_shadow(value: dict[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(value)
    out["contract_c_version"] = SHADOW_VERSION
    out["result_set_id"] = released.result_set_identity(out)
    return out


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value
