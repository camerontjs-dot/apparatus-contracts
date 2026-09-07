"""Research-only Contract B v2 RC0 candidate and pressure-test validator.

This module is not a production Contract B validator and is not exported from
``validators``. It deliberately requires the exact Contract A 2.0 object for
cross-boundary conformance checks.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from copy import deepcopy
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from validators.contract_a import CONTRACT_A_VERSION, validate_candidate as validate_contract_a

SCHEMA = "contract-b-v2-candidate-rc0"
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
        "audit_confidence",
        "verdict",
        "abstention",
        "scaffold_support_status",
        "scaffold_claim_strength",
        "scaffold_extraction_fidelity",
        "scaffold_counterevidence_found",
        "scaffold_downgraded",
    }
)


class CandidateValidationError(ValueError):
    """Raised when the RC0 candidate fails structural or cross-A conformance."""


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Producer(_Strict):
    producer_id: str = Field(min_length=1)
    producer_version: str = Field(min_length=1)


class PreparationProfile(_Strict):
    profile_id: str = Field(min_length=1)
    profile_sha256: str = Field(min_length=1)


class SourceContractA(_Strict):
    version: Literal["2.0.0"]
    handoff_id: str = Field(min_length=1)
    handoff_sha256: str = Field(min_length=1)


class Proposition(_Strict):
    proposition_id: str = Field(min_length=1)
    text: str = Field(min_length=1)
    text_sha256: str = Field(min_length=1)


class Declaration(_Strict):
    root_proposition: Proposition
    decomposition: dict[str, Any]


class ContextFact(_Strict):
    fact_id: str = Field(min_length=1)
    predicate: str = Field(min_length=1)
    value: Any
    assertion_mode: str = Field(min_length=1)
    provenance_passage_id: str = Field(min_length=1)


class SourceRef(_Strict):
    source_id: str = Field(min_length=1)
    media_type: str = Field(min_length=1)
    content_sha256: str = Field(min_length=1)
    context_facts: list[ContextFact] = Field(default_factory=list)


class Anchor(_Strict):
    type: str = Field(min_length=1)
    value: Any


class Passage(_Strict):
    passage_id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    start_utf8_byte: int = Field(ge=0)
    end_utf8_byte: int = Field(gt=0)
    text: str = Field(min_length=1)
    text_sha256: str = Field(min_length=1)
    anchors: list[Anchor] = Field(default_factory=list)

    @model_validator(mode="after")
    def _ordered_span(self) -> "Passage":
        if self.end_utf8_byte <= self.start_utf8_byte:
            raise ValueError("end_utf8_byte must be greater than start_utf8_byte")
        return self


class Query(_Strict):
    query_id: str = Field(min_length=1)
    text: str = Field(min_length=1)
    text_sha256: str = Field(min_length=1)
    origin: Literal[
        "exact_proposition_text",
        "producer_derived",
        "operator_supplied",
        "unknown",
    ]


class Retrieval(_Strict):
    retrieval_id: str = Field(min_length=1)
    proposition_id: str = Field(min_length=1)
    lane_kind: str = Field(min_length=1)
    implementation_id: str = Field(min_length=1)
    query: Query
    candidate_limit: int = Field(gt=0)
    search_source_ids: list[str]
    execution_state: Literal["completed", "partial", "failed"]
    limitations: list[Any] = Field(default_factory=list)


class Nomination(_Strict):
    retrieval_id: str = Field(min_length=1)
    rank: int = Field(gt=0)


class Selection(_Strict):
    state: Literal["selected", "not_selected"]
    order: int | None = None

    @model_validator(mode="after")
    def _selection_consistency(self) -> "Selection":
        if self.state == "selected":
            if self.order is None or self.order <= 0:
                raise ValueError("selected requires positive order")
        elif self.order is not None:
            raise ValueError("not_selected requires null order")
        return self


class Review(_Strict):
    state: Literal["not_reviewed", "accepted", "rejected", "needs_review"]


class CandidateLink(_Strict):
    link_id: str = Field(min_length=1)
    proposition_id: str = Field(min_length=1)
    passage_id: str = Field(min_length=1)
    nominations: list[Nomination] = Field(min_length=1)
    selection: Selection
    review: Review

    @model_validator(mode="after")
    def _stage_consistency(self) -> "CandidateLink":
        if self.selection.state == "not_selected" and self.review.state != "not_reviewed":
            raise ValueError("unselected candidate cannot have a review/admission decision")
        return self


class Aperture(_Strict):
    proposition_id: str = Field(min_length=1)
    execution_state: Literal["complete", "partial", "failed", "not_run"]
    search_source_ids: list[str]
    limitations: list[Any] = Field(default_factory=list)


class Bundle(_Strict):
    schema: Literal["contract-b-v2-candidate-rc0"]
    bundle_id: str = Field(min_length=1)
    producer: Producer
    preparation_profile: PreparationProfile
    source_contract_a: SourceContractA
    declaration: Declaration
    sources: list[SourceRef]
    passages: list[Passage]
    retrievals: list[Retrieval]
    candidate_links: list[CandidateLink]
    aperture: list[Aperture]
    history_complete: Literal[True]
    bundle_sha256: str = Field(min_length=1)


def _hash_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _hash_text(value: str) -> str:
    return _hash_bytes(value.encode("utf-8"))


def _json_key(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _walk_for_prohibited(value: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in PROHIBITED_KEYS:
                errors.append(f"prohibited semantic/legacy field: {child_path}")
            errors.extend(_walk_for_prohibited(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(_walk_for_prohibited(child, f"{path}[{index}]"))
    return errors


def _duplicates(values: list[str]) -> list[str]:
    counts = Counter(values)
    return sorted(value for value, count in counts.items() if count > 1)


def _normalize_object(data: dict[str, Any]) -> dict[str, Any]:
    out = deepcopy(data)
    out["sources"] = sorted(out["sources"], key=lambda item: item["source_id"])
    for source in out["sources"]:
        source["context_facts"] = sorted(source["context_facts"], key=lambda item: item["fact_id"])
    out["passages"] = sorted(out["passages"], key=lambda item: item["passage_id"])
    for passage in out["passages"]:
        passage["anchors"] = sorted(
            passage["anchors"], key=lambda item: (item["type"], _json_key(item["value"]))
        )
    out["retrievals"] = sorted(out["retrievals"], key=lambda item: item["retrieval_id"])
    for retrieval in out["retrievals"]:
        retrieval["search_source_ids"] = sorted(retrieval["search_source_ids"])
        retrieval["limitations"] = sorted(retrieval["limitations"], key=_json_key)
    out["candidate_links"] = sorted(out["candidate_links"], key=lambda item: item["link_id"])
    for link in out["candidate_links"]:
        link["nominations"] = sorted(
            link["nominations"], key=lambda item: (item["retrieval_id"], item["rank"])
        )
    out["aperture"] = sorted(out["aperture"], key=lambda item: item["proposition_id"])
    for aperture in out["aperture"]:
        aperture["search_source_ids"] = sorted(aperture["search_source_ids"])
        aperture["limitations"] = sorted(aperture["limitations"], key=_json_key)
    return out


def canonical_bytes(bundle: Bundle, *, include_hash: bool = True) -> bytes:
    data = bundle.model_dump(mode="json")
    if not include_hash:
        data.pop("bundle_sha256", None)
    data = _normalize_object(data)
    return (
        json.dumps(
            data,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def compute_bundle_sha256(bundle: Bundle) -> str:
    return _hash_bytes(canonical_bytes(bundle, include_hash=False))


def seal(value: dict[str, Any]) -> dict[str, Any]:
    """Return a structurally parsed object with a fresh whole-object hash."""
    draft = deepcopy(value)
    draft["bundle_sha256"] = "sha256:" + "0" * 64
    bundle = Bundle.model_validate(draft)
    draft["bundle_sha256"] = compute_bundle_sha256(bundle)
    return draft


def _primary_targets(contract_a: dict[str, Any]) -> list[dict[str, Any]]:
    decomposition = contract_a["decomposition"]
    if decomposition["state"] == "declared":
        return sorted(decomposition["children"], key=lambda item: item["sequence"])
    return [contract_a["root_proposition"]]


def validate_bundle(value: Any, contract_a_value: Any) -> Bundle:
    """Validate RC0 structurally and against one exact valid Contract A 2.0 object."""
    try:
        contract_a = validate_contract_a(deepcopy(contract_a_value))
        bundle = Bundle.model_validate(value)
    except (ValidationError, ValueError, TypeError) as exc:
        raise CandidateValidationError(str(exc)) from exc

    errors = _walk_for_prohibited(bundle.model_dump(mode="json"))

    if bundle.bundle_sha256 != compute_bundle_sha256(bundle):
        errors.append("bundle_sha256 mismatch")

    if bundle.source_contract_a.version != CONTRACT_A_VERSION:
        errors.append("source Contract A public version mismatch")
    if bundle.source_contract_a.handoff_id != contract_a["handoff_id"]:
        errors.append("source Contract A handoff_id mismatch")
    if bundle.source_contract_a.handoff_sha256 != contract_a["handoff_sha256"]:
        errors.append("source Contract A handoff_sha256 mismatch")

    declaration = bundle.declaration.model_dump(mode="json")
    expected_declaration = {
        "root_proposition": contract_a["root_proposition"],
        "decomposition": contract_a["decomposition"],
    }
    if declaration != expected_declaration:
        errors.append("declaration does not exactly preserve Contract A root/decomposition authority")

    source_duplicates = _duplicates([source.source_id for source in bundle.sources])
    if source_duplicates:
        errors.append(f"duplicate source_id: {', '.join(source_duplicates)}")
    passage_duplicates = _duplicates([passage.passage_id for passage in bundle.passages])
    if passage_duplicates:
        errors.append(f"duplicate passage_id: {', '.join(passage_duplicates)}")
    retrieval_duplicates = _duplicates([item.retrieval_id for item in bundle.retrievals])
    if retrieval_duplicates:
        errors.append(f"duplicate retrieval_id: {', '.join(retrieval_duplicates)}")
    link_duplicates = _duplicates([item.link_id for item in bundle.candidate_links])
    if link_duplicates:
        errors.append(f"duplicate link_id: {', '.join(link_duplicates)}")
    aperture_duplicates = _duplicates([item.proposition_id for item in bundle.aperture])
    if aperture_duplicates:
        errors.append(f"duplicate aperture proposition_id: {', '.join(aperture_duplicates)}")

    a_sources = {source["source_id"]: source for source in contract_a["sources"]}
    b_sources = {source.source_id: source for source in bundle.sources}
    if set(a_sources) != set(b_sources):
        errors.append("B2 source IDs must exactly equal Contract A source IDs")
    for source_id, a_source in a_sources.items():
        b_source = b_sources.get(source_id)
        if b_source is None:
            continue
        if b_source.media_type != a_source["media_type"]:
            errors.append(f"source media_type mismatch: {source_id}")
        if b_source.content_sha256 != a_source["content_sha256"]:
            errors.append(f"source content_sha256 mismatch: {source_id}")
        fact_duplicates = _duplicates([fact.fact_id for fact in b_source.context_facts])
        if fact_duplicates:
            errors.append(f"duplicate fact_id in source {source_id}: {', '.join(fact_duplicates)}")

    passages = {passage.passage_id: passage for passage in bundle.passages}
    for passage in bundle.passages:
        a_source = a_sources.get(passage.source_id)
        if a_source is None:
            errors.append(f"passage references unknown Contract A source: {passage.passage_id}")
            continue
        if passage.text_sha256 != _hash_text(passage.text):
            errors.append(f"passage text_sha256 mismatch: {passage.passage_id}")
        source_bytes = a_source["content"].encode("utf-8")
        if passage.end_utf8_byte > len(source_bytes):
            errors.append(f"passage byte span exceeds source: {passage.passage_id}")
        else:
            actual = source_bytes[passage.start_utf8_byte : passage.end_utf8_byte]
            if actual != passage.text.encode("utf-8"):
                errors.append(f"passage bytes do not reconstruct from Contract A source: {passage.passage_id}")

    for source in bundle.sources:
        for fact in source.context_facts:
            passage = passages.get(fact.provenance_passage_id)
            if passage is None:
                errors.append(f"context fact references unknown passage: {fact.fact_id}")
            elif passage.source_id != source.source_id:
                errors.append(f"context fact crosses source boundary: {fact.fact_id}")

    targets = _primary_targets(contract_a)
    target_by_id = {target["proposition_id"]: target for target in targets}
    target_ids = set(target_by_id)

    retrievals = {item.retrieval_id: item for item in bundle.retrievals}
    for retrieval in bundle.retrievals:
        if retrieval.proposition_id not in target_ids:
            errors.append(f"retrieval references non-primary proposition: {retrieval.retrieval_id}")
        if retrieval.query.text_sha256 != _hash_text(retrieval.query.text):
            errors.append(f"query text_sha256 mismatch: {retrieval.retrieval_id}")
        if retrieval.query.origin == "exact_proposition_text":
            target = target_by_id.get(retrieval.proposition_id)
            if target is not None and retrieval.query.text != target["text"]:
                errors.append(f"exact proposition query changed target text: {retrieval.retrieval_id}")
        if len(retrieval.search_source_ids) != len(set(retrieval.search_source_ids)):
            errors.append(f"duplicate search source in retrieval: {retrieval.retrieval_id}")
        unknown_sources = set(retrieval.search_source_ids) - set(a_sources)
        if unknown_sources:
            errors.append(
                f"retrieval references unknown search source(s): {retrieval.retrieval_id}: {sorted(unknown_sources)}"
            )

    pair_seen: set[tuple[str, str]] = set()
    rank_slots: set[tuple[str, int]] = set()
    ranks_by_retrieval: dict[str, list[int]] = defaultdict(list)
    selected_orders: dict[str, list[int]] = defaultdict(list)

    for link in bundle.candidate_links:
        pair = (link.proposition_id, link.passage_id)
        if pair in pair_seen:
            errors.append(f"duplicate proposition-passage candidate link: {pair}")
        pair_seen.add(pair)
        if link.proposition_id not in target_ids:
            errors.append(f"candidate link references non-primary proposition: {link.link_id}")
        if link.passage_id not in passages:
            errors.append(f"candidate link references unknown passage: {link.link_id}")
        nomination_ids = [nomination.retrieval_id for nomination in link.nominations]
        duplicates = _duplicates(nomination_ids)
        if duplicates:
            errors.append(f"duplicate retrieval nomination in {link.link_id}: {', '.join(duplicates)}")
        for nomination in link.nominations:
            retrieval = retrievals.get(nomination.retrieval_id)
            if retrieval is None:
                errors.append(f"candidate nomination references unknown retrieval: {link.link_id}")
                continue
            if retrieval.proposition_id != link.proposition_id:
                errors.append(f"candidate nomination crosses proposition boundary: {link.link_id}")
            if nomination.rank > retrieval.candidate_limit:
                errors.append(f"candidate rank exceeds retrieval limit: {link.link_id}")
            slot = (nomination.retrieval_id, nomination.rank)
            if slot in rank_slots:
                errors.append(f"duplicate retrieval rank slot: {slot}")
            rank_slots.add(slot)
            ranks_by_retrieval[nomination.retrieval_id].append(nomination.rank)
        if link.selection.state == "selected":
            assert link.selection.order is not None
            selected_orders[link.proposition_id].append(link.selection.order)
        if link.review.state in {"accepted", "rejected", "needs_review"} and link.selection.state != "selected":
            errors.append(f"review/admission decision requires selection: {link.link_id}")

    for retrieval_id, retrieval in retrievals.items():
        ranks = sorted(ranks_by_retrieval.get(retrieval_id, []))
        if retrieval.execution_state == "failed" and ranks:
            errors.append(f"failed retrieval cannot nominate candidates: {retrieval_id}")
        if ranks and ranks != list(range(1, len(ranks) + 1)):
            errors.append(f"retrieval ranks must be contiguous from 1: {retrieval_id}")

    for proposition_id, orders in selected_orders.items():
        ordered = sorted(orders)
        if ordered != list(range(1, len(ordered) + 1)):
            errors.append(f"selection order must be contiguous from 1: {proposition_id}")

    aperture_by_target = {item.proposition_id: item for item in bundle.aperture}
    if set(aperture_by_target) != target_ids:
        errors.append("aperture must contain exactly one record per primary target")
    retrievals_by_target: dict[str, list[Retrieval]] = defaultdict(list)
    for retrieval in bundle.retrievals:
        retrievals_by_target[retrieval.proposition_id].append(retrieval)
    for proposition_id in target_ids:
        aperture = aperture_by_target.get(proposition_id)
        if aperture is None:
            continue
        if len(aperture.search_source_ids) != len(set(aperture.search_source_ids)):
            errors.append(f"duplicate aperture source: {proposition_id}")
        if set(aperture.search_source_ids) - set(a_sources):
            errors.append(f"aperture references unknown source: {proposition_id}")
        target_retrievals = retrievals_by_target.get(proposition_id, [])
        union_sources = sorted(
            {source_id for retrieval in target_retrievals for source_id in retrieval.search_source_ids}
        )
        if sorted(aperture.search_source_ids) != union_sources:
            errors.append(f"aperture source scope does not equal observed retrieval scope: {proposition_id}")
        states = [retrieval.execution_state for retrieval in target_retrievals]
        if aperture.execution_state == "not_run":
            if target_retrievals or aperture.search_source_ids:
                errors.append(f"not_run aperture must have no retrievals or source scope: {proposition_id}")
        elif aperture.execution_state == "complete":
            if not states or any(state != "completed" for state in states):
                errors.append(f"complete aperture requires completed retrieval executions: {proposition_id}")
        elif aperture.execution_state == "failed":
            if not states or any(state != "failed" for state in states):
                errors.append(f"failed aperture requires only failed retrieval executions: {proposition_id}")
        elif aperture.execution_state == "partial":
            if not states or all(state == "completed" for state in states) or all(state == "failed" for state in states):
                errors.append(f"partial aperture requires a non-uniform/non-complete execution set: {proposition_id}")

    if errors:
        raise CandidateValidationError("; ".join(errors))
    return bundle


def semantic_measurement_context(bundle: Bundle) -> dict[str, Any]:
    """Derive the narrow CAL-facing pre-assessment context from accepted evidence only."""
    source_by_id = {source.source_id: source for source in bundle.sources}
    passage_by_id = {passage.passage_id: passage for passage in bundle.passages}
    accepted_by_target: dict[str, list[Passage]] = defaultdict(list)
    for link in bundle.candidate_links:
        if link.review.state == "accepted":
            accepted_by_target[link.proposition_id].append(passage_by_id[link.passage_id])

    targets: list[dict[str, Any]] = []
    for proposition_id in sorted(accepted_by_target):
        passages: list[dict[str, Any]] = []
        for passage in sorted(accepted_by_target[proposition_id], key=lambda item: item.passage_id):
            source = source_by_id[passage.source_id]
            passages.append(
                {
                    "passage_id": passage.passage_id,
                    "source_id": passage.source_id,
                    "text": passage.text,
                    "text_sha256": passage.text_sha256,
                    "anchors": [anchor.model_dump(mode="json") for anchor in passage.anchors],
                    "source_context_facts": [
                        fact.model_dump(mode="json") for fact in source.context_facts
                    ],
                }
            )
        targets.append({"proposition_id": proposition_id, "accepted_passages": passages})
    return {"targets": targets}
