from __future__ import annotations

import hashlib
import json
import math
import re
from copy import deepcopy
from datetime import datetime
from typing import Any, Callable

import rfc8785

STATE_SCHEMA = "contract-e-authority-state-candidate-rc3"
REQUEST_SCHEMA = "contract-e-authorization-request-candidate-rc3"
RECEIPT_SCHEMA = "contract-e-authorization-receipt-candidate-rc3"

STATE_KEYS = {"schema", "authority_state_id", "records"}
RECORD_KEYS = {
    "id", "basis_type", "subject_id", "domain", "operation", "scope",
    "target_class", "target_ref", "valid_from", "valid_until", "revoked_at",
    "parent_id", "delegated_by",
}
REQUEST_KEYS = {
    "schema", "request_id", "authority_state_id", "evaluation_time", "subject_id",
    "jurisdiction", "references", "supporting_artifacts", "conflicts", "residues",
}
JURISDICTION_KEYS = {"domain", "operation", "scope", "target_class", "target_ref"}
REFERENCE_KEYS = {"ref_id", "kind", "version", "immutable_id", "identity_sha256"}
SUPPORT_KEYS = {"id", "artifact_type", "ref_id"}
BLOCKER_KEYS = {"id", "relevant", "status"}
BOUND_KEYS = ("domain", "operation", "scope", "target_class", "target_ref")

_SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
_TIMESTAMP = re.compile(
    r"^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.(\d+))?Z$"
)


class InvalidCanonicalJSON(ValueError):
    pass


class InvalidTimestamp(ValueError):
    pass


def _assert_finite_json(value: Any, seen: set[int] | None = None) -> None:
    if seen is None:
        seen = set()
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise InvalidCanonicalJSON("non-finite number")
        return
    if isinstance(value, (list, dict)):
        marker = id(value)
        if marker in seen:
            raise InvalidCanonicalJSON("cyclic container")
        seen.add(marker)
        try:
            if isinstance(value, list):
                for child in value:
                    _assert_finite_json(child, seen)
            else:
                for key, child in value.items():
                    if not isinstance(key, str):
                        raise InvalidCanonicalJSON("non-string object key")
                    _assert_finite_json(child, seen)
        finally:
            seen.remove(marker)
        return
    raise InvalidCanonicalJSON(f"unsupported host value: {type(value).__name__}")


def canonical_bytes(value: Any) -> bytes:
    _assert_finite_json(value)
    try:
        return rfc8785.dumps(value) + b"\n"
    except Exception as exc:  # noqa: BLE001
        raise InvalidCanonicalJSON(str(exc)) from exc


def sha256_identity(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def strict_json_loads(text: str) -> Any:
    def hook(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise InvalidCanonicalJSON(f"duplicate object key: {key}")
            out[key] = value
        return out

    value = json.loads(
        text,
        object_pairs_hook=hook,
        parse_constant=lambda token: (_ for _ in ()).throw(
            InvalidCanonicalJSON(f"invalid constant: {token}")
        ),
    )
    _assert_finite_json(value)
    try:
        rfc8785.dumps(value)
    except Exception as exc:  # noqa: BLE001
        raise InvalidCanonicalJSON(str(exc)) from exc
    return value


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and _SHA256.fullmatch(value) is not None


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value)


def _exact_keys(value: Any, keys: set[str]) -> bool:
    return isinstance(value, dict) and set(value) == keys


def reference_identity(kind: str, version: str | None, immutable_id: str) -> str:
    return sha256_identity({"kind": kind, "version": version, "immutable_id": immutable_id})


def authority_state_identity(state: dict) -> str:
    payload = {key: deepcopy(value) for key, value in state.items() if key != "authority_state_id"}
    return sha256_identity(payload)


def _safe_recomputed_state_identity(state: Any) -> str | None:
    if not isinstance(state, dict):
        return None
    try:
        return authority_state_identity(state)
    except Exception:  # noqa: BLE001
        return None


def _claimed_state_identity(state: Any) -> str | None:
    if not isinstance(state, dict):
        return None
    value = state.get("authority_state_id")
    return value if _is_sha256(value) else None


def _parse_time(value: Any) -> tuple[int, int, int, int, int, int, str]:
    if not isinstance(value, str):
        raise InvalidTimestamp("timestamp must be string")
    match = _TIMESTAMP.fullmatch(value)
    if match is None:
        raise InvalidTimestamp("timestamp must be UTC Z form")
    year, month, day, hour, minute, second = (int(match.group(i)) for i in range(1, 7))
    fraction = match.group(7) or ""
    try:
        # Calendar/range validation only. Fractional ordering is handled independently below.
        datetime(year, month, day, hour, minute, second)
    except ValueError as exc:
        raise InvalidTimestamp(str(exc)) from exc
    return year, month, day, hour, minute, second, fraction


def _compare_time(left: Any, right: Any) -> int:
    a = _parse_time(left)
    b = _parse_time(right)
    if a[:6] < b[:6]:
        return -1
    if a[:6] > b[:6]:
        return 1
    width = max(len(a[6]), len(b[6]))
    af = a[6].ljust(width, "0")
    bf = b[6].ljust(width, "0")
    if af < bf:
        return -1
    if af > bf:
        return 1
    return 0


def _safe_time(value: Any) -> bool:
    try:
        _parse_time(value)
        return True
    except Exception:  # noqa: BLE001
        return False


def _record_shape(record: Any) -> bool:
    if not _exact_keys(record, RECORD_KEYS):
        return False
    if record["basis_type"] not in {"grant", "policy", "delegation"}:
        return False
    for key in ("id", "subject_id", "domain", "operation", "scope", "target_class"):
        if not _nonempty_string(record[key]):
            return False
    if not _is_sha256(record["target_ref"]):
        return False
    if not _safe_time(record["valid_from"]):
        return False
    for key in ("valid_until", "revoked_at"):
        if record[key] is not None and not _safe_time(record[key]):
            return False
    for key in ("parent_id", "delegated_by"):
        if record[key] is not None and not _nonempty_string(record[key]):
            return False
    return True


def validate_authority_state(state: Any) -> tuple[bool, list[str]]:
    errors: list[str] = []
    try:
        canonical_bytes(state)
    except Exception:  # noqa: BLE001
        return False, ["malformed_state"]
    if not _exact_keys(state, STATE_KEYS) or state.get("schema") != STATE_SCHEMA:
        return False, ["malformed_state"]
    if not _is_sha256(state.get("authority_state_id")):
        return False, ["malformed_state"]
    records = state.get("records")
    if not isinstance(records, list) or not records:
        return False, ["malformed_state"]
    if any(not _record_shape(record) for record in records):
        return False, ["malformed_state"]

    ids = [record["id"] for record in records]
    if len(ids) != len(set(ids)):
        errors.append("authority_lineage_invalid")

    root = records[0]
    if (
        root["basis_type"] not in {"grant", "policy"}
        or root["parent_id"] is not None
        or root["delegated_by"] is not None
    ):
        errors.append("authority_lineage_invalid")

    for index, record in enumerate(records[1:], start=1):
        parent = records[index - 1]
        if record["basis_type"] != "delegation":
            errors.append("authority_lineage_invalid")
        if record["parent_id"] != parent["id"] or record["delegated_by"] != parent["subject_id"]:
            errors.append("authority_lineage_invalid")
        if any(record[key] != parent[key] for key in BOUND_KEYS):
            errors.append("delegation_amplifies_or_changes_bounds")

    try:
        expected = authority_state_identity(state)
    except Exception:  # noqa: BLE001
        return False, ["malformed_state"]
    if state["authority_state_id"] != expected:
        errors.append("authority_state_identity_mismatch")
    return not errors, sorted(set(errors))


def _reference_shape(ref: Any) -> bool:
    if not _exact_keys(ref, REFERENCE_KEYS):
        return False
    if not all(_nonempty_string(ref[key]) for key in ("ref_id", "kind", "immutable_id")):
        return False
    if ref["version"] is not None and not _nonempty_string(ref["version"]):
        return False
    return _is_sha256(ref["identity_sha256"])


def _support_shape(item: Any) -> bool:
    return (
        _exact_keys(item, SUPPORT_KEYS)
        and all(_nonempty_string(item[key]) for key in ("id", "artifact_type", "ref_id"))
    )


def _blocker_shape(item: Any) -> bool:
    return (
        _exact_keys(item, BLOCKER_KEYS)
        and _nonempty_string(item["id"])
        and isinstance(item["relevant"], bool)
        and item["status"] in {"unresolved", "contested"}
    )


def _validate_references(references: Any) -> tuple[bool, set[str]]:
    if not isinstance(references, list) or not references:
        return False, set()
    local_ids: set[str] = set()
    for ref in references:
        if not _reference_shape(ref):
            return False, set()
        if ref["ref_id"] in local_ids:
            return False, set()
        local_ids.add(ref["ref_id"])
        if ref["identity_sha256"] != reference_identity(
            ref["kind"], ref["version"], ref["immutable_id"]
        ):
            return False, set()
    return True, local_ids


def _validate_support(items: Any, ref_ids: set[str]) -> bool:
    if not isinstance(items, list):
        return False
    seen: set[str] = set()
    for item in items:
        if not _support_shape(item):
            return False
        if item["id"] in seen or item["ref_id"] not in ref_ids:
            return False
        seen.add(item["id"])
    return True


def _validate_blockers(items: Any) -> bool:
    if not isinstance(items, list):
        return False
    seen: set[str] = set()
    for item in items:
        if not _blocker_shape(item):
            return False
        if item["id"] in seen:
            return False
        seen.add(item["id"])
    return True


def validate_request(request: Any) -> tuple[bool, list[str]]:
    try:
        canonical_bytes(request)
    except Exception:  # noqa: BLE001
        return False, ["malformed_request"]
    if not _exact_keys(request, REQUEST_KEYS) or request.get("schema") != REQUEST_SCHEMA:
        return False, ["malformed_request"]
    if not _nonempty_string(request.get("request_id")):
        return False, ["malformed_request"]
    if not _is_sha256(request.get("authority_state_id")):
        return False, ["malformed_request"]
    if not _safe_time(request.get("evaluation_time")) or not _nonempty_string(request.get("subject_id")):
        return False, ["malformed_request"]

    jurisdiction = request.get("jurisdiction")
    if not _exact_keys(jurisdiction, JURISDICTION_KEYS):
        return False, ["malformed_request"]
    if not all(_nonempty_string(jurisdiction[key]) for key in ("domain", "operation", "scope", "target_class")):
        return False, ["malformed_request"]
    if not _is_sha256(jurisdiction["target_ref"]):
        return False, ["malformed_request"]

    refs_ok, ref_ids = _validate_references(request.get("references"))
    if not refs_ok:
        return False, ["malformed_request"]
    if jurisdiction["target_ref"] not in {ref["identity_sha256"] for ref in request["references"]}:
        return False, ["target_reference_missing"]
    if not _validate_support(request.get("supporting_artifacts"), ref_ids):
        return False, ["malformed_request"]
    if not _validate_blockers(request.get("conflicts")) or not _validate_blockers(request.get("residues")):
        return False, ["malformed_request"]
    return True, []


def _record_current(record: dict, at: str) -> bool:
    if _compare_time(at, record["valid_from"]) < 0:
        return False
    if record["valid_until"] is not None and _compare_time(at, record["valid_until"]) > 0:
        return False
    if record["revoked_at"] is not None and _compare_time(at, record["revoked_at"]) >= 0:
        return False
    return True


def _safe_hash(value: Any) -> str | None:
    try:
        return sha256_identity(value)
    except Exception:  # noqa: BLE001
        return None


def _safe_preserve_list(request: Any, key: str, predicate: Callable[[Any], bool]) -> list:
    if not isinstance(request, dict):
        return []
    value = request.get(key)
    if not isinstance(value, list) or any(not predicate(item) for item in value):
        return []
    return deepcopy(value)


def _preserved_snapshot(request: Any) -> dict:
    return {
        "references": _safe_preserve_list(request, "references", _reference_shape),
        "supporting_artifacts": _safe_preserve_list(request, "supporting_artifacts", _support_shape),
        "conflicts": _safe_preserve_list(request, "conflicts", _blocker_shape),
        "residues": _safe_preserve_list(request, "residues", _blocker_shape),
    }


def _receipt_projection(receipt: dict) -> dict:
    return {
        key: deepcopy(value)
        for key, value in receipt.items()
        if key not in {"receipt_id", "diagnostics"}
    }


def _finalize_receipt(receipt: dict) -> dict:
    try:
        receipt["receipt_id"] = sha256_identity(_receipt_projection(receipt))
    except Exception:  # noqa: BLE001
        receipt["receipt_id"] = None
    return receipt


def _safe_request_field(request: Any, key: str, predicate: Callable[[Any], bool]) -> Any:
    if not isinstance(request, dict):
        return None
    value = request.get(key)
    return deepcopy(value) if predicate(value) else None


def evaluate(authority_state: Any, request: Any) -> dict:
    diagnostics: list[str] = []
    claimed_state_id = _claimed_state_identity(authority_state)
    recomputed_state_id = _safe_recomputed_state_identity(authority_state)

    state_ok, state_errors = validate_authority_state(authority_state)
    request_ok, request_errors = validate_request(request)
    diagnostics.extend(state_errors)
    diagnostics.extend(request_errors)

    request_id = _safe_request_field(request, "request_id", _nonempty_string)
    evaluation_time = _safe_request_field(request, "evaluation_time", _safe_time)
    subject_id = _safe_request_field(request, "subject_id", _nonempty_string)

    jurisdiction = None
    if isinstance(request, dict) and isinstance(request.get("jurisdiction"), dict):
        candidate = request["jurisdiction"]
        if (
            _exact_keys(candidate, JURISDICTION_KEYS)
            and all(_nonempty_string(candidate[key]) for key in ("domain", "operation", "scope", "target_class"))
            and _is_sha256(candidate["target_ref"])
        ):
            jurisdiction = deepcopy(candidate)

    receipt = {
        "schema": RECEIPT_SCHEMA,
        "receipt_id": None,
        "authority_conferring": False,
        "authorized": False,
        "request_id": request_id,
        "request_sha256": _safe_hash(request),
        "claimed_authority_state_id": claimed_state_id,
        "recomputed_authority_state_id": recomputed_state_id,
        "evaluation_time": evaluation_time,
        "subject_id": subject_id,
        "jurisdiction": jurisdiction,
        "authority_basis_id": None,
        "preserved": _preserved_snapshot(request),
        "diagnostics": [],
    }

    if not state_ok or not request_ok:
        receipt["diagnostics"] = sorted(set(diagnostics or ["malformed_input"]))
        return _finalize_receipt(receipt)

    if request["authority_state_id"] != authority_state["authority_state_id"]:
        diagnostics.append("authority_state_mismatch")

    if any(item["relevant"] for item in request["residues"]):
        diagnostics.append("relevant_residue_unresolved")
    if any(item["relevant"] for item in request["conflicts"]):
        diagnostics.append("relevant_conflict_unresolved")

    at = request["evaluation_time"]
    if any(not _record_current(record, at) for record in authority_state["records"]):
        diagnostics.append("authority_not_current")

    leaf = authority_state["records"][-1]
    if leaf["subject_id"] != request["subject_id"]:
        diagnostics.append("subject_mismatch")
    if any(leaf[key] != request["jurisdiction"][key] for key in BOUND_KEYS):
        diagnostics.append("jurisdiction_mismatch")

    if not diagnostics:
        receipt["authorized"] = True
        receipt["authority_basis_id"] = leaf["id"]

    receipt["diagnostics"] = sorted(set(diagnostics))
    return _finalize_receipt(receipt)
