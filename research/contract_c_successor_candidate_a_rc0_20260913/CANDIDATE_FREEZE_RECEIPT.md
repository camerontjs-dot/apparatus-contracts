# Candidate A RC0 freeze receipt

**Classification:** Draft Research / Research Infrastructure.

This is a successor record to, not a modification of, the Phase 0/1/1.5/2 frozen records on PR #94.

## Exact freeze

Candidate A RC0 is frozen at commit:

`9f1808c47503c884887dbf862e9cd8162b21b583`

Its exact parent research authority is the Phase 2 freeze:

`f5337dedaad045aa290e80f69dc83ac1a0f73436`

The candidate freeze was created on branch `research/contract-c-successor-candidate-a-rc0-20260913`, stacked onto `research/contract-c-successor-ground-up-20260913`.

Frozen candidate blobs at the freeze commit:

- `CANDIDATE_A_RC0.md`: `4fae55b156b0caea5a4815c2c665a816f39667d9`;
- `candidate_a_rc0.schema.json`: `ee89f25bfcef008c95cbb35adf696fb1b3e2dc20`;
- `candidate_a_rc0.py`: `fb0a05ca929fbcf8284799306e9861d992839aaa`.

The frozen research profile literal is `contract-c-successor-candidate-a-rc0-research`.

## No-patch rule

The three candidate files above are immutable for the decisive RC0 adversarial cohort. Qualification infrastructure, attack fixtures, result receipts, and terminal disposition records may be added after this freeze, but they may not modify the candidate bytes.

If any revealed adversarial case requires changing one of the frozen candidate files, RC0 is `FALSIFIED_REQUIRES_SUCCESSOR_CANDIDATE`. The repair must be a new candidate/freeze rather than a patch followed by recounting the same cohort.

## Boundary

This freeze is not a production Contract C release, SemVer assignment, CAL/Decision production change, Contract E / Authorization change, or execution authority. It only creates the exact object to be pressure-tested for eligibility to enter a later CAL producer-conformance research phase.