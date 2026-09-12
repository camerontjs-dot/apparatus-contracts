"""Independent consumers for Contract C surface-necessity RC0.

This module intentionally imports no producer-side attribution-vessel code.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from typing import Any


def _canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _sha256_id(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _stable_id(namespace: str, value: Any) -> str:
    return f"{namespace}:{hashlib.sha256(_canonical_bytes(value)).hexdigest()}"


def _member_id(ref: dict[str, str]) -> str:
    return _stable_id(
        "attribution-member",
        {
            "source_id": ref["source_id"],
            "passage_id": ref["passage_id"],
            "passage_sha256": ref["passage_sha256"],
        },
    )


def _receipt_id(vessel: dict[str, Any]) -> str:
    payload = deepcopy(vessel)
    payload.pop("receipt_id", None)
    return _stable_id("attribution-vessel", payload)


def _proposition(contract_c: dict[str, Any], proposition_id: str) -> dict[str, Any]:
    proposition = next(
        (
            row
            for row in contract_c["propositions"]
            if row["proposition"]["proposition_id"] == proposition_id
        ),
        None,
    )
    if proposition is None:
        raise ValueError("proposition absent from Contract C")
    return proposition


def policy_outcome(contract_c: dict[str, Any], proposition_id: str) -> str:
    """Tiny bounded destination-policy control independent of attribution vessel."""
    proposition = _proposition(contract_c, proposition_id)
    execution = proposition["execution"]
    conclusion = proposition.get("conclusion") or {}
    if execution.get("state") != "completed":
        return "HOLD"
    if execution.get("completion") == "not_checkable":
        return "HOLD"
    return "CLEAR" if conclusion.get("reported_verdict") == "supported" else "HOLD"


def _state_ids(proposition: dict[str, Any]) -> list[str]:
    conclusion = proposition.get("conclusion") or {}
    return sorted(
        row["id"]
        for row in conclusion.get("basis_members", [])
        if row.get("namespace") == "state"
    )


def reconstruct(
    *,
    contract_c: dict[str, Any],
    vessel: dict[str, Any],
    contract_b_index: dict[str, Any] | None,
) -> dict[str, Any]:
    """Recover attribution using only fields actually available to a downstream consumer.

    This is deliberately capability-oriented rather than schema-oriented: missing
    duplicated fields may be safely recovered from the exact Contract-B index when
    the remaining binding is sufficient.
    """
    pbind = vessel.get("proposition") or {}
    proposition_id = pbind.get("proposition_id")
    if proposition_id is None:
        if len(contract_c["propositions"]) != 1:
            raise ValueError("ambiguous proposition binding")
        proposition_id = contract_c["propositions"][0]["proposition"]["proposition_id"]
    proposition = _proposition(contract_c, proposition_id)

    supplied_text_hash = pbind.get("text_sha256")
    if supplied_text_hash is None:
        if contract_b_index is None:
            raise ValueError("proposition text hash unavailable without Contract-B index")
        supplied_text_hash = contract_b_index["propositions"].get(proposition_id)
    if supplied_text_hash != proposition["proposition"]["text_sha256"]:
        raise ValueError("proposition text hash mismatch")
    if contract_b_index is not None:
        if contract_b_index["propositions"].get(proposition_id) != supplied_text_hash:
            raise ValueError("proposition is not bound to Contract-B index")

    form = vessel.get("evidence_causal_form")
    if form is None:
        raise ValueError("evidence causal form unavailable")
    members = vessel.get("members")
    if not isinstance(members, list) or not members:
        raise ValueError("attribution members unavailable")

    states = _state_ids(proposition)
    causal: list[dict[str, Any]] = []
    residual: list[dict[str, Any]] = []
    for member in members:
        role = member.get("role")
        if role not in {"causal_non_deciding", "residual_non_deciding"}:
            raise ValueError("neutral attribution role unavailable or invalid")
        ref = dict(member.get("evidence_ref") or {})
        passage_id = ref.get("passage_id")
        if passage_id is None:
            raise ValueError("passage identity unavailable")
        indexed = None if contract_b_index is None else contract_b_index["passages"].get(passage_id)
        source_id = ref.get("source_id")
        passage_sha256 = ref.get("passage_sha256")
        if source_id is None:
            if indexed is None:
                raise ValueError("source identity unavailable without Contract-B index")
            source_id = indexed["source_id"]
        if passage_sha256 is None:
            if indexed is None:
                raise ValueError("passage hash unavailable without Contract-B index")
            passage_sha256 = indexed["passage_sha256"]
        if indexed is not None:
            if indexed["source_id"] != source_id or indexed["passage_sha256"] != passage_sha256:
                raise ValueError("evidence reference mismatch against Contract-B index")

        state_id = member.get("state_id")
        if role == "causal_non_deciding":
            if state_id is None:
                if len(states) == 1:
                    state_id = states[0]
                elif len(states) > 1:
                    raise ValueError("ambiguous state binding for causal neutral evidence")
            elif state_id not in states:
                raise ValueError("causal member state binding mismatch")
        elif state_id is not None and state_id not in states:
            raise ValueError("residual member state binding mismatch")

        recovered = {
            "source_id": source_id,
            "passage_id": passage_id,
            "passage_sha256": passage_sha256,
            "state_id": state_id,
        }
        if role == "causal_non_deciding":
            causal.append(recovered)
        else:
            residual.append(recovered)

    if form == "single_necessary" and len(causal) != 1:
        raise ValueError("single_necessary causal cardinality mismatch")
    if form in {"independent_sufficient_alternatives", "jointly_sufficient"} and len(causal) < 2:
        raise ValueError("multi-member evidence causal form cardinality mismatch")
    if form == "redundant_non_deciding" and causal:
        raise ValueError("redundant_non_deciding cannot contain causal members")
    return {
        "proposition_id": proposition_id,
        "text_sha256": supplied_text_hash,
        "evidence_causal_form": form,
        "causal": sorted(causal, key=lambda row: (row["passage_id"], row["source_id"])),
        "residual": sorted(residual, key=lambda row: (row["passage_id"], row["source_id"])),
        "verified_against_contract_b": contract_b_index is not None,
    }


def verify_internal_integrity(
    *,
    contract_c: dict[str, Any],
    contract_c_bytes: bytes,
    contract_b_index: dict[str, Any],
    vessel: dict[str, Any],
) -> bool:
    """Verify self-consistency and exact carrier/data bindings, but no external authority."""
    if vessel.get("receipt_id") != _receipt_id(vessel):
        raise ValueError("stale vessel receipt identity")
    cbind = vessel.get("contract_c") or {}
    if cbind.get("contract_c_version") != contract_c.get("contract_c_version"):
        raise ValueError("Contract C version binding mismatch")
    if cbind.get("result_set_id") != contract_c.get("result_set_id"):
        raise ValueError("Contract C result-set binding mismatch")
    if cbind.get("whole_object_sha256") != _sha256_id(contract_c_bytes):
        raise ValueError("Contract C whole-object binding mismatch")

    cb = contract_c["input"]["contract_b"]
    for key in ("contract_version", "bundle_id", "bundle_hash"):
        if cb[key] != contract_b_index[key]:
            raise ValueError(f"Contract-B binding mismatch: {key}")

    for member in vessel.get("members") or []:
        ref = member.get("evidence_ref") or {}
        if member.get("member_id") != _member_id(ref):
            raise ValueError("member identity mismatch")
    reconstruct(contract_c=contract_c, vessel=vessel, contract_b_index=contract_b_index)
    return True


def verify_authorized(
    *,
    contract_c: dict[str, Any],
    contract_c_bytes: bytes,
    contract_b_index: dict[str, Any],
    vessel: dict[str, Any],
    vessel_bytes: bytes,
    expected_vessel_sha256: str,
) -> bool:
    """Add immutable external-object authorization to internal self-consistency."""
    if vessel_bytes != _canonical_bytes(vessel):
        raise ValueError("vessel bytes are not canonical")
    if _sha256_id(vessel_bytes) != expected_vessel_sha256:
        raise ValueError("vessel whole-object SHA-256 mismatch")
    return verify_internal_integrity(
        contract_c=contract_c,
        contract_c_bytes=contract_c_bytes,
        contract_b_index=contract_b_index,
        vessel=vessel,
    )


__all__ = [
    "policy_outcome",
    "reconstruct",
    "verify_authorized",
    "verify_internal_integrity",
]
