# CONTEXT-FREE REQUIRED

# Contract E RC3C — Fresh Successor Independent Reproduction

Use this packet as the complete task input for the successor reproduction. Do not import surrounding CAL Pipeline conversation, prior Contract E summaries, the first Grok reproduction, or RC3C design reasoning.

## 1. Exact objective

Independently implement and test the frozen Contract E RC3C research authority/warrant specification using only the authorized pre-freeze information aperture below.

Determine whether a competent fresh implementation can recover the common authority-boundary behavior, including the RC3C currentness and canonical-wire rules, without seeing reference validators, hidden vectors, expected results, prior implementations, or the reasons RC3C was created before implementation freeze.

Do not try to make the reproduction pass. Preserve ambiguity and disagreement.

This is not authorization to define Contract E 1.0.0 or modify production behavior.

## 2. Independent implementation repository

Target repository:

`camerontjs-dot/research-scaffold-harness`

Authorized clean base:

`548bfa81f65290eda15af658f647497679b840ef`

Use a new branch and isolated workspace. Suggested branch pattern:

`research/contract-e-rc3c-fresh-reproduction-grok-<run-id>`

Existing Contract D or Contract E reproduction branches/PRs in this repository are not authorized conceptual inputs.

## 3. Complete normative pre-freeze aperture

Before implementation freeze, the fresh implementer may read exactly these five immutable specification blobs and no other Contract E research material.

### A. Authority/warrant candidate

`docs/research/contract-e/rc3a-authority-warrant-spec/SPEC-CANDIDATE.json`

Blob: `9c1090335d87eb5e4885a755542923b453c45317`

### B. Structural shapes

`docs/research/contract-e/rc3a-authority-warrant-spec/SPEC-SHAPES.json`

Blob: `c3f293430ae6ddb87523d83ea6e5380b8b832136`

### C. Participant boundary

`docs/research/contract-e/rc3a-authority-warrant-spec/SPEC-PARTICIPANT-BOUNDARY.json`

Blob: `8b1d292a240300388949d502e7b656e7a23a0b8e`

### D. Authority-basis binding

`docs/research/contract-e/rc3b-authority-basis-binding/BASIS-BINDING-SPEC.json`

Blob: `63c952c9c28f1be2173e69c79976c7dfe5880c10`

### E. RC3C amendment

`docs/research/contract-e/rc3c-native-wire-currentness/RC3C-SPEC.json`

Blob: `f05feac88128fd693cca2fb25a0b2951654377eb`

The union of those five blobs is the complete candidate semantic/wire authority for the successor implementation. When RC3C explicitly supersedes an inherited rule, RC3C governs that point.

## 4. Pre-freeze denylist

Before the fresh implementation freeze, do not access, search, inspect, summarize, or infer from:

- `camerontjs-dot/research-scaffold-harness` PR #2 or any first Contract E reproduction branch/commit beyond the clean base;
- the first Grok implementation, preregistration, fixtures, tests, notes, comparison harness, or comparison results;
- RC3C `PREREGISTRATION.md`, `FROZEN-CASES.json`, `validate.mjs`, `RESULTS.md`, `FREEZE-RECEIPT.md`, workflow, PR #42 body/comments/logs/artifacts;
- RC3A `FROZEN-CASES.json` or validator/results;
- RC3B `AUTHORITY-BASIS-REGISTRY.json`, `FROZEN-BASIS-ATTACKS.json`, `HARDENING-PREREGISTRATION.md`, validators, results, workflow logs/artifacts;
- Apparatus Contracts PRs #23, #25, #26, #27, #42 narratives/discussions;
- CAL, Evidence Bundler, or Decision Engine authority research/implementation/results;
- the cross-disciplinary authority research synthesis;
- ChatGPT/CAL Pipeline conversation history;
- another model's reproduction output;
- GitHub search, web search, browser tools, repository-discovery tools, GitHub MCP/connectors, or local CAL Pipeline repositories outside the isolated workspace.

If any denied material is observed before freeze, stop and mark the run contaminated.

## 5. Fresh implementer task

Using only the five normative blobs:

1. Write a preregistration before implementation that records your independent interpretation, ambiguities, falsifiers, and predicted behavior.
2. Implement a research-only native authority consumer/validator from scratch.
3. Design your own adversarial tests from the five blobs.
4. Do not copy or approximate an imagined reference implementation.
5. Expose a stable API or CLI capable of evaluating:
   - authority envelopes;
   - a collection/resolver of authority-basis records;
   - propagation requests;
   - delegation parent/child objects;
   - historical/current authority records.
6. Preserve deterministic accept/reject behavior and primary reason classes where the specification marks reasons normative.
7. Treat domain-local `result` payloads as opaque to common authority logic.
8. Consume the canonical wire shapes natively. Do not depend on a hidden-vector translation adapter.
9. Record unknowns rather than resolving them by guessing toward likely reference behavior.

## 6. Required pre-reveal freeze

Before any hidden/reference vector is revealed:

- commit the input aperture;
- commit the preregistration separately before implementation where practical;
- commit the complete independent implementation;
- commit all self-designed pre-reveal tests and fixtures;
- run the self-designed tests;
- record exact implementation commit and tree;
- record hashes of the input/specification files and implementation/test corpus;
- record contamination status.

The exact terminal marker must be:

`FRESH_RC3C_IMPLEMENTATION_FROZEN_BEFORE_REFERENCE_VECTOR_REVEAL`

After that marker/freeze, the independent implementation and pre-reveal tests are immutable for scientific comparison.

Do not repair a disagreement after reveal and count it as independent agreement.

## 7. Authorized post-freeze reveal

Only after the exact freeze marker is committed may the operator reveal these comparison artifacts:

1. inherited RC3A vectors
   - `docs/research/contract-e/rc3a-authority-warrant-spec/FROZEN-CASES.json`
   - blob `85bc7805d02a04c5a10b48b43a5f5a89f4e2f32a`

2. RC3B authority-basis registry
   - `docs/research/contract-e/rc3b-authority-basis-binding/AUTHORITY-BASIS-REGISTRY.json`
   - blob `76ea333ee0460d9614e9899edb69e6865e48eccb`

3. RC3B direct basis attacks
   - `docs/research/contract-e/rc3b-authority-basis-binding/FROZEN-BASIS-ATTACKS.json`
   - blob `c726fb0ef914a850620e545131a70d427f4027bd`

4. RC3B compatibility-matrix expectations
   - `docs/research/contract-e/rc3b-authority-basis-binding/HARDENING-PREREGISTRATION.md`
   - blob `1d85e2036d410b3af08d4b2b8926586da8fe6088`

5. RC3C successor hidden vectors
   - `docs/research/contract-e/rc3c-native-wire-currentness/FROZEN-CASES.json`
   - blob `17d45524125814478b987bb8e91d23f545fb514e`

Do not reveal reference validators, generated reference results, RC3C preregistration/design reasoning, workflow logs/artifacts, or the first reproduction even after freeze unless a later diagnostic phase is separately authorized.

## 8. Post-freeze comparison rules

The comparison harness may be added after freeze but must call the frozen implementation natively without semantic repair or bespoke hidden-vector coercion.

Run at minimum:

### A. Inherited authority outcomes

Run all RC3A envelope, propagation, delegation, and historical vectors.

- compare accept/reject outcomes;
- do **not** treat old RC3A reason strings as successor normative authority unless RC3C explicitly relists that boundary.

### B. RC3B authority-basis behavior

Run all RC3B direct authority-basis attacks. RC3B basis-binding primary reasons remain normative.

Run the 9 x 15 compatibility matrix and all reference-type mutations.

A single non-canonical false accept is a material authority failure.

### C. RC3C successor behavior

Run every RC3C hidden vector exactly as frozen, including:

- reference/record/revocation currentness composition;
- validity interval boundaries;
- qualification and authority-basis cardinality;
- jurisdiction/qualification scope wire shape;
- delegation operations/scope wire shape and amplification;
- relisted normative reason classes.

### D. Semantic metamorphism

For the specified positive informational baselines, replace only the opaque result payload with materially different positive, negative, and indeterminate content.

The common authority signature must not change.

### E. Native-consumption requirement

Report any field coercion, singular/plural conversion, hidden-case adapter, producer-specific translation, or representation rewrite required to call the frozen consumer.

Such a bespoke repair is evidence against independent native recoverability.

## 9. Success conditions

The RC3C fresh successor reproduction supports promotion only if all are true:

1. no pre-freeze contamination occurred;
2. the exact freeze marker preceded reveal;
3. the five normative blobs were consumed without hidden design guidance;
4. all canonical positive envelopes are natively consumable;
5. zero authority-relevant false accepts occur;
6. zero canonical false rejects occur from the specified wire/cardinality surface;
7. RC3B basis attacks and matrix agree;
8. RC3C currentness and delegation successor vectors agree;
9. explicitly normative reason classes agree;
10. semantic payload metamorphism causes zero authority-signature changes;
11. no post-reveal semantic repair or bespoke translation adapter is required.

## 10. Failure conditions

Preserve **FALSIFIED** if, among other things:

- reference/record currentness composition remains materially ambiguous;
- a false current reference or stale/revoked record can authorize a new exercise;
- canonical array/scalar shapes are not independently recoverable;
- delegation wire shape still requires coercion;
- an authority-relevant false permit occurs;
- an RC3C-listed normative reason is independently unrecoverable;
- hidden vectors require producer-specific semantics absent from the five blobs;
- semantic result payload creates authority;
- post-reveal repair is needed to restore agreement.

Use **INCONCLUSIVE** only for apparatus/aperture failures that prevent a valid scientific comparison.

## 11. Required evidence record

Open a new Draft Research PR in `camerontjs-dot/research-scaffold-harness` and preserve:

- exact clean base SHA;
- provider/model/CLI identity;
- isolation controls;
- input-aperture commit/tree;
- preregistration commit;
- frozen implementation commit/tree;
- pre-reveal test counts/hashes;
- exact freeze marker;
- contamination status;
- post-freeze revealed blob identities;
- comparison commit/results;
- false accepts and false rejects;
- reason disagreements only where successor reasons are normative;
- native-wire/adaptation deviations;
- semantic metamorphic result;
- terminal disposition.

## 12. Bounded claim

A pass would establish only that the frozen RC3C research specification is independently recoverable by this fresh implementation against the frozen heterogeneous vector set.

A fresh Grok pass is a successor regression reproduction, not yet cross-model independence. A later fresh different-model-family reproduction is the stronger confirmation gate.
