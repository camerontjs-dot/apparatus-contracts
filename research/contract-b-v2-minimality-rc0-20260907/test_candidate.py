from __future__ import annotations

import hashlib
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from candidate import (  # noqa: E402
    Bundle,
    CandidateValidationError,
    canonical_bytes,
    seal,
    validate_bundle,
)
from consumer_projection import semantic_measurement_context  # noqa: E402
from validators.contract_a import compute_handoff_sha256, validate_candidate  # noqa: E402

FIXTURES = ROOT / "fixtures" / "contract-a" / "2.0.0"


def _load(name: str) -> dict[str, Any]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _sha_text(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def _targets(a: dict[str, Any]) -> list[dict[str, Any]]:
    if a["decomposition"]["state"] == "declared":
        return sorted(a["decomposition"]["children"], key=lambda item: item["sequence"])
    return [a["root_proposition"]]


def _base_bundle(a: dict[str, Any], *, accepted: bool = True) -> dict[str, Any]:
    validate_candidate(deepcopy(a))
    sources = [
        {
            "source_id": source["source_id"],
            "media_type": source["media_type"],
            "content_sha256": source["content_sha256"],
            "context_facts": [],
        }
        for source in a["sources"]
    ]
    passages: list[dict[str, Any]] = []
    retrievals: list[dict[str, Any]] = []
    links: list[dict[str, Any]] = []
    aperture: list[dict[str, Any]] = []

    if not a["sources"]:
        for target in _targets(a):
            aperture.append(
                {
                    "proposition_id": target["proposition_id"],
                    "execution_state": "not_run",
                    "search_source_ids": [],
                    "limitations": ["no source representation supplied"],
                }
            )
    else:
        source = a["sources"][0]
        content = source["content"]
        passage_id = "pass-full-source-1"
        passages.append(
            {
                "passage_id": passage_id,
                "source_id": source["source_id"],
                "start_utf8_byte": 0,
                "end_utf8_byte": len(content.encode("utf-8")),
                "text": content,
                "text_sha256": _sha_text(content),
                "anchors": [{"type": "representation", "value": "full-source"}],
            }
        )
        sources[0]["context_facts"] = [
            {
                "fact_id": "fact-source-representation",
                "predicate": "representation_kind",
                "value": "supplied_contract_a_source",
                "assertion_mode": "mechanical",
                "provenance_passage_id": passage_id,
            }
        ]
        search_sources = [source_item["source_id"] for source_item in a["sources"]]
        for index, target in enumerate(_targets(a), start=1):
            for lane in ("bm25", "dense"):
                retrievals.append(
                    {
                        "retrieval_id": f"ret-{index}-{lane}",
                        "proposition_id": target["proposition_id"],
                        "lane_kind": lane,
                        "implementation_id": f"{lane}-fixture-v1",
                        "query": {
                            "query_id": f"q-{index}-{lane}",
                            "text": target["text"],
                            "text_sha256": _sha_text(target["text"]),
                            "origin": "exact_proposition_text",
                        },
                        "candidate_limit": 1,
                        "search_source_ids": search_sources,
                        "execution_state": "completed",
                        "limitations": [],
                    }
                )
            links.append(
                {
                    "link_id": f"link-{index}",
                    "proposition_id": target["proposition_id"],
                    "passage_id": passage_id,
                    "nominations": [
                        {"retrieval_id": f"ret-{index}-bm25", "rank": 1},
                        {"retrieval_id": f"ret-{index}-dense", "rank": 1},
                    ],
                    "selection": {"state": "selected", "order": 1},
                    "review": {"state": "accepted" if accepted else "rejected"},
                }
            )
            aperture.append(
                {
                    "proposition_id": target["proposition_id"],
                    "execution_state": "complete",
                    "search_source_ids": search_sources,
                    "limitations": [],
                }
            )

    return seal(
        {
            "schema": "contract-b-v2-candidate-rc0",
            "bundle_id": "bundle-b2-rc0-fixture",
            "producer": {
                "producer_id": "evidence-bundler",
                "producer_version": "research-rc0",
            },
            "preparation_profile": {
                "profile_id": "eb-a2-b2-minimal-pressure-v1",
                "profile_sha256": _sha_text("eb-a2-b2-minimal-pressure-v1"),
            },
            "source_contract_a": {
                "version": "2.0.0",
                "handoff_id": a["handoff_id"],
                "handoff_sha256": a["handoff_sha256"],
            },
            "declaration": {
                "root_proposition": deepcopy(a["root_proposition"]),
                "decomposition": deepcopy(a["decomposition"]),
            },
            "sources": sources,
            "passages": passages,
            "retrievals": retrievals,
            "candidate_links": links,
            "aperture": aperture,
            "history_complete": True,
            "bundle_sha256": "placeholder",
        }
    )


def _validate(b: dict[str, Any], a: dict[str, Any]) -> Bundle:
    return validate_bundle(b, a)


def _reseal(b: dict[str, Any]) -> dict[str, Any]:
    return seal(b)


def _expect_reject(b: dict[str, Any], a: dict[str, Any]) -> None:
    with pytest.raises(CandidateValidationError):
        _validate(_reseal(b), a)


def _add_second_candidate(b: dict[str, Any], target_index: int = 0) -> dict[str, Any]:
    out = deepcopy(b)
    first = deepcopy(out["passages"][0])
    first["passage_id"] = f"{first['passage_id']}-second"
    out["passages"].append(first)
    target = _targets_from_bundle(out)[target_index]
    target_id = target["proposition_id"]
    link = next(item for item in out["candidate_links"] if item["proposition_id"] == target_id)
    for nomination in link["nominations"]:
        retrieval = next(
            item for item in out["retrievals"] if item["retrieval_id"] == nomination["retrieval_id"]
        )
        retrieval["candidate_limit"] = 2
    out["candidate_links"].append(
        {
            "link_id": f"{link['link_id']}-second",
            "proposition_id": target_id,
            "passage_id": first["passage_id"],
            "nominations": [
                {"retrieval_id": nomination["retrieval_id"], "rank": 2}
                for nomination in link["nominations"]
            ],
            "selection": {"state": "not_selected", "order": None},
            "review": {"state": "not_reviewed"},
        }
    )
    return _reseal(out)


def _targets_from_bundle(b: dict[str, Any]) -> list[dict[str, Any]]:
    decomposition = b["declaration"]["decomposition"]
    if decomposition["state"] == "declared":
        return sorted(decomposition["children"], key=lambda item: item["sequence"])
    return [b["declaration"]["root_proposition"]]


@pytest.mark.parametrize(
    "fixture",
    [
        "valid-all-of.json",
        "valid-undecomposed.json",
        "valid-failed-decomposition.json",
        "valid-unknown-decomposition.json",
    ],
)
def test_valid_a2_states_round_trip_without_invented_legacy_fields(fixture: str) -> None:
    a = _load(fixture)
    b = _base_bundle(a)
    parsed = _validate(b, a)
    assert parsed.schema == "contract-b-v2-candidate-rc0"
    serialized = parsed.model_dump(mode="json")
    text = json.dumps(serialized, sort_keys=True)
    for key in (
        "scaffold_support_status",
        "scaffold_claim_strength",
        "scaffold_extraction_fidelity",
        "scaffold_counterevidence_found",
        "scaffold_downgraded",
        "audit_support_verdict",
    ):
        assert key not in text


def test_declared_targets_preserve_child_sequence_and_zero_admission_is_not_target_loss() -> None:
    a = _load("valid-all-of.json")
    b = _base_bundle(a, accepted=False)
    parsed = _validate(b, a)
    context = semantic_measurement_context(parsed)
    assert [item["proposition"]["proposition_id"] for item in context["targets"]] == [
        child["proposition_id"] for child in a["decomposition"]["children"]
    ]
    assert all(item["accepted_passages"] == [] for item in context["targets"])


def test_no_source_representation_is_explicit_not_run_with_target_preserved() -> None:
    a = _load("valid-undecomposed.json")
    a["sources"] = []
    a["handoff_sha256"] = compute_handoff_sha256(a)
    validate_candidate(deepcopy(a))
    b = _base_bundle(a)
    parsed = _validate(b, a)
    assert parsed.aperture[0].execution_state == "not_run"
    context = semantic_measurement_context(parsed)
    assert context["targets"][0]["proposition"]["proposition_id"] == a["root_proposition"]["proposition_id"]
    assert context["targets"][0]["accepted_passages"] == []


@pytest.mark.parametrize("mutation", ["reorder", "omit", "invent", "text", "hash"])
def test_a2_declaration_lineage_mutations_fail(mutation: str) -> None:
    a = _load("valid-all-of.json")
    b = _base_bundle(a)
    children = b["declaration"]["decomposition"]["children"]
    if mutation == "reorder":
        children.reverse()
    elif mutation == "omit":
        children.pop()
    elif mutation == "invent":
        invented = deepcopy(children[-1])
        invented["proposition_id"] = "invented-child"
        invented["sequence"] = 3
        children.append(invented)
    elif mutation == "text":
        children[0]["text"] += " altered"
        children[0]["text_sha256"] = _sha_text(children[0]["text"])
    elif mutation == "hash":
        children[0]["text_sha256"] = "sha256:" + "0" * 64
    _expect_reject(b, a)


def test_contract_a_handoff_substitution_fails_after_reseal() -> None:
    a = _load("valid-all-of.json")
    b = _base_bundle(a)
    b["source_contract_a"]["handoff_sha256"] = "sha256:" + "1" * 64
    _expect_reject(b, a)


@pytest.mark.parametrize("mutation", ["omit", "add", "hash"])
def test_contract_a_source_set_and_identity_mutations_fail(mutation: str) -> None:
    a = _load("valid-undecomposed.json")
    b = _base_bundle(a)
    if mutation == "omit":
        b["sources"] = []
    elif mutation == "add":
        extra = deepcopy(b["sources"][0])
        extra["source_id"] = "invented-source"
        b["sources"].append(extra)
    else:
        b["sources"][0]["content_sha256"] = "sha256:" + "2" * 64
    _expect_reject(b, a)


@pytest.mark.parametrize("mutation", ["start", "end", "text"])
def test_passage_provenance_mutations_fail(mutation: str) -> None:
    a = _load("valid-undecomposed.json")
    b = _base_bundle(a)
    passage = b["passages"][0]
    if mutation == "start":
        passage["start_utf8_byte"] += 1
    elif mutation == "end":
        passage["end_utf8_byte"] -= 1
    else:
        passage["text"] += "x"
        passage["text_sha256"] = _sha_text(passage["text"])
    _expect_reject(b, a)


def test_cross_source_passage_substitution_fails() -> None:
    a = _load("valid-undecomposed.json")
    second_content = "Different source representation."
    a["sources"].append(
        {
            "source_id": "src-two",
            "media_type": "text/plain; charset=utf-8",
            "content": second_content,
            "content_sha256": _sha_text(second_content),
        }
    )
    a["handoff_sha256"] = compute_handoff_sha256(a)
    validate_candidate(deepcopy(a))
    b = _base_bundle(a)
    b["passages"][0]["source_id"] = "src-two"
    _expect_reject(b, a)


def test_utf8_byte_coordinates_survive_non_ascii_source() -> None:
    a = _load("valid-undecomposed.json")
    content = "Café supplier résumé: ✅ qualified."
    a["sources"][0]["content"] = content
    a["sources"][0]["content_sha256"] = _sha_text(content)
    a["handoff_sha256"] = compute_handoff_sha256(a)
    validate_candidate(deepcopy(a))
    b = _base_bundle(a)
    parsed = _validate(b, a)
    assert parsed.passages[0].end_utf8_byte == len(content.encode("utf-8"))

    wrong = deepcopy(b)
    wrong["passages"][0]["end_utf8_byte"] = len(content)
    _expect_reject(wrong, a)


def test_exact_proposition_query_cannot_be_rewritten_even_with_fresh_hash() -> None:
    a = _load("valid-undecomposed.json")
    b = _base_bundle(a)
    query = b["retrievals"][0]["query"]
    query["text"] = "convenient rewritten query"
    query["text_sha256"] = _sha_text(query["text"])
    _expect_reject(b, a)


def test_declared_root_cannot_silently_become_primary_retrieval_target() -> None:
    a = _load("valid-all-of.json")
    b = _base_bundle(a)
    retrieval = b["retrievals"][0]
    retrieval["proposition_id"] = a["root_proposition"]["proposition_id"]
    retrieval["query"]["text"] = a["root_proposition"]["text"]
    retrieval["query"]["text_sha256"] = a["root_proposition"]["text_sha256"]
    _expect_reject(b, a)


def test_retrieval_rank_gap_fails() -> None:
    a = _load("valid-undecomposed.json")
    b = _base_bundle(a)
    for retrieval in b["retrievals"]:
        retrieval["candidate_limit"] = 2
    for nomination in b["candidate_links"][0]["nominations"]:
        nomination["rank"] = 2
    _expect_reject(b, a)


def test_duplicate_retrieval_rank_slot_fails() -> None:
    a = _load("valid-undecomposed.json")
    b = _add_second_candidate(_base_bundle(a))
    second = next(link for link in b["candidate_links"] if link["link_id"].endswith("-second"))
    for nomination in second["nominations"]:
        nomination["rank"] = 1
    _expect_reject(b, a)


def test_cross_proposition_nomination_fails() -> None:
    a = _load("valid-all-of.json")
    b = _base_bundle(a)
    first, second = b["candidate_links"][:2]
    first["nominations"][0]["retrieval_id"] = second["nominations"][0]["retrieval_id"]
    _expect_reject(b, a)


def test_unselected_candidate_cannot_have_review_decision() -> None:
    a = _load("valid-undecomposed.json")
    b = _base_bundle(a)
    b["candidate_links"][0]["selection"] = {"state": "not_selected", "order": None}
    with pytest.raises(ValidationError):
        _reseal(b)


def test_selection_order_gap_fails() -> None:
    a = _load("valid-undecomposed.json")
    b = _base_bundle(a)
    b["candidate_links"][0]["selection"]["order"] = 2
    _expect_reject(b, a)


def test_failed_retrieval_cannot_nominate_candidates() -> None:
    a = _load("valid-undecomposed.json")
    b = _base_bundle(a)
    for retrieval in b["retrievals"]:
        retrieval["execution_state"] = "failed"
    b["aperture"][0]["execution_state"] = "failed"
    _expect_reject(b, a)


@pytest.mark.parametrize("mutation", ["missing", "scope", "state"])
def test_aperture_mutations_fail(mutation: str) -> None:
    a = _load("valid-all-of.json")
    b = _base_bundle(a)
    if mutation == "missing":
        b["aperture"].pop()
    elif mutation == "scope":
        b["aperture"][0]["search_source_ids"] = []
    else:
        b["retrievals"][0]["execution_state"] = "partial"
    _expect_reject(b, a)


def test_rejected_candidate_remains_recoverable_but_not_semantic_input() -> None:
    a = _load("valid-undecomposed.json")
    b = _base_bundle(a, accepted=False)
    parsed = _validate(b, a)
    assert len(parsed.passages) == 1
    assert parsed.candidate_links[0].review.state == "rejected"
    context = semantic_measurement_context(parsed)
    assert len(context["targets"]) == 1
    assert context["targets"][0]["accepted_passages"] == []


def test_nomination_rank_mutation_is_semantic_context_invariant_when_admission_is_fixed() -> None:
    a = _load("valid-undecomposed.json")
    b1 = _add_second_candidate(_base_bundle(a))
    parsed1 = _validate(b1, a)
    context1 = semantic_measurement_context(parsed1)

    b2 = deepcopy(b1)
    links = sorted(b2["candidate_links"], key=lambda item: item["link_id"])
    for retrieval_id in [item["retrieval_id"] for item in links[0]["nominations"]]:
        first_nom = next(n for n in links[0]["nominations"] if n["retrieval_id"] == retrieval_id)
        second_nom = next(n for n in links[1]["nominations"] if n["retrieval_id"] == retrieval_id)
        first_nom["rank"], second_nom["rank"] = second_nom["rank"], first_nom["rank"]
    parsed2 = _validate(_reseal(b2), a)
    assert semantic_measurement_context(parsed2) == context1


def test_admission_state_changes_semantic_context_without_rewriting_history() -> None:
    a = _load("valid-undecomposed.json")
    accepted = _base_bundle(a, accepted=True)
    rejected = deepcopy(accepted)
    rejected["candidate_links"][0]["review"]["state"] = "rejected"
    rejected = _reseal(rejected)
    accepted_context = semantic_measurement_context(_validate(accepted, a))
    rejected_context = semantic_measurement_context(_validate(rejected, a))
    assert accepted_context != rejected_context
    assert rejected_context["targets"][0]["accepted_passages"] == []
    assert len(_validate(rejected, a).passages) == 1


def test_prohibited_semantic_field_nested_in_factual_value_fails() -> None:
    a = _load("valid-undecomposed.json")
    b = _base_bundle(a)
    b["sources"][0]["context_facts"][0]["value"] = {"support": "yes"}
    _expect_reject(b, a)


def test_context_fact_and_anchor_reach_semantic_context_as_facts_not_judgments() -> None:
    a = _load("valid-undecomposed.json")
    parsed = _validate(_base_bundle(a), a)
    context = semantic_measurement_context(parsed)
    admitted = context["targets"][0]["accepted_passages"][0]
    assert admitted["anchors"] == [{"type": "representation", "value": "full-source"}]
    assert admitted["source_context_facts"][0]["predicate"] == "representation_kind"
    assert "retrieval_id" not in json.dumps(context)
    assert "rank" not in json.dumps(context)


@pytest.mark.parametrize(
    "where,key,value",
    [
        ("top", "history_count_checks", []),
        ("declaration", "atomicity", {"state": "known", "value": "atomic"}),
        ("nomination", "raw_score", 0.99),
    ],
)
def test_ablated_field_families_fail_closed(where: str, key: str, value: Any) -> None:
    a = _load("valid-undecomposed.json")
    b = _base_bundle(a)
    if where == "top":
        b[key] = value
    elif where == "declaration":
        b["declaration"][key] = value
    else:
        b["candidate_links"][0]["nominations"][0][key] = value
    with pytest.raises(ValidationError):
        _reseal(b)


def test_canonical_permutation_is_byte_equivalent_but_declared_child_order_is_not_normalized_away() -> None:
    a = _load("valid-all-of.json")
    b = _base_bundle(a)
    parsed = _validate(b, a)

    permuted = deepcopy(b)
    permuted["retrievals"].reverse()
    permuted["candidate_links"].reverse()
    permuted["aperture"].reverse()
    for link in permuted["candidate_links"]:
        link["nominations"].reverse()
    permuted = _reseal(permuted)
    parsed_permuted = _validate(permuted, a)
    assert canonical_bytes(parsed_permuted) == canonical_bytes(parsed)

    hostile = deepcopy(b)
    hostile["declaration"]["decomposition"]["children"].reverse()
    _expect_reject(hostile, a)


def test_stale_whole_object_hash_fails_and_resealed_nomination_metadata_does_not_change_semantic_input() -> None:
    a = _load("valid-undecomposed.json")
    b = _base_bundle(a)
    before = semantic_measurement_context(_validate(b, a))

    stale = deepcopy(b)
    stale["retrievals"][0]["lane_kind"] = "renamed-diagnostic-lane"
    with pytest.raises(CandidateValidationError, match="bundle_sha256 mismatch"):
        _validate(stale, a)

    resealed = _reseal(stale)
    after = semantic_measurement_context(_validate(resealed, a))
    assert after == before


def test_history_complete_is_required_true() -> None:
    a = _load("valid-undecomposed.json")
    b = _base_bundle(a)
    b["history_complete"] = False
    with pytest.raises(ValidationError):
        _reseal(b)
