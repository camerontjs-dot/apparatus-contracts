# Contract E Semantic Recoverability Audit — Preregistration

Status: **RESEARCH / META-ASSURANCE / NOT RC3E**

## Question

Can the presently supported Contract E normative content be interpreted reproducibly **without using implementation quality, self-written code tests, hidden fixture materialization, or a privileged reference implementation as proxies for contract comprehension**?

The primary claim under test is:

> Given one provenance-traceable resolved normative artifact and no prior Contract E reasoning, independent competent readers derive materially the same authority semantics, including explicit underdetermination where the artifact does not decide.

## Motivation

Prior Grok and Gemini implementation reproductions mixed several causal variables:

- contract comprehension;
- reconciliation of a layered amendment stack;
- implementation completeness;
- self-test completeness;
- native wire handling;
- evaluator/reference correctness.

This audit separates those questions. No new Contract E semantics are authorized by this experiment.

## Frozen source authority

The resolver may read exactly the six already-frozen public normative blobs on the RC3D R1 research lineage:

1. `SPEC-CANDIDATE.json` — `9c1090335d87eb5e4885a755542923b453c45317`
2. `SPEC-SHAPES.json` — `c3f293430ae6ddb87523d83ea6e5380b8b832136`
3. `SPEC-PARTICIPANT-BOUNDARY.json` — `8b1d292a240300388949d502e7b656e7a23a0b8e`
4. `BASIS-BINDING-SPEC.json` — `63c952c9c28f1be2173e69c79976c7dfe5880c10`
5. `RC3C-SPEC.json` — `f05feac88128fd693cca2fb25a0b2951654377eb`
6. `RC3D-INTERFACE-SPEC.json` — `61f46b09d391e7da4aed2491e428ec2ed226fe93`

The resolver must not read hidden cases, validators, prior reproduction code/results, post-falsification diagnostics, or conversation reasoning.

## Resolution rule

The resolved artifact is a deterministic **view**, not a semantic amendment.

It may:

- copy active normative structures from the six source blobs;
- place related inherited/amended rules into one section;
- add provenance pointers;
- expose source-set underdetermination explicitly where no source establishes a unique rule;
- normalize document organization only.

It must not:

- invent a missing semantic rule;
- choose a hidden evaluator behavior;
- repair a prior model implementation;
- convert an underdetermined point into a normative answer;
- add production authority.

Two known source-set questions are intentionally preserved as underdetermined unless the six source blobs themselves mechanically decide them:

- envelope-level `warrant` cardinality;
- whether non-authority-conferring supporting-artifact references must resolve through the authority-conferring registry.

## Reader cohort design

Primary target cohort: at least three fresh interpretation-only readers from different model/runtime families where practical.

Suggested order:

1. GitHub Copilot CLI;
2. Claude-family reader;
3. Grok-family reader;
4. Gemini/Antigravity may be used as an additional stress-test reader, not the sole cross-family witness.

Each reader receives only:

- the frozen resolved contract artifact;
- the frozen interpretation-record schema;
- the context-free reader task.

Readers must not write implementation code.

Before hidden semantic questions are revealed, each reader must freeze an interpretation record containing:

- its derived authority model;
- rule-by-rule interpretation;
- explicit underdeterminations;
- load-bearing assumptions;
- claimed contradictions or missing rules;
- predicted behavior classes where justified by the contract.

## Hidden semantic question phase

A semantic question set is frozen before the first reader launches but withheld until each interpretation record is frozen.

The questions contain no privileged implementation and no executable fixture DSL. Each asks for one of:

- `PERMIT`;
- `REJECT`;
- `UNDERDETERMINED`.

Readers must cite resolved rule IDs supporting the answer.

The primary comparison is **reader-to-reader agreement**, not reader-to-reference agreement.

## Classification logic

- If independent readers converge on the same interpretation, that supports recoverability of that rule.
- If readers independently identify the same underdetermination, that is evidence of a contract gap.
- If readers disagree while each answer is compatible with the artifact, that is evidence of ambiguity.
- If one reader contradicts explicit resolved text while others agree, classify reader error before changing the contract.
- If all readers agree and a later reference evaluator disagrees, challenge the evaluator.
- Implementation behavior is out of scope for the primary semantic-recoverability claim.

## Falsifiers

The semantic-recoverability claim is materially weakened if:

- multiple competent readers derive incompatible authority outcomes from the same explicit resolved rule;
- multiple readers independently require an unstated assumption to answer an authority-relevant question;
- the resolver cannot produce one deterministic artifact without making an unpreregistered semantic choice;
- a later reader cohort repeatedly confuses supporting artifacts with authority-conferring sources despite a supposedly explicit resolved distinction;
- the semantic question set requires wire/fixture assumptions absent from the resolved artifact.

## Nonclaims

This experiment does not establish:

- Contract E 1.0.0;
- production authorization behavior;
- implementation correctness;
- evaluator correctness;
- model-family equivalence;
- universal authority ontology.

## Thread state

`CONTINUING WITHIN BOUNDS` until the resolved artifact, question set, and first interpretation-only reader packet are frozen.