# Preserved setup deviations

These attempts occurred before any Evidence Bundler outcome and before any CAL semantic result.

## Attempt 1 — dependency setup

- hosted run: `36938618438`
- job: `110624654202`
- attempted head: `0da47d8719ab5d32d839cd003fda4a733b8d5d28`
- exact authority verification: PASS
- stop: `pip check` found undeclared-installed runtime dependencies because the workflow had installed Gate, Evidence Bundler and CAL with `--no-deps`
- scientific Gate execution: not reached
- classification: `APPARATUS_DEPENDENCY_SETUP_DEFECT`

Successor correction installed the exact checked-out projects with their declared dependencies. No scientific input or criterion changed.

## Attempt 2 — Gate packet carrier

- hosted run: `36938843447`
- job: `110625362093`
- attempted head: `eee13decaf7fd4c18d83da79f18ee92269d8f587`
- exact authority verification: PASS
- dependency installation and `pip check`: PASS
- stop: production Gate runner raised `KeyError: 'request'` before constructing `AuthoringRequest`
- EB/CAL/Decision/D1 execution: not reached
- classification: `APPARATUS_GATE_PACKET_ENVELOPE_DEFECT`

The frozen semantic request had been committed without the production runner's outer packet envelope. Successor commit `9fb816476eb3d27b0ded07345646b4ab77223c47` nests the exact prior request object unchanged under `request` and adds empty `evidence_task` and `source_metadata` containers. Root claim, source representation, acceptance/falsification criteria, default-EB-admission rule and no-reroll rule are unchanged.

Neither attempt is evidence for or against the preregistered real-positive-path hypothesis.
