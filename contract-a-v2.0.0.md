# Contract A v2.0.0

**Status:** canonical production contract after the Contract A 2.0.0 promotion gate passes; released only at the immutable `contract-a-v2.0.0` release identity after the separate release-lock gate completes.

## Purpose

Contract A is the upstream declaration/source-representation handoff into Evidence Bundler for one authoritative root audit proposition. It identifies who produced the handoff, which upstream work object is represented, the exact root proposition, explicit decomposition state and declared `all_of` lineage where present, the exact UTF-8 source representations supplied downstream, and a whole-object integrity binding.

Contract A does not establish proposition truth, decomposition correctness, source trustworthiness, retrieval quality or completeness, evidence relevance, support/refutation, CAL eligibility or verdicts, Decision policy, operational Authorization, or execution permission.

## Version identity and frozen wire authority

The public compatibility version of this release is **Contract A `2.0.0`**.

The machine wire authority is deliberately the byte-identical frozen RC2 authority that passed minimality, fresh independent recovery, cross-repository conformance, and the bounded Contract E parent/atom pressure gate. Promotion does not rename the integrity-bound wire token merely to make the release name prettier.

Normative machine artifacts:

- wire specification: `schema/contract-a/2.0.0/wire-spec.md`;
- JSON Schema: `schema/contract-a/2.0.0/schema.json`;
- exact validation engine: `validators/contract_a_rc2.py`;
- production entry point: `validators/contract_a.py`;
- canonical fixtures: `fixtures/contract-a/2.0.0/`;
- version routing: `schema/contract-a/versions.json`.

The frozen wire token remains exactly:

`contract-a-wire-candidate-rc2`

That token is a bound field in every Contract A 2.0.0 object and therefore participates in `handoff_sha256`. Changing it would create different object identities and would require a new compatibility/equivalence claim. `2.0.0` is the public compatibility/release version assigned to this already-tested wire authority; it is not injected into the integrity-bound object as a cosmetic rewrite.

The copied wire specification, JSON Schema, validation engine, and seven public fixtures are byte-identical to the frozen RC2 candidate artifacts. Historical candidate-status language inside the byte-identical `wire-spec.md` describes the artifact at its research freeze. This canonical wrapper supersedes only that historical **status/release-posture language**. It does not alter any normative object shape, field ownership, validation, hashing, decomposition, source, consumer, compatibility, or non-authority rule in the frozen wire specification.

## Normative authority surface

A valid Contract A 2.0.0 wire object carries only:

- `schema`: exactly `contract-a-wire-candidate-rc2`;
- stable `handoff_id`;
- producer identity and immutable/versioned producer identity;
- upstream `work_id`;
- exact authoritative root proposition ID, text, and SHA-256;
- explicit decomposition state: `not_decomposed`, `failed`, `unknown`, or `declared`;
- for `declared`, one stable decomposition ID, operator exactly `all_of`, and at least two exact child proposition IDs/texts/hashes in contiguous sequence order;
- an explicit `sources` array, including an intentionally empty array when no representation was supplied;
- for each supplied source, exact source ID, supported UTF-8 media type, exact content bytes represented as a JSON string, and content SHA-256;
- `handoff_sha256`, computed over the complete object except the top-level hash field using the frozen canonical JSON procedure.

Unknown Contract-A-owned fields fail closed. Required identity or decomposition state may not be invented from absence.

The byte-identical `wire-spec.md`, schema, and validation engine are authoritative for all detailed constraints.

## Producer and consumer semantics

A producer emits one Contract A object per authoritative root audit proposition.

Evidence Bundler may mechanically consume the object without becoming semantic author:

- `not_decomposed`, `failed`, or `unknown`: retrieve for the exact root proposition and retain the supplied decomposition state;
- `declared`: retrieve independently for the exact declared children in sequence order while retaining root/decomposition lineage;
- begin evidence construction only from the source representations supplied in this handoff;
- do not convert producer-private metadata into relevance, support, trust, completeness, applicability, verdict, or authority state.

Representation adapters may change serialization envelopes where a downstream interface requires it. They may not mint or rewrite propositions, operators, source representations, semantic labels, or missing state.

## Whole-object integrity

`handoff_sha256` is the frozen RC2 whole-object binding. It covers producer, work, root proposition, decomposition, source representation identity/bytes, and the wire schema token. Substitution with a stale binding fails validation. A legitimate changed object must be resealed and is a different Contract A object.

The exact canonicalization algorithm is defined in `schema/contract-a/2.0.0/wire-spec.md` and implemented by the byte-identical engine `validators/contract_a_rc2.py`.

## Explicit non-authority

The following remain outside Contract A 2.0.0 authority:

- upstream support/unsupported labels, confidence, claim strength, or extraction fidelity;
- upstream-selected passages or spans;
- counterevidence flags, downgrade state/reason, or trust labels;
- retrieval/query/rank/score history;
- bibliographic/acquisition history not represented by the exact supplied source representation fields;
- model, prompt, template, workflow-condition, timestamp, run-history, or supersession metadata beyond required producer identity/version;
- CAL semantic judgments or policy;
- Decision Engine policy/effects;
- Contract E grants, policies, delegations, jurisdiction, authorization, or execution state.

Their presence as unknown Contract A fields is rejected. Their existence elsewhere in producer or downstream records does not grant them Contract A authority.

## Contract E boundary

The tested bounded Contract E pressure result established only that this exact frozen Contract A authority could survive the pinned pipeline under the preregistered parent/atom matrix without the tested forms of proposition minting, identity substitution, stale-binding acceptance, or semantic-authority laundering.

Contract A declaration/producer identity is not an authority-conferring grant, policy, delegation, or Authorization basis.

Known Contract E qualification subject/scope matching and surplus/multiple complete authority-conferring-record aggregation remain outside Contract A 2.0.0 and remain unresolved/partially closed in their own research records.

## Compatibility with legacy Contract A 1.0.0

This is a **major compatibility boundary**.

Legacy `handoff-contract-v1.0.0.md` remains immutable historical authority. It is not silently reinterpreted as 2.0.0.

A legacy object may be mechanically projected into the 2.0.0 wire authority only when producer/work/root/source requirements can be preserved. Because legacy A does not establish the new decomposition lineage, a projection lacking first-class lineage must use `decomposition.state = "unknown"`, not invent `not_decomposed`.

The reverse direction is not generally faithful: Contract A 2.0.0 does not carry the semantic-looking legacy fields expected by strict old consumers, and declared `all_of` lineage has no faithful legacy representation. A separate compatibility carrier may be used where a legacy consumer still requires it, but that carrier is not Contract A 2.0.0 authority.

## Evidence lineage

Promotion authority is bounded by:

- RC2 minimality research PR #57, terminal `SUPPORTED FOR PROMOTION`;
- frozen RC2 research head `2e50567c4da2a4046a15bddfc3feee31296da3fb`;
- frozen wire spec blob `2e7c37fca9aa6bdd1090fb527a663bdbe606ebcb`;
- frozen schema blob `ff5cddfeacf4511136a3dd3b47db1a794b631cd9`;
- frozen validator blob `42e5f5b3bf38d677445e9d01ea130ba604e53409`;
- fresh independent reproduction terminal `camerontjs-dot/research-scaffold-harness@dada22df71e1f3d26d7646a1cd7429cdab519318`, disposition `INDEPENDENTLY_RECOVERED`;
- EDR-004 / issue #60;
- A→E pressure PR #61, terminal `SUPPORTED FOR PROMOTION`;
- decisive R4 run `33557518640`, job `100021859078`, artifact `9819938146`, artifact digest `sha256:d2c2dfa97269a59d60455c8dd7d2266d2e0d3299771920965eb11d60a262dad0`.

Preserved predecessor apparatus failures remain evidence and are not erased by this promotion.

## Nonclaims

Contract A 2.0.0 does not establish source authenticity, retrieval completeness, decomposition semantic correctness, proposition truth/support/refutation, CAL semantic accuracy, Decision policy correctness, universal Contract E semantics, operational Authorization, execution permission, or execution occurrence.

Promotion of Contract A does not promote Contract E or any neighboring apparatus implementation.