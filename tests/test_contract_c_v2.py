from __future__ import annotations

import copy
import importlib.util
import shutil
import sys
from pathlib import Path
from types import ModuleType

import pytest

from validators import contract_c_v2 as PROD

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "schema" / "contract-c" / "2.0.0" / "reference"


def _load_frozen_rc2(tmp_path: Path) -> ModuleType:
    rc1_dir = tmp_path / "research" / "contract_c_successor_candidate_a_rc1_20260913"
    rc2_dir = tmp_path / "research" / "contract_c_successor_candidate_a_rc2_20260913"
    rc1_dir.mkdir(parents=True)
    rc2_dir.mkdir(parents=True)
    shutil.copyfile(REFERENCE / "candidate_a_rc1.py", rc1_dir / "candidate_a_rc1.py")
    shutil.copyfile(REFERENCE / "candidate_a_rc2.py", rc2_dir / "candidate_a_rc2.py")

    spec = importlib.util.spec_from_file_location(
        "contract_c_v2_frozen_reference", rc2_dir / "candidate_a_rc2.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _base(module: ModuleType) -> dict:
    return {
        "profile": module.PROFILE,
        "contract_b": {
            "contract_version": "1.2.0",
            "bundle_id": "bundle-c2-test",
            "bundle_hash": "sha256:" + "1" * 64,
        },
        "producer": {
            "semantic_implementation_sha": module.CAL_RC1_IMPLEMENTATION,
            "policy_sha256": module.CAL_RC1_POLICY_SHA256,
            "policy_resolver_commit_sha": module.POLICY_RESOLVER_FIXTURE_COMMIT,
        },
        "execution": {"state": "completed"},
        "propositions": [],
    }


def _participant(symbol: str, relation: str, role: str = "causal") -> dict:
    return {
        "evidence_ref": {"source_id": f"src-{symbol}", "passage_id": symbol},
        "relation": relation,
        "role": role,
    }


def _ref(symbol: str) -> dict:
    return {"source_id": f"src-{symbol}", "passage_id": symbol}


def _supported(module: ModuleType) -> dict:
    value = _base(module)
    value["propositions"] = [
        {
            "proposition": {
                "proposition_id": "Q-support",
                "content_sha256": "sha256:" + "2" * 64,
            },
            "execution": {"state": "completed", "completion": "assessed"},
            "terminal": {"verdict": "supported", "reason": "categorical_support"},
            "participants": [_participant("S1", "supports")],
            "basis_groups": [[_ref("S1")]],
        }
    ]
    return module.seal(value)


def _mixed_alternatives(module: ModuleType) -> dict:
    value = _base(module)
    value["propositions"] = [
        {
            "proposition": {
                "proposition_id": "Q-mixed",
                "content_sha256": "sha256:" + "3" * 64,
            },
            "execution": {"state": "completed", "completion": "not_checkable"},
            "terminal": {"verdict": "not_checkable", "reason": "MIXED_RELATIONS"},
            "participants": [
                _participant("S2", "supports"),
                _participant("R1", "refutes"),
                _participant("S1", "supports"),
            ],
            "basis_groups": [
                [_ref("S2"), _ref("R1")],
                [_ref("S1"), _ref("R1")],
            ],
        }
    ]
    return module.seal(value)


def _unsupported(module: ModuleType) -> dict:
    value = _base(module)
    value["propositions"] = [
        {
            "proposition": {
                "proposition_id": "Q-unsupported",
                "content_sha256": "sha256:" + "4" * 64,
            },
            "execution": {"state": "completed", "completion": "not_checkable"},
            "terminal": {
                "verdict": "not_checkable",
                "reason": "UNSUPPORTED_SEMANTIC_FAMILY",
            },
            "participants": [_participant("U1", "non_polarized", "residual")],
            "basis_groups": [],
        }
    ]
    return module.seal(value)


def _assert_rejected_by_both(frozen: ModuleType, value: dict) -> None:
    with pytest.raises(PROD.ContractCValidationError):
        PROD.validate_object(value)
    with pytest.raises(frozen.CandidateError):
        frozen.validate_object(value)


@pytest.mark.parametrize("builder", [_supported, _mixed_alternatives, _unsupported])
def test_production_adapter_matches_frozen_rc2_bytes_and_identity(tmp_path: Path, builder) -> None:
    frozen = _load_frozen_rc2(tmp_path)
    reference = builder(frozen)
    production = builder(PROD)

    frozen.validate_object(reference)
    PROD.validate_object(production)

    assert production == reference
    assert PROD.canonical_bytes(production) == frozen.canonical_bytes(reference)
    assert PROD.whole_object_sha256(production) == frozen.whole_object_sha256(reference)
    assert production["result_set_id"] == reference["result_set_id"]


def test_permutation_canonicalization_matches_frozen_rc2(tmp_path: Path) -> None:
    frozen = _load_frozen_rc2(tmp_path)
    value = _mixed_alternatives(PROD)
    mutated = copy.deepcopy(value)
    mutated.pop("result_set_id")
    mutated["propositions"][0]["participants"].reverse()
    mutated["propositions"][0]["basis_groups"].reverse()
    for group in mutated["propositions"][0]["basis_groups"]:
        group.reverse()

    assert PROD.seal(mutated) == value

    frozen_value = _mixed_alternatives(frozen)
    frozen_mutated = copy.deepcopy(frozen_value)
    frozen_mutated.pop("result_set_id")
    frozen_mutated["propositions"][0]["participants"].reverse()
    frozen_mutated["propositions"][0]["basis_groups"].reverse()
    for group in frozen_mutated["propositions"][0]["basis_groups"]:
        group.reverse()
    assert frozen.seal(frozen_mutated) == frozen_value


def test_exact_mixed_reason_case_is_fail_closed(tmp_path: Path) -> None:
    frozen = _load_frozen_rc2(tmp_path)
    value = _mixed_alternatives(PROD)
    bad = copy.deepcopy(value)
    bad.pop("result_set_id")
    bad["propositions"][0]["terminal"]["reason"] = "mixed_relations"
    bad = PROD.seal(bad)

    _assert_rejected_by_both(frozen, bad)


def test_unsupported_family_cannot_acquire_causal_basis(tmp_path: Path) -> None:
    frozen = _load_frozen_rc2(tmp_path)
    value = _unsupported(PROD)
    bad = copy.deepcopy(value)
    bad.pop("result_set_id")
    prop = bad["propositions"][0]
    prop["participants"][0]["relation"] = "supports"
    prop["participants"][0]["role"] = "causal"
    prop["basis_groups"] = [[_ref("U1")]]
    bad = PROD.seal(bad)

    _assert_rejected_by_both(frozen, bad)


def test_wrong_wire_profile_is_rejected(tmp_path: Path) -> None:
    frozen = _load_frozen_rc2(tmp_path)
    value = _supported(PROD)
    bad = copy.deepcopy(value)
    bad.pop("result_set_id")
    bad["profile"] = "2.0.0"
    bad = PROD.seal(bad)

    _assert_rejected_by_both(frozen, bad)


def test_external_authority_mismatch_is_rejected() -> None:
    value = _supported(PROD)
    with pytest.raises(PROD.ContractCValidationError):
        PROD.verify_external_authority(
            value, expected_whole_object_sha256="sha256:" + "0" * 64
        )


def test_public_version_is_external_to_frozen_wire_profile() -> None:
    assert PROD.CONTRACT_C_VERSION == "2.0.0"
    assert PROD.WIRE_PROFILE == "contract-c-successor-candidate-a-rc2-research"
    assert PROD.WIRE_PROFILE != PROD.CONTRACT_C_VERSION
