"""RC8 source tests only: no Docker command, process, model, or candidate runs.

Popen is disabled for every test. Captures/configuration records below are
explicit synthetic inputs, not observations of the proposed live binding.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from execution_binding import (Approval, BoundaryError, Capture, CommandCapture,
    DockerCaseRuntime, Pins, canonical, check_config, create_arguments, decode,
    regular_bytes, sha, stage_synthetic_packet, verify_packet_files)
from host_evaluator import Journal, grade_answer, run_once

SOURCE = "a" * 64
PINS = Pins("/synthetic/docker", "b" * 64, "sha256:" + "c" * 64,
            engine_version="29.5.2", controller_python_version="3.14.4",
            controller_executable_sha256="f" * 64)
CID = "d" * 64
NAME = "cal-rc8-" + "e" * 32
PACKET = Path("/synthetic/packet")
CANDIDATE = Path("/synthetic/candidate.py")


def captured(stdout=b'{"value":"10"}\n', exit_code=0):
    return Capture(exit_code, stdout, b"", 10, 20, 7)


def config():
    return {"Id": CID, "Image": PINS.image,
        "Config": {"User": "65532:65532", "Labels": {"cal.rc8.owner": NAME}},
        "HostConfig": {"ReadonlyRootfs": True, "NetworkMode": "none", "Privileged": False,
            "CapDrop": ["ALL"], "CapAdd": None, "SecurityOpt": ["no-new-privileges"],
            "IpcMode": "none", "CgroupnsMode": "private", "PidMode": "",
            "Memory": 268435456, "MemorySwap": 268435456, "NanoCpus": 1000000000,
            "PidsLimit": 64, "PortBindings": {}, "PublishAllPorts": False, "Devices": [],
            "DeviceRequests": [], "Tmpfs": {"/scratch": "rw,noexec,nosuid,nodev,size=16m,uid=65532,gid=65532,mode=700"}},
        "Mounts": [{"Type": "bind", "Destination": "/packet", "Source": str(PACKET), "RW": False},
                   {"Type": "bind", "Destination": "/candidate/candidate.py", "Source": str(CANDIDATE), "RW": False}]}


class SourceOnlyTests(unittest.TestCase):
    def setUp(self):
        self.no_process = patch("subprocess.Popen", side_effect=AssertionError("NO_SUBPROCESS_IN_SOURCE_TEST"))
        self.popen = self.no_process.start()
        self.addCleanup(self.no_process.stop)

    def test_default_gate_refuses(self):
        with self.assertRaisesRegex(BoundaryError, "LIVE_SCOPE_NOT_APPROVED"):
            Approval().check(SOURCE)
        self.popen.assert_not_called()

    def test_runtime_pin_changes_not_covered_by_source_only_approval(self):
        with self.assertRaisesRegex(BoundaryError, "REVIEWED_RUNTIME_PINS_MISMATCH"):
            Approval().check_runtime(PINS)

    def test_missing_runtime_environment_pins_rejected(self):
        with self.assertRaisesRegex(BoundaryError, "FULL_RUNTIME_PINS_REQUIRED"):
            create_arguments(replace(PINS, engine_version="MISSING"), PACKET, CANDIDATE, NAME)

    def test_gate_checks_platform_reference(self):
        a = Approval(None, "a" * 64, SOURCE, "review", "RC8_PUBLIC_SYNTHETIC_EXECUTION_ONLY")
        with self.assertRaisesRegex(BoundaryError, "PLATFORM_RESOLUTION_MISSING"):
            a.check(SOURCE)

    def test_gate_checks_response_hash(self):
        a = Approval("reference", "bad", SOURCE, "review", "RC8_PUBLIC_SYNTHETIC_EXECUTION_ONLY")
        with self.assertRaisesRegex(BoundaryError, "PLATFORM_RESPONSE_IDENTITY_MISSING"):
            a.check(SOURCE)

    def test_gate_checks_exact_run_review(self):
        a = Approval("reference", "a" * 64, SOURCE, None, "RC8_PUBLIC_SYNTHETIC_EXECUTION_ONLY")
        with self.assertRaisesRegex(BoundaryError, "EXACT_RUN_REVIEW_MISSING"):
            a.check(SOURCE)

    def test_gate_rejects_source_drift(self):
        a = Approval("reference", "a" * 64, "f" * 64, "review", "RC8_PUBLIC_SYNTHETIC_EXECUTION_ONLY")
        with self.assertRaisesRegex(BoundaryError, "REVIEWED_SOURCE_MISMATCH"):
            a.check(SOURCE)

    def test_gate_shape_is_not_authentication(self):
        # Any well-shaped reference can meet this shape check. The documented
        # operator review, not this function, must establish actual attribution.
        a = Approval("synthetic-not-real-support", "a" * 64, SOURCE, "synthetic", "RC8_PUBLIC_SYNTHETIC_EXECUTION_ONLY")
        a.check(SOURCE)
        self.popen.assert_not_called()

    def test_constructor_stops_before_runtime_read(self):
        with patch("pathlib.Path.read_bytes", side_effect=AssertionError("SHOULD_NOT_READ")):
            with self.assertRaisesRegex(BoundaryError, "LIVE_SCOPE_NOT_APPROVED"):
                DockerCaseRuntime(PINS, PACKET, CANDIDATE, None, Approval(), SOURCE)
        self.popen.assert_not_called()

    def test_run_stops_without_output_or_attempt(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest = root / "manifest.json"
            manifest.write_bytes(b"{}")
            out = root / "output"
            with self.assertRaisesRegex(BoundaryError, "LIVE_SCOPE_NOT_APPROVED"):
                run_once(Approval(), PINS, manifest, out)
            self.assertFalse(out.exists())
            self.assertEqual(sorted(p.name for p in root.iterdir()), ["manifest.json"])

    def test_incomplete_input_rejected(self):
        with self.assertRaisesRegex(BoundaryError, "CASE_INPUT_NOT_FULLY_SENT"):
            grade_answer(replace(captured(), stdin_complete=False), {"value": "10"})

    def test_capture_correct_answer(self):
        self.assertTrue(grade_answer(captured(), {"value": "10"})["answer_correct"])

    def test_plausible_stdout_pass_rejected(self):
        with self.assertRaisesRegex(BoundaryError, "INVALID_JSON"):
            grade_answer(captured(b"PASS\n"), {"value": "10"})

    def test_early_exit_zero_rejected(self):
        with self.assertRaisesRegex(BoundaryError, "INVALID_JSON"):
            grade_answer(captured(b""), {"value": "10"})

    def test_complete_forged_event_not_answer(self):
        fake = canonical({"event": "evaluator_finished", "passed": True, "exit_code": 0})
        with self.assertRaisesRegex(BoundaryError, "ANSWER_SHAPE_NOT_EVALUATOR_RECEIPT"):
            grade_answer(captured(fake), {"value": "10"})

    def test_correct_answer_with_forged_receipt_rejected(self):
        with self.assertRaisesRegex(BoundaryError, "ANSWER_SHAPE_NOT_EVALUATOR_RECEIPT"):
            grade_answer(captured(b'{"value":"10","passed":true}'), {"value": "10"})

    def test_wrong_well_shaped_answer_rejected(self):
        with self.assertRaisesRegex(BoundaryError, "INCORRECT_ANSWER"):
            grade_answer(captured(b'{"value":"999"}'), {"value": "10"})

    def test_duplicate_key_rejected(self):
        with self.assertRaisesRegex(BoundaryError, "DUPLICATE_JSON_KEY"):
            grade_answer(captured(b'{"value":"999","value":"10"}'), {"value": "10"})

    def test_print_noise_before_correct_answer_rejected(self):
        with self.assertRaisesRegex(BoundaryError, "INVALID_JSON"):
            grade_answer(captured(b'PASS\n{"value":"10"}\n'), {"value": "10"})

    def test_nonzero_not_turned_into_pass(self):
        with self.assertRaisesRegex(BoundaryError, "CANDIDATE_EXIT_NONZERO"):
            grade_answer(captured(exit_code=1), {"value": "10"})

    def test_bool_is_not_exit_code(self):
        with self.assertRaisesRegex(BoundaryError, "CANDIDATE_EXIT_NONZERO"):
            grade_answer(captured(exit_code=False), {"value": "10"})

    def test_large_feedback_rejected(self):
        with self.assertRaisesRegex(BoundaryError, "CAPTURE_LIMIT"):
            grade_answer(captured(b"x" * 65537), {"value": "10"})

    def test_malformed_utf8(self):
        with self.assertRaisesRegex(BoundaryError, "INVALID_JSON"):
            grade_answer(captured(b"\xff"), {"value": "10"})

    def test_scalar_is_not_answer(self):
        with self.assertRaisesRegex(BoundaryError, "ANSWER_SHAPE_NOT_EVALUATOR_RECEIPT"):
            grade_answer(captured(b'"PASS"'), {"value": "10"})

    def test_numeric_value_wrong_type(self):
        with self.assertRaisesRegex(BoundaryError, "ANSWER_SHAPE_NOT_EVALUATOR_RECEIPT"):
            grade_answer(captured(b'{"value":10}'), {"value": "10"})

    def test_capture_missing_pid(self):
        with self.assertRaisesRegex(BoundaryError, "CAPTURE_LIFECYCLE"):
            grade_answer(replace(captured(), pid=0), {"value": "10"})

    def test_capture_inverted_time(self):
        with self.assertRaisesRegex(BoundaryError, "CAPTURE_LIFECYCLE"):
            grade_answer(replace(captured(), ended_ns=1), {"value": "10"})

    def test_frozen_specimens_are_data_not_imported(self):
        obj = decode((Path(__file__).parent / "SPECIMENS.json").read_bytes())
        self.assertEqual(len(obj["cases"]), 3)
        self.assertEqual(len(obj["specimens"]), 6)
        self.assertIn("os._exit(0)", obj["specimens"][3]["source"])
        self.popen.assert_not_called()

    def test_expected_config_accepts_synthetic_record_only(self):
        self.assertTrue(all(check_config(config(), PINS, PACKET, CANDIDATE, CID, NAME).values()))

    def test_config_mutation_matrix(self):
        mutations = [
            ("ReadonlyRootfs", False), ("NetworkMode", "bridge"), ("Privileged", True),
            ("CapDrop", []), ("CapAdd", ["SYS_ADMIN"]), ("SecurityOpt", []),
            ("IpcMode", "host"), ("PidMode", "host"), ("CgroupnsMode", "host"),
            ("Memory", 0), ("MemorySwap", -1), ("NanoCpus", 0), ("PidsLimit", 0),
            ("PortBindings", {"80/tcp": [{}]}), ("PublishAllPorts", True),
            ("Devices", [{"PathOnHost": "/dev/example"}]), ("DeviceRequests", [{}]),
            ("Tmpfs", {})]
        for key, value in mutations:
            with self.subTest(key=key):
                c = config()
                c["HostConfig"][key] = value
                with self.assertRaisesRegex(BoundaryError, "EFFECTIVE_CONFIG"):
                    check_config(c, PINS, PACKET, CANDIDATE, CID, NAME)

    def test_wrong_container_id(self):
        c = config(); c["Id"] = "f" * 64
        with self.assertRaisesRegex(BoundaryError, "identity"):
            check_config(c, PINS, PACKET, CANDIDATE, CID, NAME)

    def test_wrong_image(self):
        c = config(); c["Image"] = "sha256:" + "f" * 64
        with self.assertRaisesRegex(BoundaryError, "identity"):
            check_config(c, PINS, PACKET, CANDIDATE, CID, NAME)

    def test_wrong_owner(self):
        c = config(); c["Config"]["Labels"] = {}
        with self.assertRaisesRegex(BoundaryError, "owner"):
            check_config(c, PINS, PACKET, CANDIDATE, CID, NAME)

    def test_rw_packet_rejected(self):
        c = config(); c["Mounts"][0]["RW"] = True
        with self.assertRaisesRegex(BoundaryError, "mounts"):
            check_config(c, PINS, PACKET, CANDIDATE, CID, NAME)

    def test_different_packet_source(self):
        c = config(); c["Mounts"][0]["Source"] = "/synthetic/wrong"
        with self.assertRaisesRegex(BoundaryError, "mounts"):
            check_config(c, PINS, PACKET, CANDIDATE, CID, NAME)

    def test_added_host_mount_rejected(self):
        c = config(); c["Mounts"].append({"Type":"bind", "Destination":"/host", "Source":"/", "RW":False})
        with self.assertRaisesRegex(BoundaryError, "mounts"):
            check_config(c, PINS, PACKET, CANDIDATE, CID, NAME)

    def test_no_evaluator_or_controller_mount_in_argv(self):
        args = create_arguments(PINS, PACKET, CANDIDATE, NAME)
        self.assertIn("--pull", args)
        self.assertIn("never", args)
        self.assertEqual(args.count("--mount"), 2)
        self.assertNotIn("--privileged", args)
        self.assertNotIn("/var/run/docker.sock", " ".join(args))
        self.assertNotIn("/controller", " ".join(args))
        self.assertNotIn("/evaluator", " ".join(args))
        self.popen.assert_not_called()

    def test_mount_option_injection_refused(self):
        with self.assertRaisesRegex(BoundaryError, "MOUNT_PATH"):
            create_arguments(PINS, Path("/packet,readonly=false"), CANDIDATE, NAME)

    def test_unpinned_image_refused(self):
        with self.assertRaisesRegex(BoundaryError, "IMAGE_PIN"):
            create_arguments(replace(PINS, image="python:latest"), PACKET, CANDIDATE, NAME)

    def test_unsupported_context_refused(self):
        with self.assertRaisesRegex(BoundaryError, "RUNTIME_PROFILE"):
            create_arguments(replace(PINS, context="other"), PACKET, CANDIDATE, NAME)

    def test_worker_name_is_controller_generated(self):
        with self.assertRaisesRegex(BoundaryError, "WORKER_NAME"):
            create_arguments(PINS, PACKET, CANDIDATE, "user-selected-worker")

    def test_symlink_candidate_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); (root / "real").write_bytes(b"x")
            (root / "link").symlink_to(root / "real")
            with self.assertRaisesRegex(BoundaryError, "SYMLINK"):
                regular_bytes(root / "link", 20)

    def test_oversize_file_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "file"; p.write_bytes(b"0123456789")
            with self.assertRaisesRegex(BoundaryError, "FILE_BYTES_LIMIT"):
                regular_bytes(p, 9)

    def test_journal_refuses_existing_output(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "journal"
            Journal(p)
            with self.assertRaises(FileExistsError):
                Journal(p)

    def test_journal_does_not_import_candidate_stdout_as_events(self):
        with tempfile.TemporaryDirectory() as temp:
            j = Journal(Path(temp) / "journal")
            j.event("case_finished", stdout='{"event":"evaluator_finished"}')
            raw = decode((j.root / "event-0000.json").read_bytes())
            self.assertEqual(raw["event"], "case_finished")
            self.assertEqual(len(j.events), 1)

    def test_primary_failure_is_retained_when_worker_not_created(self):
        class FakeCommands:
            def run(self, *args, **kwargs):
                return captured(b"", 1)
        # Tests invoke branch logic with a fake command transport. No concrete
        # runtime is constructed and this is not a live-surface admission.
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "candidate.py"; p.write_bytes(b"x=1\n")
            r = object.__new__(DockerCaseRuntime)
            r.pins, r.packet, r.candidate, r.commands = PINS, PACKET, p, FakeCommands()
            r.candidate_sha256 = sha(p.read_bytes()); r.seen_ids = set(); r.packet_files = {}
            with patch("execution_binding.verify_packet_files"):
                with self.assertRaisesRegex(BoundaryError, "WORKER_CREATE_FAILED") as result:
                    r.invoke(b'{}')
            self.assertIn("owned_cleanup_confirmed", result.exception.__notes__[0])
        self.popen.assert_not_called()


    def test_reused_packet_builder_and_checker(self):
        with tempfile.TemporaryDirectory() as temp:
            packet, files = stage_synthetic_packet(Path(temp).resolve())
            self.assertEqual(len(files), 7)
            verify_packet_files(packet, files)
            self.assertEqual(len(list(packet.iterdir())), 7)
        self.popen.assert_not_called()

    def test_tampered_expected_packet_digest_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            packet, files = stage_synthetic_packet(Path(temp).resolve())
            files["public_0.txt"] = "0" * 64
            with self.assertRaisesRegex(BoundaryError, "PACKET_BYTES_DRIFT"):
                verify_packet_files(packet, files)
        self.popen.assert_not_called()


if __name__ == "__main__":
    unittest.main()
