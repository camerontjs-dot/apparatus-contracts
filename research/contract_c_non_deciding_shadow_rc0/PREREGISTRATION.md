# Contract C non-deciding shadow RC0

**Classification:** Draft Research Infrastructure experiment. No production Contract C mutation, version assignment, release, merge, promotion, Decision Engine production change, Contract E, or authorization.

## Exact base

- Apparatus Contracts `main`: `c3563cff66d2c85dcbf575c693056e2d8e4563d4`
- Released Contract C validator blob: `9c75ccfbf2223578a8d1a7bf0c39673b394fbea4`
- Released Contract C schema blob: `b0369de9b5c156322d6787261bbc7658a3b33781`
- CAL repair-comparison PR #100 terminal pressure-test head: `aa5f0f1313e65e6d31493095214c76d743ca6d89`
- Frozen CAL repair-candidate implementation blob: `a7934b3c242dcf1c33a28121b3b141c9c6adc203`
- CAL multiplicity run: `34506201889`
- CAL multiplicity artifact: `10163899726`
- CAL multiplicity artifact digest: `sha256:23ba4cb13870f0b2c5f213d3279faede9d17f19e638dea49444249328a0efb19`

## Question

Can the exact surviving representation family from CAL PR #100 be expressed as a research-only Apparatus shadow contract by adding only one contribution-channel value, `non_deciding`, while preserving the released Contract C 1.0 structural, canonicalization, reference-integrity, Contract-B-binding, causal-multiplicity, and whole-object-identity rules?

## Frozen shadow delta

The shadow wire value is deliberately non-canonical: `research-non-deciding-rc0`.

Relative to released Contract C 1.0.0, the shadow schema may change only:

1. top-level `contract_c_version.const` from `1.0.0` to `research-non-deciding-rc0`;
2. `$defs.contribution.properties.channel.enum` from `[support, counterevidence]` to `[support, counterevidence, non_deciding]`.

No other schema leaf, required field, namespace, causal-form value, assessment state, measurement shape, proposition binding, evidence reference, producer binding, Contract-B binding, or result identity rule may change.

## Validation strategy

The research validator must not fork Contract C semantics wholesale. It must:

- verify the exact two-leaf schema delta above;
- validate shadow whole-object identity with the released canonicalization/result identity algorithm;
- project only the wire sentinel and `non_deciding` channel values to a compatibility copy accepted by the released 1.0 validator;
- run the released validator over that compatibility copy with the exact Contract-B index;
- preserve the actual shadow object for all provenance/multiplicity assertions;
- require at least one `non_deciding` contribution so an unchanged 1.0 object cannot accidentally satisfy the shadow test.

## Preregistered positives

P1. One causal `non_deciding` contribution can be referenced as a normal contribution basis member for a completed `not_checkable` proposition.

P2. Two causal `non_deciding` contributions can be represented as two distinct basis members with `causal_form=independent_sufficient_alternatives`.

P3. Every shadow evidence reference must bind exactly to the supplied Contract-B index.

P4. A `non_deciding` contribution can remain residual without being forced into causal basis.

P5. Existing `support` and `counterevidence` values remain structurally valid in the shadow validator.

P6. The released Contract C 1.0 validator rejects the shadow artifact rather than silently accepting the widened channel or wire sentinel.

P7. Canonical bytes and `result_set_id` remain deterministic under the released algorithm.

## Preregistered falsifiers

F1. The shadow validator must reject a non-deciding basis member whose contribution is absent.

F2. It must reject a contribution reference absent from or mismatched against Contract B.

F3. It must reject `single_necessary` with two basis members and `independent_sufficient_alternatives` with fewer than two.

F4. It must reject a contribution classified simultaneously as causal and residual.

F5. It must reject any retained contribution left unclassified by basis or residual state.

F6. It must reject whole-object/result-set identity tampering.

F7. It must reject arbitrary additional fields.

F8. It must reject unknown channel values other than the exact three frozen values.

F9. The released 1.0 validator accepting a shadow object is a version-boundary failure.

F10. Any implementation requirement to weaken an unrelated released invariant falsifies the minimal-delta claim.

## Allowed outcomes

- `SUPPORTED_BOUNDED_TWO_LEAF_SHADOW_DELTA`
- `FALSIFIED_MINIMAL_SHADOW_DELTA`
- `INCONCLUSIVE_SHADOW_VALIDATOR_INVALID`

A supported result means only that the representation survives this Apparatus research boundary. It does not select a canonical Contract C version or authorize production change.