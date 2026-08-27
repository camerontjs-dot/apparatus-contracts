"""Verifier suite for the research apparatus handoff contracts.

This package implements the verifier tools referenced by the contract specs.
"""

from __future__ import annotations

SUPPORTED_CONTRACT_VERSIONS: frozenset[str] = frozenset({"1.0.0", "1.1.0", "1.2.0"})
"""Contract versions this verifier accepts on artifact intake.

v1.2.0 adds the optional Contract-B factual-context extension while preserving
intake compatibility for v1.0.0 and v1.1.0 artifacts.
"""

CANONICAL_CONTRACT_VERSION: str = "1.2.0"
"""Current canonical contract version."""
