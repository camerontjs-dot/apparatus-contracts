# First real-input evidence-to-decision preparation

This directory is a portable integration-preparation packet for Apparatus #137. It intentionally stops before private input selection and before independent trusted-target approval.

Contents:

- `SUBJECTS.json`: exact current source subjects and executable blob pins.
- `LOCAL_HANDOFF.md`: complete local execution handoff.
- `SELECTION.template.json`: unfilled private MainFrame claim selection.
- `TARGET_REVIEW.template.json`: unfilled independent target-review gate.
- `RUN_MANIFEST.template.json`: run-record skeleton; preparation alone must not complete it.
- `scripts/ers_to_gate.py`: deterministic identity/text/byte adapter, no evidence semantics.
- `scripts/verify_subjects.py`: offline exact checkout/blob verifier.
- `scripts/check_gate_output.py`: binds Gate Contract A back to ERS and requires the CAL #183 decomposition shape.
- `scripts/verify_target_review.py`: verifies target bytes/bindings and documented independent review.
- `scripts/run_current_subject.py`: admitted A->D execution, replay and source-substitution control.
- `tests/`: public synthetic/portable tests only.

The first real-input run is **not** part of this branch.
