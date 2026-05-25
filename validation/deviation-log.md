# Validation Deviation Log

last_updated: 2026-05-22

Purpose: track validation failures, accepted limitations, and future-use gates that are visible before any non-engineering use of the apparatus contracts.

## Open Failures

None as of 2026-05-22. IQ, OQ, and PQ all closed without blocking deviations.

## Accepted Limitations

### AL-001: Research Scaffold Harness has no executable surface yet

**Stage:** PQ
**Status:** Accepted

The Research Scaffold Harness consumer carries a byte-identical embedded `schema/vocabulary.yaml` and a `.contract-version` pin at `1.1.0`, so the drift check (`verify-vocabulary`) treats it as a present, in-sync consumer. The harness does not yet emit C-A artifacts, so no Harness-produced C-A has been validated through `verify-contract-integrity`. PQ rows for Harness-produced artifacts open when the harness ships.

The validation package's scope statement (`README.md`) flags this; no public capability claim depends on Harness-produced output today.

### AL-002: PQ uses fictional fixture data

**Stage:** PQ
**Status:** Accepted

All five C-A and C-B artifacts exercised in PQ are fictional or synthetic fixtures (the handoff-demo corpus is explicitly labeled "FICTIONAL DEMO CONTENT"; CAL test fixtures use synthetic Phase 0 data; EB build outputs are deterministic test bundles). The verifier exercises structural and vocabulary integrity. It does not exercise calibration against the kind of real-world regulatory or scientific corpora the apparatus is designed to measure over.

This is consistent with the validation boundary in `README.md`: the verifier checks contract conformance, not measurement validity.

## Future-Use Gates

These items are work the verifier suite cannot do today. They are visible before any non-engineering use of the asset.

### FUG-001: Real-corpus calibration

**Trigger:** First real-research apparatus run using non-fictional corpora.
**Owner:** Research proposal / consumer assets.
**Why deferred:** Real-corpus calibration is a methodological question owned by the research proposal and the consumers' own validation packages. The apparatus-contracts asset enforces structural integrity; it does not (and is not designed to) confirm that a given measurement run actually reduces unsupported claims.
**Open before:** Any research run that produces evidence used for an external claim about scaffolding efficacy.

### FUG-002: Human-review qualification for the deferred-population e-signature surface

**Trigger:** First regulated-customer demo or any populated `reviewer_sign_off` block on a real C-B bundle.
**Owner:** Evidence Bundler (producer) and Claim Audit Lab (consumer).
**Why deferred:** The v1.0.0 contract reserves the `reviewer_sign_off` block as a forward-looking 21 CFR Part 11 surface (see `DECISIONS.md` § 2026-05-08, design decision 4). The verifier accepts `required: false` with null fields today. When a real human signature populates the block, the consumer's own validation package must qualify the e-signature capture process; the apparatus-contracts verifier confirms the schema, not the signature's legal validity.
**Open before:** Any regulated-customer-facing deployment.

## Revalidation Notes

Validation history is preserved in `DECISIONS.md` (ADR log) and in the per-protocol `Record` sections of `iq-installation.md`, `oq-operational.md`, and `pq-performance.md`. Any future re-run of a protocol appends a new dated row to the protocol's table, leaving prior entries intact.
