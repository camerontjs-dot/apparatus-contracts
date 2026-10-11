# CAL RC5 / RC6 model-generated tool qualification

**Status: NOT QUALIFIED. Q13 actor admission is NOT AUTHORIZED.**

See [FINDINGS](RC5-RC6-FINDINGS.md) and the
[SANITIZED RECEIPT INDEX](SANITIZED-RECEIPT-INDEX.json).

This Draft is stacked on
[RC4 Draft PR #181](https://github.com/camerontjs-dot/apparatus-contracts/pull/181),
under [owner issue #173](https://github.com/camerontjs-dot/apparatus-contracts/issues/173).
Original RC4 Q01–Q12 controls, frozen source, first results, private gold and
scientific authority were not modified or rerun.

## Included source

The two numbered model_controller.py scripts executed separate first actual
Ollama-generated two-function experiments. The fixed CAL RC4 adapter and
network worker source were copied from frozen commit
e53fc412a0db007ba87c4d1720cee66b781fc89c without changes. Source must be
staged at the relative directory path:

    candidate/research/cal_fixed_ollama_launcher_rc4_20261010/

The two external_checker.py scripts preserve original first-result checking;
RC5's grader had a missing-manifest-field defect, whereas RC6's graded result
was 41 of 45 with exact-answer checks failing.

Each numbered test_rc_controller.py exercises 15 **model-free development unit
cases**, including all 52 listed RC4 scripted dispatch negatives. Scripted
refusals do not establish what the model will choose or how it responds to
prompt injection.

newline_calibration.py tests a native function call's final LF fidelity
without Docker. two_model_newline_probe.py compares pinned Qwen thinking-on
and Gemma4 thinking-off native function calls. The ordinary no-tool JSON text
probe is represented by its sanitized receipt identity in the findings.

## Observed finding

The model selected two permitted reads and one write in both RC5 and RC6. The
real network-none Docker worker executed them using the original fixed adapter.
The model-generated write argument omitted the final newline byte despite
explicit instructions. Both task-owned containers were removed after testing.
The stricter external verdict for RC6 is **NOT QUALIFIED**.

A separate ordinary JSON text response preserved the exact LF; the tested
native tool outputs did not. The exact internal cause within model generation
versus provider tool serialization remains unproven.

## Evidence custody and replay policy

Raw provider messages, tool arguments, Docker inspect records, private gold,
one-attempt ledgers and historical failed receipts stay under the local
controller's custody. They are deliberately not published here. Only sanitized
first-result hashes and statuses are shared.

**Never rerun or repair an already frozen first attempt.** Any reproduction
needs new controller-owned scratch source, exact frozen model/provider binary
and image identities, fresh worker and model session, new external expected
answers and a new one-shot grader.

The worker uses Linux arm64 Python 3.14, UID 65532, 256 MiB memory and swap,
network none, read-only root, exact /packet and 16 MiB noexec/nosuid/nodev
/scratch. Ollama is a trusted host component outside the worker.

This experiment does NOT qualify fresh blind CAL science, model process memory
erasure, all side channels, Docker Codex's native/MCP gateway surface, Q13 actor
admission, or a production release.
