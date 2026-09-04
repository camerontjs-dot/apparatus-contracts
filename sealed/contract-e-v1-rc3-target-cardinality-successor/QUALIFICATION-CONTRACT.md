# Contract E RC3 target-reference cardinality successor evaluator qualification

Status: **research evaluator contract**

Production authorization: **false**

## Decision

Determine whether the separately named successor evaluator is reliable enough to test the exact RC3 target-reference cardinality rule without losing any predecessor RC3 discrimination.

The normative RC3 SPEC and schema are unchanged. Candidate freeze authority is recorded in `docs/research/contract-e/v1-rc3-target-reference-cardinality-successor-20260903/CANDIDATE_FREEZE_RECEIPT.json`.

## Required corpus

Qualification must include:

- all 59 predecessor RC3 hidden cases;
- all 3 preregistered successor target-cardinality cases;
- total successor hidden corpus: 62 cases.

The three new cases are:

1. duplicate individually valid target identities under distinct request-local `ref_id` values;
2. one valid target reference plus one duplicate-looking invalid reference;
3. multiple validated target matches among otherwise valid unrelated references.

## Normative comparison

The evaluator compares exactly the predecessor normative AuthorizationReceipt projection:

- `schema`
- `receipt_id`
- `authority_conferring`
- `authorized`
- `request_id`
- `request_sha256`
- `claimed_authority_state_id`
- `recomputed_authority_state_id`
- `evaluation_time`
- `subject_id`
- `jurisdiction`
- `authority_basis_id`
- `preserved`

Diagnostic content remains nonnormative, but diagnostic shape must remain a list of strings.

## Minimal-repair regression gate

The predecessor frozen reference and successor reference must be normatively exact on all 59 predecessor hidden cases. Any mismatch falsifies the claim that this is only a target-reference cardinality repair.

## Required predecessor weak controls

All 14 predecessor seeded weak controls remain mandatory:

1. `claimed_only`
2. `recomputed_only`
3. `microsecond_truncator`
4. `ordinary_json_canonicalizer`
5. `subject_blind`
6. `currentness_blind`
7. `blocker_blind`
8. `resolution_blocker_bypass`
9. `support_launderer`
10. `state_identity_blind`
11. `reference_identity_blind`
12. `surplus_peer_permitter`
13. `request_uniqueness_blind`
14. `preservation_dropper`

Each must still be falsified in the same required failure class used by the predecessor qualification.

## New weak discriminator

A fifteenth weak control, `target_cardinality_blind`, must reproduce the predecessor membership/at-least-one target-resolution behavior. It must be falsified by the successor evaluator and must produce a recorded false permit on at least one `target-reference-cardinality` hidden case.

If that weak control passes the same gate as the successor reference, qualification is `INCONCLUSIVE`, not repairable after observing the result.

## Diagnostic invariance

A wrapper changing only diagnostics while preserving diagnostic shape must remain `SUPPORTED` with exact normative receipt identity.

## Acceptance

Qualification is `PASS` only when all are true:

- reference passthrough: `62/62` normative exact;
- predecessor reference regression: `59/59` normative exact;
- target-cardinality corpus: `3` cases present;
- diagnostic-only variant: `SUPPORTED`;
- predecessor weak controls caught: `14/14`;
- new cardinality weak control caught: `1/1` with a false permit on a cardinality case;
- no false permit, false reject, exception, preservation failure, or diagnostic-shape failure for the reference passthrough.

No passing scientific result authorizes production use, merge, release, execution, or verification.
