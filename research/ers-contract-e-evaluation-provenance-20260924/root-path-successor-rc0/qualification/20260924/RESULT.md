# ERS 05 root-path successor qualification result

Date: 2026-09-24

Disposition: **INCONCLUSIVE before the scientific boundary**. The candidate was not frozen. The PR #130 matrix was not run.

## Candidate lineage

- Successor branch: `research/ers-contract-e-evaluation-provenance-05-root-path-successor-20260924`
- Exact base: PR #148 head `b673b2b06804e94042ad35d4621f4a4ca5ee4851` (tree `97e832138b7f9c955bc1eb1a940dbb937a230142`)
- Preregistration commit: `c7e893580c053b865e7484b68ec72e9cb200d6ef`; tree `dac59e5b62f7bf8ab6fdbd5ad7f616e464f7ce2b`; preregistration blob `ae1f65ad608aaa47d309ef8d078dbb3cc3ad1784`
- Root correction commit: `f491d3b0d37571a26fa862d9b61054a3f498ca0e`; tree `c6f9aa1fde8939d7c4f6dcd64da9c555ee2cfbb6`; runner blob `6c20a20831a34cf83eb38f0b86ae6965a15a7990`
- Freeze commit/tree: **not created**; the strengthened qualification did not pass.

## Root defect and correction

The frozen PR #148 runner assigns `ROOT = HERE.parents[1]`, which resolves to the `research/` directory. Converting a receipt path relative to that directory drops the leading `research/`; the resulting `HEAD:<path>` lookup fails even though Git commands from that directory still discover the repository root. The preserved matrix failure has empty progress and stopped at this lookup.

The diagnosis was committed before source editing. The only runner change is line 29, `HERE.parents[1]` to `HERE.parents[2]`. The mechanical proof confirms the one-line delta, AST equivalence after normalizing the index, and unchanged function/class bodies. The new root resolves to the checkout root and makes the committed receipt lookup succeed.

## Strengthened bootstrap result

The gate used the full scientific CLI argument shape and the actual pinned PR #148/PR #14 inputs. It passed repository-root and committed-receipt resolution, then stopped in the frozen pre-matrix decision setup with `pipe01_native_ers_decision_changed`. The intended pre-scientific stop boundary was not reached.

The discrimination receipt records:

| Case | Observed | Expected | Match |
|---|---|---|---|
| Frozen PR #148 predecessor | `repository_root_path_defect` | same | yes |
| Root-corrected successor | `incidental_failure` | `bootstrap_pass` | no |
| Intentionally wrong root | `repository_root_path_defect` | same | yes |
| Receipt outside repository | `receipt_path_outside_repository` | same | yes |

At the successor failure: Contract E evaluations `0`; supervisor launches `0`; scientific PIPE cases `0`; scientific mutations `0`; scientific sandbox creations `0`; network attempts `0`; MainFrame write attempts `0`; sandbox remained empty; private key material was not retained. A Node process performed the existing deterministic decision setup. The runner failed before the gate boundary and before any PR #130 matrix case.

## Qualification guard review note

The bootstrap gate stopped before its intended boundary. Its MainFrame write counter patches `builtins.open`, while the runner uses `pathlib.Path.write_bytes` for output artifacts; that wrapper alone would not intercept every possible MainFrame write API. No such MainFrame write path ran before the observed failure, and the registered apparatus-contracts workbench remained clean on post-run inspection. The zero counter is an observation for this run, not a general filesystem-write barrier. A later qualification must close this instrumentation gap before relying on that guard.

## Conflicting frozen expectation

The pinned PR #148 composition receipt records PIPE01 with parent conclusion `supported`, ERS disposition `clear`, and decision identity `decision:sha256:3427c5cb6692bf7358c13e47628ef7a91a0c53e78affc58f2ae60173daffcc15`. The frozen 05 runner pins that same decision identity, then asserts that the same decision's `evaluation.disposition` is `pending_review`. The gate passed the identity assertion and failed on that disposition assertion.

Observed evidence therefore conflicts within the frozen apparatus lineage. An inference is that the runner may be treating the `stage_pending_review` effect as the evaluation disposition; the existing receipt and exact pinned decision output do not support that interpretation. This needs reconciliation before any further source change can be preregistered. No runner change was made after the failed gate.

## Runtime and authority evidence

The PR #148 runtime qualification remains a separate PASS, with 86/86 preflight checks and 11/11 negative controls. Its exact CPython, uv, lock, and wheelhouse identities are recorded in `RUNTIME_REUSE.json`; the lock and wheelhouse hashes were rechecked, all 10 wheel checksums verified, and `uv pip check` reported 10 compatible packages. Dependency smoke covered installed versions, RFC 8785, JSON Schema, and Ed25519 positive/negative checks with zero network calls. These runtime checks do not turn the failed bootstrap into a pass.

Live GitHub identities still match the preregistration: PR #148 remains open Draft at `b673b2b…`; PR #130 remains open Draft at `dcdd10355e2f885273d843eef6e345bafca95faa`; PRs #146 and #147 remain open Draft at `cd465d7…` and `c054d2f…`; PR #131 remains closed Draft at `077ccf6…`; ERS PR #14 remains open Draft at `aa214666c9a68871c0d878a70b7f3833d49dbe9b`.

## Stop disposition

This result is **not** a scientific falsification or support for the PR #130 hypothesis. No successor freeze was made and no PR #130 scientific result was observed. Preserve the earlier PR #148 matrix attempt as `INCONCLUSIVE`, this successor bootstrap as `INCONCLUSIVE`, and all qualification receipts unchanged. The next gate is to reconcile the pinned PIPE01 disposition expectation against the frozen composition receipt before authorizing another candidate edit.

## Evidence files

- `SOURCE_DELTA.json`
- `PREDECESSOR_BOOTSTRAP.json`
- `SUCCESSOR_BOOTSTRAP.json`
- `SUCCESSOR_FAILURE.json` and `SUCCESSOR_RUNNING.json`
- `BOOTSTRAP_DISCRIMINATION.json`
- `RUNTIME_REUSE.json`
- `SHA256SUMS.txt`

## Leak-scan provenance

The scoped `.leak-scan-allow` entries cover synthetic CI fixture paths and workstation/runtime paths already present in preserved PR #148 or earlier qualification evidence. No path matching those rules was added by this successor diff. These entries preserve immutable evidence and do not permit matches in other files.
