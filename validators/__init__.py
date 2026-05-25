"""Verifier suite for the research apparatus handoff contracts.

This package implements the three verifier tools referenced in the spec
(`handoff-contract-v1.0.0.md`) and its README:

- ``verify_vocabulary``: SHA-256 drift check across canonical and consumer copies.
- ``verify_spec_vocabulary``: cross-check between the spec's controlled-vocabulary
  table and ``schema/vocabulary.yaml``.
- ``verify_contract_integrity``: artifact-tree validator that recomputes
  ``SHA256SUMS``, confirms ``CONTRACT_VERSION``, and validates each YAML against
  the Pydantic models in :mod:`validators._models`.

See ``validators/README.md`` for invocation.
"""

from __future__ import annotations

SUPPORTED_CONTRACT_VERSIONS: frozenset[str] = frozenset({"1.0.0", "1.1.0"})
"""Contract versions this verifier accepts on artifact intake.

Matches the dual-acceptance pattern adopted by Evidence Bundler (ADR-012) and
Claim Audit Lab (DECISIONS.md 2026-05-17): v1.0.0 fixtures remain valid; new
artifacts are emitted at v1.1.0.
"""

CANONICAL_CONTRACT_VERSION: str = "1.1.0"
"""Current canonical contract version (matches ``schema/vocabulary.yaml``)."""
