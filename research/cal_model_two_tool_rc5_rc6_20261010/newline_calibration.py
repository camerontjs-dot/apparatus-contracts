#!/usr/bin/env python3
"""Single frozen Ollama newline tool-output calibration. No restricted worker and
no CAL admission; observation only, cannot pass CAL model qualification.
"""
from pathlib import Path
import hashlib,json,os,sys,datetime,urllib.request

ROOT=Path(__file__).resolve().parent
STUDY=ROOT/"newline-diagnostic-20261010"
MODEL="llamacpp:c97eb11d70b1acdc88af01eef566c1fe4f7fbe93eb1afc06871132f293ff425a"
EXPECTED="CHECK-LINE-001\n"
def sha(x:bytes):return hashlib.sha256(x).hexdigest()
def strict_pairs(pairs):
    o={}
    for k,v in pairs:
        if k in o:raise RuntimeError("DUPLICATE_KEY")
        o[k]=v
    return o
def main():
    if STUDY.exists():raise RuntimeError("FIRST_CALIBRATION_ATTEMPT_ALREADY_EXISTS")
    STUDY.mkdir(mode=0o700)
    system="This is a public synthetic JSON function serialization check. You must use the provided write_result function exactly once. The content must end with a real LF newline, U+000A. Do not strip whitespace."
    user=("Use write_result with path answer.txt. Its content must be the string "
          "CHECK-LINE-001 followed by precisely one LF (U+000A) newline. "
          "In JSON notation the intended content is \"CHECK-LINE-001\\n\". "
          "No additional text before or after the newline.")
    tool={"type":"function","function":{"name":"write_result","description":"Emit a synthetic string without executing a host action.","parameters":{"type":"object","required":["path","content"],"properties":{"path":{"type":"string","enum":["answer.txt"]},"content":{"type":"string"}}}}}
    req={"model":MODEL,"messages":[{"role":"system","content":system},{"role":"user","content":user}],
         "tools":[tool],"options":{"seed":173,"temperature":0,"num_predict":320,"num_ctx":4096},
         "think":False,"stream":False,"keep_alive":"2m"}
    raw=json.dumps(req,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
    f=STUDY/"FROZEN-REQUEST.json"
    f.write_bytes(raw)
    gold={"expected_output_sha256":sha(EXPECTED.encode()),"expected_length":len(EXPECTED),"expected_terminal_u000a":True,"model_digest":MODEL.split("llamacpp:")[1],
         "probe":"ONE_JSON_TOOL_CALL_SERIALIZATION_ONLY_NOT_CAL"}
    (STUDY/"GOLD.private.json").write_text(json.dumps(gold,sort_keys=True,indent=2)+"\n")
    (STUDY/"BEFORE-INFERENCE.json").write_text(json.dumps({"request_sha256":sha(raw),"gold_sha256":sha((STUDY/"GOLD.private.json").read_bytes()),
       "model_identity":MODEL,"utc":datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2,sort_keys=True)+"\n")
    request=urllib.request.Request("http://127.0.0.1:11434/api/chat",data=raw,headers={"Content-Type":"application/json"},method="POST")
    with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(request,timeout=125) as resp:
        body=resp.read(2*1024*1024)
    (STUDY/"FIRST-PROVIDER-ORIGINAL.json").write_bytes(body)
    j=json.loads(body,object_pairs_hook=strict_pairs)
    calls=j.get("message",{}).get("tool_calls") or []
    funcs=[x.get("function",{}) for x in calls if isinstance(x,dict)]
    content=funcs[0].get("arguments",{}).get("content") if funcs else None
    equal=isinstance(content,str) and content==EXPECTED
    result={"status":"PASS_PROVIDER_TOOL_NEWLINE_PRESERVED" if equal else "FAIL_PROVIDER_TOOL_NEWLINE_MISSING_OR_NO_TOOL",
        "raw_model_response_sha256":sha(body),
        "model_id":j.get("model"),
        "tools_generated":[f.get("name") for f in funcs],
        "content_length":len(content.encode()) if isinstance(content,str) else None,
        "ends_with_lf":bool(isinstance(content,str) and content.endswith("\n")),
        "exact_reference_match":bool(equal),
        "no_tool_executed":True,"q13_admission":"NOT_APPLICABLE"}
    (STUDY/"FIRST-VERDICT.json").write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(json.dumps(result,sort_keys=True,indent=2))
    return 0 if equal else 2
if __name__=="__main__":sys.exit(main())
