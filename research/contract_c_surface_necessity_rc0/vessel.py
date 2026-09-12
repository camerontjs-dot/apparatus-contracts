"""Research-only attribution vessel for Contract C surface-necessity experiments.

This is intentionally not a contract candidate. It is a superset carrier used to
ablate semantics and bindings without changing released Contract C 1.0.0.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from typing import Any

SCHEMA = "contract-c-attribution-vessel-rc0-v1"
ROLES = {"causal_non_deciding", "residual_non_deciding"}
FORMS = {
    "single_necessary",
    "independent_sufficient_alternatives",
    "jointly_sufficient",
    "redundant_non_deciding",
}


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
        + "\n"
    ).encode("utf-8")


def sha256_id(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def stable_id(namespace: str, value: Any) -> str:
    return f"{namespace}:{hashlib.sha256(canonical_bytes(value)).hexdigest()}"


def member_identity(evidence_ref: dict[str, str]) -> str:
    return stable_id(
        "attribution-member",
        {
            "source_id": evidence_ref["source_id"],
            "passage_id": evidence_ref["passage_id"],
            "passage_sha256": evidence_ref["passage_sha256"],
        },
    )


def receipt_identity(value: dict[str, Any]) -> str:
    payload = deepcopy(value)
    payload.pop("receipt_id", None)
    return stable_id("attribution-vessel", payload)


def build_vessel(
    *,
    contract_c: dict[str, Any],
    contract_c_bytes: bytes,
    proposition_id: str,
    evidence_causal_form: str,
    members: list[dict[str, Any]],
) -> dict[str, Any]:
    proposition = next(
        row
        for row in contract_c["propositions"]
        if row["proposition"]["proposition_id"] == proposition_id
    )
    built_members: list[dict[str, Any]] = []
    for member in members:
        ref = dict(member["evidence_ref"])
        built_members.append(
            {
                "member_id": member_identity(ref),
                "role": member["role"],
                "state_id": member.get("state_id"),
                "evidence_ref": ref,
            }
        )
    built_members.sort(key=lambda row: (row["member_id"], row["role"], row["state_id"] or ""))
    body: dict[str, Any] = {
        "schema_name": SCHEMA,
        "contract_c": {
            "contract_c_version": contract_c["contract_c_version"],
            "result_set_id": contract_c["result_set_id"],
            "whole_object_sha256": sha256_id(contract_c_bytes),
        },
        "proposition": {
            "proposition_id": proposition_id,
            "text_sha256": proposition["proposition"]["text_sha256"],
        },
        "evidence_causal_form": evidence_causal_form,
        "members": built_members,
    }
    body["receipt_id"] = receipt_identity(body)
    return body


def _state_ids(proposition: dict[str, Any]) -> set[str]:
    conclusion = proposition.get("conclusion") or {}
    return {
        row["id"]
        for row in conclusion.get("basis_members", [])
        if row.get("namespace") == "state"
    }


def validate_full(
    *,
    contract_c: dict[str, Any],
    contract_c_bytes: bytes,
    contract_b_index: dict[str, Any],
    vessel: dict[str, Any],
) -> dict[str, Any]:
    expected_top = {
        "schema_name",
        "contract_c",
        "proposition",
        "evidence_causal_form",
        "members",
        "receipt_id",
    }
    if set(vessel) != expected_top:
        raise ValueError("unexpected attribution-vessel top-level fields")
    if vessel["schema_name"] != SCHEMA:
        raise ValueError("unknown attribution-vessel schema")
    if vessel["evidence_causal_form"] not in FORMS:
        raise ValueError("unknown evidence causal form")
    if vessel["receipt_id"] != receipt_identity(vessel):
        raise ValueError("stale attribution-vessel receipt identity")

    cbind = vessel["contract_c"]
    if cbind["contract_c_version"] != contract_c["contract_c_version"]:
        raise ValueError("Contract C version binding mismatch")
    if cbind["result_set_id"] != contract_c["result_set_id"]:
        raise ValueError("Contract C result-set binding mismatch")
    if cbind["whole_object_sha256"] != sha256_id(contract_c_bytes):
        raise ValueError("Contract C whole-object binding mismatch")

    cb = contract_c["input"]["contract_b"]
    for key in ("contract_version", "bundle_id", "bundle_hash"):
        if cb[key] != contract_b_index[key]:
            raise ValueError(f"Contract-B binding mismatch: {key}")

    pbind = vessel["proposition"]
    proposition = next(
        (
            row
            for row in contract_c["propositions"]
            if row["proposition"]["proposition_id"] == pbind["proposition_id"]
        ),
        None,
    )
    if proposition is None:
        raise ValueError("vessel proposition absent from Contract C")
    if proposition["proposition"]["text_sha256"] != pbind["text_sha256"]:
        raise ValueError("vessel proposition text hash mismatch")
    if contract_b_index["propositions"].get(pbind["proposition_id"]) != pbind["text_sha256"]:
        raise ValueError("vessel proposition missing from Contract-B index")

    state_ids = _state_ids(proposition)
    members = vessel["members"]
    if not isinstance(members, list) or not members:
        raise ValueError("attribution vessel requires members")
    member_ids: list[str] = []
    exact_refs: list[tuple[str, str, str]] = []
    causal_count = 0
    residual_count = 0
    for member in members:
        if member["role"] not in ROLES:
            raise ValueError("unknown attribution role")
        ref = member["evidence_ref"]
        if member["member_id"] != member_identity(ref):
            raise ValueError("member identity mismatch")
        member_ids.append(member["member_id"])
        exact = (ref["source_id"], ref["passage_id"], ref["passage_sha256"])
        exact_refs.append(exact)
        indexed = contract_b_index["passages"].get(ref["passage_id"])
        if indexed is None:
            raise ValueError("evidence passage absent from Contract-B index")
        if indexed["source_id"] != ref["source_id"] or indexed["passage_sha256"] != ref["passage_sha256"]:
            raise ValueError("exact evidence reference mismatch")
        state_id = member.get("state_id")
        if state_id is not None and state_id not in state_ids:
            raise ValueError("state binding mismatch")
        if member["role"] == "causal_non_deciding":
            causal_count += 1
        else:
            residual_count += 1

    if len(member_ids) != len(set(member_ids)):
        raise ValueError("duplicate member identity")
    if len(exact_refs) != len(set(exact_refs)):
        raise ValueError("duplicate exact evidence reference")
    canonical_order = sorted(
        members,
        key=lambda row: (row["member_id"], row["role"], row.get("state_id") or ""),
    )
    if members != canonical_order:
        raise ValueError("members are not in canonical order")

    form = vessel["evidence_causal_form"]
    if form == "single_necessary" and causal_count != 1:
        raise ValueError("single_necessary requires exactly one causal member")
    if form in {"independent_sufficient_alternatives", "jointly_sufficient"} and causal_count < 2:
        raise ValueError(f"{form} requires at least two causal members")
    if form == "redundant_non_deciding" and causal_count != 0:
        raise ValueError("redundant_non_deciding cannot contain causal members")
    if form == "redundant_non_deciding" and residual_count < 1:
        raise ValueError("redundant_non_deciding requires residual evidence")
    return deepcopy(vessel)


__all__ = [
    "FORMS",
    "ROLES",
    "SCHEMA",
    "build_vessel",
    "canonical_bytes",
    "member_identity",
    "receipt_identity",
    "sha256_id",
    "stable_id",
    "validate_full",
]
