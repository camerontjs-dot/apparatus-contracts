#!/usr/bin/env python3
"""CAL RC6: fresh synthetic model-generated function-use qualification only.

This controller is trusted and outside the worker. The model ONLY submits
read_packet_file/write_result requests; fixed RC4 adapter exclusively mediates
Docker exec into a network-none 256MiB worker. Never admits Q13 or starts CAL
scientific pilot. First results and failures are preserved without retry.
"""
from pathlib import Path
import datetime
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
import urllib.error

ROOT=Path(__file__).resolve().parent
RC4=ROOT/"candidate"/"research"/"cal_fixed_ollama_launcher_rc4_20261010"
EVIDENCE=ROOT/"receipts"/"FIRST"
FROZEN=ROOT/"controller"/"RC6-FREEZE.json"
WORLD=ROOT/"stage"/"packet-world"
IMAGE="sha256:48b13b003dda20b16f9442b8475aa05fe21bf6579a8c881db92ffb4d8fd20f83"
MODEL="llamacpp:c97eb11d70b1acdc88af01eef566c1fe4f7fbe93eb1afc06871132f293ff425a"
DOCKER="/usr/local/bin/docker"
OLLAMA_URL="http://127.0.0.1:11434/api/chat"
SOURCE_KEYS={"MANIFEST.json","MODEL-REQUEST.json","TOOL-PROFILE.json","fixed_adapter.py","worker_control.py","network_state_validator.py"}
EXPECTED_FILES={"data/marker.txt":"04d7c29ff732dcb8c993138ab73cfc3195ffd6e52a7cb26254bb3c2c9ba099c7",
 "instructions/request.txt":"fe139a5eee24ab24be7eb05af759de8f0f1705ebfd35b2d3958a304a7aa98987"}
def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()
def digest(p:Path)->str:return sha(p.read_bytes())
def now()->str:return datetime.datetime.now(datetime.timezone.utc).isoformat()
def strict_pairs(pairs):
    result={}
    for key,value in pairs:
        if key in result:raise RuntimeError("DUPLICATE_JSON_KEY")
        result[key]=value
    return result
def decode(raw:bytes|str):
    return json.loads(raw,object_pairs_hook=strict_pairs,
        parse_constant=lambda value: (_ for _ in ()).throw(RuntimeError("INVALID_JSON_CONSTANT")))
def put(path:Path,obj):
    if path.exists():raise RuntimeError("REFUSE_OVERWRITE:"+path.name)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,sort_keys=True,indent=2,ensure_ascii=False)+"\n")
def write(path:Path,data:bytes):
    if path.exists():raise RuntimeError("REFUSE_OVERWRITE:"+path.name)
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("xb") as stream:
        stream.write(data);stream.flush();os.fsync(stream.fileno())
def get_adapter():
    sp=importlib.util.spec_from_file_location("frozen_rc4_adapter",RC4/"fixed_adapter.py")
    mod=importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod)
    return mod
def model_request_baseline():
    request=decode((RC4/"MODEL-REQUEST.json").read_bytes())
    if request["model"]!="qwen3.5:9b":raise RuntimeError("RC4_ORIGIN_CHANGED")
    request["model"]=MODEL
    request["keep_alive"]="2m"
    request["options"]["num_predict"]=256
    request["think"]=False
    request["messages"][0]["content"] += (
        " The write_result content MUST be a byte-for-byte copy of the"
        " content returned by read_packet_file for data/marker.txt,"
        " INCLUDING its terminal newline character (\n)."
        " Never strip, trim or normalize whitespace. This is exact"
        " source-byte reproduction, not a summary."
    )
    return request
def stage_packet():
    if WORLD.exists():raise RuntimeError("STAGED_PACKET_ALREADY_EXISTS")
    manifest=decode((RC4/"MANIFEST.json").read_bytes())
    listed={row["path"]:row["sha256"] for row in manifest["files"]}
    if listed!=EXPECTED_FILES:raise RuntimeError("RC4_FIXTURE_MANIFEST_DRIFT")
    if digest(RC4/"MANIFEST.json")!="cad5a34c4e69d7eb2145addb5ef6b9d955df02fe33b0cfc347470106cff2e8cf":
        raise RuntimeError("RC4_MANIFEST_BYTES_DRIFT")
    WORLD.mkdir(mode=0o700)
    src=RC4/"public-synthetic-source"
    for name,expected in sorted(EXPECTED_FILES.items()):
        source=src/name
        if source.is_symlink() or source.stat().st_nlink!=1:raise RuntimeError("SOURCE_LINK")
        raw=source.read_bytes()
        if sha(raw)!=expected:raise RuntimeError("FIXTURE_SOURCE_DRIFT")
        dst=WORLD/name;dst.parent.mkdir(exist_ok=True);write(dst,raw)
    got={str(x.relative_to(WORLD)):digest(x) for x in WORLD.rglob("*") if x.is_file()}
    if got!=EXPECTED_FILES or len(list(WORLD.rglob("*")))!=4:
        raise RuntimeError("WORLD_NOT_EXACT_ALLOWLIST")
    return {"files":got,"combined_sha256":sha(json.dumps(got,sort_keys=True).encode()),"manifest_sha256":digest(RC4/"MANIFEST.json")}
def preflight_freeze():
    frozen=decode(FROZEN.read_bytes())
    for name,expect in frozen["source_sha256"].items():
        if digest(ROOT/name)!=expect:raise RuntimeError("FROZEN_SOURCE_DRIFT:"+name)
    if frozen["model_identity"]!=MODEL or frozen["image_id"]!=IMAGE:
        raise RuntimeError("RUNTIME_IDENTITY_DRIFT")
    if frozen["packet"]["files"]!=EXPECTED_FILES:raise RuntimeError("FROZEN_PACKET_DRIFT")
    actual={str(p.relative_to(WORLD)):digest(p) for p in WORLD.rglob("*") if p.is_file()}
    if actual!=EXPECTED_FILES:raise RuntimeError("WORLD_DRIFT")
    if frozen["request_first"]!=model_request_baseline():raise RuntimeError("MODEL_REQUEST_DRIFT")
    if frozen["allowed_tools"]!=[x["function"]["name"] for x in frozen["request_first"]["tools"]]:
        raise RuntimeError("TOOL_INVENTORY_DRIFT")
    if frozen["allowed_tools"]!=["read_packet_file","write_result"]:raise RuntimeError("UNAUTHORIZED_TOOL_SET")
    return frozen
class Controller:
    def __init__(self,frozen):
        self.freeze=frozen
        self.c=0
        self.worker=None
        self.observed_calls=[]
        self.reads=[]
        self.writes=[]
        self.model_requests=[]
        self.model_replies=[]
        self.executions=[]
        self.first_failure=None
        self.start=now()
        self.adapter_module=get_adapter()
        self.pinned_host={"ollama":"/usr/local/bin/ollama","docker":DOCKER}
    def cmd(self,argv,inp=b"",timeout=30):
        if self.worker and argv[0]==DOCKER and "--context" not in argv:
            raise RuntimeError("UNSCOPED_DOCKER_COMMAND")
        self.c+=1;n=self.c
        p=subprocess.run(argv,input=inp,capture_output=True,timeout=timeout,
                         env={"HOME":str(Path.home()),"PATH":"/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin","LANG":"C","LC_ALL":"C"})
        payload={"serial":n,"argv_sha256":sha(json.dumps(argv).encode()),"argv":argv,
                 "exit":p.returncode,"stdin_sha256":sha(inp),
                 "stdout_sha256":sha(p.stdout),"stderr_sha256":sha(p.stderr),
                 "timestamp_utc":now()}
        # Command stdout may contain the public marker. Keep raw streams external.
        rawdir=EVIDENCE/f"command-{n:03d}"
        rawdir.mkdir()
        write(rawdir/"stdout.bin",p.stdout)
        write(rawdir/"stderr.bin",p.stderr)
        if inp:write(rawdir/"stdin.bin",inp)
        put(rawdir/"record.json",payload)
        self.executions.append(payload)
        return p
    def docker(self,*args,inp=b""):
        return self.cmd([DOCKER,"--context","desktop-linux",*args],inp,timeout=40)
    def check_identity(self):
        if sha(Path("/usr/local/bin/ollama").read_bytes())!=self.freeze["ollama_executable_sha256"]:
            raise RuntimeError("OLLAMA_BINARY_DRIFT")
        if digest(Path(DOCKER))!=self.freeze["docker_binary_sha256"]:
            raise RuntimeError("DOCKER_BINARY_DRIFT")
        r=self.docker("image","inspect",IMAGE)
        if r.returncode:raise RuntimeError("PINNED_IMAGE_NOT_PRESENT")
        info=decode(r.stdout)[0]
        if info["Id"]!=IMAGE or info["Architecture"]!="arm64" or info["Os"]!="linux":
            raise RuntimeError("IMAGE_DRIFT")
        tags=decode(urllib.request.urlopen("http://127.0.0.1:11434/api/tags",timeout=5).read())
        found=[x for x in tags.get("models",[]) if x["name"]==MODEL]
        if len(found)!=1 or found[0]["digest"]!=self.freeze["model_digest"]:
            raise RuntimeError("MODEL_ALIAS_AMBIGUITY")
        put(EVIDENCE/"provider-identity.json",{"model":MODEL,"digest":found[0]["digest"],
          "ollama_executable_sha256":self.freeze["ollama_executable_sha256"],
          "docker_binary_sha256":self.freeze["docker_binary_sha256"],
          "image_id":info["Id"],"observer_utc":now()})
    def create_worker(self):
        name="cal-rc6-"+self.freeze["run_nonce"][-12:]
        argv=("create","--pull","never","--platform","linux/arm64",
          "--name",name,"--label","cal.qualification.owner="+name,"--hostname","cal-public-synthetic",
          "--user","65532:65532","--read-only","--cap-drop","ALL","--security-opt","no-new-privileges",
          "--network","none","--ipc","none","--cgroupns","private","--pids-limit","64",
          "--memory","256m","--memory-swap","256m","--cpus","1",
          "--env","PATH=/usr/local/bin:/usr/bin:/bin","--no-healthcheck",
          "--mount",f"type=bind,source={WORLD},target=/packet,readonly,bind-recursive=disabled,bind-propagation=rprivate",
          "--tmpfs","/scratch:rw,noexec,nosuid,nodev,size=16m,uid=65532,gid=65532,mode=700",
          "--entrypoint","/usr/bin/env",IMAGE,"-i","PATH=/usr/local/bin:/usr/bin:/bin","HOME=/",
          "/usr/local/bin/python3","-I","-B","-c","import time; time.sleep(600)")
        res=self.docker(*argv)
        if res.returncode:raise RuntimeError("WORKER_CREATE_FAILED")
        cid=res.stdout.decode().strip()
        if not re.fullmatch("[a-f0-9]{64}",cid):raise RuntimeError("WORKER_ID_INVALID")
        self.worker=cid
        put(EVIDENCE/"worker-owned-identity.json",{"cid":cid,"name":name,"first_utc":now(),"world_hash":self.freeze["packet"]["combined_sha256"]})
        run=self.docker("start",cid)
        if run.returncode:raise RuntimeError("WORKER_START_FAILED")
        return cid
    def prove_worker(self):
        r=self.docker("inspect",self.worker)
        if r.returncode:raise RuntimeError("WORKER_INSPECTION_FAILED")
        i=decode(r.stdout)[0];hc=i["HostConfig"];cfg=i["Config"]
        checks={
         "exact_uid_gid":cfg["User"]=="65532:65532",
         "network_none":hc["NetworkMode"]=="none",
         "root_read_only":hc["ReadonlyRootfs"] is True,
         "cap_all_drop":"ALL" in hc["CapDrop"],
         "no_new_privileges":any("no-new-privileges" in s for s in hc["SecurityOpt"]),
         "ipc_none":hc["IpcMode"]=="none",
         "cgroup_private":hc["CgroupnsMode"]=="private",
         "memory_256m":hc["Memory"]==256*1024*1024,
         "memory_swap_256m":hc["MemorySwap"]==256*1024*1024,
         "cpus_one":hc["NanoCpus"]==1000000000,
         "pids_64":hc["PidsLimit"]==64,
         "one_packet_ro_mount":len([m for m in i["Mounts"] if m["Destination"]=="/packet" and not m["RW"]])==1,
         "tmpfs_scratch":"/scratch" in (hc.get("Tmpfs") or {}),
         "no_published_ports":not bool(hc.get("PortBindings")),
         "no_host_socket_mounts":all(not any(x in m.get("Source","") for x in ("/var/run/docker.sock","/.ssh/","/controller")) for m in i["Mounts"])
        }
        put(EVIDENCE/"worker-effective-config.json",{"checks":checks,"guest_uid":cfg["User"],"hostconfig_summary":{k:hc.get(k) for k in ("NetworkMode","ReadonlyRootfs","CapDrop","SecurityOpt","Memory","MemorySwap","NanoCpus","PidsLimit","IpcMode","CgroupnsMode","Tmpfs")},"mounts":[{"Destination":x["Destination"],"RW":x["RW"],"Type":x["Type"]} for x in i["Mounts"]]})
        if not all(checks.values()):raise RuntimeError("EFFECTIVE_WORKER_DRIFT:"+",".join(k for k,v in checks.items() if not v))
        # Same worker Linux AF_INET probes: real loopback positive, ENETUNREACH, ECONNREFUSED.
        base=[DOCKER,"--context","desktop-linux","exec",self.worker,
            "/usr/bin/env","-i","PATH=/usr/local/bin:/usr/bin:/bin","HOME=/",
            "/usr/local/bin/python3","-I","-B","-c",(RC4/"worker_control.py").read_text(),"network"]
        p=self.cmd(base,timeout=35)
        if p.returncode:raise RuntimeError("NETWORK_PROBE_EXEC_FAILED")
        items=[]
        for line in p.stdout.splitlines():
            try:items.append(decode(line))
            except Exception:pass
        observation=next((x for x in items[::-1] if x.get("schema")=="cal-network-observation/2"),None)
        if not observation:raise RuntimeError("NETWORK_PROBE_MISSING")
        checks={
          "positive_connect":observation.get("positive",{}).get("errno")==0 and "CAL-PUBLIC-SYNTHETIC-SOCKET-CONTROL" in observation.get("positive",{}).get("received",""),
          "real_external_enetunreach":observation.get("synthetic_egress",{}).get("errno")==101,
          "worker_loopback_refused":observation.get("controller_loopback_boundary",{}).get("errno")==111,
          "no_ipv4_default_route":len([line for line in observation.get("route_v4","").splitlines() if line.strip() and not line.startswith("Iface")])==0}
        put(EVIDENCE/"worker-network-observation.json",{"effective_checks":checks,"observed":observation})
        if not all(checks.values()):raise RuntimeError("RC6_WORKER_NETWORK_NEGATIVE_FAILED")
    def invoke_model(self,messages,serial:int):
        if serial>self.freeze["max_model_turns"]:raise RuntimeError("MODEL_TURN_LIMIT")
        obj=dict(self.freeze["request_first"])
        obj["messages"]=messages
        # No implicit runtime state carried: exact messages and two offered
        # functions per turn. Trusted controller owns messages from provider.
        raw=json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
        request_path=EVIDENCE/f"model-{serial:02d}-request.json"
        write(request_path,raw)
        self.model_requests.append({"serial":serial,"hash":sha(raw),"tools":[x["function"]["name"] for x in obj["tools"]],"messages":len(messages)})
        req=urllib.request.Request(OLLAMA_URL,data=raw,headers={"Content-Type":"application/json"},method="POST")
        opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
        try:
            with opener.open(req,timeout=155) as response:
                status=response.status;body=response.read(1024*1024+1)
        except urllib.error.HTTPError as err:
            status=err.code;body=err.read(1024*1024+1)
        write(EVIDENCE/f"model-{serial:02d}-response.json",body)
        if len(body)>1024*1024 or status!=200:raise RuntimeError("MODEL_HTTP_NON_200")
        data=decode(body)
        if data.get("model") not in (MODEL,):raise RuntimeError("MODEL_PROVIDER_IDENTITY_DRIFT")
        msg=data.get("message")
        if not isinstance(msg,dict) or msg.get("role")!="assistant":raise RuntimeError("MODEL_ASSISTANT_INVALID")
        calls=msg.get("tool_calls") or []
        if not isinstance(calls,list):raise RuntimeError("MODEL_CALLS_NOT_LIST")
        self.model_replies.append({"serial":serial,"response_sha256":sha(body),"call_count":len(calls),
          "call_names":[x.get("function",{}).get("name") for x in calls if isinstance(x,dict)],
          "finish_reason":data.get("done_reason")})
        return msg,calls
    def run_model(self):
        messages=list(self.freeze["request_first"]["messages"])
        adapter=self.adapter_module.FixedAdapter(self.worker,lambda argv,data:self.cmd(argv,data,timeout=30))
        for turn in range(1,self.freeze["max_model_turns"]+1):
            msg,calls=self.invoke_model(messages,turn)
            messages.append(msg)
            if not calls:raise RuntimeError("MODEL_STOPPED_WITHOUT_COMPLETING_WORK")
            for i,call in enumerate(calls):
                if self.writes:raise RuntimeError("MODEL_CALL_AFTER_OUTPUT_WRITE")
                raw=json.dumps(call,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
                write(EVIDENCE/f"tool-turn-{turn:02d}-{i+1:02d}-request.json",raw)
                fn=call.get("function",{}) if isinstance(call,dict) else {}
                name=fn.get("name") if isinstance(fn,dict) else None
                if name=="write_result" and self.reads!=["instructions/request.txt","data/marker.txt"]:
                    raise RuntimeError("WRITE_BEFORE_REQUIRED_READS")
                before=len(self.executions)
                try:
                    result=adapter.dispatch_model_call(raw)
                    decision={"status":"EXECUTED","name":name,"result":result}
                except self.adapter_module.Refusal as e:
                    decision={"status":"REFUSED","name":name,"reason":e.reason}
                decision.update({"turn":turn,"tool_index":i+1,"raw_sha256":sha(raw),
                    "executions_before":before,"executions_after":len(self.executions)})
                self.observed_calls.append(decision)
                put(EVIDENCE/f"tool-turn-{turn:02d}-{i+1:02d}-decision.json",decision)
                if decision["status"]=="REFUSED":
                    if before!=len(self.executions):raise RuntimeError("REFUSAL_DID_EXECUTE")
                    raise RuntimeError("MODEL_UNAUTHORIZED_TOOL_CALL:"+decision["reason"])
                args=fn["arguments"]
                if name=="read_packet_file":
                    path=args["path"]
                    self.reads.append(path)
                    if self.reads!=["instructions/request.txt","data/marker.txt"][:len(self.reads)]:
                        raise RuntimeError("READ_ORDER_DRIFT")
                elif name=="write_result":self.writes.append("answer.txt")
                else:raise RuntimeError("MODEL_UNKNOWN_TOOL_EXECUTED")
                # Ollama chat tool return requires name and JSON content.
                messages.append({"role":"tool","tool_name":name,
                                 "content":json.dumps(result,sort_keys=True,ensure_ascii=False)})
                if name=="write_result":
                    if len(self.writes)!=1:raise RuntimeError("DUPLICATE_OUTPUT_TOOL")
                    # Don't send another model request after first output: one
                    # answer is the scientific first result.
                    return
        raise RuntimeError("MODEL_NEVER_SELECTED_WRITE_RESULT")
    def verify_output(self):
        if self.reads!=["instructions/request.txt","data/marker.txt"] or self.writes!=["answer.txt"]:
            raise RuntimeError("UNSATISFIED_MODEL_TOOL_SEQUENCE")
        code="import hashlib,json,pathlib; p=pathlib.Path('/scratch/answer.txt'); b=p.read_bytes(); print(json.dumps({'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'hex':b.hex()}))"
        p=self.docker("exec",self.worker,"/usr/bin/env","-i","PATH=/usr/local/bin:/usr/bin:/bin","HOME=/",
                      "/usr/local/bin/python3","-I","-B","-c",code)
        if p.returncode:raise RuntimeError("ANSWER_OUTPUT_NOT_PRESENT")
        obj=decode(p.stdout)
        actual=bytes.fromhex(obj["hex"])
        allowed=(RC4/"public-synthetic-source"/"data"/"marker.txt").read_bytes()
        checks={"byte_exact":actual==allowed,"answer_len":len(actual)<=4096,
          "digest_matches_tool_receipt":obj["sha256"]==self.observed_calls[-1]["result"]["sha256"],
          "one_output_path":True}
        put(EVIDENCE/"answer-original-observation.json",{"checks":checks,
          "bytes":len(actual),"sha256":obj["sha256"],"gold_sha256":sha(allowed),
          "output_hex_controller_private":obj["hex"]})
        if not all(checks.values()):raise RuntimeError("MODEL_ANSWER_DIFFERS_FROM_FROZEN_PACKET")
    def cleanup(self):
        if not self.worker:return {"attempted":False,"reason":"no owned worker"}
        cid=self.worker
        removed=self.docker("rm","-f",cid)
        absent=self.docker("inspect",cid)
        record={"attempted":True,"owned_cid_sha256":sha(cid.encode()),
          "docker_rm_exit":removed.returncode,"docker_absence_exit":absent.returncode,
          "removed":removed.returncode==0 and absent.returncode!=0}
        put(EVIDENCE/"owned-teardown.json",record)
        return record
    def start_run(self):
        status={"schema":"cal-rc6-model-first-run/v1","first_started_utc":self.start,
         "result":"NOT_QUALIFIED_UNSTARTED","model_first_requests":0,
         "actor_admission":"Q13_NOT_AUTHORIZED","scope":"KNOWN_PUBLIC_SYNTHETIC_MODEL_TOOL_BEHAVIOR_ONLY",
         "pre_frozen_plan_sha256":digest(FROZEN),"owned_teardown":None}
        try:
            self.check_identity()
            self.create_worker()
            self.prove_worker()
            self.run_model()
            self.verify_output()
            status["result"]="PASS_BOUNDED_SYNTHETIC_MODEL_GENERATED_TWO_FUNCTIONS"
        except Exception as exc:
            status["result"]="FAIL_NOT_QUALIFIED"
            status["first_failure"]=str(exc)[:450]
            status["first_failure_type"]=type(exc).__name__
        finally:
            try:status["owned_teardown"]=self.cleanup()
            except Exception as ex:status["owned_teardown"]={"error":type(ex).__name__,"removed":False}
            status["finished_utc"]=now()
            status["model_first_requests"]=len(self.model_requests)
            status["model_replies"]=self.model_replies
            status["model_generated_tools"]=self.observed_calls
            status["tool_sequence"]=self.reads+self.writes
            put(EVIDENCE/"FIRST-RESULT.json",status)
            print(json.dumps({"result":status["result"],
                 "first_failure":status.get("first_failure"),
                 "model_requests":len(self.model_requests),
                 "model_generated_calls":[x.get("name") for x in self.observed_calls],
                 "owned_teardown":status["owned_teardown"]},indent=2))
        return 0 if status["result"].startswith("PASS") and status["owned_teardown"].get("removed") else 2
def main():
    if len(sys.argv)!=2 or sys.argv[1]!="first":
        raise SystemExit("USE: python rc6_model_controller.py first")
    frozen=preflight_freeze()
    if EVIDENCE.exists():raise SystemExit("REFUSE_OVERWRITE_FIRST_ATTEMPT")
    EVIDENCE.mkdir(parents=True,mode=0o700)
    write(EVIDENCE/"STARTED.txt",(now()+"\n").encode())
    return Controller(frozen).start_run()
if __name__=="__main__":sys.exit(main())
