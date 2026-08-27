"""Validator and canonicalizer for the optional Contract-B factual-context extension."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

EXTENSION_PATH = Path("extensions/contract-b-factual-context-v1.json")
EXTENSION_SCHEMA = "contract-b-factual-context-v1"
PROHIBITED_KEYS = frozenset(
    {
        "support",
        "refutation",
        "proposition_specific_relation",
        "semantic_validity",
        "temporal_applicability",
        "authority_applicability",
        "supplier_applicability",
        "completeness_conclusion",
        "decision_participation",
        "audit_support_verdict",
        "verdict",
        "abstention",
    }
)


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ExplicitValue(_Strict):
    state: Literal["known", "unknown"]
    value: Any | None

    @model_validator(mode="after")
    def _state_matches_value(self) -> "ExplicitValue":
        if self.state == "known" and self.value is None:
            raise ValueError("known state requires a non-null value")
        if self.state == "unknown" and self.value is not None:
            raise ValueError("unknown state requires null value")
        return self


class ClaimContext(_Strict):
    claim_id: str = Field(min_length=1)
    origin: ExplicitValue
    atomicity: ExplicitValue


class ContextFact(_Strict):
    fact_id: str = Field(min_length=1)
    predicate: str = Field(min_length=1)
    value: Any
    assertion_mode: str = Field(min_length=1)
    provenance_passage_id: str = Field(min_length=1)


class SourceContext(_Strict):
    source_id: str = Field(min_length=1)
    context_facts: list[ContextFact] = Field(default_factory=list)


class Anchor(_Strict):
    type: str = Field(min_length=1)
    value: Any


class PassageContext(_Strict):
    passage_id: str = Field(min_length=1)
    anchors: list[Anchor] = Field(default_factory=list)


class HistoryLink(_Strict):
    link_id: str = Field(min_length=1)
    claim_id: str = Field(min_length=1)
    passage_id: str = Field(min_length=1)
    nomination: dict[str, Any]
    review: dict[str, Any]

    @model_validator(mode="after")
    def _decision_present(self) -> "HistoryLink":
        if self.review.get("decision") not in {"accepted", "rejected", "needs-review"}:
            raise ValueError("review.decision must be accepted, rejected, or needs-review")
        return self


class HistoryCountCheck(_Strict):
    claim_id: str = Field(min_length=1)
    candidate: int = Field(ge=0)
    reviewed: int = Field(ge=0)
    admitted: int = Field(ge=0)


class ApertureObservation(_Strict):
    claim_id: str = Field(min_length=1)
    search_scope: dict[str, Any]
    outcome: ExplicitValue
    limitations: list[Any] = Field(default_factory=list)


class FactualContextExtension(_Strict):
    schema: Literal["contract-b-factual-context-v1"]
    history_complete: Literal[True]
    claims: list[ClaimContext] = Field(default_factory=list)
    sources: list[SourceContext] = Field(default_factory=list)
    passages: list[PassageContext] = Field(default_factory=list)
    history: list[HistoryLink] = Field(default_factory=list)
    history_count_checks: list[HistoryCountCheck] = Field(default_factory=list)
    aperture: list[ApertureObservation] = Field(default_factory=list)


class FactualContextValidationError(ValueError):
    """Raised when a present extension violates the promoted Contract-B profile."""


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON value is forbidden: {value}")


def _json_key(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _canonical_object(extension: FactualContextExtension) -> dict[str, Any]:
    data = extension.model_dump(mode="json")
    data["claims"] = sorted(data["claims"], key=lambda item: item["claim_id"])
    data["sources"] = sorted(data["sources"], key=lambda item: item["source_id"])
    for source in data["sources"]:
        source["context_facts"] = sorted(source["context_facts"], key=lambda item: item["fact_id"])
    data["passages"] = sorted(data["passages"], key=lambda item: item["passage_id"])
    for passage in data["passages"]:
        passage["anchors"] = sorted(
            passage["anchors"], key=lambda item: (item["type"], _json_key(item["value"]))
        )
    data["history"] = sorted(data["history"], key=lambda item: item["link_id"])
    data["history_count_checks"] = sorted(
        data["history_count_checks"], key=lambda item: item["claim_id"]
    )
    data["aperture"] = sorted(data["aperture"], key=lambda item: item["claim_id"])
    for aperture in data["aperture"]:
        aperture["limitations"] = sorted(aperture["limitations"], key=_json_key)
    return data


def canonical_bytes(extension: FactualContextExtension) -> bytes:
    return (
        json.dumps(
            _canonical_object(extension),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _walk_for_prohibited(value: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in PROHIBITED_KEYS:
                errors.append(f"prohibited proposition-specific field: {child_path}")
            errors.extend(_walk_for_prohibited(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_walk_for_prohibited(child, f"{path}[{index}]"))
    return errors


def _duplicates(values: list[str]) -> list[str]:
    counts = Counter(values)
    return sorted(value for value, count in counts.items() if count > 1)


def _derived_counts(extension: FactualContextExtension) -> dict[str, tuple[int, int, int]]:
    counts: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0])
    for link in extension.history:
        row = counts[link.claim_id]
        row[0] += 1
        decision = link.review["decision"]
        if decision != "needs-review":
            row[1] += 1
        if decision == "accepted":
            row[2] += 1
    return {claim_id: tuple(values) for claim_id, values in counts.items()}


def validate_extension(
    extension: FactualContextExtension,
    *,
    claim_ids: set[str],
    source_ids: set[str],
    passage_ids: set[str],
) -> list[str]:
    errors = _walk_for_prohibited(extension.model_dump(mode="json"))

    uniqueness_sets = {
        "claim_id": [item.claim_id for item in extension.claims],
        "source_id": [item.source_id for item in extension.sources],
        "passage_id": [item.passage_id for item in extension.passages],
        "link_id": [item.link_id for item in extension.history],
        "history_count_check.claim_id": [item.claim_id for item in extension.history_count_checks],
        "aperture.claim_id": [item.claim_id for item in extension.aperture],
    }
    for label, values in uniqueness_sets.items():
        duplicates = _duplicates(values)
        if duplicates:
            errors.append(f"duplicate {label}: {', '.join(duplicates)}")
    for source in extension.sources:
        duplicates = _duplicates([fact.fact_id for fact in source.context_facts])
        if duplicates:
            errors.append(f"duplicate fact_id in source {source.source_id}: {', '.join(duplicates)}")

    for claim in extension.claims:
        if claim.claim_id not in claim_ids:
            errors.append(f"unknown canonical claim reference: {claim.claim_id}")
    for source in extension.sources:
        if source.source_id not in source_ids:
            errors.append(f"unknown canonical source reference: {source.source_id}")
        for fact in source.context_facts:
            if fact.provenance_passage_id not in passage_ids:
                errors.append(
                    f"unknown provenance passage reference: {fact.provenance_passage_id}"
                )
    for passage in extension.passages:
        if passage.passage_id not in passage_ids:
            errors.append(f"unknown canonical passage reference: {passage.passage_id}")
    for link in extension.history:
        if link.claim_id not in claim_ids:
            errors.append(f"unknown history claim reference: {link.claim_id}")
        if link.passage_id not in passage_ids:
            errors.append(f"unknown history passage reference: {link.passage_id}")
    for aperture in extension.aperture:
        if aperture.claim_id not in claim_ids:
            errors.append(f"unknown aperture claim reference: {aperture.claim_id}")

    derived = _derived_counts(extension)
    for check in extension.history_count_checks:
        expected = derived.get(check.claim_id, (0, 0, 0))
        actual = (check.candidate, check.reviewed, check.admitted)
        if actual != expected:
            errors.append(
                "history count mismatch for "
                f"{check.claim_id}: supplied={actual}, derived={expected}"
            )
    return errors


def load_extension(
    path: Path,
    *,
    claim_ids: set[str],
    source_ids: set[str],
    passage_ids: set[str],
) -> FactualContextExtension:
    raw = path.read_bytes()
    try:
        data = json.loads(raw.decode("utf-8"), parse_constant=_reject_constant)
        extension = FactualContextExtension.model_validate(data)
    except (UnicodeDecodeError, json.JSONDecodeError, ValidationError, ValueError) as exc:
        raise FactualContextValidationError(f"extension schema/JSON validation failed: {exc}") from exc
    errors = validate_extension(
        extension,
        claim_ids=claim_ids,
        source_ids=source_ids,
        passage_ids=passage_ids,
    )
    if errors:
        raise FactualContextValidationError("; ".join(errors))
    canonical = canonical_bytes(extension)
    if raw != canonical:
        raise FactualContextValidationError("extension JSON is not in canonical normalized form")
    return extension


def discovery_state(contract_version: str, extension_exists: bool) -> str:
    if extension_exists:
        return "present"
    if contract_version in {"1.0.0", "1.1.0"}:
        return "legacy_absent"
    return "absent"


__all__ = [
    "EXTENSION_PATH",
    "EXTENSION_SCHEMA",
    "FactualContextExtension",
    "FactualContextValidationError",
    "canonical_bytes",
    "discovery_state",
    "load_extension",
    "validate_extension",
]
