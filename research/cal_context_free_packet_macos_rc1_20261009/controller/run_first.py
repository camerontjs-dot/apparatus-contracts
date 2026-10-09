#!/usr/bin/env python3
"""External first-run controller. Never place receipts inside the candidate world."""
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
CANDIDATE = ROOT / "candidate"
RECEIPTS = ROOT / "controller"
FREEZE = ROOT / "FREEZE.json"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def stamp():
    return datetime.now(timezone.utc).isoformat()


def ids(expected):
    return {name: sha((CANDIDATE / name).read_bytes()) for name in expected}


def main():
    frozen = json.loads(FREEZE.read_text())
    expected = frozen["candidate_sha256"]
    before = ids(expected)
    if before != expected:
        raise RuntimeError("CANDIDATE_FREEZE_IDENTITY_MISMATCH_PRE_EXECUTION")
    script_sha = sha(Path(__file__).read_bytes())
    if script_sha != frozen["external_runner_sha256"]:
        raise RuntimeError("EXTERNAL_RUNNER_FREEZE_IDENTITY_MISMATCH")
    stdout = RECEIPTS / "first-run.stdout"
    stderr = RECEIPTS / "first-run.stderr"
    receipt_path = RECEIPTS / "first-run.json"
    for path in (stdout, stderr, receipt_path):
        if path.exists():
            raise RuntimeError(f"FIRST_RUN_ALREADY_EXISTS: {path.name}")
    command = [sys.executable, "-B", "-m", "unittest", "discover", "-s", ".", "-p", "test_*.py", "-v"]
    if command[1:] != frozen["command_args"]:
        raise RuntimeError("COMMAND_MISMATCH")
    started = stamp()
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    try:
        result = subprocess.run(command, cwd=CANDIDATE, env=env, capture_output=True, timeout=60, check=False)
        rc = result.returncode
        timed_out = False
        output_out, output_err = result.stdout, result.stderr
    except subprocess.TimeoutExpired as error:
        rc = None
        timed_out = True
        output_out, output_err = error.stdout or b"", error.stderr or b""
    ended = stamp()
    stdout.write_bytes(output_out)
    stderr.write_bytes(output_err)
    after = ids(expected)
    m = re.search(rb"Ran (\d+) tests? in", output_err)
    passed = rc == 0 and not timed_out and m is not None and int(m.group(1)) == frozen["expected_test_count"] and b"\nOK\n" in output_err
    if after != expected:
        passed = False
    receipt = {
        "experiment_id": frozen["experiment_id"],
        "run_id": "FIRST-RUN-ONLY",
        "start_utc": started, "end_utc": ended,
        "system": platform.system(), "release": platform.release(),
        "machine": platform.machine(), "python": sys.version,
        "argv": command, "working_directory": "candidate/",
        "returncode": rc, "timed_out": timed_out,
        "tests_observed": int(m.group(1)) if m else None,
        "expected_test_count": frozen["expected_test_count"],
        "candidate_before_sha256": before,
        "candidate_after_sha256": after,
        "stdout_sha256": sha(output_out), "stderr_sha256": sha(output_err),
        "stdout_bytes": len(output_out), "stderr_bytes": len(output_err),
        "status": "PASS_BOUNDED_OFFLINE_PACKET_CONTROLS" if passed else "FAIL_OR_INCONCLUSIVE_PRESERVE_FIRST_RUN",
        "actor_admission": "BLOCKED",
        "qualification_nonclaims": ["model_actor", "docker", "network_isolation", "host_mcp", "provider_context", "blind_independent_reviewer"],
    }
    receipt_path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(json.dumps({k: receipt[k] for k in ("status", "returncode", "tests_observed", "expected_test_count", "stderr_sha256")}, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
