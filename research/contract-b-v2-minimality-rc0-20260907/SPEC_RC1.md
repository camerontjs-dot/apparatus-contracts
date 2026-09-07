# Contract B v2 Minimality RC1

**Class:** Research / Draft / non-production successor candidate  
**Predecessor:** RC0, disposition `RC0_FALSIFIED_REVISION_REQUIRED`  
**Exact repository base inherited from RC0:** `c3563cff66d2c85dcbf575c693056e2d8e4563d4`

## Why RC1 exists

RC0 passed its first 42-test mutation suite but was then falsified by two smaller adversarial probes:

1. an entire intended retrieval lane could be removed and the target still resealed as aperture `complete`;
2. the tail of a returned candidate list could be removed while retaining a larger `candidate_limit`, with no surviving record of the actual returned count.

RC1 adds only the state needed to close those losses.

## RC1 top-level shape

Exact members:

- `schema`: exact `contract-b-v2-candidate-rc1`;
- `bundle_id`;
- `producer`;
- `preparation_profile`;
- `source_contract_a`;
- `declaration`;
- `sources`;
- `passages`;
- `target_plans`;
- `retrievals`;
- `candidate_links`;
- `history_complete`: exact `true`;
- `bundle_sha256`.

RC1 deliberately removes the separately stored RC0 `aperture` summary. Aperture execution state is derived from the target plan plus retrieval executions. The target plan still carries the factual aperture observation/limitations capability inherited from Contract B 1.2.

## Target plans

Exactly one target plan exists per mechanically derived Contract A 2.0 primary target, preserving declared child sequence where applicable.

Each target plan contains:

- `proposition_id`;
- `retrieval_ids`: the complete intended retrieval-execution identities for that target;
- `aperture_observation`: explicit known/unknown value;
- `limitations`: factual target-level limitations.

Every retrieval must be named by exactly one target plan. Every planned retrieval ID must resolve to a retrieval record with the same proposition ID. A planned lane that did not execute therefore remains represented rather than disappearing.

The relation between the target plan and the externally frozen Evidence Bundler preparation profile is a **producer-conformance** question. Contract B transports the plan exactly; it does not prove that the producer declared its true intended plan.

## Retrieval executions

Each retrieval contains:

- `retrieval_id`;
- `proposition_id`;
- `lane_kind`;
- immutable/versioned `implementation_id`;
- exact `query` record as in RC0;
- positive `candidate_limit`;
- `requested_source_ids`: intended source scope for this execution;
- `observed_source_ids`: source scope actually reached before termination;
- `execution_state`: `completed`, `partial`, `failed`, or `not_run`;
- non-negative `returned_count`;
- `limitations`.

Rules:

- source IDs are unique and must resolve to Contract A-bound sources;
- `observed_source_ids` must be a subset of `requested_source_ids`;
- `completed` requires observed source scope to equal requested source scope;
- `not_run` requires empty observed source scope and `returned_count == 0`;
- `failed` requires `returned_count == 0`;
- `returned_count <= candidate_limit`;
- the complete candidate nomination ledger for the retrieval must contain exactly `returned_count` nominations with ranks exactly `1..returned_count`.

`returned_count` is not a confidence/score. It is a retrieval-execution fact used to detect candidate-ledger truncation.

## Derived aperture view

For each primary target, a consumer deterministically derives:

- `complete` when all planned retrievals completed;
- `not_run` when no retrieval is planned or every planned retrieval is explicitly `not_run`;
- `failed` when every planned retrieval is explicitly `failed`;
- `partial` otherwise.

The view also exposes the union of requested and observed source scopes, plus the target's explicit known/unknown aperture observation and limitations. It does not establish corpus, search-universe or proposition-evidence completeness.

A separate stored aperture execution-state object is intentionally ablated because it is redundant with the planned/executed ledger and created an RC0 consistency hole.

## State retained unchanged from RC0

RC1 retains:

- exact A2 handoff/root/decomposition/source binding;
- UTF-8-byte-reconstructable passage provenance;
- optional provenance-bound factual source context and passage anchors;
- proposition-passage candidate links with all retrieval nominations/ranks;
- explicit deterministic selection state/order;
- explicit review/admission state;
- rejected/not-selected candidate recoverability;
- complete-history declaration;
- canonical normalization and whole-object integrity;
- narrow CAL-facing projection containing every primary target and accepted evidence only.

## Still deliberately absent

RC1 still does not carry:

- legacy scaffold support/strength/fidelity/counterevidence/downgrade fields;
- CAL `audit.*`, verdict, confidence, abstention or semantic relation;
- upstream counterevidence classification;
- source trust level as proposition-specific authority;
- separate atomicity beyond A2 decomposition state/lineage;
- raw retrieval score magnitude;
- derived history-count summaries;
- a separately stored aperture execution-state summary.

## RC1 decisive falsifiers

Reject or revise RC1 if any test shows:

1. either RC0 counterexample still survives when the preserved plan/count fields are left unchanged;
2. a planned-but-not-run lane cannot be represented distinctly from an omitted plan;
3. requested-versus-observed source aperture cannot be represented without semantic judgment;
4. candidate membership/rank/selection/admission stages collapse;
5. the derived aperture view loses an independently useful state carried by the complete underlying ledger;
6. the B1.2 explicit known/unknown aperture observation or factual-context/anchor capability cannot be preserved;
7. a legitimate consumer requires an intentionally ablated field for a pre-assessment distinction;
8. A2 lineage or passage provenance can be substituted undetected;
9. CAL semantics are required for B2 validation;
10. a materially smaller representation preserves all of the tested distinctions.

## Remaining boundary even if RC1 passes

A passing RC1 contract-sufficiency test does not prove Evidence Bundler producer conformance, CAL consumer conformance, retrieval quality, source legitimacy, completeness, or production readiness. The next costly-to-fake evidence would be an independent producer/consumer conformance test against a frozen RC1 candidate, not immediate promotion.
