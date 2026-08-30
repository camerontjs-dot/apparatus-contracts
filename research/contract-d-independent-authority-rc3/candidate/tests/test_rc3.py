from __future__ import annotations
import copy
import json
from pathlib import Path
import pytest

HERE = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(HERE))

from contract_d_core import ContractDError, canonical_json_bytes, semantic_identity, validate_decision
from contract_d_validate import require_canonical_bytes
from contract_d_consume import ApplicabilityExpectation, consume

VALID_CORPUS = json.loads((HERE / "fixtures" / "valid.json").read_text(encoding="utf-8"))["fixtures"]
INVALID_CORPUS = json.loads((HERE / "fixtures" / "invalid.json").read_text(encoding="utf-8"))["fixtures"]

def load(name): return copy.deepcopy(VALID_CORPUS[name])
def exp_for(d, op=None, params=None):
    return ApplicabilityExpectation(copy.deepcopy(d["input_authority"]),copy.deepcopy(d["policy"]),copy.deepcopy(d["target"]),op or d.get("effect",{}).get("type","knowledge.add_verified_tag"),params)

@pytest.mark.parametrize("name", sorted(VALID_CORPUS))
def test_valid_fixtures(name):
    obj=load(name); raw=canonical_json_bytes(obj)
    assert require_canonical_bytes(raw)==obj
    assert validate_decision(obj) is obj

@pytest.mark.parametrize("name", sorted(INVALID_CORPUS))
def test_invalid_fixtures(name):
    with pytest.raises(ContractDError): validate_decision(copy.deepcopy(INVALID_CORPUS[name]))

def test_positive_controls_and_state_split():
    s=load("source-audit-clear.json"); c=load("citation-use-clear.json"); t=load("task-dispatch-clear.json")
    assert consume(s,exp_for(s,params={"scope":"claim"}))["outcome"]=="candidate_for_authorization"
    assert consume(c,exp_for(c))["outcome"]=="candidate_for_authorization"
    assert consume(t,exp_for(t))["outcome"]=="candidate_for_authorization"
    h=load("completed-hold.json"); f=load("evaluation-failed.json")
    assert consume(h,exp_for(h,params={"scope":"claim"}))["outcome"]=="hold"
    assert consume(f,exp_for(f))["outcome"]=="evaluation_failed"
    assert semantic_identity(h)!=semantic_identity(f)

def test_substitution_attacks():
    d=load("source-audit-clear.json")
    mutations=[("target","kind","task"),("target","id","other"),("target","content_sha256","sha256:"+"2"*64),("input_authority","kind","task-review"),("input_authority","id","other"),("input_authority","immutable_id","result-set:"+"f"*64),("policy","id","other-policy"),("policy","version","2")]
    for family,key,value in mutations:
        e=exp_for(d,params={"scope":"claim"}); changed=copy.deepcopy(getattr(e,family)); changed[key]=value
        kwargs=dict(input_authority=e.input_authority,policy=e.policy,target=e.target,requested_operation=e.requested_operation,effect_params=e.effect_params); kwargs[family]=changed
        assert consume(d,ApplicabilityExpectation(**kwargs))["outcome"]=="not_applicable"
    assert consume(d,ApplicabilityExpectation(d["input_authority"],d["policy"],d["target"],"task.dispatch"))["outcome"]=="not_applicable"

def test_effect_param_defaults_and_identity():
    d=load("source-audit-clear.json"); x=copy.deepcopy(d); x["effect"].pop("params"); y=copy.deepcopy(d); y["effect"]["params"]={}; z=copy.deepcopy(d); z["effect"]["params"]={"scope":"claim"}
    assert semantic_identity(x)==semantic_identity(y)==semantic_identity(z)
    q=copy.deepcopy(d); q["effect"]["params"]={"scope":"object"}
    assert semantic_identity(q)!=semantic_identity(d)
    assert consume(q,exp_for(d,params={"scope":"claim"}))["outcome"]=="not_applicable"

def test_metadata_invariance_and_opaque_diagnostics():
    d=load("source-audit-clear.json"); ident=semantic_identity(d); baseline=consume(d,exp_for(d,params={"scope":"claim"}))["outcome"]
    variants=[]; x=copy.deepcopy(d); x.pop("metadata"); variants.append(x); x=copy.deepcopy(d); x["metadata"]["reason_codes"]=["different"]; variants.append(x); x=copy.deepcopy(d); x["metadata"]["explanation"]="different"; variants.append(x); x=copy.deepcopy(d); x["metadata"]["diagnostics"]={"actor":"root","approval":True,"execution_receipt":{"ok":True}}; variants.append(x)
    for x in variants:
        assert semantic_identity(x)==ident
        assert consume(x,exp_for(d,params={"scope":"claim"}))["outcome"]==baseline

def test_authorization_only_context_invariant():
    d=load("source-audit-clear.json"); ident=semantic_identity(d)
    contexts=[{"actor":"a","approved":False,"profile":"manual"},{"actor":"a","approved":True,"profile":"supervised"},{"actor":"b","approved":True,"profile":"delegated"}]
    assert all(semantic_identity(d)==ident for _ in contexts)

def test_authority_mutations_change_identity():
    d=load("source-audit-clear.json"); baseline=semantic_identity(d); variants=[]
    for family,key,value in [("input_authority","kind","other-kind"),("input_authority","id","other"),("input_authority","immutable_id","other-immutable"),("policy","id","other-policy"),("policy","version","2"),("target","kind","task"),("target","id","other"),("target","content_sha256","sha256:"+"2"*64),("evaluation","disposition","hold")]:
        x=copy.deepcopy(d); x[family][key]=value; variants.append(x)
    x=copy.deepcopy(d); x["effect"]["type"]="knowledge.cite_as_evidence"; x["effect"].pop("params",None); variants.append(x)
    x=copy.deepcopy(d); x["effect"]["params"]={"scope":"object"}; variants.append(x)
    for x in variants: validate_decision(x); assert semantic_identity(x)!=baseline

def test_field_ablation_minimality():
    d=load("source-audit-clear.json")
    for field in ["contract_d_version","input_authority","policy","target","evaluation","effect"]:
        x=copy.deepcopy(d); del x[field]
        with pytest.raises(ContractDError): validate_decision(x)
    for family,fields in [("input_authority",["kind","id","immutable_id"]),("policy",["id","version"]),("target",["kind","id","content_sha256"]),("evaluation",["state","disposition"]),("effect",["type","version"])]:
        for field in fields:
            x=copy.deepcopy(d); del x[family][field]
            with pytest.raises(ContractDError): validate_decision(x)
    x=copy.deepcopy(d); x.pop("metadata"); assert semantic_identity(x)==semantic_identity(d)
    x=copy.deepcopy(d); x["effect"].pop("params"); assert semantic_identity(x)==semantic_identity(d)

def test_conformance_cases():
    corpus=json.loads((HERE/"conformance-cases.json").read_text())
    for case in corpus["cases"]:
        d=load(case["decision_fixture"]); e=case["expect"]
        out=consume(d,ApplicabilityExpectation(e["input_authority"],e["policy"],e["target"],e["requested_operation"],e.get("effect_params")))
        assert out["outcome"]==case["outcome"],case["id"]

def test_weak_controls_discriminated():
    d=load("source-audit-clear.json")
    weak_disposition=lambda obj: obj["evaluation"].get("state")=="completed" and obj["evaluation"].get("disposition")=="clear"
    assert weak_disposition(d) and consume(d,ApplicabilityExpectation(d["input_authority"],d["policy"],d["target"],"task.dispatch"))["outcome"]=="not_applicable"
    weak_target=lambda obj,target_id: obj["target"]["id"]==target_id
    assert weak_target(d,"k1"); e=exp_for(d,params={"scope":"claim"}); wrong=copy.deepcopy(e.target); wrong["kind"]="task"
    assert consume(d,ApplicabilityExpectation(e.input_authority,e.policy,wrong,e.requested_operation,e.effect_params))["outcome"]=="not_applicable"
    r=copy.deepcopy(d); r["metadata"]["reason_codes"]=["dispatch"]
    assert consume(r,exp_for(d,params={"scope":"claim"}))["outcome"]=="candidate_for_authorization"
    u=copy.deepcopy(d); u["effect"]={"type":"future.effect","version":"1"}
    with pytest.raises(ContractDError): validate_decision(u)
    h=load("completed-hold.json"); f=load("evaluation-failed.json")
    assert consume(h,exp_for(h,params={"scope":"claim"}))["outcome"]=="hold" and consume(f,exp_for(f))["outcome"]=="evaluation_failed"

def test_canonicalization_duplicate_keys_and_formatting():
    d=load("source-audit-clear.json"); canonical=canonical_json_bytes(d); assert require_canonical_bytes(canonical)==d
    with pytest.raises(ContractDError,match="noncanonical_json"): require_canonical_bytes(json.dumps(d,indent=2).encode())
    with pytest.raises(ContractDError,match="duplicate_json_key"): require_canonical_bytes(b'{"contract_d_version":"0.3.0-rc3","contract_d_version":"0.3.0-rc3"}\n')

def test_injection_matrix():
    d=load("source-audit-clear.json"); injections={"actor":"root","requested_operation":"task.dispatch","approval":True,"delegation":{"to":"agent"},"autonomy":"full","execution_permission":True,"execution_state":"done","execution_receipt":{"ok":True}}
    for path in [(),("input_authority",),("policy",),("target",),("evaluation",),("effect",),("metadata",)]:
        for key,value in injections.items():
            x=copy.deepcopy(d); cur=x
            for part in path: cur=cur[part]
            cur[key]=copy.deepcopy(value)
            with pytest.raises(ContractDError): validate_decision(x)
    for key,value in injections.items():
        x=copy.deepcopy(d); x["effect"].setdefault("params",{})[key]=copy.deepcopy(value)
        with pytest.raises(ContractDError): validate_decision(x)

def test_diagnostics_only_opaque_surface():
    d=load("source-audit-clear.json"); baseline=semantic_identity(d); x=copy.deepcopy(d); x["metadata"]["diagnostics"]={"actor":"root","requested_operation":"task.dispatch","approval":True,"delegation":{"to":"agent"},"autonomy":"full","execution_permission":True,"execution_state":"done","execution_receipt":{"ok":True}}
    validate_decision(x); assert semantic_identity(x)==baseline; assert consume(x,exp_for(d,params={"scope":"claim"}))["outcome"]=="candidate_for_authorization"

def test_weak_policy_upstream_and_identity_controls():
    d=load("source-audit-clear.json"); weak=lambda obj: obj["evaluation"]["disposition"]=="clear" and obj["target"]["id"]=="k1" and obj["effect"]["type"]=="knowledge.add_verified_tag"; assert weak(d)
    e=exp_for(d,params={"scope":"claim"}); wrong_policy={"id":"wrong","version":"999"}; wrong_upstream={"kind":"wrong","id":"wrong","immutable_id":"wrong"}
    assert consume(d,ApplicabilityExpectation(e.input_authority,wrong_policy,e.target,e.requested_operation,e.effect_params))["outcome"]=="not_applicable"
    assert consume(d,ApplicabilityExpectation(wrong_upstream,e.policy,e.target,e.requested_operation,e.effect_params))["outcome"]=="not_applicable"
    import hashlib
    weak_id=lambda ctx: hashlib.sha256(canonical_json_bytes({"decision":d,"authorization":ctx})).hexdigest()
    assert weak_id({"actor":"a","approval":False})!=weak_id({"actor":"a","approval":True})
    assert semantic_identity(d)==semantic_identity(copy.deepcopy(d))

def test_metadata_transport_vs_semantic_identity():
    d=load("source-audit-clear.json"); x=copy.deepcopy(d); x["metadata"]["explanation"]="different wording"
    assert canonical_json_bytes(x)!=canonical_json_bytes(d)
    assert semantic_identity(x)==semantic_identity(d)
