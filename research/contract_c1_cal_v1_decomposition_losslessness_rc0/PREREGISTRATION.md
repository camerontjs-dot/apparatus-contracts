# Contract C 1.0 × CAL V1 Decomposition Losslessness RC0 — Preregistration

Date: 2026-09-18

Classification: Draft Research Infrastructure / boundary sufficiency discriminator.

## Live canonical authority

Contract C canonical version at experiment start:

- `schema/contract-c/versions.json`: canonical `1.0.0`, supported `[1.0.0]`;
- specification blob: `8c15f2e5f4047ccd17e204fb23aee1168781b9d5`;
- schema blob: `b0369de9b5c156322d6787261bbc7658a3b33781`;
- validator blob: `9c75ccfbf2223578a8d1a7bf0c39673b394fbea4`.

No Contract C successor is treated as canonical.

## Exact CAL evidence under test

The source state is frozen by Claim Audit Lab Draft Research PR #178:

- terminal record head: `47d7067476088e7b5b86944ec0df72ef949f5127`;
- exact integrated code/test head: `b695a1ca16051fde1c204987895b672e73225168`;
- decisive run: `35368736767`;
- route: Contract A 2.0 -> EB #79 -> Contract B 1.2 -> CAL child results -> DecompositionComposer;
- replay: byte-identical child CAL results and identical parent decomposition receipt.

The parent result is not merely a verdict. It is bound to:

- Contract A decomposition identity;
- `all_of` operator;
- ordered child proposition identity/text hash;
- exact immutable child CAL result identities;
- parent conclusion;
- deterministic decomposition receipt identity.

## Question

Can released Contract C 1.0 represent and independently verify that exact parent/child recomposition state without:

1. inventing a producer-private codec inside opaque `state:` IDs;
2. repurposing `producer.policy` as run-specific result storage;
3. overloading `terminal_branch`, `rule_roles.code`, or array order with semantics not established by Contract C;
4. using an external sidecar not bound by Contract C?

## Strongest legitimate C1 attempt

The discriminator grants C1 every existing relevant mechanism:

- one C1 proposition record for each child and the parent;
- exact proposition identity and text hash;
- exact child verdicts and parent verdict;
- parent `jointly_sufficient` causal form for supported `all_of`;
- parent rule role identifying CAL's all-of recomposition rule;
- parent `state:` basis members carrying opaque CAL-attributable state identities for each child result and the decomposition receipt;
- exact C1 whole-object identity and result-set identity;
- exact Contract B proposition/evidence binding.

This is intentionally stronger than a naive proposition-only encoding.

## Required recovery target

An independent consumer must recover and verify, as typed state rather than opaque string coincidence:

- `decomposition_id`;
- operator `all_of`;
- ordered child proposition IDs;
- ordered child text hashes;
- exact child CAL result identities;
- exact parent decomposition receipt identity.

The consumer may use:

- canonical Contract C 1.0 semantics;
- the bound Contract B index/artifact.

It may not use:

- CAL implementation source;
- a producer-private parser for arbitrary `state:` strings;
- Contract A as an unbound side input;
- a sidecar;
- undocumented interpretation of array position.

## Falsifiers

The current C1 surface is insufficient if all of the following hold:

1. the strongest legitimate C1 object validates;
2. replacing a child-result `state:` basis ID with another well-formed opaque state ID, followed by legitimate C1 reidentity, also validates;
3. replacing the decomposition-receipt `state:` basis ID likewise validates;
4. the C1 + Contract B consumer has no standard reference target against which either state ID can be checked;
5. two different upstream decomposition IDs can preserve the same C1 contract-defined typed semantics unless the producer encodes the ID through an extra private convention;
6. a payload-smuggling control can structurally validate only because C1 treats the state ID as opaque, demonstrating transport capacity rather than contract-defined recoverability.

## Interpretation rule

Do not conclude that C1 is mathematically incapable of carrying bytes. Its opaque strings can carry arbitrary text.

The relevant claim is narrower:

> Does canonical Contract C 1.0 provide a contract-defined, independently verifiable representation of the new CAL V1 decomposition binding?

If only a producer-private encoding can recover the state, classify C1 as **not lossless as shared contract authority**.

## Stopping rule

If the falsifiers hold, record:

`C1_CANNOT_AUTHORITATIVELY_BIND_CAL_V1_DECOMPOSITION_RC0`

and identify the smallest missing authority surface. Do not design or promote C2 in this experiment.

If C1 can independently recover and verify the exact lineage using only canonical semantics, record the successful encoding and stop.

No production Contract C, CAL, Decision Engine, release, tag, or version mutation is authorized.
