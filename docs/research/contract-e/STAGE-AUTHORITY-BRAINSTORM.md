# Contract E Brainstorm — Stage Authority, Admission, and Use Boundaries

Status: research brainstorm / non-authoritative

This note captures the next refinement of the Contract E hypothesis after Decision Engine Authority Control Plane Cross-Stage RC0. It does not define Contract E, change Contracts A/B/C, define Contract D, or authorize production behavior.

## Live authority inspected

- Apparatus Contracts `main`: `00bdf9546a877f9f6c1d7fd227fd959e1d7aa99e`
- Evidence Bundler `main`: `6011789957f3294f97bff260069cfb5bb1c5772f`
- Claim Audit Lab `main`: `53f0885b111676794d1bd20e10b91aa58b07e9d4`
- Decision Engine `main`: `ff7a0f63e5f7075b192dff04064b950bf7255ffa`
- Authority Control Plane Cross-Stage RC0 terminal evidence: Decision Engine PR #20, result commit `ae44fc001d1157b0ad5af4312833f1d39a41356c`

## Thought progression

The initial authorization picture was sequential:

```text
Decision -> Authorization -> Execution
```

RC0 supported a different bounded model:

```text
standing Authority / delegation posture
              |
     jurisdiction checks
              |
  multiple pipeline boundaries
```

The next refinement is that authority-sensitive boundaries may begin before Evidence Bundler and continue after Decision Engine. A participant may need authority not only to execute an operational Decision, but also to access material, admit material into an evidence aperture, issue an epistemic assessment, make a policy Decision, use/cite an artifact, execute an effect, or authoritatively verify resulting state.

The research question is whether Contract E can define those responsibilities and bindings without absorbing the semantic questions owned by each stage.

## Critical decomposition: `authorized for use` is ambiguous

The phrase "this source/passage is authorized for use" can hide several different relations. They should not be collapsed without evidence.

### Access / acquisition authority

Question:

> May this actor or system read, retrieve, copy, or process this source at all?

Examples include data-access scope, repository/file permissions, licensed-corpus restrictions, confidential-source boundaries, or an operator-delegated research aperture.

This says nothing about whether the source is relevant, reliable, supporting, contradictory, or sufficient.

### Evidence-admission authority

Question:

> May this exact source/passage be admitted into the frozen evidence set supplied to a downstream evaluator?

Candidate concerns include exact source identity, passage identity/hash, provenance lineage, allowed corpus/scope, operator or policy authority, and bundle-sealing authority.

Admission must not itself mean that the passage supports the proposition.

### Semantic evidence eligibility / relevance

Question:

> Is this passage actually relevant, semantically valid, supporting, contradictory, complete enough, or otherwise appropriate evidence for the proposition?

This is domain semantic machinery and must remain owned by Evidence Bundler/CAL or another explicitly designated semantic stage. Contract E must not infer this from access/admission authority.

### Epistemic assessment mandate

Question:

> Is this CAL instance/policy authorized to issue an epistemic assessment over this exact admitted Contract B authority?

CAL may consume exact source/passage identities and any upstream authority receipts as part of the input authority, but those receipts must not strengthen entailment, support, contradiction, completeness, or a reported verdict.

### Decision authority

Question:

> Is this Decision Engine policy/actor authorized to make this class of operational policy Decision over this exact Contract C/target?

This does not permit execution and does not reinterpret CAL semantics.

### Citation / downstream-use authority

Question:

> May this actor use or cite this exact evidence/claim/Decision artifact in this downstream context?

Citation permission is not the same as epistemic support. A passage could be epistemically relevant but not authorized for a particular external use, or authorized for citation while the claim remains uncertain. Prior Decision Engine cross-use-case research already treated citation as a distinct policy effect rather than generic `eligible` state.

### Execution authority

Question:

> May this actor perform this exact effect against this exact current target?

### Verification authority

Question:

> May this actor/system establish the authoritative post-state or outcome record?

## Existing contract surfaces that matter

### Contract A / Contract B

The canonical handoff contract already distinguishes structural/provenance state from CAL audit truth.

Relevant existing fields include:

- source identity and content hash;
- retrieval linkage such as `retrieved_for`;
- passage identity, offsets, extraction method, and use linkage;
- Contract B bundle identity/hash;
- passage identity/hash and provenance;
- source trust classification;
- Evidence Builder identity/config/operator;
- optional `reviewer_sign_off`;
- null CAL audit fields at handoff.

This is useful because authority can potentially bind to exact immutable identities without treating trust, retrieval, or scaffold labels as CAL conclusions.

### CAL Contract B adapter

The live CAL adapter explicitly separates transport types from CAL semantic types. It preserves source/passage identities and builds explicit claim evidence scopes, while CAL semantic claim type is derived separately from claim text.

This is a natural adapter-truthfulness test surface: Contract E should be able to bind to exact identities and allowed operations without inheriting CAL's semantic classification/reliability logic.

### Contract C

Contract C 1.0.0 already carries two materially different categories:

Authority/binding-like identity:

- exact Contract B version, bundle ID, and bundle hash;
- proposition ID and proposition text hash;
- contribution IDs;
- source ID, passage ID, and passage hash;
- producer semantic implementation SHA and policy hash.

Domain semantic state:

- measurement values;
- reported verdict;
- terminal branch;
- causal form;
- basis members;
- rule roles;
- assessment states.

A candidate Contract E adapter should be able to bind authority to the former where appropriate without interpreting the latter.

## Candidate cross-stage responsibility map

Names below are research labels only.

| Boundary | Candidate authority operation | Stage semantic responsibility that must remain outside Contract E |
|---|---|---|
| Source access | `source.acquire` / `source.read` | whether source is relevant or trustworthy evidence |
| Corpus/evidence admission | `evidence.admit_passage` / `bundle.seal` | retrieval/ranking/relevance/support semantics |
| CAL intake/assessment | `assessment.issue` | entailment, evidence state, completeness, reported epistemic conclusion |
| Decision Engine | `decision.make` | operational policy conclusion and typed effect |
| Citation/use | `citation.use` / `evidence.cite` | whether evidence actually supports the proposition |
| Execution | typed effect-specific operation | policy Decision correctness |
| Outcome verification | `outcome.verify` | original Decision correctness |

The operation labels are placeholders and must not be promoted without adapter tests.

## Candidate Contract E responsibility declaration

A Contract E participant declaration may need to answer:

```text
participant identity
semantic responsibilities owned
semantic responsibilities explicitly excluded
upstream authoritative artifacts consumed
authority-sensitive operations exposed
how actor identity is obtained
how operation identity is derived
how target identity/currentness is derived
which fields are semantic and therefore non-authoritative for jurisdiction
which authority profile/policy is consulted
what happens on unknown/revoked/out-of-jurisdiction state
where enforcement occurs
what receipt/record is emitted, if any
```

The critical property is that a participant cannot self-authorize by writing convenient values into its own semantic output.

## Candidate authority receipt references

A source, passage, bundle, Contract C result, Decision, or citation request might carry references to authority evidence such as:

- standing authority profile ID/hash;
- scope/delegation receipt;
- acquisition/access grant;
- evidence-admission/sealing receipt;
- approval/ratification receipt;
- currentness/revocation state.

These should be treated as authority inputs, not semantic evidence.

A field such as:

```text
authorized_for_use: true
```

would be too ambiguous unless the operation, target, authority identity, scope, and currentness are all recoverable.

## Strong invariant: authority must not launder semantics

Examples that must remain invalid:

```text
source is authorized to read
therefore source is relevant
```

```text
passage was admitted to Contract B
therefore passage supports the proposition
```

```text
source trust_level = primary
therefore CAL must report supported
```

```text
CAL reports supported
therefore actor may cite externally
```

```text
Decision disposition = eligible
therefore executor may perform any effect
```

Each arrow crosses an ownership boundary that must require its own semantic or authority rule.

## New research question — Adapter Truthfulness / Participant Binding RC1

> Can real frozen Evidence Bundler/Contract B, CAL/Contract C, Decision Engine, citation/use, execution, and verification boundaries satisfy common Contract E-style responsibility and binding declarations while the authority evaluator remains ignorant of their domain semantics?

### Primary falsifier

Falsify or narrow the Contract E participant-interface hypothesis if any real stage requires Contract E to interpret retrieval relevance, source reliability as epistemic truth, passage text, CAL measurement/verdict semantics, Decision rationale, or outcome semantics merely to establish actor/operation/target jurisdiction.

### Adapter-truthfulness falsifier

A stage adapter must not be able to relabel a protected operation/target as a permitted one without an independently checkable binding failure.

For example:

```text
actual Decision effect: repository runtime mutation
adapter descriptor: repository documentation mutation
```

must be detectable outside the authority evaluator itself.

### Upstream admission falsifier

An access/admission authority mutation must not change CAL's semantic conclusion when the exact Contract B semantic input is held fixed. Conversely, changing passage identity/hash or Contract B authority must be detectable without Contract E deciding whether the passage is supportive.

### Citation falsifier

Citation/use authority must bind to an exact downstream policy/effect or explicit citation policy. Generic epistemic `supported`, source `primary`, or generic Decision `eligible` must not be sufficient authority for citation.

## Working hypothesis

Contract E may be most useful as a **cross-cutting Authority Interface Contract** composed of:

1. a common jurisdiction protocol; and
2. per-participant responsibility/binding declarations.

It may therefore define who is responsible for authority-sensitive transitions across the entire chain without itself becoming a sequential pipeline stage or a semantic decision engine.

The next test should earn or falsify that shape before any Contract E schema is proposed.
