# Contract E RC3D R1 — Freeze / Execution Receipt

Status: **RESEARCH ONLY**

## Public candidate freeze

The RC3D public candidate and reference apparatus were frozen before hosted scientific execution.

R1 freeze commit:

`c8bc30a1b84207d94d35762808e462f1de024ffd`

Tree:

`96e7e27d509114760a31c413581a4fc20c5c7687`

Parent:

`5d5ffae2959d1cc4a34226cace18665d248f4f3d`

## Public normative aperture for the next fresh implementation

Exactly six public blobs:

| File | Blob |
|---|---|
| `SPEC-CANDIDATE.json` | `9c1090335d87eb5e4885a755542923b453c45317` |
| `SPEC-SHAPES.json` | `c3f293430ae6ddb87523d83ea6e5380b8b832136` |
| `SPEC-PARTICIPANT-BOUNDARY.json` | `8b1d292a240300388949d502e7b656e7a23a0b8e` |
| `BASIS-BINDING-SPEC.json` | `63c952c9c28f1be2173e69c79976c7dfe5880c10` |
| `RC3C-SPEC.json` | `f05feac88128fd693cca2fb25a0b2951654377eb` |
| `RC3D-INTERFACE-SPEC.json` | `61f46b09d391e7da4aed2491e428ec2ed226fe93` |

The sixth blob adds only the public consumer request surface. It does not expose why previous reproductions failed.

## Hidden evaluator apparatus frozen before the fresh implementation gate

| File | Blob |
|---|---|
| `VECTOR-MATERIALIZATION-SPEC.json` | `5c75e46a8eb4d7346128d84e21c25bdcea454ec4` |
| R1 `FROZEN-CASES.json` | `728b308d6eca0ebdf384e7de312c8a62b2f25577` |
| `validate.mjs` | `824916c40c863fd1e6e7f4d35943fd6e1077590b` |
| `R1-PREREGISTRATION.md` | `ca414f52077b34e1335cdc7e160926241ecf59c5` |

These artifacts are denied to the fresh implementer before its implementation freeze.

## Initial RC3D apparatus deviation

The first RC3D hosted execution from candidate head `5f424b29b27c0af1a2b821ae8dd85e4843baba51` was **INCONCLUSIVE** because a hidden case named nonexistent inherited case `HIST-N01-new-action-after-revocation`.

The actual frozen inherited identifier is `HIST-N01-revoked-new-exercise`.

R1 preregistered an apparatus-only correction. Workflow guards verified that `RC3D-INTERFACE-SPEC.json`, `VECTOR-MATERIALIZATION-SPEC.json`, and `validate.mjs` were unchanged from the initial freeze. Expected outcome and reason were also unchanged.

## Accepted hosted execution

Run:

`33395403242`

Job:

`99498611127`

Conclusion: **success**

Artifact:

- ID `9759103388`
- ZIP SHA-256 `1211d550902aab5baca5141d99d2493961e7b9db5a98db53c7868aa743b5ddd3`

Scientific failures: **0**

Terminal signals:

- `CANDIDATE_SURVIVED_RC3B`
- `RC3B_HARDENING_PASS`
- `CANDIDATE_SURVIVED_RC3C`
- `CANDIDATE_SURVIVED_RC3D`

## Internal disposition

**SUPPORTED FOR PROMOTION**

Promotion is bounded to a fresh different-model-family reproduction only.

## Fresh gate

Recommended independent implementer: **Antigravity / Gemini**.

Target repository/base:

- `camerontjs-dot/research-scaffold-harness`
- `548bfa81f65290eda15af658f647497679b840ef`

Required pre-reveal terminal marker:

`FRESH_RC3D_IMPLEMENTATION_FROZEN_BEFORE_REFERENCE_VECTOR_REVEAL`

A fresh pass may establish only that this six-blob RC3D research specification is independently recoverable by that implementation against the frozen heterogeneous evaluator corpus.
