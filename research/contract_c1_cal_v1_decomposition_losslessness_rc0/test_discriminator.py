from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass

from validators.contract_c import (
    canonical_bytes,
    sha256_hex,
    validate_internal_structure,
    with_result_set_identity,
)

CAL_INTEGRATION_HEAD = "b695a1ca16051fde1c204987895b672e73225168"

ROOT_TEXT_HASH = "1" * 64
C1_TEXT_HASH = "2" * 64
C2_TEXT_HASH = "3" * 64
P1_HASH = "sha256:" + "4" * 64
P2_HASH = "sha256:" + "5" * 64

R1 = "cal-child-result:" + "a" * 64
R2 = "cal-child-result:" + "b" * 64
DECOMP_RECEIPT_A = "decomposition-receipt:" + "c" * 64
DECOMP_RECEIPT_B = "decomposition-receipt:" + "d" * 64


@dataclass(frozen=True)
class UpstreamLineage:
    decomposition_id: str
    operator: str
    ordered_children: tuple[tuple[str, str, str], ...]
    decomposition_receipt_id: str


LINEAGE_A = UpstreamLineage(
    decomposition_id="D-PIPE-RC0",
    operator="all_of",
    ordered_children=(
        ("C1", C1_TEXT_HASH, R1),
        ("C2", C2_TEXT_HASH, R2),
    ),
    decomposition_receipt_id=DECOMP_RECEIPT_A,
)

LINEAGE_B = UpstreamLineage(
    decomposition_id="D-DIFFERENT",
    operator="all_of",
    ordered_children=(
        ("C1", C1_TEXT_HASH, R1),
        ("C2", C2_TEXT_HASH, R2),
    ),
    decomposition_receipt_id=DECOMP_RECEIPT_B,
)


def _contribution(
    seed: str, source: str, passage: str, passage_hash: str
) -> dict[str, object]:
    return {
        "contribution_id": "contribution:" + seed * 64,
        "channel": "support",
        "evidence_ref": {
            "source_id": source,
            "passage_id": passage,
            "passage_sha256": passage_hash,
        },
    }


def _assessments() -> dict[str, object]:
    return {
        "eligibility": {"state": "not_performed"},
        "semantic_validity": {"state": "not_performed"},
        "aperture_completeness": {"state": "not_performed"},
        "temporal_applicability": {"state": "not_performed"},
    }


def _child(
    proposition_id: str,
    text_hash: str,
    contribution: dict[str, object],
) -> dict[str, object]:
    contribution_id = str(contribution["contribution_id"])
    return {
        "proposition": {
            "proposition_id": proposition_id,
            "text_sha256": text_hash,
        },
        "execution": {"state": "completed", "completion": "assessed"},
        "assessments": _assessments(),
        "contributions": [contribution],
        "measurement": None,
        "conclusion": {
            "reported_verdict": "supported",
            "terminal_branch": "supports",
            "causal_form": "single_necessary",
            "basis_members": [
                {"namespace": "contribution", "id": contribution_id},
            ],
            "residual_contribution_ids": [],
            "rule_roles": [],
        },
    }


def _state_id(kind: str, value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return f"state:{kind}:{digest}"


def _strongest_c1(lineage: UpstreamLineage) -> dict[str, object]:
    policy = {
        "profile": "cal-v1-research-parent-rc0",
        "semantic_subject": CAL_INTEGRATION_HEAD,
    }
    policy_hash = sha256_hex(canonical_bytes(policy))
    parent_basis = [
        {"namespace": "state", "id": _state_id("child-result", row[2])}
        for row in lineage.ordered_children
    ]
    parent_basis.append(
        {
            "namespace": "state",
            "id": _state_id("decomposition-receipt", lineage.decomposition_receipt_id),
        }
    )

    raw: dict[str, object] = {
        "contract_c_version": "1.0.0",
        "input": {
            "contract_b": {
                "contract_version": "1.2.0",
                "bundle_id": "bundle-cal-v1-parent-rc0",
                "bundle_hash": "sha256:" + "6" * 64,
            }
        },
        "producer": {
            "semantic_implementation_sha": CAL_INTEGRATION_HEAD,
            "policy": {
                "sha256": policy_hash,
                "canonical": policy,
            },
        },
        "execution": {"state": "completed"},
        "propositions": [
            _child(
                "C1",
                C1_TEXT_HASH,
                _contribution("7", "S-C1", "P-C1", P1_HASH),
            ),
            _child(
                "C2",
                C2_TEXT_HASH,
                _contribution("8", "S-C2", "P-C2", P2_HASH),
            ),
            {
                "proposition": {
                    "proposition_id": "ROOT",
                    "text_sha256": ROOT_TEXT_HASH,
                },
                "execution": {"state": "completed", "completion": "assessed"},
                "assessments": _assessments(),
                "contributions": [],
                "measurement": None,
                "conclusion": {
                    "reported_verdict": "supported",
                    "terminal_branch": "decomposition_all_of_supported",
                    "causal_form": "jointly_sufficient",
                    "basis_members": parent_basis,
                    "residual_contribution_ids": [],
                    "rule_roles": [
                        {
                            "rule_id": "rule-role:contract-a-all-of",
                            "code": "all_of",
                            "terminal_role": "causal",
                        }
                    ],
                },
            },
        ],
        "result_set_id": "result-set:" + "0" * 64,
    }
    return with_result_set_identity(raw)


def _contract_b_index() -> dict[str, object]:
    return {
        "contract_version": "1.2.0",
        "bundle_id": "bundle-cal-v1-parent-rc0",
        "bundle_hash": "sha256:" + "6" * 64,
        "propositions": {
            "ROOT": ROOT_TEXT_HASH,
            "C1": C1_TEXT_HASH,
            "C2": C2_TEXT_HASH,
        },
        "passages": {
            "P-C1": {"source_id": "S-C1", "passage_sha256": P1_HASH},
            "P-C2": {"source_id": "S-C2", "passage_sha256": P2_HASH},
        },
    }


def _authorized_recovery(value: dict[str, object]) -> dict[str, object]:
    """Recover only semantics Contract C 1.0 actually types.

    State IDs remain opaque. Rule codes remain CAL-attributable rule labels.
    No producer-private parser is introduced here.
    """
    propositions = []
    for row in value["propositions"]:  # type: ignore[index]
        conclusion = row["conclusion"]
        propositions.append(
            {
                "proposition_id": row["proposition"]["proposition_id"],
                "text_sha256": row["proposition"]["text_sha256"],
                "reported_verdict": conclusion["reported_verdict"],
                "terminal_branch": conclusion["terminal_branch"],
                "causal_form": conclusion["causal_form"],
                "basis_members": tuple(
                    (item["namespace"], item["id"])
                    for item in conclusion["basis_members"]
                ),
                "rule_roles": tuple(
                    (
                        item["rule_id"],
                        item["code"],
                        item["terminal_role"],
                    )
                    for item in conclusion["rule_roles"]
                ),
            }
        )
    return {
        "contract_b": value["input"]["contract_b"],  # type: ignore[index]
        "propositions": tuple(propositions),
    }


def _typed_decomposition_recovery(
    value: dict[str, object],
) -> UpstreamLineage | None:
    """Canonical C1 has no typed decoder for decomposition lineage."""
    _ = _authorized_recovery(value)
    return None


def _mutate_state_basis(
    value: dict[str, object],
    *,
    index: int,
    replacement: str,
) -> dict[str, object]:
    mutated = copy.deepcopy(value)
    parent = mutated["propositions"][2]  # type: ignore[index]
    parent["conclusion"]["basis_members"][index]["id"] = replacement
    return with_result_set_identity(mutated)


def test_strongest_c1_object_is_structurally_valid() -> None:
    value = _strongest_c1(LINEAGE_A)
    assert validate_internal_structure(value, _contract_b_index()) == []


def test_child_result_state_reference_has_no_c1_reference_integrity() -> None:
    original = _strongest_c1(LINEAGE_A)
    mutated = _mutate_state_basis(
        original,
        index=0,
        replacement="state:child-result:" + "e" * 64,
    )
    assert validate_internal_structure(mutated, _contract_b_index()) == []
    assert original["result_set_id"] != mutated["result_set_id"]


def test_decomposition_receipt_state_reference_has_no_c1_reference_integrity() -> None:
    original = _strongest_c1(LINEAGE_A)
    mutated = _mutate_state_basis(
        original,
        index=2,
        replacement="state:decomposition-receipt:" + "f" * 64,
    )
    assert validate_internal_structure(mutated, _contract_b_index()) == []
    assert original["result_set_id"] != mutated["result_set_id"]


def test_c1_and_contract_b_cannot_typed_recover_decomposition_lineage() -> None:
    value = _strongest_c1(LINEAGE_A)
    assert validate_internal_structure(value, _contract_b_index()) == []
    assert _typed_decomposition_recovery(value) is None


def test_distinct_upstream_decomposition_identity_remains_only_opaque_state_difference() -> (
    None
):
    first = _strongest_c1(LINEAGE_A)
    second = _strongest_c1(LINEAGE_B)

    assert validate_internal_structure(first, _contract_b_index()) == []
    assert validate_internal_structure(second, _contract_b_index()) == []

    first_authorized = _authorized_recovery(first)
    second_authorized = _authorized_recovery(second)

    first_parent = first_authorized["propositions"][2]
    second_parent = second_authorized["propositions"][2]
    assert first_parent["reported_verdict"] == second_parent["reported_verdict"]
    assert first_parent["causal_form"] == second_parent["causal_form"]
    assert first_parent["rule_roles"] == second_parent["rule_roles"]

    assert _typed_decomposition_recovery(first) is None
    assert _typed_decomposition_recovery(second) is None


def test_payload_smuggling_is_transport_capacity_not_contract_defined_recovery() -> (
    None
):
    value = _strongest_c1(LINEAGE_A)
    payload = (
        json.dumps(
            {
                "decomposition_id": LINEAGE_A.decomposition_id,
                "operator": LINEAGE_A.operator,
                "children": LINEAGE_A.ordered_children,
                "receipt": LINEAGE_A.decomposition_receipt_id,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        .encode("utf-8")
        .hex()
    )

    mutated = _mutate_state_basis(
        value,
        index=2,
        replacement="state:private-codec:" + payload,
    )
    assert validate_internal_structure(mutated, _contract_b_index()) == []

    # A producer-specific parser could decode this string, but canonical C1
    # defines state IDs as opaque and provides no such codec.
    assert _typed_decomposition_recovery(mutated) is None
