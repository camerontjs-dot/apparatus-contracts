# Contract E RC2 evaluator apparatus deviations

## Qualification run 33675118769

Evaluator branch head: `22f621330bf6f4d824b147ab3f368fb5d69c6e7f`

Observed:

- frozen RC2 candidate identity checks passed;
- Contract D 1.0.0 identity checks passed;
- frozen RC2 reference scored `61/61` normative exact matches with no false permits, false rejects, exceptions, preservation failures, or diagnostic-shape failures;
- all 14 seeded weak core implementations were caught;
- frozen 121-case trusted-origin / point-of-use integration pressure passed;
- integration sensitivity qualification crashed before executing its controls because the evaluator's dynamic loader did not insert the loaded module into `sys.modules` before `exec_module`, causing Python 3.12 `dataclasses` to fail while loading the frozen integration profile.

Classification: **test-apparatus defect; no scientific disposition**.

Repair boundary: change only the evaluator dynamic loader by registering the module in `sys.modules` before execution. Do not modify the frozen RC2 candidate, hidden cases, weak semantic controls, frozen integration profile, Contract D pins, or acceptance criteria. Re-run qualification from a new evaluator head.
