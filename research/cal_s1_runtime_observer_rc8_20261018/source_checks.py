"""Run source-level tests only. Blocks every subprocess launch during tests."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import platform
import sys
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent


class Records(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.records = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.records.append({"test": test.id(), "status": "PASS"})

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.records.append({"test": test.id(), "status": "FAIL"})

    def addError(self, test, err):
        super().addError(test, err)
        self.records.append({"test": test.id(), "status": "ERROR"})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(mode=0o700, parents=False, exist_ok=False)
    stream = io.StringIO()
    suite = unittest.defaultTestLoader.discover(str(HERE), pattern="test_*.py")
    with patch("subprocess.Popen", side_effect=AssertionError("LIVE_CALL_PROHIBITED_IN_SOURCE_TESTS")) as block:
        result = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=Records).run(suite)
        attempted = block.call_count
    raw = stream.getvalue().encode()
    (args.output / "TESTS.txt").write_bytes(raw)
    report = {"schema": "cal-rc8-source-tests-v1", "tests_run": result.testsRun,
              "failures": len(result.failures), "errors": len(result.errors), "skipped": len(result.skipped),
              "passed": result.wasSuccessful() and attempted == 0,
              "cases": result.records, "python": platform.python_version(), "platform": sys.platform,
              "source_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(HERE.glob("*.py"))},
              "log_sha256": hashlib.sha256(raw).hexdigest(),
              "evidence_class": "SOURCE_TESTS_AND_SYNTHETIC_CAPTURE_RECORDS_ONLY",
              "actual_candidate_execution": "NOT_RUN", "actual_docker_execution": "NOT_RUN",
              "model_inference": "NOT_RUN", "q13_admitted": False,
              "subprocess_guard_attempts": attempted,
              "observation_limit": "fake captures exercise code; not actual runtime observations"}
    (args.output / "RESULTS.json").write_text(json.dumps(report, sort_keys=True, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in ("tests_run", "failures", "errors", "skipped", "passed",
                                            "actual_candidate_execution", "actual_docker_execution", "q13_admitted")}, sort_keys=True))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
