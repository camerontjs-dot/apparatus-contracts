from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path

import rfc8785

CANDIDATE = Path(__file__).resolve().parent / "candidate"
if str(CANDIDATE) not in sys.path:
    sys.path.insert(0, str(CANDIDATE))

import reference as e


def jcs_lf(value) -> bytes:
    return rfc8785.dumps(value) + b"\n"


def main() -> int:
    target = e.reference_identity("example", None, "target:1")
    valid_state = {
        "schema": e.STATE_SCHEMA,
        "authority_state_id": "",
        "records": [
            {
                "id": "root",
                "basis_type": "grant",
                "subject_id": "actor:1",
                "domain": "knowledge",
                "operation": "knowledge.cite_as_evidence",
                "scope": "claim",
                "target_class": "claim-evidence-link",
                "target_ref": target,
                "valid_from": "2026-01-01T00:00:00Z",
                "valid_until": None,
                "revoked_at": None,
                "parent_id": None,
                "delegated_by": None,
            }
        ],
    }
    valid_payload = {k: deepcopy(v) for k, v in valid_state.items() if k != "authority_state_id"}
    assert e.canonical_bytes(valid_payload) == jcs_lf(valid_payload), "valid-state canonical bytes unexpectedly diverge"

    cases = []
    for label, number in [
        ("one-point-zero", 1.0),
        ("negative-zero", -0.0),
        ("small-exponent", 1e-6),
        ("large-integer-float", 1e20),
    ]:
        malformed = deepcopy(valid_state)
        malformed["future_numeric_field"] = number
        payload = {k: deepcopy(v) for k, v in malformed.items() if k != "authority_state_id"}
        python_bytes = e.canonical_bytes(payload)
        jcs_bytes = jcs_lf(payload)
        cases.append(
            {
                "id": label,
                "python": python_bytes.decode("utf-8"),
                "rfc8785": jcs_bytes.decode("utf-8"),
                "same": python_bytes == jcs_bytes,
            }
        )

    divergent = [case["id"] for case in cases if not case["same"]]
    result = {
        "status": "AMBIGUITY_DETECTED" if divergent else "NO_DIVERGENCE_OBSERVED",
        "valid_state_bytes_agree": True,
        "malformed_numeric_case_count": len(cases),
        "divergent_case_ids": divergent,
        "cases": cases,
        "interpretation": (
            "RC2 recomputed_authority_state_id covers canonicalizable invalid AuthorityState JSON, but the public canonicalization rules do not currently select a unique JSON-number serialization."
            if divergent
            else "No tested serializer divergence observed."
        ),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 1 if divergent else 0


if __name__ == "__main__":
    raise SystemExit(main())
