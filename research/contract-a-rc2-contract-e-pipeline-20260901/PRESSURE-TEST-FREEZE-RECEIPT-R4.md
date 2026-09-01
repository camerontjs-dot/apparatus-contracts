# Contract A RC2 → Contract E Parent/Atom Pressure Test R4 — Freeze Receipt

Status: **PRESSURE_TEST_READY_R4 / NOT_EXECUTED**

Class: successor research apparatus freeze after R3 `INCONCLUSIVE`.

This receipt freezes the R4 projection-transport repair before any R4 parent/atom pressure target execution. It is not a scientific result and does not promote, merge, release, tag, or otherwise change Contract A production authority.

## 1. Preserved R3 terminal result

R3 remains terminally:

`INCONCLUSIVE / PROJECTION_ADAPTER_DEFECT`

Preserved evidence:

- run: `33555030121`
- job: `100013640254`
- artifact: `9818980174`
- R3 experiment head: `07b7912c802b785cb9f3d19e1a0be54f45055e47`
- failure record commit: `99e70712dc630dc69a56b2c4a3e16323cde7b971`
- failure record: `FAILURE-002-R3-PROJECTION-CONDITION.md`

R3 reached and passed subject preflight, both evaluator self-tests, the original A→C pipeline, Decision Engine→D, and original E gate, but failed before any parent/atom projection row because the frozen RSH fixture API rejected workflow condition `pressure`.

R3 is not `SUPPORTED_FOR_PROMOTION` and is not `FALSIFIED`.

## 2. R4 preregistration

R4 successor preregistration was frozen before the executable repair:

- commit: `7275c67dceefe2f23005e6b5f4bfc509a3c874cb`
- path: `PRESSURE-TEST-PREREGISTRATION-R4.md`

Authorized scientific-executable change was exactly:

```diff
- template = rc2.build_fixture_write_input(rc2.PILOT, "pressure")
+ template = rc2.build_fixture_write_input(rc2.PILOT, "baseline")
```

`baseline` is the same frozen RSH transport condition already used by the successful original A→C pipeline in this experiment. No RSH API or condition set was changed.

## 3. Frozen R4 executable cut

Repository: `camerontjs-dot/apparatus-contracts`

Branch: `research/contract-a-rc2-contract-e-pipeline-gate-20260901`

Frozen executable cut immediately before this receipt:

`1006445b4fced8d91b9fade933ea7679f507c2ce`

Exact repaired pressure projection:

- path: `research/contract-a-rc2-contract-e-pipeline-20260901/pressure_projection.py`
- blob: `40bd6981ea08479b7e47475ad6a3678697b71794`

Exact workflow:

- path: `.github/workflows/contract-a-rc2-contract-e-pipeline-gate.yml`
- blob: `68529c5935d1903703af34e571fa241ecc8711d5`

The workflow pins both the R4 preregistration commit and repaired pressure-projection blob before target execution.

## 4. Delta from R3 readiness

Comparison from R3 readiness head `07b7912c802b785cb9f3d19e1a0be54f45055e47` to R4 executable cut `1006445b4fced8d91b9fade933ea7679f507c2ce` contains exactly four changed paths:

1. `.github/workflows/contract-a-rc2-contract-e-pipeline-gate.yml` — six additive R4 pin/receipt fields;
2. `FAILURE-002-R3-PROJECTION-CONDITION.md` — preserved R3 failure record;
3. `PRESSURE-TEST-PREREGISTRATION-R4.md` — successor preregistration;
4. `pressure_projection.py` — one addition / one deletion, the preregistered `pressure` → `baseline` transport-condition replacement.

No Contract A candidate/reference/evaluator object changed. No Contract E candidate/protocol/evaluator/held-out object changed. `pipeline_gate.py`, `decision_gate.mjs`, `e_gate.py`, `pressure_decision.mjs`, and `pressure_e.py` are unchanged from R3.

## 5. Frozen subject and scientific matrix unchanged

The exact Contract A scientific subject remains the R3 real-pilot declaration with handoff:

`sha256:de23b0eb66b3316e85bd9fbc73f4dfe2b6525a1e73783fca8d6e1fbd9bb0189d`

`SUBJECT-IDENTITY-R3.json` remains unchanged.

The complete R2/R3 parent/atom matrix and expected outcomes remain unchanged. R4 does not add a composition rule, inheritance rule, or new Contract E authority semantics.

Known Contract E underdeterminations remain excluded from primary scoring:

- qualification subject/scope matching from #58;
- surplus/multiple-conferring-record aggregation from #59.

## 6. Execution boundary

At the time the R4 executable cut was frozen, the branch had exactly one `workflow_dispatch` run: R3 run `33555030121` at head `07b7912c...`, conclusion `failure`.

There was no `workflow_dispatch` run at the R4 executable cut and no R4 scientific target result had been exposed.

The workflow remains manual only. Execution requires exactly:

`RUN_CONTRACT_E_PRESSURE_TEST`

Do not rerun R3 as a substitute for R4; GitHub Actions rerun semantics would execute the preserved R3 SHA rather than this successor cut.

## 7. Promotion boundary

A fully executed supported R4 result may authorize only the next minimal Contract A 2.0.0 production-transcription/equivalence step under EDR-004/#60. It does not itself promote, merge, release, or tag Contract A.

A Contract-A-attributable falsification stops promotion. Apparatus/evaluator inability remains `INCONCLUSIVE`. Any disagreement must be classified before repair.

**Stop boundary: R4 ready to execute, not executed.**
