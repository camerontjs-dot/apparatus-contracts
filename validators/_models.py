"""Pydantic models for the eight YAML artifact types defined by the handoff contracts.

Each model encodes the required fields, controlled-vocabulary literals, and
nested structure as specified in ``handoff-contract-v1.0.0.md``. The models
double as a machine-readable schema for the spec.

Controlled-vocabulary literals are kept in sync with ``schema/vocabulary.yaml``;
the ``verify_spec_vocabulary`` verifier catches drift between this file's
Literals, the spec's markdown table, and the canonical YAML.

All models use ``extra="forbid"`` to honor ALCOA+ Complete: any extra field that
the contract did not anticipate is a chain-of-custody break, not a benign
addition.
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Controlled-vocabulary literal types (kept in sync with schema/vocabulary.yaml).
# ---------------------------------------------------------------------------

ContractVersion = Literal["1.0.0", "1.1.0"]
WorkflowCondition = Literal[
    "baseline",
    "format_only",
    "provenance_scaffold",
    "full_scaffold",
]
ClaimType = Literal["retrieval_seed", "extracted_claim"]
SupportStatus = Literal["sourced", "inferred", "uncertain", "unsupported"]
AuditSupportVerdict = Literal[
    "supported",
    "partially_supported",
    "unsupported",
    "overstated",
    "needs_source",
    "not_checkable",
]
SourceType = Literal[
    "journal_article",
    "regulatory_guidance",
    "preprint",
    "web_page",
    "book",
    "other",
]
TrustLevel = Literal["primary", "secondary", "background"]
ExtractionMethod = Literal["scaffold_cited", "scaffold_inferred", "auto_retrieved"]
DeviationType = Literal[
    "intake_hash_mismatch",
    "schema_validation_failure",
    "vocabulary_drift",
    "missing_required_field",
    "other",
]


class _Strict(BaseModel):
    """Base class: forbid undeclared fields and validate on assignment."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)


# ---------------------------------------------------------------------------
# C-A: scaffold_run.yaml
# ---------------------------------------------------------------------------


class ScaffoldInfo(_Strict):
    version: str
    prompt_template_id: str
    prompt_template_hash: str
    config_hash: str


class ModelInfo(_Strict):
    model_id: str
    model_version: str
    api_endpoint: str
    temperature: float
    max_tokens: int


class TaskInfo(_Strict):
    research_question: str
    domain: str
    expert_checkable: bool
    ground_truth_ref: Optional[str] = None


class CorpusInfo(_Strict):
    total_sources: int = Field(ge=0)
    corpus_hash: str
    retrieval_strategy: str
    retrieval_timestamp_utc: str


class RunMetadata(_Strict):
    operator: str
    environment: str
    notes: str = ""


class ScaffoldRun(_Strict):
    """C-A frozen state manifest (``scaffold_run.yaml``)."""

    run_id: str
    task_id: str
    workflow_condition: WorkflowCondition
    timestamp_utc: str
    scaffold: ScaffoldInfo
    model: ModelInfo
    task: TaskInfo
    corpus: CorpusInfo
    intermediates_present: bool
    run_metadata: RunMetadata


# ---------------------------------------------------------------------------
# C-A: claims.yaml
# ---------------------------------------------------------------------------


class SourceRef(_Strict):
    source_id: str
    passage_id: str


class ClaimRecord(_Strict):
    """One entry in C-A ``claims.yaml`` (all claims, including downgraded)."""

    claim_id: str
    claim_type: ClaimType
    claim_text: str
    support_status: SupportStatus
    claim_strength: float = Field(ge=0.0, le=1.0)
    extraction_fidelity: float = Field(ge=0.0, le=1.0)
    source_refs: list[SourceRef]
    counterevidence_checked: bool
    counterevidence_found: bool
    downgraded: bool
    downgrade_reason: Optional[str] = None
    scaffold_notes: str = ""


class ClaimsRegistry(_Strict):
    """C-A ``claims.yaml`` top-level shape."""

    schema_version: ContractVersion
    run_id: str
    generated_at_utc: str
    claims: list[ClaimRecord]


# ---------------------------------------------------------------------------
# C-A: corpus/{source_id}/metadata.yaml
# ---------------------------------------------------------------------------


class BibliographicInfo(_Strict):
    source_type: SourceType
    title: str
    authors: list[str]
    publication_date: Optional[str] = None
    pmid: Optional[str] = None
    doi: Optional[str] = None
    url: str
    access_date_utc: str


class RetrievalInfo(_Strict):
    retrieved_for: list[str]
    retrieval_query: str
    retrieval_rank: int = Field(ge=0)


class SourceMetadata(_Strict):
    """Per-source metadata at ``corpus/{source_id}/metadata.yaml``."""

    source_id: str
    schema_version: ContractVersion
    bibliographic: BibliographicInfo
    trust_level: TrustLevel
    content_hash: str
    retrieval: RetrievalInfo
    notes: str = ""


# ---------------------------------------------------------------------------
# C-A: corpus/{source_id}/passages.yaml
# ---------------------------------------------------------------------------


class PassageEntry(_Strict):
    passage_id: str
    section: str
    paragraph_index: int = Field(ge=0)
    char_start: int = Field(ge=0)
    char_end: int = Field(ge=0)
    text_preview: str
    used_for_claims: list[str]
    extraction_method: ExtractionMethod


class PassagesFile(_Strict):
    """Per-source passages at ``corpus/{source_id}/passages.yaml``."""

    source_id: str
    schema_version: ContractVersion
    passages: list[PassageEntry]


# ---------------------------------------------------------------------------
# C-B: bundle_manifest.yaml
# ---------------------------------------------------------------------------


class EvidenceBuilderInfo(_Strict):
    """Producer block on the bundle manifest.

    Field name retains the historical "evidence_builder" identifier per the
    locked v1.0.0 contract roles. The project component is now called
    "Evidence Bundler"; see ``DECISIONS.md``.
    """

    version: str
    config_hash: str
    operator: str
    build_timestamp_utc: str


class BundleStats(_Strict):
    total_claims_in_source: int = Field(ge=0)
    claims_included: int = Field(ge=0)
    claims_excluded: int = Field(ge=0)
    exclusion_rationale: str
    total_evidence_passages: int = Field(ge=0)
    bundle_hash: str


class TransformationRecord(_Strict):
    type: str
    description: str
    claims_affected: list[str]


class QualityGates(_Strict):
    every_claim_has_at_least_one_passage: bool
    every_passage_links_to_source_profile: bool
    source_hashes_verified: bool
    bundle_integrity_verified: bool


class ReviewerSignOff(_Strict):
    """21 CFR Part 11 e-signature surface. Null fields for demo runs."""

    required: bool
    signed_by: Optional[str] = None
    signature_timestamp_utc: Optional[str] = None
    signature_notes: Optional[str] = None


class BundleManifest(_Strict):
    """C-B certificate of analysis (``bundle_manifest.yaml``)."""

    bundle_id: str
    schema_version: ContractVersion
    generated_at_utc: str
    source_run_id: str
    source_contract_version: ContractVersion
    source_corpus_hash: str
    evidence_builder: EvidenceBuilderInfo
    bundle: BundleStats
    transformations: list[TransformationRecord]
    quality_gates: QualityGates
    audit_config_version: str
    audit_config_hash: str
    validation_set_version: str
    validation_set_hash: str
    reviewer_sign_off: ReviewerSignOff


# ---------------------------------------------------------------------------
# C-B: claims/{claim_id}.yaml
# ---------------------------------------------------------------------------


class EvidencePassageEntry(_Strict):
    passage_id: str
    source_id: str
    passage_text: str
    section: str
    char_start: int = Field(ge=0)
    char_end: int = Field(ge=0)
    source_trust_level: TrustLevel
    passage_hash: str


class CounterevidencePassageEntry(_Strict):
    passage_id: str
    source_id: str
    passage_text: str
    section: str
    char_start: int = Field(ge=0)
    char_end: int = Field(ge=0)
    source_trust_level: TrustLevel
    passage_hash: str


class AuditBlock(_Strict):
    """Audit fields populated by Claim Audit Lab. Null at handoff."""

    audit_run_id: Optional[str] = None
    audited_at_utc: Optional[str] = None
    audit_support_verdict: Optional[AuditSupportVerdict] = None
    audit_confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    audit_notes: Optional[str] = None
    false_caution_flag: Optional[bool] = None
    deviation_flag: Optional[bool] = None
    deviation_notes: Optional[str] = None


class ClaimAuditUnit(_Strict):
    """Self-contained audit unit at ``claims/{claim_id}.yaml``."""

    claim_id: str
    bundle_id: str
    schema_version: ContractVersion
    claim_text: str
    claim_type: ClaimType
    workflow_condition: WorkflowCondition
    task_id: str
    scaffold_support_status: SupportStatus
    scaffold_claim_strength: float = Field(ge=0.0, le=1.0)
    scaffold_extraction_fidelity: float = Field(ge=0.0, le=1.0)
    scaffold_counterevidence_found: bool
    scaffold_downgraded: bool
    evidence_passages: list[EvidencePassageEntry]
    counterevidence_passages: list[CounterevidencePassageEntry]
    audit: AuditBlock


# ---------------------------------------------------------------------------
# C-B: evidence/{source_id}/passages/{passage_id}.yaml
# ---------------------------------------------------------------------------


class ProvenanceBlock(_Strict):
    source_url: str
    source_access_date_utc: str
    source_content_hash: str
    scaffold_run_id: str
    evidence_builder_version: str
    bundle_created_at_utc: str


class PassageRecord(_Strict):
    """One passage at ``evidence/{source_id}/passages/{passage_id}.yaml``."""

    passage_id: str
    source_id: str
    bundle_id: str
    schema_version: ContractVersion
    passage_text: str
    section: str
    paragraph_index: int = Field(ge=0)
    char_start: int = Field(ge=0)
    char_end: int = Field(ge=0)
    passage_hash: str
    cited_by_claims: list[str]
    extraction_method: ExtractionMethod
    provenance: ProvenanceBlock


# ---------------------------------------------------------------------------
# C-B: audit_config.yaml
# ---------------------------------------------------------------------------


class ScoringConfig(_Strict):
    support_threshold_sourced: float = Field(ge=0.0, le=1.0)
    support_threshold_partial: float = Field(ge=0.0, le=1.0)
    counterevidence_weight: float = Field(ge=0.0, le=1.0)


class RulePolicies(_Strict):
    require_passage_level_match: bool
    flag_unsupported_threshold: float = Field(ge=0.0, le=1.0)
    false_caution_detection: bool
    false_caution_threshold: float = Field(ge=0.0, le=1.0)
    overstated_detection: bool
    needs_source_detection: bool


class ChangeLogEntry(_Strict):
    version: str
    date: str
    changes: str
    rationale: str


class AuditConfig(_Strict):
    """Frozen audit rules at ``audit_config.yaml``."""

    config_id: str
    config_hash: str
    schema_version: ContractVersion
    frozen_at_utc: str
    scoring: ScoringConfig
    rule_policies: RulePolicies
    known_limitations: list[str]
    change_log: list[ChangeLogEntry]


# ---------------------------------------------------------------------------
# Deviation record (used by the integrity verifier when it emits one).
# ---------------------------------------------------------------------------


class DeviationRecord(_Strict):
    """A formal deviation per the spec's Deviation Handling section."""

    deviation_id: str
    deviation_type: DeviationType
    artifact_id: str
    detected_at_utc: str
    detected_by: str
    description: str
    impact_assessment: str
    resolution: str = "pending"
    capa_notes: str = ""


__all__ = [
    "ContractVersion",
    "WorkflowCondition",
    "ClaimType",
    "SupportStatus",
    "AuditSupportVerdict",
    "SourceType",
    "TrustLevel",
    "ExtractionMethod",
    "DeviationType",
    "ScaffoldRun",
    "ClaimsRegistry",
    "ClaimRecord",
    "SourceMetadata",
    "PassagesFile",
    "PassageEntry",
    "BundleManifest",
    "ClaimAuditUnit",
    "PassageRecord",
    "AuditConfig",
    "DeviationRecord",
]
