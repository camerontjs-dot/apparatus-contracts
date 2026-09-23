# ERS-EVAL-TIME-PROV-20260922-05 receipt/preflight qualification

## Disposition

**PASS — bounded, non-evaluating receipt/preflight qualification only.** This establishes internal consistency of the frozen 05 receipt authority contract. It does not establish evaluation-time provenance as a scientific result. PR #130's matrix remains out of scope and has not run.

## Frozen identities

| Item | Identity |
|---|---|
| Apparatus base (PR #145 head) | commit `ae72c6293cb7e7833a55b181e3abc31f116a75ee` |
| 05 preregistration freeze | commit `48f88111a39402f5ae6f0565e39b2482e6e58fe0`, tree `ff1220fe1988bb1803ce6aad21c5c76f69d53b4d`; prereg blob `2b9a4f07d5527e30beb60f3d0c98507e060a804f`, authority blob `9e55f84820a98532cb854cee804c8428aee6e80c` |
| ERS base (PR #13 head) | commit `cd9e0cc725863261513cc5fd5dd3587fc6e721cf` |
| ERS receipt successor | commit `aa214666c9a68871c0d878a70b7f3833d49dbe9b`, tree `1ad0bb7df9a6d836a5fdca7157173c60429619a3`, receipt blob `50c9493d3f0584de74399118da01b7b603c813e0` |
| Apparatus preflight successor | commit `9f75ee325f31971ca8f0d4e1ddf9a7c04c98e940`, tree `53e4d53f5f62112d28d080da0a732475c3c51df5`, blob `3314048d5904fa59fdb00e67a1ee108c167097aa` |
| Apparatus receipt successor | commit `af3385cab18789450d1e02c00a0e07a84ffcfcc9`, tree `b5c28580b14d9fb96a99a3ce3af1068e34858da4`, receipt blob `bc7d3938be9146dd6455ab5f9fda896f22a70274` |
| ERS implementation | source `65f47d029fb734be1d5d506a135cbeba813f6be8`, tree `405bb622e0d7d0f69f3da7506a15fa0b2390e191`; runtime blobs match the original receipt |
| Apparatus source and runner | source `b868e66523ed622dbc6615d22d5f73f81cbda94f`, tree `082d0bce4c1be496b2590e835817e68592e2e2bc`; runner blob `d0f3b69949bdeedea87fe0ac82b6d3407eac1a67` |
| PR #130 scientific authority | `dcdd10355e2f885273d843eef6e345bafca95faa` |
| PR #131 contract lineage and artifact | commit `077ccf6d386526bda258b3e90bd43e153c4c04c5`; blob `92b029e6fb5e1a7c11a661911647e618594cd797` |

## Qualification results

- Positive: **PASS**, exact fresh detached receipt/source pairing, 86 recorded checks passed.
- Authority negative mappings: **7/7 PASS**. Missing ERS #131 binding, missing apparatus #131 binding, wrong #131 commit, right commit/wrong contract blob, wrong #130 commit, obsolete ERS alias without canonical path, and the exact PR #13 old ERS receipt cross-paired with the new apparatus receipt all rejected at the expected authority checks. See `NEGATIVE_AUTHORITY_MAPPINGS.json` for every failed check per case.
- Altered receipt bytes: **PASS as a negative**; rejected only at `apparatus_receipt_bytes_match_frozen_blob` in the corrected run.
- Wrong ERS source identity (`aa214666...` passed as the source): **PASS as a negative**; rejected at receipt/CLI source identity and source tree checks.
- Wrong apparatus source identity (`ae72c629...` passed as the source): **PASS as a negative**; rejected at receipt/CLI source identity and source tree checks.
- Old ERS receipt full-preflight attempt: **rejected** because the exact predecessor commit has no file at the new successor receipt path. The pure authority check separately exercised the exact old receipt bytes against the new apparatus receipt and reported the #131 and successor-preregistration mismatches.

## Instrumentation

Positive preflight: `contract_e_evaluation_calls: 0`, `supervisor_process_launches: 0`, `candidate_runtime_imports: []`, `network_attempts: 0`; all 36 subprocesses were Git. The pure authority negative checks used zero subprocesses. Every full-preflight negative also reported zero evaluations, supervisor launches, candidate imports, and network attempts.

## Preserved superseded attempt

The first altered-byte CLI attempt used the clean-checkout preflight executable while pointing `--apparatus-root` at the altered checkout. It rejected the changed receipt and also reported `executing_preflight_path`. That exact output is preserved as `FAIL_ALTERED_APP_RECEIPT.json`. The exact altered input is preserved as base64 in `ALTERED_APP_RECEIPT.bytes.b64` (179 bytes, SHA-256 `81719df8efc9fcd20ac85f4ba0e993dfc8a7290be932c13db4571102c6b7b5d5`, Git blob `171cba206a721d51da47e0e9eec88ca2cff04b4c`). The corrected detached run invoked the byte-identical preflight from the altered checkout and failed only the intended frozen-receipt-byte check. No frozen implementation was patched after this attempt; only the negative invocation was corrected, and the altered receipt remains isolated and preserved as a negative input.

## Changed surfaces

- Apparatus: one new preregistration, one new preflight, one new receipt, and this qualification evidence directory.
- ERS: one new receipt file only.
- Unchanged: PR #130 controls, Contract E/D, Decision Engine, CAL, Contract C consumer, ERS runtime and transcript schema, issuer semantics, scientific runner, fixture bytes/subject, and expected scientific outcomes.
- No mutation to PRs #143, #144, #145, #13, #130, or #131.

## Next authorized step

Reconcile/publish these two successors as Draft research lineage and attach the qualification evidence. Stop before the PR #130 scientific matrix; that matrix requires separate authorization.
