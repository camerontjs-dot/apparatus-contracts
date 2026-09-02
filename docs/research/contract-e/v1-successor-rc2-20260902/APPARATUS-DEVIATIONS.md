# RC2 successor apparatus deviations

## Initial hosted run — matrix-count sentinel mismatch

Run: `33673708516`

Head: `52fefe8fea3cbdb3b308033752bbf89bd6f40909`

Observed on Python 3.11 and 3.12 before the branch advanced:

- exact Contract D authority checks: pass;
- RC2 schema parse/compile: pass;
- RC2 core regression/adversarial suite: `CONTRACT_E_RC2_CORE_PASS=57`;
- all 112 substantive integration assertions preceding the final size sentinel completed;
- final assertion failed only because the harness required `COUNT >= 120` while the authored matrix contained 112 cases before that sentinel.

This was a test-apparatus cardinality defect. The preregistration required a replay/superset of the prior 101-case pressure surface; it did not require the arbitrary value 120.

Repair posture: do not lower or delete any semantic assertion. Add eight real malformed ExecutionIntent controls in a separate driver so the matrix reaches the intended larger surface while leaving the original 112 assertions unchanged. Re-run all runtimes from a new exact head.

No scientific disposition is inferred from run `33673708516`.
