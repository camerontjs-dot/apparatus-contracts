"""Canonical Contract A 2.0.0 production entry point.

Contract A 2.0.0 deliberately retains the exact frozen RC2 validation engine and
integrity-bound wire token that passed the promotion evidence program. Public
release versioning is external to the wire object so promotion does not rewrite
already-tested object identities.
"""

from __future__ import annotations

from .contract_a_rc2 import (
    CandidateValidationError,
    compute_handoff_sha256,
    load_candidate,
    validate_candidate,
)

CONTRACT_A_VERSION = "2.0.0"
WIRE_SCHEMA_TOKEN = "contract-a-wire-candidate-rc2"

ContractAValidationError = CandidateValidationError

__all__ = [
    "CONTRACT_A_VERSION",
    "WIRE_SCHEMA_TOKEN",
    "ContractAValidationError",
    "compute_handoff_sha256",
    "load_candidate",
    "validate_candidate",
]
