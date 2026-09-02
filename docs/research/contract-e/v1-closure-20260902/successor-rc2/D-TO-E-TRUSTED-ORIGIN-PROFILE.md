# Contract D → Contract E RC2 Trusted-Origin Profile

Status: **research-only integration profile**

This profile is not Contract E core semantics and is not a production authorization mechanism. It freezes the smallest integration assumptions required by the terminal D→E pressure experiment.

## 1. Question

Can an exact released Contract D Decision progress to a Contract E RC2 authorization evaluation and then to a human handoff or machine execution gate without allowing content hashes to masquerade as trusted origin?

## 2. Decision trust anchor

Before Contract D applicability is evaluated, the consumer receives an external `TrustedDecisionBinding` from configuration or another trusted control-plane channel:

```json
{
  "producer_id": "decision-engine:<exact trusted producer identity>",
  "decision_sha256": "sha256:<exact canonical Contract D bytes>"
}
```

The trusted binding MUST NOT be derived from the candidate Decision bytes during the same consumption operation.

The consumer MUST:

1. verify the exact released Contract D authority/validator/consumer;
2. validate and canonicalize the supplied Decision;
3. recompute the supplied Decision's exact canonical SHA-256;
4. require exact equality to `TrustedDecisionBinding.decision_sha256`;
5. only then run exact Contract D applicability against independently supplied requested operation/effect/target expectations.

A structurally valid fabricated Decision with a new self-consistent hash MUST fail this profile when its hash is not the externally trusted Decision hash.

The profile does not specify how `producer_id` or the trusted digest is distributed. Signatures, attestations, transparency logs, and transport authentication remain possible future mechanisms rather than implicit v1 assumptions.

## 3. AuthorityState trust anchor

Before Contract E evaluation, the consumer receives an external `TrustedAuthorityBinding`:

```json
{
  "source_id": "<trusted authority configuration source>",
  "authority_state_id": "sha256:<expected canonical AuthorityState identity>"
}
```

The trusted binding MUST NOT be derived from the candidate AuthorityState during the same consumption operation.

At point of use the consumer MUST:

1. recompute the AuthorityState canonical identity according to RC2;
2. require exact equality between claimed and recomputed AuthorityState identities;
3. require exact equality between the recomputed identity and `TrustedAuthorityBinding.authority_state_id`;
4. then invoke Contract E RC2 against the current AuthorityState and exact AuthorizationRequest.

A self-consistent fabricated root grant therefore remains valid under Contract E core semantics but fails this integration profile unless the external trust anchor explicitly authorizes that exact AuthorityState.

## 4. D→E request construction

An AuthorizationRequest may be constructed only after the exact Contract D consumer returns `candidate_for_authorization` under the external Decision trust binding.

The exact Decision is preserved as an immutable request reference/supporting artifact. It remains non-conferring under Contract E.

The adapter MUST NOT:

- derive requested operation/effect expectations from the Decision and then treat the comparison as independent applicability;
- allow Contract D CLEAR to substitute for standing AuthorityState;
- allow a supporting artifact to replace AuthorityState;
- rewrite subject, operation, scope, target, or effect identity to make authorization succeed.

## 5. Human path

The human handoff consumer must bind an exact human `subject_id` before Contract E evaluation.

A handoff package may be emitted only after fresh point-of-use evaluation of the current externally trusted AuthorityState returns `authorized=true` for that exact human subject and jurisdiction.

The handoff package is non-conferring presentation/audit material. It must preserve the exact Decision and AuthorizationRequest/Receipt identities used for the point-of-use check.

Changing operator, operation, scope, target, current AuthorityState, or unresolved blockers requires a new evaluation.

## 6. Machine path

The machine path binds an immutable `ExecutionIntent` before Contract E evaluation. The ExecutionIntent includes all execution-critical content selected by the experiment, including exact executable/script identity, entry point, arguments, input artifact identities, environment restrictions, and declared external side-effect target.

The Contract E authorization target is the canonical immutable identity of that exact ExecutionIntent.

A machine gate may execute only after fresh point-of-use evaluation of the current externally trusted AuthorityState returns `authorized=true` for the exact machine subject and exact ExecutionIntent target.

Any mutation of the ExecutionIntent changes its identity and invalidates the old authorization binding.

## 7. AuthorizationReceipt consumption

A receipt content hash proves exact receipt bytes/semantic projection. It does not authenticate evaluator origin.

This profile therefore does not treat a previously supplied `authorized=true` AuthorizationReceipt as sufficient permission to act.

For both human handoff creation and machine execution, the bounded v1 rule is:

> Re-evaluate Contract E RC2 at point of use against the current externally trusted AuthorityState and exact request.

A previously issued receipt remains historical evidence. It is not a reusable permit.

## 8. Falsifiers

The profile is falsified if any of the following can still produce an actionable human handoff or executable machine gate:

- fabricated but structurally valid Contract D Decision with a self-consistent new hash not present in the external Decision trust anchor;
- fabricated but self-consistent AuthorityState root not present in the external AuthorityState trust anchor;
- forged `authorized=true` receipt accepted without fresh evaluation;
- Decision hash, AuthorityState hash, or receipt hash treated as proof of producer/evaluator/root legitimacy;
- changed human subject accepted under an old authorization;
- changed ExecutionIntent accepted under an old authorization;
- revoked/stale AuthorityState accepted because an older receipt was authorized;
- mismatched claimed and recomputed AuthorityState identities hidden or collapsed;
- relevant unresolved conflict/residue removed or laundered without a separately authorized resolution operation.

## 9. Nonclaims

Passing this profile does not establish a universal provenance/authentication protocol, cryptographic root legitimacy, role/group authorization, reusable execution permits, replay protection across distributed systems, execution occurrence, execution correctness, or verification correctness.