"""Synthetic unit controls for the versioned offline coding-profile adapter.

These tests use only synthetic packet bytes and a fake runtime. They do not
establish container, model, or CAL qualification behavior.
"""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from offline_profile import Adapter, Entry, Profile, Refusal, Witness


PATHS = (
    "dev/README.md",
    "dev/cases.json",
    "dev/evaluator.py",
    "dev/guide.txt",
    "dev/manifest.json",
    "dev/notes.md",
    "dev/starter.py",
)
PACKET = {path: ("synthetic:" + path).encode("utf-8") for path in PATHS}
CASES = ("case-a", "case-b", "case-c")
OBSERVER = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
EVALUATOR = OBSERVER


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def profile(**changes: object) -> Profile:
    values = {
        "reads": {path: digest(PACKET[path]) for path in PATHS},
        "evaluator_sha256": EVALUATOR,
        "observer_sha256": OBSERVER,
        "cases": CASES,
    }
    values.update(changes)
    return Profile(**values)


def envelope(name: str, arguments: object, *, version: str = "cal-s1-lines-v1") -> bytes:
    return json.dumps(
        {"version": version, "name": name, "arguments": arguments},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")


class FakeRuntime:
    """Synthetic transport; its return values never supply observer evidence."""

    def __init__(self, files: dict[str, Entry] | None = None, *, mode: str = "pass"):
        self.files = files or {path: Entry(data) for path, data in PACKET.items()}
        self.candidates: dict[str, Entry] = {}
        self.mode = mode
        self.runs: list[dict[str, object]] = []

    def read_packet(self, path: str) -> Entry:
        return self.files[path]

    def list_candidates(self) -> tuple[str, ...]:
        return tuple(sorted(self.candidates))

    def read_candidate(self, path: str) -> Entry:
        return self.candidates[path]

    def write_candidate(self, path: str, data: bytes) -> None:
        self.candidates[path] = Entry(data)

    def run_development_tests(self, request: dict[str, object]) -> dict[str, object]:
        self.runs.append(request.copy())
        return {"exit_code": 0, "stdout": "PASS", "receipt": {"all_cases_passed": True}}


class FakeObserver:
    """Explicitly fake, independent observer fixture for checker transcripts."""

    identity_sha256 = OBSERVER
    evidence_layer = "SYNTHETIC_FAKE_RUNTIME"

    def __init__(self, mode: str = "pass"):
        self.mode = mode
        self.requests = {}
        self.last_events = ()

    def begin(self, request: dict[str, object]) -> None:
        self.requests[request["run_id"]] = request.copy()

    def finish(self, run_id: str) -> tuple[dict[str, object], ...]:
        request = self.requests[run_id]
        common = {key: request[key] for key in (
            "run_id", "profile_sha256", "candidate_sha256", "evaluator_sha256", "observer_sha256")}

        def event(name: str, **fields: object) -> dict[str, object]:
            return {**common, "event": name, **fields}

        events = []
        if self.mode != "stdout_only":
            started = event("evaluator_started", consumed_candidate_sha256=request["candidate_sha256"])
            if self.mode == "wrong_consumed_candidate":
                started["consumed_candidate_sha256"] = "0" * 64
            if self.mode == "oversize_event":
                started["oversized"] = "x" * 5000
            events.append(started)
            if self.mode == "early_exit":
                events.append(event("evaluator_finished", exit_code=0))
            else:
                for index, case_id in enumerate(request["cases"]):
                    if self.mode == "skip_case" and index == 1:
                        continue
                    events.append(event("case_started", case_id=case_id))
                    passed = not (self.mode == "weak_candidate" and index == 0)
                    events.append(event("case_finished", case_id=case_id, passed=passed))
                    if self.mode == "duplicate_case" and index == 0:
                        events.extend((event("case_started", case_id=case_id),
                                       event("case_finished", case_id=case_id, passed=True)))
                    if self.mode == "replay" and index == 0:
                        events.append({**event("case_started", case_id=case_id), "run_id": "old-run"})
                if self.mode == "malformed_event":
                    events.append({"event": "evaluator_finished", "exit_code": 0})
                else:
                    events.append(event("evaluator_finished", exit_code=0))
        if self.mode == "extra_event":
            events.append(event("extra"))
        if self.mode == "extra_event_key" and events:
            events[0]["claimed_by_candidate"] = True
        self.last_events = tuple(events)
        return self.last_events


class MissingRuntime:
    pass


class OfflineProfileTests(unittest.TestCase):
    def make_adapter(self, runtime: FakeRuntime | None = None, p: Profile | None = None,
                     observer=None, with_observer: bool = True):
        runtime = runtime or FakeRuntime()
        if observer is None and with_observer:
            observer = FakeObserver(mode=runtime.mode)
        witness = Witness(observer) if with_observer else Witness()
        return Adapter(p or profile(), runtime, witness), runtime, witness

    def refusal(self, call) -> None:
        try:
            result = call()
        except Refusal:
            return
        self.assertIsInstance(result, Refusal, "unsafe input must produce Refusal")

    def dispatch(self, adapter, tool: str, args: object):
        return adapter.dispatch(envelope(tool, args))

    def write_candidate(self, adapter, lines: list[str] | None = None):
        return self.dispatch(adapter, "write_candidate_lines", {
            "path": "candidate.py",
            "lines": ["def answer():", "    return 42"] if lines is None else lines,
        })

    def test_profile_accepts_exactly_seven_sorted_synthetic_paths(self):
        self.assertEqual(tuple(sorted(PATHS)), PATHS)
        self.make_adapter()

    def test_profile_rejects_wrong_path_count(self):
        self.refusal(lambda: self.make_adapter(p=profile(reads={"dev/a.py": "a" * 64})))

    def test_profile_rejects_unsorted_paths(self):
        reversed_reads = dict((path, digest(PACKET[path])) for path in reversed(PATHS))
        self.refusal(lambda: self.make_adapter(p=profile(reads=reversed_reads)))

    def test_profile_rejects_malformed_observer_identity(self):
        self.refusal(lambda: self.make_adapter(p=profile(observer_sha256="bad")))

    def test_profile_rejects_traversal_path(self):
        bad = {path: digest(PACKET[path]) for path in PATHS}
        bad["../escape.py"] = bad.pop(PATHS[-1])
        self.refusal(lambda: self.make_adapter(p=profile(reads=bad)))

    def test_profile_rejects_unsupported_suffix(self):
        bad = {path: digest(PACKET[path]) for path in PATHS}
        bad["dev/starter.py"] = bad.pop("dev/starter.py")
        bad["dev/starter.bin"] = bad.pop("dev/starter.py")
        self.refusal(lambda: self.make_adapter(p=profile(reads=bad)))

    def test_missing_runtime_is_refused(self):
        self.refusal(lambda: Adapter(profile(), MissingRuntime(), Witness()))

    def test_stale_candidate_at_construction_is_refused(self):
        runtime = FakeRuntime()
        runtime.candidates["old.py"] = Entry(b"old")
        self.refusal(lambda: Adapter(profile(), runtime, Witness()))

    def test_read_returns_exact_bytes_and_hash(self):
        adapter, _, _ = self.make_adapter()
        result = self.dispatch(adapter, "read_packet_file", {"path": "dev/starter.py"})
        self.assertIsInstance(result["content"], str)
        self.assertEqual(result["content"].encode("utf-8"), PACKET["dev/starter.py"])
        self.assertEqual(result["bytes"], len(PACKET["dev/starter.py"]))
        self.assertEqual(result["sha256"], digest(PACKET["dev/starter.py"]))

    def test_read_refuses_unlisted_path(self):
        adapter, _, _ = self.make_adapter()
        self.refusal(lambda: self.dispatch(adapter, "read_packet_file", {"path": "dev/extra.py"}))

    def test_read_refuses_traversal(self):
        adapter, _, _ = self.make_adapter()
        self.refusal(lambda: self.dispatch(adapter, "read_packet_file", {"path": "../dev/starter.py"}))

    def test_read_refuses_absolute_path(self):
        adapter, _, _ = self.make_adapter()
        self.refusal(lambda: self.dispatch(adapter, "read_packet_file", {"path": "/tmp/starter.py"}))

    def test_read_refuses_symlink_entry(self):
        files = dict(FakeRuntime().files)
        files["dev/starter.py"] = Entry(PACKET["dev/starter.py"], kind="symlink")
        adapter, _, _ = self.make_adapter(FakeRuntime(files))
        self.refusal(lambda: self.dispatch(adapter, "read_packet_file", {"path": "dev/starter.py"}))

    def test_read_refuses_hardlinked_entry(self):
        files = dict(FakeRuntime().files)
        files["dev/starter.py"] = Entry(PACKET["dev/starter.py"], nlink=2)
        adapter, _, _ = self.make_adapter(FakeRuntime(files))
        self.refusal(lambda: self.dispatch(adapter, "read_packet_file", {"path": "dev/starter.py"}))

    def test_read_refuses_entry_with_symlinked_ancestor(self):
        files = dict(FakeRuntime().files)
        files["dev/starter.py"] = Entry(PACKET["dev/starter.py"], ancestors_clean=False)
        adapter, _, _ = self.make_adapter(FakeRuntime(files))
        self.refusal(lambda: self.dispatch(adapter, "read_packet_file", {"path": "dev/starter.py"}))

    def test_read_refuses_hash_mismatch(self):
        files = dict(FakeRuntime().files)
        files["dev/starter.py"] = Entry(b"tampered")
        adapter, _, _ = self.make_adapter(FakeRuntime(files))
        self.refusal(lambda: self.dispatch(adapter, "read_packet_file", {"path": "dev/starter.py"}))

    def test_read_refuses_extra_argument(self):
        adapter, _, _ = self.make_adapter()
        self.refusal(lambda: self.dispatch(adapter, "read_packet_file", {"path": PATHS[0], "mode": "raw"}))

    def test_write_preserves_quotes_backslashes_indentation_empty_lines_and_unicode(self):
        adapter, runtime, _ = self.make_adapter()
        lines = ['quote = "it\'s\\fine"', "", "    label = 'café 雪'", "    return label"]
        self.write_candidate(adapter, lines)
        expected = "\n".join(lines).encode("utf-8") + b"\n"
        self.assertEqual(runtime.candidates["candidate.py"].data, expected)

    def test_write_reply_identifies_exact_candidate_bytes(self):
        adapter, runtime, _ = self.make_adapter()
        reply = self.write_candidate(adapter, ["x = 1"])
        data = runtime.candidates["candidate.py"].data
        self.assertEqual(reply, {"path": "candidate.py", "bytes": len(data), "sha256": digest(data)})

    def test_empty_line_array_writes_empty_bytes(self):
        adapter, runtime, _ = self.make_adapter()
        self.write_candidate(adapter, [])
        self.assertEqual(runtime.candidates["candidate.py"].data, b"")

    def test_write_refuses_embedded_lf(self):
        adapter, _, _ = self.make_adapter()
        self.refusal(lambda: self.write_candidate(adapter, ["a\nb"]))

    def test_write_refuses_embedded_cr(self):
        adapter, _, _ = self.make_adapter()
        self.refusal(lambda: self.write_candidate(adapter, ["a\rb"]))

    def test_write_refuses_unicode_line_separators(self):
        adapter, _, _ = self.make_adapter()
        for separator in ("\x85", "\u2028", "\u2029"):
            with self.subTest(separator=ord(separator)):
                self.refusal(lambda: self.write_candidate(adapter, ["a" + separator + "b"]))

    def test_write_refuses_surrogate(self):
        adapter, _, _ = self.make_adapter()
        self.refusal(lambda: self.write_candidate(adapter, ["bad\ud800"]))

    def test_write_refuses_oversize_output(self):
        adapter, _, _ = self.make_adapter()
        self.refusal(lambda: self.write_candidate(adapter, ["x" * 32768]))

    def test_write_refuses_other_candidate_path(self):
        adapter, _, _ = self.make_adapter()
        self.refusal(lambda: self.dispatch(adapter, "write_candidate_lines", {"path": "other.py", "lines": ["x"]}))

    def test_write_refuses_wrong_argument_shape(self):
        adapter, _, _ = self.make_adapter()
        self.refusal(lambda: self.dispatch(adapter, "write_candidate_lines", {"path": "candidate.py", "lines": [1]}))

    def test_write_refuses_candidate_symlink(self):
        class SymlinkRuntime(FakeRuntime):
            def write_candidate(self, path: str, data: bytes) -> None:
                self.candidates[path] = Entry(data, kind="symlink")
        adapter, _, _ = self.make_adapter(SymlinkRuntime())
        self.refusal(lambda: self.write_candidate(adapter, ["x = 1"]))

    def test_write_refuses_candidate_hardlink(self):
        class HardlinkRuntime(FakeRuntime):
            def write_candidate(self, path: str, data: bytes) -> None:
                self.candidates[path] = Entry(data, nlink=2)
        adapter, _, _ = self.make_adapter(HardlinkRuntime())
        self.refusal(lambda: self.write_candidate(adapter, ["x = 1"]))

    def test_write_accepts_exact_byte_limit(self):
        adapter, runtime, _ = self.make_adapter()
        self.write_candidate(adapter, ["x" * 32767])
        self.assertEqual(len(runtime.candidates["candidate.py"].data), 32768)

    def test_adapter_allows_rewrite_of_its_named_candidate(self):
        adapter, runtime, _ = self.make_adapter()
        self.write_candidate(adapter, ["x = 1"])
        self.write_candidate(adapter, ["x = 2"])
        self.assertEqual(runtime.candidates["candidate.py"].data, b"x = 2\n")

    def test_external_untracked_candidate_drift_is_refused(self):
        adapter, runtime, _ = self.make_adapter()
        self.write_candidate(adapter)
        runtime.candidates["injected.py"] = Entry(b"untracked")
        self.refusal(lambda: self.dispatch(adapter, "run_development_tests", {}))

    def test_dispatch_refuses_malformed_json(self):
        adapter, _, _ = self.make_adapter()
        self.refusal(lambda: adapter.dispatch(b"{"))

    def test_dispatch_refuses_duplicate_json_keys(self):
        adapter, _, _ = self.make_adapter()
        self.refusal(lambda: adapter.dispatch(b'{"version":"cal-s1-lines-v1","version":"x","name":"read_packet_file","arguments":{"path":"dev/starter.py"}}'))

    def test_dispatch_refuses_nonfinite_json_number(self):
        adapter, _, _ = self.make_adapter()
        self.refusal(lambda: adapter.dispatch(b'{"version":"cal-s1-lines-v1","name":"read_packet_file","arguments":{"path":"dev/starter.py","unused":NaN}}'))

    def test_dispatch_refuses_unknown_top_level_key(self):
        adapter, _, _ = self.make_adapter()
        raw = envelope("read_packet_file", {"path": "dev/starter.py"})[:-1] + b',"extra":1}'
        self.refusal(lambda: adapter.dispatch(raw))

    def test_dispatch_refuses_unknown_tool(self):
        adapter, _, _ = self.make_adapter()
        self.refusal(lambda: self.dispatch(adapter, "shell", {"command": "echo hi"}))

    def test_dispatch_refuses_unknown_version(self):
        adapter, _, _ = self.make_adapter()
        self.refusal(lambda: adapter.dispatch(envelope("read_packet_file", {"path": PATHS[0]}, version="legacy")))

    def test_dispatch_refuses_oversize_envelope(self):
        adapter, _, _ = self.make_adapter()
        raw = envelope("read_packet_file", {"path": "x" * 262200})
        self.refusal(lambda: adapter.dispatch(raw))

    def test_test_operation_requires_a_candidate_write(self):
        adapter, _, _ = self.make_adapter()
        self.refusal(lambda: self.dispatch(adapter, "run_development_tests", {}))

    def test_test_operation_refuses_unknown_arguments(self):
        adapter, _, _ = self.make_adapter()
        self.write_candidate(adapter)
        self.refusal(lambda: self.dispatch(adapter, "run_development_tests", {"command": "pytest"}))

    def test_success_requires_exact_evaluator_and_case_event_order(self):
        observer = FakeObserver()
        adapter, runtime, _ = self.make_adapter(observer=observer)
        self.write_candidate(adapter)
        result = self.dispatch(adapter, "run_development_tests", {})
        self.assertEqual(result["status"], "OFFLINE_DEV_TESTS_PASS")
        self.assertEqual(result["evidence_layer"], "SYNTHETIC_FAKE_RUNTIME")
        self.assertEqual(len(runtime.runs), 1)
        request = runtime.runs[0]
        self.assertEqual(request["schema"], "cal-s1-dev-request/v1")
        self.assertEqual(request["cases"], list(CASES))
        self.assertRegex(request["run_id"], r"^[0-9a-f]+$")
        self.assertEqual(request["observer_sha256"], OBSERVER)
        self.assertEqual(bytes.fromhex(request["candidate_hex"]), b"def answer():\n    return 42\n")
        self.assertEqual(len(observer.last_events), 8)

    def test_second_run_uses_fresh_run_id(self):
        adapter, runtime, _ = self.make_adapter()
        self.write_candidate(adapter)
        self.dispatch(adapter, "run_development_tests", {})
        self.dispatch(adapter, "run_development_tests", {})
        self.assertNotEqual(runtime.runs[0]["run_id"], runtime.runs[1]["run_id"])

    def test_stdout_pass_and_exit_zero_without_witness_is_refused(self):
        adapter, _, _ = self.make_adapter(FakeRuntime(mode="stdout_only"))
        self.write_candidate(adapter)
        self.refusal(lambda: self.dispatch(adapter, "run_development_tests", {}))

    def test_missing_observer_provider_is_refused(self):
        adapter, _, _ = self.make_adapter(with_observer=False)
        self.write_candidate(adapter)
        self.refusal(lambda: self.dispatch(adapter, "run_development_tests", {}))

    def test_observer_identity_mismatch_is_refused(self):
        observer = FakeObserver()
        observer.identity_sha256 = "0" * 64
        adapter, _, _ = self.make_adapter(observer=observer)
        self.write_candidate(adapter)
        self.refusal(lambda: self.dispatch(adapter, "run_development_tests", {}))

    def test_observer_transcript_consumed_different_candidate_even_when_runtime_restores(self):
        class RestoringRuntime(FakeRuntime):
            def run_development_tests(self, request):
                original = self.candidates["candidate.py"]
                self.candidates["candidate.py"] = Entry(b"temporary candidate")
                self.candidates["candidate.py"] = original
                return super().run_development_tests(request)
        runtime = RestoringRuntime()
        observer = FakeObserver(mode="wrong_consumed_candidate")
        adapter, _, _ = self.make_adapter(runtime, observer=observer)
        self.write_candidate(adapter)
        self.refusal(lambda: self.dispatch(adapter, "run_development_tests", {}))
        self.assertEqual(runtime.candidates["candidate.py"].data, b"def answer():\n    return 42\n")

    def test_oversized_observer_event_is_refused(self):
        adapter, _, _ = self.make_adapter(observer=FakeObserver(mode="oversize_event"))
        self.write_candidate(adapter)
        self.refusal(lambda: self.dispatch(adapter, "run_development_tests", {}))

    def test_passed_result_finalizes(self):
        adapter, _, _ = self.make_adapter()
        self.write_candidate(adapter)
        result = self.dispatch(adapter, "run_development_tests", {})
        self.assertEqual(adapter.finalize(result), result)

    def test_pass_result_cannot_finalize_after_candidate_rewrite(self):
        adapter, _, _ = self.make_adapter()
        self.write_candidate(adapter)
        passed = self.dispatch(adapter, "run_development_tests", {})
        self.write_candidate(adapter, ["def answer():", "    return 43"])
        self.refusal(lambda: adapter.finalize(passed))

    def test_dispatch_budget_refuses_after_256_operations(self):
        adapter, _, _ = self.make_adapter()
        for _ in range(256):
            self.dispatch(adapter, "read_packet_file", {"path": PATHS[0]})
        self.refusal(lambda: self.dispatch(adapter, "read_packet_file", {"path": PATHS[0]}))

    def test_refused_request_counts_toward_256_dispatch_budget(self):
        adapter, _, _ = self.make_adapter()
        for _ in range(255):
            self.dispatch(adapter, "read_packet_file", {"path": PATHS[0]})
        self.refusal(lambda: self.dispatch(adapter, "missing_tool", {}))
        self.refusal(lambda: self.dispatch(adapter, "read_packet_file", {"path": PATHS[0]}))

    def test_witness_run_budget_refuses_after_32_runs(self):
        adapter, _, _ = self.make_adapter()
        self.write_candidate(adapter)
        for _ in range(32):
            self.dispatch(adapter, "run_development_tests", {})
        self.refusal(lambda: self.dispatch(adapter, "run_development_tests", {}))

    def test_forged_complete_return_receipt_is_ignored(self):
        class ForgedRuntime(FakeRuntime):
            def run_development_tests(self, request):
                return {"exit_code": 0, "stdout": "PASS", "receipt": {"cases": list(CASES), "passed": True}}
        adapter, _, _ = self.make_adapter(ForgedRuntime(), observer=FakeObserver(mode="stdout_only"))
        self.write_candidate(adapter)
        self.refusal(lambda: self.dispatch(adapter, "run_development_tests", {}))

    def test_early_exit_after_evaluator_start_is_refused(self):
        adapter, _, _ = self.make_adapter(FakeRuntime(mode="early_exit"))
        self.write_candidate(adapter)
        self.refusal(lambda: self.dispatch(adapter, "run_development_tests", {}))

    def test_valid_shaped_weak_candidate_fails_case_evidence(self):
        observer = FakeObserver(mode="weak_candidate")
        adapter, _, _ = self.make_adapter(FakeRuntime(mode="weak_candidate"), observer=observer)
        self.write_candidate(adapter, ["def answer():", "    return None"])
        self.refusal(lambda: self.dispatch(adapter, "run_development_tests", {}))
        self.assertTrue(any(event.get("event") == "case_finished" and event.get("passed") is False for event in observer.last_events))

    def test_missing_case_receipt_is_refused(self):
        adapter, _, _ = self.make_adapter(FakeRuntime(mode="skip_case"))
        self.write_candidate(adapter)
        self.refusal(lambda: self.dispatch(adapter, "run_development_tests", {}))

    def test_duplicate_case_receipt_is_refused(self):
        adapter, _, _ = self.make_adapter(FakeRuntime(mode="duplicate_case"))
        self.write_candidate(adapter)
        self.refusal(lambda: self.dispatch(adapter, "run_development_tests", {}))

    def test_replayed_event_with_old_run_id_is_refused(self):
        adapter, _, _ = self.make_adapter(FakeRuntime(mode="replay"))
        self.write_candidate(adapter)
        self.refusal(lambda: self.dispatch(adapter, "run_development_tests", {}))

    def test_malformed_event_missing_identity_is_refused(self):
        adapter, _, _ = self.make_adapter(FakeRuntime(mode="malformed_event"))
        self.write_candidate(adapter)
        self.refusal(lambda: self.dispatch(adapter, "run_development_tests", {}))

    def test_candidate_mutation_during_test_run_is_refused(self):
        class MutatingRuntime(FakeRuntime):
            def run_development_tests(self, request):
                result = super().run_development_tests(request)
                self.candidates["candidate.py"] = Entry(b"changed after evaluation")
                return result
        adapter, _, _ = self.make_adapter(MutatingRuntime())
        self.write_candidate(adapter)
        self.refusal(lambda: self.dispatch(adapter, "run_development_tests", {}))


if __name__ == "__main__":
    unittest.main()
