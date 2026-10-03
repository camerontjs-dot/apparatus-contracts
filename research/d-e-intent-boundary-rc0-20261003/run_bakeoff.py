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

EXPECTED_PREFREEZE_HEAD = "0df2117ea6175f20a67e8748efd3f232b20f226b"
EXPECTED_PREFREEZE_TREE = "02e4c3b9bf5e1785c331efd91940f5a9003f31b9"
EXPECTED_PREREG_BLOB = "e9a70c352892445abd3d339a4f898936bfa3dbf7"
EXPECTED_CASES_BLOB = "eccf3520996b6c73d5d4a289eba2fe6f7ccf16c2"


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def identity(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical(value)).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()


def check_freeze() -> dict[str, Any]:
    freeze = json.loads(FREEZE.read_text())
    assert freeze["prefreeze_head"] == EXPECTED_PREFREEZE_HEAD
    assert freeze["prefreeze_tree"] == EXPECTED_PREFREEZE_TREE
    assert freeze["preregistration_blob"] == EXPECTED_PREREG_BLOB
    assert freeze["cases_blob"] == EXPECTED_CASES_BLOB
    assert git("rev-parse", f"{EXPECTED_PREFREEZE_HEAD}^{{tree}}") == EXPECTED_PREFREEZE_TREE
    assert git("rev-parse", f"{EXPECTED_PREFREEZE_HEAD}:research/d-e-intent-boundary-rc0-20261003/PREREGISTRATION.md") == EXPECTED_PREREG_BLOB
    assert git("rev-parse", f"{EXPECTED_PREFREEZE_HEAD}:research/d-e-intent-boundary-rc0-20261003/CASES.json") == EXPECTED_CASES_BLOB
    return freeze


def set_path(obj: dict[str, Any], path: str, value: Any) -> None:
    parts = path.split(".")
    cursor: Any = obj
    for part in parts[:-1]:
        cursor = cursor[part]
    cursor[parts[-1]] = value


def exact_equal(actual: Any, expected: Any) -> bool:
    return canonical(actual) == canonical(expected)


def validate_profile(profile: str, native: dict[str, Any], domains: dict[str, Any]) -> tuple[bool, str]:
    by_profile = {cfg["profile"]: cfg for cfg in domains.values()}
    cfg = by_profile.get(profile)
    if cfg is None:
        return False, "unknown_profile"
    rules = cfg["profile_rules"]
    for key, expected in rules.items():
        if key == "network":
            actual = native.get("environment", {}).get("network")
        elif key == "mode":
            actual = native.get("environment", {}).get("mode")
        elif key == "editable":
            actual = native.get("side_effect_scope", {}).get("editable")
        elif key == "create":
            actual = native.get("side_effect_scope", {}).get("create")
        else:
            actual = native.get(key)
        if not exact_equal(actual, expected):
            return False, f"profile_rule_mismatch:{key}"
    return True, "profile_valid"


def implementation_identity(domain: str, native: dict[str, Any]) -> str:
    if domain == "mainframe_task_dispatch":
        return identity({
            "executor": native.get("executor"),
            "agent_profile": native.get("agent_profile"),
            "task_category": native.get("task_category"),
        })
    return native.get("executable_identity", "")


def material_input_identity(domain: str, native: dict[str, Any]) -> str:
    if domain == "mainframe_task_dispatch":
        return identity({
            "arguments_identity": native.get("arguments_identity"),
            "source_contract_identity": native.get("source_contract_identity"),
            "verification_identity": native.get("verification_identity"),
        })
    return identity({
        "arguments": native.get("arguments"),
        "input_identities": native.get("input_identities"),
        "entry_point": native.get("entry_point"),
    })


def constraint_identity(native: dict[str, Any]) -> str:
    return identity(native.get("environment", {}))


def side_effect_identity(domain: str, native: dict[str, Any]) -> str:
    value = native.get("side_effect_scope") if domain == "mainframe_task_dispatch" else native.get("side_effect_targets")
    return identity(value)


def common_envelope(domain: str, cfg: dict[str, Any], native: dict[str, Any], profile: str) -> dict[str, Any]:
    value = {
        "schema": "execution-intent-common-envelope-rc0",
        "profile": profile,
        "decision_identity": cfg["decision_identity"],
        "effect": copy.deepcopy(cfg["effect"]),
        "target_identity": cfg["target_identity"],
        "implementation_identity": implementation_identity(domain, native),
        "material_input_identity": material_input_identity(domain, native),
        "constraint_identity": constraint_identity(native),
        "side_effect_identity": side_effect_identity(domain, native),
        "pre_state_identity": native.get("pre_state_identity"),
        "native_intent_identity": identity(native),
    }
    value["intent_identity"] = identity(value)
    return value


def validate_common(envelope: dict[str, Any]) -> tuple[bool, str]:
    required = {
        "schema", "profile", "decision_identity", "effect", "target_identity",
        "implementation_identity", "material_input_identity", "constraint_identity",
        "side_effect_identity", "pre_state_identity", "native_intent_identity",
        "intent_identity",
    }
    if set(envelope) != required:
        return False, "common_shape_invalid"
    if envelope["schema"] != "execution-intent-common-envelope-rc0":
        return False, "common_schema_invalid"
    if not isinstance(envelope["profile"], str) or not envelope["profile"]:
        return False, "common_profile_invalid"
    if not isinstance(envelope["effect"], dict) or set(envelope["effect"]) != {"type", "version"}:
        return False, "common_effect_invalid"
    supplied = envelope["intent_identity"]
    probe = dict(envelope)
    del probe["intent_identity"]
    if supplied != identity(probe):
        return False, "common_identity_invalid"
    for field in (
        "implementation_identity", "material_input_identity", "constraint_identity",
        "side_effect_identity", "native_intent_identity",
    ):
        if not isinstance(envelope[field], str) or not envelope[field].startswith("sha256:"):
            return False, f"common_hash_invalid:{field}"
    return True, "common_valid"


def weak_bind(cfg: dict[str, Any]) -> tuple[bool, str]:
    # Frozen weak control: exact D/effect/target only. Every mutation in CASES
    # intentionally leaves these broad values unchanged.
    ok = bool(cfg["decision_identity"] and cfg["effect"]["type"] and cfg["target_identity"])
    return ok, "effect_target_bound" if ok else "weak_shape_invalid"


def evaluate_case(case: dict[str, Any], data: dict[str, Any]) -> dict[str, Any]:
    domain = case["domain"]
    cfg = data["domains"][domain]
    native = copy.deepcopy(cfg["baseline"])
    profile = cfg["profile"]
    mutation = case.get("mutation")
    if mutation:
        if mutation["path"] == "__profile__":
            profile = mutation["value"]
        else:
            set_path(native, mutation["path"], copy.deepcopy(mutation["value"]))

    envelope = common_envelope(domain, cfg, native, profile)
    common_ok, common_reason = validate_common(envelope)
    profile_ok, profile_reason = validate_profile(profile, native, data["domains"])
    weak_ok, weak_reason = weak_bind(cfg)

    candidates = {
        "R0_effect_target_only": {
            "accepted": weak_ok,
            "reason": weak_reason,
        },
        "R1_common_envelope_only": {
            "accepted": common_ok,
            "reason": common_reason,
        },
        "R2_opaque_native_plus_profile": {
            "accepted": profile_ok,
            "reason": profile_reason,
            "native_intent_identity": identity(native),
        },
        "R3_common_envelope_plus_profile": {
            "accepted": common_ok and profile_ok,
            "reason": profile_reason if not profile_ok else common_reason,
            "intent_identity": envelope["intent_identity"],
        },
    }
    expected_valid = bool(case["expected_profile_valid"])
    return {
        "id": case["id"],
        "domain": domain,
        "material": bool(case["material"]),
        "expected_profile_valid": expected_valid,
        "profile": profile,
        "candidates": candidates,
    }


def summarize(rows: list[dict[str, Any]], candidate: str) -> dict[str, Any]:
    false_accepts = []
    false_rejects = []
    accepted = []
    rejected = []
    for row in rows:
        got = bool(row["candidates"][candidate]["accepted"])
        expected = bool(row["expected_profile_valid"])
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
    rows = [evaluate_case(case, data) for case in data["cases"]]
    names = [
        "R0_effect_target_only",
        "R1_common_envelope_only",
        "R2_opaque_native_plus_profile",
        "R3_common_envelope_plus_profile",
    ]
    summary = {name: summarize(rows, name) for name in names}

    weak_discriminates = bool(summary["R0_effect_target_only"]["false_accepts"])
    r1_insufficient = bool(summary["R1_common_envelope_only"]["false_accepts"])
    r2_clean = not summary["R2_opaque_native_plus_profile"]["false_accepts"] and not summary["R2_opaque_native_plus_profile"]["false_rejects"]
    r3_clean = not summary["R3_common_envelope_plus_profile"]["false_accepts"] and not summary["R3_common_envelope_plus_profile"]["false_rejects"]
    r2_r3_same = (
        summary["R2_opaque_native_plus_profile"]["accepted"]
        == summary["R3_common_envelope_plus_profile"]["accepted"]
    )

    if not weak_discriminates:
        disposition = "INCONCLUSIVE_WEAK_CONTROL_DID_NOT_DISCRIMINATE"
    elif r1_insufficient and r2_clean and r3_clean and r2_r3_same:
        disposition = "SUPPORTED_PROFILE_SPECIFIC_VALIDATION_LOAD_BEARING_COMMON_ENVELOPE_NOT_SUFFICIENT_ALONE"
    elif (not r1_insufficient) and r2_clean and r3_clean:
        disposition = "SUPPORTED_COMMON_ENVELOPE_STRUCTURALLY_SUFFICIENT_ON_FROZEN_CASES"
    else:
        disposition = "INCONCLUSIVE_REPRESENTATION_BAKEOFF"

    result = {
        "schema": "d-e-intent-boundary-result/1",
        "prefreeze": freeze,
        "cases_blob": EXPECTED_CASES_BLOB,
        "candidate_summaries": summary,
        "case_results": rows,
        "weak_control_discriminates": weak_discriminates,
        "profile_specific_validation_load_bearing": r1_insufficient and r2_clean,
        "common_envelope_additional_authorization_discrimination_observed": not r2_r3_same,
        "disposition": disposition,
        "nonclaims": [
            "does not establish production intent semantics",
            "does not establish that a common envelope has no operational or observability value",
            "does not establish universal effect-profile sufficiency",
            "does not authorize a new contract letter or Contract E promotion",
        ],
    }
    RESULT.write_bytes(canonical(result))
    print(json.dumps({
        "disposition": disposition,
        "weak_false_accepts": summary["R0_effect_target_only"]["false_accepts"],
        "common_only_false_accepts": summary["R1_common_envelope_only"]["false_accepts"],
        "opaque_profile_false_accepts": summary["R2_opaque_native_plus_profile"]["false_accepts"],
        "common_plus_profile_false_accepts": summary["R3_common_envelope_plus_profile"]["false_accepts"],
    }, indent=2))
    return 0 if disposition.startswith("SUPPORTED_") else 2


if __name__ == "__main__":
    raise SystemExit(main())
