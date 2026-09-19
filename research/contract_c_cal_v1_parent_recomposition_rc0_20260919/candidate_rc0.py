from __future__ import annotations

import copy
import hashlib
import json
import re
from collections.abc import Mapping
from typing import Any

PROFILE = "contract-c-cal-v1-parent-recomposition-rc0"
CAL_FREEZE_COMMIT = "e24e405f5336ee024674f39dba97255bb58a2dd9"
CAL_SEMANTIC_SOURCE_COMMIT = "7cf0d2e50562ec4ce4082d1e1c058a11025b1a48"
CAL_SEMANTIC_IMPLEMENTATION = "847cc970642bb648dc994b929c2053b5c9d4648c"
POLICY_SHA256 = "44ecc33519fa8911079595d322f5f0decbf0389af42e153ac32214931798e42c"
POLICY_RESOLVER_COMMIT = "1d33e0612befcf8016816197c90c062373796df9"

_SHA = re.compile(r"^sha256:[0-9a-f]{64}$")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_CHILD_RESULT = re.compile(r"^cal-child-result:[0-9a-f]{64}$")
_CONCLUSIONS = {"supported", "contradicted", "not_checkable"}


class CandidateError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CandidateError(message)


def _exact_keys(value: Mapping[str, Any], expected: set[str], where: str) -> None:
    _require(set(value) == expected, f"{where}: field mismatch")


def _canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode("utf-8")


def _normalize_unsealed(value: Mapping[str, Any]) -> dict[str, Any]:
    x = copy.deepcopy(dict(value))
    x.pop("result_set_id", None)
    recomposition = x.get("recomposition")
    if isinstance(recomposition, dict):
        children = recomposition.get("ordered_children")
        if isinstance(children, list):
            children.sort(
                key=lambda row: row.get("sequence", -1) if isinstance(row, dict) else -1
            )
    return x


def compute_result_set_id(unsealed: Mapping[str, Any]) -> str:
    normalized = _normalize_unsealed(unsealed)
    return "sha256:" + hashlib.sha256(_canonical_json_bytes(normalized)).hexdigest()


def seal(unsealed: Mapping[str, Any]) -> dict[str, Any]:
    normalized = _normalize_unsealed(unsealed)
    normalized["result_set_id"] = compute_result_set_id(normalized)
    return json.loads(_canonical_json_bytes(normalized))


def canonical_bytes(value: Mapping[str, Any], *, rc2_validator: Any) -> bytes:
    validate_object(value, rc2_validator=rc2_validator)
    normalized = _normalize_unsealed(value)
    normalized["result_set_id"] = value["result_set_id"]
    return _canonical_json_bytes(normalized)


def whole_object_sha256(value: Mapping[str, Any], *, rc2_validator: Any) -> str:
    return "sha256:" + hashlib.sha256(
        canonical_bytes(value, rc2_validator=rc2_validator)
    ).hexdigest()


def _terminal_conclusion(prop: Mapping[str, Any]) -> str:
    execution = prop.get("execution")
    terminal = prop.get("terminal")
    _require(isinstance(execution, dict), "rc2 proposition execution missing")
    _require(execution.get("state") == "completed", "recomposition child must be completed")
    _require(isinstance(terminal, dict), "recomposition child terminal missing")
    verdict = terminal.get("verdict")
    _require(verdict in _CONCLUSIONS, "recomposition child terminal verdict invalid")
    return str(verdict)


def validate_object(value: Mapping[str, Any], *, rc2_validator: Any) -> None:
    _require(isinstance(value, dict), "candidate: expected object")
    _exact_keys(
        value,
        {"profile", "result_set_id", "rc2_result", "recomposition"},
        "candidate",
    )
    _require(value["profile"] == PROFILE, "candidate.profile mismatch")
    _require(
        isinstance(value["result_set_id"], str)
        and _SHA.fullmatch(value["result_set_id"]) is not None,
        "candidate.result_set_id invalid",
    )

    rc2 = value["rc2_result"]
    _require(isinstance(rc2, dict), "candidate.rc2_result: expected object")
    rc2_validator.validate_object(rc2)
    producer = rc2["producer"]
    _require(
        producer["semantic_implementation_sha"] == CAL_SEMANTIC_IMPLEMENTATION,
        "rc2 producer semantic implementation is not frozen CAL V1",
    )
    _require(
        producer["policy_sha256"] == POLICY_SHA256,
        "rc2 producer policy digest mismatch",
    )
    _require(
        producer["policy_resolver_commit_sha"] == POLICY_RESOLVER_COMMIT,
        "rc2 producer resolver mismatch",
    )

    rows = {
        row["proposition"]["proposition_id"]: row
        for row in rc2["propositions"]
    }

    r = value["recomposition"]
    _require(isinstance(r, dict), "candidate.recomposition: expected object")
    _exact_keys(
        r,
        {
            "cal_freeze_commit",
            "cal_semantic_source_commit",
            "root",
            "decomposition_id",
            "operator",
            "ordered_children",
            "decomposition_receipt_id",
            "parent_conclusion",
        },
        "candidate.recomposition",
    )
    _require(
        r["cal_freeze_commit"] == CAL_FREEZE_COMMIT,
        "recomposition CAL freeze mismatch",
    )
    _require(
        r["cal_semantic_source_commit"] == CAL_SEMANTIC_SOURCE_COMMIT,
        "recomposition semantic source mismatch",
    )
    _require(
        isinstance(r["decomposition_id"], str) and r["decomposition_id"].strip(),
        "recomposition decomposition_id invalid",
    )
    _require(r["operator"] == "all_of", "recomposition operator must be all_of")
    _require(
        isinstance(r["decomposition_receipt_id"], str)
        and _HEX64.fullmatch(r["decomposition_receipt_id"]) is not None,
        "recomposition receipt id invalid",
    )
    _require(
        r["parent_conclusion"] in _CONCLUSIONS,
        "recomposition parent conclusion invalid",
    )

    root = r["root"]
    _require(isinstance(root, dict), "recomposition.root invalid")
    _exact_keys(root, {"proposition_id", "text_sha256"}, "recomposition.root")
    _require(
        isinstance(root["proposition_id"], str) and root["proposition_id"].strip(),
        "root proposition_id invalid",
    )
    _require(
        isinstance(root["text_sha256"], str)
        and _SHA.fullmatch(root["text_sha256"]) is not None,
        "root text_sha256 invalid",
    )

    children = r["ordered_children"]
    _require(
        isinstance(children, list) and len(children) >= 2,
        "recomposition requires >=2 children",
    )
    expected_sequences = list(range(1, len(children) + 1))
    actual_sequences = [
        row.get("sequence") if isinstance(row, dict) else None for row in children
    ]
    _require(
        actual_sequences == expected_sequences,
        "recomposition child sequence is not contiguous canonical order",
    )

    seen_ids: set[str] = set()
    seen_results: set[str] = set()
    for index, child in enumerate(children):
        where = f"recomposition.ordered_children[{index}]"
        _require(isinstance(child, dict), f"{where}: expected object")
        _exact_keys(
            child,
            {
                "sequence",
                "proposition_id",
                "text_sha256",
                "contract_c_content_sha256",
                "native_result_sha256",
                "cal_result_id",
                "conclusion",
            },
            where,
        )
        pid = child["proposition_id"]
        _require(isinstance(pid, str) and pid.strip(), f"{where}.proposition_id invalid")
        _require(pid not in seen_ids, f"{where}: duplicate proposition")
        _require(pid != root["proposition_id"], f"{where}: child equals root")
        seen_ids.add(pid)
        _require(
            isinstance(child["text_sha256"], str)
            and _SHA.fullmatch(child["text_sha256"]) is not None,
            f"{where}.text_sha256 invalid",
        )
        _require(
            isinstance(child["contract_c_content_sha256"], str)
            and _SHA.fullmatch(child["contract_c_content_sha256"]) is not None,
            f"{where}.contract_c_content_sha256 invalid",
        )
        _require(
            isinstance(child["native_result_sha256"], str)
            and _SHA.fullmatch(child["native_result_sha256"]) is not None,
            f"{where}.native_result_sha256 invalid",
        )
        _require(
            isinstance(child["cal_result_id"], str)
            and _CHILD_RESULT.fullmatch(child["cal_result_id"]) is not None,
            f"{where}.cal_result_id invalid",
        )
        _require(
            child["cal_result_id"] not in seen_results,
            f"{where}: reused child result id",
        )
        seen_results.add(child["cal_result_id"])
        _require(child["conclusion"] in _CONCLUSIONS, f"{where}.conclusion invalid")
        _require(pid in rows, f"{where}: missing matching RC2 proposition")
        row = rows[pid]
        _require(
            row["proposition"]["content_sha256"]
            == child["contract_c_content_sha256"],
            f"{where}: RC2 content binding mismatch",
        )
        _require(
            _terminal_conclusion(row) == child["conclusion"],
            f"{where}: RC2 terminal conclusion mismatch",
        )

    _require(
        set(rows) == seen_ids,
        "RC2 proposition set must equal recomposition child set in RC0",
    )

    expected = compute_result_set_id(value)
    _require(
        value["result_set_id"] == expected,
        "candidate.result_set_id stale or attacker-selected",
    )


def verify_recomposition_authority(
    value: Mapping[str, Any],
    *,
    exact_recomposition: Mapping[str, Any],
    rc2_validator: Any,
) -> None:
    validate_object(value, rc2_validator=rc2_validator)
    _require(
        value["recomposition"] == dict(exact_recomposition),
        "recomposition: does not match independently selected CAL V1 parent authority",
    )


def verify_external_authority(
    value: Mapping[str, Any],
    *,
    expected_whole_object_sha256: str,
    rc2_validator: Any,
) -> None:
    validate_object(value, rc2_validator=rc2_validator)
    _require(
        isinstance(expected_whole_object_sha256, str)
        and _SHA.fullmatch(expected_whole_object_sha256) is not None,
        "expected whole-object authority invalid",
    )
    _require(
        whole_object_sha256(value, rc2_validator=rc2_validator)
        == expected_whole_object_sha256,
        "whole object: does not match independently established authority",
    )
