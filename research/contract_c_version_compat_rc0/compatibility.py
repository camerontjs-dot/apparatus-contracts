"""Research-only Contract C version-compatibility apparatus.

No production Contract C version or validator is changed here.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any, Callable

from validators import contract_c as released
from research.contract_c_non_deciding_shadow_rc0.shadow import (
    SHADOW_VERSION,
    validate_shadow_bytes,
)


RELEASED_PROFILE = "contract-c-released-1.0.0"
SUCCESSOR_PROFILE = "contract-c-non-deciding-shadow-rc0"


@dataclass(frozen=True)
class Profile:
    profile_id: str
    contract_c_version: str
    validator_identity: str
    validator: Callable[..., list[str]]


PROFILES = {
    RELEASED_PROFILE: Profile(
        profile_id=RELEASED_PROFILE,
        contract_c_version="1.0.0",
        validator_identity="sha1:9c75ccfbf2223578a8d1a7bf0c39673b394fbea4",
        validator=released.validate_contract_c_bytes,
    ),
    SUCCESSOR_PROFILE: Profile(
        profile_id=SUCCESSOR_PROFILE,
        contract_c_version=SHADOW_VERSION,
        validator_identity="research:contract-c-non-deciding-shadow-rc0",
        validator=validate_shadow_bytes,
    ),
}


class CompatibilityError(ValueError):
    pass


def validate_bound_profile(
    raw: bytes,
    *,
    expected_profile: str,
    expected_sha256: str,
    contract_b_index: dict[str, Any],
) -> dict[str, Any]:
    """Validate under an externally selected exact profile.

    Artifact metadata may confirm the profile but cannot select another validator.
    """
    profile = PROFILES.get(expected_profile)
    if profile is None:
        raise CompatibilityError(f"unknown externally expected profile: {expected_profile}")

    try:
        value = released.parse_json_bytes(raw)
    except ValueError as exc:
        raise CompatibilityError(str(exc)) from exc

    actual_version = value.get("contract_c_version")
    if actual_version != profile.contract_c_version:
        raise CompatibilityError(
            "profile_version_mismatch: "
            f"profile {expected_profile} requires {profile.contract_c_version}, got {actual_version}"
        )

    errors = profile.validator(
        raw,
        expected_sha256=expected_sha256,
        contract_b_index=contract_b_index,
    )
    if errors:
        raise CompatibilityError("profile_validation_failed: " + " | ".join(errors))

    return {
        "profile_id": profile.profile_id,
        "contract_c_version": actual_version,
        "validator_identity": profile.validator_identity,
        "whole_object_sha256": "sha256:" + released.sha256_hex(raw),
        "result_set_id": value["result_set_id"],
        "value": value,
    }


def safe_downgrade_to_1_0(value: dict[str, Any]) -> dict[str, Any]:
    """Fail closed when successor-only semantics are present."""
    for proposition in value.get("propositions", []):
        for contribution in proposition.get("contributions", []):
            if contribution.get("channel") == "non_deciding":
                raise CompatibilityError(
                    "lossless_downgrade_unavailable: non_deciding has no released 1.0 channel"
                )
    out = copy.deepcopy(value)
    out["contract_c_version"] = "1.0.0"
    out["result_set_id"] = released.result_set_identity(out)
    return out


def unsafe_map_channel_to_1_0(value: dict[str, Any], channel: str) -> dict[str, Any]:
    if channel not in {"support", "counterevidence"}:
        raise ValueError(channel)
    out = copy.deepcopy(value)
    out["contract_c_version"] = "1.0.0"
    for proposition in out.get("propositions", []):
        for contribution in proposition.get("contributions", []):
            if contribution.get("channel") == "non_deciding":
                contribution["channel"] = channel
    out["result_set_id"] = released.result_set_identity(out)
    return out


def unsafe_drop_non_deciding_to_1_0(value: dict[str, Any]) -> dict[str, Any]:
    """Erase neutral evidence and repair local structure into legal 1.0 shape."""
    out = copy.deepcopy(value)
    out["contract_c_version"] = "1.0.0"
    for proposition in out.get("propositions", []):
        removed_ids = {
            row["contribution_id"]
            for row in proposition.get("contributions", [])
            if row.get("channel") == "non_deciding"
        }
        proposition["contributions"] = [
            row
            for row in proposition.get("contributions", [])
            if row.get("contribution_id") not in removed_ids
        ]
        conclusion = proposition.get("conclusion")
        if conclusion is not None:
            conclusion["basis_members"] = [
                row
                for row in conclusion.get("basis_members", [])
                if not (
                    row.get("namespace") == "contribution" and row.get("id") in removed_ids
                )
            ]
            conclusion["residual_contribution_ids"] = [
                cid
                for cid in conclusion.get("residual_contribution_ids", [])
                if cid not in removed_ids
            ]
            if not conclusion["basis_members"]:
                conclusion["causal_form"] = "redundant_non_deciding"
    out["result_set_id"] = released.result_set_identity(out)
    return out


def canonical_materialize(value: dict[str, Any]) -> bytes:
    out = copy.deepcopy(value)
    out["result_set_id"] = released.result_set_identity(out)
    return released.canonical_bytes(out)


def provenance_fingerprint(value: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for proposition in value.get("propositions", []):
        contribution_by_id = {
            row["contribution_id"]: row for row in proposition.get("contributions", [])
        }
        causal_ids = [
            row["id"]
            for row in (proposition.get("conclusion") or {}).get("basis_members", [])
            if row.get("namespace") == "contribution"
        ]
        rows.append(
            {
                "proposition_id": proposition["proposition"]["proposition_id"],
                "causal_form": (proposition.get("conclusion") or {}).get("causal_form"),
                "causal": [
                    {
                        "contribution_id": cid,
                        "channel": contribution_by_id[cid]["channel"],
                        "evidence_ref": copy.deepcopy(contribution_by_id[cid]["evidence_ref"]),
                    }
                    for cid in causal_ids
                    if cid in contribution_by_id
                ],
                "residual": list(
                    (proposition.get("conclusion") or {}).get("residual_contribution_ids", [])
                ),
            }
        )
    return rows
