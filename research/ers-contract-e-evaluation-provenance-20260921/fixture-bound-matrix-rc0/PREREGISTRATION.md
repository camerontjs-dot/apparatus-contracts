# Fixture-bound evaluation-time provenance matrix — execution preregistration

## Experiment

`ERS-EVAL-TIME-PROV-20260922-05`

## Purpose

This record creates a dedicated evidence carrier for the decisive fixture-bound evaluation-time provenance matrix.

It inherits:

- the scientific question and controls from PR #130;
- the frozen scientific runner from PR #134;
- the explicit mixed-provenance fixture authority from PR #139;
- the independently qualified fixture-binding gate from PR #140.

No scientific code is changed by this execution preregistration.

## Exact predecessor

PR #140 receipt head:

`dee0aaa2483349ec8106d376d214d99c6790336f`

Qualified gate disposition:

`QUALIFIED_FIXTURE_BOUND_SCIENTIFIC_SUBJECT`

Fixture subject identity:

`sha256:bebbb1b7973a962d59c92061e8e70283a2fb4b2b8c388705b8d80ce13000c7ad`

Frozen scientific runner blob:

`35bf0e98d7575b9db7ffe2f6906aff757e865e72`

Frozen receipt-preflight blob:

`e7e94523bff84792d355ef2a6da805a91919e076`

## Scientific question

Unchanged:

Can the frozen Contract E → ERS shadow composition bind an independently sourced evaluation time to the exact Contract E invocation and exact Contract E result, so that changing the result time after evaluation is rejected before `shadow_ready`?

## Required order of operations

A future operator-initiated run must:

1. inspect live GitHub and verify this execution carrier has not moved;
2. use a fresh detached checkout at its exact frozen head;
3. verify the worktree is clean;
4. independently establish the qualified PR #138 fixture artifact bytes;
5. run the frozen PR #140 fixture-binding gate against the exact supplied fixture root;
6. require the gate to PASS with subject identity `sha256:bebbb1b7973a962d59c92061e8e70283a2fb4b2b8c388705b8d80ce13000c7ad`;
7. recheck the scientific runner and receipt-preflight Git blobs;
8. verify all other frozen runner dependencies and source receipts before candidate execution;
9. create and snapshot an empty qualification sandbox;
10. execute the unchanged decisive matrix once;
11. preserve RESULT, FAILURE, MATRIX_PROGRESS, sidecars, sandbox before/after snapshots, exact commands, exact dependency identities, and environment;
12. stop on the first exposed evaluator, authority, infrastructure, or scientific failure.

The fixture gate is a prerequisite. A gate PASS is not a scientific result.

## Decisive controls

The complete frozen matrix must run. Do not cherry-pick a favorable subset.

The first decisive falsifier remains:

> after an authentic Contract E evaluation, changing only the result's evaluation time by +1 second without rerunning Contract E must be rejected before `shadow_ready`.

The remaining preregistered controls must also execute unchanged, including authentic PIPE01, both cross-pairs, one-byte result mutation, wrong intent, wrong authority state, wrong issuer, stale transcript, replayed challenge, caller-supplied time/result injection, PIPE02 expected HOLD, PIPE03 expected HOLD, and sandbox non-mutation.

Any forbidden mutation reaching `shadow_ready=true` is a falsification.

## One-run rule

This execution subject permits at most one decisive matrix run after the pre-execution gates pass.

Do not repair and rerun this frozen subject after exposure.

If execution fails because of an apparatus or environment defect before a scientific result is reached, preserve that result and classify it. Any repaired successor requires a new explicit successor record rather than rewriting this execution.

If a scientific counterexample is observed, stop and preserve it.

## Boundaries

This record does not itself authorize execution. Human/operator initiation of the run remains required.

It does not:

- reinterpret reconstructed fixtures as historical bytes;
- change Contract E, Contract D, CAL, Decision Engine, ERS, or the frozen runner;
- authorize an executor or pending-review write;
- authorize production promotion, release, effect registration, or real MainFrame mutation.

The only next scientific action after explicit operator initiation is the unchanged fixture-bound evaluation-time provenance matrix.
