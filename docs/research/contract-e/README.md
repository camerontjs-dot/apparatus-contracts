# Contract E Brainstorm — Authority, Ratification, Execution, and Outcome Verification

Status: research brainstorm / non-authoritative

This document is a holding surface for the authority-boundary research question. It does **not** define Contract E, establish that a fifth durable contract is required, assign field names, or authorize production behavior.

The name `Contract E` is provisional shorthand only. Decision Engine research explicitly left open whether authorization should be a persisted contract, a policy query, a scoped capability, an approval record, or a combination of transient authorization plus durable execution receipts. Do not infer persistence from the letter.

## Current evidence update

The initial cross-stage jurisdiction experiment has now completed in Decision Engine PR #20 with terminal disposition:

**SUPPORTED FOR PROMOTION**

The detailed evidence correspondence is preserved in:

- `docs/research/contract-e/THOUGHT-PROCESS.md`
- `docs/research/contract-e/RC0-EVIDENCE-UPDATE.md`
- Decision Engine `research/authority-control-plane-cross-stage-rc0/RESULTS.md` at result commit `ae44fc001d1157b0ad5af4312833f1d39a41356c`

The bounded supported claim is that, for the tested stage classes and profiles, authority can operate as cross-cutting standing governance state with common jurisdiction checks while semantic payloads remain opaque. This does **not** establish a production Authority Control Plane or Contract E schema.

The strongest next falsifier is adapter truthfulness: whether real stages can construct truthful typed actor/operation/target/context descriptors without semantic reinterpretation or authority laundering.

## Working decomposition

The current conceptual model distinguishes:

```text
standing Authority / Delegation Policy
            │
            ├────────────┬────────────┬────────────┐
            ▼            ▼            ▼            ▼
       assessment     decision     execution    verification
            │            │            │            │
       jurisdiction? jurisdiction? jurisdiction? jurisdiction?
```

Human approval is potentially a higher-authority exception path rather than a mandatory pipeline stage.

The downstream state distinctions remain:

```text
Decision
  != authorization

authorization
  != execution

execution
  != executor report

executor report
  != observed outcome

observed outcome
  != authoritative verification unless verification authority is established
```

## Candidate authority relations

### Decision authority / mandate

Who or what has jurisdiction to make this class of Decision over this class of target under this policy?

### Ratification / adoption authority

Where required, who may approve or adopt a Decision so that it becomes effective? This relation may be absent for fully delegated decision classes.

### Execution authority

Who or what may perform the requested operation on the exact target under the applicable Decision and standing authority?

### Verification authority

Who or what may authoritatively establish what actually happened after execution?

These relations should remain separate unless experiments show that a distinction does not earn its keep.

## Working terminology

- **Authority**: standing/delegated governance state.
- **Jurisdiction**: whether that authority covers the matter at hand.
- **Authorization**: runtime determination that a proposed act is permitted under applicable authority.
- **Approval / ratification**: a bounded higher-authority act that changes authorization context.
- **Enforcement**: refusal to invoke a capability unless required authority is established.
- **Execution**: the process/attempt that causes or attempts the side effect.
- **Observation**: evidence about resulting reality.
- **Outcome verification**: authoritative assessment of observed post-state.

Vocabulary remains research-only.

## Centralization hypothesis

The centralizable component may be a logically shared **Authority Control Plane**, not a universal Decision Engine and not necessarily a durable Authorization object.

Potential shared concerns include:

- principals / actor identities;
- delegation and scope;
- operation/effect registry;
- target scope;
- policy identity/version;
- validity, expiry, and revocation;
- ratification/approval requirements;
- segregation of duties;
- bounded autonomy constraints;
- policy distribution and authority lineage.

Domain semantics remain with the systems that own them. The authority layer should not need entailment scores, CAL evidence-state semantics, or Decision reason semantics to determine jurisdiction.

## User-facing control hypothesis

The operator-facing surface may resemble platform permission settings or an autonomy posture rather than a pipeline artifact.

A UI may present something like manual / supervised / delegated, while the underlying representation remains explicit about operation classes, targets, limits, expiry, verification requirements, and retained authority. A single numeric trust/confidence slider is not currently supported.

## Candidate runtime outcomes

Illustrative only:

```text
IN_JURISDICTION
OUT_OF_JURISDICTION
REQUIRES_HIGHER_AUTHORITY
INDETERMINATE
```

Unknown authority state must not silently become permission.

## Current evidence-backed answer

The first synthetic/hardened RC0 answers the research question **yes, with bounds**:

> One standing authority model governed the tested assessment, Decision, execution, and verification request classes through a common jurisdiction evaluator while domain semantic payloads remained opaque. Explicit delegation reduced higher-authority escalations without producing protected false permits in the tested surface.

This is evidence for the architecture hypothesis, not production authorization.

## Strongest residual risk

The adapter-truthfulness problem is now load-bearing.

A common evaluator is useful only if real stage adapters truthfully bind authoritative semantic outputs to typed operation and target descriptors. Mislabeling a runtime mutation as a documentation mutation could bypass correct authority policy without the authority evaluator ever reading semantics.

The successor must therefore test independently verifiable effect/action/target binding on real/frozen producer artifacts.

## Current Contract E posture

Do not freeze Contract E.

The evidence currently points toward authority as cross-cutting control-plane state, with transient jurisdiction evaluations and only the receipts/grants/outcomes that prove necessary made durable. A separate serialized Contract E may turn out to be unnecessary.

## Explicit non-claims

This brainstorm does not establish:

- Contract E 1.0.0;
- a production Authority Control Plane;
- canonical authority vocabulary;
- production delegation profiles;
- automatic MainFrame mutation;
- universal applicability across future stages;
- that every Decision requires ratification;
- that every outcome requires independent human verification;
- that Decision Engine should own production authority policy;
- that successful outcome proves the original Decision was correct.
