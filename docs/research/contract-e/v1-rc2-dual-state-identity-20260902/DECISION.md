# Contract E RC2 Successor Decision Record

Status: **operator-approved research successor; not production authorization**

Date: 2026-09-02

## Trigger

Frozen Contract E candidate RC1 was independently reproduced from its frozen public specification and schema. The sealed evaluator returned `FALSIFIED` with 48/50 normative exact matches, zero false permits, zero false rejects, zero exceptions, zero preservation failures, and zero diagnostic-shape failures.

The two mismatch case IDs, `NEG-SUPPORT-CANNOT-CONFER` and `NEG-STATE-ID`, had one common cause: the RC1 receipt exposed one ambiguous `authority_state_id` field when the supplied AuthorityState identity did not match the canonical identity of the supplied state bytes.

- RC1 reference reported the supplied/claimed state identity.
- The fresh independent implementation reported the recomputed canonical state identity.
- Both denied the requests.

The RC1 public specification did not determine which fact the single receipt field represented after integrity failure.

## Operator decision

Preserve **both facts**, separately named.

RC2 receipts therefore carry:

- `authority_state_claimed_id`: the syntactically valid SHA-256 identity supplied in `AuthorityState.authority_state_id`, otherwise null;
- `authority_state_computed_id`: the canonical SHA-256 identity recomputed from the supplied AuthorityState excluding `authority_state_id`, whenever canonicalization is possible, otherwise null.

For a valid AuthorityState the two values are equal. For an identity-tampered but canonicalizable AuthorityState they diverge. Both fields are part of receipt semantic identity.

This is an audit/provenance rule. Neither field independently confers authority.

## Additional pre-freeze findings carried into RC2

The fresh RC1 implementation recorded uncertainties that exposed several places where RC1 implementation behavior was more specific than the public specification. RC2 makes these explicit rather than leaving another recoverability trap:

1. immutable-reference `ref_id` values, supporting-artifact `id` values, conflict `id` values, and residue `id` values are unique within their respective request arrays;
2. each supporting artifact `ref_id` must resolve to a request-local immutable reference;
3. the same canonical JSON algorithm is used for AuthorityState identity, immutable-reference identity, request hash, and receipt semantic identity;
4. decoded-object evaluation cannot recover duplicate raw JSON member names after a lossy parser; normative raw JSON ingestion must reject duplicates before decoding;
5. on malformed requests, receipt preservation remains schema-valid: each request list is copied only when that list consists of schema-valid item shapes, otherwise that preserved list is empty;
6. relevant unresolved/contested blockers remain blocking on every request, including resolution requests; the item being resolved is represented by the immutable target reference and is not discharged through the blocker arrays.

These clarifications are intended to preserve RC1 reference behavior and the already-preregistered D→E pressure profile rather than enlarge authority.

## Exact-time safety correction

A separate discriminating check found an RC1 reference defect: Python `datetime.fromisoformat` truncates fractional seconds after six digits. Under RC1 this could compare `...1234568Z` equal to `...1234567Z`, creating a false permit immediately after `valid_until` or at a sub-microsecond revocation boundary.

RC2 compares arbitrary fractional-second precision exactly. Leap-second `:60` timestamps remain rejected. This is an authority-safety correction and is not backported into frozen RC1 evidence.

## Research posture

RC1 remains permanently `FALSIFIED` for exact fresh recoverability and is not repaired in place.

RC2 requires its own:

- candidate tests and adversarial pressure;
- immutable candidate freeze;
- evaluator qualification and seal before any fresh RC2 implementation exists;
- fresh independent reproduction from a narrow context-free aperture;
- post-freeze comparison;
- separate owner authorization before any production Contract E promotion/tag/release.
