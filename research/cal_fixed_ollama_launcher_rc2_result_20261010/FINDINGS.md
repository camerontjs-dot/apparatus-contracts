# Frozen RC2 first result: checker defect at Q04

**Disposition:** `BLOCKED_FIRST_FAILURE_Q04_CHECKER_DEFECT`.
**Actor admission:** `NOT_JUSTIFIED`.

## Observed
- Prep commit `a9a91f0ebd683c870ef8d26a16932a79697c2f94`; scientific candidate `290bee5a163f70f5d7bb42662131dd5b0375a761`, frozen before exposure at `sha256:b96731112f79768ccb76c6b9802a1fc13b1feaa196747ac4de8b8156a1b2c46c`. No candidate bytes changed.
- A separate **pre-freeze** positive availability receipt recorded Ollama 0.40.0 at controller loopback `127.0.0.1:11434`. This is not a Q03 pass by itself.
- The first and only Q01–Q13 qualification attempt exited **1**, stopping `2026-10-10T01:24:30.570624Z` at Q04, `KeyError: 'pins'`. Zero inference calls; one Docker worker created and removed by owned cleanup.
- Q03 **PASS_BOUNDED**: actual provider HTTP 200 render-only response, exactly two declared functions, full rendered prompt byte-identical to frozen `sha256:6a85f69698413ac5a4a92922479bbd41cddcd07dbc2ec86b1b8501dc9f7174ea`.
- Q01 **PASS_BOUNDED**: actual packet staging with two exact synthetic file inputs and code-isolated same-controller checker. Q02 **PASS_BOUNDED**: actually copied entire synthetic source, including outside-world sentinel; checker rejected intended `EXTRA_FILE`.
- Q04 **FAIL_OR_UNKNOWN**: the controller tried to read absent `freeze["pins"]` while inspecting the actual worker. `FREEZE.json` intentionally binds the private runtime pins by SHA only; pin bytes live outside the repository. This is an evaluator/checker defect, not an observed Docker isolation failure. No Q04 conformance is inferred.
- Q05–Q11 **NOT_RUN_AFTER_FIRST_STOP**; Q12 `OWNED_CLEANUP_ONLY`, fresh reset `NOT_RUN`; Q13 **BLOCKED**.
- Controller-only receipt index contains **196** actual raw entries. A separate readback matched exact filenames, sizes and SHA-256. Raw first-failure `sha256:cb5d8f65c3592c4ce73d409dc53d2f88f65191078a53af710802bade8f01c0d7`; first result `sha256:ffeef6ef62c2085c1e1527abbe9f16ef709a2fc1e152684eeda66e6cd5920551`; index `sha256:a6d6491edc09e783421486520ab452d7e85090e7d36a0119741223f940d6b861`.
- The one-shot ledger reservation is retained. One exact created container was recorded as removed; an independent post-stop Docker listing showed none. Cleanup-only is not a two-worker reset.

## Falsifier and next bounded step

The only literal `freeze["pins"]` lookup in the frozen RC2 controller occurs in Q04 when checking Docker image identity. A **new** successor must use the already-validated, SHA-bound external `self.pins["image_id"]` instead, and include a *pre-exposure* static/schema check proving Q04 can address the actual freeze layout. Preserve unchanged Q03 source/render expectations and all later Q08–Q12 negative controls. Do not weaken any expected outcomes, modify the frozen RC2, or rerun its subject.

A later zero-model pass would qualify only the exact scripted tool/worker boundary tested, not Ollama build provenance, actual model-generated tool-use behavior, provider internal memory freshness, or a CAL scientific agent. Q13 requires separate owner admission review. No G89 retry, frozen CAL pilot, contract/release or integration follows.

**Reporting correction:** the first *retrospective report assembly* (not a scientific run) stopped on a manually mistyped empty-stderr SHA assertion before staging a report commit. It did not modify the frozen candidate or raw receipts. The exact stored wrapper stderr was rehashed and confirmed empty; this final public map was generated from actual raw bytes rather than transcribed values.
