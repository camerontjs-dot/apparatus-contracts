from __future__ import annotations

import argparse
import copy
import importlib
import json
import sys
from pathlib import Path
from typing import Any

DEPTHS = (900, 950, 975, 985, 990, 992, 994, 995, 996, 1000, 1024, 1200, 1500)


def observe(fn):
    try:
        value = fn()
        if isinstance(value, dict) and "outcome" in value:
            value = value["outcome"]
        return {"status": "ok", "value": value if isinstance(value, str) else type(value).__name__}
    except BaseException as exc:
        return {"status": "exception", "type": type(exc).__name__, "message": str(exc)[:300]}


def deep_decision(base: dict[str, Any], depth: int) -> dict[str, Any]:
    decision = copy.deepcopy(base)
    nested: Any = "leaf"
    for _ in range(depth):
        nested = [nested]
    decision["metadata"]["diagnostics"] = {"deep": nested}
    return decision


def run_reference(target: Path) -> list[dict[str, Any]]:
    sys.path.insert(0, str(target))
    core = importlib.import_module("contract_d_core")
    consume_mod = importlib.import_module("contract_d_consume")
    valid = json.loads((target / "fixtures" / "valid.json").read_text())["fixtures"]
    base = valid["source-audit-clear.json"]
    rows = []
    for depth in DEPTHS:
        d = deep_decision(base, depth)
        exp = consume_mod.ApplicabilityExpectation(
            copy.deepcopy(d["input_authority"]), copy.deepcopy(d["policy"]), copy.deepcopy(d["target"]),
            d["effect"]["type"], None,
        )
        rows.append({
            "depth": depth,
            "validate": observe(lambda d=d: core.validate_decision(d)),
            "canonical": observe(lambda d=d: core.canonical_json_bytes(d)),
            "identity": observe(lambda d=d: core.semantic_identity(d)),
            "consume": observe(lambda d=d, e=exp: consume_mod.consume(d, e)),
        })
    return rows


def run_independent(target: Path, fixture_path: Path) -> list[dict[str, Any]]:
    sys.path.insert(0, str(target))
    impl = importlib.import_module("contract_d_independent")
    valid = json.loads(fixture_path.read_text())["fixtures"]
    base = valid["source-audit-clear.json"]
    rows = []
    for depth in DEPTHS:
        d = deep_decision(base, depth)
        rows.append({
            "depth": depth,
            "validate": observe(lambda d=d: impl.validate_decision(d)),
            "canonical": observe(lambda d=d: impl.canonical_json_bytes(d)),
            "identity": observe(lambda d=d: impl.semantic_identity(d)),
            "consume": observe(lambda d=d: impl.consume(
                d,
                expected_input_authority=copy.deepcopy(d["input_authority"]),
                expected_policy=copy.deepcopy(d["policy"]),
                expected_target=copy.deepcopy(d["target"]),
                requested_operation=d["effect"]["type"],
                requested_effect_params=None,
            )),
        })
    return rows


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--kind", choices=("reference", "independent"), required=True)
    p.add_argument("--target", type=Path, required=True)
    p.add_argument("--fixture", type=Path)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()

    if args.kind == "reference":
        rows = run_reference(args.target)
    else:
        if args.fixture is None:
            p.error("--fixture required for independent")
        rows = run_independent(args.target, args.fixture)

    payload = {
        "schema": "contract-d-depth-implementation-probe-v1",
        "implementation": args.kind,
        "python": sys.version,
        "rows": rows,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
