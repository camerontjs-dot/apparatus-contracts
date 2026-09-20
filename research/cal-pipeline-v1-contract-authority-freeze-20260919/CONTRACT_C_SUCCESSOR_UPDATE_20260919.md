# Contract C successor update to the CAL Pipeline authority slice

Date: 2026-09-19

Classification: integration evidence update. This record does not rewrite the original authority freeze, promote Contract C, merge PR #98 or #118, change canonical discovery, release a tag, or authorize Decision/Contract E execution.

## Existing frozen authority remains intact

The original freeze remains byte-preserved:

- `FREEZE_RECORD.md`
- `SLICE_MANIFEST.json`

Its released authority chain remains:

`Contract A 2.0.0 -> Contract B 1.2.0 -> Contract C 1.0.0 -> Contract D 1.0.0`

The reason is evidence-based rather than procedural: the new Contract C successor work is stronger than the prior C1-only state, but it has not yet completed its clean-room independent-consumer gate.

## New Contract C evidence observed

### C2 promotion candidate

Apparatus PR #98 is the exact Contract C 2.0.0 production-shaped candidate:

- branch: `promotion/contract-c-2.0.0-exact-rc2-authority-20260913`
- exact head: `b42c827acb0a9fe65353354d709add0e27bab307`
- state: Draft / open / not merge-authorized
- candidate public version: `2.0.0`
- frozen wire profile: `contract-c-successor-candidate-a-rc2-research`
- canonical discovery on the production base remains Contract C 1.0.0

Exact-head hosted checks are green:

- Contract C 2.0.0 promotion conformance: run `34804396671` — success
- Contract C 1.0.0 conformance: run `34804396591` — success
- Contract B 1.2 production acceptance: run `34804396660` — success

This makes PR #98 a concrete frozen successor candidate, not released authority.

### Typed parent-recomposition binding

Apparatus PR #118 tested the smallest additional surface required by the frozen CAL V1 parent/decomposition state.

Exact research identities:

- decisive experiment head: `7138f6c1599b9b8f8c655f85c9eba0c264fb3b26`
- terminal record commit: `7aafa6e9235e76f0703a394ee42b799f09136846`
- candidate blob: `df6b6ed410f52cafaeadfe1578d770f480a34b09`
- evaluator blob: `dd279c8bff695bfb09cac2f782f39be1300a0cdd`
- decisive run/job: `35445002704` / `105902301724`
- artifact: `10584872739`
- artifact digest: `sha256:dfbf166cef3bb54ead82a32eea6cb38ce831b45f2c9433e996ead275b2ede938`

Observed result:

- terminal disposition: `SUPPORTED_FOR_INDEPENDENT_CONSUMER_APERTURE`
- frozen CAL decomposition controls: 27 passed
- released C1 regression: 16 passed
- parent-binding mutation/replay/reseal checks: 49/49 true
- unchanged Candidate A RC2 public child-result grammar carried all eight frozen PIPE01–PIPE04 child results

This is a genuine narrowing of the earlier C1 insufficiency: the tested successor shape can preserve the frozen CAL V1 child/native/decomposition lineage by adding a typed, externally checked parent-recomposition binding.

## Remaining falsifier

The clean-room independent consumer has not yet run.

Research Scaffold Harness PR #39 currently freezes only the sparse aperture:

- repository: `camerontjs-dot/research-scaffold-harness`
- PR: #39
- exact aperture commit: `52869e08f98ebaaf4acd31dd5955874f7fdaec81`
- state: Draft / open
- consumer execution: not yet present

The aperture deliberately excludes the producer candidate, evaluator, prior consumer code, post-freeze expected output, and Decision policy.

Therefore the new Contract C successor is **not admitted to the shared authority lane yet**.

## Local pipeline rule after this update

Two lanes are now explicit:

1. **Released authority lane:** A2 -> B1.2 -> C1 -> D1. This remains the qualified shared contract-authority path.
2. **C2 successor research lane:** A2 -> B1.2 -> exact PR #98 C2 candidate -> exact PR #118 typed parent-recomposition binding -> **STOP**.

The successor lane may be used only for bounded local research against the exact pinned subjects. Do not call it canonical Contract C authority, do not relabel it as released C2, and do not feed the parent-binding extension into Decision as qualified shared authority until the clean-room consumer closes and Decision compatibility is separately established.

## Why the slice is not silently switched to C2

The heaviest assumption would be that a green producer-side discriminator proves a public contract boundary. PR #118 explicitly does not establish that. The clean-room consumer is the smallest discriminating test because it asks whether a legitimate downstream consumer can reconstruct and verify the binding without producer-private knowledge.

Switching the authority slice before that gate would erase the exact uncertainty the experiment was designed to measure.

## Updated machine-readable handoff

Use:

`SLICE_MANIFEST_V2.json`

for the current local handoff. It preserves all v1 released-authority pins and adds the exact C2 successor lane, its qualification evidence, and the outstanding independent-consumer stop.

Disposition of the released authority lane remains:

`QUALIFIED_FOR_LOCAL_PIPELINE_CONTRACT_AUTHORITY`

Disposition of the C2 parent-binding successor remains exactly:

`SUPPORTED_FOR_INDEPENDENT_CONSUMER_APERTURE`
