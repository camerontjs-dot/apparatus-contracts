# Contract C non-deciding shadow RC0 terminal record

## Disposition

`SUPPORTED_BOUNDED_TWO_LEAF_SHADOW_DELTA`

This is a research-only structural/conformance result. It does not authorize a Contract C version, production schema/validator change, merge, release, tag, promotion, Decision Engine change, Contract E, or authorization.

## Exact execution

- exact tested head: `361f962fb8b0a43b208d739fd57e9aa1f1b364a0`
- exact production base: `c3563cff66d2c85dcbf575c693056e2d8e4563d4`
- run: `34528850394`
- artifact: `10172655148`
- artifact digest: `sha256:94b5edd27cc2515ce9af3c460d88a821c1d59d477c18c97d832a543df2479f24`
- shadow object SHA-256: `sha256:34e3b84357e4424fb69c41fc228c2feda81d73d12bd103ee46132a9bb832f017`
- shadow result-set identity: `result-set:b6c9a7aa7ab0f627fb4cb4d29eb7638a03e8e21f9f5c7aa360f42e99b357ee2b`

## Exact released authority held fixed

- released Contract C validator blob: `9c75ccfbf2223578a8d1a7bf0c39673b394fbea4`
- released Contract C schema blob: `b0369de9b5c156322d6787261bbc7658a3b33781`
- released Contract C 1.0 files were not modified.

## Observed results

The shadow schema differed semantically from released 1.0 at exactly two leaves:

1. `properties.contract_c_version.const`
2. `$defs.contribution.properties.channel.enum`

The only new contribution channel was `non_deciding`.

All preregistered structural controls passed, including:

- one causal non-deciding contribution;
- two causal non-deciding contributions preserving `independent_sufficient_alternatives`;
- residual non-deciding contribution classification;
- legacy support and counterevidence compatibility inside the shadow;
- exact Contract-B evidence-reference checking;
- causal/residual disjointness;
- complete retained-contribution classification;
- causal-form cardinality;
- unknown-field rejection;
- unknown-channel rejection;
- deterministic canonical bytes and result-set identity;
- whole-object hash tamper rejection;
- detection of unrelated schema relaxation.

Released Contract C 1.0 rejected the shadow object specifically because the research wire sentinel is not `1.0.0` and `non_deciding` is not a released 1.0 channel. This is the intended version-boundary negative control.

Released Contract C regression on the same job: `17 passed, 8 skipped`.

## Bounded inference

Within this frozen Apparatus pressure test, the CAL PR #100 survivor can be represented without widening unrelated Contract C semantics. The smallest tested semantic schema delta is one new contribution-channel value plus an explicit research-only wire-version sentinel.

This supports preparing an independent consumer handoff. It does not establish a canonical versioning strategy or production compatibility policy.

## Next falsifier

Freeze only the shadow spec/schema/valid fixture/Contract-B index and their exact hashes. Give those artifacts to a separate consumer without the shadow implementation or evaluator. Require that consumer to reconstruct exact non-deciding provenance and causal multiplicity, reject malformed references/cardinality/version mutations, and demonstrate that destination policy behavior does not reinterpret `non_deciding` as support or counterevidence.