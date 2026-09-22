from __future__ import annotations

import sys
from pathlib import Path

import pytest


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EXPERIMENT_ROOT))

from receipt_preflight import PreflightError, inspect_supervisor_api  # noqa: E402


CLIENT_SOURCE = b'''\
from typing import Any

def make_request(*, decision: dict[str, Any], execution_intent: dict[str, Any], authority_state: dict[str, Any], challenge: str) -> dict[str, Any]:
    return {"schema": "request-v1", "decision": decision, "execution_intent": execution_intent, "authority_state": authority_state, "challenge": challenge}

def evaluate_and_attest(socket_path: str, *, decision: dict[str, Any], execution_intent: dict[str, Any], authority_state: dict[str, Any], challenge: str) -> dict[str, bytes]:
    return {}
'''

SERVER_SOURCE = b'''\
from typing import Any

_REQUEST_KEYS = {"schema", "decision", "execution_intent", "authority_state", "challenge"}

class _EvaluationServer:
    def evaluate_and_attest(self, request: Any) -> dict[str, str]:
        return {}
'''

TRANSCRIPT_SOURCE = b'''\
ISSUER_PUBLIC_KEY_PEM = b"""-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEAKlHbYp+oTHO3iaBSwhqyYW+ybobI/iFP4iDXESQm0Tg=
-----END PUBLIC KEY-----
"""
ISSUER_KEY_ID = "sha256:e7f4581c2d58eecd0279f895cf3dd49df3098d092fa1e083731d802fcd1db259"
'''


def inspect(
    client: bytes = CLIENT_SOURCE,
    server: bytes = SERVER_SOURCE,
    transcript: bytes = TRANSCRIPT_SOURCE,
) -> dict:
    return inspect_supervisor_api(client, server, transcript)


def test_exact_supervisor_and_wire_api_is_accepted() -> None:
    result = inspect()
    assert result["wire_keys"] == [
        "schema",
        "decision",
        "execution_intent",
        "authority_state",
        "challenge",
    ]
    assert result["issuer_public_key_identity"] == (
        "sha256:e7f4581c2d58eecd0279f895cf3dd49df3098d092fa1e083731d802fcd1db259"
    )


def test_caller_evaluation_time_parameter_is_rejected() -> None:
    changed = CLIENT_SOURCE.replace(
        b"authority_state: dict[str, Any], challenge: str",
        b"authority_state: dict[str, Any], evaluation_time: str, challenge: str",
    )
    with pytest.raises(PreflightError, match="public_supervisor_api_shape_mismatch"):
        inspect(client=changed)


def test_caller_contract_e_result_parameter_is_rejected() -> None:
    changed = CLIENT_SOURCE.replace(
        b"authority_state: dict[str, Any], challenge: str",
        b"authority_state: dict[str, Any], contract_e_result: dict[str, Any], challenge: str",
    )
    with pytest.raises(PreflightError, match="public_supervisor_api_shape_mismatch"):
        inspect(client=changed)


def test_variadic_caller_signing_path_is_rejected() -> None:
    changed = CLIENT_SOURCE.replace(
        b"challenge: str) -> dict[str, bytes]",
        b"challenge: str, **caller_values: Any) -> dict[str, bytes]",
    )
    with pytest.raises(PreflightError, match="public_api_variadic_parameters_forbidden"):
        inspect(client=changed)


def test_contract_e_result_wire_field_is_rejected() -> None:
    changed = CLIENT_SOURCE.replace(
        b'"challenge": challenge}',
        b'"challenge": challenge, "contract_e_result": {}}',
    )
    with pytest.raises(PreflightError, match="supervisor_wire_keys_changed"):
        inspect(client=changed)


def test_server_allowlist_cannot_admit_result_or_time() -> None:
    changed = SERVER_SOURCE.replace(
        b'"challenge"}',
        b'"challenge", "evaluation_time", "contract_e_result"}',
    )
    with pytest.raises(PreflightError, match="supervisor_wire_keys_changed"):
        inspect(server=changed)


def test_receipt_cannot_bind_a_different_public_issuer_key() -> None:
    changed = TRANSCRIPT_SOURCE.replace(
        b"e7f4581c2d58eecd0279f895cf3dd49df3098d092fa1e083731d802fcd1db259",
        b"0" * 64,
    )
    with pytest.raises(PreflightError, match="issuer_public_key_identity_mismatch"):
        inspect(transcript=changed)
