from __future__ import annotations
import copy, json, math
from pathlib import Path
import pytest
HERE=Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0,str(HERE))
from contract_d_core import ContractDError, canonical_json_bytes, semantic_identity, validate_decision
from contract_d_validate import parse_json_bytes, require_canonical_bytes
from contract_d_consume import ApplicabilityExpectation, consume

VALID=json.loads((HERE/"fixtures"/"valid.json").read_text())["fixtures"]
INVALID=json.loads((HERE/"fixtures"/"invalid.json").read_text())["fixtures"]
def load(n): return copy.deepcopy(VALID[n])
def exp(d,op=None,params=None): return ApplicabilityExpectation(copy.deepcopy(d["input_authority"]),copy.deepcopy(d["policy"]),copy.deepcopy(d["target"]),op or d.get("effect",{}).get("type","knowledge.add_verified_tag"),params)

@pytest.mark.parametrize("name", sorted(VALID))
def test_valid(name):
    d=load(name); validate_decision(d); assert require_canonical_bytes(canonical_json_bytes(d))==d

@pytest.mark.parametrize("name", sorted(INVALID))
def test_invalid(name):
    with pytest.raises(ContractDError): validate_decision(copy.deepcopy(INVALID[name]))

def test_state_controls():
    for n in ("source-audit-clear.json","citation-use-clear.json","task-dispatch-clear.json"):
        d=load(n); assert consume(d,exp(d))["outcome"]=="candidate_for_authorization"
    h=load("completed-hold.json"); f=load("evaluation-failed.json")
    assert consume(h,exp(h))["outcome"]=="hold"
    assert consume(f,exp(f))["outcome"]=="evaluation_failed"
    assert semantic_identity(h)!=semantic_identity(f)

def test_hold_still_binds_effect_and_request():
    h=load("completed-hold.json")
    assert consume(h,exp(h,op="task.dispatch"))["outcome"]=="not_applicable"
    assert consume(h,exp(h,params={"scope":"object"}))["outcome"]=="not_applicable"
    assert consume(h,exp(h))["outcome"]=="hold"

def test_omitted_external_params_are_unconstrained():
    d=load("source-audit-object-scope-clear.json")
    assert consume(d,exp(d,params=None))["outcome"]=="candidate_for_authorization"
    assert consume(d,exp(d,params={}))["outcome"]=="candidate_for_authorization"
    assert consume(d,exp(d,params={"scope":"claim"}))["outcome"]=="not_applicable"
    assert consume(d,exp(d,params={"scope":"object"}))["outcome"]=="candidate_for_authorization"

def test_safe_default_only_normalizes_decision_effect():
    d=load("source-audit-clear.json")
    a=copy.deepcopy(d); a["effect"].pop("params")
    b=copy.deepcopy(d); b["effect"]["params"]={}
    assert semantic_identity(a)==semantic_identity(b)==semantic_identity(d)

def test_json_ingress_and_host_values_fail_closed():
    d=load("source-audit-clear.json")
    x=copy.deepcopy(d); x["metadata"]["diagnostics"]={"bad":{1,2}}
    with pytest.raises(ContractDError,match="non_json_value"): validate_decision(x)
    x=copy.deepcopy(d); x["metadata"]["diagnostics"]={1:"bad-key"}
    with pytest.raises(ContractDError,match="non_json_object_key"): validate_decision(x)
    x=copy.deepcopy(d); x["metadata"]["diagnostics"]={"n":math.inf}
    with pytest.raises(ContractDError,match="non_finite_number"): validate_decision(x)
    with pytest.raises(ContractDError,match="invalid_utf8"): parse_json_bytes(b"\xff")
    with pytest.raises(ContractDError,match="duplicate_json_key"): parse_json_bytes(b'{"contract_d_version":"0.3.0-rc4","contract_d_version":"0.3.0-rc4"}')

def test_metadata_invariance():
    d=load("source-audit-clear.json"); ident=semantic_identity(d)
    x=copy.deepcopy(d); x["metadata"]["diagnostics"]={"actor":"root","approval":True}
    assert semantic_identity(x)==ident
    x=copy.deepcopy(d); x.pop("metadata")
    assert semantic_identity(x)==ident

def test_conformance_cases():
    corpus=json.loads((HERE/"conformance-cases.json").read_text())
    for case in corpus["cases"]:
        d=load(case["decision_fixture"]); e=case["expect"]
        got=consume(d,ApplicabilityExpectation(e["input_authority"],e["policy"],e["target"],e["requested_operation"],e.get("effect_params")))
        assert got["outcome"]==case["outcome"],case["id"]

def test_weak_consumers_are_discriminated():
    d=load("source-audit-clear.json")
    weak_clear=lambda x:x["evaluation"].get("disposition")=="clear"
    assert weak_clear(d)
    assert consume(d,exp(d,op="task.dispatch"))["outcome"]=="not_applicable"
    wrong=exp(d); wrong.target["kind"]="task"
    assert consume(d,wrong)["outcome"]=="not_applicable"
