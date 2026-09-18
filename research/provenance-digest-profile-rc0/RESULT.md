# Provenance Digest Profile RC0 — Context-Free Reproduction Result

**Disposition:** `SUPPORTED_PROVENANCE_DIGEST_PROFILE_RC0`

**Classification:** Draft Research evidence record only.

**Date:** 2026-09-18

## Authority lineage

- candidate provenance schema/architecture authority: `camerontjs-dot/apparatus-contracts@1a5929295e735e351320cbd8c966dc43afed2859`
- explicit bounded digest profile/vector head: `camerontjs-dot/apparatus-contracts@28cc32240660a2181a45dc0ffb4b53c44a001175`
- minimal expected-root authority: `camerontjs-dot/apparatus-contracts@a21a5e528d49342423561520d4cd887f87956580`
- unchanged Fresh Full-Chain RC0 package preparation: `camerontjs-dot/research-scaffold-harness@5a984ab1053a40d053681f00522fbe63e96a73a0`

## Evidence source and aperture

A fresh local context-free consumer was reported frozen before package/root reveal.

Consumer:

- version/aperture: built from `PROFILE.md` Sections 2–4 at `28cc32240660a2181a45dc0ffb4b53c44a001175` plus the two candidate schemas at `1a5929295e735e351320cbd8c966dc43afed2859`
- bytes SHA-256: `sha256:8e50b94c31b8ea0a5eec292ebfe73ca78d6868841ba87dfcf05deaad41da8880`
- bytes: 5337
- lines: 163
- local file frozen read-only after construction
- profile: `cal-provenance-canonical-json-bounded-1`

The local durable receipt was reported as:

`sha256:1e46373c9ef3fb3d26c00172050b25d6284664463963603461cf5cbdcc0a1627`

This GitHub record preserves the operator-transmitted result identity and counts. The private local receipt remains the byte authority for the local reproduction.

## Portable vectors

The fresh consumer independently reproduced both frozen profile vectors:

| Vector | Result | Digest |
| --- | --- | --- |
| `unicode-null-nested-attestation` | PASS | `sha256:e1d99cc2f181610ab355fee57b65e64285f60942bfce96b47ef3b277f90a6e4d` |
| `unicode-retention-manifest` | PASS | `sha256:ad2933137a17bb01402aac8cd979dd3561f5578bb0464b06c4e75acb76649ebf` |

Both preimages included the profile-required terminal LF.

## Unchanged manifest roots

All four unchanged manifests recomputed exactly to both their claimed identity/digest and the independently frozen expected root:

| Case | Expected/recomputed root | Result |
| --- | --- | --- |
| `not-needed-single` | `sha256:9f713080ae9c42b4674ede0b58742504d856df963772b03af5cd426b365c580f` | PASS |
| `health-canada-text-representation` | `sha256:0fd17e3e15cca4c77923eff9450160e80f470dcebaad697f130bec82cfc00ec9` | PASS |
| `valve-temporal-status` | `sha256:0e81c6de1abf39a2c8272f43c11d7e2510b566f40ab9592b86806b1941ff6372` | PASS |
| `declared-all-of` | `sha256:7a3c9f78fdc6cb6dbee32a580769bf65f6bc1cdfa40bc4b2144026ca8d6222c8` | PASS |

No expected root or package was moved, resealed, repaired, or rewritten.

## Attestation identities

Every present-stage sealed attestation reproduced under the explicit profile:

- `not-needed-single`: 5 / 5 PASS
- `health-canada-text-representation`: 5 / 5 PASS
- `valve-temporal-status`: 5 / 5 PASS
- `declared-all-of`: 3 / 3 PASS
- total: **18 / 18 PASS, 0 FAIL**

The declared/all_of case correctly has no CAL or Decision attestation because those stages were not present.

## Mutation controls

Six disposable mutations were reported rejected while canonical package bytes remained unchanged:

1. manifest digest preimage without terminal LF;
2. attestation digest preimage without terminal LF;
3. manifest self identity/digest retained in its own preimage;
4. attestation self identity/digest retained in its own preimage;
5. manifest bound `run_id` mutation;
6. attestation bound `operation.name` mutation.

Result: **6 / 6 rejected**.

## Interpretation

This successor resolves the specific ambiguity exposed by the preceding context-free failure.

The prior disposition:

`FALSIFIED_PROVENANCE_V1_CONTEXT_FREE_DIGEST_PORTABILITY_RC0`

remains valid for the earlier underspecified schema/architecture aperture. It is not erased or relabeled.

This result supports the narrower successor claim:

> Given the explicit `cal-provenance-canonical-json-bounded-1` profile, a fresh consumer can independently derive the unchanged Fresh Full-Chain RC0 RunManifest and ApparatusAttestation identities from the existing package bytes and independently frozen roots.

The result therefore supports the profile as the missing bounded digest/identity specification.

## Remaining separate question

The preceding full reconstruction consumer also reported logical-link/configuration alias gaps. Those observations were intentionally excluded from this discriminator.

This result does not establish that those links are canonical, unambiguous, or independently resolvable. They require a separate bounded discriminator now that digest identity is portable.

## Nonclaims

This result does **not** establish:

- complete cross-object logical-link portability;
- alias normalization correctness;
- provenance-schema release readiness;
- retrieval recall or evidence completeness;
- CAL semantic correctness;
- Decision correctness;
- production readiness;
- Authorization;
- merge, release, or promotion authority.

Keep this evidence in Draft Research state.
