"""Trusted external oracle and one-shot synthetic execution qualification.

Candidate Python is NEVER imported into this interpreter. Candidate stdout is
only an answer; it cannot supply evaluator/case events or a success verdict.
This observer proves bounded external behavior, not internal causal execution.
Live entry is gated and has NOT BEEN EXECUTED in this preparation.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import os
from pathlib import Path
import sys
import time

from execution_binding import (Approval, BoundaryError, Capture, CommandCapture,
                               DockerCaseRuntime, Pins, canonical, decode, regular_bytes,
                               require, sha, stage_synthetic_packet)

HERE = Path(__file__).resolve().parent


def grade_answer(captured: Capture, expected: dict) -> dict:
    """Pure judging logic. This function alone cannot attest a process ran."""
    require(type(captured) is Capture, "CAPTURE_MISSING")
    require(type(captured.returncode) is int and captured.returncode == 0, "CANDIDATE_EXIT_NONZERO")
    require(captured.stdin_complete is True, "CASE_INPUT_NOT_FULLY_SENT")
    require(type(captured.stdout) is bytes and type(captured.stderr) is bytes, "CAPTURE_STREAM_TYPES")
    require(len(captured.stdout) + len(captured.stderr) <= 65536, "CAPTURE_LIMIT")
    require(type(captured.pid) is int and captured.pid > 0 and
            type(captured.started_ns) is int and type(captured.ended_ns) is int and
            captured.started_ns <= captured.ended_ns, "CAPTURE_LIFECYCLE")
    value = decode(captured.stdout, 16384)
    require(type(value) is dict and set(value) == {"value"} and type(value["value"]) is str,
            "ANSWER_SHAPE_NOT_EVALUATOR_RECEIPT")
    require(canonical(value) == canonical(expected), "INCORRECT_ANSWER")
    return {"answer_correct": True, "answer_sha256": sha(captured.stdout),
            "not_established": "internal function/case causality or observer authentication"}


class Journal:
    """Only the trusted evaluator writes this. It is never mounted in a worker."""
    def __init__(self, root: Path):
        root.mkdir(mode=0o700, exist_ok=False)
        self.root = root
        self.events: list[dict] = []

    def event(self, kind: str, **data):
        obj = {"sequence": len(self.events), "event": kind, "time_ns": time.time_ns(), **data}
        self.events.append(obj)
        with (self.root / f"event-{obj['sequence']:04d}.json").open("xb") as stream:
            stream.write(canonical(obj))
        return obj


def verify_sources(manifest: dict):
    require(manifest.get("schema") == "cal-rc8-source-setup-v1", "MANIFEST_SCHEMA")
    files = manifest.get("files")
    require(type(files) is dict and len(files) > 0, "MANIFEST_EMPTY")
    for name, digest in files.items():
        relative = Path(name)
        require(not relative.is_absolute() and ".." not in relative.parts, "MANIFEST_PATH")
        require(sha(regular_bytes(HERE / relative, 1048576)) == digest, "SOURCE_DRIFT:" + name)
    require(manifest.get("phase") == "PUBLIC_SYNTHETIC_RUNTIME_OBSERVER_ONLY", "PHASE")
    require(manifest.get("model_inference") is False and manifest.get("q13_admission") is False, "SCOPE")


def run_once(approval: Approval, pins: Pins, manifest_path: Path, output: Path):
    manifest_raw = regular_bytes(manifest_path, 1048576)
    manifest_digest = sha(manifest_raw)
    approval.check(manifest_digest)  # no subprocess/metadata access before this
    approval.check_runtime(pins)
    manifest = decode(manifest_raw, 1048576)
    verify_sources(manifest)
    require(output.is_absolute() and output.parent.resolve() == output.parent, "OUTPUT_PARENT")
    require(output.parent.is_dir() and not output.exists(), "FRESH_OUTPUT_REQUIRED")
    repo = HERE.parents[1]
    require(not output.is_relative_to(repo) and not repo.is_relative_to(output), "OUTPUT_OVERLAPS_SOURCE")
    # A trusted operator must reserve this digest in the external attempt ledger.
    # The per-output marker below is not a global anti-replay registry.
    ledger = output.parent / ("rc8-attempt-" + manifest_digest + ".json")
    with ledger.open("xb") as stream:
        stream.write(canonical({"source_manifest_sha256": manifest_digest,
                                "started_ns": time.time_ns(), "run_scope": approval.scope}))
        stream.flush()
        os.fsync(stream.fileno())
    journal = Journal(output)
    spec = decode((HERE / "SPECIMENS.json").read_bytes(), 1048576)
    journal.event("qualification_started", source_manifest_sha256=manifest_digest,
                  evaluator_sha256=sha(Path(__file__).read_bytes()), model_inference=False)
    all_ok = True
    first_failure = None
    results = []
    try:
        for specimen in spec["specimens"]:
            sid = specimen["id"]
            require(type(sid) is str and sid.isidentifier(), "SPECIMEN_ID")
            trial = output / sid
            trial.mkdir(mode=0o700)
            packet, packet_files = stage_synthetic_packet(trial)
            candidate = trial / "candidate.py"
            data = specimen["source"].encode("utf-8")
            with candidate.open("xb") as stream:
                stream.write(data)
            candidate.chmod(0o444)
            commands = CommandCapture(trial / "commands")
            runtime = DockerCaseRuntime(pins, packet, candidate, commands, approval, manifest_digest, packet_files)
            journal.event("specimen_started", specimen=sid, candidate_sha256=sha(data))
            for case in spec["cases"]:
                request = canonical({"claim": case["claim"], "evidence": case["evidence"]})
                journal.event("case_started", specimen=sid, case=case["id"],
                              candidate_sha256=sha(data), input_sha256=sha(request))
                # Boundary exceptions are not converted into an expected bad answer.
                observed = runtime.invoke(request)
                try:
                    judged = grade_answer(observed["capture"], case["expected"])
                    verdict = "CORRECT_ANSWER"
                except BoundaryError as error:
                    judged = {"answer_correct": False, "reason": str(error)}
                    verdict = str(error)
                capture = observed["capture"]
                public_observation = {k: v for k, v in observed.items() if k != "capture"}
                public_observation.update({"returncode": capture.returncode,
                                           "stdout_sha256": sha(capture.stdout),
                                           "stderr_sha256": sha(capture.stderr)})
                matches = verdict == specimen["expected_verdict"]
                journal.event("case_finished", specimen=sid, case=case["id"],
                              observed=public_observation, oracle=judged,
                              expected_control_outcome=specimen["expected_verdict"], matched=matches)
                results.append({"specimen": sid, "case": case["id"], "matched": matches, "verdict": verdict})
                if not matches:
                    first_failure = {"specimen": sid, "case": case["id"], "verdict": verdict}
                    all_ok = False
                    break
            if not all_ok:
                break
    except BaseException as error:
        all_ok = False
        first_failure = {"type": type(error).__name__, "reason": str(error), "notes": getattr(error, "__notes__", [])}
    expected_total = len(spec["specimens"]) * len(spec["cases"])
    completed = len(results) == expected_total
    all_ok = all_ok and completed
    disposition = "PASS_BOUNDED_SYNTHETIC_RUNTIME_OBSERVER" if all_ok else "FAIL_OR_INCONCLUSIVE_RUNTIME_OBSERVER"
    result = {"disposition": disposition, "first_failure": first_failure,
              "case_controls_completed": len(results), "case_controls_planned": expected_total,
              "results": results, "source_manifest_sha256": manifest_digest,
              "evidence_layer": "HOST_OWNED_INVOCATIONS_AND_EXTERNAL_ORACLE",
              "q13_admitted": False, "model_generated_tools": "NOT_RUN",
              "cal_qualification": "NOT_RUN", "independent_authorship": False,
              "claim_limit": "trusted host observed exact isolated artifact output; not proof of candidate internals"}
    journal.event("qualification_finished", **result)
    with (output / "RESULT.json").open("xb") as stream:
        stream.write(canonical(result))
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--readiness", action="store_true")
    p.add_argument("--approval", type=Path, required=True)
    p.add_argument("--source-manifest", type=Path, required=True)
    p.add_argument("--pins", type=Path)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    try:
        approval = Approval(**decode(args.approval.read_bytes()))
        raw = args.source_manifest.read_bytes()
        approval.check(sha(raw))
        verify_sources(decode(raw, 1048576))
        if args.readiness:
            print(json.dumps({"record_shape": "ACCEPTABLE", "authenticity": "REQUIRES_EXTERNAL_OPERATOR_REVIEW",
                              "runtime_executed": False, "q13_admitted": False}))
            return 0
        require(args.pins is not None and args.output is not None, "LIVE_ARGUMENTS_MISSING")
        pins = Pins(**decode(args.pins.read_bytes()))
        result = run_once(approval, pins, args.source_manifest, args.output)
        print(json.dumps(result, sort_keys=True))
        return 0 if result["disposition"].startswith("PASS_") else 2
    except (BoundaryError, OSError, TypeError) as error:
        print(json.dumps({"status": "BLOCKED", "reason": str(error),
                          "q13_admitted": False, "permission_not_inferred": True}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
