#!/usr/bin/env python3
"""Normal-context Contract A RC2 cross-repository conformance experiment.

This is reference/research scaffolding, deliberately separate from candidate/
and forbidden from the later fresh-reproduction aperture.
"""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
from dataclasses import replace
from pathlib import Path
from typing import Any

from pydantic import ValidationError

ROOT = Path(__file__).resolve().parents[3]
LANE = Path(__file__).resolve().parents[1]
CANDIDATE_DIR = LANE / "candidate"
DEPS = ROOT / "_deps"
RSH_ROOT = DEPS / "research-scaffold-harness"
EB_ROOT = DEPS / "evidence-bundler"
CAL_ROOT = DEPS / "claim-audit-lab"
PILOT = RSH_ROOT / "pilots" / "pilot-001-rsh-001"

EXPECTED = {
    "apparatus": "6a45ab2de09370f3048ffb083e25b487f81117e4",
    "rsh": "548bfa81f65290eda15af658f647497679b840ef",
    "eb": "6011789957f3294f97bff260069cfb5bb1c5772f",
    "cal": "53f0885b111676794d1bd20e10b91aa58b07e9d4",
}

# Candidate authority is imported explicitly from its public subtree. The later
# independent implementation may receive the public authority but not this file.
sys.path.insert(0, str(CANDIDATE_DIR))
from validate import CandidateValidationError, compute_handoff_sha256, validate_candidate  # noqa: E402

from evidence_bundler.contracts.intake import load_scaffold_run, verify_intake  # noqa: E402
from evidence_bundler.contracts.writer import (  # noqa: E402
    build_retrieval_bundle,
    validate_bundle_tree,
)
from evidence_bundler.models.ca import ScaffoldClaim as EBScaffoldClaim  # noqa: E402
from evidence_bundler.models.document import DocumentChunk  # noqa: E402
from evidence_bundler.models.retrieval import RetrievalConfig  # noqa: E402
from evidence_bundler.retrieval.bm25_retriever import BM25Retriever  # noqa: E402

from research_scaffold_harness.contracts.writer import (  # noqa: E402
    CAWriteInput,
    SourceWriteInput,
    write_scaffold_run,
)
from research_scaffold_harness.fixture import (  # noqa: E402
    _compute_fixture_corpus_hash,
    build_fixture_write_input,
)
from research_scaffold_harness.models.ca import (  # noqa: E402
    ClaimsRegistry,
    ScaffoldClaim,
    SourceRef,
)
from research_scaffold_harness.runner.source_packet import load_source_packet  # noqa: E402

from validators.verify_contract_integrity import verify as apparatus_verify  # noqa: E402

from claim_audit_lab import __version__ as CAL_VERSION  # noqa: E402
from claim_audit_lab.contracts.bundle_loader import load_bundle  # noqa: E402
from claim_audit_lab.contracts.factual_context import load_contract_b_intake  # noqa: E402
from claim_audit_lab.v1.config import hash_audit_config  # noqa: E402
from claim_audit_lab.v1.explicit_claims import (  # noqa: E402
    AtomProvenance,
    ExplicitClaimAtom,
    ExplicitClaimRequest,
    hash_explicit_claim_request,
    run_explicit_claim_audit,
)
from claim_audit_lab.v1.models import (  # noqa: E402
    AuditConfig,
    AuditTrace,
    ExtractedFeatures,
    ModelRevision,
    Passage,
    SupportSignal,
    Verdict,
)

PARENT_TEXT = (
    "The manufacturer requires supplier qualification audits before approving alternative "
    "raw material sources, and documents all supplier changes through the site change control "
    "system with impact assessments reviewed by the quality unit."
)
CHILD_A = (
    "The manufacturer requires supplier qualification audits before approving alternative "
    "raw material sources."
)
CHILD_B = (
    "The manufacturer documents all supplier changes through the site change control system "
    "with impact assessments reviewed by the quality unit."
)


def htext(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def git_sha(path: Path) -> str:
    return subprocess.check_output(["git", "-C", str(path), "rev-parse", "HEAD"], text=True).strip()


def _repo_pins() -> dict[str, str]:
    observed = {
        "apparatus": git_sha(ROOT),
        "rsh": git_sha(RSH_ROOT),
        "eb": git_sha(EB_ROOT),
        "cal": git_sha(CAL_ROOT),
    }
    # Apparatus is expected to be a research descendant of the live-main pin.
    if subprocess.run(
        ["git", "-C", str(ROOT), "merge-base", "--is-ancestor", EXPECTED["apparatus"], observed["apparatus"]],
        check=False,
    ).returncode != 0:
        raise AssertionError(
            f"research head {observed['apparatus']} is not descended from live main {EXPECTED['apparatus']}"
        )
    for key in ("rsh", "eb", "cal"):
        assert observed[key] == EXPECTED[key], (key, observed[key], EXPECTED[key])
    return observed


def _candidate_sources() -> list[dict[str, str]]:
    packet = load_source_packet(PILOT)
    fictional = next(source for source in packet.sources if source.source_id == "src-fictional-compliance-review-note")
    assert PARENT_TEXT in fictional.text, "real RSH pilot source no longer contains the declared root proposition"
    return [
        {
            "source_id": source.source_id,
            "media_type": "text/markdown; charset=utf-8",
            "content": source.text,
            "content_sha256": htext(source.text),
        }
        for source in packet.sources
    ]


def make_candidate(state: str = "declared") -> dict[str, Any]:
    root: dict[str, Any] = {
        "schema": "contract-a-wire-candidate-rc2",
        "handoff_id": f"contract-a-rc2-rsh-supplier-{state}",
        "producer": {
            "producer_id": "research-scaffold-harness",
            "producer_version": EXPECTED["rsh"],
        },
        "work": {"work_id": "pilot-001-rsh-001:clm-supplier-qualification"},
        "root_proposition": {
            "proposition_id": "clm-supplier-qualification",
            "text": PARENT_TEXT,
            "text_sha256": htext(PARENT_TEXT),
        },
        "decomposition": {"state": state},
        "sources": _candidate_sources(),
    }
    if state == "declared":
        root["decomposition"] = {
            "state": "declared",
            "decomposition_id": "decomp-supplier-all-of-001",
            "operator": "all_of",
            "children": [
                {
                    "proposition_id": "clm-supplier-qualification-a",
                    "text": CHILD_A,
                    "text_sha256": htext(CHILD_A),
                    "sequence": 1,
                },
                {
                    "proposition_id": "clm-supplier-qualification-b",
                    "text": CHILD_B,
                    "text_sha256": htext(CHILD_B),
                    "sequence": 2,
                },
            ],
        }
    root["handoff_sha256"] = compute_handoff_sha256(root)
    validate_candidate(root)
    return root


def semantic_propositions(candidate: dict[str, Any]) -> list[dict[str, Any]]:
    decomposition = candidate["decomposition"]
    if decomposition["state"] == "declared":
        return list(decomposition["children"])
    return [candidate["root_proposition"]]


def candidate_chunks(candidate: dict[str, Any]) -> list[DocumentChunk]:
    chunks: list[DocumentChunk] = []
    for index, source in enumerate(candidate["sources"], start=1):
        text = source["content"]
        if not text:
            continue
        chunks.append(
            DocumentChunk(
                chunk_id=f"contract-a-rc2-source-{index}-{source['source_id']}",
                source_id=source["source_id"],
                source_path=Path(f"{source['source_id']}.md"),
                title=None,
                chunk_level="document",
                parent_chunk_id=None,
                heading_path=[],
                section_tag=None,
                char_start=0,
                char_end=len(text),
                chunk_hash=htext(text),
                excerpt=text[:240],
                text=text,
            )
        )
    return chunks


def direct_eb_signature(candidate: dict[str, Any]) -> dict[str, list[tuple[str, int]]]:
    retriever = BM25Retriever(candidate_chunks(candidate))
    signature: dict[str, list[tuple[str, int]]] = {}
    for proposition in semantic_propositions(candidate):
        hits = retriever.query(proposition["text"], top_k=5, score_floor=0.0)
        signature[proposition["proposition_id"]] = [
            (hit.chunk.source_id, hit.rank) for hit in hits
        ]
    return signature


def _compat_observations(**overrides: Any) -> dict[str, Any]:
    values: dict[str, Any] = {
        "support_status": "uncertain",
        "claim_strength": 0.5,
        "extraction_fidelity": 0.5,
        "counterevidence_checked": False,
        "counterevidence_found": False,
        "downgraded": False,
        "downgrade_reason": None,
        "source_refs": False,
        "trust_level": None,
        "retrieval_query": None,
        "retrieval_rank": None,
        "access_date_utc": None,
        "model_prompt_config": False,
        "workflow_condition": None,
        "timestamp_utc": None,
    }
    values.update(overrides)
    return values


def legacy_write_input(
    candidate: dict[str, Any],
    template: CAWriteInput,
    observations: dict[str, Any],
) -> CAWriteInput:
    """Mechanical compatibility projection for current legacy EB/B 1.2 machinery.

    Proposition IDs/text come only from the candidate. Semantic-looking legacy
    values come only from an explicitly separate compatibility observation set.
    The adapter never derives one from the other.
    """
    claims: list[ScaffoldClaim] = []
    for proposition in semantic_propositions(candidate):
        refs: list[SourceRef] = []
        if observations["source_refs"]:
            first_source = template.sources[0]
            first_passage = first_source.passages.passages[0]
            refs = [SourceRef(source_id=first_source.source_id, passage_id=first_passage.passage_id)]
        claims.append(
            ScaffoldClaim(
                claim_id=proposition["proposition_id"],
                claim_type="extracted_claim",
                claim_text=proposition["text"],
                support_status=observations["support_status"],
                claim_strength=observations["claim_strength"],
                extraction_fidelity=observations["extraction_fidelity"],
                source_refs=refs,
                counterevidence_checked=observations["counterevidence_checked"],
                counterevidence_found=observations["counterevidence_found"],
                downgraded=observations["downgraded"],
                downgrade_reason=observations["downgrade_reason"],
            )
        )

    registry = ClaimsRegistry(
        schema_version=template.claims.schema_version,
        run_id=template.claims.run_id,
        generated_at_utc=observations["timestamp_utc"] or template.claims.generated_at_utc,
        claims=claims,
    )

    sources: list[SourceWriteInput] = []
    source_metadata_changed = False
    for source in template.sources:
        metadata = source.metadata
        update: dict[str, Any] = {}
        if observations["trust_level"] is not None:
            update["trust_level"] = observations["trust_level"]
        if observations["retrieval_query"] is not None or observations["retrieval_rank"] is not None:
            retrieval_update: dict[str, Any] = {}
            if observations["retrieval_query"] is not None:
                retrieval_update["retrieval_query"] = observations["retrieval_query"]
            if observations["retrieval_rank"] is not None:
                retrieval_update["retrieval_rank"] = observations["retrieval_rank"]
            update["retrieval"] = metadata.retrieval.model_copy(update=retrieval_update)
        if observations["access_date_utc"] is not None:
            update["bibliographic"] = metadata.bibliographic.model_copy(
                update={"access_date_utc": observations["access_date_utc"]}
            )
        if update:
            source_metadata_changed = True
            metadata = metadata.model_copy(update=update)
        sources.append(replace(source, metadata=metadata))

    manifest = template.manifest
    manifest_update: dict[str, Any] = {}
    if observations["model_prompt_config"]:
        manifest_update["model"] = manifest.model.model_copy(
            update={"model_id": "hostile-compatibility-model", "model_version": "999"}
        )
        manifest_update["scaffold"] = manifest.scaffold.model_copy(
            update={"config_hash": htext("hostile compatibility config")}
        )
    if observations["workflow_condition"] is not None:
        manifest_update["workflow_condition"] = observations["workflow_condition"]
    if observations["timestamp_utc"] is not None:
        manifest_update["timestamp_utc"] = observations["timestamp_utc"]
    if source_metadata_changed:
        corpus_hash = _compute_fixture_corpus_hash(sources)
        manifest_update["corpus"] = manifest.corpus.model_copy(update={"corpus_hash": corpus_hash})
    if manifest_update:
        manifest = manifest.model_copy(update=manifest_update)

    return CAWriteInput(
        manifest=manifest,
        claims=registry,
        sources=sources,
        intermediates=None,
    )


def _bundle_semantic_signature(contents: Any) -> dict[str, Any]:
    claims: dict[str, Any] = {}
    for claim in sorted(contents.claims, key=lambda row: row.claim_id):
        claims[claim.claim_id] = {
            "claim_text": claim.claim_text,
            "evidence": [
                (row.source_id, row.passage_id, row.passage_text)
                for row in claim.evidence_passages
            ],
            "counterevidence": [
                (row.source_id, row.passage_id, row.passage_text)
                for row in claim.counterevidence_passages
            ],
        }
    return claims


def build_b_variant(
    *,
    name: str,
    candidate: dict[str, Any],
    template: CAWriteInput,
    observations: dict[str, Any],
    tmp: Path,
) -> tuple[Any, Path, Any]:
    legacy_parent = tmp / f"legacy-{name}"
    legacy_parent.mkdir()
    write_input = legacy_write_input(candidate, template, observations)
    legacy_dir = write_scaffold_run(write_input, legacy_parent)
    intake = verify_intake(legacy_dir)
    assert intake.valid and intake.artifact is not None, intake.errors

    bundle_dir = tmp / f"bundle-{name}"
    report_path = tmp / f"retrieval-{name}.yaml"
    build_retrieval_bundle(
        legacy_dir,
        bundle_dir,
        config=RetrievalConfig(retrieval_method="bm25", top_k=5, lexical_score_floor=0.0),
        report_out=report_path,
    )
    assert not validate_bundle_tree(bundle_dir), validate_bundle_tree(bundle_dir)
    apparatus = apparatus_verify(bundle_dir, against_pin="1.2.0")
    assert apparatus.passed, apparatus.errors
    factual = load_contract_b_intake(bundle_dir)
    assert factual.extension_state in {"absent", "legacy_absent"}
    contents = load_bundle(bundle_dir)
    expected_claim_ids = [row["proposition_id"] for row in semantic_propositions(candidate)]
    assert sorted(row.claim_id for row in contents.claims) == sorted(expected_claim_ids)
    assert {
        row.claim_id: row.claim_text for row in contents.claims
    } == {
        row["proposition_id"]: row["text"] for row in semantic_propositions(candidate)
    }
    return contents, legacy_dir, factual


def _audit_config() -> AuditConfig:
    return AuditConfig(
        top_k=5,
        retrieval_floor=0.4,
        supported_threshold=0.7,
        contradicted_threshold=0.7,
        numeric_tolerance=0.0,
        approx_numeric_tolerance=0.05,
        aggregation="max_entailment",
        rules_file_sha="sha256:" + "1" * 64,
        retriever=ModelRevision(model_id="contract-a-conformance-retriever", hf_revision_sha="1" * 40),
        entailer=ModelRevision(model_id="contract-a-conformance-entailer", hf_revision_sha="2" * 40),
    )


def candidate_to_cal(candidate: dict[str, Any], contents: Any) -> ExplicitClaimRequest:
    passage_rows: list[Passage] = []
    for source_id in sorted(contents.passages):
        for passage in sorted(contents.passages[source_id], key=lambda row: row.passage_id):
            passage_rows.append(
                Passage(
                    passage_id=passage.passage_id,
                    text=passage.passage_text,
                    source_meta={"source_id": passage.source_id},
                )
            )

    root = candidate["root_proposition"]
    decomposition = candidate["decomposition"]
    if decomposition["state"] == "declared":
        parent_id = root["proposition_id"]
        atoms_source = list(decomposition["children"])
        operator = "all_of"
    else:
        # CAL requires the single parent envelope ID to differ from its atom ID.
        # This deterministic wrapper does not replace or rename the authoritative
        # Contract A proposition, which remains the atom identity.
        parent_id = f"contract-a-single:{candidate['handoff_id']}:{candidate['work']['work_id']}"
        atoms_source = [root]
        operator = "single"

    atoms = [
        ExplicitClaimAtom(
            atom_id=row["proposition_id"],
            claim_text=row["text"],
            provenance=AtomProvenance(
                origin="source_contract",
                reference_id=f"{candidate['handoff_id']}#{row['proposition_id']}",
                reference_sha256=candidate["handoff_sha256"],
            ),
        )
        for row in atoms_source
    ]
    return ExplicitClaimRequest(
        parent_claim_id=parent_id,
        parent_claim_text=root["text"],
        operator=operator,
        atoms=atoms,
        passages=passage_rows,
        audit_config=_audit_config(),
    )


def _stub_auditor(request: Any) -> AuditTrace:
    if request.claim_id.endswith("-a"):
        degree = "supported"
    elif request.claim_id.endswith("-b"):
        degree = "unsupported"
    else:
        degree = "supported"
    return AuditTrace(
        claim_id=request.claim_id,
        claim_text=request.claim_text,
        retrieval=[],
        entailment=[],
        features=ExtractedFeatures(),
        support_signal=SupportSignal(label="neutral", max_entailment_score=0.0),
        rules_fired=[],
        verdict=Verdict(
            support_verdict=degree,
            support_verdict_reason=None,
            audit_flags=[],
            citation_status="not_applicable",
            audit_confidence="medium",
        ),
        audit_config_hash=hash_audit_config(request.audit_config),
        library_version=CAL_VERSION,
    )


def _expect_candidate_invalid(value: dict[str, Any], label: str) -> str:
    try:
        validate_candidate(value)
    except CandidateValidationError as exc:
        return f"{label}: {exc}"
    raise AssertionError(f"expected candidate invalid: {label}")


def _core_ablation(candidate: dict[str, Any]) -> dict[str, Any]:
    results: dict[str, Any] = {}

    for key, family in (("handoff_id", "handoff_identity"),):
        mutated = copy.deepcopy(candidate)
        del mutated[key]
        results[family] = _expect_candidate_invalid(mutated, family)

    mutated = copy.deepcopy(candidate)
    del mutated["work"]["work_id"]
    results["work_identity"] = _expect_candidate_invalid(mutated, "work_identity")

    mutated = copy.deepcopy(candidate)
    del mutated["root_proposition"]["proposition_id"]
    results["proposition_identity"] = _expect_candidate_invalid(mutated, "proposition_identity")

    mutated = copy.deepcopy(candidate)
    del mutated["decomposition"]["children"]
    results["decomposition_lineage"] = _expect_candidate_invalid(mutated, "decomposition_lineage")

    mutated = copy.deepcopy(candidate)
    del mutated["decomposition"]["operator"]
    results["composition_relation"] = _expect_candidate_invalid(mutated, "composition_relation")

    mutated = copy.deepcopy(candidate)
    mutated["decomposition"]["decomposition_producer"] = {"id": "redundant"}
    mutated["handoff_sha256"] = compute_handoff_sha256(mutated)
    results["duplicate_decomposition_producer"] = _expect_candidate_invalid(
        mutated, "duplicate_decomposition_producer"
    )

    mutated = copy.deepcopy(candidate)
    del mutated["sources"][0]["source_id"]
    results["source_identity"] = _expect_candidate_invalid(mutated, "source_identity")

    empty = copy.deepcopy(candidate)
    empty["sources"] = []
    empty["handoff_sha256"] = compute_handoff_sha256(empty)
    validate_candidate(empty)
    assert BM25Retriever([]).query(PARENT_TEXT, top_k=5, score_floor=0.0) == []
    results["explicit_empty_sources"] = "valid; real EB BM25 returns no hits and invents no source"

    return results


def _compatibility(candidate: dict[str, Any], legacy_dir: Path) -> dict[str, Any]:
    root = candidate["root_proposition"]
    direct_new_to_old = False
    try:
        EBScaffoldClaim.model_validate(root)
    except ValidationError:
        direct_new_to_old = False
    else:
        direct_new_to_old = True

    artifact = load_scaffold_run(legacy_dir)
    legacy_claim = artifact.claims.claims[0]
    projected: dict[str, Any] = {
        "schema": "contract-a-wire-candidate-rc2",
        "handoff_id": f"legacy-projection:{artifact.manifest.run_id}:{legacy_claim.claim_id}",
        "producer": {
            # The legacy object does not name its producing repository. This value
            # is supplied by the known producer-side compatibility adapter.
            "producer_id": "research-scaffold-harness",
            "producer_version": EXPECTED["rsh"],
        },
        "work": {"work_id": f"{artifact.manifest.task_id}:{legacy_claim.claim_id}"},
        "root_proposition": {
            "proposition_id": legacy_claim.claim_id,
            "text": legacy_claim.claim_text,
            "text_sha256": htext(legacy_claim.claim_text),
        },
        # Legacy A carries no authoritative decomposition history, so fail closed
        # to unknown rather than inventing not_decomposed.
        "decomposition": {"state": "unknown"},
        "sources": [
            {
                "source_id": source.source_id,
                "media_type": (
                    "text/markdown; charset=utf-8"
                    if source.content_path.suffix == ".md"
                    else "text/plain; charset=utf-8"
                ),
                "content": source.content_path.read_text(encoding="utf-8"),
                "content_sha256": htext(source.content_path.read_text(encoding="utf-8")),
            }
            for source in artifact.sources.values()
        ],
    }
    projected["handoff_sha256"] = compute_handoff_sha256(projected)
    validate_candidate(projected)

    missing_legacy_fields_fails = False
    try:
        ScaffoldClaim(
            claim_id=root["proposition_id"],
            claim_type="extracted_claim",
            claim_text=root["text"],
            # Intentionally omit support/confidence/fidelity/counterevidence/downgrade.
            source_refs=[],
        )
    except ValidationError:
        missing_legacy_fields_fails = True

    return {
        "direct_new_candidate_as_legacy_scaffold_claim": direct_new_to_old,
        "legacy_to_candidate_authority_projection_valid": True,
        "legacy_projection_decomposition_state": projected["decomposition"]["state"],
        "legacy_bytes_name_producer_repository": False,
        "new_candidate_without_legacy_observations_can_feed_current_legacy_claim_model": not missing_legacy_fields_fails,
        "declared_all_of_has_faithful_legacy_lineage_representation": False,
        "version_implication": "major-class if promoted over legacy Contract A 1.0.0; no canonical version assigned here",
    }


def main() -> int:
    pins = _repo_pins()
    declared = make_candidate("declared")
    undecomposed = make_candidate("not_decomposed")
    failed = make_candidate("failed")
    unknown = make_candidate("unknown")

    direct_declared = direct_eb_signature(declared)
    direct_single = direct_eb_signature(undecomposed)
    assert set(direct_declared) == {
        "clm-supplier-qualification-a",
        "clm-supplier-qualification-b",
    }
    assert all(direct_declared.values()), direct_declared
    assert direct_single["clm-supplier-qualification"], direct_single

    core = _core_ablation(declared)
    template = build_fixture_write_input(PILOT, "baseline")

    variants: dict[str, dict[str, Any]] = {
        "baseline": _compat_observations(),
        "source_acquisition_provenance": _compat_observations(access_date_utc="1999-01-01T00:00:00Z"),
        "upstream_selected_passage": _compat_observations(source_refs=True),
        "upstream_query_history": _compat_observations(retrieval_query="hostile upstream query text"),
        "retrieval_rank": _compat_observations(retrieval_rank=99),
        "support_label": _compat_observations(support_status="unsupported"),
        "confidence_claim_strength": _compat_observations(claim_strength=0.01),
        "extraction_fidelity": _compat_observations(extraction_fidelity=0.01),
        "counterevidence_flag": _compat_observations(
            counterevidence_checked=True, counterevidence_found=True
        ),
        "downgrade_state": _compat_observations(
            downgraded=True, downgrade_reason="hostile upstream downgrade"
        ),
        "trust_label": _compat_observations(trust_level="background"),
        "model_prompt_config": _compat_observations(model_prompt_config=True),
        "workflow_condition": _compat_observations(workflow_condition="format_only"),
        "timestamps_history": _compat_observations(timestamp_utc="1999-01-01T00:00:00Z"),
    }

    with tempfile.TemporaryDirectory(prefix="contract-a-rc2-") as raw_tmp:
        tmp = Path(raw_tmp)
        built: dict[str, tuple[Any, Path, Any]] = {}
        for name, observations in variants.items():
            built[name] = build_b_variant(
                name=name,
                candidate=declared,
                template=template,
                observations=observations,
                tmp=tmp,
            )

        baseline_contents, baseline_legacy, _ = built["baseline"]
        baseline_signature = _bundle_semantic_signature(baseline_contents)
        baseline_request = candidate_to_cal(declared, baseline_contents)
        baseline_request_hash = hash_explicit_claim_request(baseline_request)
        baseline_trace = run_explicit_claim_audit(baseline_request, auditor=_stub_auditor)
        assert [atom.atom_id for atom in baseline_request.atoms] == [
            "clm-supplier-qualification-a",
            "clm-supplier-qualification-b",
        ]
        assert baseline_trace.parent_aggregation.atom_support_verdicts == ["supported", "unsupported"]
        assert baseline_trace.verdict.support_verdict == "partially_supported"

        noncore_results: dict[str, Any] = {}
        for name, (contents, _legacy, _factual) in built.items():
            if name == "baseline":
                continue
            signature_equal = _bundle_semantic_signature(contents) == baseline_signature
            request = candidate_to_cal(declared, contents)
            request_hash = hash_explicit_claim_request(request)
            trace = run_explicit_claim_audit(request, auditor=_stub_auditor)
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

        # Undecomposed is a normal first-class case, not a decomposition failure.
        single_contents, single_legacy, _ = build_b_variant(
            name="undecomposed",
            candidate=undecomposed,
            template=template,
            observations=_compat_observations(),
            tmp=tmp,
        )
        single_request = candidate_to_cal(undecomposed, single_contents)
        assert single_request.operator == "single"
        assert [atom.atom_id for atom in single_request.atoms] == ["clm-supplier-qualification"]
        single_trace = run_explicit_claim_audit(single_request, auditor=_stub_auditor)
        assert single_trace.verdict.support_verdict == "supported"

        # Failed and unknown remain distinct provenance states while retaining the
        # authoritative root proposition and single-claim semantic shape.
        failed_request = candidate_to_cal(failed, single_contents)
        unknown_request = candidate_to_cal(unknown, single_contents)
        assert failed_request.operator == unknown_request.operator == "single"
        assert failed_request.atoms[0].atom_id == unknown_request.atoms[0].atom_id
        assert failed["handoff_sha256"] != unknown["handoff_sha256"]
        assert failed_request.atoms[0].provenance.reference_sha256 != unknown_request.atoms[0].provenance.reference_sha256

        compatibility = _compatibility(undecomposed, single_legacy)

        # Current canonical B 1.2 requires legacy observation fields. This is
        # explicitly preserved as compatibility debt, not promoted to RC2 core
        # semantic authority.
        assert compatibility[
            "new_candidate_without_legacy_observations_can_feed_current_legacy_claim_model"
        ] is False

        receipt = {
            "experiment": "contract-a-minimality-rc2-normal-context-conformance",
            "repository_pins": pins,
            "candidate_handoffs": {
                "declared": declared["handoff_sha256"],
                "undecomposed": undecomposed["handoff_sha256"],
                "failed": failed["handoff_sha256"],
                "unknown": unknown["handoff_sha256"],
            },
            "direct_real_eb": {
                "declared_all_of_query_ids": list(direct_declared),
                "declared_all_of_hits": direct_declared,
                "undecomposed_query_ids": list(direct_single),
                "undecomposed_hits": direct_single,
            },
            "core_ablation": core,
            "noncore_hostile_invariance": noncore_results,
            "contract_b_1_2": {
                "production_writer": "evidence_bundler.contracts.writer.build_retrieval_bundle",
                "apparatus_validation": "PASS",
                "cal_bundle_intake": "PASS",
                "base_claim_ids": sorted(row.claim_id for row in baseline_contents.claims),
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
            },
            "missing_state": {
                "not_decomposed": "valid root/single path",
                "failed": "valid root/single path with distinct provenance binding",
                "unknown": "valid root/single path with distinct provenance binding",
                "omitted_required_identity": "fails closed in public candidate validator",
                "explicit_empty_sources": core["explicit_empty_sources"],
            },
            "compatibility": compatibility,
            "preserved_deviation": {
                "current_contract_b_1_2_base_schema_requires_legacy_scaffold_observations": True,
                "interpretation": (
                    "The fields are necessary for current production writer/schema compatibility, "
                    "but hostile mutation shows they are not needed for candidate proposition authority, "
                    "EB retrieval identity, or CAL explicit semantic authority."
                ),
            },
        }
        print("CONTRACT_A_RC2_RECEIPT_BEGIN")
        print(json.dumps(receipt, indent=2, sort_keys=True))
        print("CONTRACT_A_RC2_RECEIPT_END")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
