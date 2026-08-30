# Contract E / Authority Control Plane — Thought Process Record

Status: research narrative / non-authoritative

Purpose: preserve the conceptual evolution that led from a simple Decision -> Authorization -> Execution model to the current cross-cutting authority/jurisdiction hypothesis. This is a research record, not architecture authority and not a Contract E schema proposal.

## 1. Starting seam

Decision Engine RC0/RC1 established a bounded result:

- Decision and operational authorization can vary independently;
- authorization can narrow or refuse a Decision without rewriting Decision semantics;
- generic `eligible` / `clear` is too weak as operational authority;
- requested operations need typed/equivalent binding to Decision effects;
- execution remains downstream.

That initially suggested a sequential model:

```text
Evidence -> Decision -> Authorization -> Execution
```

## 2. Regulated-work analogy

A stronger analogy emerged from regulated operations:

- a technical or policy conclusion can be reached;
- an authorized person or system may then sign off / approve;
- the approved action still has not happened merely because it was approved;
- a later record establishes what was actually done and what resulting state was observed.

This reinforced the Decision / Authorization seam but also exposed another collapse: authorization is not execution, and execution is not the same thing as a successful outcome report.

## 3. Execution/process/outcome separation

The model was refined to distinguish:

```text
execution authorization
        ↓
execution attempt
        ↓
execution process
        ↓
resulting reality
        ↓
observation
        ↓
outcome verification
        ↓
outcome record
```

Materially distinct states include:

- authorized execution that fails;
- unauthorized execution that nevertheless succeeds;
- executor self-report of success while observed post-state disagrees;
- partial application;
- execution occurrence with outcome not yet verified.

Therefore `execution = success` is too lossy for the intended governance model.

## 4. Authorization split into multiple authority relations

A second conflation was identified: `Authorization` had been carrying at least two different questions.

### Decision authority

Who or what has jurisdiction to make this class of Decision over this class of target under this policy?

A substantively correct conclusion from an actor outside its mandate may be a recommendation without being an authoritative Decision.

### Decision ratification / adoption authority

Where required, who may make a Decision effective by approving/adopting it?

Ratification may be absent for fully delegated decision classes. It must not strengthen or rewrite the semantic Decision.

### Execution authority

Who or what may perform the operation implied/requested by an effective Decision?

This can differ from the decision-maker and ratifier.

### Verification authority

Who or what is authoritative for establishing what actually happened after execution?

The executor's statement may be evidence but need not be sufficient verification.

This produced a richer candidate chain:

```text
Authority to Decide
        ↓
Decision Process
        ↓
Decision
        ↓
Ratification / Adoption, where required
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

The working rule is not that every workflow must instantiate every box. The research question is which distinctions are independently load-bearing.

## 5. Shift from pipeline-stage authorization to cross-cutting authority

A further problem appeared when considering bounded autonomy and minimization of human-in-the-loop.

If authorization is a mandatory pipeline stage interpreted as human approval, then every run pauses at the same location regardless of risk or delegated scope. That conflicts with the intended autonomy model.

The stronger mental model became:

> Authority is standing governance state configured outside the semantic pipeline. Authorization is a runtime determination that a particular proposed act falls within that authority.

That suggests a topology closer to:

```text
                  standing Authority / Delegation Policy
                              │
                ┌─────────────┼─────────────┐
                ▼             ▼             ▼
           assessment      decision      execution
                │             │             │
          jurisdiction?  jurisdiction?  jurisdiction?
                │             │             │
                └─────────────┼─────────────┘
                              ▼
                         verification
                         jurisdiction?
```

Human approval becomes an exception or higher-authority path rather than a mandatory stage.

## 6. Settings / lever intuition

The user-facing control may resemble platform permission settings or an autonomy posture rather than a contract artifact.

Examples:

```text
research assessment            delegated
documentation mutation          delegated
durable memory admission        supervised
runtime mutation                approval required
production promotion            retained by operator
external side effects           approval required
```

A simple UI may present profiles such as manual / supervised / delegated, but the underlying authority should remain explicit. A single numeric trust score is likely too lossy because it cannot express which operations, targets, domains, limits, expiry, or side effects are covered.

The UI can be dial-like while compiling to a structured delegation policy.

## 7. Jurisdiction as the missing runtime concept

The authority question became more precise:

> Does the standing authority invoked for this act have jurisdiction over this actor, operation, target, context, and scope now?

Candidate dimensions:

- authority identity and validity;
- actor/principal;
- operation/effect class;
- target class and exact target;
- policy/domain scope;
- currentness / expiry / revocation;
- batch/rate/budget/side-effect bounds;
- ratification/approval prerequisites;
- segregation-of-duties constraints;
- whether this stage recognizes the supplied authority as sufficient.

Possible runtime outcomes are conceptually closer to:

```text
IN_JURISDICTION
OUT_OF_JURISDICTION
REQUIRES_HIGHER_AUTHORITY
INDETERMINATE
```

Vocabulary is not frozen.

## 8. Authority versus authorization

Current terminology hypothesis:

- **Authority**: standing/delegated governance state.
- **Jurisdiction**: whether that authority covers the matter at hand.
- **Authorization**: runtime determination that a particular proposed act is permitted under applicable authority.
- **Approval / ratification**: an act by an authority that changes the authorization context for a bounded object/action.
- **Enforcement**: refusal to invoke a capability unless required authority is established.
- **Execution**: the process/attempt that causes or attempts the side effect.
- **Observation**: evidence about resulting reality.
- **Outcome verification**: authoritative assessment of the observed post-state.

This terminology is still experimental, but it removes several earlier conflations.

## 9. Centralization hypothesis

The centralizable component may not be an Authorization apparatus and may not sit after Decision Engine.

The stronger candidate is a logically shared **Authority Control Plane** responsible for authority mechanics such as:

- principals / actor identities;
- delegation;
- authority scopes;
- policy identity/version;
- operation/effect registry;
- target scopes;
- approval/ratification requirements;
- validity/expiry/revocation;
- segregation of duties;
- bounded autonomy constraints;
- policy distribution;
- authority/audit lineage.

Domain semantics remain local:

- Evidence Bundler owns retrieval/evidence construction semantics;
- CAL owns epistemic assessment semantics;
- Decision Engine/domain policies own Decision semantics;
- local executors own execution implementation;
- outcome observers/verifiers own bounded observation/verification methods.

The common authority layer should not need to understand entailment scores, CAL evidence-state semantics, or domain policy conclusions to decide jurisdiction.

## 10. Strongest current research question

> Can one standing authority model govern heterogeneous pipeline stages through jurisdiction checks while remaining ignorant of their domain semantics and allowing safe autonomy without constant human approval?

This decomposes into four tests:

1. **Cross-stage reuse:** one frozen authority profile governs assessment, decision, execution, and verification.
2. **Semantic ignorance:** the authority evaluator can operate on typed actor/operation/target/context descriptors without reading domain semantic payloads.
3. **Independent variation:** changing delegation/jurisdiction changes authority outcomes without changing Decision or epistemic semantics.
4. **Bounded autonomy:** more permissive profiles reduce human escalations without increasing unauthorized permits.

## 11. Key falsifiers

The cross-cutting control-plane hypothesis should be weakened or falsified if:

- every stage requires materially different authority semantics with no stable common core;
- the authority evaluator must interpret CAL/Decision semantic internals to function;
- changing delegation requires rewriting semantic artifacts;
- unknown operation/target classes inherit authority through vague similarity;
- delegated actors can expand or redelegate authority they do not possess;
- centralized policy introduces hidden authority that local enforcement cannot independently verify;
- the common interface becomes so generic that each consumer reinterprets it differently;
- human-intervention reductions are achieved by false permits rather than legitimate delegation;
- outcome verification contributes no information independent of executor receipts in the tested domain.

## 12. Experiment direction

The next executable experiment should freeze one authority profile and several heterogeneous stage requests before examples are expanded.

The authority evaluator should receive only normalized authority-relevant descriptors, not domain semantic payloads.

At minimum test:

- actor substitution;
- operation substitution;
- target substitution;
- scope/batch widening;
- expiry/revocation;
- unknown operation;
- same actor authorized at one stage but not another;
- delegation non-amplification;
- policy-profile changes without semantic artifact mutation;
- executor self-report versus independently observed post-state;
- manual / supervised / delegated profiles measured for escalation count and unauthorized permits;
- deliberately fragmented per-stage authorization as one negative control;
- deliberately semantics-aware central evaluator as another negative control.

The target is not to prove a universal permissions system. It is to determine whether the authority/jurisdiction abstraction earns a real cross-stage architecture role.

## 13. Current non-claims

Nothing in this record establishes:

- Contract E as a durable contract;
- a canonical Authority Control Plane;
- production delegation settings;
- automatic production mutation;
- universal applicability across all future stages;
- that every Decision requires ratification;
- that every outcome requires an independent human verifier;
- that a successful execution proves the Decision was correct;
- that an authority evaluator may reinterpret domain semantics.

The next claim must come from executable evidence, not further architectural intuition.
