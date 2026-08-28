# Contract C RC2 producer sufficiency deviation 001 — code hygiene after scientific pass

## Run identity

- Apparatus branch head: `400b82891c6eacec472e7846d4da324cadb15976`
- Workflow run: `33208772556`
- Job: `98976514448`
- Evidence artifact: `9700739537`
- Artifact ZIP digest: `sha256:c97d76a92ffe567606055c2a094235a2678490e0381747e702959a958ddce943`

## Observation

The frozen semantic pins, CAL RC2-D reproduction, real Contract-B -> CAL producer execution, producer-gate evaluator, weak-system controls, and eight research tests all completed successfully before the workflow reached code hygiene.

The experiment emitted `CONTRACT_C_RC2_PRODUCER_GATE=SATISFIED` with zero scientific blockers and zero apparatus blockers. The evidence artifact was uploaded successfully.

The workflow then failed only because Ruff reported three research-code hygiene findings:

1. import `Iterable` from `collections.abc` rather than `typing` (`UP035`);
2. use `min()` rather than `sorted(...)[0]` in the tamper-fixture selector (`FURB192`);
3. remove the shebang from the non-executable Python runner (`EXE001`).

## Scientific effect

None of the three findings changes the frozen inputs, candidate semantics, intervention logic, expected results, thresholds, validators, or disposition rules. They were discovered after the scientific producer gate and evaluator tests had already completed.

Run `33208772556` is therefore preserved as a scientifically informative but workflow-deviating run. It is **not** being relabeled as the terminal clean CI receipt.

## Correction

Apply only the three hygiene-equivalent edits above, then rerun the unchanged experiment. Do not change the preregistration, candidate semantics, frozen upstream identities, evaluator criteria, or gate logic.

## Invalidated outputs

None for scientific interpretation. The run remains evidence that the encoded apparatus produced `SATISFIED`; however, terminal reconciliation must use a subsequent clean run if the formatting-only correction leaves the scientific result unchanged.
