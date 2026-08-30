# Contract D RC3 — Independent Consumption Authority Hardening Preregistration

**PR class:** Research / apparatus-contract hardening  
**Branch:** `research/contract-d-independent-authority-rc3`  
**Production impact authorized:** none

## Exact live authorities at preregistration

- `camerontjs-dot/apparatus-contracts` main: `00bdf9546a877f9f6c1d7fd227fd959e1d7aa99e`
- Contract D coordination issue: `camerontjs-dot/apparatus-contracts#22`
- `camerontjs-dot/decision-engine` main: `ff7a0f63e5f7075b192dff04064b950bf7255ffa`
- promoted Decision / Authorization boundary: `f7c3759dfac7ee4be45879b8266b5eb1440530ee`
- Contract D research PR #19 fixed reference head: `6c1ddb5a6b6b1a5373261e41d64a4baee83e0efb`
- RC0 preregistration: `6d6f003cc705264e4f8ecda24602da1da1820bc0`
- RC0 written results: `cc27d766d751dbc1d062e0790f2bee5e04276c23`
- RC1 preregistration: `785a407e71797e88c89e81fd164302c05785d9d0`
- RC2 preregistration: `bc1cc749bcea5a12aa66f6ac091cc17a8463991c`
- RC2 reference head / hosted execution head: `6c1ddb5a6b6b1a5373261e41d64a4baee83e0efb`
- `camerontjs-dot/research-scaffold-harness` main: `548bfa81f65290eda15af658f647497679b840ef`
- prior fresh reproduction preregistration: `3b63269b29488b7ffe45d2933eab0fec0279c5b4`
- prior fresh reproduction freeze: `43f3acc4e2c8a456e38723ee7031d89e75086529`
- prior post-reveal comparison: `0a50f01c288634e115091bafa85284672b9f8c43`
- prior terminal results: `0ad80dbecca43dc3a057d015617914d742f32d23`
- prior fresh reproduction terminal disposition: `CROSS_REPOSITORY_CONFORMANCE_FAILED`

## Research question

Can the presently supported Contract D semantic core be encoded as the smallest complete, research-only, mechanically consumable authority package such that a competent independent implementation can determine all authority-relevant behavior from the apparatus package alone, without Decision Engine internals, prior Contract D reasoning, or downstream reinterpretation of Contract C semantics?

This run does not test independence. It hardens and freezes the authority that a later isolated run may attempt to reproduce.

## Predecessor evidence preserved

The predecessor is immutable experimental evidence, not a draft to repair.

Observed predecessor findings to preserve:

1. the independent implementation recovered the Contract D semantic spine before reference reveal;
2. native Decision Engine -> independent consumer interchange failed;
3. the first native failure was version/serialization disagreement;
4. diagnostic alignment then exposed disposition/effect-version representation differences;
5. after representation alignment, no shared published typed effect registry existed, so the independent consumer returned unknown effect / cannot establish;
6. unknown structural-field handling was underspecified;
7. canonical bytes and semantic-identity projection were underspecified;
8. the RC2 local consumer failed to bind request target kind and did not externally pin upstream/policy applicability;
9. RC1, rather than RC2 alone, carried the unknown-effect/version fail-closed evolution behavior;
10. reason/explanation/diagnostic material was not required for downstream authority;
11. stored Decision ID was not demonstrated as necessary when semantic identity was derivable.

No RC3 artifact may amend away those observations.

## Bounded candidate semantic hypothesis

The smallest currently supported candidate semantic core is:

1. exact Contract D version identity;
2. exact upstream authority binding;
3. exact Decision policy identity/version;
4. exact target kind, target id, and immutable target content/version identity;
5. evaluation state distinct from policy disposition;
6. completed CLEAR versus completed HOLD, with Decision evaluation failure establishing no disposition/effect authority;
7. typed/versioned effect with machine-semantic parameters;
8. a deterministic semantic identity over authority-bearing semantics only;
9. Authorization-only state remains external and cannot change Decision semantic identity.

Candidate explanatory metadata such as reason codes, explanations, and diagnostics is non-authoritative unless a later experiment promotes a specific machine semantic into a typed effect field.

## Competing choices to discriminate

### Version representation

- exact semantic-version string on wire;
- alternate aliases/legacy wire tokens;
- permissive forward-version parsing.

Default hypothesis to test: one exact declared candidate version token is normative and unknown/future Contract D versions fail closed.

### Unknown structural fields

- strict rejection for an exact declared Contract D version;
- preservation/ignore at explicitly extension-safe locations.

Default hypothesis to test: strict rejection is the smaller safe rule for the exact RC3 version. The package may contain intentionally opaque metadata only if tests establish that it cannot alter authority.

### Upstream authority immutable binding

- kind + id only;
- kind + id + opaque immutable content/version identity.

Hypothesis: independent applicability requires an exact immutable upstream binding when the upstream authority can otherwise be replayed under the same logical id. The consumer must compare identity, not reinterpret upstream epistemic semantics.

### Semantic identity

- hash entire transport object;
- hash authority-bearing projection only;
- trust a stored opaque `decision_id`.

Hypothesis: semantic identity is derived from a normative authority projection; explanatory metadata and Authorization-only state are excluded. A stored Decision ID is unnecessary unless it can add a tested authority capability.

### Canonicalization

- transport-byte identity equals semantic identity;
- deterministic canonical transport plus separate semantic projection.

Hypothesis: transport canonicalization is deterministic, while semantic identity may exclude non-authoritative metadata. Formatting-only changes must not change parsed semantic identity, but noncanonical received bytes may still be rejected when canonical bytes are explicitly required.

### Effect evolution

- unversioned effect strings;
- typed/versioned registry with exact parameter schemas/defaults;
- free-form reason-driven interpretation.

Hypothesis: a typed/versioned effect registry is necessary; unknown type/version/parameter must never silently acquire authority.

## Authority-relevant invariants

A conforming candidate must make the following mechanically decidable:

- exact version support;
- completed versus failed evaluation;
- CLEAR versus HOLD;
- target kind/id/content applicability;
- upstream authority kind/id/immutable identity applicability;
- policy id/version applicability;
- effect type/version/parameter meaning;
- requested-operation applicability;
- unknown/future behavior;
- explanation versus authority distinction;
- semantic identity and Authorization-only invariance.

Contract D must not acquire actor identity, approval state, delegation state, autonomy state, execution permission, execution state, or execution receipt authority.

## Required positive controls

At minimum:

- source-audit / knowledge effect;
- citation-use effect;
- task-dispatch effect;
- completed CLEAR;
- completed HOLD;
- Decision evaluation failure.

## Required authority mutations

Independently mutate:

- Contract D version;
- upstream authority kind;
- upstream authority id;
- upstream immutable identity;
- policy id;
- policy version;
- target kind;
- target id;
- target immutable content/version identity;
- evaluation state;
- disposition;
- effect type;
- effect version;
- every machine-semantic effect parameter.

Each valid authority-bearing mutation must change semantic identity. Invalid mutations must be rejected rather than normalized into authority.

## Required invariance tests

Mutate independently:

- actor;
- trust/profile;
- human approval;
- delegation;
- Authorization context;
- requested operation in the external request;
- reason codes;
- explanation;
- diagnostics.

Authorization outcome may change from external Authorization-only mutations while the Decision semantic identity remains unchanged. Reason/explanation/diagnostic mutations must not alter semantic identity or machine authority.

## Required replay/substitution attacks

- effect reused for a different requested operation;
- Decision used for another target id;
- same target id with different immutable content;
- same target id/content under different target kind;
- policy substitution;
- policy-version substitution;
- upstream-authority kind/id/immutable substitution.

## Required future/unknown tests

- unknown Contract D version;
- unknown evaluation state;
- unknown disposition;
- unknown effect type;
- unknown effect version;
- unknown machine parameter;
- unknown structural field.

No unknown item may silently obtain current-version Decision authority.

## Required injection tests

Inject at every plausible Contract-D-owned object level where mechanically possible:

- actor;
- requested operation;
- approval;
- delegation;
- autonomy;
- execution permission;
- execution state;
- execution receipt.

The exact-version validator must either reject the injected structure or prove that it is inside an intentionally opaque non-authoritative container. No injected field may affect Decision semantic identity or applicability.

## Field/minimality ablation

For every normative field or field family, remove it and record the exact capability lost. A field is not justified merely because the candidate implementation uses it.

The candidate is weakened if a required field can be removed without changing any authority-relevant behavior in the full frozen suite.

## Evaluator assurance

Treat validator, canonicalizer, semantic-identity implementation, effect registry, and consumer applicability oracle as systems under test.

Required intentionally weak controls include:

- generic `eligible=true` / disposition-only consumer;
- target-id-only consumer;
- target-id/content consumer ignoring target kind;
- consumer treating HOLD as evaluation failure;
- consumer inferring effect from reason text;
- consumer accepting unknown effect/version;
- consumer ignoring policy binding;
- consumer ignoring upstream-authority binding;
- semantic identity that changes under actor/context changes.

The suite must reject each weak control for the intended semantic reason.

## Cross-repository reference validation

After the RC3 apparatus package exists, the existing Decision Engine research producer at fixed reference head `6c1ddb5a6b6b1a5373261e41d64a4baee83e0efb` will be tested against the candidate package.

The candidate must not be changed merely to make the reference producer pass. Every mismatch must be classified as one of:

- contract candidate defect;
- Decision Engine reference defect;
- prior implementation artifact;
- specification ambiguity;
- representation-only difference;
- evaluator defect;
- unknown.

Any Decision Engine adaptation remains research-only and separate from production behavior.

## Preregistered falsifiers

Serious negative evidence includes any of:

1. two reasonable consumers can still derive different authority-relevant behavior from the package;
2. a consumer requires Decision Engine internals or undocumented knowledge;
3. target kind/id/content cannot all be bound mechanically without unrelated semantics;
4. effect meaning still depends on prose/reason text;
5. unknown effect/version can produce actionable authority;
6. Authorization-only state changes Decision semantic identity;
7. Contract D requires downstream reinterpretation of Contract C semantics;
8. HOLD and evaluation failure cannot remain distinguishable;
9. canonicalization/identity requires hidden assumptions;
10. the suite accepts an intentionally weak plausible consumer violating a claimed invariant;
11. a supposedly normative field can be removed with no authority-relevant behavioral difference;
12. a future independent implementation would still need prior research results to know what to implement.

Do not redefine these after observing results.

## Candidate freeze requirement

If the package survives the preregistered tests, freeze it before any successor clean-room implementation. The freeze receipt must record base SHA, preregistration SHA, candidate freeze SHA, exact spec/schema/validator/canonicalizer/registry/fixture/conformance identities, CI receipts, deviations, and unresolved questions.

Any post-freeze repair becomes RC4 or another explicitly versioned successor.

## Planned clean-room successor

A later separate Context-Free execution will implement an independent consumer in a genuinely isolated repository/surface using only the frozen RC3 apparatus package and explicitly allowed durable governance inputs.

Pre-freeze forbidden material will include Decision Engine Contract D implementation files, prior fresh reproduction implementation/tests/predictions/results, PR/issue narrative revealing expected disagreements, and this conversation.

The successor success criterion is native:

`Decision Engine -> frozen Contract D RC3 object -> independent consumer`

with no bespoke translation adapter and agreement on all authority-relevant behavior named above.

## Allowed terminal research dispositions

Primary:

- `SUPPORTED FOR PROMOTION`
- `FALSIFIED`
- `INCONCLUSIVE`
- `SUPERSEDED`

Secondary Contract-D finding may include:

- `READY_FOR_FRESH_INDEPENDENT_REPRODUCTION`
- `CONTRACT_AUTHORITY_STILL_UNDERSPECIFIED`
- `REFERENCE_IMPLEMENTATION_DEFECT`
- `SEMANTIC_CORE_REQUIRES_REVISION`

`READY_FOR_FRESH_INDEPENDENT_REPRODUCTION` is not Contract D promotion and does not predict that reproduction will succeed.

## Explicit non-claims

This experiment does not authorize:

- Contract D production release or merge;
- production Decision Engine behavior changes;
- production Authorization machinery changes;
- automatic execution or mutation;
- Decision/Authorization interface collapse;
- reinterpretation of Contract C epistemic semantics downstream.
