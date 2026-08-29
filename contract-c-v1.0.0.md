# Apparatus Contract C 1.0.0

**Status:** production promotion candidate, not yet released  
**Canonical owner:** `camerontjs-dot/apparatus-contracts`  
**Decision authority:** EDR-002 / issue #17

## Purpose

Contract C is the immutable, decision-agnostic representation of CAL-attributable epistemic/result state required by legitimate downstream consumers, exactly bound to the Contract-B input and exact CAL/policy identity that produced it.

Contract C does not authorize an action, choose destination policy, restate the Contract-B evidence world, or expose producer-private reasoning/telemetry.

## Version discovery

Consumers must discover the version from the explicit top-level `contract_c_version` field. The canonical/supported version registry is `schema/contract-c/versions.json`.

The first canonical value is exactly `1.0.0`. An exact `1.0.0` object rejects unknown contract fields. Consumers must not infer Contract-C version from filenames, repository tags, CAL package versions, or Contract-B versions.

## Canonical object

The normative schema is `schema/contract-c/1.0.0/schema.json`. The reference validator is `validators/contract_c.py`.

Top-level families are:

- `contract_c_version`: exact Contract-C version;
- `input.contract_b`: exact Contract-B version, bundle ID, and bundle hash;
- `producer`: exact CAL semantic implementation commit plus behaviorally relevant policy hash/payload;
- `execution`: result-set execution state, independent of proposition verdicts;
- `propositions`: proposition-bound CAL result records;
- `result_set_id`: content-derived identity over the canonical object excluding this field itself.

No Contract-B source/evidence payload is duplicated into Contract C.

## Exact Contract-B binding

`input.contract_b` contains only:

- `contract_version`;
- `bundle_id`;
- `bundle_hash`.

The binding identifies the exact evidence-world input. Transport/package digests such as a research ZIP hash, artifact-tree digest, or embedded `SHA256SUMS` digest are not Contract-C semantic fields.

A conformance consumer that has the Contract-B artifact must independently verify proposition and evidence references against that bound artifact. The frozen conformance index in this repository is a test projection only, not a replacement for Contract B.

## CAL producer and policy identity

`producer.semantic_implementation_sha` is the exact CAL semantic implementation commit identity.

`producer.policy` contains:

- `sha256`: SHA-256 of the deterministic canonical bytes of `canonical`;
- `canonical`: the exact behaviorally relevant CAL policy payload.

A human-readable policy/config name is not sufficient identity.

The full canonical policy payload remains in Contract C 1.0.0 because this promotion precedes the separately promoted CAL exporter/release artifact. It may only be omitted in a later compatible/incompatible contract decision if the required hash is durably resolvable from an immutable promoted CAL artifact without weakening reproduction.

## Proposition binding

Each proposition record binds:

- `proposition.proposition_id` to the Contract-B proposition/claim ID;
- `proposition.text_sha256` to the SHA-256 of its exact UTF-8 proposition text.

Full proposition text is not duplicated into Contract C.

## Retained evidence contribution state

`contributions` retains stable contribution identity, channel, and exact Contract-B evidence reference:

- `contribution_id`;
- `channel`: `support` or `counterevidence`;
- `evidence_ref.source_id`;
- `evidence_ref.passage_id`;
- `evidence_ref.passage_sha256`.

All retained contributions must be classified by the conclusion as either part of the terminal causal basis or residual/non-deciding state. A contribution cannot be both.

Raw source payloads and per-candidate scalar telemetry are not carried.

## Measurement receipt

`measurement`, when present, carries:

- `kind`: CAL-owned measurement identity;
- `value`: the exact finite aggregate value, or explicit `null` where that typed measurement has no value;
- `basis_contribution_ids`: exact retained contribution references forming the measurement/co-maximal basis.

The measurement is recorded CAL-attributable state. Contract C does not assign downstream threshold, utility, routing, or action semantics to it.

A proposition may have `measurement: null` when no aggregate measurement was produced, including a supported early-return shape.

## Assessment-stage execution state

Contract C 1.0.0 has exactly four demonstrated generic stage slots:

- `eligibility`;
- `semantic_validity`;
- `aperture_completeness`;
- `temporal_applicability`.

Citation is intentionally not a Contract-C 1.0.0 generic stage obligation.

Each required slot uses one of these explicit states:

| State | Meaning |
| --- | --- |
| `{"state":"not_performed"}` | the named stage did not execute |
| `{"state":"performed","value":"unknown"}` | the stage executed and retained an explicit unknown/unresolved result |
| `{"state":"performed","value":"adverse"}` | the stage executed and retained an explicit adverse/negative result |
| `{"state":"not_applicable"}` | the named stage is explicitly not applicable where defined |
| `{"state":"failed"}` | execution of the named stage failed |

A missing slot is invalid. A malformed state is invalid. `not_performed`, performed-unknown, performed-adverse, not-applicable, and failed are never inferred from one another.

The current frozen CAL v0.2 producer fixture truthfully records all four stages as `not_performed`.

## Proposition and result-set execution

Execution state is separate from subject-matter verdict.

Result-set execution has one of:

- `completed`;
- `failed`;
- `incomplete`.

Proposition execution has one of:

- `completed` with `completion: assessed`;
- `completed` with `completion: not_checkable`;
- `failed`;
- `incomplete`.

A failed/incomplete proposition cannot carry a subject-matter conclusion. A completed `not_checkable` proposition carries `reported_verdict: not_checkable` and remains distinct from execution failure.

## Conclusion, terminal basis, and causal multiplicity

A completed proposition conclusion preserves:

- `reported_verdict`: CAL-attributable conclusion label only;
- `terminal_branch`: stable CAL terminal branch identity;
- `causal_form`;
- `basis_members`;
- `residual_contribution_ids`;
- `rule_roles`.

`causal_form` is exactly one of:

- `single_necessary`;
- `independent_sufficient_alternatives`;
- `jointly_sufficient`;
- `redundant_non_deciding`.

`basis_members` is the compact cross-family basis representation. Each member is an opaque but typed CAL-attributable reference in one of three namespaces:

- `contribution` -> a retained `contribution:<sha256>`;
- `rule` -> a declared `rule-role:...` identifier;
- `state` -> a stable `state:...` CAL basis identifier.

This permits the demonstrated single-contributor, tied/co-maximal independent, jointly required/co-sufficient state, and rule-mediated forms without selecting an artificial unique winner. State basis IDs are not producer-private traces or explanatory prose; they are stable typed basis identities supported by the attribution evidence.

Contribution roles and rule roles remain separate namespaces. `rule_roles` records each retained rule identity/code as `causal` or `residual`; a residual rule cannot appear in the causal basis.

Tied/co-maximal evidence is preserved by retaining every tied contribution in `measurement.basis_contribution_ids` and, where it is independently sufficient for the terminal result, every such contributor in `conclusion.basis_members`.

## Deterministic canonicalization

Normative JSON bytes use the tested RC2 rule:

1. UTF-8 JSON;
2. object keys sorted lexicographically;
3. compact separators with no presentation whitespace;
4. Unicode preserved rather than ASCII-escaped;
5. non-finite numbers rejected;
6. exactly one trailing newline.

Duplicate JSON object keys are invalid.

Array order is part of canonical byte identity. The schema does not silently sort arrays. A consumer may demonstrate order-invariant semantic interpretation where appropriate, but reordering an array changes canonical bytes, `result_set_id`, and the whole-object hash.

## Content identity

`result_set_id` is:

`result-set:` + lowercase SHA-256 of the deterministic canonical payload after removing only the top-level `result_set_id` field.

The reference validator recomputes and verifies it.

## Normative whole-object immutable hash

Whole-object binding is separate from internal structural/reference validation.

At a handoff boundary, the exact canonical object bytes must be accompanied by an expected external SHA-256 from the immutable manifest/release/transport binding. The validator must compare the exact received bytes to that expected digest and fail closed on mismatch.

The whole-object SHA-256 is intentionally not stored inside the object it hashes.

A structurally coherent deletion can remain locally self-consistent after its internal references and `result_set_id` are recomputed. That mutation is still a different immutable object and must be rejected when validated against the authorized external whole-object digest.

## Validation layers

The reference validator exposes separate checks for:

1. exact whole-object SHA-256 binding;
2. UTF-8/canonical JSON form;
3. exact v1 schema and controlled vocabulary;
4. content-derived `result_set_id`;
5. CAL policy payload/hash binding;
6. internal contribution/measurement/basis/rule reference integrity;
7. Contract-B binding/proposition/evidence reference integrity when the bound Contract-B index/artifact is supplied.

Passing structural validation alone is not evidence that a field was semantically necessary. Field necessity comes from EDR-002 and its linked frozen evidence.

## Exact-version unknown fields

Unknown fields are rejected for an object declaring `contract_c_version: 1.0.0` at every Contract-C-owned object level.

The sole intentionally opaque subobject is `producer.policy.canonical`, whose complete JSON content is hashed as producer-owned policy state. Its contents are not interpreted as Contract-C fields.

## Downstream-policy firewall

Contract C 1.0.0 contains no destination-specific:

- materiality threshold;
- utility/preference;
- risk tolerance;
- routing;
- authority/delegation;
- action vocabulary;
- application state;
- expected-utility or future-outcome state.

Changing downstream policy must not mutate Contract-C bytes or CAL state.

## Deliberately omitted from 1.0.0

The canonical core omits:

- research candidate/profile labels;
- producer-private traces, helper state, and raw per-candidate telemetry;
- generic citation assessment;
- mandatory reassessment/supersession bookkeeping for the current producer path;
- presentation prose/explanations;
- duplicated Contract-B source/evidence payloads;
- duplicate research artifact/ZIP/`SHA256SUMS` digests;
- destination decision policy or Decision Engine runtime state.

## Frozen conformance evidence

`fixtures/contract-c/1.0.0/` contains the frozen canonical v1 fixture, its exact whole-object SHA-256, an exact Contract-B test index, and the conformance/compression manifest.

The canonical fixture is a lossless production compression of the exact RC2 producer candidate at SHA-256 `e142f4aab119751dc201bca7994c0f97636c65647489f7edbee823a7f8aee3b4` for every EDR-002-supported invariant represented by that candidate. The source candidate is 5,868 canonical bytes; the v1 fixture is 4,968 canonical bytes, a 900-byte / 15.34% diagnostic reduction. Byte reduction is not the semantic proof; the frozen invariant controls and compression map are.

Additional conformance tests exercise the RC2-D multiplicity forms that do not all occur in the real three-proposition producer fixture.

## Compatibility and release posture

Contract C 1.0.0 is the first canonical Contract-C compatibility surface. There is no prior production Contract-C version to migrate.

This promotion candidate does not create an immutable release/tag. Publication of Contract C 1.0.0 remains gated on the separately promoted CAL exporter/producer conformance, clean consumer conformance against the exact candidate, compatibility assertions, and post-merge lock evidence required by EDR-002.

An incompatible required shape or semantic reinterpretation requires a later MAJOR-version decision. An additive capability is MINOR only after legitimate v1 consumer compatibility is demonstrated.

## Non-claims

Contract C 1.0.0 does not establish:

- universal Contract-C interoperability;
- correctness of CAL semantic judgments;
- generic assessment behavior CAL did not execute;
- corpus completeness or source legitimacy;
- Decision Engine policy correctness or runtime generality;
- operational authorization;
- Contract-B changes;
- arbitrary future CAL producer compatibility.

## Evidence lineage

Primary immutable/review identities for this promotion candidate:

- EDR-002 / Apparatus issue #17;
- Apparatus producer-sufficiency PR #13, head `e844852d20b1dae204943ea8fa8f3373cef81b1a`;
- frozen RC2 producer candidate SHA-256 `e142f4aab119751dc201bca7994c0f97636c65647489f7edbee823a7f8aee3b4`;
- Apparatus clean-room handoff PR #16, exact handoff commit `213ed9e912b922bd5c57ef58009eb6b0d7fff398`;
- CAL RC2-D decisive receipt SHA-256 `a953a14b8bf9a5bd9cf9060e7fb58c868df9b15c8b578d88f13a1090c4eca5fa`;
- CAL production semantic identity `33a928db97316a3652d57df9cafb8ca240305233`;
- CAL policy SHA-256 `88f007c96f3acf63a191556fe7fa46b80b37e9fcb5224ec1e90fb626a061104d`;
- Decision Engine clean-room Consumer B PR #8 terminal record `ec66ebd5e05b85f4541fe3ea5ea57f4f66d7c8a2`.
