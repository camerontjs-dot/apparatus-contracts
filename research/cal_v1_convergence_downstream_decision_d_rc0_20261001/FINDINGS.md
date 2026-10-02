---
title: "Exact CAL convergence downstream equivalence — terminal findings"
domain: applied-ai-research
type: research-findings
status: completed
source: "Frozen apparatus-r1; real local run-02 and raw component outputs"
tags: [cal, integration-qualification, contract-c, decision, contract-d]
updated: "2026-10-01"
---

# Exact CAL convergence downstream equivalence

**`SUPPORTED_EXACT_CAL_CONVERGENCE_DOWNSTREAM_EQUIVALENCE`** on the three
preregistered PIPE specimens and the two control designs.

Swapping exact CAL Slice 2 `ddaf945…` for convergence `6bb0d60…`, using the
candidate's author → conform → execute workflow, changed none of the required
native or downstream bytes. The observed result is bounded integration evidence
for [issue #158](https://github.com/camerontjs-dot/apparatus-contracts/issues/158).

## Exact apparatus and subjects

Base: `c3563cff66d2c85dcbf575c693056e2d8e4563d4`.

Executed successor freeze:
`fd4a8052364de37b6948e81cb7269e9409aaad69`, tree
`3eb8a5fb9577d47328f4339ccb81c78064621337`.

Harness blob: `4cb9a9b7ba276a04eb2018a031a6cd88bca92a57`.
Harness SHA-256:
`sha256:51dd0cba07ff4990300b71508715aa6dad9b42a1975515a51fc759e7dcdfe504`.

All 11 exact subject commits/trees and 594 relevant working blobs were verified
before and after execution. The full matrix is [SUBJECTS.json](SUBJECTS.json).
No pin advanced. No component implementation changed. The historical PR #123
source is reused byte-for-byte; the new wrapper owns only orchestration, custody,
the conformance gate, and exact byte discriminators.

Both CAL wheels were built from their exact trees, verified against 81 Arm A and
83 Arm B packaged source blobs, and clean-installed in separate environments.
Python 3.11.15 and Node 22.19.0 were used. Dependency versions matched between
arms. Installed CAL imports came from the corresponding clean environment.
The inherited `0.6.0` package token remains subject metadata.

Protected semantic implementation remained
`847cc970642bb648dc994b929c2053b5c9d4648c`; DecompositionComposer remained blob
`268d0dc4dd22ddde3848141d62b7d719e48d374d`. The four protected maintained Decision
blobs, external C authorities/consumer, and released D validator/consumer were
unchanged and physically invoked.

## Paired observations

| Case | Required A/B bytes | Parent | Decision | Released D consumer |
|---|---|---|---|---|
| PIPE01 | identical | supported | clear | candidate_for_authorization |
| PIPE02 | identical | contradicted | hold | hold |
| PIPE03 | identical | not_checkable | hold | hold |

Each paired comparison included trusted/authored targets, all six native files
per child, parent-result bytes, external C bytes and manifest-bound whole-object
identity, materialized Decision/canonical D bytes, and actual D consumer stdout.
Contract A, EB native package, and complete Contract B artifact sets also matched.
Explicit clean-installed child runs equaled the parent CLI's own child runs.
No semantic or JSON-object comparison replaced available byte comparisons.

The shared C1 trusted/authored target hash was
`sha256:f7a341852be2ad6cfac6dfe5f1f082450248a15989edc16e171e8e45f18d980c`;
C2 was
`sha256:baa835920af21912332c0aa0f95079fa7d18e044ab2befe83f24b270693f5b7f`.

| Case | Identical C whole-object SHA-256 | Identical canonical D SHA-256 |
|---|---|---|
| PIPE01 | `ba02ec570b0048832a2fc9f6b958f426b11e5dc0fe73cf1e12ae515d38ea23a0` | `509862ec4b28ba211406eb21d9398f1fab7e153e0c7e12595d6ab8476d053e24` |
| PIPE02 | `60328dc4413a436b4559a975a60fe35e67e3e1253289ad7c63bca512af41374d` | `8c7b28718691d6a84ecda4172051172e1c9ecf1d106cbc7e4a9132fda5ff9230` |
| PIPE03 | `f152754526aa7ea3b47401e9ae956786c73ae6795a53bfabc2a163474bc7f526` | `12d9619bb4afc449ab5d8b01089940a9917ec28670fd4ed5e6602dd283abe55e` |

Arm B PIPE01 repeated in a separate root with byte-identical complete native
child sets, parent result, C, and D.

## Negative controls

The preserved C1 cross-run replay from PIPE03 into PIPE01 was rejected in both
arms. Attack-input bytes were identical. Both maintained Decision invocations
exited 1 with `contract_c_validation_failed` and frozen-consumer
`NATIVE_RESULT_HASH_MISMATCH`; stdout was zero bytes, so no D was emitted.
False accepts: zero.

For the frozen #184 comparison-direction drift shape, unchanged raw structural
validation accepted with exit 0. Candidate conformance rejected with exit 2.
The actual gated orchestration trace ended at conformance: zero child, parent,
Decision, and D consumer invocations; no native/C/D output. Structural validation
remained the weaker comparison. Raw `run-bundle` is not claimed to enforce this
gate by itself.

## Receipts and repository regression

The real operational run recorded 217 subprocess commands. All 434 stdout/stderr
files were rehashed against the receipt. A separate custody check directly
rechecked 111 byte pairs, complete artifact sets, C manifest identities, repeat
outputs, and negative-control traces. This is a second mechanical custody check
by the same engineering run, not independent scientific review.

The machine result is [LOCAL_RESULT.json](LOCAL_RESULT.json), exact SHA-256
`sha256:5e2bcc20763338c2de6850f14bca7eecd68293dddf5cbb98d152b29bc2838d1f`.
Private raw receipt SHA-256:
`sha256:f38d9da4de12a8a84c3e00a0c9e593d19533ad5d0ab029b2d9917f968ded6d87`.
Raw native files, both wheels, exact commands and streams are retained outside
the source checkout. The task workflow reproduces the frozen wrapper and uploads
these evidence types from hosted execution.

Repository-maintained `make verify test` passed: spec/canonical parity over eight
vocabularies; full pytest **99 passed, 8 skipped, 1 warning**. The generic
vocabulary verifier reported three absent default sibling consumer paths in this
isolated layout. Those absent checks and skipped tests are not counted as executed
cross-repository coverage; the exact-subject pipeline checks above ran separately.
The new wrapper also passed compile, Ruff checks, and formatting before freeze.

## Preserved first failure and deviations

[FIRST_RUN_FAILURE.json](FIRST_RUN_FAILURE.json) and
[DEVIATION_RUN01.md](DEVIATION_RUN01.md) preserve the first frozen run at
`e0b94f8…`. It stopped before decisive exposure because the new wheel guard tried
to read undeclared, unrelated UI HTML from the predecessor's wheel. The bounded
successor checks actual packaged files and still requires every Python module
and production V1 file. It changes no component, subject, input, expected outcome,
mutation, replay falsifier, target grammar, or primary byte discriminator.

Both wheels retained the predecessor's omission of that nonruntime UI data.
Two earlier setup observations (worktree path resolution and shared-cache access)
were corrected only in task-owned setup resources. Inherited Pydantic schema-name
warnings remained on stderr and were preserved separately from result bytes.
No scientific counterexample or compatibility failure was observed on this path.

## Interpretation and remaining boundary

These exact CAL subjects were downstream-equivalent on this fixed three-case
path, and the supported target workflow composed fail-closed with external C,
maintained supported-claim Decision, and released D 1.0.0.

This does not independently qualify accuracy, unrestricted target authoring,
Decision's ERS pending-review effect, Contract E, Authorization, or execution.
It does not release/version C, merge CAL PR #186, change a consumer pin, or decide
CAL's release version. Newly generated inputs/outputs are explicit reconstructions
of the preserved specimen, not recovered historical PR #123 output bytes.

Before CAL 1.0: independent promotion review and operator acceptance of #186's
exact candidate and this integration evidence; separately governed public
interface/compatibility/version and successor release-lock decisions; qualified
release artifact custody and the authorized consumer-migration procedure.
Representative accuracy evidence remains necessary before any validated-accuracy
claim. The smallest next action is independent review of these exact receipts.

## Hosted transport observation and apparatus-r2

Both initial hosted runs ([push 36960792497](https://github.com/camerontjs-dot/apparatus-contracts/actions/runs/36960792497),
[PR 36960818148](https://github.com/camerontjs-dot/apparatus-contracts/actions/runs/36960818148))
completed the paired experiment and maintained regression but failed evidence
upload. The uploader rejected `:` in an unchanged native Contract B filename;
932 selected files were found and zero artifacts created. Neither is reported
as a hosted artifact-custody pass.

[DEVIATION_HOSTED_UPLOAD.md](DEVIATION_HOSTED_UPLOAD.md) records the classification
before correction. The separately frozen apparatus-r2 changes only transport:
a helper packages the same evidence files with original internal paths/bytes
and rechecks every member SHA-256. Its local roundtrip covered all 932 files.
The scientific harness blob, subjects, targets, controls, and byte discriminator
remain unchanged. The valid apparatus-r1 local result above is preserved.
Hosted successor results are separate receipts in Draft PR #160; no earlier
failed run is relabeled.

## Verified hosted successor receipt

The separately frozen [push run 36961507754](https://github.com/camerontjs-dot/apparatus-contracts/actions/runs/36961507754)
at `d35b68cca865f3ba96503bc81d3c23ba38704d1a`, tree
`e774be2c87dff1e83a0e3c90ce75fcf96f78b04c`, completed successfully.
Its [artifact 11207922919](https://github.com/camerontjs-dot/apparatus-contracts/actions/runs/36961507754/artifacts/11207922919)
was downloaded and verified: ZIP digest
`sha256:0f79b6e429ec1365b19035950da488080dad12338a5a99f52f3e5266e6d871b6`,
internal transport archive digest
`sha256:54498af29096e8738e113bc606be6948165d5ecaefb9b52a5c4d5041df4bc441`.

All 932 archive members matched their manifest; all 434 command streams matched
the 217-command receipt; both wheels matched recorded hashes. A supplementary
mechanical check directly verified 330 pairs, complete native sets and identities,
repeat outputs, replay errors/no D stdout, and the conformance stop trace.
All 450 generated world files were also byte-identical across local macOS and
hosted Linux, including A/EB/B artifacts and the complete native/downstream output.

Hosted runtime: Python 3.11.16 / Node 22.23.3. Maintained regression again reported
99 passed, 8 skipped, 1 warning. The
[PR run 36961510781](https://github.com/camerontjs-dot/apparatus-contracts/actions/runs/36961510781)
also passed; the push receipt is canonical. These are implementer-authored
engineering receipts, not independent review.

[HOSTED_RESULT.json](HOSTED_RESULT.json) is the exact hosted machine result:
`sha256:2c5a3079e25010cdbbf501812c5e071fc84c074afd94c15e975038c01709a061`.
Hosted raw receipt:
`sha256:819ab5230336b02ed23ff101ec81902587fd35aedfafb75c16ac4ebe6966046b`.
Result-record hashes differ from local because apparatus identity changed;
scientific output bytes did not.

One supplementary post-run custody assertion failed before completed direct
verification: it compared entire A/B world file sets and included Arm B's four
extra authoring/conformance receipts. This was classified
`POST_RUN_CUSTODY_FILE_SET_OVERREACH` before a bounded checker correction.
The correction requires all corresponding A/B bytes, exactly those four B-only
files, authored/trusted byte equality and successful conformance receipts, and
retains complete native/repeat/platform set equality. The first checker record
and classification addendum remain preserved. The frozen scientific evaluator,
cases, expected results, controls, and discriminator never changed.
