# Minimal Production Slice Convention

**Status:** Proposed repository-wide governance  
**Scope:** CAL Pipeline apparatuses and contract-facing runtime surfaces

## Purpose

Research branches are evidence records. They are not automatically the runtime surface that should be composed into the CAL Pipeline.

Once an apparatus has converged on a bounded, frozen subject, the repository SHOULD expose the smallest production-shaped slice justified by that evidence so the component is easy to pin, invoke, replace, compare, and qualify independently.

The default lifecycle is:

```text
research convergence
-> exact frozen candidate
-> promotion design
-> minimal production slice
-> cross-repository qualification
-> release/promotion only if separately justified
```

This convention does not weaken the contract/apparatus separation invariant. Contracts remain separate authorities with separate change histories.

## Minimal production slice

A minimal production slice is a maintained, production-shaped apparatus surface derived from exact frozen evidence.

It SHOULD:

1. start from the live maintained production base rather than treating a research branch as production by default;
2. identify the exact frozen research subject that authorizes the slice;
3. import or transcribe only behavior already supported by that frozen evidence;
4. expose a simple, stable operator/API surface suitable for pipeline composition and substitution testing;
5. pin every behaviorally relevant semantic/configuration authority needed to reproduce the slice;
6. exclude research harnesses, superseded implementations, exploratory machinery, and unqualified capabilities;
7. preserve known falsifications, limitations, unsupported regions, and fail-closed behavior;
8. define exact production regression and cross-repository conformance gates;
9. stop if the minimum slice would require inventing new semantics or relying on unqualified authority.

Promotion design is therefore a narrowing step, not a license to collect every successful research mechanism into one runtime.

## Existing production surfaces

Where an apparatus already has a maintained, qualified production surface, verify and reuse it. Do not rebuild a new slice merely to make repositories look symmetrical.

A release, mainline convergence, or already-promoted bounded runtime can satisfy this convention when it provides the same properties: exact authority, simple invocation, bounded behavior, and independent qualification.

## Research-qualified but unreachable capability

A research-qualified capability does not automatically belong in the production slice.

It may remain outside when:

- ordinary runtime inputs do not yet produce the authority it requires;
- orchestration is not yet production-reachable;
- the governing output contract cannot represent the resulting state losslessly;
- the downstream consumer is not qualified for that state;
- the capability was qualified only in a bounded research aperture.

Repositories SHOULD preserve two distinct identities when useful:

1. the **minimal production slice** used for ordinary pipeline composition; and
2. an **exact frozen research/full-capability subject** used only for experiments that intentionally exercise capability outside the production slice.

These identities MUST NOT be silently substituted for one another.

## Contract boundary rule

Changing or promoting an apparatus does not itself change its governing contracts.

For every apparatus promotion:

```text
input contract -> apparatus production slice -> output contract
```

must remain three separately justified authorities.

If a frozen apparatus exposes state that the current output contract cannot authoritatively represent, preserve that as a contract-sufficiency falsifier and stop the production route at that boundary. Do not hide the state in producer-private fields, opaque conventions, or a downstream adapter.

Likewise, do not widen a contract solely because a new apparatus implementation makes a wider surface convenient. Contract evolution requires its own producer/consumer evidence and promotion decision.

## Cross-repository qualification

Before a new production slice is treated as a pipeline candidate, qualification SHOULD establish at minimum:

- exact frozen-subject provenance;
- unchanged inherited semantics outside the authorized slice;
- deterministic replay where the apparatus promises determinism;
- producer conformance to its output contract;
- consumer conformance at the next boundary;
- fail-closed hostile/substitution controls appropriate to the apparatus;
- preservation of known negative cases;
- a simple reproducible invocation from a clean checkout or packaged artifact.

A green repository-local CI run alone is not sufficient evidence of a valid cross-apparatus boundary.

## Pipeline substitution experiments

Production slices are the preferred subjects for staged pipeline replacement experiments because they provide stable, bounded identities.

Experiments SHOULD change one production slice or contract authority at a time where possible and preserve the first divergence.

When a research-only/full-capability subject is deliberately substituted instead, the run manifest must identify that subject explicitly and must not describe it as the production slice.

## Contract E / Authorization exception

Contract E and the authority control plane remain research-only until the authority model itself has converged sufficiently to justify:

- a frozen candidate authority model;
- independent consumption/reconstruction;
- adversarial qualification;
- a bounded production-facing responsibility.

Do not create a Contract E production slice merely for pipeline symmetry.

A Contract D result remains non-conferring unless and until separately governed Authorization machinery establishes authority.

## Recommended repository record

A promotion-design PR SHOULD record:

- maintained production base;
- exact frozen research authority;
- minimum file/configuration dependency closure;
- simple proposed invocation surface;
- active behavior included in the slice;
- research-qualified behavior explicitly deferred;
- input/output contract identities;
- compatibility or version consequences;
- qualification gates;
- preserved falsifications and nonclaims;
- stop condition if new semantics are required.

Research evidence remains in its original branches/PRs. The promotion slice should point to that evidence rather than importing the whole research lineage.

## Short form

**Research proves machinery. Promotion design selects the smallest already-proven machinery that should become easy to run. Contracts remain separate. Unqualified capability stays out.**
