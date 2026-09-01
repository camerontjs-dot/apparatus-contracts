# Contract A Minimality RC2 Research Lane

Status: **Research / Draft**

This lane tests the smallest mechanically defensible Contract A authority surface at the upstream -> Evidence Bundler boundary.

It is not a production promotion. Legacy Contract A remains canonical until a separate promotion decision. No canonical Contract A version is assigned by preference in this lane. Contract E is not implemented here and is not treated as a prerequisite. A genuinely fresh independent reproduction is required after any candidate freeze.

## Live starting authority

Observed before branch creation on 2026-09-01:

- `camerontjs-dot/apparatus-contracts` main: `6a45ab2de09370f3048ffb083e25b487f81117e4`
- `camerontjs-dot/evidence-bundler` main: `6011789957f3294f97bff260069cfb5bb1c5772f`
- `camerontjs-dot/claim-audit-lab` main: `53f0885b111676794d1bd20e10b91aa58b07e9d4`
- `camerontjs-dot/research-scaffold-harness` main: `548bfa81f65290eda15af658f647497679b840ef`

Contract B 1.2.0 release evidence additionally pins its promotion path at Apparatus `c314e53bd91c0736aa4370a364673b069aceb43e`, Evidence Bundler `c8189c31adbab11729c31430c2070126224a2d42`, and CAL `33a928db97316a3652d57df9cafb8ca240305233`.

## Prior durable evidence used, not rerun unchanged

- Evidence Bundler PR #43: decomposition is retrieval-consequential, but retrieval behavior alone does not locate semantic ownership.
- Evidence Bundler PR #44: query lineage is insufficient for child-sensitive downstream semantics when retrieval is held fixed.
- Evidence Bundler PR #45: bounded ownership is upstream Contract A for proposition/decomposition identity and lineage, Evidence Bundler for retrieval/query/evidence construction, CAL for semantic audit and governed composition.
- Apparatus PR #12 remains the umbrella research/decision record. This lane does not reuse its implementation branch.

## Primary gate

A 20-family field ablation must classify every candidate family as one of:

- `CORE_CANONICAL`
- `OPTIONAL_CANONICAL`
- `PRODUCER_SPECIFIC_ATTACHMENT`
- `LEGACY_ONLY`
- `FORBIDDEN_AUTHORITY`
- `REMOVE`

A field is retained only when its absence produces a legitimate producer/consumer failure, identity/provenance loss, missing-state collapse, or downstream semantic ambiguity that Contract A itself must prevent.

## Required conformance path

The candidate must be exercised through a pinned real path:

`research-scaffold-harness producer bytes -> candidate Contract A -> real Evidence Bundler retrieval/intake machinery -> canonical Contract B 1.2.0 validation -> real CAL explicit proposition intake`

Required cases include undecomposed, declared `all_of`, hostile upstream semantic-looking labels, material missing state, and identity substitution.

A mechanical adapter is allowed only if it is lossless and provenance-preserving. It may not invent propositions, composition, semantic labels, or authority.

## Freeze boundary

If and only if the normal-context evidence supports a precise candidate, candidate authority bytes, reference implementation, and evaluator/conformance authority will be frozen separately with an immutable receipt. A sanitized fresh-reproduction aperture and launch packet may then be prepared, but the independent implementation must not run in this context.

Strongest allowed normal-context disposition: `SUPPORTED FOR FRESH INDEPENDENT REPRODUCTION`.
