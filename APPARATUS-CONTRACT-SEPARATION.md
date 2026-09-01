# Contract / Apparatus Separation Invariant

**Status:** Accepted repository-wide governance  
**Scope:** Every current and future apparatus boundary represented or researched in this repository

## Normative rule

Every apparatus MUST be developed, tested, and reasoned about against its governing contract, not against the incidental output shape of the current upstream apparatus.

The boundary model is always:

```text
upstream apparatus -> governing contract -> downstream apparatus
```

The apparatus and the contract are separate authorities with separate change histories.

## Separation rules

1. **An apparatus owns its implementation and the way it produces a result.** Its current output is evidence about that apparatus implementation.
2. **The contract owns the cross-apparatus interface.** It defines the authority, state, identity, vocabulary, bindings, unknowns, and other semantics that a legitimate consumer may rely on.
3. **A downstream apparatus consumes the contract.** It MUST NOT be designed around undocumented properties of the current producer, reconstruct producer-private state, or treat today's producer output as the complete capability of the contract.
4. **A current output object is a concrete contract instance, not the definition of the contract.**
5. **Unused contract capacity remains contract capacity.** A field or state not populated by today's producer does not become irrelevant merely because the present implementation does not exercise it.
6. **Producer-private behavior does not become downstream authority.** A behavior, field, convention, or inference present in an apparatus but absent from the governing contract cannot silently become a downstream dependency.
7. **Apparatus evolution and contract evolution are separate decisions.** Improving or replacing an apparatus does not itself change its contracts. Changing a contract requires its own evidence and promotion decision.
8. **Failures are assigned to the first violated authority boundary.** A downstream rejection does not automatically imply downstream incompatibility; first determine whether the producer emitted a conforming contract object and whether the contract itself permits the observed state.

## Apparatus-by-apparatus application

### Upstream producer / Research Scaffold Harness -> Contract A

The upstream producer is judged by whether it can produce the authority Contract A requires. Evidence Bundler must be designed against Contract A, not against the current producer's private data structures, helper fields, prompts, or incidental serialization choices.

Contract A modernization must therefore be justified by producer/consumer evidence about the boundary itself, not by convenience inside either implementation.

### Evidence Bundler -> Contract B

Evidence Bundler consumes Contract A and produces Contract B.

Evidence Bundler must not encode CAL-owned semantic judgments merely because current CAL would find them convenient. CAL must not depend on Evidence Bundler implementation details that Contract B does not carry.

A current Contract B artifact is one population of Contract B, not a template that constrains every future valid Contract B producer.

### Claim Audit Lab -> Contract C

CAL consumes Contract B and produces Contract C.

CAL must reason from Contract B authority rather than Evidence Bundler-private state. Downstream consumers must reason from Contract C rather than CAL-private traces, internal classifiers, unpublished rule state, or the particular subset of Contract C fields that current CAL happens to populate.

In particular, today's CAL output MUST NOT be treated as the design target or complete semantic envelope of Contract C. Contract C is the authority surface; current CAL is one producer under test against it.

### Decision Engine -> Contract D

Decision Engine consumes Contract C and produces Contract D.

Decision Engine must be designed against Contract C's canonical semantics, not against today's CAL output patterns. It must not inspect CAL-private state, reconstruct omitted CAL reasoning, or narrow Contract C to the subset exercised by current fixtures.

Likewise, consumers of Decision Engine output must consume Contract D rather than Decision Engine-private state.

### Authorization / authority control plane

Authorization machinery must consume the canonical authority surfaces that govern it. A valid Contract D object does not silently acquire authority semantics that belong to a separately governed Contract E or other authority surface.

Research Contract E candidates do not become downstream assumptions until separately promoted as canonical authority.

### Future apparatuses

Every future boundary inherits the same rule automatically:

```text
producer implementation != contract != consumer implementation
```

A new apparatus should be able to replace an old producer or consumer without forcing unrelated implementations to imitate the old apparatus, provided the governing contract remains satisfied.

## Required test separation

Cross-apparatus testing SHOULD keep three questions distinct:

1. **Producer conformance:** Does the apparatus produce a valid object under the governing output contract?
2. **Contract sufficiency:** Does the contract carry the minimum authority legitimate consumers actually require, including adverse, unknown, failed, and edge states?
3. **Consumer recoverability/conformance:** Can an independent consumer correctly use the contract without knowledge of producer-private implementation details?

A vertical slice may test all three, but a passing or failing slice must not collapse them into one claim.

## Research and promotion consequences

- A successful end-to-end run is evidence about the tested implementations and contract instances. It does not redefine any contract.
- A producer defect should be fixed in the producer when the contract already specifies the correct boundary behavior.
- A consumer defect should be fixed in the consumer when the contract already carries sufficient authority.
- A contract change is justified only when evidence shows that a legitimate producer/consumer boundary cannot be represented correctly by the current contract.
- Research outputs remain evidence records until a separate promotion decision establishes canonical authority.
- Promotion should always be the smallest change justified by the evidence.

## Short form

**Always build each apparatus from the contract boundary, never from the current neighboring apparatus output. Keep producer, contract, and consumer separate.**
