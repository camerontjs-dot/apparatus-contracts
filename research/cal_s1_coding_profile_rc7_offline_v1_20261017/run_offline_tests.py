#!/usr/bin/env python3
"""Run stdlib source controls and save machine evidence; no runtime launch.

All adapter execution and observation interfaces are synthetic fixtures. The
unchanged packet builder/checker exercise real temporary filesystem bytes only.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import io
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Result(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rows = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.rows.append({"test": test.id(), "status": "PASS"})

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.rows.append({"test": test.id(), "status": "FAIL"})

    def addError(self, test, err):
        super().addError(test, err)
        self.rows.append({"test": test.id(), "status": "ERROR"})


def adverse_controls():
    from offline_profile import Adapter, Refusal, Witness
    from test_offline_profile import FakeRuntime, FakeObserver, profile, envelope

    class DropLF(FakeRuntime):
        def write_candidate(self, path, data):
            super().write_candidate(path, data[:-1])

    class ForgedReport(FakeRuntime):
        def run_development_tests(self, request):
            forged = FakeObserver()
            forged.begin(request)
            return {"exit_code": 0, "stdout": "Ran 3 tests: PASS",
                    "receipt": {"events": forged.finish(request["run_id"]), "passed": True}}

    rows = []
    for name, runtime, observer in (
        ("positive_synthetic_transcript", FakeRuntime(), FakeObserver()),
        ("plausible_pass_no_case_execution", FakeRuntime(), FakeObserver("stdout_only")),
        ("early_exit_before_cases", FakeRuntime(), FakeObserver("early_exit")),
        ("well_shaped_weak_candidate_failed_case", FakeRuntime(), FakeObserver("weak_candidate")),
        ("fully_forged_runtime_receipt", ForgedReport(), FakeObserver("stdout_only")),
        ("missing_external_observer", FakeRuntime(), None),
        ("write_drops_terminal_lf", DropLF(), FakeObserver()),
        ("different_consumed_candidate", FakeRuntime(), FakeObserver("wrong_consumed_candidate")),
    ):
        witness = Witness(observer)
        adapter = Adapter(profile(), runtime, witness)
        request = envelope("write_candidate_lines", {"path": "candidate.py", "lines": ["def answer():", "    return None" if "weak_candidate" in name else "    return 42"]})
        try:
            adapter.dispatch(request)
            verdict = adapter.dispatch(envelope("run_development_tests", {}))
            adapter.finalize(verdict)
            status, reason = "ACCEPTED_SYNTHETIC_ONLY", None
        except Refusal as error:
            status, reason = "REFUSED", error.reason
        expected = "ACCEPTED_SYNTHETIC_ONLY" if name == "positive_synthetic_transcript" else "REFUSED"
        rows.append({"control": name, "observed": status, "reason": reason,
                     "expected": expected, "matched": status == expected,
                     "observer_events": len(witness.events),
                     "decisions": adapter.decisions,
                     "evidence_layer": "SYNTHETIC_FAKE_RUNTIME"})
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    source = {p.name: digest(p) for p in sorted(HERE.iterdir())
              if p.is_file() and (p.suffix == ".py" or p.name == "CONTROLS.json")}
    dependencies = {}
    for name in ("prepare_packet.py", "independent_packet_checker.py"):
        p = HERE.parent / "cal_context_free_packet_macos_rc1_20261009" / "candidate" / name
        dependencies[str(p.relative_to(HERE.parent.parent))] = digest(p)
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    stream = io.StringIO()
    suite = unittest.defaultTestLoader.discover(str(HERE), pattern="test_*.py")
    result = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=Result).run(suite)
    controls = adverse_controls()
    (args.output / "ADVERSARIAL-RECEIPTS.json").write_text(json.dumps(controls, indent=2, sort_keys=True) + "\n")
    log = stream.getvalue()
    # Raw failing paths remain available to the invoking controller. Public
    # receipts use a repo-relative display root, explicitly a sanitized copy.
    log = log.replace(str(HERE.parent.parent), "<repository>")
    (args.output / "TESTS.txt").write_text(log, encoding="utf-8")
    unchanged = all(digest(HERE / name) == expected for name, expected in source.items())
    report = {
        "schema": "cal-rc7-offline-source-tests/v1", "started_utc": started,
        "completed_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "classification": "OFFLINE_PROFILE_PREPARATION_ONLY",
        "q13": "NOT_ADMITTED", "live_qualification": "NOT_RUN",
        "qualification_stop": "BLOCKED_PREFLIGHT_TOOL_SAFETY_DENIAL",
        "engine": "python.stdlib.unittest", "python_version": sys.version,
        "platform": sys.platform, "tests_run": result.testsRun,
        "failures": len(result.failures), "errors": len(result.errors),
        "skipped": len(result.skipped), "cases": result.rows,
        "passed": result.wasSuccessful() and unchanged and result.testsRun > 0 and not result.skipped and all(x["matched"] for x in controls),
        "source_unchanged": unchanged, "source_sha256": source,
        "retained_dependency_sha256": dependencies,
        "log_sha256": digest(args.output / "TESTS.txt"),
        "adversarial_receipts_sha256": digest(args.output / "ADVERSARIAL-RECEIPTS.json"),
        "log_path_sanitization": "repository display root replaced; original controller logs retained externally",
        "adapter_execution": "FAKE_RUNTIME_INTERFACE",
        "execution_observer": "SEPARATE_FAKE_OBSERVER_INTERFACE",
        "actual_candidate_or_CAL_evaluator_execution": "NOT_RUN",
        "independence": "source-informed subagent tests/review; parent ran unittest; no blind scientific independence",
    }
    (args.output / "RESULTS.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: report[key] for key in ("classification", "tests_run", "failures", "errors", "passed", "q13")}))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
