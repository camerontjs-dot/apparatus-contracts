# Contract E Authority-Chain Fresh Independent Reproduction RC1 — Sealed Evaluator Contract

## Classification

Sealed before fresh independent implementation. Research only. No production authorization.

## Primary question

Does a fresh implementation produced from only the frozen RC1 pre-freeze aperture independently recover the authority-chain behavior on unseen cases without post-reveal repair?

## Hidden corpus

The sealed corpus contains 94 cases and is frozen as a compressed payload with both compressed and canonical decompressed hashes. Cases include positive and negative coverage for every authority kind, recursive lineage, status-forgery, missing ancestry, cycles, source mismatch, non-conferring basis substitution, comparison narrowness, embedding/scope preservation, exact resolver jurisdiction, partial resolution, composition, decision/action separation, verification separation, blocking versus irrelevant residue/conflict, evidence preservation, and metamorphic pairs.

The hidden corpus is not available to the fresh implementer before its immutable freeze.

## Scored output

For every hidden case the fresh `evaluate(case)` output is compared against the frozen expected tuple:

- `allowed`;
- `status`;
- `reason`;
- `authority_kind`.

The following input evidence must also be preserved by exact structural equality:

- `raw_source`;
- `proposals`;
- `conflicts`;
- `residues`;
- `comparison_receipts`.

Any exception/non-dict output is preserved as a failure.

## Metamorphic scoring

Frozen pairs are marked `same` or `flip`.

- `same`: allowed outcomes must be identical.
- `flip`: allowed outcomes must differ.

## Terminal scientific state

`INDEPENDENT_RECOVERABILITY_SUPPORTED` requires all of the following:

- exact contract match on 94/94 cases;
- zero false permits;
- zero false rejects;
- zero exceptions;
- exact evidence preservation on 94/94 cases;
- all metamorphic pairs pass.

Anything less, after a valid completed apparatus run, yields `INDEPENDENT_RECOVERABILITY_FALSIFIED`.

The corresponding primary research disposition is:

- `SUPPORTED_FOR_PROMOTION` only when the supported state is reached;
- otherwise `FALSIFIED`.

`SUPPORTED_FOR_PROMOTION` is bounded to the next research/governance gate only. It is not production promotion, merge, release, Contract E 1.0.0, Authorization, or execution authority.

If the sealed payload, hash guards, comparator, evaluator self-controls, or qualification apparatus fail before scientific comparison, use `INCONCLUSIVE` and preserve the apparatus failure rather than treating it as a scientific disagreement.

## Evaluator assurance

Before any fresh implementation exists, qualification must prove:

1. the sealed reference exactly matches every frozen expected tuple and preservation requirement;
2. false permits are detected;
3. false rejects are detected;
4. evidence mutation is detected;
5. every authority kind has at least one positive and one negative hidden case;
6. pair cardinality and same/flip expectations are coherent;
7. a status-flag weak control falsely permits at least one status-forgery case;
8. an any-current-basis weak control falsely permits at least one non-conferring-basis case;
9. a bare-resolution-id weak control falsely permits at least one unauthorized-resolution case.

No evaluator rule may be changed after the fresh implementation freeze and counted as the same reproduction.
