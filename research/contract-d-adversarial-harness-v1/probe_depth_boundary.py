from __future__ import annotations

import argparse
import copy
import importlib
import json
import sys
from pathlib import Path
from typing import Any


def outcome(fn):
    try:
        fn()
        return {"status": "ok"}
    except BaseException as exc:
        return {"status": "exception", "type": type(exc).__name__, "message": str(exc)[:300]}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--target", type=Path, required=True)
    p.add_argument("--report-dir", type=Path, required=True)
    args = p.parse_args()

    sys.path.insert(0, str(args.target))
    core = importlib.import_module("contract_d_core")
    parser = importlib.import_module("contract_d_validate")
    consume_mod = importlib.import_module("contract_d_consume")
    fixtures = json.loads((args.target / "fixtures" / "valid.json").read_text())["fixtures"]
    base = fixtures["source-audit-clear.json"]

    rows = []
    for depth in (768, 800, 850, 900, 925, 950, 975, 990, 995, 1000, 1005, 1024, 1100, 1200):
        decision = copy.deepcopy(base)
        nested: Any = "leaf"
        for _ in range(depth):
            nested = [nested]
        decision["metadata"]["diagnostics"] = {"deep": nested}

        expectation = consume_mod.ApplicabilityExpectation(
            copy.deepcopy(decision["input_authority"]),
            copy.deepcopy(decision["policy"]),
            copy.deepcopy(decision["target"]),
            decision["effect"]["type"],
            None,
        )

        raw_array = ("[" * depth + "0" + "]" * depth).encode("ascii")
        rows.append({
            "depth": depth,
            "parse_raw_array": outcome(lambda raw=raw_array: parser.parse_json_bytes(raw)),
            "validate_decoded_decision": outcome(lambda d=decision: core.validate_decision(d)),
            "canonicalize_decision": outcome(lambda d=decision: core.canonical_json_bytes(d)),
            "semantic_identity": outcome(lambda d=decision: core.semantic_identity(d)),
            "consume": outcome(lambda d=decision, e=expectation: consume_mod.consume(d, e)),
        })

    args.report_dir.mkdir(parents=True, exist_ok=True)
    payload = {"schema": "contract-d-depth-boundary-v1", "rows": rows}
    (args.report_dir / "depth-boundary.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    lines = [
        "# Contract D finite-JSON depth boundary probe",
        "",
        "This probe is diagnostic. It does not pre-classify escaped recursion as semantic or resource-only.",
        "",
        "| Depth | Raw parse | Validate decoded | Canonicalize | Identity | Consume |",
        "|---:|---|---|---|---|---|",
    ]
    for r in rows:
        def fmt(k):
            x = r[k]
            return "OK" if x["status"] == "ok" else x.get("type", "exception")
        lines.append(
            f"| {r['depth']} | {fmt('parse_raw_array')} | {fmt('validate_decoded_decision')} | "
            f"{fmt('canonicalize_decision')} | {fmt('semantic_identity')} | {fmt('consume')} |"
        )
    (args.report_dir / "depth-boundary.md").write_text("\n".join(lines) + "\n")
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
