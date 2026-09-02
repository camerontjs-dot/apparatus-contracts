# Contract E RC2 Successor Candidate Freeze Receipt

Status: **FROZEN RESEARCH CANDIDATE — NOT PRODUCTION AUTHORITY**

Date: 2026-09-02

## 1. Pre-implementation preregistration

The experiment semantics and falsifiers were frozen before the RC2 reference implementation existed.

- preregistration commit/head: `161aaac44bc846f49ba3aeb6fe44bb0b8c46a92b`
- preregistration blob: `a6fb67b598c50df37035b198f74105c6ae008db2`
- operator decision blob: `4f8dd5f9a8bbce0dca5056fff4658081a6c6c08a`
- trusted-origin profile blob: `896b4a8494d9bd19d3e0f7d80ef34e6c214c54e6`

The accepted normative delta is limited to preserving separately named claimed and recomputed AuthorityState identities in AuthorizationReceipt semantics. The integration profile separately requires external Decision/AuthorityState trust bindings and fresh point-of-use Contract E evaluation.

## 2. Candidate freeze

Exact tested candidate head:

`3a206729f53672fb28a711980925a24c77e6910a`

Frozen candidate files at that head:

- `candidate/SPEC.md`
  - Git blob: `f05b679a30bafb8a08eef175ecefdb4a38245c9c`
- `candidate/schema.json`
  - Git blob: `42df79ff2c55fb5eaed9e880648abd87d6c20413`
- `candidate/reference.py`
  - Git blob: `98e3bf38dd1fb6028231a7f6b5c2459b387909c6`
- `candidate/test_candidate.py`
  - Git blob: `52c1ff54032b0ee02f00d9abb3e6ac5c3595340e`
- `profile_pressure.py`
  - Git blob: `cea77f3c06b339192c946ad81d9c9ca1dbd89bd3`

No semantic changes to these frozen files may be counted as the same RC2 candidate after this receipt. Any semantic repair requires a separately named successor.

## 3. RC2 core candidate evidence

Hosted RC2 core matrix was executed against the frozen candidate on Python 3.11, 3.12, and 3.13.

Accepted standalone run: `33672743951`.

Result per runtime:

- cases: `60`
- passed: `60`
- failed: none

A downloaded Python 3.11 `RESULTS.json` has SHA-256:

`1fdd555e8eb789ff1c329424035a255ee1085ebe247c9cfc0435a51035ffba57`

Run artifacts:

- Python 3.11: artifact `9863142361`, archive digest `sha256:cd0f1c8e7312968a777a8b26ddfee13e63e28e6bd2719f6bd606dfb8141e95ba`
- Python 3.12: artifact `9863143045`, archive digest `sha256:200e0c17cf782cb957c46f40a62243bf26f66adfdcd8d1e0db0737f729af5190`
- Python 3.13: artifact `9863142324`, archive digest `sha256:cd0f1c8e7312968a777a8b26ddfee13e63e28e6bd2719f6bd606dfb8141e95ba`

The matrix includes the two exact RC1 disagreement families and the new dual-identity obligations. RC2 preserves the supplied/claimed and recomputed canonical AuthorityState identities separately on denial and requires equality for authorization.

## 4. D→E trusted-origin profile evidence

The companion pressure harness was executed against exact released Contract D 1.0.0 and the frozen RC2 reference on Python 3.11, 3.12, and 3.13.

Accepted standalone run: `33672743951`.

Result per runtime:

- cases: `127`
- passed: `127`
- failed: none

A downloaded Python 3.11 `PROFILE_RESULTS.json` has SHA-256:

`fe34cd65c944d25e2b0db68f98354d4f44e803abdbd50913c9a98bfc5f76ba61`

Run artifacts:

- Python 3.11: artifact `9863147329`, archive digest `sha256:24eab9d2b7267b118fdca3d2412a10b3938bed7ea3f55a9f79b7f96a61b2a203`
- Python 3.12: artifact `9863146494`, archive digest `sha256:999615029bb22ed1fb74a3d07f5dd08d31fe64adb83387416a3850d16428de4f`
- Python 3.13: artifact `9863144191`, archive digest `sha256:6171f78941ec1631c309dfdeb2571c388b0678533015925b0dd58cf8b3a3b0f4`

The harness demonstrated and discriminated three deliberately weak controls:

- `O04-weak-derived-decision-anchor-is-fooled`
- `A04-weak-derived-state-anchor-is-fooled`
- `R01-forged-receipt-fools-receipt-only`

The actual profile rejected those forged-origin paths by requiring external trust bindings and fresh point-of-use E evaluation.

## 5. Exact downstream authority used by profile

Released Contract D 1.0.0:

- release commit: `298a1a0f7b7b6d7712e11200d04faec3e1ca169b`
- core validator blob: `564dcde5677df5ac8f86f21dc0ffd1692f44c9f0`
- consumer blob: `8b4ad5c9d6fc1145cf334d1416b5d52b9ed93c68`
- effect registry blob: `a40f4f4447470654bdc16d852f5927189ae30cc5`

The released Contract D checkout remained unmodified after the hosted pressure runs.

## 6. Apparatus note

GitHub initially did not immediately register the newly introduced branch workflow. A branch-only additive job was therefore also attached to an already registered workflow without weakening its existing production acceptance job. The standalone RC2 workflow subsequently registered and successfully executed the accepted evidence at run `33672743951`. The temporary registration workaround is apparatus/control-plane evidence, not semantic evidence.

## 7. Independence state at candidate freeze

`fresh_independent_rc2_implementation_existed_at_candidate_freeze = false`

No fresh independent RC2 implementation has been created or inspected. The next authorized activity is evaluator construction, qualification, and final seal against these frozen candidate bytes. The evaluator must be sealed before any fresh independent implementation begins.

## 8. Current scientific disposition

- RC2 local core candidate: **SUPPORTED BY CURRENT ADVERSARIAL EVIDENCE, PENDING INDEPENDENT RECOVERABILITY**
- D→E trusted-origin profile: **SUPPORTED BY CURRENT ADVERSARIAL EVIDENCE, NOT A PRODUCTION AUTHENTICATION PROTOCOL**
- Contract E production promotion: **NOT YET SUPPORTED**

No production merge, release, operational Authorization, execution, or verification is authorized by this receipt.