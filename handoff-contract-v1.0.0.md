# Handoff Contract Specification: Research Apparatus

**Version:** 1.0.0 (LOCKED)
**Locked at:** 2026-05-08
**Applies to:** Scaffold Harness → Evidence Builder → Claim Audit Lab
**Primary domain:** Regulated industries (pharma QA, regulatory submissions)

---

## v1.0.0 Design Decisions

Four design choices in v1.0.0 are non-obvious enough to surface up front. The spec body below carries them inline.

### Canonical Home and Vocabulary Distribution

This document is the canonical spec. The machine-readable vocabulary lives at `schema/vocabulary.yaml` next to this file. Every consumer (Claim Audit Lab, Evidence Builder, future Scaffold Harness) embeds a byte-identical copy at its own `schema/vocabulary.yaml` plus a `schema/.contract-version` pin file. The verifier under `validators/` hashes all consumer copies against canonical and fails on drift.

### Why `audit_support_verdict` Has Six Values

The intuitive vocabulary is four: `supported`, `partially_supported`, `unsupported`, `not_checkable`. v1.0.0 uses six. It adds `overstated` and `needs_source` to preserve two failure modes the research proposal enumerates as primary metrics. Tables and examples below reflect the six-value vocabulary.

### `not_checkable` over `not_audit_ready`

Claim Audit Lab's pre-contract vocabulary used `not_audit_ready` for the same concept. v1.0.0 picks `not_checkable` as the cleaner term. Consumer-side renames are recorded in each consumer's own decision log.

### `reviewer_sign_off` Ships Forward-Looking with Deferred Population

The optional `reviewer_sign_off` block on `bundle_manifest.yaml` exists in v1.0.0 as a 21 CFR Part 11 e-signature surface. For demo and experimental runs, fields stay null and `required: false`. Populate only when human review actually occurs (e.g., a pharma-customer-facing demo). The block is distinct from the always-populated `operator` field.

---

## Overview and Epistemological Framing

This document specifies the two handoff contracts that connect the three components of the research scaffold evaluation apparatus. A handoff contract is a formally defined, versioned, integrity-verified data package that one component produces and the next component consumes. The contract guarantees that no information is silently added, dropped, or transformed between stages without an explicit, auditable record.

The regulated-industry framing is not cosmetic. Pharmaceutical QA and regulatory submission environments operate under ALCOA+ data integrity principles (Attributable, Legible, Contemporaneous, Original, Accurate, Complete, Consistent, Enduring, Available), which the EU GMP Chapter 4 July 2025 draft is now codifying as binding regulation. ALCOA++ further adds **Traceable** as a tenth principle, requiring full record-history reconstruction from raw input to final report. Every design choice in these contracts is evaluated against those standards.

The two contracts:

- **Contract A (C-A):** Research Scaffold Harness → Evidence Builder
- **Contract B (C-B):** Evidence Builder → Claim Audit Lab

They are intentionally asymmetric. C-A is a production artifact: it records what the scaffold saw and claimed, with enough state to reproduce the run. C-B is a measurement-ready artifact: it presents curated, passage-resolved, integrity-sealed evidence specifically formatted for deterministic audit. This mirrors the GMP separation between manufacturing and QC.

---

## Regulatory and Standards Grounding

### ALCOA+ / ALCOA++ Compliance

| Dimension | Applicable to | Contract requirement |
|---|---|---|
| Attributable | Both contracts | `run_id`, `agent_id`, `model_id` in all manifests |
| Legible | Both contracts | Human-readable YAML with controlled vocabulary; no opaque encoded blobs in primary fields |
| Contemporaneous | Both contracts | `timestamp_utc` (ISO 8601) recorded at handoff, not retroactively |
| Original | C-A | `content.*` files are unmodified source outputs; hash computed before any transformation |
| Accurate | Both contracts | `corpus_hash`, `bundle_hash` verify no silent mutation between stages |
| Complete | Both contracts | `claims.yaml` must carry **all** claims produced, including downgraded and removed ones, not only survivors |
| Consistent | Both contracts | Timestamps in expected sequence; no gaps in claim lineage |
| Enduring | Both contracts | Immutable artifacts after handoff; amendments require a new versioned artifact, not in-place edits |
| Available | Both contracts | Flat file layout in version-controlled directory; no opaque database required to read |
| Traceable (ALCOA++) | Both contracts | Every final audit result traceable to a specific claim instance → specific passage → specific source document → specific scaffold run |

### 21 CFR Part 11 Alignment

For organizations deploying this apparatus in FDA-regulated contexts, the handoff artifacts function as electronic records under 21 CFR Part 11:

- **§11.10(e) Audit trails:** `scaffold_run.yaml` and `bundle_manifest.yaml` are computer-generated, time-stamped, and hash-sealed. They record the date and time of creation and cannot be manually modified without breaking the hash.
- **Preservation of recorded information:** Artifacts are immutable after handoff. Amendments produce a new `run_id` and a new hash. Previously recorded information is never obscured or deleted.
- **Authority and accountability:** `agent_id` and `model_id` fields satisfy the attribution requirement. In human-in-the-loop deployments, the optional `reviewer_sign_off` block provides the e-signature surface, with fields staying null and `required: false` for demo runs.

### ICH Q10 and ISO 9001:2015 Alignment

ICH Q10 requires that records show data analysis, decision rationale, effectiveness checks, and lifecycle traceability. ISO 9001:2015 Clause 7.5 requires documented information to be available, legible, identifiable, and protected from modification. Both contracts satisfy these through:
- Explicit `schema_version` field on every artifact, enabling change control
- `workflow_condition` as a controlled vocabulary field: the experimental treatment variable, equivalent to a process parameter in a batch record
- Cross-project review requirement: any schema change that breaks C-A or C-B requires review across all three components, documented in `decisions.md`, before implementation

---

## Contract A: Scaffold Harness → Evidence Builder

### Purpose

C-A records everything the scaffold produced during a single research run: the source corpus it retrieved, the claims it made, the support labels it assigned, the passages it used, and the configuration state that governed the run. It is the **original record** in ALCOA+ terms. The Evidence Builder consumes it but never modifies it; any derived work product is the Evidence Builder's own output, C-B.

### C-A Directory Layout

```
scaffold-run-{run_id}/              # top-level: named by run_id (UUID v4)
  scaffold_run.yaml                 # frozen state manifest, the "batch record"
  claims.yaml                       # all claims: seeds and extracted instances
  corpus/
    {source_id}/                    # source_id = sha256[:12] of canonical URL or content hash
      content.{md,txt,pdf}          # raw, unmodified source content
      passages.yaml                 # scaffold-used text spans from this source
      metadata.yaml                 # bibliographic identity + retrieval linkage
  intermediates/                    # optional; only for full-scaffold condition
    disconfirmation_pass.yaml       # raw output of the disconfirmation step
    claim_table_draft.yaml          # pre-audit claim table produced by the scaffold
  CONTRACT_VERSION                  # plain-text file containing "1.0.0"
  SHA256SUMS                        # content hash of every file at handoff time
```

### `scaffold_run.yaml`: Frozen State Manifest

```yaml
# scaffold_run.yaml
# Schema version: 1.0.0

run_id: "550e8400-e29b-41d4-a716-446655440000"   # UUID v4; stable identifier for this run
task_id: "pharma-reg-submission-task-03"          # links to the evaluation task set
workflow_condition: "full_scaffold"               # CONTROLLED VOCAB: baseline | provenance_scaffold | full_scaffold
timestamp_utc: "2026-05-08T14:32:17Z"             # ISO 8601; time of corpus handoff

scaffold:
  version: "0.3.1"                                # semver; major bump = breaking change
  prompt_template_id: "scaffold-v3-full"          # human-readable template name
  prompt_template_hash: "sha256:abc123..."        # SHA-256 of the prompt template file
  config_hash: "sha256:def456..."                 # SHA-256 of the full scaffold config at runtime

model:
  model_id: "gpt-4o"
  model_version: "2024-11-20"                     # exact version or API snapshot date
  api_endpoint: "https://api.openai.com/v1"
  temperature: 0.2
  max_tokens: 8192

task:
  research_question: "What are the current FDA guidance requirements for..."
  domain: "pharma_regulatory"
  expert_checkable: true
  ground_truth_ref: "task-set/task-03-gt.yaml"    # optional

corpus:
  total_sources: 12
  corpus_hash: "sha256:789abc..."                 # SHA-256 of corpus/ directory tree at handoff
  retrieval_strategy: "web_search_plus_pmid"
  retrieval_timestamp_utc: "2026-05-08T14:28:02Z"

intermediates_present: true

run_metadata:
  operator: "cameron"                             # human operator or "automated"
  environment: "local-dev"                        # local-dev | ci | production
  notes: ""
```

### `claims.yaml`: Claim Registry

Carries all claim objects produced during the run. Distinguishes retrieval seeds (inputs) from extracted claims (outputs). Preserves all claims including those the scaffold downgraded or removed in its own audit step. This is the complete record per ALCOA+ Complete and ICH Q10.

```yaml
# claims.yaml
# Schema version: 1.0.0

schema_version: "1.0.0"
run_id: "550e8400-e29b-41d4-a716-446655440000"
generated_at_utc: "2026-05-08T14:32:17Z"

claims:
  - claim_id: "clm-001"                           # stable, unique within this run
    claim_type: "retrieval_seed"                  # CONTROLLED VOCAB: retrieval_seed | extracted_claim
    claim_text: "FDA requires 30-day stability data for accelerated approval applications."
    support_status: "sourced"                     # CONTROLLED VOCAB: sourced | inferred | uncertain | unsupported
    claim_strength: 0.9                           # 0.0–1.0: how strongly scaffold asserts this claim
    extraction_fidelity: 0.85                     # 0.0–1.0: how faithfully scaffold represents the source
    source_refs:
      - source_id: "a1b2c3d4e5f6"
        passage_id: "pass-003"
    counterevidence_checked: true
    counterevidence_found: false
    downgraded: false
    downgrade_reason: null
    scaffold_notes: ""

  - claim_id: "clm-002"
    claim_type: "extracted_claim"
    claim_text: "The agency has not issued final guidance on AI-assisted NDA submissions as of Q1 2026."
    support_status: "uncertain"
    claim_strength: 0.55
    extraction_fidelity: 0.70
    source_refs:
      - source_id: "b2c3d4e5f6a1"
        passage_id: "pass-007"
    counterevidence_checked: true
    counterevidence_found: true
    downgraded: true
    downgrade_reason: "Disconfirmation pass found draft guidance document dated Feb 2026 that partially contradicts this claim."
    scaffold_notes: "Retained in registry but flagged as uncertain. See intermediates/disconfirmation_pass.yaml."
```

Two-dimensional confidence (`claim_strength` + `extraction_fidelity`) is drawn from the Knows agent-native schema. Collapsing them into a single label loses the distinction between a well-sourced but tentative conclusion and an unsourced confident assertion. These are two different failure modes Claim Audit Lab needs to distinguish.

### `corpus/{source_id}/metadata.yaml`: Source Identity and Retrieval Linkage

```yaml
# corpus/{source_id}/metadata.yaml
# Schema version: 1.0.0

source_id: "a1b2c3d4e5f6"                         # sha256[:12] of canonical URL
schema_version: "1.0.0"

bibliographic:
  source_type: "regulatory_guidance"              # CONTROLLED VOCAB
  title: "Guidance for Industry: Accelerated Approval..."
  authors: ["FDA Center for Drug Evaluation and Research"]
  publication_date: "2023-01-15"
  pmid: null
  doi: null
  url: "https://www.fda.gov/media/..."
  access_date_utc: "2026-05-08T14:28:01Z"

trust_level: "primary"                            # CONTROLLED VOCAB: primary | secondary | background
content_hash: "sha256:123abc..."                  # SHA-256 of content.* file at retrieval time

retrieval:
  retrieved_for: ["clm-001", "clm-004"]           # claim IDs this source was retrieved to address
  retrieval_query: "FDA accelerated approval stability requirements"
  retrieval_rank: 1

notes: ""
```

The `retrieved_for` field creates the explicit claim-to-source link the Evidence Builder needs to construct targeted evidence bundles without re-inferring relevance. The `content_hash` satisfies ALCOA Original by proving the file has not been modified since retrieval.

### `corpus/{source_id}/passages.yaml`: Scaffold-Used Text Spans

```yaml
# corpus/{source_id}/passages.yaml
# Schema version: 1.0.0

source_id: "a1b2c3d4e5f6"
schema_version: "1.0.0"

passages:
  - passage_id: "pass-003"
    section: "Section 4.2"
    paragraph_index: 2
    char_start: 1842
    char_end: 2105
    text_preview: "The Agency recommends submission of..."   # first 80 chars; for human readability
    used_for_claims: ["clm-001"]
    extraction_method: "scaffold_cited"           # CONTROLLED VOCAB
```

Passage-level provenance is the key differentiator between a genuine evidence bundle and a document-level citation list. `char_start`/`char_end` offsets allow Claim Audit Lab to quote exact text without re-processing the source.

---

## Contract B: Evidence Builder → Claim Audit Lab

### Purpose

C-B is the **measurement-ready** artifact. The Evidence Builder has curated, deduplicated, and integrity-sealed the scaffold's output into a bundle structured for deterministic audit. Claim Audit Lab evaluates claim support against this frozen bundle without accessing the live corpus, live model, or any state outside the bundle. This independence is what makes the audit measurement credible: it cannot be contaminated by post-hoc access to new information.

C-B is the regulated-industry equivalent of a validated test method applied to a prepared sample.

### C-B Directory Layout

```
evidence-bundle-{bundle_id}/                      # top-level: named by bundle_id (UUID v4)
  bundle_manifest.yaml                            # frozen state; the "certificate of analysis"
  claims/
    {claim_id}.yaml                               # one file per extracted claim; self-contained audit unit
  evidence/
    {source_id}/
      passages/
        {passage_id}.yaml                         # passage text + full provenance lineage
      source_profile.yaml                         # abbreviated source identity; no raw content
  audit_config.yaml                               # frozen audit rules and scoring weights
  validation_set_ref.yaml                         # pointer to validation set; version-locked
  CONTRACT_VERSION                                # plain-text file containing "1.0.0"
  SHA256SUMS                                      # content hash of every file at handoff time
```

### `bundle_manifest.yaml`: Certificate of Analysis

```yaml
# bundle_manifest.yaml
# Schema version: 1.0.0

bundle_id: "7f3a1b2c-8d4e-5f6a-b7c8-d9e0f1a2b3c4"  # UUID v4
schema_version: "1.0.0"
generated_at_utc: "2026-05-08T15:01:44Z"

# Upstream lineage
source_run_id: "550e8400-e29b-41d4-a716-446655440000"  # the C-A run this bundle was built from
source_contract_version: "1.0.0"                       # C-A schema version consumed
source_corpus_hash: "sha256:789abc..."                 # MUST match C-A corpus_hash; integrity check

evidence_builder:
  version: "0.2.0"
  config_hash: "sha256:xyz789..."
  operator: "cameron"
  build_timestamp_utc: "2026-05-08T14:58:20Z"

bundle:
  total_claims_in_source: 18                      # claim count in C-A claims.yaml
  claims_included: 14                             # claims carried into this bundle
  claims_excluded: 4                              # claims intentionally excluded
  exclusion_rationale: "4 claims were retrieval_seed type only; no extracted_claim instance produced."
  total_evidence_passages: 31
  bundle_hash: "sha256:efg012..."                 # SHA-256 of entire bundle at seal time

# Transformations applied by Evidence Builder
transformations:
  - type: "passage_deduplication"
    description: "Identical passages cited by multiple claims merged to single canonical passage record."
    claims_affected: ["clm-005", "clm-009"]
  - type: "trust_level_annotation"
    description: "Evidence Builder assigned trust_level to 3 sources lacking explicit scaffold annotation."
    claims_affected: ["clm-003"]

# Quality gates applied before seal
quality_gates:
  every_claim_has_at_least_one_passage: true
  every_passage_links_to_source_profile: true
  source_hashes_verified: true                    # all content_hash values re-verified before seal
  bundle_integrity_verified: true

# Frozen audit configuration reference
audit_config_version: "cal-rules-v1.2.0"
audit_config_hash: "sha256:hij345..."
validation_set_version: "valset-v1.0.0"
validation_set_hash: "sha256:klm678..."

# Forward-looking 21 CFR Part 11 e-signature surface.
# Fields stay null for demo runs; populate only when human review actually occurs.
reviewer_sign_off:
  required: false
  signed_by: null
  signature_timestamp_utc: null
  signature_notes: null
```

The `source_corpus_hash` must match the C-A `corpus_hash` exactly. If it does not, the Evidence Builder must halt and raise a deviation. This is a chain-of-custody break equivalent to a sample integrity failure in a pharmaceutical laboratory. Documented, not silently resolved. The `transformations` block satisfies ICH Q10's decision-rationale requirement.

### `claims/{claim_id}.yaml`: Self-Contained Audit Unit

Each claim file is a self-contained audit unit. Claim Audit Lab must be able to evaluate one claim in isolation without loading the entire bundle. Supports parallel audit execution; the C-B equivalent of a single batch test record.

```yaml
# claims/clm-001.yaml
# Schema version: 1.0.0

claim_id: "clm-001"
bundle_id: "7f3a1b2c-8d4e-5f6a-b7c8-d9e0f1a2b3c4"
schema_version: "1.0.0"

# Claim identity (propagated from C-A, immutable)
claim_text: "FDA requires 30-day stability data for accelerated approval applications."
claim_type: "extracted_claim"
workflow_condition: "full_scaffold"                # inherited from C-A scaffold_run.yaml
task_id: "pharma-reg-submission-task-03"

# Scaffold-assigned labels (from C-A; immutable in C-B)
scaffold_support_status: "sourced"                # CONTROLLED VOCAB
scaffold_claim_strength: 0.9
scaffold_extraction_fidelity: 0.85
scaffold_counterevidence_found: false
scaffold_downgraded: false

# Evidence package for this claim
evidence_passages:
  - passage_id: "pass-003"
    source_id: "a1b2c3d4e5f6"
    passage_text: "The Agency recommends submission of 30-day accelerated stability data..."
    section: "Section 4.2"
    char_start: 1842
    char_end: 2105
    source_trust_level: "primary"
    passage_hash: "sha256:nop901..."

counterevidence_passages: []                       # populated if scaffold_counterevidence_found: true

# Audit target fields (populated by Claim Audit Lab; null at handoff)
audit:
  audit_run_id: null
  audited_at_utc: null
  audit_support_verdict: null                      # CONTROLLED VOCAB: supported | partially_supported | unsupported | overstated | needs_source | not_checkable
  audit_confidence: null                           # 0.0–1.0
  audit_notes: null
  false_caution_flag: null                         # true if claim was over-cautiously labeled by scaffold
  deviation_flag: null                             # true if audit verdict contradicts scaffold_support_status
  deviation_notes: null
```

The `audit.*` fields ship as null at handoff and are populated by Claim Audit Lab. Preserves the production / quality-control separation analogous to GMP's QC-independent-of-manufacturing requirement. The `deviation_flag` and `deviation_notes` are the equivalent of a formal deviation record: when audit verdict contradicts scaffold label, the disagreement is documented, not discarded.

The six-value `audit_support_verdict` lets the audit distinguish:
- `overstated`: claim is stronger than evidence supports (the research proposal's "overconfident conclusions" failure mode)
- `needs_source`: claim is stateable but lacks citation (the research proposal's "missing source provenance" failure mode)
- `not_checkable`: claim too vague or malformed to audit (instrument limitation, not a model failure)

The `false_caution_flag` operationalizes the proposal's secondary metric: cases where the scaffold became too timid despite adequate evidence. A scaffold that inflates uncertainty labels is not a success.

### `evidence/{source_id}/passages/{passage_id}.yaml`: Passage Record

```yaml
# evidence/a1b2c3d4e5f6/passages/pass-003.yaml
# Schema version: 1.0.0

passage_id: "pass-003"
source_id: "a1b2c3d4e5f6"
bundle_id: "7f3a1b2c-8d4e-5f6a-b7c8-d9e0f1a2b3c4"
schema_version: "1.0.0"

passage_text: "The Agency recommends submission of 30-day accelerated stability data for applications seeking accelerated approval under 21 CFR 314.510..."
section: "Section 4.2"
paragraph_index: 2
char_start: 1842
char_end: 2105
passage_hash: "sha256:nop901..."

cited_by_claims: ["clm-001"]
extraction_method: "scaffold_cited"               # CONTROLLED VOCAB

# Provenance lineage: full chain from source to bundle (W3C PROV-DM pattern)
provenance:
  source_url: "https://www.fda.gov/media/..."
  source_access_date_utc: "2026-05-08T14:28:01Z"
  source_content_hash: "sha256:123abc..."
  scaffold_run_id: "550e8400-e29b-41d4-a716-446655440000"
  evidence_builder_version: "0.2.0"
  bundle_created_at_utc: "2026-05-08T15:01:44Z"
```

The `provenance` block implements the W3C PROV-DM pattern: entity (passage) derived from entity (source document) through activity (retrieval) by agent (scaffold). This chain is what satisfies ALCOA++ Traceable.

### `audit_config.yaml`: Frozen Audit Rules

```yaml
# audit_config.yaml
# Schema version: 1.0.0

config_id: "cal-rules-v1.2.0"
config_hash: "sha256:hij345..."                   # self-referential; computed after file is written
schema_version: "1.0.0"
frozen_at_utc: "2026-05-01T09:00:00Z"

scoring:
  support_threshold_sourced: 0.80
  support_threshold_partial: 0.55
  counterevidence_weight: 0.30

rule_policies:
  require_passage_level_match: true
  flag_unsupported_threshold: 0.40
  false_caution_detection: true
  false_caution_threshold: 0.85
  overstated_detection: true                       # detect overstated verdict
  needs_source_detection: true                     # detect needs_source verdict

known_limitations:
  - "Rule engine does not resolve contradictions between multiple sourced passages."
  - "Similarity scoring may underperform on regulatory document boilerplate."

change_log:
  - version: "1.2.0"
    date: "2026-05-01"
    changes: "Added false_caution_detection, overstated_detection, and needs_source_detection rules. Raised support_threshold_sourced from 0.75 to 0.80."
    rationale: "Validation set calibration showed 0.75 produced excessive partial_supported verdicts on regulatory guidance documents. Six-value verdict vocabulary requires explicit detection rules for overstated and needs_source."
```

Freezing the audit config and recording its hash in `bundle_manifest.yaml` implements the proposal's requirement to freeze "the tool version, audit config, rule policy, and validation status" before evaluating experiment outputs. Any rule change made after seeing experiment outcomes must be labeled exploratory and requires a new frozen version.

---

## Controlled Vocabulary Summary

The table below reflects the current canonical vocabulary, including any values added by amendments after v1.0.0 lock. Per-value provenance is recorded in the [Amendments After v1.0.0 Lock](#amendments-after-v100-lock) section and in [`DECISIONS.md`](DECISIONS.md).

| Field | Values |
|---|---|
| `workflow_condition` | `baseline`, `format_only`, `provenance_scaffold`, `full_scaffold` |
| `claim_type` | `retrieval_seed`, `extracted_claim` |
| `support_status` (scaffold) | `sourced`, `inferred`, `uncertain`, `unsupported` |
| `audit_support_verdict` (audit) | `supported`, `partially_supported`, `unsupported`, `overstated`, `needs_source`, `not_checkable` |
| `source_type` | `journal_article`, `regulatory_guidance`, `preprint`, `web_page`, `book`, `other` |
| `trust_level` | `primary`, `secondary`, `background` |
| `extraction_method` | `scaffold_cited`, `scaffold_inferred`, `auto_retrieved` |
| `deviation_type` | `intake_hash_mismatch`, `schema_validation_failure`, `vocabulary_drift`, `missing_required_field`, `other` |

Machine-readable canonical at [`schema/vocabulary.yaml`](schema/vocabulary.yaml). Any change requires a MINOR version bump minimum, a [`DECISIONS.md`](DECISIONS.md) entry, and synchronized updates to every consumer's embedded copy. `validators/verify_spec_vocabulary.py` enforces parity between this table and the canonical YAML.

---

## Contract Governance

### Schema Version Control

Both contracts use semantic versioning:

| Change type | Version bump | Requirement |
|---|---|---|
| New required field | MAJOR (e.g., 1.0.0 → 2.0.0) | Cross-project review; rerun required |
| New optional field | MINOR (e.g., 1.0.0 → 1.1.0) | Backward compatible; existing bundles remain valid |
| Vocabulary value addition | MINOR | Each consumer updates its embedded `schema/vocabulary.yaml` and `.contract-version` pin in the same change |
| Clarification / vocabulary fix | PATCH (e.g., 1.0.0 → 1.0.1) | No schema change; documentation only |

Schema changes are recorded in `decisions.md` before implementation. The `CONTRACT_VERSION` plain-text file in each artifact root makes the schema version machine-readable without parsing YAML.

### Vocabulary Distribution and Verification

- Canonical: `schema/vocabulary.yaml` next to this spec
- Each consumer (CAL, Evidence Builder, Harness) embeds a byte-identical copy at its own `schema/vocabulary.yaml`
- Each consumer carries a plain-text `schema/.contract-version` pin file (e.g., contents `1.0.0`)
- `validators/verify-vocabulary` hashes all consumer copies against canonical and fails non-zero on drift
- `validators/verify-spec-vocabulary` cross-checks the controlled-vocabulary table in this document against `schema/vocabulary.yaml`

### Integrity Verification Protocol

Before the Evidence Builder begins processing C-A:
1. Parse `scaffold_run.yaml` and extract `corpus_hash`
2. Recompute hash of `corpus/` directory tree
3. If hashes match: proceed
4. If hashes do not match: **halt, do not proceed, raise deviation**. Log to `deviations/intake-{run_id}.yaml`.

Before Claim Audit Lab begins processing C-B:
1. Parse `bundle_manifest.yaml` and extract `bundle_hash`
2. Recompute hash of bundle contents
3. If hashes match: proceed
4. If mismatch: halt and raise deviation

In both cases, the consumer also verifies its embedded `schema/.contract-version` pin is compatible with the upstream artifact's `schema_version`. A `vocabulary_drift` deviation is raised if the consumer's pinned contract version is older than the upstream artifact's.

This protocol is the digital equivalent of a sample receipt check in a GLP laboratory: the sample must be verified before testing begins, and any discrepancy is a formal deviation, not a silent override.

### Deviation Handling

Deviations are not failures. They are expected and must be formally recorded. A deviation file:

```yaml
deviation_id: "dev-001"
deviation_type: "intake_hash_mismatch"           # CONTROLLED VOCAB
artifact_id: "550e8400-..."
detected_at_utc: "2026-05-08T15:02:01Z"
detected_by: "evidence_builder_v0.2.0"
description: "corpus_hash in scaffold_run.yaml does not match recomputed hash of corpus/ directory."
impact_assessment: "Cannot proceed; bundle production halted."
resolution: "pending"
capa_notes: ""
```

This pattern is drawn from pharmaceutical CAPA practice and 21 CFR Part 11's requirement that previously recorded information cannot be obscured.

---

## What This Contract Does Not Do

- **Validation that the apparatus measures what it claims.** That is methodological validation, governed by the research proposal's experiment-design plan. The contract enables that validation. It does not perform it.
- **Specify retrieval, chunking, or scoring algorithms.** Those are implementation choices owned by each consumer. The contract specifies what crosses the boundary, not how it was produced.
- **Enforce any specific Python or storage framework.** Pure file-on-disk YAML and Markdown was chosen for ALCOA Available. No opaque database is required.
- **Replace human review.** The `reviewer_sign_off` block is a forward-looking surface. The contract does not perform the review.

---

## Amendments After v1.0.0 Lock

The locked-body principle treats v1.0.0 prose as immutable. Vocabulary additions and other non-breaking changes are recorded here. Each amendment also carries a full ADR entry in [`DECISIONS.md`](DECISIONS.md).

### v1.1.0 (2026-05-15): `format_only` added to `workflow_condition`

The `workflow_condition` controlled vocabulary gained a fourth value, `format_only`, alongside the original `baseline`, `provenance_scaffold`, and `full_scaffold`. The MINOR bump preserves backward compatibility: consumers accept both v1.0.0 and v1.1.0 inputs.

`format_only` names the experimental condition where the scaffold shows visible structure (sections, citations, claim tables) without the provenance, disconfirmation, or audit discipline that backs the higher-discipline conditions. Distinguishing this condition lets the experiment measure the effect of structure alone versus the effect of structure plus discipline.

The canonical `schema/vocabulary.yaml` declares `contract_version: "1.1.0"` and `locked_at_utc: "2026-05-15T00:00:00Z"`. Consumer adoption (Evidence Bundler ADR-012, Claim Audit Lab DECISIONS.md 2026-05-17) completed on 2026-05-17. See [`DECISIONS.md`](DECISIONS.md) § 2026-05-15 for rationale, rejected alternatives, and consumer propagation details.

---

## See Also

- [`schema/vocabulary.yaml`](schema/vocabulary.yaml): machine-readable canonical vocabulary
- [`validators/README.md`](validators/README.md): verifier suite
- [`DECISIONS.md`](DECISIONS.md): ADR log
- [`README.md`](README.md): asset overview and distribution model
