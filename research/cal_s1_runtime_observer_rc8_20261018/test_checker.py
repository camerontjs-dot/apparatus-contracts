"""Synthetic host-record tests; zero command or candidate execution.

A coherent fixture can satisfy an integrity checker. That is expressly not
proof of origin. Real origin depends on the controller-only custody boundary.
"""
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

import check_phase_a as peer


class PeerCheckerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / "source"; self.source.mkdir()
        self.run = self.root / "run"; self.run.mkdir()
        self.popen_patch = patch("subprocess.Popen", side_effect=AssertionError("NO_LIVE_CALL"))
        self.popen = self.popen_patch.start(); self.addCleanup(self.popen_patch.stop)
        source_spec = Path(__file__).parent / "SPECIMENS.json"
        self.spec = json.loads(source_spec.read_text())
        (self.source / "SPECIMENS.json").write_bytes(source_spec.read_bytes())
        self.guest = "SYNTHETIC WRAPPER DATA; NOT EXECUTED"
        self.manifest = self.source / "MANIFEST.json"
        self.manifest.write_bytes(peer.compact({"schema":"cal-rc8-source-setup-v1", "guest_program_sha256":peer.digest(self.guest.encode()),
            "files":{"SPECIMENS.json":peer.digest(source_spec.read_bytes())}}))
        self.result = {"source_manifest_sha256":peer.digest(self.manifest.read_bytes()),
            "case_controls_completed":18,"q13_admitted":False,"model_generated_tools":"NOT_RUN",
            "disposition":"PASS_BOUNDED_SYNTHETIC_RUNTIME_OBSERVER","results":[]}
        serial = 0
        for sidx, specimen in enumerate(self.spec["specimens"]):
            trial = self.run / specimen["id"]; trial.mkdir()
            (trial / "candidate.py").write_bytes(specimen["source"].encode())
            commands = trial / "commands"; commands.mkdir()
            for cidx, case in enumerate(self.spec["cases"]):
                serial += 1; cid = f"{serial:064x}"
                start = 100 * serial
                info = {"Id":cid,"Config":{"User":"65532:65532"},"HostConfig":{"ReadonlyRootfs":True,
                    "NetworkMode":"none","Privileged":False,"CapDrop":["ALL"],"CapAdd":None},
                    "Mounts":[{"Destination":"/packet"},{"Destination":"/candidate/candidate.py"}]}
                self.command(commands, cidx*4+1, ["inspect",cid], b"",peer.compact([info]),start)
                verdict = specimen["expected_verdict"]
                if verdict == "CORRECT_ANSWER": output = peer.compact(case["expected"])
                elif verdict == "INCORRECT_ANSWER": output = b'{"value":"999"}'
                elif verdict == "INVALID_JSON": output = b'PASS'
                else: output = b'{"event":"evaluator_finished","passed":true}'
                request = peer.compact({"claim":case["claim"],"evidence":case["evidence"]})
                self.command(commands,cidx*4+2,["exec","-i",cid,"-c",self.guest],request,output,start+10)
                self.command(commands,cidx*4+3,["rm","-f",cid],b"",b"",start+20)
                self.command(commands,cidx*4+4,["ps","-aq","--no-trunc"],b"",b"",start+30)
                self.result["results"].append({"specimen":specimen["id"],"case":case["id"],"verdict":verdict,"matched":True})
        (self.run / "RESULT.json").write_bytes(peer.compact(self.result))

    def command(self,parent,num,args,stdin,stdout,start):
        slot=parent/f"command-{num:04d}"; slot.mkdir()
        record={"argv":["/synthetic/docker","--context","desktop-linux",*args],
            "stdin_sha256":peer.digest(stdin),"stdout_sha256":peer.digest(stdout),"stderr_sha256":peer.digest(b""),
            "pid":42,"started_ns":start,"ended_ns":start+1,"failure":None,"returncode":0,
            "stdin_complete":True,"stdin_bytes_sent":len(stdin)}
        for name,raw in (("stdin.bin",stdin),("stdout.bin",stdout),("stderr.bin",b""),("command.json",peer.compact(record))):
            (slot/name).write_bytes(raw)
        return slot

    def evaluate(self):
        return peer.check(self.source,self.manifest,self.run)

    def slot(self):
        return self.run/"correct"/"commands"/"command-0002"

    def replace_stream_coherently(self,stream,data):
        slot=self.slot(); (slot/(stream+".bin")).write_bytes(data)
        record=json.loads((slot/"command.json").read_text())
        record[stream+"_sha256"]=peer.digest(data)
        (slot/"command.json").write_bytes(peer.compact(record))

    def test_coherent_synthetic_fixture_passes_integrity_not_authentication(self):
        r=self.evaluate()
        self.assertEqual(r["controls"],18)
        self.assertEqual(r["unique_workers"],18)
        self.assertFalse(r["q13_admitted"])
        self.popen.assert_not_called()

    def test_large_coherently_rehashed_answer_rejected(self):
        self.replace_stream_coherently("stdout", b" " * 17000 + b'{"value":"10"}')
        with self.assertRaisesRegex(peer.CheckError,"CONTROL_WRONG_REASON:RAW_BYTES_LIMIT"):
            self.evaluate()

    def test_changed_raw_bytes_fail_digest_check(self):
        (self.slot()/"stdout.bin").write_bytes(b'PASS')
        with self.assertRaisesRegex(peer.CheckError,"CAPTURE_BYTES_DRIFT"):self.evaluate()

    def test_coherently_rehashed_wrong_answer_does_not_pass(self):
        self.replace_stream_coherently("stdout",b'{"value":"999"}')
        with self.assertRaisesRegex(peer.CheckError,"CONTROL_WRONG_REASON:INCORRECT_ANSWER"):self.evaluate()

    def test_coherently_rehashed_fake_pass_is_rejected(self):
        self.replace_stream_coherently("stdout",b'PASS')
        with self.assertRaisesRegex(peer.CheckError,"CONTROL_WRONG_REASON:INVALID_JSON"):self.evaluate()

    def test_coherently_rehashed_forged_receipt_is_rejected(self):
        self.replace_stream_coherently("stdout",b'{"passed":true,"exit_code":0}')
        with self.assertRaisesRegex(peer.CheckError,"CONTROL_WRONG_REASON:ANSWER_SHAPE"):self.evaluate()

    def test_missing_invocation_does_not_count_as_case(self):
        shutil.rmtree(self.slot())
        with self.assertRaisesRegex(peer.CheckError,"ACTUAL_CASE_INVOCATIONS_MISSING"):self.evaluate()

    def test_input_substitution_rejected_even_with_new_hash(self):
        self.replace_stream_coherently("stdin",b'{"claim":"9","evidence":"1"}')
        with self.assertRaisesRegex(peer.CheckError,"CASE_INPUT_DRIFT"):self.evaluate()

    def test_failed_cleanup_is_not_success(self):
        slot=self.run/"correct"/"commands"/"command-0003"
        rec=json.loads((slot/"command.json").read_text());rec["returncode"]=1
        (slot/"command.json").write_bytes(peer.compact(rec))
        with self.assertRaisesRegex(peer.CheckError,"OWNED_TEARDOWN_MISSING"):self.evaluate()

    def test_summary_cannot_replace_observed_outcomes(self):
        self.result["results"][0]["verdict"]="INCORRECT_ANSWER"
        (self.run/"RESULT.json").write_bytes(peer.compact(self.result))
        with self.assertRaisesRegex(peer.CheckError,"SUMMARY_DISAGREES"):self.evaluate()

    def test_source_drift_rejected(self):
        with (self.source/"SPECIMENS.json").open("ab") as f:f.write(b" ")
        with self.assertRaisesRegex(peer.CheckError,"SOURCE_DRIFT"):self.evaluate()

    def test_candidate_artifact_drift_rejected(self):
        (self.run/"correct"/"candidate.py").write_bytes(b'# changed\n')
        with self.assertRaisesRegex(peer.CheckError,"CANDIDATE_ARTIFACT_DRIFT"):self.evaluate()

    def test_q13_overclaim_rejected(self):
        self.result["q13_admitted"]=True
        (self.run/"RESULT.json").write_bytes(peer.compact(self.result))
        with self.assertRaisesRegex(peer.CheckError,"CLAIM_CEILING"):self.evaluate()


if __name__ == "__main__":
    unittest.main()
