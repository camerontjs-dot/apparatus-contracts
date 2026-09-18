# CAL Pipeline Provenance RC1 — Terminal Reconstruction Receipt

**Disposition:** `SUPPORTED_PROVENANCE_RECONSTRUCTION_V1_RC1`

**Classification:** Draft Research evidence record only.

**Date:** 2026-09-17

## Authority lineage

- provenance architecture / candidate schemas: `camerontjs-dot/apparatus-contracts@1a5929295e735e351320cbd8c966dc43afed2859`
- execution preparation: `camerontjs-dot/research-scaffold-harness` Draft PR #37 at `976522f87da104ff0ac0d14baa148d298c02c538`
- independently frozen expected manifest roots: `camerontjs-dot/apparatus-contracts@92ebde5ad9274ca2632c9db13325c1110fe4edc7`
- root-freeze record: `research/cal-pipeline-provenance-rc1-root-freeze/EXPECTED-MANIFEST-ROOTS.json`

## Evidence source and boundary

A fresh/context-free local reconstruction consumer reported completion against the five externally frozen manifest roots. The durable local overall receipt was reported with:

`sha256:6d3bcc0b57aae2b81254fcbdd7e1e2e3ab5808838f3f1b3e03a17fdc1a6da9ac`

The private-local evidence package remains the byte authority for the reconstruction result. This GitHub record captures the result identity, totals, tested aperture, and nonclaims without publishing private local paths or run-package contents.

## Frozen roots and reconstruction result

| Case | Expected manifest root | Result |
| --- | --- | --- |
| `first-genuine-b-side-replay` | `sha256:9c450afa89078c23c12bb92254cf562d65a3589bf90c46e8762a3e292f234d2b` | `reconstructable` |
| `health-canada-ozempic-001` | `sha256:6e4290f6804a4a86d137411d337d00d6521fdf3f7d3fe534e6689fb032e0ae8d` | `reconstructable` |
| `rimebridge-simple-support` | `sha256:c2532604f75c78d954965096953eb53901e3ce41ea606060e08c49b45f74f8cc` | `reconstructable` |
| `amberbraid-temporal-supersession` | `sha256:8ba9d7544a225526235b45b5e6ff1e02e718ba6dde500d8a263c3103aba035d9` | `reconstructable` |
| `wick-missing-decisive` | `sha256:28adf52413da1631ad3c8477c5f7d8a53b2f0c86592e9327cfd2d2e0694b513f` | `reconstructable` |

## Independent reconstruction totals

Reported independent totals:

- required artifacts recovered: **49 / 49**
- commitments verified: **60 / 60**
- apparatus attestations valid: **12 / 12**
- artifact links resolved: **38 / 38**
- missing locators: **0**
- missing bytes: **0**
- digest mismatches: **0**
- schema failures: **0**
- unresolved authorities: **0**
- ambiguous links: **0**

Four metadata label aliases and one authority metadata alias were preserved explicitly in the private overall receipt. Their exact local rows are not re-transcribed here.

The Health Canada Evidence Bundler failure remained unchanged, including its fail-closed validation outcome. Reconstruction did not repair or reinterpret it.

## Supported claim

Under this five-run RC1 aperture, the candidate `ApparatusAttestation v1` + `RunManifest v1` provenance architecture supported independent reconstruction from externally frozen expected manifest commitments and retained artifacts.

The tested aperture includes:

- a complete historical B → CAL → C2 → Decision execution;
- legitimate ClaimGate negative stops with downstream non-execution;
- a downstream fail-closed Contract-A / Evidence-Bundler boundary;
- explicit absent-stage reconstruction;
- independently fixed manifest roots that were not moved to fit the presented package.

This supports the architecture's reconstruction capability under the tested aperture.

## Nonclaims

This result does **not** establish:

- universal Evidence Bundler retrieval recall or corpus completeness;
- ClaimGate coverage or authoring adequacy;
- CAL semantic correctness or accuracy;
- Contract C2 production promotion;
- Decision Engine semantic correctness;
- Authorization or automatic action;
- production readiness;
- released status for the candidate provenance schemas;
- merge, release, or promotion authority.

The provenance schemas remain research candidates. Promotion, if ever justified, requires a separate decision.

## Preserved follow-on observations

RC1 also exposed adjacent component questions that remain separate from provenance qualification:

1. Proposition Authoring can emit a Contract A carrying a media type outside released Contract A 2.0.0's allowed source representation vocabulary; Evidence Bundler correctly failed closed.
2. The three frozen benchmark cases did not create fresh downstream B → CAL → Decision executions because ClaimGate legitimately abstained.
3. The four metadata aliases and one authority alias require a bounded schema-normalization audit before any released provenance schema is considered.

## Terminal interpretation

The prior architecture disposition:

`PROMISING_ARCHITECTURE_REQUIRES_SCHEMA_AND_RECONSTRUCTION_QUALIFICATION`

is superseded for the reconstruction question by:

`SUPPORTED_PROVENANCE_RECONSTRUCTION_V1_RC1`

This is an evidence disposition, not production authorization.
