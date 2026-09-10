# Contract C attribution sidecar RC1 — terminal research record

**Classification:** Draft Research Infrastructure / alternative representation evidence. This record does not amend Contract C 1.0, select a canonical architecture, assign a version, authorize a companion-receipt standard, merge, release, tag, promote, or authorize production use.

## Exact lineage

- protected Apparatus base: `c3563cff66d2c85dcbf575c693056e2d8e4563d4`
- exact base branch: `research/contract-c-attribution-sidecar-rc1-base-20260910`
- released Contract C authority: `5fe55f9ed5d0ee9f026ca1b077e9d70ce0487ea1`
- released Contract C validator blob held fixed: `9c75ccfbf2223578a8d1a7bf0c39673b394fbea4`
- released Contract C schema blob held fixed: `b0369de9b5c156322d6787261bbc7658a3b33781`
- CAL PR #100 multiplicity head: `aa5f0f1313e65e6d31493095214c76d743ca6d89`
- CAL multiplicity run: `34506201889`
- CAL multiplicity artifact: `10163899726`
- CAL multiplicity digest: `sha256:23ba4cb13870f0b2c5f213d3279faede9d17f19e638dea49444249328a0efb19`

The CAL multiplicity result is treated as frozen external semantic evidence. This Apparatus experiment does not rerun CAL semantics.

## Question

Can a separately immutable companion receipt, while leaving Contract C 1.0 bytes untouched, preserve the exact unresolved causal evidence references and the evidence-level causal multiplicity that the original PR #100 sidecar failed to preserve?

## Preserved apparatus failure

Initial workflow run `34532296461` at head `8d2f68a3fad53dc4ef44b8d61fb16675827508d3` failed before semantic execution.

The exact-base/research-surface gate passed. The next guard attempted to prove that the independent consumer imported no producer-side sidecar code, but its broad text regex matched the consumer's own docstring sentence stating that it **does not import** that implementation.

No sidecar semantic evaluator executed. This run is therefore `INCONCLUSIVE_SIDECAR_APPARATUS_INVALID`, not evidence against the sidecar candidate.

The correction changed only the workflow guard from a broad prose grep to a Python import-statement grep plus a separate prohibited-semantic-code-token grep. No producer, consumer, carrier, hostile-test, or interpretation semantics changed.

Guard-fix head: `132a11587af3cfc7d0e05122390babe630cf26f4`.

## Decisive execution

Corrected run `34532374495`: PASS.

- exact tested head: `132a11587af3cfc7d0e05122390babe630cf26f4`
- disposition: `SUPPORTED_RICHER_SIDECAR_TECHNICALLY_SUFFICIENT`
- artifact: `10174010034`
- artifact digest: `sha256:94b4e6f3e5497b3c577c66bf869854de8b30a162633c1540a6c8c006b5cd4567`
- released Contract C regression: `17 passed, 8 skipped`

## Exact frozen outputs

Released-1.0 carrier:

- Contract C SHA-256: `sha256:f17903c8d829b3ca29c59a71f91c49635945c9ad54ebe1a10fdb055b2275de09`
- terminal basis: one opaque `state:` member
- retained Contract C contributions: none
- Contract C alone reconstructs exact unresolved causes: **false**

Richer companion receipt:

- schema sentinel: `cal-producer-attribution-sidecar-rc1-v1`
- sidecar SHA-256: `sha256:3819b662f844b9a0cd5516001101a7bf4d93342d8a58426921600227bafd70b1`
- receipt identity: `producer-attribution:013530def9a0a5407ac65af312baac8d77d23bf3e9d3a9836803cc848712f994`
- recovered causal passages: `U1`, `U2`
- role: `causal_non_deciding`
- evidence-level causal form: `independent_sufficient_alternatives`

The independent consumer performed no CAL semantic re-audit and imported no producer-side sidecar implementation.

## Passed positive and hostile controls

The decisive cohort established all preregistered checks, including:

- exact released Contract C 1.0 validation and whole-object binding;
- Contract C alone lacks the missing unresolved evidence mapping;
- exact sidecar binding to Contract C version, result-set identity and whole-object SHA;
- exact proposition/text-hash and `state:` basis binding;
- exact Contract-B top-level and passage/source/hash reference binding;
- independent reconstruction of both `U1` and `U2`;
- independent reconstruction of `independent_sufficient_alternatives` rather than a bag of refs;
- neutral `causal_non_deciding` role preserved without support/counterevidence vocabulary;
- reverse producer input order canonicalized to identical sidecar bytes;
- released Contract C bytes remained bit-for-bit unchanged;
- wrong Contract C hash/result/version rejected;
- wrong proposition/hash/state rejected;
- wrong or missing evidence ref rejected;
- duplicate member/ref rejected;
- unknown role or causal form rejected;
- invalid causal cardinality rejected;
- stale member identity and stale receipt identity rejected;
- non-canonical member ordering rejected at the wire boundary;
- an externally stale sidecar whole-object digest rejected otherwise internally coherent tampering.

## Bounded inference

For the exact demonstrated `U1/U2` counterexample, a Contract C wire revision is **not technically necessary merely to preserve the missing information**. A richer separately immutable sidecar can preserve exact unresolved provenance and evidence-level multiplicity while exact Contract C 1.0 remains unchanged.

This falsifies only the claim that the in-band `non_deciding` successor is technically forced by information transport.

It does **not** establish that the sidecar is the architecturally correct boundary.

## Remaining architectural conflict

Contract C 1.0 states that Contract C is the immutable, decision-agnostic representation of CAL-attributable epistemic/result state required by legitimate downstream consumers. In this sidecar architecture, Contract C alone remains information-insufficient for the demonstrated unresolved causal provenance and multiplicity; a second artifact is required.

The next discriminating question is therefore normative but testable against the existing Contract C authority record:

> Did the Contract C promotion decision require these attribution/multiplicity invariants to be reconstructable from Contract C itself, or did it permit an independently bound companion artifact as part of the legitimate handoff boundary?

If the authoritative decision requires Contract C itself to retain that state, this sidecar is architecturally falsified despite technical sufficiency. If the authority permits a composed immutable handoff package, the sidecar remains a live candidate and the MAJOR in-band revision is not yet justified.

## Not established

- architectural preference between in-band neutral contributions and richer sidecar;
- canonical sidecar schema or release;
- Contract C successor version;
- fresh independent reproduction;
- arbitrary semantic-family sufficiency;
- root / `all_of` composition;
- Contract E / operational authorization;
- promotion or release readiness.
