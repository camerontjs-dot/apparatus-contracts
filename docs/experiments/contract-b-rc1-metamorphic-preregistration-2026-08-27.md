# Contract B RC1 Metamorphic-Control Preregistration

**Date:** 2026-08-27  
**Status:** PREREGISTERED RESEARCH, NOT PRODUCTION  
**Base:** `aa016bcebd57dd09870a9cd4cc129ea7f7f5fc43`  
**Canonical Contract B changed:** no  
**Contract C work:** prohibited

## Decision this informs

Determine whether the RC1 normalization/interface candidate is stable enough under the previously deferred independent-consumer controls to be admitted as evidence in a fresh Contract B promotion review.

This experiment does **not** itself promote Contract B and does not assign a production version.

## Prior evidence

The RC1 baseline at Apparatus commit `aa016bcebd57dd09870a9cd4cc129ea7f7f5fc43` produced byte-identical full intake ledgers and blinded semantic payloads across the Python and JavaScript consumers on the frozen V1 evidence world.

That baseline did not execute the mutation/metamorphic controls that had been deferred when the earlier independent-consumer baseline failed.

Pinned external states remain:

- Evidence Bundler: `b4ca9111f5957ef7e7955e2c5024f2280ee19eb5`
- Claim Audit Lab context: `6acc3462dad73959ccec6bccf8407215f5274cf6`
- frozen V1 canonical hash: `sha256:a861eeafe9a360e9280e2d2c092bd2bbcdee6661c55412802be6fecbf8c7b2d7`

## Claim under review

> Given the explicit RC1 physical and normalization profile, the two existing code-isolated consumers preserve the same Contract-B/CAL boundary under controlled irrelevant mutations, normalize declared unknown states consistently, canonicalize declared unordered collections consistently, and fail closed when integrity/count invariants are violated.

## Important independence limitation

This suite is **not** a new independent-implementation experiment. It reuses the already frozen Consumer A and Consumer B implementations unchanged.

The harness is permitted to substitute only the expected test-input SHA-256 constant so a deliberately mutated, preregistered input can pass the integrity gate when integrity is not itself the variable under test. No normalization or projection logic may be patched after observing results.

For the integrity-corruption control, the original frozen expected hash must remain in force.

## Frozen controls

### Baseline repeat

The frozen V1 must still produce the previously observed byte-identical cross-consumer ledger and semantic payload.

### M1 — nomination mutation / semantic blinding

Change nomination rank, score, and hypothesized role on one admitted link while leaving claim/passages/admission state unchanged.

Required observation:

- A and B remain byte-identical;
- full intake ledger changes because preparation history is auditable;
- semantic-measurement payload remains byte-identical to baseline.

Falsifier: nomination metadata changes the semantic payload or the consumers disagree.

### M2 — hostile downstream-judgment injection

Inject a top-level research sidecar containing proposition-specific CAL judgment keys.

Required observation:

- A and B remain byte-identical;
- prohibited CAL judgment keys do not enter the normalized Contract-B intake ledger;
- semantic payload remains byte-identical to baseline;
- after masking only the input SHA identity, the normalized ledger remains baseline-equivalent.

Falsifier: injected CAL judgment state enters either canonical output or consumers disagree.

### M3 — absent versus explicit unknown

Compare two otherwise identical inputs:

1. `claim.atomicity` absent;
2. `claim.atomicity: null`.

Required observation:

- both normalize to `{state:"unknown", value:null}`;
- semantic payloads remain baseline-equivalent;
- after masking only input SHA identity, the two normalized ledgers are byte-equivalent.

This tests extension-aware unknown normalization only. It does **not** test whole-extension `legacy_absent`, which remains a distinct production-packaging concern.

Falsifier: absent and explicit-null normalize differently or either becomes a fabricated known value.

### M4 — integrity corruption

Mutate the V1 input but require the original frozen V1 hash.

Required observation:

- both consumers reject before producing ledger/semantic artifacts.

Falsifier: either consumer accepts the hash-mismatched input.

### M5 — declared ordering invariance

Permute only collections for which RC1 declares canonical ordering: sources, passages, links, context facts, typed anchors, and limitations.

Required observation:

- A and B remain byte-identical;
- semantic payload is byte-identical to baseline;
- after masking only input SHA identity, the full normalized ledger is byte-identical to baseline.

Do not reorder `coverage.search_scope.source_ids`, because RC1 currently copies that field and does not normatively declare its list order irrelevant.

Falsifier: declared unordered input ordering changes the normalized content or consumers disagree.

### M6 — stored coverage-count corruption

Change a stored coverage count while preserving complete link history, then recompute the test input hash.

Required observation:

- both consumers reject because stored counts conflict with the complete history from which canonical counts are derived.

Falsifier: either consumer accepts inconsistent stored counts.

## Success boundary

The suite supports admission of RC1 to the promotion review only if **all** preregistered controls meet their required observations.

A passing suite does not establish:

- independently authored Consumer C reproducibility;
- universal interoperability;
- field-level minimality across every evidence world;
- final production extension filename/discovery mechanism;
- PATCH/MINOR/MAJOR by itself;
- Contract C or CAL result packaging.

## Deviation rule

Any harness correction after first decisive execution must be recorded with:

- failed run ID;
- exact failure;
- whether the system under test or only the apparatus changed;
- why the correction does not move an acceptance criterion;
- which prior run is invalidated.

Failed runs remain part of the record.