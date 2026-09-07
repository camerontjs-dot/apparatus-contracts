from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from candidate_rc1 import (  # noqa: E402
    BundleRC1,
    CandidateRC1ValidationError,
    canonical_bytes,
    derive_aperture,
    seal,
    validate_bundle,
)
from consumer_projection import semantic_measurement_context  # noqa: E402
from test_candidate import _base_bundle, _load, _sha_text, _targets  # noqa: E402
from validators.contract_a import compute_handoff_sha256, validate_candidate  # noqa: E402


def _from_rc0(a: dict[str, Any], *, accepted: bool = True) -> dict[str, Any]:
    rc0 = _base_bundle(a, accepted=accepted)
    target_plans = []
    for target in _targets(a):
        target_id = target["proposition_id"]
        retrieval_ids = [
            retrieval["retrieval_id"]
            for retrieval in rc0["retrievals"]
            if retrieval["proposition_id"] == target_id
        ]
        target_plans.append(
            {
                "proposition_id": target_id,
                "retrieval_ids": retrieval_ids,
                "aperture_observation": {"state": "unknown", "value": None},
                "limitations": [],
            }
        )

    nominations_by_retrieval: dict[str, int] = {}
    for link in rc0["candidate_links"]:
        for nomination in link["nominations"]:
            retrieval_id = nomination["retrieval_id"]
            nominations_by_retrieval[retrieval_id] = nominations_by_retrieval.get(retrieval_id, 0) + 1

    retrievals = []
    for retrieval in rc0["retrievals"]:
        retrievals.append(
            {
                "retrieval_id": retrieval["retrieval_id"],
                "proposition_id": retrieval["proposition_id"],
                "lane_kind": retrieval["lane_kind"],
                "implementation_id": retrieval["implementation_id"],
                "query": deepcopy(retrieval["query"]),
                "candidate_limit": retrieval["candidate_limit"],
                "requested_source_ids": deepcopy(retrieval["search_source_ids"]),
                "observed_source_ids": deepcopy(retrieval["search_source_ids"]),
                "execution_state": retrieval["execution_state"],
                "returned_count": nominations_by_retrieval.get(retrieval["retrieval_id"], 0),
                "limitations": deepcopy(retrieval["limitations"]),
            }
        )

    return seal(
        {
            "schema": "contract-b-v2-candidate-rc1",
            "bundle_id": rc0["bundle_id"],
            "producer": deepcopy(rc0["producer"]),
            "preparation_profile": deepcopy(rc0["preparation_profile"]),
            "source_contract_a": deepcopy(rc0["source_contract_a"]),
            "declaration": deepcopy(rc0["declaration"]),
            "sources": deepcopy(rc0["sources"]),
            "passages": deepcopy(rc0["passages"]),
            "target_plans": target_plans,
            "retrievals": retrievals,
            "candidate_links": deepcopy(rc0["candidate_links"]),
            "history_complete": True,
            "bundle_sha256": "placeholder",
        }
    )


def _validate(b: dict[str, Any], a: dict[str, Any]) -> BundleRC1:
    return validate_bundle(b, a)


def _reject_after_reseal(b: dict[str, Any], a: dict[str, Any]) -> None:
    with pytest.raises(CandidateRC1ValidationError):
        _validate(seal(b), a)


def _add_second_candidate(b: dict[str, Any]) -> dict[str, Any]:
    out = deepcopy(b)
    passage = deepcopy(out["passages"][0])
    passage["passage_id"] = f"{passage['passage_id']}-second"
    out["passages"].append(passage)
    link = deepcopy(out["candidate_links"][0])
    link["link_id"] = f"{link['link_id']}-second"
    link["passage_id"] = passage["passage_id"]
    link["selection"] = {"state": "not_selected", "order": None}
    link["review"] = {"state": "not_reviewed"}
    for nomination in link["nominations"]:
        nomination["rank"] = 2
        retrieval = next(
            item for item in out["retrievals"] if item["retrieval_id"] == nomination["retrieval_id"]
        )
        retrieval["candidate_limit"] = 2
        retrieval["returned_count"] = 2
    out["candidate_links"].append(link)
    return seal(out)


@pytest.mark.parametrize(
    "fixture",
    [
        "valid-all-of.json",
        "valid-undecomposed.json",
        "valid-failed-decomposition.json",
        "valid-unknown-decomposition.json",
    ],
)
def test_rc1_represents_all_a2_target_states_without_legacy_semantic_fields(fixture: str) -> None:
    a = _load(fixture)
    parsed = _validate(_from_rc0(a), a)
    text = json.dumps(parsed.model_dump(mode="json"), sort_keys=True)
    for forbidden in (
        "scaffold_support_status",
        "scaffold_claim_strength",
        "scaffold_extraction_fidelity",
        "scaffold_counterevidence_found",
        "scaffold_downgraded",
        "audit_support_verdict",
    ):
        assert forbidden not in text


def test_rc1_closes_rc0_silent_lane_omission_counterexample() -> None:
    a = _load("valid-undecomposed.json")
    b = _from_rc0(a)
    omitted_id = "ret-1-dense"
    b["retrievals"] = [r for r in b["retrievals"] if r["retrieval_id"] != omitted_id]
    for link in b["candidate_links"]:
        link["nominations"] = [n for n in link["nominations"] if n["retrieval_id"] != omitted_id]
    _reject_after_reseal(b, a)


def test_rc1_represents_planned_but_not_run_lane_and_derives_partial_aperture() -> None:
    a = _load("valid-undecomposed.json")
    b = _from_rc0(a)
    retrieval = next(item for item in b["retrievals"] if item["retrieval_id"] == "ret-1-dense")
    retrieval["execution_state"] = "not_run"
    retrieval["observed_source_ids"] = []
    retrieval["returned_count"] = 0
    for link in b["candidate_links"]:
        link["nominations"] = [n for n in link["nominations"] if n["retrieval_id"] != retrieval["retrieval_id"]]
    parsed = _validate(seal(b), a)
    aperture = derive_aperture(parsed)
    assert aperture[0]["execution_state"] == "partial"
    assert retrieval["retrieval_id"] in parsed.target_plans[0].retrieval_ids


def test_rc1_all_planned_not_run_is_distinct_from_missing_plan() -> None:
    a = _load("valid-undecomposed.json")
    b = _from_rc0(a)
    for retrieval in b["retrievals"]:
        retrieval["execution_state"] = "not_run"
        retrieval["observed_source_ids"] = []
        retrieval["returned_count"] = 0
    b["candidate_links"] = []
    parsed = _validate(seal(b), a)
    assert derive_aperture(parsed)[0]["execution_state"] == "not_run"

    missing = deepcopy(b)
    missing_id = missing["target_plans"][0]["retrieval_ids"].pop()
    missing["retrievals"] = [r for r in missing["retrievals"] if r["retrieval_id"] != missing_id]
    # Coordinated plan+record removal is structurally valid. Detecting whether the
    # producer lied about its externally frozen profile remains producer conformance.
    _validate(seal(missing), a)


def test_rc1_closes_rc0_silent_tail_candidate_truncation_counterexample() -> None:
    a = _load("valid-undecomposed.json")
    b = _add_second_candidate(_from_rc0(a))
    second = next(link for link in b["candidate_links"] if link["link_id"].endswith("-second"))
    second_passage_id = second["passage_id"]
    b["candidate_links"] = [link for link in b["candidate_links"] if link["link_id"] != second["link_id"]]
    b["passages"] = [p for p in b["passages"] if p["passage_id"] != second_passage_id]
    _reject_after_reseal(b, a)


@pytest.mark.parametrize("delta", [-1, 1])
def test_returned_count_must_equal_complete_nomination_ledger(delta: int) -> None:
    a = _load("valid-undecomposed.json")
    b = _from_rc0(a)
    b["retrievals"][0]["returned_count"] += delta
    if b["retrievals"][0]["returned_count"] < 0:
        with pytest.raises(ValidationError):
            seal(b)
    else:
        _reject_after_reseal(b, a)


def test_completed_retrieval_requires_observed_scope_equal_requested_scope() -> None:
    a = _load("valid-undecomposed.json")
    b = _from_rc0(a)
    b["retrievals"][0]["observed_source_ids"] = []
    _reject_after_reseal(b, a)


def test_observed_source_cannot_escape_requested_scope() -> None:
    a = _load("valid-undecomposed.json")
    b = _from_rc0(a)
    b["retrievals"][0]["observed_source_ids"].append("invented-source")
    _reject_after_reseal(b, a)


def test_known_unknown_aperture_observation_is_preserved_without_semantic_authority() -> None:
    a = _load("valid-undecomposed.json")
    b = _from_rc0(a)
    b["target_plans"][0]["aperture_observation"] = {
        "state": "known",
        "value": {"search_window": "supplied-source-representations-only"},
    }
    parsed = _validate(seal(b), a)
    aperture = derive_aperture(parsed)
    assert aperture[0]["observation"]["state"] == "known"
    assert aperture[0]["observation"]["value"]["search_window"] == "supplied-source-representations-only"


def test_unknown_aperture_observation_requires_null() -> None:
    a = _load("valid-undecomposed.json")
    b = _from_rc0(a)
    b["target_plans"][0]["aperture_observation"] = {"state": "unknown", "value": "invented"}
    with pytest.raises(ValidationError):
        seal(b)


def test_separate_stored_aperture_summary_is_ablated_and_fails_closed() -> None:
    a = _load("valid-undecomposed.json")
    b = _from_rc0(a)
    b["aperture"] = []
    with pytest.raises(ValidationError):
        seal(b)


def test_target_plan_must_exist_for_every_primary_target() -> None:
    a = _load("valid-all-of.json")
    b = _from_rc0(a)
    b["target_plans"].pop()
    _reject_after_reseal(b, a)


def test_unplanned_retrieval_record_fails() -> None:
    a = _load("valid-undecomposed.json")
    b = _from_rc0(a)
    extra = deepcopy(b["retrievals"][0])
    extra["retrieval_id"] = "unplanned-retrieval"
    extra["query"]["query_id"] = "unplanned-query"
    extra["returned_count"] = 0
    extra["execution_state"] = "not_run"
    extra["observed_source_ids"] = []
    b["retrievals"].append(extra)
    _reject_after_reseal(b, a)


def test_planned_retrieval_cannot_cross_proposition_target() -> None:
    a = _load("valid-all-of.json")
    b = _from_rc0(a)
    first_plan, second_plan = b["target_plans"]
    moved = first_plan["retrieval_ids"][0]
    first_plan["retrieval_ids"].remove(moved)
    second_plan["retrieval_ids"].append(moved)
    _reject_after_reseal(b, a)


def test_a2_declared_child_reorder_still_fails() -> None:
    a = _load("valid-all-of.json")
    b = _from_rc0(a)
    b["declaration"]["decomposition"]["children"].reverse()
    _reject_after_reseal(b, a)


def test_passage_byte_provenance_still_fails_on_off_by_one() -> None:
    a = _load("valid-undecomposed.json")
    b = _from_rc0(a)
    b["passages"][0]["start_utf8_byte"] += 1
    _reject_after_reseal(b, a)


def test_exact_proposition_query_rewrite_still_fails() -> None:
    a = _load("valid-undecomposed.json")
    b = _from_rc0(a)
    query = b["retrievals"][0]["query"]
    query["text"] = "rewritten"
    query["text_sha256"] = _sha_text(query["text"])
    _reject_after_reseal(b, a)


def test_rejected_evidence_remains_recoverable_and_target_remains_in_semantic_projection() -> None:
    a = _load("valid-undecomposed.json")
    parsed = _validate(_from_rc0(a, accepted=False), a)
    assert parsed.candidate_links[0].review.state == "rejected"
    context = semantic_measurement_context(parsed)  # type: ignore[arg-type]
    assert len(context["targets"]) == 1
    assert context["targets"][0]["accepted_passages"] == []


def test_rank_only_permutation_is_semantic_projection_invariant_with_fixed_admission() -> None:
    a = _load("valid-undecomposed.json")
    b1 = _add_second_candidate(_from_rc0(a))
    parsed1 = _validate(b1, a)
    context1 = semantic_measurement_context(parsed1)  # type: ignore[arg-type]

    b2 = deepcopy(b1)
    links = sorted(b2["candidate_links"], key=lambda item: item["link_id"])
    for retrieval_id in [n["retrieval_id"] for n in links[0]["nominations"]]:
        n1 = next(n for n in links[0]["nominations"] if n["retrieval_id"] == retrieval_id)
        n2 = next(n for n in links[1]["nominations"] if n["retrieval_id"] == retrieval_id)
        n1["rank"], n2["rank"] = n2["rank"], n1["rank"]
    parsed2 = _validate(seal(b2), a)
    assert semantic_measurement_context(parsed2) == context1  # type: ignore[arg-type]


def test_admission_change_alters_semantic_projection_but_keeps_candidate_history() -> None:
    a = _load("valid-undecomposed.json")
    accepted = _from_rc0(a)
    rejected = deepcopy(accepted)
    rejected["candidate_links"][0]["review"]["state"] = "rejected"
    rejected = seal(rejected)
    before = semantic_measurement_context(_validate(accepted, a))  # type: ignore[arg-type]
    after_parsed = _validate(rejected, a)
    after = semantic_measurement_context(after_parsed)  # type: ignore[arg-type]
    assert before != after
    assert after["targets"][0]["accepted_passages"] == []
    assert len(after_parsed.candidate_links) == 1


@pytest.mark.parametrize(
    "where,key,value",
    [
        ("top", "history_count_checks", []),
        ("declaration", "atomicity", {"state": "known", "value": "atomic"}),
        ("nomination", "raw_score", 0.99),
    ],
)
def test_rc1_still_fails_closed_on_ablated_field_families(where: str, key: str, value: Any) -> None:
    a = _load("valid-undecomposed.json")
    b = _from_rc0(a)
    if where == "top":
        b[key] = value
    elif where == "declaration":
        b["declaration"][key] = value
    else:
        b["candidate_links"][0]["nominations"][0][key] = value
    with pytest.raises(ValidationError):
        seal(b)


def test_prohibited_semantic_field_cannot_hide_in_aperture_observation() -> None:
    a = _load("valid-undecomposed.json")
    b = _from_rc0(a)
    b["target_plans"][0]["aperture_observation"] = {
        "state": "known",
        "value": {"support": "yes"},
    }
    _reject_after_reseal(b, a)


def test_rc1_canonical_permutation_is_byte_equivalent() -> None:
    a = _load("valid-all-of.json")
    b = _from_rc0(a)
    parsed = _validate(b, a)
    permuted = deepcopy(b)
    permuted["retrievals"].reverse()
    permuted["target_plans"].reverse()
    permuted["candidate_links"].reverse()
    for plan in permuted["target_plans"]:
        plan["retrieval_ids"].reverse()
    for link in permuted["candidate_links"]:
        link["nominations"].reverse()
    parsed_permuted = _validate(seal(permuted), a)
    assert canonical_bytes(parsed) == canonical_bytes(parsed_permuted)


def test_rc1_stale_whole_object_hash_fails_and_reseal_preserves_nonsemantic_invariance() -> None:
    a = _load("valid-undecomposed.json")
    b = _from_rc0(a)
    before = semantic_measurement_context(_validate(b, a))  # type: ignore[arg-type]
    stale = deepcopy(b)
    stale["retrievals"][0]["implementation_id"] = "different-versioned-implementation"
    with pytest.raises(CandidateRC1ValidationError, match="bundle_sha256 mismatch"):
        _validate(stale, a)
    after = semantic_measurement_context(_validate(seal(stale), a))  # type: ignore[arg-type]
    assert before == after


def test_rc1_unicode_source_still_uses_utf8_byte_coordinates() -> None:
    a = _load("valid-undecomposed.json")
    content = "Café supplier résumé: ✅ qualified."
    a["sources"][0]["content"] = content
    a["sources"][0]["content_sha256"] = _sha_text(content)
    a["handoff_sha256"] = compute_handoff_sha256(a)
    validate_candidate(deepcopy(a))
    parsed = _validate(_from_rc0(a), a)
    assert parsed.passages[0].end_utf8_byte == len(content.encode("utf-8"))
