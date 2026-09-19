# Contract E × ERS cross-repository shadow RC1 result

Disposition: `FALSIFIED_CONSUMER_CURRENTNESS_AND_DECISION_BINDING`

RC1 is falsified. No merge, release, promotion, production registration, or real execution is justified.

## Exact subjects

- Contract E subject: `a678c73a661853a3a704666fc6bbf29fa378948f`
- RC1 preregistration commit: `59afb99eada26abec8ae7ee94a818f61d16b6e78`
- independent ERS consumer: `0038ae3f16894e96f9aaf45ffe3bc93a6059da2c`
- ERS Draft PR: `camerontjs-dot/epistemic-research-system#1`
- exploratory predecessor only: `camerontjs-dot/apparatus-contracts#113`
- candidate principal: `agent:epistemic-auditor`
- candidate operation: `epistemic_audit.stage_pending_review@1`
- execution mode: shadow only

## Preserved Contract D counterexample

Released Contract D 1.0.0 continues to reject the ERS-specific effect as
`unknown_effect_type`.

RC1 used only a research-local effect extension. Released Contract D registry and normative schemas were not changed.

## Identity representation mismatch observed before the main discriminator

Contract D exposes its semantic identity as a typed string:

`decision:sha256:<digest>`

The ERS RC0 consumer currently accepts only bare:

`sha256:<digest>`

These are not natively the same representation. RC1 used an explicit, reversible research projection that removes only the `decision:` type prefix and verifies that adding the prefix back reproduces the original Contract D identity.

This projection is a research adapter and a limitation. It is not evidence of native cross-repository identity conformance.

## Exact case

With the exact ERS consumer commit, current authority, current target pre-state, exact target, exact principal, and exact research-local operation:

- Contract E: `execution_permitted=true`
- Contract E: `execution_occurred=false`
- ERS shadow consumer: accepted
- no real MainFrame mutation occurred

This exact pass does not rescue the preregistered claim because required negative cases failed.

## Falsifying counterexamples

### 1. Historical authorization replay after revocation

A fresh Contract E reevaluation against an AuthorityState revoked before the evaluation time correctly returns:

- `execution_permitted=false`
- `execution_occurred=false`

However, the previously authorized Contract E result remains accepted by the exact ERS consumer after revocation.

Observed:

`REPLAY_OLD_AFTER_REVOCATION_ERS ACCEPTED True`

This falsifies the preregistered replay/currentness requirement.

### 2. Target pre-state change after authorization

The target pre-state identity was changed after authorization by writing only inside a disposable temporary fixture. Re-observation confirmed a different `state_sha256`.

The exact ERS consumer nevertheless accepted the old authorized result without re-observing or comparing the current target state.

Observed:

`OLD_AFTER_TARGET_CHANGE_ERS ACCEPTED True`

This falsifies the preregistered point-of-use target-currentness requirement.

### 3. Swapped Contract D decision identity inside the execution intent

An ERS execution intent was constructed with a deliberately unrelated bare decision digest while the actual Contract D decision supplied to Contract E remained unchanged.

A research-local authority record was issued for that intent's target reference.

Observed:

- Contract E permitted the swapped-input intent.
- ERS accepted the resulting Contract E shadow result.

The current Contract E machinery verifies the actual Contract D decision separately but does not establish that the execution intent's input-identity field is the typed identity of that exact decision. The ERS consumer likewise does not establish that relationship.

This falsifies the preregistered swapped-decision binding requirement.

## Controls that behaved correctly

The same cross-repository run observed:

- wrong principal: denied by Contract E;
- wrong execution target/reference: denied by Contract E;
- fresh revoked authority: denied by Contract E;
- generic `knowledge.add_verified_tag` operation substituted into the receipt: rejected by ERS;
- mismatched execution-intent identity in the receipt: rejected by ERS;
- exact shadow case: permitted;
- `execution_occurred=false` throughout.

The weakness is therefore narrower than total authorization failure. It is concentrated at the consumer-side currentness/point-of-use boundary and the semantic binding between the execution intent's decision input and the actual typed Contract D decision identity.

## Interpretation

What else could explain the observations?

- Revocation works in Contract E when reevaluated, so the replay failure is not evidence that Contract E ignores revocation.
- The old result contains the historical request and authority-state identity, but the ERS consumer does not receive current AuthorityState or current evaluation context and therefore cannot establish freshness.
- Target identity was bound into the execution intent, but the ERS consumer does not re-observe target pre-state at consumption time.
- Contract E separately verifies the trusted Contract D decision but does not currently require the execution intent's `input_identities` to encode that same typed decision identity.

The smallest supported conclusion is not that Contract E as a whole is broken. The composition is incomplete: the current ERS consumer can validate receipt shape and exact target-reference identity, but it cannot safely turn an old shadow permit into a point-of-use authorization decision.

## Falsifier for the successor

A successor should pass only if an independent consumer can demonstrate all three properties without weakening the existing negatives:

1. fresh current AuthorityState is checked at consumption/point of use, so an old permit is rejected after revocation;
2. current target pre-state is re-observed and matched to the authorized intent immediately before execution;
3. the execution intent is explicitly bound to the exact typed Contract D decision identity, without a lossy or ambiguous identity projection.

A smaller discriminator should test these three properties before adding a real executor or production effect registration.

## Non-claims

RC1 does not establish and does not attempt:

- production Contract E readiness;
- production Contract D registration of the ERS operation;
- a real ERS executor;
- authenticated workload/principal identity;
- authenticated AuthorityState/config origin;
- production threat-model sufficiency;
- rollback/recovery/exactly-once execution;
- permission to write `10_knowledge/`;
- permission to assign `status: stable`;
- merge, release, promotion, or operational authorization.
