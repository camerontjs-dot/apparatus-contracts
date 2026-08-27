# Contract B CAL Consumer Conformance Plan — RC0

**Status:** PRE-LOCK TEST PLAN  
**Candidate profile:** `contract-b-cal-consumer-profile-rc0.md`  
**Canonical issue:** apparatus-contracts#1

## Purpose

Determine whether the CAL-side Contract-B profile is sufficiently specified to lock, and whether the eventual canonical change is a clarification, optional extension, or breaking revision.

No candidate schema becomes canonical merely because the architecture is internally coherent.

## Pinned evidence sources

Use exact repository states so the test is reproducible:

- Evidence Bundler seam fixture / V0-V1-V2 builders: pin the exact EB research head referenced from apparatus-contracts#1 before execution;
- Claim Audit Lab consumer seam: pin the exact CAL research head carrying Rungs 03–05;
- Apparatus Contracts: execute against the current locked Contract-B verifier plus this RC0 profile as a non-normative test oracle.

Record all three SHAs in the result artifact.

## Test object

One evidence world must be represented through three handoff variants without changing the underlying claim text or passage content:

### V0 — Current C-B-shaped handoff

Contains only fields available under the current locked contract representation.

Purpose: identify which downstream states CAL genuinely cannot establish without additional information.

### V1 — Minimal factual-context handoff

Adds only the smallest provenance-bound facts EB and Apparatus Contracts can defensibly own.

No proposition-specific CAL judgment may be added here.

### V2 — Full research sidecar

Contains the richer Rung-04 decision annotations used to make all downstream states explicit.

Purpose: upper-bound reference, not proposed contract design.

## Required assertions

### T1 — Input integrity

All variants must pass their declared integrity checks. Any malformed or hash-inconsistent input must fail before CAL semantic processing.

### T2 — V0 fail-closed behavior

Where V0 lacks a state required for proposition-specific eligibility, temporal applicability, authority applicability, or completeness, CAL must produce explicit `unknown` / abstention or a typed intake limitation.

It must not manufacture a default from:

- trust level;
- nomination lane;
- source type;
- retrieval rank;
- absent fields.

### T3 — V1 sufficiency for pre-assessment ledger

V1 must be sufficient for CAL to construct a deterministic pre-assessment ledger containing:

- exact audit proposition;
- exact admitted passages;
- provenance and relevant context facts;
- EB nomination/admission history as context only;
- coverage/search facts when supplied.

No CAL semantic judgment is permitted in this construction step.

### T4 — V1/V2 semantic-measurement equivalence

Given identical proposition and passage content, V1 and V2 must produce the same CAL semantic measurements before decision annotations are applied.

If V2's sidecar changes semantic measurement merely by existing, the boundary fails.

### T5 — Upstream judgment blinding

Any CAL-like judgment embedded in V2 must not become authoritative solely because it crossed the handoff.

CAL must either:

- independently reproduce the assessment under a named policy/operator and emit its own receipt; or
- mark the required assessment unresolved.

### T6 — Nomination invariance

Changing only EB nomination lane / role / rank / score must leave CAL semantic measurement invariant.

The upstream history remains auditable.

### T7 — Mechanical-context sensitivity

Changing a true provenance-bound fact that is relevant to the audited state, such as a declared system version or effective date, must change the corresponding CAL context input.

The semantic proposition/passage measurement may remain unchanged while downstream applicability assessment changes.

### T8 — Trust-policy separation

Changing only `trust_level` must not change semantic measurement.

If it changes decision participation, the change must identify a CAL policy/operator and receipt rather than appearing as direct Contract-B semantics.

### T9 — Completeness separation

Coverage/search/count facts may cross the handoff.

A proposition-specific `complete | incomplete | unknown` aperture conclusion must be CAL-owned unless future evidence falsifies this ownership split.

### T10 — Preservation

Every admitted passage and every recorded upstream context fact remains reconstructable regardless of later CAL eligibility, validity, applicability, or decision basis.

No filtering step may physically rewrite the historical input record.

### T11 — Result immutability

Re-auditing the same C-B input under a different CAL policy or after additional facts become available must create a new result trace/artifact, not mutate the prior result.

### T12 — Result packaging comparison

Run the same decision through both candidate output shapes if feasible:

1. current resealed audited C-B derivative;
2. separate CAL result artifact bound to immutable C-B.

Compare:

- reconstruction completeness;
- semantic ownership clarity;
- duplication;
- compatibility;
- audit-history preservation;
- risk of confusing upstream facts with downstream judgments.

Do not choose packaging before this comparison.

## Falsification criteria

Reject or revise RC0 if any of the following occurs:

1. CAL cannot operate without proposition-specific judgments being supplied upstream.
2. V1 cannot represent required factual context without embedding semantic judgments.
3. V1 and V2 produce different semantic measurements from identical claim/passage content because of sidecar metadata.
4. CAL must reinterpret EB nomination as semantic support/refutation to reproduce valid outcomes.
5. trust/source class cannot be separated from proposition-specific eligibility in practice.
6. preservation requires duplicating the entire EB draft state into Contract B.
7. a simpler seam explains all tested cases with fewer semantic transformations.
8. different CAL consumers cannot reproduce the same pre-assessment ledger from identical V1 input.

## Version-class decision after testing

### PATCH

Use only if no machine-readable field changes are required and the existing schema already supports the intended semantics. Changes would be clarification/governance wording.

### MINOR

Use if V1 proves that additional **optional factual-context fields** are necessary and backward compatibility can be maintained.

Current canonical vocabulary has already advanced to v1.1.0, so the likely next compatible extension would be v1.2.0.

### MAJOR

Use if correct CAL consumption requires:

- new required fields;
- incompatible reinterpretation of existing fields;
- removal/redefinition of existing semantics;
- a mandatory new result-artifact packaging model.

Likely version class would be v2.0.0.

## Lock gate

The candidate may be proposed for lock only when all of the following exist:

- reproducible tri-repo test result;
- pinned EB/CAL/Apparatus SHAs;
- passing integrity and consumer conformance tests;
- explicit unresolved issues list;
- documented falsification attempts;
- cross-repo review from EB and CAL sides;
- version-class rationale;
- proposed schema/vocabulary diff, if any;
- migration plan for existing C-B artifacts and consumers.

Until then, RC0 remains research documentation only.
