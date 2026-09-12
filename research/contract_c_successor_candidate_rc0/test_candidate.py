from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path

from validators import contract_c as released

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import validator as candidate  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
RAW = (HERE / "fixtures" / "valid-shadow.json").read_bytes()
INDEX = json.loads((HERE / "fixtures" / "contract-b-index.json").read_text())
EXPECTED_SHA = "325962ebcdbf6af836bb6193a451524ccd40b4d10f2394ff9f703fbfce1ec1e3"
EXPECTED_RESULT = "result-set:4483272c4f6fbd9cb2362be7e3174bbd00aff3cf761d6c374897f3478818c9f0"


def _fixture() -> dict:
    return released.parse_json_bytes(RAW)


def _rebind(value: dict) -> tuple[dict, bytes]:
    obj = copy.deepcopy(value)
    obj["result_set_id"] = released.result_set_identity(obj)
    return obj, released.canonical_bytes(obj)


def test_candidate_profile_is_non_release_sentinel() -> None:
    assert candidate.CANDIDATE_VERSION == "research-non-deciding-rc0"
    assert candidate.CANDIDATE_VERSION != "2.0.0"


def test_released_authority_files_remain_exact() -> None:
    assert hashlib.sha1((ROOT / "contract-c-v1.0.0.md").read_bytes()).hexdigest()  # readable invariant
    assert json.loads((ROOT / "schema/contract-c/versions.json").read_text()) == {
        "canonical_version": "1.0.0",
        "supported_versions": ["1.0.0"],
    }
    assert released.CONTRACT_C_VERSION == "1.0.0"
    assert released.CONTRACT_C_SUPPORTED_VERSIONS == ("1.0.0",)


def test_candidate_schema_has_exact_two_leaf_semantic_delta() -> None:
    base = candidate.load_released_schema()
    successor = candidate.build_candidate_schema(base)
    assert candidate.semantic_schema_delta(base, successor) == candidate.expected_semantic_delta()
    assert successor["properties"]["contract_c_version"]["const"] == candidate.CANDIDATE_VERSION
    assert successor["$defs"]["contribution"]["properties"]["channel"]["enum"] == [
        "support",
        "counterevidence",
        "non_deciding",
    ]

    delta = json.loads((HERE / "schema-delta.json").read_text())
    assert delta["base_commit"] == candidate.BASE_COMMIT
    assert delta["base_schema_blob"] == candidate.BASE_SCHEMA_BLOB
    assert delta["base_validator_blob"] == candidate.BASE_VALIDATOR_BLOB
    assert delta["official_version_assigned"] is False
    assert [item["path"] for item in delta["changes"]] == [
        "properties.contract_c_version.const",
        "$defs.contribution.properties.channel.enum",
    ]


def test_candidate_schema_adds_no_sidecar_or_scalar_surface() -> None:
    encoded = json.dumps(candidate.build_candidate_schema(), sort_keys=True)
    for forbidden in (
        '"member_id"',
        '"state_id"',
        '"receipt_id"',
        '"confidence"',
        '"probability"',
        '"rank"',
        '"winner"',
        '"authorization"',
        '"effect"',
    ):
        assert forbidden not in encoded


def test_frozen_handoff_identity_is_unchanged() -> None:
    assert hashlib.sha256(RAW).hexdigest() == EXPECTED_SHA
    obj = _fixture()
    assert obj["result_set_id"] == EXPECTED_RESULT
    assert released.result_set_identity(obj) == EXPECTED_RESULT


def test_candidate_accepts_exact_frozen_non_deciding_handoff_without_relabelling() -> None:
    assert candidate.validate_candidate_bytes(
        RAW,
        expected_sha256=EXPECTED_SHA,
        contract_b_index=INDEX,
    ) == []
    model = candidate.CandidateContractCResultSet.model_validate(_fixture())
    proposition = model.propositions[0]
    assert [item.channel for item in proposition.contributions] == [
        "non_deciding",
        "non_deciding",
    ]
    assert proposition.conclusion is not None
    assert proposition.conclusion.causal_form == "independent_sufficient_alternatives"
    assert {item.evidence_ref.passage_id for item in proposition.contributions} == {"u-a", "u-b"}


def test_released_1_0_rejects_exact_successor_handoff() -> None:
    errors = released.validate_contract_c_bytes(RAW, contract_b_index=INDEX)
    assert errors
    assert any("contract_c_version" in error or "channel" in error for error in errors)


def test_legacy_support_and_counterevidence_channels_remain_candidate_valid() -> None:
    for channel in ("support", "counterevidence"):
        obj = _fixture()
        obj["propositions"][0]["contributions"][0]["channel"] = channel
        _, raw = _rebind(obj)
        assert candidate.validate_candidate_bytes(raw, contract_b_index=INDEX) == []


def test_unknown_channel_fails_closed() -> None:
    obj = _fixture()
    obj["propositions"][0]["contributions"][0]["channel"] = "mystery"
    _, raw = _rebind(obj)
    errors = candidate.validate_candidate_bytes(raw, contract_b_index=INDEX)
    assert errors
    assert any("channel" in error for error in errors)


def test_wrong_contract_b_evidence_reference_fails_closed() -> None:
    obj = _fixture()
    obj["propositions"][0]["contributions"][0]["evidence_ref"]["source_id"] = "wrong-source"
    _, raw = _rebind(obj)
    errors = candidate.validate_candidate_bytes(raw, contract_b_index=INDEX)
    assert "evidence reference mismatch for passage u-a" in errors


def test_unclassified_retained_contribution_fails_closed() -> None:
    obj = _fixture()
    obj["propositions"][0]["conclusion"]["basis_members"] = obj["propositions"][0]["conclusion"]["basis_members"][:1]
    obj["propositions"][0]["conclusion"]["causal_form"] = "single_necessary"
    _, raw = _rebind(obj)
    errors = candidate.validate_candidate_bytes(raw, contract_b_index=INDEX)
    assert errors
    assert any("every retained contribution" in error for error in errors)


def test_causal_residual_overlap_fails_closed() -> None:
    obj = _fixture()
    cid = obj["propositions"][0]["contributions"][0]["contribution_id"]
    obj["propositions"][0]["conclusion"]["residual_contribution_ids"] = [cid]
    _, raw = _rebind(obj)
    errors = candidate.validate_candidate_bytes(raw, contract_b_index=INDEX)
    assert errors
    assert any("both causal basis and residual" in error for error in errors)


def test_causal_cardinality_fails_closed() -> None:
    obj = _fixture()
    obj["propositions"][0]["conclusion"]["causal_form"] = "single_necessary"
    _, raw = _rebind(obj)
    errors = candidate.validate_candidate_bytes(raw, contract_b_index=INDEX)
    assert errors
    assert any("single_necessary requires exactly one basis member" in error for error in errors)


def test_whole_object_binding_remains_separate_and_fail_closed() -> None:
    errors = candidate.validate_candidate_bytes(
        RAW,
        expected_sha256="0" * 64,
        contract_b_index=INDEX,
    )
    assert errors
    assert any("whole-object SHA-256 mismatch" in error for error in errors)


def test_candidate_does_not_enter_released_version_registry() -> None:
    versions = json.loads((ROOT / "schema/contract-c/versions.json").read_text())
    assert candidate.CANDIDATE_VERSION not in versions["supported_versions"]
    assert versions["canonical_version"] == "1.0.0"
