# Contract D → Contract E Authorization Consumer Pressure Test

Status: **preregistered before harness implementation or execution**

## Scientific question

Can the smallest supported downstream chain

`exact Contract D applicability → exact AuthorizationRequest construction → frozen Contract E RC1 evaluation → human or machine point-of-use consumption`

preserve the distinction between Decision, Authorization, and execution under adversarial substitution, replay, laundering, stale-authority, and consumer-confusion attacks?

This experiment does not test whether Contract E RC1 is production-ready. It uses the exact frozen research candidate as the authority-evaluation subject while its separate fresh independent recoverability gate remains independently governed.

## Exact pinned authorities

- Apparatus Contracts experiment base: `c3563cff66d2c85dcbf575c693056e2d8e4563d4`.
- Contract D 1.0.0 release commit: `298a1a0f7b7b6d7712e11200d04faec3e1ca169b`.
- Contract D core validator blob: `564dcde5677df5ac8f86f21dc0ffd1692f44c9f0`.
- Contract D consumer blob: `8b4ad5c9d6fc1145cf334d1416b5d52b9ed93c68`.
- Contract D effect registry blob: `a40f4f4447470654bdc16d852f5927189ae30cc5`.
- Contract D public fixture blob: `66f59bc50e5062aa8550491defa2fee37e75fcc7`.
- Frozen Contract E RC1 candidate commit: `8876b7bcc2afa1a4902400b0cc507cf2ef02e6e7`.
- Contract E RC1 SPEC blob: `3041d31ed0905d50ff355e483fbb9422df994997`.
- Contract E RC1 schema blob: `d934d055e39c81e6eb93830e7c6f6f43fc8a0870`.
- Contract E RC1 reference implementation blob: `378cdb7835df3959c82a0fe98068b1434b1b68ec`.
- Decision Engine live main observed before preregistration: `a4425f8eb47449ff6c683222921bbea9483742e2`.

The executable experiment starts at released Contract D rather than rebuilding CAL → Decision Engine. The maintained Decision Engine → Contract D path is already separately gated; this test owns the new downstream seam and must keep failure attribution local.

## Candidate integration profile under test

### Shared D → E adapter rule

An AuthorizationRequest may be constructed only when the exact released Contract D consumer returns `candidate_for_authorization` for an exact applicability expectation containing:

- exact input authority;
- exact Decision policy;
- exact Decision target;
- exact requested operation;
- requested effect-parameter constraints where supplied.

The exact Contract D Decision is preserved as a **non-conferring supporting artifact**. It never replaces AuthorityState.

HOLD, evaluation failure, malformed Decision, invalid expectation, or non-applicable Decision must not cross the adapter as an authorization candidate.

### Human profile

The request names one exact human `subject_id`. The E target is the exact immutable action target derived from the Decision target. A receipt for another subject, operation, target, state, or time is not reusable.

### Machine profile

The machine request names one exact machine `subject_id`. The E target is an immutable `ExecutionIntent`, not a generic script permission.

The test-only ExecutionIntent contains exactly:

- exact Contract D semantic identity;
- requested operation;
- requested effect-parameter constraints;
- exact Decision target binding;
- exact executor subject;
- executable/script digest;
- entry point;
- arguments;
- exact input identities;
- explicit environment constraints.

Its identity is deterministic canonical JSON SHA-256. Any authority-relevant mutation creates a different target identity.

The machine point-of-use gate must re-evaluate the current AuthorityState against the exact request at execution time. A previously authorized receipt is historical evidence, not a reusable execution permit.

## Required positive controls

1. Exact Contract D CLEAR citation fixture + exact D applicability → `candidate_for_authorization`.
2. Matching direct human AuthorityState/request → authorized receipt.
3. Matching machine AuthorityState + exact ExecutionIntent request → authorized receipt.
4. Valid linear delegation that changes only subject → authorization for the delegated subject.
5. Evaluation exactly at `valid_from` → current.
6. Evaluation exactly at `valid_until` → current.
7. Irrelevant conflict/residue preserved but non-blocking.
8. Contract D metadata-only mutation that preserves D semantic identity must not change downstream semantic binding.
9. Canonically equivalent ExecutionIntent key ordering must preserve intent identity.

## Required negative / adversarial controls

### Contract D applicability boundary

- HOLD must remain `hold`.
- failed evaluation must remain `evaluation_failed`.
- requested-operation substitution.
- requested-effect-parameter substitution.
- target kind/id/content substitution.
- policy id/version substitution.
- upstream kind/id/immutable-id substitution.
- malformed applicability expectation.
- malformed/tampered Contract D object.

### Adapter laundering controls

- no E request from HOLD.
- no E request from failed evaluation.
- no E request from `not_applicable`.
- no E request from `cannot_establish`.
- removing the exact D supporting artifact must make the integration profile invalid.
- substituting a different D Decision supporting artifact must make the profile invalid.
- Contract D `candidate_for_authorization` alone must not confer E authority.
- a previous AuthorizationReceipt used as a supporting artifact must not confer E authority.

### Contract E authority-chain attacks

- human ↔ machine subject swap.
- wildcard / `any operator` subject attempt.
- domain substitution.
- operation substitution.
- scope substitution.
- target-class substitution.
- target-ref substitution.
- AuthorityState identity tamper.
- request AuthorityState-id mismatch.
- not-yet-valid authority.
- expired authority.
- revocation before evaluation.
- evaluation exactly at revocation time.
- broken delegation parent.
- wrong `delegated_by`.
- delegation changes domain/operation/scope/target bounds.
- duplicate authority record IDs.
- non-delegation descendant.
- duplicate request reference IDs.
- bad immutable-reference identity.
- missing target reference.
- duplicate supporting-artifact IDs.
- supporting artifact references unknown ref.
- duplicate conflict/residue IDs.
- relevant unresolved conflict.
- relevant contested conflict.
- relevant unresolved residue.
- relevant contested residue.
- forbidden request-side `resolved_*` discharge field.
- unknown request field.

### Receipt/replay/TOCTOU attacks

- mutate request after receipt and replay old receipt.
- replay human receipt for machine request.
- replay machine receipt for human request.
- replay receipt after target change.
- replay receipt after operation change.
- replay receipt after AuthorityState change.
- use previously authorized machine receipt after authority becomes revoked.

The last case must demonstrate why point-of-use re-evaluation is required: the old receipt remains valid historical evidence for the old evaluation, but the current machine gate must refuse execution.

### ExecutionIntent mutation attacks

Each of these must produce a different immutable intent identity and therefore fail under stale authority:

- script/executable digest;
- entry point;
- arguments;
- input identity;
- environment constraint;
- executor subject;
- requested operation;
- requested effect parameters;
- Decision semantic identity;
- Decision target binding.

## Metamorphic invariants

- diagnostic/reason ordering may not create authority.
- Contract D metadata that is excluded from D semantic identity may not create a new authorization target.
- representation key order alone may not change ExecutionIntent identity.
- irrelevant blockers may not change authorization outcome but must remain preserved in the receipt.
- changing an authority-critical field must change applicability, authorization, target identity, or point-of-use acceptance.

## Deliberately weak controls

The evaluator is not trusted merely because the target passes. At minimum the harness must run weak strategies expected to fail:

1. **CLEAR-is-authorization**: treats Contract D CLEAR/candidate as authorization without AuthorityState.
2. **receipt-only machine gate**: trusts any prior `authorized=true` receipt without current-state re-evaluation.
3. **subject-blind consumer**: ignores receipt/request subject binding.
4. **target-blind consumer**: ignores target identity.
5. **supporting-artifact-laundering**: treats the D Decision reference as an authority-conferring basis.

A meaningful evaluator must expose false permits from these strategies on the corresponding attack cases.

## Falsification criteria

The candidate integration profile is **FALSIFIED** if any authority-relevant attack produces a false permit, including:

- a non-CLEAR/non-applicable D Decision crossing into valid authorization;
- E authorization without a valid matching AuthorityState;
- cross-subject or cross-target receipt reuse;
- stale machine authorization surviving revocation at point of use;
- ExecutionIntent mutation surviving old target authority;
- relevant unresolved/contested blocker being ignored;
- supporting artifacts becoming authority-conferring;
- evaluator weak controls not being discriminated for the failure mode they are intended to expose.

A false reject of a preregistered positive control also falsifies the claimed profile as an interoperable usable path.

Use **INCONCLUSIVE** only for apparatus failure that prevents the scientific target from being exercised.

## Controlled boundaries / nonclaims

This experiment does not establish:

- Contract E 1.0.0 production promotion or independent recoverability;
- legitimacy of the configured root grant/policy in the real world;
- correctness of CAL or Decision Engine policy;
- source truth or evidence completeness;
- role/group/wildcard authorization semantics;
- reusable permit/lease semantics;
- distributed locking or exactly-once execution;
- execution occurrence or success;
- verification correctness;
- Qualification semantics;
- surplus peer authority-conferring aggregation;
- broader delegation narrowing/containment/`any-of` semantics.

If the exact frozen Contract E candidate cannot express one of the preregistered positive controls without inventing new semantics, classify that point explicitly rather than patching the candidate.

## Terminal dispositions

Only these primary research dispositions are allowed:

- `SUPPORTED FOR PROMOTION`
- `FALSIFIED`
- `INCONCLUSIVE`
- `SUPERSEDED`

A green workflow alone is not a research disposition.
