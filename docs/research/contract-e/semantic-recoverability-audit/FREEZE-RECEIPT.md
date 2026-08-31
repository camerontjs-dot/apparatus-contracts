# Contract E Semantic Recoverability Audit — Freeze Receipt

Status: **FROZEN FOR INTERPRETATION-ONLY READER COHORT**

This receipt freezes the interpretation-only apparatus. It is not a Contract E semantic amendment and does not authorize production behavior.

## Candidate content freeze

The complete reader/evaluator content was frozen before this receipt at:

- content commit: `3e522b79208f5b918d51d903b4fcc0623145923d`
- content tree: `455c286c1569f80b0f34fdcb9b444f7dcf7d2ea6`
- Draft Research PR: `#47`

This receipt is metadata-only relative to that content freeze.

## Exact six-source authority

1. `SPEC-CANDIDATE.json` — `9c1090335d87eb5e4885a755542923b453c45317`
2. `SPEC-SHAPES.json` — `c3f293430ae6ddb87523d83ea6e5380b8b832136`
3. `SPEC-PARTICIPANT-BOUNDARY.json` — `8b1d292a240300388949d502e7b656e7a23a0b8e`
4. `BASIS-BINDING-SPEC.json` — `63c952c9c28f1be2173e69c79976c7dfe5880c10`
5. `RC3C-SPEC.json` — `f05feac88128fd693cca2fb25a0b2951654377eb`
6. `RC3D-INTERFACE-SPEC.json` — `61f46b09d391e7da4aed2491e428ec2ed226fe93`

## Resolved contract artifact

- deterministic builder: `build-resolved.mjs`
- frozen compressed bytes: `RESOLVED-CONTRACT.json.gz.b64`
- compressed Git blob: `ddf667cf53c8388e6e8bfc6f099ec453a0c2628d`
- materialized `RESOLVED-CONTRACT.json` SHA-256: `d883e5678aa7d39db6bd98d9607c94ee74ae68cd4c17a1def5cd00e6468634f9`
- materializer: `materialize-resolved.mjs`

The resolved artifact is a deterministic view only. It does not import hidden evaluator rules or prior model behavior.

Explicit source-set underdeterminations preserved in the resolved artifact:

1. envelope-level warrant cardinality;
2. registry-resolution obligation for non-authority-conferring supporting-artifact references.

## Frozen reader apparatus

- interpretation schema: `INTERPRETATION-RECORD-SCHEMA.json`
  - blob `54268fe089aa88507faa03f63cdbd9b37e27993d`
- pre-question reader task: `READER-TASK.md`
  - blob `a04d2d05df31ddb8bfa3731dd7857276f9a34134`
- hidden semantic questions: `FROZEN-SEMANTIC-QUESTIONS.json`
  - blob `867dfe4d1be40344bc07b651c060c78b5e9307d7`
  - question count: `51`
- post-interpretation question task: `QUESTION-PHASE-TASK.md`
  - blob `52dd27a23bde3cd0b465cd8cdc93347fd1bdba5d`

There is no privileged semantic answer key in this apparatus.

## Required phase markers

Interpretation freeze:

`FRESH_CONTRACT_E_INTERPRETATION_FROZEN_BEFORE_SEMANTIC_QUESTIONS_REVEAL`

Question-response freeze:

`FRESH_CONTRACT_E_SEMANTIC_ANSWERS_FROZEN_WITHOUT_REFERENCE_KEY`

## Hosted verification

Accepted content-freeze push run:

- workflow run `33441877797`
- conclusion: `SUCCESS`
- resolved-view artifact `9776537622`
- artifact digest: `sha256:e258d22acf0886cb412565c5d52aee9bc1c850cad4238426402edb8f1c8b4594`

The run verified:

- all six source Git blobs;
- deterministic rebuild of the resolved view;
- valid JSON materialization;
- byte identity between regenerated and frozen resolved artifacts;
- exact materialized SHA-256 `d883e5678aa7d39db6bd98d9607c94ee74ae68cd4c17a1def5cd00e6468634f9`.

## Reader cohort rule

Do not change this contract/audit apparatus after observing reader 1 in order to improve later-reader agreement.

Prefer at least three fresh independent reader/runtime families before a semantic recoverability disposition.

Primary comparison is reader-to-reader. `UNDERDETERMINED` is a legitimate result.

Reader 1 target: GitHub Copilot CLI.

Gemini/Antigravity may be used as an additional stress reader or apparatus fallback, but a failed Copilot launch before semantic output is an apparatus deviation, not a reader result.

## Nonclaims

This freeze does not establish:

- Contract E 1.0.0;
- production authorization semantics;
- implementation correctness;
- evaluator correctness;
- that the two explicit underdeterminations are the only possible ambiguities;
- that any particular model family is a competent reader.

## Next authority

Launch reader 1 in a fresh interpretation-only context. Stop after its immutable interpretation record. Semantic questions remain withheld until that record is frozen.