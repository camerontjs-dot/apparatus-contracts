# IQ: Installation Qualification

status: verified
last_updated: 2026-05-22

Purpose: verify that the apparatus-contracts verifier suite can be installed and invoked in a clean local environment without hidden setup assumptions.

This is a validation-inspired record for a non-regulated portfolio context. It does not claim FDA, EMA, GxP, GMP, CSV, or regulated-compliance status.

## Scope

- Python version compatibility (>= 3.11)
- editable local install via `pyproject.toml`
- dev dependency resolution (pytest, ruff, types-PyYAML)
- runtime dependency resolution (PyYAML, pydantic)
- CLI availability via `python -m validators`
- Makefile targets (`install`, `verify`, `verify-vocabulary`, `verify-spec`, `verify-integrity`, `test`, `clean`)
- absence of required network, API key, or private data for normal checks
- ignored build artifacts and local caches

## Prerequisites

- A POSIX environment with `python3 >= 3.11` and `make` available.
- The asset directory (`live-asset/apparatus-contracts/`) is reachable as the working directory.
- Public examples use fictional or sanitized data (the sibling Evidence Bundler `examples/handoff-demo/` corpus is synthetic).

## Protocol

| Step | Command or inspection | Expected result | Date run | Result | Evidence reference | Status |
| --- | --- | --- | --- | --- | --- | --- |
| IQ-001 | Inspect `pyproject.toml` | Package metadata (`name`, `version`, `requires-python`, `dependencies`, `optional-dependencies.dev`, `[project.scripts]`, package discovery) is present. | 2026-05-22 | Metadata present: `apparatus-contracts 0.1.0`, Python `>=3.11`, deps `PyYAML>=6.0,<7` and `pydantic>=2.6,<3`, dev deps `pytest`, `ruff`, `types-PyYAML`, console script `apparatus-verify`, package discovery includes `validators*`. | `pyproject.toml`; `../docs/verification.md` | verified |
| IQ-002 | `make install` from asset root | Clean `.venv/` created and `pip install -e ".[dev]"` succeeds. | 2026-05-22 | Venv created at `.venv/`; editable install succeeded; runtime deps `PyYAML-6.0.3`, `pydantic-2.13.4`, `pydantic-core-2.46.4`; dev deps `pytest-9.0.3`, `ruff-0.15.14`, `types-PyYAML-6.0.12.20260518` installed. | `make install` output; `../docs/verification.md` | verified |
| IQ-003 | `.venv/bin/python -m validators --help` and per-subcommand help | Dispatcher recognizes `verify-vocabulary`, `verify-spec-vocabulary`, `verify-integrity`, `all` subcommands. | 2026-05-22 | All four subcommands present in `--help` output. | `validators/__main__.py`; `../docs/verification.md` | verified |
| IQ-004 | `.venv/bin/python -c "from validators import _models, _hashing, _vocabulary; print('ok')"` | Package and all private modules import without error. | 2026-05-22 | Import succeeded; no missing-dependency or syntax errors. | `validators/__init__.py`; `../docs/verification.md` | verified |
| IQ-005 | Inspect `.gitignore` | Caches, virtualenv, build artifacts ignored. | 2026-05-22 | `.venv/`, `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`, `build/`, `dist/`, `*.egg-info/`, `.DS_Store` all ignored. | `.gitignore` | verified |
| IQ-006 | Inspect Makefile targets | `install`, `verify`, `verify-vocabulary`, `verify-spec`, `verify-integrity`, `test`, `clean` are present and documented in the header. | 2026-05-22 | All seven targets present; usage banner correct. | `Makefile` | verified |
| IQ-007 | Inspect README setup instructions | Quick-start commands match the Makefile and CLI. | 2026-05-22 | README "Try the verifier" section uses `make install && make verify && make test`. | `README.md` § Try the verifier | verified |

## Acceptance Criteria

IQ passes when every row above is `verified` or carries an accepted deviation in `deviation-log.md`.

## Record

IQ passed on 2026-05-22 against the v1 release candidate. No IQ-blocking deviations were recorded.
