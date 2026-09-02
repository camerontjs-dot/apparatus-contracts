# Contract E RC2 Fresh Evaluator Qualification Contract

Status: **pre-independent-implementation evaluator qualification authority**

No fresh independent Contract E RC2 implementation may exist before the evaluator described here is qualified and sealed.

## Candidate authority

The evaluator is qualified only against the frozen RC2 candidate at exact tested head:

`3a206729f53672fb28a711980925a24c77e6910a`

Frozen candidate blobs:

- SPEC: `f05b679a30bafb8a08eef175ecefdb4a38245c9c`
- schema: `42df79ff2c55fb5eaed9e880648abd87d6c20413`
- reference: `98e3bf38dd1fb6028231a7f6b5c2459b387909c6`
- candidate tests: `52c1ff54032b0ee02f00d9abb3e6ac5c3595340e`
- trusted-origin profile: `896b4a8494d9bd19d3e0f7d80ef34e6c214c54e6`
- trusted-origin pressure harness: `cea77f3c06b339192c946ad81d9c9ca1dbd89bd3`
- experiment preregistration: `a6fb67b598c50df37035b198f74105c6ae008db2`

## Core evaluator normative projection

The fresh evaluator compares exact receipt fields:

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

Diagnostic string content is non-normative. Diagnostic shape remains required.

The evaluator separately records false permits, false rejects, exceptions, preservation failures, diagnostic-shape failures, and dual-identity failures.

## Hidden-case obligations

The hidden corpus must cover the full RC1 safety families adapted to RC2 plus RC2-specific identity cases. It must include at minimum:

- positive policy/grant/delegation;
- each exact jurisdiction binding;
- currentness/revocation and boundary edges;
- delegation non-amplification and lineage;
- supporting-artifact non-conferral;
- conflict/residue blocking and resolution separation;
- malformed/unknown/version state;
- reference/target identity;
- execution/verification separation;
- surplus peer invalidity;
- `NEG-SUPPORT-CANNOT-CONFER` regression;
- `NEG-STATE-ID` regression;
- malformed claimed identity with recomputable state;
- non-object AuthorityState;
- multiple independently varied claimed identities over the same payload;
- multiple independently varied payloads with stale claimed identity.

## Reference qualification

The frozen reference must obtain:

- normative exact matches: all hidden cases;
- false permits: zero;
- false rejects: zero;
- exceptions: zero;
- preservation failures: zero;
- diagnostic-shape failures: zero;
- dual-identity failures: zero.

Diagnostic-only mutations must leave receipt semantic identity invariant.

## Seeded weak controls

Qualification must demonstrate that the apparatus does not merely reward almost-correct implementations. The following weak strategies must be detected before seal:

1. **claimed-only identity collapse** — substitute the claimed identity into the recomputed field;
2. **recomputed-only identity collapse** — substitute the recomputed identity into the claimed field;
3. **supporting-artifact conferral** — turn an invalid standing AuthorityState into authorization when a Contract D supporting artifact exists;
4. **self-derived Decision trust** — derive the supposedly trusted Decision digest from candidate Decision bytes;
5. **self-derived AuthorityState trust** — derive the supposedly trusted AuthorityState binding from candidate state bytes;
6. **receipt-only permission** — accept a self-rehashed forged `authorized=true` receipt without fresh E evaluation;
7. **historical-receipt currentness** — reuse an old authorized receipt after current AuthorityState revocation instead of evaluating at point of use;
8. **ExecutionIntent substitution** — accept a mutated execution-critical intent under an authorization for the previous intent identity.

Controls 1-3 are core evaluator mutation controls. Controls 4-8 are qualification controls for the separately frozen D→E trusted-origin profile and its pressure harness. They do not become core Contract E semantics.

## Seal rule

The evaluator may be sealed only if all reference obligations pass and all eight weak strategies are discriminated.

The seal receipt must record:

- exact candidate freeze/head and blobs;
- exact evaluator/hidden-case/qualification file blobs;
- hidden case count;
- reference exact-match count;
- weak controls caught;
- qualification run/job/artifact identity;
- `fresh_independent_implementation_existed_at_seal=false`.

Any evaluator repair after seal requires a new seal identity. Any fresh independent implementation created before final seal invalidates the intended independence gate.

## Independent comparison terminal rule

After seal, a fresh independent implementation is `SUPPORTED` only with zero normative mismatches, false permits, false rejects, exceptions, preservation failures, diagnostic-shape failures, and dual-identity failures. Any normative disagreement is `FALSIFIED`. Apparatus/contamination failure preventing valid comparison is `INCONCLUSIVE`.
