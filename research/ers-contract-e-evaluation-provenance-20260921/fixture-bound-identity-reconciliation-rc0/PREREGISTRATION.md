# Fixture-bound experiment-identity reconciliation — preregistration

## Status

Pre-scientific, non-evaluating identity reconciliation only.

The fixture-bound scientific subject remains experiment:

`ERS-EVAL-TIME-PROV-20260922-05`

The decisive matrix is not authorized by this preregistration.

## Why this successor exists

PR #140 qualified the fixture-bound subject, but the inherited frozen scientific machinery still identifies predecessor experiment `ERS-EVAL-TIME-PROV-20260922-04`.

The mismatch is not merely descriptive:

- the frozen runner rejects a preflight whose `experiment_id` does not equal its own `EXPERIMENT_ID`;
- the frozen receipt preflight cross-checks ERS and apparatus receipt experiment identities against its own `EXPERIMENT_ID`;
- runner outputs propagate the ID into RESULT/RUNNING/FAILURE and into sidecar/manifest run identifiers that participate in content-addressed attestations.

Therefore a wrapper that calls the old runner `04` while claiming outer experiment `05` is rejected. It would require special interpretation of one executed run under two experiment identities.

## Chosen architecture

Use a full identity successor with the smallest possible behavioral-neutral source delta.

### Apparatus source successor

Create two new source files alongside the frozen originals:

- `fixture-bound-identity-successor-rc0/reproduce_rc6_fixture_bound.py`
- `fixture-bound-identity-successor-rc0/receipt_preflight_fixture_bound.py`

Each must be copied from its exact frozen predecessor.

The **only** authorized text change in each source file is:

`ERS-EVAL-TIME-PROV-20260922-04`

to

`ERS-EVAL-TIME-PROV-20260922-05`

The original frozen files remain unchanged.

Any additional source diff is a falsifier for this reconciliation candidate.

## ERS successor

Create a receipt-only ERS successor.

ERS implementation source remains exactly:

- commit `65f47d029fb734be1d5d506a135cbeba813f6be8`
- tree `405bb622e0d7d0f69f3da7506a15fa0b2390e191`

No ERS runtime source change is authorized.

The new receipt must identify experiment `05` and bind the new apparatus source commit plus the new runner/preflight blobs.

## Apparatus freeze successor

After the ERS receipt-only freeze exists, create a new apparatus freeze receipt that binds:

- experiment `05`;
- the new runner blob;
- the new receipt-preflight blob;
- the new ERS receipt commit/blob;
- the unchanged scientific question and decisive matrix;
- all unchanged dependencies and fixture authority.

## Required qualification

Qualification is identity-only and non-evaluating.

It must demonstrate:

1. each successor source contains one `05` experiment literal and zero residual `04` literal;
2. each successor source differs from its predecessor only at that literal;
3. wrong-ID runner preflight is rejected;
4. wrong-ID receipt preflight is rejected;
5. an `04` receipt cross-paired with `05` authority is rejected;
6. altered fixture-subject identity is rejected;
7. altered runner identity is rejected;
8. new apparatus/ERS freeze receipts cross-check one experiment identity end to end;
9. zero Contract E evaluations;
10. zero supervisor launches;
11. zero candidate-runtime imports;
12. zero network activity.

Do not import or execute scientific candidate code to establish the source-delta claim.

## Frozen scientific invariants

No change is authorized to:

- PR #130 scientific question;
- decisive controls or expected rejection boundaries;
- Contract E;
- Contract D;
- Decision Engine;
- CAL;
- Contract C consumer;
- ERS runtime behavior;
- transcript schema;
- issuer semantics;
- fixture bytes or provenance classifications;
- fixture subject identity `sha256:bebbb1b7973a962d59c92061e8e70283a2fb4b2b8c388705b8d80ce13000c7ad`.

## Stop rule

Preserve the first unexpected diff, wrong-ID acceptance, receipt mismatch, evaluator defect, or instrumentation violation.

Do not repair and continue inside the same frozen candidate.

## Next boundary

Only after this identity successor is frozen and independently qualified may the state become:

`READY_FOR_FIXTURE_BOUND_EVALUATION_TIME_PROVENANCE_MATRIX`

This preregistration does not run or authorize that matrix.
