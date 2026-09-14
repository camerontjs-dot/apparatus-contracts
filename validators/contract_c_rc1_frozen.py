from __future__ import annotations

import copy
import hashlib
import json
import re
from typing import Any, Iterable, Mapping

PROFILE = "contract-c-successor-candidate-a-rc1-research"
PROFILE_ANCHOR = "f5337dedaad045aa290e80f69dc83ac1a0f73436"
POLICY_RESOLVER_FIXTURE_COMMIT = "43b571464734325277374ee81098553fb7c1b944"
CAL_RC1_IMPLEMENTATION = "a902621e8baea3063dddd7f92ba975aade305464"
CAL_RC1_POLICY_SHA256 = "44ecc33519fa8911079595d322f5f0decbf0389af42e153ac32214931798e42c"

_HEX40 = re.compile(r"^[0-9a-f]{40}$")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")

EXECUTION_STATES = {"completed", "failed", "incomplete"}
COMPLETIONS = {"assessed", "not_checkable"}
VERDICTS = {"supported", "contradicted", "not_checkable"}
RELATIONS = {"supports", "refutes", "non_polarized"}
ROLES = {"causal", "residual"}
PUBLIC_REASONS = {
    "categorical_support",
    "categorical_refutation",
    "MIXED_RELATIONS",
    "unresolved_categorical_relation",
    "joint_public_cause",
    "no_deciding_relation",
}


class CandidateError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CandidateError(message)


def _keys(value: Mapping[str, Any], expected: set[str], where: str) -> None:
    _require(set(value) == expected, f"{where}: field mismatch: {sorted(value)} != {sorted(expected)}")


def _nonempty_string(value: Any, where: str) -> str:
    _require(isinstance(value, str) and value != "", f"{where}: expected non-empty string")
    return value


def _sha256_prefixed(value: Any, where: str) -> str:
    _require(isinstance(value, str) and _SHA256.fullmatch(value) is not None, f"{where}: expected sha256:<64 lowercase hex>")
    return value


def _hex40(value: Any, where: str) -> str:
    _require(isinstance(value, str) and _HEX40.fullmatch(value) is not None, f"{where}: expected 40 lowercase hex")
    return value


def _hex64(value: Any, where: str) -> str:
    _require(isinstance(value, str) and _HEX64.fullmatch(value) is not None, f"{where}: expected 64 lowercase hex")
    return value


def _ref_key(ref: Mapping[str, Any]) -> tuple[str, str]:
    _keys(ref, {"source_id", "passage_id"}, "evidence_ref")
    return (
        _nonempty_string(ref["source_id"], "evidence_ref.source_id"),
        _nonempty_string(ref["passage_id"], "evidence_ref.passage_id"),
    )


def _canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def _normalize_unsealed(value: Mapping[str, Any]) -> dict[str, Any]:
    x = copy.deepcopy(dict(value))
    x.pop("result_set_id", None)
    props = x.get("propositions", [])
    if isinstance(props, list):
        for p in props:
            if not isinstance(p, dict):
                continue
            participants = p.get("participants", [])
            if isinstance(participants, list):
                participants.sort(key=lambda row: _ref_key(row["evidence_ref"]) if isinstance(row, dict) and isinstance(row.get("evidence_ref"), dict) else ("", ""))
            groups = p.get("basis_groups", [])
            if isinstance(groups, list):
                for group in groups:
                    if isinstance(group, list):
                        group.sort(key=lambda ref: _ref_key(ref) if isinstance(ref, dict) else ("", ""))
                groups.sort(key=lambda group: tuple(_ref_key(ref) for ref in group) if isinstance(group, list) else tuple())
        props.sort(key=lambda p: (p.get("proposition", {}).get("proposition_id", ""), p.get("proposition", {}).get("content_sha256", "")) if isinstance(p, dict) else ("", ""))
    return x


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


def _validate_contract_b(cb: Any) -> None:
    _require(isinstance(cb, dict), "contract_b: expected object")
    _keys(cb, {"contract_version", "bundle_id", "bundle_hash"}, "contract_b")
    _nonempty_string(cb["contract_version"], "contract_b.contract_version")
    _nonempty_string(cb["bundle_id"], "contract_b.bundle_id")
    _sha256_prefixed(cb["bundle_hash"], "contract_b.bundle_hash")


def _validate_producer(producer: Any) -> None:
    _require(isinstance(producer, dict), "producer: expected object")
    _keys(producer, {"semantic_implementation_sha", "policy_sha256", "policy_resolver_commit_sha"}, "producer")
    _hex40(producer["semantic_implementation_sha"], "producer.semantic_implementation_sha")
    _hex64(producer["policy_sha256"], "producer.policy_sha256")
    _hex40(producer["policy_resolver_commit_sha"], "producer.policy_resolver_commit_sha")


def _validate_result_execution(execution: Any, where: str) -> str:
    _require(isinstance(execution, dict), f"{where}: expected object")
    _keys(execution, {"state"}, where)
    state = execution["state"]
    _require(state in EXECUTION_STATES, f"{where}.state: unknown state")
    return state


def _validate_execution(execution: Any, where: str) -> tuple[str, str | None]:
    _require(isinstance(execution, dict), f"{where}: expected object")
    _keys(execution, {"state", "completion"}, where)
    state = execution["state"]
    completion = execution["completion"]
    _require(state in EXECUTION_STATES, f"{where}.state: unknown state")
    if state == "completed":
        _require(completion in COMPLETIONS, f"{where}.completion: completed execution requires assessed|not_checkable")
    else:
        _require(completion is None, f"{where}.completion: failed/incomplete execution requires null")
    return state, completion


def _validate_terminal(terminal: Any, completion: str | None, where: str) -> tuple[str | None, str | None]:
    if completion is None:
        _require(terminal is None, f"{where}: failed/incomplete execution cannot carry terminal epistemic state")
        return None, None
    _require(isinstance(terminal, dict), f"{where}: completed execution requires terminal object")
    _keys(terminal, {"verdict", "reason"}, where)
    verdict = terminal["verdict"]
    reason = terminal["reason"]
    _require(verdict in VERDICTS, f"{where}.verdict: unknown verdict")
    _require(reason in PUBLIC_REASONS, f"{where}.reason: unknown public reason")
    if completion == "assessed":
        _require(verdict in {"supported", "contradicted"}, f"{where}: assessed completion cannot be not_checkable")
    else:
        _require(verdict == "not_checkable", f"{where}: not_checkable completion requires not_checkable verdict")
    allowed = {
        "supported": {"categorical_support"},
        "contradicted": {"categorical_refutation"},
        "not_checkable": {"MIXED_RELATIONS", "unresolved_categorical_relation", "joint_public_cause", "no_deciding_relation"},
    }
    _require(reason in allowed[verdict], f"{where}: verdict/reason incoherent")
    return verdict, reason


def _validate_participants(rows: Any, where: str) -> dict[tuple[str, str], dict[str, Any]]:
    _require(isinstance(rows, list), f"{where}: expected array")
    out: dict[tuple[str, str], dict[str, Any]] = {}
    for i, row in enumerate(rows):
        _require(isinstance(row, dict), f"{where}[{i}]: expected object")
        _keys(row, {"evidence_ref", "relation", "role"}, f"{where}[{i}]")
        _require(isinstance(row["evidence_ref"], dict), f"{where}[{i}].evidence_ref: expected object")
        k = _ref_key(row["evidence_ref"])
        _require(k not in out, f"{where}: duplicate exact participant {k}")
        _require(row["relation"] in RELATIONS, f"{where}[{i}].relation: unknown relation")
        _require(row["role"] in ROLES, f"{where}[{i}].role: unknown role")
        out[k] = row
    return out


def _validate_basis_groups(groups: Any, participants: Mapping[tuple[str, str], Mapping[str, Any]], where: str) -> list[frozenset[tuple[str, str]]]:
    _require(isinstance(groups, list), f"{where}: expected array")
    seen: set[frozenset[tuple[str, str]]] = set()
    normalized: list[frozenset[tuple[str, str]]] = []
    for i, group in enumerate(groups):
        _require(isinstance(group, list) and len(group) > 0, f"{where}[{i}]: basis group must be non-empty array")
        keys: list[tuple[str, str]] = []
        for j, ref in enumerate(group):
            _require(isinstance(ref, dict), f"{where}[{i}][{j}]: expected evidence ref")
            k = _ref_key(ref)
            _require(k not in keys, f"{where}[{i}]: duplicate member")
            _require(k in participants, f"{where}[{i}]: unknown participant {k}")
            _require(participants[k]["role"] == "causal", f"{where}[{i}]: residual participant cannot enter basis")
            keys.append(k)
        frozen = frozenset(keys)
        _require(frozen not in seen, f"{where}: duplicate equivalent basis group")
        seen.add(frozen)
        normalized.append(frozen)
    for group in normalized:
        _require(not any(other < group for other in normalized), f"{where}: non-minimal represented basis group")
    causal = {k for k, row in participants.items() if row["role"] == "causal"}
    covered = set().union(*normalized) if normalized else set()
    _require(causal == covered, f"{where}: basis family must cover exactly all causal participants")
    return normalized


def _group_relations(groups: Iterable[frozenset[tuple[str, str]]], participants: Mapping[tuple[str, str], Mapping[str, Any]]) -> list[set[str]]:
    return [{participants[k]["relation"] for k in group} for group in groups]


def _validate_terminal_coherence(verdict: str | None, reason: str | None, participants: Mapping[tuple[str, str], Mapping[str, Any]], groups: list[frozenset[tuple[str, str]]], where: str) -> None:
    if verdict is None:
        _require(not participants and not groups, f"{where}: failed/incomplete proposition cannot retain participants or basis")
        return
    relsets = _group_relations(groups, participants)
    if verdict == "supported":
        _require(groups, f"{where}: supported result requires a causal basis")
        _require(all("supports" in rs and "refutes" not in rs and "non_polarized" not in rs for rs in relsets), f"{where}: supported basis groups must be support-only in current scope")
    elif verdict == "contradicted":
        _require(groups, f"{where}: contradicted result requires a causal basis")
        _require(all("refutes" in rs and "supports" not in rs and "non_polarized" not in rs for rs in relsets), f"{where}: contradicted basis groups must be refute-only in current scope")
    elif reason == "MIXED_RELATIONS":
        _require(groups, f"{where}: mixed result requires basis groups")
        _require(all("supports" in rs and "refutes" in rs and "non_polarized" not in rs for rs in relsets), f"{where}: every mixed basis must contain support and refutation")
    elif reason in {"unresolved_categorical_relation", "joint_public_cause"}:
        _require(groups, f"{where}: unresolved/joint public cause requires causal basis")
        _require(all(rs == {"non_polarized"} for rs in relsets), f"{where}: unresolved/joint public cause bases must be non-polarized in current scope")
    elif reason == "no_deciding_relation":
        _require(not groups, f"{where}: no_deciding_relation cannot carry causal basis")
        _require(all(row["role"] == "residual" and row["relation"] == "non_polarized" for row in participants.values()), f"{where}: no_deciding_relation participants must be residual non-polarized")


def validate_object(value: Mapping[str, Any]) -> None:
    _require(isinstance(value, dict), "candidate: expected object")
    _keys(value, {"profile", "result_set_id", "contract_b", "producer", "execution", "propositions"}, "candidate")
    _require(value["profile"] == PROFILE, "candidate.profile: wrong/unknown research profile")
    _sha256_prefixed(value["result_set_id"], "candidate.result_set_id")
    _validate_contract_b(value["contract_b"])
    _validate_producer(value["producer"])
    result_state = _validate_result_execution(value["execution"], "candidate.execution")
    props = value["propositions"]
    _require(isinstance(props, list), "candidate.propositions: expected array")
    if result_state != "completed":
        _require(len(props) == 0, "candidate.propositions: failed/incomplete result-set cannot invent proposition results")
    seen_prop_ids: set[str] = set()
    for i, prop in enumerate(props):
        where = f"candidate.propositions[{i}]"
        _require(isinstance(prop, dict), f"{where}: expected object")
        _keys(prop, {"proposition", "execution", "terminal", "participants", "basis_groups"}, where)
        binding = prop["proposition"]
        _require(isinstance(binding, dict), f"{where}.proposition: expected object")
        _keys(binding, {"proposition_id", "content_sha256"}, f"{where}.proposition")
        pid = _nonempty_string(binding["proposition_id"], f"{where}.proposition.proposition_id")
        _require(pid not in seen_prop_ids, f"{where}: duplicate proposition_id")
        seen_prop_ids.add(pid)
        _sha256_prefixed(binding["content_sha256"], f"{where}.proposition.content_sha256")
        state, completion = _validate_execution(prop["execution"], f"{where}.execution")
        verdict, reason = _validate_terminal(prop["terminal"], completion, f"{where}.terminal")
        participants = _validate_participants(prop["participants"], f"{where}.participants")
        groups = _validate_basis_groups(prop["basis_groups"], participants, f"{where}.basis_groups")
        if state != "completed":
            _require(completion is None, f"{where}: non-completed proposition cannot have completion")
        _validate_terminal_coherence(verdict, reason, participants, groups, where)
    expected_id = compute_result_set_id(value)
    _require(value["result_set_id"] == expected_id, "candidate.result_set_id: stale or attacker-selected local content identity")


def verify_contract_b_references(value: Mapping[str, Any], *, exact_contract_b: Mapping[str, Any], evidence_index: Iterable[tuple[str, str]]) -> None:
    validate_object(value)
    _require(value["contract_b"] == dict(exact_contract_b), "contract_b: object is not bound to the independently selected exact Contract-B world")
    allowed = set(evidence_index)
    for prop in value["propositions"]:
        for participant in prop["participants"]:
            _require(_ref_key(participant["evidence_ref"]) in allowed, "participant: evidence reference is absent from the exact bound Contract-B world")


def verify_policy_resolution(value: Mapping[str, Any], *, independently_selected_resolver_commit_sha: str, resolver_entries: Iterable[Mapping[str, Any]]) -> Mapping[str, Any]:
    validate_object(value)
    _hex40(independently_selected_resolver_commit_sha, "independently_selected_resolver_commit_sha")
    producer = value["producer"]
    _require(producer["policy_resolver_commit_sha"] == independently_selected_resolver_commit_sha, "producer.policy_resolver_commit_sha: wrong resolver authority")
    matches = [entry for entry in resolver_entries if entry.get("semantic_implementation_sha") == producer["semantic_implementation_sha"] and entry.get("policy_sha256") == producer["policy_sha256"]]
    _require(len(matches) == 1, "producer: unknown or ambiguous implementation/policy binding in immutable resolver")
    return matches[0]


def verify_external_authority(value: Mapping[str, Any], *, expected_whole_object_sha256: str) -> None:
    validate_object(value)
    _sha256_prefixed(expected_whole_object_sha256, "expected_whole_object_sha256")
    _require(whole_object_sha256(value) == expected_whole_object_sha256, "whole object: does not match independently established handoff authority")


def verify_candidate(value: Mapping[str, Any], *, exact_contract_b: Mapping[str, Any], evidence_index: Iterable[tuple[str, str]], independently_selected_resolver_commit_sha: str, resolver_entries: Iterable[Mapping[str, Any]], expected_whole_object_sha256: str) -> None:
    verify_contract_b_references(value, exact_contract_b=exact_contract_b, evidence_index=evidence_index)
    verify_policy_resolution(value, independently_selected_resolver_commit_sha=independently_selected_resolver_commit_sha, resolver_entries=resolver_entries)
    verify_external_authority(value, expected_whole_object_sha256=expected_whole_object_sha256)
