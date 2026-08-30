# CONTEXT-FREE REQUIRED

# Contract E Authority / Warrant Specification — Fresh Independent Reproduction RC0

Use this packet as the complete task input. Do not import surrounding CAL Pipeline conversation, prior Contract E summaries, prior authority-model reasoning, or prior reproduction conclusions.

## 1. Exact objective

Independently implement and test the frozen research authority/warrant specification using only the authorized pre-freeze information aperture below.

Determine whether a competent implementation created from the frozen specification alone independently recovers the same authority-boundary behavior across informational and operational authority without seeing the reference validators, reference results, hidden test vectors, PR narrative, or prior implementation reasoning before implementation freeze.

The implementation must distinguish, where the specification requires it:

- participant responsibility;
- authority domain;
- authority-conferring basis;
- jurisdiction scope;
- competence/qualification;
- warrant;
- propagation;
- delegation;
- historical valid-at-time state;
- current authority;
- local domain result payload.

Do not try to make the reproduction pass. Preserve every ambiguity and disagreement.

This is not authorization to define Contract E 1.0.0, modify production CAL/Evidence Bundler/Decision Engine behavior, create a production authority registry/control plane, merge a release, or execute consequential downstream actions.

## 2. Independent implementation repository

Target repository:

`camerontjs-dot/research-scaffold-harness`

Fresh implementation base:

`548bfa81f65290eda15af658f647497679b840ef`

Create a new research branch from exactly that base. Suggested branch name:

`research/contract-e-authority-warrant-fresh-reproduction-rc0`

Existing Contract D reproduction PR/history in this repository is unrelated and must not be used as Contract E design guidance.

## 3. Frozen authority under reproduction

Authoritative source repository for the specification bytes:

`camerontjs-dot/apparatus-contracts`

The authority under reproduction is the union of exactly four immutable specification blobs:

1. `docs/research/contract-e/rc3a-authority-warrant-spec/SPEC-CANDIDATE.json`
   - Git blob: `9c1090335d87eb5e4885a755542923b453c45317`

2. `docs/research/contract-e/rc3a-authority-warrant-spec/SPEC-SHAPES.json`
   - Git blob: `c3f293430ae6ddb87523d83ea6e5380b8b832136`

3. `docs/research/contract-e/rc3a-authority-warrant-spec/SPEC-PARTICIPANT-BOUNDARY.json`
   - Git blob: `8b1d292a240300388949d502e7b656e7a23a0b8e`

4. `docs/research/contract-e/rc3b-authority-basis-binding/BASIS-BINDING-SPEC.json`
   - Git blob: `63c952c9c28f1be2173e69c79976c7dfe5880c10`

Treat those bytes as the complete normative candidate authority for the fresh implementation.

The specification is research-only and non-canonical.

## 4. Authorized pre-freeze information aperture

Before implementation freeze, you MAY access only:

### A. The four exact specification blobs above

Fetch them by exact path/ref or blob identity without browsing adjacent directories, commits, PRs, issues, search results, or repository history.

### B. Stable project governance necessary to execute the experiment

Only if provided directly in the context-free project/task environment:

- research evidence must preserve failures/deviations;
- no production promotion is implied;
- implementation must be frozen before hidden comparison vectors are revealed;
- contamination invalidates the independence claim.

### C. Target repository base

You may inspect `camerontjs-dot/research-scaffold-harness` at exact base `548bfa81f65290eda15af658f647497679b840ef` only as needed to add an isolated research implementation and tests.

Do not inspect its existing Contract D reproduction implementation, PR narrative, or reasoning as conceptual guidance for this task.

## 5. Pre-freeze denylist

Before implementation freeze, DO NOT access, retrieve, search, summarize, infer from snippets, or inspect:

### Apparatus reference implementations/evaluators

- `docs/research/contract-e/rc3a-authority-warrant-spec/validate.mjs`
- `docs/research/contract-e/rc3b-authority-basis-binding/validate.mjs`
- `docs/research/contract-e/rc3b-authority-basis-binding/hardening.mjs`

### Hidden/reference test vectors and authority registry

- `docs/research/contract-e/rc3a-authority-warrant-spec/FROZEN-CASES.json`
- `docs/research/contract-e/rc3b-authority-basis-binding/AUTHORITY-BASIS-REGISTRY.json`
- `docs/research/contract-e/rc3b-authority-basis-binding/FROZEN-BASIS-ATTACKS.json`
- `docs/research/contract-e/rc3b-authority-basis-binding/HARDENING-PREREGISTRATION.md`
- any generated `RESULTS.json` or `HARDENING-RESULTS.json`

### Results / reasoning / narratives

- RC3A `RESULTS.md`
- RC3B `RESULTS.md`
- RC3A/RC3B PR bodies, comments, reviews, workflow logs/artifacts, Actions summaries, or issue correspondence;
- Apparatus Contracts PRs #23, #25, #26, #27;
- Decision Engine authority PRs/results;
- CAL semantic-authority PRs/results;
- Evidence Bundler authority PRs/results;
- this conversation or any Contract E/authority summary from it;
- the cross-disciplinary authority deep-research report that motivated the candidate;
- prior agent reasoning about what fields are important or why.

Do not use GitHub code search or general search terms that could return snippets from denied files.

If a denied artifact is exposed before freeze, stop and record the contamination. Do not continue under an independence claim.

## 6. Pre-freeze task

Using only the authorized aperture:

1. Read the four frozen specification blobs.
2. Write a preregistration stating your independent interpretation of:
   - required authority envelope semantics;
   - authority domains and operations;
   - participant conformance rules;
   - authority-basis resolution/binding;
   - competence/qualification rules;
   - warrant rules;
   - propagation rules;
   - delegation rules;
   - historical/currentness semantics;
   - unknown/fail-closed behavior.
3. Record any ambiguity before implementing. Do not silently choose a reference-friendly interpretation.
4. Implement a research-only consumer from scratch.
5. Create your own tests derived only from the specification.
6. The implementation should expose enough stable API/CLI behavior that, after freeze, an external comparison harness can supply:
   - an authority envelope;
   - a collection/registry of authority-basis records;
   - propagation requests;
   - delegation objects;
   - historical/current authority records;
   and observe deterministic accept/reject/indeterminate behavior plus reasons where your interpretation specifies them.
7. Do not copy or approximate a reference implementation.
8. Do not add a translation adapter specifically for the hidden vectors after reveal.

## 7. Required implementation freeze

Before any hidden/reference vectors are revealed:

- commit the preregistration;
- commit the complete independent implementation;
- commit independent pre-reveal tests;
- run those tests in hosted CI where practical;
- record exact implementation commit and tree;
- record hashes of implementation and test corpus;
- write a freeze receipt stating:

`FRESH_IMPLEMENTATION_FROZEN_BEFORE_REFERENCE_VECTOR_REVEAL`

After this freeze, the independent implementation and its pre-reveal tests are immutable for scientific comparison.

A later disagreement must not be repaired in place and counted as the same reproduction.

## 8. Authorized post-freeze reveal

Only after the freeze receipt is committed may you reveal exactly these comparison artifacts:

1. RC3A hidden cases:
   - path `docs/research/contract-e/rc3a-authority-warrant-spec/FROZEN-CASES.json`
   - Git blob `85bc7805d02a04c5a10b48b43a5f5a89f4e2f32a`

2. RC3B authority-basis registry:
   - path `docs/research/contract-e/rc3b-authority-basis-binding/AUTHORITY-BASIS-REGISTRY.json`
   - Git blob `76ea333ee0460d9614e9899edb69e6865e48eccb`

3. RC3B direct basis attacks:
   - path `docs/research/contract-e/rc3b-authority-basis-binding/FROZEN-BASIS-ATTACKS.json`
   - Git blob `c726fb0ef914a850620e545131a70d427f4027bd`

4. RC3B compatibility-matrix expectations:
   - path `docs/research/contract-e/rc3b-authority-basis-binding/HARDENING-PREREGISTRATION.md`
   - Git blob `1d85e2036d410b3af08d4b2b8926586da8fe6088`

Do not reveal the reference validators or reference generated results even after implementation freeze unless a later diagnostic phase is separately authorized. They are unnecessary for the primary comparison.

## 9. Post-freeze comparison rules

After reveal, you MAY add a comparison harness only. It must call the frozen independent implementation without changing its authority semantics.

Run at least:

### A. Frozen envelope vectors

Evaluate all frozen RC3A envelope cases against the revealed basis registry.

Compare:

- accept/reject outcome;
- reason where the frozen vector specifies one;
- positive baselines;
- cross-domain laundering cases;
- competence/mandate separation;
- warrant/mandate separation;
- participant responsibility boundaries;
- unknown-domain/generic-authorized behavior.

### B. Propagation, delegation, historical vectors

Run every frozen propagation, delegation, and historical case without altering the implementation.

### C. Direct RC3B authority-basis attacks

Run all revealed direct authority-basis substitution cases.

### D. Compatibility matrix

For each of the nine frozen positive baseline requests, substitute every revealed authority-conferring registry record.

The exact expected canonical mapping is defined in the revealed hardening preregistration. Report false accepts and false rejects.

Also run the specified reference-type-only mutations.

### E. Semantic-payload metamorphism

For every positive baseline, replace only the domain-local `result` payload with at least three materially different opaque payloads.

Authority-boundary outcome must remain unchanged unless your preregistered interpretation explicitly and independently concluded otherwise before reveal. Any disagreement is evidence and must be preserved.

## 10. Primary success conditions

The fresh reproduction supports the specification only if all are true:

1. no pre-freeze aperture violation occurred;
2. the independent implementation was frozen before hidden vectors were revealed;
3. all positive frozen baseline cases are consumable natively;
4. all frozen negative/laundering cases agree with their expected disposition;
5. all direct RC3B authority-basis attacks agree;
6. the full compatibility matrix has zero false accepts and zero false rejects;
7. type-only authority-reference mutations are rejected as specified;
8. propagation/delegation/historical cases agree;
9. opaque semantic-result mutations do not change common authority results unless that behavior was explicitly preregistered from the specification alone;
10. no post-reveal implementation repair or bespoke translation adapter is required.

Agreement counts are evidence, but a single authority-relevant false permit is a material failure.

## 11. Failure / falsification conditions

Preserve a failure if any of the following occurs:

- the specification is ambiguous enough that a competent independent implementation chooses a materially different authority boundary;
- a reference field/shape required for hidden vectors was not recoverable from the specification;
- a hidden vector requires producer-specific semantics not present in the four normative blobs;
- an authority-basis record can be laundered across subject/domain/operation/scope/target/currentness;
- competence/warrant/mandate collapse occurs;
- identity/provenance propagation silently carries semantic or operational authority;
- a positive result/confidence/success field creates authority;
- hidden vectors require a bespoke adapter after reveal;
- the implementation or tests are modified after reveal to restore agreement;
- pre-freeze contamination occurs.

Do not reinterpret a failure as partial success merely because most cases agree.

## 12. Required evidence record

Open a Draft Research PR in `camerontjs-dot/research-scaffold-harness` and preserve:

- exact clean base SHA;
- preregistration commit;
- frozen implementation commit/tree;
- pre-reveal test hashes and CI receipts;
- freeze receipt;
- exact post-freeze revealed blob identities;
- comparison harness commit;
- per-case disagreements;
- compatibility matrix counts;
- any ambiguity discovered before or after reveal;
- contamination/deviation record if applicable;
- explicit non-claims;
- terminal disposition.

Primary research disposition must be one of:

- **SUPPORTED FOR PROMOTION** — only if the frozen research specification is independently recoverable under the success conditions;
- **FALSIFIED** — if authority-relevant behavior materially disagrees because the frozen specification is insufficient or misleading;
- **INCONCLUSIVE** — if execution/aperture apparatus prevents a valid comparison;
- **SUPERSEDED** — only if the experiment is explicitly replaced before decisive execution.

## 13. Non-claims

Even a full pass does not establish:

- Contract E 1.0.0;
- production authority policy;
- a universal authority ontology;
- a universal evaluator;
- production cryptographic trust roots;
- production delegation/revocation topology;
- that every industry/domain uses these authority relations;
- semantic correctness of CAL, Evidence Bundler, or Decision Engine;
- automatic execution permission;
- production release authorization.

A pass would establish only that the frozen research specification is sufficiently explicit for this independent consumer and frozen heterogeneous authority vector set.
