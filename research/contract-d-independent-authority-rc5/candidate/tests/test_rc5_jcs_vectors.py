from __future__ import annotations

import copy
import json
import struct
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

from contract_d_core import ContractDError, canonical_json_bytes
from contract_d_validate import parse_json_bytes, require_canonical_bytes

VALID = json.loads((HERE / "fixtures" / "valid.json").read_text())["fixtures"]


def f64(hex_bits: str) -> float:
    return struct.unpack(">d", bytes.fromhex(hex_bits))[0]


@pytest.mark.parametrize(
    ("bits", "expected"),
    [
        ("0000000000000000", "0"),
        ("8000000000000000", "0"),
        ("0000000000000001", "5e-324"),
        ("8000000000000001", "-5e-324"),
        ("7fefffffffffffff", "1.7976931348623157e+308"),
        ("ffefffffffffffff", "-1.7976931348623157e+308"),
        ("4340000000000000", "9007199254740992"),
        ("c340000000000000", "-9007199254740992"),
        ("4430000000000000", "295147905179352830000"),
        ("44b52d02c7e14af5", "9.999999999999997e+22"),
        ("44b52d02c7e14af6", "1e+23"),
        ("44b52d02c7e14af7", "1.0000000000000001e+23"),
        ("444b1ae4d6e2ef4e", "999999999999999700000"),
        ("444b1ae4d6e2ef4f", "999999999999999900000"),
        ("444b1ae4d6e2ef50", "1e+21"),
        ("3eb0c6f7a0b5ed8c", "9.999999999999997e-7"),
        ("3eb0c6f7a0b5ed8d", "0.000001"),
        ("41b3de4355555553", "333333333.3333332"),
        ("41b3de4355555554", "333333333.33333325"),
        ("41b3de4355555555", "333333333.3333333"),
        ("41b3de4355555556", "333333333.3333334"),
        ("41b3de4355555557", "333333333.33333343"),
        ("becbf647612f3696", "-0.0000033333333333333333"),
        ("43143ff3c1cb0959", "1424953923781206.2"),
    ],
)
def test_rfc8785_appendix_b_number_samples(bits, expected):
    assert canonical_json_bytes({"n": f64(bits)}) == (f'{{"n":{expected}}}\n').encode()


@pytest.mark.parametrize("number", [1e20, float(2**53), float(2**68)])
def test_integral_looking_binary64_values_roundtrip_through_contract_bytes(number):
    d = copy.deepcopy(VALID["source-audit-clear.json"])
    d["metadata"]["diagnostics"] = {"number": number}
    canonical = canonical_json_bytes(d)
    parsed = require_canonical_bytes(canonical)
    assert canonical_json_bytes(parsed) == canonical


def test_precision_losing_integer_token_is_rejected_at_byte_ingress():
    d = copy.deepcopy(VALID["source-audit-clear.json"])
    d["metadata"]["diagnostics"] = {"number": 9007199254740993}
    raw = json.dumps(d, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    with pytest.raises(ContractDError, match="non_interoperable_integer"):
        parse_json_bytes(raw)


def test_exact_binary64_integer_token_outside_safe_host_int_range_is_accepted():
    d = copy.deepcopy(VALID["source-audit-clear.json"])
    d["metadata"]["diagnostics"] = {"number": 9007199254740992}
    raw = json.dumps(d, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    parsed = parse_json_bytes(raw)
    assert parsed["metadata"]["diagnostics"]["number"] == float(9007199254740992)
