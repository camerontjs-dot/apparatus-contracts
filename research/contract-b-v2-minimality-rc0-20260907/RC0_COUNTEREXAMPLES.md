# Contract B v2 Minimality RC0 Counterexamples

**Disposition:** `RC0_FALSIFIED_REVISION_REQUIRED`

The initial 42-test pressure suite passed across Python 3.11, 3.12 and 3.13, but a subsequent adversarial pass found two information-loss cases not represented by that suite. The green gate is preserved as evidence of the tested envelope, not treated as sufficient evidence for RC0.

## CE-01: silent planned retrieval-lane omission

Starting from a valid RC0 bundle with two retrieval lanes for one target:

1. remove one complete retrieval execution;
2. remove that retrieval's nomination from the candidate link;
3. leave the target aperture marked `complete`;
4. reseal the whole-object hash.

RC0 accepts the result. It has no independent representation of the **planned** retrieval executions, so `complete` means only that every retrieval still present in the artifact completed. An entire intended lane can disappear without becoming an aperture failure.

This violates the RC0 goal of preserving enough state to distinguish retrieval/aperture failures later.

## CE-02: silent tail-candidate truncation

Starting from a valid RC0 bundle where each retrieval has `candidate_limit = 2` and two ranked candidates:

1. remove the rank-2 candidate link and its otherwise-unused passage;
2. leave `candidate_limit = 2`;
3. reseal the whole-object hash.

RC0 accepts the result because the remaining ranks are contiguous from 1 and no field records the actual number of candidates returned by the retrieval execution.

This violates the RC0 goal of preserving the candidate pool strongly enough to distinguish candidate-recall from later selection/admission failures.

## What these counterexamples do and do not show

They show that the RC0 representation is insufficient for its stated diagnostic purpose even though its initial mutation suite passed.

They do **not** show that Contract A 2.0 lacks information, that legacy Contract B 1.x semantic fields are required, that raw retrieval score magnitude is required, or that Contract B should acquire CAL semantic authority.

## Smallest successor repair to test

A successor should add only the information needed to close these exact losses:

- an explicit per-target retrieval plan that survives even when an execution is omitted/not run;
- explicit retrieval execution state including `not_run`;
- requested versus actually observed source scope for each retrieval;
- actual `returned_count`, checked against the complete nomination ledger;
- candidate nomination ranks exactly `1..returned_count` for usable returned candidates.

A separate stored aperture summary may be unnecessary if aperture state can be deterministically derived from the target plan plus retrieval execution records. That ablation should itself be pressure-tested.

The successor must remain A2-native, evidence-world-only, and CAL-semantic-free.
