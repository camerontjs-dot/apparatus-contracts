# validators/

The contract-integrity verifier suite. Three Python modules enforce every claim the spec makes about hash-verified canonical distribution, spec/YAML parity, and artifact-tree integrity.

## Quick start

```bash
make install         # one-time: create .venv and install package + dev deps
make verify          # run vocabulary + spec checks
make verify-integrity ARTIFACT=../evidence-bundler/examples/handoff-demo/scaffold-run-bm25-handoff-demo
make test            # run the pytest suite
```

Direct invocation without the Makefile:

```bash
python -m validators verify-vocabulary
python -m validators verify-spec-vocabulary
python -m validators verify-integrity path/to/artifact
```

## Tools

### `verify-vocabulary`

Hashes the canonical `../schema/vocabulary.yaml` against the embedded copy in every consumer and confirms each consumer's `.contract-version` pin matches the canonical contract version. Default search paths use the portfolio sibling layout (`../<consumer>/schema/`); override individual paths with `--consumer name=/abs/path/to/schema` (repeatable).

Consumers absent from disk are reported as `[absent]` and do not fail unless `--strict` is passed.

Exit 0 on success. Exit 1 with a per-consumer report on drift, pin mismatch, or strict-mode missing files.

### `verify-spec-vocabulary`

Parses the controlled-vocabulary table in `../handoff-contract-v1.0.0.md` (the section headed "Controlled Vocabulary Summary") and asserts that each vocabulary's value set is identical to the corresponding list in `../schema/vocabulary.yaml`. Catches the failure mode where the spec text is updated but the machine-readable file is not, or vice versa.

Exit 0 on parity. Exit 1 with a per-vocabulary divergence report.

### `verify-contract-integrity`

Validates an artifact tree end-to-end. Pass the path to a `scaffold-run-{run_id}/` (C-A) or `evidence-bundle-{bundle_id}/` (C-B) directory. The verifier:

1. Confirms the `CONTRACT_VERSION` file is present and names a version in `{"1.0.0", "1.1.0"}` (matches the dual-acceptance pattern from Evidence Bundler ADR-012 and CAL DECISIONS.md 2026-05-17).
2. Recomputes SHA-256 for every file listed in `SHA256SUMS` and reports any mismatch.
3. Loads every YAML through the matching Pydantic model in `_models.py` and collects all schema-validation errors before exiting.

Pass `--against-pin VERSION` to require the artifact's `CONTRACT_VERSION` to equal a specific version (useful when a consumer wants to assert it received the version it expected).

A failed check exits 1 with a per-file error list. The check accumulates errors before exiting so one run surfaces every problem instead of one at a time.

## Module layout

- `_hashing.py`: SHA-256 helpers and `SHA256SUMS` parsing.
- `_vocabulary.py`: canonical vocabulary loader.
- `_models.py`: Pydantic models for the eight YAML types the spec defines.
- `verify_vocabulary.py`, `verify_spec_vocabulary.py`, `verify_contract_integrity.py`: the three verifiers.
- `__main__.py`: subcommand dispatcher invoked by `python -m validators`.

The Pydantic models in `_models.py` double as machine-readable schema documentation. Each model carries the field constraints the spec specifies (required vs. optional, controlled-vocabulary literals, value ranges). The `verify-spec-vocabulary` check catches drift between the model literals, the spec markdown, and the canonical YAML.
