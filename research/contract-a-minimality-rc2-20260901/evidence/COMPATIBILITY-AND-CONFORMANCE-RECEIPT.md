# Contract A RC2 Compatibility and Cross-Repository Conformance Receipt

Status: Research evidence record. No production promotion authority.

## Pinned repositories

Normal-context production-path experiment used:

- Apparatus research branch based on production `main` `6a45ab2de09370f3048ffb083e25b487f81117e4`;
- Research Scaffold Harness `548bfa81f65290eda15af658f647497679b840ef`;
- Evidence Bundler `6011789957f3294f97bff260069cfb5bb1c5772f`;
- Claim Audit Lab `53f0885b111676794d1bd20e10b91aa58b07e9d4`.

The successful separated-surface run was GitHub Actions run `33471728968`, job `99742721714`. GitHub tested synthetic PR merge commit `8d1471c54d0cbd005bed21a8aebc28f01884b83c`, which merged branch head `805bf5e2b1766dad23f97dd301e0420b591dd6c8` into the unchanged production base.

Frozen-surface candidates tested by that run:

- candidate tree: `54e5cfc659c574a1520ebc119d66e93d4f71ce34`;
- reference tree: `18b9cec2bc3063ecad17d12d55e49ea4dcb61ff8`;
- evaluator tree: `5d7eb3e3a9a98ba1626118a5e06a018c02fa81ec`.

Evidence artifact:

- artifact ID: `9786765413`;
- artifact name: `contract-a-minimality-rc2-33471728968`;
- artifact ZIP SHA-256: `82f07a926b351916a5f3eddedac54ac96b959fd39d3d4186c26d766662fb7454`.

The untouched Contract B 1.2 production-acceptance workflow also passed on the same branch state in run `33471728973`, job `99742693704`.

## Real bounded path

The experiment exercised:

`pinned real RSH source packet`
→ `Contract A RC2 candidate declaration`
→ `separate legacy compatibility projection where current strict schemas require it`
→ `evidence_bundler.contracts.writer.build_retrieval_bundle`
→ `canonical Contract B 1.2 validation`
→ `real CAL Contract B intake`
→ `CAL ExplicitClaimRequest / source_contract proposition orchestration and aggregation`.

The CAL semantic auditor used for the final explicit-claim aggregation was a deterministic injected stub. The experiment therefore tests identity, provenance, declared composition, and semantic-authority isolation. It does **not** claim to test CAL NLI quality.

## Undecomposed case

Result: PASS.

- Contract A decomposition state: `not_decomposed`.
- CAL operator: `single`.
- CAL atom ID: `clm-supplier-qualification`.
- No child proposition is invented.
- Root proposition remains the source-contract authority.

Failed and unknown decomposition states also remain valid root/single paths, but receive distinct immutable Contract A bindings. They are not collapsed to `not_decomposed`.

## Declared `all_of` case

Result: PASS.

Exact child proposition IDs:

1. `clm-supplier-qualification-a`
2. `clm-supplier-qualification-b`

CAL operator: `all_of`.

CAL explicit request SHA-256:

`sha256:f3190c172859900f4839a094e70a874bdf272b41000078a2b429817be0c36dc7`

The production EB writer emitted Contract B 1.2 claim records with those exact child IDs. Apparatus validation passed and CAL Contract B intake passed. The final deterministic aggregation produced `partially_supported` from one stub-supported and one stub-unsupported child; this value is a structural aggregation control, not a scientific support conclusion.

Production EB retrieval produced non-empty evidence passages for both children. EB used the declared child text as the proposition query while remaining the author of retrieval/evidence construction, not of the child propositions.

## Hostile upstream semantic-isolation result

Each of the following mutations was made independently while the Contract A proposition declaration was held fixed:

- support label;
- claim strength/confidence;
- extraction fidelity;
- counterevidence state;
- downgrade state/reason;
- trust label;
- retrieval query/history;
- retrieval rank;
- upstream-selected passage/source refs;
- source acquisition date/provenance;
- model/prompt/config identity;
- workflow condition;
- timestamps/history.

For **every** mutation:

- EB retrieval evidence signature remained equal to baseline;
- CAL explicit request hash remained equal to baseline;
- CAL explicit semantic aggregation result remained equal to baseline.

This supports treating these observations as non-authoritative for Contract A's proposition/decomposition promise even when current legacy schemas require some of them for compatibility.

## Identity-substitution result

Candidate conformance checks establish that changing each of the following without resealing fails the immutable binding:

- root/parent proposition identity;
- child proposition identity;
- source identity;
- work-object identity.

Source content hash mismatch also fails closed.

## Missing-state result

- `not_decomposed`: valid, root/single path.
- `failed`: valid, root/single path, distinct binding.
- `unknown`: valid, root/single path, distinct binding.
- omitted required proposition identity: fail closed.
- omitted required `sources`: fail closed.
- explicit empty `sources: []`: valid; direct EB probe invents no source.

## Compatibility matrix

| Direction / property | Observed result | Consequence |
|---|---|---|
| legitimate legacy producer → RC2 projection | Supported when required root/work/producer/source bytes can be preserved | Projection must set decomposition state `unknown`; legacy silence cannot be interpreted as `not_decomposed`. |
| RC2 undecomposed object → current strict legacy C-A claim model without compatibility observations | Not supported | Current legacy parser/writer requires additional scaffold observations absent from RC2. |
| RC2 declared `all_of` → faithful legacy Contract A representation | Not supported | Legacy A has no first-class parent/child/operator/sequence representation. |
| current Contract B 1.2 production writer with separate legacy compatibility carrier | Supported | Compatibility observations can satisfy old structural requirements without entering Contract A semantic authority. |
| hostile compatibility-observation mutation → EB evidence identity | Invariant in tested family mutations | Parser/writer dependency is not evidence of Contract A authority ownership. |
| hostile compatibility-observation mutation → CAL source-contract request / aggregation | Invariant in tested family mutations | Legacy observations do not silently establish CAL proposition semantics. |

Observed version implication:

> **major-class if promoted over legacy Contract A 1.0.0; no canonical version assigned by this research lane.**

The reason is representational, not aesthetic: a declared first-class decomposition cannot be faithfully interpreted by an old consumer, and the new minimal object intentionally omits fields required by the old strict surface.

## Candidate handoff identities from the real pilot construction

- declared `all_of`: `sha256:de23b0eb66b3316e85bd9fbc73f4dfe2b6525a1e73783fca8d6e1fbd9bb0189d`;
- undecomposed: `sha256:2816c5e36d70fc4d7a48223500be8ff480fc535b6eac7a74c6f5f11057550148`;
- failed decomposition: `sha256:fe4c0ea6a3955594c74d9ea4d40cd4a0542baa836f53561332aa7f2108da39d4`;
- unknown decomposition: `sha256:ada57eddefb02c65f6af65394a9f5e43e7a08bde1c3f37453668aa7102788f25`.

## Source-representation normalization

One harness failure exposed that the real RSH Markdown source line-wraps the root sentence while the candidate proposition is stored as a normalized single line. The successor comparison uses whitespace-only normalization **only to establish source/proposition correspondence**.

- candidate proposition bytes changed: no;
- source bytes changed: no;
- candidate text hashes changed: no.

This normalization is therefore an explicit mechanical representation behavior, not semantic rewriting.

## Auxiliary BM25 negative control

A deliberately coarse direct probe represented the two supplied sources as one whole-document chunk each. Real EB BM25 returned zero positive-score hits for the root and both children. This falsified the evaluator assumption that a positive direct hit was a prerequisite for proving exact-query consumption.

The result is preserved. It is not repaired or reclassified as retrieval success.

The production EB loader/chunker/retrieval writer, exercised separately in the same experiment, did retrieve evidence for both declared children. Contract A does not claim retrieval completeness or require a particular retrieval score.

## Bounded conclusion

The observed path supports the following narrower claim:

> Contract A RC2 can preserve upstream proposition/decomposition/source identity through real Evidence Bundler, canonical Contract B 1.2, and CAL source-contract proposition intake without granting upstream semantic-looking legacy observations downstream authority.

It does not prove independent recoverability. That requires the separately prepared fresh reproduction.
