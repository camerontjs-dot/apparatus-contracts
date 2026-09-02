from __future__ import annotations

import hashlib
import json
import math
import re
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction
from typing import Any

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
SHA_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
TS_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.(\d+))?Z$")


class InvalidCanonicalJSON(ValueError):
    pass


def _assert_finite_json(value: Any, seen: set[int] | None = None) -> None:
    if seen is None:
        seen = set()
    if value is None or type(value) in (str, bool, int):
        return
    if type(value) is float:
        if not math.isfinite(value):
            raise InvalidCanonicalJSON("non-finite number")
        return
    if type(value) in (list, dict):
        oid = id(value)
        if oid in seen:
            raise InvalidCanonicalJSON("cyclic container")
        seen.add(oid)
        try:
            if type(value) is list:
                for item in value:
                    _assert_finite_json(item, seen)
            else:
                for key, item in value.items():
                    if type(key) is not str:
                        raise InvalidCanonicalJSON("non-string object key")
                    _assert_finite_json(item, seen)
        finally:
            seen.remove(oid)
        return
    raise InvalidCanonicalJSON(f"unsupported host value: {type(value).__name__}")


def canonical_bytes(value: Any) -> bytes:
    _assert_finite_json(value)
    try:
        return (json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ) + "\n").encode("utf-8")
    except (TypeError, ValueError, UnicodeEncodeError) as exc:
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
    canonical_bytes(value)
    return value


def reference_identity(kind: str, version: str | None, immutable_id: str) -> str:
    return sha256_identity({"kind": kind, "version": version, "immutable_id": immutable_id})


def authority_state_identity(state: dict) -> str:
    payload = {k: deepcopy(v) for k, v in state.items() if k != "authority_state_id"}
    return sha256_identity(payload)


def _is_sha256(value: Any) -> bool:
    return type(value) is str and SHA_RE.fullmatch(value) is not None


def _parse_time(value: Any):
    if type(value) is not str:
        raise ValueError("timestamp must be a string")
    match = TS_RE.fullmatch(value)
    if match is None:
        raise ValueError("timestamp must be canonical UTC Z form")
    year, month, day, hour, minute, second = map(int, match.groups()[:6])
    if second > 59:
        raise ValueError("leap seconds are not accepted")
    base = datetime(year, month, day, hour, minute, second, tzinfo=timezone.utc)
    frac_text = match.group(7)
    frac = Fraction(int(frac_text), 10 ** len(frac_text)) if frac_text else Fraction(0, 1)
    return base, frac


def _exact_keys(value: Any, keys: set[str]) -> bool:
    return type(value) is dict and set(value) == keys


def _nonempty_string(value: Any) -> bool:
    return type(value) is str and bool(value)


def _record_shape(record: Any) -> bool:
    if not _exact_keys(record, RECORD_KEYS):
        return False
    if type(record["basis_type"]) is not str or record["basis_type"] not in {"grant", "policy", "delegation"}:
        return False
    for key in ("id", "subject_id", *BOUND_KEYS):
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


def _state_id_observations(state: Any) -> tuple[str | None, str | None]:
    claimed = None
    computed = None
    if type(state) is dict:
        value = state.get("authority_state_id")
        if _is_sha256(value):
            claimed = value
        try:
            computed = authority_state_identity(state)
        except Exception:
            computed = None
    return claimed, computed


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
    if type(records) is not list or not records:
        return False, ["malformed_state"]
    if any(not _record_shape(record) for record in records):
        return False, ["malformed_state"]
    ids = [record["id"] for record in records]
    if len(ids) != len(set(ids)):
        errors.append("authority_lineage_invalid")
    root = records[0]
    if root["basis_type"] not in {"grant", "policy"} or root["parent_id"] is not None or root["delegated_by"] is not None:
        errors.append("authority_lineage_invalid")
    for index, record in enumerate(records[1:], start=1):
        parent = records[index - 1]
        if record["basis_type"] != "delegation":
            errors.append("authority_lineage_invalid")
        if record["parent_id"] != parent["id"] or record["delegated_by"] != parent["subject_id"]:
            errors.append("authority_lineage_invalid")
        if any(record[key] != parent[key] for key in BOUND_KEYS):
            errors.append("delegation_amplifies_or_changes_bounds")
    expected = authority_state_identity(state)
    if state["authority_state_id"] != expected:
        errors.append("authority_state_identity_mismatch")
    return not errors, sorted(set(errors))


def _valid_reference_shape(ref: Any) -> bool:
    return (
        _exact_keys(ref, REFERENCE_KEYS)
        and all(_nonempty_string(ref[k]) for k in ("ref_id", "kind", "immutable_id"))
        and (ref["version"] is None or _nonempty_string(ref["version"]))
        and _is_sha256(ref["identity_sha256"])
    )


def _validate_references(references: Any) -> tuple[bool, set[str]]:
    if type(references) is not list or not references:
        return False, set()
    ids: set[str] = set()
    for ref in references:
        if not _valid_reference_shape(ref):
            return False, set()
        if ref["ref_id"] in ids:
            return False, set()
        ids.add(ref["ref_id"])
        try:
            expected = reference_identity(ref["kind"], ref["version"], ref["immutable_id"])
        except Exception:
            return False, set()
        if ref["identity_sha256"] != expected:
            return False, set()
    return True, ids


def _valid_support_shape(item: Any) -> bool:
    return (
        _exact_keys(item, SUPPORT_KEYS)
        and all(_nonempty_string(item[k]) for k in ("id", "artifact_type", "ref_id"))
    )


def _validate_support(items: Any, ref_ids: set[str]) -> bool:
    if type(items) is not list:
        return False
    seen = set()
    for item in items:
        if not _valid_support_shape(item):
            return False
        if item["id"] in seen or item["ref_id"] not in ref_ids:
            return False
        seen.add(item["id"])
    return True


def _valid_blocker_shape(item: Any) -> bool:
    return (
        _exact_keys(item, BLOCKER_KEYS)
        and _nonempty_string(item["id"])
        and type(item["relevant"]) is bool
        and type(item["status"]) is str
        and item["status"] in {"unresolved", "contested"}
    )


def _validate_blockers(items: Any) -> bool:
    if type(items) is not list:
        return False
    seen = set()
    for item in items:
        if not _valid_blocker_shape(item):
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
    if not _nonempty_string(request.get("subject_id")):
        return False, ["malformed_request"]
    try:
        _parse_time(request.get("evaluation_time"))
    except Exception:
        return False, ["malformed_request"]
    jurisdiction = request.get("jurisdiction")
    if not _exact_keys(jurisdiction, JURISDICTION_KEYS):
        return False, ["malformed_request"]
    if not all(_nonempty_string(jurisdiction[k]) for k in ("domain", "operation", "scope", "target_class")):
        return False, ["malformed_request"]
    if not _is_sha256(jurisdiction["target_ref"]):
        return False, ["malformed_request"]
    refs_ok, ref_ids = _validate_references(request.get("references"))
    if not refs_ok:
        return False, ["malformed_request"]
    target_identity = jurisdiction["target_ref"]
    if target_identity not in {ref["identity_sha256"] for ref in request["references"]}:
        return False, ["target_reference_missing"]
    if not _validate_support(request.get("supporting_artifacts"), ref_ids):
        return False, ["malformed_request"]
    if not _validate_blockers(request.get("conflicts")) or not _validate_blockers(request.get("residues")):
        return False, ["malformed_request"]
    return True, []


def _record_current(record: dict, at) -> bool:
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


def _safe_scalar_request_fields(request: Any):
    request_hash = _safe_hash(request)
    canonicalizable = request_hash is not None and type(request) is dict
    if not canonicalizable:
        return None, request_hash, None, None, None
    request_id = request.get("request_id") if _nonempty_string(request.get("request_id")) else None
    evaluation_time = request.get("evaluation_time")
    try:
        _parse_time(evaluation_time)
    except Exception:
        evaluation_time = None
    subject_id = request.get("subject_id") if _nonempty_string(request.get("subject_id")) else None
    jurisdiction = request.get("jurisdiction")
    if not (
        _exact_keys(jurisdiction, JURISDICTION_KEYS)
        and all(_nonempty_string(jurisdiction[k]) for k in ("domain", "operation", "scope", "target_class"))
        and _is_sha256(jurisdiction["target_ref"])
    ):
        jurisdiction = None
    else:
        jurisdiction = deepcopy(jurisdiction)
    return request_id, request_hash, evaluation_time, subject_id, jurisdiction


def _schema_safe_preserved(request: Any) -> dict:
    empty = {"references": [], "supporting_artifacts": [], "conflicts": [], "residues": []}
    if type(request) is not dict or _safe_hash(request) is None:
        return empty
    refs = request.get("references")
    supports = request.get("supporting_artifacts")
    conflicts = request.get("conflicts")
    residues = request.get("residues")
    return {
        "references": deepcopy(refs) if type(refs) is list and all(_valid_reference_shape(x) for x in refs) else [],
        "supporting_artifacts": deepcopy(supports) if type(supports) is list and all(_valid_support_shape(x) for x in supports) else [],
        "conflicts": deepcopy(conflicts) if type(conflicts) is list and all(_valid_blocker_shape(x) for x in conflicts) else [],
        "residues": deepcopy(residues) if type(residues) is list and all(_valid_blocker_shape(x) for x in residues) else [],
    }


def _receipt_projection(receipt: dict) -> dict:
    return {k: deepcopy(v) for k, v in receipt.items() if k not in {"receipt_id", "diagnostics"}}


def _finalize_receipt(receipt: dict) -> dict:
    try:
        receipt["receipt_id"] = sha256_identity(_receipt_projection(receipt))
    except Exception:
        receipt["receipt_id"] = None
    return receipt


def evaluate(authority_state: Any, request: Any) -> dict:
    diagnostics: list[str] = []
    claimed_id, computed_id = _state_id_observations(authority_state)
    state_ok, state_errors = validate_authority_state(authority_state)
    request_ok, request_errors = validate_request(request)
    diagnostics.extend(state_errors)
    diagnostics.extend(request_errors)

    request_id, request_hash, evaluation_time_text, subject_id, jurisdiction = _safe_scalar_request_fields(request)
    receipt = {
        "schema": RECEIPT_SCHEMA,
        "receipt_id": None,
        "authority_conferring": False,
        "authorized": False,
        "request_id": request_id,
        "request_sha256": request_hash,
        "authority_state_claimed_id": claimed_id,
        "authority_state_computed_id": computed_id,
        "evaluation_time": evaluation_time_text,
        "subject_id": subject_id,
        "jurisdiction": jurisdiction,
        "authority_basis_id": None,
        "preserved": _schema_safe_preserved(request),
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

    at = _parse_time(request["evaluation_time"])
    for record in authority_state["records"]:
        if not _record_current(record, at):
            diagnostics.append("authority_not_current")
            break

    leaf = authority_state["records"][-1]
    if leaf["subject_id"] != request["subject_id"]:
        diagnostics.append("subject_mismatch")
    jurisdiction = request["jurisdiction"]
    if any(leaf[key] != jurisdiction[key] for key in BOUND_KEYS):
        diagnostics.append("jurisdiction_mismatch")

    if not diagnostics:
        receipt["authorized"] = True
        receipt["authority_basis_id"] = leaf["id"]

    receipt["diagnostics"] = sorted(set(diagnostics))
    return _finalize_receipt(receipt)
