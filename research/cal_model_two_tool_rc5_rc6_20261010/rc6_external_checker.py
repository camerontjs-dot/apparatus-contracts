#!/usr/bin/env python3
"""Host-side machine adjudicator of frozen CAL RC6 first model-generated tools.
Written and source-identity pinned before first model invocation. No new model
requests or actions. Never awards Q13 admission or general context-free status.
"""
from pathlib import Path
import hashlib
import json
import re
import sys

ROOT=Path(__file__).resolve().parent
RC4=ROOT/"candidate"/"research"/"cal_fixed_ollama_launcher_rc4_20261010"
EVID=ROOT/"receipts"/"FIRST"
FREEZE=ROOT/"controller"/"RC6-FREEZE.json"
MODEL="llamacpp:c97eb11d70b1acdc88af01eef566c1fe4f7fbe93eb1afc06871132f293ff425a"
EXPECTED_FILES={
 "data/marker.txt":"04d7c29ff732dcb8c993138ab73cfc3195ffd6e52a7cb26254bb3c2c9ba099c7",
 "instructions/request.txt":"fe139a5eee24ab24be7eb05af759de8f0f1705ebfd35b2d3958a304a7aa98987"}
def sha(b:bytes):return hashlib.sha256(b).hexdigest()
def digest(p:Path):return sha(p.read_bytes())
def pairs_hook(pairs):
    x={}
    for k,v in pairs:
        if k in x:raise ValueError("DUPLICATE_JSON_KEY")
        x[k]=v
    return x
def decode(data):return json.loads(data,object_pairs_hook=pairs_hook)
def load(p:Path):return decode(p.read_bytes())
def adjudicate():
    out=ROOT/"receipts"/"RC6-FIRST-EXTERNAL-VERDICT.json"
    if out.exists():raise RuntimeError("FIRST_GRADE_ALREADY_EXISTS")
    freeze=load(FREEZE)
    result=load(EVID/"FIRST-RESULT.json")
    checks={}
    checks["model_first_trace_completed"]=result.get("result")=="PASS_BOUNDED_SYNTHETIC_MODEL_GENERATED_TWO_FUNCTIONS"
    checks["source_all_frozen_sha_valid"]=all(digest(ROOT/p)==h for p,h in freeze["source_sha256"].items())
    checks["checker_source_pre_frozen"]=digest(Path(__file__))==freeze["source_sha256"]["rc6_external_checker.py"]
    checks["rc4_precursor_identity"]=freeze["rc4_frozen_commit"]=="e53fc412a0db007ba87c4d1720cee66b781fc89c"
    checks["rc4_frozen_manifest"]=digest(RC4/"MANIFEST.json")=="cad5a34c4e69d7eb2145addb5ef6b9d955df02fe33b0cfc347470106cff2e8cf"
    checks["rc4_packet_hashes_exact"]=freeze["packet"]["files"]==EXPECTED_FILES
    checks["bounded_two_tools_configured"]=freeze["allowed_tools"]==["read_packet_file","write_result"]
    checks["q13_admission_absent"]=result.get("actor_admission")=="Q13_NOT_AUTHORIZED"
    tools=result.get("model_generated_tools",[])
    checks["model_generated_three_action_positive"]=len(tools)==3 and [x.get("name") for x in tools]==["read_packet_file","read_packet_file","write_result"]
    checks["model_tools_all_executed_not_mocked"]=len(tools)==3 and all(x.get("status")=="EXECUTED" and x.get("executions_after",0)>x.get("executions_before",0) for x in tools)
    checks["exact_read_order_then_one_write"]=result.get("tool_sequence")==["instructions/request.txt","data/marker.txt","answer.txt"]
    checks["original_first_model_requests_stored"]=result.get("model_first_requests") in (2,3,4,5)
    checks["worker_fresh_and_owned"]=load(EVID/"worker-owned-identity.json").get("world_hash")==freeze["packet"]["combined_sha256"]
    conf=load(EVID/"worker-effective-config.json")
    checks["worker_effective_runtime_constraints"]=bool(conf["checks"]) and all(conf["checks"].values())
    obs=load(EVID/"worker-network-observation.json")
    checks["same_worker_network_controls"]=bool(obs["effective_checks"]) and all(obs["effective_checks"].values())
    teardown=load(EVID/"owned-teardown.json")
    checks["task_owned_worker_removed"]=teardown.get("removed") is True and result.get("owned_teardown",{}).get("removed") is True
    provider=load(EVID/"provider-identity.json")
    checks["pinned_model_id_before_inference"]=provider["model"]==MODEL and provider["digest"]==freeze["model_digest"]
    checks["source_host_ollama_binary"]=provider["ollama_executable_sha256"]==freeze["ollama_executable_sha256"]
    checks["source_host_docker_binary"]=provider["docker_binary_sha256"]==freeze["docker_binary_sha256"]
    checks["worker_image_exact"]=provider["image_id"]==freeze["image_id"]
    msg_basis=list(freeze["request_first"]["messages"])
    request_n=result.get("model_first_requests",0)
    seen_calls=[]
    requests=[];responses=[]
    for turn in range(1,request_n+1):
        reqfile=EVID/f"model-{turn:02d}-request.json"
        respfile=EVID/f"model-{turn:02d}-response.json"
        if not reqfile.exists() or not respfile.exists():
            checks[f"turn_{turn:02d}_raw_preserved"]=False
            continue
        req=load(reqfile);resp=load(respfile)
        requests.append(req);responses.append(resp)
        expect=dict(freeze["request_first"]);expect["messages"]=msg_basis
        checks[f"turn_{turn:02d}_request_exact_pinned_tools_and_messages"]=(req==expect)
        checks[f"turn_{turn:02d}_model_identity"]=resp.get("model")==MODEL
        message=resp.get("message") or {}
        rawcalls=message.get("tool_calls") or []
        checks[f"turn_{turn:02d}_provider_generated_calls_present"]=isinstance(rawcalls,list) and len(rawcalls)>0
        msg_basis.append(message)
        for i,call in enumerate(rawcalls,1):
            try:
                actual=load(EVID/f"tool-turn-{turn:02d}-{i:02d}-request.json")
                action=load(EVID/f"tool-turn-{turn:02d}-{i:02d}-decision.json")
                same=actual==call and action["raw_sha256"]==digest(EVID/f"tool-turn-{turn:02d}-{i:02d}-request.json") # normalized bytes? raw file canonical eq sha
                # sha check for canonical recorded raw bytes
                checks[f"tool_{turn:02d}_{i:02d}_unmodified_provider_call"]=same
                name=call["function"]["name"]
                args=call["function"]["arguments"]
                checks[f"tool_{turn:02d}_{i:02d}_allowlisted_name"]=name in ("read_packet_file","write_result")
                checks[f"tool_{turn:02d}_{i:02d}_exact_args"]=(
                  args=={"path":"instructions/request.txt"} or
                  args=={"path":"data/marker.txt"} or
                  (isinstance(args,dict) and set(args)=={"path","content"} and args.get("path")=="answer.txt"
                   and isinstance(args.get("content"),str)))
                checks[f"tool_{turn:02d}_{i:02d}_no_forged_success"]=action.get("status")=="EXECUTED" and action.get("executions_after",0)>action.get("executions_before",0)
                seen_calls.append(name)
                msg_basis.append({"role":"tool","tool_name":name,
                  "content":json.dumps(action["result"],sort_keys=True,ensure_ascii=False)})
            except Exception:
                checks[f"tool_{turn:02d}_{i:02d}_raw_integrity"]=False
    checks["all_messages_reconstructed"]=len(requests)==request_n and len(responses)==request_n and all(checks.get(f"turn_{i:02d}_request_exact_pinned_tools_and_messages") for i in range(1,request_n+1))
    checks["visible_model_requested_tools_match_actions"]=seen_calls==[v.get("name") for v in tools]
    checks["two_tools_only_in_every_model_request"]=bool(requests) and all([x["function"]["name"] for x in req.get("tools",[])]==["read_packet_file","write_result"] for req in requests)
    checks["no_hidden_gold_in_initial_prompt"]=bool(requests) and "hidden expectations" not in json.dumps(requests[0]["messages"]).lower() and "controller-private" not in json.dumps(requests[0]["messages"]).lower()
    actual=load(EVID/"answer-original-observation.json")
    expected=(RC4/"public-synthetic-source"/"data"/"marker.txt").read_bytes()
    checks["answer_original_bytes_exact_expected"]=bytes.fromhex(actual["output_hex_controller_private"])==expected
    checks["all_answer_checks_true"]=bool(actual.get("checks")) and all(actual["checks"].values())
    checks["answer_exact_approved_sha256"]=actual["sha256"]==EXPECTED_FILES["data/marker.txt"]
    n=len(checks);count=sum(bool(x) for x in checks.values())
    verdict="QUALIFIED_FOR_BOUNDED_SYNTHETIC_MODEL_GENERATED_CAL_TOOL_USE" if count==n else "NOT_QUALIFIED_REQUIRED_EVIDENCE_FAILED_OR_MISSING"
    report={"schema":"cal-rc6-external-first-grade/v1","disposition":verdict,
      "passed":count,"total":n,"failed":[k for k,v in checks.items() if not v],
      "checks":checks,
      "rc4_frozen_sha256":freeze["rc4_freeze_sha256"],
      "new_rc6_model_digest":freeze["model_digest"],
      "new_rc6_first_result_sha256":digest(EVID/"FIRST-RESULT.json"),
      "model_tool_order":seen_calls,
      "claim_ceiling":"known public synthetic model-generated tool-use, hosted Ollama/controller trusted, worker network-none; no blind CAL science",
      "q13_actor_admitted":False,
      "independent_authorship":"NO: host-side mechanical checker separately frozen, same research author"}
    if out.exists():raise RuntimeError("FIRST_GRADE_IMMUTABLE")
    out.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"disposition":verdict,"passed":count,"total":n,
      "failed":report["failed"],"model_tool_order":seen_calls,"q13":False},indent=2))
    return 0 if count==n else 2
if __name__=="__main__":
    try:sys.exit(adjudicate())
    except Exception as e:
        print(json.dumps({"status":"NOT_QUALIFIED_CHECKER_EXCEPTION","type":type(e).__name__,"detail":str(e)[:250]}))
        # Structured fail, never a silent false pass.
        path=ROOT/"receipts"/"RC6-FIRST-EXTERNAL-VERDICT.json"
        if not path.exists():
            path.write_text(json.dumps({"schema":"cal-rc6-external-first-grade-error",
              "disposition":"NOT_QUALIFIED_REQUIRED_EVIDENCE_FAILED_OR_MISSING",
              "exception":type(e).__name__,"q13_actor_admitted":False,
              "passed":0,"total":1,"failed":["MISSING_OR_MALFORMED_OR_INCONSISTENT_EVIDENCE"]},sort_keys=True,indent=2)+"\n")
        sys.exit(2)
