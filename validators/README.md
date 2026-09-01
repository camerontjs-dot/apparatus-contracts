# validators/

Canonical validators and legacy verification tools for the independently versioned apparatus contracts.

## Current contract validators

- `contract_a.py`: canonical Contract A 2.0.0 production entry point. It delegates validation and whole-object hashing to the byte-identical frozen RC2 engine in `contract_a_rc2.py` while exposing the public compatibility version separately.
- `contract_a_rc2.py`: byte-identical frozen Contract A wire validation engine used by 2.0.0. Its historical candidate naming is retained intentionally so the promoted machine authority can be proven identical to the tested research authority.
- `contract_b_factual_context.py`: Contract B factual-context extension validation.
- `contract_c.py`: Contract C 1.0.0 validation/canonicalization.
- `contract_d_core.py`, `contract_d_validate.py`, `contract_d_consume.py`: Contract D 1.0.0 validation, identity, and bounded consumption.

Each contract is independently versioned. Do not infer one contract's version from another contract or from the repository package version.

## Legacy Contract A/B artifact-tree verifier

The original 1.0/1.1 scaffold/evidence-bundle verifier remains available for historical and compatibility work:

```bash
make install
make verify
make verify-integrity ARTIFACT=../evidence-bundler/examples/handoff-demo/scaffold-run-bm25-handoff-demo
make test
```

Direct invocation:

```bash
python -m validators verify-vocabulary
python -m validators verify-spec-vocabulary
python -m validators verify-integrity path/to/artifact
```

### `verify-vocabulary`

Hashes the canonical `../schema/vocabulary.yaml` against embedded consumer copies and checks their legacy `.contract-version` pins. Consumers absent from disk are reported as absent unless strict mode is requested.

### `verify-spec-vocabulary`

Checks controlled-vocabulary parity between the legacy `handoff-contract-v1.0.0.md` specification and `schema/vocabulary.yaml`.

### `verify-contract-integrity`

Validates a legacy `scaffold-run-*` or `evidence-bundle-*` artifact tree, including `CONTRACT_VERSION`, `SHA256SUMS`, and the matching Pydantic YAML models. This tool is not the Contract A 2.0.0 single-object validator.

## Contract A 2.0.0 usage

```python
from validators.contract_a import (
    CONTRACT_A_VERSION,
    ContractAValidationError,
    compute_handoff_sha256,
    load_candidate,
    validate_candidate,
)
```

`CONTRACT_A_VERSION` is `2.0.0`. The integrity-bound object field `schema` remains exactly `contract-a-wire-candidate-rc2` so promoted objects preserve the identities exercised by the frozen research and pressure evidence.

The canonical machine schema and byte-identical frozen wire specification live under `schema/contract-a/2.0.0/`.

## Assurance boundary

A validator establishes only the properties encoded by its contract authority. Passing structural/integrity validation does not establish source legitimacy, retrieval completeness, proposition truth, CAL semantic correctness, Decision policy correctness, Contract E Authorization, or execution permission.
