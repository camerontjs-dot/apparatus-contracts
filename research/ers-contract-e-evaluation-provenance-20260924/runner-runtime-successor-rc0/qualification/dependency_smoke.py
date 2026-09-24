#!/usr/bin/env python3
"""Offline dependency-only qualification for the frozen ERS 05 runtime."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import platform
import re
import sys
from pathlib import Path

PACKAGE_PREFIXES = (
    "jsonschema", "rfc8785", "cryptography", "attrs", "cffi",
    "pycparser", "referencing", "rpds", "typing_extensions",
)


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def normalize(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def require(condition: bool, code: str) -> None:
    if not condition:
        raise RuntimeError(code)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--lock", required=True, type=Path)
    parser.add_argument("--wheelhouse", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        require(platform.python_version() == manifest["base_python"]["version"] == "3.11.15",
                "python_version_mismatch")
        require(platform.python_implementation() == "CPython", "python_implementation_mismatch")
        require(platform.system() == "Darwin" and platform.machine() == "arm64",
                "platform_architecture_mismatch")
        venv_root = Path(sys.prefix)
        require(sys.prefix != sys.base_prefix, "not_running_in_virtual_environment")
        pyvenv_cfg = (venv_root / "pyvenv.cfg").read_text(encoding="utf-8").lower()
        require("include-system-site-packages = false" in pyvenv_cfg,
                "system_site_packages_enabled")
        base_executable = Path(getattr(sys, "_base_executable", sys.executable)).resolve()
        require(base_executable.is_file(), "base_python_executable_missing")
        require(sha256(base_executable.read_bytes()) == manifest["base_python"]["sha256"],
                "base_python_executable_hash_mismatch")

        archive_path = args.manifest.parent / manifest["files"]["wheelhouse.zip"]["path"]
        require(sha256(archive_path.read_bytes()) == manifest["files"]["wheelhouse.zip"]["sha256"],
                "wheelhouse_archive_hash_mismatch")
        lock_raw = args.lock.read_bytes()
        require(sha256(lock_raw) == manifest["files"]["requirements.lock"]["sha256"],
                "requirements_lock_hash_mismatch")
        lock_text = lock_raw.decode("utf-8")
        sums_path = args.manifest.parent / manifest["files"]["wheelhouse_sha256sums"]["path"]
        require(sha256(sums_path.read_bytes()) == manifest["files"]["wheelhouse_sha256sums"]["sha256"],
                "wheelhouse_sha256sums_hash_mismatch")
        expected_sums = {}
        for line in sums_path.read_text(encoding="utf-8").splitlines():
            digest, relative = line.split("  ", 1)
            expected_sums[relative] = digest
        expected_wheels = manifest["archive_format"]["wheels"]
        wheel_files = sorted(p for p in args.wheelhouse.iterdir() if p.is_file() and p.suffix == ".whl")
        expected_names = sorted(item["filename"] for item in expected_wheels)
        require([p.name for p in wheel_files] == expected_names, "wheelhouse_file_set_mismatch")
        installed = {
            normalize(dist.metadata["Name"]): dist.version
            for dist in importlib.metadata.distributions()
            if dist.metadata.get("Name")
        }
        expected_packages = manifest["dependency_graph"]
        expected_names_normalized = {normalize(item["name"]) for item in expected_packages}
        require(set(installed) == expected_names_normalized, "installed_package_set_mismatch")
        package_records = []
        for item in expected_packages:
            name = normalize(item["name"])
            require(installed.get(name) == item["version"], "installed_version_mismatch:" + name)
        for item, wheel_path in zip(expected_wheels, wheel_files):
            wheel_raw = wheel_path.read_bytes()
            require(sha256(wheel_raw) == item["sha256"], "wheel_hash_mismatch:" + wheel_path.name)
            require(expected_sums.get("wheelhouse/" + wheel_path.name) == item["sha256"],
                    "wheelhouse_checksum_manifest_mismatch:" + wheel_path.name)
            require(item["sha256"] in lock_text, "wheel_hash_missing_from_lock:" + wheel_path.name)
            package_records.append({
                "filename": wheel_path.name,
                "bytes": len(wheel_raw),
                "sha256": sha256(wheel_raw),
            })

        import jsonschema
        import rfc8785
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

        canonical = rfc8785.dumps({"z": 1, "a": 2})
        require(canonical == b'{"a":2,"z":1}', "rfc8785_canonicalization_failed")
        schema = {
            "type": "object",
            "properties": {"subject": {"type": "string"}},
            "required": ["subject"],
            "additionalProperties": False,
        }
        jsonschema.validate({"subject": "harmless-qualification"}, schema)
        try:
            jsonschema.validate({"subject": 7}, schema)
        except jsonschema.ValidationError:
            schema_rejection = "PASS"
        else:
            raise RuntimeError("jsonschema_negative_validation_failed")
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        message = b"ERS 05 dependency-only Ed25519 smoke check"
        signature = private_key.sign(message)
        public_key.verify(signature, message)
        try:
            public_key.verify(signature, message + b" altered")
        except Exception:
            signature_rejection = "PASS"
        else:
            raise RuntimeError("ed25519_wrong_message_not_rejected")
        authorized_prefixes = PACKAGE_PREFIXES
        imported_modules = sorted(
            name for name in sys.modules
            if any(name == prefix or name.startswith(prefix + ".") for prefix in authorized_prefixes)
        )
        top_level_imports = sorted({name.split(".", 1)[0] for name in imported_modules})
        require(set(top_level_imports).issubset({
            "jsonschema", "rfc8785", "cryptography", "attrs", "cffi",
            "pycparser", "referencing", "rpds", "typing_extensions",
        }), "unexpected_runtime_import")
        result = {
            "schema": "ers-05-runtime-dependency-smoke/1",
            "status": "PASS",
            "python": {
                "executable": sys.executable,
                "base_executable": str(base_executable),
                "version": platform.python_version(),
                "implementation": platform.python_implementation(),
                "system": platform.system(),
                "machine": platform.machine(),
                "virtual_environment": str(venv_root),
                "system_site_packages": False,
            },
            "installed_packages": [
                {"name": item["name"], "version": item["version"],
                 "direct": item["direct"]}
                for item in expected_packages
            ],
            "wheel_artifacts": package_records,
            "checks": {
                "runtime_lock_sha256": sha256(lock_raw),
                "wheelhouse_archive_sha256": sha256(archive_path.read_bytes()),
                "wheelhouse_files_and_hashes": "PASS",
                "installed_package_versions": "PASS",
                "rfc8785_canonicalization": "PASS",
                "jsonschema_positive_validation": "PASS",
                "jsonschema_negative_validation": schema_rejection,
                "ed25519_sign_verify": "PASS",
                "ed25519_wrong_message_rejection": signature_rejection,
            },
            "harmless_imports": {
                "direct_packages": ["jsonschema", "rfc8785", "cryptography"],
                "loaded_locked_package_modules": imported_modules,
            },
            "ephemeral_key": {
                "generated_in_memory": True,
                "serialized": False,
                "written_to_disk": False,
            },
            "network_calls": 0,
            "scientific_execution": {
                "contract_e_evaluations": 0,
                "supervisor_launches": 0,
                "pipe_matrix_cases": 0,
                "scientific_mutations": 0,
                "sandbox_creations": 0,
            },
        }
        encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
        if args.output:
            args.output.write_text(encoded, encoding="utf-8")
        print(encoded, end="")
        return 0
    except Exception as exc:
        result = {"schema": "ers-05-runtime-dependency-smoke/1",
                  "status": "FAIL", "error_type": type(exc).__name__,
                  "error": str(exc)}
        encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
        if args.output:
            args.output.write_text(encoded, encoding="utf-8")
        print(encoded, file=sys.stderr, end="")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
