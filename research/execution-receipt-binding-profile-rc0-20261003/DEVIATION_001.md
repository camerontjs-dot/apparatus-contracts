# Deviation 001 — evaluator repository-root calculation

**Classification:** apparatus failure before scientific case evaluation.

First hosted run: `37153859833`  
Job: `111293085549`

## Observed

The evaluator set `ROOT = HERE.parents[2]`. For:

`<checkout>/research/execution-receipt-binding-profile-rc0-20261003/run_bakeoff.py`

that resolves to the parent of the Git checkout rather than the repository root.

The first freeze check failed at `git -C <parent-of-checkout> rev-parse ...`.

No case in the frozen matrix was evaluated and no candidate result/disposition was observed.

## Correction

Change only evaluator repository-root resolution to `HERE.parents[1]`.

Protected unchanged objects:

- preregistration blob `027b46d1d0a70b0eb56c0a6dc39afb7f66062944`;
- cases blob `d93b6be433280e43c8b92f41e68fbe1de62d4d48`;
- preimplementation head/tree;
- candidate definitions;
- expected outcomes;
- weak-control rule;
- interpretation/disposition logic.

This is an apparatus-path correction before decisive exposure, not a scientific repair.
