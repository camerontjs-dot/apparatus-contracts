# Contract A RC2 → Contract E Parent/Atom Pressure Test R4 — Preregistration

Status: **PREREGISTERED / NOT_EXECUTED**

Class: successor apparatus repair after R3 `INCONCLUSIVE`.

This preregistration is frozen before any R4 parent/atom pressure target is executed. R3 remains preserved in `FAILURE-002-R3-PROJECTION-CONDITION.md` and is not repaired or reinterpreted as a scientific result.

## 1. Successor question

Can the already-preregistered R2/R3 parent-only, atoms-only, and parent+atoms pressure matrix execute when its mechanical legacy RSH transport shell uses an actually admitted frozen workflow condition, without changing any Contract A or Contract E scientific semantics?

## 2. Observed R3 apparatus defect

R3 failed at:

```python
template = rc2.build_fixture_write_input(rc2.PILOT, "pressure")
```

The frozen RSH fixture API admits only:

- `baseline`
- `format_only`
- `provenance_scaffold`
- `full_scaffold`

No pressure projection row was emitted before this exception.

## 3. Frozen repair

R4 is authorized to make exactly this scientific-executable change in `pressure_projection.py`:

```diff
- template = rc2.build_fixture_write_input(rc2.PILOT, "pressure")
+ template = rc2.build_fixture_write_input(rc2.PILOT, "baseline")
```

No new RSH workflow condition may be added. The pinned RSH repository may not be changed. No bespoke translation adapter may be introduced.

### Why `baseline`

The already-successful original A→C pipeline in this same experiment uses the exact same frozen `build_fixture_write_input(rc2.PILOT, "baseline")` call as its transport template before mechanically projecting Contract A propositions through the legacy RSH/EB surface.

The Contract A RC2 normal-context conformance implementation also treats workflow condition as excluded compatibility metadata rather than Contract A semantic authority: its hostile isolation path can replace `workflow_condition` while requiring the same Contract A handoff and targets.

For pressure projections, `mechanical_write_input()` replaces the template claims with the exact parent/atom proposition set. The selected fixture condition therefore supplies a valid frozen legacy manifest/source shell. All three projections receive the same template, holding that transport metadata constant across parent-only, atoms-only, and parent+atoms comparisons.

## 4. Scientific assertions remain frozen

R4 must not change the R2/R3 primary scientific matrix or expected outcomes. In particular:

- the exact same frozen real-pilot Contract A declared `all_of` subject remains the source object;
- parent identity must be identical parent-only vs parent+atoms;
- each atom identity must be identical atoms-only vs parent+atoms;
- exact independent E basis remains the positive control for each exact target;
- no E basis remains rejected;
- Contract A alone / supporting-artifact pseudo-authority remains rejected;
- parent grant on atom remains rejected;
- atom grant on parent remains rejected;
- sibling grant cross-use remains rejected;
- atom co-presence must not synthesize parent authorization;
- parent co-presence must not synthesize atom authorization;
- reversed child order remains a separately resealed Contract A declaration and old A binding must be rejected;
- wrong Contract B binding, wrong target hash, wrong Contract C object, forged A handoff, excluded-metadata laundering, source substitution, and lineage substitution controls remain unchanged.

Known Contract E underdeterminations remain excluded from primary scoring:

- qualification subject/scope matching from #58;
- surplus/multiple-conferring-record aggregation from #59.

## 5. Frozen subject identity remains R3

R4 does not alter `SUBJECT-IDENTITY-R3.json` or its pins.

Expected real-pilot Contract A handoff remains:

`sha256:de23b0eb66b3316e85bd9fbc73f4dfe2b6525a1e73783fca8d6e1fbd9bb0189d`

The public `valid-all-of.json` `f9d2...` fixture remains a distinct non-subject object.

## 6. Failure taxonomy

- If the successor still cannot construct the projections before pressure rows exist: `INCONCLUSIVE / APPARATUS_DEFECT`.
- If evaluators or downstream apparatus cannot discriminate the preregistered cases: `INCONCLUSIVE`.
- If target execution reaches the matrix and a Contract-A-attributable identity/lineage invariant fails: Contract A pressure falsification, promotion remains stopped.
- If target execution reaches the matrix and an exact Contract E authority boundary assertion fails, classify the disagreement before attributing it to A, E, an adapter, or evaluator.
- Only a fully executed matrix satisfying all primary assertions may report the preregistered pressure gate `SUPPORTED_FOR_PROMOTION`.

## 7. Promotion boundary

Even a supported R4 result does not merge, release, tag, or promote Contract A. It may authorize only the next minimal Contract A 2.0.0 production-transcription/equivalence step under EDR-004/#60.

## 8. Execution boundary

After the one-line executable repair and corresponding workflow/receipt pin updates are frozen, execution remains manual `workflow_dispatch` only and requires exactly:

`RUN_CONTRACT_E_PRESSURE_TEST`

No R4 scientific target may be run before that successor executable freeze is recorded.
