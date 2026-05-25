# Apparatus Contracts: verifier suite targets.
#
# Usage:
#   make install        Create .venv and install the package + dev deps.
#   make verify         Run all three verifiers (skips integrity check).
#   make verify-vocabulary
#   make verify-spec
#   make verify-integrity ARTIFACT=path/to/scaffold-run-or-bundle
#   make test           Run the pytest suite.
#   make clean          Remove .venv and caches.

PYTHON      ?= python3
VENV        ?= .venv
VENV_PY     := $(VENV)/bin/python
VENV_PIP    := $(VENV)/bin/pip
PYTEST      := $(VENV)/bin/pytest
ARTIFACT    ?=

.PHONY: install verify verify-vocabulary verify-spec verify-integrity test clean

install: $(VENV)/.installed

$(VENV)/.installed: pyproject.toml
	$(PYTHON) -m venv $(VENV)
	$(VENV_PIP) install --upgrade pip
	$(VENV_PIP) install -e ".[dev]"
	@touch $(VENV)/.installed

verify: verify-vocabulary verify-spec

verify-vocabulary: install
	$(VENV_PY) -m validators verify-vocabulary

verify-spec: install
	$(VENV_PY) -m validators verify-spec-vocabulary

verify-integrity: install
	@if [ -z "$(ARTIFACT)" ]; then \
		echo "usage: make verify-integrity ARTIFACT=path/to/scaffold-run-or-bundle"; \
		exit 2; \
	fi
	$(VENV_PY) -m validators verify-integrity "$(ARTIFACT)"

test: install
	$(PYTEST) tests/

clean:
	rm -rf $(VENV) .pytest_cache **/__pycache__
