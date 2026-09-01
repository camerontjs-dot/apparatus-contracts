# FAILURE-002 — R3 Pressure Projection Transport Condition

Status: **INCONCLUSIVE / PROJECTION_ADAPTER_DEFECT**

This record preserves the terminal disposition of Contract A RC2 → Contract E parent/atom pressure-test R3. It is not a Contract A or Contract E scientific result.

## Frozen run

- GitHub Actions run: `33555030121`
- Job: `100013640254`
- Artifact: `9818980174`
- Experiment head: `07b7912c802b785cb9f3d19e1a0be54f45055e47`
- Event: `workflow_dispatch`
- R3 executable cut: `c0d84c4b4efd3842a07512464d213b31eed71bcc`
- R3 readiness receipt: `07b7912c802b785cb9f3d19e1a0be54f45055e47`

## Observed completed stages

Before the failure:

- R3 exact Contract A subject-identity preflight: `PASS`
- frozen Contract A evaluator self-test: `PASS`
- frozen bounded Contract E evaluator self-test: `AUTHORITY_CHAIN_PROTOCOL_SUPPORTED_WITH_BOUNDS` over 82 cases
- original Contract A → Evidence Bundler → CAL → Contract C stage: `PASS`, receipt `sha256:b40befc27f95a9b397cc23ffae27d4ecdcfbcd62ebf3d0e2eccd97335b9f5a65`
- maintained Decision Engine → canonical Contract D stage: `PASS`, 7 decisions and 3 negative controls
- original bounded Contract E gate: `SUPPORTED_FOR_PROMOTION`, 7 rows

These completed predecessor stages do not substitute for the unexecuted parent/atom pressure matrix.

## Failure

The first parent/atom projection stage failed before producing any pressure row:

```text
research_scaffold_harness.fixture.FixtureError: Invalid condition 'pressure';
expected one of ('baseline', 'format_only', 'provenance_scaffold', 'full_scaffold')
```

Frozen failing call in `pressure_projection.py` blob `199ca57737c6368ae4eeae7e1a80d9354f65b719`:

```python
template = rc2.build_fixture_write_input(rc2.PILOT, "pressure")
```

The pinned RSH fixture API at commit `548bfa81f65290eda15af658f647497679b840ef`, fixture blob `ccba7894d6e4ce7564e54b449c13065c30c6eed1`, admits only the four frozen workflow conditions above.

`PRESSURE-PROJECTION-STAGE.txt` is empty because the exception occurred before the projection builder emitted a result. Pressure Decision and Contract E pressure-matrix stages were skipped. No sealed pressure-test run receipt was produced.

The uploaded artifact ZIP digest reported by Actions was:

`17cdfaf4e473cc26be207692d8660691a7ce061525e68e75100ae1313e1e3dd5`

## Classification

This is apparatus inability to construct the preregistered mechanical pressure views against the frozen RSH transport API. It does not establish agreement or disagreement for Contract A parent/atom identity, Contract E authority cross-use, or the A/E boundary.

Terminal disposition for R3:

`INCONCLUSIVE`

Do not relabel this run `SUPPORTED_FOR_PROMOTION` or `FALSIFIED`.

## Distinction from predecessor failure

This defect is distinct from `FAILURE-001-PREFLIGHT-E-PATH.md` / run `33514354077`, which failed before target execution because the Contract E checkout path was doubled. Both failures remain preserved independently.

## Successor constraint

Any successor may repair only the projection transport defect unless separately preregistered. It must not change Contract A RC2 authority, Contract E semantics, target identities, pressure expectations, or known-undertermination exclusions after observing this failure.
