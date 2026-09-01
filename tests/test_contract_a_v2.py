from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from validators import contract_a
from validators import contract_a_rc2 as frozen

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures" / "contract-a" / "2.0.0"

VALID = [
    "valid-all-of.json",
    "valid-failed-decomposition.json",
    "valid-undecomposed.json",
    "valid-unknown-decomposition.json",
]
INVALID = [
    "invalid-forbidden-semantic-field.json",
    "invalid-missing-proposition-id.json",
    "invalid-source-content-hash.json",
]


def load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def reseal(obj: dict) -> dict:
    out = copy.deepcopy(obj)
    out["handoff_sha256"] = contract_a.compute_handoff_sha256(out)
    return out


def test_public_version_routes_to_exact_frozen_engine() -> None:
    assert contract_a.CONTRACT_A_VERSION == "2.0.0"
    assert contract_a.WIRE_SCHEMA_TOKEN == "contract-a-wire-candidate-rc2"
    assert contract_a.validate_candidate is frozen.validate_candidate
    assert contract_a.compute_handoff_sha256 is frozen.compute_handoff_sha256
    assert contract_a.load_candidate is frozen.load_candidate
    assert contract_a.ContractAValidationError is frozen.CandidateValidationError


def test_version_registry_and_schema_token_agree() -> None:
    versions = json.loads((ROOT / "schema" / "contract-a" / "versions.json").read_text())
    assert versions["canonical_version"] == "2.0.0"
    assert versions["supported_versions"] == ["2.0.0"]
    assert versions["wire_schema_token"] == contract_a.WIRE_SCHEMA_TOKEN
    assert versions["legacy_authority"]["version"] == "1.0.0"
    assert versions["legacy_authority"]["status"] == "immutable_historical_major_version"
    schema = json.loads((ROOT / "schema" / "contract-a" / "2.0.0" / "schema.json").read_text())
    assert schema["properties"]["schema"]["const"] == contract_a.WIRE_SCHEMA_TOKEN


@pytest.mark.parametrize("name", VALID)
def test_frozen_valid_fixtures_accept(name: str) -> None:
    obj = load(name)
    assert contract_a.validate_candidate(obj) is obj
    assert contract_a.compute_handoff_sha256(obj) == obj["handoff_sha256"]


@pytest.mark.parametrize("name", INVALID)
def test_frozen_invalid_fixtures_reject(name: str) -> None:
    with pytest.raises(contract_a.ContractAValidationError):
        contract_a.validate_candidate(load(name))


def test_bound_identity_substitution_requires_fresh_reseal() -> None:
    for path, new_value in [
        (("handoff_id",), "different-handoff"),
        (("work", "work_id"), "different-work"),
        (("root_proposition", "proposition_id"), "different-root"),
        (("sources", 0, "source_id"), "different-source"),
    ]:
        obj = load("valid-all-of.json")
        target = obj
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = new_value
        with pytest.raises(contract_a.ContractAValidationError):
            contract_a.validate_candidate(obj)
        contract_a.validate_candidate(reseal(obj))


def test_text_and_source_bytes_cannot_be_resealed_over_stale_inner_hashes() -> None:
    obj = load("valid-all-of.json")
    obj["root_proposition"]["text"] += " changed"
    with pytest.raises(contract_a.ContractAValidationError):
        contract_a.validate_candidate(reseal(obj))

    obj = load("valid-all-of.json")
    obj["decomposition"]["children"][0]["text"] += " changed"
    with pytest.raises(contract_a.ContractAValidationError):
        contract_a.validate_candidate(reseal(obj))

    obj = load("valid-all-of.json")
    obj["sources"][0]["content"] += " changed"
    with pytest.raises(contract_a.ContractAValidationError):
        contract_a.validate_candidate(reseal(obj))


def test_decomposition_order_and_operator_fail_closed() -> None:
    obj = load("valid-all-of.json")
    obj["decomposition"]["operator"] = "any_of"
    with pytest.raises(contract_a.ContractAValidationError):
        contract_a.validate_candidate(reseal(obj))

    obj = load("valid-all-of.json")
    obj["decomposition"]["children"][1]["sequence"] = 3
    with pytest.raises(contract_a.ContractAValidationError):
        contract_a.validate_candidate(reseal(obj))

    obj = load("valid-all-of.json")
    children = list(reversed(obj["decomposition"]["children"]))
    for i, child in enumerate(children, 1):
        child["sequence"] = i
    obj["decomposition"]["children"] = children
    changed = reseal(obj)
    contract_a.validate_candidate(changed)
    assert changed["handoff_sha256"] != load("valid-all-of.json")["handoff_sha256"]


def test_missing_and_explicit_empty_sources_are_distinct() -> None:
    obj = load("valid-undecomposed.json")
    del obj["sources"]
    with pytest.raises(contract_a.ContractAValidationError):
        contract_a.validate_candidate(reseal(obj))

    obj = load("valid-undecomposed.json")
    obj["sources"] = []
    contract_a.validate_candidate(reseal(obj))


def test_semantic_looking_fields_cannot_enter_contract_a_authority() -> None:
    names = ["support_status", "confidence", "trust_level", "retrieval_rank", "authorization"]
    for name in names:
        obj = load("valid-undecomposed.json")
        obj[name] = "not-contract-a-authority"
        with pytest.raises(contract_a.ContractAValidationError):
            contract_a.validate_candidate(reseal(obj))


def test_canonical_wrapper_preserves_authority_boundary() -> None:
    spec = (ROOT / "contract-a-v2.0.0.md").read_text()
    assert "contract-a-wire-candidate-rc2" in spec
    assert "operational Authorization" in spec
    assert "major compatibility boundary" in spec
    assert "byte-identical" in spec
    assert "Contract E" in spec
