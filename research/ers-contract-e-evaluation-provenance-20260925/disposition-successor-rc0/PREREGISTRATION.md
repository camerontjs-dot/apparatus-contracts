# ERS 05 evaluation-time provenance: disposition expectation successor

Status: **preregistered before runner edit**  
Experiment: `ERS-EVAL-TIME-PROV-20260922-05` (unchanged hypothesis and matrix)  
Successor: `ERS-EVAL-TIME-PROV-20260922-05-DISPOSITION-20260925`

## Predecessor record

This successor starts exactly at apparatus-contracts PR #149 head
`4bd5b030726ed064d410cb8c99e79c23a0426c8a` (tree
`6aff39c21f777912472ae62324b94619ef4956de`), based on PR #148 head
`b673b2b06804e94042ad35d4621f4a4ca5ee4851`.

Preserve all predecessor objects and outcomes:

1. The earlier 85/86 preflight failure remains at
   `$PRESERVED_RUNTIME_QUAL_ROOT/final-qualification/preflight.json`.
2. PR #148 remains an OPEN Draft and retains the first matrix attempt:
   `INCONCLUSIVE` before any matrix case at the repository-root/path lookup;
   `matrix_progress` is empty.
3. PR #149 remains an OPEN Draft and was not frozen. Its full bootstrap ended
   `INCONCLUSIVE` at `pipe01_native_ers_decision_changed`; no PR #130 scientific
   result was observed.
4. Neither failed scientific attempt invoked Contract E. The PR #149 bootstrap
   counters also record zero Contract E evaluations, supervisor launches,
   scientific PIPE cases, scientific mutations, sandbox creations, and network
   attempts.
5. No predecessor branch, commit, receipt, deviation, or qualification artifact
   will be amended, rewritten, force-pushed, or erased.

The retained root correction is `ROOT = HERE.parents[2]`. PR #148's receipt-path
and `apparatus.scientific_preregistration.commit` corrections are also retained.

## Frozen PIPE01 decision reconciliation

The decision was reconstructed from the pinned Decision source and frozen PIPE01
inputs before this preregistration and before any runner edit. The companion
`decision-reconciliation/RECONCILIATION.json` records the exact commits, trees,
blobs, input hashes, JSON pointers, and the canonical decision bytes.

The reconstructed decision has semantic identity
`decision:sha256:3427c5cb6692bf7358c13e47628ef7a91a0c53e78affc58f2ae60173daffcc15`.
Its RFC 8785 canonical bytes are 766 bytes with digest
`sha256:7ddea63c77b2cf1223489129b64aef6ecc71ed31238b805689abb2f68f7a03eb`.
The exact object has `evaluation.disposition = "clear"`; its
`effect.type = "epistemic_audit.stage_pending_review"`.

The frozen render-bound receipt for that same identity records parent conclusion
`supported`, ERS disposition `clear`, `ers_shadow_ready=true`, and
`ers_execution_occurred=false`. The bound policy receipt names the downstream
effect as `epistemic_audit.stage_pending_review@1`. PIPE02 and PIPE03 remain
`hold` and stop at `decision_not_candidate:hold` with zero Contract E
evaluation calls.

**Conclusion:** `pending_review` is not an evaluation disposition in the
authoritative PIPE01 decision. The old runner asserted the downstream staging
effect as the evaluation disposition. The only newly authorized runner semantic
change is the demonstrated expectation correction from `"pending_review"` to
`"clear"`.

## Unchanged scientific authority

Live GitHub authority was checked before this branch was created:

- Apparatus PR #130 remains OPEN Draft at
  `dcdd10355e2f885273d843eef6e345bafca95faa` (tree and preregistration blob are
  recorded in the reconciliation receipt).
- PR #146 remains OPEN Draft at `cd465d798220daa3f45261d3e6f385cf67224a46`.
- PR #147 remains OPEN Draft at `c054d2fb0822e61833cb9e8a5acb7072dbce6531`,
  based on #146.
- PR #131 remains CLOSED Draft at
  `077ccf6d386526bda258b3e90bd43e153c4c04c5`; it remains the immutable
  receipt-contract authority referenced by the frozen lineage.
- ERS PR #14 remains OPEN Draft at
  `aa214666c9a68871c0d878a70b7f3833d49dbe9b`.

The PR #130 hypothesis, matrix cases, scientific mutations, expected outcomes,
transcript schema, verifier, supervisor API, and ERS/Contract E semantics remain
unchanged. No decisive PR #130 scientific result has been observed.

## Authorized scope

1. Retain the PR #148 receipt-path and preregistration-commit corrections and
   the PR #149 repository-root correction.
2. Change only the PIPE01 evaluation-disposition expectation established above.
3. Change qualification infrastructure only to strengthen pre-scientific
   containment and discrimination.
4. Do not alter fixtures, scientific matrix cases, scientific mutations,
   expected outcomes, transcript schema/signing, verifier, supervisor, or ERS /
   Contract E behavior.
5. Use the unchanged PR #148 runtime artifacts only if all pinned identities
   still match. Do not rebuild dependencies or change versions.

## Strengthened qualification gate

Run the complete bootstrap with the unchanged scientific CLI argument shape. It
must verify all deterministic setup through an explicit stop immediately before
the first Contract E, supervisor, or scientific shadow operation, including
repository/path and committed-receipt resolution, Git ancestry/object checks,
PR #130/#131 authority, CAL v3, ERS/apparatus freezes, preflight receipts,
Contract E/D/Decision/consumer roots, frozen fixture identities, exact PIPE01
decision bytes/identity and clear disposition, PIPE02/03 holds, render-bound
module setup, execution-intent construction, issuer/public-key checks,
transcript schema, sandbox initial state, and all remaining setup.

The bootstrap must execute under an OS-level deny-write profile. Writes are
allowed only inside declared qualification output/temp paths; MainFrame,
repository checkouts, frozen fixtures, and the scientific sandbox are denied.
Python audit/monkeypatch instrumentation is supplemental. A controlled protected
canary outside the allowlist must reject writes through both ordinary
`open(..., "wb")` and `Path.write_bytes(...)`. Protected-tree snapshots must
match before and after.

Discrimination must independently show:

- frozen PR #148 runner: repository-root/path-resolution defect;
- frozen PR #149 runner: PIPE01 disposition expectation defect;
- this successor: explicit pre-scientific boundary;
- wrong-root control: repository-root/path rejection;
- wrong-disposition control: rejection at the PIPE01 disposition check;
- wrong-receipt-path control: committed receipt/repository-relative path rejection.

Every bootstrap case must have zero Contract E evaluations, supervisor launches,
scientific PIPE executions, scientific mutations, scientific sandbox mutations,
provenance captures, unauthorized network attempts, and protected filesystem
mutations. Any incidental failure, missing exact authority, identity ambiguity,
or failed containment control stops qualification before freeze.

## Freeze and matrix boundary

Only a complete strengthened qualification PASS authorizes a new freeze. The
freeze receipt must bind the preregistration, source commit/tree/blob, cumulative
runner lineage/delta, bootstrap gate, OS profile and hash, canary receipt,
runtime, all authority and fixture identities, issuer key, complete argument
shape, protected-tree snapshots, and the absence of a decisive PR #130 result
before freeze.

After freeze, execute the exact unchanged PR #130 matrix only if every gate has
passed. Do not repair or retry after decisive exposure. If any prerequisite or
qualification fails before freeze, preserve the result and stop. No merge,
promotion, release, or tag is authorized.

## Artifact profile

- `structural_type`: project-plan
- `lifecycle_scope`: workbench
- `owner_surface`: `research/ers-contract-e-evaluation-provenance-20260925/disposition-successor-rc0/`
- `authority`: this preregistration controls only this successor's qualification and stop rules; frozen scientific authority remains PR #130
- `privacy`: public-safe
- `volatility`: active until freeze; immutable after its preregistration commit
- `source_of_truth`: true for the successor's pre-execution commitments
- `update_rule`: append-only; post-preregistration deviations are separate artifacts
- `verification`: exact Git commit/tree/blob checks, source-delta proof, protected-write negative controls, bootstrap receipts, freeze receipt
- `related_surfaces`: PR #148, PR #149, PR #130, PR #131, PR #146, PR #147, ERS PR #14, `decision-reconciliation/RECONCILIATION.json`
- `do_not_use_for`: a PR #130 scientific result, promotion, release, or merge authorization
