# PQ: Performance Qualification

status: verified for v1
last_updated: 2026-05-22

Purpose: verify that the apparatus-contracts verifier suite behaves correctly against real C-A and C-B artifact trees produced by sibling consumers.

This is a validation-inspired record for a non-regulated portfolio context. It does not claim FDA, EMA, GxP, GMP, CSV, or regulated-compliance status. PQ exercises the engineering handoff path with fictional fixture data; calibration against real research corpora is a future-use gate (see `deviation-log.md`).

## Scope

- Vocabulary drift verifier run against the three real consumers committed in the portfolio sibling layout (Claim Audit Lab, Evidence Bundler, Research Scaffold Harness).
- Spec/canonical parity verifier run against the real spec markdown and canonical YAML in this asset.
- Contract-integrity verifier run against a real committed C-A artifact and four real C-B artifacts produced by the two extant consumers, including one CAL-audited bundle with populated `audit.*` fields.

## Real Artifacts Exercised

| Artifact | Type | Provenance | Committed location |
| --- | --- | --- | --- |
| `scaffold-run-bm25-handoff-demo` | C-A | Evidence Bundler synthetic handoff demo fixture | `../evidence-bundler/examples/handoff-demo/` |
| `evidence-bundle-minimal` (CAL fixture) | C-B (pre-audit) | Committed CAL test fixture | `../claim-audit-lab/tests/fixtures/cb/` |
| `evidence-bundle-minimal` (EB unit7 build) | C-B (pre-audit) | EB unit7 round-trip build output | `../evidence-bundler/build/unit7-roundtrip/` |
| `evidence-bundle-retrieval` (EB phase-2a) | C-B (pre-audit, larger) | EB phase-2a retrieval smoke build | `../evidence-bundler/build/phase-2a-retrieval-smoke.5xSa7J/` |
| `evidence-bundle-minimal-audited` (CAL) | C-B (audited, populated `audit.*`) | CAL unit7 round-trip audited output | `../claim-audit-lab/build/unit7-roundtrip/` |

## Protocol

| Step | Command | Expected result | Date run | Result | Evidence reference | Status |
| --- | --- | --- | --- | --- | --- | --- |
| PQ-001 | `.venv/bin/python -m validators verify-vocabulary` | All three real consumers report `[OK]`. Canonical hash matches consumer-embedded hashes. | 2026-05-22 | All three consumers `[OK]`; canonical hash `30e2ac74…05526bb` matches every consumer copy. | `../docs/verification.md` § PQ-001 | verified |
| PQ-002 | `.venv/bin/python -m validators verify-spec-vocabulary` | Spec controlled-vocabulary table matches `schema/vocabulary.yaml` for all 8 vocabularies. | 2026-05-22 | OK (8 vocabularies). | `../docs/verification.md` § PQ-002 | verified |
| PQ-003 | `.venv/bin/python -m validators verify-integrity ../evidence-bundler/examples/handoff-demo/scaffold-run-bm25-handoff-demo` | Real C-A handoff-demo passes (8 files checked). | 2026-05-22 | `result: OK` (8 files: scaffold_run.yaml, claims.yaml, 3 sources × 2 yaml). | `../docs/verification.md` § PQ-003 | verified |
| PQ-004 | `.venv/bin/python -m validators verify-integrity ../claim-audit-lab/tests/fixtures/cb/evidence-bundle-minimal` | Committed CAL C-B test fixture passes (4 files checked). | 2026-05-22 | `result: OK` (4 files: bundle_manifest.yaml, audit_config.yaml, 1 claim, 1 passage record). | `../docs/verification.md` § PQ-004 | verified |
| PQ-005 | `.venv/bin/python -m validators verify-integrity ../evidence-bundler/build/unit7-roundtrip/evidence-bundle-minimal` | EB-generated minimal bundle passes (4 files checked). | 2026-05-22 | `result: OK` (4 files). | `../docs/verification.md` § PQ-005 | verified |
| PQ-006 | `.venv/bin/python -m validators verify-integrity ../evidence-bundler/build/phase-2a-retrieval-smoke.5xSa7J/evidence-bundle-retrieval` | EB phase-2a retrieval bundle passes (8 files checked). | 2026-05-22 | `result: OK` (8 files: bundle_manifest.yaml, audit_config.yaml, 2 claims, 4 passage records). | `../docs/verification.md` § PQ-006 | verified |
| PQ-007 | `.venv/bin/python -m validators verify-integrity ../claim-audit-lab/build/unit7-roundtrip/evidence-bundle-minimal-audited` | CAL audited bundle with populated `audit.*` block passes (4 files checked). | 2026-05-22 | `result: OK` (4 files); `AuditBlock` model accepted `audit_run_id`, `audited_at_utc`, `audit_support_verdict="supported"`, `audit_confidence=1.0`, `audit_notes`, `false_caution_flag=false`, `deviation_flag=false`, `deviation_notes`. | `../docs/verification.md` § PQ-007 | verified |
| PQ-008 | Construct a v1.1.0 C-A artifact (tmp copy of handoff-demo with `CONTRACT_VERSION` bumped and SHA256SUMS regenerated for that entry), then `verify-integrity`. | Verifier accepts v1.1.0 artifact through the dual-acceptance pattern. | 2026-05-22 | `result: OK` (8 files); v1.1.0 acceptance verified. | `../docs/verification.md` § PQ-008 | verified |

## Acceptance Criteria

PQ passes when every row above is `verified` or carries an accepted deviation in `deviation-log.md`, and when at least one C-A and one C-B artifact from real consumer output have been exercised end-to-end.

## Record

PQ passed on 2026-05-22 against the v1 release candidate. All eight Pydantic models in `validators/_models.py` were exercised against real consumer artifacts (four C-A model types via PQ-003, four C-B model types via PQ-004 through PQ-007). The v1.1.0 vocabulary addendum was verified at PQ-008. No PQ-blocking deviations were recorded.
