# Contract E Authority / Warrant Specification RC3A — Preregistration

## Classification

Research / apparatus-contract architecture falsification.

This experiment is stacked on the accepted cross-repository authority-interface RC2 evidence. It is not a clean-room or independent reproduction because this execution context already knows the prior architecture and results.

## Question

Can a minimal Contract E research specification represent bounded informational and operational authority strongly enough to reject authority laundering, over-broad propagation, and competence/warrant/jurisdiction collapse without importing Evidence Bundler, CAL, Decision Engine, or executor domain semantics into a universal evaluator?

## Starting authority

- Apparatus Contracts parent research head: `cfb717304388d2997f86f85850a6c32c3c0758f8`
- Parent cross-repository RC2 accepted science head: `c9ec5242818755c3e92c92e75412b84cef0eaa50`
- CAL semantic-authority RC2 accepted science head: `4000f37b1f861cca696cb9852722fee8f4f50f0b`
- Prior RC2 independent consumer result: common structural authority envelope supported; universal authority evaluator not established.

The cross-disciplinary authority review supplied by the operator is used only as a hypothesis and counterexample generator. It is not treated as contractual authority or proof that a proposed field belongs in Contract E.

## Candidate distinctions under test

The specification must keep independently mutable:

1. identity / provenance;
2. competence or qualification;
3. authority basis / mandate / delegation;
4. jurisdiction scope;
5. applicability/currentness;
6. evidence or observation identity;
7. warrant for a specific inference or transition;
8. domain-specific conclusion/status;
9. operational permission;
10. execution occurrence;
11. verification authority and observed outcome;
12. accountability / audit identity where represented.

## Hypotheses

### H1 — Shared grammar, disjoint domains

Informational and operational authority can share a common structural envelope while authority domains remain non-interchangeable.

### H2 — Competence firewall

Competence/qualification does not imply mandate/jurisdiction, and mandate/jurisdiction does not imply competence when a domain requires a qualification predicate.

### H3 — Warrant firewall

A warrant licenses only its declared inference/transition over its exact inputs, domain, target, and applicability conditions. Possessing a valid warrant does not itself grant organizational or execution authority.

### H4 — Propagation is explicit and default-non-transitive

Identity/provenance may propagate when explicitly declared, but semantic, decision, citation, execution, and verification authority do not automatically flow downstream. A downstream transition must either consume explicitly propagable authority or establish a new authority relation.

### H5 — Applicability before authority exercise

A current credential or receipt outside scope, target, time, relation family, or operation is insufficient to exercise authority.

### H6 — Evidence-state distinctions do not collapse

Authentication, admission, relevance, support, sufficiency, semantic validity, and decision authority are distinct. No positive state in one domain may silently imply the next.

### H7 — Historical authorization is not rewritten by later revocation

The system can represent `valid_at_execution=true` while `currently_valid=false` when authority was legitimately exercised before later expiry/revocation, unless a domain explicitly defines retroactive invalidation.

### H8 — Explicit non-implications are enforceable

A participant/specification can declare conclusions or operations that MUST NOT be derived from a receipt/artifact, and the validator can detect prohibited cross-use without understanding the semantic payload itself.

## Primary adversarial cases

1. qualified actor, no mandate;
2. mandated actor, missing/expired required qualification;
3. valid numeric warrant used for source-boundary conclusion;
4. valid source-boundary warrant used for numeric conclusion;
5. CAL assessment mandate used as support authority;
6. supported CAL conclusion used as citation authority;
7. typed Decision used as execution permission with no standing grant;
8. execution permission used as verified-outcome authority;
9. authenticated source used as evidence relevance;
10. admitted evidence used as evidential support;
11. relevant evidence used as sufficiency;
12. sufficient evidence used as decision mandate;
13. source identity/provenance propagation across stages;
14. semantic authority propagation attempt across stages;
15. delegation wider than parent authority;
16. valid credential used for wrong operation/target;
17. expired authority used for a new act;
18. later revocation applied to an earlier valid act;
19. unknown authority domain;
20. generic `authorized: true` shortcut;
21. missing warrant where the transition claims an inference;
22. correct warrant, wrong target hash/currentness;
23. correct authority domain, inapplicable scope;
24. correct semantics with wrong participant responsibility domain.

## Negative controls

### N1 — Collapsed authority object

A naive object with `trusted`, `authorized`, `confidence`, and `success` fields is expected to permit at least one cross-domain laundering attack.

### N2 — Transitive inheritance

A naive propagation rule that carries all upstream authority to all descendants is expected to over-authorize at least one semantic or operational transition.

### N3 — Credential-only authority

A naive rule that treats a valid credential/qualification as sufficient authority is expected to accept a competent but out-of-jurisdiction actor.

## Success criteria

RC3A supports a specification candidate only if all of the following hold:

- every intended positive case validates;
- every preregistered laundering/substitution case is rejected or preserved as indeterminate;
- competence and jurisdiction can vary independently;
- warrant and mandate can vary independently;
- provenance propagation can be allowed without propagating semantic/action authority;
- later revocation can invalidate new actions without rewriting an earlier valid-at-time receipt;
- the validator does not inspect domain semantic payload fields to determine cross-domain authority;
- no generic `authorized: true`, confidence score, positive verdict, or success report is sufficient authority;
- negative controls fail in the intended direction.

## Falsifiers

Falsify or substantially narrow the candidate if:

- correct behavior requires the common validator to understand CAL/EB/Decision semantic internals;
- a single authority state must simultaneously encode epistemic validity and execution permission;
- competence and mandate cannot be represented independently without contradiction;
- warrant cannot be bounded to a declared transition/inference;
- safe propagation requires implicit transitive inheritance;
- domain-specific validity cannot coexist with common structural validation;
- the proposed minimal fields cannot distinguish valid-at-time from current authority;
- explicit non-implications cannot be mechanically checked without a domain ontology.

## Controlled invariants

- no production schema or runtime changes;
- no Contract E canonical version;
- no change to Contracts A/B/C/D;
- no production CAL/Decision Engine/Evidence Bundler behavior;
- parent RC2 artifacts remain immutable;
- the candidate spec and fixture set must be frozen before the executable validator is written;
- failures are preserved, not tuned away under the same freeze.

## Independence boundary

A passing RC3A does **not** establish independent recoverability of the specification. If RC3A survives, a separate `CONTEXT-FREE REQUIRED` reproduction must implement the consumer using only the frozen specification/fixtures and allowed governance aperture.

## Allowed terminal dispositions

- SUPPORTED FOR PROMOTION — only to the next research-specification/fresh-reproduction gate, never production;
- FALSIFIED;
- INCONCLUSIVE;
- SUPERSEDED.
