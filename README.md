# Apparatus Contracts

This repository is the canonical home for shared contracts and contract-level research across the evidence-to-decision pipeline.

The maintained architecture is intentionally asymmetric. A contract exists only where producer/consumer evidence supports one; research candidates do not become canonical because they are convenient to draw as a pipeline.

## Current contract surfaces

### Contract A — upstream work object → Evidence Bundler

The legacy v1.0 handoff remains the maintained upstream contract authority while modernization research continues. Current research is testing the smallest upstream representation Evidence Bundler actually needs, including proposition identity and decomposition lineage, without treating upstream semantic assertions as downstream truth.

Canonical legacy specification: [`handoff-contract-v1.0.0.md`](handoff-contract-v1.0.0.md)

### Contract B — Evidence Bundler → Claim Audit Lab

Contract B 1.2.0 is the canonical production handoff. Its additive factual-context/history extension carries provenance-bound evidence-world facts, explicit history and aperture observations, and preserved nomination/admission state without converting those fields into proposition-specific semantic judgments.

Specification: [`contract-b-factual-context-extension-v1.2.0.md`](contract-b-factual-context-extension-v1.2.0.md)

The production/version decision and exact cross-repository evidence are recorded in EDR-001, GitHub issue #14.

### Contract C — Claim Audit Lab → downstream decision consumer

Contract C 1.0.0 is the first canonical CAL result contract. It is decision-agnostic: it exports CAL-attributable epistemic state, exact Contract-B binding, producer/policy identity, retained contribution state, explicit unknown/failure state, and deterministic object identity without granting operational authorization.

Specification: [`contract-c-v1.0.0.md`](contract-c-v1.0.0.md)

The immutable public release is tagged `contract-c-v1.0.0`. Its release record contains the exact promotion, producer, clean-consumer, and release-lock lineage.

### Contract D — Decision output

Contract D 1.0.0 is the first canonical production Decision contract. It binds exact upstream authority, Decision policy, target/content identity, evaluation state, and a typed requested effect while stopping at outcomes such as `candidate_for_authorization`, `hold`, `evaluation_failed`, `not_applicable`, or `cannot_establish`.

Specification: [`contract-d-v1.0.0.md`](contract-d-v1.0.0.md)

The immutable public release is tagged `contract-d-v1.0.0`. Its post-merge release lock reruns the exact Decision Engine producer, frozen independent consumer, frozen adversarial apparatus, and full conformance before publication.

A Decision is not automatic permission to execute an effect.

### Contract E / authority control plane

Contract E is research-only, and the current question is deliberately broader than "what should the next serialized contract look like?" Research is testing standing authority state, typed jurisdiction, authority-basis binding, delegation/currentness, participant declarations, transient authorization receipts, and local enforcement as potentially cross-cutting machinery.

No canonical Contract E schema or production authority control plane is established here.

## Boundary rules

**Repository-wide architectural invariant:** every apparatus is built, tested, and reasoned about from its governing contract, not from the incidental output shape of the current neighboring apparatus. Producer implementation, contract authority, and consumer implementation remain separate. The full rule and its apparatus-by-apparatus application are normative repository governance in [`APPARATUS-CONTRACT-SEPARATION.md`](APPARATUS-CONTRACT-SEPARATION.md).

A current output object is a concrete contract instance, not the definition of the contract. Unused contract states do not disappear because today's producer does not populate them, and producer-private behavior does not become downstream authority merely because today's consumer can observe it.

The contracts preserve several pipeline invariants:

- evidence-world facts do not silently become semantic conclusions;
- CAL epistemic conclusions do not silently become Decision Engine policy;
- a valid Decision does not automatically become execution permission;
- missing or unestablished state remains explicit rather than being filled with a convenient default;
- exact upstream identity is preserved where substitution could change authority;
- research candidates, validators, and harnesses remain distinguishable from canonical contract authority;
- producer conformance, contract sufficiency, and consumer conformance/recoverability are tested as distinct claims.

## Repository structure

The repository contains five different kinds of material. They should not be conflated:

- **Canonical authority:** maintained specifications, schemas, validators, fixtures, and release records.
- **Candidate authority:** explicitly non-canonical contract candidates awaiting evidence.
- **Research:** preregistrations, attacks, reproductions, results, and preserved failures.
- **Research infrastructure:** evaluators, validators, harnesses, hidden fixtures, and workflows used to test claims.
- **Historical authority:** superseded or legacy contract objects retained for reconstruction and compatibility.

Important top-level surfaces include:

```text
APPARATUS-CONTRACT-SEPARATION.md             repository-wide boundary governance
handoff-contract-v1.0.0.md                  legacy Contract A / original A+B authority
contract-b-factual-context-extension-v1.2.0.md
contract-c-v1.0.0.md
contract-d-v1.0.0.md
schema/                                      canonical machine-readable contract material
validators/                                  contract validators
fixtures/                                    canonical/public fixtures where applicable
docs/research/                               research records and frozen candidates
DECISIONS.md                                 durable contract decision history
CHANGELOG.md                                 maintained contract history
```

## How to use this repository

Start from the contract that owns the boundary you are changing, then follow its exact schema/validator/fixture and decision lineage. Do not start from a current producer output and infer that its populated subset defines the contract. See [`APPARATUS-CONTRACT-SEPARATION.md`](APPARATUS-CONTRACT-SEPARATION.md).

For cross-repository work, pin the producer, contract authority, and consumer identities. A passing test in only one repository is not evidence that the shared boundary works.

Research branches may contain newer-looking schemas or richer objects. They are not canonical unless a separate promotion decision establishes that status.

## Verification

The repository's verifier and acceptance workflows protect structural, vocabulary, identity, integrity, and cross-repository conformance properties appropriate to each maintained contract.

These checks are intentionally narrower than semantic truth. Structural validation does not establish source legitimacy, retrieval completeness, CAL semantic correctness, Decision policy correctness, or execution authorization.

When a contract claim depends on independent recoverability, the independent implementation is executed in a separate fresh context and frozen before reference reveal. Failed or disagreeing reproductions remain part of the research record.

## Change control

Shared contract changes require evidence at the real producer/consumer boundary. Version changes follow compatibility consequences rather than milestone aesthetics.

For a canonical change:

1. identify the exact producer/consumer need;
2. establish the smallest authority that must cross the boundary;
3. test missing/hostile/unknown state and compatibility where relevant;
4. preserve failed candidates and deviations;
5. make a separate promotion decision;
6. update canonical specification/schema/validator/fixtures coherently;
7. publish a release only when an immutable named checkpoint is justified.

Changing an apparatus does not itself change its contract. Changing a contract requires a separate evidence and promotion decision.

A research result does not become production behavior merely because its branch is green.

## Known limits

The legacy Contract A surface predates the current proposition/decomposition ownership research and is being revalidated rather than silently reinterpreted.

Contract B 1.2.0 is production-locked, but its contract-specific release identity is tracked separately from that behavioral lock.

Contract C 1.0.0 is canonical and released, but that does not establish correctness of CAL's semantic judgments.

Contract D 1.0.0 is canonical and released, but it deliberately stops before operational Authorization or execution and does not establish correctness of upstream epistemic judgments or Decision policy outside the tested domain.

Contract E remains a research program. Its frozen candidates, attack harnesses, clean-room reproductions, interpretation audits, and failures are evidence, not production authority.
