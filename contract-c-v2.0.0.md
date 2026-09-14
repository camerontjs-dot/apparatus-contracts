# Contract C 2.0.0

Status: production promotion candidate. This file does not make Contract C 2.0.0 canonical until the promotion, producer, consumer, compatibility, adversarial, release-lock, and immutable-release gates complete.

Promotion authority: EDR-005 / GitHub issue #97.

## Role

Contract C is the immutable, decision-agnostic public representation of CAL-attributable result state required by a legitimate downstream decision consumer. It binds the result to the exact Contract-B evidence world and exact CAL semantic/policy authority that produced it without importing downstream Decision policy, Contract E Authorization, actor/delegation state, or execution permission/occurrence.

## Public compatibility version and frozen wire profile

Public compatibility version: `2.0.0`.

Integrity-bearing wire profile: `contract-c-successor-candidate-a-rc2-research`.

The wire profile is intentionally retained from the exact frozen Candidate A RC2 subject. Renaming that field would change canonical bytes, result-set identities, whole-object hashes, and the subject qualified by the producer and independent-consumer evidence programme. Contract version discovery is therefore kept outside the integrity-bearing object, following the same promotion pattern used by Contract A 2.0.0.

Version registry: `schema/contract-c/versions.json`.

Exact frozen wire specification: `schema/contract-c/2.0.0/wire-spec.md`.

Exact frozen JSON Schema: `schema/contract-c/2.0.0/schema.json`.

Production entry point: `validators.contract_c_v2`.

## Required semantic obligations

The 2.0 surface preserves the exact tested Candidate A RC2 obligations:

- exact Contract-B version, bundle identity, and bundle hash;
- exact CAL semantic implementation, policy digest, and immutable policy-resolver authority;
- exact proposition identity and proposition-content hash;
- result-set execution state distinct from proposition execution/completion state;
- public evidence participation by exact Contract-B source/passage identity;
- participant relation `supports | refutes | non_polarized`;
- independent participant role `causal | residual`;
- canonical families of minimal sufficient `basis_groups`, including multiple alternative sufficient groups without inventing a unique winner;
- stable terminal verdict/reason distinctions, including exact `MIXED_RELATIONS` and `UNSUPPORTED_SEMANTIC_FAMILY`;
- deterministic canonicalization and content-derived local result-set identity;
- independently supplied whole-object handoff authority;
- fail-closed unknown-field/profile/authority behavior.

## Compatibility

Contract C 2.0.0 is **MAJOR / breaking** relative to 1.0.0.

Contract C 1.0.0 remains immutable historical authority. A 2.0 object must not be silently translated or downgraded to 1.0 by deleting or relabelling basis-group, participant-role, relation, unsupported-family, or execution-state semantics. Exact-version consumers must select authority independently rather than letting an object choose its own validator.

No lossless C2 -> C1 downgrade is claimed or authorized.

## Canonicalization and identity

The frozen RC2 canonicalization rules are normative for this promotion candidate. Arrays representing participants, basis groups, proposition rows, and members are normalized exactly as specified by the frozen validator before local `result_set_id` derivation. Whole-object SHA-256 remains a separate externally supplied handoff-authority check.

The production adapter may change only import/package wiring relative to the frozen RC2 validator. Differential conformance against the frozen RC1/RC2 source authorities is required before merge.

## Release boundary

This promotion does not establish CAL semantic correctness, Evidence Bundler retrieval completeness, source legitimacy, Decision Engine policy correctness, Contract E Authorization, operational execution, or automatic MainFrame/Brain mutation.

Before merge/release, require at minimum:

1. exact wire-spec/schema blob preservation;
2. production-adapter equivalence to the frozen Candidate A RC2 validator;
3. exact CAL producer conformance against this promotion head;
4. exact independent-consumer conformance against this promotion head;
5. RC2-specific 1.0/2.0 compatibility matrix and no-downgrade controls;
6. adversarial mutation and seeded weak-validator/consumer discrimination;
7. clean repository tests and release-artifact reproducibility;
8. a separate post-merge release lock before immutable `contract-c-v2.0.0` publication.

Any new in-domain counterexample stops promotion and returns to the smallest discriminating successor experiment. Do not widen this production PR merely to turn a red gate green.
