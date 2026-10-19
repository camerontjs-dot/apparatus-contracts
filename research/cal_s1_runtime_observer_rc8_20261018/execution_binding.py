"""RC8 source candidate: fixed Docker invocation, external raw receipts.

NOT LIVE-QUALIFIED. There is no host-Python fallback and no model endpoint.
The default gate refuses before executable inspection or any subprocess.
Container/host control remains trusted. Candidate output is always untrusted.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
import hashlib
import importlib.util
import json
import os
import platform
import sys
from pathlib import Path
import re
import selectors
import signal
import stat
import subprocess
import time
import uuid

HERE = Path(__file__).resolve().parent
RC4 = HERE.parent / "cal_fixed_ollama_launcher_rc4_20261010"
MAX_OUTPUT = 65536
MAX_INPUT = 16384
MAX_CANDIDATE = 32768
PACKAGER_ROOT = HERE.parent / "cal_context_free_packet_macos_rc1_20261009" / "candidate"
REUSED = {
    "worker_control.py": "2938f75974b76b4aad87bbd28dd6754d2b10f246",
    "network_state_validator.py": "b2415f0a59ecd7b50e7c9ea82f3a4679f7a9307a",
}
# This is a fixed protocol wrapper, not model-selected code or a host evaluator.
# Correct output demonstrates black-box behavior, not a trusted internal trace.
GUEST = '''import importlib.util,json,sys
request=json.loads(sys.stdin.buffer.read())
if type(request) is not dict or set(request)!={"claim","evidence"}:raise ValueError("INPUT")
sys.path.insert(0,"/packet/input/baseline")
spec=importlib.util.spec_from_file_location("candidate","/candidate/candidate.py")
module=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=module
spec.loader.exec_module(module)
answer=module.analyze(request["claim"],request["evidence"])
sys.stdout.write(json.dumps(answer,ensure_ascii=True,allow_nan=False,separators=(",",":"))+"\\n")
'''
CLEAN = ["/usr/bin/env", "-i", "PATH=/usr/local/bin:/usr/bin:/bin", "HOME=/"]


class BoundaryError(RuntimeError):
    pass


def require(value: bool, reason: str) -> None:
    if not value:
        raise BoundaryError(reason)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\x00" + data).hexdigest()


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=True,
                      separators=(",", ":"), allow_nan=False).encode()


def decode(data: bytes, limit: int = MAX_OUTPUT):
    require(type(data) is bytes and len(data) <= limit, "RAW_BYTES_LIMIT")
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "DUPLICATE_JSON_KEY")
            result[key] = value
        return result
    def constant(_):
        raise BoundaryError("NONFINITE_JSON")
    try:
        return json.loads(data.decode("utf-8"), object_pairs_hook=unique,
                          parse_constant=constant)
    except (ValueError, UnicodeError, RecursionError) as error:
        raise BoundaryError("INVALID_JSON") from error


def regular_bytes(path: Path, limit: int) -> bytes:
    require(not path.is_symlink(), "SYMLINK")
    st = path.lstat()
    require(stat.S_ISREG(st.st_mode) and st.st_nlink == 1, "NONREGULAR_OR_LINK")
    require(st.st_size <= limit, "FILE_BYTES_LIMIT")
    data = path.read_bytes()
    after = path.lstat()
    require((st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns) ==
            (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns), "FILE_CHANGED")
    require(len(data) <= limit, "FILE_BYTES_LIMIT")
    return data


def retained_module(name: str, path: Path, expected_blob: str):
    require(git_blob(path.read_bytes()) == expected_blob, "DEPENDENCY_DRIFT:" + name)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def packet_tools():
    packager = retained_module("rc8_retained_packager", PACKAGER_ROOT / "prepare_packet.py",
                               "473c5382ff9b11d9c9c364c57f58bcc4a10ad472")
    checker = retained_module("rc8_retained_packet_checker", PACKAGER_ROOT / "independent_packet_checker.py",
                              "26ed7584504cd19b176df4bb934fbffd18c9ed60")
    return packager, checker


def verify_packet_files(packet: Path, expected: dict):
    require(type(expected) is dict and len(expected) == 7, "PACKET_SEVEN_FILES")
    packager, _ = packet_tools()
    found = packager.collect_files(packet, set(expected))
    require(set(found) == set(expected), "PACKET_FILE_SET")
    require(all(sha(data) == expected[name] for name, data in found.items()), "PACKET_BYTES_DRIFT")


def stage_synthetic_packet(trial: Path):
    """Reuse #175 exactly; no container or process is involved in this function."""
    source = trial / "source"
    source.mkdir(mode=0o700)
    files = {}
    for i in range(7):
        name = f"public_{i}.txt"
        data = f"SYNTHETIC FILE {i}\n".encode()
        (source / name).write_bytes(data)
        files[name] = sha(data)
    manifest = trial / "packet-manifest.json"
    manifest.write_bytes(canonical({"schema": "cal-context-free-packet-rc0", "experiment_id": "rc8-" + trial.name,
                                  "files": [{"path": k, "sha256": v} for k, v in sorted(files.items())]}))
    packager, checker = packet_tools()
    prepared = trial / "packet-layout"
    packager.prepare(manifest, source, prepared)
    packager.verify(manifest, prepared)
    checker.check(manifest, source, prepared)
    return prepared / "world", files


@dataclass(frozen=True)
class Approval:
    """Trusted operator inputs, NOT authentication of a support decision.

    An operator must verify the actual attributable platform response externally.
    A boolean, issue comment, signature-shaped string or passing test is not one.
    """
    platform_resolution_ref: str | None = None
    platform_response_sha256: str | None = None
    exact_source_manifest_sha256: str | None = None
    reviewed_run_ref: str | None = None
    scope: str = "NOT_APPROVED"
    runtime_pins_sha256: str | None = None

    def check(self, source_manifest_sha256: str) -> None:
        require(self.scope == "RC8_PUBLIC_SYNTHETIC_EXECUTION_ONLY", "LIVE_SCOPE_NOT_APPROVED")
        require(type(self.platform_resolution_ref) is str and
                bool(self.platform_resolution_ref.strip()), "PLATFORM_RESOLUTION_MISSING")
        require(type(self.platform_response_sha256) is str and
                re.fullmatch(r"[a-f0-9]{64}", self.platform_response_sha256) is not None,
                "PLATFORM_RESPONSE_IDENTITY_MISSING")
        require(type(self.reviewed_run_ref) is str and bool(self.reviewed_run_ref.strip()),
                "EXACT_RUN_REVIEW_MISSING")
        require(self.exact_source_manifest_sha256 == source_manifest_sha256,
                "REVIEWED_SOURCE_MISMATCH")


    def check_runtime(self, pins) -> None:
        require(type(self.runtime_pins_sha256) is str and
                re.fullmatch(r"[a-f0-9]{64}", self.runtime_pins_sha256) is not None and
                self.runtime_pins_sha256 == sha(canonical(asdict(pins))), "REVIEWED_RUNTIME_PINS_MISMATCH")


@dataclass(frozen=True)
class Pins:
    docker: str
    docker_sha256: str
    image: str
    context: str = "desktop-linux"
    architecture: str = "arm64"
    engine_version: str = "MISSING"
    controller_python_version: str = "MISSING"
    controller_executable_sha256: str = "MISSING"

    def validate_shape(self):
        require(Path(self.docker).is_absolute(), "DOCKER_PATH_NOT_ABSOLUTE")
        require(re.fullmatch(r"[a-f0-9]{64}", self.docker_sha256) is not None, "DOCKER_PIN")
        require(re.fullmatch(r"sha256:[a-f0-9]{64}", self.image) is not None, "IMAGE_PIN")
        require(self.context == "desktop-linux" and self.architecture == "arm64", "RUNTIME_PROFILE")
        require(re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", self.engine_version) is not None and
                re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", self.controller_python_version) is not None and
                re.fullmatch(r"[a-f0-9]{64}", self.controller_executable_sha256) is not None, "FULL_RUNTIME_PINS_REQUIRED")


@dataclass(frozen=True)
class Capture:
    returncode: int
    stdout: bytes
    stderr: bytes
    started_ns: int
    ended_ns: int
    pid: int
    stdin_complete: bool = True


class CommandCapture:
    """Actual bounded binary subprocess capture. Source-tested; not run here."""
    def __init__(self, root: Path):
        root.mkdir(mode=0o700, parents=False, exist_ok=False)
        self.root = root
        self.serial = 0

    def run(self, argv: list[str], data: bytes = b"", timeout: float = 15.0) -> Capture:
        require(type(data) is bytes and len(data) <= MAX_INPUT, "STDIN_LIMIT")
        self.serial += 1
        slot = self.root / f"command-{self.serial:04d}"
        slot.mkdir(mode=0o700)
        started = time.time_ns()
        out, err = bytearray(), bytearray()
        process = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, shell=False, close_fds=True,
                                   start_new_session=True,
                                   env={"PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": str(Path.home()),
                                        "LANG": "C", "LC_ALL": "C"})
        sel = selectors.DefaultSelector()
        failure = None
        bytes_sent = 0
        stdin_complete = True
        try:
            for stream, tag in ((process.stdout, "out"), (process.stderr, "err")):
                os.set_blocking(stream.fileno(), False)
                sel.register(stream, selectors.EVENT_READ, tag)
            os.set_blocking(process.stdin.fileno(), False)
            pending = memoryview(data)
            if pending:
                sel.register(process.stdin, selectors.EVENT_WRITE, "in")
            else:
                process.stdin.close()
            deadline = time.monotonic() + timeout
            while sel.get_map():
                require(time.monotonic() < deadline, "PROCESS_TIMEOUT")
                for key, _ in sel.select(timeout=0.05):
                    if key.data == "in":
                        try:
                            n = os.write(key.fileobj.fileno(), pending[:4096])
                            pending = pending[n:]
                            bytes_sent += n
                        except BrokenPipeError:
                            stdin_complete = False
                            pending = pending[len(pending):]
                        if not pending:
                            sel.unregister(key.fileobj)
                            key.fileobj.close()
                    else:
                        chunk = os.read(key.fileobj.fileno(), 4096)
                        if not chunk:
                            sel.unregister(key.fileobj)
                            key.fileobj.close()
                        else:
                            target = out if key.data == "out" else err
                            target.extend(chunk)
                            require(len(out) + len(err) <= MAX_OUTPUT, "PROCESS_OUTPUT_LIMIT")
            code = process.wait(timeout=max(0.001, deadline - time.monotonic()))
        except BaseException as error:
            failure = type(error).__name__ + ":" + str(error)
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGKILL)
            process.wait(timeout=5)
            code = process.returncode
            raise
        finally:
            sel.close()
            for stream in (process.stdin, process.stdout, process.stderr):
                if stream and not stream.closed:
                    stream.close()
            record = {"argv": argv, "stdin_sha256": sha(data), "stdout_sha256": sha(bytes(out)),
                      "stderr_sha256": sha(bytes(err)), "started_ns": started,
                      "ended_ns": time.time_ns(), "pid": process.pid,
                      "returncode": process.returncode, "failure": failure,
                      "stdin_bytes_sent": bytes_sent, "stdin_complete": stdin_complete and bytes_sent == len(data)}
            for name, content in (("stdin.bin", data), ("stdout.bin", bytes(out)),
                                  ("stderr.bin", bytes(err)), ("command.json", canonical(record))):
                with (slot / name).open("xb") as stream:
                    stream.write(content)
        return Capture(code, bytes(out), bytes(err), started, time.time_ns(), process.pid, stdin_complete and bytes_sent == len(data))


def create_arguments(pins: Pins, packet: Path, candidate: Path, name: str) -> list[str]:
    pins.validate_shape()
    require(re.fullmatch(r"cal-rc8-[a-f0-9]{32}", name) is not None, "WORKER_NAME")
    require(all(p.is_absolute() and "," not in str(p) for p in (packet, candidate)), "MOUNT_PATH")
    return [pins.docker, "--context", pins.context, "create", "--pull", "never",
            "--platform", "linux/arm64", "--name", name, "--label", "cal.rc8.owner=" + name,
            "--user", "65532:65532", "--read-only", "--cap-drop", "ALL",
            "--security-opt", "no-new-privileges", "--network", "none", "--ipc", "none",
            "--cgroupns", "private", "--pids-limit", "64", "--memory", "256m",
            "--memory-swap", "256m", "--cpus", "1", "--no-healthcheck", "--log-driver", "none",
            "--mount", f"type=bind,source={packet},target=/packet,readonly,bind-recursive=disabled,bind-propagation=rprivate",
            "--mount", f"type=bind,source={candidate},target=/candidate/candidate.py,readonly,bind-propagation=rprivate",
            "--tmpfs", "/scratch:rw,noexec,nosuid,nodev,size=16m,uid=65532,gid=65532,mode=700",
            "--entrypoint", "/usr/bin/env", pins.image, "-i", "PATH=/usr/local/bin:/usr/bin:/bin",
            "HOME=/", "/usr/local/bin/python3", "-I", "-B", "-c", "import time; time.sleep(300)"]


def check_config(info: dict, pins: Pins, packet: Path, candidate: Path, cid: str, name: str):
    h, c = info["HostConfig"], info["Config"]
    checks = {
        "identity": info["Id"] == cid and info["Image"] == pins.image,
        "owner": (c.get("Labels") or {}).get("cal.rc8.owner") == name,
        "uid": c["User"] == "65532:65532", "readonly": h["ReadonlyRootfs"] is True,
        "network": h["NetworkMode"] == "none", "privileged": h["Privileged"] is False,
        "caps": set(h.get("CapDrop") or []) == {"ALL"} and not h.get("CapAdd"),
        "privilege_escalation": h.get("SecurityOpt") == ["no-new-privileges"],
        "namespaces": h["IpcMode"] == "none" and h["CgroupnsMode"] == "private" and not h.get("PidMode"),
        "limits": h["Memory"] == h["MemorySwap"] == 268435456 and h["NanoCpus"] == 1000000000 and h["PidsLimit"] == 64,
        "ports": not h.get("PortBindings") and h.get("PublishAllPorts") is False,
        "devices": not h.get("Devices") and not h.get("DeviceRequests"),
        "mounts": False,
        "scratch": (h.get("Tmpfs") or {}) == {"/scratch": "rw,noexec,nosuid,nodev,size=16m,uid=65532,gid=65532,mode=700"},
    }
    mounts = [m for m in info["Mounts"] if m["Type"] != "tmpfs"]
    expected = {"/packet": str(packet), "/candidate/candidate.py": str(candidate)}
    checks["mounts"] = (len(mounts) == 2 and {m["Destination"] for m in mounts} == set(expected)
        and all(m["Type"] == "bind" and m["RW"] is False and m["Source"] == expected[m["Destination"]] for m in mounts)
        and all(m["Type"] == "bind" or (m["Type"] == "tmpfs" and m["Destination"] == "/scratch") for m in info["Mounts"]))
    require(all(checks.values()), "EFFECTIVE_CONFIG:" + ",".join(k for k, v in checks.items() if not v))
    return checks


class DockerCaseRuntime:
    """Each invocation gets a fresh worker. No candidate-authored observation API."""
    def __init__(self, pins: Pins, packet: Path, candidate: Path, commands: CommandCapture,
                 approval: Approval, source_manifest_sha256: str, packet_files: dict | None = None):
        approval.check(source_manifest_sha256)  # MUST precede all live inspection.
        approval.check_runtime(pins)
        pins.validate_shape()
        require(platform.python_version() == pins.controller_python_version and
                sha(Path(sys.executable).read_bytes()) == pins.controller_executable_sha256, "CONTROLLER_IDENTITY_DRIFT")
        require(sha(Path(pins.docker).read_bytes()) == pins.docker_sha256, "DOCKER_EXECUTABLE_DRIFT")
        require(packet.resolve() == packet and packet.is_dir(), "PACKET_ROOT")
        require(candidate.resolve() == candidate, "CANDIDATE_PATH")
        self.pins, self.packet, self.candidate, self.commands = pins, packet, candidate, commands
        self.candidate_sha256 = sha(regular_bytes(candidate, MAX_CANDIDATE))
        self.packet_files = dict(packet_files or {})
        verify_packet_files(packet, self.packet_files)
        self.seen_ids: set[str] = set()
        engine = self._cmd("version", "--format", "{{.Server.Version}}")
        require(engine.returncode == 0 and engine.stdout.decode("ascii").strip() == pins.engine_version, "ENGINE_IDENTITY_DRIFT")
        image = self._cmd("image", "inspect", pins.image)
        require(image.returncode == 0, "IMAGE_INSPECTION_FAILED")
        identity = decode(image.stdout)[0]
        require(identity["Id"] == pins.image and identity["Architecture"] == pins.architecture and identity["Os"] == "linux", "IMAGE_IDENTITY_DRIFT")
        for filename, digest in REUSED.items():
            require(git_blob((RC4 / filename).read_bytes()) == digest, "RC4_DEPENDENCY_DRIFT")
        spec = importlib.util.spec_from_file_location("rc8_retained_network_validator", RC4 / "network_state_validator.py")
        self.network_validator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.network_validator)

    def _cmd(self, *args, data=b"", timeout=15):
        return self.commands.run([self.pins.docker, "--context", self.pins.context, *args], data, timeout)

    def invoke(self, request: bytes) -> dict:
        require(len(request) <= MAX_INPUT, "CASE_INPUT_LIMIT")
        verify_packet_files(self.packet, self.packet_files)
        require(sha(regular_bytes(self.candidate, MAX_CANDIDATE)) == self.candidate_sha256, "CANDIDATE_DRIFT")
        name = "cal-rc8-" + uuid.uuid4().hex
        cid = None
        result = None
        cleanup = None
        primary = None
        owned = False
        cleanup_error = None
        try:
            made = self.commands.run(create_arguments(self.pins, self.packet, self.candidate, name))
            require(made.returncode == 0, "WORKER_CREATE_FAILED")
            cid = made.stdout.decode("ascii").strip()
            require(re.fullmatch(r"[a-f0-9]{64}", cid) is not None and cid not in self.seen_ids, "WORKER_ID_INVALID_OR_REUSED")
            self.seen_ids.add(cid)
            inspected = self._cmd("inspect", cid)
            require(inspected.returncode == 0, "INSPECT_FAILED")
            info = decode(inspected.stdout)[0]
            owned = info.get("Id") == cid and (info.get("Config", {}).get("Labels") or {}).get("cal.rc8.owner") == name
            checks = check_config(info, self.pins, self.packet, self.candidate, cid, name)
            require(self._cmd("start", cid).returncode == 0, "WORKER_START_FAILED")
            probe = self._cmd("exec", cid, *CLEAN, "/usr/local/bin/python3", "-I", "-B", "-c",
                              (RC4 / "worker_control.py").read_text(), "network", timeout=10)
            require(probe.returncode == 0, "NETWORK_PROBE_FAILED")
            observation = decode(probe.stdout.splitlines()[-1])
            network = self.network_validator.validate(observation)
            require(observation["positive"]["errno"] == 0 and
                    observation["positive"]["received"] == "CAL-PUBLIC-SYNTHETIC-SOCKET-CONTROL\n" and
                    observation["synthetic_egress"]["errno"] == 101 and
                    observation["controller_loopback_boundary"]["errno"] == 111, "NETWORK_SOCKET_CONTROL")
            captured = self._cmd("exec", "-i", cid, *CLEAN, "/usr/local/bin/python3", "-I", "-B", "-c", GUEST,
                                 data=request, timeout=10)
            require(captured.stdin_complete, "CASE_INPUT_NOT_FULLY_SENT")
            result = {"capture": captured, "worker_id": cid, "config_checks": checks,
                      "network": network, "candidate_sha256": self.candidate_sha256,
                      "input_sha256": sha(request), "layer": "HOST_CAPTURED_DOCKER_INVOCATION"}
        except BaseException as error:
            primary = error
        finally:
            if owned and cid and re.fullmatch(r"[a-f0-9]{64}", cid):
                try:
                    removed = self._cmd("rm", "-f", cid)
                    listing = self._cmd("ps", "-aq", "--no-trunc")
                    cleanup = removed.returncode == 0 and listing.returncode == 0 and cid not in listing.stdout.decode().splitlines()
                except BaseException as error:
                    cleanup_error = type(error).__name__ + ":" + str(error)
                    cleanup = False
            elif cid is None:
                cleanup = True  # no returned owned worker; retain primary creation error
        if primary is not None:
            primary.add_note("owned_cleanup_confirmed=" + str(cleanup) + ";cleanup_error=" + str(cleanup_error))
            raise primary
        require(cleanup is True, "OWNED_CLEANUP_UNCONFIRMED")
        require(sha(regular_bytes(self.candidate, MAX_CANDIDATE)) == self.candidate_sha256, "CANDIDATE_CHANGED_DURING_RUN")
        verify_packet_files(self.packet, self.packet_files)
        result["cleanup_confirmed"] = cleanup
        return result
