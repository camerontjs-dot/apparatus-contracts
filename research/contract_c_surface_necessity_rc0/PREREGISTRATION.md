# Contract C surface necessity RC0 preregistration

Status: **PREREGISTERED / NOT YET SCORED**

This is a research experiment. It does not modify released Contract C 1.0.0, assign a successor version, authorize a sidecar standard, mutate Decision Engine production behavior, promote CAL, release/tag anything, or perform operational Authorization.

## Exact lineage

- repository: `camerontjs-dot/apparatus-contracts`
- protected production `main` observed at start: `c3563cff66d2c85dcbf575c693056e2d8e4563d4`
- exact research base: richer sidecar RC1 terminal head `f58f531abf6f2c8ab264db41346592b1498514d0` from Draft PR #87
- released Contract C authority: `5fe55f9ed5d0ee9f026ca1b077e9d70ce0487ea1`
- released Contract C specification blob held fixed: `8c15f2e5f4047ccd17e204fb23aee1168781b9d5`
- released Contract C schema blob held fixed: `b0369de9b5c156322d6787261bbc7658a3b33781`
- released Contract C validator blob held fixed: `9c75ccfbf2223578a8d1a7bf0c39673b394fbea4`
- EDR-002 authority: Apparatus issue #17
- qualified in-band non-deciding research authority: Draft PR #85 / receipt `ad1ffbd7906a7cf34cce5afa906a5797cd4a14ff`
- qualified richer sidecar research authority: Draft PR #87 / terminal head `f58f531abf6f2c8ab264db41346592b1498514d0`

## Authority observation before experiment

EDR-002 and released Contract C 1.0.0 define Contract C as the immutable, decision-agnostic representation of CAL-attributable epistemic/result state required by legitimate downstream consumers. EDR-002 explicitly lists retained contribution/provenance state, including non-deciding/residual contributions, as a required semantic obligation.

Therefore this experiment does **not** begin from the assumption that a companion sidecar is already an equally authorized canonical alternative. The sidecar is used as a research vessel to determine the smallest semantic and integrity surface justified by consumer necessity. Any later architectural change to make a companion receipt canonical would require an explicit authority/EDR decision.

## Question

Which pieces of the current in-band `non_deciding` candidate and richer sidecar are actually necessary for legitimate downstream capabilities, and which are redundant, convenience-only, or integrity scaffolding?

The experiment must distinguish:

1. **semantic necessity**: omission makes a legitimate consumer unable to reconstruct a materially distinct CAL-attributable state without guessing;
2. **integrity necessity**: omission permits replay, substitution, stale binding, or silent carrier/sidecar mismatch;
3. **policy irrelevance**: omission does not affect a destination policy that legitimately needs only the Contract C verdict/state;
4. **representation choice**: multiple encodings may preserve the same necessary invariant, so this experiment may support an invariant without canonizing a field name or JSON shape.

## Research vessel

Build a research-only attribution vessel over exact released Contract C 1.0 carriers. The vessel may express neutral/non-deciding evidence as:

- role: `causal_non_deciding` or `residual_non_deciding`;
- exact Contract-B evidence reference: source, passage, passage hash;
- stable member identity;
- proposition binding;
- exact Contract C version/result-set/whole-object binding;
- optional state-basis binding where an opaque Contract C `state:` basis member is being elaborated;
- proposition-level causal form;
- canonical receipt identity and external whole-object digest.

The vessel is deliberately a superset. Ablation determines which elements survive necessity pressure.

## Consumer capabilities under test

### C1: destination-policy consumer

Given Contract C terminal state/verdict, produce the same bounded policy outcome regardless of attribution-vessel content. For a `not_checkable` proposition the control outcome is HOLD. For a released supported control the outcome is CLEAR. Neutral attribution must never create support/counterevidence or authorization.

### C2: attribution reconstruction consumer

Recover every retained neutral evidence reference and distinguish causal from residual evidence without producer-private code or semantic re-audit.

### C3: causal multiplicity consumer

Distinguish at least:

- one necessary causal member;
- two independently sufficient alternatives;
- two jointly sufficient members;
- residual-only/non-deciding evidence.

Same evidence members with different causal forms must remain observably different.

### C4: integrity/conformance consumer

Fail closed on carrier, proposition, state, Contract-B evidence, receipt/member identity, canonicalization, and whole-object substitution/replay where the corresponding binding is claimed to be necessary.

### C5: audit/explanation reconstruction consumer

Produce a structured, non-prose reconstruction containing exact causal evidence, exact residual evidence, causal form, proposition identity, and carrier identity. It must not invent a unique winner or polarity.

## Frozen positive shapes

At minimum evaluate:

1. causal single neutral evidence;
2. two neutral causal alternatives with `independent_sufficient_alternatives`;
3. two neutral causal members with `jointly_sufficient`;
4. supported result plus neutral residual evidence;
5. neutral residual-only / non-deciding result;
6. two opaque `state:` basis members where the vessel elaborates only one state, to test whether state binding is genuinely necessary in a sidecar architecture;
7. released supported Contract C 1.0 control with no sidecar requirement.

## Ablation / mutation matrix

Pressure at least these elements independently and, where useful, metamorphically:

- role classification;
- causal form;
- member list;
- member identity;
- source ID;
- passage ID;
- passage hash;
- proposition ID;
- proposition text hash;
- state-basis ID;
- Contract C version binding;
- Contract C result-set identity;
- Contract C whole-object hash;
- Contract-B bundle/index binding;
- sidecar receipt identity;
- external sidecar whole-object digest;
- canonical member ordering;
- missing sidecar;
- sidecar from a different proposition;
- sidecar from a different but structurally similar carrier;
- support/counterevidence laundering of a neutral member;
- dropping neutral evidence entirely;
- mapping neutral evidence to support;
- mapping neutral evidence to counterevidence.

Also test pairwise indistinguishability where a field is suspected necessary. Example: if `causal_form` is removed, two objects with the same members but `independent_sufficient_alternatives` versus `jointly_sufficient` should collapse to the same observable representation; that collapse is evidence of necessity.

## Expected classification rule

For each candidate element emit a matrix over C1-C5:

- `REQUIRED_SEMANTIC` if its removal makes two materially distinct CAL-attributable states indistinguishable or forces guessing;
- `REQUIRED_INTEGRITY` if semantic reconstruction remains possible but safe binding/replay resistance fails;
- `CONDITIONALLY_REQUIRED` if required only for a specific carrier shape, such as multiple opaque state basis members;
- `NOT_REQUIRED_FOR_TESTED_CAPABILITIES` if all tested legitimate capabilities remain intact after removal;
- `INCONCLUSIVE` if the apparatus cannot discriminate.

A field may have different classifications for different capabilities.

## Strong falsifiers

- If a claimed semantic field can be removed while C2/C3/C5 remain exact across all positive shapes, do not call it semantically necessary.
- If a binding can be removed without enabling any preregistered replay/substitution mutation, do not call it integrity-necessary.
- If destination policy changes solely because neutral attribution is present or mutated, the policy firewall is falsified.
- If the vessel cannot represent both causal and residual neutral evidence without ambiguity, the vessel is falsified as a useful research instrument.
- If an in-band representation and a vessel representation disagree about exact evidence membership or causal multiplicity for the same frozen semantics, stop and mark inconclusive/falsified rather than choosing the preferred architecture.
- If released Contract C 1.0 bytes/schema/validator change, the experiment is invalid.

## In-band comparison

Use the already-qualified PR #85 shadow as the in-band reference point. Its semantic delta from released 1.0 is intentionally tiny: a research version sentinel plus `non_deciding` added to the existing contribution channel enum. The experiment should compare **invariants**, not merely byte size or field count.

## Governance test

Separately from executable capability tests, compare the result against EDR-002. Technical sidecar sufficiency cannot by itself override EDR-002's current requirement that retained non-deciding/residual contribution provenance is part of Contract C's semantic obligation.

Possible terminal outcomes include:

- `SUPPORTED_MINIMAL_IN_BAND_INVARIANTS`: ablation identifies a bounded set of invariants that align naturally with the in-band candidate;
- `SUPPORTED_COMPOSED_HANDOFF_CANDIDATE`: a companion architecture is technically sufficient and no tested consumer requires Contract C-alone sufficiency, but this remains blocked on explicit EDR authority change;
- `FALSIFIED_SIDECAR_RESEARCH_VESSEL`;
- `INCONCLUSIVE_SURFACE_NECESSITY`.

More than one technical finding may coexist with an authority blocker.

## Stop boundary

Do not merge, promote, release, tag, assign `2.0.0`, amend released Contract C, mutate maintained Decision Engine, or authorize a sidecar standard in this experiment. Preserve every failed/deviating run and evaluator correction.