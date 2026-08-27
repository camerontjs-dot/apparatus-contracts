#!/usr/bin/env python3
"""Contract B -> CAL temporal/version applicability seam experiment.

Research-only. This runner does not modify canonical Contract B or CAL production
behavior. It reuses the pinned Evidence Bundler minimal-context projection and
adds only an experiment-local CAL temporal/lifecycle assessment receipt.
"""

from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import re
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

APPARATUS_BASE_SHA = "f4ee2dbd853821ba54328156bbab1c71235fae55"
EB_SHA = "b4ca9111f5957ef7e7955e2c5024f2280ee19eb5"
CAL_SHA = "6acc3462dad73959ccec6bccf8407215f5274cf6"
POLICY_ID = "cal-temporal-lifecycle-shadow-v1"


def canonical_hash(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def text_hash(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def make_world(version: str, validation_date: str) -> dict[str, Any]:
    claim_text = (
        "The currently deployed v2 model is adequately validated for release "
        "under the audited policy."
    )
    validation_text = (
        f"Model version {version} passed the recorded validation protocol on "
        f"{validation_date}."
    )
    supplier_text = "Acme Models Ltd is recorded as qualified in the supplier record."

    validation_facts = [
        {
            "fact_id": "fact-validation-version",
            "predicate": "system_version",
            "value": version,
            "assertion_mode": "source_declared",
            "provenance": {"passage_id": "psg-validation"},
        },
        {
            "fact_id": "fact-validation-date",
            "predicate": "validation_date",
            "value": validation_date,
            "assertion_mode": "source_declared",
            "provenance": {"passage_id": "psg-validation"},
        },
    ]
    supplier_facts = [
        {
            "fact_id": "fact-supplier-status",
            "predicate": "supplier_qualification_status",
            "value": "qualified",
            "assertion_mode": "source_declared",
            "provenance": {"passage_id": "psg-supplier"},
        }
    ]

    validation_source_hash = canonical_hash(
        {
            "title": "Validation report",
            "source_type": "validation_report",
            "context_facts": validation_facts,
            "passage_text": validation_text,
        }
    )
    supplier_source_hash = canonical_hash(
        {
            "title": "Supplier qualification record",
            "source_type": "supplier_record",
            "context_facts": supplier_facts,
            "passage_text": supplier_text,
        }
    )

    return {
        "fixture_schema": "contract-b-temporal-applicability-shadow-v1",
        "status": "research_only",
        "prototype_only": True,
        "bundle": {
            "bundle_id": "temporal-seam-pair-001",
            "purpose": "current_state_validation_audit",
            "created_at_utc": "2026-08-27T12:20:00Z",
            "claim_id": "clm-current-validation",
        },
        "claim": {
            "claim_id": "clm-current-validation",
            "claim_text": claim_text,
            "claim_form": "assertion",
            "atomicity": "composite",
            "origin": {"kind": "external"},
        },
        "required_mechanical_fact_ids": [
            "fact-validation-version",
            "fact-validation-date",
            "fact-supplier-status",
        ],
        "sources": [
            {
                "source_id": "src-validation",
                "title": "Validation report",
                "source_type": "validation_report",
                "content_hash": validation_source_hash,
                "source_trust_level": "primary",
                "context_facts": validation_facts,
            },
            {
                "source_id": "src-supplier",
                "title": "Supplier qualification record",
                "source_type": "supplier_record",
                "content_hash": supplier_source_hash,
                "source_trust_level": "primary",
                "context_facts": supplier_facts,
            },
        ],
        "passages": [
            {
                "passage_id": "psg-validation",
                "source_id": "src-validation",
                "text": validation_text,
                "passage_hash": text_hash(validation_text),
                "anchors": [{"type": "section", "value": "validation-summary"}],
            },
            {
                "passage_id": "psg-supplier",
                "source_id": "src-supplier",
                "text": supplier_text,
                "passage_hash": text_hash(supplier_text),
                "anchors": [{"type": "record_id", "value": "SUP-17"}],
            },
        ],
        "links": [
            {
                "link_id": "lnk-validation",
                "claim_id": "clm-current-validation",
                "passage_id": "psg-validation",
                "nomination": {
                    "method": "hybrid",
                    "retrieval_run_id": "temporal-run-001",
                    "rank": 1,
                    "scores": {"fusion": 0.91},
                    "hypothesized_role": "support_candidate",
                },
                "review": {
                    "decision": "accepted",
                    "review_basis": "audit_relevance_and_excerpt_sufficiency",
                    "reviewed_by": "temporal-shadow",
                    "reviewed_at_utc": "2026-08-27T12:20:00Z",
                    "notes": "Validation evidence admitted; CAL decides applicability.",
                },
            },
            {
                "link_id": "lnk-supplier",
                "claim_id": "clm-current-validation",
                "passage_id": "psg-supplier",
                "nomination": {
                    "method": "hybrid",
                    "retrieval_run_id": "temporal-run-001",
                    "rank": 2,
                    "scores": {"fusion": 0.80},
                    "hypothesized_role": "qualifier_candidate",
                },
                "review": {
                    "decision": "accepted",
                    "review_basis": "audit_relevance_and_excerpt_sufficiency",
                    "reviewed_by": "temporal-shadow",
                    "reviewed_at_utc": "2026-08-27T12:20:00Z",
                    "notes": "Frozen unrelated evidence for preservation control.",
                },
            },
        ],
        "coverage": {
            "claim_id": "clm-current-validation",
            "search_scope": {
                "source_ids": ["src-validation", "src-supplier"],
                "closed_world": True,
                "source_selection_basis": "supplied_fixture",
            },
            "candidate_count": 2,
            "reviewed_count": 2,
            "admitted_count": 2,
            "outcome": "admitted",
            "limitations": ["Synthetic fixture; tests seam semantics only."],
        },
        # Required only by the existing EB research fixture validator. It carries
        # no proposition-specific judgment values and never enters minimal_context.
        "cal_research_sidecar": {
            "assessments": [
                {"passage_id": "psg-validation"},
                {"passage_id": "psg-supplier"},
            ],
            "aperture_assessment": {},
        },
    }


VERSION_RE = re.compile(r"\bversion\s+(\d+(?:\.\d+)?)\b", re.IGNORECASE)
DATE_RE = re.compile(r"\b(20\d{2}-\d{2}-\d{2})\b")
TARGET_RE = re.compile(r"\bdeployed\s+v(\d+(?:\.\d+)?)\b", re.IGNORECASE)


def normalize_version(value: str) -> str:
    return value if "." in value else value + ".0"


def source_text_consistency(world: dict[str, Any]) -> dict[str, Any]:
    passages = {item["passage_id"]: item for item in world["passages"]}
    conflicts: list[dict[str, Any]] = []
    checked: list[dict[str, Any]] = []

    for source in world["sources"]:
        if source["source_type"] != "validation_report":
            continue
        facts = {item["predicate"]: item for item in source["context_facts"]}
        version_fact = facts.get("system_version")
        date_fact = facts.get("validation_date")
        passage_id = (
            version_fact.get("provenance", {}).get("passage_id")
            if version_fact is not None
            else None
        )
        if passage_id not in passages:
            conflicts.append(
                {
                    "code": "validation_fact_missing_provenance",
                    "source_id": source["source_id"],
                }
            )
            continue

        text = passages[passage_id]["text"]
        text_version_match = VERSION_RE.search(text)
        text_date_match = DATE_RE.search(text)
        row = {
            "source_id": source["source_id"],
            "passage_id": passage_id,
            "metadata_version": version_fact.get("value") if version_fact else None,
            "text_version": text_version_match.group(1) if text_version_match else None,
            "metadata_date": date_fact.get("value") if date_fact else None,
            "text_date": text_date_match.group(1) if text_date_match else None,
        }
        checked.append(row)
        if row["metadata_version"] != row["text_version"]:
            conflicts.append({"code": "system_version_conflict", **row})
        if row["metadata_date"] != row["text_date"]:
            conflicts.append({"code": "validation_date_conflict", **row})

    return {
        "status": "pass" if not conflicts else "conflict",
        "checked": checked,
        "conflicts": conflicts,
    }


def semantic_payload(measurement_view: dict[str, Any]) -> dict[str, str]:
    passage = next(
        item
        for item in measurement_view["admitted_passages"]
        if item["passage_id"] == "psg-validation"
    )
    return {
        "claim": measurement_view["claim"]["claim_text"],
        "premise": passage["text"],
        "passage_id": passage["passage_id"],
    }


def claim_target_version(claim_text: str) -> str | None:
    match = TARGET_RE.search(claim_text)
    return normalize_version(match.group(1)) if match else None


def temporal_receipt(
    world: dict[str, Any], *, allowed_statuses: set[str], input_hash: str
) -> dict[str, Any]:
    consistency = source_text_consistency(world)
    policy_spec = {
        "policy_id": POLICY_ID,
        "family": "temporal_lifecycle_applicability",
        "rule": (
            "For a current-state validation proposition with an explicit target "
            "system version, a provenance-bound validation record is current only "
            "when its source-declared system_version matches the audited target; a "
            "mismatching historical version is stale_for_current_state. Refuse "
            "assessment on source-text consistency conflict."
        ),
        "age_cutoff": "none_defined",
    }
    policy_hash = canonical_hash(policy_spec)

    if consistency["status"] != "pass":
        body = {
            "assessment_family": "temporal_lifecycle_applicability",
            "status": None,
            "disposition": "refused",
            "reason": "source_context_conflict",
            "conflicts": consistency["conflicts"],
            "policy_id": POLICY_ID,
            "policy_receipt_sha256": policy_hash,
            "input_artifact_hash": input_hash,
        }
        return {**body, "receipt_sha256": canonical_hash(body)}

    target = claim_target_version(world["claim"]["claim_text"])
    if target is None:
        body = {
            "assessment_family": "temporal_lifecycle_applicability",
            "status": None,
            "disposition": "refused",
            "reason": "audited_target_version_unresolved",
            "policy_id": POLICY_ID,
            "policy_receipt_sha256": policy_hash,
            "input_artifact_hash": input_hash,
        }
        return {**body, "receipt_sha256": canonical_hash(body)}

    validation_source = next(
        item for item in world["sources"] if item["source_type"] == "validation_report"
    )
    facts = {item["predicate"]: item for item in validation_source["context_facts"]}
    version = normalize_version(str(facts["system_version"]["value"]))
    validation_date = str(facts["validation_date"]["value"])
    status = "current" if version == target else "stale_for_current_state"
    if status not in allowed_statuses:
        raise AssertionError(f"Temporal status {status!r} is not in pinned CAL research vocabulary")

    body = {
        "assessment_family": "temporal_lifecycle_applicability",
        "status": status,
        "disposition": "assessed",
        "reason": (
            "provenance_bound_system_version_matches_audited_target"
            if status == "current"
            else "provenance_bound_system_version_differs_from_audited_target"
        ),
        "claim_id": world["claim"]["claim_id"],
        "target_system_version": target,
        "affected_contribution": "psg-validation",
        "factual_inputs": [
            {
                "fact_id": facts["system_version"]["fact_id"],
                "predicate": "system_version",
                "value": version,
                "provenance": facts["system_version"]["provenance"],
            },
            {
                "fact_id": facts["validation_date"]["fact_id"],
                "predicate": "validation_date",
                "value": validation_date,
                "provenance": facts["validation_date"]["provenance"],
            },
        ],
        "policy_id": POLICY_ID,
        "policy_receipt_sha256": policy_hash,
        "input_artifact_hash": input_hash,
    }
    return {**body, "receipt_sha256": canonical_hash(body)}


def recompute_validation_source_hash(world: dict[str, Any]) -> None:
    source = next(item for item in world["sources"] if item["source_id"] == "src-validation")
    passage = next(item for item in world["passages"] if item["passage_id"] == "psg-validation")
    source["content_hash"] = canonical_hash(
        {
            "title": source["title"],
            "source_type": source["source_type"],
            "context_facts": source["context_facts"],
            "passage_text": passage["text"],
        }
    )


def diff_paths(left: Any, right: Any, path: str = "$") -> list[str]:
    changed: list[str] = []
    if type(left) is not type(right):
        return [path]
    if isinstance(left, dict):
        for key in sorted(set(left) | set(right)):
            child = f"{path}.{key}"
            if key not in left or key not in right:
                changed.append(child)
            else:
                changed.extend(diff_paths(left[key], right[key], child))
        return changed
    if isinstance(left, list):
        if len(left) != len(right):
            changed.append(path + ".length")
        for index, (a_item, b_item) in enumerate(zip(left, right, strict=False)):
            changed.extend(diff_paths(a_item, b_item, f"{path}[{index}]"))
        return changed
    if left != right:
        changed.append(path)
    return changed


def decision_view(measurement_view: dict[str, Any], receipt: dict[str, Any]) -> dict[str, Any]:
    retained = tuple(sorted(item["passage_id"] for item in measurement_view["admitted_passages"]))
    basis = ("psg-validation",) if receipt.get("status") == "current" else ()
    return {
        "retained_ledger_passage_ids": retained,
        "current_state_validation_basis": basis,
        "non_deciding_preserved": tuple(item for item in retained if item not in basis),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-bundler-root", type=Path, required=True)
    parser.add_argument("--cal-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    eb_src = args.evidence_bundler_root / "src"
    sys.path.insert(0, str(eb_src.resolve()))
    sys.path.insert(0, str((args.cal_root / "src").resolve()))

    from evidence_bundler.experiments.contract_b_seam_probe import (  # noqa: PLC0415
        build_cal_measurement_view,
        build_handoff_variant,
        canonical_hash as eb_canonical_hash,
        find_audit_judgment_keys,
        validate_fixture,
    )
    from claim_audit_lab.v1.protocols import Entailer  # noqa: PLC0415

    # Recover temporal vocabulary from the pinned CAL-only research sidecar rather
    # than inventing a new status enum for this test.
    source_fixture = yaml.safe_load(
        (
            args.evidence_bundler_root
            / "examples/contract-b-seam/tri-repo-fixture.yaml"
        ).read_text(encoding="utf-8")
    )
    allowed_temporal_statuses = {
        item["temporal_applicability"]
        for item in source_fixture["cal_research_sidecar"]["assessments"]
    }
    assert "stale_for_current_state" in allowed_temporal_statuses
    assert "current" in allowed_temporal_statuses

    world_a = make_world("1.0", "2026-01-10")
    world_b = make_world("2.0", "2026-07-01")

    # T1: exact pinned EB seam fixture validation plus explicit source-text
    # consistency. The latter is separate because the existing EB validator is
    # structural/referential and does not semantically compare fact values to text.
    validate_fixture(world_a)
    validate_fixture(world_b)
    consistency_a = source_text_consistency(world_a)
    consistency_b = source_text_consistency(world_b)
    assert consistency_a["status"] == "pass"
    assert consistency_b["status"] == "pass"

    handoff_a = build_handoff_variant(world_a, "minimal_context")
    handoff_b = build_handoff_variant(world_b, "minimal_context")
    view_a = build_cal_measurement_view(handoff_a)
    view_b = build_cal_measurement_view(handoff_b)
    handoff_hash_a = eb_canonical_hash(handoff_a)
    handoff_hash_b = eb_canonical_hash(handoff_b)

    # T2: the exact CAL Entailer interface accepts only claim, premise and passage
    # ID. Numeric DeBERTa execution is intentionally not introduced here; text
    # changes between A/B are allowed to change NLI scores. The metadata-only
    # negative control below must leave this semantic payload unchanged.
    entailer_signature = str(inspect.signature(Entailer.entail))
    assert "claim" in entailer_signature
    assert "premise" in entailer_signature
    assert "passage_id" in entailer_signature
    semantic_a = semantic_payload(view_a)
    semantic_b = semantic_payload(view_b)
    semantic_hash_a = canonical_hash(semantic_a)
    semantic_hash_b = canonical_hash(semantic_b)
    assert semantic_a != semantic_b

    # T3/T4: derive a CAL-owned shadow assessment from factual context. Minimal
    # handoff contains no proposition-specific judgment key.
    assert find_audit_judgment_keys(handoff_a) == set()
    assert find_audit_judgment_keys(handoff_b) == set()
    receipt_a = temporal_receipt(
        world_a,
        allowed_statuses=allowed_temporal_statuses,
        input_hash=handoff_hash_a,
    )
    receipt_b = temporal_receipt(
        world_b,
        allowed_statuses=allowed_temporal_statuses,
        input_hash=handoff_hash_b,
    )
    assert receipt_a["status"] == "stale_for_current_state"
    assert receipt_b["status"] == "current"
    assert receipt_a["policy_receipt_sha256"] == receipt_b["policy_receipt_sha256"]
    assert receipt_a["receipt_sha256"] != receipt_b["receipt_sha256"]

    # T5: non-deciding stale evidence remains in the retained audit ledger.
    decision_a = decision_view(view_a, receipt_a)
    decision_b = decision_view(view_b, receipt_b)
    assert "psg-validation" in decision_a["retained_ledger_passage_ids"]
    assert "psg-validation" not in decision_a["current_state_validation_basis"]
    assert "psg-validation" in decision_b["current_state_validation_basis"]

    # T6: A -> B changes the complete internally consistent fact cluster while
    # unrelated supplier evidence remains byte-equivalent in the research view.
    changed_paths = diff_paths(handoff_a, handoff_b)
    expected_changed_suffixes = {
        "$.passages[0].passage_hash",
        "$.passages[0].text",
        "$.sources[0].content_hash",
        "$.sources[0].context_facts[0].value",
        "$.sources[0].context_facts[1].value",
    }
    assert set(changed_paths) == expected_changed_suffixes, changed_paths
    supplier_source_a = next(item for item in view_a["sources"] if item["source_id"] == "src-supplier")
    supplier_source_b = next(item for item in view_b["sources"] if item["source_id"] == "src-supplier")
    supplier_passage_a = next(
        item for item in view_a["admitted_passages"] if item["passage_id"] == "psg-supplier"
    )
    supplier_passage_b = next(
        item for item in view_b["admitted_passages"] if item["passage_id"] == "psg-supplier"
    )
    assert supplier_source_a == supplier_source_b
    assert supplier_passage_a == supplier_passage_b

    # Negative control: structured metadata says v2 while source passage still
    # says v1. Recompute the source hash so ordinary structural/hash consistency
    # cannot reject it for the wrong reason. The explicit consistency layer must.
    negative = deepcopy(world_a)
    validation_source = next(
        item for item in negative["sources"] if item["source_id"] == "src-validation"
    )
    for fact in validation_source["context_facts"]:
        if fact["predicate"] == "system_version":
            fact["value"] = "2.0"
    recompute_validation_source_hash(negative)
    validate_fixture(negative)
    negative_consistency = source_text_consistency(negative)
    assert negative_consistency["status"] == "conflict"
    assert [item["code"] for item in negative_consistency["conflicts"]] == [
        "system_version_conflict"
    ]
    negative_handoff = build_handoff_variant(negative, "minimal_context")
    negative_view = build_cal_measurement_view(negative_handoff)
    semantic_negative = semantic_payload(negative_view)
    assert semantic_negative == semantic_a
    negative_receipt = temporal_receipt(
        negative,
        allowed_statuses=allowed_temporal_statuses,
        input_hash=eb_canonical_hash(negative_handoff),
    )
    assert negative_receipt["status"] is None
    assert negative_receipt["disposition"] == "refused"
    assert negative_receipt["reason"] == "source_context_conflict"

    cal_decision_model = (
        args.cal_root / "src/claim_audit_lab/v1/decision_model.py"
    ).read_text(encoding="utf-8")
    temporal_receipt_is_currently_typed_in_cal = "TemporalApplicabilityAssessment" in cal_decision_model

    result = {
        "experiment": "contract-b-cal-temporal-version-applicability-v1",
        "status": "research_only",
        "pins": {
            "apparatus_base": APPARATUS_BASE_SHA,
            "evidence_bundler": EB_SHA,
            "claim_audit_lab": CAL_SHA,
        },
        "T1_integrity": {
            "world_a_eb_fixture_validation": "pass",
            "world_b_eb_fixture_validation": "pass",
            "world_a_source_text_consistency": consistency_a,
            "world_b_source_text_consistency": consistency_b,
            "handoff_hash_a": handoff_hash_a,
            "handoff_hash_b": handoff_hash_b,
        },
        "T2_semantic_relation_isolation": {
            "cal_entailer_signature": entailer_signature,
            "semantic_payload_hash_a": semantic_hash_a,
            "semantic_payload_hash_b": semantic_hash_b,
            "a_b_payload_equal": semantic_a == semantic_b,
            "numeric_cal_nli_scores": "not_executed",
            "reason": (
                "A/B passage text legitimately differs. The test isolates metadata by "
                "the negative control, whose exact claim/premise/passage_id payload "
                "matches A."
            ),
        },
        "T3_applicability_sensitivity": {
            "world_a": receipt_a,
            "world_b": receipt_b,
        },
        "T4_receipt_attribution": {
            "handoff_a_audit_judgment_keys": sorted(find_audit_judgment_keys(handoff_a)),
            "handoff_b_audit_judgment_keys": sorted(find_audit_judgment_keys(handoff_b)),
            "world_a_receipt": receipt_a["receipt_sha256"],
            "world_b_receipt": receipt_b["receipt_sha256"],
            "shared_policy_receipt": receipt_a["policy_receipt_sha256"],
            "temporal_receipt_is_currently_typed_in_pinned_cal": temporal_receipt_is_currently_typed_in_cal,
        },
        "T5_preservation": {"world_a": decision_a, "world_b": decision_b},
        "T6_counterfactual": {
            "changed_handoff_paths": changed_paths,
            "world_a_status": receipt_a["status"],
            "world_b_status": receipt_b["status"],
            "supplier_source_unchanged": supplier_source_a == supplier_source_b,
            "supplier_passage_unchanged": supplier_passage_a == supplier_passage_b,
        },
        "negative_control": {
            "eb_fixture_validation": "pass",
            "source_text_consistency": negative_consistency,
            "semantic_payload_hash": canonical_hash(semantic_negative),
            "semantic_payload_equal_to_world_a": semantic_negative == semantic_a,
            "assessment": negative_receipt,
        },
        "research_vocabulary_observed": sorted(allowed_temporal_statuses),
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
