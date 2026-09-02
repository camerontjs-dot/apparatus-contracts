# Post-preregistration authenticity / provenance adversarial extension

Status: **frozen before extension implementation or execution**

This extension does not rewrite the original preregistration or its 101-case result. It was prompted by a distinct attack question surfaced during post-run review:

> Do deterministic semantic/content identities establish only integrity/binding, or are downstream consumers accidentally treating them as proof that a trusted producer/evaluator/root authority created the object?

## Why this is separate

The original matrix aggressively mutates exact supplied objects but does not substitute a newly fabricated object that is internally valid and freshly re-hashed. That is a materially different adversary.

Contract E RC1 already states that AuthorityState root provenance/legitimacy is an external trust/configuration boundary. This extension tests whether the proposed D→E and receipt-consumer profiles need analogous explicit provenance boundaries.

## Frozen attack cases

### F1 — forged-but-valid Contract D CLEAR

Start from a valid released Contract D HOLD fixture. Fabricate a new internally valid Decision by changing the completed disposition to `clear`, retaining the same registered effect, then recompute its semantic identity implicitly through the released Contract D consumer.

Observe whether exact Contract D validation/applicability accepts the fabricated bytes as `candidate_for_authorization` when the expectation is constructed from those same fabricated bytes.

Expected observation: **yes**. Contract D provides deterministic identity and semantic validation, not cryptographic producer authenticity.

Safety consequence under test: a D→E adapter must not infer trusted Decision provenance merely from Contract D validity/semantic identity. It needs either a trusted producer invocation boundary, authenticated artifact provenance, or another explicitly trusted source channel.

### F2 — fabricated but self-consistent AuthorityState

Construct a new root `grant` for an attacker-selected subject/operation/target and recompute a valid AuthorityState identity.

Expected observation: Contract E RC1 can authorize against it if the request matches. This is not counted as a Contract E bug because the SPEC explicitly defines root legitimacy as external.

Safety consequence: AuthorityState must enter from an explicitly trusted configuration/provenance boundary; its content hash is not a signature or entitlement proof.

### F3 — forged `authorized=true` AuthorizationReceipt

Take a denied Contract E receipt for a real request. Fabricate a new receipt with `authorized=true` and a plausible `authority_basis_id`, then recompute the deterministic receipt ID according to the candidate's documented semantic projection.

Expected observation: a consumer that checks only request binding + receipt self-hash can be fooled, because an unkeyed deterministic hash does not authenticate the evaluator.

Safety consequence: consumers must either re-evaluate Contract E at point of use or accept receipts only over an explicitly trusted evaluator/provenance channel. Machine execution should retain the preregistered point-of-use re-evaluation requirement.

### F4 — strong point-of-use re-evaluation defeats forged receipt

Feed the forged receipt beside the actual denied AuthorityState/request and require fresh Contract E evaluation.

Expected observation: authorization remains denied despite the forged receipt.

### F5 — diagnostic mutation remains non-authoritative

Mutate diagnostic strings/order only and verify receipt semantic identity remains unchanged while no authorization conclusion is created by diagnostics.

## Falsification / finding rule

If F1/F2/F3 are unexpectedly rejected due to authenticated producer/root/evaluator provenance already encoded in the released/candidate objects, record that stronger property.

If F1/F2/F3 are accepted as expected but a consumer profile treats that acceptance as sufficient proof of trusted origin, record a **PROVENANCE/AUTHENTICITY GAP**. Do not repair history by claiming content identity already solved authenticity.

F4 must reject the forged-receipt attempt under fresh evaluation. Failure is an authority-relevant false permit.

This extension may narrow the promotion claim even if the original 101 cases remain green.

## Nonclaims

This extension does not select a cryptographic signature scheme, PKI, transparency log, attestation format, trusted-computing mechanism, or deployment topology. It tests only whether an explicit trusted-origin boundary is necessary.
