# Cross-Repository Authority Interface RC2 — Preregistration

## Classification

Research / apparatus-contract architecture falsification.

This experiment consumes frozen outputs produced natively in Evidence Bundler, Claim Audit Lab, and Decision Engine. It does not define Contract E.

## Question

Can independently produced stage-jurisdiction descriptors and semantic-authority receipts share a minimal structural authority envelope while remaining unable to authorize across domain boundaries?

## Frozen producer evidence

- Evidence Bundler PR #46, head `45702fc80f529654d4745760b071132131d3a509`, run `33321329523`.
- CAL PR #46, head `4000f37b1f861cca696cb9852722fee8f4f50f0b`, run `33321461944`.
- Decision Engine PR #22, head `e4d96071e2870d3edbb87140f23824e1d4dee580`, run `33321116949`.

The exact output artifact digests are recorded in `FROZEN-NATIVE-OUTPUTS.json`.

## Hypothesis

A reusable authority interface can normalize:

- subject/mechanism;
- authority domain;
- typed operation;
- exact target;
- currentness;
- applicability;

without allowing:

- source access -> evidence relevance/support;
- evidence admission -> CAL support;
- CAL assessment mandate -> semantic validity;
- numeric semantic authority -> Decision/execution authority;
- Decision authority -> source-boundary truth;
- source-boundary authority -> numeric validity;
- citation authority -> task authority.

## Falsifier

Fail if the independent consumer must inspect domain semantic payload to distinguish these jurisdiction boundaries, or if cross-domain substitution can pass the normalized authority check.

A pass supports a shared **interface pattern**, not a universal authority evaluator or production Contract E schema.
