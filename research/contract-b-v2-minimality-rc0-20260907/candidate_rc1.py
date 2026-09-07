"""Research-only Contract B v2 minimality RC1 candidate.

RC1 is a successor to the falsified RC0 representation. It adds only planned
retrieval identity, requested/observed source scope, explicit not-run state and
returned candidate count. A separately stored aperture execution summary is
removed and derived from those lower-level receipts.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from copy import deepcopy
from typing import Any, Literal

from pydantic import ConfigDict, Field, ValidationError, model_validator

from candidate import (
    Anchor,
    CandidateLink,
    ContextFact,
    Declaration,
    Passage,
    PreparationProfile,
    Producer,
    Proposition,
    Query,
    SourceContractA,
    SourceRef,
    _Strict,
    _json_key,
    _walk_for_prohibited,
)
from validators.contract_a import CONTRACT_A_VERSION, validate_candidate as validate_contract_a

SCHEMA = "contract-b-v2-candidate-rc1"


class CandidateRC1ValidationError(ValueError):
    """Raised when the RC1 candidate fails structural or cross-A conformance."""


class KnownUnknown(_Strict):
    state: Literal["known", "unknown"]
    value: Any | None

    @model_validator(mode="after")
    def _state_value(self) -> "KnownUnknown":
        if self.state == "known" and self.value is None:
            raise ValueError("known requires non-null value")
        if self.state == "unknown" and self.value is not None:
            raise ValueError("unknown requires null value")
        return self


class TargetPlan(_Strict):
    proposition_id: str = Field(min_length=1)
    retrieval_ids: list[str]
    aperture_observation: KnownUnknown
    limitations: list[Any] = Field(default_factory=list)


class RetrievalRC1(_Strict):
    retrieval_id: str = Field(min_length=1)
    proposition_id: str = Field(min_length=1)
    lane_kind: str = Field(min_length=1)
    implementation_id: str = Field(min_length=1)
    query: Query
    candidate_limit: int = Field(gt=0)
    requested_source_ids: list[str]
    observed_source_ids: list[str]
    execution_state: Literal["completed", "partial", "failed", "not_run"]
    returned_count: int = Field(ge=0)
    limitations: list[Any] = Field(default_factory=list)


class BundleRC1(_Strict):
    model_config = ConfigDict(extra="forbid")

    schema: Literal["contract-b-v2-candidate-rc1"]
    bundle_id: str = Field(min_length=1)
    producer: Producer
    preparation_profile: PreparationProfile
    source_contract_a: SourceContractA
    declaration: Declaration
    sources: list[SourceRef]
    passages: list[Passage]
    target_plans: list[TargetPlan]
    retrievals: list[RetrievalRC1]
    candidate_links: list[CandidateLink]
    history_complete: Literal[True]
    bundle_sha256: str = Field(min_length=1)


def _hash_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _hash_text(value: str) -> str:
    return _hash_bytes(value.encode("utf-8"))


def _duplicates(values: list[str]) -> list[str]:
    counts = Counter(values)
    return sorted(value for value, count in counts.items() if count > 1)


def _primary_targets(contract_a: dict[str, Any]) -> list[dict[str, Any]]:
    decomposition = contract_a["decomposition"]
    if decomposition["state"] == "declared":
        return sorted(decomposition["children"], key=lambda item: item["sequence"])
    return [contract_a["root_proposition"]]


def _normalize(data: dict[str, Any]) -> dict[str, Any]:
    out = deepcopy(data)
    out["sources"] = sorted(out["sources"], key=lambda item: item["source_id"])
    for source in out["sources"]:
        source["context_facts"] = sorted(source["context_facts"], key=lambda item: item["fact_id"])
    out["passages"] = sorted(out["passages"], key=lambda item: item["passage_id"])
    for passage in out["passages"]:
        passage["anchors"] = sorted(
            passage["anchors"], key=lambda item: (item["type"], _json_key(item["value"]))
        )
    out["target_plans"] = sorted(out["target_plans"], key=lambda item: item["proposition_id"])
    for plan in out["target_plans"]:
        plan["retrieval_ids"] = sorted(plan["retrieval_ids"])
        plan["limitations"] = sorted(plan["limitations"], key=_json_key)
    out["retrievals"] = sorted(out["retrievals"], key=lambda item: item["retrieval_id"])
    for retrieval in out["retrievals"]:
        retrieval["requested_source_ids"] = sorted(retrieval["requested_source_ids"])
        retrieval["observed_source_ids"] = sorted(retrieval["observed_source_ids"])
        retrieval["limitations"] = sorted(retrieval["limitations"], key=_json_key)
    out["candidate_links"] = sorted(out["candidate_links"], key=lambda item: item["link_id"])
    for link in out["candidate_links"]:
        link["nominations"] = sorted(
            link["nominations"], key=lambda item: (item["retrieval_id"], item["rank"])
        )
    return out


def canonical_bytes(bundle: BundleRC1, *, include_hash: bool = True) -> bytes:
    data = bundle.model_dump(mode="json")
    if not include_hash:
        data.pop("bundle_sha256", None)
    data = _normalize(data)
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


def compute_bundle_sha256(bundle: BundleRC1) -> str:
    return _hash_bytes(canonical_bytes(bundle, include_hash=False))


def seal(value: dict[str, Any]) -> dict[str, Any]:
    draft = deepcopy(value)
    draft["bundle_sha256"] = "sha256:" + "0" * 64
    bundle = BundleRC1.model_validate(draft)
    draft["bundle_sha256"] = compute_bundle_sha256(bundle)
    return draft


def validate_bundle(value: Any, contract_a_value: Any) -> BundleRC1:
    try:
        contract_a = validate_contract_a(deepcopy(contract_a_value))
        bundle = BundleRC1.model_validate(value)
    except (ValidationError, ValueError, TypeError) as exc:
        raise CandidateRC1ValidationError(str(exc)) from exc

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
        errors.append(f"duplicate source_id: {source_duplicates}")
    passage_duplicates = _duplicates([passage.passage_id for passage in bundle.passages])
    if passage_duplicates:
        errors.append(f"duplicate passage_id: {passage_duplicates}")
    plan_duplicates = _duplicates([plan.proposition_id for plan in bundle.target_plans])
    if plan_duplicates:
        errors.append(f"duplicate target plan: {plan_duplicates}")
    retrieval_duplicates = _duplicates([retrieval.retrieval_id for retrieval in bundle.retrievals])
    if retrieval_duplicates:
        errors.append(f"duplicate retrieval_id: {retrieval_duplicates}")
    link_duplicates = _duplicates([link.link_id for link in bundle.candidate_links])
    if link_duplicates:
        errors.append(f"duplicate link_id: {link_duplicates}")

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
            errors.append(f"duplicate fact_id in source {source_id}: {fact_duplicates}")

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
    plan_by_target = {plan.proposition_id: plan for plan in bundle.target_plans}
    if set(plan_by_target) != target_ids:
        errors.append("target_plans must contain exactly one plan per primary target")

    planned_owner: dict[str, str] = {}
    for plan in bundle.target_plans:
        duplicates = _duplicates(plan.retrieval_ids)
        if duplicates:
            errors.append(f"duplicate retrieval ID in target plan {plan.proposition_id}: {duplicates}")
        for retrieval_id in plan.retrieval_ids:
            if retrieval_id in planned_owner:
                errors.append(f"retrieval planned by more than one target: {retrieval_id}")
            planned_owner[retrieval_id] = plan.proposition_id

    retrievals = {retrieval.retrieval_id: retrieval for retrieval in bundle.retrievals}
    if set(planned_owner) != set(retrievals):
        missing = sorted(set(planned_owner) - set(retrievals))
        unplanned = sorted(set(retrievals) - set(planned_owner))
        if missing:
            errors.append(f"planned retrieval record missing: {missing}")
        if unplanned:
            errors.append(f"unplanned retrieval record present: {unplanned}")

    for retrieval in bundle.retrievals:
        if retrieval.proposition_id not in target_ids:
            errors.append(f"retrieval references non-primary proposition: {retrieval.retrieval_id}")
        owner = planned_owner.get(retrieval.retrieval_id)
        if owner is not None and owner != retrieval.proposition_id:
            errors.append(f"retrieval proposition differs from target plan: {retrieval.retrieval_id}")
        if retrieval.query.text_sha256 != _hash_text(retrieval.query.text):
            errors.append(f"query text_sha256 mismatch: {retrieval.retrieval_id}")
        if retrieval.query.origin == "exact_proposition_text":
            target = target_by_id.get(retrieval.proposition_id)
            if target is not None and retrieval.query.text != target["text"]:
                errors.append(f"exact proposition query changed target text: {retrieval.retrieval_id}")

        if len(retrieval.requested_source_ids) != len(set(retrieval.requested_source_ids)):
            errors.append(f"duplicate requested source: {retrieval.retrieval_id}")
        if len(retrieval.observed_source_ids) != len(set(retrieval.observed_source_ids)):
            errors.append(f"duplicate observed source: {retrieval.retrieval_id}")
        requested = set(retrieval.requested_source_ids)
        observed = set(retrieval.observed_source_ids)
        if requested - set(a_sources):
            errors.append(f"retrieval requests unknown source: {retrieval.retrieval_id}")
        if observed - requested:
            errors.append(f"observed source outside requested scope: {retrieval.retrieval_id}")
        if retrieval.execution_state == "completed" and observed != requested:
            errors.append(f"completed retrieval must observe its full requested scope: {retrieval.retrieval_id}")
        if retrieval.execution_state == "not_run":
            if observed:
                errors.append(f"not_run retrieval cannot have observed sources: {retrieval.retrieval_id}")
            if retrieval.returned_count != 0:
                errors.append(f"not_run retrieval must return zero candidates: {retrieval.retrieval_id}")
        if retrieval.execution_state == "failed" and retrieval.returned_count != 0:
            errors.append(f"failed retrieval must return zero candidates: {retrieval.retrieval_id}")
        if retrieval.returned_count > retrieval.candidate_limit:
            errors.append(f"returned_count exceeds candidate_limit: {retrieval.retrieval_id}")

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
            errors.append(f"duplicate retrieval nomination in {link.link_id}: {duplicates}")
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
        expected = list(range(1, retrieval.returned_count + 1))
        if ranks != expected:
            errors.append(
                f"candidate nomination ranks must exactly match returned_count for {retrieval_id}: "
                f"observed={ranks}, expected={expected}"
            )

    for proposition_id, orders in selected_orders.items():
        ordered = sorted(orders)
        if ordered != list(range(1, len(ordered) + 1)):
            errors.append(f"selection order must be contiguous from 1: {proposition_id}")

    if errors:
        raise CandidateRC1ValidationError("; ".join(errors))
    return bundle


def derive_aperture(bundle: BundleRC1) -> list[dict[str, Any]]:
    """Derive target aperture execution state from plan + execution receipts."""
    retrieval_by_id = {retrieval.retrieval_id: retrieval for retrieval in bundle.retrievals}
    if bundle.declaration.decomposition["state"] == "declared":
        target_ids = [
            child["proposition_id"]
            for child in sorted(
                bundle.declaration.decomposition["children"], key=lambda item: item["sequence"]
            )
        ]
    else:
        target_ids = [bundle.declaration.root_proposition.proposition_id]
    plans = {plan.proposition_id: plan for plan in bundle.target_plans}

    output: list[dict[str, Any]] = []
    for proposition_id in target_ids:
        plan = plans[proposition_id]
        executions = [retrieval_by_id[item] for item in plan.retrieval_ids]
        states = [item.execution_state for item in executions]
        if not states or all(state == "not_run" for state in states):
            state = "not_run"
        elif all(state == "completed" for state in states):
            state = "complete"
        elif all(state == "failed" for state in states):
            state = "failed"
        else:
            state = "partial"
        requested = sorted({sid for item in executions for sid in item.requested_source_ids})
        observed = sorted({sid for item in executions for sid in item.observed_source_ids})
        output.append(
            {
                "proposition_id": proposition_id,
                "execution_state": state,
                "requested_source_ids": requested,
                "observed_source_ids": observed,
                "observation": plan.aperture_observation.model_dump(mode="json"),
                "limitations": deepcopy(plan.limitations),
            }
        )
    return output
