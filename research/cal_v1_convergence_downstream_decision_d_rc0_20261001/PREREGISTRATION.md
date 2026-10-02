---
title: "Exact CAL convergence downstream equivalence RC0"
domain: applied-ai-research
type: research-preregistration
status: frozen
source: "Apparatus issue 158; preserved PR 123; exact component Git objects"
tags: [cal, contract-c, decision, contract-d, integration-qualification]
updated: "2026-10-01"
structural_type: verification
lifecycle_scope: workbench
owner_surface: "Apparatus issue 158"
authority: deterministic-source
privacy: public-safe
volatility: stable
update_rule: append-only
verification: ["run_qualification.py with exact subject checkouts and a new run root"]
do_not_use_for: [release, representative-accuracy, Authorization, execution]
---

# Exact CAL convergence downstream equivalence RC0

This experiment asks whether swapping qualified CAL Slice 2 `ddaf945…` for
convergence candidate `6bb0d60…` changes the supported parent-bound path through
external Contract C, maintained Decision, and released Contract D 1.0.0.

Authority is [Apparatus issue #158](https://github.com/camerontjs-dot/apparatus-contracts/issues/158).
`SUBJECTS.json` binds all 11 exact commits, trees, 594 relevant source/schema/script
blobs, release tag objects, the trusted target bytes, cases, and controls. These
pins remain fixed if a repository advances. The apparatus base is
`c3563cff66d2c85dcbf575c693056e2d8e4563d4`.

## Factor, unit, and evidence layer

The sole subject factor is CAL Arm A versus CAL Arm B. Arm B also uses its
supported author → conform → execute workflow. Both receive the same exact
Contract A, admission decisions, EB configuration, and Contract B world. This is
a paired integration reproduction on exposed regression specimens, not fresh
blind semantic or accuracy qualification.

The primary metric is exact file-set and byte equality for three paired PIPE
cases, with zero false accepts in the two frozen negative-control designs.

| Case | C1 admission | C2 admission | Parent | Decision | D consumer |
|---|---|---|---|---|---|
| PIPE01 | support | support | supported | clear | candidate_for_authorization |
| PIPE02 | contradiction | support | contradicted | hold | hold |
| PIPE03 | support | none | not_checkable | hold | hold |

`candidate_for_authorization` does not perform Authorization.

## Preserved source and input construction

`source_pr123.py` is an exact copy of the harness at PR #123 head
`e68e5ab387e9779b0be62d92766b76e475964790`. That historical PR is preserved and
unchanged. Its claim text, source corpus, EB configuration, admission construction,
case expectations, canonical serialization, public frozen-consumer inputs, Decision
arguments, D validation, and D consumption remain the source of this path.

The two `trusted-targets/` files are the exact output of that source's preserved
target and serialization functions. Their hashes are frozen before any decisive
execution. They are historical trusted inputs, not targets selected from verdicts.
Newly generated fixture outputs are new-run reconstructions of those fixed inputs;
this experiment does not claim recovery of PR #123's historical output files.

The new operational wrapper records real subprocess stdout and stderr separately,
verifies protected identities, and compares bytes. It intercepts the preserved
parent invocation to author/conform Arm B targets before any child invocation.
Both arms explicitly invoke clean-installed `run-bundle` for each child, then run
the preserved parent CLI. The parent independently reruns the same children;
their entire native artifact sets must equal the explicit child runs.

No result is normalized or semantically adapted between stages. The Decision CLI's
materialized output is the canonical Contract D object; its actual stdout bytes
must equal the emitted file bytes. D consumer stdout is retained and compared.

## Freeze and execution

Before decisive exposure, commit this protocol, source, trusted inputs, subjects,
wrapper, and task workflow; then commit `EXPERIMENT.json` binding the source
commit/tree, file hashes, and harness blob. Runtime receipts record the exact
freeze/executed head and tree. Results and findings may be appended after exposure;
the frozen files remain unchanged.

Use Python 3.11 and Node 22, matching PR #123's runtime pattern. Build a new wheel
for each exact CAL tree with `python -m build --wheel`. Install each wheel in its
own new environment with source `PYTHONPATH` absent. Record complete dependency
versions and wheel digests; require matching dependency versions. Verify every
packaged CAL source blob against its exact subject and prove imports originate
inside the corresponding clean environment. Each package inherits `0.6.0`; this
is subject metadata, not a release/version decision.

The orchestration worker uses Arm A's environment with `rfc8785==0.1.4` and
`rank-bm25==0.2.2` for the preserved EB v1 import path. EB itself executes from
its exact verified source tree. Unused embedding and PDF paths are outside this
experiment. The frozen EB integration uses its deterministic v1 retrieval path;
there is no model or substituted retrieval implementation.

Invoke from the repository root, supplying exact subject roots and a new output
root outside the apparatus source checkout:

```sh
python3.11 research/cal_v1_convergence_downstream_decision_d_rc0_20261001/run_qualification.py \
  --subjects-root SUBJECTS_ROOT --run-root NEW_RUN_ROOT \
  --python python3.11 --node NODE_22_EXECUTABLE
```

Record the source identities again after all controls. Any dirty or mismatched
component stops the run. Build caches and ignored interpreter caches are not
component implementation changes.

## Primary acceptance and determinism

For each PIPE case require exact equality of:

- frozen Arm A trusted and Arm B authored targets;
- Contract A bytes, EB native package bytes, and the Contract B artifact set;
- complete native child artifact names and bytes, including both explicit and
  parent-produced children;
- parent-result bytes;
- Contract C bytes and the whole-object hash bound by the CAL manifest;
- Decision disposition, materialized Decision/canonical D stdout and file bytes;
- actual D consumer output bytes and result.

Repeat PIPE01 in a separate Arm B output root. Require exact native child file-set
and byte equality, parent bytes, C bytes, and D bytes. Hashes supplement direct
byte comparisons; JSON-object or label equality cannot replace them.

## Frozen negative controls

**Cross-run replay:** Preserve PR #123's first-common-child substitution from
PIPE03 into PIPE01's frozen-consumer input, retaining PIPE01 C and authority. Run
the same attack for both arms and compare the attack input bytes. Decision must
exit 1 with `contract_c_validation_failed` and the frozen consumer's
`NATIVE_RESULT_HASH_MISMATCH`, with zero stdout/D bytes. Unavailable backends or
an unrelated rejection do not count as a successful falsifier.

**Conformance stop:** In a separate Arm B PIPE01 root, author the C1 target and
change only `comparison_direction` from `MORE_THAN` to `LESS_THAN`, the exposed
#184 `strict_direction_disagrees_with_claim` shape. The unchanged ordinary
`validate-bundle` structural validator must accept with exit 0. Candidate
conformance must reject with exit 2 and `conform rejected:` on stderr. The same
orchestration gate must stop immediately before any explicit child, parent,
Decision, or D consumer invocation; no native child, C, or D output may exist.

If the structural validator ceases to accept this shape, classify the apparatus
or exact-subject observation. Do not rewrite it into a different weak control.
This tests the gated workflow; it makes no claim that raw `run-bundle` itself
enforces semantic conformance.

## Terminal and failure rules

Allowed dispositions are:

- `SUPPORTED_EXACT_CAL_CONVERGENCE_DOWNSTREAM_EQUIVALENCE` only after all paired,
  expected-outcome, determinism, identity, and negative-control checks pass;
- `FALSIFIED_EXACT_CAL_CONVERGENCE_DOWNSTREAM_EQUIVALENCE` for an observed byte,
  expected-outcome, or fail-closed counterexample on valid apparatus;
- `INCONCLUSIVE_APPARATUS_INVALID` for an environment, runner, or discriminator
  defect preventing a valid contrast;
- `BLOCKED_EXACT_SUBJECT_UNAVAILABLE` for missing or mismatched frozen authority.

Stop at the first material failure and preserve the head/tree, command, streams,
receipt, and downstream `NOT_RUN`. Classify it before any bounded apparatus-only
successor. A correction must state why it cannot change subjects, inputs,
expectations, grammar, component behavior, or the byte/rejection discriminator.
No exposed run is rerun into its old output root.

> **Binds:** this exact issue #158 apparatus and its experiment runs
> **Tier:** T1 (identity, byte, outcome, and control violations detected)
> **Check:** frozen wrapper plus raw component subprocesses and receipts
> **Escape:** preserve a terminal invalid/blocked/falsified result; use a separately
> identified apparatus successor for a classified apparatus-only defect

## Boundaries and handoff

No CAL, Decision, or Contract A/B/C/D implementation is changed. C remains
external and unversioned at its frozen parent-bound subject; D remains released
1.0.0. Do not invoke ERS pending-review dispatch, Contract E, Authorization, or
execution. No broad grammar, new family, effect registration, release/version
choice, merge, tag, consumer repin, or change to CAL PR #186 is authorized.

A valid terminal result is published as a Draft Research PR against Apparatus
main and linked from issues #158 and #137. It supplies only this exact bounded
integration evidence. CAL 1.0 still requires independent promotion review and
acceptance, separately governed compatibility/version/release decisions and
artifact custody. Representative accuracy remains unestablished.
