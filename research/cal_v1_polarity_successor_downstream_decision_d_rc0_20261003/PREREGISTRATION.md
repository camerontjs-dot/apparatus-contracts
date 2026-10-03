---
title: "CAL polarity successor downstream Decision D RC0"
domain: applied-ai-research
type: research-preregistration
status: frozen
source: "Apparatus issue 166; preserved issue 158 constructor; exact component Git objects"
tags: [cal, contract-c, decision, contract-d, integration-qualification, polarity]
updated: "2026-10-03"
structural_type: verification
lifecycle_scope: workbench
owner_surface: "Apparatus issue 166"
authority: deterministic-source
privacy: public-safe
volatility: stable
update_rule: append-only
verification: ["run_qualification.py with exact subject checkouts and a new run root"]
do_not_use_for: [release, representative-accuracy, Authorization, execution, contract-c-byte-identity]
---

# CAL polarity successor downstream Decision D RC0

This experiment asks whether the exact CAL polarity successor preserves its
corrected semantics through parent-bound Contract C, the maintained Decision
Engine, and the released Contract D 1.0.0 consumer.

Authority is [Apparatus issue #166](https://github.com/camerontjs-dot/apparatus-contracts/issues/166).
Issue #158 and Draft PR #160 supply the prepared upstream world and the
historical downstream subjects. Their byte-equivalence conclusion is source
material. It is not the evaluator for this successor.

## Subjects

The sole product subject is CAL `64b6c7702696c851057c1cf0b2c105b1c81db543`,
semantic implementation `caa0048f8f511ec3c4aa1ce713766f2219a04bc1`.

Contract C authority is candidate `c183d2d12306ee30c509169a58db55e7430fe8c5`
blob `aeb50dee8d24bda5f62eb879654e80437a50912d`, resolver
`292168222f83c67a24190b4846eebe84392e3d04` blob
`b9297ba06beefe1de8488bc25a4c424b0e10e58b`, and RC2
`b42c827acb0a9fe65353354d709add0e27bab307`.

Decision is maintained `main` `cadef9e103edeba32f1247b99d81d5e25175bcd9`.
Protected ingress, supported-claim policy, and materializer blobs are bound in
`SUBJECTS.json`. Contract D is released 1.0.0 commit
`298a1a0f7b7b6d7712e11200d04faec3e1ca169b`.

`SUBJECTS.json` binds every exact subject commit, tree, tracked blob, release
tag object, trusted target, preserved case, and constructor digest. The
apparatus base is `c3563cff66d2c85dcbf575c693056e2d8e4563d4`.

## What must stay and what may change

PIPE01–PIPE03 reuse the preserved Contract A handoff, Evidence Bundler package,
and Contract B bundle. Those upstream bytes must match the historical #158 arm.
Producer and provenance bytes may change. Each inherited Contract C whole-object
digest must differ from the historical object, and the difference must be
attributable to the successor semantic implementation, resolver commit, and
candidate identity. Downstream decision semantics must stay:

| Case | Parent | Decision | D consumer |
|---|---|---|---|
| PIPE01 | supported | clear | candidate_for_authorization |
| PIPE02 | contradicted | hold | hold |
| PIPE03 | not_checkable | hold | hold |

`candidate_for_authorization` does not perform Authorization.

The polarity specimen is new. It appends one source,
`Alpha did not have a higher rate than Beta.`, to the preserved Contract A
world, recomputes the handoff, and admits that retained passage for C1 together
with the retained C2 support passage. A pre-freeze Evidence Bundler probe on
commit `4e1f6fe00e7c350b28f52bfea14f1f8988847884` retained that negation passage
at nomination rank 3 under `retained_k=3`. If that passage is not uniquely
retained at execution, the run is apparatus-invalid. CAL must preserve a
negative `MORE_THAN` relation, conclude `contradicted`, and carry that
conclusion to Decision `hold` and Contract D consumer `hold`.

## Runtime pin

`source_pr123.py` stays byte-exact. Its historical constants still name the
predecessor producer. After import, and before any case, the runner rebinds
only:

- `CAL_SEMANTIC_IMPLEMENTATION` to `caa0048f8f511ec3c4aa1ce713766f2219a04bc1`
- `C_FREEZE` to `c183d2d12306ee30c509169a58db55e7430fe8c5`
- `RESOLVER_COMMIT` to `292168222f83c67a24190b4846eebe84392e3d04`

The Decision root is the maintained checkout supplied by the environment. No
adapter may rewrite a CAL conclusion or assertion polarity between measurement,
authority, parent, Contract C, Decision, and the Contract D consumer.

## Residue

Structured comparison covers parent result, Contract C, both child results, and
Contract D. Report prose is excluded. The residue normalizes the successor
instrument version `strict-comparison-polarity-rc0` back to
`rc7fb1-comparator-1`, replaces content hashes and generated identifiers, and
drops only `assertion_polarity`, `freeze_commit`, and `candidate_blob`. Explicit
checks separately require polarity, the new instrument version, unchanged
conclusions and relations, producer pins, policy, effect, and reason codes.
Old and new Contract C byte identity is not required.

## Negative controls

- Cross-run native-result replay substitutes the PIPE03 native child into the
  PIPE01 Decision inputs and must reject with `contract_c_validation_failed`
  and `NATIVE_RESULT_HASH_MISMATCH` before any Contract D stdout.
- Semantic-drift conformance mutates the authored C1 comparison direction to
  `LESS_THAN`. Structural validation may accept it. Target conformance must
  reject it before any CAL child, parent, Decision, or Contract D invocation.
- The predecessor Contract C candidate must reject the new CAL producer
  identity.
- The successor candidate must reject the predecessor resolver state.
- Successor resolver membership may accept the predecessor semantic
  implementation. The successor candidate pin must still reject that producer.
  The predecessor resolver list must reject the new producer. That is the
  required weak, fail-open path, and it must fail for the pin reason.

## Freeze and non-repair

Commit this protocol, the constructor, trusted inputs, historical byte copies,
subjects, wrapper, evidence packager, and task workflow before any decisive
CAL, Decision, or Contract D invocation. `EXPERIMENT.json` binds the apparatus
base tree, the harness blob, and the digest of every frozen file except itself.
Results may be appended after exposure. Frozen bytes stay unchanged.

If the first exposed run fails because the apparatus is wrong, preserve that
failure and identify a successor harness. Do not edit the exposed evaluator in
place. Do not modify CAL, Contract C, RC2, the Decision Engine, Contract D, or
the frozen expected outcomes after exposure.

Use Python 3.11 and Node 22. Build one wheel from the exact CAL tree, install
it in a new environment with `rfc8785==0.1.4` and `rank-bm25==0.2.2`, and
require the installed inspect identity to be the polarity semantic
implementation. Imports must come from that environment.

## Dispositions

One of:

- `SUPPORTED_POLARITY_SUCCESSOR_DOWNSTREAM_DECISION_D_CONFORMANCE`
- `FALSIFIED_POLARITY_SUCCESSOR_DOWNSTREAM_CONFORMANCE`
- `INCONCLUSIVE_APPARATUS_INVALID`
- `BLOCKED_EXACT_SUBJECT_UNAVAILABLE`

A supported result does not establish representative accuracy, independent
promotion acceptance, a public interface or version, merge, release,
Authorization, or execution.
