"""Canonical Contract C 2.0.0 production entry point.

Contract C 2.0.0 deliberately retains the exact frozen Candidate A RC2 wire
profile that passed producer and independent-consumer conformance. Public
compatibility versioning is external to the integrity-bearing wire object so
promotion does not silently create a new, untested Contract C subject.
"""

from __future__ import annotations

from .contract_c_rc2 import (
    CAL_RC1_IMPLEMENTATION,
    CAL_RC1_POLICY_SHA256,
    POLICY_RESOLVER_FIXTURE_COMMIT,
    CandidateError,
    canonical_bytes,
    canonical_object,
    compute_result_set_id,
    seal,
    validate_object,
    verify_candidate,
    verify_contract_b_references,
    verify_external_authority,
    verify_policy_resolution,
    whole_object_sha256,
)

CONTRACT_C_VERSION = "2.0.0"
WIRE_PROFILE = "contract-c-successor-candidate-a-rc2-research"
# Compatibility alias for callers that operate on the integrity-bearing wire
# profile directly. It is intentionally not the public SemVer version.
PROFILE = WIRE_PROFILE

ContractCValidationError = CandidateError

__all__ = [
    "CONTRACT_C_VERSION",
    "WIRE_PROFILE",
    "PROFILE",
    "CAL_RC1_IMPLEMENTATION",
    "CAL_RC1_POLICY_SHA256",
    "POLICY_RESOLVER_FIXTURE_COMMIT",
    "ContractCValidationError",
    "canonical_bytes",
    "canonical_object",
    "compute_result_set_id",
    "seal",
    "validate_object",
    "verify_candidate",
    "verify_contract_b_references",
    "verify_external_authority",
    "verify_policy_resolution",
    "whole_object_sha256",
]
