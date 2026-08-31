from __future__ import annotations

import argparse
import copy
import importlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


NODE_CANON = r'''
const fs = require('fs');
const value = JSON.parse(fs.readFileSync(0, 'utf8'));
function sortValue(v) {
  if (Array.isArray(v)) return v.map(sortValue);
  if (v !== null && typeof v === 'object') {
    const out = {};
    for (const k of Object.keys(v).sort()) out[k] = sortValue(v[k]);
    return out;
  }
  return v;
}
process.stdout.write(JSON.stringify(sortValue(value)) + '\n');
'''


def capture(fn):
    try:
        value = fn()
    except BaseException as exc:
        return {"status": "exception", "type": type(exc).__name__, "message": str(exc)}
    if isinstance(value, bytes):
        try:
            shown = value.decode("utf-8")
        except UnicodeDecodeError:
            shown = value.hex()
        return {"status": "ok", "value": shown}
    if isinstance(value, dict) and "outcome" in value:
        return {"status": "ok", "value": value["outcome"]}
    return {"status": "ok", "value": type(value).__name__}


def node_canonical(raw: bytes) -> dict[str, Any]:
    proc = subprocess.run(
        ["node", "-e", NODE_CANON],
        input=raw,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode:
        return {
            "status": "exception",
            "type": "NodeError",
            "message": proc.stderr.decode("utf-8", "replace").strip(),
        }
    return {"status": "ok", "value": proc.stdout.decode("utf-8")}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--report-dir", type=Path, required=True)
    args = parser.parse_args()

    sys.path.insert(0, str(args.target))
    core = importlib.import_module("contract_d_core")
    validator = importlib.import_module("contract_d_validate")
    consumer = importlib.import_module("contract_d_consume")
    fixtures = json.loads((args.target / "fixtures" / "valid.json").read_text(encoding="utf-8"))["fixtures"]
    base = copy.deepcopy(fixtures["source-audit-clear.json"])

    expected = consumer.ApplicabilityExpectation(
        copy.deepcopy(base["input_authority"]),
        copy.deepcopy(base["policy"]),
        copy.deepcopy(base["target"]),
        base["effect"]["type"],
        None,
    )

    # A syntactically valid UTF-8 JSON text containing an escaped unpaired surrogate.
    # The decoded host string cannot itself be encoded as valid UTF-8.
    surrogate = copy.deepcopy(base)
    surrogate.setdefault("metadata", {})["diagnostics"] = {"surrogate": "\ud800"}
    surrogate_raw = json.dumps(surrogate, ensure_ascii=True, separators=(",", ":")).encode("ascii")
    parsed_holder: dict[str, Any] = {}

    def parse_surrogate():
        parsed_holder["value"] = validator.parse_json_bytes(surrogate_raw)
        return parsed_holder["value"]

    surrogate_result = {
        "raw_is_utf8": True,
        "parse": capture(parse_surrogate),
    }
    parsed = parsed_holder.get("value")
    if parsed is not None:
        surrogate_result.update(
            validate=capture(lambda: core.validate_decision(parsed)),
            canonical=capture(lambda: core.canonical_json_bytes(parsed)),
            identity=capture(lambda: core.semantic_identity(parsed)),
            consume=capture(lambda: consumer.consume(parsed, expected)),
        )

    numeric_cases = [
        ("negative-zero", -0.0),
        ("one-e-minus-7", 1e-7),
        ("one-e-minus-6", 1e-6),
        ("one-e-20", 1e20),
        ("one-e-21", 1e21),
        ("precision-edge-float", 333333333.33333329),
        ("safe-int-max", 9007199254740991),
        ("unsafe-int-plus-one", 9007199254740992),
        ("unsafe-int-plus-two", 9007199254740993),
    ]
    numeric_rows: list[dict[str, Any]] = []
    for name, number in numeric_cases:
        d = copy.deepcopy(base)
        d.setdefault("metadata", {})["diagnostics"] = {"number": number}
        raw = json.dumps(d, ensure_ascii=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
        py = capture(lambda d=d: core.canonical_json_bytes(d))
        node = node_canonical(raw)
        numeric_rows.append(
            {
                "case": name,
                "input_number_repr": repr(number),
                "python": py,
                "node": node,
                "same": py.get("status") == "ok" and node.get("status") == "ok" and py.get("value") == node.get("value"),
            }
        )

    # Object-key ordering can differ if "lexicographic" is implemented using
    # language-native string ordering. Python compares Unicode code points;
    # JavaScript Array.sort compares UTF-16 code units.
    key_order = copy.deepcopy(base)
    key_order.setdefault("metadata", {})["diagnostics"] = {"\uffff": 1, "\U0001f4a9": 2}
    key_raw = json.dumps(key_order, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")
    py_keys = capture(lambda: core.canonical_json_bytes(key_order))
    node_keys = node_canonical(key_raw)
    key_result = {
        "python": py_keys,
        "node": node_keys,
        "same": py_keys.get("status") == "ok" and node_keys.get("status") == "ok" and py_keys.get("value") == node_keys.get("value"),
    }

    payload = {
        "schema": "contract-d-unicode-numeric-probe-v1",
        "surrogate": surrogate_result,
        "numeric": numeric_rows,
        "non_bmp_key_order": key_result,
    }
    args.report_dir.mkdir(parents=True, exist_ok=True)
    out = args.report_dir / "unicode-numeric.json"
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=True, sort_keys=True) + "\n", encoding="utf-8")

    md = [
        "# Unicode and numeric canonicalization probe",
        "",
        "## Escaped unpaired surrogate",
        "",
        f"- parse: `{surrogate_result['parse']}`",
    ]
    for key in ("validate", "canonical", "identity", "consume"):
        if key in surrogate_result:
            md.append(f"- {key}: `{surrogate_result[key]}`")
    md.extend(["", "## Python vs Node numeric canonical bytes", "", "| Case | Same bytes |", "|---|---:|"])
    md.extend(f"| {row['case']} | {'YES' if row['same'] else 'NO'} |" for row in numeric_rows)
    md.extend([
        "",
        "## Non-BMP key-order probe",
        "",
        f"Same bytes: **{'YES' if key_result['same'] else 'NO'}**",
        "",
    ])
    (args.report_dir / "unicode-numeric.md").write_text("\n".join(md), encoding="utf-8")

    print(json.dumps({
        "surrogate_parse": surrogate_result["parse"]["status"],
        "surrogate_canonical": surrogate_result.get("canonical", {}).get("status"),
        "numeric_mismatches": sum(not row["same"] for row in numeric_rows),
        "key_order_same": key_result["same"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
