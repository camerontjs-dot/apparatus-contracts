# Contract E × ERS point-of-use cross-repository RC2 result

Disposition: `SUPPORTED_FOR_BOUNDED_CROSS_REPOSITORY_POINT_OF_USE_RC2`

This is a bounded shadow-composition result. It is not production authorization
and does not justify merge, release, promotion, a production Contract D effect
registration, or real MainFrame mutation.

## Exact subjects

- Contract E subject:
  `a678c73a661853a3a704666fc6bbf29fa378948f`
- RC2 preregistration branch:
  `research/contract-e-ers-point-of-use-crossrepo-rc2-20260919`
- independent ERS point-of-use consumer:
  `73a47dc0ce2e3ae6c7aa6e55c4183e223797724b`
  - repository: `camerontjs-dot/epistemic-research-system`
  - Draft PR: `#2`
- falsified predecessor:
  - Apparatus Draft PR `#115`
  - head `ce253413f8f8a86ca7fab8a05b2620bbb4997e73`

RC2 is based directly on the Contract E subject and does not inherit the
falsified RC1 harness as code ancestry.

## Preserved Contract D boundary

Released Contract D 1.0.0 still rejects
`epistemic_audit.stage_pending_review@1` as `unknown_effect_type`.

RC2 uses only an in-process research-local effect extension for composition
testing. No released Contract D registry or normative schema is changed.

## Qualification result

The exact pinned ERS checkout was verified before import. A different ERS HEAD
is a qualification failure.

The exact cross-repository case passed:

- Contract D research-local composition reached
  `candidate_for_authorization`;
- ERS preserved the exact typed Contract D identity
  `decision:sha256:<digest>` without projection;
- Contract E accepted the ERS-generated execution intent unchanged;
- ERS and Contract E computed identical execution-intent identities;
- ERS and Contract E computed identical target-reference identities;
- Contract E returned `execution_permitted=true`;
- Contract E returned `execution_occurred=false`;
- ERS accepted the fresh point-of-use handoff;
- the exact shadow case did not mutate the target.

Reproducer disposition:

`CONTRACT_E_ERS_POINT_OF_USE_RC2: PASS`

## Preregistered falsifiers

All required RC1 successor discriminators rejected as expected:

- wrong principal: rejected;
- wrong target/reference: rejected;
- fresh revoked AuthorityState: rejected by Contract E;
- replay after revocation using the current revoked AuthorityState identity:
  rejected by ERS;
- replay at a newer point-of-use evaluation time: rejected by ERS;
- target pre-state changed after authorization: rejected by ERS;
- swapped/unrelated typed Contract D decision identity: rejected by ERS;
- generic knowledge-operation receipt: rejected by ERS;
- mismatched execution-intent receipt: rejected by ERS;
- already-executed result: rejected by ERS.

A non-exact ERS checkout was also supplied deliberately. The reproducer failed
before qualification with:

`AssertionError: non_exact_ers_consumer_commit`

## Controls

### Contract E successor

The frozen Contract E target-reference-cardinality successor remains green:

- predecessor asserted controls: 62;
- new target-cardinality controls: 3;
- total asserted controls: 65;
- result: pass.

### ERS successor

The exact ERS consumer's focused point-of-use profile remains green:

- 17/17 tests pass.

The ERS checkout remained clean after the RC2 run.

### Historical integration deviation

The broader historical integration profile still fails exactly as inherited:

`AssertionError: MATRIX-SIZE: count before sentinel=112`

against its current assertion of at least 120.

RC2 does not repair, reinterpret, or attribute this pre-existing failure to the
point-of-use successor.

### Repository boundary

The RC2 implementation is confined to:

`docs/research/contract-e/ers-point-of-use-crossrepo-rc2-20260919/`

It adds only the preregistration, a research-only Contract E profile adapter,
the deterministic reproducer, and this result record.

No released registry, schema, fixture, or implementation file is changed.

## What RC2 supports

Within the bounded shadow model, the observed safe handoff is:

`typed Contract D decision -> ERS immutable execution intent -> Contract E fresh authorization -> ERS point-of-use currentness checks + target re-observation -> shadow-ready`

The evidence supports the claim that the RC1 failures were composition gaps,
not a need for a second authorization engine inside ERS.

Specifically, the missing consumer obligations were:

1. preserve and compare the exact typed Contract D decision identity;
2. require point-of-use AuthorityState/evaluation context to match the fresh
   Contract E request;
3. re-observe target pre-state immediately before accepting the handoff.

## Remaining trust gap

RC2 still treats `current_authority_state_id` and
`current_evaluation_time` as trusted point-of-use inputs.

The experiment does not establish:

- authenticated provenance of AuthorityState;
- authenticated/current clock provenance;
- authenticated workload/principal identity;
- protection against a malicious same-user process supplying false context;
- OS/service mediation of the final write boundary.

Therefore the smallest next trust question is not another semantic
authorization rule. It is how the production consumer obtains trustworthy
point-of-use context.

## Non-claims

RC2 does not establish:

- production Contract E readiness;
- production registration of
  `epistemic_audit.stage_pending_review@1`;
- a real pending-review executor;
- production retry/recovery/rollback;
- exactly-once behavior;
- a production threat model;
- permission to write `10_knowledge/`;
- permission to assign `status: stable`;
- merge, release, promotion, or operational authorization.

## Next smallest discriminator

Before implementing a real executor, test the source and ownership of
point-of-use context.

A successor should determine whether a bounded trusted local mediator can
supply, at the moment of execution:

- the current AuthorityState identity from an authenticated/config-owned source;
- the current evaluation time from the chosen trusted runtime boundary;
- the exact actor/workload identity;
- the re-observed target state;

and whether ERS can consume that mediated context without gaining authority to
alter it.

Only after that should the program revisit a real pending-review write or a
production Contract D effect registration.
