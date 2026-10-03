# ERS 05 fresh-process evaluation-provenance successor

**Classification:** Draft Research successor. No scientific matrix has been run by this branch.

**Parent:** apparatus-contracts PR #150 at `f6ac1ecd3d1220834f6f5b245ab0d57aeca92e79`.

## Objective

Resolve the remaining PR #130 evaluation-time provenance question by running the unchanged frozen scientific matrix with process isolation that prevents released Contract D checks from being contaminated by later research-profile module state.

The decision remains:

> Can the frozen Contract E → ERS shadow composition bind supervisor-sourced evaluation time to the exact Contract E invocation and exact Contract E result, rejecting result/time/request substitution before `shadow_ready`?

## Preserved scientific authority

The successor must keep these subjects unchanged:

- PR #130 preregistration: `dcdd10355e2f885273d843eef6e345bafca95faa`;
- Decision subject: `816374379ba7eb23f5bfdadaf203b7e287c052db`;
- Contract E: `b153dcc4434cbe8a98616a9e410c6125378144c7`;
- ERS RC5 authority: `099f84700f28e118734f1ca74feb977da1c4cf17`;
- exact frozen ERS RC6 source/freeze lineage already bound by the receipt successor;
- Contract D tag object: `6eadd688b482f3c9fce2ce5e7a2841089d852096`;
- peeled Contract D commit: `298a1a0f7b7b6d7712e11200d04faec3e1ca169b`;
- Contract D effect-registry blob: `a40f4f4447470654bdc16d852f5927189ae30cc5`;
- Contract-C consumer: `12e7e640b229619501960b1b89cf4716d8d985b3`;
- provenance profile: `3934423b1a97ad1b099057c40fe8014e5dd08c97`;
- transcript schema blob: `b85b38ce95263e348d2ebd1293f76ffc87adcf6d`;
- frozen issuer public key identity: `sha256:e7f4581c2d58eecd0279f895cf3dd49df3098d092fa1e083731d802fcd1db259`;
- PR #138 fixture authority, including PIPE01 Contract-C bytes `sha256:ba02ec570b0048832a2fc9f6b958f426b11e5dc0fe73cf1e12ae515d38ea23a0`.

Do not substitute Decision PR #90, current Decision main, a different Contract E candidate, a new issuer key, or a reconstructed scientific expectation after observing the matrix.

## Trigger / preserved predecessor result

PR #150 stopped before freeze and before any Contract E scientific evaluation because the strengthened qualification harness observed:

`ERS effect unexpectedly present in released Contract D registry`

Subsequent discrimination established that the released registry file remained unchanged and that the effect existed only in cached in-memory `validators.contract_d_core.REGISTRY` after a research profile had rebound that module inside a long-lived interpreter.

The discrepancy is therefore explained as qualification-harness process-state contamination. It is not evidence that released Contract D contains the ERS effect.

No PR #130 scientific result was obtained.

## Hard protocol

### Process A: released-D preflight

Before any research-profile import:

1. start a fresh Python interpreter;
2. verify exact Contract-D HEAD/tag/peeled commit/effect-registry blob;
3. load the exact released `validators/contract_d_core.py` under a fresh module name;
4. construct the frozen research ERS-effect Decision shape;
5. require released D to reject it with `unknown_effect_type`;
6. terminate the interpreter.

Process A may not import Contract E research profiles, ERS candidate modules, the provenance profile, or the scientific runner.

### Process B: decisive candidate

Only after Process A exits PASS:

1. start another fresh Python interpreter;
2. execute the exact PR #150 scientific runner blob `45eab4fc9aba4b851020b649546b09272c249c36`;
3. use an empty dedicated scientific sandbox;
4. supply the exact frozen issuer private key matching the frozen public-key identity;
5. run the existing PR #130 matrix once;
6. preserve all outputs, including a negative or inconclusive result.

No in-process reuse of Process A modules is permitted.

## Matrix

The decisive matrix remains the PR #130 matrix already encoded in the frozen runner, including:

- +1-second result substitution without re-evaluating E;
- cross-pairing authentic evaluations/transcripts;
- one-byte result mutation;
- wrong intent;
- wrong AuthorityState;
- wrong issuer;
- stale transcript;
- replayed challenge;
- caller-supplied time attempt;
- caller-supplied result attempt;
- positive write-free path;
- weak caller-time control already encoded by the experiment.

Do not add or delete cases after exposure.

## Dedicated sandbox

The scientific sandbox must:

- exist before Process B;
- be empty before the decisive run;
- be a dedicated disposable path, not MainFrame and not a repository root;
- remain write-free on the positive shadow path except for experiment output outside the sandbox;
- be snapshotted before/after by the runner.

Whole-MainFrame metadata deltas are **not** part of this successor's scientific property. PR #150's unexplained three-entry MainFrame metadata delta remains preserved as predecessor evidence rather than being silently relabeled.

## Issuer custody

The current frozen ERS verifier and supervisor hard-pin the issuer public key identity above and reject any nonmatching private key.

The matching qualification-only private key exists under local custody. This successor does not rotate, export, replace, regenerate, or weaken that identity.

Absence of the exact private key is `BLOCKED`, not a reason to change the verifier after freeze.

## Acceptance / dispositions

Allowed final states:

- `SUPPORTED_FOR_BOUNDED_EVALUATION_PROVENANCE`: Process A passes; weak control discriminates; all target falsifiers reject before `shadow_ready`; positive path reaches the preregistered write-free state with `execution_occurred=false`.
- `FALSIFIED`: a preregistered target falsifier reaches `shadow_ready` or another preregistered falsification condition occurs.
- `INCONCLUSIVE`: apparatus executes but cannot discriminate the intended property, including target/weak-control non-discrimination.
- `BLOCKED`: a required exact frozen artifact, key, environment, or authority cannot be established before decisive exposure.

A green process or test is not itself the research disposition.

## Nonclaims

A supported result would not establish:

- real-world AuthorityState root legitimacy;
- OS clock correctness;
- same-user compromise resistance;
- production Contract E readiness;
- production effect registration;
- real execution or write authorization;
- executor correctness;
- universal point-of-use authorization semantics.

## Stop rule

Stop after one decisive matrix disposition. Do not repair the runner, verifier, frozen cases, issuer identity, Contract E, Contract D, Decision subject, ERS subject, or expected outcomes after exposure.
