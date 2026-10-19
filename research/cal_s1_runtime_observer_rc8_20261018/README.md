# RC8: real-runtime binding and external evaluator, prepared but not executed

Owner: apparatus-contracts #173. Base: Draft #184 at
64844bd88b5f84b62c27c04f2be6fff6c7c1f1d2. This is a separate additive
research-infrastructure source candidate. #183's denied preflight, #184's
fake-only profile, and the failed RC5/RC6 first runs are unchanged.

**SOURCE_PREPARATION_ONLY. LIVE_EXECUTION_BLOCKED. Q13_NOT_ADMITTED.**
No Docker command, candidate program, CAL evaluator, provider request or model
inference was executed during this preparation. Source tests explicitly disable
subprocess.Popen. Do not equate their success with working Docker code.

## Engineering change

The earlier adapter has fake execution and fake observation interfaces. RC8 adds
concrete, bounded Docker command/capture code, with no host-Python execution
fallback. It uses the existing RC4 non-root, read-only, network-none, limited
worker design and its exact retained network probe and validator. It does not
edit that worker or the shared project-env helper.

The evaluator lives outside candidate execution. A candidate is mounted read-only
and invoked in a fresh restricted container for each case; stdout/stderr and the
command lifecycle are captured by the trusted controller. The external evaluator
then checks the answer against a controller-owned frozen synthetic oracle. Neither
that oracle nor its journal is mounted in the candidate container. A candidate
cannot submit case/evaluator events or a passing receipt as authority. Correct
output plus a zero exit is necessary, but a zero exit or PASS claim alone fails.

The independently implemented post-run checker recomputes expected answers from
raw controller captures; it imports neither the runner nor candidate code.
All host-side capture and checking still trust the host kernel, Docker daemon and
controller process. Files or hashes cannot authenticate a malicious host. The
claim is exact-artifact black-box behavior, not proof of an internal function call,
model-independent authorship, or causal consumption of particular source spans.

## Reuse and transfer limits

- #175 prepare_packet.py and independent_packet_checker.py are loaded at their
  exact retained Git blobs. They construct/check each new seven-file **synthetic**
  packet. CAL source bodies, calibration and held-out material are absent.
- RC4 worker_control.py and network_state_validator.py retain their exact bytes.
  RC8 would rerun their controls on its own new workers after permission resolution,
  not rerun an old frozen trial or inherit an old PASS.
- #184's explicit LF line-array proposal remains a future model-tool profile.
  This first RC8 phase runs preselected synthetic programs, not a model. It does
  not remove LIVE_OBSERVER_NOT_IMPLEMENTED from #184 or relabel its fake Witness.
- Python subprocess supplies binary pipes, subprocess lifecycle and timeouts.
  Docker supplies container constraints. New code is a bounded binding, not an
  independent sandbox platform or a change to project-wide architecture.

Primary implementation references consulted on 2026-10-18:
https://docs.python.org/3/library/subprocess.html
https://docs.docker.com/engine/containers/run/

## Exact planned qualification

SPECIMENS.json contains six known synthetic programs and three input/expected-output
pairs: 18 case-control evaluations. The good program must return all three correct
answers. Wrong-value, fake-PASS, early-exit, forged-event and extra-receipt-field
controls must be rejected for the declared reason. Runtime/identity/cleanup failures
are never counted as successful negative semantic controls. The first unexpected
result ends the attempt. No source/fixture/evaluator repair and rescore is allowed.

The initial qualification deliberately answers only: can this runtime/evaluator
boundary distinguish actual correct output from plausible false completion?
A subsequent, separately frozen model-facing qualification must still exercise
real generated read/write/test calls, LF line-array fidelity, source-data injection,
forbidden operations, full tool inventory, reset and context boundaries. Only
then can #173 decide Q13 for an exact coding profile. Neither phase consumes CAL's
single held-out attempt.

## Permission and freeze gates

APPROVAL.template.json and PINS.template.json are intentionally incomplete.
Source identity and runtime pins must both be bound to a separately reviewed run.
A platform response reference and its digest are required by the record schema,
but a well-shaped reference is **not** authentication or a permission grant.
A trusted operator must review the actual attributable response to #177; do not
fill the template with invented approvals or change the gate to force execution.

The default gate refuses before executable inspection or any subprocess. No denied
operation was retried through a different tool, syntax, subprocess or host. The
current user approved preparation; approval does not erase the recorded platform
stop. SUPPORT_REQUEST.md is ready for the official support channel. No support
case or favorable decision was obtained in this session.

SOURCE_SETUP.json is an exact source/plan inventory, **not a scientific runtime
freeze**. Before a live attempt, supply observed current pins, an attributable
platform resolution, exact run review and one external attempt ledger location.
Private support replies, executable paths and raw command receipts remain local.
The live routine never performs automatic image pulls or changes global settings.

The controller creates an exclusive one-attempt marker keyed by source manifest
in the designated external custody parent. Using a different parent could evade
that local marker; the custodian must keep one authoritative attempt location.
This is not a distributed anti-replay service. Ownership/teardown checks only
remove the full returned worker ID after its task-owner label was observed.

## Source-only checks

From this directory, an existing Python 3.11+ can run:

    python3 -B -m unittest -v test_binding

These tests run no candidate, Docker or model. Native source checks are not an
alternate route for the denied live preflight. The supported-interface question
remains separate from code preparation and synthetic protocol checking.
