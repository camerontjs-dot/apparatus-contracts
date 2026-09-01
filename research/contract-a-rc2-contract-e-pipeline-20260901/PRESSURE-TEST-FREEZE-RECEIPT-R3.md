# Contract A RC2 → Contract E Parent/Atom Pressure Test R3 — Freeze Receipt

Status: **PRESSURE_TEST_READY_R3 / NOT_EXECUTED**

Class: Research apparatus freeze / pre-promotion falsification.

This receipt freezes the R3 subject-identity correction and executable pressure-test apparatus before operator-authorized target execution. It is not a scientific result and does not promote, merge, release, tag, or otherwise change Contract A production authority.

## 1. R3 reason

Independent pre-execution verification found one record defect in R2/readiness material: the public candidate `valid-all-of.json` blob `c9e2e886d7fa2bcd3d979bfc6cdebd0de2763ce0` was listed beside the different real-pilot Contract A handoff `sha256:de23b0eb...` used by the executable harness.

The public fixture is valid RC2 material, but its own handoff is `sha256:f9d2f7be6eaaa21bcc032d3d91a9f9b42d645b15ed5130fc4b69807ba0ed6142`.

No scientific target result had been exposed when this mismatch was found. R3 therefore corrects subject identity before execution without changing the scientific question or scoring.

## 2. Frozen R3 subject identity

Subject identity manifest:

- path: `research/contract-a-rc2-contract-e-pipeline-20260901/SUBJECT-IDENTITY-R3.json`
- freeze commit: `98bbc43be8694284d67cb373bed488e74f7e16f4`
- blob: `f9b7c7fc389c4e852c5406ecab3e09ac9f6f3171`

R3 preregistration:

- commit: `28e61f51a217f25b028018dc7432477f327864f9`
- path: `research/contract-a-rc2-contract-e-pipeline-20260901/PRESSURE-TEST-PREREGISTRATION-R3.md`

Exact scientific subject:

- Contract A research head: `2e50567c4da2a4046a15bddfc3feee31296da3fb`
- candidate tree: `54e5cfc659c574a1520ebc119d66e93d4f71ce34`
- reference tree: `18b9cec2bc3063ecad17d12d55e49ea4dcb61ff8`
- reference generator blob: `1765b489590fca10462ad451847e0ddcb249f77f`
- generator call: `make_candidate("declared")`
- RSH source-packet commit: `548bfa81f65290eda15af658f647497679b840ef`
- RSH source loader blob: `0f7dd438df770239137b7ab11f796390b45155fe`
- source-content blobs: `616634d68b0b9026222eabe94696a56bf8d93140`, `51e538a85c8501c055393396c2bece121ccb0795`
- expected Contract A handoff: `sha256:de23b0eb66b3316e85bd9fbc73f4dfe2b6525a1e73783fca8d6e1fbd9bb0189d`

The workflow now reconstructs this exact real-pilot declaration and verifies its root/work/producer/decomposition/child/source identity against the frozen manifest before evaluator self-tests or any target execution.

## 3. Frozen executable R3 cut

Repository: `camerontjs-dot/apparatus-contracts`

Branch: `research/contract-a-rc2-contract-e-pipeline-gate-20260901`

Frozen executable implementation cut immediately before this receipt:

`c0d84c4b4efd3842a07512464d213b31eed71bcc`

Manual workflow:

- `.github/workflows/contract-a-rc2-contract-e-pipeline-gate.yml`
- blob: `936cd9412c7a181cd656b9a89d2aec5bc2a80597`

Relative to R2 executable cut `2ecd8b5b6c199bf23a706bbf3a41cc05ece70c95`, the scientific scoring scripts remain unchanged:

- `pipeline_gate.py`: `8638b6af763df53342bdf684367e7105b08baa26`
- `decision_gate.mjs`: `3ebd0770a016394b14fb2b02cd088fa748df300b`
- `e_gate.py`: `64928127f192109c2eb415171fc0a4647f692d31`
- `pressure_projection.py`: `199ca57737c6368ae4eeae7e1a80d9354f65b719`
- `pressure_decision.mjs`: `ed7eeb14b34293a08c25a504f0f9c7280582815f`
- `pressure_e.py`: `0b971c6dfbf5725fcdba461e2e74d017a30e5c37`

The workflow change adds only R3 identity pins, static blob checks, reconstruction verification, and R3 identity fields in the hosted run receipt.

## 4. Preserved predecessor records

The original preflight failure remains preserved as `PIPELINE_ADAPTER_DEFECT`:

- run `33514354077`
- job `99877508977`
- target execution not reached

R2 readiness remains preserved at:

- executable cut: `2ecd8b5b6c199bf23a706bbf3a41cc05ece70c95`
- readiness head: `08cb6dec9dfb95e4a7a10dbaebb8aa86af973735`

R3 does not rewrite either record.

## 5. Scientific assertions unchanged

The complete R2 pressure matrix remains intact, including:

- all four Contract A states through the pinned real pipeline;
- same-object parent-only, atoms-only, and parent+atoms projections;
- exact proposition identity invariance;
- exact-target independent E basis positive controls;
- no-basis and A-only pseudo-authority negatives;
- parent→atom, atom→parent, and sibling→sibling grant cross-use rejection;
- no synthetic E-level `all_of` authorization;
- resealed child-order successor as a distinct A binding;
- wrong B, target, C, A-handoff, metadata-laundering, source, and lineage controls.

Known Contract E underdeterminations remain excluded from primary scoring exactly as in R2.

## 6. Execution boundary

The workflow remains `workflow_dispatch` only with no push or pull-request trigger.

Execution requires exactly:

`RUN_CONTRACT_E_PRESSURE_TEST`

At the time the R3 executable cut was frozen, the experiment branch had zero `workflow_dispatch` runs. No preparation commit produced a scientific target result.

## 7. Promotion hold

Contract A remains unpromoted. A supported R3 result may authorize only the next minimal Contract A `2.0.0` production-transcription/equivalence step. It does not itself promote, merge, release, or tag Contract A.

**Stop boundary: R3 ready to execute, not executed.**
