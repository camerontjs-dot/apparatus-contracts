#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNNER_REL = Path(
    "research/ers-contract-e-evaluation-provenance-20260921/"
    "fixture-bound-identity-successor-rc0/reproduce_rc6_fixture_bound.py"
)
EXPECTED_RUNNER_BLOB = "45eab4fc9aba4b851020b649546b09272c249c36"
EXPECTED_ISSUER = "sha256:e7f4581c2d58eecd0279f895cf3dd49df3098d092fa1e083731d802fcd1db259"
EXPECTED_APPARATUS_SOURCE = "b868e66523ed622dbc6615d22d5f73f81cbda94f"


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return "sha256:" + h.hexdigest()


def public_key_identity(private_key_path: Path) -> str:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    loaded = serialization.load_pem_private_key(private_key_path.read_bytes(), password=None)
    if not isinstance(loaded, Ed25519PrivateKey):
        raise RuntimeError("issuer_key_not_ed25519")
    public = loaded.public_key().public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return "sha256:" + hashlib.sha256(public).hexdigest()


def snapshot_empty(root: Path) -> dict:
    entries = sorted(
        p.relative_to(root).as_posix() + ("/" if p.is_dir() else "")
        for p in root.rglob("*")
    )
    return {"entries": entries, "count": len(entries)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--ers-root", required=True, type=Path)
    parser.add_argument("--ers-source-commit", required=True)
    parser.add_argument("--apparatus-freeze-receipt", required=True, type=Path)
    parser.add_argument("--preflight-pass-receipt", required=True, type=Path)
    parser.add_argument("--decision-root", required=True, type=Path)
    parser.add_argument("--contract-e-root", required=True, type=Path)
    parser.add_argument("--contract-d-root", required=True, type=Path)
    parser.add_argument("--consumer-root", required=True, type=Path)
    parser.add_argument("--fixtures", required=True, type=Path)
    parser.add_argument("--sandbox-root", required=True, type=Path)
    parser.add_argument("--transcript-schema", required=True, type=Path)
    parser.add_argument("--provenance-profile", required=True, type=Path)
    parser.add_argument("--issuer-private-key", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    args = parser.parse_args()

    repo = args.repo.resolve()
    output_root = args.output_root.resolve()
    sandbox = args.sandbox_root.resolve()
    key = args.issuer_private_key.resolve()

    if output_root.exists():
        raise SystemExit("successor_output_root_exists")
    output_root.mkdir(parents=True)
    if not sandbox.is_dir():
        raise SystemExit("sandbox_root_missing")
    before = snapshot_empty(sandbox)
    if before["count"] != 0:
        raise SystemExit("sandbox_not_empty_before_decisive_run")

    if not key.is_file():
        raise SystemExit("qualification_private_key_unavailable")
    if stat.S_IMODE(key.stat().st_mode) & 0o077:
        raise SystemExit("qualification_private_key_permissions_too_open")
    if public_key_identity(key) != EXPECTED_ISSUER:
        raise SystemExit("qualification_key_does_not_match_frozen_issuer")

    runner = repo / RUNNER_REL
    if not runner.is_file():
        raise SystemExit("scientific_runner_missing")
    if git(repo, "rev-parse", f"HEAD:{RUNNER_REL.as_posix()}") != EXPECTED_RUNNER_BLOB:
        raise SystemExit("scientific_runner_blob_changed")

    # Process A is intentionally a separate interpreter and imports no research
    # profile, Contract E profile, ERS candidate, or scientific runner.
    released_d_result = output_root / "RELEASED_D_FRESH_PROCESS.json"
    process_a = subprocess.run(
        [
            sys.executable,
            str(HERE / "fresh_released_d_preflight.py"),
            "--contract-d-root", str(args.contract_d_root.resolve()),
            "--output", str(released_d_result),
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "GIT_OPTIONAL_LOCKS": "0"},
    )
    (output_root / "PROCESS_A.log").write_text(process_a.stdout, encoding="utf-8")
    if process_a.returncode != 0 or not released_d_result.is_file():
        failure = {
            "schema": "ers-05-fresh-process-successor/1",
            "disposition": "BLOCKED",
            "stage": "released_d_fresh_process",
            "returncode": process_a.returncode,
            "sandbox_before": before,
        }
        (output_root / "FAILURE.json").write_text(
            json.dumps(failure, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        return 3

    # Process B is the exact already-frozen scientific runner, now started only
    # after Process A has terminated.
    matrix_output = output_root / "MATRIX"
    command = [
        sys.executable, str(runner),
        "--ers-root", str(args.ers_root.resolve()),
        "--ers-source-commit", args.ers_source_commit,
        "--apparatus-source-commit", EXPECTED_APPARATUS_SOURCE,
        "--apparatus-freeze-receipt", str(args.apparatus_freeze_receipt.resolve()),
        "--preflight-pass-receipt", str(args.preflight_pass_receipt.resolve()),
        "--decision-root", str(args.decision_root.resolve()),
        "--contract-e-root", str(args.contract_e_root.resolve()),
        "--contract-d-root", str(args.contract_d_root.resolve()),
        "--consumer-root", str(args.consumer_root.resolve()),
        "--fixtures", str(args.fixtures.resolve()),
        "--sandbox-root", str(sandbox),
        "--transcript-schema", str(args.transcript_schema.resolve()),
        "--provenance-profile", str(args.provenance_profile.resolve()),
        "--issuer-private-key", str(key),
        "--output", str(matrix_output),
    ]
    process_b = subprocess.run(
        command,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "GIT_OPTIONAL_LOCKS": "0"},
    )
    (output_root / "PROCESS_B.log").write_text(process_b.stdout, encoding="utf-8")

    after = snapshot_empty(sandbox)
    matrix_result = matrix_output / "RESULT.json"
    matrix_failure = matrix_output / "FAILURE.json"
    matrix_document = None
    if matrix_result.is_file():
        matrix_document = json.loads(matrix_result.read_text(encoding="utf-8"))
    elif matrix_failure.is_file():
        matrix_document = json.loads(matrix_failure.read_text(encoding="utf-8"))

    result = {
        "schema": "ers-05-fresh-process-successor/1",
        "process_a": json.loads(released_d_result.read_text(encoding="utf-8")),
        "process_a_returncode": process_a.returncode,
        "process_b_returncode": process_b.returncode,
        "process_b_result_kind": (
            "RESULT" if matrix_result.is_file()
            else "FAILURE" if matrix_failure.is_file()
            else "MISSING"
        ),
        "matrix": matrix_document,
        "sandbox_before": before,
        "sandbox_after": after,
        "sandbox_unchanged": before == after,
        "issuer_public_key_identity": EXPECTED_ISSUER,
        "scientific_runner_blob": EXPECTED_RUNNER_BLOB,
        "released_d_preflight_sha256": sha256_file(released_d_result),
    }
    (output_root / "SUCCESSOR_RESULT.json").write_text(
        json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))

    if matrix_document is None:
        return 3
    disposition = matrix_document.get("disposition")
    if isinstance(disposition, str) and disposition.startswith("SUPPORTED_"):
        return 0
    return process_b.returncode if process_b.returncode else 2


if __name__ == "__main__":
    raise SystemExit(main())
