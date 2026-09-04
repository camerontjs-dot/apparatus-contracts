# Contract E RC3 target-reference cardinality successor apparatus deviations

Status: **research evidence record**

Production authorization: **false**

## 2026-09-03 / first hosted qualification attempt

Workflow run: `33834615021`

Qualification job: `100904491435`

Head: `759dd61e36455d88bc8f966953c982ecbfb2f568`

Disposition: **APPARATUS FAILURE BEFORE SCIENTIFIC COMPARISON**

Observed evidence:

- candidate controls passed on Python 3.11, 3.12, and 3.13;
- each candidate execution reported `PREDECESSOR_ASSERTED_CONTROLS=62`, `NEW_TARGET_CARDINALITY_CONTROLS=3`, `TOTAL_ASSERTED_CONTROLS=65`;
- candidate frozen-byte verification passed;
- qualifier failed before predecessor-reference regression, reference passthrough, or weak-control execution;
- exception: `ModuleNotFoundError: No module named 'hidden_cases'` while loading the frozen predecessor `hidden_cases_reference_identity_extension.py`;
- the frozen predecessor extension uses `from hidden_cases import _request, _state, _target`, while the successor evaluator had loaded the sibling base module under a unique import name without registering the historical `hidden_cases` alias.

This failure is not evidence for or against the target-reference semantic repair. No decisive evaluator result was observed.

Repair scope:

- candidate reference and candidate tests remain frozen and unchanged;
- SPEC/schema remain unchanged;
- successor evaluator import plumbing may register the exact frozen predecessor hidden-case module under the literal historical name `hidden_cases` only while loading the exact frozen extension;
- no hidden case, expected result, weak control, normative projection, or candidate behavior may be changed as part of this apparatus repair.

Repair commit:

`1f509b36d3ca61dfd3dcf808d1da27ef34b05a8c`

The failed run and its artifact remain historical evidence and must not be replaced or relabeled as a scientific result.
