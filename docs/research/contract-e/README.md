# Contract E Brainstorm — Authority, Ratification, Execution, and Outcome Verification

Status: research brainstorm / non-authoritative

This document is a holding surface for the next authority-boundary research question. It does **not** define Contract E, establish that a fifth durable contract is required, assign field names, or authorize production behavior.

The name `Contract E` is provisional shorthand only. Decision Engine research explicitly left open whether authorization should be a persisted contract, a policy query, a scoped capability, an approval record, or a combination of transient authorization plus durable execution receipts. Do not infer persistence from the letter.

## Live authority inspected before this note

Apparatus Contracts:

- `main`: `00bdf9546a877f9f6c1d7fd227fd959e1d7aa99e`

Decision Engine:

- promoted Decision / Authorization boundary on `main`: `f7c3759dfac7ee4be45879b8266b5eb1440530ee`
- Decision / Authorization Seam RC0: PR #14
- Decision / Authorization Cross-Use-Case RC1: PR #15
- architecture promotion: PR #17
- authorization research handoff: PR #18, inspected at head `aebb1ba04b8ebd795920d00b90c1671e74c85246`

Primary Decision Engine architecture authority remains:

- `docs/DECISION_AUTHORIZATION_BOUNDARY.md`

PR #18's `docs/AUTHORIZATION_RESEARCH_NOTES.md` is research guidance, not promoted architecture authority.

## Starting observation

The currently promoted Decision Engine evidence supports this narrow boundary:

```text
Decision
  != operational permission

Authorization
  consumes exact Decision + actor/action/context

Execution
  remains downstream
```

RC0 showed that authorization context could change while a frozen Decision remained byte-identical.

RC1 showed that a generic `eligible` conclusion was not enough operational authority: cross-use-case substitution was possible until the requested action was bound to a typed Decision effect or equivalent policy-specific output.

That evidence supports a seam. It does not yet tell us how many authority relations exist around the seam or what must be persisted.

## New decomposition under investigation

The working model is now richer than:

```text
Decision -> Authorization -> Execution
```

A candidate decomposition is:

```text
Authority to Decide
        ↓
Decision Process
        ↓
Decision
        ↓
Decision Ratification / Adoption, where required
        ↓
Authority to Execute
        ↓
Enforcement
        ↓
Execution Process
        ↓
Resulting Reality
        ↓
Observation
        ↓
Outcome Verification
        ↓
Outcome Record
```

Not every use case should require every stage. The research question is whether these are genuinely separable authority/state relations and, if so, which ones deserve common machinery.

## Important correction: execution is not outcome truth

A previous shorthand risked collapsing execution with a report that an action occurred successfully.

These should remain distinct:

```text
execution authorization
        ↓
execution attempt
        ↓
execution process
        ↓
observed resulting state
        ↓
outcome assessment / verification
        ↓
outcome record
```

Examples of materially different states:

```text
Decision: valid
Execution authorization: valid
Execution: attempted
Observed outcome: failed
```

```text
Decision: valid
Execution authorization: missing
Execution: occurred anyway
Observed outcome: successful
```

```text
Decision: valid
Execution authorization: valid
Executor reports success
Observed target state: unchanged
Outcome verification: failure / inconsistency
```

A system that compresses all three to `success` loses decision-relevant information.

## Candidate authority relations

### 1. Decision authority / decision mandate

Question:

> Who or what is authorized to make this class of decision over this class of target under this policy?

The same substantive conclusion produced by an actor outside its mandate may be a correct recommendation without being an authoritative Decision.

Candidate inputs:

- actor / decision-maker identity;
- role or system identity;
- decision-policy identity and version;
- target class and scope;
- input-authority class;
- validity window;
- delegation state;
- revocation state.

### 2. Decision ratification / adoption authority

Question:

> Must another authorized actor approve, adopt, or sign off the Decision before it becomes effective?

This may be absent in fully delegated decision classes.

Possible patterns:

```text
authorized system decides
-> Decision is effective immediately
```

or:

```text
authorized system recommends / decides
-> authorized reviewer ratifies
-> Decision becomes effective
```

Ratification must not silently rewrite the Decision's semantic content.

### 3. Execution authority

Question:

> Given an effective Decision, who or what may perform this exact operation on this exact target now?

Candidate inputs overlap with, but are not identical to, decision authority:

- exact Decision identity/hash;
- execution actor identity/role;
- requested operation/effect;
- exact target identity and current hash;
- execution delegation profile;
- approval/ratification receipts where applicable;
- environment;
- validity/expiry/currentness;
- revocation/supersession state;
- rate, batch, budget, rollback, or side-effect restrictions.

### 4. Verification authority

Question:

> Who or what is trusted to establish what actually happened after execution?

The executor's own statement may be evidence, but it need not be sufficient verification.

Possible authoritative verifiers include:

- independent human review;
- validated instrumentation;
- deterministic post-condition checks;
- independent consumers;
- external system-of-record state;
- second-person verification where required.

The verifier may establish observed post-state without deciding whether the original Decision was correct.

## Working hypothesis: authority may be the centralizable apparatus

The strongest current centralization hypothesis is not a universal Decision Engine and not necessarily a universal Authorization object.

It is a shared **Authority Control Plane** that can answer different authority questions while leaving domain semantics with the systems that own them.

Candidate query families:

```text
may_decide(actor, policy, target, context)

may_ratify(actor, decision, context)

may_execute(actor, decision, operation, target, context)

may_verify(actor_or_system, outcome_type, target, context)
```

Potential shared control-plane concerns:

- actor/principal identity;
- role and delegation;
- scope;
- target identity;
- typed operation/effect identity;
- policy identity/version/hash;
- validity and expiry;
- revocation;
- approval/ratification requirements;
- segregation-of-duties rules;
- rate, batch, budget, or side-effect constraints;
- approval receipt verification;
- policy distribution;
- audit reconstruction.

This would centralize authority mechanics without centralizing epistemic truth or domain policy semantics.

## Candidate topology

A plausible topology to test is logically centralized governance with local enforcement:

```text
                 Authority Control Plane
        ┌───────────────────────────────────┐
        │ delegation / policy administration│
        │ actor + scope registry            │
        │ effect / operation registry       │
        │ ratification requirements         │
        │ revocation + currentness          │
        │ approval receipt validation       │
        │ audit / policy lineage            │
        └────────────────┬──────────────────┘
                         │
                  versioned policy
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
      local policy   local policy   local policy
      evaluator      evaluator      evaluator
          │              │              │
      enforcement    enforcement    enforcement
          │              │              │
       executor       executor       executor
          │              │              │
       observed       observed       observed
       outcome        outcome        outcome
          │              │              │
      verification   verification   verification
```

A centralized online policy-decision point remains an alternative. The topology should be determined experimentally rather than by architectural preference.

## Candidate artifact classes

Do not freeze these as contracts yet.

A useful conceptual shorthand is:

```text
E = epistemic/evidence authority
D = Decision
R = ratification or approval receipt, if required
A = execution authorization / scoped grant, if required
X = execution attempt/process record
O = observed outcome / verification record
```

Possible bindings:

```text
D -> exact upstream authority + target + decision policy

R -> exact D + ratifier + scope + time

A -> exact effective D + actor + operation + target + execution policy + approvals

X -> exact authorization/grant + exact attempted operation + pre-state

O -> exact execution identity + observed post-state + verifier identity + verification method
```

A major open question is whether `R`, `A`, `X`, and `O` need separate durable objects, can be receipts under one protocol, or should be partly transient and reproducible.

## Approval should not be a bare boolean in production machinery

Research harnesses may use a boolean to isolate a seam, but a real approval/ratification representation likely needs to bind to the exact object reviewed.

Candidate approval receipt properties:

- approver identity;
- role / approval authority identity;
- exact Decision hash;
- exact authorization request hash where relevant;
- target identity and current hash;
- requested operation;
- scope;
- issued time;
- expiry;
- reuse policy;
- integrity/signature identity;
- revocation/supersession state.

Changing the reviewed object should not silently preserve the approval.

## Distinguish authorization from authorization evaluability

Do not collapse policy-evaluation failure into a substantive denial if the distinction matters downstream.

Candidate two-axis representation:

```text
evaluation:
  APPLICABLE
  NOT_APPLICABLE
  INDETERMINATE

authorization:
  PERMIT
  DENY
  REQUIRE_APPROVAL
```

Execution should proceed only on explicit `PERMIT` under a valid evaluation.

This vocabulary is illustrative, not proposed contract semantics.

## Candidate enforcement seam

Authorization is not enough if the component holding the dangerous capability can ignore it.

Candidate separation:

```text
Authorization / grant
        ↓
Enforcement point
        ↓
Executor
```

The enforcement point should verify, as applicable:

- authorization/grant integrity;
- exact Decision binding;
- actor binding;
- operation/effect binding;
- target identity and current hash;
- expiry/currentness;
- revocation;
- ratification/approval requirements;
- policy version;
- one-use / replay constraints.

The component capable of producing the side effect must enforce the boundary. Central bookkeeping that an operation was intended to be authorized is not sufficient.

## Proposed research program

The next work should test the decomposition before designing a schema.

### Experiment E-RC0 — Authority-relation separability

Objective:

Determine whether decision mandate, decision ratification, execution authority, and outcome verification can vary independently while the underlying Decision semantics and operation are held fixed.

Use one frozen Decision and one bounded operation class. Prefer a research-only or reversible operation with an independently observable target state.

Candidate operation:

- protected repository documentation mutation in a disposable research fixture; or
- frozen MainFrame task-dispatch canary with no consequential external side effect.

Freeze:

- Decision bytes/hash;
- target pre-state/hash;
- requested operation bytes/hash;
- authority-policy fixtures;
- actor identities/roles;
- expected post-condition;
- evaluator logic;
- falsifiers.

Run a factorial or pairwise matrix covering at least:

1. authorized decision-maker / unauthorized decision-maker;
2. ratification not required / required and absent / required and present;
3. correct ratifier / wrong ratifier;
4. execution actor authorized / unauthorized;
5. correct operation / operation substitution;
6. correct target / target substitution;
7. target unchanged / target mutated after authorization;
8. Decision current / superseded;
9. execution succeeds / execution fails / execution partially applies;
10. executor reports success while observed state disagrees;
11. verifier is executor / verifier is independent;
12. verifier authorized / unauthorized;
13. verification method valid / unavailable / malformed;
14. authorization policy current / stale / revoked;
15. executor restart and authorization replay.

Key invariants:

- changing decision authority must not rewrite the Decision's semantic payload;
- ratification may make a Decision effective but must not strengthen its semantic conclusion;
- execution authorization may narrow/refuse an effective Decision but must not change what was decided;
- wrong actor/action/target substitution fails closed;
- successful execution must not manufacture missing authorization;
- valid authorization must not manufacture successful execution;
- executor self-report must not override contradictory observed post-state;
- verification authority must not rewrite Decision or authorization semantics;
- outcome verification must be able to report failure/partial/unknown even when authorization was valid;
- an unauthorized but factually correct verifier report remains distinguishable from an authoritative verification record.

Primary discriminating question:

> Can the four authority relations change independently in real workflow states without requiring semantic mutation of the Decision or outcome record?

If yes, the case for a common authority protocol strengthens.

### Negative control — collapsed authority object

Implement a deliberately entangled control that puts decision authority, ratification, execution permission, and outcome success into one mutable object.

Attempt the same context changes while holding the Decision semantics fixed.

Expected failure modes to look for:

- changing executor authority requires rewriting the Decision;
- approval is accidentally treated as evidence that execution occurred;
- successful execution launders missing approval;
- verifier result rewrites authorization state;
- stale target state cannot invalidate only execution authority;
- cross-use-case action substitution becomes possible through generic `approved` / `eligible` state.

The collapsed control is useful only if it is allowed to fail visibly.

### Experiment E-RC1 — Representation comparison

Only if E-RC0 supports separability, compare the smallest practical representations.

Candidate implementations:

1. centralized online policy query;
2. central policy/delegation control plane + local evaluator/enforcement point;
3. policy query that mints a short-lived scoped capability/grant;
4. persisted authorization record;
5. approval receipt + transient authorization + durable execution/outcome receipts.

Hold domain Decision semantics fixed.

Evaluate:

- replay resistance;
- revocation;
- actor substitution;
- action substitution;
- target mutation;
- stale Decision handling;
- approval addition/removal;
- delegation-profile changes;
- service outage behavior;
- executor restart;
- policy bundle staleness;
- independent verification;
- audit reconstruction;
- implementation complexity;
- cross-system portability;
- ability to fail closed without inventing adverse semantic conclusions.

### Experiment E-RC2 — Cross-use-case conformance

Only after a representation survives RC1, repeat across materially different operation classes, for example:

- source-audit verified/stable state mutation;
- citation permission;
- real-task dispatch;
- protected repository mutation;
- research/experiment promotion;
- durable-memory admission;
- external tool/API side effect.

The aim is not to prove universal applicability. It is to identify the smallest common authority envelope that survives materially different consumers without semantic reinterpretation.

## Falsifiers / reasons to collapse layers

Do not preserve distinctions merely because they look governance-friendly.

Reconsider this decomposition if controlled experiments show that:

- decision mandate and ratification cannot vary independently in any real target workflow;
- execution authority is already fully and safely determined by Decision semantics in tested domains;
- outcome verification adds no independent information beyond deterministic executor receipts;
- a separate verification authority creates more ambiguity than it resolves;
- a central authority layer must duplicate domain Decision semantics to function;
- exact identity binding cannot resolve authority ambiguity;
- a capability/enforcement architecture makes a separate authorization result unnecessary;
- the common envelope becomes so generic that every consumer must reinterpret it differently.

Collapse only the distinctions that fail to earn their keep in discriminating tests.

## Evidence hierarchy for this research

Prefer, in order:

1. frozen real producer/consumer artifacts;
2. independently observable side effects / post-state;
3. mutation and substitution tests;
4. independent consumers/verifiers;
5. cross-repository conformance;
6. deterministic replay from exact policy/artifact identities;
7. synthetic examples used only where real states are unreachable or unsafe.

Do not treat a green workflow as proof that the ontology is correct.

## Explicit non-claims

This brainstorm does not establish:

- Contract E 1.0.0;
- that Contract E should exist as a durable serialized contract;
- a canonical authorization vocabulary;
- a canonical authority-control-plane implementation;
- production actor roles;
- production delegation profiles;
- production ratification requirements;
- automatic MainFrame mutation;
- that every decision requires human sign-off;
- that every execution requires independent outcome verification;
- that Decision Engine should own authority policy;
- that CAL or Contract C semantics should change;
- that successful outcome verifies the correctness of the original Decision;
- that a signed/authorized Decision proves the corresponding operation occurred.

## Current working hypothesis

The strongest hypothesis worth testing is:

> Decision authority, decision ratification, execution authority, execution occurrence, and outcome verification are distinct relations. A common authority-control protocol may govern the authority-bearing transitions while domain systems retain semantic ownership and local executors retain enforcement responsibility.

A useful system should make the following reconstruction possible without inference from generic success flags:

```text
Why was this Decision authoritative?
Who, if anyone, ratified it?
Who was permitted to execute it?
What exact operation was attempted?
What actually happened to the target?
Who or what established that observed outcome?
Which exact policies, approvals, artifacts, and hashes were in force?
```

The next step is not schema design. It is a smaller experiment that tries to make these distinctions fail.
