"""Independent standard-library consumer for the richer sidecar RC1.

This module intentionally does not import the producer-side sidecar implementation.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

SCHEMA = "cal-producer-attribution-sidecar-rc1-v1"
ROLE = "causal_non_deciding"
ALLOWED_FORMS = {"single_necessary", "independent_sufficient_alternatives", "jointly_sufficient"}


def _canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def _sha256(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _stable_id(namespace: str, value: Any) -> str:
    return f"{namespace}:{hashlib.sha256(_canonical_bytes(value)).hexdigest()}"


def _member_id(ref: dict[str, str]) -> str:
    return _stable_id("attribution-member", {
        "passage_id": ref["passage_id"],
        "passage_sha256": ref["passage_sha256"],
        "source_id": ref["source_id"],
    })


def _receipt_id(sidecar: dict[str, Any]) -> str:
    payload = dict(sidecar)
    payload.pop("receipt_id", None)
    return _stable_id("producer-attribution", payload)


def consume(
    *,
    contract_c: dict[str, Any],
    contract_c_bytes: bytes,
    contract_b_index: dict[str, Any],
    sidecar: dict[str, Any],
    sidecar_bytes: bytes,
    expected_sidecar_sha256: str,
) -> dict[str, Any]:
    if _sha256(sidecar_bytes) != expected_sidecar_sha256:
        raise ValueError("sidecar whole-object SHA-256 mismatch")
    if sidecar_bytes != _canonical_bytes(sidecar):
        raise ValueError("sidecar bytes are not canonical")

    expected_top = {"schema_name", "contract_c", "proposition", "state_id", "role", "causal_form", "members", "receipt_id"}
    if set(sidecar) != expected_top:
        raise ValueError("unexpected sidecar top-level fields")
    if sidecar["schema_name"] != SCHEMA:
        raise ValueError("unknown sidecar schema")
    if sidecar["role"] != ROLE:
        raise ValueError("unknown sidecar role")
    if sidecar["causal_form"] not in ALLOWED_FORMS:
        raise ValueError("unknown sidecar causal form")
    if sidecar["receipt_id"] != _receipt_id(sidecar):
        raise ValueError("stale sidecar receipt identity")

    cbind = sidecar["contract_c"]
    if set(cbind) != {"contract_c_version", "result_set_id", "whole_object_sha256"}:
        raise ValueError("unexpected Contract C binding fields")
    if cbind["contract_c_version"] != "1.0.0" or cbind["contract_c_version"] != contract_c.get("contract_c_version"):
        raise ValueError("Contract C version binding mismatch")
    if cbind["result_set_id"] != contract_c.get("result_set_id"):
        raise ValueError("Contract C result-set binding mismatch")
    if cbind["whole_object_sha256"] != _sha256(contract_c_bytes):
        raise ValueError("Contract C whole-object binding mismatch")

    cb = contract_c["input"]["contract_b"]
    for key in ("contract_version", "bundle_id", "bundle_hash"):
        if cb[key] != contract_b_index[key]:
            raise ValueError(f"Contract-B index binding mismatch: {key}")

    pbind = sidecar["proposition"]
    if set(pbind) != {"proposition_id", "text_sha256"}:
        raise ValueError("unexpected proposition binding fields")
    proposition = next((row for row in contract_c["propositions"] if row["proposition"]["proposition_id"] == pbind["proposition_id"]), None)
    if proposition is None:
        raise ValueError("sidecar proposition missing from Contract C")
    if proposition["proposition"]["text_sha256"] != pbind["text_sha256"]:
        raise ValueError("sidecar proposition text hash mismatch")
    if contract_b_index["propositions"].get(pbind["proposition_id"]) != pbind["text_sha256"]:
        raise ValueError("sidecar proposition missing from Contract-B index")

    state_ids = {
        row["id"] for row in proposition["conclusion"]["basis_members"]
        if row.get("namespace") == "state"
    }
    if sidecar["state_id"] not in state_ids:
        raise ValueError("sidecar state binding mismatch")

    members = sidecar["members"]
    if not isinstance(members, list) or not members:
        raise ValueError("sidecar requires causal members")
    member_ids = [row.get("member_id") for row in members]
    if member_ids != sorted(member_ids):
        raise ValueError("sidecar members are not in canonical order")
    if len(member_ids) != len(set(member_ids)):
        raise ValueError("duplicate sidecar member identity")

    refs_seen: set[tuple[str, str, str]] = set()
    recovered: list[dict[str, str]] = []
    for row in members:
        if set(row) != {"member_id", "evidence_ref"}:
            raise ValueError("unexpected sidecar member fields")
        ref = row["evidence_ref"]
        if set(ref) != {"source_id", "passage_id", "passage_sha256"}:
            raise ValueError("unexpected evidence reference fields")
        if row["member_id"] != _member_id(ref):
            raise ValueError("sidecar member identity mismatch")
        key = (ref["source_id"], ref["passage_id"], ref["passage_sha256"])
        if key in refs_seen:
            raise ValueError("duplicate exact evidence reference")
        refs_seen.add(key)
        indexed = contract_b_index["passages"].get(ref["passage_id"])
        if indexed is None or indexed["source_id"] != ref["source_id"] or indexed["passage_sha256"] != ref["passage_sha256"]:
            raise ValueError("sidecar evidence reference mismatch")
        recovered.append(dict(ref))

    form = sidecar["causal_form"]
    if form == "single_necessary" and len(recovered) != 1:
        raise ValueError("single_necessary cardinality mismatch")
    if form in {"independent_sufficient_alternatives", "jointly_sufficient"} and len(recovered) < 2:
        raise ValueError("multi-member causal form cardinality mismatch")

    return {
        "proposition_id": pbind["proposition_id"],
        "state_id": sidecar["state_id"],
        "role": sidecar["role"],
        "causal_form": form,
        "causal_passages": sorted(ref["passage_id"] for ref in recovered),
        "semantic_reaudit_performed": False,
    }


__all__ = ["consume"]
