# Validation Package

status: verified for v1 public release; v1.1.0 vocabulary path verified
last_updated: 2026-05-22

Purpose: make Apparatus Contracts' validation approach visible as part of the project, not only as planning notes. This package adapts pharma equipment qualification habits (IQ / OQ / PQ) for a non-GxP portfolio asset. It does not claim FDA, EMA, GxP, GMP, CSV, or regulated-validation status.

## Boundary

Apparatus Contracts validates the contracts themselves (the canonical vocabulary, the spec, and the verifier suite that enforces both).

It does not validate the *methodological correctness* of any specific scaffold run or evidence bundle a consumer produces. That measurement validity is owned by the research proposal and the consumers' own validation packages (`live-asset/claim-audit-lab/validation/`, `live-asset/evidence-bundler/`).

A passing validation artifact in this package means the verifier suite behaved as expected for a defined requirement, fixture, command, or artifact tree.

## Validation Package Map

| File | Purpose | Current state |
| --- | --- | --- |
| `qualification-plan.md` | Overall qualification strategy, acceptance rules, deviations, and revalidation triggers. | verified strategy |
| `iq-installation.md` | Installation qualification protocol and record. | verified |
| `oq-operational.md` | Operational qualification protocol and record (verifier behavior on synthetic positive and negative cases). | verified |
| `pq-performance.md` | Performance qualification protocol and record (verifier behavior on real C-A and C-B artifacts from sibling assets). | verified for v1 |
| `deviation-log.md` | Visible log for validation failures, accepted limitations, and follow-up actions. | no open failures; future-use gates recorded |
| `../docs/verification.md` | Public release verification summary and command results. | active |

## How This Should Be Used

During implementation, add or update a protocol row before adding a public capability claim. The asset publishes verifier behavior, so every new verifier-side feature should land with a matching OQ or PQ row.

The validation package was executed for the public v1 scope on 2026-05-22:

1. IQ verified clean local installation, editable install, CLI availability, and ignored artifacts.
2. OQ verified the verifier suite's behavior on synthetic positive and negative cases through the automated pytest suite and CLI smoke runs.
3. PQ verified the verifier suite against five real artifact trees committed in sibling assets (one C-A and four C-B bundles, including a CAL-audited bundle with populated `audit.*` fields).
4. Outcomes are recorded in the protocol files and `../docs/verification.md`.
5. Accepted future-use gates are visible in `deviation-log.md`.

## Pass Standard

The validation package is acceptable for a public portfolio release when:

- README capability claims trace to a protocol row in IQ, OQ, or PQ
- every verifier in `validators/` has matching synthetic positive and negative coverage in pytest
- every verifier exit path (`OK`, `FAIL`, structured error report) is exercised in OQ or PQ
- PQ runs the verifier against at least one real C-A artifact and one real C-B artifact emitted by the consumers
- the spec's "Controlled Vocabulary Summary" table and `schema/vocabulary.yaml` agree by `verify-spec-vocabulary`
- every consumer's embedded `schema/vocabulary.yaml` is byte-identical to canonical (`verify-vocabulary` reports `[OK]` for every present consumer)
- there are no open v1 validation failures

The validation package meets this pass standard for the v1 portfolio release.

## v1.1.0 Vocabulary Addendum

On 2026-05-22, the package was extended to verify the v1.1.0 vocabulary path (`format_only` added to `workflow_condition`). The addendum covers:

- artifact acceptance at `CONTRACT_VERSION: 1.1.0` through the dual-acceptance pattern
- `--against-pin` enforcement when a caller requires a specific version
- spec/canonical parity after the v1.1.0 amendment was added to the spec's controlled-vocabulary table

The addendum entries are integrated inline in `oq-operational.md` and `pq-performance.md`.
