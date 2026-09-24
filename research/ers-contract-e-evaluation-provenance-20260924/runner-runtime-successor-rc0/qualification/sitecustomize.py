"""Audit guard loaded before the runner for harmless --help qualification."""
from __future__ import annotations

import atexit
import importlib.util
import json
import os
import sys
from pathlib import Path

_ALLOWED = ("jsonschema", "rfc8785", "cryptography")
_FORBIDDEN = (
    "contract_e", "contract_d", "decision_engine", "cal_pipeline",
    "pipeline_slices", "qualification_supervisor", "provenance_profile",
)
_PROCESS_EVENTS = {
    "subprocess.Popen", "os.system", "os.exec", "os.fork",
    "os.posix_spawn", "os.spawn",
}
_NETWORK_EVENTS = {
    "socket.connect", "socket.connect_ex", "socket.getaddrinfo",
    "socket.getnameinfo", "socket.bind", "socket.sendto",
}
_MUTATION_EVENTS = {
    "os.mkdir", "os.remove", "os.rmdir", "os.rename", "os.replace",
    "os.link", "os.symlink", "os.chmod", "os.chown", "os.truncate",
}
_LOG = Path(os.environ["CAL_GUARD_LOG"]).resolve()
_EVENTS = {
    "candidate_import_requests": [],
    "forbidden_import_attempts": [],
    "process_attempts": [],
    "network_attempts": [],
    "filesystem_mutation_attempts": [],
    "dynamic_source_load_attempts": [],
}


def _is_allowed_log(path: object) -> bool:
    try:
        return Path(os.fsdecode(path)).resolve() == _LOG
    except (TypeError, ValueError, OSError):
        return False


def _audit(event: str, args: tuple) -> None:
    if event == "import" and args:
        name = str(args[0])
        if any(name == prefix or name.startswith(prefix + ".") for prefix in _ALLOWED):
            _EVENTS["candidate_import_requests"].append(name)
        if any(name == prefix or name.startswith(prefix + ".") for prefix in _FORBIDDEN):
            _EVENTS["forbidden_import_attempts"].append(name)
            raise PermissionError("blocked_forbidden_scientific_import:" + name)
    if event in _PROCESS_EVENTS:
        _EVENTS["process_attempts"].append(event)
        raise PermissionError("blocked_process_launch:" + event)
    if event in _NETWORK_EVENTS:
        _EVENTS["network_attempts"].append(event)
        raise PermissionError("blocked_network_use:" + event)
    if event in _MUTATION_EVENTS:
        _EVENTS["filesystem_mutation_attempts"].append(event)
        raise PermissionError("blocked_filesystem_mutation:" + event)
    if event == "open" and args:
        path = args[0]
        mode = args[1] if len(args) > 1 else None
        flags = args[2] if len(args) > 2 and isinstance(args[2], int) else 0
        write_mode = isinstance(mode, str) and any(flag in mode for flag in ("w", "a", "x", "+"))
        write_flags = flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)
        if (write_mode or write_flags) and not _is_allowed_log(path):
            _EVENTS["filesystem_mutation_attempts"].append("open:" + os.fsdecode(path))
            raise PermissionError("blocked_file_write")
    if event == "importlib.util.spec_from_file_location":
        _EVENTS["dynamic_source_load_attempts"].append(event)
        raise PermissionError("blocked_dynamic_source_load")


sys.addaudithook(_audit)


def _blocked_spec_from_file_location(*args, **kwargs):
    _EVENTS["dynamic_source_load_attempts"].append("spec_from_file_location")
    raise PermissionError("blocked_dynamic_source_load")


importlib.util.spec_from_file_location = _blocked_spec_from_file_location


def _finish() -> None:
    loaded = sorted(
        name for name in sys.modules
        if any(name == prefix or name.startswith(prefix + ".") for prefix in _ALLOWED)
    )
    _EVENTS["loaded_allowed_modules"] = loaded
    _EVENTS["candidate_import_requests"] = sorted(set(_EVENTS["candidate_import_requests"]))
    try:
        _LOG.write_text(json.dumps(_EVENTS, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except Exception as exc:
        sys.stderr.write("guard_log_write_failed:" + type(exc).__name__ + ":" + str(exc) + "\n")


atexit.register(_finish)
