# Contract B V0/V1/V2 Conformance Experiment

**Date:** 2026-08-27  
**Status:** research result only  
**Disposition:** SUPPORTED  
**Version implication:** MINOR, provisional for the Contract-B input seam  
**Promotion status:** NOT PROPOSED by this experiment

This report records the preregistered Evidence Bundler -> Apparatus Contract B -> Claim Audit Lab conformance experiment. It is evidence for a later promotion decision, not a schema lock, merge, release, or final version assignment.

## Claim under review

> The V1 minimal factual-context Contract B handoff contains enough upstream evidence-world state for CAL to construct its pre-assessment measurement view without inventing defaults or accepting upstream proposition-specific semantic judgments.

## Pinned research states

| Repository | SHA used | Role |
|---|---|---|
| `camerontjs-dot/evidence-bundler` | `b4ca9111f5957ef7e7955e2c5024f2280ee19eb5` | fixture and V0/V1/V2 research helpers |
| `camerontjs-dot/claim-audit-lab` | `6acc3462dad73959ccec6bccf8407215f5274cf6` | relation-preserving consumer research and writeback controls |
| `camerontjs-dot/apparatus-contracts` | `63e8506396132a44ebc0e6c2312047e99b1125eb` | preregistered base / RC0 conformance plan |
| `camerontjs-dot/decision-engine` | `55f108c196ead020b5965c7d4d737464c92bc4a0` | downstream context only |

The expected research heads had not advanced. No silent substitution was made.

Research execution branches in Apparatus Contracts:

- run 1: `research/contract-b-v0-v1-v2-conformance`, execution head `5673bc45e1fe3718758b811139358562c29c5fba`
- run 2: `research/contract-b-v0-v1-v2-conformance-r2`, execution head `e92d8725cefc8043f76a877ed4f9211e38b402bf`
- run 3 environment correction: `research/contract-b-v0-v1-v2-conformance-r3`, execution head `6f30707fc07c2eea94979e4eebea81fabf40751b`

No canonical Contract B file, CAL production behavior, Decision Engine fixture, merge, release, or schema version was changed.

## Evidence world

Fixture: `evidence-bundler/examples/contract-b-seam/tri-repo-fixture.yaml`

Frozen fixture file SHA-256:

`sha256:4d5a900232cd243d82fffdc6a5422d32287e9496f3e9728ae684e1ef04fdc7cf`

Research projection hashes:

- V0: `sha256:39ab83f75568b577b5016ef9e9be8464c84d4b6cab915d4b9a7980ea81a73e3c`
- V1: `sha256:a861eeafe9a360e9280e2d2c092bd2bbcdee6661c55412802be6fecbf8c7b2d7`
- V2: `sha256:97f274911c55921552b1d1eacaf25a48c186467ecde3c146c6dbeae43821002a`

The claim and passage text were unchanged across V0/V1/V2.

## Preserved failed runs and deviations

### Run 1: harness/orchestration failure

Run 1 is preserved as a failed experimental run. It is not counted as seam evidence.

Observed harness failures:

1. The custom runner addressed the fixture claim as `text` rather than the actual `claim_text` key, causing T3/T4/T7/T11/T12 runner failures.
2. T9 addressed `aperture` rather than the actual `aperture_assessment` key.
3. The Apparatus pytest command recursed into checked-out dependency repositories rather than only the Apparatus verifier suite.
4. CAL research tests were invoked without the repository root on the test import path.

These are experiment-harness defects. They do not satisfy a Contract-B hard falsifier.

### Run 2: corrected harness, CAL environment omission

Run 2 corrected only the research harness and test scoping.

Observed suite results:

- Apparatus locked verifier: `12 passed, 8 skipped`
- Evidence Bundler Contract-B seam controls: `11 passed`
- CAL resealed-C-B writeback controls: `14 passed`
- corrected custom T1-T12 runner: all 12 passed, 0 failures
- CAL Rung-04/Rung-05: `12 passed, 2 failed`

The two CAL failures occurred before the H05_2/H05_3 assertions because `en_core_web_sm` was not installed. CAL's pinned `pyproject.toml` documents this as a separate post-install step for the v1 stack.

### Run 3: environment correction

Run 3 changed only the execution environment by adding the documented:

`python -m spacy download en_core_web_sm`

It reran the same CAL Rung-04/Rung-05 files at the same CAL SHA.

Result: `14 passed in 6.43s`.

### T7 control redesign

The preregistration suggested changing a mechanical version/effective-date fact. On this fixture, changing a version/date while freezing passage content could create an internally inconsistent evidence world. The control was therefore redesigned before interpretation to mutate only:

`coverage.search_scope.closed_world: true -> false`

This was exactly one fixture-field change. It changed CAL's context input while leaving the proposition/passage semantic payload unchanged.

### T12 feasibility limit

The pinned CAL resealed-C-B writer consumes canonical on-disk C-B, not the V1 research projection. Creating a synthetic V1-to-canonical-C-B converter solely for this experiment would have introduced an unpreregistered second handoff transformation.

Therefore T12 is a mechanism comparison, not a same-world byte-for-byte packaging comparison. This is retained as an unresolved packaging question rather than silently manufactured evidence.

## Observed evidence

### T1: input/hash/integrity validation

PASS.

- Frozen fixture hash recorded above.
- A single tamper to `coverage.admitted_count` was rejected with: `Coverage counts are (5, 5, 5), expected (5, 5, 4).`
- V0, V1, and V2 received distinct stable projection hashes.

### T2: V0 fail-closed behavior

PASS.

Calling the existing EB CAL measurement-view builder on V0 produced the typed failure:

`CAL measurement view requires a minimal-context handoff.`

No measurement view was constructed from absent state and no factual default was fabricated.

### T3: deterministic V1 pre-assessment ledger construction

PASS.

- Rebuilding V1 reproduced the same hash: `sha256:a861eeafe9a360e9280e2d2c092bd2bbcdee6661c55412802be6fecbf8c7b2d7`.
- All 9 preregistered required mechanical fact IDs were present.
- All 5 upstream link histories and supplied coverage/search facts remained represented.
- `find_audit_judgment_keys(V1)` returned an empty set.
- Claim and passage content exactly matched the frozen fixture.

### T4: V1/V2 pre-assessment semantic-measurement equivalence

PASS.

V1 and V2 produced the same pre-assessment measurement-view hash:

`sha256:b18715b861343a541fd8317d38cfa3b4f6acf2efdcb9578fac55313bf721f8db`

The proposition/passage-only semantic payload hash was also identical:

`sha256:bc5dad7d498a8da607e24edb6a3d927ebbcf6d6d2d318e250fd7b40478b272c1`

### T5: hostile V2-sidecar mutation/blinding

PASS.

Twenty-two V2 sidecar values were deliberately mutated, including proposition-specific relation, semantic validity, temporal applicability, authority applicability, decision participation, and completeness conclusion.

The blinded CAL measurement-view hash remained exactly:

`sha256:b18715b861343a541fd8317d38cfa3b4f6acf2efdcb9578fac55313bf721f8db`

The hostile sidecar therefore did not become authoritative merely by crossing the research handoff.

### T6: EB nomination role/rank/score invariance

PASS.

Mutating EB nomination metadata changed the auditable V1 handoff hash from:

`sha256:a861eeafe9a360e9280e2d2c092bd2bbcdee6661c55412802be6fecbf8c7b2d7`

to:

`sha256:4751b906ef719edb36d5bd857311d4b35554c016496326ec2229fc0869835f15`

but the CAL pre-assessment semantic measurement view remained:

`sha256:b18715b861343a541fd8317d38cfa3b4f6acf2efdcb9578fac55313bf721f8db`.

Nomination history remained auditable without controlling CAL semantic measurement.

### T7: single-variable mechanical-context sensitivity

PASS with preregistered-control redesign recorded above.

Exactly one field changed:

`$.coverage.search_scope.closed_world: true -> false`

The context-bearing measurement-view hash changed from:

`sha256:b18715b861343a541fd8317d38cfa3b4f6acf2efdcb9578fac55313bf721f8db`

to:

`sha256:3603cdac3d6728a7ffbd3f58001d22cd086de872624d6940994c889663b2e0a5`

while the proposition/passage semantic payload remained:

`sha256:bc5dad7d498a8da607e24edb6a3d927ebbcf6d6d2d318e250fd7b40478b272c1`.

### T8: trust-level versus CAL-policy separation

PASS.

On the tri-repo fixture, a single trust mutation:

`$.sources[1].source_trust_level: primary -> secondary`

left the EB research CAL semantic measurement view unchanged.

The pinned CAL Rung-05 controls then independently established the current consumer behavior:

- H05_2: primary vs secondary trust leaves retrieval, entailment, and support signal unchanged.
- H05_3: the final verdict may differ only at CAL's policy/rule layer, with the secondary-source case recording `P1_eligibility_suppressed`.
- H05_5: the explicit shadow `EvidenceDecisionInput` has no implicit `trust_level`, `source_reliability`, or `authority` field; eligibility is an explicit receipt-bound CAL assessment.

Run 3 executed these controls successfully after installing the documented spaCy model.

### T9: coverage facts versus CAL completeness judgment

PASS.

V1 carried supplied search/coverage facts:

- candidate count: 5
- reviewed count: 5
- admitted count: 4
- closed-world search-scope declaration: true
- source-selection basis: supplied fixture
- explicit limitation that fixture scope does not establish real-world retrieval completeness

V1 contained no proposition-specific completeness conclusion.

V2's downstream-only sidecar separately contained:

`completeness_conclusion: sufficient_for_fixture_only`

### T10: non-destructive evidence/context preservation

PASS.

All five upstream passages remained reconstructable in V1.

Four were admitted to the CAL-facing semantic view. `psg-validation-old` and `psg-incident` were explicitly non-deciding in V2, yet both remained preserved and admitted. The rejected `psg-marketing` candidate remained recoverable in upstream history.

All 9 required mechanical fact IDs remained reconstructable.

No later CAL decision-participation state physically rewrote the historical input record.

### T11: re-audit/result immutability

PASS for the separate immutable-B-bound research result shape.

Two result artifacts were constructed over the same immutable V1 hash and same semantic-measurement hash under different CAL policy/assessment states.

They received distinct result hashes while the first artifact remained byte-stable in the experiment.

This demonstrates the desired immutability property for a separate result artifact. It does not by itself choose that packaging as canonical.

### T12: resealed audited-C-B output versus separate immutable-B-bound CAL result

PASS as a mechanism comparison, with the same-world feasibility limit retained.

Current CAL resealed derivative behavior:

- copies the full source C-B bundle;
- writes downstream audit material into the derivative;
- adds full CAL trace material;
- reseals the derivative;
- is self-contained;
- produces a new C-B-shaped bundle identity/hash.

Separate immutable-B-bound research result behavior:

- binds the upstream V1 object by hash;
- does not duplicate claim/source/passage/link/coverage payloads;
- leaves CAL judgment ownership visibly downstream;
- is not self-contained without the bound B artifact.

The comparison favors the separate artifact on semantic-ownership clarity, duplication, and append-only audit history, while the resealed derivative favors current-format compatibility and self-containment. Same-world byte-for-byte comparison remains unresolved.

## Inference

1. **The claim under review is supported for the tested evidence world and pinned implementations.** V1 carried the factual evidence-world state needed to construct the pre-assessment CAL view while excluding proposition-specific CAL judgments.
2. **V0 is genuinely information-insufficient for this seam.** The current C-B-shaped research projection cannot construct the pre-assessment view and fails closed rather than inventing state.
3. **The V2 semantic sidecar is not necessary for pre-assessment semantic measurement.** Its existence and even hostile mutation do not alter the blinded view.
4. **EB nomination metadata is provenance/history, not CAL semantic evidence.** It can change auditable handoff bytes without changing CAL semantic measurement.
5. **Trust and proposition-specific eligibility are separable in the current CAL research machinery.** Trust can influence a named CAL policy decision without changing retrieval/entailment measurement.
6. **Coverage/search observations can cross Contract B without crossing a completeness verdict.** The completeness conclusion remains downstream-owned.
7. **Non-deciding evidence need not be destructively filtered.** Historical evidence/context can remain intact while downstream participation changes.
8. **A separate CAL result bound to immutable B appears cleaner than resealing B for semantic ownership and audit history, but this experiment does not establish that it must become canonical.**
9. **The current V1 projection is sufficient, but its field-level minimality is not proven.** Some history fields are intentionally preserved for auditability even though they are blinded from semantic measurement.

## Falsified hypotheses

The following alternatives were falsified for this fixture and the pinned implementations:

- **V0 already contains enough information for the CAL pre-assessment view.** Falsified by typed V0 failure.
- **CAL must accept proposition-specific judgments from upstream to construct its pre-assessment view.** Falsified by V1 construction with no CAL judgment keys and by V1/V2 equivalence.
- **The mere presence of V2 CAL judgments changes semantic measurement.** Falsified by 22 hostile sidecar mutations with an invariant blinded view.
- **EB nomination lane/rank/score must control CAL semantic measurement.** Falsified by nomination mutation with invariant CAL semantic view.
- **Changing trust level must change semantic measurement.** Falsified by the tri-repo trust control and pinned CAL H05_2 execution.
- **Trust and CAL eligibility/policy cannot be separated in practice.** Falsified for the tested CAL research path by H05_2/H05_3/H05_5.
- **Coverage facts necessarily encode a CAL completeness judgment.** Falsified by V1/V2 separation.
- **Evidence that becomes non-deciding must be discarded or rewritten.** Falsified by preservation controls.

None of the preregistered hard falsifiers for the V1 input boundary fired in this experiment.

## Remaining unknowns

1. **Field-level minimality.** The experiment proves sufficiency, not that every V1 field is necessary. A smaller field set may preserve the same semantic and audit properties.
2. **Canonical schema compatibility.** We have not yet encoded the V1 factual-context additions into a candidate canonical schema diff and proven they can remain optional without ambiguous legacy semantics.
3. **Independent consumer reproducibility.** The preregistration's stronger criterion that different CAL consumers reproduce the same pre-assessment ledger from identical V1 input has not yet been tested with a second independent consumer implementation.
4. **Open-world retrieval/completeness.** The fixture is synthetic and explicitly does not establish real-world retrieval completeness.
5. **Mechanical applicability beyond search scope.** T7 demonstrates isolated context sensitivity using a clean coverage fact. It does not yet demonstrate a version/effective-date applicability operator on a separately constructed internally consistent world.
6. **Exact T12 same-world packaging.** The current resealed-C-B writer and the V1 research projection do not share a direct existing input representation, so the byte-for-byte same-world comparison was not manufactured.
7. **Output packaging decision.** The evidence favors a separate immutable-B-bound result on ownership/immutability grounds, but current-format compatibility and self-containment remain real tradeoffs.
8. **CAL convenience defaults.** Current CAL request models contain API convenience defaults such as absent source-boundary state. This experiment distinguishes those from evidence-world factual defaults, but a future canonical adapter should make that distinction explicit in receipts/intake limitations.

## Disposition: SUPPORTED

**Scope of support:** the specific claim under review, on the frozen tri-repo evidence world and the pinned EB/CAL/Apparatus research implementations.

This is **not** evidence that Contract B is ready to lock. The Apparatus lock gate still requires, among other items, a candidate schema/vocabulary diff if needed, migration evidence, unresolved-issue closure, and cross-repo review.

## Version implication: MINOR

**Provisional implication only. No schema version is assigned here.**

Reasoning:

- V0 can remain valid but fail closed for consumers that need factual context it does not carry.
- V1 demonstrates that additional factual-context fields can supply the missing information without changing the meaning of existing semantic fields or forcing upstream CAL judgments.
- That pattern matches the preregistered MINOR case if the additions can be made optional and backward-compatible.

This implication would move to **MAJOR** or **UNRESOLVED** if the next experiment shows that the required facts cannot be represented as optional additions, require incompatible reinterpretation, or force a mandatory new packaging model.

## Exact next experiment

### Optional-extension / independent-consumer falsification test

Freeze the successful V1 object from this run at:

`sha256:a861eeafe9a360e9280e2d2c092bd2bbcdee6661c55412802be6fecbf8c7b2d7`

Then, on research branches only:

1. Express **only the factual-context capabilities demonstrated necessary by V1** as a candidate optional Contract-B extension. Do not add CAL semantic judgments and do not promote it.
2. Verify an unchanged canonical/V0 artifact with the candidate verifier and require legacy validity plus explicit CAL fail-closed behavior for unavailable factual state.
3. Verify the frozen V1 evidence world through the candidate extension.
4. Feed the same verified V1 bytes to **two independently implemented consumers**: the existing CAL research consumer path and a second minimal read-only consumer written from the candidate profile, not by importing the first consumer's projection function.
5. Normalize both outputs to the preregistered pre-assessment ledger fields and require identical ledger hashes.
6. Perform one field-ablation series over the optional additions. Remove exactly one factual-context capability at a time and record whether the ledger becomes incomplete, fails closed, or stays equivalent.
7. Treat any field whose removal leaves every required property unchanged as evidence that V1 is not field-minimal and simplify before promotion.
8. Treat any requirement for a new mandatory field or incompatible reinterpretation as falsification of the provisional MINOR implication.

**Primary discriminator:** whether the V1 capabilities can be represented as optional, backward-compatible factual context and independently reproduced without importing semantic judgments or defaults.

Do not proceed to Contract C until this Contract-B promotion question is epistemically compressed.
