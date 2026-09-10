# Contract C version compatibility RC0 — terminal research record

**Classification:** Draft Research Infrastructure / compatibility pressure test. This record is evidence only. It does not amend Contract C, assign an official successor version, authorize a migration adapter, merge, release, tag, promote, or authorize production use.

## Exact lineage

- predecessor / qualified non-deciding shadow receipt: `ad1ffbd7906a7cf34cce5afa906a5797cd4a14ff`
- exact compatibility base branch: `research/contract-c-version-compat-rc0-base-20260910`
- tested implementation head: `a8ee05e758a7be97c567cdc95ff70db75814946d`
- released Contract C validator blob held fixed: `9c75ccfbf2223578a8d1a7bf0c39673b394fbea4`
- released Contract C 1.0 schema blob held fixed: `b0369de9b5c156322d6787261bbc7658a3b33781`
- predecessor shadow research directory held byte-stable during the test

## Question

Can the qualified `non_deciding` representation be introduced through a safe compatibility/migration strategy without allowing semantic laundering into Contract C 1.0, and what version-class signal follows from observed consumer behavior under project governance?

## Decisive execution

- workflow run: `34530811489`
- conclusion: `success`
- research disposition: `SUPPORTED_PARALLEL_VERSIONING_AND_BREAKING_CHANGE_SIGNAL`
- artifact: `10173394540`
- artifact digest: `sha256:0080176223202f7c55bdedb602692429946518d04fa8c7fb52d6fbd62bc5f6eb`
- tested head: `a8ee05e758a7be97c567cdc95ff70db75814946d`

Released Contract C regression remained green: `17 passed, 8 skipped`.

## Observed compatibility

The preregistered matrix established:

- released 1.0 validator accepts released 1.0;
- released 1.0 validator rejects the qualified successor/shadow unchanged;
- successor/shadow validator accepts the successor/shadow;
- an existing strict 1.0 consumer therefore breaks on the successor bytes rather than silently accepting widened vocabulary;
- the supported migration pattern in this cohort is `parallel_exact_version_authority_no_downgrade`.

Validator selection in the tested architecture is controlled by an independently established expected contract profile. The artifact's own version metadata must agree with that profile; it does not select its own authority.

## Downgrade attacks

Three attempted successor -> 1.0 translations produced structurally validator-valid Contract C 1.0 objects while changing the qualified neutral-evidence semantics:

1. `map_non_deciding_to_support`
2. `map_non_deciding_to_counterevidence`
3. `drop_non_deciding_and_repair_basis`

These are **validator-valid semantic-laundering downgrades**. Acceptance by the 1.0 validator does not make the translation faithful: the adapter has already altered or erased the original neutral causal provenance before validation.

Therefore a semantic downgrade adapter is not authorized by this experiment.

## Version-class evidence

Under the project release/version governance, version class follows demonstrated compatibility rather than edit size. In this cohort, existing strict 1.0 consumers cannot consume the successor unchanged. The experimental governance signal **if a successor were later promoted** is therefore `MAJOR`.

No official Contract C successor version is assigned by this record. In particular, this record does not itself establish or authorize a `2.0.0` release.

## Bounded inference

The qualified `non_deciding` vocabulary can coexist safely with released 1.0 only when version authorities remain parallel and exact, with no semantic downgrade of successor artifacts into 1.0.

This supports a breaking-change signal for the in-band Contract C successor candidate. It does **not** yet establish that an in-band Contract C successor is the smallest architecture that satisfies the CAL requirement.

## Remaining discriminating alternative

The strongest remaining alternative explanation is that neutral unresolved provenance and causal multiplicity do not need to widen Contract C at all. A separately immutable, Contract-C-bound companion receipt might preserve the additional CAL-attributable state while Contract C 1.0 remains unchanged.

The next bounded experiment should therefore compare the in-band successor against the smallest richer sidecar capable of preserving:

- exact Contract C 1.0 identity;
- exact Contract-B evidence references;
- all neutral unresolved causal contributors;
- causal basis membership and multiplicity, including `independent_sufficient_alternatives`;
- proposition/result binding;
- no support/counterevidence reinterpretation;
- fail-closed behavior on stale, substituted, deleted, duplicated, or reordered authority-relevant state where applicable.

A sidecar that cannot preserve those properties is falsified. A sidecar that can preserve them without changing Contract C 1.0 would falsify the claim that a major Contract C wire revision is presently necessary.

## Not established

- canonical Contract C successor schema or version;
- production migration strategy;
- fresh independent reproduction;
- arbitrary semantic-family sufficiency;
- root / `all_of` CAL composition;
- Contract E / operational authorization;
- promotion or release readiness.
