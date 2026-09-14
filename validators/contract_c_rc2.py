from __future__ import annotations

import copy
import hashlib
import json
from collections.abc import Iterable, Mapping
from typing import Any

from . import contract_c_rc1_frozen as RC1

PROFILE = "contract-c-successor-candidate-a-rc2-research"
PROFILE_ANCHOR = "ba5f55b0fb6ca54e0461a688813b66fd81bf8c4c"
POLICY_RESOLVER_FIXTURE_COMMIT = "43b571464734325277374ee81098553fb7c1b944"
CAL_RC1_IMPLEMENTATION = "a902621e8baea3063dddd7f92ba975aade305464"
CAL_RC1_POLICY_SHA256 = "44ecc33519fa8911079595d322f5f0decbf0389af42e153ac32214931798e42c"
UNSUPPORTED_REASON = "UNSUPPORTED_SEMANTIC_FAMILY"

PUBLIC_REASONS = set(RC1.PUBLIC_REASONS) | {UNSUPPORTED_REASON}


class CandidateError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CandidateError(message)


def _canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        + "\n"
    ).encode("utf-8")


def _normalize_unsealed(value: Mapping[str, Any]) -> dict[str, Any]:
    # RC2 deliberately inherits RC1's canonical ordering rules unchanged.
    return RC1._normalize_unsealed(value)


def compute_result_set_id(unsealed: Mapping[str, Any]) -> str:
    normalized = _normalize_unsealed(unsealed)
    return "sha256:" + hashlib.sha256(_canonical_json_bytes(normalized)).hexdigest()


def seal(unsealed: Mapping[str, Any]) -> dict[str, Any]:
    normalized = _normalize_unsealed(unsealed)
    normalized["result_set_id"] = compute_result_set_id(normalized)
    return canonical_object(normalized)


def canonical_object(value: Mapping[str, Any]) -> dict[str, Any]:
    x = _normalize_unsealed(value)
    if "result_set_id" in value:
        x["result_set_id"] = value["result_set_id"]
    return json.loads(_canonical_json_bytes(x))


def canonical_bytes(value: Mapping[str, Any], *, validate: bool = True) -> bytes:
    if validate:
        validate_object(value)
    return _canonical_json_bytes(canonical_object(value))


def whole_object_sha256(value: Mapping[str, Any]) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def _reason_rows(value: Mapping[str, Any]) -> list[tuple[Mapping[str, Any], str | None]]:
    rows: list[tuple[Mapping[str, Any], str | None]] = []
    props = value.get("propositions", [])
    if not isinstance(props, list):
        return rows
    for prop in props:
        if not isinstance(prop, dict):
            continue
        terminal = prop.get("terminal")
        reason = terminal.get("reason") if isinstance(terminal, dict) else None
        rows.append((prop, reason))
    return rows


def _rc1_compatibility_view(value: Mapping[str, Any]) -> dict[str, Any]:
    """Reuse exact RC1 structure/causal validation without changing RC2 public bytes.

    The only RC2-only public state is UNSUPPORTED_SEMANTIC_FAMILY. For purposes
    of reusing RC1's already-qualified structural rules, that row is presented
    internally as the structurally identical no-deciding shape. RC2 separately
    validates the exact unsupported reason and never rewrites the public object.
    """
    x = copy.deepcopy(dict(value))
    x.pop("result_set_id", None)
    x["profile"] = RC1.PROFILE
    props = x.get("propositions", [])
    if isinstance(props, list):
        for prop in props:
            if not isinstance(prop, dict):
                continue
            terminal = prop.get("terminal")
            if (
                isinstance(terminal, dict)
                and terminal.get("reason") == UNSUPPORTED_REASON
            ):
                terminal["reason"] = "no_deciding_relation"
    return RC1.seal(x)


def _validate_rc2_only_terminal(
    prop: Mapping[str, Any], reason: str | None, where: str
) -> None:
    if reason != UNSUPPORTED_REASON:
        return
    execution = prop.get("execution")
    terminal = prop.get("terminal")
    participants = prop.get("participants")
    groups = prop.get("basis_groups")
    _require(isinstance(execution, dict), f"{where}.execution: expected object")
    _require(
        execution.get("state") == "completed",
        f"{where}: unsupported family requires completed execution",
    )
    _require(
        execution.get("completion") == "not_checkable",
        f"{where}: unsupported family requires not_checkable completion",
    )
    _require(isinstance(terminal, dict), f"{where}.terminal: expected object")
    _require(
        terminal.get("verdict") == "not_checkable",
        f"{where}: unsupported family requires not_checkable verdict",
    )
    _require(
        groups == [], f"{where}: unsupported family cannot carry causal basis groups"
    )
    _require(isinstance(participants, list), f"{where}.participants: expected array")
    for index, participant in enumerate(participants):
        _require(
            isinstance(participant, dict),
            f"{where}.participants[{index}]: expected object",
        )
        _require(
            participant.get("relation") == "non_polarized"
            and participant.get("role") == "residual",
            f"{where}.participants[{index}]: unsupported family participants must be non_polarized residual",
        )


def validate_object(value: Mapping[str, Any]) -> None:
    _require(isinstance(value, dict), "candidate: expected object")
    RC1._keys(
        value,
        {"profile", "result_set_id", "contract_b", "producer", "execution", "propositions"},
        "candidate",
    )
    _require(
        value["profile"] == PROFILE,
        "candidate.profile: wrong/unknown RC2 research profile",
    )
    RC1._sha256_prefixed(value["result_set_id"], "candidate.result_set_id")

    for index, (prop, reason) in enumerate(_reason_rows(value)):
        if reason is not None:
            _require(
                reason in PUBLIC_REASONS,
                f"candidate.propositions[{index}].terminal.reason: unknown public reason",
            )
        _validate_rc2_only_terminal(prop, reason, f"candidate.propositions[{index}]")

    # Exact RC1 validation remains the authority for every unchanged structure,
    # causal, execution and participant rule.
    compatibility = _rc1_compatibility_view(value)
    try:
        RC1.validate_object(compatibility)
    except Exception as exc:
        raise CandidateError(f"inherited RC1 validation failed: {exc}") from exc

    expected_id = compute_result_set_id(value)
    _require(
        value["result_set_id"] == expected_id,
        "candidate.result_set_id: stale or attacker-selected local content identity",
    )


def verify_contract_b_references(
    value: Mapping[str, Any],
    *,
    exact_contract_b: Mapping[str, Any],
    evidence_index: Iterable[tuple[str, str]],
) -> None:
    validate_object(value)
    _require(
        value["contract_b"] == dict(exact_contract_b),
        "contract_b: object is not bound to the independently selected exact Contract-B world",
    )
    allowed = set(evidence_index)
    for prop in value["propositions"]:
        for participant in prop["participants"]:
            _require(
                RC1._ref_key(participant["evidence_ref"]) in allowed,
                "participant: evidence reference is absent from the exact bound Contract-B world",
            )


def verify_policy_resolution(
    value: Mapping[str, Any],
    *,
    independently_selected_resolver_commit_sha: str,
    resolver_entries: Iterable[Mapping[str, Any]],
) -> Mapping[str, Any]:
    validate_object(value)
    RC1._hex40(
        independently_selected_resolver_commit_sha,
        "independently_selected_resolver_commit_sha",
    )
    producer = value["producer"]
    _require(
        producer["policy_resolver_commit_sha"]
        == independently_selected_resolver_commit_sha,
        "producer.policy_resolver_commit_sha: wrong resolver authority",
    )
    matches = [
        entry
        for entry in resolver_entries
        if entry.get("semantic_implementation_sha")
        == producer["semantic_implementation_sha"]
        and entry.get("policy_sha256") == producer["policy_sha256"]
    ]
    _require(
        len(matches) == 1,
        "producer: unknown or ambiguous implementation/policy binding in immutable resolver",
    )
    return matches[0]


def verify_external_authority(
    value: Mapping[str, Any], *, expected_whole_object_sha256: str
) -> None:
    validate_object(value)
    RC1._sha256_prefixed(
        expected_whole_object_sha256,
        "expected_whole_object_sha256",
    )
    _require(
        whole_object_sha256(value) == expected_whole_object_sha256,
        "whole object: does not match independently established handoff authority",
    )


def verify_candidate(
    value: Mapping[str, Any],
    *,
    exact_contract_b: Mapping[str, Any],
    evidence_index: Iterable[tuple[str, str]],
    independently_selected_resolver_commit_sha: str,
    resolver_entries: Iterable[Mapping[str, Any]],
    expected_whole_object_sha256: str,
) -> None:
    verify_contract_b_references(
        value,
        exact_contract_b=exact_contract_b,
        evidence_index=evidence_index,
    )
    verify_policy_resolution(
        value,
        independently_selected_resolver_commit_sha=independently_selected_resolver_commit_sha,
        resolver_entries=resolver_entries,
    )
    verify_external_authority(
        value,
        expected_whole_object_sha256=expected_whole_object_sha256,
    )
