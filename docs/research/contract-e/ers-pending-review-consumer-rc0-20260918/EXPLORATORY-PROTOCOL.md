# ERS pending-review Contract E consumer RC0

Status: exploratory research protocol, not preregistration.

## Timing note

The first `ers_profile.py` and `test_ers_profile.py` prototype existed before this
protocol text was written. This document therefore MUST NOT be treated as a
preregistration or used to claim preregistered qualification evidence.

RC0 is retained as exploratory design/discriminator evidence only.

## Subject

- Contract E subject: target-cardinality successor head
  `a678c73a661853a3a704666fc6bbf29fa378948f`
- ERS canonical baseline:
  `0637deae76d22afa4ef3a7ccbf722974ef20edbf`
- consumer: Epistemic Research System
- principal: `agent:epistemic-auditor`
- candidate operation: `epistemic_audit.stage_pending_review@1`
- allowed destination class: `20_live/epistemic-audit/pending-review/`
- execution mode: shadow only
- expressly excluded: `10_knowledge/`, `status: stable`, generic knowledge mutation

## Discriminator

Released Contract D 1.0.0 does not admit the candidate ERS operation. Its
effect registry admits `knowledge.add_verified_tag@1`,
`knowledge.cite_as_evidence@1`, and `task.dispatch@1`.

RC0 must preserve that counterexample and may add only an in-process,
research-only effect extension for composition testing. It does not modify the
released Contract D registry.

## Required RC0 cases

The shadow profile exercises:

1. exact authorized ERS case;
2. wrong principal;
3. wrong execution target;
4. swapped Contract D decision;
5. stale authority;
6. revoked authority;
7. historical receipt/replay after revocation;
8. changed target pre-state;
9. generic knowledge-operation authority substituted for the ERS operation.

The exact case may report `execution_permitted=true`, but all RC0 cases must
report `execution_occurred=false`.

## Non-claims

RC0 does not establish:

- a production Contract D effect registration;
- authenticated workload/principal identity;
- trusted AuthorityState origin;
- production threat-model controls;
- real ERS filesystem mutation;
- production retry/recovery/rollback;
- merge, release, promotion, or operational authorization.
