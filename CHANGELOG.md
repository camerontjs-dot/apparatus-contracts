# Changelog

This repository contains independently versioned public artifacts. Changelog entries identify the artifact and its own compatibility version; repository-level tags must not be used to infer a contract version.

## Contract D 1.0.0 — proposed / unreleased

### Proposed

- First canonical Contract D compatibility surface: `1.0.0`.
- Exact upstream-authority, Decision-policy, and target/content binding.
- Distinct completed CLEAR, completed HOLD, and failed-evaluation states.
- Typed/versioned effect registry with safe stored-effect defaults.
- Total normalized effect shape with exactly `type`, `version`, and `params`, including explicit `params: {}` for empty parameter schemas.
- Exact requested-operation and explicitly supplied requested-parameter applicability before any authority-bearing outcome.
- RFC 8785/JCS canonicalization with Contract-D trailing-LF framing, finite/interoperable JSON controls, Unicode-scalar validation, duplicate-key rejection, safe-number ingress handling, deterministic depth-128 processing, and controlled fail-closed behavior.
- Semantic Decision identity excluding metadata and Authorization-only context.
- Production validator/canonicalizer/consumer helpers, fixtures, conformance cases, and promotion CI.

### Compatibility

- This is the proposed first canonical Contract D release; there is no prior Contract D production version to migrate.
- Research identifiers such as `0.3.0-rc6` remain evidence identities and are not supported production versions.
- Exact `1.0.0` objects reject unknown Contract-D fields and unknown/future Contract-D versions fail closed.
- Incompatible removal or reinterpretation of a required v1 obligation requires a later major-version decision.
- Additive capability is minor only after semantic compatibility is demonstrated against legitimate v1 producers and consumers.

### Evidence and release gate

- Decision authority: EDR-003 / issue #28.
- RC6 research candidate: `bb656fc50806c344fda1ddeaf08a9878f5cb460e`.
- Terminal fresh independent reproduction: `camerontjs-dot/research-scaffold-harness@1b51b421b96fb10f260f58a087c8376b35afdb5d`.
- Terminal record blob: `08ebd8af17b6029274c282fb803a373a25e9b081`.
- Differential: 166 comparisons; 159 authority-relevant agreements; 0 authority-relevant disagreements; 0 public-authority ambiguities.
- This entry remains **unreleased** until the production producer/consumer/adversarial gates, merge acceptance, immutable `contract-d-v1.0.0` tag, GitHub Release, and post-merge lock evidence are complete.

### Known limits / non-claims

Contract D 1.0.0 does not itself establish actor identity, approval, delegation, autonomy/trust state, operational Authorization, execution permission or occurrence, execution receipts, correctness of upstream epistemic judgments, universal language/runtime interoperability, arbitrary future producers/consumers/transports, or unlimited resource behavior.

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
