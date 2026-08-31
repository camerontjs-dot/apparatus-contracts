# Contract D adversarial attack harness v1

Research infrastructure linked to #29 and EDR #28.

## Purpose

This harness exists to find counterexamples, not to make Contract D pass. It attacks the immutable frozen successor target first, then may be pointed at a canonical promotion candidate using an explicit pinned target.

Initial frozen target:

- repository: `camerontjs-dot/apparatus-contracts`
- commit: `fd6923115116b0ced0f9feb5c005099d2e51ea88`
- candidate subtree: `fe449f9ec27eeddb434276ded375f9dc16b48e29`
- research token: `0.3.0-rc4`

## Attack families

- finite-JSON ingress and decoded host values;
- cycles, aliases, and depth/resource boundaries;
- canonicalization and semantic-identity metamorphics;
- upstream/policy/target/effect replay and substitution;
- requested-operation and requested-parameter applicability;
- unknown/future values;
- Authorization-context leakage;
- pairwise mismatch combinations;
- seeded weak-consumer discrimination.

## Finding classes

Every probe is classified separately as one of:

- `declared-v1`: a failure here can block promotion;
- `external-api-shape`: malformed/out-of-declared caller behavior;
- `bounded-runtime-robustness`: depth/resource behavior outside the current semantic promise;
- `evaluator-assurance`: seeded weak-consumer discrimination.

A runtime or malformed-caller finding is not silently upgraded into a Contract-D semantic defect. Conversely, a reproducible `declared-v1` counterexample is not downgraded to keep promotion moving.

## Modes

Normal mode always writes `report.json` and `report.md` and exits zero so findings remain visible as evidence.

`--gate` exits non-zero only when the report contains an in-domain promotion blocker. The research-infrastructure baseline intentionally runs normal mode until seeded-mutant discrimination and finding classification have been reviewed.

## Non-claims

A green harness run does not establish universal correctness, Authorization correctness, execution safety, arbitrary language/runtime interoperability, or unlimited depth/resource support. It only reports what this exact attack set observed against the pinned target.

## Setup deviation

During initial GitHub setup, a connector write-selection error accidentally created placeholder issues #30 through #38 while branch creation was being invoked. Each was immediately renamed, classified as a tooling deviation, and closed `not_planned`. They contain no scientific or promotion evidence and changed no contract/branch state. The deviation is preserved rather than hidden.
