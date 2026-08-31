# Contract E RC3C — Native Wire / Currentness Hardening Preregistration

Status: **RESEARCH ONLY / successor to falsified fresh reproduction**

## Question

Can the smallest specification repair make the Contract E authority/warrant candidate independently recoverable without changing the authority-domain architecture that survived the first fresh reproduction?

The predecessor fresh independent Grok reproduction is preserved in `camerontjs-dot/research-scaffold-harness` PR #2 with terminal disposition **FALSIFIED**. Its decisive evidence was not broad semantic collapse. The failures clustered around authority-currentness composition, canonical wire/cardinality choices, delegation shape, and diagnostic-reason semantics.

RC3C must not repair unrelated semantics merely because the predecessor disagreed somewhere.

## Frozen predecessor authority

RC3B head: `f7e41ff09b7f8c33dd908ff1696a8b62b4851b6e`.

Inherited normative blobs remain unchanged unless RC3C explicitly supersedes one rule:

- `SPEC-CANDIDATE.json` blob `9c1090335d87eb5e4885a755542923b453c45317`
- `SPEC-SHAPES.json` blob `c3f293430ae6ddb87523d83ea6e5380b8b832136`
- `SPEC-PARTICIPANT-BOUNDARY.json` blob `8b1d292a240300388949d502e7b656e7a23a0b8e`
- `BASIS-BINDING-SPEC.json` blob `63c952c9c28f1be2173e69c79976c7dfe5880c10`

Predecessor fresh reproduction freeze:

- preregistration `9d2b6345c8387de8615375495a16cfcb3e67c503`
- frozen implementation `8987bf2fa183e7a00c40e256694b0d9de007a566`
- post-reveal comparison `4505b89c6d6987ab3a8d6f86c3d1053e25c2e7c6`

## Observed predecessor failures that RC3C is allowed to address

1. **Currentness ownership/composition**
   - authority-reference `current=false` was accepted when the resolved record remained current;
   - hidden authority expected fail-closed rejection;
   - the prior text said reference currentness must not override record currentness but did not state the asymmetric composition rule precisely enough.

2. **Canonical qualification cardinality**
   - hidden envelopes use `competence` as an array;
   - the fresh implementation chose a singular-object representation;
   - three positive baselines, three canonical matrix rows, and nine semantic variants rejected from that shape mismatch.

3. **Canonical delegation cardinality**
   - hidden delegation vectors use array-valued `scope` and `operations`;
   - the fresh implementation did not recover the same native shape, so all four delegation cases failed before clean semantic comparison.

4. **Reason semantics**
   - several safe rejections used different reason classes;
   - predecessor specification did not make clear whether old hidden reason strings were normative after RC3B introduced more specific basis-binding reasons, nor did it define a whole-envelope reason contract.

## Explicit non-targets

Do not alter in RC3C unless a direct contradiction makes the candidate incoherent:

- authority domains;
- participant responsibility boundaries;
- subject/domain/operation/scope/target authority-basis binding;
- competence vs jurisdiction separation;
- warrant vs operational permission separation;
- semantic result opacity;
- default non-transitive authority propagation;
- historical validity not being rewritten by later revocation;
- the frozen authority-basis registry;
- production representation, trust roots, delegation topology, or Contract E 1.0.0.

## Candidate repair hypotheses

### H1 — conjunctive fail-closed currentness

For a **new exercise**, a resolved authority reference is usable only when:

- the envelope reference explicitly reports `current=true`;
- the resolved authority record reports `current=true`;
- `evaluated_at` lies inclusively within `[valid_from, valid_until]`;
- if `revoked_at` exists, `evaluated_at < revoked_at`.

`reference.current=true` can never resurrect a stale/revoked record. `reference.current=false` is a veto/freshness failure, not an authoritative statement that rewrites the resolved record.

All failures in this group use canonical primary reason `authority_basis_not_current` except pure validity-window failure, which uses `authority_basis_outside_validity_interval`.

### H2 — one canonical wire shape

Authority-relevant fields must not rely on singular/plural coercion.

Candidate canonical cardinalities:

- `authority_basis`: array of authority references;
- `competence`: array of qualification objects, present on every envelope and allowed to be empty;
- `jurisdiction.scope`: scalar string;
- resolved basis `scopes`: array of strings;
- qualification `scope`: scalar string;
- delegation `operations`: array of strings;
- delegation `scope`: array of strings;
- participant/domain/non-implication collections remain arrays where already declared.

A consumer must reject malformed cardinality rather than silently coerce it.

### H3 — bounded normative reason contract

Acceptance/rejection is normative. For rejection paths explicitly listed by RC3C, a single canonical primary reason is also normative.

RC3A hidden reason strings are not automatically normative after RC3B/RC3C. They remain historical evidence unless RC3C explicitly relists that case or reason class.

RC3C will freeze a bounded whole-envelope precedence for authority-relevant public reasons, including:

1. malformed/canonical-wire failures;
2. forbidden generic authorization flag;
3. required-field/domain/operation/participant failures;
4. jurisdiction applicability/currentness;
5. authority-basis binding using RC3B precedence;
6. qualification failures;
7. warrant failures;
8. propagation/delegation/historical reason classes when those validators are invoked.

This is not authorization to expose internal implementation order as a production API.

## Falsifiers

RC3C is falsified internally if any of the following occurs:

- either currentness false-permit remains possible under the frozen rules;
- `reference.current=true` can make a non-current/revoked record usable;
- the canonical wire spec still permits both singular and array interpretations for an authority-relevant field under test;
- delegation scope/operations cardinality remains ambiguous;
- repairing cardinality requires changing domain semantics or reading opaque `result` payloads;
- semantic payload mutations change the common authority decision;
- predecessor authority-basis matrix develops a non-canonical false accept;
- a fresh successor implementation still needs a bespoke translation adapter for the specified wire shapes;
- the successor fresh reproduction cannot determine whether an old reason expectation remains normative.

## Required internal tests before fresh reproduction

Freeze before decisive execution:

- the RC3C amendment specification;
- a successor hidden case corpus targeting currentness, wire cardinality, delegation shape, and reason semantics;
- the successor validator/hardening apparatus.

Then run:

- the inherited RC3B validator suite unchanged;
- the inherited RC3B 9 x 15 compatibility matrix unchanged;
- the RC3C successor cases;
- semantic-result metamorphic invariance;
- negative controls for silent singular/plural coercion and duplicated-currentness laundering.

## Fresh reproduction rule

If internal hardening survives, a successor reproduction must use a **fresh context and fresh workspace**. The first Grok implementation, PR #2, comparison report, hidden vectors, reference validators, and this preregistration reasoning are denied pre-freeze.

A fresh Grok run is a successor regression reproduction because its model family exposed the predecessor counterexamples. A later different-model-family reproduction is still required for stronger cross-model independence.

## Promotion bound

Even a complete RC3C pass supports only another fresh independent reproduction. It does not establish Contract E 1.0.0, production authority policy, or a universal authority ontology/evaluator.
