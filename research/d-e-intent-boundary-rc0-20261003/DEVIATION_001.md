# Deviation 001 — evaluator repository-root calculation

**Classification:** apparatus failure before scientific case evaluation.

First hosted run: `37153699090`  
Job: `111292604848`  
Preserved artifact: `11285201657`

## Observed

The evaluator set `ROOT = HERE.parents[2]`. For:

`<checkout>/research/d-e-intent-boundary-rc0-20261003/run_bakeoff.py`

that resolves to the parent of the Git checkout rather than the repository root.

The first freeze check therefore failed at:

`git -C <parent-of-checkout> rev-parse <prefreeze>^{tree}`

with `fatal: not a git repository`.

No case in `CASES.json` was evaluated and no candidate result/disposition was observed.

## Correction

Change only evaluator repository-root resolution to `HERE.parents[1]`.

Protected unchanged objects:

- preregistration blob `e9a70c352892445abd3d339a4f898936bfa3dbf7`;
- cases blob `eccf3520996b6c73d5d4a289eba2fe6f7ccf16c2`;
- preimplementation head/tree;
- candidate definitions;
- expected materiality;
- weak-control rule;
- interpretation/disposition logic.

This is an apparatus-path correction before decisive exposure, not a scientific repair.
