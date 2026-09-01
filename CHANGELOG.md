# Changelog

This repository contains independently versioned public artifacts. Changelog entries identify the artifact and its own compatibility version; repository-level tags must not be used to infer a contract version.

## Contract A 2.0.0 — 2026-09-01

### Added

- First canonical standalone Contract A production release, version `2.0.0`.
- Exact producer/work/root proposition identity and whole-object integrity binding.
- Explicit decomposition states with exact declared `all_of` child identity/text/hash/order/lineage.
- Exact supplied UTF-8 source representation identity, bytes, media type, and content hashes.
- Fail-closed unknown-field and missing-state handling.
- Canonical production validator entry point, schema routing, frozen fixtures, and release-lock evidence.

### Compatibility

- This is a major compatibility successor to legacy Contract A `1.0.0`; the legacy specification remains immutable historical authority.
- The public release version is `2.0.0`, while the tested integrity-bound wire token remains exactly `contract-a-wire-candidate-rc2` so release does not rewrite already-tested handoff identities.
- Legacy inputs without first-class decomposition lineage must preserve `unknown`, not invent `not_decomposed`.
- Reverse projection into strict legacy A is not generally faithful and is not claimed as Contract A 2.0.0 authority.

### Evidence and release identity

- Decision authority: EDR-004 / issue #60.
- RC2 terminal research: PR #57, `SUPPORTED FOR PROMOTION`.
- Fresh independent recovery terminal: `camerontjs-dot/research-scaffold-harness@dada22df71e1f3d26d7646a1cd7429cdab519318`.
- Bounded A→E pressure terminal: PR #61, `SUPPORTED FOR PROMOTION`.
- Decisive pressure run: `33557518640`, artifact `9819938146`.
- Production promotion PR: #65.
- Production promotion merge: `b59c2fbe38bae78a3a35699362c0e67d17152e4b`.
- Official immutable release tag: `contract-a-v2.0.0` on the exact release commit after the post-promotion release-lock workflow passes.

### Known limits / nonclaims

Contract A 2.0.0 does not establish source authenticity/trust, retrieval completeness, decomposition semantic correctness, proposition truth/support/refutation, CAL semantic accuracy, Decision policy correctness, Contract E qualification/surplus-record closure, operational Authorization, execution permission, or execution occurrence.

## Contract C 1.0.0 — 2026-08-29

### Added

- First canonical Contract C compatibility surface: `1.0.0`.
- Exact Contract-B version/bundle/hash binding and proposition/evidence reference integrity.
- Exact CAL semantic implementation and canonical policy identity.
- Explicit eligibility, semantic-validity, aperture/completeness, and temporal/applicability execution-state slots.
- Retained support/counterevidence contributions, aggregate measurement identity/value and exact co-maximal basis references.
- Lossless terminal-basis and causal-multiplicity representation for single necessary, independent alternatives, jointly sufficient/co-sufficient, residual/non-deciding, and tied/co-maximal cases demonstrated by the promotion evidence.
- Deterministic canonical JSON, content-derived result-set identity, and separate normative whole-object SHA-256 validation.
- Frozen schema, validator, reference fixture, Contract-B conformance index, fail-closed controls, and downstream-policy firewall.

### Compatibility

- This is the first canonical Contract C release; there is no prior Contract C production version to migrate.
- Exact `1.0.0` objects reject unknown Contract-C fields.
- Incompatible required shape or semantic reinterpretation requires a later major-version decision.
- Additive capability is minor only after compatibility is demonstrated against legitimate v1 consumers.
- Contract B and Contract C remain independently versioned artifacts even though both are housed in this repository.

### Evidence and release identity

- Decision authority: EDR-002 / issue #17.
- Promotion candidate: `5759985ee0ae82c469a129152b2eac278b30e919`.
- Apparatus production promotion merge: `b804958be9da841b7fb1541b0535767a933a2769`.
- CAL producer candidate: `095d0fc0d4a8746a1b5296d9414ba9e6e173dc96`.
- CAL production exporter merge: `a069707e5031cef5b82af02d08b0f1a47ea8752e`.
- Clean-consumer evidence head: `a488c1b8058b5cda8766e670eb2b18d65e4e504e`.
- Frozen handoff commit: `213ed9e912b922bd5c57ef58009eb6b0d7fff398`.
- Canonical Contract C fixture SHA-256: `7a66583e332be4901d13ba9f2d7e12419938c77a41b83223a4b0946ad529b7a1`.
- Official immutable release tag: `contract-c-v1.0.0` on the exact release commit after the post-merge release-lock workflow passes.

### Known limits / non-claims

Contract C 1.0.0 does not establish universal interoperability, correctness of CAL semantic judgments, generic assessment behavior CAL did not execute, source/corpus completeness, Decision Engine production policy correctness, operational authorization, Contract-B changes, or arbitrary future CAL producer compatibility.