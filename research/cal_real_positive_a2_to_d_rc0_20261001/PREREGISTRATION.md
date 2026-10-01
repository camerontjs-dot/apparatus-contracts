# Real positive A2→D RC0

## Decision

Determine whether the **same frozen real BLS evidence representation** from predecessor PR #155 can earn the bounded positive downstream path when the Gate-authoring question is removed and a valid predeclared Contract A 2.0 `declared all_of` object is supplied:

`A2 -> EB #120 -> B1.2 -> CAL #184 -> parent-bound C #121 -> independent C consumer -> Decision #86 -> D1`

Desired case-specific outcome:

`supported -> clear -> candidate_for_authorization`

## Why this is a separate successor

PR #155 terminated `BLOCKED_BEFORE_EB` because Gate #54 deterministically abstained with:

`NO_UNIQUE_WARRANTED_DECLARATION:unsupported:NO_BOUNDED_FRAME_PARSE`

EB never ran. This successor does **not** repair or relabel that result. It asks the smaller downstream question that #155 could not reach.

The source representation is unchanged from #155. The only new scientific subject is the explicitly frozen, independently A2-valid decomposition below.

## Frozen subjects

- Apparatus base: `c3563cff66d2c85dcbf575c693056e2d8e4563d4`
- Contract A 2.0.0 authority: `529c92b49a34d5c610618551a8737f019f9fa332`
- Evidence Bundler #120: `08ca896debd6d16fa21be2f178ed7cbe62395d00`
- Contract B 1.2.0
- CAL #184: `76b7c4dee6369cc6494486eb115a096e9da370b0`
- parent-bound Contract C #121: `c5b1d757f3a0ad4f6e2c3f6dbdc2dd2d3c1403ec`
- inner Contract C RC2: `b42c827acb0a9fe65353354d709add0e27bab307`
- resolver: `1d33e0612befcf8016816197c90c062373796df9`
- independent C consumer: `12e7e640b229619501960b1b89cf4716d8d985b3`
- Decision #86: `6cdb59c2ba41779ac954af56dd077574ba090013`
- Contract D 1.0.0: `298a1a0f7b7b6d7712e11200d04faec3e1ca169b`

## Frozen A2

`CONTRACT-A.json` is committed before any EB outcome and must validate under released A2 unchanged.

Root:

> Black Men had a higher rate than White Men, and Black Women had a higher rate than White Women.

Declared `all_of` children:

1. `Black Men had a higher rate than White Men.`
2. `Black Women had a higher rate than White Women.`

The source representation is the same BLS 2025 union-membership representation used in #155.

## Hard protocol

1. Validate exact committed A2 under released Contract A 2.0 authority.
2. Before EB execution, author targets from the exact committed child IDs/text using frozen CAL #184 target authoring.
3. Require both targets to be inside the already-qualified `strict_comparison` family and freeze their exact bytes/hashes.
4. Run EB #120 with **unchanged default admission**. No `--admission` override.
5. Execute the exact A2→D path twice.
6. Require deterministic replay across EB package/B tree, CAL parent, Contract C and D1 bytes.
7. Run the unresealed source-byte substitution control.
8. Do not change A2, child text, source bytes, target bytes, EB admission, CAL semantics, Contract C, Decision policy/materializer or D1 after first EB outcome.
9. No third case/source is pooled into this experiment.

## Acceptance

`SUPPORTED_FOR_BOUNDED_REAL_A2_TO_D_POSITIVE_PATH` only if:

- committed A2 validates;
- both frozen targets author as `strict_comparison`;
- EB accepts enough relationships for both children to support the parent;
- CAL parent = `supported`;
- Decision = `clear`;
- D1 consumer = `candidate_for_authorization`;
- replay is byte-identical on required identities;
- source substitution rejects before EB artifact emission;
- Contract E, Authorization and execution remain false.

## Legitimate negative outcomes

- `FALSIFIED_REAL_A2_TO_D_POSITIVE_CASE`: exact case completes downstream but does not reach the positive path under unchanged admission.
- `BLOCKED_BEFORE_EB`: committed A2 or target freeze cannot satisfy its exact preconditions.
- `INCONCLUSIVE_APPARATUS`: an apparatus/environment failure prevents the downstream discriminator.
- `SUPPORTED_FOR_BOUNDED_REAL_A2_TO_D_POSITIVE_PATH`.

A negative result is terminal for this exact case. Do not tune admission or rewrite child text after exposure.

## Nonclaims

Even a supported result would not establish Gate coverage, general retrieval/admission adequacy, universal CAL correctness, unrestricted target authoring, production readiness, Contract E readiness, Authorization, or execution.
