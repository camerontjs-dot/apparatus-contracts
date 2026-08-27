# Contract B RC1 Independent-Consumer Baseline

**Date:** 2026-08-27  
**Status:** completed research experiment  
**Canonical Contract B changed:** no  
**Production PR created:** no  
**Contract C work performed:** no  
**Experiment disposition:** **BASELINE REPRODUCIBLE, INDEPENDENCE-LIMITED**

## Question

After replacing RC0's prose-only ownership boundary with a normative research profile that fixes the V1 physical shape, normalized intake ledger, semantic-measurement subset, absence/unknown rules, ordering and canonicalization, can two separately implemented read-only consumers produce the same canonical outputs from the same frozen V1 evidence world?

## Evidence basis

RC1 was derived from the completed evidence program rather than by promoting a research implementation:

- V0/V1/V2 conformance: `f4ee2dbd853821ba54328156bbab1c71235fae55`
- optional-extension + ablation: `4fb5dcde81c3ae0a9a99133f6a3f721aeab639dc`
- prior independent-consumer negative result: `40349629c289a340c95735510cf04b1926d200d0`
- temporal/version applicability: `41627c9a313ffd2c73d9b8ea54f1e018e2d676e7`
- frozen EB producer/evidence world: `b4ca9111f5957ef7e7955e2c5024f2280ee19eb5`
- frozen CAL research context: `6acc3462dad73959ccec6bccf8407215f5274cf6`

Research branch used for this execution:

`research/contract-b-promotion-gate-rc1`

Execution head:

`ed770566e6c03abadd5f6ce8f41a10b891a3b050`

## What RC1 froze

RC1 resolved the ambiguities that caused the previous reproducibility failure:

1. V1 root is explicitly the flat `minimal_context` object; no `bundle` wrapper is inferred.
2. Full CAL intake ledger and narrower semantic-measurement payload are separate normative objects.
3. Exact field inclusion/exclusion rules are specified.
4. All ordering rules are specified.
5. Canonical UTF-8 JSON and SHA-256 rules are specified.
6. Absent optional value and explicit unknown normalize identically inside an extension-aware input, while whole-extension legacy absence remains a distinct `legacy_absent` state.
7. Stored candidate/reviewed/admitted counts are checked but are not canonical facts; counts are derived from the complete history ledger.
8. Nomination/review history remains in the intake ledger but is excluded from the blinded semantic payload.
9. Provenance-bound version/effective/context facts may cross B; proposition-specific CAL applicability judgments may not.

The RC1 profile is research-only and does not define a production schema or semantic version.

## Implementations

### Consumer A

- Python implementation.
- Uses the pinned existing Evidence Bundler `build_cal_measurement_view` only for the narrow semantic-measurement subset.
- Normalizes the complete intake ledger from verified V1 according to RC1.

### Consumer B

- JavaScript/Node implementation.
- Standard library only.
- Does not import, call, wrap or inspect Evidence Bundler or Claim Audit Lab implementation modules during execution.
- Implements RC1 directly against the verified V1 JSON object.

The consumers share no normalization helper/module and no serialized expected ledger.

## CI execution

GitHub Actions run:

- run ID: `33086276933`
- job ID: `98566662049`
- conclusion: **success**
- execution step conclusion: **success**
- evidence upload conclusion: **success**

All exact dependency-head checks passed before execution.

Uploaded evidence artifact:

- artifact ID: `9652273669`
- artifact name: `contract-b-rc1-baseline-33086276933`
- artifact ZIP digest: `sha256:a66ef9613ea0306236cc4063b4682fac3764921dd785022fef4743e0d7dcdd20`

No failed RC1 workflow run preceded the successful run.

## Observed evidence

### O1 — frozen V1 identity reproduced

Both consumers received and accepted:

`sha256:a861eeafe9a360e9280e2d2c092bd2bbcdee6661c55412802be6fecbf8c7b2d7`

This is the same V1 canonical hash from the prior experiments.

### O2 — full normalized intake ledger reproduced byte-for-byte

Consumer A ledger SHA-256:

`sha256:5e168cf01e3e187280a3ea3cca9fe8b88741e3e015616aca50f6043a4a310c57`

Consumer B ledger SHA-256:

`sha256:5e168cf01e3e187280a3ea3cca9fe8b88741e3e015616aca50f6043a4a310c57`

Observed ledger bytes were identical.

### O3 — blinded semantic-measurement payload reproduced byte-for-byte

Consumer A semantic SHA-256:

`sha256:814d5966f876a26bca40e2fc189134ea3921736b5a92e8bd6ec30a3a392b54dc`

Consumer B semantic SHA-256:

`sha256:814d5966f876a26bca40e2fc189134ea3921736b5a92e8bd6ec30a3a392b54dc`

Observed semantic payload bytes were identical.

### O4 — prohibited CAL judgments did not enter the canonical ledger

Both structural checks passed for exclusion of proposition-specific CAL judgment keys.

### O5 — redundant stored coverage counts did not become canonical facts

Both consumers verified the V1 stored counts against complete link history, derived the canonical counts from that history, and excluded `candidate_count`, `reviewed_count`, and `admitted_count` as independent canonical fields.

This preserves the prior ablation result rather than silently reintroducing the falsified V1-minimality assumption.

## All baseline checks

- input hash equal: PASS
- ledger bytes equal: PASS
- ledger hashes equal: PASS
- semantic bytes equal: PASS
- semantic hashes equal: PASS
- prohibited CAL judgments absent, Consumer A: PASS
- prohibited CAL judgments absent, Consumer B: PASS
- stored coverage-count fields excluded from canonical ledger, Consumer A: PASS
- stored coverage-count fields excluded from canonical ledger, Consumer B: PASS

## Inference

The previous failure is now localized more strongly.

The frozen evidence world was not the problem. The underlying ownership model was not the problem. Once RC1 supplied the missing physical and normalization rules, two separately coded implementations in different languages converged on exactly the same canonical full ledger and semantic payload.

This is evidence that the earlier `NOT REPRODUCIBLE` result was caused by specification underspecification rather than by irreconcilable evidence semantics.

It also supports keeping two views distinct:

- a non-destructive intake/audit ledger that retains preparation history;
- a blinded semantic-measurement payload that excludes upstream nomination/review authority cues.

## Independence limitation

This result does **not** claim the strongest possible independent-implementation evidence.

Both implementations were authored under the same supervisory/reviewer context. Consumer B is implementation-isolated and written in another language with no EB/CAL imports, but it was not produced by a separate agent/runtime whose context was restricted to RC1.

Therefore the strongest justified statement is:

> RC1 is deterministically reproducible across two code-isolated implementations on the frozen V1 evidence world.

The stronger claim:

> An independently authored consumer with no shared supervisory context reproduces RC1 from the specification alone.

remains untested by this run.

No consumer was patched after observing the other's baseline output.

## What this result does not establish

- It does not promote Contract B.
- It does not prove the reduced field families are universally minimal across other evidence worlds.
- It does not assign PATCH, MINOR or MAJOR.
- It does not establish final production extension filename/discovery/packaging.
- It does not define a CAL result artifact.
- It does not begin Contract C.

## Epistemic disposition

### Observed

The explicit RC1 specification was sufficient for two code-isolated implementations to produce identical canonical results from identical frozen V1 input.

### Inference

The major interface ambiguity exposed by the prior independent-consumer experiment has been repaired at the specification level for this evidence world.

### Remaining hypothesis

A separately authored/isolated implementation will also converge from RC1 alone.

### Remaining unknown

Whether the same normalization rules survive materially different evidence worlds and whether the eventual optional production packaging preserves this reproducibility while remaining backward compatible.

## Next gate

Do not open a production Contract B PR from this research branch.

The next discriminating gate, if stronger promotion evidence is required, is one independently authored Consumer C implementation built from RC1 with no access to Consumer A/B code, followed by the same baseline comparison. If that passes, the promotion review can decide whether the accumulated evidence is sufficient for a fresh production MINOR candidate PR.
