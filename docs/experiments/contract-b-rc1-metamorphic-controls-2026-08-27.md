# Contract B RC1 Metamorphic Controls

**Date:** 2026-08-27  
**Status:** completed research experiment  
**Canonical Contract B changed:** no  
**Production PR created:** no  
**Contract C work performed:** no  
**Disposition:** **SUPPORTED WITHIN PREREGISTERED CONTROL SCOPE**

## Question

Does the explicit RC1 Contract-B normalization/interface candidate preserve its intended epistemic boundary under the mutation, missing-state, ordering, integrity, and redundancy controls that were previously deferred after the first independent-consumer baseline failed?

This experiment does not create a new independent-consumer claim. It reuses the frozen RC1 Consumer A and Consumer B implementations unchanged.

## Pins

- RC1 evidence/result parent: `aa016bcebd57dd09870a9cd4cc129ea7f7f5fc43`
- Evidence Bundler: `b4ca9111f5957ef7e7955e2c5024f2280ee19eb5`
- Claim Audit Lab research context: `6acc3462dad73959ccec6bccf8407215f5274cf6`
- frozen V1 hash: `sha256:a861eeafe9a360e9280e2d2c092bd2bbcdee6661c55412802be6fecbf8c7b2d7`
- frozen RC1 Consumer A blob: `2df5419ce8ca138f27ac381e246e864411bb8587`
- frozen RC1 Consumer B blob: `230c86dd2d84d1d2618cbf4f92291d6da596e597`

Research branch:

`research/contract-b-rc1-metamorphic-controls`

Decisive execution head:

`15f9c45e973bfa80938a35bf98886e19335c1b78`

## Preregistration

The controls and falsifiers were frozen before the first workflow execution in:

`docs/experiments/contract-b-rc1-metamorphic-preregistration-2026-08-27.md`

No acceptance criterion was changed after execution began.

## Preserved apparatus deviation

### Run 1: pre-execution failure

GitHub Actions run `33088001635` failed before any experimental control ran.

Exact failure:

- pinned EB and CAL head verification: PASS;
- frozen-consumer guard: FAIL;
- experimental controls: NOT RUN.

The guard attempted to inspect the RC1 parent revision from a shallow checkout. The parent commit object was unavailable locally, so the workflow could not resolve the frozen consumer path.

The deviation is preserved in:

`docs/experiments/contract-b-rc1-metamorphic-deviation-001.md`

The correction changed only the apparatus guard. It replaced parent-history resolution with direct comparison against the already frozen Consumer A/B Git blob IDs. No consumer code, fixture, mutation, expected result, threshold, or falsifier changed.

Run `33088001635` is therefore an invalid apparatus execution, not a negative result against RC1.

## Decisive CI execution

GitHub Actions:

- run ID: `33088093642`
- job ID: `98573189934`
- workflow conclusion: **success**
- preregistered-control step: **success**
- evidence upload: **success**

All pinned-repository checks passed. Both frozen-consumer blob checks passed before execution.

Uploaded artifact:

- artifact ID: `9653086317`
- name: `contract-b-rc1-metamorphic-33088093642`
- size: 71,955 bytes
- ZIP SHA-256: `sha256:d6485dfe7ff833470e21bf96879bb31101cf3e37c6b074fe65f54d0903392ad7`

Suite result:

`ALL_PREREGISTERED_CONTROLS_PASS`

## Observed evidence

### Baseline repeat

The previous RC1 baseline reproduced exactly:

- V1 input: `sha256:a861eeafe9a360e9280e2d2c092bd2bbcdee6661c55412802be6fecbf8c7b2d7`
- normalized full intake ledger: `sha256:5e168cf01e3e187280a3ea3cca9fe8b88741e3e015616aca50f6043a4a310c57`
- blinded semantic payload: `sha256:814d5966f876a26bca40e2fc189134ea3921736b5a92e8bd6ec30a3a392b54dc`

Consumer A and Consumer B remained byte-identical for both outputs.

### M1 — nomination mutation

One admitted link's nomination rank, score, and hypothesized role were changed without changing admission or evidence content.

Observed:

- Consumer A/B full ledgers: byte-identical to each other;
- Consumer A/B semantic payloads: byte-identical to each other;
- normalized full ledger changed, as required for auditable preparation history;
- semantic payload remained exactly at the baseline hash `sha256:814d5966f876a26bca40e2fc189134ea3921736b5a92e8bd6ec30a3a392b54dc`.

Interpretation: nomination metadata remains auditable but did not become semantic authority.

### M2 — hostile CAL-judgment injection

A top-level sidecar containing `verdict`, `semantic_validity`, `temporal_applicability`, and `decision_participation` was injected into the V1 research object.

Observed:

- A/B normalized outputs remained byte-identical;
- prohibited CAL judgment keys appeared in neither canonical ledger nor semantic payload;
- semantic payload remained baseline-identical;
- after masking only the changed input hash identity, the normalized intake ledger remained baseline-identical.

Interpretation: proposition-specific CAL result state does not leak upstream through Contract B merely because it is colocated in an input object.

### M3 — absent versus explicit unknown

Two variants were tested:

1. `claim.atomicity` omitted;
2. `claim.atomicity: null`.

Observed for both consumers:

```json
{"state":"unknown","value":null}
```

The two normalized ledgers were identical after masking only their distinct input hashes. Both semantic payloads remained baseline-identical.

Interpretation: extension-aware missing value and explicit null normalize to the same explicit unknown state under RC1. This does not collapse whole-extension legacy absence, which remains a separate `legacy_absent` packaging state.

### M4 — integrity corruption

The V1 input was mutated while both consumers retained the original frozen V1 expected hash.

Observed:

- Consumer A rejected before output with `RC1_INTAKE_FAIL: input hash ...`;
- Consumer B rejected before output with the same failure class;
- neither consumer emitted normalized ledger or semantic-output artifacts.

Interpretation: integrity failure is fail-closed before semantic processing.

### M5 — declared ordering invariance

Only collections that RC1 explicitly normalizes were permuted: sources, passages, links, source context facts, passage anchors, and limitations.

Observed:

- A/B normalized outputs remained byte-identical;
- semantic payload remained baseline-identical;
- after masking only the changed input hash, the full normalized ledger remained baseline-identical.

`coverage.search_scope.source_ids` was deliberately not permuted because RC1 does not currently state that its list order is semantically irrelevant.

Interpretation: the stated canonical ordering rules remove the intended representation-order degrees of freedom.

### M6 — stored coverage-count corruption

The stored `candidate_count` was changed from 5 to 6 while the complete preparation history still contained 5 links. The mutated input's test hash was recomputed so integrity was not the tested variable.

Observed:

- both consumers rejected before output;
- Consumer A explicitly reported stored counts `{candidate: 6, reviewed: 5, admitted: 4}` versus derived `{candidate: 5, reviewed: 5, admitted: 4}`;
- Consumer B rejected the same invariant violation;
- neither emitted ledger/semantic artifacts.

Interpretation: stored counts remain redundant verification inputs rather than independent canonical facts, consistent with the earlier ablation result.

## Preregistered check summary

All registered checks were true:

- baseline repeat and known hashes;
- cross-consumer equivalence under every accepted mutation;
- semantic blinding under nomination mutation;
- CAL-sidecar exclusion;
- missing/null unknown normalization;
- fail-closed integrity behavior;
- declared ordering invariance;
- fail-closed stored-count consistency.

## Observed evidence versus inference

### Observed

The frozen RC1 A/B implementations behave identically across the preregistered control family, and each control changed or preserved the expected output layer.

### Inference

The RC1 specification is not merely sufficient for one happy-path serialization. On the tested evidence world, its central separation is behaviorally stable:

- preparation history can change without changing blinded semantics;
- downstream CAL judgments cannot silently enter the B ledger;
- unknown state is explicit rather than defaulted;
- declared representation ordering is canonicalized;
- integrity and complete-history/count contradictions fail closed.

### Remaining hypothesis

A consumer authored under a genuinely isolated context from RC1 alone will reproduce the same interface semantics.

### Remaining unknowns

1. Generalization to materially different evidence worlds, especially interrupted/partial retrieval, re-review, deduplication, and deliberately incomplete histories.
2. Final production optional-extension filename/discovery and completeness declaration.
3. Strongest-form independently authored Consumer C reproducibility.
4. Ecosystem compatibility beyond the current legacy verifier and first-party research consumers.

## Falsified alternatives

Within this experiment's scope, evidence rejects the alternatives that:

- nomination metadata must alter semantic measurement merely because it crosses Contract B;
- colocated proposition-specific CAL judgment state necessarily leaks into canonical B output;
- missing atomicity must be fabricated or differ semantically from explicit unknown;
- declared input ordering should alter canonical outputs;
- a hash-mismatched input can proceed to semantic processing;
- inconsistent stored coverage counts can silently override complete ledger history.

## Disposition

**SUPPORTED WITHIN PREREGISTERED CONTROL SCOPE.**

This result is evidence for a fresh Contract B promotion review. It is not itself `SUPPORTED FOR PROMOTION`, does not assign a semantic version, and does not authorize merging this research branch.

No new independent-authorship claim is made.