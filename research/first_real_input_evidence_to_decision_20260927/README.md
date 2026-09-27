# First real-input evidence-to-decision preparation

This directory now has a separately identified strict single-item successor over PR #151.

The predecessor preparation remains preserved at PR #151 / `06fcfbedb49f598195f7be9bb5c7aa7d94c75312`. It pinned frozen ERS #4 and its project-tag scanning CLI. The current successor does **not** reuse that intake identity.

Current first-input intake authority:
- ERS Draft PR #15
- commit `3cf04f2defa07513ec2be4418d41698ca7aeebab`
- surface `harness/backlog_single_item_intake.py`
- exact one-item allowlist, no knowledge-tree scan
- frozen legacy `harness/backlog_intake.py` remains blob `976f7d506dcbd9363896894fd056e7b47a0f755c`

Contents:

- `SUBJECTS.json`: exact current source subjects and explicit predecessor identities.
- `LOCAL_HANDOFF.md`: single executable continuation; runtime health is checked before private input.
- `ERS_ALLOWLIST.template.json`: unfilled exactly-one-document admission.
- `SELECTION.template.json`: claim selection within that already admitted document.
- `TARGET_REVIEW.template.json`: unfilled independent target-review gate.
- `RUN_MANIFEST.template.json`: records strict subject identity and forbids first-case reroll.
- `scripts/ers_to_gate.py`: accepts only strict ERS RC1 inventory and copies identity/text/bytes.
- `scripts/check_gate_output.py`: preserves non-`all_of` as a stopped first-case outcome.
- `scripts/verify_subjects.py`: offline exact checkout/blob verifier.
- `scripts/verify_target_review.py`: exact target-byte/text binding plus documented independent review.
- `scripts/run_current_subject.py`: admitted A->D execution, replay and source-substitution control.
- `tests/`: public portable tests only.

No private MainFrame item, model service change, target approval, evidence admission, real A->D run, Contract E operation, or ERS write is part of this branch.
