# RC6 successor: freeze-receipt contract preflight

**Experiment successor ID:** `ERS-EVAL-TIME-PROV-20260921-03`

**Classification:** Draft Research apparatus successor. This does not change the scientific hypothesis, decisive matrix, Contract E, ERS evaluation semantics, production authority, or write permissions.

## Why this successor exists

The first frozen RC6 launch was `INCONCLUSIVE` before the decisive matrix. The exact runner expected ERS source identity at a nonexistent top-level field `implementation_source_commit`; the exact ERS freeze receipt records it at `implementation.source_commit`.

Contract E evaluation calls were zero. Matrix progress was empty. The scientific hypothesis was therefore not exposed.

This successor repairs only the freeze-receipt integration contract and adds a non-evaluating consistency preflight so that the same class of mismatch is detected before the next candidate is frozen.

## Preserved scientific authority

The scientific preregistration remains apparatus-contracts PR #130 at:

`dcdd10355e2f885273d843eef6e345bafca95faa`

Its hypothesis, positive control, +1 second falsifier, cross-pair controls, exact-result mutation, wrong-intent/state/issuer controls, stale/replay controls, production boundaries, and provenance-sidecar role remain unchanged.

Do not edit or reinterpret that matrix in this successor.

## Predecessor evidence

- RC6 ERS source: `65bde55f770c3c3d6e9b7b2b37f74c054e809e11`
- RC6 ERS freeze receipt/final: `66a82e8ac28c380ddc7eb4388bdc3daf289c1db9`
- RC6 apparatus source: `e28c0950227f6fcf031aa413d07f94f85454ae90`
- RC6 apparatus freeze: `21c960e4eba8306c855bec76afce829a801eb050`
- preserved inconclusive result: `5c437c0a11e1250e319871448cda4dd8023b8cb3`
- ERS PR #10
- apparatus PR #130 update comment recording `INCONCLUSIVE`

## Canonical freeze-receipt field contract for this successor

Use these exact semantic paths:

### ERS freeze receipt

- schema: `schema`
- experiment ID: `experiment_id`
- source repository: `implementation.repository`
- source branch: `implementation.branch`
- base commit: `implementation.base_commit`
- source commit: `implementation.source_commit`
- source tree: `implementation.source_tree`
- source blobs: `implementation.blobs`
- preregistration head: `apparatus.preregistration_head`
- apparatus candidate source commit: `apparatus.candidate_source_commit`
- transcript schema blob: `apparatus.transcript_schema_blob`
- issuer key identity: `issuer.public_key_identity`
- public API: `public_api`
- decisive result observed before freeze: `decisive_rc6_matrix_observed_before_freeze`

### Apparatus freeze receipt

- schema: `schema`
- experiment ID: `experiment_id`
- apparatus candidate source commit: `apparatus_candidate_source_commit`
- apparatus candidate source tree: `apparatus_candidate_source_tree`
- ERS source commit: `ers_candidate.source_commit`
- ERS source tree: `ers_candidate.source_tree`
- ERS freeze receipt commit: `ers_candidate.freeze_receipt_commit`
- ERS freeze receipt blob: `ers_candidate.freeze_receipt_blob`
- preregistration head: `preregistration.frozen_head`
- transcript schema blob: `preregistration.transcript_schema_blob`
- issuer key identity: `issuer.public_key_identity`
- public supervisor API: `public_supervisor_api`
- decisive result observed before freeze: `decisive_rc6_matrix_observed_before_freeze`

Do not add alias fields solely to make old code pass. The runner/preflight should consume the canonical nested paths above.

## Required non-evaluating consistency preflight

Before the successor freeze, run a deterministic preflight against the exact candidate receipts without starting the Contract E supervisor and without importing/calling the Contract E evaluator.

The preflight must establish at minimum:

1. both receipts parse and have the expected schemas;
2. both carry the same experiment ID;
3. ERS `implementation.source_commit` equals apparatus `ers_candidate.source_commit`;
4. ERS `implementation.source_tree` equals apparatus `ers_candidate.source_tree`;
5. both bind the same frozen PR #130 preregistration head;
6. both bind the exact transcript schema blob `b85b38ce95263e348d2ebd1293f76ffc87adcf6d`;
7. both bind the same issuer public-key identity;
8. apparatus receipt points to the exact ERS freeze receipt commit/blob that was read;
9. the CLI `--ers-source-commit` equals the receipt source commit;
10. the CLI `--apparatus-source-commit` equals the apparatus receipt source commit;
11. Git verifies the recorded source commits/trees;
12. both receipts assert no decisive matrix result was observed before freeze;
13. the public supervisor API still has no caller evaluation-time or caller Contract E result parameter.

The preflight must emit a machine-readable PASS receipt containing the exact input receipt hashes and compared values.

A failed preflight stops before freeze and before Contract E evaluation. It is a harness/setup failure, not a hypothesis result.

## Allowed code changes

Only changes needed to:

- consume the canonical receipt paths above;
- add/test the non-evaluating receipt-consistency preflight;
- create new successor freeze receipts/results;
- update identifiers/paths needed to distinguish this successor from the preserved RC6 attempt.

The ERS supervisor, transcript semantics, verifier semantics, Contract E invocation semantics, and decisive matrix should remain byte-identical to RC6 where possible. Any change to those scientific surfaces requires an explicit deviation and a new scientific successor rather than being hidden in this repair.

## Freeze rule

Run development tests and the new consistency preflight first.

Then freeze a new ERS successor and new apparatus runner/receipt. Record exact commits, trees, blobs, receipt identities, issuer key, environment, and a PASS preflight receipt.

After that freeze, run the complete PR #130 decisive matrix unchanged.

No repair after decisive exposure.

## Dispositions

- Preflight mismatch before freeze: `BLOCKED` or `INCONCLUSIVE` as appropriate, with no hypothesis conclusion.
- Frozen evaluator/apparatus defect after freeze but before meaningful discrimination: `INCONCLUSIVE`.
- Any preregistered substitution reaches `shadow_ready=true`: `FALSIFIED`.
- Full unchanged matrix passes: bounded support only, with all PR #130 non-claims retained.

No real MainFrame mutation, executor, effect registration, merge, release, or production promotion is authorized.
