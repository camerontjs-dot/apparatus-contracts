# ERS pending-review Contract E consumer RC0 result

Disposition: `SUPPORTED_EXPLORATORY_SHADOW_PROFILE_ONLY`

This is exploratory evidence, not preregistered qualification and not
production authorization.

## Exact subjects

- Contract E target-cardinality successor:
  `a678c73a661853a3a704666fc6bbf29fa378948f`
- ERS canonical baseline:
  `0637deae76d22afa4ef3a7ccbf722974ef20edbf`
- candidate principal: `agent:epistemic-auditor`
- candidate operation: `epistemic_audit.stage_pending_review@1`
- mode: shadow only

## Observed evidence

Released Contract D 1.0.0 rejects the ERS-specific effect as
`unknown_effect_type`. RC0 therefore used an in-process research-only registry
extension to test composition without changing released Contract D semantics.

The Contract E target-cardinality successor test passed:

- predecessor asserted controls: 62
- new target-cardinality controls: 3
- total: 65

The ERS shadow profile passed all 9 requested discriminator cases and reported:

- `ERS_CONTRACT_E_SHADOW_RC0: PASS`
- `cases=9`
- `execution_occurred=false`

The tested cases include exact authorization, wrong principal, wrong target,
swapped Contract D decision, stale authority, revoked authority, replay after
revocation, changed target pre-state, and generic knowledge-operation
authority.

## Preserved failures and deviations

Initial RC0 runs failed on prototype plumbing defects before the 9-case pass:

1. incorrect repository-parent path;
2. dynamic import module registration under Python 3.14;
3. incorrect test root;
4. misspelled `jurisdiction` keyword.

Those failures are preserved in the task/session evidence and were corrected
without changing Contract E normative core.

A broader historical integration test on this branch reports:

`MATRIX-SIZE: count before sentinel=112`

where the test currently asserts `COUNT >= 120`.

The same failure reproduces on a clean detached checkout of the untouched
Contract E subject `a678c73a661853a3a704666fc6bbf29fa378948f`.
Therefore RC0 does not attribute this failure to the ERS profile and does not
repair it.

## Interpretation

The existing Contract E machinery can discriminate the bounded ERS
pending-review authorization shape in shadow mode when supplied a research-only
Contract D effect profile and exact trusted bindings.

The evidence does NOT yet justify changing Contract D's released effect
registry or calling Contract E production-ready.

A fresh successor must freeze a real ERS consumer commit, preregister before
implementation/qualification, and test cross-repository conformance against
that exact consumer.
