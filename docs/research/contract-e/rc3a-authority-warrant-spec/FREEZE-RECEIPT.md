# Contract E Authority / Warrant Specification RC3A — Freeze Receipt

## Freeze point

The candidate specification and adversarial fixture set were frozen before any executable RC3A validator was written.

- freeze commit: `c21454ad474a3beefa4bd7bd5baaf29f75188419`
- freeze tree: `23a7afec0a40d9a4acffb66065a3185841f34090`
- parent before fixture freeze: `72e839c212a42d21c792cc7c94279c4c9cc8423c`

## Frozen blobs

- `PREREGISTRATION.md`: `7cb70808fe7e8099129ddb56d5de523435922814`
- `SPEC-CANDIDATE.json`: `9c1090335d87eb5e4885a755542923b453c45317`
- `SPEC-SHAPES.json`: `c3f293430ae6ddb87523d83ea6e5380b8b832136`
- `SPEC-PARTICIPANT-BOUNDARY.json`: `8b1d292a240300388949d502e7b656e7a23a0b8e`
- `FROZEN-CASES.json`: `85bc7805d02a04c5a10b48b43a5f5a89f4e2f32a`

## Information state

This RC3A execution is intentionally not independent. Prior Contract E, CAL semantic-authority, Decision Engine action-authority, and cross-disciplinary authority research were available before the freeze and are legitimate hypothesis-generating inputs.

No claim of clean-room recoverability will be made from RC3A.

## Post-freeze rule

After this receipt, executable validators/tests may be added, but the frozen specification or cases MUST NOT be repaired and still called the same RC3A freeze if a scientific failure is observed. A material specification/fixture repair requires RC3B or another explicitly new freeze.

Mechanical workflow fixes that do not change candidate semantics may be repaired forward with the failed run preserved.

## Protected surfaces

RC3A is confined to `docs/research/contract-e/rc3a-authority-warrant-spec/` plus a dedicated research workflow. No canonical contract, production validator, release, or upstream repository behavior is modified.
