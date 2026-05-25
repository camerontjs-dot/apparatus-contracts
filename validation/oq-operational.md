# OQ: Operational Qualification

status: verified
last_updated: 2026-05-22

Purpose: verify that each verifier in the apparatus-contracts suite behaves correctly on synthetic positive and negative inputs, and that the codebase passes style checks.

This is a validation-inspired record for a non-regulated portfolio context. It does not claim FDA, EMA, GxP, GMP, CSV, or regulated-compliance status.

## Scope

- Vocabulary drift verifier (`validators/verify_vocabulary.py`): canonical/consumer hash check, `.contract-version` pin check, absent-consumer behavior with and without `--strict`.
- Spec/canonical parity verifier (`validators/verify_spec_vocabulary.py`): controlled-vocabulary table parsing, divergence detection on both directions, missing-heading error.
- Contract-integrity verifier (`validators/verify_contract_integrity.py`): `CONTRACT_VERSION` checks, `SHA256SUMS` recompute, Pydantic-model schema validation, `--against-pin` enforcement, artifact-type auto-detection.
- Style compliance: `ruff check .` passes across the asset.

## Protocol

| Step | Command or inspection | Expected result | Date run | Result | Evidence reference | Status |
| --- | --- | --- | --- | --- | --- | --- |
| OQ-001 | `make test` | Full pytest suite passes; 20 cases collected across three test files. | 2026-05-22 | 20 passed in 0.15s (9 integrity, 5 spec-vocabulary, 6 vocabulary). | `tests/`; `../docs/verification.md` | verified |
| OQ-002 | `pytest tests/test_verify_vocabulary.py -v` | Six cases pass: real-consumer pass, synthetic-layout pass, drift detected, pin mismatch detected, absent silent without `--strict`, absent fails with `--strict`. | 2026-05-22 | 6/6 passed. | `tests/test_verify_vocabulary.py` | verified |
| OQ-003 | `pytest tests/test_verify_spec_vocabulary.py -v` | Five cases pass: real-spec parity, drop from YAML detected, drop from spec detected, parser finds eight known vocabularies, missing-heading raises. | 2026-05-22 | 5/5 passed. | `tests/test_verify_spec_vocabulary.py` | verified |
| OQ-004 | `pytest tests/test_verify_contract_integrity.py -v` | Nine cases pass: real C-A pass, missing CONTRACT_VERSION, invalid CONTRACT_VERSION, `--against-pin` mismatch, missing SHA256SUMS, tampered file, invalid vocabulary value, missing required field, unknown artifact type. | 2026-05-22 | 9/9 passed. | `tests/test_verify_contract_integrity.py` | verified |
| OQ-005 | `.venv/bin/ruff check .` | All Python files pass ruff style checks. | 2026-05-22 | `All checks passed!` | `pyproject.toml`; `../docs/verification.md` | verified |
| OQ-006 | CLI smoke: tamper a tmp copy of the handoff-demo and run `python -m validators verify-integrity`. | Verifier reports `FAIL` with file-level hash mismatch and exits 1. | 2026-05-22 | `FAIL (1 error)` with `claims.yaml: hash mismatch (expected eb5ff57d…, got 9c252978…)`; exit code 1. | `../docs/verification.md` | verified |
| OQ-007 | `make verify` | `verify-vocabulary` and `verify-spec-vocabulary` both pass against the real apparatus state. | 2026-05-22 | Vocabulary verification passed (3 consumers `[OK]`); spec/canonical parity OK (8 vocabularies). | `Makefile`; `../docs/verification.md` | verified |
| OQ-008 | CLI smoke: tmp-copy a v1.0.0 C-A artifact, bump `CONTRACT_VERSION` to `1.1.0`, regenerate the SHA256SUMS entry, run `verify-integrity`. | Verifier accepts the v1.1.0 artifact under the dual-acceptance pattern. | 2026-05-22 | `result: OK` (8 files checked); accepted. | `../docs/verification.md` § v1.1.0 acceptance | verified |
| OQ-009 | CLI smoke: `verify-integrity --against-pin 1.0.0` against the bumped v1.1.0 artifact. | Verifier fails with a structured pin-mismatch error and exits 1. | 2026-05-22 | `FAIL (1 error)`: `CONTRACT_VERSION is '1.1.0' but --against-pin requires '1.0.0'`; exit 1. | `../docs/verification.md` § v1.1.0 acceptance | verified |

## Acceptance Criteria

OQ passes when every row above is `verified` or carries an accepted deviation in `deviation-log.md`.

## Record

OQ passed on 2026-05-22 against the v1 release candidate, including the v1.1.0 vocabulary addendum. No OQ-blocking deviations were recorded.
