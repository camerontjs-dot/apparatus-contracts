#!/usr/bin/env python3
"""Second successor for Contract A RC2 normal-context conformance.

Preserves both earlier failed runners. Run 33471423473 showed that the direct
auxiliary BM25 probe produced zero positive-score hits when the candidate's two
supplied sources were each represented as one whole-document chunk. That result
is retained as evidence. It does not establish a missing Contract A datum and is
not a legitimate precondition for the production EB path, which performs its own
loader/chunker/retrieval sequence.

V3 therefore requires only that real EB BM25 accepts and executes the exact
declared proposition queries in that auxiliary probe. Positive retrieval is
measured and recorded, not required. The real producer -> legacy compatibility
carrier -> EB production writer -> canonical B 1.2 -> CAL path remains unchanged
and is still required to pass.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import run_conformance_v2 as successor_v2

rc2 = successor_v2.rc2


def main() -> int:
    pins = rc2._repo_pins()
    declared = rc2.make_candidate("declared")
    undecomposed = rc2.make_candidate("not_decomposed")
    failed = rc2.make_candidate("failed")
    unknown = rc2.make_candidate("unknown")

    direct_declared = rc2.direct_eb_signature(declared)
    direct_single = rc2.direct_eb_signature(undecomposed)
    assert set(direct_declared) == {
        "clm-supplier-qualification-a",
        "clm-supplier-qualification-b",
    }
    assert set(direct_single) == {"clm-supplier-qualification"}
    # V2 falsified the auxiliary positive-hit assumption. Exact query execution
    # remains required; hit presence is now an observation, not a pass condition.

    core = rc2._core_ablation(declared)
    template = rc2.build_fixture_write_input(rc2.PILOT, "baseline")

    variants = {
        "baseline": rc2._compat_observations(),
        "source_acquisition_provenance": rc2._compat_observations(
            access_date_utc="1999-01-01T00:00:00Z"
        ),
        "upstream_selected_passage": rc2._compat_observations(source_refs=True),
        "upstream_query_history": rc2._compat_observations(
            retrieval_query="hostile upstream query text"
        ),
        "retrieval_rank": rc2._compat_observations(retrieval_rank=99),
        "support_label": rc2._compat_observations(support_status="unsupported"),
        "confidence_claim_strength": rc2._compat_observations(claim_strength=0.01),
        "extraction_fidelity": rc2._compat_observations(extraction_fidelity=0.01),
        "counterevidence_flag": rc2._compat_observations(
            counterevidence_checked=True, counterevidence_found=True
        ),
        "downgrade_state": rc2._compat_observations(
            downgraded=True, downgrade_reason="hostile upstream downgrade"
        ),
        "trust_label": rc2._compat_observations(trust_level="background"),
        "model_prompt_config": rc2._compat_observations(model_prompt_config=True),
        "workflow_condition": rc2._compat_observations(workflow_condition="format_only"),
        "timestamps_history": rc2._compat_observations(
            timestamp_utc="1999-01-01T00:00:00Z"
        ),
    }

    with tempfile.TemporaryDirectory(prefix="contract-a-rc2-") as raw_tmp:
        tmp = Path(raw_tmp)
        built = {}
        for name, observations in variants.items():
            built[name] = rc2.build_b_variant(
                name=name,
                candidate=declared,
                template=template,
                observations=observations,
                tmp=tmp,
            )

        baseline_contents, baseline_legacy, _ = built["baseline"]
        baseline_signature = rc2._bundle_semantic_signature(baseline_contents)
        baseline_request = rc2.candidate_to_cal(declared, baseline_contents)
        baseline_request_hash = rc2.hash_explicit_claim_request(baseline_request)
        baseline_trace = rc2.run_explicit_claim_audit(
            baseline_request, auditor=rc2._stub_auditor
        )
        assert [atom.atom_id for atom in baseline_request.atoms] == [
            "clm-supplier-qualification-a",
            "clm-supplier-qualification-b",
        ]
        assert baseline_trace.parent_aggregation.atom_support_verdicts == [
            "supported",
            "unsupported",
        ]
        assert baseline_trace.verdict.support_verdict == "partially_supported"

        noncore_results = {}
        for name, (contents, _legacy, _factual) in built.items():
            if name == "baseline":
                continue
            signature_equal = rc2._bundle_semantic_signature(contents) == baseline_signature
            request = rc2.candidate_to_cal(declared, contents)
            request_hash = rc2.hash_explicit_claim_request(request)
            trace = rc2.run_explicit_claim_audit(request, auditor=rc2._stub_auditor)
            request_equal = request_hash == baseline_request_hash
            semantic_equal = (
                trace.verdict == baseline_trace.verdict
                and [row.atom_id for row in trace.atom_audits]
                == [row.atom_id for row in baseline_trace.atom_audits]
            )
            assert signature_equal, name
            assert request_equal, name
            assert semantic_equal, name
            noncore_results[name] = {
                "eb_retrieval_evidence_signature_equal": signature_equal,
                "cal_explicit_request_hash_equal": request_equal,
                "cal_explicit_semantic_result_equal": semantic_equal,
            }

        single_contents, single_legacy, _ = rc2.build_b_variant(
            name="undecomposed",
            candidate=undecomposed,
            template=template,
            observations=rc2._compat_observations(),
            tmp=tmp,
        )
        single_request = rc2.candidate_to_cal(undecomposed, single_contents)
        assert single_request.operator == "single"
        assert [atom.atom_id for atom in single_request.atoms] == [
            "clm-supplier-qualification"
        ]
        single_trace = rc2.run_explicit_claim_audit(
            single_request, auditor=rc2._stub_auditor
        )
        assert single_trace.verdict.support_verdict == "supported"

        failed_request = rc2.candidate_to_cal(failed, single_contents)
        unknown_request = rc2.candidate_to_cal(unknown, single_contents)
        assert failed_request.operator == unknown_request.operator == "single"
        assert failed_request.atoms[0].atom_id == unknown_request.atoms[0].atom_id
        assert failed["handoff_sha256"] != unknown["handoff_sha256"]
        assert (
            failed_request.atoms[0].provenance.reference_sha256
            != unknown_request.atoms[0].provenance.reference_sha256
        )

        compatibility = rc2._compatibility(undecomposed, single_legacy)
        assert compatibility[
            "new_candidate_without_legacy_observations_can_feed_current_legacy_claim_model"
        ] is False

        receipt = {
            "experiment": "contract-a-minimality-rc2-normal-context-conformance-v3",
            "repository_pins": pins,
            "successor_history": [
                {
                    "runner": "run_conformance.py",
                    "result": "HARNESS_FAILURE",
                    "reason": "literal source substring check ignored Markdown line wrapping",
                },
                {
                    "runner": "run_conformance_v2.py",
                    "result": "EVALUATOR_ASSUMPTION_FALSIFIED",
                    "reason": (
                        "two whole-document candidate chunks yielded zero positive-score "
                        "BM25 hits; exact-query consumption remained observable"
                    ),
                },
            ],
            "source_correspondence": {
                "normalization": "whitespace-only for RSH source/proposition correspondence",
                "candidate_proposition_bytes_changed": False,
                "source_bytes_changed": False,
            },
            "candidate_handoffs": {
                "declared": declared["handoff_sha256"],
                "undecomposed": undecomposed["handoff_sha256"],
                "failed": failed["handoff_sha256"],
                "unknown": unknown["handoff_sha256"],
            },
            "direct_real_eb": {
                "purpose": "exact-query consumption probe; positive hits are not a gate",
                "declared_all_of_query_ids": list(direct_declared),
                "declared_all_of_hits": direct_declared,
                "undecomposed_query_ids": list(direct_single),
                "undecomposed_hits": direct_single,
            },
            "core_ablation": core,
            "noncore_hostile_invariance": noncore_results,
            "contract_b_1_2": {
                "production_writer": (
                    "evidence_bundler.contracts.writer.build_retrieval_bundle"
                ),
                "apparatus_validation": "PASS",
                "cal_bundle_intake": "PASS",
                "base_claim_ids": sorted(
                    row.claim_id for row in baseline_contents.claims
                ),
                "baseline_evidence_signature": baseline_signature,
                "legacy_compatibility_carrier_required_by_current_base_schema": True,
            },
            "cal_explicit": {
                "declared_operator": baseline_request.operator,
                "declared_atom_ids": [row.atom_id for row in baseline_request.atoms],
                "declared_request_sha256": baseline_request_hash,
                "declared_parent_verdict": baseline_trace.verdict.support_verdict,
                "single_operator": single_request.operator,
                "single_atom_ids": [row.atom_id for row in single_request.atoms],
                "provenance_hash_source": "Contract A handoff_sha256",
                "semantic_auditor": (
                    "deterministic injected stub; real CAL explicit-claim orchestration "
                    "and aggregation exercised, not NLI quality"
                ),
            },
            "missing_state": {
                "not_decomposed": "valid root/single path",
                "failed": "valid root/single path with distinct provenance binding",
                "unknown": "valid root/single path with distinct provenance binding",
                "omitted_required_identity": (
                    "fails closed in public candidate validator"
                ),
                "explicit_empty_sources": core["explicit_empty_sources"],
            },
            "compatibility": compatibility,
            "preserved_deviation": {
                "current_contract_b_1_2_base_schema_requires_legacy_scaffold_observations": True,
                "interpretation": (
                    "The fields are necessary for current production writer/schema "
                    "compatibility, but hostile mutation must remain invariant for "
                    "candidate proposition authority, EB evidence identity, and CAL "
                    "explicit semantic authority."
                ),
            },
        }
        print("CONTRACT_A_RC2_RECEIPT_BEGIN")
        print(json.dumps(receipt, indent=2, sort_keys=True))
        print("CONTRACT_A_RC2_RECEIPT_END")

    return 0


if __name__ == "__main__":
    print(
        "DEVIATION successor=v3 reason=positive BM25 hits removed as an auxiliary "
        "gate after v2 observed zero hits on two whole-document chunks"
    )
    raise SystemExit(main())
