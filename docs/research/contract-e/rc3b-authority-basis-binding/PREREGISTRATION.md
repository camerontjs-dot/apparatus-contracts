# Contract E Authority Basis Binding RC3B — Preregistration

## Classification

Research / apparatus-contract architecture falsification.

## Parent result

RC3A primary disposition: **FALSIFIED**.

Observed counterexample: the frozen RC3A `authority_basis` shape carried only type/id/currentness. A CAL assessment policy reference therefore satisfied the generic policy requirement after the envelope was relabeled as citation authority. A second Decision→task substitution was rejected only incidentally by a leftover warrant.

Parent result commit: `d6561975ef395bc7cfe96d599d118bc901feb5f6`.

## Exact question

Does binding each authority-basis reference to its own subject/principal, authority domain, operation set, scope, target class, currentness, and validity interval eliminate the RC3A laundering counterexamples without requiring the common validator to interpret CAL/EB/Decision semantic payloads?

## Smallest repair hypothesis

Keep the RC3A common envelope, participant declarations, warrant separation, competence separation, propagation rules, delegation rules, historical validity, and frozen case family unchanged.

Change only the interpretation of `authority_basis`:

> an authority-basis reference has no operative authority unless it resolves to an authoritative basis record whose declared bounds cover the requested subject, domain, operation, scope, target class/identity, and current time.

The research harness may use a frozen registry to resolve basis references. This does **not** require a production centralized registry; a future Contract E may use embedded signed grants, policy records, capabilities, credentials, or other resolvable basis objects.

## Hypotheses

H1 — RC3A counterexamples are rejected for the intended reason: authority-basis binding mismatch.

H2 — Valid RC3A positive envelopes remain valid when their basis references resolve to matching bound records.

H3 — A basis record cannot be repurposed across authority domain, operation, subject, scope, target class, exact target constraint, or validity/currentness.

H4 — Semantic result payload remains irrelevant to common authority validation.

H5 — Warrant remains independent from authority basis: a correct warrant cannot repair a missing/wrong mandate, and a correct mandate cannot repair a wrong warrant where one is required.

## Additional direct basis substitutions

- correct type, wrong authority domain;
- correct domain, wrong operation;
- correct domain/operation, wrong subject;
- correct domain/operation/subject, wrong scope;
- correct domain/operation/subject/scope, wrong target class;
- exact-target grant used for another target;
- revoked/stale authoritative basis while envelope claims current;
- unresolvable basis identifier;
- basis type mismatch between envelope reference and resolved record;
- valid CAL policy reused as citation authority;
- valid Decision policy reused as task authority.

## Success criteria

- all RC3A positive baselines remain accepted;
- all RC3A negative cases are rejected for their preregistered reason or a strictly earlier, more specific authority-basis reason;
- `N13-supported-does-not-cite` and `N14-decision-does-not-execute` are rejected specifically by basis binding before result/warrant semantics can matter;
- all new direct basis substitutions fail closed;
- 27 RC3A semantic-result invariance mutations remain invariant;
- existing propagation, delegation, and historical tests remain unchanged and pass;
- negative controls still fail in the intended unsafe direction;
- no common-validation branch depends on `result.status`, `reported_verdict`, `confidence`, `effect`, or execution-success semantics.

## Falsifiers

Falsify RC3B if:

- basis binding still permits a cross-domain or cross-operation reuse;
- safe basis resolution requires interpreting semantic result payloads;
- exact subject/scope/target binding cannot coexist with reusable standing grants;
- the repair breaks valid participant/warrant separation;
- successful behavior requires changing the frozen RC3A semantic cases rather than authority-basis representation alone.

## Freeze rule

RC3B basis specification, basis registry, and new basis attack cases must be frozen before the RC3B validator is implemented. RC3A frozen files remain immutable.

A scientific failure after freeze requires another successor rather than in-place repair.

## Independence claim

RC3B remains ordinary-context adversarial hardening, not clean-room reproduction. If it survives, the next gate remains `CONTEXT-FREE REQUIRED` independent consumption from a frozen research specification.
