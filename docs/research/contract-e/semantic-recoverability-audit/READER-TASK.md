# CONTEXT-FREE REQUIRED

# Contract E Semantic Recoverability Audit — Interpretation-Only Reader

You are an independent semantic reader, not an implementer.

## Exact objective

Using only the attached/materialized `RESOLVED-CONTRACT.json` and `INTERPRETATION-RECORD-SCHEMA.json`, determine what authority semantics the resolved Contract E research artifact actually states.

This experiment tests **contract comprehension only**.

Do not write code.
Do not design a validator.
Do not guess hidden tests.
Do not infer a reference implementation.
Do not retrieve project history.

## Authorized aperture

You may use exactly:

1. `RESOLVED-CONTRACT.json`
   - required SHA-256: `d883e5678aa7d39db6bd98d9607c94ee74ae68cd4c17a1def5cd00e6468634f9`
2. `INTERPRETATION-RECORD-SCHEMA.json`
3. this task

No other Contract E, CAL Pipeline, GitHub, local repository, web, memory, prior conversation, implementation, test, evaluator, or reproduction material is authorized.

If you observe any project-specific material outside this aperture, mark contamination and stop.

## Required method

1. Read `RESOLVED-CONTRACT.json` completely.
2. Read the interpretation schema completely.
3. Treat the resolved artifact as the only normative authority.
4. Distinguish:
   - direct normative text;
   - necessary inference;
   - explicit underdetermination;
   - genuine contradiction, if any.
5. Do not choose a preferred answer for an item explicitly marked `UNDERDETERMINED_BY_SOURCE_SET`.
6. Do not repair wording based on what you think the designers probably intended.
7. Do not create implementation pseudocode as a substitute for interpretation.

## Required output

Produce one JSON object conforming to `INTERPRETATION-RECORD-SCHEMA.json`.

It must include:

- reader runtime/model/session identity;
- the exact resolved-contract SHA-256 above;
- a domain-by-domain interpretation;
- authority-basis semantics;
- qualification and warrant semantics;
- currentness and temporal semantics;
- participant responsibility semantics;
- propagation semantics;
- delegation semantics;
- historical semantics;
- result-payload authority semantics;
- public evaluation-interface interpretation;
- reason/precedence interpretation;
- every underdetermination you find, including but not limited to the explicitly recorded open questions;
- any contradictions you believe remain;
- load-bearing assumptions;
- falsifiers for your interpretation.

Every material statement must cite one or more JSON pointers into `RESOLVED-CONTRACT.json`.

## Important separation

You are **not** being asked whether you could implement this contract.

You are **not** being asked whether the contract is a good architecture.

You are **not** being asked to make every case determinate.

`UNDERDETERMINED` is a valid and important finding.

## Freeze

Your interpretation becomes immutable before any semantic question set is revealed.

The final JSON must contain exactly this marker:

`FRESH_CONTRACT_E_INTERPRETATION_FROZEN_BEFORE_SEMANTIC_QUESTIONS_REVEAL`

Once the interpretation record is produced, STOP.

Do not answer any scenario/question corpus yet.
