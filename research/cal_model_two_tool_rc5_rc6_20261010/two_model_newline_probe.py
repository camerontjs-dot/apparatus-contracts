#!/usr/bin/env python3
"""Frozen comparative native-function newline calibration, two model profiles.
Not a CAL worker experiment and not Q13 admission.
"""
from pathlib import Path
import datetime,hashlib,json,sys,urllib.request,urllib.error,time
ROOT=Path(__file__).resolve().parent
OUT=ROOT/"two-model-native-tool-newline-20261010"
EXPECTED="CHECK-LINE-001\n"
def sha(v):return hashlib.sha256(v).hexdigest()
def write(p,b):
    if p.exists():raise RuntimeError("REFUSE_OVERWRITE")
    with p.open("xb") as f:f.write(b)
def jsonb(v):return (json.dumps(v,sort_keys=True,indent=2,ensure_ascii=False)+"\n").encode()
def main():
    if OUT.exists():raise RuntimeError("TWO_ARM_CALIBRATION_ALREADY_EXISTS")
    OUT.mkdir()
    arms=[
      ("qwen3.5-9b-think-true", "llamacpp:c97eb11d70b1acdc88af01eef566c1fe4f7fbe93eb1afc06871132f293ff425a",True,850),
      ("gemma4-12b-think-false","gemma4:12b",False,350)]
    frozen={}
    system=("Synthetic function-call serialization test. Call write_result once, with path answer.txt. "
      "The content string MUST preserve the final U+000A linefeed, not strip it. "
      "In JSON representation, the final character MUST be encoded as \\n, for example \"EXAMPLE\\n\".")
    user=("Call write_result with path answer.txt and content equal to CHECK-LINE-001 "
      "followed by precisely one newline LF (U+000A). No other content or output.")
    tool={"type":"function","function":{"name":"write_result",
      "description":"Synthetic tool. Not executed; returns arguments to checker.",
      "parameters":{"type":"object","required":["path","content"],"properties":{"path":{"type":"string","enum":["answer.txt"]},"content":{"type":"string"}}}}}
    for short,model,think,budget in arms:
        req={"model":model,"messages":[{"role":"system","content":system},{"role":"user","content":user}],
         "tools":[tool],"options":{"seed":173,"temperature":0,"num_predict":budget,"num_ctx":4096},
         "stream":False,"think":think,"keep_alive":0}
        raw=json.dumps(req,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
        arm=OUT/short;arm.mkdir()
        write(arm/"FROZEN-REQUEST.json",raw)
        frozen[short]={"request_sha256":sha(raw),"model":model,"think":think,"num_predict":budget,
          "expected_sha256":sha(EXPECTED.encode()),"first_response":"NOT_RUN"}
    write(OUT/"PREEXPOSURE-PLAN.json",jsonb({"schema":"two-model-native-function-linefeed-comparison/v1",
     "prepared_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
     "arms":frozen,"known_synthetic_gold_sha256":sha(EXPECTED.encode()),
     "source_provenance":"Qwen native tool output missing final LF twice, while Qwen text JSON preserved LF",
     "not_CAL_Q13_admission":True}))
    results=[]
    for short,model,think,budget in arms:
        dir_=OUT/short;raw=(dir_/"FROZEN-REQUEST.json").read_bytes()
        if sha(raw)!=frozen[short]["request_sha256"]:raise RuntimeError("FROZEN_REQUEST_DRIFT")
        begin=time.monotonic();status=None;err=None
        try:
            opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
            with opener.open(urllib.request.Request("http://127.0.0.1:11434/api/chat",
                  data=raw,headers={"Content-Type":"application/json"},method="POST"),timeout=175) as f:
                b=f.read(2*1024*1024)
            write(dir_/"MODEL-RESPONSE-FIRST.json",b)
            envelope=json.loads(b)
            calls=envelope.get("message",{}).get("tool_calls") or []
            functions=[x.get("function",{}) for x in calls]
            args=functions[0].get("arguments",{}) if functions else {}
            content=args.get("content") if isinstance(args,dict) else None
            status="PASS_NATIVE_TOOL_EXACT_NEWLINE" if content==EXPECTED else "FAIL_NATIVE_TOOL_NEWLINE_OR_MISSING_CALL"
        except Exception as e:
            content=None;functions=[];status="INCONCLUSIVE_TRANSPORT_ERROR";err=type(e).__name__
        result={"arm":short,"model":model,"think":think,"num_predict":budget,
         "status":status,"elapsed_seconds":round(time.monotonic()-begin,2),
         "tool_names":[x.get("name") for x in functions],
         "content_length":len(content.encode()) if isinstance(content,str) else None,
         "content_ends_lf":bool(isinstance(content,str) and content.endswith("\n")),
         "exact_expected":content==EXPECTED,"transport_error":err,
         "raw_first_sha256":sha((dir_/"MODEL-RESPONSE-FIRST.json").read_bytes()) if (dir_/"MODEL-RESPONSE-FIRST.json").exists() else None,
         "no_tools_executed":True}
        write(dir_/"FIRST-RESULT.json",jsonb(result))
        print(json.dumps(result,indent=2),flush=True)
        results.append(result)
    write(OUT/"COMPARISON-FIRST.json",jsonb({"schema":"native-tool-linefeed-operator-only-calibration",
      "results":results,
      "Q13":"NOT_AUTHORIZED","no_model_actor_admitted":True,
      "external_gold_not_exposed_to_worker":True}))
    return 0
if __name__=="__main__":sys.exit(main())
