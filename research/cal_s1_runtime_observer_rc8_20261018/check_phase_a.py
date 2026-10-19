"""Code-isolated post-run checker of host-owned raw command captures.

Imports no runner, evaluator or candidate. Integrity is not origin authentication:
this trusts the external controller custody root, host and Docker daemon. Fully
forged host captures are outside this claim, not made authentic by their hashes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import stat


class CheckError(ValueError):
    pass


def need(condition, reason):
    if not condition:
        raise CheckError(reason)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path, limit=1048576):
    st = path.lstat()
    need(stat.S_ISREG(st.st_mode) and st.st_nlink == 1 and st.st_size <= limit, "FILE_CUSTODY")
    return path.read_bytes()


def parse(raw):
    def unique(pairs):
        obj = {}
        for k, v in pairs:
            if k in obj:
                raise CheckError("DUPLICATE_JSON")
            obj[k] = v
        return obj
    def constant(_):
        raise CheckError("NONFINITE_JSON")
    return json.loads(raw.decode("utf-8"), object_pairs_hook=unique, parse_constant=constant)


def compact(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=True, separators=(",", ":"), allow_nan=False).encode()


def classify(raw, returncode):
    if type(raw) is not bytes or len(raw) > 16384:
        return "RAW_BYTES_LIMIT", None
    if type(returncode) is not int or returncode != 0:
        return "CANDIDATE_EXIT_NONZERO", None
    try:
        value = parse(raw)
    except CheckError as error:
        return ("DUPLICATE_JSON_KEY" if str(error) == "DUPLICATE_JSON" else "NONFINITE_JSON"), None
    except (ValueError, UnicodeError, RecursionError):
        return "INVALID_JSON", None
    if type(value) is not dict or set(value) != {"value"} or type(value["value"]) is not str:
        return "ANSWER_SHAPE_NOT_EVALUATOR_RECEIPT", None
    return "ANSWER", value


def check(source: Path, manifest_file: Path, root: Path):
    manifest_raw = read(manifest_file)
    manifest = parse(manifest_raw)
    need(manifest["schema"] == "cal-rc8-source-setup-v1", "SOURCE_SCHEMA")
    for name, expected in manifest["files"].items():
        p = Path(name)
        need(not p.is_absolute() and ".." not in p.parts, "SOURCE_PATH")
        need(digest(read(source / name)) == expected, "SOURCE_DRIFT")
    spec = parse(read(source / "SPECIMENS.json"))
    report = parse(read(root / "RESULT.json"))
    need(report["source_manifest_sha256"] == digest(manifest_raw), "RESULT_SOURCE_IDENTITY")
    need(report.get("q13_admitted") is False and report.get("model_generated_tools") == "NOT_RUN", "CLAIM_CEILING")
    expected_total = len(spec["cases"]) * len(spec["specimens"])
    need(report.get("case_controls_completed") == expected_total, "INCOMPLETE_CASES")
    seen_ids = set()
    outcomes = []
    for specimen in spec["specimens"]:
        trial = root / specimen["id"]
        need(digest(read(trial / "candidate.py", 32768)) == digest(specimen["source"].encode()), "CANDIDATE_ARTIFACT_DRIFT")
        directories = sorted((trial / "commands").iterdir())
        need(0 < len(directories) <= 128, "COMMAND_COUNT")
        records = []
        for directory in directories:
            need(directory.is_dir() and not directory.is_symlink() and
                 re.fullmatch(r"command-[0-9]{4}", directory.name) is not None, "COMMAND_DIRECTORY")
            record = parse(read(directory / "command.json"))
            record["raw_in"] = read(directory / "stdin.bin", 16384)
            record["raw_out"] = read(directory / "stdout.bin", 69632)
            record["raw_err"] = read(directory / "stderr.bin", 69632)
            need(len(record["raw_out"]) + len(record["raw_err"]) <= 65536, "STREAM_LIMIT")
            for raw_key, hash_key in (("raw_in", "stdin_sha256"), ("raw_out", "stdout_sha256"), ("raw_err", "stderr_sha256")):
                need(digest(record[raw_key]) == record[hash_key], "CAPTURE_BYTES_DRIFT")
            need(type(record["pid"]) is int and record["pid"] > 0 and
                 type(record["started_ns"]) is int and type(record["ended_ns"]) is int and
                 record["started_ns"] <= record["ended_ns"], "CAPTURE_LIFECYCLE")
            need(record.get("failure") is None, "CAPTURE_FAILURE")
            records.append(record)
        invoked = [r for r in records if r["argv"][3:5] == ["exec", "-i"] and
                   digest(r["argv"][-1].encode()) == manifest["guest_program_sha256"]]
        need(len(invoked) == len(spec["cases"]), "ACTUAL_CASE_INVOCATIONS_MISSING")
        for case, invocation in zip(spec["cases"], invoked):
            cid = invocation["argv"][5]
            need(re.fullmatch(r"[a-f0-9]{64}", cid) is not None and cid not in seen_ids, "WORKER_REUSED")
            seen_ids.add(cid)
            need(invocation["raw_in"] == compact({"claim": case["claim"], "evidence": case["evidence"]}), "CASE_INPUT_DRIFT")
            need(invocation.get("stdin_complete") is True and invocation.get("stdin_bytes_sent") == len(invocation["raw_in"]), "INPUT_DELIVERY")
            inspected = [r for r in records if r["argv"][3:] == ["inspect", cid] and r["returncode"] == 0]
            need(len(inspected) == 1, "WORKER_INSPECTION_MISSING")
            info = parse(inspected[0]["raw_out"])[0]
            h, c = info["HostConfig"], info["Config"]
            need(info["Id"] == cid and c["User"] == "65532:65532" and
                 h["ReadonlyRootfs"] is True and h["NetworkMode"] == "none" and h["Privileged"] is False,
                 "RAW_WORKER_BOUNDARY")
            need(not h.get("CapAdd") and h.get("CapDrop") == ["ALL"], "RAW_CAPABILITIES")
            need(all(m["Destination"] in {"/packet", "/candidate/candidate.py", "/scratch"} for m in info["Mounts"]), "RAW_EXTRA_MOUNT")
            removals = [r for r in records if r["argv"][3:] == ["rm", "-f", cid] and r["returncode"] == 0 and r["started_ns"] >= invocation["ended_ns"]]
            need(len(removals) == 1, "OWNED_TEARDOWN_MISSING")
            absent = [r for r in records if r["argv"][3:] == ["ps", "-aq", "--no-trunc"] and r["returncode"] == 0 and
                      r["started_ns"] >= removals[0]["ended_ns"] and cid not in r["raw_out"].decode().splitlines()]
            need(bool(absent), "REMOVAL_NOT_OBSERVED")
            category, value = classify(invocation["raw_out"], invocation["returncode"])
            if category == "ANSWER":
                category = "CORRECT_ANSWER" if compact(value) == compact(case["expected"]) else "INCORRECT_ANSWER"
            need(category == specimen["expected_verdict"], "CONTROL_WRONG_REASON:" + category)
            outcomes.append({"specimen": specimen["id"], "case": case["id"], "verdict": category, "matched": True})
    need(outcomes == report["results"], "SUMMARY_DISAGREES_WITH_RAW_CAPTURE")
    need(report["disposition"] == "PASS_BOUNDED_SYNTHETIC_RUNTIME_OBSERVER", "SUMMARY_DISPOSITION")
    return {"result": "RAW_CAPTURE_AND_ORACLE_AGREE", "controls": len(outcomes),
            "unique_workers": len(seen_ids), "q13_admitted": False,
            "trust_limit": "external host custody and daemon; not cryptographic origin or independent authorship"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--run", type=Path, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(check(args.source, args.manifest, args.run), sort_keys=True))
    except (CheckError, OSError, KeyError, ValueError, TypeError) as error:
        print(json.dumps({"result": "NOT_ACCEPTED", "reason": str(error), "q13_admitted": False}))
        raise SystemExit(2)
