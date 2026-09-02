# Contract E RC2 Consumer Migration Pressure Preregistration

Status: **preregistered before RC2 consumer verifier adaptation is executed**

## Trigger

The first direct replay of the frozen Contract D → E pressure harness against RC2 reached the scientific target and failed at the first positive consumer case:

- workflow run: `33673015461`
- pressure job: `100390939280`
- first mismatch: `H01-human-positive`
- expected: `true`
- observed: `false`

The exact frozen pressure harness was `attack_matrix.py` Git blob `10eb80cd1ca3b2279c17be934eff62b77c3f4513` from accepted RC1 pressure head `79c0918af76c42e66c30831cd30a8d98d146c30c`.

The failure is an expected wire-contract incompatibility introduced by the operator-approved RC2 receipt change. The RC1 consumer verifier requires receipt field `authority_state_id`. RC2 intentionally replaces that ambiguous field with two normative facts:

- `authority_state_claimed_id`;
- `authority_state_computed_id`.

The old consumer therefore fails closed rather than silently accepting a new receipt schema.

This direct failure is evidence and MUST remain preserved. It is not to be relabeled as an RC2 authority failure or erased by the migration test.

## Migration hypothesis

A minimally migrated RC2 consumer should preserve every existing D→E authority/replay/TOCTOU expectation if its only semantic receipt-binding change is:

For an `authorized=true` RC2 receipt:

1. `authority_state_claimed_id == AuthorizationRequest.authority_state_id`;
2. `authority_state_computed_id == AuthorizationRequest.authority_state_id`;
3. `evaluation_time`, `subject_id`, and `jurisdiction` still exactly equal the request;
4. `request_id` and `request_sha256` still bind the exact request;
5. `receipt_id` still verifies over the complete normative receipt projection excluding `receipt_id` and diagnostics.

No consumer is permitted to accept merely because the two state identity fields exist. Both must agree with the request for an authorized receipt.

## Frozen comparison corpus

Reuse the exact 101-case attack matrix from:

- experiment head: `79c0918af76c42e66c30831cd30a8d98d146c30c`;
- `attack_matrix.py` blob: `10eb80cd1ca3b2279c17be934eff62b77c3f4513`;
- exact Contract D release: `298a1a0f7b7b6d7712e11200d04faec3e1ca169b`.

All 101 original expected outcomes remain unchanged.

The migration apparatus may change **only** the inner `verify_receipt_for_request` function's AuthorityState receipt-field binding from the RC1 single-field rule to the RC2 two-field rule above. No attack case, expected value, adapter rule, machine/human profile, weak strategy, Decision binding, replay rule, target identity rule, currentness rule, or point-of-use rule may be changed.

The applied transformation must be exact, deterministic, and fail if the expected RC1 verifier source block is not found exactly once.

## Falsifiers

The RC2 migrated consumer profile is falsified if:

- any of the 101 original cases changes expected outcome;
- any positive becomes a false reject after the minimal verifier migration;
- any negative/attack becomes a false permit;
- any of the five deliberately weak consumers is no longer discriminated;
- the migration requires an adapter that changes RC2 receipt content, manufactures an RC1 compatibility alias, or ignores either claimed or computed identity;
- execution/replay/TOCTOU behavior differs from the frozen corpus after the minimal verifier migration.

Infrastructure failure before the 101-case matrix executes is `INCONCLUSIVE`, not a semantic failure.

## Nonclaims

Passing this migration comparison would show that the RC2 receipt schema can be consumed by a deliberately migrated downstream verifier without changing the already-preregistered authority-boundary outcomes. It would not establish fresh recoverability, production compatibility, promotion authorization, root authority legitimacy, execution occurrence, or verification correctness.
