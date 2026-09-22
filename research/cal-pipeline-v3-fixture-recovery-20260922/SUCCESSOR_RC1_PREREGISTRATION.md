# CAL Pipeline v3 fixture recovery protocol successor RC1

Date: 2026-09-22

Classification: **Research infrastructure successor** to PR #135.

Parent exposed result: `BLOCKED_FIXTURE_RECOVERY` at PR #135 head
`7cdf2d54372af40b15b3693b7ed87acaf0f5b33d`.

This successor exists only to repair two recovery-apparatus defects observed before any successful reproduction:

1. the hosted Contract D checkout omitted the release tag ref required by the frozen Decision candidate;
2. the verifier did not fail closed when the historical artifact or expected historical Contract C / Contract D files were absent.

No CAL, Contract C, Decision, Contract D, Contract E, ERS, PR #130, or PR #134 scientific semantics may change.

## Exact parent failure preserved

Hosted run `35755521644` reached PIPE01 Decision evaluation and stopped with
`contract_d_authority_identity_mismatch` because
`refs/tags/contract-d-v1.0.0` was not present in the shallow Contract D checkout.

The tag itself is not defective. Live GitHub shows annotated tag object
`6eadd688b482f3c9fce2ce5e7a2841089d852096` peeling to exact frozen Contract D commit
`298a1a0f7b7b6d7712e11200d04faec3e1ca169b`.

The original PR #123 workflow used `fetch-depth: 0` for this exact Contract D checkout and asserted both identities. RC1 restores that historical checkout behavior.

## Frozen historical references

Generator:
`e68e5ab387e9779b0be62d92766b76e475964790`

Historical composition result:
`sha256:2ef133c504cd33bf5b9912acb06e154b43d7060b967dd4230081d4a8ad4f9753`

Historical run / artifact:
- run `35479370533`
- artifact `10594929710`
- artifact ZIP `sha256:bab1e7522a69e404208d9e65d9edae89d860827ef08fd3da1ad01813554b0841`

Contract D release:
- commit `298a1a0f7b7b6d7712e11200d04faec3e1ca169b`
- annotated tag object `6eadd688b482f3c9fce2ce5e7a2841089d852096`
- tag `contract-d-v1.0.0`

Expected PIPE C/D identities remain exactly those frozen in PR #127 and PR #135.

## Successor delta

Only these changes are allowed relative to the PR #135 parent:

- make the Contract D checkout include the historical release tag exactly as PR #123 did;
- assert Contract D HEAD, annotated tag object, and peeled tag commit;
- require `--historical-artifact`;
- fail if that artifact root does not exist;
- require exactly one historical Contract C and Contract D candidate for each PIPE;
- require those historical C/D bytes to equal each reconstructed C/D file;
- emit the exact provenance classifications:
  - `byte_matched_to_surviving_historical_artifact`
  - `deterministically_reconstructed_without_preserved_historical_reference`
- retain the existing two-run byte-identity and historical composition-digest gates.

No expected hash or scientific acceptance criterion may be relaxed.

## Acceptance

RC1 is supported only if both isolated reproductions run to completion and the verifier passes all gates.

For each PIPE:
- Contract C and Contract D must be byte-identical between reproduction A and B;
- Contract C and Contract D must match PR #127 frozen hashes;
- Contract C and Contract D must each match exactly one surviving historical PR #123 artifact file byte-for-byte;
- consumer inputs and decision target must be byte-identical between reproductions;
- absent historical references for consumer inputs / decision target are classified only as deterministic reconstruction.

Both composition result files must be byte-identical and match the frozen historical composition-result SHA-256.

## Stop

Preserve and stop on any:
- subject identity mismatch;
- tag object / peeled tag mismatch;
- missing or ambiguous expected historical C/D file;
- historical C/D byte mismatch;
- cross-run fixture mismatch;
- composition-result mismatch;
- verifier defect requiring a semantic or expected-hash change.

Do not run the PR #130 Contract E / ERS scientific matrix under this task.

A reconstruction-only pass still requires a fixture-bound scientific successor before that matrix is authorized.
