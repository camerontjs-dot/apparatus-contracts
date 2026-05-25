# Apparatus Contracts

This asset is the canonical home for the two handoff contracts that connect the three components of the research scaffold evaluation apparatus:

- **C-A:** Research Scaffold Harness → Evidence Bundler
- **C-B:** Evidence Bundler → Claim Audit Lab

The apparatus is the experimental measurement instrument behind a research question: do scaffolds reduce unsupported claims in AI research workflows?

A naming note. The locked v1.0.0 spec refers to the middle component as "Evidence Builder," which was the original contract role name. Active project docs and the sibling asset call it "Evidence Bundler." Both refer to the same component.

## Why this is a live-asset

Most live-asset folders carry executable tools. This one carries a *contract*: a versioned, schema-defined, integrity-verified specification that three other tools must satisfy. It earns live-asset status because:

- All three apparatus components reference it as their I/O specification.
- It has a versioning lifecycle (semver plus change-control) independent of any single tool.
- The vocabulary file is consumed at runtime by every component's CI as a hash-verified copy.
- Without it, the apparatus claim (a small empirical study on AI workflow reliability) collapses.

It is not a tool you run. It is a tool the other tools comply with.

## Layout

```
apparatus-contracts/
├── README.md                          # this file
├── DECISIONS.md                       # ADR log for the contract itself
├── LICENSE                            # MIT
├── Makefile                           # install / verify / test targets
├── pyproject.toml                     # package metadata for the verifier suite
├── handoff-contract-v1.0.0.md         # canonical spec (v1.0.0 locked; v1.1.0 amendments appended)
├── schema/
│   ├── vocabulary.yaml                # canonical machine-readable controlled vocabulary
│   └── .contract-version              # plain-text version pin (currently 1.1.0)
├── validators/                        # verifier suite (Python)
│   ├── README.md
│   ├── _models.py                     # Pydantic models for the eight YAML types
│   ├── _hashing.py
│   ├── _vocabulary.py
│   ├── verify_vocabulary.py
│   ├── verify_spec_vocabulary.py
│   └── verify_contract_integrity.py
├── tests/                             # pytest suite covering all three verifiers
├── validation/                        # IQ/OQ/PQ qualification package
│   ├── README.md
│   ├── qualification-plan.md
│   ├── iq-installation.md
│   ├── oq-operational.md
│   ├── pq-performance.md
│   └── deviation-log.md
└── docs/
    └── verification.md                # release verification with command transcripts
```

## What this asset demonstrates

Versioned contracts as load-bearing infrastructure. Three components that do not share code share a controlled, hash-verified specification instead.

Regulated-industry data-integrity grammar applied to AI workflow tooling. ALCOA+, 21 CFR Part 11, ICH Q10, and ISO 9001 dimensions are mapped onto the schemas, not bolted on as compliance theater.

Asymmetric contract design. C-A is a production artifact (a batch record). C-B is a measurement-ready artifact (a certificate of analysis with a prepared sample). The split mirrors the GMP separation between manufacturing and QC.

A forward-compatible regulated-deployment surface. The schema carries 21 CFR Part 11 e-signature fields with deferred population, ready for any future regulated-customer demo without a schema change.

## Vocabulary distribution model

Each consumer (Claim Audit Lab, Evidence Bundler, future Harness) embeds its own copy of `schema/vocabulary.yaml` plus a `schema/.contract-version` pin file. The verifier under `validators/` hashes all consumer copies against this canonical and fails on drift.

Components are designed to be cloneable independently, so an install-time dependency would break "clone and run." Explicit duplication with hash verification is also more on-brand for the regulated-industry framing than a hidden Python import.

## How to use this asset

You do not run it. You read it before designing or modifying any of:

- Research Scaffold Harness output (C-A)
- Evidence Bundler input or output (C-A consumer, C-B producer)
- Claim Audit Lab input (C-B consumer)

Read order for a cold session:

1. This README
2. `handoff-contract-v1.0.0.md` (the spec)
3. `DECISIONS.md` (why the spec made the choices it did, and what changed after v1.0.0 lock)
4. `schema/vocabulary.yaml` (the controlled-vocabulary canonical)
5. `validators/README.md` (verifier suite invocation)

## Try the verifier

The verifier suite enforces every drift claim the spec makes. From the asset root:

```bash
make install                    # one-time: creates .venv and installs deps
make verify                     # canonical-vs-consumer drift + spec/YAML parity
make test                       # pytest suite (passing + negative cases)
make verify-integrity \
  ARTIFACT=../evidence-bundler/examples/handoff-demo/scaffold-run-bm25-handoff-demo
```

Three verifiers, all in `validators/`:

- `verify_vocabulary.py` hashes `schema/vocabulary.yaml` against every consumer's embedded copy and confirms their `.contract-version` pin matches the canonical.
- `verify_spec_vocabulary.py` cross-checks the spec's controlled-vocabulary table against `schema/vocabulary.yaml`.
- `verify_contract_integrity.py` validates a C-A or C-B artifact tree (CONTRACT_VERSION presence, SHA256SUMS recompute, Pydantic-model schema validation per YAML).

## Example artifacts

The sibling Evidence Bundler asset ships a real C-A fixture at `../evidence-bundler/examples/handoff-demo/scaffold-run-bm25-handoff-demo/`. Committed contents: `scaffold_run.yaml`, `claims.yaml`, `corpus/` (three sources), `SHA256SUMS`, `CONTRACT_VERSION`. The matching C-B bundle is generated on demand by Evidence Bundler's `scripts/run_phase_4_unit1_handoff_demo.py` rather than committed. The committed C-A is sufficient to exercise `verify-integrity` end-to-end.

## Change control

Any change to the contract or vocabulary requires:

1. A decision-log entry stating the change, the affected schema version, and the rationale.
2. A semver bump per the spec's Schema Version Control section.
3. Updated copies in every consumer (CAL, Evidence Bundler, Harness) under their own `schema/` folder.
4. A re-run of the canonical-vocabulary verifier to confirm no drift.

## Validation

The verifier suite was qualified under an IQ/OQ/PQ-style validation package adapted from pharma equipment qualification (no GxP claim). The package is visible in the repo:

- `validation/README.md`: package overview, boundary, validation matrix, pass standard.
- `validation/iq-installation.md`, `oq-operational.md`, `pq-performance.md`: dated protocols with per-step expected results and evidence references.
- `validation/deviation-log.md`: accepted limitations and future-use gates (real-corpus calibration, e-signature human-review qualification).
- `docs/verification.md`: release verification summary with the actual commands run and their results.

The v1 package closed clean on 2026-05-22: 20/20 pytest, ruff clean, and the integrity verifier validated against one real C-A and four real C-B artifact trees from the sibling consumers (including a CAL-audited bundle with populated `audit.*` fields). The v1.1.0 vocabulary path was verified separately.

## Known limits

The Research Scaffold Harness has no executable surface yet. It carries an in-sync embedded vocabulary copy and pin, so `verify-vocabulary` treats it as a present consumer. No Harness-produced C-A has been validated through `verify-contract-integrity` because none exists.

The verifier suite enforces structural and vocabulary integrity. It does not validate methodological correctness of any specific scaffold run or evidence bundle. That is the research proposal's experimental design, not the contract's job.
