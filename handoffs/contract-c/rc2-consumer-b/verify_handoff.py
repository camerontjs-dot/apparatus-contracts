#!/usr/bin/env python3
from __future__ import annotations

import base64
import hashlib
import io
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXPECTED_CANDIDATE = "e142f4aab119751dc201bca7994c0f97636c65647489f7edbee823a7f8aee3b4"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_outer_hashes() -> None:
    for line in (ROOT / "SHA256SUMS").read_text().splitlines():
        expected, name = line.split("  ", 1)
        observed = sha256_bytes((ROOT / name).read_bytes())
        if observed != expected:
            raise SystemExit(f"handoff hash mismatch: {name}: {observed} != {expected}")


def verify_contract_b(manifest: dict) -> None:
    cbi = manifest["contract_b_input"]
    encoded = "".join((ROOT / name).read_text().rstrip("\n") for name in cbi["base64_parts"])
    zip_bytes = base64.b64decode(encoded, validate=True)
    observed_zip = sha256_bytes(zip_bytes)
    if observed_zip != cbi["decoded_zip_sha256"]:
        raise SystemExit(f"decoded Contract-B ZIP hash mismatch: {observed_zip}")

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        prefix = "contract-b-1.2.0/"
        sums_name = prefix + "SHA256SUMS"
        sums = zf.read(sums_name)
        if sha256_bytes(sums) != cbi["sha256sums_sha256"]:
            raise SystemExit("Contract-B SHA256SUMS identity mismatch")
        for line in sums.decode("utf-8").splitlines():
            expected, rel = line.split("  ", 1)
            observed = sha256_bytes(zf.read(prefix + rel))
            if observed != expected:
                raise SystemExit(f"Contract-B file mismatch: {rel}: {observed} != {expected}")
        bundle_manifest = zf.read(prefix + "bundle_manifest.yaml").decode("utf-8")
        if f"bundle_id: {cbi['bundle_id']}" not in bundle_manifest:
            raise SystemExit("Contract-B bundle_id mismatch")
        if f"bundle_hash: {cbi['bundle_hash']}" not in bundle_manifest:
            raise SystemExit("Contract-B bundle_hash mismatch")
        if zf.read(prefix + "CONTRACT_VERSION").decode("utf-8").strip() != cbi["contract_version"]:
            raise SystemExit("Contract-B version mismatch")


def main() -> None:
    verify_outer_hashes()
    manifest = json.loads((ROOT / "MANIFEST.json").read_text())
    candidate_hash = sha256_bytes((ROOT / manifest["candidate"]["path"]).read_bytes())
    if candidate_hash != EXPECTED_CANDIDATE or candidate_hash != manifest["candidate"]["sha256"]:
        raise SystemExit(f"candidate identity mismatch: {candidate_hash}")
    candidate = json.loads((ROOT / manifest["candidate"]["path"]).read_text())
    if candidate["result_set_id"] != manifest["candidate"]["result_set_id"]:
        raise SystemExit("candidate result_set_id mismatch")
    verify_contract_b(manifest)
    print("CONTRACT_C_RC2_CONSUMER_B_HANDOFF_INTEGRITY=PASS")


if __name__ == "__main__":
    main()
