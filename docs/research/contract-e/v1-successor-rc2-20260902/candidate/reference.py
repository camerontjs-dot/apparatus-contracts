from __future__ import annotations

import hashlib
import json
import math
import re
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

import rfc8785

STATE_SCHEMA = "contract-e-authority-state-candidate-rc2"
REQUEST_SCHEMA = "contract-e-authorization-request-candidate-rc2"
RECEIPT_SCHEMA = "contract-e-authorization-receipt-candidate-rc2"

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


class InvalidCanonicalJSON(ValueError):
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
    except Exception as exc:
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
    except Exception as exc:
        raise InvalidCanonicalJSON(str(exc)) from exc
    return value


def _is_sha256(value: Any) -> bool:
    return isinstance(value, str) and _SHA256.fullmatch(value) is not None


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
    except Exception:
        return None


def _claimed_state_identity(state: Any) -> str | None:
    if not isinstance(state, dict):
        return None
    claimed = state.get("authority_state_id")
    return claimed if _is_sha256(claimed) else None


def _parse_time(value: Any) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError("timestamp must be UTC Z string")
    dt = datetime.fromisoformat(value[:-1] + "+00:00")
    if dt.tzinfo is None or dt.utcoffset() != timezone.utc.utcoffset(dt):
        raise ValueError("timestamp must be UTC")
    return dt


def _exact_keys(value: Any, keys: set[str]) -> bool:
    return isinstance(value, dict) and set(value) == keys


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value)


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
    if not _nonempty_string(record["valid_from"]):
        return False
    for key in ("valid_until", "revoked_at", "parent_id", "delegated_by"):
        if record[key] is not None and not _nonempty_string(record[key]):
            return False
    try:
        _parse_time(record["valid_from"])
        if record["valid_until"] is not None:
            _parse_time(record["valid_until"])
        if record["revoked_at"] is not None:
            _parse_time(record["revoked_at"])
    except Exception:
        return False
    return True


def validate_authority_state(state: Any) -> tuple[bool, list[str]]:
    errors: list[str] = []
    try:
        _assert_finite_json(state)
        canonical_bytes(state)
    except Exception:
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
    except Exception:
        return False, ["malformed_state"]
    if state["authority_state_id"] != expected:
        errors.append("authority_state_identity_mismatch")
    return not errors, sorted(set(errors))


def _validate_references(references: Any) -> tuple[bool, set[str]]:
    if not isinstance(references, list) or not references:
        return False, set()
    local_ids: set[str] = set()
    for ref in references:
        if not _exact_keys(ref, REFERENCE_KEYS):
            return False, set()
        if not all(_nonempty_string(ref[key]) for key in ("ref_id", "kind", "immutable_id")):
            return False, set()
        if ref["version"] is not None and not _nonempty_string(ref["version"]):
            return False, set()
        if not _is_sha256(ref["identity_sha256"]):
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
        if not _exact_keys(item, SUPPORT_KEYS):
            return False
        if not all(_nonempty_string(item[key]) for key in ("id", "artifact_type", "ref_id")):
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
        if not _exact_keys(item, BLOCKER_KEYS):
            return False
        if not _nonempty_string(item["id"]) or not isinstance(item["relevant"], bool):
            return False
        if item["status"] not in {"unresolved", "contested"}:
            return False
        if item["id"] in seen:
            return False
        seen.add(item["id"])
    return True


def validate_request(request: Any) -> tuple[bool, list[str]]:
    try:
        _assert_finite_json(request)
        canonical_bytes(request)
    except Exception:
        return False, ["malformed_request"]
    if not _exact_keys(request, REQUEST_KEYS) or request.get("schema") != REQUEST_SCHEMA:
        return False, ["malformed_request"]
    if not _nonempty_string(request.get("request_id")):
        return False, ["malformed_request"]
    if not _is_sha256(request.get("authority_state_id")):
        return False, ["malformed_request"]
    if not _nonempty_string(request.get("evaluation_time")) or not _nonempty_string(request.get("subject_id")):
        return False, ["malformed_request"]
    try:
        _parse_time(request["evaluation_time"])
    except Exception:
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


def _record_current(record: dict, at: datetime) -> bool:
    start = _parse_time(record["valid_from"])
    if at < start:
        return False
    if record["valid_until"] is not None and at > _parse_time(record["valid_until"]):
        return False
    if record["revoked_at"] is not None and at >= _parse_time(record["revoked_at"]):
        return False
    return True


def _safe_hash(value: Any) -> str | None:
    try:
        return sha256_identity(value)
    except Exception:
        return None


def _preserved_snapshot(request: Any) -> dict:
    if not isinstance(request, dict):
        return {"references": [], "supporting_artifacts": [], "conflicts": [], "residues": []}
    return {
        "references": deepcopy(request.get("references", [])) if isinstance(request.get("references"), list) else [],
        "supporting_artifacts": deepcopy(request.get("supporting_artifacts", [])) if isinstance(request.get("supporting_artifacts"), list) else [],
        "conflicts": deepcopy(request.get("conflicts", [])) if isinstance(request.get("conflicts"), list) else [],
        "residues": deepcopy(request.get("residues", [])) if isinstance(request.get("residues"), list) else [],
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
    except Exception:
        receipt["receipt_id"] = None
    return receipt


def _safe_request_field(request: Any, key: str, predicate) -> Any:
    if not isinstance(request, dict):
        return None
    value = request.get(key)
    return value if predicate(value) else None


def _safe_time(value: Any) -> bool:
    try:
        _parse_time(value)
        return True
    except Exception:
        return False


def evaluate(authority_state: Any, request: Any) -> dict:
    diagnostics: list[str] = []
    claimed_state_id = _claimed_state_identity(authority_state)
    recomputed_state_id = _safe_recomputed_state_identity(authority_state)

    state_ok, state_errors = validate_authority_state(authority_state)
    request_ok, request_errors = validate_request(request)
    diagnostics.extend(state_errors)
    diagnostics.extend(request_errors)

    request_id = _safe_request_field(request, "request_id", _nonempty_string)
    evaluation_time = _safe_request_field(
        request,
        "evaluation_time",
        lambda value: _nonempty_string(value) and _safe_time(value),
    )
    subject_id = _safe_request_field(request, "subject_id", _nonempty_string)
    jurisdiction = None
    if isinstance(request, dict) and isinstance(request.get("jurisdiction"), dict):
        candidate = request["jurisdiction"]
        if _exact_keys(candidate, JURISDICTION_KEYS):
            if (
                all(_nonempty_string(candidate[key]) for key in ("domain", "operation", "scope", "target_class"))
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

    resolution_request = (
        request["jurisdiction"]["domain"] == "resolution"
        and request["jurisdiction"]["operation"] == "resolve"
    )
    if not resolution_request:
        if any(item["relevant"] for item in request["residues"]):
            diagnostics.append("relevant_residue_unresolved")
        if any(item["relevant"] for item in request["conflicts"]):
            diagnostics.append("relevant_conflict_unresolved")

    at = _parse_time(request["evaluation_time"])
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
