#!/usr/bin/env python3
"""Final bounded driver for the Contract B -> CAL temporal/version experiment.

This driver reuses the original research fixture helpers and the exact pinned
Evidence Bundler minimal-context consumer. It corrects only a brittle list-order
assertion discovered in the preregistered harness. Canonical Contract B and CAL
production code are not modified.
"""

from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

APPARATUS_BASE_SHA = "f4ee2dbd853821ba54328156bbab1c71235fae55"
EB_SHA = "b4ca9111f5957ef7e7955e2c5024f2280ee19eb5"
CAL_SHA = "6acc3462dad73959ccec6bccf8407215f5274cf6"


def load_original() -> Any:
    path = Path(__file__).with_name("contract_b_temporal_version_applicability.py")
    spec = importlib.util.spec_from_file_location("temporal_original", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def entailer_args_from_source(cal_root: Path) -> list[str]:
    source = (cal_root / "src/claim_audit_lab/v1/protocols.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "Entailer":
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child.name == "entail":
                    return [arg.arg for arg in child.args.args]
    raise AssertionError("Pinned CAL Entailer.entail protocol not found")


def by_id(items: list[dict[str, Any]], key: str, value: str) -> dict[str, Any]:
    return next(item for item in items if item[key] == value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-bundler-root", type=Path, required=True)
    parser.add_argument("--cal-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    sys.path.insert(0, str((args.evidence_bundler_root / "src").resolve()))
    from evidence_bundler.experiments.contract_b_seam_probe import (  # noqa: PLC0415
        build_cal_measurement_view,
        build_handoff_variant,
        canonical_hash as eb_canonical_hash,
        find_audit_judgment_keys,
        validate_fixture,
    )

    orig = load_original()

    pinned_fixture = yaml.safe_load(
        (args.evidence_bundler_root / "examples/contract-b-seam/tri-repo-fixture.yaml").read_text(
            encoding="utf-8"
        )
    )
    allowed_statuses = {
        item["temporal_applicability"]
        for item in pinned_fixture["cal_research_sidecar"]["assessments"]
    }
    assert {"stale_for_current_state", "current"} <= allowed_statuses

    world_a = orig.make_world("1.0", "2026-01-10")
    world_b = orig.make_world("2.0", "2026-07-01")

    # T1: exact existing EB fixture validation plus explicit source-text consistency.
    validate_fixture(world_a)
    validate_fixture(world_b)
    consistency_a = orig.source_text_consistency(world_a)
    consistency_b = orig.source_text_consistency(world_b)
    assert consistency_a["status"] == "pass"
    assert consistency_b["status"] == "pass"

    handoff_a = build_handoff_variant(world_a, "minimal_context")
    handoff_b = build_handoff_variant(world_b, "minimal_context")
    view_a = build_cal_measurement_view(handoff_a)
    view_b = build_cal_measurement_view(handoff_b)
    handoff_hash_a = eb_canonical_hash(handoff_a)
    handoff_hash_b = eb_canonical_hash(handoff_b)

    # T2: inspect the pinned CAL protocol source directly. Structured provenance is
    # not an argument to semantic entailment. A/B text is allowed to differ.
    entailer_args = entailer_args_from_source(args.cal_root)
    assert entailer_args == ["self", "claim", "premise", "passage_id"]
    semantic_a = orig.semantic_payload(view_a)
    semantic_b = orig.semantic_payload(view_b)
    semantic_hash_a = orig.canonical_hash(semantic_a)
    semantic_hash_b = orig.canonical_hash(semantic_b)
    assert semantic_a != semantic_b

    # T3/T4: no proposition-specific temporal judgment crosses in minimal context;
    # CAL-owned research receipt derives applicability from provenance-bound facts.
    assert find_audit_judgment_keys(handoff_a) == set()
    assert find_audit_judgment_keys(handoff_b) == set()
    receipt_a = orig.temporal_receipt(
        world_a, allowed_statuses=allowed_statuses, input_hash=handoff_hash_a
    )
    receipt_b = orig.temporal_receipt(
        world_b, allowed_statuses=allowed_statuses, input_hash=handoff_hash_b
    )
    assert receipt_a["status"] == "stale_for_current_state"
    assert receipt_b["status"] == "current"
    assert receipt_a["policy_receipt_sha256"] == receipt_b["policy_receipt_sha256"]
    assert receipt_a["receipt_sha256"] != receipt_b["receipt_sha256"]

    # T5: old evidence remains retained even when not current-state deciding evidence.
    decision_a = orig.decision_view(view_a, receipt_a)
    decision_b = orig.decision_view(view_b, receipt_b)
    assert "psg-validation" in decision_a["retained_ledger_passage_ids"]
    assert "psg-validation" not in decision_a["current_state_validation_basis"]
    assert "psg-validation" in decision_b["current_state_validation_basis"]

    # T6: compare by stable IDs, not list positions. Only the validation fact cluster
    # changes; unrelated supplier evidence remains byte-equivalent in the projection.
    changed_paths = orig.diff_paths(handoff_a, handoff_b)
    assert len(changed_paths) == 5, changed_paths
    supplier_source_a = by_id(view_a["sources"], "source_id", "src-supplier")
    supplier_source_b = by_id(view_b["sources"], "source_id", "src-supplier")
    supplier_passage_a = by_id(view_a["admitted_passages"], "passage_id", "psg-supplier")
    supplier_passage_b = by_id(view_b["admitted_passages"], "passage_id", "psg-supplier")
    assert supplier_source_a == supplier_source_b
    assert supplier_passage_a == supplier_passage_b
    validation_source_a = by_id(view_a["sources"], "source_id", "src-validation")
    validation_source_b = by_id(view_b["sources"], "source_id", "src-validation")
    validation_passage_a = by_id(view_a["admitted_passages"], "passage_id", "psg-validation")
    validation_passage_b = by_id(view_b["admitted_passages"], "passage_id", "psg-validation")
    assert validation_source_a != validation_source_b
    assert validation_passage_a != validation_passage_b

    # Negative control: change metadata to v2 while keeping the v1 passage. Recompute
    # the source hash so failure cannot be attributed merely to stale hash bytes.
    negative = deepcopy(world_a)
    validation_source = by_id(negative["sources"], "source_id", "src-validation")
    for fact in validation_source["context_facts"]:
        if fact["predicate"] == "system_version":
            fact["value"] = "2.0"
    orig.recompute_validation_source_hash(negative)
    validate_fixture(negative)
    negative_consistency = orig.source_text_consistency(negative)
    assert negative_consistency["status"] == "conflict"
    assert [item["code"] for item in negative_consistency["conflicts"]] == [
        "system_version_conflict"
    ]
    negative_handoff = build_handoff_variant(negative, "minimal_context")
    negative_view = build_cal_measurement_view(negative_handoff)
    semantic_negative = orig.semantic_payload(negative_view)
    assert semantic_negative == semantic_a
    negative_receipt = orig.temporal_receipt(
        negative,
        allowed_statuses=allowed_statuses,
        input_hash=eb_canonical_hash(negative_handoff),
    )
    assert negative_receipt["status"] is None
    assert negative_receipt["disposition"] == "refused"
    assert negative_receipt["reason"] == "source_context_conflict"

    decision_model_source = (
        args.cal_root / "src/claim_audit_lab/v1/decision_model.py"
    ).read_text(encoding="utf-8")
    typed_temporal_receipt = "TemporalApplicabilityAssessment" in decision_model_source

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
            "cal_entailer_args": entailer_args,
            "semantic_payload_hash_a": semantic_hash_a,
            "semantic_payload_hash_b": semantic_hash_b,
            "a_b_payload_equal": semantic_a == semantic_b,
            "numeric_cal_nli_scores": "not_executed",
            "reason": (
                "A/B passage text legitimately differs. Metadata isolation is tested "
                "by the negative control, whose exact claim/premise/passage_id payload "
                "matches World A."
            ),
        },
        "T3_applicability_sensitivity": {"world_a": receipt_a, "world_b": receipt_b},
        "T4_receipt_attribution": {
            "handoff_a_audit_judgment_keys": sorted(find_audit_judgment_keys(handoff_a)),
            "handoff_b_audit_judgment_keys": sorted(find_audit_judgment_keys(handoff_b)),
            "world_a_receipt": receipt_a["receipt_sha256"],
            "world_b_receipt": receipt_b["receipt_sha256"],
            "shared_policy_receipt": receipt_a["policy_receipt_sha256"],
            "temporal_receipt_is_currently_typed_in_pinned_cal": typed_temporal_receipt,
        },
        "T5_preservation": {"world_a": decision_a, "world_b": decision_b},
        "T6_counterfactual": {
            "changed_handoff_paths": changed_paths,
            "changed_path_count": len(changed_paths),
            "world_a_status": receipt_a["status"],
            "world_b_status": receipt_b["status"],
            "supplier_source_unchanged": supplier_source_a == supplier_source_b,
            "supplier_passage_unchanged": supplier_passage_a == supplier_passage_b,
        },
        "negative_control": {
            "eb_fixture_validation": "pass",
            "source_text_consistency": negative_consistency,
            "semantic_payload_hash": orig.canonical_hash(semantic_negative),
            "semantic_payload_equal_to_world_a": semantic_negative == semantic_a,
            "assessment": negative_receipt,
        },
        "research_vocabulary_observed": sorted(allowed_statuses),
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
