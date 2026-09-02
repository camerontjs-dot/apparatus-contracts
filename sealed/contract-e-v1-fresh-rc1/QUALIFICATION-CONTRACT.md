# Contract E v1 Fresh Evaluator Qualification Contract

Classification: **Research Infrastructure / pre-reveal evaluator assurance**.

This qualification applies only to the frozen Contract E v1 candidate at commit `8876b7bcc2afa1a4902400b0cc507cf2ef02e6e7` and the fresh-reproduction evaluator in `sealed/contract-e-v1-fresh-rc1/`.

## Property measured

The evaluator asks whether a fresh implementation produces the same **normative AuthorizationReceipt projection** as the frozen reference candidate over sealed adversarial cases.

Normative comparison fields are:

- `schema`
- `receipt_id`
- `authority_conferring`
- `authorized`
- `request_id`
- `request_sha256`
- `authority_state_id`
- `evaluation_time`
- `subject_id`
- `jurisdiction`
- `authority_basis_id`
- `preserved`

Diagnostic text content is deliberately **not normative**. A conforming implementation must still emit `diagnostics` as a list of strings, but different diagnostic vocabulary or ordering must not falsify semantic recovery.

## Qualification requirements

Before the evaluator may be sealed for a fresh independent reproduction, all of the following must hold:

1. the frozen candidate files remain byte-identical to commit `8876b7bcc2afa1a4902400b0cc507cf2ef02e6e7`;
2. the frozen candidate's own adversarial suite passes unchanged;
3. evaluator self-reference wiring yields complete normative agreement on every hidden case;
4. a diagnostic-only variant also passes, demonstrating that diagnostic wording is outside the normative comparison surface;
5. each seeded weak implementation below is rejected;
6. false-permit mutants produce at least one evaluator-recorded false permit;
7. the preservation mutant produces at least one preservation failure;
8. evaluator qualification occurs before any fresh independent implementation exists.

## Required weak controls

The qualification suite must reject at least these plausible weak consumers:

- `subject_blind`: converts a subject mismatch into authorization;
- `currentness_blind`: converts stale/future/revoked authority into authorization;
- `blocker_blind`: ignores relevant conflict/residue blockers;
- `support_launderer`: lets supporting artifacts substitute for a valid AuthorityState;
- `identity_blind`: accepts malformed/missing/tampered reference identity state;
- `surplus_peer_permitter`: accepts a peer/surplus conferring record rather than rejecting the v1 representation;
- `preservation_dropper`: returns an otherwise reference-derived receipt while deleting preserved evidence state.

These controls are evaluator tests, not alternate Contract E semantics.

## Seal rule

The evaluator is sealable only after a hosted qualification run passes all requirements and emits a qualification receipt containing exact candidate/evaluator identities and weak-control results.

The final seal receipt must pin the accepted run, job, artifact, artifact digest, evaluator/case/qualification blobs and SHA-256 values, and state that no fresh implementation existed at seal time.

After the final seal, `hidden_cases.py`, `evaluate_fresh.py`, `qualify.py`, and this qualification contract are immutable for the reproduction. A defect discovered later must create a successor evaluator and preserve the old seal as evidence.

## Nonclaims

Qualification does not establish Contract E correctness, source legitimacy, root-grant legitimacy, universal interoperability, production promotion, Authorization in the real world, execution, or verification. It establishes only bounded sensitivity and invariance of this evaluator for the named fresh-reproduction comparison.