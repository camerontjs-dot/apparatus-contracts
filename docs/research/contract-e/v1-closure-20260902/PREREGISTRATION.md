# Contract E v1 Closure — Preregistration

## Work class

Research + Research Infrastructure + pre-promotion Contract E closure.

This branch is not a production promotion, release, tag, operational Authorization implementation, or execution authority.

## Scientific/design question

Can Contract E be reduced to a bounded, fail-closed **standing authority state + transient authorization evaluation** protocol that:

1. references immutable A/B/C/D objects without redefining their semantics;
2. permits authority only from one complete explicit `grant | policy | delegation` lineage;
3. rejects authority laundering from evidence, CAL state, Decision state, supporting artifacts, status strings, or execution reports;
4. binds subject, domain, operation, scope, target, currentness, revocation, and delegation without requiring the known underdetermined Qualification or surplus-record predicates;
5. keeps Decision, Authorization, execution, and verification distinct;
6. preserves rejected/conflicting/residual information and exact referenced identities; and
7. fails closed on missing, malformed, unknown, stale, revoked, cyclic, substituted, or future Contract-E state.

The goal is the smallest stable control-plane protocol justified by evidence, not a universal authority ontology.

## Starting evidence

### Observed

- RC0 (`#52`) produced 10 unsafe promotions from forged resolution IDs, established-looking receipts without lineage, and a non-conferring supporting artifact.
- RC0B (`#53`) eliminated those tested unsafe promotions by recursively validating authority lineage, discriminating explicit conferring basis types, and requiring authorized resolution.
- Semantic recoverability audit (`#47`) falsified broad recoverability because Qualification subject/scope predicates were absent from the normative source.
- Qualification closure (`#58`) found subject and scope binding underdetermined; historical exact equality is not normative authority.
- Aggregation closure (`#59`) established that authority cannot be synthesized from several individually insufficient records, but did not determine the quantifier for surplus complete/mismatching conferring records.
- Contract A parent/atom pressure (`#61`) supported exact-target authority binding and rejected parent/child/sibling cross-use without reopening Contract A.
- Fresh authority-chain RC1 successor comparison against the byte-frozen independent implementation produced 94/94 authority outcomes, 0 false permits, 0 false rejects, 0 exceptions, 0 preservation failures, 13/13 metamorphic pairs, and one canonical reason-precedence disagreement (`OBS-NEG-KIND`), making exact RC1 recoverability `FALSIFIED` under its sealed evaluator.

### Inference to test, not assume

A useful Contract E v1 may not need Qualification semantics, multi-conferring aggregation, semantic/comparison/composition authority kinds, or normative primary-reason precedence. A smaller control-plane protocol may preserve the tested safety boundary while avoiding those underdeterminations and stage-semantic duplication.

## Candidate shape fixed before implementation

The candidate will have exactly two normative input objects and one non-conferring output:

1. **AuthorityState** — an immutable authority-bearing object containing exactly one linear authority chain.
2. **AuthorizationRequest** — a transient request naming one AuthorityState and one exact typed jurisdiction/target.
3. **AuthorizationReceipt** — a deterministic audit receipt that records the evaluation result but is explicitly `authority_conferring=false` and can never become a standing authority basis by itself.

### AuthorityState constraints

- exactly one linear chain per state;
- first record is `grant` or `policy`;
- later records, if any, are `delegation` only;
- every record carries complete scalar domain/operation/scope/target bounds;
- delegation may not widen, narrow, union, inherit, or use `any-of`: delegated bounds must be byte/equality-identical to the parent bounds;
- delegation may change only the authorized subject, with explicit `delegated_by` equal to the parent subject;
- every record is independently current at evaluation time under inclusive validity bounds and fail-closed revocation;
- chain IDs are unique and parent links are exact, so cycles/branching are invalid;
- the state has deterministic canonical identity.

This is a new representational constraint for the v1 candidate. It is not asserted to have been the missing quantifier in #59.

### AuthorizationRequest constraints

- request references AuthorityState by exact canonical identity;
- subject, domain, operation, scope, target class, and target reference are scalar and exact-match only;
- no containment, inheritance, aliasing, wildcard, `any-of`, or implicit default semantics;
- referenced A-D objects are opaque immutable references; their semantic payload is not interpreted by E;
- supporting artifacts are separate and never conferring;
- relevant unresolved/contested conflict or residue blocks authorization;
- no request field may claim that a conflict/residue was resolved; applying/discharging resolution state is outside this v1 evaluation surface;
- a separate `domain=resolution, operation=resolve` request may itself be authorized against an exact conflict/residue target, but E does not infer that the resolution occurred.

### Qualification and competence constraint

Qualification is absent from the v1 authority predicate. Competence/qualification material may only appear as non-conferring supporting artifact references. No subject/scope matching predicate is invented.

### Diagnostics

Authorization outcome and authority binding are normative. Diagnostic failure codes may be emitted for observability but are non-authoritative, unordered, excluded from receipt semantic identity, and not a compatibility promise about primary-reason precedence.

## Primary falsifiers

The candidate is falsified for bounded v1 support if any in-domain test demonstrates one of the following:

1. a forged `established`/status-like value creates authority;
2. a supporting artifact, Contract A declaration, Contract B fact, Contract C result, Contract D Decision, execution report, or AuthorizationReceipt can act as standing authority;
3. several partial records can synthesize one authorization;
4. a second surplus conferring record creates an unchosen quantifier inside one evaluation;
5. a delegation widens/changes domain, operation, scope, target class, or target reference;
6. a cyclic, missing-parent, branching, stale, future, or revoked chain authorizes;
7. wrong subject, domain, operation, scope, target class, or target reference authorizes;
8. a parent authority authorizes a child target, a child authorizes a parent, or sibling authority cross-applies without exact target authority;
9. `candidate_for_authorization` becomes execution permission;
10. an execution occurrence is inferred from Authorization;
11. verification authority is inferred from execution authority or report occurrence;
12. an unknown/missing/malformed Contract-E field or version receives a convenient default;
13. relevant conflict/residue information disappears or fails to block;
14. excluded A-D metadata/presentation state mints or changes authority while the immutable A-D reference identity is held fixed;
15. substitution of an immutable A-D target identity fails to invalidate applicability;
16. AuthorizationReceipt identity or AuthorityState identity is non-deterministic for semantically identical canonical objects;
17. the evaluator fails to catch seeded weak implementations for target-blind, stale-blind, nonconferring-basis, Decision→execution, partial-synthesis, or unknown-default behavior.

## Promotion stop rules

Even if the candidate survives internal adversarial testing, do not production-promote in this thread.

If the final candidate is materially different from the frozen RC1 authority-chain object, prepare a new context-free independent reproduction packet and stop at that promotion gate.

If a useful v1 cannot avoid Qualification matching, surplus-conferring quantification, delegation-domain `any-of`, or another unresolved semantic predicate, escalate only that smallest owner decision.
