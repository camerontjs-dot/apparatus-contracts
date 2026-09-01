# Contract A RC2 → Contract E Parent/Atom Pressure Test R2

Status: **PREREGISTERED SUCCESSOR / NOT EXECUTED**

Class: Research / pre-promotion falsification.

This is a named successor to original preregistration `b13ba252bb2a48336402baebbdf854f7874f52b7`. It strengthens the primary scoring boundary before any target A→E execution. It does not change the frozen Contract A subject, pipeline pins, Contract E oracle identities, or known Contract E exclusion boundary.

The predecessor harness cut `acd0dad3e61dd6b41124b1fa4f6b5c6cac4b3e2c` exposed only `FAILURE-001-PREFLIGHT-E-PATH.md`; no scientific target result was observed before this successor was frozen.

## 1. Why R2 exists

The original gate tests root/atom lineage, but the existing declared-`all_of` compatibility path naturally selects the declared atoms as downstream semantic targets. A green atoms-only path could therefore fail to discriminate a system that cannot preserve or consume the authoritative root proposition beside its atoms.

R2 adds a smaller, more discriminating test:

> Hold the same exact frozen declared Contract A object fixed and exercise three mechanical downstream projections of propositions already present in that object: parent-only, atoms-only, and parent+atoms. Compare exact target identity and downstream authority behavior without inventing a composition rule or allowing one proposition's authorization to stand in for another's.

## 2. Frozen authorities remain unchanged

### Contract A

- repository: `camerontjs-dot/apparatus-contracts`
- frozen research head: `2e50567c4da2a4046a15bddfc3feee31296da3fb`
- candidate tree: `54e5cfc659c574a1520ebc119d66e93d4f71ce34`
- `SPEC.md`: `2e7c37fca9aa6bdd1090fb527a663bdbe606ebcb`
- `schema.json`: `ff5cddfeacf4511136a3dd3b47db1a794b631cd9`
- validator: `42e5f5b3bf38d677445e9d01ea130ba604e53409`
- declared fixture: `c9e2e886d7fa2bcd3d979bfc6cdebd0de2763ce0`
- declared handoff SHA-256: `sha256:de23b0eb66b3316e85bd9fbc73f4dfe2b6525a1e73783fca8d6e1fbd9bb0189d`
- independent recovery terminal: `camerontjs-dot/research-scaffold-harness@dada22df71e1f3d26d7646a1cd7429cdab519318`, disposition `INDEPENDENTLY_RECOVERED`

### Pipeline

- Research Scaffold Harness: `548bfa81f65290eda15af658f647497679b840ef`
- Evidence Bundler: `6011789957f3294f97bff260069cfb5bb1c5772f`
- Claim Audit Lab: `53f0885b111676794d1bd20e10b91aa58b07e9d4`
- Decision Engine: `9f5ffc04a0184abe44dc49509058a7ff88893e30`
- Contract C release: `5fe55f9ed5d0ee9f026ca1b077e9d70ce0487ea1`
- Contract D release: `298a1a0f7b7b6d7712e11200d04faec3e1ca169b`
- Apparatus production base: `6a45ab2de09370f3048ffb083e25b487f81117e4`

### Bounded Contract E oracle

- held-out freeze: `a937f85aa5ebd6c9ae118b28828580684ff2986d`
- `AUTHORITY-CHAIN-CANDIDATE.json`: `b33f1da1400385470b4cfc6bf54061eae7051c9d`
- `authority_chain.py`: `73d09ecfb56ad26296ae261db1328ec7af9ea5b8`
- `evaluate.py`: `afaeba44f794d142517af7c000e0100391300d33`
- `heldout_cases.py`: `33bdbd39c5e7e9564c358dbac80e148637216e43`

No later Contract E implementation may silently replace these oracle bytes in this R2 run.

## 3. Known Contract E exclusions remain frozen

Primary scoring excludes:

1. Qualification subject/scope matching. PR #58 is terminal `QUALIFICATION_BINDING_UNDERDETERMINED`.
2. Surplus/multiple-conferring-record behavior after one complete match. PR #59 is terminal `PARTIAL_AGGREGATION_CLOSURE`.

Primary positive authority controls therefore use one complete independent conferring basis per exact request. No result that depends only on either excluded E question may promote or falsify Contract A.

## 4. Frozen pressure projections

Use the one exact declared `all_of` Contract A object and create only these research compatibility projections:

### P1 — parent-only

Downstream claim set contains exactly the frozen A `root_proposition`.

### P2 — atoms-only

Downstream claim set contains exactly the two frozen declared children, preserving each child ID, text, text hash, and sequence.

### P3 — parent+atoms

Downstream claim set contains exactly the frozen root plus the same two frozen children.

These are representation/selection probes only. They may not:

- mint a proposition;
- rewrite proposition text or IDs;
- infer a new parent/child relation;
- infer truth/support from decomposition;
- add a Contract E authority field to Contract A;
- treat `all_of` as an E authorization operator.

## 5. Parent/atom primary assertions

### Identity invariance

For every proposition appearing in two projections, its exact proposition ID and text SHA-256 must be identical in both projections and at every scored downstream target boundary.

Expected comparisons:

- parent in P1 == parent in P3;
- child A in P2 == child A in P3;
- child B in P2 == child B in P3.

A changed Contract C/B container identity is allowed because the projected claim set differs. The exact proposition target may not change.

### Independent authority

For each exact parent or atom target:

- one complete independent Contract E conferring basis targeted to that proposition must permit only according to the frozen E oracle;
- no basis must reject;
- Contract A declaration/producer/handoff material presented as a non-conferring supporting artifact must reject.

### Cross-use rejection

- an exact parent-target grant must not authorize child A or child B;
- an exact child-target grant must not authorize the parent;
- a child A grant must not authorize child B and vice versa where the target differs.

No parent/atom authority may be inferred by family resemblance, shared work ID, shared A handoff, or decomposition membership alone.

### No synthetic composition authorization

R2 must not compute an E-level `all_of` authorization by combining child decisions. It records separate target outcomes only.

A positive parent result and positive child results may be compared, but the harness must not claim that one set caused or conferred the other.

## 6. Resealing/metamorphic control

Create a research-only successor declaration by reversing the declared child order, assigning contiguous sequence values in the new order, and recomputing the A whole-object handoff hash.

Required properties:

- the successor declaration validates as its own object;
- its `handoff_sha256` differs from the frozen RC2 handoff;
- the old A binding must not silently accept the resealed successor as the same declaration;
- this control is not evidence that the successor inherits any old downstream E authority.

The successor object is never substituted for the frozen A scientific subject in the primary run.

## 7. Existing baseline controls remain required

R2 retains the original gate's primary controls for:

- `not_decomposed`, `failed`, `unknown`, and declared `all_of` states;
- exact A integrity and handoff behavior;
- real Evidence Bundler and CAL participation;
- Contract C and Contract D exact bindings;
- excluded compatibility metadata invariance;
- wrong Contract B binding;
- wrong target hash;
- wrong Contract C whole-object hash;
- no E basis;
- A-only non-conferring pseudo-basis;
- E target substitution;
- E source-lineage mismatch;
- forged A handoff rejection.

The parent/atom pressure matrix is additive. It does not waive any predecessor control.

## 8. Evaluator discrimination

Before R2 target interpretation:

1. rerun the frozen Contract A evaluator self-test;
2. rerun the frozen Contract E held-out evaluator and require its bounded supported state, zero false permits, and zero false rejects on its frozen corpus;
3. run matched positive/no-basis/A-only E controls against the new parent/atom projections;
4. require cross-target grants to fail for the intended target-binding reason;
5. classify any harness or evaluator defect before repair.

If a target result is observed and then evaluator or scoring code is changed, the modified code is a successor and cannot count as the original R2 result.

## 9. Failure classifications

Use the original classification vocabulary:

- `CONTRACT_A_DEFECT`
- `CONTRACT_E_DEFECT`
- `CONTRACT_E_UNDERDETERMINED`
- `PIPELINE_ADAPTER_DEFECT`
- `PIPELINE_STAGE_DEFECT`
- `EVALUATOR_DEFECT`
- `REPRESENTATION_ONLY_DIFFERENCE`
- `OUT_OF_SCOPE_DIFFERENCE`
- `UNRESOLVED_DISAGREEMENT`
- `AGREEMENT`

In particular, inability of a research compatibility projection to use a native production interface is not automatically a Contract A defect. Record whether the failure belongs to A semantics, the adapter, or the downstream stage.

## 10. R2 terminal gate

`SUPPORTED FOR PROMOTION` is allowed only if both the original primary gate and this pressure matrix survive without an unresolved in-scope A disagreement.

`FALSIFIED` applies if a failure attributable to frozen Contract A demonstrates identity/lineage loss, authority laundering, or unsafe parent/atom substitution under a legitimate downstream path.

`INCONCLUSIVE` applies if apparatus/evaluator limitations prevent discrimination or if the decisive condition falls inside frozen Contract E underdetermination.

A supported R2 result authorizes only the next minimal Contract A `2.0.0` production-transcription/equivalence step. It does not itself promote, merge, release, or tag Contract A.

## 11. Execution boundary

The hosted workflow must be manual-only and require the exact operator input:

`RUN_CONTRACT_E_PRESSURE_TEST`

Preparation commits, freeze receipt creation, or PR edits must not automatically execute the scientific run.

Stop after the preparation freeze until the operator explicitly authorizes execution.
