# Contract E RC3 Fresh Evaluator Qualification Contract

Status: **research evaluator contract**

Production authorization: **false**

## Purpose

Qualify a sealed evaluator for a future fresh independent implementation of the frozen Contract E RC3 candidate.

The evaluator itself is a system under test. Qualification must occur after candidate freeze and before any fresh independent RC3 implementation exists.

## Frozen candidate authority

Candidate freeze receipt:

`docs/research/contract-e/v1-rc3-exact-currentness-jcs-20260902/CANDIDATE_FREEZE_RECEIPT.json`

Accepted candidate head:

`72f44d206f4f7e64d6993ac85e2fe2f086afb381`

Frozen reference blob:

`ede55efbe3f8afc35a25716af4a896a669a904e7`

## Normative comparison

The evaluator compares these AuthorizationReceipt fields exactly:

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

Diagnostic content is nonnormative, but `diagnostics` must be a list of strings.

A false permit or false reject is additionally recorded from `authorized`.

## Required hidden sensitivity

The hidden corpus must discriminate at least:

- exact subject/jurisdiction/target binding;
- claimed vs recomputed AuthorityState identities;
- request/state identity mismatch;
- exact arbitrary-precision fractional currentness including the three RC2 terminal falsifiers;
- inclusive validity and revocation-at-boundary semantics;
- RFC 8785 JCS + LF identity/hash behavior on schema-invalid but canonicalizable numeric/Unicode observations;
- delegation lineage and non-amplification;
- request-local uniqueness and immutable-reference integrity;
- support non-conferral and local support reference resolution;
- fail-closed conflict/residue behavior including resolution requests;
- surplus peer rejection;
- safe malformed-input preservation.

## Required seeded weak controls

Qualification must catch all seeded weak implementations, including:

1. claimed-only state identity reporter;
2. recomputed-only state identity reporter;
3. host-microsecond currentness truncator;
4. ordinary sorted JSON canonicalizer instead of RFC 8785 JCS + LF;
5. subject-blind evaluator;
6. currentness-blind evaluator;
7. blocker-blind evaluator;
8. resolution-blocker bypass;
9. support launderer;
10. state-identity-blind evaluator;
11. surplus-peer permitter;
12. request-local uniqueness blind evaluator;
13. preservation dropper.

The host-microsecond mutant must produce a recorded false permit or false reject on a hidden fractional-currentness case. The ordinary-JSON mutant must produce a normative hash/identity mismatch on a hidden JCS-sensitive case.

## Diagnostic invariance

A wrapper that changes only diagnostic strings while preserving diagnostic shape must still be `SUPPORTED` and retain exact normative receipt identity.

## Qualification acceptance

Qualification is `PASS` only when:

- a reference passthrough is exact on every hidden case;
- the diagnostic-only variant is supported;
- every seeded weak control is falsified in its required failure class;
- no fresh independent RC3 implementation existed before qualification/seal;
- frozen candidate bytes remain exact.

No failing weak control may be deleted, weakened, or reclassified merely to obtain a passing qualification.

## Seal rule

After accepted hosted qualification, record exact evaluator/hidden-case/qualifier blobs, qualification run/job/artifact/digest, hidden case count, weak-control outcomes, and the absence of a fresh implementation in a final seal receipt.

After the final seal, evaluator semantics and hidden cases are immutable for that fresh reproduction programme. An evaluator repair after fresh implementation freeze would require a separately named successor evaluator/reproduction.
