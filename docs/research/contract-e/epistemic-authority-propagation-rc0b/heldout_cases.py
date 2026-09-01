from __future__ import annotations

import hashlib


def H(s): return hashlib.sha256(s.encode()).hexdigest()


def basis(domain, operation, scope, target_class, *, subject="cal", basis_type="policy", authority_conferring=True, current=True, valid=True, **extra):
    b={"basis_type":basis_type,"authority_conferring":authority_conferring,"subject":subject,"domain":domain,"operation":operation,"scope":scope,"target_class":target_class,"current":current,"valid":valid}
    b.update(extra); return b


def obs(h, rid="o1", producer="source_observer"):
    return {"id":rid,"authority_kind":"observation","producer_type":producer,"status":"established","source_hash":h,"dependencies":[]}


def meas(h, rid="m1", dep="o1", *, b=None, status="established"):
    return {"id":rid,"authority_kind":"measurement","producer_type":"language_instrument","status":status,"source_hash":h,"subject":"cal","domain":"measurement","operation":"measure","scope":"claim","target_class":"claim","dependencies":[dep],"basis":b or basis("measurement","measure","claim","claim")}


def proposal(pid="p1", dimension="role_binding", atom="review(auditor,packet)", embedding=None):
    return {"id":pid,"dimension":dimension,"atom":atom,"embedding":embedding}


def sem_receipt(h, rid="s1", dep="m1", pid="p1", *, b=None, embedding=None, claim_level="narrator_fact", preserves=False, status="established"):
    return {"id":rid,"authority_kind":"semantic","producer_type":"semantic_validator","status":status,"source_hash":h,"subject":"cal","domain":"semantic","operation":"interpret","scope":"claim","target_class":"claim","dependencies":[dep],"proposal_id":pid,"claim_level":claim_level,"preserves_embedding":preserves,"promotion_source":"independent_semantic_validation","basis":b or basis("semantic","interpret","claim","claim",semantic_dimensions=["role_binding"],allowed_embeddings=[] if embedding is None else [embedding])}


def decision_receipt(h, rid="d1", dep="s1", *, b=None, status="established"):
    return {"id":rid,"authority_kind":"decision","producer_type":"decision_engine","status":status,"source_hash":h,"subject":"cal","domain":"decision","operation":"decide","scope":"claim","target_class":"decision","dependencies":[dep],"basis":b or basis("decision","decide","claim","decision")}


def resolution_receipt(h, rid, resolves, dep="m1", *, b=None, status="established"):
    return {"id":rid,"authority_kind":"resolution","producer_type":"authority_resolver","status":status,"source_hash":h,"subject":"cal","domain":"resolution","operation":"resolve","scope":"claim","target_class":"claim","dependencies":[dep],"resolves_ids":list(resolves),"basis":b or basis("resolution","resolve","claim","claim")}


def sem_request(h, *, pid="p1", dep="m1", b=None, promotion="independent_semantic_validation", level="narrator_fact", preserves=False, resolver_ids=None, **extra):
    q={"authority_kind":"semantic","producer_type":"semantic_validator","source_hash":h,"subject":"cal","domain":"semantic","operation":"interpret","scope":"claim","target_class":"claim","dependencies":[dep],"proposal_id":pid,"claim_level":level,"preserves_embedding":preserves,"promotion_source":promotion,"basis":b or basis("semantic","interpret","claim","claim",semantic_dimensions=["role_binding"],allowed_embeddings=[]),"resolver_receipt_ids":resolver_ids or []}
    q.update(extra); return q


def case(cid,family,source,proposals,receipts,request,expected,*,tags=(),conflicts=(),residues=(),comparisons=(),pair_id=None,pair_expectation=None):
    return {"id":cid,"family":family,"tags":list(tags),"raw_source":source,"source_hash":H(source),"proposals":list(proposals),"receipts":list(receipts),"conflicts":list(conflicts),"residues":list(residues),"comparison_receipts":list(comparisons),"request":request,"expected_allowed":expected,"pair_id":pair_id,"pair_expectation":pair_expectation}


CASES=[]

# 1. Plain semantic positives with recursively valid measurement lineage.
for i,dim in enumerate(["role_binding","membership","quantifier","permission","temporal","comparison","polarity","subclass"],1):
    src=f"Fresh RC0B semantic control {i}: the source explicitly warrants {dim}."; h=H(src)
    p=proposal("p1",dim,f"{dim}_atom_{i}")
    sb=basis("semantic","interpret","claim","claim",semantic_dimensions=[dim],allowed_embeddings=[])
    CASES.append(case(f"S-POS-{i:02d}","semantic_positive",src,[p],[obs(h),meas(h)],sem_request(h,b=sb),True))

# 2. Embedded semantics: preserving scope can be authoritative; narrator-level promotion cannot.
for i,emb in enumerate(["quantifier","modality","permission","conditional","attribution","quantitative"],1):
    src=f"Fresh embedding {i}: an event appears only under {emb} scope."; h=H(src)
    p=proposal("p1","role_binding",f"embedded_{i}",emb)
    sb=basis("semantic","interpret","claim","claim",semantic_dimensions=["role_binding"],allowed_embeddings=[emb])
    CASES.append(case(f"E-POS-{i:02d}","scope_positive",src,[p],[obs(h),meas(h)],sem_request(h,b=sb,level="embedded_semantic",preserves=True),True))
    CASES.append(case(f"E-NEG-{i:02d}","scope_embedding",src,[p],[obs(h),meas(h)],sem_request(h,b=sb,level="narrator_fact",preserves=False),False,tags=["rc0_safety_regression"]))

# 3. Established-looking semantic dependency without valid recursive lineage.
for i,mode in enumerate(["missing_measurement","missing_observation","ancestor_domain_relabel","ancestor_operation_relabel","stale_ancestor","invalid_ancestor"],1):
    src=f"Recursive lineage attack {i}: {mode}."; h=H(src); p=proposal()
    receipts=[]
    if mode=="missing_measurement":
        receipts=[sem_receipt(h,dep="m-missing")]
    elif mode=="missing_observation":
        receipts=[meas(h,dep="o-missing"),sem_receipt(h)]
    else:
        mb=basis("measurement","measure","claim","claim")
        if mode=="ancestor_domain_relabel": mb["domain"]="citation"
        if mode=="ancestor_operation_relabel": mb["operation"]="quote"
        if mode=="stale_ancestor": mb["current"]=False
        if mode=="invalid_ancestor": mb["valid"]=False
        receipts=[obs(h),meas(h,b=mb),sem_receipt(h)]
    q={"authority_kind":"decision","producer_type":"decision_engine","source_hash":h,"subject":"cal","domain":"decision","operation":"decide","scope":"claim","target_class":"decision","dependencies":["s1"],"basis":basis("decision","decide","claim","decision")}
    CASES.append(case(f"LIN-NEG-{i:02d}","lineage",src,[p],receipts,q,False,tags=["recursive_lineage_attack","rc0_safety_regression"]))

# 4. Cycles in lineage graph.
for i in range(1,4):
    src=f"Authority lineage cycle {i}: semantic and measurement receipts depend on each other."; h=H(src); p=proposal()
    m=meas(h,dep="s1"); s=sem_receipt(h,dep="m1")
    q={"authority_kind":"decision","producer_type":"decision_engine","source_hash":h,"subject":"cal","domain":"decision","operation":"decide","scope":"claim","target_class":"decision","dependencies":["s1"],"basis":basis("decision","decide","claim","decision")}
    CASES.append(case(f"CYCLE-NEG-{i:02d}","lineage_cycle",src,[p],[m,s],q,False,tags=["recursive_lineage_attack","cycle_attack"]))

# 5. Non-authority-conferring basis substitutions at semantic transition.
for i,bt in enumerate(["supporting_artifact","citation","warrant","competence","evidence_receipt","comparison_receipt","result_payload","execution_report"],1):
    src=f"Non-conferring basis substitution {i}: {bt}."; h=H(src); p=proposal()
    b=basis("semantic","interpret","claim","claim",basis_type=bt,authority_conferring=False,semantic_dimensions=["role_binding"],allowed_embeddings=[])
    CASES.append(case(f"BASIS-NEG-{i:02d}","basis",src,[p],[obs(h),meas(h)],sem_request(h,b=b),False,tags=["nonconferring_basis_attack","rc0_safety_regression"]))

# 6. Valid resolver receipts discharge exact relevant residue/conflict IDs.
for i in range(1,4):
    src=f"Valid residue resolution {i}: an authorized resolver discharges exactly r{i}."; h=H(src); p=proposal()
    rr=resolution_receipt(h,"rr1",[f"r{i}"])
    CASES.append(case(f"RES-POS-{i:02d}","resolution_positive",src,[p],[obs(h),meas(h),rr],sem_request(h,resolver_ids=["rr1"]),True,tags=["valid_resolution"],residues=[{"id":f"r{i}","status":"unresolved","relevant":True}]))
for i in range(1,3):
    src=f"Valid multi-residue resolution {i}: resolver explicitly covers both blocking IDs."; h=H(src); p=proposal()
    rr=resolution_receipt(h,"rr1",[f"ra{i}",f"rb{i}"])
    CASES.append(case(f"RES-MULTI-POS-{i:02d}","resolution_positive",src,[p],[obs(h),meas(h),rr],sem_request(h,resolver_ids=["rr1"]),True,tags=["valid_resolution"],residues=[{"id":f"ra{i}","status":"unresolved","relevant":True},{"id":f"rb{i}","status":"contested","relevant":True}]))
src="Valid conflict resolution: resolver explicitly covers the contested conflict."; h=H(src); p=proposal(); rr=resolution_receipt(h,"rr1",["c1"])
CASES.append(case("CON-POS-01","resolution_positive",src,[p],[obs(h),meas(h),rr],sem_request(h,resolver_ids=["rr1"]),True,tags=["valid_resolution"],conflicts=[{"id":"c1","status":"contested","relevant":True}]))

# 7. Bare resolved IDs are never resolution authority.
for i in range(1,4):
    src=f"Bare residue ID attack {i}: request merely names r{i} as resolved."; h=H(src); p=proposal()
    CASES.append(case(f"RES-BARE-NEG-{i:02d}","resolution",src,[p],[obs(h),meas(h)],sem_request(h,resolved_residue_ids=[f"r{i}"]),False,tags=["unauthorized_resolution_attack","rc0_safety_regression"],residues=[{"id":f"r{i}","status":"unresolved","relevant":True}]))
for i in range(1,3):
    src=f"Bare conflict ID attack {i}: request merely names c{i} as resolved."; h=H(src); p=proposal()
    CASES.append(case(f"CON-BARE-NEG-{i:02d}","resolution",src,[p],[obs(h),meas(h)],sem_request(h,resolved_conflict_ids=[f"c{i}"]),False,tags=["unauthorized_resolution_attack","rc0_safety_regression"],conflicts=[{"id":f"c{i}","status":"contested","relevant":True}]))

# 8. Resolver receipt attacks: wrong basis, partial coverage, unrelated coverage, missing lineage.
for i,mode in enumerate(["nonconferring","basis_domain","partial","unrelated","missing_dependency"],1):
    src=f"Resolver attack {i}: {mode}."; h=H(src); p=proposal(); residues=[{"id":"r1","status":"unresolved","relevant":True}]
    if mode=="partial": residues.append({"id":"r2","status":"unresolved","relevant":True})
    rb=basis("resolution","resolve","claim","claim")
    resolves=["r1"]
    dep="m1"
    if mode=="nonconferring": rb=basis("resolution","resolve","claim","claim",basis_type="supporting_artifact",authority_conferring=False)
    elif mode=="basis_domain": rb["domain"]="semantic"
    elif mode=="unrelated": resolves=["other"]
    elif mode=="missing_dependency": dep="m-missing"
    rr=resolution_receipt(h,"rr1",resolves,dep=dep,b=rb)
    CASES.append(case(f"RES-AUTH-NEG-{i:02d}","resolution",src,[p],[obs(h),meas(h),rr],sem_request(h,resolver_ids=["rr1"]),False,tags=["unauthorized_resolution_attack"],residues=residues))

# 9. Agreement does not confer semantic truth.
for i in range(1,4):
    src=f"Agreement laundering regression {i}: two measurements share an unsupported atom."; h=H(src)
    ps=[proposal("p1","role_binding",f"wrong{i}"),proposal("p2","role_binding",f"wrong{i}")]
    rec=[obs(h,"o1"),meas(h,"m1","o1"),obs(h,"o2"),meas(h,"m2","o2")]
    q=sem_request(h,dep="m1",promotion="comparison_agreement")
    CASES.append(case(f"AGR-NEG-{i:02d}","agreement",src,ps,rec,q,False,tags=["rc0_safety_regression"]))

# 10. Composition positive and missing-rule negative.
for i in range(1,3):
    src=f"Composition control {i}: independently established semantics compose under an explicit rule."; h=H(src); ps=[proposal("p1"),proposal("p2","temporal",f"before{i}")]
    rec=[obs(h),meas(h),sem_receipt(h,"s1",pid="p1"),sem_receipt(h,"s2",pid="p2",b=basis("semantic","interpret","claim","claim",semantic_dimensions=["temporal"],allowed_embeddings=[]))]
    cb=basis("composition","compose","claim","claim",component_dimensions=["role_binding","temporal"],composition_rule=f"rule{i}")
    q={"authority_kind":"composition","producer_type":"composition_governor","source_hash":h,"subject":"cal","domain":"composition","operation":"compose","scope":"claim","target_class":"claim","dependencies":["s1","s2"],"component_dimensions":["role_binding","temporal"],"basis":cb}
    CASES.append(case(f"COMP-POS-{i:02d}","composition_positive",src,ps,rec,q,True))
    cb2=dict(cb); cb2.pop("composition_rule")
    q2=dict(q); q2["basis"]=cb2
    CASES.append(case(f"COMP-NEG-{i:02d}","composition",src+" No composition rule is authorized.",ps,rec,q2,False,tags=["rc0_safety_regression"]))

# 11. Fully recursive semantic -> decision -> action chains.
for i in range(1,3):
    src=f"Valid action chain {i}: source→measurement→semantic→decision plus separate execution grant."; h=H(src); p=proposal()
    rec=[obs(h),meas(h),sem_receipt(h),decision_receipt(h)]
    ab=basis("action","execute","task","task",authority_domain="execution")
    q={"authority_kind":"action","producer_type":"action_authorizer","source_hash":h,"subject":"cal","domain":"action","operation":"execute","scope":"task","target_class":"task","dependencies":["d1"],"basis":ab}
    CASES.append(case(f"ACT-POS-{i:02d}","action_positive",src,[p],rec,q,True))
for i in range(1,3):
    src=f"Decision-to-action regression {i}: valid decision exists but action basis is not execution authority."; h=H(src); p=proposal()
    rec=[obs(h),meas(h),sem_receipt(h),decision_receipt(h)]
    ab=basis("action","execute","task","task")
    q={"authority_kind":"action","producer_type":"action_authorizer","source_hash":h,"subject":"cal","domain":"action","operation":"execute","scope":"task","target_class":"task","dependencies":["d1"],"basis":ab}
    CASES.append(case(f"ACT-NEG-{i:02d}","decision_action",src,[p],rec,q,False,tags=["rc0_safety_regression"]))

# 12. Verification requires independent observation, never an executor report.
for i in range(1,3):
    src=f"Independent verification {i}: independent observer records outcome."; h=H(src)
    vb=basis("verification","verify","outcome","outcome",authority_domain="verification")
    q={"authority_kind":"verification","producer_type":"outcome_verifier","source_hash":h,"subject":"cal","domain":"verification","operation":"verify","scope":"outcome","target_class":"outcome","dependencies":["o1"],"basis":vb}
    CASES.append(case(f"VER-POS-{i:02d}","verification_positive",src,[],[obs(h)],q,True))
for i in range(1,3):
    src=f"Executor verification regression {i}: only executor self-report exists."; h=H(src)
    bad={"id":"o1","authority_kind":"observation","producer_type":"executor_reporter","status":"established","source_hash":h,"dependencies":[]}
    vb=basis("verification","verify","outcome","outcome",authority_domain="verification")
    q={"authority_kind":"verification","producer_type":"outcome_verifier","source_hash":h,"subject":"cal","domain":"verification","operation":"verify","scope":"outcome","target_class":"outcome","dependencies":["o1"],"basis":vb}
    CASES.append(case(f"VER-NEG-{i:02d}","execution_verification",src,[],[bad],q,False,tags=["rc0_safety_regression"]))

# 13. Correct final outcome cannot repair missing authority lineage.
for i in range(1,3):
    src=f"Correct-outcome chain attack {i}: terminal result is right but semantic dependency is forged."; h=H(src); p=proposal()
    forged=sem_receipt(h,dep="m-missing")
    q={"authority_kind":"decision","producer_type":"decision_engine","source_hash":h,"subject":"cal","domain":"decision","operation":"decide","scope":"claim","target_class":"decision","dependencies":["s1"],"basis":basis("decision","decide","claim","decision"),"terminal_outcome":"correct"}
    CASES.append(case(f"CHAIN-NEG-{i:02d}","cross_stage",src,[p],[forged],q,False,tags=["recursive_lineage_attack","rc0_safety_regression"]))

# 14. Metamorphic same pairs: result/confidence wording changes, authority identical.
for i in range(1,4):
    pid=f"META-SAME-{i}"
    for suff,payload in [("A","low confidence"),("B","high confidence")]:
        src=f"Metamorphic same {i}-{suff}: {payload}; authority structure unchanged."; h=H(src); p=proposal()
        CASES.append(case(f"{pid}-{suff}","semantic_positive",src,[p],[obs(h),meas(h)],sem_request(h),True,pair_id=pid,pair_expectation="same"))

# 15. Flip pairs: basis currentness, basis type, and resolution authority alone change authority.
for i,mode in enumerate(["currentness","basis_type","resolver"],1):
    pid=f"META-FLIP-{i}"
    if mode=="currentness":
        for suff,current,expected in [("A",True,True),("B",False,False)]:
            src=f"Currentness flip {suff}: only currentness differs."; h=H(src); p=proposal(); sb=basis("semantic","interpret","claim","claim",current=current,semantic_dimensions=["role_binding"],allowed_embeddings=[])
            CASES.append(case(f"{pid}-{suff}","mutation",src,[p],[obs(h),meas(h)],sem_request(h,b=sb),expected,pair_id=pid,pair_expectation="flip"))
    elif mode=="basis_type":
        for suff,bt,conf,expected in [("A","policy",True,True),("B","supporting_artifact",False,False)]:
            src=f"Basis-type flip {suff}: only authority-conferring type differs."; h=H(src); p=proposal(); sb=basis("semantic","interpret","claim","claim",basis_type=bt,authority_conferring=conf,semantic_dimensions=["role_binding"],allowed_embeddings=[])
            CASES.append(case(f"{pid}-{suff}","mutation",src,[p],[obs(h),meas(h)],sem_request(h,b=sb),expected,pair_id=pid,pair_expectation="flip"))
    else:
        for suff,with_resolver,expected in [("A",True,True),("B",False,False)]:
            src=f"Resolver flip {suff}: only authorized resolver presence differs."; h=H(src); p=proposal(); rec=[obs(h),meas(h)]
            ids=[]
            if with_resolver:
                rec.append(resolution_receipt(h,"rr1",["r1"])); ids=["rr1"]
            CASES.append(case(f"{pid}-{suff}","mutation",src,[p],rec,sem_request(h,resolver_ids=ids),expected,residues=[{"id":"r1","status":"unresolved","relevant":True}],pair_id=pid,pair_expectation="flip"))

CASE_IDS=tuple(c["id"] for c in CASES)
assert len(CASE_IDS)==len(set(CASE_IDS))
assert len(CASES)>=70, len(CASES)
