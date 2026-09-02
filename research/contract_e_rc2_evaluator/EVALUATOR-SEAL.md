# Contract E RC2 successor evaluator seal

Status: **QUALIFIED AND SEALED FOR FRESH INDEPENDENT REPRODUCTION**

This seal authorizes the evaluator only for comparison against the frozen Contract E RC2 successor candidate identified below. It does not authorize promotion, production use, execution, or modification of a frozen independent implementation after evaluator reveal.

## Frozen candidate authority

- candidate commit: `44c919ea7f571b9a01ccf420ac710822c29476e4`
- `candidate/SPEC.md` Git blob: `90bfa10fda928796f9b14c6a430ee12e412d9e3e`
- `candidate/schema.json` Git blob: `ababc25a6dc9fc938251df57bea3ddcc3dd78850`
- `candidate/reference.py` Git blob: `fda14bb18c66c51747b7b506abb8df8a55a8d166`
- `candidate/test_candidate.py` Git blob: `7b51b8ad8e7523d29b45a153a6427934cb5661f5`
- integration profile Git blob: `6f19875d4f21765e02d51fef50ca53fae3daf177`
- integration pressure test Git blob: `7c84806033a80b93c08d51492dce265a29dc2b40`
- integration superset driver Git blob: `8cd53b679f39f6b08a5184eb3133f3c7d610eb2c`

## Qualified evaluator bytes

Accepted qualification execution head: `4d1dd1d433b4f3ab7b206304ba5b1df5a9847cb0`

The following evaluator code blobs are sealed:

- `research/contract_e_rc2_evaluator/evaluate_fresh.py`: `5b322f64530eef68db8170f37f1c563dc43b4559`
- `research/contract_e_rc2_evaluator/hidden_cases.py`: `0ee24146e5a242719ed4e7e99bfe7c36d6129f3d`
- `research/contract_e_rc2_evaluator/qualify_evaluator.py`: `889d453909b180de2bccdfa3133dabe41848161f`
- `research/contract_e_rc2_evaluator/qualify_integration_sensitivity.py`: `b8c7ee3d637d6ce4b223350157d98cefc7d1cfc3`

The branch subsequently added only the preserved apparatus-deviation record before this seal. The sealed evaluator code blobs above are unchanged from the accepted qualification execution.

## Qualification evidence

Accepted workflow run: `33684878972`

Accepted job: `100429831333`

Artifact: `9867677372`

Artifact digest: `sha256:1b1faf0c7f4283735d4f7f92d8a173f2b6adeec1cfa62c4cca6089f8a6f06997`

Observed qualification results:

- hidden evaluator cases: `61`
- reference normative exact matches: `61/61`
- reference false permits: none
- reference false rejects: none
- reference exceptions: none
- preservation failures: none
- diagnostic-shape failures: none
- cross-case dual-identity invariant: pass
- diagnostic-content semantic-identity invariance: pass
- seeded weak core controls caught: `14/14`
- frozen trusted-origin / point-of-use integration pressure: `121` cases, pass
- seeded integration shortcut controls caught: `10/10`
- frozen candidate checkout remained unmodified: pass
- exact Contract D 1.0.0 checkout remained unmodified: pass

## Preserved evaluator apparatus deviation

Initial qualification run `33675118769` is retained as a test-apparatus failure. Its core qualification and frozen integration pressure passed, but integration sensitivity crashed because the evaluator loader did not register a dynamically loaded module in `sys.modules` before executing a dataclass-bearing module on Python 3.12.

The repair changed only that loader behavior. It did not change the frozen candidate, hidden cases, semantic weak controls, integration profile, Contract D pins, or acceptance criteria.

## Reveal rule

Before implementation/test freeze, a fresh independent implementer MUST NOT receive or inspect:

- the sealed evaluator or hidden cases;
- the reference implementation or candidate tests;
- expected hidden outputs;
- prior RC1/RC2 implementation behavior or disagreement records;
- the integration pressure implementation or expected results;
- any prior explanation that would supply an inferred answer key beyond the public frozen specification/schema/task aperture.

After the independent implementation and prereveal tests are frozen and externally identified, a separate supervisor may reveal only the exact evaluator authority necessary for differential comparison.

No post-reveal repair may be counted as the same independent reproduction.
