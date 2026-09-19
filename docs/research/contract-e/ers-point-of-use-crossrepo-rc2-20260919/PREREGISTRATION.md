# Contract E × ERS point-of-use cross-repository RC2 preregistration

Status: preregistered before RC2 qualification-harness implementation.

## Exact subjects

- Contract E subject:
  `a678c73a661853a3a704666fc6bbf29fa378948f`
- independent ERS point-of-use consumer:
  `73a47dc0ce2e3ae6c7aa6e55c4183e223797724b`
  - repository: `camerontjs-dot/epistemic-research-system`
  - Draft PR: `#2`
  - preregistration: `ab97537fd21ec69853fac0343bf396b23af4a285`
- falsified predecessor:
  - Apparatus Draft PR `#115`
  - head `ce253413f8f8a86ca7fab8a05b2620bbb4997e73`
  - `FALSIFIED_CONSUMER_CURRENTNESS_AND_DECISION_BINDING`

RC2 branches directly from the Contract E subject, not from the falsified RC1
branch.

## Preserved upstream counterexample

Released Contract D 1.0.0 does not admit
`epistemic_audit.stage_pending_review@1`; the released registry returns
`unknown_effect_type`.

RC2 may use only an explicit research-local effect extension. It must not modify
or reinterpret the released Contract D effect registry.

## Preregistered claim

The exact ERS consumer commit above will compose with the exact Contract E
subject above in shadow mode such that:

1. the ERS execution intent preserves the exact typed Contract D identity
   `decision:sha256:<digest>` without projection;
2. Contract E accepts the ERS-generated intent unchanged;
3. ERS and Contract E compute identical execution-intent and target-reference
   identities;
4. an exact fresh Contract E result is accepted by ERS only when the supplied
   point-of-use AuthorityState identity and evaluation time exactly match the
   request embedded in that result;
5. ERS re-observes the target at consumption and requires current pre-state to
   equal the pre-state bound into the authorized intent;
6. all three RC1 counterexamples are rejected;
7. no execution or real MainFrame mutation occurs.

## Required exact-case evidence

The harness must verify the independent ERS checkout HEAD is exactly
`73a47dc0ce2e3ae6c7aa6e55c4183e223797724b`.

The exact case must demonstrate:

- released Contract D rejects the ERS effect before research extension;
- research-local Contract D composition reaches
  `candidate_for_authorization`;
- exact typed Decision identity survives into ERS intent;
- Contract E permits the exact shadow request;
- `execution_occurred=false`;
- ERS accepts the exact point-of-use result;
- ERS/Contract E JCS intent identity matches;
- ERS/Contract E target-reference identity matches;
- no target bytes or MainFrame state change.

## Required falsifiers

At minimum:

1. wrong principal -> deny;
2. wrong target/reference -> deny;
3. fresh revoked AuthorityState -> Contract E deny;
4. replay old authorized result using current revoked AuthorityState identity ->
   ERS reject;
5. replay old result at a newer point-of-use evaluation time -> ERS reject;
6. target pre-state changed after authorization -> ERS reject;
7. swapped/unrelated typed Contract D identity in the execution intent -> ERS
   reject even if Contract E separately verifies the actual decision;
8. generic knowledge-operation receipt -> ERS reject;
9. mismatched execution-intent receipt -> ERS reject;
10. already-executed result -> ERS reject;
11. non-exact ERS consumer commit -> qualification failure.

## Required controls

- frozen Contract E target-cardinality successor: 65/65 controls remain green;
- exact ERS consumer focused tests remain green;
- released Contract D/E normative registry and schemas remain unchanged;
- no real pending-review write;
- no `10_knowledge/` write;
- no `status: stable`;
- cached diff check passes.

The historical broad integration `MATRIX-SIZE 112 < 120` deviation on the
Contract E subject remains inherited and must not be repaired within RC2.

## Trust boundary

RC2 treats `current_authority_state_id` and `current_evaluation_time` as
trusted point-of-use context supplied to the ERS consumer.

RC2 does not establish their authenticated provenance. A pass therefore supports
only the bounded composition claim, not a production trust model.

## Falsification rules

RC2 is falsified if:

- any RC1 counterexample remains accepted;
- ERS and Contract E disagree on intent or target-reference identity;
- exact composition requires projecting away the typed Decision identity;
- the harness must alter the pinned ERS checkout;
- real MainFrame mutation is required;
- released Contract D semantics must change.

## Non-claims

A passing RC2 does not establish:

- production Contract E readiness;
- a production Contract D effect registration;
- authenticated workload/principal identity;
- authenticated AuthorityState/current-time provenance;
- a production threat model;
- a real executor;
- recovery/rollback/exactly-once behavior;
- permission to mutate `10_knowledge/`;
- permission to assign `status: stable`;
- merge, release, promotion, or operational authorization.
