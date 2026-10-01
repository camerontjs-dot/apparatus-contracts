# Real positive-path RC0

## Question

Can one frozen real public-source case traverse the unchanged current controlled A-to-D path and produce `supported -> clear -> candidate_for_authorization` without tuning Evidence Bundler admission or changing CAL, Contract C, Decision, or Contract D semantics?

## Frozen subjects

- Gate #54: `89ca88c7f0a661601f7eb798b6759667fa20ab3f`
- Contract A 2.0.0: `529c92b49a34d5c610618551a8737f019f9fa332`
- EB #120: `08ca896debd6d16fa21be2f178ed7cbe62395d00`
- Contract B 1.2.0
- CAL #184: `76b7c4dee6369cc6494486eb115a096e9da370b0`
- parent-bound C #121: `c5b1d757f3a0ad4f6e2c3f6dbdc2dd2d3c1403ec`
- inner C RC2: `b42c827acb0a9fe65353354d709add0e27bab307`
- resolver: `1d33e0612befcf8016816197c90c062373796df9`
- independent C consumer: `12e7e640b229619501960b1b89cf4716d8d985b3`
- Decision #86: `6cdb59c2ba41779ac954af56dd077574ba090013`
- Contract D 1.0.0: `298a1a0f7b7b6d7712e11200d04faec3e1ca169b`

## Frozen case

The committed packet uses a normalized factual representation of a 2026-03-17 U.S. Bureau of Labor Statistics publication.

Root claim:

`Black Men had a higher rate than White Men, and Black Women had a higher rate than White Women.`

The case was selected before any Gate, EB, or CAL outcome because the intended children are inside CAL's already-qualified `strict_comparison` target-authoring aperture.

## Protocol

1. Run exact Gate twice and require byte-identical Contract A.
2. Require valid A2, declared `all_of`, exactly two children.
3. Before EB runs, author and hash target bytes from the exact Gate child text using frozen CAL #184 target authoring.
4. Freeze those hashes in a pre-EB receipt.
5. Run EB #120 with unchanged default admission. No admission override.
6. Run the exact A-to-D path twice and require deterministic replay.
7. Run source-byte substitution rejection.
8. Do not change source, claim, target bytes, admission, CAL semantics, Contract C, Decision policy, or D after outcome exposure.
9. Do not reroll another case into this experiment.

## Dispositions

- `SUPPORTED_FOR_BOUNDED_REAL_POSITIVE_PATH`: exact case reaches supported / clear / candidate_for_authorization.
- `FALSIFIED_PREREGISTERED_REAL_POSITIVE_CASE`: exact case completes but does not reach that path under unchanged admission.
- `BLOCKED_BEFORE_EB`: Gate/A2/target authoring cannot produce the required frozen input.
- `INCONCLUSIVE_APPARATUS`: harness/environment failure prevents the discriminator.

A negative result is terminal for this case. It must not trigger tuning or source replacement.

## Nonclaims

This cannot establish general retrieval/admission adequacy, universal CAL correctness, unrestricted target authoring, production readiness, Contract E readiness, authorization, or execution.
