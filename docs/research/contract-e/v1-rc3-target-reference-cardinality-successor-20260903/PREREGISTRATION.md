# Contract E RC3 target-reference cardinality successor preregistration

Status: **research successor preregistration**

Production authorization: **false**

## Objective

Test the smallest successor repair for one defect in the frozen RC3 reference/evaluator apparatus: the public RC3 specification requires `jurisdiction.target_ref` to resolve to **exactly one validated request reference**, while the frozen RC3 reference implementation accepts any request in which the target identity is present at least once.

This is a candidate-reference/evaluator defect. It does not amend the frozen RC3 specification.

## Frozen predecessor evidence

Predecessor RC3 candidate head:

`72f44d206f4f7e64d6993ac85e2fe2f086afb381`

Predecessor candidate freeze receipt:

`51431b7423040c924c34b78a6c97cc6c7605ba8a`

Predecessor evaluator final seal:

`3943dd9e5e0711c894356fd4dfef25fd45507d91`

Accepted predecessor qualification:

- run `33688538939`
- job `100441660043`
- artifact `9869084680`
- digest `sha256:3d46a575db9b48c1fe1dd936870a8ace18944e9a5348e74d9d301433bed01be1`
- hidden cases `59`
- reference normative exact `59/59`
- seeded weak controls caught `14/14`

All predecessor commits, bytes, qualification evidence, and the earlier pre-seal weak-control failure remain immutable historical evidence.

Live RSH state at preregistration: Draft PR `camerontjs-dot/research-scaffold-harness#18` remains aperture-only at `91e3970caf7e8b03836df0882158e9e23ff3eb36`; no durable fresh independent RC3 implementation is present there. Therefore this successor does **not** claim that RC3 independent recoverability has already been established.

## Normative authority held fixed

The successor MUST reuse the exact frozen RC3 public specification and schema semantics. In particular:

- SPEC blob `8c142c6b86dd2512f1df0c19aa36dbef759d6c18` remains authoritative and unchanged;
- schema blob `87ec0e536de1d07b45f49c20b14bfa0c81f53a86` remains authoritative and unchanged;
- the relevant SPEC sentence remains: `jurisdiction.target_ref` is an immutable `identity_sha256` and MUST resolve to exactly one validated request reference.

No new Contract E authority semantic is introduced by this experiment.

## Controlled repair

Allowed change:

- create a separately named successor reference/evaluator apparatus that changes target-reference resolution from membership / at-least-one behavior to exactly-one validated-match behavior;
- add tests/evaluator cases required to discriminate that property;
- preserve all other predecessor behavior.

Forbidden change:

- editing or rewriting predecessor commits or seal receipts;
- changing SPEC or schema semantics;
- weakening request/reference structural validation;
- deleting, weakening, or reclassifying predecessor hidden cases or weak controls merely to obtain a pass;
- promotion, merge, tag, release, or production authorization.

## Required new discriminators

The successor candidate/evaluator must explicitly exercise:

1. **duplicate valid target identities**: distinct request-local `ref_id` values whose individually valid references have the same target `identity_sha256`; expected authorization: `false`;
2. **one valid plus one invalid duplicate**: a valid target reference plus a second duplicate-looking reference that fails reference validation; expected authorization: `false` because the request/reference collection is structurally invalid;
3. **target resolution with multiple matches**: a request containing unrelated valid references plus at least two independently validated references matching `jurisdiction.target_ref`; expected authorization: `false`.

The new evaluator must also include a seeded **membership-only / cardinality-blind** weak implementation reproducing the predecessor defect.

## Predecessor-regression requirement

The successor reference must remain normatively exact with the predecessor reference on every predecessor hidden case. Any predecessor normative divergence outside the newly added target-cardinality cases falsifies the minimal-repair claim.

## Qualification acceptance

Qualification is `PASS` only when all are true:

- successor reference is exact on the complete successor hidden corpus with zero normative mismatches;
- all predecessor 59 hidden cases remain covered;
- all three new target-cardinality cases are covered;
- the diagnostic-only variant remains supported;
- all predecessor 14 seeded weak controls are still falsified in their required failure classes;
- the new membership-only/cardinality-blind weak control is falsified on a target-cardinality case;
- no failing discriminator is removed, weakened, or reclassified after observing the result.

If the reference and membership-only weak control both pass the promotion-critical gate, evaluator discrimination is `INCONCLUSIVE` rather than repaired post hoc.

## Production-profile review

After scientific qualification, perform a separate production-profile review covering at minimum:

- trusted authority/root and Decision origins;
- integration and point-of-use binding;
- security and integrity/authentication boundaries;
- fail-closed handling and operational failure modes;
- Authorization versus execution versus verification boundaries;
- operational ownership, configuration authority, incident/rollback ownership, and audit responsibilities.

The production review may legitimately conclude `NOT_READY` or `INCONCLUSIVE`. Research qualification does not force a production-pass disposition.

## Stop rule

Stop without promotion if:

- any qualification acceptance condition fails;
- the repair requires a semantic change to the frozen SPEC/schema;
- the evaluator cannot discriminate the predecessor membership-only defect;
- production-profile review does not pass;
- fresh independent recoverability remains unevidenced.

Even if all research gates pass, production promotion remains a separate explicit operator-authority decision.
