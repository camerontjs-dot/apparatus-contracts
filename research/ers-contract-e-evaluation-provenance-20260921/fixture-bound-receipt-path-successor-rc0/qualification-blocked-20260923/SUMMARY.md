# Receipt-path compat qualification — BLOCKED

Positive exact-pairing gate failed. No patch, no retry, no matrix.

- Branch base: `9ac48b98f564962a9cb0e79c3202cfb0d41bf53a` (PR #144 head)
- Prereg freeze: `a5fc406eb9072c0ca3af56cb1884514bd926abe3`
- Compat source commit: `91057d97ffb0586449e4f8ba07408abb0f41ea9d`
- Compat blob: `30c2f4767215e504031f1953cb490bb51c481815`
- Predecessor preflight blob: `ddf19ab89ebbb021891262b34664162020b8ac41`
- Apparatus freeze: `e9e364acfaa763abe5971ac95debc850ffcbfc69`
- Apparatus source: `b868e66523ed622dbc6615d22d5f73f81cbda94f`
- ERS receipt: `cd9e0cc725863261513cc5fd5dd3587fc6e721cf`
- ERS source: `65f47d029fb734be1d5d506a135cbeba813f6be8`
- PR130 head: `dcdd10355e2f885273d843eef6e345bafca95faa`
- Fixture subject: `sha256:bebbb1b7973a962d59c92061e8e70283a2fb4b2b8c388705b8d80ce13000c7ad`

## Positive (exact pairing, compat paths, single-root source checkout)

`FAIL` with 4 check failures:

- `ers_pr130_head` (actual null)
- `matching_pr130_head`
- `ers_pr131_head` (actual null)
- `apparatus_pr131_head` (actual null)

The compat copy fixed only the two canonical paths, as authorized.
The exact receipts do not contain the PR131 receipt-contract fields
expected by the frozen preflight lineage, and the ERS receipt does not
expose `apparatus.preregistration_head` at the expected dotted path.
Schema reconciliation is outside this path-only preregistration.
No patch was applied.

See `RECEIPT_SOURCE_PREFLIGHT.json`.

## Negatives (all correctly rejected, exit 1)

- `N1_predecessor_app_path`: old preflight vs new receipts → `apparatus_freeze_receipt_path_not_canonical` (reproduces PR #144 BLOCKED)
- `N2_predecessor_ers_freeze`: compat vs old ERS freeze `64ed29cc...` → `git_object_check_failed` (new ERS path absent)
- `N3_swapped_ers_freeze`: ERS freeze = apparatus commit `e9e364...` → `git_object_check_failed` (rejected)
- `N4_wrong_app_source`: apparatus source `f14fbcc...` → `git_object_check_failed` (rejected)
- `N5_wrong_ers_source`: ERS source `64ed29cc...` → check failure (rejected)
- `N6b_altered_blob`: altered apparatus receipt bytes → check failure (rejected)

See `NEGATIVES.json`.

## Controls preserved

- Runner imports: 0
- Supervisor launches: 0
- Contract E evaluations: 0
- Network attempts: 0
- Sandbox creation: none
- Matrix controls run: 0
- Scientific claim: none

Instrumentation in `RECEIPT_SOURCE_PREFLIGHT.json` records
`contract_e_evaluation_calls: 0`,
`supervisor_process_launches: 0`,
`candidate_runtime_imports: []`,
`network_attempts: 0`.

Fresh detached checkouts were used for apparatus source
(`b868e66523ed622dbc6615d22d5f73f81cbda94f`),
apparatus freeze (`e9e364acfaa763abe5971ac95debc850ffcbfc69`),
and ERS freeze (`cd9e0cc725863261513cc5fd5dd3587fc6e721cf`).
No matrix runner was invoked.

## Disposition

`BLOCKED`

Do not patch in place or retry toward a pass.
Keep Draft. Do not run the matrix.
