from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

from contract_d_consume import ApplicabilityExpectation, consume

VALID = json.loads((HERE / "fixtures" / "valid.json").read_text())["fixtures"]


def base():
    return copy.deepcopy(VALID["source-audit-clear.json"])


def expectation(d):
    return ApplicabilityExpectation(
        copy.deepcopy(d["input_authority"]),
        copy.deepcopy(d["policy"]),
        copy.deepcopy(d["target"]),
        d["effect"]["type"],
        None,
    )


def assert_invalid(d, e):
    got = consume(d, e)
    assert got["outcome"] == "cannot_establish"
    assert got["reason"] == "invalid_expectation"


def test_host_only_requested_parameter_value_is_invalid_expectation():
    d = base()
    e = expectation(d)
    object.__setattr__(e, "effect_params", {"scope": {"claim"}})
    assert_invalid(d, e)


def test_nonfinite_requested_parameter_value_is_invalid_expectation():
    d = base()
    e = expectation(d)
    object.__setattr__(e, "effect_params", {"scope": float("nan")})
    assert_invalid(d, e)


def test_unpaired_surrogate_requested_operation_is_invalid_expectation():
    d = base()
    e = expectation(d)
    object.__setattr__(e, "requested_operation", "knowledge.add_verified_tag\ud800")
    assert_invalid(d, e)


def test_malformed_expected_target_hash_is_invalid_expectation():
    d = base()
    e = expectation(d)
    e.target["content_sha256"] = "not-a-sha256"
    assert_invalid(d, e)
