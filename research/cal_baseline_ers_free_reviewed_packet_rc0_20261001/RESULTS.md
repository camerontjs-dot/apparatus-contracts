---
title: "ERS-free real-packet baseline RC0: bounded execution result"
domain: ai-systems
type: note
status: stable
source: RUN-RECEIPT.json
tags: [cal-pipeline, research-infrastructure, bounded-baseline]
links: [PREREGISTRATION.md, RUN-RECEIPT.json, PRESSURE-RECEIPT.PUBLIC.json]
---

# ERS-free real-packet baseline RC0

`SUPPORTED_FOR_BOUNDED_ERS_FREE_REAL_PACKET_BASELINE`

One frozen real-source packet completed the exact Gate → A2 → EB → B1.2 → CAL → parent-bound C → independent C consumer → Decision → D1 consumer path. Both full runs produced CAL `not_checkable`, Decision `hold`, and D consumer `hold`. This is the preregistered bounded pipeline disposition; it does not turn those semantic observations into factual support.

## Authority and input

Execution used Apparatus [Draft PR #153](https://github.com/camerontjs-dot/apparatus-contracts/pull/153) at `1cc9efc52fa591846af473ee165a643f9ac41c22`, tree `18a3f38c70b61456bedeb929440bbb688985556a`. [PREREGISTRATION.md](PREREGISTRATION.md) remains unchanged: SHA-256 `4654da884ac19a7c083e0a1b698d9e4d01f9b56957452770fb20dfffedb8d5e6`. This evidence commit appends records after execution; it is not a new scientific subject.

The local search found no eligible existing reviewed packet in the inspected scopes. The operator-authorized separate predecessor preparation selected one manually authored factual conjunction from the real [NASA metric factsheet](https://nssdc.gsfc.nasa.gov/planetary/factsheet/) before outcomes, ran current Gate, authored two targets, obtained separate semantic-fidelity review, and froze the packet before this fresh baseline attempt. The selected source, root, and target meanings were not rerolled.

| Object | SHA-256 |
|---|---|
| Frozen Gate input packet | `8abd8b98eeec1bdc6cb9f1f0be0870fbf9ecdcfc6c1c3b8de76c2267636a44e2` |
| Reviewed Contract A file | `8a4a42b57020d710b0e68a57fac5d31d8a977e75bde2c7d535a656bacefabb41` |
| Contract A handoff | `b59ba3b35d2b1d8b0378ac277703cd4a8867ec1e88b8ea34be577df0c3eeb843` |
| Target-review manifest | `df4eb5b84fb9b1f65a9a7f8245397d85a1b2aff6b19c3f5a456d83a6c5fc0903` |
| Target 1 | `416811675261a1f12e2c4c5ebd3d8fdaf769def57a3fea6fe0ca5a26b270a4c4` |
| Target 2 | `22797d998748039a7aa582c997b6727c1d2f11c01a009a82cf508104cd051aaf` |

The exact author and reviewer identities are retained locally; [PACKET-REVIEW.PUBLIC.json](PACKET-REVIEW.PUBLIC.json) publishes their distinct identity digests and review-artifact hashes. The reviewer inherited no parent conversation and froze source-first judgment before reading the targets. Generic startup memory was injected and is disclosed; this is not a claim of a memory-free context. The reviewer retrieved the table's linked property-definition note for fidelity review only. Those extra bytes were not added to Contract A or EB.

All subjects and required helper blobs appear in [SUBJECTS.ERS-FREE.json](SUBJECTS.ERS-FREE.json) and [PRESSURE-RECEIPT.PUBLIC.json](PRESSURE-RECEIPT.PUBLIC.json). The unchanged A→D runner and target verifier came from PR #152 at `6c08fcafecf4cfca553500a3b0918292e447391c`, blobs `f5b06c6711e7799823155e5f8d95597940950b92` and `32b644de87fc23ac721a740a2db7ef34c56b4992`. ERS was excluded from the downstream subject projection.

## Observed stages

| Stage | Observation |
|---|---|
| Ownership | No competing baseline executor observed among 457 Conduit tasks, the recent app task listing, or matching local processes; one fresh owner/output receipt. No machine-global exclusivity claim. |
| Exact preflight | 20/20 live GitHub checks before execution and 20/20 after; 11/11 downstream checkouts, 21/21 pinned workfiles, 3/3 PR #152 helper blobs, 8/8 Gate dependency blobs; released A2/B1.2/D1 verified. |
| Gate #54 → released A2 | 2/2 replays and 2/2 A2 validations passed. Both A files and handoff identities equal each other and the reviewed predecessor bytes. |
| Reviewed targets | Exact verifier printed `TARGET_REVIEW_VERIFIED`; 2/2 children have independently attested fidelity, distinct author/reviewer identities, exact target/text bindings, and active `strict_comparison` family. |
| EB #120 → B1.2 | Both runs completed. Each produced 20 candidate relationships, 6 retained, 0 accepted. No admission override was supplied. |
| CAL #183 → parent-bound C #121 | Both runs completed; both children and parent concluded `not_checkable`; automatic action allowed `false`. |
| Frozen independent C consumer | Invoked by Decision in both runs and directly rechecked twice against the preserved bytes; all accepted the parent-bound artifact. |
| Decision #86 → D1 | Both evaluations completed with `hold`; canonical D1 artifacts emitted. |
| Released D1 consumer | Both original consumes and both direct rechecks returned `hold`; no effect was performed. |
| Deterministic replay | 7/7 required identity comparisons passed; pressure comparison additionally found 41/41 emitted files byte-identical, with equal file sets. |
| Source substitution | Original control and one bounded pressure replay rejected an unresealed source-content mutation before any EB artifact. The observed reason was `$.sources[0].content_sha256 mismatch`. |
| Frozen-state pressure | 19/19 packet/review/source files unchanged; 69/69 installed CAL Python files still byte-equal to pinned source; all subject heads/workfiles fixed. |

The unmodified primary [RUN-RECEIPT.json](RUN-RECEIPT.json), [GATE-REPLAY-RECEIPT.json](GATE-REPLAY-RECEIPT.json), and [PRESSURE-RECEIPT.PUBLIC.json](PRESSURE-RECEIPT.PUBLIC.json) bind these observations. [COMMANDS.PUBLIC.json](COMMANDS.PUBLIC.json) preserves correspondence to the actual local command receipts while redacting the local output root. No separate unit-suite count is claimed.

## Failures and deviations

Two material failed commands preceded the baseline. Both first failures remain preserved.

The predecessor Gate preparation failed on unsupported locator enum `url`. A separately identified preparation successor corrected only the carrier enum to `web_uri`; the selected root and raw/working source bytes stayed fixed. No CAL or Decision result had been exposed.

The exact subject verifier then reported Gate's checkout dirty because the declared fetch script created unignored predecessor dependencies. The repair excluded only the eight individually verified fetched files locally. Tracked source and versioned ignore rules stayed fixed; the retry passed.

The first candidate descriptor's non-exact tree description remains preserved beside a separate exact-tree correction. A pressure inventory also recovered a `RUN-1`/`RUN1` path assumption before any comparison receipt was published. There were zero failed baseline commands and no post-result scientific repair. [FAILURES-DEVIATIONS.PUBLIC.json](FAILURES-DEVIATIONS.PUBLIC.json) binds these records.

Publication hygiene passed the current working-tree path/credential checks. The full repository-history scan exited 1 on preexisting historical matches, then encountered a broken pipe while displaying them; no full historical finding count or clean-history claim is made. The scan occurred before this evidence commit. Its original stdout/stderr remain hash-bound in the failure record. History was not rewritten; the evidence delta is checked by the active pre-commit guard.

## Inference and competing explanations

The exact frozen packet traversed the complete controlled-local path reproducibly and rejected source substitution at the input-integrity boundary. That supports the bounded disposition above.

A missing dependency or bad invocation could have explained a generic nonzero substitution exit. The pressure replay preserved the same mutated bytes and reproduced the original stderr identity, explicitly identifying source-content hash mismatch with no EB artifacts. Positive EB runs and direct C/D consumer rechecks also completed.

Zero accepted EB relationships explain the downstream `not_checkable/hold` path. This run does not exercise positive factual-support discrimination or qualify numeric-table interpretation. No admission was invented to obtain a preferred outcome.

## Nonclaims and handoff

Authorization performed: `false`. Operational execution performed: `false`. Contract E invoked: `false`. ERS invoked/written: `false`. No merge, release, promotion, or retag occurred.

This establishes one bounded real-source packet through the exact pinned local subjects. It does not establish universal CAL semantics, source authority, corpus completeness, natural claim discovery, production readiness, Contract E readiness, or equivalence to an ERS-inclusive run. Separate target-fidelity review does not establish memory-free reviewer context or engine correctness.

The full private packet, raw sources, targets, review record, command logs, intermediate artifacts, first failures, and terminal receipt remain retained locally. Public records contain content identities and observations; they do not publish private claim/source/target bytes. No remaining operator decision is required to finish this baseline.
