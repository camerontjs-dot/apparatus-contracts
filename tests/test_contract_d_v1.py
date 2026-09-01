from __future__ import annotations

import copy
import json
import math
import struct
from pathlib import Path

import pytest

from validators.contract_d_consume import ApplicabilityExpectation, consume
from validators.contract_d_core import (
    ContractDError,
    MAX_JSON_CONTAINER_DEPTH,
    SAFE_INTEGER_MAX,
    canonical_json_bytes,
    semantic_identity,
    semantic_projection,
    validate_decision,
    validate_effect,
)
from validators.contract_d_validate import parse_json_bytes, require_canonical_bytes

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures" / "contract-d" / "1.0.0"
VALID = json.loads((FIXTURES / "valid.json").read_text())["fixtures"]
INVALID = json.loads((FIXTURES / "invalid.json").read_text())["fixtures"]


def load(name: str):
    return copy.deepcopy(VALID[name])


def exp(d, op=None, params=None):
    return ApplicabilityExpectation(
        copy.deepcopy(d["input_authority"]),
        copy.deepcopy(d["policy"]),
        copy.deepcopy(d["target"]),
        op or d.get("effect", {}).get("type", "knowledge.add_verified_tag"),
        params,
    )


@pytest.mark.parametrize("name", sorted(VALID))
def test_valid_fixtures(name):
    d = load(name)
    validate_decision(d)
    assert require_canonical_bytes(canonical_json_bytes(d)) == d


@pytest.mark.parametrize("name", sorted(INVALID))
def test_invalid_fixtures(name):
    with pytest.raises(ContractDError):
        validate_decision(copy.deepcopy(INVALID[name]))


def test_exact_version_future_numeric_and_case_fail_closed():
    d = load("source-audit-clear.json")
    for version in ("1.0.1", "1.1.0", "V1.0.0", 1.0):
        x = copy.deepcopy(d)
        x["contract_d_version"] = version
        with pytest.raises(ContractDError, match="unknown_contract_version"):
            validate_decision(x)


def test_state_controls():
    for name in ("source-audit-clear.json", "citation-use-clear.json", "task-dispatch-clear.json"):
        d = load(name)
        assert consume(d, exp(d))["outcome"] == "candidate_for_authorization"
    hold = load("completed-hold.json")
    failed = load("evaluation-failed.json")
    assert consume(hold, exp(hold))["outcome"] == "hold"
    assert consume(failed, exp(failed))["outcome"] == "evaluation_failed"
    assert semantic_identity(hold) != semantic_identity(failed)


def test_hold_still_binds_effect_and_request():
    hold = load("completed-hold.json")
    assert consume(hold, exp(hold, op="task.dispatch"))["outcome"] == "not_applicable"
    assert consume(hold, exp(hold, params={"scope": "object"}))["outcome"] == "not_applicable"
    assert consume(hold, exp(hold))["outcome"] == "hold"


def test_omitted_external_params_are_unconstrained():
    d = load("source-audit-object-scope-clear.json")
    assert consume(d, exp(d, params=None))["outcome"] == "candidate_for_authorization"
    assert consume(d, exp(d, params={}))["outcome"] == "candidate_for_authorization"
    assert consume(d, exp(d, params={"scope": "claim"}))["outcome"] == "not_applicable"
    assert consume(d, exp(d, params={"scope": "object"}))["outcome"] == "candidate_for_authorization"


@pytest.mark.parametrize(
    ("fixture_name", "effect_type"),
    [("citation-use-clear.json", "knowledge.cite_as_evidence"), ("task-dispatch-clear.json", "task.dispatch")],
)
def test_empty_schema_effect_total_shape_and_identity(fixture_name, effect_type):
    decision = load(fixture_name)
    omitted = copy.deepcopy(decision)
    explicit = copy.deepcopy(decision)
    explicit["effect"]["params"] = {}
    expected = {"type": effect_type, "version": "1", "params": {}}
    assert validate_effect(omitted["effect"]) == expected
    assert validate_effect(explicit["effect"]) == expected
    assert set(validate_effect(omitted["effect"])) == {"type", "version", "params"}
    assert semantic_projection(omitted)["effect"] == expected
    assert semantic_projection(explicit)["effect"] == expected
    assert semantic_identity(omitted) == semantic_identity(explicit)


def test_defaulted_effect_total_shape_and_object_scope_distinct():
    claim = load("source-audit-clear.json")
    omitted = copy.deepcopy(claim)
    omitted["effect"].pop("params")
    empty = copy.deepcopy(claim)
    empty["effect"]["params"] = {}
    explicit = copy.deepcopy(claim)
    explicit["effect"]["params"] = {"scope": "claim"}
    expected = {"type": "knowledge.add_verified_tag", "version": "1", "params": {"scope": "claim"}}
    for candidate in (omitted, empty, explicit):
        assert validate_effect(candidate["effect"]) == expected
        assert semantic_projection(candidate)["effect"] == expected
    assert len({semantic_identity(x) for x in (omitted, empty, explicit)}) == 1
    obj = load("source-audit-object-scope-clear.json")
    assert semantic_projection(obj)["effect"]["params"] == {"scope": "object"}
    assert semantic_identity(claim) != semantic_identity(obj)


def test_json_ingress_and_host_values_fail_closed():
    d = load("source-audit-clear.json")
    x = copy.deepcopy(d)
    x["metadata"]["diagnostics"] = {"bad": {1, 2}}
    with pytest.raises(ContractDError, match="non_json_value"):
        validate_decision(x)
    x = copy.deepcopy(d)
    x["metadata"]["diagnostics"] = {1: "bad-key"}
    with pytest.raises(ContractDError, match="non_json_object_key"):
        validate_decision(x)
    x = copy.deepcopy(d)
    x["metadata"]["diagnostics"] = {"n": math.inf}
    with pytest.raises(ContractDError, match="non_finite_number"):
        validate_decision(x)
    with pytest.raises(ContractDError, match="invalid_utf8"):
        parse_json_bytes(b"\xff")
    with pytest.raises(ContractDError, match="duplicate_json_key"):
        parse_json_bytes(b'{"contract_d_version":"1.0.0","contract_d_version":"1.0.0"}')


def test_cycles_shared_acyclic_and_unicode():
    base = load("source-audit-clear.json")
    cycle = {}
    cycle["self"] = cycle
    d = copy.deepcopy(base)
    d["metadata"]["diagnostics"] = cycle
    with pytest.raises(ContractDError, match="non_json_value"):
        validate_decision(d)
    left = []
    right = {"left": left}
    left.append(right)
    d = copy.deepcopy(base)
    d["metadata"]["diagnostics"] = {"cycle": left}
    with pytest.raises(ContractDError, match="non_json_value"):
        validate_decision(d)
    shared = {"values": [1, 2, 3]}
    d = copy.deepcopy(base)
    d["metadata"]["diagnostics"] = {"a": shared, "b": shared}
    validate_decision(d)
    d = copy.deepcopy(base)
    d["metadata"]["diagnostics"] = {"bad": "\ud800"}
    with pytest.raises(ContractDError, match="invalid_unicode_scalar"):
        validate_decision(d)


def _nested_lists(count: int):
    x = "leaf"
    for _ in range(count):
        x = [x]
    return x


def test_depth_boundary_and_controlled_failure():
    accepted = load("source-audit-clear.json")
    accepted["metadata"]["diagnostics"] = {"deep": _nested_lists(MAX_JSON_CONTAINER_DEPTH - 3)}
    validate_decision(accepted)
    canonical_json_bytes(accepted)
    assert consume(accepted, exp(accepted))["outcome"] == "candidate_for_authorization"
    rejected = load("source-audit-clear.json")
    rejected["metadata"]["diagnostics"] = {"deep": _nested_lists(MAX_JSON_CONTAINER_DEPTH - 2)}
    with pytest.raises(ContractDError, match="json_depth_exceeded"):
        validate_decision(rejected)
    got = consume(rejected, exp(load("source-audit-clear.json")))
    assert got == {"outcome": "cannot_establish", "reason": "json_depth_exceeded"}
    very_deep = load("source-audit-clear.json")
    very_deep["metadata"]["diagnostics"] = {"deep": _nested_lists(1200)}
    with pytest.raises(ContractDError, match="json_depth_exceeded"):
        validate_decision(very_deep)


def test_malformed_external_expectations_fail_closed():
    d = load("source-audit-clear.json")
    extra = exp(d)
    extra.target["extra"] = "x"
    assert consume(d, extra)["reason"] == "invalid_expectation"
    malformed = exp(d)
    object.__setattr__(malformed, "effect_params", [])
    assert consume(d, malformed)["reason"] == "invalid_expectation"
    malformed = exp(d)
    object.__setattr__(malformed, "effect_params", {"scope": float("nan")})
    assert consume(d, malformed)["reason"] == "invalid_expectation"


def test_replay_substitution_controls():
    d = load("source-audit-clear.json")
    variants = []
    e = exp(d); e.input_authority["immutable_id"] = "result-set:" + "9" * 64; variants.append(e)
    e = exp(d); e.policy["version"] = "2"; variants.append(e)
    e = exp(d); e.target["content_sha256"] = "sha256:" + "2" * 64; variants.append(e)
    e = exp(d, op="task.dispatch"); variants.append(e)
    for candidate in variants:
        assert consume(d, candidate)["outcome"] == "not_applicable"


def test_metadata_and_authorization_firewall():
    d = load("source-audit-clear.json")
    identity = semantic_identity(d)
    x = copy.deepcopy(d)
    x["metadata"]["diagnostics"] = {"actor": "root", "approval": True, "delegation": "yes"}
    assert semantic_identity(x) == identity
    x = copy.deepcopy(d)
    x["actor"] = "root"
    with pytest.raises(ContractDError, match="unknown_field"):
        validate_decision(x)


def test_conformance_cases():
    corpus = json.loads((FIXTURES / "conformance-cases.json").read_text())
    for case in corpus["cases"]:
        d = load(case["decision_fixture"])
        e = case["expect"]
        got = consume(d, ApplicabilityExpectation(e["input_authority"], e["policy"], e["target"], e["requested_operation"], e.get("effect_params")))
        assert got["outcome"] == case["outcome"], case["id"]


def f64(hex_bits: str) -> float:
    return struct.unpack(">d", bytes.fromhex(hex_bits))[0]


@pytest.mark.parametrize(
    ("bits", "expected"),
    [
        ("0000000000000000", "0"), ("8000000000000000", "0"),
        ("0000000000000001", "5e-324"), ("8000000000000001", "-5e-324"),
        ("7fefffffffffffff", "1.7976931348623157e+308"), ("ffefffffffffffff", "-1.7976931348623157e+308"),
        ("4340000000000000", "9007199254740992"), ("c340000000000000", "-9007199254740992"),
        ("4430000000000000", "295147905179352830000"),
        ("44b52d02c7e14af5", "9.999999999999997e+22"), ("44b52d02c7e14af6", "1e+23"), ("44b52d02c7e14af7", "1.0000000000000001e+23"),
        ("444b1ae4d6e2ef4e", "999999999999999700000"), ("444b1ae4d6e2ef4f", "999999999999999900000"), ("444b1ae4d6e2ef50", "1e+21"),
        ("3eb0c6f7a0b5ed8c", "9.999999999999997e-7"), ("3eb0c6f7a0b5ed8d", "0.000001"),
        ("41b3de4355555553", "333333333.3333332"), ("41b3de4355555554", "333333333.33333325"), ("41b3de4355555555", "333333333.3333333"),
        ("41b3de4355555556", "333333333.3333334"), ("41b3de4355555557", "333333333.33333343"),
        ("becbf647612f3696", "-0.0000033333333333333333"), ("43143ff3c1cb0959", "1424953923781206.2"),
    ],
)
def test_rfc8785_appendix_b_number_samples(bits, expected):
    assert canonical_json_bytes({"n": f64(bits)}) == (f'{{"n":{expected}}}\n').encode()


def test_jcs_boundaries_and_integer_ingress():
    assert canonical_json_bytes({"n": -0.0}) == b'{"n":0}\n'
    assert canonical_json_bytes({"n": 1e-7}) == b'{"n":1e-7}\n'
    assert canonical_json_bytes({"n": 1e-6}) == b'{"n":0.000001}\n'
    assert canonical_json_bytes({"n": 1e20}) == b'{"n":100000000000000000000}\n'
    assert canonical_json_bytes({"n": 1e21}) == b'{"n":1e+21}\n'
    assert canonical_json_bytes({"n": SAFE_INTEGER_MAX}) == b'{"n":9007199254740991}\n'
    with pytest.raises(ContractDError, match="non_interoperable_integer"):
        canonical_json_bytes({"n": SAFE_INTEGER_MAX + 1})
    d = load("source-audit-clear.json")
    d["metadata"]["diagnostics"] = {"number": 9007199254740993}
    raw = json.dumps(d, ensure_ascii=False, separators=(",", ":")).encode()
    with pytest.raises(ContractDError, match="non_interoperable_integer"):
        parse_json_bytes(raw)


def test_non_bmp_property_order_uses_jcs_utf16_ordering():
    got = canonical_json_bytes({"\uffff": 1, "\U0001f4a9": 2}).decode("utf-8")
    assert got.index("\U0001f4a9") < got.index("\uffff")
