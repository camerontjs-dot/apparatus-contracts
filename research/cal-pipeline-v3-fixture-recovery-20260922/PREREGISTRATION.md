# CAL Pipeline v3 complete fixture recovery

Date: 2026-09-22

Classification: **Research infrastructure**. This task repairs fixture preservation for an already-observed controlled integration path. It does not change CAL, Contract C, Decision, Contract D, Contract E, ERS, or the PR #130 scientific matrix.

## Decision

Determine whether the complete PIPE01-PIPE03 fixture world used by the frozen CAL Pipeline v3 composition can be recovered or deterministically reconstructed strongly enough to become an explicit immutable input to a successor ERS provenance run.

The missing preservation surface is:

```text
PIPE01/
  cal/contract-c.json
  consumer-inputs.json
  decision-target.json
  contract-d.json
```

with the same four files for PIPE02 and PIPE03.

## Authority

Historical generator and composition:
- apparatus-contracts PR #123
- generator head: `e68e5ab387e9779b0be62d92766b76e475964790`
- hosted run: `35479370533`
- artifact: `10594929710`
- artifact digest: `sha256:bab1e7522a69e404208d9e65d9edae89d860827ef08fd3da1ad01813554b0841`
- composition-result digest: `sha256:2ef133c504cd33bf5b9912acb06e154b43d7060b967dd4230081d4a8ad4f9753`

Carried-forward case identities from PR #127:
- PIPE01 Contract C: `sha256:ba02ec570b0048832a2fc9f6b958f426b11e5dc0fe73cf1e12ae515d38ea23a0`
- PIPE01 Contract D: `sha256:509862ec4b28ba211406eb21d9398f1fab7e153e0c7e12595d6ab8476d053e24`
- PIPE02 Contract C: `sha256:60328dc4413a436b4559a975a60fe35e67e3e1253289ad7c63bca512af41374d`
- PIPE02 Contract D: `sha256:8c7b28718691d6a84ecda4172051172e1c9ecf1d106cbc7e4a9132fda5ff9230`
- PIPE03 Contract C: `sha256:f152754526aa7ea3b47401e9ae956786c73ae6795a53bfabc2a163474bc7f526`
- PIPE03 Contract D: `sha256:12d9619bb4afc449ab5d8b01089940a9917ec28670fd4ed5e6602dd283abe55e`

Exact generator subjects remain those pinned by PR #123. Do not update them to newer component candidates.

## Boundary

Allowed:
- search for a surviving complete historical fixture root;
- download and inspect the exact PR #123 artifact;
- execute the exact PR #123 generator from its frozen commit;
- execute it twice in fresh roots;
- compare bytes and hashes;
- package a complete fixture bundle and machine-readable recovery manifest.

Forbidden:
- modifying PR #130, PR #134, or their frozen runners;
- changing any Contract C, Decision, Contract D, Contract E, CAL, or ERS semantics;
- substituting a nearby fixture;
- claiming newly reproduced `consumer-inputs.json` or `decision-target.json` are historical bytes unless an actual historical copy is recovered and compared;
- running the PR #130 scientific matrix from a reconstructed bundle before that bundle is explicitly frozen/bound by a successor authority record.

## Acceptance

A deterministic reconstruction is supported only if:

1. two fresh executions of the exact PR #123 generator complete;
2. both full composition result files are byte-identical and match the historical result digest;
3. every required fixture file exists for PIPE01-PIPE03 in both executions;
4. historical Contract C and Contract D bytes match the surviving PR #123 artifact when available and always match the PR #127 recorded hashes;
5. all twelve required fixture files are byte-identical across the two fresh executions;
6. a manifest records every file hash and distinguishes:
   - bytes directly matched to surviving historical artifact bytes;
   - bytes reconstructed twice but lacking a preserved historical byte/hash reference.

A recovered historical complete root is stronger evidence and should be preferred if found.

## Failure / stop

Stop and preserve the result if:
- any pinned subject cannot be established;
- any historical C/D identity mismatches;
- the two reproductions differ;
- the historical composition-result digest is not reproduced;
- completing the task would require changing the frozen generator or a semantic subject.

A failed reconstruction does not weaken the prior PR #123 composition result. It means the missing complete fixture package is not reconstructable under this protocol.

## Consequence

If the full historical root is recovered, it may be qualified as the original fixture world after exact comparison.

If only deterministic reconstruction succeeds, freeze it as a **new explicit fixture-bound successor**. Do not relabel it as the original unpreserved fixture bytes. The ERS scientific matrix may then proceed only under a successor authority record that names that bundle.
