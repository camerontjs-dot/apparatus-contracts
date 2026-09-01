# Contract A RC2 → Contract E Parent/Atom Pressure Test — Freeze Receipt

Status: **PRESSURE_TEST_READY / NOT_EXECUTED**

Class: Research apparatus freeze / pre-promotion falsification.

This receipt freezes the complete executable pressure-test apparatus before operator-authorized target execution. It is not a scientific result and does not promote, merge, release, tag, or otherwise change Contract A production authority.

## 1. Frozen implementation cut

Repository: `camerontjs-dot/apparatus-contracts`

Branch:

`research/contract-a-rc2-contract-e-pipeline-gate-20260901`

Production base:

`6a45ab2de09370f3048ffb083e25b487f81117e4`

Frozen pressure-test implementation commit, immediately before this receipt:

`2ecd8b5b6c199bf23a706bbf3a41cc05ece70c95`

At that implementation cut, comparison with production base is ahead-only and contains exactly one research workflow plus files under:

`research/contract-a-rc2-contract-e-pipeline-20260901/`

No production contract, canonical schema, production validator, immutable release, or production Decision Engine code is modified by this pressure apparatus.

## 2. Frozen preregistrations

Original gate preregistration:

- commit: `b13ba252bb2a48336402baebbdf854f7874f52b7`
- path: `research/contract-a-rc2-contract-e-pipeline-20260901/PREREGISTRATION.md`
- blob: `e74be8bbae2b7161013caa73768a9c38db7d395f`

Parent/atom pressure successor R2:

- commit: `44e8a714596423fb372257e150be02c1ea8e8533`
- path: `research/contract-a-rc2-contract-e-pipeline-20260901/PRESSURE-TEST-PREREGISTRATION-R2.md`
- blob: `92a6c849a5a71a984ba3631b6f6c3be73af2d6a2`

R2 was frozen after the predecessor path failure but before any A→E target result was exposed.

## 3. Preserved predecessor failure

First frozen harness cut:

`acd0dad3e61dd6b41124b1fa4f6b5c6cac4b3e2c`

Hosted run:

- run: `33514354077`
- job: `99877508977`
- conclusion: `failure`
- scientific target execution: **not reached**

Failure record:

- path: `research/contract-a-rc2-contract-e-pipeline-20260901/FAILURE-001-PREFLIGHT-E-PATH.md`
- blob: `6ea68c0029c2ca86f9d3ab6efc8f8b0eb62d5186`
- classification: `PIPELINE_ADAPTER_DEFECT`

The successor fixes only the doubled Contract E checkout path in preflight. The failed run remains preserved and may not be counted as a Contract A or Contract E result.

## 4. Frozen executable apparatus blobs

Manual hosted workflow:

- `.github/workflows/contract-a-rc2-contract-e-pipeline-gate.yml`
- blob: `eeac5c15e0787445d279a87b5948556fb7c3342e`

Baseline gate:

- `pipeline_gate.py`: `8638b6af763df53342bdf684367e7105b08baa26`
- `decision_gate.mjs`: `3ebd0770a016394b14fb2b02cd088fa748df300b`
- `e_gate.py`: `64928127f192109c2eb415171fc0a4647f692d31`

Parent/atom pressure layer:

- `pressure_projection.py`: `199ca57737c6368ae4eeae7e1a80d9354f65b719`
- `pressure_decision.mjs`: `ed7eeb14b34293a08c25a504f0f9c7280582815f`
- `pressure_e.py`: `0b971c6dfbf5725fcdba461e2e74d017a30e5c37`

The pressure layer tests the same frozen declared Contract A object as:

1. parent-only;
2. atoms-only;
3. parent+atoms.

It scores exact per-target identity and authority behavior and attacks parent→atom, atom→parent, and atom→different-atom grant cross-use. It does not synthesize a parent authorization from atom authorizations or vice versa.

## 5. Frozen Contract A scientific subject

Repository: `camerontjs-dot/apparatus-contracts`

- research head: `2e50567c4da2a4046a15bddfc3feee31296da3fb`
- candidate tree: `54e5cfc659c574a1520ebc119d66e93d4f71ce34`
- public `SPEC.md`: `2e7c37fca9aa6bdd1090fb527a663bdbe606ebcb`
- public `schema.json`: `ff5cddfeacf4511136a3dd3b47db1a794b631cd9`
- validator: `42e5f5b3bf38d677445e9d01ea130ba604e53409`
- declared fixture: `c9e2e886d7fa2bcd3d979bfc6cdebd0de2763ce0`
- declared handoff SHA-256: `sha256:de23b0eb66b3316e85bd9fbc73f4dfe2b6525a1e73783fca8d6e1fbd9bb0189d`
- independent recovery terminal: `camerontjs-dot/research-scaffold-harness@dada22df71e1f3d26d7646a1cd7429cdab519318`
- independent disposition: `INDEPENDENTLY_RECOVERED`

No frozen A byte may be changed during execution and still count as this scientific subject.

## 6. Frozen pipeline pins

- Research Scaffold Harness: `548bfa81f65290eda15af658f647497679b840ef`
- Evidence Bundler: `6011789957f3294f97bff260069cfb5bb1c5772f`
- Claim Audit Lab: `53f0885b111676794d1bd20e10b91aa58b07e9d4`
- Decision Engine: `9f5ffc04a0184abe44dc49509058a7ff88893e30`
- Contract C release: `5fe55f9ed5d0ee9f026ca1b077e9d70ce0487ea1`
- Contract C tag object: `6bd135a948e407212b2e77ec18ac5c402f93565e`
- Contract C validator blob: `9c75ccfbf2223578a8d1a7bf0c39673b394fbea4`
- Contract D release: `298a1a0f7b7b6d7712e11200d04faec3e1ca169b`
- Contract D tag object: `6eadd688b482f3c9fce2ce5e7a2841089d852096`

## 7. Frozen bounded Contract E oracle

No canonical Contract E release is claimed.

- held-out freeze: `a937f85aa5ebd6c9ae118b28828580684ff2986d`
- `AUTHORITY-CHAIN-CANDIDATE.json`: `b33f1da1400385470b4cfc6bf54061eae7051c9d`
- `authority_chain.py`: `73d09ecfb56ad26296ae261db1328ec7af9ea5b8`
- `evaluate.py`: `afaeba44f794d142517af7c000e0100391300d33`
- `heldout_cases.py`: `33bdbd39c5e7e9564c358dbac80e148637216e43`

The workflow must self-test this exact evaluator before target interpretation.

Primary scoring explicitly excludes:

- Qualification subject/scope matching: `QUALIFICATION_BINDING_UNDERDETERMINED` from research PR #58.
- Surplus/multiple-conferring-record behavior after one complete match: `PARTIAL_AGGREGATION_CLOSURE` from research PR #59.

Exactly one complete independent conferring basis is used for primary E-positive controls.

## 8. Pressure-test controls frozen at this cut

The executable cut contains all original gate controls plus the R2 pressure matrix.

Original baseline includes:

- `not_decomposed`, `failed`, `unknown`, and declared `all_of` A states;
- exact A handoff/integrity checks;
- real Evidence Bundler and real CAL participation;
- Contract C proposition identity/text-hash preservation;
- real maintained Decision Engine → Contract D;
- wrong Contract B, wrong target hash, and wrong Contract C whole-object controls;
- excluded compatibility metadata invariance;
- independent E grant positive controls;
- no-E-basis negatives;
- A-declaration-as-non-conferring-basis negatives;
- E target/source lineage substitution negatives;
- forged A handoff rejection.

R2 additionally includes:

- parent-only vs parent+atoms proposition identity invariance;
- atoms-only vs parent+atoms atom identity invariance;
- parent-target grant → atom rejection;
- atom-target grant → parent rejection;
- child-A-target grant → child-B rejection and reverse;
- no synthetic `all_of` authorization inference;
- resealed reversed-child-order successor must have a different A handoff and must not pass the old A binding.

## 9. Manual execution gate

The workflow has **no push or pull-request trigger**. It is `workflow_dispatch` only.

Execution requires the exact operator input:

`RUN_CONTRACT_E_PRESSURE_TEST`

Preparation commits and this receipt must not execute the scientific run.

## 10. Post-freeze rule

After this receipt, changing any preregistration, workflow, baseline evaluator/harness file, pressure-test file, Contract A pin, pipeline pin, Contract E oracle identity, scoring boundary, or exclusion rule creates a successor pressure-test apparatus.

If a scientific target result is observed and code is then changed, the changed code cannot be counted as the same frozen run.

Failures must be classified before repair using the preregistered vocabulary. Inconvenient results are preserved.

## 11. Promotion boundary

Contract A production promotion remains **HELD**.

This receipt establishes only:

`PRESSURE_TEST_READY / NOT_EXECUTED`

A later supported hosted pressure-test result may authorize only the next minimal Contract A `2.0.0` production-transcription/equivalence step under EDR-004. It does not itself merge or release Contract A.
