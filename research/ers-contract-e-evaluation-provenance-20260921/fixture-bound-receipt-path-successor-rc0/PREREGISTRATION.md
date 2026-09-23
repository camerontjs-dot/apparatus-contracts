# Receipt-path-compatible preflight successor — preregistration

## Status

Draft pre-scientific receipt-path reconciliation only.

Experiment:

`ERS-EVAL-TIME-PROV-20260922-05`

The decisive matrix is not authorized by this preregistration.
No scientific claim is made.

## Why this successor exists

PR #144 is the recorded `BLOCKED` attempt, based on PR #143.

- Pre-run commit: `e9e364acfaa763abe5971ac95debc850ffcbfc69` (exact PR #143 head)
- Evidence commit: `9ac48b98f564962a9cb0e79c3202cfb0d41bf53a` (exact PR #144 head)
- Failure: `apparatus_freeze_receipt_path_not_canonical` (exit 1)

The frozen preflight at blob `ddf19ab89ebbb021891262b34664162020b8ac41`
hard-codes predecessor canonical paths:

- ERS: `research/ers-contract-e-evaluation-transcript-rc6-exec-identity-successor-20260922/FREEZE_RECEIPT.json`
- APP: `research/ers-contract-e-evaluation-provenance-20260921/successor-executable-source-identity-rc0/FREEZE_RECEIPT.json`

It therefore rejects the PR #143 freeze receipt before ERS comparison.
The exact #13 ERS receipt path is also not the path bound in the frozen source.

PR #142's scope covered the 04→05 identity change only:

1. new runner copy single literal `...-04` → `...-05`;
2. new preflight copy single literal `...-04` → `...-05`;
3. receipt-only ERS successor on unchanged source;
4. apparatus freeze binding new blobs and ERS receipt;
5. identity-only qualification.

PR #142 does not authorize receipt-path changes.
Do not treat it as authorization for receipt-path changes.

## Exact base

Base for this successor branch:

`9ac48b98f564962a9cb0e79c3202cfb0d41bf53a`

Exact PR #144 head, whose parent is exact PR #143 head
`e9e364acfaa763abe5971ac95debc850ffcbfc69`.

## Exact authorities bound by this preregistration

- Apparatus freeze: `e9e364acfaa763abe5971ac95debc850ffcbfc69`
  tree `370d2f3dd191cbbf7139d07c037744cec8baef77`
  freeze blob `6d5ffde330cda4614baa61844f1f6a83489603df`
  path `research/ers-contract-e-evaluation-provenance-20260921/fixture-bound-identity-successor-rc0/FREEZE_RECEIPT.json`
- ERS #13 receipt: `cd9e0cc725863261513cc5fd5dd3587fc6e721cf`
  tree `419a66fa2408bd06c51266e1a6820d74e249a4ce`
  blob `31d9978f21902d458d758386343e87f0be429252`
  path `research/ers-contract-e-evaluation-transcript-rc6-fixture-bound-identity-successor-20260923/FREEZE_RECEIPT.json`
- Unchanged ERS source: `65f47d029fb734be1d5d506a135cbeba813f6be8`
  tree `405bb622e0d7d0f69f3da7506a15fa0b2390e191`
- PR #130 head: `dcdd10355e2f885273d843eef6e345bafca95faa`
  question and decisive controls unchanged
- Fixture subject: `sha256:bebbb1b7973a962d59c92061e8e70283a2fb4b2b8c388705b8d80ce13000c7ad`
- Apparatus source: `b868e66523ed622dbc6615d22d5f73f81cbda94f`
  tree `082d0bce4c1be496b2590e835817e68592e2e2bc`
  runner blob `d0f3b69949bdeedea87fe0ac82b6d3407eac1a67`
  predecessor preflight blob `ddf19ab89ebbb021891262b34664162020b8ac41`

## Authorized implementation

Future implementation may add only, in new directory
`fixture-bound-receipt-path-successor-rc0/`:

1. a new apparatus receipt-preflight copy
   `receipt_preflight_fixture_bound_compat.py`,
   copied from exact blob `ddf19ab89ebbb021891262b34664162020b8ac41`
   with only the two canonical path constants changed to:
   - ERS: `research/ers-contract-e-evaluation-transcript-rc6-fixture-bound-identity-successor-20260923/FREEZE_RECEIPT.json`
   - APP: `research/ers-contract-e-evaluation-provenance-20260921/fixture-bound-identity-successor-rc0/FREEZE_RECEIPT.json`;
2. a new apparatus freeze receipt `FREEZE_RECEIPT.json`
   binding that copy plus the exact authorities above.

Original frozen files remain unchanged.
Any additional scientific-source delta is outside this preregistration.

## Explicit non-authorization

- No ERS source change.
- No runner change.
- No scientific implementation change.
- No fixture change.
- No mutation of PRs #142–#144.
- No matrix run.
- No scientific claim.

## Required qualification

After this preregistration is frozen, qualify only the
non-evaluating receipt/source preflight in fresh detached checkouts.

It must demonstrate:

1. exact path/receipt pairing accepts the authorities above;
2. predecessor APP path is rejected with
   `apparatus_freeze_receipt_path_not_canonical`;
3. predecessor ERS path mismatch is rejected;
4. swapped receipts are rejected;
5. mismatched commit/tree/blob identities are rejected;
6. zero runner imports;
7. zero supervisor launches;
8. zero Contract E evaluations;
9. zero network access;
10. zero sandbox creation;
11. zero matrix controls run.

Do not import or execute scientific candidate code.
Do not launch supervisors or Contract E.
Do not create sandboxes or run matrix controls.

## Stop rule

If any gate fails, record `BLOCKED` and stop.
Do not patch in place or retry toward a pass.

## Next boundary

Only after this receipt-path successor is frozen and qualified may the state become:

`RECEIPT_PATH_COMPAT_PREFLIGHT_QUALIFIED`

That state still does not run or authorize the PR #130 decisive matrix.
Keep Draft.
