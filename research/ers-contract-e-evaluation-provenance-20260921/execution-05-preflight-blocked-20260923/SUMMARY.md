# Experiment 05 execution preflight — BLOCKED

The qualified PR #138 fixture artifact was downloaded by ID and its archive digest matched the value bound by #139/#140. The frozen #140 fixture-binding gate passed with the exact required subject identity. The frozen 05 receipt/source preflight then failed with `apparatus_freeze_receipt_path_not_canonical` (exit 1). Its pinned canonical path is the predecessor receipt path, so it cannot consume the #143 freeze receipt; the source also points at the predecessor ERS receipt path rather than PR #13. No Contract E evaluation or matrix control ran.

- Execution branch: `research/ers-contract-e-evaluation-provenance-05-execution-20260923`
- Pre-run commit: `e9e364acfaa763abe5971ac95debc850ffcbfc69` (exact #143 head)
- Disposition: `BLOCKED`
- Contract E evaluations: 0
- Sandbox: not created; no before/after comparison
- Scientific result: none

See [FAILURE.json](FAILURE.json), [MATRIX_PROGRESS.json](MATRIX_PROGRESS.json), the gate receipt, the exact preflight failure, and command/environment records. The raw gate receipt contains local scratch paths; the committed gate receipt and command record redact the scratch-root prefix while retaining the raw output digests.

References: [apparatus #143](https://github.com/camerontjs-dot/apparatus-contracts/pull/143), [apparatus #130](https://github.com/camerontjs-dot/apparatus-contracts/pull/130), [issue #137](https://github.com/camerontjs-dot/apparatus-contracts/issues/137), [ERS #13](https://github.com/camerontjs-dot/epistemic-research-system/pull/13).
