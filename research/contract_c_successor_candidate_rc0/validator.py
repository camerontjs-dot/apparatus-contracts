"""Reference validator for the bounded Contract C successor research candidate.

The candidate inherits released Contract C 1.0 semantics and widens exactly two
semantic leaves: the provisional version sentinel and contribution channel
vocabulary. It never relabels ``non_deciding`` as support/counterevidence.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Literal

from pydantic import ValidationError

from validators import contract_c as released

CANDIDATE_VERSION = "research-non-deciding-rc0"
CANDIDATE_CHANNELS = ("support", "counterevidence", "non_deciding")
BASE_COMMIT = "c3563cff66d2c85dcbf575c693056e2d8e4563d4"
BASE_SCHEMA_BLOB = "b0369de9b5c156322d6787261bbc7658a3b33781"
BASE_VALIDATOR_BLOB = "9c75ccfbf2223578a8d1a7bf0c39673b394fbea4"


class CandidateContribution(released.Contribution):
    channel: Literal["support", "counterevidence", "non_deciding"]


class CandidatePropositionResult(released.PropositionResult):
    contributions: list[CandidateContribution]


class CandidateContractCResultSet(released.ContractCResultSet):
    contract_c_version: Literal["research-non-deciding-rc0"]
    propositions: list[CandidatePropositionResult]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_released_schema() -> dict[str, Any]:
    path = repo_root() / "schema" / "contract-c" / "1.0.0" / "schema.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("released Contract C schema must be an object")
    return value


def build_candidate_schema(released_schema: dict[str, Any] | None = None) -> dict[str, Any]:
    """Materialize the exact research candidate from the released 1.0 schema."""
    schema = copy.deepcopy(released_schema if released_schema is not None else load_released_schema())
    schema["title"] = "Apparatus Contract C minimal in-band successor candidate RC0"
    schema["$id"] = "urn:apparatus:research:contract-c:minimal-in-band:rc0"
    schema["properties"]["contract_c_version"]["const"] = CANDIDATE_VERSION
    schema["$defs"]["contribution"]["properties"]["channel"]["enum"] = list(CANDIDATE_CHANNELS)
    return schema


def semantic_schema_delta(
    released_schema: dict[str, Any], candidate_schema: dict[str, Any]
) -> list[str]:
    """Return semantic leaf differences, ignoring research-only title/ID metadata."""
    left = copy.deepcopy(released_schema)
    right = copy.deepcopy(candidate_schema)
    for obj in (left, right):
        obj.pop("title", None)
        obj.pop("$id", None)

    diffs: list[str] = []

    def walk(a: Any, b: Any, path: str) -> None:
        if type(a) is not type(b):
            diffs.append(path)
            return
        if isinstance(a, dict):
            for key in sorted(set(a) | set(b)):
                child = f"{path}.{key}" if path else key
                if key not in a or key not in b:
                    diffs.append(child)
                else:
                    walk(a[key], b[key], child)
            return
        if isinstance(a, list):
            if a != b:
                diffs.append(path)
            return
        if a != b:
            diffs.append(path)

    walk(left, right, "")
    return sorted(diffs)


def expected_semantic_delta() -> list[str]:
    return sorted(
        [
            "properties.contract_c_version.const",
            "$defs.contribution.properties.channel.enum",
        ]
    )


def _policy_hash_errors(model: CandidateContractCResultSet) -> list[str]:
    actual = released.sha256_hex(released.canonical_bytes(model.producer.policy.canonical))
    if actual == model.producer.policy.sha256:
        return []
    return [
        "CAL policy hash mismatch: "
        f"expected {model.producer.policy.sha256}, computed {actual}"
    ]


def validate_candidate_object(
    value: dict[str, Any],
    *,
    contract_b_index: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    try:
        model = CandidateContractCResultSet.model_validate(value)
    except ValidationError as exc:
        return [
            f"schema/semantic validation failed: {item['loc']}: {item['msg']}"
            for item in exc.errors()
        ]

    expected_result_id = released.result_set_identity(value)
    if model.result_set_id != expected_result_id:
        errors.append(
            "result_set_id mismatch: "
            f"expected {expected_result_id}, got {model.result_set_id}"
        )
    errors.extend(_policy_hash_errors(model))

    if contract_b_index is None:
        return errors

    try:
        index = released.ContractBIndex.model_validate(contract_b_index)
    except ValidationError as exc:
        errors.extend(
            f"Contract-B index invalid: {item['loc']}: {item['msg']}"
            for item in exc.errors()
        )
        return errors

    binding = model.input.contract_b
    if (
        binding.contract_version != index.contract_version
        or binding.bundle_id != index.bundle_id
        or binding.bundle_hash != index.bundle_hash
    ):
        errors.append("exact Contract-B binding does not match supplied Contract-B index")

    for proposition in model.propositions:
        pid = proposition.proposition.proposition_id
        expected_text_hash = index.propositions.get(pid)
        if expected_text_hash is None:
            errors.append(f"proposition is absent from Contract-B index: {pid}")
        elif proposition.proposition.text_sha256 != expected_text_hash:
            errors.append(f"proposition text hash mismatch for {pid}")

        for contribution in proposition.contributions:
            ref = contribution.evidence_ref
            indexed = index.passages.get(ref.passage_id)
            if indexed is None:
                errors.append(f"passage is absent from Contract-B index: {ref.passage_id}")
                continue
            if ref.source_id != indexed.source_id or ref.passage_sha256 != indexed.passage_sha256:
                errors.append(f"evidence reference mismatch for passage {ref.passage_id}")

    return errors


def validate_candidate_bytes(
    raw: bytes,
    *,
    expected_sha256: str | None = None,
    contract_b_index: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    if expected_sha256 is not None:
        errors.extend(released.validate_whole_object_hash(raw, expected_sha256))
    try:
        value = released.parse_json_bytes(raw)
    except ValueError as exc:
        return errors + [str(exc)]
    try:
        expected_canonical = released.canonical_bytes(value)
    except (TypeError, ValueError) as exc:
        return errors + [f"canonicalization failed: {exc}"]
    if raw != expected_canonical:
        errors.append(
            "non-canonical candidate Contract-C bytes: require sorted object keys, "
            "compact separators, UTF-8 Unicode, finite numbers, and exactly one trailing newline"
        )
    errors.extend(validate_candidate_object(value, contract_b_index=contract_b_index))
    return errors


def canonical_candidate(value: dict[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(value)
    out["contract_c_version"] = CANDIDATE_VERSION
    out["result_set_id"] = released.result_set_identity(out)
    return out
