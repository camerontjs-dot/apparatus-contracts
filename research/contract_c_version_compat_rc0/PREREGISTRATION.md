# Contract C version compatibility RC0

**Classification:** Draft Research Infrastructure / compatibility experiment. No canonical version assignment, no released Contract C mutation, no merge/release/tag/promotion, no Decision Engine production change, no Contract E or Authorization.

## Exact base

- predecessor Apparatus PR #85 receipt/head: `ad1ffbd7906a7cf34cce5afa906a5797cd4a14ff`
- underlying released Apparatus base: `c3563cff66d2c85dcbf575c693056e2d8e4563d4`
- released Contract C release commit: `5fe55f9ed5d0ee9f026ca1b077e9d70ce0487ea1`
- released Contract C schema blob: `b0369de9b5c156322d6787261bbc7658a3b33781`
- released Contract C validator blob: `9c75ccfbf2223578a8d1a7bf0c39673b394fbea4`
- frozen successor research sentinel: `research-non-deciding-rc0`
- frozen successor handoff SHA-256: `sha256:325962ebcdbf6af836bb6193a451524ccd40b4d10f2394ff9f703fbfce1ec1e3`
- frozen successor handoff result-set: `result-set:4483272c4f6fbd9cb2362be7e3174bbd00aff3cf761d6c374897f3478818c9f0`
- Decision Engine cross-repo consumer decisive run: `34530232915`
- Decision Engine Draft Research PR: #67

## Question

What compatibility architecture is justified if the `non_deciding` contribution representation were ever promoted as a Contract C successor?

Do not assign a SemVer number first. Determine what legitimate existing 1.0 consumers observe and whether any downgrade preserves semantics.

## Competing architectures

### A. Translation / downgrade compatibility

A successor producer or adapter rewrites a successor artifact into released 1.0 syntax by one of:

- `non_deciding -> support`;
- `non_deciding -> counterevidence`;
- dropping non-deciding contributions and repairing the basis/residual structure.

This architecture is falsified if a translated artifact can pass released 1.0 validation while changing or erasing the successor's neutral evidence meaning, provenance, or causal multiplicity.

### B. Parallel exact-version authority

A consumer supports multiple contract profiles without translating semantic state. An independently supplied expected contract profile selects a pinned validator/authority. The artifact's own `contract_c_version` must match that external profile before semantic validation.

This architecture is supported only if:

- exact released 1.0 bytes validate unchanged under the released profile;
- exact successor bytes validate unchanged under the successor research profile;
- cross-profile substitution fails before semantic consumption;
- no successor evidence is relabelled or dropped;
- whole-object identity remains profile-specific.

## Preregistered observations

O1. Released 1.0 strict validator accepts the canonical released 1.0 fixture unchanged.

O2. Released 1.0 strict validator rejects the exact successor handoff unchanged.

O3. Successor shadow validator accepts the exact successor handoff unchanged.

O4. Parallel exact-version dispatch accepts each artifact only under its externally expected profile and rejects profile/artifact version mismatch.

## Downgrade falsifiers

D1. Map every `non_deciding` contribution to `support`, change wire version to `1.0.0`, recompute immutable internal identity, and test released 1.0 validation.

D2. Repeat with `counterevidence`.

D3. Remove all non-deciding contributions, clear their basis, use an otherwise legal non-deciding causal form, change wire version to `1.0.0`, recompute identity, and test released validation.

For any downgrade that validates, compare exact evidence references, contribution channels, basis membership and causal multiplicity against the frozen successor source. A validator-valid but semantically changed downgrade is evidence **against** translation compatibility, not evidence for it.

D4. A safe downgrade function must refuse a successor object containing `non_deciding`; it must not guess a polarized channel or silently erase the evidence.

## Authority-selection falsifiers

A1. Successor artifact presented under the externally expected released-1.0 profile must fail even though its self-declared version requests successor semantics.

A2. Released 1.0 artifact presented under the externally expected successor profile must fail rather than be silently upgraded/relabelled.

A3. Caller/artifact metadata must not be able to change the pinned validator identity within a profile.

A4. Rewriting an artifact to another version/profile necessarily changes canonical bytes/result identity/whole-object SHA and must fail against the original immutable digest.

## Version-class decision rule

Record only observed compatibility facts first.

If a legitimate existing strict 1.0 consumer cannot consume the successor artifact and no lossless downgrade exists, record `BREAKING_FOR_EXISTING_STRICT_1_0_CONSUMERS`.

Under the project's post-1.0 release governance, that observation is a **MAJOR-version signal if promotion is later authorized**, not an official version assignment in this research PR.

If an actually lossless path allows old legitimate consumers to preserve the successor meaning, the breaking-change hypothesis is falsified.

## Allowed dispositions

- `SUPPORTED_PARALLEL_VERSIONING_AND_BREAKING_CHANGE_SIGNAL`
- `SUPPORTED_LOSSLESS_BACKWARD_COMPATIBILITY`
- `INCONCLUSIVE_VERSION_COMPATIBILITY_APPARATUS_INVALID`

No outcome by itself authorizes a Contract C release.