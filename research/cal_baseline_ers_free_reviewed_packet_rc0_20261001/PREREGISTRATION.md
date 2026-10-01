# CAL Pipeline ERS-free reviewed-packet baseline RC0 — preregistration

Date: 2026-10-01

Classification: **Research Infrastructure / controlled local baseline preparation**.

This successor is deliberately separate from Apparatus PR #152. PR #152 remains the exact ERS single-item RC1 first-input handoff and is not modified, weakened, or reinterpreted here.

## Objective / decision

Establish whether one already-reviewed **real** input packet can be replayed through the current Gate and exact pinned A→D controlled-local subjects without ERS participation, semantic adaptation, target re-authoring, result chasing, Contract E, Authorization, or operational execution.

This is the ERS-free baseline. A later ERS-inclusive run is a separate comparison and must not be backfilled into this result.

The baseline path is:

```text
one frozen real reviewed Gate packet
  -> current Gate #54 replay
  -> released Contract A 2.0 validation
  -> current Evidence Bundler #120
  -> Contract B 1.2.0
  -> pre-existing independently reviewed CAL targets
  -> CAL #183
  -> parent-bound Contract C #121
  -> frozen independent Contract C consumer
  -> Decision #86
  -> released Contract D 1.0.0
```

## Authority

Repository base:

- `camerontjs-dot/apparatus-contracts`
- main: `c3563cff66d2c85dcbf575c693056e2d8e4563d4`

Predecessor preparation retained as evidence, not as the baseline intake authority:

- Apparatus PR #152: `6c08fcafecf4cfca553500a3b0918292e447391c`
- PR #152 subjects manifest blob: `e4afc030d1a01c2ea7fb640b25bb8cea31a12d5e`
- PR #152 A→D runner blob: `f5b06c6711e7799823155e5f8d95597940950b92`
- PR #152 target-review verifier blob: `32b644de87fc23ac721a740a2db7ef34c56b4992`

Exact baseline subjects are the PR #152 downstream subjects **excluding ERS**:

- Gate #54: `89ca88c7f0a661601f7eb798b6759667fa20ab3f`
- Contract A 2.0.0: `529c92b49a34d5c610618551a8737f019f9fa332`
- Evidence Bundler #120: `08ca896debd6d16fa21be2f178ed7cbe62395d00`
- Contract B 1.2.0 lock: `c314e53bd91c0736aa4370a364673b069aceb43e`
- CAL #183: `ddaf94551e38663920593cab89f9c60d43c1555f`
- parent-bound Contract C #121: `c5b1d757f3a0ad4f6e2c3f6dbdc2dd2d3c1403ec`
- Contract C RC2 authority: `b42c827acb0a9fe65353354d709add0e27bab307`
- current-CAL resolver: `1d33e0612befcf8016816197c90c062373796df9`
- frozen independent Contract C consumer: `12e7e640b229619501960b1b89cf4716d8d985b3`
- Decision #86: `6cdb59c2ba41779ac954af56dd077574ba090013`
- Contract D 1.0.0: `298a1a0f7b7b6d7712e11200d04faec3e1ca169b`

GitHub and exact immutable artifacts remain authoritative if any local summary disagrees.

## Boundary

### In scope

- locate at most one already-existing real reviewed packet;
- freeze its exact packet, expected Contract A, target-review manifest, and reviewed target identities before baseline execution;
- verify exact subject checkouts/blobs;
- replay current Gate on the exact frozen packet;
- run the already-qualified PR #152 target-review verifier against the exact reproduced Contract A;
- run the already-qualified PR #152 A→D runner against the exact reproduced Contract A and reviewed targets;
- preserve receipts, first failures, deterministic replay results, substitution-control results, and the observed CAL/Decision disposition.

### Allowed local mutations

Only fresh baseline output/receipt directories and, if needed, this successor's research-infrastructure evidence files.

### Protected / prohibited

Do not:

- invoke ERS or use an ERS inventory as the baseline input;
- invoke Contract E;
- perform Authorization or operational execution;
- create, regenerate, reinterpret, or repair CAL target semantics during the baseline run;
- select a different packet after seeing Gate/CAL/Decision output;
- use the synthetic PIPE01/PIPE02/PIPE03 apparatus cases from PR #123 as the “real” baseline packet;
- change Gate, Contract A/B/C/D, EB, CAL, independent-consumer, or Decision semantics;
- change EB admission after observing CAL/Decision output;
- repair a frozen evaluator or acceptance rule after decisive exposure.

PR #123 remains valid bounded synthetic integration evidence. It is not a substitute for a real reviewed packet because its sources and target objects are created by the integration harness.

## Eligible real reviewed packet

Exactly one candidate may be admitted.

Before any baseline stage runs, the candidate must already contain and freeze:

1. a real, non-synthetic Gate input packet accepted by the exact Gate #54 input surface;
2. the exact expected Contract A bytes previously produced from that packet;
3. an exact `cal-pipeline-trusted-target-review-v1` manifest bound to that Contract A handoff and file hash;
4. all target files named by that review;
5. `independent_review=true` and `semantic_fidelity_attested=true` for every Contract A child;
6. distinct non-empty target-author and reviewer context identities for every child;
7. target byte hashes and proposition/text bindings that pass PR #152's exact verifier;
8. semantic families inside CAL #183's qualified active set.

The packet may be private/local. Private claim/source bytes must not be committed merely to make the baseline public.

If no candidate satisfies all eight conditions, stop:

`BLOCKED_NO_ELIGIBLE_REVIEWED_PACKET`

Do not author or review a fresh target inside this baseline attempt merely to turn the stop into a runnable case. That is a separate preparation task.

## Gate replay

Gate replay is part of the baseline, not historical evidence.

Using the exact same frozen Gate packet, run Gate #54 twice into separate fresh output roots.

Require:

- both runs emit Contract A;
- both emitted Contract A files validate under released A2;
- the two Contract A files are byte-identical;
- both Contract A handoff identities are identical;
- the reproduced Contract A bytes are byte-identical to the packet's frozen reviewed Contract A.

Any mismatch stops the run. Preserve both outputs.

A Gate replay failure is not repaired in place after exposure.

## Target-review gate

Run the exact PR #152 verifier:

- source commit: `6c08fcafecf4cfca553500a3b0918292e447391c`
- blob: `32b644de87fc23ac721a740a2db7ef34c56b4992`

It must print `TARGET_REVIEW_VERIFIED` for the reproduced Contract A and the already-frozen review.

This mechanical check does not create semantic review. It only verifies the frozen review's binding and recorded independence properties.

## A→D execution

After Gate replay and target-review verification pass, use the exact PR #152 runner:

- source commit: `6c08fcafecf4cfca553500a3b0918292e447391c`
- blob: `f5b06c6711e7799823155e5f8d95597940950b92`

The runner must use the exact pinned downstream subjects above.

Its existing requirements remain intact:

- released A2 validation;
- current EB #120;
- Contract B 1.2.0;
- CAL #183 with exact reviewed target files;
- parent-bound Contract C and frozen independent consumer;
- Decision #86 and released D1;
- two exact A→D runs with required byte-equivalent key artifacts;
- unresealed Contract-A source-byte substitution rejected before EB artifact emission;
- no Contract E;
- no ERS write;
- no Authorization or execution.

No expected CAL parent conclusion or Decision disposition is preregistered. `not_checkable/HOLD` is a legitimate observation.

## Exclusive execution ownership

Before reading the selected packet or starting Gate, establish one execution owner for this baseline attempt.

Minimum observable evidence:

1. no live Conduit task is already executing this baseline objective;
2. no relevant Gate/A→D runner process is already active for the same baseline;
3. a fresh output root is created for this attempt and is not reused;
4. one attempt/owner receipt records the supervising task/session identity when available, process identity, output root, and start time before stage execution;
5. if ownership is ambiguous, stop rather than launching a second executor.

Allowed stop:

`BLOCKED_EXCLUSIVE_EXECUTION_OWNERSHIP_UNESTABLISHED`

This records only the inspected ownership surface. It is not a claim that no unrelated process exists anywhere on the machine.

## Acceptance evidence

A successful baseline requires all of:

- exact downstream subject/blob verification;
- one eligible frozen real reviewed packet;
- exclusive execution ownership established;
- current Gate replay twice, byte-identical and identical to the frozen reviewed Contract A;
- target-review verifier PASS;
- complete A→D run receipt;
- A→D deterministic replay PASS;
- Contract-A source-substitution control rejected before EB artifact emission;
- exact observed CAL parent conclusion;
- exact observed Decision disposition;
- exact Contract D consumer outcome;
- Authorization performed: false;
- execution performed: false;
- Contract E invoked: false;
- ERS invoked/written: false.

## Legitimate terminal states

- `SUPPORTED_FOR_BOUNDED_ERS_FREE_REAL_PACKET_BASELINE`
- `BLOCKED_NO_ELIGIBLE_REVIEWED_PACKET`
- `BLOCKED_EXCLUSIVE_EXECUTION_OWNERSHIP_UNESTABLISHED`
- `FALSIFIED_GATE_REPLAY`
- `FALSIFIED_A_TO_D_REPLAY_OR_SUBSTITUTION_CONTROL`
- `INCONCLUSIVE_APPARATUS_INVALID`

A semantic `supported`, `contradicted`, `mixed`, or `not_checkable` CAL result is an observed pipeline result, not by itself the research disposition above.

## Stop rule

Stop when:

- no eligible reviewed packet exists;
- subject identity differs;
- execution ownership cannot be established;
- Gate replay differs;
- target review does not bind the reproduced Contract A;
- A→D deterministic replay or substitution control fails;
- a next step would require new target semantics, a different packet, ERS, Contract E, Authorization, execution, release/promotion, or an invented semantic default.

Preserve the first failure. Do not reroll the packet or move the acceptance boundary after result exposure.

## Non-claims

This baseline does not establish:

- ERS intake correctness;
- end-to-end MainFrame claim discovery;
- source authority or corpus completeness;
- universal CAL semantic correctness;
- production authorization;
- Contract E readiness;
- a production release or SemVer decision;
- equivalence between an ERS-inclusive run and this ERS-free baseline.

It establishes only what the exact frozen real reviewed packet and exact pinned controlled-local subjects actually demonstrate.
