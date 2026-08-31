from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
CANDIDATE = HERE.parent / "contract-d-independent-authority-rc4" / "candidate"
sys.path.insert(0, str(CANDIDATE))

import contract_d_core as core
import contract_d_consume as consume_mod
import contract_d_validate as parser_mod

from variants import catch_only, iterative_container_patch

VALID = json.loads((CANDIDATE / "fixtures" / "valid.json").read_text())["fixtures"]
INVALID = json.loads((CANDIDATE / "fixtures" / "invalid.json").read_text())["fixtures"]
CASES = json.loads((CANDIDATE / "conformance-cases.json").read_text())["cases"]


def load(name: str) -> dict[str, Any]:
    return copy.deepcopy(VALID[name])


def expectation(d: dict[str, Any], op: str | None = None, params: Any = None):
    return consume_mod.ApplicabilityExpectation(
        copy.deepcopy(d["input_authority"]),
        copy.deepcopy(d["policy"]),
        copy.deepcopy(d["target"]),
        op or d.get("effect", {}).get("type", "knowledge.add_verified_tag"),
        params,
    )


def deep_metadata(base: dict[str, Any], depth: int) -> dict[str, Any]:
    d = copy.deepcopy(base)
    nested: Any = "leaf"
    for _ in range(depth):
        nested = [nested]
    d["metadata"]["diagnostics"] = {"deep": nested}
    return d


def observe(fn):
    try:
        value = fn()
        if isinstance(value, dict) and "outcome" in value:
            value = value["outcome"]
        return {"status": "ok", "value": value if isinstance(value, str) else type(value).__name__}
    except core.ContractDError as exc:
        return {"status": "controlled", "type": type(exc).__name__, "code": exc.code, "message": str(exc)[:240]}
    except BaseException as exc:
        return {"status": "escaped", "type": type(exc).__name__, "message": str(exc)[:240]}


def baseline_corpus() -> dict[str, Any]:
    valid = {}
    for name in sorted(VALID):
        d = load(name)
        valid[name] = {
            "canonical_hex": core.canonical_json_bytes(d).hex(),
            "identity": core.semantic_identity(d),
        }

    invalid = {}
    for name in sorted(INVALID):
        try:
            core.validate_decision(copy.deepcopy(INVALID[name]))
        except core.ContractDError as exc:
            invalid[name] = {"status": "rejected", "code": exc.code}
        else:
            invalid[name] = {"status": "accepted"}

    conformance = {}
    for case in CASES:
        d = load(case["decision_fixture"])
        e = case["expect"]
        got = consume_mod.consume(
            d,
            consume_mod.ApplicabilityExpectation(
                copy.deepcopy(e["input_authority"]),
                copy.deepcopy(e["policy"]),
                copy.deepcopy(e["target"]),
                e["requested_operation"],
                copy.deepcopy(e.get("effect_params")),
            ),
        )["outcome"]
        conformance[case["id"]] = got
    return {"valid": valid, "invalid": invalid, "conformance": conformance}


def iterative_corpus_equivalence(baseline: dict[str, Any]) -> dict[str, Any]:
    results: dict[str, Any] = {"valid": {}, "invalid": {}, "conformance": {}, "all_equal": True}
    with iterative_container_patch(core):
        for name in sorted(VALID):
            d = load(name)
            got_bytes = core.canonical_json_bytes(d).hex()
            got_id = core.semantic_identity(d)
            expected = baseline["valid"][name]
            equal = got_bytes == expected["canonical_hex"] and got_id == expected["identity"]
            results["valid"][name] = {"equal": equal, "identity": got_id}
            results["all_equal"] &= equal

        for name in sorted(INVALID):
            try:
                core.validate_decision(copy.deepcopy(INVALID[name]))
            except core.ContractDError as exc:
                got = {"status": "rejected", "code": exc.code}
            else:
                got = {"status": "accepted"}
            expected = baseline["invalid"][name]
            equal = got == expected
            results["invalid"][name] = {"equal": equal, "got": got, "expected": expected}
            results["all_equal"] &= equal

        for case in CASES:
            d = load(case["decision_fixture"])
            e = case["expect"]
            got = consume_mod.consume(
                d,
                consume_mod.ApplicabilityExpectation(
                    copy.deepcopy(e["input_authority"]),
                    copy.deepcopy(e["policy"]),
                    copy.deepcopy(e["target"]),
                    e["requested_operation"],
                    copy.deepcopy(e.get("effect_params")),
                ),
            )["outcome"]
            expected = baseline["conformance"][case["id"]]
            equal = got == expected
            results["conformance"][case["id"]] = {"equal": equal, "got": got, "expected": expected}
            results["all_equal"] &= equal

        # Metamorphic controls: cycle remains invalid; repeated acyclic alias remains valid.
        cyc = load("source-audit-clear.json")
        x: list[Any] = []
        x.append(x)
        cyc["metadata"]["diagnostics"] = {"cycle": x}
        results["cycle"] = observe(lambda: core.validate_decision(cyc))

        alias = load("source-audit-clear.json")
        leaf = {"k": [1, 2, 3]}
        alias["metadata"]["diagnostics"] = {"left": leaf, "right": leaf}
        results["shared_acyclic"] = observe(lambda: core.validate_decision(alias))

    return results


def depth_matrix() -> dict[str, Any]:
    base = load("source-audit-clear.json")
    result: dict[str, Any] = {"reference": {}, "catch_only": {}, "iterative": {}}

    for depth in (985, 990, 992, 995, 1200, 2000, 4000):
        d = deep_metadata(base, depth)
        exp = expectation(d)
        result["reference"][str(depth)] = {
            "validate": observe(lambda d=d: core.validate_decision(d)),
            "canonical": observe(lambda d=d: core.canonical_json_bytes(d)),
            "identity": observe(lambda d=d: core.semantic_identity(d)),
            "consume": observe(lambda d=d, exp=exp: consume_mod.consume(d, exp)),
        }

        result["catch_only"][str(depth)] = {}
        for label, fn in (
            ("validate", lambda d=d: core.validate_decision(d)),
            ("canonical", lambda d=d: core.canonical_json_bytes(d)),
            ("identity", lambda d=d: core.semantic_identity(d)),
            ("consume", lambda d=d, exp=exp: consume_mod.consume(d, exp)),
        ):
            status, value = catch_only(fn, core.ContractDError)
            result["catch_only"][str(depth)][label] = {
                "status": status,
                "value": value.get("outcome") if status == "ok" and isinstance(value, dict) and "outcome" in value else (
                    value if status == "ok" and isinstance(value, str) else type(value).__name__
                ),
                "code": getattr(value, "code", None),
            }

    with iterative_container_patch(core):
        for depth in (985, 990, 992, 995, 1200, 2000, 4000):
            d = deep_metadata(base, depth)
            exp = expectation(d)
            canonical = observe(lambda d=d: core.canonical_json_bytes(d))
            result["iterative"][str(depth)] = {
                "validate": observe(lambda d=d: core.validate_decision(d)),
                "canonical": canonical,
                "identity": observe(lambda d=d: core.semantic_identity(d)),
                "consume": observe(lambda d=d, exp=exp: consume_mod.consume(d, exp)),
            }
            if canonical["status"] == "ok":
                raw = core.canonical_json_bytes(d)
                result["iterative"][str(depth)]["raw_parse"] = observe(lambda raw=raw: parser_mod.parse_json_bytes(raw))

    return result


def main() -> int:
    outdir = HERE / "results"
    outdir.mkdir(exist_ok=True)
    baseline = baseline_corpus()
    equivalence = iterative_corpus_equivalence(baseline)
    depths = depth_matrix()

    payload = {
        "schema": "contract-d-finite-json-depth-hardening-v1",
        "python": sys.version,
        "baseline": baseline,
        "iterative_equivalence": equivalence,
        "depth_matrix": depths,
    }
    (outdir / "result.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    lines = [
        "# Contract D finite-JSON depth hardening result",
        "",
        f"Python: `{sys.version}`",
        "",
        f"Ordinary frozen corpus equivalence under iterative container handling: **{'PASS' if equivalence['all_equal'] else 'FAIL'}**",
        "",
        "| Depth | Reference validate | Reference identity | Reference consume | Catch-only consume | Iterative validate | Iterative canonical | Iterative identity | Iterative consume | Iterative raw parse |",
        "|---:|---|---|---|---|---|---|---|---|---|",
    ]
    for depth in (985, 990, 992, 995, 1200, 2000, 4000):
        key = str(depth)
        def fmt(cell):
            if cell["status"] == "ok": return str(cell.get("value", "OK"))
            if cell["status"] == "controlled": return "controlled:" + str(cell.get("code") or cell.get("type"))
            return "ESCAPED:" + str(cell.get("type"))
        r = depths["reference"][key]
        c = depths["catch_only"][key]["consume"]
        i = depths["iterative"][key]
        catch = c["status"] + (":" + c["code"] if c.get("code") else "")
        raw = i.get("raw_parse", {"status": "n/a"})
        raw_text = fmt(raw) if raw.get("status") != "n/a" else "n/a"
        lines.append(
            f"| {depth} | {fmt(r['validate'])} | {fmt(r['identity'])} | {fmt(r['consume'])} | {catch} | "
            f"{fmt(i['validate'])} | {fmt(i['canonical'])} | {fmt(i['identity'])} | {fmt(i['consume'])} | {raw_text} |"
        )

    lines += [
        "",
        "## Interpretation guardrail",
        "",
        "This experiment distinguishes repair mechanisms. It does not itself authorize changing the public contract or production code.",
        "A catch-only success demonstrates controlled failure is possible while preserving recursive acceptance limits.",
        "An iterative success demonstrates that the recursion cliff is not inherent to the frozen Decision semantics.",
        "Raw-byte parser limits are recorded separately from already-decoded host-value handling.",
    ]
    (outdir / "RESULT.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))

    # The experiment executable fails only if the iterative variant changes the ordinary frozen corpus.
    return 0 if equivalence["all_equal"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
