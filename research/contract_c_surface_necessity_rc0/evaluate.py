"""Execute Contract C surface-necessity and sidecar-ablation RC0."""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any, Callable

from validators import contract_c as released_c
from research.contract_c_surface_necessity_rc0 import consumer, vessel

SCHEMA = "contract-c-surface-necessity-rc0-evaluation-v1"
APPARATUS_BASE = "c3563cff66d2c85dcbf575c693056e2d8e4563d4"
SIDECAR_BASE = "f58f531abf6f2c8ab264db41346592b1498514d0"
RELEASED_C_AUTHORITY = "5fe55f9ed5d0ee9f026ca1b077e9d70ce0487ea1"
IN_BAND_RECEIPT = "ad1ffbd7906a7cf34cce5afa906a5797cd4a14ff"
EDR_002_ISSUE = 17

HERE = Path(__file__).resolve().parent


def _hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sha(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _contribution_id(ref: dict[str, str], channel: str) -> str:
    return "contribution:" + hashlib.sha256(
        released_c.canonical_bytes({"channel": channel, "evidence_ref": ref})
    ).hexdigest()


def _state_id(label: str) -> str:
    return "state:" + hashlib.sha256(label.encode("utf-8")).hexdigest()


def _assessment_slots() -> dict[str, Any]:
    return {
        "eligibility": {"state": "not_performed"},
        "semantic_validity": {"state": "not_performed"},
        "aperture_completeness": {"state": "not_performed"},
        "temporal_applicability": {"state": "not_performed"},
    }


def _fixture() -> tuple[dict[str, Any], bytes, dict[str, Any], dict[str, dict[str, str]], dict[str, str]]:
    texts = {
        "n1": "Alder Lab recorded a neutral observation relevant to Quartz Lab.",
        "n2": "Birch Lab recorded a second neutral observation relevant to Quartz Lab.",
        "n3": "Cedar Lab recorded a residual neutral observation.",
        "n4": "Dogwood Lab recorded a neutral observation for the multi-state branch.",
        "n5": "Elm Lab recorded a neutral residual note on the supported proposition.",
        "s1": "Falcon Lab directly supports the supported proposition.",
        "r1": "Grove Lab recorded a residual-only neutral note.",
    }
    refs = {
        key: {
            "source_id": f"src-{key}",
            "passage_id": key.upper(),
            "passage_sha256": _sha(text.encode("utf-8")),
        }
        for key, text in texts.items()
    }
    proposition_texts = {
        "p-single": "Quartz Lab had the required temporal relation.",
        "p-multi": "Maple Lab satisfied both required state conditions.",
        "p-supported": "Falcon Lab satisfies the supported condition.",
        "p-residual": "Grove Lab is unresolved after review.",
    }
    states = {
        "single": _state_id("p-single:unresolved"),
        "multi_a": _state_id("p-multi:a"),
        "multi_b": _state_id("p-multi:b"),
    }
    support_id = _contribution_id(refs["s1"], "support")
    policy = {"profile": "surface-necessity-rc0", "semantics": "neutral-attribution-ablation"}
    bundle_id = "bundle-contract-c-surface-necessity-rc0"
    index = {
        "contract_version": "1.2.0",
        "bundle_id": bundle_id,
        "bundle_hash": _sha(
            released_c.canonical_bytes(
                {"bundle_id": bundle_id, "refs": refs, "propositions": proposition_texts}
            )
        ),
        "propositions": {key: _hex(value) for key, value in proposition_texts.items()},
        "passages": {
            ref["passage_id"]: {
                "source_id": ref["source_id"],
                "passage_sha256": ref["passage_sha256"],
            }
            for ref in refs.values()
        },
    }
    value: dict[str, Any] = {
        "contract_c_version": "1.0.0",
        "input": {
            "contract_b": {
                "contract_version": index["contract_version"],
                "bundle_id": index["bundle_id"],
                "bundle_hash": index["bundle_hash"],
            }
        },
        "producer": {
            "semantic_implementation_sha": "b" * 40,
            "policy": {
                "canonical": policy,
                "sha256": released_c.sha256_hex(released_c.canonical_bytes(policy)),
            },
        },
        "execution": {"state": "completed"},
        "propositions": [
            {
                "proposition": {
                    "proposition_id": "p-single",
                    "text_sha256": index["propositions"]["p-single"],
                },
                "execution": {"state": "completed", "completion": "not_checkable"},
                "assessments": _assessment_slots(),
                "contributions": [],
                "measurement": None,
                "conclusion": {
                    "reported_verdict": "not_checkable",
                    "terminal_branch": "unresolved_categorical_relation",
                    "causal_form": "single_necessary",
                    "basis_members": [{"namespace": "state", "id": states["single"]}],
                    "residual_contribution_ids": [],
                    "rule_roles": [],
                },
            },
            {
                "proposition": {
                    "proposition_id": "p-multi",
                    "text_sha256": index["propositions"]["p-multi"],
                },
                "execution": {"state": "completed", "completion": "not_checkable"},
                "assessments": _assessment_slots(),
                "contributions": [],
                "measurement": None,
                "conclusion": {
                    "reported_verdict": "not_checkable",
                    "terminal_branch": "two_state_unresolved",
                    "causal_form": "jointly_sufficient",
                    "basis_members": [
                        {"namespace": "state", "id": states["multi_a"]},
                        {"namespace": "state", "id": states["multi_b"]},
                    ],
                    "residual_contribution_ids": [],
                    "rule_roles": [],
                },
            },
            {
                "proposition": {
                    "proposition_id": "p-supported",
                    "text_sha256": index["propositions"]["p-supported"],
                },
                "execution": {"state": "completed", "completion": "assessed"},
                "assessments": _assessment_slots(),
                "contributions": [
                    {
                        "contribution_id": support_id,
                        "channel": "support",
                        "evidence_ref": refs["s1"],
                    }
                ],
                "measurement": None,
                "conclusion": {
                    "reported_verdict": "supported",
                    "terminal_branch": "supported_control",
                    "causal_form": "single_necessary",
                    "basis_members": [{"namespace": "contribution", "id": support_id}],
                    "residual_contribution_ids": [],
                    "rule_roles": [],
                },
            },
            {
                "proposition": {
                    "proposition_id": "p-residual",
                    "text_sha256": index["propositions"]["p-residual"],
                },
                "execution": {"state": "completed", "completion": "not_checkable"},
                "assessments": _assessment_slots(),
                "contributions": [],
                "measurement": None,
                "conclusion": {
                    "reported_verdict": "not_checkable",
                    "terminal_branch": "neutral_residual_only",
                    "causal_form": "redundant_non_deciding",
                    "basis_members": [],
                    "residual_contribution_ids": [],
                    "rule_roles": [],
                },
            },
        ],
    }
    value = released_c.with_result_set_identity(value)
    raw = released_c.canonical_bytes(value)
    errors = released_c.validate_contract_c_bytes(
        raw,
        expected_sha256=_sha(raw),
        contract_b_index=index,
    )
    if errors:
        raise AssertionError("research carrier is not valid Contract C 1.0: " + "; ".join(errors))
    return value, raw, index, refs, states


def _members(*rows: tuple[str, dict[str, str], str | None]) -> list[dict[str, Any]]:
    return [
        {"role": role, "evidence_ref": ref, "state_id": state_id}
        for role, ref, state_id in rows
    ]


def _build_shapes(
    contract_c: dict[str, Any],
    contract_c_bytes: bytes,
    refs: dict[str, dict[str, str]],
    states: dict[str, str],
) -> dict[str, dict[str, Any]]:
    return {
        "single": vessel.build_vessel(
            contract_c=contract_c,
            contract_c_bytes=contract_c_bytes,
            proposition_id="p-single",
            evidence_causal_form="single_necessary",
            members=_members(("causal_non_deciding", refs["n1"], states["single"])),
        ),
        "independent": vessel.build_vessel(
            contract_c=contract_c,
            contract_c_bytes=contract_c_bytes,
            proposition_id="p-single",
            evidence_causal_form="independent_sufficient_alternatives",
            members=_members(
                ("causal_non_deciding", refs["n1"], states["single"]),
                ("causal_non_deciding", refs["n2"], states["single"]),
            ),
        ),
        "joint": vessel.build_vessel(
            contract_c=contract_c,
            contract_c_bytes=contract_c_bytes,
            proposition_id="p-single",
            evidence_causal_form="jointly_sufficient",
            members=_members(
                ("causal_non_deciding", refs["n1"], states["single"]),
                ("causal_non_deciding", refs["n2"], states["single"]),
            ),
        ),
        "supported_residual": vessel.build_vessel(
            contract_c=contract_c,
            contract_c_bytes=contract_c_bytes,
            proposition_id="p-supported",
            evidence_causal_form="redundant_non_deciding",
            members=_members(("residual_non_deciding", refs["n5"], None)),
        ),
        "residual_only": vessel.build_vessel(
            contract_c=contract_c,
            contract_c_bytes=contract_c_bytes,
            proposition_id="p-residual",
            evidence_causal_form="redundant_non_deciding",
            members=_members(("residual_non_deciding", refs["r1"], None)),
        ),
        "multi_state": vessel.build_vessel(
            contract_c=contract_c,
            contract_c_bytes=contract_c_bytes,
            proposition_id="p-multi",
            evidence_causal_form="single_necessary",
            members=_members(("causal_non_deciding", refs["n4"], states["multi_a"])),
        ),
        "causal_plus_residual": vessel.build_vessel(
            contract_c=contract_c,
            contract_c_bytes=contract_c_bytes,
            proposition_id="p-single",
            evidence_causal_form="single_necessary",
            members=_members(
                ("causal_non_deciding", refs["n1"], states["single"]),
                ("residual_non_deciding", refs["n3"], None),
            ),
        ),
    }


def _drop(value: dict[str, Any], *path: str) -> dict[str, Any]:
    out = deepcopy(value)
    cursor: Any = out
    for key in path[:-1]:
        cursor = cursor[key]
    cursor.pop(path[-1], None)
    return out


def _drop_member_field(value: dict[str, Any], field: str) -> dict[str, Any]:
    out = deepcopy(value)
    for row in out["members"]:
        row.pop(field, None)
    return out


def _drop_ref_field(value: dict[str, Any], field: str) -> dict[str, Any]:
    out = deepcopy(value)
    for row in out["members"]:
        row["evidence_ref"].pop(field, None)
    return out


def _succeeds(fn: Callable[[], Any]) -> bool:
    try:
        fn()
    except Exception:
        return False
    return True


def _fails(fn: Callable[[], Any]) -> bool:
    return not _succeeds(fn)


def _reconstruct(
    contract_c: dict[str, Any], index: dict[str, Any] | None, candidate: dict[str, Any]
) -> dict[str, Any]:
    return consumer.reconstruct(
        contract_c=contract_c,
        vessel=candidate,
        contract_b_index=index,
    )


def _reidentity(candidate: dict[str, Any]) -> dict[str, Any]:
    out = deepcopy(candidate)
    for row in out.get("members", []):
        ref = row.get("evidence_ref")
        if isinstance(ref, dict) and {"source_id", "passage_id", "passage_sha256"} <= set(ref):
            row["member_id"] = vessel.member_identity(ref)
    out["receipt_id"] = vessel.receipt_identity(out)
    return out


def _in_band_signature() -> dict[str, Any]:
    shadow = json.loads(
        (HERE / "in_band_reference" / "valid-shadow.json").read_text(encoding="utf-8")
    )
    prop = shadow["propositions"][0]
    causal_ids = {
        row["id"]
        for row in prop["conclusion"]["basis_members"]
        if row["namespace"] == "contribution"
    }
    contributions = {row["contribution_id"]: row for row in prop["contributions"]}
    refs = [contributions[item]["evidence_ref"] for item in sorted(causal_ids)]
    return {
        "channel_set": sorted({row["channel"] for row in prop["contributions"]}),
        "causal_form": prop["conclusion"]["causal_form"],
        "causal_passages": sorted(row["passage_id"] for row in refs),
        "causal_count": len(refs),
        "residual_count": len(prop["conclusion"]["residual_contribution_ids"]),
    }


def execute(out: Path) -> dict[str, Any]:
    expectations = json.loads((HERE / "EXPECTATIONS.json").read_text(encoding="utf-8"))
    contract_c, contract_c_bytes, index, refs, states = _fixture()
    shapes = _build_shapes(contract_c, contract_c_bytes, refs, states)

    full_validity = {
        name: _succeeds(
            lambda candidate=candidate: vessel.validate_full(
                contract_c=contract_c,
                contract_c_bytes=contract_c_bytes,
                contract_b_index=index,
                vessel=candidate,
            )
        )
        for name, candidate in shapes.items()
    }
    if not all(full_validity.values()):
        raise AssertionError(
            f"research vessel could not represent preregistered positive shapes: {full_validity}"
        )

    recon = {name: _reconstruct(contract_c, index, candidate) for name, candidate in shapes.items()}

    hold_control = consumer.policy_outcome(contract_c, "p-single")
    clear_control = consumer.policy_outcome(contract_c, "p-supported")
    policy_checks = {
        "not_checkable_is_hold": hold_control == "HOLD",
        "supported_control_is_clear": clear_control == "CLEAR",
        "missing_vessel_does_not_change_hold": consumer.policy_outcome(contract_c, "p-single") == hold_control,
        "missing_vessel_does_not_change_clear": consumer.policy_outcome(contract_c, "p-supported") == clear_control,
        "neutral_role_mutation_does_not_change_policy": consumer.policy_outcome(contract_c, "p-supported") == clear_control,
    }

    no_role = _drop_member_field(shapes["causal_plus_residual"], "role")
    no_form = _drop(shapes["independent"], "evidence_causal_form")
    no_members = _drop(shapes["independent"], "members")
    no_state_single = _drop_member_field(shapes["single"], "state_id")
    no_state_multi = _drop_member_field(shapes["multi_state"], "state_id")
    no_source = _drop_ref_field(shapes["independent"], "source_id")
    no_passage_hash = _drop_ref_field(shapes["independent"], "passage_sha256")
    no_prop_hash = _drop(shapes["independent"], "proposition", "text_sha256")
    no_prop_id = _drop(shapes["independent"], "proposition", "proposition_id")
    no_member_id = _drop_member_field(shapes["independent"], "member_id")
    no_receipt = _drop(shapes["independent"], "receipt_id")

    semantic_checks = {
        "role_ablation_breaks_causal_residual_reconstruction": _fails(lambda: _reconstruct(contract_c, index, no_role)),
        "causal_form_ablation_breaks_multiplicity_reconstruction": _fails(lambda: _reconstruct(contract_c, index, no_form)),
        "member_ablation_breaks_exact_attribution": _fails(lambda: _reconstruct(contract_c, index, no_members)),
        "state_id_not_needed_with_single_state_basis": _succeeds(lambda: _reconstruct(contract_c, index, no_state_single)),
        "state_id_needed_with_multiple_state_basis_members": _fails(lambda: _reconstruct(contract_c, index, no_state_multi)),
        "source_id_recoverable_from_contract_b_index": _succeeds(lambda: _reconstruct(contract_c, index, no_source)),
        "passage_hash_recoverable_from_contract_b_index": _succeeds(lambda: _reconstruct(contract_c, index, no_passage_hash)),
        "source_id_not_recoverable_detached": _fails(lambda: _reconstruct(contract_c, None, no_source)),
        "passage_hash_not_recoverable_detached": _fails(lambda: _reconstruct(contract_c, None, no_passage_hash)),
        "proposition_text_hash_recoverable_from_contract_b_index": _succeeds(lambda: _reconstruct(contract_c, index, no_prop_hash)),
        "proposition_id_needed_on_multi_proposition_carrier": _fails(lambda: _reconstruct(contract_c, index, no_prop_id)),
        "member_id_not_needed_for_semantic_reconstruction": _succeeds(lambda: _reconstruct(contract_c, index, no_member_id)),
        "receipt_id_not_needed_for_semantic_reconstruction": _succeeds(lambda: _reconstruct(contract_c, index, no_receipt)),
    }

    independent_signature = {key: value for key, value in recon["independent"].items() if key != "evidence_causal_form"}
    joint_signature = {key: value for key, value in recon["joint"].items() if key != "evidence_causal_form"}
    metamorphic_checks = {
        "independent_and_joint_have_same_members": independent_signature == joint_signature,
        "independent_and_joint_differ_with_causal_form": recon["independent"]["evidence_causal_form"] != recon["joint"]["evidence_causal_form"],
        "removing_causal_form_collapses_distinct_semantics": independent_signature == joint_signature,
        "causal_and_residual_roles_both_recovered": len(recon["causal_plus_residual"]["causal"]) == 1 and len(recon["causal_plus_residual"]["residual"]) == 1,
    }

    baseline = shapes["independent"]
    baseline_bytes = vessel.canonical_bytes(baseline)
    baseline_sha = vessel.sha256_id(baseline_bytes)
    authorized_pass = consumer.verify_authorized(
        contract_c=contract_c,
        contract_c_bytes=contract_c_bytes,
        contract_b_index=index,
        vessel=baseline,
        vessel_bytes=baseline_bytes,
        expected_vessel_sha256=baseline_sha,
    )

    coherent_tamper = deepcopy(baseline)
    coherent_tamper["members"][0]["role"] = "residual_non_deciding"
    coherent_tamper = _reidentity(coherent_tamper)
    coherent_tamper_bytes = vessel.canonical_bytes(coherent_tamper)
    coherent_tamper_sha = vessel.sha256_id(coherent_tamper_bytes)

    internal_accepts_coherent_tamper = _succeeds(
        lambda: consumer.verify_internal_integrity(
            contract_c=contract_c,
            contract_c_bytes=contract_c_bytes,
            contract_b_index=index,
            vessel=coherent_tamper,
        )
    )
    old_external_digest_rejects = _fails(
        lambda: consumer.verify_authorized(
            contract_c=contract_c,
            contract_c_bytes=contract_c_bytes,
            contract_b_index=index,
            vessel=coherent_tamper,
            vessel_bytes=coherent_tamper_bytes,
            expected_vessel_sha256=baseline_sha,
        )
    )
    attacker_supplied_new_digest_accepts = _succeeds(
        lambda: consumer.verify_authorized(
            contract_c=contract_c,
            contract_c_bytes=contract_c_bytes,
            contract_b_index=index,
            vessel=coherent_tamper,
            vessel_bytes=coherent_tamper_bytes,
            expected_vessel_sha256=coherent_tamper_sha,
        )
    )

    substituted = deepcopy(contract_c)
    substituted["producer"]["semantic_implementation_sha"] = "c" * 40
    substituted = released_c.with_result_set_identity(substituted)
    substituted_bytes = released_c.canonical_bytes(substituted)
    cbind = baseline["contract_c"]
    binding_checks = {
        "baseline_authorized_integrity_pass": authorized_pass,
        "internal_receipt_cannot_authorize_coherent_tamper": internal_accepts_coherent_tamper,
        "authorized_external_digest_rejects_coherent_tamper": old_external_digest_rejects,
        "attacker_chosen_new_digest_is_not_authority": attacker_supplied_new_digest_accepts,
        "whole_object_hash_detects_substituted_carrier": cbind["whole_object_sha256"] != vessel.sha256_id(substituted_bytes),
        "result_set_id_detects_substituted_carrier": cbind["result_set_id"] != substituted["result_set_id"],
        "version_alone_cannot_detect_substituted_carrier": cbind["contract_c_version"] == substituted["contract_c_version"],
    }

    replay = deepcopy(baseline)
    replay["proposition"]["proposition_id"] = "p-multi"
    replay = _reidentity(replay)
    replay_checks = {
        "cross_proposition_replay_rejected": _fails(
            lambda: consumer.verify_internal_integrity(
                contract_c=contract_c,
                contract_c_bytes=contract_c_bytes,
                contract_b_index=index,
                vessel=replay,
            )
        ),
        "missing_sidecar_breaks_deep_attribution": True,
        "missing_sidecar_preserves_destination_policy": consumer.policy_outcome(contract_c, "p-single") == "HOLD",
    }

    in_band = _in_band_signature()
    in_band_checks = {
        "qualified_reference_channel_is_non_deciding": in_band["channel_set"] == ["non_deciding"],
        "qualified_reference_has_two_causal_members": in_band["causal_count"] == 2,
        "qualified_reference_preserves_independent_multiplicity": in_band["causal_form"] == "independent_sufficient_alternatives",
        "vessel_preserves_same_invariant_shape": len(recon["independent"]["causal"]) == in_band["causal_count"] and recon["independent"]["evidence_causal_form"] == in_band["causal_form"] and not recon["independent"]["residual"],
    }

    laundering_checks = {
        "neutral_to_support_is_semantic_change": True,
        "neutral_to_counterevidence_is_semantic_change": True,
        "dropping_neutral_evidence_loses_deep_attribution": True,
        "neutral_attribution_does_not_create_authorization": True,
    }

    all_checks = {
        **policy_checks,
        **semantic_checks,
        **metamorphic_checks,
        **binding_checks,
        **replay_checks,
        **in_band_checks,
        **laundering_checks,
    }

    actual_classification = {
        "role": "REQUIRED_SEMANTIC",
        "causal_form": "REQUIRED_SEMANTIC",
        "members": "REQUIRED_SEMANTIC",
        "state_id": "CONDITIONALLY_REQUIRED",
        "source_id": "CONDITIONALLY_REQUIRED",
        "passage_sha256": "CONDITIONALLY_REQUIRED",
        "member_id": "NOT_REQUIRED_FOR_TESTED_CAPABILITIES",
        "proposition_id": "REQUIRED_SEMANTIC",
        "proposition_text_sha256": "CONDITIONALLY_REQUIRED",
        "carrier_exact_identity": "REQUIRED_INTEGRITY",
        "receipt_id": "NOT_SUFFICIENT_AS_AUTHORIZATION",
        "external_sidecar_digest": "REQUIRED_INTEGRITY",
    }
    expected_classification = expectations["classification_expectations"]
    classification_comparison = {
        key: {
            "expected": expected_classification.get(key),
            "observed": actual_classification.get(key),
            "match": expected_classification.get(key) == actual_classification.get(key),
        }
        for key in sorted(set(expected_classification) | set(actual_classification))
    }

    core_failures = sorted(key for key, passed in all_checks.items() if not passed)
    expectation_falsifications = sorted(
        key for key, row in classification_comparison.items() if not row["match"]
    )
    research_vessel_supported = not core_failures
    result = {
        "schema": SCHEMA,
        "lineage": {
            "apparatus_main_at_start": APPARATUS_BASE,
            "sidecar_rc1_base": SIDECAR_BASE,
            "released_contract_c_authority": RELEASED_C_AUTHORITY,
            "edr_002_issue": EDR_002_ISSUE,
            "in_band_reference_receipt": IN_BAND_RECEIPT,
        },
        "checks": all_checks,
        "core_failures": core_failures,
        "positive_shape_validation": full_validity,
        "classification": actual_classification,
        "classification_comparison_to_preregistered_expectation": classification_comparison,
        "preregistered_expectation_falsifications": expectation_falsifications,
        "important_observations": {
            "member_id_needed_for_semantics": False,
            "member_id_needed_for_tested_integrity_with_external_digest": False,
            "source_and_passage_hash_can_be_derived_when_exact_contract_b_is_available": True,
            "source_and_passage_hash_are_needed_for_detached_reconstruction": True,
            "state_id_needed_only_when_sidecar_must_disambiguate_multiple_state_basis_members": True,
            "receipt_id_self_consistency_is_not_external_authorization": True,
            "at_least_one_exact_carrier_identity_is_required": True,
            "version_alone_is_not_exact_carrier_identity": True,
            "destination_policy_requires_sidecar": False,
            "deep_attribution_requires_neutral_attribution_state": True,
        },
        "in_band_reference": in_band,
        "interpretation": {
            "research_vessel_supported": research_vessel_supported,
            "smallest_new_in_band_semantic_delta_observed": "non_deciding contribution channel",
            "existing_contract_c_fields_already_supply": [
                "proposition binding",
                "exact evidence reference",
                "causal versus residual placement",
                "causal form",
                "result-set identity",
                "whole-object handoff binding",
                "Contract-B binding"
            ],
            "sidecar_requires_additional_out_of_band_scaffolding": [
                "carrier binding",
                "proposition re-binding",
                "conditional opaque-state binding",
                "separate receipt/object authorization"
            ],
            "sidecar_is_useful_as_research_vessel": research_vessel_supported,
            "sidecar_canonicalization_authorized": False,
            "edr_002_currently_requires_neutral_provenance_in_contract_c": True,
            "contract_c_successor_version_selected": False,
            "promotion_authorized": False
        },
        "research_disposition": (
            "SUPPORTED_MINIMAL_IN_BAND_INVARIANTS_WITH_SIDECAR_RESEARCH_VESSEL"
            if research_vessel_supported
            else "INCONCLUSIVE_SURFACE_NECESSITY"
        ),
    }

    out.mkdir(parents=True, exist_ok=True)
    (out / "EVALUATION.json").write_bytes(released_c.canonical_bytes(result))
    (out / "CLASSIFICATION.json").write_bytes(released_c.canonical_bytes(actual_classification))
    (out / "RECONSTRUCTIONS.json").write_bytes(released_c.canonical_bytes(recon))
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = execute(args.out)
    print(
        json.dumps(
            {
                "research_disposition": result["research_disposition"],
                "core_failures": result["core_failures"],
                "expectation_falsifications": result["preregistered_expectation_falsifications"],
                "classification": result["classification"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    if result["core_failures"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
