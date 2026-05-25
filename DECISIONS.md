# Apparatus Contracts: design decisions

This file tracks architecturally significant decisions for the apparatus-contracts asset. Each entry follows ADR format: what was decided, what was rejected, and why. Decision substance is append-only. Add a superseding entry if a prior decision changes; do not edit history.

A new entry is required when a change touches:

- The contract version (semver bump under the spec's Schema Version Control rule)
- The controlled vocabulary (value additions, renames, removals)
- The schema shape (required fields, nested structure, vocabulary distribution model)
- Anything that breaks one of the three consumers (Claim Audit Lab, Evidence Bundler, future Research Scaffold Harness)

The portfolio-level `decisions.md` (one level up) holds cross-asset decisions and stays out of the public repo. This file is the on-asset record a public reader sees.

---

## Decision index

| Date | Title | Status |
|---|---|---|
| 2026-05-08 | v1.0.0 contract lock and design choices | Accepted |
| 2026-05-08 | Naming: spec retains "Evidence Builder" as a contract role | Accepted |
| 2026-05-15 | v1.1.0 vocabulary addition: `format_only` workflow condition | Accepted |

---

## 2026-05-08: v1.0.0 contract lock and design choices

**Status:** Accepted

**Decision:** Lock the C-A (Scaffold Harness → Evidence Builder) and C-B (Evidence Builder → Claim Audit Lab) contracts at v1.0.0 with four design choices baked in. The full spec lives in `handoff-contract-v1.0.0.md`; this entry records the choices that were non-obvious enough to warrant ADR capture.

**The four choices:**

1. **Canonical home and vocabulary distribution.** The canonical spec lives here. The machine-readable vocabulary lives at `schema/vocabulary.yaml`. Every consumer embeds a byte-identical copy plus a `schema/.contract-version` pin file. The verifier in `validators/` hashes consumer copies against canonical and fails on drift. Rejected alternative: install-time dependency on a shared package. That would break the "clone and run independently" guarantee the portfolio depends on, and would hide the vocabulary distribution behind a Python import rather than making it a first-class regulated-industry artifact.

2. **`audit_support_verdict` uses six values, not four.** The intuitive vocabulary is `supported`, `partially_supported`, `unsupported`, `not_checkable`. v1.0.0 adds `overstated` and `needs_source` to preserve two failure modes the research proposal enumerates as primary metrics: "overconfident conclusions" maps to `overstated`, and "missing source provenance" maps to `needs_source`. Collapsing them into `unsupported` would erase the distinction the experiment is designed to measure.

3. **`not_checkable` over `not_audit_ready`.** Claim Audit Lab's pre-contract vocabulary used `not_audit_ready` for the same concept. v1.0.0 picks `not_checkable` as the cleaner term: the verdict says something about the claim, not about the auditor's readiness. Consumer-side rename is recorded in `live-asset/claim-audit-lab/DECISIONS.md`.

4. **`reviewer_sign_off` ships forward-looking with deferred population.** The optional block on `bundle_manifest.yaml` exists in v1.0.0 as a 21 CFR Part 11 e-signature surface. For demo and experimental runs, fields stay null and `required: false`. Populate only when human review actually occurs (e.g., a pharma-customer-facing demo). The block is distinct from the always-populated `operator` field. Rejected alternative: omit the block until a regulated demo materializes. Adding e-signature surface later would require a MAJOR version bump and coordinated consumer updates; reserving the surface now costs nothing for non-regulated runs.

**Rejected alternatives at the contract level:**

- A single contract from Harness → CAL with no Evidence Builder middle stage. Rejected because the production/QC separation (C-A vs C-B) mirrors the GMP discipline the portfolio claim depends on. A merged contract would collapse the regulated-industry framing.
- Database-backed artifacts (SQLite or similar) instead of flat YAML/Markdown trees. Rejected because ALCOA Available requires the records to be readable without specialized tooling. Flat files are the highest-portability option.

---

## 2026-05-08: Naming: spec retains "Evidence Builder" as a contract role

**Status:** Accepted

**Decision:** The locked v1.0.0 spec, the schema field names (e.g., `evidence_builder.version` on the bundle manifest), and the C-A and C-B contract role descriptions all retain the name "Evidence Builder." Active project documentation, the sibling repository name (`evidence-bundler/`), and the README's narrative all use "Evidence Bundler."

**Why retain the historical name in the spec:** Renaming `evidence_builder.*` schema fields would be a MAJOR version bump per the contract's own change-control rule. v1.0.0 is locked; downstream consumers (Claim Audit Lab, Evidence Bundler) read and write `evidence_builder.*` fields. A rename would require coordinated MAJOR-bump deployments across every consumer.

**Why the project uses "Evidence Bundler":** The original name "Evidence Builder" implied building evidence, which overstates what the component does. It does not construct evidence; it bundles, curates, and integrity-seals already-retrieved evidence into a measurement-ready C-B artifact. "Bundler" is the more accurate term. The project adopted it for active development, leaving the locked spec untouched.

**Rejected alternatives:**

- Coordinated MAJOR-bump rename across all consumers. Rejected because the bump would propagate through CAL, EB, and the future Harness, and would force every existing fixture artifact to be regenerated. The naming inconsistency is documented; the cost of fixing it exceeds the benefit until another schema-level change forces a MAJOR bump anyway.
- Rename only in prose, keep field names. Rejected because that creates worse confusion than the current state: the spec text would say "Evidence Bundler" while the YAML schema would still say `evidence_builder`. A single name in the spec (matching the field names) is clearer than a split.

A short naming note in `README.md` flags the two-name situation so a fresh reader is not surprised.

---

## 2026-05-15: v1.1.0 vocabulary addition: `format_only` workflow condition

**Status:** Accepted

**Decision:** Add `format_only` as a fourth value to the `workflow_condition` controlled vocabulary. The MINOR bump preserves `baseline`, `provenance_scaffold`, and `full_scaffold`. The canonical `schema/vocabulary.yaml` declares `contract_version: "1.1.0"` and `locked_at_utc: "2026-05-15T00:00:00Z"`. Every consumer updates its embedded copy plus its `schema/.contract-version` pin in the same change.

**Why `format_only`:** The research proposal enumerates workflow conditions as the experimental treatment variable. The original three conditions cover an ascending discipline ladder: `baseline` (no scaffolding), `provenance_scaffold` (provenance only), `full_scaffold` (provenance plus disconfirmation plus audit). The proposal also wants to isolate the effect of visible structure without the discipline that backs it. `format_only` names that condition: the scaffold shows structure (sections, citations, claim tables) without enforcing provenance, disconfirmation, or audit. Distinguishing `format_only` from `provenance_scaffold` lets the experiment measure whether structure alone changes claim quality, or whether the discipline is what matters.

**Why the spec body stays at v1.0.0:** The spec's locked-body principle treats the v1.0.0 prose as immutable. Recording the v1.1.0 change in this DECISIONS.md and in the canonical `vocabulary.yaml` honors that principle without freezing future evolution. A new spec document at `handoff-contract-v1.1.0.md` is deferred until the Research Scaffold Harness ships; consolidating the deltas into a single update at that point is cheaper than maintaining multiple spec versions in parallel.

**Consumer propagation (completed 2026-05-17):**

- Evidence Bundler ADR-012 accepted the v1.1.0 vocabulary passthrough. `CONTRACT_VERSION` bumped to "1.1.0", `SUPPORTED_CONTRACT_VERSIONS` widened to `{"1.0.0", "1.1.0"}`, `WorkflowCondition` Literal extended with `format_only`, embedded `schema/vocabulary.yaml` replaced with byte-identical canonical copy (SHA-256 `30e2ac74…05526bb`), `schema/.contract-version` bumped to `1.1.0`.
- Claim Audit Lab DECISIONS.md 2026-05-17 accepted the same passthrough with identical mechanics. Both consumers accept v1.0.0 and v1.1.0 inputs without semantic difference; the new value flows through unchanged.

**Rejected alternatives:**

- Add `format_only` as a separate top-level field instead of a `workflow_condition` value. Rejected because the experimental design treats workflow_condition as one categorical variable; adding a second field doubles the analysis surface without adding signal.
- Reserve the bump until the Harness lands and bump multiple things at once. Rejected because the consumers needed the value to validate harness-produced artifacts before the harness shipped. Decoupling the vocabulary bump from the harness build is what made parallel work possible.
- Skip the canonical update and let each consumer add `format_only` to its own Literal. Rejected because that would silently allow consumer drift: the verifier hashes vocabularies, so without a canonical addition the consumer literal would be locally permissive but globally inconsistent. The vocabulary distribution model requires the addition to happen at canonical first.

**Verification:** Running `python -m validators verify-vocabulary` from the apparatus-contracts root reports zero drift across both extant consumers (CAL and EB) and marks the absent Harness consumer as `[absent]`. Running `python -m validators verify-spec-vocabulary` confirms the spec's controlled-vocabulary table and the canonical YAML agree.
