"""Additional fake-runtime and synthetic packet-custody controls for offline v1."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from test_offline_profile import (
    Adapter, Entry, FakeObserver, FakeRuntime, PACKET, PATHS,
    Refusal, Witness, digest, envelope, profile,
)


HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent


def import_file(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import retained source: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PACKET_BUILDER = import_file(
    "retained_rc1_prepare_packet",
    RESEARCH / "cal_context_free_packet_macos_rc1_20261009" / "candidate" / "prepare_packet.py",
)
PACKET_CHECKER = import_file(
    "retained_rc1_independent_packet_checker",
    RESEARCH / "cal_context_free_packet_macos_rc1_20261009" / "candidate" / "independent_packet_checker.py",
)


class SupplementalAdapterTests(unittest.TestCase):
    """Reuse the primary module's profile, envelope, and fake-runtime fixtures."""

    def make_adapter(self, runtime=None, p=None, observer=None, with_observer=True):
        runtime = runtime or FakeRuntime()
        if observer is None and with_observer:
            observer = FakeObserver(mode=runtime.mode)
        witness = Witness(observer) if with_observer else Witness()
        return Adapter(p or profile(), runtime, witness), runtime, witness

    def refusal(self, call):
        try:
            result = call()
        except Refusal:
            return
        self.assertIsInstance(result, Refusal, "unsafe input must produce Refusal")

    def dispatch(self, adapter, tool, args):
        return adapter.dispatch(envelope(tool, args))

    def write_candidate(self, adapter, lines=None):
        lines = ["def answer():", "    return 42"] if lines is None else lines
        return self.dispatch(adapter, "write_candidate_lines", {
            "path": "candidate.py", "lines": lines,
        })

    def test_all_seven_allowlisted_reads_return_exact_text_and_digest(self):
        adapter, _, _ = self.make_adapter()
        for path in PATHS:
            with self.subTest(path=path):
                result = self.dispatch(adapter, "read_packet_file", {"path": path})
                self.assertEqual(result["content"].encode("utf-8"), PACKET[path])
                self.assertEqual(result["sha256"], digest(PACKET[path]))

    def test_same_instance_executor_observer_wiring_is_refused(self):
        from test_offline_profile import FakeObserver
        class Combined(FakeRuntime, FakeObserver):
            pass
        combined = Combined()
        with self.assertRaises(Refusal) as caught:
            Adapter(profile(), combined, Witness(combined))
        self.assertEqual(caught.exception.reason, "EXECUTOR_OBSERVER_ALIAS")

    def test_missing_allowlisted_packet_entry_is_refused(self):
        files = dict(FakeRuntime().files)
        del files["dev/guide.txt"]
        adapter, _, _ = self.make_adapter(FakeRuntime(files))
        self.refusal(lambda: self.dispatch(adapter, "read_packet_file", {"path": "dev/guide.txt"}))

    def test_oversize_packet_read_is_refused_even_with_matching_profile_hash(self):
        path = "dev/guide.txt"
        data = b"x" * 65537
        files = dict(FakeRuntime().files)
        files[path] = Entry(data)
        reads = {p: digest(PACKET[p]) for p in PATHS}
        reads[path] = digest(data)
        adapter, _, _ = self.make_adapter(FakeRuntime(files), profile(reads=reads))
        self.refusal(lambda: self.dispatch(adapter, "read_packet_file", {"path": path}))

    def test_hash_matching_non_utf8_packet_bytes_are_refused(self):
        path = "dev/guide.txt"
        data = b"\xff\xfe"
        files = dict(FakeRuntime().files)
        files[path] = Entry(data)
        reads = {p: digest(PACKET[p]) for p in PATHS}
        reads[path] = digest(data)
        adapter, _, _ = self.make_adapter(FakeRuntime(files), profile(reads=reads))
        self.refusal(lambda: self.dispatch(adapter, "read_packet_file", {"path": path}))

    def test_wrong_evaluator_candidate_and_profile_bindings_are_refused(self):
        for changed in ("evaluator_sha256", "candidate_sha256", "profile_sha256"):
            class WrongBindingObserver(FakeObserver):
                def finish(self, run_id):
                    events = super().finish(run_id)
                    changed_events = []
                    for event in events:
                        altered = dict(event)
                        altered[changed] = "0" * 64
                        changed_events.append(altered)
                    self.last_events = tuple(changed_events)
                    return self.last_events
            with self.subTest(binding=changed):
                adapter, _, _ = self.make_adapter(observer=WrongBindingObserver())
                self.write_candidate(adapter)
                self.refusal(lambda: self.dispatch(adapter, "run_development_tests", {}))

    def test_boolean_exit_code_is_not_integer_success(self):
        class BoolExitRuntime(FakeRuntime):
            def run_development_tests(self, request):
                return {"exit_code": True, "stdout": "PASS"}
        adapter, _, _ = self.make_adapter(BoolExitRuntime())
        self.write_candidate(adapter)
        self.refusal(lambda: self.dispatch(adapter, "run_development_tests", {}))

    def test_boolean_integer_case_result_is_not_boolean_pass(self):
        class BoolLikeObserver(FakeObserver):
            def finish(self, run_id):
                events = super().finish(run_id)
                changed = []
                for event in events:
                    altered = dict(event)
                    if altered.get("event") == "case_finished":
                        altered["passed"] = 1
                    changed.append(altered)
                self.last_events = tuple(changed)
                return self.last_events
        adapter, _, _ = self.make_adapter(observer=BoolLikeObserver())
        self.write_candidate(adapter)
        self.refusal(lambda: self.dispatch(adapter, "run_development_tests", {}))

    def test_extra_witness_event_is_refused(self):
        class ExtraEventObserver(FakeObserver):
            def finish(self, run_id):
                self.last_events = (*super().finish(run_id), {"event": "extra", "run_id": run_id})
                return self.last_events
        adapter, _, _ = self.make_adapter(observer=ExtraEventObserver())
        self.write_candidate(adapter)
        self.refusal(lambda: self.dispatch(adapter, "run_development_tests", {}))

    def test_extra_witness_event_key_is_refused(self):
        class ExtraKeyObserver(FakeObserver):
            def finish(self, run_id):
                events = list(super().finish(run_id))
                events[0] = {**events[0], "claimed_by_candidate": True}
                self.last_events = tuple(events)
                return self.last_events
        adapter, _, _ = self.make_adapter(observer=ExtraKeyObserver())
        self.write_candidate(adapter)
        self.refusal(lambda: self.dispatch(adapter, "run_development_tests", {}))

    def test_runtime_read_exception_fails_closed(self):
        class BrokenReadRuntime(FakeRuntime):
            def read_packet(self, path):
                raise OSError("synthetic transport unavailable")
        adapter, _, _ = self.make_adapter(BrokenReadRuntime())
        self.refusal(lambda: self.dispatch(adapter, "read_packet_file", {"path": PATHS[0]}))

    def test_runtime_test_exception_fails_closed(self):
        class BrokenTestRuntime(FakeRuntime):
            def run_development_tests(self, request):
                raise OSError("synthetic evaluator transport unavailable")
        adapter, _, _ = self.make_adapter(BrokenTestRuntime())
        self.write_candidate(adapter)
        self.refusal(lambda: self.dispatch(adapter, "run_development_tests", {}))

    def test_oversize_stdout_feedback_is_refused(self):
        class LargeOutputRuntime(FakeRuntime):
            def run_development_tests(self, request):
                super().run_development_tests(request)
                return {"exit_code": 0, "stdout": "x" * 8193}
        adapter, _, _ = self.make_adapter(LargeOutputRuntime())
        self.write_candidate(adapter)
        self.refusal(lambda: self.dispatch(adapter, "run_development_tests", {}))

    def test_malformed_runtime_feedback_is_refused(self):
        class MalformedFeedbackRuntime(FakeRuntime):
            def run_development_tests(self, request):
                super().run_development_tests(request)
                return {"exit_code": 0, "stdout": b"PASS"}
        adapter, _, _ = self.make_adapter(MalformedFeedbackRuntime())
        self.write_candidate(adapter)
        self.refusal(lambda: self.dispatch(adapter, "run_development_tests", {}))

    def test_oversize_optional_receipt_is_refused(self):
        class LargeReceiptRuntime(FakeRuntime):
            def run_development_tests(self, request):
                super().run_development_tests(request)
                return {"exit_code": 0, "stdout": "PASS", "receipt": {"padding": "x" * 16384}}
        adapter, _, _ = self.make_adapter(LargeReceiptRuntime())
        self.write_candidate(adapter)
        self.refusal(lambda: self.dispatch(adapter, "run_development_tests", {}))

    def test_write_without_readback_is_refused(self):
        class NoReadbackRuntime(FakeRuntime):
            def write_candidate(self, path, data):
                pass
        adapter, _, _ = self.make_adapter(NoReadbackRuntime())
        self.refusal(lambda: self.write_candidate(adapter, ["x = 1"]))

    def test_external_scratch_drift_after_write_is_refused(self):
        adapter, runtime, _ = self.make_adapter()
        self.write_candidate(adapter)
        runtime.candidates["untracked.py"] = Entry(b"untracked")
        self.refusal(lambda: self.dispatch(adapter, "run_development_tests", {}))

    def test_valid_shaped_writer_that_drops_final_lf_fails_byte_drift(self):
        class DropsFinalLF(FakeRuntime):
            def write_candidate(self, path, data):
                super().write_candidate(path, data[:-1] if data.endswith(b"\n") else data)
        adapter, _, _ = self.make_adapter(DropsFinalLF())
        try:
            self.write_candidate(adapter, ["def answer():", "    return 42"])
        except Refusal as error:
            self.assertEqual(error.reason, "WRITE_BYTES_DRIFT")
        else:
            self.fail("writer silently dropped the protocol's final LF")

    def test_extra_envelope_tool_key_is_refused(self):
        adapter, _, _ = self.make_adapter()
        raw = envelope("read_packet_file", {"path": PATHS[0]})[:-1] + b',"tool_call_id":"synthetic"}'
        self.refusal(lambda: adapter.dispatch(raw))

    def test_extra_test_operation_argument_is_refused(self):
        adapter, _, _ = self.make_adapter()
        self.write_candidate(adapter)
        self.refusal(lambda: self.dispatch(adapter, "run_development_tests", {"evaluator": "other.py"}))


class PacketCustodyIntegrationTests(unittest.TestCase):
    """Exercise retained file-world staging only with synthetic bytes."""

    def prepare_synthetic(self, root: Path):
        source = root / "source"
        source.mkdir()
        paths = tuple(f"synthetic-file-{i}.txt" for i in range(7))
        files = []
        for i, rel in enumerate(paths):
            target = source / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            data = f"synthetic payload {i}\n".encode()
            target.write_bytes(data)
            files.append({"path": rel, "sha256": hashlib.sha256(data).hexdigest()})
        hidden = source / "hidden-source-only.txt"
        hidden.write_text("excluded controller-only fixture", encoding="utf-8")
        manifest = root / "manifest.json"
        manifest.write_text(json.dumps({
            "schema": "cal-context-free-packet-rc0",
            "experiment_id": "synthetic-custody-control",
            "files": files,
        }, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
        packet = root / "packet"
        PACKET_BUILDER.prepare(manifest, source, packet)
        return manifest, source, packet, hidden

    def test_builder_stages_only_allowlist_and_independent_checker_accepts(self):
        with tempfile.TemporaryDirectory() as temporary:
            manifest, source, packet, hidden = self.prepare_synthetic(Path(temporary))
            result = PACKET_CHECKER.check(manifest, source, packet)
            self.assertEqual(result["file_count"], 7)
            self.assertEqual(result["status"], "STAGED_BYTES_CODE_ISOLATED_CHECK")
            self.assertTrue(hidden.exists(), "synthetic unlisted source fixture should remain in source")
            self.assertFalse((packet / "world" / hidden.name).exists())
            (packet / "world").chmod(0o755)

    def test_independent_checker_rejects_extra_synthetic_staged_world_file(self):
        with tempfile.TemporaryDirectory() as temporary:
            manifest, source, packet, _ = self.prepare_synthetic(Path(temporary))
            world = packet / "world"
            world.chmod(0o755)
            (world / "extra.txt").write_text("synthetic drift", encoding="utf-8")
            with self.assertRaises(PACKET_CHECKER.CheckFailure) as caught:
                PACKET_CHECKER.check(manifest, source, packet)
            self.assertEqual(caught.exception.reason, "EXTRA_FILE")
            world.chmod(0o755)

    def test_independent_checker_rejects_stale_scratch_entry(self):
        with tempfile.TemporaryDirectory() as temporary:
            manifest, source, packet, _ = self.prepare_synthetic(Path(temporary))
            (packet / "scratch" / "stale.txt").write_text("synthetic scratch drift", encoding="utf-8")
            with self.assertRaises(PACKET_CHECKER.CheckFailure) as caught:
                PACKET_CHECKER.check(manifest, source, packet)
            self.assertEqual(caught.exception.reason, "SCRATCH_NOT_EMPTY")
            (packet / "world").chmod(0o755)


if __name__ == "__main__":
    unittest.main()
