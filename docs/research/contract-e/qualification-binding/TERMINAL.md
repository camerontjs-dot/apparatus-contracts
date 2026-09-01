# Contract E Qualification Binding Semantic-Closure Experiment — Terminal Record

Thread state: **TERMINAL**

Primary research disposition: **QUALIFICATION_BINDING_UNDERDETERMINED**

This is a research evidence record. It does not authorize a Contract E semantic amendment, release, merge, production authorization policy, or fresh independent reproduction in this thread.

## Live starting identities verified

### Apparatus Contracts semantic-recoverability audit

- repository: `camerontjs-dot/apparatus-contracts`
- PR: `#47`
- state at experiment start: closed Draft Research PR, unmerged
- frozen head: `b7fa5e3885bb75a21573f32268bf7c66d7428fdb`
- terminal disposition: `TERMINAL — FALSIFIED`
- resolved Contract E SHA-256: `d883e5678aa7d39db6bd98d9607c94ee74ae68cd4c17a1def5cd00e6468634f9`

PR #47 was not modified or reopened.

### Terminal reader-cohort comparison

- repository: `camerontjs-dot/research-scaffold-harness`
- PR: `#12`
- state at experiment start: closed Draft Research PR, unmerged
- comparison/head commit: `a9e7c39fa08eeb72261a3e3ca47d9d48f6012847`
- broad disposition: FALSIFIED for full semantic recoverability; narrower recoverable core supported

Durable reader evidence consulted as needed:

- Copilot Reader PR #8; pre-question interpretation commit `a3c2ea532e5d4ba42bec404760509058198bec62`
- Grok Reader PR #10
- Gemini Reader PR #11

### Experiment base

- apparatus-contracts live `main` at branch creation: `6a45ab2de09370f3048ffb083e25b487f81117e4`

## Experiment identities

- branch: `research/contract-e-qualification-binding-20260901`
- Draft Research PR: `#58`
- preregistration commit: `bc9b867e3350ad3081b04b0921d7b32e6f60b4fa`
- evidence record commit: `c9424a2d7f5ffbc191441efaf8a749b533273876`
- frozen candidate-matrix commit: `6a796e4de49448391a70b5cdb07f52b8cd1e5c4a`
- matrix-adjudication/results commit: `d7a9f8596e566e9fe93c94f642a95acca03b34a5`

Post-matrix-freeze held-out evidence inspected:

- RC3C successor hidden/frozen case blob: `17d45524125814478b987bb8e91d23f545fb514e`
- RC3C candidate/apparatus freeze head: `31a606230229ecd378f3840ae48b3cd502374dd8`

No new evaluator run or workflow artifact was required or treated as dispositive. The disputed question is a missing normative relation; executing another implementation against an unlabelled semantic case would only re-encode an assumption.

## Exact dispositions

### Subject binding

`UNDERDETERMINED`

The current source set does not justify any unique predicate relating `Qualification.subject_id` to `envelope.subject.id`.

Exact equality is historically implemented but not normatively established. Membership/delegation-aware or other explicit applicability models are not normatively established either.

### Scope binding

`UNDERDETERMINED`

The current source set does not justify any unique predicate relating scalar `Qualification.scope` to scalar `envelope.jurisdiction.scope`.

Exact equality is historically implemented but not normatively established. No containment hierarchy or Qualification-specific applicability relation exists in the frozen sources.

### Qualification aggregation dependency

`DEFERRED — NOT REQUIRED TO ANSWER Q1/Q2`

The canonical wire establishes an array of Qualifications, but same-item versus cross-item satisfaction is not normatively defined. The historical validator's separate `some(...)` checks are preserved as implementation history, not promoted to semantics.

### Failure semantics

`qualification_subject_mismatch` and `qualification_scope_mismatch` remain recognized RC3C primary-reason classes, but their truth conditions are under-specified. Their names cannot create exact-equality predicates.

## False-permit / false-reject findings

No valid quantitative false-permit or false-reject rate can be measured for subject/scope mismatch because there is no authoritative labelled cohort defining which non-equal Qualification relationships are valid.

Using the historical validator as an answer key would be circular because its equality behavior is part of the evidence under test.

## Alternatives preserved

1. **Reason-name overreach** — best-supported explanation: reason vocabulary survived without semantic closure.
2. **Implicit conventional exact binding** — compatible with fixtures and historical implementation, but not normatively established.
3. **Richer relation** — possible but unsupported; no Qualification-specific subject bridge or scope hierarchy exists.
4. **Apparatus defect only** — partially supported for Q-QUAL-04, whose determinate REJECT presumed an unstated subject predicate; Qualification itself remains meaningful.

## Load-bearing assumption

The assumption that mismatch reason names imply exact equality predicates is **NOT SUPPORTED**.

Strongest discriminating evidence:

1. Qualification fields were frozen without matching rules.
2. RC3A frozen cases did not test subject/scope mismatch semantics.
3. Exact equality appeared in validator implementation only after the specification/case freeze.
4. RC3C was preregistered as a currentness/wire/delegation-shape/reason-semantics repair, not a Qualification semantic-binding amendment.
5. RC3C's frozen held-out corpus tested Qualification wire/cardinality but not subject/scope semantic mismatch.
6. Grok independently surfaced the missing predicates before semantic-question reveal.

## Falsifiers tested

- `F1`: no authoritative nonmatching-subject valid case found; not triggered.
- `F2`: no authoritative non-equality scope applicability relation found; not triggered.
- `F3`: no incompatible live consumer predicates demonstrated; not triggered.
- `F4`: material warning triggered: existing positive fixtures encode equality but do not discriminate it.
- `F5`: not measurable because non-equal structures are currently unlabelled rather than normatively valid/invalid.
- `F6`: supported by provenance: reason relisting occurred without a Qualification mismatch predicate or held-out predicate test.

## Deviations

1. No executable held-out evaluator was created. This is intentional: an evaluator could not scientifically decide an absent normative predicate without embedding the candidate answer.
2. Cross-repository search was bounded to current default branches of Evidence Bundler, Claim Audit Lab, and Decision Engine. It found no independent Qualification predicate, but this is not claimed as exhaustive historical archaeology.
3. The experiment used an already-frozen RC3C hidden case corpus as post-registration held-out evidence rather than manufacturing a new labelled corpus whose expected answers would depend on the very rule under test.
4. Reader PRs #8, #10, and #11 remain open Draft evidence records; their live PR state does not alter their frozen pre-question interpretation evidence.

No deviation changes the terminal disposition.

## Semantic amendment disposition

**No specific Qualification binding amendment is justified by the current evidence.**

The experiment does not authorize exact subject equality, exact scope equality, richer subject transfer, scope containment, or aggregation semantics.

Documenting the unresolved predicate as an explicit research gap would be consistent with this result; choosing the predicate would be a new normative decision requiring separate authority and subsequent independent reproduction.

## Nonclaims

This result does not claim:

- Contract E production readiness;
- Contract E 1.0.0;
- production authorization behavior;
- evaluator correctness;
- that fail-closed posture licenses an invented equality reject rule;
- that a richer binding model is preferred;
- that the existing mismatch reasons should be deleted.

## Smallest next experiment

**Authority-basis aggregation semantic closure.**

That gap was independently surfaced in the semantic-recoverability audit and remains outside this experiment. It is not started here.

## Terminal reconciliation

The research branch and Draft PR preserve preregistration, provenance evidence, the frozen candidate matrix, post-freeze adjudication, alternatives, falsifiers, negative findings, and this terminal record.

PR #58 should remain unmerged and be closed as a terminal research evidence record.
