#!/usr/bin/env python3
"""Reverify the frozen PR #148 runtime and install it offline from its wheelhouse."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

EXPECTED = {
    "lock_sha256": "4d0bd11eadca52c292cb883afc062fd95de6b03e8304dedf4820a027898a419f",
    "wheelhouse_zip_sha256": "68474c180d4e5d2b35df36354d68cc477a69061960cd26385661cad9a63a0214",
    "python_sha256": "06f1bfa6c5e9d42bc4c8371dd9217a2a185dcdc15ae888193d01f75dc04a3eb1",
    "python_version": "3.11.15",
    "uv_sha256": "b2859884b9693e7ffe7ba8c3ad912b78fa2b77b3519bb58a82b6f8fedb983f23",
    "uv_version": "uv 0.11.11 (ed7b06001 2026-05-06 aarch64-apple-darwin)",
    "node_sha256": "1ef99ea25fe70c9b67e7efe768ef8ee22148d3cabc703db6131b57aeb617d040",
    "node_version": "v26.7.0",
    "direct_versions": {"cryptography": "50.0.1", "jsonschema": "4.26.0", "rfc8785": "0.1.4"},
}


class RuntimeFailure(RuntimeError):
    pass


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def run(command: list[str], env: dict[str, str]) -> str:
    completed = subprocess.run(command, env=env, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if completed.returncode:
        raise RuntimeFailure(f"command_failed:{Path(command[0]).name}:{completed.returncode}:{completed.stdout[-1500:]}")
    return completed.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime-root", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--temp-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    runtime = args.runtime_root.resolve()
    output_root = args.output_root.resolve()
    temp_root = args.temp_root.resolve()
    lock = runtime / "requirements.lock"
    wheelhouse = runtime / "wheelhouse"
    zip_path = runtime / "wheelhouse.zip"
    manifest_path = runtime / "MANIFEST.json"
    base_python = runtime / "venv/bin/python"
    if not all(path.is_file() for path in (lock, zip_path, manifest_path, base_python)):
        raise RuntimeFailure("frozen_runtime_artifact_missing")

    manifest = json.loads(manifest_path.read_text())
    wheels = manifest["archive_format"]["wheels"]
    if len(wheels) != 10:
        raise RuntimeFailure(f"wheel_count:{len(wheels)}")
    wheel_receipts = []
    for entry in wheels:
        path = wheelhouse / entry["filename"]
        actual = sha256(path)
        if actual != entry["sha256"] or path.stat().st_size != entry["bytes"]:
            raise RuntimeFailure(f"wheel_identity_mismatch:{entry['filename']}")
        wheel_receipts.append({"filename": entry["filename"], "sha256": actual, "bytes": path.stat().st_size})

    resolved_python = Path(os.path.realpath(base_python))
    python_version = run([str(base_python), "--version"], os.environ.copy()).replace("Python ", "")
    python_sha = sha256(resolved_python)
    if python_version != EXPECTED["python_version"] or python_sha != EXPECTED["python_sha256"]:
        raise RuntimeFailure("python_identity_mismatch")
    if sha256(lock) != EXPECTED["lock_sha256"] or sha256(zip_path) != EXPECTED["wheelhouse_zip_sha256"]:
        raise RuntimeFailure("lock_or_wheelhouse_identity_mismatch")

    uv_name = shutil.which("uv")
    node_name = shutil.which("node")
    if not uv_name or not node_name:
        raise RuntimeFailure("uv_or_node_missing")
    uv_path = Path(uv_name).resolve()
    node_path = Path(node_name).resolve()
    uv_version = run([str(uv_path), "--version"], os.environ.copy())
    node_version = run([str(node_path), "--version"], os.environ.copy())
    if uv_version != EXPECTED["uv_version"] or sha256(uv_path) != EXPECTED["uv_sha256"]:
        raise RuntimeFailure("uv_identity_mismatch")
    if node_version != EXPECTED["node_version"] or sha256(node_path) != EXPECTED["node_sha256"]:
        raise RuntimeFailure("node_identity_mismatch")

    fresh = output_root / "runtime-offline-install"
    if fresh.exists():
        raise RuntimeFailure("fresh_runtime_output_exists")
    env = os.environ.copy()
    env.update({
        "TMPDIR": str(temp_root),
        "UV_CACHE_DIR": str(temp_root / "uv-cache"),
        "PYTHONDONTWRITEBYTECODE": "1",
        "GIT_OPTIONAL_LOCKS": "0",
    })
    run([str(base_python), "-m", "venv", str(fresh)], env)
    install_output = run([
        str(uv_path), "pip", "install", "--offline", "--no-index", "--no-cache",
        "--find-links", str(wheelhouse), "--require-hashes", "--python", str(fresh / "bin/python"),
        "-r", str(lock),
    ], env)
    check_output = run([str(uv_path), "pip", "check", "--python", str(fresh / "bin/python")], env)

    smoke = r'''
import importlib.metadata as md
import jsonschema
import rfc8785
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.exceptions import InvalidSignature
versions={name:md.version(name) for name in ("cryptography","jsonschema","rfc8785")}
assert versions == {"cryptography":"50.0.1","jsonschema":"4.26.0","rfc8785":"0.1.4"}
assert rfc8785.dumps({"b":1,"a":2}) == b'{"a":2,"b":1}'
try:
    rfc8785.dumps({"n":float("nan")})
except Exception as exc:
    rfc_negative=type(exc).__name__
else:
    raise AssertionError("rfc8785 accepted NaN")
schema={"type":"object","required":["x"],"properties":{"x":{"type":"integer"}}}
jsonschema.validate({"x":1},schema)
try:
    jsonschema.validate({"x":"1"},schema)
except jsonschema.ValidationError:
    schema_negative=True
else:
    raise AssertionError("jsonschema accepted invalid instance")
key=Ed25519PrivateKey.generate(); message=b"ERS05 runtime smoke"
signature=key.sign(message); key.public_key().verify(signature,message)
try:
    key.public_key().verify(signature,message+b"x")
except InvalidSignature:
    ed25519_negative=True
else:
    raise AssertionError("Ed25519 accepted changed message")
print(json.dumps({"versions":versions,"rfc8785_positive":"PASS","rfc8785_negative":rfc_negative,"jsonschema_positive":"PASS","jsonschema_negative":"PASS","ed25519_positive":"PASS","ed25519_negative":"PASS"},sort_keys=True))
'''
    smoke_output = run([str(fresh / "bin/python"), "-c", smoke], env)
    smoke_result = json.loads(smoke_output.splitlines()[-1])
    report = {
        "schema": "ers05-runtime-reverification/1",
        "status": "PASS",
        "runtime_artifacts": {
            "interpreter": {"path_alias": "$FROZEN_RUNTIME/venv/bin/python", "version": python_version, "resolved_binary_sha256": python_sha},
            "lock_sha256": sha256(lock),
            "wheelhouse_zip_sha256": sha256(zip_path),
            "wheels": wheel_receipts,
            "wheel_count": len(wheel_receipts),
        },
        "toolchain": {
            "uv": {"version": uv_version, "binary_sha256": sha256(uv_path)},
            "node": {"version": node_version, "binary_sha256": sha256(node_path)},
            "platform": platform.platform(),
            "machine": platform.machine(),
        },
        "offline_install": {
            "status": "PASS",
            "network_mode": "offline; no-index; no-cache; exact wheelhouse only",
            "uv_output_tail": install_output.splitlines()[-8:],
            "pip_check": check_output,
        },
        "dependency_smoke": smoke_result,
        "source_runtime_manifest_sha256": sha256(manifest_path),
    }
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", "wheel_count": len(wheel_receipts), "pip_check": check_output}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"status": "FAIL", "error_type": type(exc).__name__, "error": str(exc)}, sort_keys=True))
        raise SystemExit(1)
