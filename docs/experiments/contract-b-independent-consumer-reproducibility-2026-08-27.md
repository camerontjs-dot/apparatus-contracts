# Contract B Independent-Consumer Reproducibility Experiment

**Date:** 2026-08-27  
**Status:** research result only  
**Disposition:** **NOT REPRODUCIBLE**  
**Canonical Contract B changed:** no  
**Contract C work performed:** no

## Claim under review

> Two independently implemented read-only consumers can derive the same normalized CAL pre-assessment ledger from identical verified V1 Contract-B input using the candidate Contract-B specification alone.

## Pinned repository states

| Repository | SHA used | Role |
|---|---|---|
| `camerontjs-dot/evidence-bundler` | `b4ca9111f5957ef7e7955e2c5024f2280ee19eb5` | frozen evidence world, V1 producer, existing research consumer A |
| `camerontjs-dot/claim-audit-lab` | `6acc3462dad73959ccec6bccf8407215f5274cf6` | pinned CAL research context |
| `camerontjs-dot/apparatus-contracts` candidate/profile | `63e8506396132a44ebc0e6c2312047e99b1125eb` | candidate semantics / conformance plan |
| prior experiment report | `f4ee2dbd853821ba54328156bbab1c71235fae55` | prior evidence and frozen hashes |

Current repository heads observed before execution:

- Apparatus Contracts `main`: `17f13e77081816da809550154af2b9e2b72eb776`
- Evidence Bundler `main`: `af4fddd3a5b42fea0c0bdbddcdcaae8b4611e3d2`
- Claim Audit Lab `main`: `fbe27056d02bb08d9aa332203ce38312673a0aa0`

The expected Contract-B research heads had not advanced, so no research SHA was silently substituted.

## Prior evidence used

The prior V0/V1/V2 experiment established V1 sufficiency for the tested pre-assessment evidence-world state. It did not establish independent-consumer reproducibility.

Frozen prior hashes:

- fixture file: `sha256:4d5a900232cd243d82fffdc6a5422d32287e9496f3e9728ae684e1ef04fdc7cf`
- V1 research projection: `sha256:a861eeafe9a360e9280e2d2c092bd2bbcdee6661c55412802be6fecbf8c7b2d7`
- existing CAL pre-assessment measurement view: `sha256:b18715b861343a541fd8317d38cfa3b4f6acf2efdcb9578fac55313bf721f8db`

The prior GitHub Actions artifact was inspected. It retains the run logs/results and the V1 hash, but **does not retain the serialized V1 bytes as a standalone artifact**.

## Independence procedure

The preferred isolation procedure was to launch Consumer B in a separate agent/runtime with restricted context. The connected MainFrame Conduit endpoint was unavailable during execution, first returning HTTP 404 and later HTTP 429 before an agent session could be created.

A sequential isolation boundary was therefore used:

1. Read only the candidate Contract-B consumer profile, conformance plan, frozen evidence-world fixture, and prior result metadata.
2. Define an experimental normalized ledger representation before reading Consumer A implementation source.
3. Implement and freeze Consumer B locally.
4. Record Consumer B source SHA-256.
5. Only after that freeze, inspect Consumer A implementation logic.
6. Do not patch Consumer B after discovering Consumer A conventions.

Frozen Consumer B source SHA-256:

`da218d8030b0c9eae3f79345c5f6b5f035a8c1cd4bd79cb5d9b7e7e4994d099a`

### Independence limitation

The prior experiment did not preserve standalone V1 bytes. Consumer B was therefore frozen from the candidate specification plus the frozen evidence-world fixture before the V1 physical projection was regenerated. This limitation is recorded rather than hidden. It does not rescue the interface claim because additional normalization ambiguities remain even when the V1 physical object is available.

## Preregistered normalized ledger hypothesis

Before Consumer A source inspection, Consumer B's ledger representation was frozen to contain:

- input identity;
- exact proposition identity/text plus supplied proposition metadata;
- every admitted passage with exact text, source identity, passage hash and anchors when present;
- provenance-bound source/context facts;
- all nomination/admission link history explicitly marked `non_authoritative_history`;
- coverage/search observations;
- explicit optional-field state (`present`, `absent`, or explicit-null `unknown`);
- no proposition-specific CAL judgments;
- a semantic-input payload containing only proposition identity/text and admitted passage identity/source/text.

Canonicalization was preregistered as UTF-8 JSON with sorted object keys, compact separators, no NaN values, then SHA-256.

This representation was an experimental normalization hypothesis. It was not copied from Consumer A.

## Observed evidence

### O1 — Frozen V1 evidence world was regenerated exactly

After Consumer B was frozen, the V1 research projection was regenerated from the pinned evidence world using the pinned V1 producer semantics.

Observed V1 canonical hash:

`sha256:a861eeafe9a360e9280e2d2c092bd2bbcdee6661c55412802be6fecbf8c7b2d7`

This exactly matches the prior successful experiment. Therefore the baseline failure below is not explained by evidence-world drift.

### O2 — Consumer A reproduces its prior measurement-view hash

The pinned existing research consumer projects the regenerated V1 into the same narrow CAL measurement view observed previously.

Observed Consumer A measurement-view hash:

`sha256:b18715b861343a541fd8317d38cfa3b4f6acf2efdcb9578fac55313bf721f8db`

This matches the prior experiment.

### O3 — Independently frozen Consumer B rejects the verified V1 before projection

Consumer B was run against the hash-matched V1 object.

Observed result:

```text
FAIL
IntakeError: bundle must be an object
```

The independently implemented consumer expected the bundle identity/claim linkage to remain under a `bundle` object. The actual V1 research projection flattens `bundle_id` to the top level and omits the fixture's `bundle` object.

No Consumer B patch was made after this discrepancy.

### O4 — The physical V1 convention is implementation-defined, not candidate-profile-defined

The candidate Contract-B profile is explicitly a consumer-semantics research profile rather than a schema amendment. The Evidence Bundler seam probe likewise describes its projections as information-ownership experiments rather than proposed final field names.

The V1 physical shape therefore depends on research implementation conventions not specified as a Contract-B profile.

### O5 — `pre-assessment ledger` and `measurement view` are not the same specified object

The prior T3 experiment labels the full V1 `minimal_context` handoff itself as the deterministic pre-assessment ledger and records its hash as:

`sha256:a861eeafe9a360e9280e2d2c092bd2bbcdee6661c55412802be6fecbf8c7b2d7`

The existing Consumer A function later projects that object into a narrower measurement view with hash:

`sha256:b18715b861343a541fd8317d38cfa3b4f6acf2efdcb9578fac55313bf721f8db`

That measurement view deliberately excludes nomination rank/score/role, reviewer identity/notes, rejected candidates, and `source_trust_level` while retaining admitted evidence, context facts, anchors, and coverage.

The candidate specification does not provide a machine-readable normalized pre-assessment-ledger schema that resolves which of these two objects is the comparison target.

### O6 — Canonical normalization is not specified by the candidate profile

Consumer A contains implementation conventions including:

- sorted admitted passage IDs;
- sorted admitted source IDs;
- a particular source-field subset;
- a particular passage-field subset;
- verbatim coverage retention;
- exclusion of nomination/review metadata from the measurement view;
- JSON canonicalization rules in implementation code.

Those rules are not fully stated as normative candidate Contract-B consumer semantics.

### O7 — Absence versus unknown is semantically required but not serialization-defined

The profile requires missing state not to become a favorable or adverse default and requires unresolved state to remain first-class. It does not define a normative representation for:

- absent optional field;
- present field with explicit null/unknown;
- omitted capability versus unknown value;
- how those states enter the normalized ledger/hash.

Therefore M3 does not yet have a unique expected canonical representation across independent consumers.

### O8 — Research V1 integrity is not a self-contained declared envelope

The hash-matched V1 can be externally verified against the prior expected hash and regenerated fixture constraints. The research V1 object itself does not define a complete standalone integrity envelope equivalent to canonical Contract-B `SHA256SUMS`/reference verification.

An independent consumer therefore needs out-of-band information to know exactly which integrity assertions are mandatory before semantic processing.

## Consumer A ledger/hash

Existing pinned research consumer:

- V1 input hash: `sha256:a861eeafe9a360e9280e2d2c092bd2bbcdee6661c55412802be6fecbf8c7b2d7`
- CAL measurement-view hash: `sha256:b18715b861343a541fd8317d38cfa3b4f6acf2efdcb9578fac55313bf721f8db`
- normalized pre-assessment-ledger hash under the new experiment: **not uniquely defined by the candidate specification**

## Consumer B ledger/hash

Independent frozen Consumer B:

- source hash: `sha256:da218d8030b0c9eae3f79345c5f6b5f035a8c1cd4bd79cb5d9b7e7e4994d099a`
- verified V1 input hash supplied to execution: `sha256:a861eeafe9a360e9280e2d2c092bd2bbcdee6661c55412802be6fecbf8c7b2d7`
- result: intake rejection, `bundle must be an object`
- ledger hash: **not produced**

## Difference analysis

| Difference | Classification | Rationale |
|---|---|---|
| V1 bundle identity physical location | specification/profile underspecified; Consumer B guessed incorrectly | candidate semantics name bundle identity but do not define the V1 research serialization |
| definition of normalized pre-assessment ledger | specification underspecified | prior T3 treats full V1 as ledger while Consumer A exposes a narrower measurement view |
| nomination/admission history in normalized output | normalization underspecified | T3 requires history to remain represented, but Consumer A measurement view intentionally drops it |
| `source_trust_level` retention | normalization underspecified | profile treats it as apparatus history, A measurement view excludes it |
| rejected-candidate history | normalization underspecified | V1 retains it; A measurement view excludes it |
| absent versus explicit unknown | specification underspecified | semantic rule exists, canonical representation does not |
| canonical ordering and field subset | hidden implementation convention | Consumer A's exact projection rules live in code, not the candidate profile |
| integrity envelope for research V1 | specification underspecified | verification depends on fixture/out-of-band expected hash rather than a self-contained V1 declaration |

This is not classified as evidence that the underlying evidence-world semantics disagree. It is evidence that the current research semantics do not yet constitute a reproducible interface with a unique normalized representation.

## Specification-hypothesis revision before implementation change

The pre-experiment hypothesis was:

> The candidate profile plus verified V1 is sufficiently specified for independent consumers to derive one canonical pre-assessment ledger.

Evidence requires revising it to:

> The candidate profile currently specifies an ownership/semantic boundary, but a separate physical V1 profile plus normalized-ledger/canonicalization specification is required before canonical independent-consumer equivalence can be tested fairly.

Consumer B was not changed after this revision.

## Metamorphic results

The preregistered sequence required baseline equivalence before M1–M4. Baseline equivalence was not reached, so the new experiment **did not execute M1–M4 as conformance evidence**.

Prior evidence remains relevant but is not promoted into new independent-consumer evidence:

- prior nomination mutation showed Consumer A's semantic measurement view invariant while handoff history changed;
- prior hostile downstream sidecar mutation left Consumer A's measurement view unchanged;
- prior integrity/count corruption was rejected by the existing research validator.

M3 optional-field absence remains especially important because its expected absent/unknown representation is one of the ambiguities exposed here.

## Hard falsifiers reached

### Reached

- **Consumer B cannot be specified to a unique canonical output from the candidate specification alone.** Multiple representation choices remain compliant with the prose semantics.
- **Hidden implementation conventions are required to reproduce Consumer A's exact measurement view.**
- **The normalized-ledger comparison target itself is underspecified.**

### Not tested because baseline gate failed

- cross-consumer disagreement under M1 nomination mutation;
- cross-consumer sidecar blinding under M2;
- cross-consumer absence/unknown behavior under M3;
- materially equivalent malformed-input behavior under M4.

## Inference

The prior V1 sufficiency result survives this experiment: the tested evidence-world state can still support CAL's pre-assessment measurement needs without importing proposition-specific judgments.

What does **not** survive is the stronger interface claim.

At the current revision, Contract B's research semantics are better described as a supported semantic/ownership model plus one working implementation than as a fully reproducible independent-consumer interface.

The distinction matters: semantic adequacy and interface reproducibility are separate claims.

## Falsified hypotheses

1. **Falsified:** the candidate profile alone determines a unique normalized pre-assessment ledger representation.
2. **Falsified:** Consumer A's exact pre-assessment projection can be reproduced without relying on conventions currently present only in implementation code.
3. **Not falsified:** V1 carries enough evidence-world information for the tested CAL pre-assessment use case.
4. **Not tested:** field-level minimality of V1.
5. **Not tested:** backward-compatible optional-extension feasibility/version class.

## Remaining unknowns

1. Once a physical V1 profile and ledger schema are frozen, will a newly isolated Consumer B reproduce Consumer A exactly?
2. Which history fields belong in the retained pre-assessment ledger versus the semantic-input payload?
3. Is `source_trust_level` required in the retained ledger even though it must not steer semantic measurement?
4. Should rejected-candidate history cross the CAL-facing contract, or be bound by a separate upstream receipt?
5. What is the exact normative distinction between an absent optional capability and an explicitly unknown value?
6. What malformed-input error equivalence is materially required across implementations?
7. Can the required additions remain a backward-compatible optional Contract-B extension? This experiment does not answer the version question.

## Disposition

# NOT REPRODUCIBLE

The candidate Contract-B research semantics do not yet define a sufficiently complete independent-consumer interface to require canonical ledger hash equality.

This disposition applies to **interface reproducibility**, not to the earlier supported claim of V1 evidence-world sufficiency.

## Specification changes justified by evidence

Before rerunning the independent-consumer experiment, add a research-only candidate specification for:

1. **Named physical V1 profile**
   - exact top-level fields and locations;
   - required versus optional fields;
   - allowed extra/sidecar behavior;
   - identity/reference constraints.

2. **Normative pre-assessment ledger schema**
   - exact retained identity/content/provenance fields;
   - exact preparation-history representation;
   - treatment of rejected candidates;
   - treatment of `source_trust_level` and similar non-authoritative metadata;
   - explicit separation from the narrower semantic measurement payload.

3. **Absence/unknown rules**
   - absent capability;
   - explicit unknown/null value;
   - prohibited default invention;
   - canonical encoding for each state.

4. **Canonicalization and hash algorithm**
   - serialization format;
   - key ordering;
   - list ordering or identity-sorting rules;
   - Unicode/number handling;
   - hash prefix/algorithm.

5. **Research V1 integrity envelope**
   - expected object hash or manifest;
   - reference/count invariants;
   - controlled-vocabulary version binding;
   - fail-closed error classes.

6. **Frozen reference artifact**
   - commit the exact serialized V1 reference bytes or preserve them as a durable fixture, not only a reported hash.

Then rerun Consumer B in a genuinely isolated context with only those documents plus the frozen V1 bytes. Do not expose Consumer A source until Consumer B source and baseline output are sealed.

No canonical Contract B modification is justified by this experiment alone. No Contract C work should begin from this result.