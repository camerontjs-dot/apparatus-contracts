from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
PREDECESSOR_REFERENCE_PATH = (
    REPO
    / "docs/research/contract-e/v1-rc3-exact-currentness-jcs-20260902/candidate/reference.py"
)

_spec = importlib.util.spec_from_file_location(
    "contract_e_v1_rc3_predecessor_reference", PREDECESSOR_REFERENCE_PATH
)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"cannot load predecessor reference: {PREDECESSOR_REFERENCE_PATH}")
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)

# Re-export the frozen predecessor machinery so the successor differs only in
# the target-reference resolution predicate below.
for _name in dir(_base):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_base, _name)


def validate_request(request: Any) -> tuple[bool, list[str]]:
    """Validate the frozen RC3 request with exact-one target resolution.

    The predecessor validated every reference and then tested only membership
    of jurisdiction.target_ref in the set of reference identities. The frozen
    RC3 SPEC requires that target_ref resolve to exactly one *validated*
    request reference. This successor retains all predecessor structural rules
    and changes only that cardinality check.
    """

    try:
        _base.canonical_bytes(request)
    except Exception:  # noqa: BLE001
        return False, ["malformed_request"]
    if not _base._exact_keys(request, _base.REQUEST_KEYS) or request.get("schema") != _base.REQUEST_SCHEMA:
        return False, ["malformed_request"]
    if not _base._nonempty_string(request.get("request_id")):
        return False, ["malformed_request"]
    if not _base._is_sha256(request.get("authority_state_id")):
        return False, ["malformed_request"]
    if not _base._safe_time(request.get("evaluation_time")) or not _base._nonempty_string(request.get("subject_id")):
        return False, ["malformed_request"]

    jurisdiction = request.get("jurisdiction")
    if not _base._exact_keys(jurisdiction, _base.JURISDICTION_KEYS):
        return False, ["malformed_request"]
    if not all(
        _base._nonempty_string(jurisdiction[key])
        for key in ("domain", "operation", "scope", "target_class")
    ):
        return False, ["malformed_request"]
    if not _base._is_sha256(jurisdiction["target_ref"]):
        return False, ["malformed_request"]

    refs_ok, ref_ids = _base._validate_references(request.get("references"))
    if not refs_ok:
        return False, ["malformed_request"]

    target_matches = [
        ref
        for ref in request["references"]
        if ref["identity_sha256"] == jurisdiction["target_ref"]
    ]
    if not target_matches:
        return False, ["target_reference_missing"]
    if len(target_matches) != 1:
        return False, ["target_reference_ambiguous"]

    if not _base._validate_support(request.get("supporting_artifacts"), ref_ids):
        return False, ["malformed_request"]
    if not _base._validate_blockers(request.get("conflicts")) or not _base._validate_blockers(request.get("residues")):
        return False, ["malformed_request"]
    return True, []


# The frozen evaluate() resolves validate_request through its module globals.
# Patch only this in-memory successor module instance; predecessor repository
# bytes remain untouched.
_base.validate_request = validate_request


def evaluate(authority_state: Any, request: Any) -> dict:
    return _base.evaluate(authority_state, request)
