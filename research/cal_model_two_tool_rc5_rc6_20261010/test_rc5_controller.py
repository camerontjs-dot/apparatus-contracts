#!/usr/bin/env python3
"""Pre-model CAL RC5 same-author deterministic tests: no Docker/Ollama calls.
Always distinguish scripted adapter negatives from model-generated behavior.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import subprocess
import unittest

ROOT=Path(__file__).resolve().parent
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
C=load(ROOT/"rc5_model_controller.py","rc5_controller")
A=C.get_adapter()
BASE=C.RC4
CASES=json.loads((BASE/"DISPATCH-CONTROLS.json").read_text())
class ScriptedRC4Controls(unittest.TestCase):
    def setUp(self):
        self.commands=[]
        def executor(argv,data):
            self.commands.append((argv,data))
            if any(x.endswith("/packet/instructions/request.txt") for x in argv):
                value=(BASE/"public-synthetic-source"/"instructions"/"request.txt").read_bytes()
            elif any(x.endswith("/packet/data/marker.txt") for x in argv):
                value=(BASE/"public-synthetic-source"/"data"/"marker.txt").read_bytes()
            else:value=b""
            return subprocess.CompletedProcess(argv,0,value,b"")
        self.ad=A.FixedAdapter("a"*64,executor)
    def test_rc4_public_manifest_sha(self):
        self.assertEqual(C.digest(BASE/"MANIFEST.json"),"cad5a34c4e69d7eb2145addb5ef6b9d955df02fe33b0cfc347470106cff2e8cf")
    def test_strict_approved_model_tools(self):
        r=C.model_request_baseline()
        self.assertEqual([t["function"]["name"] for t in r["tools"]],["read_packet_file","write_result"])
        self.assertEqual(r["model"],C.MODEL)
        self.assertFalse(r["think"])
        self.assertEqual([v["role"] for v in r["messages"]],["system","user"])
        self.assertNotIn("CAL-PUBLIC-SYNTHETIC-MARKER-001",json.dumps(r["messages"]))
    def test_frozen_source_path_allowlist(self):
        self.assertEqual(A.READS,C.EXPECTED_FILES)
    def test_frozen_native_dispatch_rejection_suite(self):
        failures=[]
        for case in CASES:
            if case.get("expected") is None:continue
            before=len(self.commands)
            try:
                if case.get("model"):
                    self.ad.dispatch_model_call(case["raw"].encode("utf-8"))
                else:self.ad.dispatch(case["raw"].encode("utf-8"))
                observed="ACCEPTED"
            except A.Refusal as e:observed=e.reason
            if observed!=case["expected"] or len(self.commands)!=before:
                failures.append((case.get("id"),observed,case["expected"]))
        self.assertFalse(failures,failures)
        self.assertGreaterEqual(len(CASES),50)
    def test_positive_reads_exact_source_bytes(self):
        for path in ("instructions/request.txt","data/marker.txt"):
            result=self.ad.dispatch(json.dumps({"name":"read_packet_file","arguments":{"path":path}}).encode())
            self.assertEqual(result["sha256"],A.READS[path])
        self.assertEqual(len(self.commands),2)
    def test_model_native_tool_call_dispatch_positive(self):
        x={"function":{"name":"read_packet_file","arguments":{"path":"data/marker.txt"}}}
        result=self.ad.dispatch_model_call(json.dumps(x).encode())
        self.assertEqual(result["sha256"],A.READS["data/marker.txt"])
        self.assertEqual(len(self.commands),1)
    def test_positive_exclusive_output_create(self):
        value=(BASE/"public-synthetic-source"/"data"/"marker.txt").read_text()
        result=self.ad.dispatch(json.dumps({"name":"write_result","arguments":{"path":"answer.txt","content":value}}).encode())
        self.assertEqual(result["sha256"],C.sha(value.encode()))
        self.assertEqual(len(self.commands),1)
        argv,body=self.commands[0]
        self.assertIn("docker",argv[0])
        self.assertEqual(body,value.encode())
        self.assertTrue(any("open('/scratch/answer.txt','xb')" in s for s in argv))
    def test_duplicate_function_name_rejected(self):
        raw=b'{"name":"read_packet_file","name":"write_result","arguments":{"path":"answer.txt","content":"X"}}'
        with self.assertRaises(A.Refusal):self.ad.dispatch(raw)
        self.assertEqual(len(self.commands),0)
    def test_traversal_denied_before_worker(self):
        with self.assertRaises(A.Refusal):self.ad.dispatch(b'{"name":"read_packet_file","arguments":{"path":"../controller/GOLD.json"}}')
        self.assertEqual(len(self.commands),0)
    def test_shell_tool_denied_before_worker(self):
        with self.assertRaises(A.Refusal):self.ad.dispatch_model_call(b'{"function":{"name":"exec_command","arguments":{"cmd":"pwd"}}}')
        self.assertEqual(len(self.commands),0)
    def test_write_utf8_bytes_limit_not_character_length(self):
        many="é"*2050
        with self.assertRaises(A.Refusal):self.ad.dispatch(json.dumps({"name":"write_result","arguments":{"path":"answer.txt","content":many}}).encode())
        self.assertEqual(len(self.commands),0)
    def test_extra_keys_denied_even_if_schema_cannot_render(self):
        raw=b'{"name":"write_result","arguments":{"path":"answer.txt","content":"ok","directory":"/tmp"}}'
        with self.assertRaises(A.Refusal):self.ad.dispatch(raw)
        self.assertEqual(len(self.commands),0)
    def test_invalid_absolute_result_name(self):
        raw=b'{"name":"write_result","arguments":{"path":"/tmp/answer.txt","content":"X"}}'
        with self.assertRaises(A.Refusal):self.ad.dispatch(raw)
        self.assertEqual(len(self.commands),0)
    def test_json_duplicate_parser_against_model_request(self):
        with self.assertRaises((ValueError,RuntimeError)):
            C.decode(b'{"role":"user","role":"system"}')
    def test_cannot_create_v1_if_stage_exists(self):
        self.assertIsInstance(C.ROOT,Path)
        self.assertTrue(C.ROOT.is_dir())
if __name__=="__main__":unittest.main()
