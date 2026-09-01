# Contract A RC2 Immutable Candidate Freeze Receipt

Freeze status: **FROZEN FOR FRESH INDEPENDENT REPRODUCTION**

Research disposition supported by this receipt: `SUPPORTED FOR FRESH INDEPENDENT REPRODUCTION`.

This is a research freeze, not Contract A production promotion, release, merge authorization, or canonical version assignment.

## Freeze boundary

This receipt freezes three logically separate surfaces. Any later mutation to one of these trees creates a successor object and may not be counted as the same frozen candidate/reference/evaluator.

### 1. Public candidate authority

Tree SHA:

`54e5cfc659c574a1520ebc119d66e93d4f71ce34`

Frozen files / Git blob identities:

- `SPEC.md` → `2e7c37fca9aa6bdd1090fb527a663bdbe606ebcb`
- `schema.json` → `ff5cddfeacf4511136a3dd3b47db1a794b631cd9`
- `validate.py` → `42e5f5b3bf38d677445e9d01ea130ba604e53409`
- `fixtures/valid-all-of.json` → `c9e2e886d7fa2bcd3d979bfc6cdebd0de2763ce0`
- `fixtures/valid-failed-decomposition.json` → `b54dfee6b48f2d6a78d48d723409fdbc314202fd`
- `fixtures/valid-undecomposed.json` → `5bf59a4b310496fda9f8bdc9f1a88aa9345660b5`
- `fixtures/valid-unknown-decomposition.json` → `873536d219d46aa846466a836e65db312e82e574`
- `fixtures/invalid-forbidden-semantic-field.json` → `3cc1fb6790e3a58f54641c8ad77dc4737100f0a1`
- `fixtures/invalid-missing-proposition-id.json` → `68162754ec00dc00c838ad52c7150441aa8e8c08`
- `fixtures/invalid-source-content-hash.json` → `113c668d517325a05e959f15a64c06f939153f97`

The evaluator is not inside this public-candidate tree.

### 2. Reference / normal-context experiment authority

Tree SHA:

`18b9cec2bc3063ecad17d12d55e49ea4dcb61ff8`

Frozen files / Git blob identities:

- `run_conformance.py` → `1765b489590fca10462ad451847e0ddcb249f77f`
- `run_conformance_v2.py` → `3fbaa3882921c13286c07c81751dc6527e6be348`
- `run_conformance_v3.py` → `27199e94f80b4f8686d4c460fd7b86eccb00e8eb`

The failed predecessors remain frozen alongside V3. They are evidence, not dead code to be erased.

### 3. Evaluator / public-conformance authority

Tree SHA:

`5d7eb3e3a9a98ba1626118a5e06a018c02fa81ec`

Frozen file / Git blob identity:

- `test_candidate.py` → `c5e489033ffc566511e70fa14192a0f88a62ab6a`

This evaluator is deliberately separate from the clean-room public aperture.

## Exact pre-freeze repository authorities

- Apparatus production `main`: `6a45ab2de09370f3048ffb083e25b487f81117e4`
- RC2 research branch head whose separated surfaces were tested: `805bf5e2b1766dad23f97dd301e0420b591dd6c8`
- GitHub synthetic PR merge tested: `8d1471c54d0cbd005bed21a8aebc28f01884b83c`
- Research Scaffold Harness: `548bfa81f65290eda15af658f647497679b840ef`
- Evidence Bundler: `6011789957f3294f97bff260069cfb5bb1c5772f`
- Claim Audit Lab: `53f0885b111676794d1bd20e10b91aa58b07e9d4`

Production `main` was re-read immediately before freeze preparation and remained unchanged at the stated SHA.

## Accepted normal-context evidence

Dedicated Contract A RC2 workflow:

- run: `33471728968`
- job: `99742721714`
- result: PASS
- artifact ID: `9786765413`
- artifact name: `contract-a-minimality-rc2-33471728968`
- artifact ZIP SHA-256: `82f07a926b351916a5f3eddedac54ac96b959fd39d3d4186c26d766662fb7454`

The workflow recorded and tested the exact candidate/reference/evaluator tree SHAs above.

Untouched canonical Contract B 1.2 production acceptance on the same research state:

- run: `33471728973`
- job: `99742693704`
- result: PASS

## Candidate-level identities observed in the real producer path

- declared `all_of`: `sha256:de23b0eb66b3316e85bd9fbc73f4dfe2b6525a1e73783fca8d6e1fbd9bb0189d`
- undecomposed: `sha256:2816c5e36d70fc4d7a48223500be8ff480fc535b6eac7a74c6f5f11057550148`
- failed decomposition: `sha256:fe4c0ea6a3955594c74d9ea4d40cd4a0542baa836f53561332aa7f2108da39d4`
- unknown decomposition: `sha256:ada57eddefb02c65f6af65394a9f5e43e7a08bde1c3f37453668aa7102788f25`

## What the freeze supports

Normal-context evidence supports that the frozen candidate is sufficiently precise to expose for an independent recoverability test because:

1. required proposition/work/source/integrity identities fail closed when removed or substituted;
2. undecomposed, failed, and unknown states remain explicit and distinct;
3. declared `all_of` parent/child identity survives the real RSH → EB → Contract B 1.2 → CAL explicit-proposition path;
4. semantic-looking legacy observations can satisfy current compatibility structure without changing EB evidence identity or CAL source-contract proposition authority when mutated hostilely;
5. the current legacy path's incompatibilities are recorded rather than hidden;
6. evaluator failures and the zero-hit auxiliary BM25 result are preserved;
7. the candidate makes no retrieval-completeness, decomposition-correctness, CAL-NLI-quality, Contract E, or production-promotion claim.

## Strongest remaining falsifier

Independent recoverability remains untested by this contaminated context.

A fresh implementer receiving only the sanitized public aperture must independently recover the validation and consumer behavior. A prereveal disagreement on canonicalization, missing-state semantics, immutable binding, undecomposed behavior, or declared `all_of` lineage is evidence against the recoverability claim and must be preserved.

## Contamination rule after freeze

This thread and the normal-context branch contain reference reasoning, evaluator behavior, compatibility conclusions, ablation outcomes, and prior failures. They are contaminated for the independent implementation.

The fresh implementer must not receive:

- the reference tree;
- the evaluator tree;
- field-family/ablation outcomes;
- compatibility conclusions;
- hidden expected outputs;
- prior implementation reasoning;
- this surrounding conversation;
- any promotion conclusion.

Only a separately prepared sanitized public aperture may be used before its implementation freeze.

## Promotion boundary

This receipt authorizes **only** the next research phase: fresh independent reproduction.

It does not authorize:

- canonical Contract A promotion;
- assigning `1.1.0`, `2.0.0`, or any other release number;
- merging this research PR as production authority;
- Contract E semantics;
- Evidence Bundler production redesign;
- CAL semantic-policy changes.
