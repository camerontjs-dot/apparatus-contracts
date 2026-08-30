# Next experiment notes — Contract E authority specification and fresh reproduction

Status: successor experiment notes only. This file does not authorize execution, define Contract E, or freeze an acceptance surface. It records the smallest next experiment currently justified by RC0/RC1/RC2 and leaves room to incorporate the pending external deep research before preregistration.

## Working name

**Contract E Authority Interface Specification RC3 — Specification-First Independent Reproduction**

The name is provisional. Do not infer a Contract E version or release from it.

## Primary question

Can the currently supported authority distinctions be expressed as a sufficiently explicit, domain-agnostic **research specification** such that a fresh independent implementation can reproduce the intended participant responsibility, exact binding, jurisdiction, and cross-domain rejection behavior **without access to the reference implementations or hidden stage semantics**?

This is the next discriminating question because RC2 already showed that a common structural authority envelope can be consumed independently from frozen producer-native outputs. It has not shown that the interface can be implemented from prose/schema authority alone.

## Core claim under test

A Contract E research specification can define:

1. common authority-envelope structure;
2. participant responsibility / exclusion declarations;
3. accepted domain / operation / effect boundaries;
4. exact subject / target / currentness bindings;
5. domain-specific receipts without cross-domain implication;
6. standing jurisdiction / delegation references;
7. fail-closed enforcement and escalation behavior;
8. execution / observation / verification separation;

without requiring the consumer to understand Evidence Bundler retrieval semantics, CAL epistemic semantics, Decision Engine policy semantics, or executor-specific business logic.

## Competing explanations

The experiment must preserve at least these alternatives:

### H1 — Real contract hypothesis

The authority interface can be specified independently enough that a fresh implementation reproduces the expected boundaries and rejects the same laundering attacks.

### H2 — Hidden adapter hypothesis

The apparent common interface only works because current research implementations contain undocumented stage-specific knowledge. A fresh consumer cannot reproduce behavior from the specification alone.

### H3 — Over-generalization hypothesis

The common envelope is too generic. Correct behavior requires separate authority-interface families rather than one Contract E pattern.

### H4 — Domain-collapse hypothesis

Information / epistemic authority and operational authority cannot safely share even a structural grammar without introducing ambiguity or accidental authority transfer.

### H5 — Ceremony hypothesis

The declarations add documentation but no discriminating power. Existing contracts/policies already determine all required boundaries, and Contract E adds no costly-to-fake conformance evidence.

## External deep-research intake before freeze

A parallel deep-research effort is examining common authority structures across regulated industries, organizations, business decision-making, and general human processes.

Before preregistration, reconcile that research into a bounded **external-pattern inventory**. Keep source-derived external observations separate from CAL Pipeline evidence.

Candidate categories to extract if the research supports them:

- mandate / competent authority;
- delegation;
- jurisdiction / scope of office;
- ratification / countersignature / adoption;
- separation of duties;
- authority to access information;
- authority to admit / rely on information;
- authority to issue an assessment;
- authority to make a decision;
- authority to communicate / cite / certify;
- authority to execute;
- authority to attest / verify / audit;
- temporal validity / term of authority;
- revocation / supersession;
- conflict / precedence among authorities;
- custody / chain-of-command / provenance of authority;
- residual or retained authority at a higher level.

For every external pattern, record:

- observed source/domain;
- exact authority relation;
- what it governs;
- what it explicitly does not govern, if stated;
- whether delegation is allowed;
- whether ratification is separate;
- what happens on missing / conflicting / expired authority;
- whether enforcement is local or central;
- whether outcome verification is independent;
- whether the pattern is descriptive, normative, legal, procedural, or inferred.

Do not add an external pattern to Contract E merely because it is common. It must either explain an observed pipeline failure, generate a useful falsifier, or improve independent recoverability.

## Proposed specification surfaces to freeze

### Surface A — Common authority envelope

Research candidate fields, names not frozen:

```text
authority_subject / principal / mechanism
authority_type
bounded authority_domain
typed operation / relation
exact subject_or_target identity
currentness / version / hash
applicability
basis / receipt reference
standing grant / delegation reference
status / outcome
reason code
```

The specification must define field semantics and forbidden implications, not merely names.

### Surface B — Participant responsibility declaration

Each participant declares:

```text
participant identity
responsibilities owned
responsibilities explicitly excluded
authoritative upstream artifacts
accepted authority domains
accepted effects / operations
exact binding rules
required jurisdiction checks
forbidden semantic fields for authority derivation
fail-closed behavior
local enforcement point
outputs / receipts produced
```

### Surface C — Domain-specific authority receipt

At minimum include research examples for:

- source access;
- evidence admission;
- assessment mandate;
- numeric semantic authority;
- source-boundary / absence authority;
- Decision mandate;
- citation/use authority;
- execution authority;
- outcome-verification authority.

If CAL entity/population or exception/scope experiments have reached a frozen supported disposition before preregistration, they may be added as **new independent domains**, not folded into a generic semantic-authority field.

### Surface D — Standing jurisdiction / delegation

Research-only representation should cover:

- grant / profile identity;
- grantor / delegator where known;
- grantee / actor;
- domain / operation / target scope;
- expiry / currentness;
- revocation / supersession;
- approval / ratification references;
- delegation constraints;
- independence / separation-of-duty constraints where required.

Do not assume one scalar autonomy level is authoritative.

### Surface E — Enforcement / execution / verification

Specify the separation among:

```text
jurisdiction determination
local enforcement decision
execution attempt / process
executor report
observed post-state
outcome verification
outcome record
```

Execution occurrence must not retroactively establish authorization. Executor self-report must not automatically establish verified post-state.

## Freeze requirements

Before the independent implementer sees any reference behavior, freeze:

1. the complete research specification;
2. normative vocabulary / schemas / examples;
3. participant declarations;
4. mutation rules;
5. acceptance criteria;
6. external-pattern test cases selected from the deep research;
7. producer-native internal fixtures;
8. explicit non-claims;
9. hidden expected outcomes or a sealed oracle where feasible;
10. the information aperture for the independent implementer.

The fresh implementer must not see:

- reference validator / evaluator implementation;
- current Decision Engine authority evaluator source;
- prior Contract E RC implementation details beyond the authorized specification aperture;
- hidden expected outcomes;
- repair history explaining individual fixtures;
- downstream semantic implementations.

## Independent implementation task

From the frozen specification alone, implement a consumer / validator that can:

1. parse participant declarations and domain receipts;
2. validate exact actor / mechanism / operation / target bindings;
3. determine whether a receipt is applicable/current within its declared domain;
4. reject cross-domain use;
5. reject participant effect / operation use outside the participant's declared responsibility;
6. preserve unknown / indeterminate rather than manufacturing permit or semantic validity;
7. distinguish standing jurisdiction from semantic truth;
8. distinguish authorization from execution and verified outcome;
9. emit deterministic reasoned conformance results.

The independent implementation should not be required to reproduce CAL numeric reasoning, retrieval ranking, Decision Engine policy, or executor business logic. If it must, the Contract E abstraction is leaking domain semantics.

## Primary mutation / metamorphic suite

### Identity and currentness

- actor substitution;
- mechanism substitution;
- exact target ID substitution;
- target hash/currentness mutation;
- stale contract version;
- expired authority;
- revoked authority;
- superseded authority.

### Participant responsibility

- citation participant receives task effect;
- task executor receives citation effect;
- CAL assessment participant receives numeric authority receipt as mandate;
- Evidence Bundler admission participant receives source-access receipt as admission authority;
- verifier receives execution authority but no verification authority;
- participant declaration missing;
- responsibility omitted;
- accepted effect/domain omitted.

### Information-authority laundering

- high NLI score used as source-completeness authority;
- source-boundary `valid` used as support authority;
- numeric `invalid` used as composition / policy-decision authority;
- CAL supported conclusion used as citation authority;
- semantic strength/status used as generic authorization;
- unperformed assessment inferred from downstream conclusion;
- inapplicable semantic receipt treated as adverse evidence.

### Operational-authority laundering

- Decision effect treated as self-authorizing execution;
- access authority treated as admission authority;
- citation authority treated as external-send authority;
- execution occurrence treated as proof of prior authorization;
- tool possession treated as authority;
- broad standing grant overrides participant-domain restriction.

### Delegation

- delegate attempts to grant authority it does not possess;
- delegate broadens target scope;
- delegate extends expiry;
- delegate removes verification / separation-of-duty requirement;
- revoked parent grant leaves child grant active;
- conflicting grants with no precedence rule.

### Semantic invariance

Hold the authority descriptor fixed while changing irrelevant semantic payload bytes. Jurisdiction / conformance should remain unchanged.

### Authority invariance

Hold semantic artifacts fixed while changing standing grant / jurisdiction state. Semantic outputs should remain unchanged while authorization outcome changes appropriately.

### Unknowns

- unknown authority domain;
- unknown operation;
- missing currentness;
- missing applicability;
- conflicting authority receipts;
- unresolved precedence;
- unavailable authority source.

Unknown must remain distinguishable from explicit denial and explicit semantic invalidity.

## External-pattern cohort

After the deep research is complete, construct a small heterogeneous cohort from real authority patterns without importing domain-specific conclusions.

Possible shapes only if supported by the research:

- regulated batch / quality release: assessor, approver, release authority, executor, independent verification;
- financial payment / treasury: preparer, approver, signer, settlement executor, reconciliation;
- software release: code author, reviewer, release authority, deployment executor, post-deploy verifier;
- legal / corporate action: recommendation, authorized officer / board adoption, execution, attestation;
- clinical / medical process: information source, qualified decision authority, order execution, outcome observation;
- ordinary delegated work: principal delegates bounded authority to agent, agent encounters out-of-scope action and escalates.

The objective is not to prove every industry follows one ontology. The objective is to test whether the Contract E grammar can represent materially different authority arrangements without losing the distinctions each arrangement requires.

## Acceptance criteria

A strong PASS requires all of the following:

1. independent implementation reproduces the frozen conformance outcomes without reference implementation access;
2. internal producer-native fixtures remain consumable without hidden translation logic;
3. cross-domain laundering mutations fail closed;
4. participant-domain substitutions fail closed;
5. semantic payload mutations outside authority fields do not change jurisdiction;
6. authority-profile mutations do not rewrite semantic artifacts;
7. unknown / inapplicable / revoked / denied remain distinct where specified;
8. execution and verification remain distinct from authorization;
9. external-pattern cohort can be represented without adding domain-specific semantic logic to the common authority layer;
10. the independent implementer can explain each result using only specification-defined fields / rules.

## Falsifiers / stopping rules

### Falsify the single Contract E pattern if

- different domains require incompatible meanings for the same core field;
- independent implementation needs hidden knowledge of CAL / EB / Decision semantics;
- external patterns require mutually incompatible authority relationships that cannot be represented without semantic special cases;
- participant declarations cannot prevent laundering without embedding domain decision logic;
- a common envelope introduces ambiguity that separate typed interfaces avoid.

### Narrow rather than fail universally if

- informational and operational authority need separate contract families sharing only lower-level vocabulary;
- standing delegation and semantic authority require different persistence / currentness models;
- ratification or verification proves to be a distinct interface rather than a subtype;
- only some stages need Contract E declarations.

### Stop before implementation repair if

- the frozen specification omits a field necessary for independent reproduction;
- acceptance requires guessing an unstated semantic mapping;
- a new external authority relation appears after freeze that would materially change the specification.

Preserve the failure and create a successor revision rather than repairing the same frozen experiment after reveal.

## Evidence to preserve

The terminal record should include:

- exact SHAs and frozen artifacts;
- specification hash;
- information aperture;
- independent implementation freeze;
- mutation outcomes;
- disagreements against reference behavior;
- apparatus failures and deviations;
- any fields or concepts the independent implementer could not recover;
- false permits / false semantic authority grants;
- false escalations / unnecessary human-intervention cases;
- external-pattern cases that did not fit the model;
- explicit non-claims.

## Promotion boundary

Even a clean PASS would justify only a **minimal Contract E research candidate / promotion proposal**. It would not by itself authorize:

- production Authority Control Plane implementation;
- automatic operational mutation;
- production delegation defaults;
- a universal semantic evaluator;
- legal / regulatory authority claims;
- replacement of domain-specific policy;
- Contract E 1.0.0 release without the separate governance and release gates.

## Current thread state

The conceptual convergence question is terminal for RC2: a common structural authority-interface pattern has independent cross-repository support on the tested cuts.

The remaining question above is a **new experiment** because it tests specification sufficiency and independent recoverability rather than the already-tested architecture pattern.

The pending external deep research should be incorporated before the new preregistration freeze if it arrives in time, primarily as counterexample and falsifier material rather than as normative contract authority.
