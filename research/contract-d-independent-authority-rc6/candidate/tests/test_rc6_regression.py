from __future__ import annotations

import copy
import json
import math
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

from contract_d_consume import ApplicabilityExpectation, consume
from contract_d_core import (
    ContractDError,
    MAX_JSON_CONTAINER_DEPTH,
    SAFE_INTEGER_MAX,
    canonical_json_bytes,
    semantic_identity,
    validate_decision,
)
from contract_d_validate import parse_json_bytes, require_canonical_bytes

VALID = json.loads((HERE / "fixtures" / "valid.json").read_text())["fixtures"]
INVALID = json.loads((HERE / "fixtures" / "invalid.json").read_text())["fixtures"]


def load(name):
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
def test_valid(name):
    d = load(name)
    validate_decision(d)
    assert require_canonical_bytes(canonical_json_bytes(d)) == d


@pytest.mark.parametrize("name", sorted(INVALID))
def test_invalid(name):
    with pytest.raises(ContractDError):
        validate_decision(copy.deepcopy(INVALID[name]))


def test_state_controls():
    for name in (
        "source-audit-clear.json",
        "citation-use-clear.json",
        "task-dispatch-clear.json",
    ):
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


def test_safe_default_only_normalizes_decision_effect():
    d = load("source-audit-clear.json")
    a = copy.deepcopy(d)
    a["effect"].pop("params")
    b = copy.deepcopy(d)
    b["effect"]["params"] = {}
    assert semantic_identity(a) == semantic_identity(b) == semantic_identity(d)


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
        parse_json_bytes(
            b'{"contract_d_version":"0.3.0-rc5","contract_d_version":"0.3.0-rc5"}'
        )


def test_cyclic_host_container_fails_closed():
    d = load("source-audit-clear.json")
    cycle = {}
    cycle["self"] = cycle
    d["metadata"]["diagnostics"] = cycle
    with pytest.raises(ContractDError, match="non_json_value"):
        validate_decision(d)
    got = consume(d, exp(load("source-audit-clear.json")))
    assert got["outcome"] == "cannot_establish"
    assert got["reason"] == "non_json_value"


def test_mutual_host_container_cycle_fails_closed():
    d = load("source-audit-clear.json")
    left = []
    right = {"left": left}
    left.append(right)
    d["metadata"]["diagnostics"] = {"cycle": left}
    with pytest.raises(ContractDError, match="non_json_value"):
        validate_decision(d)


def test_shared_acyclic_host_container_remains_valid():
    d = load("source-audit-clear.json")
    shared = {"values": [1, 2, 3]}
    d["metadata"]["diagnostics"] = {"a": shared, "b": shared}
    validate_decision(d)
    canonical_json_bytes(d)
    assert consume(d, exp(d))["outcome"] == "candidate_for_authorization"


def test_unpaired_surrogate_is_rejected_before_authority_or_canonicalization():
    base = load("source-audit-clear.json")
    base["metadata"]["diagnostics"] = {"bad": "\ud800"}
    raw = json.dumps(base, ensure_ascii=True, separators=(",", ":")).encode("ascii")
    with pytest.raises(ContractDError, match="invalid_unicode_scalar"):
        parse_json_bytes(raw)
    with pytest.raises(ContractDError, match="invalid_unicode_scalar"):
        validate_decision(base)
    got = consume(base, exp(load("source-audit-clear.json")))
    assert got["outcome"] == "cannot_establish"
    assert got["reason"] == "invalid_unicode_scalar"


def test_unpaired_surrogate_in_authority_string_is_rejected():
    d = load("source-audit-clear.json")
    d["policy"]["id"] = "bad-\ud800"
    with pytest.raises(ContractDError, match="invalid_unicode_scalar"):
        validate_decision(d)
    assert consume(d, exp(load("source-audit-clear.json")))["outcome"] == "cannot_establish"


def test_jcs_number_serialization_and_safe_integer_domain():
    assert canonical_json_bytes({"n": -0.0}) == b'{"n":0}\n'
    assert canonical_json_bytes({"n": 1e-7}) == b'{"n":1e-7}\n'
    assert canonical_json_bytes({"n": 1e-6}) == b'{"n":0.000001}\n'
    assert canonical_json_bytes({"n": 1e20}) == b'{"n":100000000000000000000}\n'
    assert canonical_json_bytes({"n": 1e21}) == b'{"n":1e+21}\n'
    assert canonical_json_bytes({"n": SAFE_INTEGER_MAX}) == (
        b'{"n":9007199254740991}\n'
    )
    with pytest.raises(ContractDError, match="non_interoperable_integer"):
        canonical_json_bytes({"n": SAFE_INTEGER_MAX + 1})


def test_non_bmp_property_order_uses_jcs_utf16_ordering():
    got = canonical_json_bytes({"\uffff": 1, "\U0001f4a9": 2}).decode("utf-8")
    assert got.index("\U0001f4a9") < got.index("\uffff")


def _nested_lists(count: int):
    x = "leaf"
    for _ in range(count):
        x = [x]
    return x


def test_depth_boundary_is_deterministic_and_controlled():
    # Root Decision object depth=1, metadata depth=2, diagnostics depth=3.
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
    assert got["outcome"] == "cannot_establish"
    assert got["reason"] == "json_depth_exceeded"


def test_very_deep_finite_value_never_leaks_recursion_error():
    d = load("source-audit-clear.json")
    d["metadata"]["diagnostics"] = {"deep": _nested_lists(1200)}
    with pytest.raises(ContractDError, match="json_depth_exceeded"):
        validate_decision(d)
    got = consume(d, exp(load("source-audit-clear.json")))
    assert got["outcome"] == "cannot_establish"
    assert got["reason"] == "json_depth_exceeded"


def test_malformed_external_expectations_fail_closed():
    d = load("source-audit-clear.json")
    extra = exp(d)
    extra.target["extra"] = "x"
    got = consume(d, extra)
    assert got["outcome"] == "cannot_establish"
    assert got["reason"] == "invalid_expectation"

    malformed = exp(d)
    object.__setattr__(malformed, "effect_params", [])
    got = consume(d, malformed)
    assert got["outcome"] == "cannot_establish"
    assert got["reason"] == "invalid_expectation"


def test_metadata_invariance():
    d = load("source-audit-clear.json")
    ident = semantic_identity(d)
    x = copy.deepcopy(d)
    x["metadata"]["diagnostics"] = {"actor": "root", "approval": True, "n": 1e-6}
    assert semantic_identity(x) == ident
    x = copy.deepcopy(d)
    x.pop("metadata")
    assert semantic_identity(x) == ident


def test_conformance_cases():
    corpus = json.loads((HERE / "conformance-cases.json").read_text())
    for case in corpus["cases"]:
        d = load(case["decision_fixture"])
        e = case["expect"]
        got = consume(
            d,
            ApplicabilityExpectation(
                e["input_authority"],
                e["policy"],
                e["target"],
                e["requested_operation"],
                e.get("effect_params"),
            ),
        )
        assert got["outcome"] == case["outcome"], case["id"]


def test_weak_consumers_are_discriminated():
    d = load("source-audit-clear.json")
    weak_clear = lambda x: x["evaluation"].get("disposition") == "clear"
    assert weak_clear(d)
    assert consume(d, exp(d, op="task.dispatch"))["outcome"] == "not_applicable"
    wrong = exp(d)
    wrong.target["kind"] = "task"
    assert consume(d, wrong)["outcome"] == "not_applicable"
