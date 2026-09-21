# ERS render-bound shadow composition successor

Date: 2026-09-21

This is a successor research candidate for apparatus-contracts PR #120's
`FALSIFIED_EXECUTION_PAYLOAD_UNBOUND` result. It is evaluated from the exact
frozen ERS successor before cross-repository composition.

## Subjects

- apparatus-contracts PR #127 base: `bb8ff5c5d9fd3e221b0dea76e4748fe85be30796`
- Decision successor: `816374379ba7eb23f5bfdadaf203b7e287c052db`
- CAL Pipeline v3: `ffc43d4e89f5b1f7748e9cde0fa1efc7db47b463`
- Contract D: `298a1a0f7b7b6d7712e11200d04faec3e1ca169b`
- Contract E profile: `b153dcc4434cbe8a98616a9e410c6125378144c7`
- frozen ERS RC3 preserved: `319e325cdf678673fae645a70e3e34afb7dddef0`
- ERS successor: frozen locally before this composition run

## Hypothesis

An immutable, canonically identified render packet containing every live
promoter dependency, explicit render date, and deterministic collection order
can be rendered to one exact terminal-newline payload. Binding the packet and
payload identities as additional `input_identities` in the existing generic
`execution-intent-candidate-v1` should make the existing whole-intent Contract
E authorization specific to those exact bytes.

## Required controls

The harness must independently recompute packet and payload identities, use
the exact PIPE01 claim-content identity
`sha256:fe9a393b0c31f7e2f200cbefc08d9293e364f8a0810865a73003ec3502c387d0`,
and use disposable source rows only. It must exercise deterministic replay,
row reordering, render-relevant mutation, exact Contract E composition,
write-free point-of-use acceptance, missing/different payload rejection,
Decision/executable/pre-state/target/stale-authority rejection, PIPE02/03
stop-before-E, supported-claim compatibility, released Contract D rejection,
unchanged frozen upstream bytes, and an empty sandbox before and after.

No executor, file write, real MainFrame mutation, Contract D registration,
Contract E source change, release, or promotion is permitted.

If deterministic rendering fails, the candidate disposition is a render
falsification. If rendering passes but exact-byte binding fails, preserve that
narrower binding falsifier. Only a complete pass may receive
`SUPPORTED_FOR_CONTROLLED_LOCAL_RENDER_BOUND_ERS_SHADOW_COMPOSITION`.
