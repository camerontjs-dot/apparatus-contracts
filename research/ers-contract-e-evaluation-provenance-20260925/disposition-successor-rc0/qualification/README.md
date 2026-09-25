# ERS 05 pre-matrix qualification gate

## Purpose and authority

This gate qualifies deterministic setup and filesystem containment before the
first Contract E evaluation, supervisor launch, or scientific shadow operation.
It does not execute the PR #130 scientific matrix or alter its hypothesis,
cases, mutations, transcript contract, or expected outcomes. The immutable
scientific authority remains PR #130 at `dcdd10355e2f885273d843eef6e345bafca95faa`.

## Procedure

`run_strengthened_gate.sh` launches the complete gate under the checked-in
macOS deny-default profile. The profile allows file writes only below the two
caller-designated qualification output and temporary directories. It explicitly
denies MainFrame, apparatus and predecessor checkouts, control worktrees,
frozen checkouts, fixtures, runtime, sandbox, and the protected canary. Network
access is denied.

Before any bootstrap case, the gate attempts writes to an empty protected canary
through ordinary `open(..., "wb")` and `Path.write_bytes`. Both must raise
`PermissionError`; the directory snapshot must remain identical. Python
instrumentation inside the bootstrap is supplemental. A before/after tree
snapshot and MainFrame Git state check must also match.

The gate re-verifies the pinned runtime, installs a fresh copy offline from the
frozen lock and wheelhouse, and runs the dependency smoke checks. It then
qualifies six inputs independently: frozen PR #148, frozen PR #149, this
successor, wrong-root control, wrong-disposition control, and wrong-receipt-path
control. Each candidate runner receives the actual scientific CLI flag shape
and stops at the source line immediately before the first hold-case/scientific
operation. Every scientific counter must remain zero.

## Inputs and outputs

The shell launcher requires exact checkout, fixture, runtime, sandbox, output,
temporary, and canary paths through `ERS05_*` variables. Its profile parameters
bind those paths at launch. `SOURCE_DELTA.json`, `RUNTIME_REUSE.json`, per-case
bootstrap receipts, snapshots, and `QUALIFICATION.json` are written only below
the designated output directory. The private issuer key is read from the
configured macOS Keychain, materialized temporarily with mode `0600`, and
removed before each case report is returned.

## Verification and stop rule

A PASS requires the source-delta proof, runtime re-verification, both denied
canary writes, unchanged protected snapshots, all six expected discrimination
outcomes, a reached pre-scientific boundary for the successor, and zero
scientific or protected-write counters. Any missing identity, incidental
control failure, containment miss, or snapshot difference is preserved as
INCONCLUSIVE before freeze. No matrix command is part of this gate.

## Artifact profile

- `structural_type`: deterministic-operation
- `lifecycle_scope`: workbench
- `owner_surface`: this successor's `qualification/` directory
- `authority`: qualification only; PR #130 remains the scientific authority
- `privacy`: public-safe receipts; runtime output and key material remain local
- `volatility`: active until freeze, then immutable
- `source_of_truth`: true for this gate's qualification outcome
- `update_rule`: append-only after preregistration; no gate changes after freeze
- `verification`: source-delta proof, runtime receipt, canary receipt, bootstrap receipts, protected snapshots
- `related_surfaces`: `PREREGISTRATION.md`, `decision-reconciliation/RECONCILIATION.json`, PR #148, PR #149, PR #130
- `do_not_use_for`: Contract E scientific findings, promotion, release, or merge authorization
