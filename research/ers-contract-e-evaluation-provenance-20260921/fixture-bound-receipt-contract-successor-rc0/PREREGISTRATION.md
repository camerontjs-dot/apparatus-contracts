# 05 receipt-contract preregistration

## Status

Draft pre-scientific receipt-contract reconciliation only.

Experiment:

`ERS-EVAL-TIME-PROV-20260922-05`

No receipt edits in this task. No matrix. No scientific claim.

## Base

Staged child branch from exact published PR #145 head:

`ae72c6293cb7e7833a55b181e3abc31f116a75ee`

Parent lineage `9ac48b98...` (PR #144 BLOCKED) on
`e9e364ac...` (PR #143 freeze).

## PR #131 is precedent, not authority

PR #131 is CLOSED at:

`077ccf6d386526bda258b3e90bd43e153c4c04c5`

Its contract blob at:

`research/ers-contract-e-evaluation-provenance-20260921/successor-receipt-contract-rc0/FREEZE_RECEIPT_CONTRACT.json`

is:

`92b029e6fb5e1a7c11a661911647e618594cd797`

It was written for an earlier successor (`...-20260921-03`).
The new 05 preregistration explicitly adopts the relevant PR #131
semantics while defining their current paths.

PR #131's original rule stands: do not add alias fields solely to
make old code pass.

## Exact 05 receipt contract

| Meaning | ERS receipt | Apparatus receipt |
|---|---|---|
| PR #130 scientific authority | `apparatus.scientific_preregistration.commit` | `preregistration.frozen_head` |
| PR #131 receipt-contract lineage | `apparatus.receipt_contract_preregistration.commit` | `receipt_contract_preregistration.frozen_head` |
| PR #131 contract blob | `apparatus.receipt_contract_preregistration.freeze_receipt_contract_blob` | `receipt_contract_preregistration.freeze_receipt_contract_blob` |

Pinned values:

- PR #130: `dcdd10355e2f885273d843eef6e345bafca95faa`
- PR #131 commit: `077ccf6d386526bda258b3e90bd43e153c4c04c5`
- PR #131 contract blob: `92b029e6fb5e1a7c11a661911647e618594cd797`

## No-alias rule

No alias for the obsolete ERS PR #130 path is permitted.

The preflight moves to `apparatus.scientific_preregistration.commit`;
we do not add `apparatus.preregistration_head` back just to placate
old code. That is consistent with #131's original rule against adding
aliases solely to satisfy predecessors.

## Bound 05 authorities (unchanged)

- Apparatus freeze `e9e364ac...`, source `b868e665...`/`082d0bce...`
- Runner `d0f3b699...` byte-identical
- Predecessor preflight `ddf19ab...`; path-fixed compat `30c2f47...`
- ERS receipt `cd9e0cc...`; ERS source `65f47d...`/`405bb6...`
- Transcript schema `b85b38ce...`
- Fixture `sha256:bebbb1b7973a962d59c92061e8e70283a2fb4b2b8c388705b8d80ce13000c7ad`

## After freeze (mechanical, not now)

1. ERS successor from exact #13 head `cd9e0cc...`: new receipt only.
   Implementation remains `65f47d...`, all runtime blobs unchanged.
   New receipt adds explicit PR #131 contract binding, otherwise
   preserves 05 authority.
2. Apparatus successor: runner unchanged; new preflight copy with only
   (a) ERS PR #130 read from `apparatus.scientific_preregistration.commit`
   and (b) PR #131 fields required via the paths above, beyond the
   already-authorized path fix. Then freeze a new apparatus receipt
   binding the exact new ERS receipt and exact preflight blob.

## Qualification gate (later, not now)

Run only the non-evaluating preflight. Positive exact pairing must
pass. Required negatives at least: missing ERS PR #131 binding;
missing apparatus PR #131 binding; wrong PR #131 commit; correct
commit but wrong contract blob; wrong PR #130 commit; obsolete ERS
PR #130-only path; predecessor/old receipt cross-pair; altered receipt
bytes; wrong ERS or apparatus source identity.

Hard-zero instrumentation: Contract E evaluations = 0, supervisor
launches = 0, candidate runtime imports = [], network attempts = 0.

If exact pairing passes and all negatives reject for the intended
reason, freeze and stop. Do not run PR #130's matrix in that same task.

This separation matters because the current work is still apparatus
reconciliation, not scientific evaluation.

## Stop rule

Freeze this preregistration before creating either successor receipt.
Keep Draft.
