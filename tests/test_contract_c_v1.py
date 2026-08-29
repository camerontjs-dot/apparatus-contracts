from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from validators.contract_c import (
    CONTRACT_C_SUPPORTED_VERSIONS,
    CONTRACT_C_VERSION,
    ContractCResultSet,
    canonical_bytes,
    parse_json_bytes,
    result_set_identity,
    sha256_hex,
    validate_contract_c_bytes,
    validate_internal_structure,
    validate_whole_object_hash,
    with_result_set_identity,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures" / "contract-c" / "1.0.0"
VALID_PATH = FIXTURES / "valid-canonical.json"
INDEX_PATH = FIXTURES / "contract-b-index.json"
VERSIONS_PATH = ROOT / "schema" / "contract-c" / "versions.json"
SCHEMA_PATH = ROOT / "schema" / "contract-c" / "1.0.0" / "schema.json"


def _valid() -> dict:
    return parse_json_bytes(VALID_PATH.read_bytes())


def _index() -> dict:
    return parse_json_bytes(INDEX_PATH.read_bytes())


def _errors(value: dict, *, with_index: bool = False) -> list[str]:
    candidate = with_result_set_identity(value)
    return validate_internal_structure(candidate, _index() if with_index else None)


def _fake_id(prefix: str, label: str) -> str:
    return f"{prefix}:" + hashlib.sha256(label.encode("utf-8")).hexdigest()


def _fake_contribution(label: str) -> dict:
    digest = hashlib.sha256((label + ":passage").encode("utf-8")).hexdigest()
    return {
        "contribution_id": _fake_id("contribution", label),
        "channel": "support",
        "evidence_ref": {
            "source_id": f"source-{label}",
            "passage_id": f"passage-{label}",
            "passage_sha256": f"sha256:{digest}",
        },
    }


def _replace_first_proposition(value: dict, proposition: dict) -> dict:
    candidate = copy.deepcopy(value)
    candidate["propositions"][0] = proposition
    return candidate


def _semantic_projection(value: dict) -> dict:
    projected = copy.deepcopy(value)
    projected.pop("result_set_id", None)
    projected["propositions"] = sorted(
        projected["propositions"], key=lambda item: item["proposition"]["proposition_id"]
    )
    for proposition in projected["propositions"]:
        proposition["contributions"] = sorted(
            proposition["contributions"], key=lambda item: item["contribution_id"]
        )
        conclusion = proposition.get("conclusion")
        if conclusion:
            conclusion["basis_members"] = sorted(
                conclusion["basis_members"], key=lambda item: (item["namespace"], item["id"])
            )
            conclusion["residual_contribution_ids"] = sorted(
                conclusion["residual_contribution_ids"]
            )
            conclusion["rule_roles"] = sorted(
                conclusion["rule_roles"], key=lambda item: item["rule_id"]
            )
        measurement = proposition.get("measurement")
        if measurement:
            measurement["basis_contribution_ids"] = sorted(
                measurement["basis_contribution_ids"]
            )
    return projected


def test_version_discovery_and_schema_agree() -> None:
    versions = parse_json_bytes(VERSIONS_PATH.read_bytes())
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert versions == {"canonical_version": "1.0.0", "supported_versions": ["1.0.0"]}
    assert CONTRACT_C_VERSION == "1.0.0"
    assert CONTRACT_C_SUPPORTED_VERSIONS == ("1.0.0",)
    assert schema["properties"]["contract_c_version"]["const"] == "1.0.0"
    assert schema["additionalProperties"] is False
    assert set(schema["required"]) == {
        "contract_c_version",
        "input",
        "producer",
        "execution",
        "propositions",
        "result_set_id",
    }


def test_frozen_valid_fixture_exact_binding_and_whole_hash() -> None:
    raw = VALID_PATH.read_bytes()
    expected = (FIXTURES / "valid-canonical.sha256").read_text().split()[0]
    errors = validate_contract_c_bytes(
        raw,
        expected_sha256=expected,
        contract_b_index=_index(),
    )
    assert errors == []
    value = parse_json_bytes(raw)
    assert value["input"]["contract_b"] == {
        "contract_version": "1.2.0",
        "bundle_id": "85f8f6dc-f46f-5efa-b7e7-6e049da84591",
        "bundle_hash": "sha256:a40fe687c19944248fe77d044801dca02bba56259198b297b897f6a5a304f2fa",
    }
    assert value["producer"]["semantic_implementation_sha"] == (
        "33a928db97316a3652d57df9cafb8ca240305233"
    )
    assert value["producer"]["policy"]["sha256"] == (
        "88f007c96f3acf63a191556fe7fa46b80b37e9fcb5224ec1e90fb626a061104d"
    )


def test_canonicalization_and_content_identity_are_strict() -> None:
    value = _valid()
    raw = VALID_PATH.read_bytes()
    assert raw == canonical_bytes(value)
    assert raw.endswith(b"\n") and not raw.endswith(b"\n\n")
    assert value["result_set_id"] == result_set_identity(value)

    pretty = (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    errors = validate_contract_c_bytes(pretty)
    assert any("non-canonical" in error for error in errors)

    changed = copy.deepcopy(value)
    changed["execution"]["state"] = "failed"
    assert any("result_set_id mismatch" in error for error in validate_internal_structure(changed))

    unicode_raw = canonical_bytes({"clé": "µ"})
    assert "µ".encode("utf-8") in unicode_raw
    assert b"\\u00b5" not in unicode_raw.lower()

    with pytest.raises(ValueError):
        parse_json_bytes(b'{"x":NaN}\n')
    with pytest.raises(ValueError):
        parse_json_bytes(b'{"x":1,"x":2}\n')


def test_exact_contract_b_proposition_and_evidence_reference_integrity() -> None:
    value = _valid()

    changed_binding = copy.deepcopy(value)
    changed_binding["input"]["contract_b"]["bundle_hash"] = "sha256:" + "0" * 64
    changed_binding = with_result_set_identity(changed_binding)
    assert not [e for e in validate_internal_structure(changed_binding) if "result_set_id" in e]
    assert any(
        "exact Contract-B binding" in error
        for error in validate_internal_structure(changed_binding, _index())
    )

    changed_claim = copy.deepcopy(value)
    changed_claim["propositions"][0]["proposition"]["text_sha256"] = "0" * 64
    changed_claim = with_result_set_identity(changed_claim)
    assert any(
        "proposition text hash mismatch" in error
        for error in validate_internal_structure(changed_claim, _index())
    )

    changed_passage = copy.deepcopy(value)
    changed_passage["propositions"][0]["contributions"][0]["evidence_ref"][
        "passage_sha256"
    ] = "sha256:" + "0" * 64
    changed_passage = with_result_set_identity(changed_passage)
    assert any(
        "evidence reference mismatch" in error
        for error in validate_internal_structure(changed_passage, _index())
    )


def test_policy_payload_is_hash_bound_not_config_name_bound() -> None:
    value = _valid()
    changed = copy.deepcopy(value)
    changed["producer"]["policy"]["canonical"]["needs_source_detection"] = False
    changed = with_result_set_identity(changed)
    errors = validate_internal_structure(changed)
    assert any("CAL policy hash mismatch" in error for error in errors)


def test_required_assessment_state_distinctions_round_trip() -> None:
    value = _valid()
    stage = value["propositions"][0]["assessments"]
    assert stage["eligibility"] == {"state": "not_performed"}

    cases = [
        {"state": "not_performed"},
        {"state": "performed", "value": "unknown"},
        {"state": "performed", "value": "adverse"},
        {"state": "not_applicable"},
        {"state": "failed"},
    ]
    observed = []
    for state in cases:
        candidate = copy.deepcopy(value)
        candidate["propositions"][0]["assessments"]["eligibility"] = state
        assert _errors(candidate) == []
        observed.append(canonical_bytes(with_result_set_identity(candidate)))
    assert len(set(observed)) == len(cases)

    missing = copy.deepcopy(value)
    del missing["propositions"][0]["assessments"]["eligibility"]
    assert any("eligibility" in error for error in _errors(missing))

    malformed = copy.deepcopy(value)
    malformed["propositions"][0]["assessments"]["eligibility"] = {"state": "unknown"}
    assert _errors(malformed)

    invalid_performed = copy.deepcopy(value)
    invalid_performed["propositions"][0]["assessments"]["eligibility"] = {
        "state": "performed"
    }
    assert _errors(invalid_performed)


def test_execution_failure_incomplete_and_early_return_remain_distinct_from_verdict() -> None:
    value = _valid()
    base_prop = copy.deepcopy(value["propositions"][0])

    failed = copy.deepcopy(base_prop)
    failed["execution"] = {"state": "failed"}
    failed["conclusion"] = None
    assert _errors(_replace_first_proposition(value, failed)) == []

    incomplete = copy.deepcopy(base_prop)
    incomplete["execution"] = {"state": "incomplete"}
    incomplete["conclusion"] = None
    assert _errors(_replace_first_proposition(value, incomplete)) == []

    not_checkable = copy.deepcopy(base_prop)
    not_checkable["execution"] = {"state": "completed", "completion": "not_checkable"}
    not_checkable["contributions"] = []
    not_checkable["measurement"] = None
    not_checkable["conclusion"] = {
        "reported_verdict": "not_checkable",
        "terminal_branch": "unclassified_early_return",
        "causal_form": "single_necessary",
        "basis_members": [{"namespace": "state", "id": "state:claim_type_unclassified"}],
        "residual_contribution_ids": [],
        "rule_roles": [],
    }
    assert _errors(_replace_first_proposition(value, not_checkable)) == []

    bad_failure = copy.deepcopy(failed)
    bad_failure["conclusion"] = copy.deepcopy(base_prop["conclusion"])
    assert _errors(_replace_first_proposition(value, bad_failure))

    assert canonical_bytes(with_result_set_identity(_replace_first_proposition(value, failed))) != canonical_bytes(
        with_result_set_identity(_replace_first_proposition(value, incomplete))
    )
    assert canonical_bytes(with_result_set_identity(_replace_first_proposition(value, failed))) != canonical_bytes(
        with_result_set_identity(_replace_first_proposition(value, not_checkable))
    )


def test_causal_multiplicity_and_co_maximal_basis_are_losslessly_representable() -> None:
    value = _valid()
    base_prop = copy.deepcopy(value["propositions"][0])
    a = _fake_contribution("tie-a")
    b = _fake_contribution("tie-b")

    independent = copy.deepcopy(base_prop)
    independent["contributions"] = [a, b]
    independent["measurement"] = {
        "kind": "cal_v0_2_aggregate_support_signal",
        "value": 0.8,
        "basis_contribution_ids": [a["contribution_id"], b["contribution_id"]],
    }
    independent["conclusion"] = {
        "reported_verdict": "supported",
        "terminal_branch": "supported_score_branch",
        "causal_form": "independent_sufficient_alternatives",
        "basis_members": [
            {"namespace": "contribution", "id": a["contribution_id"]},
            {"namespace": "contribution", "id": b["contribution_id"]},
        ],
        "residual_contribution_ids": [],
        "rule_roles": [],
    }
    independent_obj = with_result_set_identity(_replace_first_proposition(value, independent))
    assert validate_internal_structure(independent_obj) == []
    assert independent_obj["propositions"][0]["measurement"]["basis_contribution_ids"] == [
        a["contribution_id"],
        b["contribution_id"],
    ]

    joint = copy.deepcopy(base_prop)
    joint["contributions"] = []
    joint["measurement"] = None
    joint["conclusion"] = {
        "reported_verdict": "overstated",
        "terminal_branch": "overstated_rule_family",
        "causal_form": "jointly_sufficient",
        "basis_members": [
            {"namespace": "state", "id": "state:absolute_lexical_trigger"},
            {"namespace": "state", "id": "state:counterevidence_contexts_nonempty"},
        ],
        "residual_contribution_ids": [],
        "rule_roles": [
            {
                "rule_id": "rule-role:absolute:future_certainty",
                "code": "future_certainty",
                "terminal_role": "causal",
            },
            {
                "rule_id": "rule-role:absolute:overconfident_wording",
                "code": "overconfident_wording",
                "terminal_role": "causal",
            },
            {
                "rule_id": "rule-role:absolute:counterevidence_present",
                "code": "counterevidence_present",
                "terminal_role": "residual",
            },
        ],
    }
    joint_obj = with_result_set_identity(_replace_first_proposition(value, joint))
    assert validate_internal_structure(joint_obj) == []

    single = value["propositions"][0]["conclusion"]
    residual = value["propositions"][2]["conclusion"]
    assert single["causal_form"] == "single_necessary"
    assert len(single["basis_members"]) == 1
    assert residual["causal_form"] == "redundant_non_deciding"
    assert residual["basis_members"] == []
    assert residual["residual_contribution_ids"]

    false_single = copy.deepcopy(independent)
    false_single["conclusion"]["causal_form"] = "single_necessary"
    assert _errors(_replace_first_proposition(value, false_single))


def test_measurement_basis_and_residual_state_fail_closed_on_broken_refs() -> None:
    value = _valid()
    changed = copy.deepcopy(value)
    changed["propositions"][0]["measurement"]["basis_contribution_ids"] = [
        _fake_id("contribution", "missing")
    ]
    assert any("measurement basis" in error for error in _errors(changed))

    missing_residual = copy.deepcopy(value)
    missing_residual["propositions"][0]["conclusion"]["residual_contribution_ids"] = []
    assert any("every retained contribution" in error for error in _errors(missing_residual))


def test_coherent_residual_deletion_requires_normative_whole_object_hash() -> None:
    original = _valid()
    original_raw = VALID_PATH.read_bytes()
    original_sha = sha256_hex(original_raw)
    residual_id = original["propositions"][0]["conclusion"]["residual_contribution_ids"][0]

    deleted = copy.deepcopy(original)
    deleted["propositions"][0]["contributions"] = [
        item
        for item in deleted["propositions"][0]["contributions"]
        if item["contribution_id"] != residual_id
    ]
    deleted["propositions"][0]["conclusion"]["residual_contribution_ids"] = []
    deleted = with_result_set_identity(deleted)
    deleted_raw = canonical_bytes(deleted)

    assert validate_internal_structure(deleted, _index()) == []
    assert validate_whole_object_hash(deleted_raw, original_sha)
    assert sha256_hex(deleted_raw) != original_sha


def test_array_order_can_be_semantically_invariant_while_byte_identity_changes() -> None:
    original = _valid()
    reordered = copy.deepcopy(original)
    reordered["propositions"] = list(reversed(reordered["propositions"]))
    reordered = with_result_set_identity(reordered)

    assert validate_internal_structure(reordered, _index()) == []
    assert _semantic_projection(reordered) == _semantic_projection(original)
    assert canonical_bytes(reordered) != canonical_bytes(original)
    assert reordered["result_set_id"] != original["result_set_id"]
    assert sha256_hex(canonical_bytes(reordered)) != sha256_hex(canonical_bytes(original))


def test_downstream_policy_firewall_and_exact_version_unknown_field_rejection() -> None:
    value = _valid()
    raw = VALID_PATH.read_bytes()
    before = sha256_hex(raw)
    downstream_a = {"materiality": 0.2, "route": "hold"}
    downstream_b = {"materiality": 0.9, "route": "escalate"}
    assert downstream_a != downstream_b
    assert sha256_hex(raw) == before
    assert parse_json_bytes(raw) == value

    leaked = copy.deepcopy(value)
    leaked["destination_policy"] = downstream_a
    leaked = with_result_set_identity(leaked)
    assert any("destination_policy" in error for error in validate_internal_structure(leaked))

    nested_unknown = copy.deepcopy(value)
    nested_unknown["propositions"][0]["execution"]["reason"] = "presentation-only"
    nested_unknown = with_result_set_identity(nested_unknown)
    assert any("reason" in error for error in validate_internal_structure(nested_unknown))


def test_result_set_execution_state_is_separate_and_distinct() -> None:
    value = _valid()
    raws = []
    for state in ("completed", "failed", "incomplete"):
        candidate = copy.deepcopy(value)
        candidate["execution"] = {"state": state}
        candidate = with_result_set_identity(candidate)
        assert validate_internal_structure(candidate) == []
        raws.append(canonical_bytes(candidate))
    assert len(set(raws)) == 3


def test_full_policy_payload_is_retained_until_durable_promoted_resolution_exists() -> None:
    value = _valid()
    policy = value["producer"]["policy"]
    assert policy["canonical"]
    assert policy["sha256"] == sha256_hex(canonical_bytes(policy["canonical"]))


def test_reference_schema_can_validate_the_frozen_model_shape() -> None:
    value = _valid()
    model = ContractCResultSet.model_validate(value)
    round_trip = model.model_dump(mode="json")
    assert round_trip == value


def test_frozen_conformance_manifest_covers_every_promotion_control() -> None:
    manifest = parse_json_bytes((FIXTURES / "conformance-manifest.json").read_bytes())
    assert manifest["source_lineage"]["apparatus_handoff_commit"] == (
        "213ed9e912b922bd5c57ef58009eb6b0d7fff398"
    )
    assert manifest["source_lineage"]["cal_rc2d_receipt_sha256"] == (
        "a953a14b8bf9a5bd9cf9060e7fb58c868df9b15c8b578d88f13a1090c4eca5fa"
    )
    assert manifest["compression"]["source_candidate_sha256"] == (
        "e142f4aab119751dc201bca7994c0f97636c65647489f7edbee823a7f8aee3b4"
    )
    assert manifest["compression"]["source_candidate_canonical_bytes"] == 5868
    assert manifest["canonical_fixture"]["canonical_bytes"] == len(VALID_PATH.read_bytes()) == 4968
    assert manifest["compression"]["diagnostic_byte_reduction"] == 900
    assert manifest["canonical_fixture"]["sha256"] == sha256_hex(VALID_PATH.read_bytes())
    expected_controls = {
        "valid_canonical_v1",
        "exact_contract_b_binding",
        "proposition_evidence_reference_integrity",
        "assessment_state_distinctions",
        "malformed_missing_fail_closed",
        "execution_failure_incomplete_not_checkable",
        "causal_multiplicity_preservation",
        "residual_state_preservation",
        "aggregate_measurement_basis_preservation",
        "coherent_deletion_whole_hash",
        "array_order_semantic_vs_byte_identity",
        "downstream_policy_firewall",
        "exact_v1_unknown_field_rejection",
        "policy_hash_binding",
        "lossless_compression_map",
    }
    assert set(manifest["required_controls"]) == expected_controls
    assert len(manifest["invariant_map"]) == 11
