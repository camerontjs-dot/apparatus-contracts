# Contract E RC2 Fresh-Reproduction Evaluator Qualification Contract

Status: research evaluator qualification contract. This file does not authorize production Contract E behavior.

## Subject

Frozen RC2 research candidate:

- candidate freeze head: `f616f6ed06bf922a53846d464dfc44838c55804d`
- freeze receipt commit: `d48d24c791837bb64c9ef7ea5ae1771e13892a91`

The evaluator is for a future fresh implementation reconstructed from the frozen RC2 specification/schema. It MUST be qualified and sealed before any such fresh implementation exists.

## Normative comparison surface

For each hidden case, the evaluator compares these receipt fields exactly against the frozen reference:

- `schema`
- `receipt_id`
- `authority_conferring`
- `authorized`
- `request_id`
- `request_sha256`
- `authority_state_claimed_id`
- `authority_state_computed_id`
- `evaluation_time`
- `subject_id`
- `jurisdiction`
- `authority_basis_id`
- `preserved`

Diagnostic strings are nonnormative. The observed `diagnostics` value MUST still be a list of strings.

A fresh implementation is `SUPPORTED` only if every hidden case has an exact normative projection match, no exception, no preservation failure, and no diagnostic-shape failure. Authorization-direction agreement alone is insufficient.

## Required hidden-case families

The sealed corpus MUST cover at least:

1. root policy/grant and valid non-amplifying delegation;
2. exact subject/domain/operation/scope/target-class/target-ref binding;
3. future, expired, revoked, validity-edge, revocation-edge currentness;
4. arbitrary fractional-second precision beyond host microseconds;
5. lineage parent/delegator/record-ID/non-delegation/bounds failures;
6. claimed vs computed AuthorityState identity divergence;
7. malformed claimed identity with recoverable computed identity;
8. uncanonicalizable state where computed identity is unavailable;
9. request AuthorityState identity mismatch;
10. immutable-reference identity and target-resolution failures;
11. request-local duplicate reference/support/conflict/residue IDs;
12. supporting-artifact local resolution and non-conferring behavior;
13. relevant conflict/residue blocking and irrelevant-item preservation;
14. resolution requests remaining fail-closed when relevant blockers are present;
15. future/unknown fields and future schema tokens failing closed;
16. malformed request JSON/host values and schema-safe preservation;
17. upstream A-D/support/status material never substituting for standing AuthorityState;
18. receipt semantic identity including both AuthorityState identity fields.

## Evaluator qualification requirements

Before seal:

- the frozen reference must pass through the evaluator with exact normative match on every hidden case;
- changing only diagnostic wording must still pass;
- seeded weak implementations must be rejected;
- the evaluator must specifically reject a **claimed-only** receipt mutant;
- the evaluator must specifically reject a **computed-only** receipt mutant;
- the evaluator must reject a **microsecond-truncating currentness** mutant that would permit a request after an exact fractional `valid_until` boundary;
- standard subject/currentness/blocker/support/state-identity/request-state/preservation weak controls must also be rejected.

Qualification is evaluator evidence only. It does not establish candidate correctness, fresh recoverability, production compatibility, or promotion readiness.

## Seal rule

After accepted hosted qualification, evaluator semantic files and hidden cases are immutable for the fresh reproduction. Any evaluator defect discovered later requires a successor seal. The final seal receipt must pin candidate identities, evaluator identities, accepted qualification run/job/artifact identities, hidden-case count, weak-control results, and `fresh_implementation_existed_at_seal=false`.
