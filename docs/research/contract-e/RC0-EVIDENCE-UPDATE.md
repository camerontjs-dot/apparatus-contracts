# Contract E Brainstorm — Authority Control Plane RC0 Evidence Update

Status: research evidence correspondence / non-authoritative

## Result

Decision Engine Authority Control Plane Cross-Stage RC0 reached:

**SUPPORTED FOR PROMOTION**

Primary evidence:

- Decision Engine PR #20 — `Research: cross-stage authority control plane RC0`
- frozen result commit: `ae44fc001d1157b0ad5af4312833f1d39a41356c`
- result artifact: `research/authority-control-plane-cross-stage-rc0/RESULTS.md`

## Narrow supported claim

For the tested authority profiles and stage classes, one standing authority model plus a common jurisdiction evaluator was sufficient to govern:

- research assessment issuance;
- bounded Decision-making;
- repository execution request classes;
- outcome verification;

without reading domain semantic payloads.

Changing the standing delegation posture reduced higher-authority escalation while the frozen protected cases remained unpermitted.

## Key evidence

Frozen workflow posture comparison:

| Profile | Automatic | Higher-authority escalations | Protected false permits |
|---|---:|---:|---:|
| manual | 1 | 5 | 0 |
| supervised | 4 | 2 | 0 |
| delegated-research | 5 | 1 | 0 |

Hardening:

- 1,680 generated authority-relevant request descriptors;
- 3 opaque semantic payload variants per descriptor;
- 5,040 semantic-invariance comparisons;
- 5,040 alternate-implementation comparisons;
- 0 alternate-evaluator disagreements;
- 0 protected false permits;
- three preserved Decision Engine RC1 Decision specimens produced identical jurisdiction when inserted only as opaque payloads;
- target evaluator did not read the semantic payload;
- semantics-aware negative control falsely permitted a protected runtime request and therefore failed in the intended direction;
- fragmented stage-local control exhibited stale verification state when a posture update was omitted;
- ordinary Decision Engine CI remained green.

## Conceptual update

The evidence strengthens this working model:

- **Authority** is standing/delegated governance state configured around the pipeline;
- **Jurisdiction** asks whether that authority covers a particular actor/operation/target/context;
- **Authorization** is the runtime application of that authority;
- human approval can be a higher-authority exception path rather than a mandatory pipeline stage;
- enforcement remains local to the component holding the capability;
- execution remains distinct from observed outcome and authoritative outcome verification.

This supports studying an Authority Control Plane as cross-cutting governance machinery rather than treating Authorization as a mandatory sequential contract stage.

## Strongest remaining falsifier

The primary unresolved risk is **adapter truthfulness**.

RC0 starts after a stage has constructed truthful typed authority descriptors. It does not prove that real CAL Pipeline stages can map semantic outputs into actor/operation/target/context descriptors without reinterpretation or authority laundering.

A defective adapter could mislabel a protected runtime operation as a permitted documentation operation. The next experiment therefore needs independently checkable real-producer adapters and mutation tests that relabel effects, operations, or targets.

## Current Contract E posture

Do **not** promote a Contract E schema from this result.

The result makes a durable Authorization contract less necessary, not more established. The stronger current hypothesis is:

```text
semantic pipeline artifacts
        +
standing Authority / Delegation policy
        ↓
local jurisdiction checks
        ↓
local enforcement
        ↓
execution
        ↓
observation / verification
```

Whether any authority event requires a durable contract remains an open representation question.

## Successor

Run a real-consumer cross-repository authority RC1 with the common evaluator frozen and real/frozen producer artifacts supplying independently verified operation/target bindings.

No production Authority Control Plane, automatic mutation, or Contract E promotion is authorized by this update.
