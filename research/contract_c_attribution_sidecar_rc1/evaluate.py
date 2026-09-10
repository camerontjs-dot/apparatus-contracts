"""Execute the richer Contract C attribution sidecar RC1 pressure test."""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any, Callable

from validators import contract_c as released_c
from research.contract_c_attribution_sidecar_rc1 import consumer
from research.contract_c_attribution_sidecar_rc1 import sidecar

SCHEMA = "contract-c-attribution-sidecar-rc1-evaluation-v1"
CAL_PR100_HEAD = "aa5f0f1313e65e6d31493095214c76d743ca6d89"
CAL_MULTIPLICITY_RUN = "34506201889"
CAL_MULTIPLICITY_ARTIFACT = "10163899726"
CAL_MULTIPLICITY_DIGEST = "sha256:23ba4cb13870f0b2c5f213d3279faede9d17f19e638dea49444249328a0efb19"
APPARATUS_BASE = "c3563cff66d2c85dcbf575c693056e2d8e4563d4"
RELEASED_C_HEAD = "5fe55f9ed5d0ee9f026ca1b077e9d70ce0487ea1"


def _text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sha256_id(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def _counterexample_fixture() -> tuple[dict[str, Any], bytes, dict[str, Any], list[dict[str, str]]]:
    proposition_id = "TEMP-C-SIDECAR-RC1"
    proposition_text = "Alice reviewed dossier before Bob archived dossier."
    u1 = "Alice did not review dossier before Bob archived dossier."
    u2 = "Alice did not review dossier after Bob archived dossier."
    refs = [
        {
            "source_id": "src-u1",
            "passage_id": "U1",
            "passage_sha256": _sha256_id(u1.encode("utf-8")),
        },
        {
            "source_id": "src-u2",
            "passage_id": "U2",
            "passage_sha256": _sha256_id(u2.encode("utf-8")),
        },
    ]
    bundle_id = "bundle-contract-c-sidecar-rc1"
    bundle_hash = _sha256_id(released_c.canonical_bytes({
        "bundle_id": bundle_id,
        "passages": refs,
        "proposition_id": proposition_id,
        "proposition_text_sha256": _text_hash(proposition_text),
    }))
    index = {
        "contract_version": "1.2.0",
        "bundle_id": bundle_id,
        "bundle_hash": bundle_hash,
        "propositions": {proposition_id: _text_hash(proposition_text)},
        "passages": {
            ref["passage_id"]: {
                "source_id": ref["source_id"],
                "passage_sha256": ref["passage_sha256"],
            }
            for ref in refs
        },
    }
    policy = {
        "profile": "counterexample-derived-sidecar-carrier-rc1",
        "semantics": "unresolved-causal-state",
    }
    state_id = "state:" + hashlib.sha256(released_c.canonical_bytes({
        "proposition_id": proposition_id,
        "terminal_branch": "unresolved_categorical_relation",
    })).hexdigest()
    value = {
        "contract_c_version": "1.0.0",
        "input": {
            "contract_b": {
                "contract_version": index["contract_version"],
                "bundle_id": index["bundle_id"],
                "bundle_hash": index["bundle_hash"],
            }
        },
        "producer": {
            "semantic_implementation_sha": "a" * 40,
            "policy": {
                "canonical": policy,
                "sha256": released_c.sha256_hex(released_c.canonical_bytes(policy)),
            },
        },
        "execution": {"state": "completed"},
        "propositions": [
            {
                "proposition": {
                    "proposition_id": proposition_id,
                    "text_sha256": _text_hash(proposition_text),
                },
                "execution": {"state": "completed", "completion": "not_checkable"},
                "assessments": {
                    "eligibility": {"state": "not_performed"},
                    "semantic_validity": {"state": "not_performed"},
                    "aperture_completeness": {"state": "not_performed"},
                    "temporal_applicability": {"state": "not_performed"},
                },
                "contributions": [],
                "measurement": None,
                "conclusion": {
                    "reported_verdict": "not_checkable",
                    "terminal_branch": "unresolved_categorical_relation",
                    "causal_form": "single_necessary",
                    "basis_members": [{"namespace": "state", "id": state_id}],
                    "residual_contribution_ids": [],
                    "rule_roles": [],
                },
            }
        ],
    }
    value = released_c.with_result_set_identity(value)
    raw = released_c.canonical_bytes(value)
    return value, raw, index, refs


def _reidentity(value: dict[str, Any]) -> dict[str, Any]:
    out = deepcopy(value)
    out["receipt_id"] = sidecar.receipt_identity(out)
    return out


def _reidentity_members(value: dict[str, Any]) -> dict[str, Any]:
    out = deepcopy(value)
    for member in out["members"]:
        member["member_id"] = sidecar.member_identity(member["evidence_ref"])
    out["receipt_id"] = sidecar.receipt_identity(out)
    return out


def _rejects(fn: Callable[[], Any]) -> bool:
    try:
        fn()
    except Exception:
        return True
    return False


def execute(out: Path) -> dict[str, Any]:
    contract_c, contract_c_bytes, index, refs = _counterexample_fixture()
    c_sha = _sha256_id(contract_c_bytes)
    released_errors = released_c.validate_contract_c_bytes(
        contract_c_bytes,
        expected_sha256=c_sha,
        contract_b_index=index,
    )
    if released_errors:
        raise AssertionError("counterexample carrier is not valid released Contract C 1.0: " + "; ".join(released_errors))

    prop = contract_c["propositions"][0]
    state_id = prop["conclusion"]["basis_members"][0]["id"]
    contract_c_alone_has_evidence_mapping = bool(prop["contributions"])

    valid = sidecar.build_sidecar(
        contract_c=contract_c,
        contract_c_bytes=contract_c_bytes,
        proposition_id=prop["proposition"]["proposition_id"],
        state_id=state_id,
        causal_form="independent_sufficient_alternatives",
        evidence_refs=refs,
    )
    validated = sidecar.validate_sidecar_against(
        contract_c=contract_c,
        contract_c_bytes=contract_c_bytes,
        contract_b_index=index,
        sidecar=valid,
    )
    valid_bytes = sidecar.canonical_bytes(validated)
    valid_sha = sidecar.sha256_id(valid_bytes)

    observed = consumer.consume(
        contract_c=contract_c,
        contract_c_bytes=contract_c_bytes,
        contract_b_index=index,
        sidecar=validated,
        sidecar_bytes=valid_bytes,
        expected_sidecar_sha256=valid_sha,
    )

    reversed_built = sidecar.build_sidecar(
        contract_c=contract_c,
        contract_c_bytes=contract_c_bytes,
        proposition_id=prop["proposition"]["proposition_id"],
        state_id=state_id,
        causal_form="independent_sufficient_alternatives",
        evidence_refs=list(reversed(refs)),
    )
    reversed_bytes = sidecar.canonical_bytes(reversed_built)

    def validate_variant(candidate: dict[str, Any]) -> None:
        sidecar.validate_sidecar_against(
            contract_c=contract_c,
            contract_c_bytes=contract_c_bytes,
            contract_b_index=index,
            sidecar=candidate,
        )

    wrong_c_sha = _reidentity({**deepcopy(valid), "contract_c": {**valid["contract_c"], "whole_object_sha256": "sha256:" + "0" * 64}})
    wrong_result = _reidentity({**deepcopy(valid), "contract_c": {**valid["contract_c"], "result_set_id": "result-set:" + "0" * 64}})
    wrong_version = _reidentity({**deepcopy(valid), "contract_c": {**valid["contract_c"], "contract_c_version": "1.0.1"}})
    wrong_prop = _reidentity({**deepcopy(valid), "proposition": {**valid["proposition"], "proposition_id": "other-proposition"}})
    wrong_prop_hash = _reidentity({**deepcopy(valid), "proposition": {**valid["proposition"], "text_sha256": "0" * 64}})
    wrong_state = _reidentity({**deepcopy(valid), "state_id": "state:" + "f" * 64})

    wrong_ref = deepcopy(valid)
    wrong_ref["members"][0]["evidence_ref"]["passage_sha256"] = "sha256:" + "0" * 64
    wrong_ref = _reidentity_members(wrong_ref)

    missing_ref = deepcopy(valid)
    missing_ref["members"][0]["evidence_ref"]["passage_id"] = "ABSENT"
    missing_ref = _reidentity_members(missing_ref)

    duplicate_member = deepcopy(valid)
    duplicate_member["members"][1] = deepcopy(duplicate_member["members"][0])
    duplicate_member = _reidentity(duplicate_member)

    unknown_role = _reidentity({**deepcopy(valid), "role": "support"})
    unknown_form = _reidentity({**deepcopy(valid), "causal_form": "bag_of_refs"})
    bad_single = _reidentity({**deepcopy(valid), "causal_form": "single_necessary"})

    bad_independent = deepcopy(valid)
    bad_independent["members"] = [bad_independent["members"][0]]
    bad_independent = _reidentity(bad_independent)

    stale_member = deepcopy(valid)
    stale_member["members"][0]["member_id"] = "attribution-member:" + "0" * 64
    stale_member = _reidentity(stale_member)

    stale_receipt = deepcopy(valid)
    stale_receipt["receipt_id"] = "producer-attribution:" + "0" * 64

    noncanonical_order = deepcopy(valid)
    noncanonical_order["members"] = list(reversed(noncanonical_order["members"]))
    noncanonical_order = _reidentity(noncanonical_order)

    tampered_wire = _reidentity({**deepcopy(valid), "state_id": state_id + "-tampered"})
    tampered_wire_bytes = sidecar.canonical_bytes(tampered_wire)
    external_hash_reject = _rejects(lambda: consumer.consume(
        contract_c=contract_c,
        contract_c_bytes=contract_c_bytes,
        contract_b_index=index,
        sidecar=tampered_wire,
        sidecar_bytes=tampered_wire_bytes,
        expected_sidecar_sha256=valid_sha,
    ))

    checks = {
        "released_contract_c_1_0_carrier_valid": True,
        "contract_c_alone_has_no_unresolved_evidence_mapping": not contract_c_alone_has_evidence_mapping,
        "sidecar_producer_validation_pass": validated == valid,
        "independent_consumer_recovers_both_passages": observed["causal_passages"] == ["U1", "U2"],
        "independent_consumer_recovers_multiplicity": observed["causal_form"] == "independent_sufficient_alternatives",
        "independent_consumer_preserves_neutral_role": observed["role"] == "causal_non_deciding",
        "independent_consumer_did_not_reaudit_semantics": observed["semantic_reaudit_performed"] is False,
        "reverse_builder_input_same_bytes": reversed_bytes == valid_bytes,
        "contract_c_bytes_unchanged": released_c.canonical_bytes(contract_c) == contract_c_bytes,
        "wrong_contract_c_sha_rejected": _rejects(lambda: validate_variant(wrong_c_sha)),
        "wrong_result_set_rejected": _rejects(lambda: validate_variant(wrong_result)),
        "wrong_contract_c_version_rejected": _rejects(lambda: validate_variant(wrong_version)),
        "wrong_proposition_rejected": _rejects(lambda: validate_variant(wrong_prop)),
        "wrong_proposition_hash_rejected": _rejects(lambda: validate_variant(wrong_prop_hash)),
        "wrong_state_rejected": _rejects(lambda: validate_variant(wrong_state)),
        "wrong_evidence_hash_rejected": _rejects(lambda: validate_variant(wrong_ref)),
        "missing_evidence_ref_rejected": _rejects(lambda: validate_variant(missing_ref)),
        "duplicate_member_rejected": _rejects(lambda: validate_variant(duplicate_member)),
        "unknown_role_rejected": _rejects(lambda: validate_variant(unknown_role)),
        "unknown_causal_form_rejected": _rejects(lambda: validate_variant(unknown_form)),
        "single_necessary_two_members_rejected": _rejects(lambda: validate_variant(bad_single)),
        "independent_one_member_rejected": _rejects(lambda: validate_variant(bad_independent)),
        "stale_member_identity_rejected": _rejects(lambda: validate_variant(stale_member)),
        "stale_receipt_identity_rejected": _rejects(lambda: validate_variant(stale_receipt)),
        "noncanonical_member_order_rejected": _rejects(lambda: validate_variant(noncanonical_order)),
        "external_sidecar_whole_object_hash_rejects_tamper": external_hash_reject,
    }

    passed = all(checks.values())
    result = {
        "schema": SCHEMA,
        "research_disposition": (
            "SUPPORTED_RICHER_SIDECAR_TECHNICALLY_SUFFICIENT"
            if passed
            else "FALSIFIED_RICHER_SIDECAR"
        ),
        "lineage": {
            "apparatus_base": APPARATUS_BASE,
            "released_contract_c_authority": RELEASED_C_HEAD,
            "cal_pr100_head": CAL_PR100_HEAD,
            "cal_multiplicity_run": CAL_MULTIPLICITY_RUN,
            "cal_multiplicity_artifact": CAL_MULTIPLICITY_ARTIFACT,
            "cal_multiplicity_digest": CAL_MULTIPLICITY_DIGEST,
        },
        "frozen_external_semantic_observation": {
            "relations": ["U1", "U2"],
            "terminal_state": "unresolved_categorical_relation",
            "evidence_level_causal_form": "independent_sufficient_alternatives",
            "semantic_reaudit_performed_here": False,
        },
        "carrier": {
            "contract_c_version": contract_c["contract_c_version"],
            "result_set_id": contract_c["result_set_id"],
            "sha256": c_sha,
            "state_id": state_id,
            "contract_c_alone_reconstructs_exact_unresolved_causes": False,
        },
        "sidecar": {
            "schema_name": valid["schema_name"],
            "receipt_id": valid["receipt_id"],
            "sha256": valid_sha,
            "bytes": len(valid_bytes),
            "causal_passages": observed["causal_passages"],
            "role": observed["role"],
            "causal_form": observed["causal_form"],
        },
        "checks": checks,
        "interpretation": {
            "contract_c_wire_revision_technically_necessary_for_exact_counterexample": False if passed else None,
            "contract_c_alone_information_sufficient": False,
            "sidecar_architecturally_preferred": None,
            "major_in_band_successor_falsified_as_technically_necessary_only": passed,
            "canonical_contract_decision_authorized": False,
            "production_promotion_authorized": False,
            "authorization_evaluated": False,
        },
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "EVALUATION.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    (out / "CARRIER-CONTRACT-C-1.0.0.json").write_bytes(contract_c_bytes)
    (out / "CONTRACT-B-INDEX.json").write_text(json.dumps(index, sort_keys=True, separators=(",", ":")) + "\n")
    (out / "ATTRIBUTION-SIDECAR.json").write_bytes(valid_bytes)
    print(json.dumps({
        "research_disposition": result["research_disposition"],
        "carrier_contract_c_sha256": c_sha,
        "sidecar_sha256": valid_sha,
        "sidecar_receipt_id": valid["receipt_id"],
        "causal_passages": observed["causal_passages"],
        "causal_form": observed["causal_form"],
    }, sort_keys=True))
    if not passed:
        raise SystemExit(1)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    execute(args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
