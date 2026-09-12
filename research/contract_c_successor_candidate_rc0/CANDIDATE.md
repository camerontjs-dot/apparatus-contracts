# Contract C minimal in-band successor candidate RC0

**Classification:** Draft research successor candidate. This is not a canonical Contract C version, release, promotion, tag, Decision Engine production change, Contract E change, or operational authorization.

## Exact production base

This candidate is constructed directly from protected `apparatus-contracts/main`:

- base commit: `c3563cff66d2c85dcbf575c693056e2d8e4563d4`
- base tree: `0e2174571c7a0f449f8b5945569266847e9ba97c`
- released Contract C 1.0 spec blob: `8c15f2e5f4047ccd17e204fb23aee1168781b9d5`
- released Contract C 1.0 schema blob: `b0369de9b5c156322d6787261bbc7658a3b33781`
- released Contract C 1.0 validator blob: `9c75ccfbf2223578a8d1a7bf0c39673b394fbea4`
- released version registry blob: `6e805e274f8b1f491bf0c10735a46962ab91d2d4`

The released files above are invariants. This candidate must not modify them.

## Candidate identity

The provisional wire/profile identity remains the already-tested non-release sentinel:

`research-non-deciding-rc0`

Keeping the exact sentinel preserves the identity of the frozen handoff and the independent Consumer B evidence. It deliberately avoids assigning an official SemVer version before compatibility/promotion qualification.

## Evidence basis

This candidate is the smallest implementation surface justified by the completed research chain:

- Apparatus PR #85: bounded two-leaf non-deciding shadow delta supported;
- Apparatus PR #86: strict 1.0 consumers reject the successor unchanged; semantic downgrade laundering demonstrated; MAJOR signal if later promoted;
- Apparatus PR #89: richer attribution sidecar supported as a research vessel, but not as the smallest canonical architecture; separate sidecar member identity was not required;
- Decision Engine PR #72: current-main minimal in-band conformance supported;
- Research Scaffold Harness PR #29 / Decision run `34717144897`: fresh context-free Consumer B reproduction supported, with no hidden-evaluator exposure before freeze.

The decisive context-free handoff is reused byte-for-byte:

- `valid-shadow.json` Git blob: `14e88cbc691f7eba9366b4bf88611ef834637f27`
- whole-object SHA-256: `sha256:325962ebcdbf6af836bb6193a451524ccd40b4d10f2394ff9f703fbfce1ec1e3`
- result-set ID: `result-set:4483272c4f6fbd9cb2362be7e3174bbd00aff3cf761d6c374897f3478818c9f0`
- Contract-B index Git blob: `4de40713482a1fc5a075a230a61e19acc25afbd9`

## Normative candidate delta

Relative to released Contract C 1.0.0, this candidate changes exactly two semantic leaves:

1. `properties.contract_c_version.const` becomes `research-non-deciding-rc0`;
2. `$defs.contribution.properties.channel.enum` becomes `[support, counterevidence, non_deciding]`.

Candidate schema title/ID metadata may differ to identify the research surface. No other semantic schema difference is permitted.

All released Contract C 1.0 semantics are inherited unchanged unless one of the two leaves above explicitly differs.

## `non_deciding` meaning

`non_deciding` is CAL-attributable retained evidence state that is neither `support` nor `counterevidence` for the proposition conclusion.

A `non_deciding` contribution uses the existing Contract C machinery without a companion attribution object:

- existing `contribution_id`;
- existing exact Contract-B `evidence_ref`;
- existing conclusion `basis_members` for causal participation;
- existing `residual_contribution_ids` for residual participation;
- existing `causal_form` for multiplicity;
- existing proposition/result/whole-object bindings.

The channel does not authorize an action, imply support, imply counterevidence, create scalar confidence, select a winner, or carry Contract E authority.

## Explicitly excluded additions

This candidate does not add:

- sidecar `member_id`;
- sidecar `state_id`;
- sidecar receipt IDs;
- a second attribution object;
- duplicated source/proposition/hash fields already recoverable from Contract B;
- scalar confidence, probability, score, rank, or winner fields;
- destination policy, action, effect, routing, authority, or authorization fields.

## Validator construction rule

The candidate validator may reuse released 1.0 implementation/types for unchanged semantics, but it must not validate `non_deciding` by relabelling it as `support` or `counterevidence`.

The candidate types therefore extend only the contribution-channel vocabulary and exact provisional version while inheriting the released structural/reference/canonicalization rules.

## Candidate falsifiers

The candidate is invalid if any of the following occur:

1. released Contract C 1.0 spec/schema/validator/version-registry bytes change;
2. generated candidate schema differs semantically from released 1.0 anywhere outside the two declared leaves;
3. the frozen non-deciding handoff fails candidate validation;
4. candidate validation requires semantic relabelling of neutral evidence;
5. exact Contract-B evidence/proposition binding, causal/residual closure, multiplicity, result identity, policy identity, or whole-object binding is weakened;
6. support/counterevidence cease to be valid candidate channels;
7. unknown channels or unrelated new fields become accepted;
8. the candidate introduces sidecar-only or scalar/winner semantics not justified by the evidence;
9. released 1.0 accepts the successor bytes unchanged.

## Version and promotion boundary

No official Contract C successor version is assigned by this candidate.

Prior compatibility evidence records a **MAJOR-version signal if this exact in-band class is later promoted**, because legitimate strict 1.0 consumers reject it and no lossless 1.0 downgrade was demonstrated. That signal must be rechecked against this exact candidate during a separate qualification step before any promotion/version decision.

`schema/contract-c/versions.json` remains unchanged and must continue to declare canonical/supported `1.0.0` only.

## Promotion impact

None. This branch is evidence-generating candidate material only.

A later promotion decision, if supported, must use a separate minimal Promotion / Production PR from then-current protected `main`, with an explicit SemVer decision, migration/parallel-version notes, producer/consumer conformance, schema/spec/validator agreement, release acceptance gates, and an EDR or EDR update.
