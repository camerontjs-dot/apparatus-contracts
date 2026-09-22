# CAL Pipeline v3 fixture recovery RC2 preregistration

## Classification

Research-infrastructure successor to PR #136 only.

Parent candidate: `208ffad09e55a55d48745bf4de9135080245df27`.

Parent hosted run: `35760558562`.

Observed parent result: fixture worlds A and B completed, but the "Verify and package complete fixture bundle" step failed before the verifier process launched because shell redirection targeted `build/cal-pipeline-v3-fixture-recovery-verification.json` while the parent `build/` directory did not exist.

This is an infrastructure-path failure. It is not a scientific result and does not change PR #130, PR #134, Contract E, ERS, or any pipeline semantic subject.

## Hypothesis

If the workflow creates only the required parent `build/` directory before invoking the unchanged verifier command, the verifier can execute and expose the next real recovery outcome.

## Authorized implementation delta

Exactly one functional workflow change is authorized:

- create `build/` before the verifier stdout redirection.

Do not pre-create `build/cal-pipeline-v3-fixture-recovery/frozen-fixtures`, because the verifier requires its `--out` path not to exist and creates it itself.

No other recovery logic, expected digest, historical identity, generator subject, checkout identity, provenance classification, verifier rule, or upload rule is authorized to change.

## Acceptance / falsifiers

The successor is acceptable as a recovery-apparatus candidate only if:

1. the diff from PR #136 contains no functional change other than creation of the parent `build/` directory;
2. exact subject-identity checks remain unchanged;
3. both fixture worlds are still generated from the same frozen subjects;
4. the unchanged verifier launches;
5. any verifier rejection is preserved as the successor result rather than repaired in the same candidate;
6. no PR #130 scientific matrix, Contract E evaluation, ERS shadow/write, or downstream authorization is run as part of this successor.

If the verifier exposes a new defect or evidence mismatch, stop and preserve it.

## Downstream boundary

A successful recovery does not by itself authorize PR #130.

If any required scientific input is only deterministically reconstructed and lacks a preserved historical byte reference, freeze the recovered fixture bundle under a new explicit fixture-bound scientific successor before running the unchanged PR #130 matrix.
