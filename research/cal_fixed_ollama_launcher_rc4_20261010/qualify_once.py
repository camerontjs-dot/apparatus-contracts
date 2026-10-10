#!/usr/bin/env python3
"""External, source-informed one-attempt Q01-Q13 controller. Never runs inference.

Run only with a separately empty receipt directory after FREEZE.json is committed.
No checker/control/receipt file is mounted into either disposable Docker worker.
The checker authorship is the same engineering controller; it is not blind review.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import traceback

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PACKET_CODE = REPO / "research/cal_context_free_packet_macos_rc1_20261009/candidate"
from identity import BASE, inventory, check_local
import receipt_check
import network_state_validator
PYTHON = "/usr/local/bin/python3"
CLEAN_ENV = ["/usr/bin/env", "-i", "PATH=/usr/local/bin:/usr/bin:/bin", "HOME=/"]
CELLS = {f"Q{i:02}": {"status": "NOT_RUN"} for i in range(1, 14)}


def stamp():
    return datetime.datetime.now(datetime.UTC).isoformat()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Stop(Exception):
    pass


class Controller:
    def __init__(self, output, candidate_commit, freeze_sha256, review, pins_path):
        self.output = output.resolve()
        if self.output == REPO or self.output.is_relative_to(REPO):
            raise Stop("RECEIPTS_MUST_BE_OUTSIDE_REPO")
        self.output.mkdir()  # Never overwrite an attempt or receipt.
        self.started_at = stamp()
        self.candidate_commit = candidate_commit
        self.freeze_sha256 = freeze_sha256
        self.review_path = review
        self.pins_path = pins_path
        self.commands = []
        self.process_events = []
        def observe_process(event, args):
            if event in {"subprocess.Popen", "os.system", "os.posix_spawn", "os.spawn", "os.exec", "os.fork", "os.forkpty"}:
                self.process_events.append({"event": event, "at": stamp()})
        sys.addaudithook(observe_process)
        self.tools = []
        self.artifacts = {}
        self.resources = {}
        self.cleanup_attempted = set()
        self.tool_serial = 0
        self.docker_path = None
        self.serial = 0
        self.owned = []
        self.current = "PRECHECK"
        self.first_failure = None
        self.env = {"HOME": os.environ["HOME"], "PATH": "/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin", "LC_ALL": "C", "TZ": "UTC"}

    def save(self, name, value):
        raw = json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False).encode() + b"\n"
        return self.save_raw(name, raw)

    def save_raw(self, name, raw):
        (self.output / name).write_bytes(raw)
        self.artifacts[name] = {"sha256": digest(raw), "bytes": len(raw)}
        return digest(raw)

    def check(self, condition, reason):
        if not condition:
            raise Stop(reason)

    def command(self, argv, data=b""):
        if argv[0] == "docker":
            self.check(self.docker_path is not None, "UNPINNED_DOCKER")
            argv = [self.docker_path, *argv[1:]]
        self.serial += 1
        directory = self.output / f"command-{self.serial:03}"
        directory.mkdir()
        start = stamp()
        timed_out = False
        launch_error = None
        try:
            result = subprocess.run(argv, input=data, capture_output=True, env=self.env, timeout=15)
        except subprocess.TimeoutExpired as error:
            timed_out = True
            result = subprocess.CompletedProcess(argv, 124, error.stdout or b"", error.stderr or b"")
        except OSError as error:
            launch_error = {"type": type(error).__name__, "errno": error.errno, "detail": str(error)}
            result = subprocess.CompletedProcess(argv, 126, b"", str(error).encode())
        for name, raw in (("stdin", data), ("stdout", result.stdout), ("stderr", result.stderr)):
            (directory / name).write_bytes(raw)
        receipt = {"serial": self.serial, "cell": self.current, "argv": argv, "started_at": start, "ended_at": stamp(), "exit_code": result.returncode,
                   "timed_out": timed_out, "launch_error": launch_error, "stdin_sha256": digest(data), "stdout_sha256": digest(result.stdout),
                   "stderr_sha256": digest(result.stderr), "environment": self.env}
        (directory / "receipt.json").write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
        self.commands.append(receipt)
        if launch_error:
            raise Stop("PROCESS_LAUNCH_INSTRUMENTATION_FAILED")
        return result

    def docker(self, *args):
        return self.command(["docker", "--context", "desktop-linux", *args])

    def probe(self, cid, *args):
        return self.docker("exec", cid, *CLEAN_ENV, PYTHON, "-I", "-B", "-c", (HERE / "worker_control.py").read_text(), *args)

    def create(self, world, suffix):
        name = "cal-q-" + digest(str(self.output).encode())[:12] + "-" + suffix
        argv = ["docker", "--context", "desktop-linux", "create", "--pull", "never", "--platform", "linux/arm64",
                "--name", name, "--label", "cal.qualification.owner=" + name, "--hostname", "cal-public-synthetic",
                "--user", "65532:65532", "--read-only", "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
                "--network", "none", "--ipc", "none", "--cgroupns", "private", "--pids-limit", "64", "--memory", "256m",
                "--memory-swap", "256m", "--cpus", "1", "--env", "PATH=/usr/local/bin:/usr/bin:/bin", "--no-healthcheck",
                "--mount", f"type=bind,source={world},target=/packet,readonly,bind-recursive=disabled,bind-propagation=rprivate",
                "--tmpfs", "/scratch:rw,noexec,nosuid,nodev,size=16m,uid=65532,gid=65532,mode=700",
                "--entrypoint", "/usr/bin/env", self.pins["image_ref"], "-i", "PATH=/usr/local/bin:/usr/bin:/bin", "HOME=/", PYTHON, "-I", "-B", "-c", "import time; time.sleep(600)"]
        result = self.command(argv)
        self.check(result.returncode == 0, "CONTAINER_CREATE_FAILED")
        cid = result.stdout.decode().strip()
        self.check(re.fullmatch(r"[a-f0-9]{64}", cid), "UNKNOWN_CONTAINER_ID")
        self.owned.append(cid)
        self.resources[cid] = {"name": name, "world": str(world), "suffix": suffix, "created_at": stamp(), "removed": False}
        self.save("OWNED-RESOURCES.json", self.resources)
        self.check(self.docker("start", cid).returncode == 0, "CONTAINER_START_FAILED")
        return cid

    def tool(self, adapter, raw, expected=None, model=False, execution_refusal=None):
        self.tool_serial += 1
        number = self.tool_serial
        command_before = self.serial
        process_before = len(self.process_events)
        self.save_raw(f"tool-{number:03}.request", raw)
        start = stamp()
        try:
            result = adapter.dispatch_model_call(raw) if model else adapter.dispatch(raw)
            observed = {"status": "OK", "result": result}
        except self.adapter.Refusal as error:
            observed = {"status": "REFUSED", "reason": error.reason}
        receipt = {"started_at": start, "ended_at": stamp(), "request_sha256": digest(raw),
                   "host_process_before": process_before, "host_process_after": len(self.process_events),
                   "model_binding": model, "command_before": command_before, "command_after": self.serial,
                   "expected_refusal": expected, **observed}
        self.tools.append(receipt)
        self.save(f"tool-{number:03}.response.json", receipt)
        if expected:
            self.check(self.serial == command_before and len(self.process_events) == process_before, "REFUSAL_DISPATCHED_HOST_COMMAND")
        if expected:
            self.check(observed == {"status": "REFUSED", "reason": expected}, "WRONG_TOOL_REFUSAL:" + str(observed))
        elif execution_refusal:
            self.check(observed == {"status": "REFUSED", "reason": execution_refusal} and self.serial == command_before + 1, "WRONG_EXECUTION_REFUSAL")
        else:
            self.check(observed["status"] == "OK", "ALLOWED_TOOL_FAILED:" + str(observed))
        return observed

    def call(self, adapter, name, arguments, expected=None, execution_refusal=None):
        return self.tool(adapter, json.dumps({"name": name, "arguments": arguments}, ensure_ascii=True).encode(), expected, execution_refusal=execution_refusal)

    def pass_cell(self, details):
        CELLS[self.current] = {"status": "PASS_BOUNDED", "details": details, "completed_at": stamp()}

    def run(self):
        self.check(sys.flags.ignore_environment and sys.flags.no_user_site and sys.flags.dont_write_bytecode, "REQUIRE_PYTHON_E_s_B_FLAGS")
        freeze_raw = (HERE / "FREEZE.json").read_bytes()
        freeze = json.loads(freeze_raw)
        self.check(digest(freeze_raw) == self.freeze_sha256, "FREEZE_IDENTITY_MISMATCH")
        self.check(freeze["state"] == "FROZEN_BEFORE_EXPOSURE" and freeze["model_inference_calls_authorized"] == 0, "NOT_FROZEN")
        self.check(not self.pins_path.resolve().is_relative_to(REPO), "PINS_MUST_BE_EXTERNAL")
        pins_raw = self.pins_path.read_bytes()
        self.check(digest(pins_raw) == freeze["pins_sha256"], "EXTERNAL_PINS_IDENTITY_MISMATCH")
        self.pins = json.loads(pins_raw)
        self.check(inventory() == freeze["frozen_files"], "CANDIDATE_INVENTORY_DRIFT")
        check_local(self.pins)
        self.check(self.env["HOME"] == self.pins["controller_home"], "CONTROLLER_HOME_DRIFT")
        self.docker_path = self.pins["docker_binary"]["path"]
        head = self.command(["git", "-C", str(REPO), "rev-parse", "HEAD"])
        self.check(head.returncode == 0 and head.stdout.decode().strip() == self.candidate_commit, "CANDIDATE_COMMIT_DRIFT")
        clean = self.command(["git", "-C", str(REPO), "status", "--porcelain", "--untracked-files=all"])
        self.check(clean.returncode == 0 and not clean.stdout, "DIRTY_CANDIDATE")
        changed = self.command(["git", "-C", str(REPO), "diff", "--name-only", freeze["prepared_commit"], self.candidate_commit])
        self.check(changed.returncode == 0 and changed.stdout.decode().splitlines() == [str((HERE / "FREEZE.json").relative_to(REPO))], "FREEZE_COMMIT_MUST_ONLY_ADD_FREEZE")
        lineage = self.command(["git", "-C", str(REPO), "merge-base", "--is-ancestor", freeze["prepared_commit"], self.candidate_commit])
        self.check(lineage.returncode == 0 and freeze["base_commit"] == BASE, "CANDIDATE_LINEAGE_DRIFT")
        scope = self.command(["git", "-C", str(REPO), "diff", "--name-only", BASE, self.candidate_commit])
        self.check(scope.returncode == 0 and all(x.startswith(str(HERE.relative_to(REPO)) + "/") for x in scope.stdout.decode().splitlines()), "HISTORICAL_REPO_CHANGE")
        for path, expected_hash in freeze["frozen_files"].items():
            committed = self.command(["git", "-C", str(REPO), "show", self.candidate_commit + ":" + path])
            self.check(committed.returncode == 0 and digest(committed.stdout) == expected_hash, "UNCOMMITTED_FROZEN_BYTES:" + path)
        committed_freeze = self.command(["git", "-C", str(REPO), "show", self.candidate_commit + ":" + str((HERE / "FREEZE.json").relative_to(REPO))])
        self.check(committed_freeze.returncode == 0 and digest(committed_freeze.stdout) == self.freeze_sha256, "UNCOMMITTED_FREEZE")
        review_raw = self.review_path.read_bytes()
        review = json.loads(review_raw)
        self.check(review["candidate_commit"] == self.candidate_commit and review["freeze_sha256"] == self.freeze_sha256
                   and review["authorization"] == "ONE_ZERO_MODEL_PUBLIC_SYNTHETIC_QUALIFICATION"
                   and review["receipt_directory"] == str(self.output)
                   and review["authority"] == "camerontjs-dot/apparatus-contracts#173"
                   and bool(review["reviewer"]), "MISSING_EXPLICIT_OPERATOR_REVIEW")
        reviewed_at = datetime.datetime.fromisoformat(review["reviewed_at"])
        self.check(datetime.datetime.fromisoformat(freeze["frozen_at"]) <= reviewed_at <= datetime.datetime.fromisoformat(self.started_at), "REVIEW_TIME_INVALID")
        ledger = Path(review["attempt_ledger"]).resolve(strict=True)
        self.check(not ledger.is_relative_to(REPO) and not ledger.is_relative_to(self.output), "LEDGER_MUST_BE_EXTERNAL")
        (ledger / self.freeze_sha256).mkdir()  # irreversible attempt reservation; never remove/retry
        self.save_raw("OPERATOR-REVIEW.json", review_raw)
        context_result = self.docker("context", "inspect", "desktop-linux")
        self.check(context_result.returncode == 0 and json.loads(context_result.stdout)[0]["Endpoints"]["docker"]["Host"] == self.pins["docker_endpoint"], "DAEMON_ENDPOINT_DRIFT")
        version = self.docker("version", "--format", "{{.Server.Version}}")
        self.check(version.returncode == 0 and version.stdout.decode().strip() == self.pins["docker_engine"], "ENGINE_DRIFT")
        image_result = self.docker("image", "inspect", self.pins["image_ref"])
        self.check(image_result.returncode == 0, "PINNED_IMAGE_NOT_PROVISIONED")
        image = json.loads(image_result.stdout)[0]
        self.check(image["Id"] == self.pins["image_id"] and image["Architecture"] == self.pins["image_architecture"]
                   and image["Os"] == self.pins["image_os"] and image["Config"]["Env"] == self.pins["image_config_env"]
                   and not image["Config"].get("Volumes"), "IMAGE_CONFIG_DRIFT")
        before = {path: digest((REPO / path).read_bytes()) for path in freeze["frozen_files"]}
        self.check(before == freeze["frozen_files"], "FROZEN_BYTES_CHANGED")
        self.save("start.json", {"started_at": stamp(), "freeze_sha256": digest((HERE / "FREEZE.json").read_bytes()),
                                "commit": self.command(["git", "-C", str(REPO), "rev-parse", "HEAD"]).stdout.decode().strip(),
                                "frozen_files": before, "actor_inference_calls": 0})
        self.adapter = load_module("fixed_adapter", HERE / "fixed_adapter.py")

        # Q03 is deliberately first. Missing/unknown effective prompt blocks workers.
        self.current = "Q03"
        raw = self.adapter.render_request_bytes()
        self.check(json.loads(raw) == {**json.loads(self.adapter.model_request_bytes()), "_debug_render_only": True}, "RENDER_REQUEST_NOT_EXACT_DEBUG_VARIANT")
        self.check([t["function"]["name"] for t in json.loads(raw)["tools"]] == ["read_packet_file", "write_result"], "TOOL_INVENTORY_NOT_EXACT_TWO")
        self.save_raw("Q03.request.json", raw)
        started = stamp()
        try:
            status, headers, response = self.adapter.observe_render_only()
        except Exception as error:
            self.save("Q03.http-failure.json", {"started_at": started, "ended_at": stamp(), "type": type(error).__name__, "detail": str(error)})
            raise Stop("PROVIDER_RENDER_OBSERVATION_FAILED") from error
        self.save_raw("Q03.response.json", response)
        self.save("Q03.http-receipt.json", {"started_at": started, "ended_at": stamp(), "url": self.adapter.ENDPOINT,
                  "status": status, "headers": headers, "request_sha256": digest(raw), "response_sha256": digest(response)})
        self.check(status == 200 and len(response) <= 1024 * 1024, "PROVIDER_RENDER_RESPONSE_INVALID")
        obj = json.loads(response)
        self.check("_debug_info" in obj and obj.get("message", {}).get("content", "") == ""
                   and not obj.get("message", {}).get("tool_calls"), "MISSING_RENDER_ARTIFACT_OR_INFERENCE_RESPONSE")
        prompt = obj["_debug_info"].get("rendered_template")
        self.check(isinstance(prompt, str), "MISSING_RENDERED_TEMPLATE")
        self.save_raw("Q03.rendered-prompt.txt", prompt.encode())
        segments = re.findall(r"<tools>(.*?)</tools>", prompt, flags=re.S)
        self.check(len(segments) == 1, "UNKNOWN_EFFECTIVE_TOOL_SECTION")
        actual_tools = [json.loads(line) for line in segments[0].strip().splitlines()]
        approved = json.loads(raw)["tools"]
        self.check(actual_tools == approved, "EFFECTIVE_TOOL_PROFILE_DRIFT")
        self.check(prompt.encode() == (HERE / "EXPECTED-Q03-PROMPT.txt").read_bytes(), "FULL_EFFECTIVE_CONTEXT_DRIFT")
        request = json.loads(raw)
        self.check(prompt.count("<|im_start|>system\n") == 1 and prompt.count("<|im_start|>user\n") == 1,
                   "UNEXPECTED_CONTEXT_ROLES")
        self.check(all(message["content"] in prompt for message in request["messages"]), "MISSING_CONTEXT")
        self.check(prompt.endswith("<|im_start|>assistant\n<think>\n\n</think>\n\n"), "UNKNOWN_ASSISTANT_PREFIX")
        self.check(not obj.get("remote_host") and not obj.get("remote_model") and not obj.get("eval_count")
                   and not obj.get("prompt_eval_count") and not obj.get("message", {}).get("thinking"), "UNEXPECTED_PROVIDER_MODE")
        self.pass_cell({"request_sha256": digest(raw), "rendered_prompt_sha256": digest(prompt.encode()),
                        "effective_tools": actual_tools, "observed_additions": "pinned qwen3.5 tool-format postamble and empty thinking prefix",
                        "scope": "live render-only prompt + exact client/dispatch source; not binary attestation or inference fitness"})

        self.current = "Q01"
        builder = load_module("pinned_packet_builder", PACKET_CODE / "prepare_packet.py")
        checker = load_module("code_isolated_checker", PACKET_CODE / "independent_packet_checker.py")
        source = self.output / "synthetic-source"
        shutil.copytree(HERE / "public-synthetic-source", source)
        outside = source / "outside-world-sentinel.txt"
        outside.write_bytes(b"PUBLIC-SYNTHETIC-OUTSIDE-WORLD-ONLY\n")
        packet = self.output / "packet"
        builder.prepare(HERE / "MANIFEST.json", source, packet)
        checked = checker.check(HERE / "MANIFEST.json", source, packet)
        prepared_receipt = json.loads((packet / "controller-receipts/PREPARE.json").read_bytes())
        manifest = json.loads((HERE / "MANIFEST.json").read_bytes())
        expected_allowlist = [{"path": e["path"], "sha256": e["sha256"], "bytes": len((source / e["path"]).read_bytes())} for e in manifest["files"]]
        self.check(prepared_receipt["allowlisted"] == expected_allowlist and prepared_receipt["total_bytes"] == sum(e["bytes"] for e in expected_allowlist), "PACKET_RECEIPT_CONTENT_DRIFT")
        self.save("Q01.packet-check.json", checked)
        sentinel = self.output / "external-controller-sentinel.txt"
        sentinel.write_bytes(b"PUBLIC-SYNTHETIC-CONTROLLER-ONLY\n")
        sentinel_before = digest(sentinel.read_bytes())
        outside_before = digest(outside.read_bytes())
        self.pass_cell({"new_packet": checked, "reused_scope": "same exact #175 packet-code/hash controls; 34/34 is preserved, not rerun",
                        "authorship": "code-isolated same-controller checker"})

        self.current = "Q02"
        weak = self.output / "weak-copy-all-packet"
        weak.mkdir()
        shutil.copytree(source, weak / "world")
        (weak / "scratch").mkdir()
        shutil.copytree(packet / "controller-receipts", weak / "controller-receipts")
        try:
            checker.check(HERE / "MANIFEST.json", source, weak)
        except checker.CheckFailure as error:
            self.save("Q02.weak-rejection.json", {"reason": error.reason, "detail": str(error),
                      "copied_outside_hash": digest((weak / "world/outside-world-sentinel.txt").read_bytes())})
            self.check(error.reason == "EXTRA_FILE", "WRONG_WEAK_BASELINE_REASON")
        else:
            raise Stop("WEAK_BASELINE_ACCEPTED")
        self.pass_cell("actual copy-all rejected EXTRA_FILE for existing synthetic outside-world bytes")

        self.current = "Q04"
        cid = self.create(packet / "world", "first")
        inspector = self.docker("inspect", cid)
        self.check(inspector.returncode == 0, "INSPECT_FAILED")
        config = json.loads(inspector.stdout)[0]
        hc, cc = config["HostConfig"], config["Config"]
        expected = {"ReadonlyRootfs": True, "Privileged": False, "NetworkMode": "none", "IpcMode": "none",
                    "PidsLimit": 64, "Memory": 268435456, "MemorySwap": 268435456, "NanoCpus": 1000000000, "CgroupnsMode": "private"}
        self.check(all(hc.get(k) == v for k, v in expected.items()), "EFFECTIVE_DOCKER_CONTROL_DRIFT")
        self.check(cc["User"] == "65532:65532" and cc["Env"] == self.pins["worker_config_env"], "USER_OR_ENV_DRIFT")
        self.check(hc.get("CapDrop") == ["ALL"] and any(s.startswith("no-new-privileges") for s in hc.get("SecurityOpt", [])), "PRIVILEGE_DRIFT")
        self.check(hc.get("PidMode", "") == "" and hc.get("UTSMode", "") == ""
                   and not hc.get("DeviceRequests") and not hc.get("ExtraHosts") and not hc.get("Links")
                   and not hc.get("VolumesFrom") and not hc.get("Dns") and not cc.get("Volumes"), "HOST_NAMESPACE_OR_EXTRA_SURFACE")
        self.check(hc.get("Tmpfs") == {"/scratch": "rw,noexec,nosuid,nodev,size=16m,uid=65532,gid=65532,mode=700"}, "SCRATCH_CONFIG_DRIFT")
        self.check(not hc.get("PortBindings") and not hc.get("Devices") and not hc.get("CapAdd") and not hc.get("Binds"), "UNEXPECTED_HOST_INTEGRATION")
        mounts = config["Mounts"]
        binds = [m for m in mounts if m["Type"] == "bind"]
        self.check(len(binds) == 1 and binds[0]["Destination"] == "/packet" and not binds[0]["RW"]
                   and Path(binds[0]["Source"]) == packet / "world" and binds[0]["Propagation"] == "rprivate", "MOUNT_APERTURE_DRIFT")
        self.check(all(m["Type"] == "bind" or (m["Type"] == "tmpfs" and m["Destination"] == "/scratch") for m in mounts), "UNKNOWN_MOUNT")
        self.check(config["Image"] == self.pins["image_id"], "IMAGE_ID_DRIFT")
        uid = self.probe(cid, "id", "-u")
        self.check(uid.returncode == 0 and uid.stdout.strip() == b"65532", "ACTUAL_UID_DRIFT")
        process = self.probe(cid, "cat", "/proc/self/status")
        self.check(process.returncode == 0 and b"CapEff:\t0000000000000000" in process.stdout and b"NoNewPrivs:\t1" in process.stdout, "ACTUAL_PRIVILEGE_DRIFT")
        mounts_observed = self.probe(cid, "cat", "/proc/self/mountinfo")
        self.check(mounts_observed.returncode == 0 and b" /scratch " in mounts_observed.stdout and b" /packet " in mounts_observed.stdout, "ACTUAL_MOUNTS_UNKNOWN")
        environment = self.probe(cid, "cat", "/proc/self/environ")
        self.check(environment.returncode == 0 and set(environment.stdout.rstrip(b"\0").split(b"\0")) == {b"PATH=/usr/local/bin:/usr/bin:/bin", b"HOME=/"}, "ACTUAL_ENV_DRIFT")
        python_version = self.docker("exec", cid, *CLEAN_ENV, PYTHON, "-I", "-B", "-c", "import json,platform,sys; print(json.dumps({'version':platform.python_version(),'implementation':platform.python_implementation(),'build':sys.version}))")
        self.check(python_version.returncode == 0 and json.loads(python_version.stdout)["version"] == self.pins["worker_python_version"] and json.loads(python_version.stdout)["implementation"] == "CPython", "WORKER_RUNTIME_DRIFT")
        initial_scratch = self.probe(cid, "ls", "-A", "/scratch")
        self.check(initial_scratch.returncode == 0 and initial_scratch.stdout == b"", "INITIAL_SCRATCH_NOT_EMPTY")
        self.pass_cell({"container_id": cid, "image_id": config["Image"], "inspect_sha256": digest(inspector.stdout), "effective": expected})
        adapter = self.adapter.FixedAdapter(cid, self.command)

        self.current = "Q05"
        for path in self.adapter.READS:
            raw_call = json.dumps({"function": {"index": 0, "name": "read_packet_file", "arguments": {"path": path}}}).encode()
            result = self.tool(adapter, raw_call, model=True)["result"]
            self.check(result["content"].encode() == (source / path).read_bytes(), "ALLOWED_BYTES_MISMATCH")
        self.pass_cell("both actual Ollama-to-dispatch read bindings returned exact controller-held bytes")

        self.current = "Q06"
        forbidden = ["/etc/passwd", "../data/marker.txt", "data/../data/marker.txt", "data//marker.txt", "DATA/marker.txt",
                     "data/marker.txt/", "outside-world-sentinel.txt", str(outside), str(sentinel),
                     "../controller-receipts/PREPARE.json", "/packet/../controller-receipts/PREPARE.json", "unknown.txt"]
        for path in forbidden:
            self.call(adapter, "read_packet_file", {"path": path}, "AUTHORIZATION_PATH_DENIED")
        self.pass_cell({"negative_requests": len(forbidden), "reason": "AUTHORIZATION_PATH_DENIED",
                        "meaningful_external_targets": "outside-world and controller sentinels exist; no filesystem exception used"})

        self.current = "Q07"
        for path in ["../answer.txt", "/scratch/answer.txt", "/packet/data/marker.txt", "/tmp/forbidden.txt", str(sentinel), "ANSWER.TXT"]:
            self.call(adapter, "write_result", {"path": path, "content": "PUBLIC-WRITE-CONTROL"}, "AUTHORIZATION_PATH_DENIED")
        self.call(adapter, "write_result", {"path": "answer.txt", "content": "x" * 4097}, "OUTPUT_BYTES_LIMIT")
        self.call(adapter, "write_result", {"path": "answer.txt", "content": "é" * 2049}, "OUTPUT_BYTES_LIMIT")
        result_bytes = (source / "data/marker.txt").read_bytes()
        self.tool(adapter, json.dumps({"function": {"name": "write_result", "arguments": {"path": "answer.txt", "content": result_bytes.decode()}}}).encode(), model=True)
        output_readback = self.probe(cid, "cat", "/scratch/answer.txt")
        self.check(output_readback.returncode == 0 and output_readback.stdout == result_bytes, "OUTPUT_BYTES_MISMATCH")
        # Exclusive creation must reject a second write and preserve first bytes.
        self.call(adapter, "write_result", {"path": "answer.txt", "content": "SHOULD-NOT-REPLACE"}, execution_refusal="WORKER_EXEC_FAILED")
        duplicate_error = json.loads((self.output / f"command-{self.serial:03}/stderr").read_bytes())
        self.check(duplicate_error == {"errno": 17, "errname": "EEXIST"}, "WRONG_EXCLUSIVE_WRITE_ERROR")
        readback = self.probe(cid, "cat", "/scratch/answer.txt")
        self.check(readback.returncode == 0 and readback.stdout == result_bytes, "OUTPUT_REPLACED")
        denied = self.probe(cid, "touch", "/packet/data/marker.txt")
        self.check(denied.returncode != 0 and json.loads(denied.stderr).get("errname") == "EROFS", "PACKET_WRITE_CONTROL_FAILED")
        denied = self.probe(cid, "touch", "/tmp/forbidden.txt")
        self.check(denied.returncode != 0 and json.loads(denied.stderr).get("errname") == "EROFS", "ROOT_WRITE_CONTROL_FAILED")
        self.check(digest(sentinel.read_bytes()) == sentinel_before and digest(outside.read_bytes()) == outside_before, "CONTROLLER_SENTINEL_CHANGED")
        checker.check(HERE / "MANIFEST.json", source, packet)
        self.pass_cell("scratch bytes independently observed; actual read-only mount/root refusals; source/world/controller bytes unchanged")

        self.current = "Q08"
        network = self.probe(cid, "network")
        self.check(network.returncode == 0, "Q08_INSTRUMENTATION_FAILURE_NO_DENIAL_INFERRED")
        try:
            observation = json.loads(network.stdout.splitlines()[-1])
            positive = observation["positive"]
            egress = observation["synthetic_egress"]
        except (ValueError, KeyError, IndexError) as error:
            raise Stop("Q08_INSTRUMENTATION_OUTPUT_INVALID") from error
        self.save("Q08.network-observation.json", observation)
        self.check(positive["attempted"] and positive["errno"] == 0 and positive["errname"] == "SUCCESS"
                   and positive["received"] == "CAL-PUBLIC-SYNTHETIC-SOCKET-CONTROL\n"
                   and positive["destination"][0] == "127.0.0.1" and 1024 < positive["destination"][1] <= 65535 and positive["destination"][1] != 11434, "Q08_POSITIVE_ABILITY_FAILED")
        for key, destination, code, name in [("synthetic_egress", ["192.0.2.1", 9], 101, "ENETUNREACH"),
                                            ("controller_loopback_boundary", ["127.0.0.1", 11434], 111, "ECONNREFUSED")]:
            self.check(key in observation, "Q08_INSTRUMENTATION_OUTPUT_MISSING")
            item = observation[key]
            self.check(item["attempted"] and item["syscall"] == "connect_ex" and item["destination"] == destination,
                       "Q08_NO_ACTUAL_FIXED_CONNECTION_ATTEMPT")
            self.check(item["errno"] != 0, "Q08_ISOLATION_FAILURE_CONNECTION_SUCCEEDED")
            self.check(item["errno"] == code and item["errname"] == name, "Q08_ISOLATION_UNKNOWN_WRONG_KERNEL_ERROR")
        try:
            link_result = network_state_validator.validate(observation)
        except network_state_validator.NetworkShapeError as error:
            self.save("Q08.link-shape-first-failure.json",
                      {"reason": error.reason, "scope": "unqualified network state"})
            raise Stop("Q08_NETWORK_CONFIG_DRIFT:" + error.reason) from error
        self.save("Q08.link-validation.json", link_result)
        for path in ("/var/run/docker.sock", "/controller", str(sentinel)):
            self.check(self.probe(cid, "test", "-e", path).returncode == 1, "HOST_SURFACE_PRESENT")
        self.pass_cell({"observation": "Q08.network-observation.json",
                        "link_validation": "Q08.link-validation.json",
                        "scope": "same-worker positive/negative kernel sockets plus actual inert link flags/state and loopback-only routes; not arbitrary egress audit"})

        self.current = "Q09"
        controls = json.loads((HERE / "DISPATCH-CONTROLS.json").read_bytes())
        for control in controls:
            self.tool(adapter, control["raw"].encode(), control["expected"], control["model"])
        self.tool(adapter, b"\xff", "MALFORMED_JSON")
        self.tool(adapter, b" " * 16385, "MALFORMED_ENVELOPE_SIZE")
        # Plausible weak decoder: JSON last-key-wins would dispatch an allowed
        # read from an explicitly duplicate envelope. Only a recording sink is
        # used; no host process or worker command is available to this baseline.
        weak_calls = []
        duplicate = next(c for c in controls if c["id"] == "duplicate-name")
        weak = json.loads(duplicate["raw"])
        if weak["name"] == "read_packet_file":
            weak_calls.append([weak["name"], weak["arguments"]])
        self.save("Q09.weak-dispatcher.json", {"input": duplicate, "would_dispatch": weak_calls, "real_processes": 0})
        self.check(len(weak_calls) == 1, "WEAK_DISPATCHER_CONTROL_NOT_SENSITIVE")
        self.pass_cell({"frozen_negative_controls": len(controls) + 2, "invariant": "every refusal preserves actual command serial", "weak_baseline": "last-key-wins decoder reaches recording sink"})

        self.current = "Q10"
        fresh = self.create(packet / "world", "fresh")
        self.check(fresh != cid, "CONTAINER_ID_REUSED")
        listing = self.probe(fresh, "ls", "-A", "/scratch")
        self.check(listing.returncode == 0 and listing.stdout == b"", "FRESH_SCRATCH_FAILED")
        fresh_inspect = self.docker("inspect", fresh)
        self.check(fresh_inspect.returncode == 0, "FRESH_INSPECT_FAILED")
        fresh_config = json.loads(fresh_inspect.stdout)[0]
        self.check(fresh_config["Image"] == config["Image"] and fresh_config["HostConfig"] == config["HostConfig"]
                   and {k: v for k, v in fresh_config["Config"].items() if k != "Labels"} == {k: v for k, v in config["Config"].items() if k != "Labels"}, "FRESH_PROFILE_DRIFT")
        self.check(self.probe(fresh, "test", "-e", "/scratch/answer.txt").returncode == 1, "SCRATCH_MARKER_REUSED")
        self.check(json.loads(self.adapter.model_request_bytes())["messages"] == json.loads(raw)["messages"], "REQUEST_HISTORY_DRIFT")
        fresh_readback = self.probe(fresh, "cat", "/packet/data/marker.txt")
        self.check(fresh_readback.returncode == 0 and fresh_readback.stdout == result_bytes, "FRESH_PACKET_DRIFT")
        self.pass_cell({"fresh_container_id": fresh, "scope": "fresh worker + exact request/rendered context only",
                        "provider_internal_cache_or_host_permission_isolation": "not claimed; existing inference service is controller trusted machinery"})

        self.current = "Q11"
        self.check(not sentinel.is_relative_to(packet / "world") and (packet / "world") not in self.output.parents,
                   "RECEIPT_APERTURE_INVALID")
        self.check(digest(sentinel.read_bytes()) == sentinel_before, "RECEIPT_SENTINEL_DRIFT")
        self.receipt_required = {"Q03.request.json", "Q03.response.json", "Q03.http-receipt.json", "Q03.rendered-prompt.txt",
                                 "Q01.packet-check.json", "Q02.weak-rejection.json", "Q08.network-observation.json", "Q08.link-validation.json", "Q09.weak-dispatcher.json", "OWNED-RESOURCES.json", "start.json", "OPERATOR-REVIEW.json"}
        self.pass_cell(self.audit_receipts("Q11"))

        self.current = "Q12"
        self.cleanup()
        self.pass_cell("both owned containers removed and removal observed; existing service/G89/unrelated resources untouched")

        self.current = "Q13"
        # Review does not authorize an actual model pilot or invent independent authorship.
        CELLS["Q13"] = {"status": "PENDING_EXPLICIT_OWNER_ADMISSION_REVIEW", "actor_launch_authorized": False}
        self.check(inventory() == before and digest((HERE / "FREEZE.json").read_bytes()) == self.freeze_sha256, "POSTRUN_FROZEN_BYTES_CHANGED")
        check_local(self.pins)
        self.audit_receipts("FINAL-CUSTODY")

    def audit_receipts(self, label):
        entries = {str(p.relative_to(self.output)): {"sha256": digest(p.read_bytes()), "bytes": p.stat().st_size}
                   for p in sorted(self.output.rglob("*")) if p.is_file()}
        self.check(getattr(self, "receipt_required", set()) <= set(entries), "MISSING_REQUIRED_RECEIPTS")
        self.check(all(entries.get(name) == record for name, record in self.artifacts.items()), "SAVED_ARTIFACT_CONTENT_DRIFT")
        checked = receipt_check.check(self.output, entries, self.commands, self.tools, self.started_at, stamp())
        if label == "Q11":
            # A weak inventory-only checker would miss content corruption. The
            # frozen negative control alters only an in-memory expected digest.
            corrupt = {k: dict(v) for k, v in entries.items()}
            corrupt["Q03.request.json"]["sha256"] = "0" * 64
            try:
                receipt_check.check(self.output, corrupt, self.commands, self.tools, self.started_at, stamp())
            except ValueError as error:
                self.check(str(error) == "RECEIPT_BYTES_MISMATCH:Q03.request.json", "WRONG_CUSTODY_NEGATIVE_REASON")
            else:
                raise Stop("CUSTODY_CHECKER_ACCEPTED_WRONG_HASH")
        self.save(label + ".inventory.json", entries)
        # Read the inventory back; it must retain the original ledger exactly.
        self.check(json.loads((self.output / (label + ".inventory.json")).read_bytes()) == entries, "INDEX_WRITE_DRIFT")
        self.save(label + ".audit.json", checked)
        return checked

    def cleanup(self):
        errors = []
        for cid in list(self.owned):
            if cid in self.cleanup_attempted:
                errors.append({"container_id": cid, "reason": "NO_RETRY_OF_FAILED_CLEANUP"})
                continue
            self.cleanup_attempted.add(cid)
            try:
                observed = self.docker("inspect", cid)
                self.check(observed.returncode == 0, "OWNED_RESOURCE_IDENTITY_UNKNOWN")
                obj = json.loads(observed.stdout)[0]
                expected = self.resources[cid]
                self.check(obj["Id"] == cid and obj["Name"] == "/" + expected["name"]
                           and obj["Config"]["Labels"].get("cal.qualification.owner") == expected["name"], "OWNERSHIP_DRIFT")
                removed = self.docker("rm", "-f", cid)
                self.check(removed.returncode == 0, "OWNED_TEARDOWN_FAILED")
                absent = self.docker("inspect", cid)
                listing = self.docker("ps", "-a", "--no-trunc", "--format", "{{.ID}}")
                ids = listing.stdout.decode().splitlines()
                self.check(listing.returncode == 0 and all(re.fullmatch(r"[a-f0-9]{64}", x) for x in ids), "RESOURCE_INVENTORY_UNKNOWN")
                self.check(absent.returncode != 0 and absent.returncode != 124 and cid not in ids, "REMOVAL_NOT_OBSERVED")
                self.owned.remove(cid)
                self.resources[cid]["removed"] = True
                self.resources[cid]["absence_observed_at"] = stamp()
                self.save("OWNED-RESOURCES.json", self.resources)
            except Exception as error:
                errors.append({"container_id": cid, "type": type(error).__name__, "reason": str(error)})
        if errors:
            self.save("CLEANUP-ERRORS.json", errors)
            raise Stop("OWNED_CLEANUP_INCOMPLETE")

    def finish(self):
        try:
            self.run()
        except Exception as error:
            self.first_failure = {"cell": self.current, "type": type(error).__name__, "reason": str(error), "at": stamp()}
            self.save("FIRST-FAILURE.json", self.first_failure)
            self.save_raw("FIRST-FAILURE.traceback.txt", traceback.format_exc().encode())
            if self.current in CELLS:
                CELLS[self.current] = {"status": "FAIL_OR_UNKNOWN", "first_failure": self.first_failure}
            CELLS["Q13"] = {"status": "BLOCKED", "reason": "Required first failure/unknown; actor admission not justified"}
            try:
                self.cleanup()
                if CELLS["Q12"]["status"] == "NOT_RUN":
                    CELLS["Q12"] = {"status": "OWNED_CLEANUP_ONLY", "fresh_reset": CELLS["Q10"]["status"]}
            except Exception as cleanup_error:
                self.save("CLEANUP-FAILURE.json", {"type": type(cleanup_error).__name__, "reason": str(cleanup_error)})
        result = {"finished_at": stamp(), "status": "BLOCKED_FIRST_FAILURE" if self.first_failure else "PASS_BOUNDED_ZERO_MODEL_CONTROLS",
                  "actor_admission": "BLOCKED" if self.first_failure else "PENDING_EXPLICIT_OWNER_ADMISSION_REVIEW",
                  "actor_inference_calls": 0, "cells": CELLS, "first_failure": self.first_failure,
                  "authorship": "same-controller source-informed implementation and external observation; no blind independent review"}
        self.save("PROCESS-EVENTS.json", self.process_events)
        self.save("RESULT.json", result)
        entries = {str(p.relative_to(self.output)): {"sha256": digest(p.read_bytes()), "bytes": p.stat().st_size}
                   for p in sorted(self.output.rglob("*")) if p.is_file()}
        self.save("RECEIPT-INDEX.json", entries)
        # Terminal index excludes itself; verify the stored index and every byte
        # it names. Its SHA is printed for external custody, not self-hashed.
        try:
            self.check(json.loads((self.output / "RECEIPT-INDEX.json").read_bytes()) == entries, "FINAL_INDEX_DRIFT")
            for name, record in entries.items():
                content = (self.output / name).read_bytes()
                self.check(len(content) == record["bytes"] and digest(content) == record["sha256"], "FINAL_RECEIPT_DRIFT")
        except Exception as error:
            # Never publish an unqualified successful return on a terminal I/O
            # failure. Preserve the earlier checkpoint/index as failed evidence.
            print("TERMINAL_CUSTODY_FAILURE:" + str(error), file=sys.stderr)
            return 1
        result["terminal_receipt_index_sha256"] = digest((self.output / "RECEIPT-INDEX.json").read_bytes())
        print(json.dumps(result, sort_keys=True, indent=2))
        return 1 if self.first_failure else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--candidate-commit", required=True)
    parser.add_argument("--freeze-sha256", required=True)
    parser.add_argument("--operator-review", type=Path, required=True)
    parser.add_argument("--pins-path", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(Controller(args.output, args.candidate_commit, args.freeze_sha256, args.operator_review, args.pins_path).finish())
