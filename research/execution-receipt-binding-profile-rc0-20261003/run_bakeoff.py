#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CASES = HERE / "CASES.json"
FREEZE = HERE / "FREEZE.json"
RESULT = HERE / "RESULT.json"

PREFREEZE_HEAD = "87d7d83a9fd3df9aa9bf75252eaba58dd6a0e692"
PREFREEZE_TREE = "8606581301a63fe1d14c1168a8746e27bc010ea8"
PREREG_BLOB = "027b46d1d0a70b0eb56c0a6dc39afb7f66062944"
CASES_BLOB = "d93b6be433280e43c8b92f41e68fbe1de62d4d48"


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical(value)).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()


def check_freeze() -> dict[str, Any]:
    freeze = json.loads(FREEZE.read_text())
    assert freeze["prefreeze_head"] == PREFREEZE_HEAD
    assert freeze["prefreeze_tree"] == PREFREEZE_TREE
    assert freeze["preregistration_blob"] == PREREG_BLOB
    assert freeze["cases_blob"] == CASES_BLOB
    assert git("rev-parse", f"{PREFREEZE_HEAD}^{{tree}}") == PREFREEZE_TREE
    assert git("rev-parse", f"{PREFREEZE_HEAD}:research/execution-receipt-binding-profile-rc0-20261003/PREREGISTRATION.md") == PREREG_BLOB
    assert git("rev-parse", f"{PREFREEZE_HEAD}:research/execution-receipt-binding-profile-rc0-20261003/CASES.json") == CASES_BLOB
    return freeze


def set_or_delete(obj: dict[str, Any], path: str, op: str, value: Any = None) -> None:
    parts = path.split(".")
    cursor: Any = obj
    for part in parts[:-1]:
        cursor = cursor[part]
    key = parts[-1]
    if op == "delete":
        cursor.pop(key, None)
    else:
        cursor[key] = copy.deepcopy(value)


def prepare_receipt(fixture: dict[str, Any]) -> dict[str, Any]:
    receipt = copy.deepcopy(fixture)
    if receipt["result_sha256"] == "__COMPUTE_FROM_RESULT__":
        receipt["result_sha256"] = sha(receipt["result"])
    return receipt


def build_binding(receipt: dict[str, Any], expected: dict[str, Any]) -> dict[str, Any]:
    binding = {
        "schema": "cal-pipeline-execution-binding-profile-rc0",
        "receipt_id": receipt["id"],
        "receipt_result_sha256": receipt["result_sha256"],
        **copy.deepcopy(expected),
    }
    binding["binding_identity"] = sha(binding)
    return binding


def validate_carrier(receipt: dict[str, Any], *, require_applied: bool) -> tuple[bool, str]:
    required = {
        "id", "idempotency_key", "task_id", "project_id", "command_type", "state",
        "actor", "authority_class", "packet_id", "contract_sha256", "source_sha256",
        "requested_at", "accepted_at", "completed_at", "result", "result_sha256",
        "error_code", "error_message",
    }
    if set(receipt) != required:
        return False, "carrier_shape_invalid"
    if receipt["state"] != "completed":
        return False, f"carrier_not_completed:{receipt['state']}"
    if not isinstance(receipt["result"], dict):
        return False, "carrier_result_missing"
    if receipt["result_sha256"] != sha(receipt["result"]):
        return False, "carrier_result_hash_mismatch"
    if require_applied and receipt["result"].get("applied") is not True:
        return False, "carrier_not_applied"
    if not receipt["requested_at"] or not receipt["accepted_at"] or not receipt["completed_at"]:
        return False, "carrier_timestamps_missing"
    return True, "carrier_valid"


def valid_identity(value: Any) -> bool:
    return isinstance(value, str) and bool(value) and (
        value.startswith("sha256:")
        or value.startswith("decision:sha256:")
        or value.startswith("authorization-evaluation:sha256:")
        or value.startswith("verifier:sha256:")
    )


def validate_binding(
    receipt: dict[str, Any],
    binding: dict[str, Any],
    expected: dict[str, Any],
) -> tuple[bool, str]:
    required = {
        "schema", "receipt_id", "receipt_result_sha256",
        "decision_identity", "authorization_evaluation_identity", "intent_identity",
        "target_pre_state_identity", "target_post_state_identity",
        "verifier_identity", "verification_evidence_identity", "binding_identity",
    }
    if set(binding) != required:
        return False, "binding_shape_invalid"
    if binding["schema"] != "cal-pipeline-execution-binding-profile-rc0":
        return False, "binding_schema_invalid"
    supplied_identity = binding["binding_identity"]
    probe = dict(binding)
    del probe["binding_identity"]
    if supplied_identity != sha(probe):
        return False, "binding_identity_invalid"
    if binding["receipt_id"] != receipt["id"]:
        return False, "binding_receipt_id_mismatch"
    if binding["receipt_result_sha256"] != receipt["result_sha256"]:
        return False, "binding_receipt_result_mismatch"
    for field, wanted in expected.items():
        actual = binding.get(field)
        if not valid_identity(actual):
            return False, f"binding_identity_field_invalid:{field}"
        if actual != wanted:
            return False, f"binding_expectation_mismatch:{field}"
    evidence = receipt["result"].get("verification", {}).get("evidence_identity")
    if evidence != binding["verification_evidence_identity"]:
        return False, "binding_verification_evidence_mismatch"
    return True, "binding_valid"


def weak_receipt_only(receipt: dict[str, Any]) -> tuple[bool, str]:
    # Intentionally ignores D/E/action bindings but still checks the native
    # terminal result hash so the weak control fails only on the intended seam.
    return validate_carrier(receipt, require_applied=True)


def sidecar_candidate(
    receipt: dict[str, Any],
    binding: dict[str, Any],
    expected: dict[str, Any],
) -> tuple[bool, str]:
    ok, reason = validate_carrier(receipt, require_applied=True)
    if not ok:
        return ok, reason
    return validate_binding(receipt, binding, expected)


def inline_candidate(
    receipt: dict[str, Any],
    binding: dict[str, Any],
    expected: dict[str, Any],
) -> tuple[bool, str]:
    extended = copy.deepcopy(receipt)
    extended["cal_pipeline_binding"] = copy.deepcopy(binding)
    inline_binding = extended.pop("cal_pipeline_binding")
    ok, reason = validate_carrier(extended, require_applied=True)
    if not ok:
        return ok, reason
    return validate_binding(extended, inline_binding, expected)


def evaluate(case: dict[str, Any], fixture: dict[str, Any], expected: dict[str, Any]) -> dict[str, Any]:
    receipt = prepare_receipt(fixture)
    binding = build_binding(receipt, expected)

    for mutation in case["mutations"]:
        target = mutation["target"]
        if target.startswith("receipt."):
            set_or_delete(receipt, target.removeprefix("receipt."), mutation["op"], mutation.get("value"))
        elif target.startswith("binding."):
            set_or_delete(binding, target.removeprefix("binding."), mutation["op"], mutation.get("value"))
            if mutation["op"] != "delete":
                old = binding.pop("binding_identity", None)
                binding["binding_identity"] = sha(binding)
            else:
                binding.pop("binding_identity", None)
                binding["binding_identity"] = sha(binding)
        else:
            raise AssertionError(f"unknown mutation target: {target}")

    weak_ok, weak_reason = weak_receipt_only(receipt)
    sidecar_ok, sidecar_reason = sidecar_candidate(receipt, binding, expected)
    inline_ok, inline_reason = inline_candidate(receipt, binding, expected)

    return {
        "id": case["id"],
        "expected_valid": bool(case["expected_valid"]),
        "R0_receipt_only": {"accepted": weak_ok, "reason": weak_reason},
        "R1_receipt_plus_sidecar": {"accepted": sidecar_ok, "reason": sidecar_reason},
        "R2_inline_binding": {"accepted": inline_ok, "reason": inline_reason},
    }


def summarize(rows: list[dict[str, Any]], candidate: str) -> dict[str, Any]:
    false_accepts, false_rejects, accepted, rejected = [], [], [], []
    for row in rows:
        got = bool(row[candidate]["accepted"])
        expected = bool(row["expected_valid"])
        (accepted if got else rejected).append(row["id"])
        if got and not expected:
            false_accepts.append(row["id"])
        if not got and expected:
            false_rejects.append(row["id"])
    return {
        "accepted": accepted,
        "rejected": rejected,
        "false_accepts": false_accepts,
        "false_rejects": false_rejects,
    }


def main() -> int:
    freeze = check_freeze()
    data = json.loads(CASES.read_text())
    rows = [
        evaluate(case, data["receipt_fixture"], data["expected_bindings"])
        for case in data["cases"]
    ]
    summary = {
        candidate: summarize(rows, candidate)
        for candidate in (
            "R0_receipt_only",
            "R1_receipt_plus_sidecar",
            "R2_inline_binding",
        )
    }

    weak_discriminates = bool(summary["R0_receipt_only"]["false_accepts"])
    sidecar_clean = not summary["R1_receipt_plus_sidecar"]["false_accepts"] and not summary["R1_receipt_plus_sidecar"]["false_rejects"]
    inline_clean = not summary["R2_inline_binding"]["false_accepts"] and not summary["R2_inline_binding"]["false_rejects"]
    same = summary["R1_receipt_plus_sidecar"]["accepted"] == summary["R2_inline_binding"]["accepted"]

    if not weak_discriminates:
        disposition = "INCONCLUSIVE_WEAK_CONTROL_DID_NOT_DISCRIMINATE"
    elif sidecar_clean and inline_clean and same:
        disposition = "SUPPORTED_SIDECAR_BINDING_PROFILE_REPRESENTATIONALLY_SUFFICIENT_INLINE_EXTENSION_NO_ADDITIONAL_DISCRIMINATION"
    elif inline_clean and not sidecar_clean:
        disposition = "SUPPORTED_INLINE_BINDING_REQUIRED_ON_FROZEN_CASES"
    else:
        disposition = "INCONCLUSIVE_EXECUTION_RECEIPT_BINDING_BAKEOFF"

    result = {
        "schema": "execution-receipt-binding-result/1",
        "prefreeze": freeze,
        "mainframe_live_source": {
            "commit": "dbff8c39790ce70961de2310809e1bd737ccb7a9",
            "control_plane_blob": "075b899e844a11b628862169a9a21ec2b3b82d2c",
            "task_authority_blob": "b8d1e56c595674e9243d8ca564737dc6187952d3",
            "schema_blob": "0c7341244f0d4733da0de2c5b748561ebf86814a",
            "repository_blob": "2e7403f2b8945a3c7511300cfeb051f683ad864b",
        },
        "candidate_summaries": summary,
        "case_results": rows,
        "weak_control_discriminates": weak_discriminates,
        "sidecar_inline_same_discrimination": same,
        "disposition": disposition,
        "nonclaims": [
            "synthetic representation result only",
            "does not establish real execution or filesystem pre/post state",
            "does not establish production MainFrame integration",
            "does not establish verifier correctness or rollback correctness",
            "does not authorize a new execution-result contract",
        ],
    }
    RESULT.write_bytes(canonical(result) + b"\n")
    print(json.dumps({
        "disposition": disposition,
        "weak_false_accepts": summary["R0_receipt_only"]["false_accepts"],
        "sidecar_false_accepts": summary["R1_receipt_plus_sidecar"]["false_accepts"],
        "inline_false_accepts": summary["R2_inline_binding"]["false_accepts"],
        "sidecar_inline_same_discrimination": same,
    }, indent=2))
    return 0 if disposition.startswith("SUPPORTED_") else 2


if __name__ == "__main__":
    raise SystemExit(main())
