# Authority model thread synthesis

Status: research synthesis only. This document captures the conceptual progression and evidence accumulated across the Contract E / authority discussion. It does not define Contract E 1.0.0, establish production authority policy, or promote a universal evaluator.

## 1. Starting point: Decision -> Authorization -> Execution

The initial model treated authorization as a downstream stage after Decision:

```text
Evidence / assessment -> Decision -> Authorization -> Execution
```

That framing was useful for establishing three separations:

1. a Decision does not itself grant mutation authority;
2. Authorization is not Execution;
3. an execution attempt or executor success report is not proof of the resulting external state.

This led to the more explicit execution chain:

```text
Execution authorization
-> enforcement
-> execution attempt / process
-> resulting reality
-> observation
-> outcome verification
-> outcome record
```

An operation can be authorized and fail. An operation can occur without authorization. An executor can report success while the post-state disagrees. None of those facts retroactively rewrite the others.

## 2. Authority to decide, ratify, execute, and verify

The next refinement separated several authority relations that had been hidden under one word:

- **Decision authority / mandate**: who or what is empowered to make a class of Decision;
- **Ratification / adoption authority**: who must approve or adopt a Decision before it becomes effective, where required;
- **Execution authority**: who may perform the resulting operation;
- **Verification authority**: who or what may authoritatively establish the resulting state.

Candidate lifecycle:

```text
Authority to Decide
-> Decision Process
-> Decision
-> Ratification / Adoption, where required
-> Authority to Execute
-> Enforcement
-> Execution
-> Reality changes
-> Observation
-> Outcome Verification
-> Outcome Record
```

Not every workflow needs every step. In low-consequence settings, several relations may be delegated to one actor or automated policy. In regulated or high-consequence settings, separation of duties may require different actors.

A load-bearing alternative remains important: these authority relations may be orthogonal predicates over lifecycle transitions rather than mandatory serial pipeline stages.

## 3. Authorization is better modeled as cross-cutting standing authority

The discussion then shifted from a sequential Authorization apparatus toward a standing authority / delegation model configured at the platform or operator level.

The key idea is:

> Authorization policy is ambient; authorization evaluation is event-specific.

An operator may configure a posture such as manual, supervised, or delegated. The posture compiles to explicit grants, restrictions, approval requirements, scope limits, expiry, revocation, and verification obligations. A simple UI may feel like a dial or gear selector, but the underlying authority should remain typed and auditable rather than represented as a vague percentage of autonomy.

Example conceptual policy:

```text
research.read                 delegated
research.assess               delegated
repository.write.docs         delegated
memory.admit                  supervised
repository.write.runtime      higher authority required
production.promote            retained by operator
external.send                 higher authority required
```

Human intervention is therefore an exception path when standing authority is insufficient, not a required stop after every Decision.

## 4. Jurisdiction is the key runtime concept

A standing authority does not make every operation permissible. Each authority-sensitive boundary must determine whether the relevant authority has **jurisdiction** over the exact matter.

A jurisdiction check asks questions such as:

- does the authority exist and remain current?
- does it cover this actor or mechanism?
- does it cover this typed operation?
- does it cover this exact target / target class / current state?
- does it cover this context, environment, domain, scale, or consequence level?
- does it satisfy any required approval / ratification / independence condition?

Candidate outcomes are intentionally richer than a boolean:

```text
IN_JURISDICTION
OUT_OF_JURISDICTION
REQUIRES_HIGHER_AUTHORITY
INDETERMINATE
```

Only a positive in-jurisdiction result may permit local enforcement to proceed. Unknown authority must not silently become permission.

## 5. Authority and authorization terminology

The working terminology became:

- **Authority**: standing or delegated governance state defining who or what has power over a bounded domain;
- **Jurisdiction**: whether that authority covers the exact subject / operation / target / context now;
- **Authorization**: runtime determination that a proposed act is permitted under applicable authority;
- **Approval / Ratification**: an act by a higher or required authority that changes the authorization context for a bounded matter;
- **Enforcement**: the local capability holder refusing to act without sufficient jurisdiction;
- **Execution**: the actual attempted/performed process;
- **Observation / Verification**: separately establishing what happened in reality.

This avoids treating possession of a tool or API capability as authority.

## 6. Contract E changed from an Authorization object to an authority interface contract

The working Contract E hypothesis changed substantially.

Contract E is no longer best described as a mandatory serialized object between Contract D and execution. The stronger candidate is a **cross-cutting Authority Interface Contract** implemented by pipeline participants.

Its candidate responsibilities are:

1. define what each participant is authoritative for;
2. define what each participant explicitly does not own;
3. define what authority-sensitive operations it may expose or consume;
4. define exact bindings from authoritative upstream artifacts to actor / operation / target descriptors;
5. define participant-specific accepted effect / operation domains;
6. define required jurisdiction checks before authority-sensitive transitions;
7. define enforcement, escalation, and fail-closed obligations;
8. preserve semantic fields that are explicitly forbidden from acquiring authority in the current domain.

Contract E therefore resembles a protocol plus participant conformance declarations more than one universal runtime JSON record.

## 7. Participant responsibility declarations

A participant declaration is expected to say, conceptually:

```yaml
participant: claim-audit-lab

owns:
  - epistemic_assessment

excludes:
  - operational_decision
  - citation_permission
  - execution
  - verified_outcome

authority_sensitive_operations:
  - assessment.issue

authoritative_inputs:
  - exact Contract B bundle / claim identity

forbidden_as_authority:
  - generic source trust label
  - upstream nomination lane
  - downstream operational policy
```

A citation consumer might instead declare that it consumes only a typed Decision effect such as `cite_as_evidence`, and a task executor only `dispatch_task`.

This matters because exact field mapping is insufficient if a participant can truthfully map an effect it was never responsible for consuming.

## 8. RC1 result: participant-domain boundaries are necessary

The first frozen participant-binding implementation failed usefully.

A citation participant and task participant both truthfully mapped typed Decision effects through a global effect registry. Because the declarations did not restrict which effects each participant could consume, citation could consume `dispatch_task` and task execution could consume `cite_as_evidence`.

The smallest repair was not an evaluator change. It was a participant-domain declaration:

```text
citation participant accepts only: cite_as_evidence
task participant accepts only: dispatch_task
```

Cross-use then failed as `participant_effect_out_of_scope`.

This established an important principle:

> Truthful fields do not by themselves establish truthful responsibility. Contract E must define both exact binding and the domain over which a participant has authority to make that binding.

## 9. Upstream authority: access and evidence admission are separate

The authority model expanded upstream of CAL and potentially upstream of Evidence Bundler.

Two distinct relations were identified and experimentally separated:

### Source access authority

May an actor / apparatus access, read, retrieve, or process this source or corpus?

Example operation:

```text
source.read
```

### Evidence admission authority

May this exact source / passage / artifact enter the evidence aperture being supplied downstream?

Example operation:

```text
evidence.admit_passage
```

These are not equivalent to semantic relevance, support, truth, completeness, or reliability.

A real policy may require source access as a prerequisite to evidence admission, but the two relations remain semantically separable.

The representation could range from exact-item authority to an aperture delegation such as:

> Evidence Bundler may access this corpus and admit passages within this bounded retrieval/admission policy.

The latter is more compatible with low-human-intervention operation. Contract E should describe the authority relation without deciding which governance posture is correct.

## 10. CAL assessment mandate is separate from CAL semantic authority

CAL may possess the operational mandate to issue an assessment over an exact Contract B claim / bundle while its internal semantic apparatuses possess narrower informational authority over particular measurements or relations.

Therefore:

```text
CAL has valid evidence
!= CAL is authorized to issue an assessment
```

and:

```text
CAL is authorized to issue an assessment
!= every CAL mechanism has authority over every semantic relation
```

The operational `assessment.issue` mandate and epistemic semantic-authority domains must not be collapsed.

## 11. Citation / use authority is downstream and distinct

A CAL or Contract C conclusion does not automatically authorize downstream citation or use.

The research negative control demonstrated that a broad standing profile could permit a syntactically valid `citation.use` request if participant binding was bypassed. Contract E-style binding rejected a citation request constructed directly from a CAL conclusion because the required typed citation Decision / effect / target was absent.

Therefore:

```text
CAL conclusion
!= citation authority
```

Likewise, a valid typed Decision effect does not self-authorize execution:

```text
Decision effect
!= current execution authority
```

Both truthful artifact binding and current standing jurisdiction are required.

## 12. Information / epistemic authority emerged as a second axis

A parallel CAL research thread introduced a deeper question:

> What information is allowed to have authority over what downstream semantic state?

This is distinct from operational authority but structurally related.

Examples:

- an NLI model may have bounded authority over a textual-relation measurement but not over source completeness or execution permission;
- a structural-negation operator may have authority only within a demonstrated semantic family, not generic authority to invalidate refutation evidence;
- a numeric relation apparatus may establish a bounded numeric relation but not automatically a composed policy conclusion;
- a source-boundary apparatus may establish absence / completeness state but not proposition support.

The core epistemic principle is:

> A measurement, receipt, or apparatus may only decide inside the semantic domain for which its applicability and authority have been established.

Missing or inapplicable authority remains unknown rather than being reverse-engineered from downstream status.

## 13. CAL Semantic Authority / Jurisdiction RC2

The CAL semantic-authority experiment supported the typed pattern:

```text
measurement
-> applicability
-> authority domain
-> validity
-> aggregation / decision
```

Observed bounded domains included:

- numeric relation;
- source boundary / absence;
- assessment mandate;
- composition as a separate authority domain.

Property, scope, unit, and relation geometry mutations failed closed for numeric authority. Numeric receipts could not acquire composition authority. Source-boundary receipts could not be substituted for numeric authority.

The result supports typed semantic authority as a research architecture candidate, not production promotion.

## 14. Information authority and operational authority share a grammar, not an evaluator

The independent Apparatus Contracts cross-repository RC2 consumed producer-native outputs from Evidence Bundler, CAL, and Decision Engine.

It normalized stage descriptors and semantic receipts into a common structural envelope containing concepts such as:

```text
authority subject / mechanism
bounded authority domain
typed operation
exact target
currentness / reference
applicability
basis / receipt
```

Seven cross-domain laundering attempts were rejected, including:

- source access -> evidence admission;
- evidence admission -> CAL assessment mandate;
- CAL assessment mandate -> numeric semantic authority;
- numeric semantic authority -> Decision mandate;
- Decision mandate -> source-boundary authority;
- source-boundary authority -> numeric authority;
- citation use -> task dispatch.

This supports a common **authority interface pattern** while explicitly not establishing one universal authority evaluator.

The strongest supported formulation is:

```text
authoritative observation / artifact
-> truthful participant binding
-> typed jurisdiction domain
-> applicable operation / target
-> local semantic or action evaluation
```

## 15. Apparatus authority envelope

A useful general abstraction is that every apparatus or artifact has an **authority envelope**: the bounded set of propositions, transitions, or operations it may legitimately govern, plus explicit exclusions.

Conceptually:

```yaml
authority_holder: apparatus / actor / policy / receipt
authority_type: informational | operational
domain: bounded relation or operation family
subject_or_target: exact identity / scope
basis: exact observation / artifact / delegation
currentness: current / expired / revoked / superseded
applicability: applicable / inapplicable / unknown
may_establish_or_perform:
  - ...
explicitly_excludes:
  - ...
```

This can be viewed as an authority graph or an information-flow type system for authority, but that broader formulation remains a hypothesis rather than a promoted architecture.

## 16. Contract authority envelopes

The same discipline can be applied to transport contracts themselves.

### Contract B

May authoritatively represent exact evidence inputs, identities, provenance, and declared factual context supported by its schema.

Must not silently authorize a consumer to infer proposition support, semantic validity, source completeness, or downstream action.

### Contract C

May authoritatively represent CAL's performed assessments, measurements, conclusions, basis, policy identity, and explicit unknown state actually emitted by CAL.

Must not silently authorize citation, operational mutation, universal truth, or unmeasured completeness.

### Contract D

May authoritatively represent the exact downstream policy Decision / typed effect supported by the frozen Decision contract.

Must not silently establish epistemic correctness or actor execution authority.

### Candidate Contract E

Would define the authority interface, participant responsibility, exact binding, bounded authority domains, standing jurisdiction references, and enforcement obligations.

It must not become a universal truth or policy engine.

## 17. Candidate Contract E surfaces supported for research specification

The current evidence supports separating at least five surfaces:

1. **Common authority envelope**
   - authority subject / mechanism identity;
   - authority domain;
   - typed operation / relation;
   - exact target / subject identity and currentness;
   - applicability / validity prerequisites;
   - basis / receipt reference.

2. **Participant responsibility / binding declaration**
   - responsibilities owned;
   - responsibilities explicitly excluded;
   - accepted effect / operation domain;
   - authoritative upstream artifacts;
   - exact binding rules;
   - semantic fields forbidden from authority use.

3. **Domain-specific authority receipt / payload**
   - semantic validity, source boundary, access/admission, Decision mandate, citation/use, execution, verification, or other bounded domain;
   - domain-local status and reasons;
   - no cross-domain implication.

4. **Standing jurisdiction / grant reference**
   - delegation / profile / grant identity;
   - currentness / expiry / revocation / supersession;
   - approval / ratification references where applicable;
   - kept distinct from semantic truth.

5. **Enforcement / outcome receipt**
   - what the local participant attempted / performed;
   - what was observed afterward;
   - verification authority independently bindable where required.

## 18. Human-in-the-loop minimization

The authority model is intended to reduce unnecessary operator intervention without weakening boundaries.

The objective is not "maximum autonomy." It is:

> minimize operator interventions while preserving all required authority boundaries and escalating only when standing authority is insufficient.

The earlier bounded autonomy experiment showed decreasing higher-authority escalation under increasingly delegated profiles without creating protected false permits in the frozen cases.

A future user-facing "dial" should therefore compile to explicit grants and restrictions rather than encode authority as a scalar trust score.

## 19. Important unknowns and falsifiers

Still unresolved:

- canonical Contract E field names and schema;
- whether Contract E is one artifact, a family of artifacts, a protocol, sidecars, embedded declarations, or some combination;
- persistence rules for jurisdiction evaluations, approvals, grants, execution receipts, and verification receipts;
- production delegation hierarchy and revocation topology;
- conflict / precedence when multiple authorities overlap or disagree;
- whether ratification is a distinct generic authority relation or a specialized approval relation;
- how authority provenance terminates without infinite regress;
- how root / organizational / regulatory authority is represented;
- how independently verified participant identity is established;
- reliable natural-language extraction for typed semantic inputs;
- composition, quantifier, temporal, entity/population, exception, and other semantic authority domains beyond tested cuts;
- independent conformance across every eventual producer and consumer;
- whether the common authority grammar remains useful outside the current CAL Pipeline domains.

Falsify or narrow the model if:

- safe operation requires semantic truth and execution permission to collapse into one state;
- a participant cannot truthfully declare its authority boundary without importing another participant's domain semantics;
- common authority fields become so generic that consumers need hidden stage-specific knowledge to interpret them;
- independent implementations cannot reproduce the boundary behavior from the specification;
- authority declarations merely rename existing policy without improving falsifiability, conformance, or audit reconstruction.

## 20. External deep research posture

A parallel deep-research effort is examining authority commonalities in industry, regulated environments, organizations, and general decision processes.

That research should be used as:

- a source of candidate authority relations and terminology;
- a source of counterexamples to the current architecture;
- a way to identify recurring human / institutional patterns such as mandate, delegation, ratification, separation of duties, jurisdiction, competent authority, approval, custody, attestation, verification, and revocation;
- a generator of new falsifiers and cross-domain test cases.

It should **not** automatically become Contract E authority. External practice, legal doctrine, or organizational convention must remain distinguishable from what the CAL Pipeline experiments have established.

The correct reconciliation question is not "does industry use the same words?" It is:

> Does a proposed authority abstraction preserve the distinctions required by both the observed pipeline failures and independently documented real-world authority systems, without importing one domain's semantics into another?

## 21. Current bounded conclusion

The strongest supported architecture at this point is:

> Authority is cross-cutting standing governance and epistemic state expressed through bounded domains. Jurisdiction determines whether a particular authority applies to an exact subject / operation / target in context. Contract E is best researched as the common interface and responsibility contract that makes those boundaries explicit, while local semantic and operational apparatuses retain ownership of their own domain logic.

This is supported for a research specification. It is not yet sufficient for Contract E 1.0.0 or production promotion.
