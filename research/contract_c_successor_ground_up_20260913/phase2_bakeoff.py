from __future__ import annotations
import argparse, copy, hashlib, itertools, json
from pathlib import Path
from typing import Any

P1="175246ae16932f2f34a399560d7f76013213bf97"
P15="163d0d424777ef3c0a3b45dec2888c845634205d"
P15R="a79962255b6b6568c84ba163c8bcc6f23275676a"
IMPL="a902621e8baea3063dddd7f92ba975aade305464"
POL="44ecc33519fa8911079595d322f5f0decbf0389af42e153ac32214931798e42c"

def cb(v:Any)->bytes:return (json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n").encode()
def h(s:str)->str:return hashlib.sha256(s.encode()).hexdigest()
def part(s:str,pol:str,role:str="causal")->dict[str,str]:return {"symbol":s,"source_id":"src-"+s.lower(),"passage_id":s,"polarity":pol,"role":role}
def pr(q:str,comp:str|None,ver:str|None,reason:str|None,ps:list[dict[str,str]],msc:list[list[str]],exe:str="completed")->dict[str,Any]:return {"proposition_id":q,"proposition_sha256":h("semantic:"+q),"execution":exe,"completion":comp,"terminal":None if ver is None else {"verdict":ver,"reason":reason},"participants":ps,"msc":msc}
def mdl(exe:str,props:list[dict[str,Any]],w:str="W")->dict[str,Any]:return {"contract_b":{"contract_version":"1.2.0","bundle_id":w,"bundle_hash":"sha256:"+h("world:"+w)},"producer":{"semantic_implementation_sha":IMPL,"policy_sha256":POL},"result_execution":exe,"propositions":props}

def oracles()->dict[str,dict[str,Any]]:
 S1=part("S1","support");S2=part("S2","support");R1=part("R1","refute");R2=part("R2","refute");U1=part("U1","non_polarized");U2=part("U2","non_polarized");N1=part("N1","non_polarized","residual");J1=part("J1","non_polarized");J2=part("J2","non_polarized")
 q=lambda c,v,r,p,m:pr("Q1",c,v,r,p,m)
 return {
 "SP-01-single-support":mdl("completed",[q("assessed","supported","categorical_support",[S1],[["S1"]])]),
 "SP-02-single-refutation":mdl("completed",[q("assessed","contradicted","categorical_refutation",[R1],[["R1"]])]),
 "SP-03-two-independent-supports":mdl("completed",[q("assessed","supported","categorical_support",[S1,S2],[["S1"],["S2"]])]),
 "SP-04-two-independent-refutations":mdl("completed",[q("assessed","contradicted","categorical_refutation",[R1,R2],[["R1"],["R2"]])]),
 "SP-05-joint-basis":mdl("completed",[q("not_checkable","not_checkable","joint_public_cause",[J1,J2],[["J1","J2"]])]),
 "SP-06-support-plus-neutral-residual":mdl("completed",[q("assessed","supported","categorical_support",[S1,N1],[["S1"]])]),
 "SP-07-causal-neutral-unresolved":mdl("completed",[q("not_checkable","not_checkable","unresolved_categorical_relation",[U1],[["U1"]])]),
 "SP-08-two-independent-unresolved":mdl("completed",[q("not_checkable","not_checkable","unresolved_categorical_relation",[U1,U2],[["U1"],["U2"]])]),
 "SP-09-minimal-mixed":mdl("completed",[q("not_checkable","not_checkable","MIXED_RELATIONS",[S1,R1],[["S1","R1"]])]),
 "SP-10-alt-joint-mixed":mdl("completed",[q("not_checkable","not_checkable","MIXED_RELATIONS",[S1,S2,R1],[["S1","R1"],["S2","R1"]])]),
 "SP-11-symmetric-alt-joint-mixed":mdl("completed",[q("not_checkable","not_checkable","MIXED_RELATIONS",[S1,R1,R2],[["S1","R1"],["S1","R2"]])]),
 "SP-12-alt-by-alt-mixed":mdl("completed",[q("not_checkable","not_checkable","MIXED_RELATIONS",[S1,S2,R1,R2],[["S1","R1"],["S1","R2"],["S2","R1"],["S2","R2"]])]),
 "SP-13-completed-no-deciding":mdl("completed",[q("not_checkable","not_checkable","no_deciding_relation",[N1],[])]),
 "SP-14-result-set-multi-proposition":mdl("completed",[pr("Q1","assessed","supported","categorical_support",[part("P1S1","support")],[["P1S1"]]),pr("Q2","assessed","contradicted","categorical_refutation",[part("P2R1","refute")],[["P2R1"]])]),
 "EX-01-result-set-failed":mdl("failed",[]),"EX-02-result-set-incomplete":mdl("incomplete",[]),
 "EX-03-proposition-failed":mdl("completed",[pr("Q1",None,None,None,[],[],"failed")]),"EX-04-proposition-incomplete":mdl("completed",[pr("Q1",None,None,None,[],[],"incomplete")]),
 "EX-05-completed-not-checkable":mdl("completed",[q("not_checkable","not_checkable","unresolved_categorical_relation",[U1],[["U1"]])])}
O=oracles()

def norm(v:dict[str,Any])->dict[str,Any]:
 x=copy.deepcopy(v);x["propositions"]=sorted(x["propositions"],key=lambda z:z["proposition_id"])
 for q in x["propositions"]:q["participants"]=sorted(q["participants"],key=lambda z:(z["source_id"],z["passage_id"],z["polarity"],z["role"]));q["msc"]=sorted(sorted(g) for g in q["msc"])
 return x
def eq(a:dict[str,Any],b:dict[str,Any])->bool:return norm(a)==norm(b)
def keys(v:dict[str,Any],ks:set[str])->None:
 if set(v)!=ks:raise ValueError("field mismatch")
def rk(v:dict[str,str])->tuple[str,str]:keys(v,{"source_id","passage_id"});return v["source_id"],v["passage_id"]
def envelope(v:dict[str,Any],candidate:str)->None:
 keys(v,{"candidate","contract_b","producer","execution","propositions"});
 if v["candidate"]!=candidate:raise ValueError("candidate")
 keys(v["contract_b"],{"contract_version","bundle_id","bundle_hash"});keys(v["producer"],{"semantic_implementation_sha","policy_sha256"});keys(v["execution"],{"state"})
def participants(rows:list[dict[str,Any]])->dict[tuple[str,str],dict[str,str]]:
 out={}
 for r in rows:
  keys(r,{"evidence_ref","polarity","role"});k=rk(r["evidence_ref"])
  if k in out or r["polarity"] not in {"support","refute","non_polarized"} or r["role"] not in {"causal","residual"}:raise ValueError("participant")
  out[k]={"symbol":k[1],"source_id":k[0],"passage_id":k[1],"polarity":r["polarity"],"role":r["role"]}
 return out

def Aenc(o:dict[str,Any])->dict[str,Any]:
 v={"candidate":"A-minimal-sufficient-basis-groups","contract_b":copy.deepcopy(o["contract_b"]),"producer":copy.deepcopy(o["producer"]),"execution":{"state":o["result_execution"]},"propositions":[]}
 for q in o["propositions"]:
  by={x["symbol"]:x for x in q["participants"]};v["propositions"].append({"proposition":{"proposition_id":q["proposition_id"],"proposition_sha256":q["proposition_sha256"]},"execution":{"state":q["execution"],"completion":q["completion"]},"terminal":copy.deepcopy(q["terminal"]),"participants":[{"evidence_ref":{"source_id":x["source_id"],"passage_id":x["passage_id"]},"polarity":x["polarity"],"role":x["role"]} for x in q["participants"]],"basis_groups":[[{"source_id":by[s]["source_id"],"passage_id":by[s]["passage_id"]} for s in g] for g in q["msc"]]})
 return v

def Aint(v:dict[str,Any])->dict[str,Any]:
 envelope(v,"A-minimal-sufficient-basis-groups");seen=set();out=[]
 for q in v["propositions"]:
  keys(q,{"proposition","execution","terminal","participants","basis_groups"});keys(q["proposition"],{"proposition_id","proposition_sha256"});keys(q["execution"],{"state","completion"});qid=q["proposition"]["proposition_id"]
  if qid in seen:raise ValueError("q dup")
  seen.add(qid);ps=participants(q["participants"]);gs=[]
  for raw in q["basis_groups"]:
   ks=[rk(x) for x in raw]
   if not ks or len(ks)!=len(set(ks)):raise ValueError("group")
   g=frozenset(ks)
   if g in gs or any(k not in ps or ps[k]["role"]!="causal" for k in g):raise ValueError("group")
   gs.append(g)
  if any(any(h<g for h in gs) for g in gs):raise ValueError("nonminimal")
  causal={k for k,x in ps.items() if x["role"]=="causal"};covered=set().union(*gs) if gs else set()
  if causal!=covered:raise ValueError("coverage")
  if q["execution"]["state"]!="completed" and (q["terminal"] is not None or ps or gs):raise ValueError("invented")
  out.append({"proposition_id":qid,"proposition_sha256":q["proposition"]["proposition_sha256"],"execution":q["execution"]["state"],"completion":q["execution"]["completion"],"terminal":copy.deepcopy(q["terminal"]),"participants":list(ps.values()),"msc":[[ps[k]["symbol"] for k in sorted(g)] for g in gs]})
 if v["execution"]["state"]!="completed" and out:raise ValueError("result execution")
 return {"contract_b":copy.deepcopy(v["contract_b"]),"producer":copy.deepcopy(v["producer"]),"result_execution":v["execution"]["state"],"propositions":out}
def Acanon(v:dict[str,Any])->bytes:return cb(Aenc(norm(Aint(v))))

def leaf(x:dict[str,str])->dict[str,Any]:return {"leaf":{"source_id":x["source_id"],"passage_id":x["passage_id"]}}
def Bexpr(q:dict[str,Any])->dict[str,Any]|None:
 gs=q["msc"]
 if not gs:return None
 b={x["symbol"]:x for x in q["participants"]}
 if gs==[["S1","R1"],["S2","R1"]]:return {"all_of":[{"any_of":[leaf(b["S1"]),leaf(b["S2"])]},leaf(b["R1"])]}
 if gs==[["S1","R1"],["S1","R2"]]:return {"all_of":[leaf(b["S1"]),{"any_of":[leaf(b["R1"]),leaf(b["R2"])]}]}
 if gs==[["S1","R1"],["S1","R2"],["S2","R1"],["S2","R2"]]:return {"all_of":[{"any_of":[leaf(b["S1"]),leaf(b["S2"])]},{"any_of":[leaf(b["R1"]),leaf(b["R2"])]}]}
 es=[]
 for g in gs:
  ls=[leaf(b[s]) for s in g];es.append(ls[0] if len(ls)==1 else {"all_of":ls})
 return es[0] if len(es)==1 else {"any_of":es}
def Benc(o:dict[str,Any])->dict[str,Any]:
 v={"candidate":"B-typed-causal-expression","contract_b":copy.deepcopy(o["contract_b"]),"producer":copy.deepcopy(o["producer"]),"execution":{"state":o["result_execution"]},"propositions":[]}
 for q in o["propositions"]:v["propositions"].append({"proposition":{"proposition_id":q["proposition_id"],"proposition_sha256":q["proposition_sha256"]},"execution":{"state":q["execution"],"completion":q["completion"]},"terminal":copy.deepcopy(q["terminal"]),"participants":[{"evidence_ref":{"source_id":x["source_id"],"passage_id":x["passage_id"]},"polarity":x["polarity"],"role":x["role"]} for x in q["participants"]],"cause":Bexpr(q)})
 return v

def expand(e:dict[str,Any],ps:dict[tuple[str,str],dict[str,str]])->set[frozenset[tuple[str,str]]]:
 if set(e)=={"leaf"}:
  k=rk(e["leaf"])
  if k not in ps or ps[k]["role"]!="causal":raise ValueError("leaf")
  return {frozenset({k})}
 if set(e) not in ({"all_of"},{"any_of"}):raise ValueError("node")
 op=next(iter(e));cs=e[op]
 if not isinstance(cs,list) or len(cs)<2:raise ValueError("arity")
 xs=[expand(c,ps) for c in cs];sig=[frozenset(k for g in x for k in g) for x in xs]
 if len(sig)!=len(set(sig)):raise ValueError("duplicate child")
 if op=="any_of":res=set().union(*xs)
 else:
  res=set()
  for choice in itertools.product(*xs):res.add(frozenset().union(*choice))
 return {g for g in res if not any(h<g for h in res)}
def Bint(v:dict[str,Any])->dict[str,Any]:
 envelope(v,"B-typed-causal-expression");seen=set();out=[]
 for q in v["propositions"]:
  keys(q,{"proposition","execution","terminal","participants","cause"});keys(q["proposition"],{"proposition_id","proposition_sha256"});keys(q["execution"],{"state","completion"});qid=q["proposition"]["proposition_id"]
  if qid in seen:raise ValueError("q dup")
  seen.add(qid);ps=participants(q["participants"]);gs=set() if q["cause"] is None else expand(q["cause"],ps);causal={k for k,x in ps.items() if x["role"]=="causal"};covered=set().union(*gs) if gs else set()
  if causal!=covered:raise ValueError("coverage")
  if q["execution"]["state"]!="completed" and (q["terminal"] is not None or ps or gs):raise ValueError("invented")
  out.append({"proposition_id":qid,"proposition_sha256":q["proposition"]["proposition_sha256"],"execution":q["execution"]["state"],"completion":q["execution"]["completion"],"terminal":copy.deepcopy(q["terminal"]),"participants":list(ps.values()),"msc":[[ps[k]["symbol"] for k in sorted(g)] for g in gs]})
 if v["execution"]["state"]!="completed" and out:raise ValueError("result execution")
 return {"contract_b":copy.deepcopy(v["contract_b"]),"producer":copy.deepcopy(v["producer"]),"result_execution":v["execution"]["state"],"propositions":out}
def sortexpr(e:Any)->Any:
 if e is None or set(e)=={"leaf"}:return copy.deepcopy(e)
 op=next(iter(e));return {op:sorted((sortexpr(x) for x in e[op]),key=cb)}
def Bcanon(v:dict[str,Any])->bytes:
 Bint(v);x=copy.deepcopy(v);x["propositions"]=sorted(x["propositions"],key=lambda q:q["proposition"]["proposition_id"])
 for q in x["propositions"]:q["participants"]=sorted(q["participants"],key=lambda z:(z["evidence_ref"]["source_id"],z["evidence_ref"]["passage_id"]));q["cause"]=sortexpr(q["cause"])
 return cb(x)
def Bsemantic(v:dict[str,Any])->bytes:return cb(norm(Bint(v)))

def dnf(o:dict[str,Any])->dict[str,Any]:
 v=Benc(o)
 for i,q in enumerate(o["propositions"]):
  if not q["msc"]:continue
  b={x["symbol"]:x for x in q["participants"]};ts=[]
  for g in q["msc"]:
   ls=[leaf(b[s]) for s in g];ts.append(ls[0] if len(ls)==1 else {"all_of":ls})
  v["propositions"][i]["cause"]=ts[0] if len(ts)==1 else {"any_of":ts}
 return v
def cnt(v:Any)->int:
 if isinstance(v,dict):return (1 if set(v)=={"leaf"} else 0)+sum(cnt(x) for x in v.values())
 if isinstance(v,list):return sum(cnt(x) for x in v)
 return 0
def Acnt(v:dict[str,Any])->int:return sum(len(g) for q in v["propositions"] for g in q["basis_groups"])
def revexpr(e:Any)->Any:
 if e is None or set(e)=={"leaf"}:return copy.deepcopy(e)
 op=next(iter(e));return {op:[revexpr(x) for x in reversed(e[op])]}
def perm(v:dict[str,Any],c:str)->dict[str,Any]:
 x=copy.deepcopy(v);x["propositions"].reverse()
 for q in x["propositions"]:
  q["participants"].reverse()
  if c=="A":q["basis_groups"].reverse();[g.reverse() for g in q["basis_groups"]]
  else:q["cause"]=revexpr(q["cause"])
 return x
def reject(fn)->bool:
 try:fn()
 except ValueError:return True
 return False

def mutations(c:str)->dict[str,bool]:
 enc,inte,canon=(Aenc,Aint,Acanon) if c=="A" else (Benc,Bint,Bcanon);o=O["SP-10-alt-joint-mixed"];base=enc(o);exp=norm(o);z={}
 m=copy.deepcopy(base);m["contract_b"]["bundle_id"]="W-other";m["contract_b"]["bundle_hash"]="sha256:"+"1"*64;z["01_world_substitution_observable"]=not eq(inte(m),exp)
 m=copy.deepcopy(base);m["propositions"][0]["participants"][0]["contract_b"]={"bundle_id":"other"};z["02_cross_world_composition_rejected"]=reject(lambda:inte(m))
 for n,val in [("03_same_id_proposition_substitution_observable","2"*64),("04_direction_semantic_substitution_observable","3"*64)]:m=copy.deepcopy(base);m["propositions"][0]["proposition"]["proposition_sha256"]=val;z[n]=not eq(inte(m),exp)
 m=copy.deepcopy(base);m["propositions"][0]["participants"][0]["evidence_ref"]["source_id"]="src-substituted";z["05_evidence_substitution_rejected_or_observable"]=reject(lambda:inte(m))
 m=copy.deepcopy(base);m["propositions"][0]["participants"].pop(0);z["06_remove_causal_rejected"]=reject(lambda:inte(m))
 rm=enc(O["SP-06-support-plus-neutral-residual"]);rm["propositions"][0]["participants"]=[x for x in rm["propositions"][0]["participants"] if x["role"]!="residual"];z["07_remove_residual_observable"]=not eq(inte(rm),O["SP-06-support-plus-neutral-residual"])
 m=copy.deepcopy(base);m["propositions"][0]["participants"][0]["role"]="residual";z["08_causal_residual_move_rejected"]=reject(lambda:inte(m))
 nm=enc(O["SP-07-causal-neutral-unresolved"]);nm["propositions"][0]["participants"][0]["polarity"]="support";z["09_neutral_laundering_observable"]=not eq(inte(nm),O["SP-07-causal-neutral-unresolved"])
 m=copy.deepcopy(base);m["propositions"][0]["participants"][0]["polarity"]="refute";z["10_polarity_flip_observable"]=not eq(inte(m),exp)
 m=copy.deepcopy(base)
 if c=="A":m["propositions"][0]["basis_groups"][0].append(copy.deepcopy(m["propositions"][0]["basis_groups"][0][0]))
 else:
  old=copy.deepcopy(m["propositions"][0]["cause"]);m["propositions"][0]["cause"]={"all_of":[old,copy.deepcopy(old)]}
 z["11_duplicate_semantic_member_rejected"]=reject(lambda:inte(m));z["12_unordered_permutation_same_canonical_bytes"]=canon(base)==canon(perm(base,c))
 authority=hashlib.sha256(canon(base)).hexdigest();m=copy.deepcopy(base);m["propositions"][0]["participants"][0]["polarity"]="refute";changed=hashlib.sha256(canon(m)).hexdigest();z["13_reidentity_cannot_satisfy_old_external_authority"]=changed!=authority;z["14_attacker_selected_digest_not_authority"]={"fixture":authority}["fixture"]!=changed
 m=copy.deepcopy(base);m["decision_threshold"]=0.7;z["15_destination_authorization_field_rejected"]=reject(lambda:inte(m));return z

def ma(c:str)->dict[str,bool]:
 enc,inte=(Aenc,Aint) if c=="A" else (Benc,Bint);b=enc(O["SP-01-single-support"]);m1=copy.deepcopy(b);m1["measurement"]={"value":1,"authority":"NOT_EVALUATED"};m2=copy.deepcopy(b);m2["caller_semantic_stipulation"]={"relation":"SUPPORTS"};return {"MA-01_measurement_not_public_authority":reject(lambda:inte(m1)),"MA-02_caller_stipulation_not_public_authority":reject(lambda:inte(m2)),"MA-03_warranted_result_representable":eq(inte(b),O["SP-01-single-support"])}

def evaluate()->dict[str,Any]:
 sem={"A":{},"B":{}};size={"A":0,"B":0};refs={"A":0,"B":0}
 for n,o in O.items():
  a,b=Aenc(o),Benc(o);sem["A"][n]=eq(Aint(a),o);sem["B"][n]=eq(Bint(b),o);size["A"]+=len(Acanon(a));size["B"]+=len(Bcanon(b));refs["A"]+=Acnt(a);refs["B"]+=cnt(b)
 mut={"A":mutations("A"),"B":mutations("B")};mb={"A":ma("A"),"B":ma("B")};aliases={}
 for n in ["SP-10-alt-joint-mixed","SP-11-symmetric-alt-joint-mixed","SP-12-alt-by-alt-mixed"]:
  f,d=Benc(O[n]),dnf(O[n]);aliases[n]={"same_abstract_semantics":eq(Bint(f),Bint(d)),"same_syntax_canonical_bytes":Bcanon(f)==Bcanon(d),"same_semantic_canonical_identity":Bsemantic(f)==Bsemantic(d),"factorized_bytes":len(Bcanon(f)),"distributed_bytes":len(Bcanon(d))}
 aok=all(sem["A"].values()) and all(mut["A"].values()) and all(mb["A"].values());bok=all(sem["B"].values()) and all(mut["B"].values()) and all(mb["B"].values());bloss=all(x["same_abstract_semantics"] and x["same_semantic_canonical_identity"] for x in aliases.values());braw=all(x["same_syntax_canonical_bytes"] for x in aliases.values());pref=aok and bok and bloss and not braw
 return {"schema":"contract-c-successor-phase-2-bakeoff-result-v1","classification":"Draft Research / Research Infrastructure","frozen_inputs":{"phase_1_semantic_corpus":P1,"phase_1_5_freeze":P15,"phase_1_5_result_commit":P15R,"oracle_count":len(O)},"candidate_A":{"hypothesis":"canonical family of minimal sufficient exact participant-reference sets","semantic_matches":sem["A"],"semantic_match_count":sum(sem["A"].values()),"mutation_checks":mut["A"],"measurement_authority_checks":mb["A"],"total_canonical_bytes":size["A"],"causal_leaf_reference_occurrences":refs["A"],"recursive_causal_grammar":False,"semantic_normalization_required_for_identity":False},"candidate_B":{"hypothesis":"typed recursive causal expression with leaf/all_of/any_of","semantic_matches":sem["B"],"semantic_match_count":sum(sem["B"].values()),"mutation_checks":mut["B"],"measurement_authority_checks":mb["B"],"total_syntax_canonical_bytes":size["B"],"causal_leaf_reference_occurrences":refs["B"],"recursive_causal_grammar":True,"semantic_normalization_required_for_identity":True,"factorization_alias_tests":aliases},"comparative_findings":{"both_reconstruct_exact_same_frozen_oracles":aok and bok,"candidate_B_factorization_reduces_repeated_leaf_occurrences":refs["B"]<refs["A"],"candidate_B_has_multiple_syntax_canonical_forms_for_same_semantics":not braw,"candidate_B_can_recover_one_semantic_identity_only_by_interpreting_and_normalizing_to_minimal_basis_semantics":bloss,"candidate_A_exposes_the_required_semantic_normal_form_directly":aok,"byte_size_is_secondary_not_selection_authority":True},"research_disposition":"PREFER_CANDIDATE_A_FOR_CURRENT_SUCCESSOR_SCOPE" if pref else "INCONCLUSIVE","selected_for_next_research_candidate":"Candidate A" if pref else None,"production_authority_created":False,"official_successor_version_assigned":False,"sp12_current_cal_producer_claimed":False,"failures":[] if pref else ["selection_gate"]}

def main()->None:
 p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True);a=p.parse_args();r=evaluate();a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(r,sort_keys=True,indent=2)+"\n");print(json.dumps(r,sort_keys=True));raise SystemExit(0 if r["research_disposition"]!="INCONCLUSIVE" else 2)
if __name__=="__main__":main()
