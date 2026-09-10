"""Research-only richer producer-attribution sidecar.

This module does not modify or replace Contract C 1.0.0. It defines a separately
immutable companion receipt for the bounded unresolved-provenance experiment.
"""
from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import re
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

SCHEMA = "cal-producer-attribution-sidecar-rc1-v1"
ROLE = "causal_non_deciding"
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_MEMBER_ID = re.compile(r"^attribution-member:[0-9a-f]{64}$")
_RECEIPT_ID = re.compile(r"^producer-attribution:[0-9a-f]{64}$")
_RESULT_SET_ID = re.compile(r"^result-set:[0-9a-f]{64}$")
_SHA256_ID = re.compile(r"^sha256:[0-9a-f]{64}$")


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
        + "\n"
    ).encode("utf-8")


def sha256_id(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _stable_id(namespace: str, value: Any) -> str:
    return f"{namespace}:{hashlib.sha256(canonical_bytes(value)).hexdigest()}"


def member_identity(evidence_ref: dict[str, str]) -> str:
    payload = {
        "passage_id": evidence_ref["passage_id"],
        "passage_sha256": evidence_ref["passage_sha256"],
        "source_id": evidence_ref["source_id"],
    }
    return _stable_id("attribution-member", payload)


def receipt_identity(value: dict[str, Any]) -> str:
    payload = deepcopy(value)
    payload.pop("receipt_id", None)
    return _stable_id("producer-attribution", payload)


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class EvidenceRef(_Strict):
    source_id: str = Field(min_length=1)
    passage_id: str = Field(min_length=1)
    passage_sha256: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")


class ContractCBinding(_Strict):
    contract_c_version: Literal["1.0.0"]
    result_set_id: str = Field(pattern=r"^result-set:[0-9a-f]{64}$")
    whole_object_sha256: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")


class PropositionBinding(_Strict):
    proposition_id: str = Field(min_length=1)
    text_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class AttributionMember(_Strict):
    member_id: str = Field(pattern=r"^attribution-member:[0-9a-f]{64}$")
    evidence_ref: EvidenceRef

    @model_validator(mode="after")
    def validate_member_identity(self) -> "AttributionMember":
        expected = member_identity(self.evidence_ref.model_dump())
        if self.member_id != expected:
            raise ValueError("member_id does not match exact evidence reference")
        return self


class AttributionSidecar(_Strict):
    schema_name: Literal[SCHEMA]
    contract_c: ContractCBinding
    proposition: PropositionBinding
    state_id: str = Field(pattern=r"^state:.+")
    role: Literal[ROLE]
    causal_form: Literal[
        "single_necessary",
        "independent_sufficient_alternatives",
        "jointly_sufficient",
    ]
    members: list[AttributionMember] = Field(min_length=1)
    receipt_id: str = Field(pattern=r"^producer-attribution:[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_structure(self) -> "AttributionSidecar":
        member_ids = [item.member_id for item in self.members]
        if len(member_ids) != len(set(member_ids)):
            raise ValueError("sidecar member ids must be unique")
        refs = [
            (
                item.evidence_ref.source_id,
                item.evidence_ref.passage_id,
                item.evidence_ref.passage_sha256,
            )
            for item in self.members
        ]
        if len(refs) != len(set(refs)):
            raise ValueError("sidecar exact evidence references must be unique")
        if member_ids != sorted(member_ids):
            raise ValueError("sidecar members must be in canonical member_id order")
        if self.causal_form == "single_necessary" and len(self.members) != 1:
            raise ValueError("single_necessary requires exactly one attribution member")
        if self.causal_form in {"independent_sufficient_alternatives", "jointly_sufficient"} and len(self.members) < 2:
            raise ValueError(f"{self.causal_form} requires at least two attribution members")
        expected_receipt = receipt_identity(self.model_dump())
        if self.receipt_id != expected_receipt:
            raise ValueError("receipt_id does not match canonical sidecar content")
        return self


def build_sidecar(
    *,
    contract_c: dict[str, Any],
    contract_c_bytes: bytes,
    proposition_id: str,
    state_id: str,
    causal_form: str,
    evidence_refs: list[dict[str, str]],
) -> dict[str, Any]:
    proposition = next(
        (row for row in contract_c["propositions"] if row["proposition"]["proposition_id"] == proposition_id),
        None,
    )
    if proposition is None:
        raise ValueError("sidecar proposition is absent from Contract C")
    members = [
        {
            "member_id": member_identity(ref),
            "evidence_ref": {
                "source_id": ref["source_id"],
                "passage_id": ref["passage_id"],
                "passage_sha256": ref["passage_sha256"],
            },
        }
        for ref in evidence_refs
    ]
    members.sort(key=lambda item: item["member_id"])
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
        "state_id": state_id,
        "role": ROLE,
        "causal_form": causal_form,
        "members": members,
    }
    body["receipt_id"] = receipt_identity(body)
    return body


def _state_basis_ids(proposition: dict[str, Any]) -> set[str]:
    conclusion = proposition.get("conclusion") or {}
    return {
        row["id"]
        for row in conclusion.get("basis_members", [])
        if row.get("namespace") == "state"
    }


def validate_sidecar_against(
    *,
    contract_c: dict[str, Any],
    contract_c_bytes: bytes,
    contract_b_index: dict[str, Any],
    sidecar: dict[str, Any],
) -> dict[str, Any]:
    model = AttributionSidecar.model_validate(sidecar)

    if model.contract_c.contract_c_version != contract_c.get("contract_c_version"):
        raise ValueError("sidecar Contract C version binding mismatch")
    if model.contract_c.result_set_id != contract_c.get("result_set_id"):
        raise ValueError("sidecar Contract C result_set_id binding mismatch")
    if model.contract_c.whole_object_sha256 != sha256_id(contract_c_bytes):
        raise ValueError("sidecar Contract C whole-object binding mismatch")

    c_binding = contract_c.get("input", {}).get("contract_b", {})
    for key in ("contract_version", "bundle_id", "bundle_hash"):
        if c_binding.get(key) != contract_b_index.get(key):
            raise ValueError(f"Contract-B index binding mismatch: {key}")

    proposition = next(
        (
            row
            for row in contract_c.get("propositions", [])
            if row.get("proposition", {}).get("proposition_id") == model.proposition.proposition_id
        ),
        None,
    )
    if proposition is None:
        raise ValueError("sidecar proposition is absent from Contract C")
    if proposition["proposition"]["text_sha256"] != model.proposition.text_sha256:
        raise ValueError("sidecar proposition text hash mismatch")
    indexed_text_hash = contract_b_index.get("propositions", {}).get(model.proposition.proposition_id)
    if indexed_text_hash != model.proposition.text_sha256:
        raise ValueError("sidecar proposition is not bound to Contract-B index")
    if model.state_id not in _state_basis_ids(proposition):
        raise ValueError("sidecar state_id is not a causal state basis member in Contract C")

    indexed_passages = contract_b_index.get("passages", {})
    for member in model.members:
        ref = member.evidence_ref
        indexed = indexed_passages.get(ref.passage_id)
        if indexed is None:
            raise ValueError(f"sidecar passage absent from Contract-B index: {ref.passage_id}")
        if indexed.get("source_id") != ref.source_id or indexed.get("passage_sha256") != ref.passage_sha256:
            raise ValueError(f"sidecar evidence reference mismatch: {ref.passage_id}")

    return model.model_dump()


__all__ = [
    "AttributionSidecar",
    "SCHEMA",
    "ROLE",
    "build_sidecar",
    "canonical_bytes",
    "member_identity",
    "receipt_identity",
    "sha256_id",
    "validate_sidecar_against",
]
