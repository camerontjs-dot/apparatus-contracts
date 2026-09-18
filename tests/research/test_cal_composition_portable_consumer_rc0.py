from __future__ import annotations

import hashlib
import json
from pathlib import Path

from research.cal_composition_portable_consumer_rc0.consumer import (
    BOUND_RECEIPT_FIELDS,
    mutated_receipts,
    verify_payload,
    verify_vector,
)

ROOT = Path(__file__).resolve().parents[2]
VECTOR_PATH = ROOT / "research" / "cal_composition_portable_consumer_rc0" / "vectors.json"
EXPECTED_VECTOR_SHA256 = (
    "11818e585780ff70b5bf00fe519463fb487dba9d191abb7810946ad43afebf39"
)


def _payload() -> dict[str, object]:
    return json.loads(VECTOR_PATH.read_text(encoding="utf-8"))


def test_exact_frozen_vector_bytes() -> None:
    assert hashlib.sha256(VECTOR_PATH.read_bytes()).hexdigest() == EXPECTED_VECTOR_SHA256


def test_independent_consumer_accepts_all_frozen_vectors() -> None:
    verify_payload(_payload())


def test_every_bound_receipt_field_is_mutation_sensitive() -> None:
    payload = _payload()
    vectors = payload["vectors"]
    assert isinstance(vectors, list)
    observed_fields: set[str] = set()
    for vector in vectors:
        assert isinstance(vector, dict)
        request = vector["request"]
        receipt = vector["expected_receipt"]
        assert isinstance(request, dict)
        assert isinstance(receipt, dict)
        mutations = mutated_receipts(receipt)
        assert len(mutations) == len(BOUND_RECEIPT_FIELDS)
        for field, mutated in zip(BOUND_RECEIPT_FIELDS, mutations, strict=True):
            observed_fields.add(field)
            assert not verify_vector(
                {
                    "vector_id": vector["vector_id"],
                    "request": request,
                    "expected_receipt": mutated,
                }
            )
    assert observed_fields == set(BOUND_RECEIPT_FIELDS)


def test_consumer_has_no_cal_import_dependency() -> None:
    consumer_path = (
        ROOT / "research" / "cal_composition_portable_consumer_rc0" / "consumer.py"
    )
    source = consumer_path.read_text(encoding="utf-8")
    assert "claim_audit_lab" not in source
    assert "composition_provenance_carrier_rc0" not in source
