# Qualification Plan

status: verified strategy
last_updated: 2026-05-22

Purpose: state how Apparatus Contracts qualifies itself for public portfolio release, adapting the IQ / OQ / PQ idiom from pharma equipment qualification.

This is a validation-inspired record for a non-regulated portfolio context. It is not a GxP, GMP, CSV, FDA, or EMA qualification claim.

## Scope

The asset under qualification is the apparatus-contracts repository: the canonical spec (`handoff-contract-v1.0.0.md` plus appended amendments), the canonical controlled vocabulary (`schema/vocabulary.yaml`), and the verifier suite (`validators/`) that enforces both.

In scope:

- The verifier suite's behavior on positive and negative inputs.
- Drift detection across the canonical and every consumer's embedded vocabulary copy.
- Parity between the spec's "Controlled Vocabulary Summary" table and the canonical YAML.
- Integrity validation of real C-A and C-B artifact trees produced by sibling consumers.

Out of scope:

- Methodological validity of any individual scaffold run or evidence bundle (owned by the research proposal).
- Consumer-internal logic (owned by each consumer's own validation package).
- Real-data audit calibration and human-review qualification (deferred future-use gates, listed in `deviation-log.md`).

## Qualification Stages

**IQ (Installation Qualification).** Verifies that the asset can be installed and invoked in a clean local environment without hidden setup assumptions. Covers `pyproject.toml` metadata, dev install, package importability, CLI availability via `python -m validators`, Makefile targets, and ignored-artifact behavior.

**OQ (Operational Qualification).** Verifies that each verifier behaves correctly on synthetic positive and negative inputs. Covers the pytest suite (20 cases across `verify-vocabulary`, `verify-spec-vocabulary`, and `verify-contract-integrity`), ruff style compliance, and CLI smoke runs of negative paths.

**PQ (Performance Qualification).** Verifies that the verifier suite behaves correctly against real artifact trees produced by sibling consumers. Covers one real C-A (Evidence Bundler `examples/handoff-demo/`) and four real C-B bundles (one committed CAL test fixture, two EB-generated builds, one CAL audited output with populated `audit.*` fields).

## Acceptance Rules

- IQ, OQ, and PQ each pass when every protocol row in their respective file is `verified` or has an explicit accepted deviation in `deviation-log.md`.
- The package as a whole passes when all three stages pass and the Pass Standard in `README.md` is satisfied.
- Vocabulary or schema changes that bump the canonical contract version trigger a re-run of OQ-007 (spec/canonical parity) and at least one PQ row per affected artifact type.

## Deviations and Future-Use Gates

Validation failures and accepted limitations are recorded in `deviation-log.md`. v1 closed with no open failures. Two future-use gates are recorded for work the verifier suite cannot do today (full real-corpus calibration, human-review qualification for the deferred-population e-signature block).

## Revalidation Triggers

A re-run of the relevant protocol is required when any of the following lands:

- Canonical `schema/vocabulary.yaml` changes (rerun `verify-vocabulary` PQ rows for every consumer plus `verify-spec-vocabulary`).
- A new YAML artifact type is added to the spec (add OQ and PQ rows for the new Pydantic model in `validators/_models.py`).
- The verifier CLI surface changes (rerun IQ-004 and any affected OQ rows).
- A new consumer joins the apparatus (add it to PQ and to the verifier's default consumer list).
