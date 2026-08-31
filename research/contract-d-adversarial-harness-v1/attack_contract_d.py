from __future__ import annotations

import argparse
import copy
import importlib
import json
import math
import sys
import traceback
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable


@dataclass
class Finding:
    attack_id: str
    category: str
    domain: str
    expected: str
    observed: str
    status: str
    promotion_blocker: bool
    detail: str = ""


class Harness:
    def __init__(self, target: Path):
        sys.path.insert(0, str(target))
        self.core = importlib.import_module("contract_d_core")
        self.parser = importlib.import_module("contract_d_validate")
        self.consumer = importlib.import_module("contract_d_consume")
        self.ContractDError = self.core.ContractDError
        self.valid = json.loads((target / "fixtures" / "valid.json").read_text())["fixtures"]
        self.findings: list[Finding] = []

    def load(self, name: str) -> dict[str, Any]:
        return copy.deepcopy(self.valid[name])

    def exp(self, d: dict[str, Any], op: str | None = None, params: Any = None):
        return self.consumer.ApplicabilityExpectation(
            copy.deepcopy(d["input_authority"]), copy.deepcopy(d["policy"]),
            copy.deepcopy(d["target"]), op or d.get("effect", {}).get("type", "knowledge.add_verified_tag"), params,
        )

    def record(self, attack_id: str, category: str, domain: str, expected: str,
               observed: str, passed: bool, blocker: bool = True, detail: str = "") -> None:
        self.findings.append(Finding(attack_id, category, domain, expected, observed,
                                     "PASS" if passed else "FINDING", (not passed) and blocker, detail))

    def rejected(self, attack_id: str, category: str, mutate: Callable[[dict[str, Any]], None],
                 domain: str = "declared-v1", blocker: bool = True) -> None:
        d = self.load("source-audit-clear.json")
        mutate(d)
        try:
            self.core.validate_decision(d)
        except self.ContractDError as exc:
            self.record(attack_id, category, domain, "controlled rejection", type(exc).__name__, True, blocker, str(exc))
        except BaseException as exc:
            self.record(attack_id, category, domain, "controlled rejection", type(exc).__name__, False, blocker,
                        "escaped exception: " + "".join(traceback.format_exception_only(type(exc), exc)).strip())
        else:
            self.record(attack_id, category, domain, "rejection", "accepted", False, blocker)

    def valid_case(self, attack_id: str, category: str, mutate: Callable[[dict[str, Any]], None],
                   domain: str = "declared-v1", blocker: bool = True) -> None:
        d = self.load("source-audit-clear.json")
        mutate(d)
        try:
            self.core.validate_decision(d); self.core.canonical_json_bytes(d); self.core.semantic_identity(d)
        except BaseException as exc:
            self.record(attack_id, category, domain, "valid/canonicalizable/identifiable", type(exc).__name__, False, blocker,
                        "".join(traceback.format_exception_only(type(exc), exc)).strip())
        else:
            self.record(attack_id, category, domain, "valid/canonicalizable/identifiable", "completed", True, blocker)

    def finite_json(self) -> None:
        self.rejected("json.host-set", "finite-json", lambda d: d["metadata"].__setitem__("diagnostics", {"x": {1, 2}}))
        self.rejected("json.non-string-key", "finite-json", lambda d: d["metadata"].__setitem__("diagnostics", {1: "x"}))
        self.rejected("json.nan", "finite-json", lambda d: d["metadata"].__setitem__("diagnostics", {"n": math.nan}))
        self.rejected("json.inf", "finite-json", lambda d: d["metadata"].__setitem__("diagnostics", {"n": math.inf}))

        def self_cycle(d):
            x: list[Any] = []; x.append(x); d["metadata"]["diagnostics"] = {"cycle": x}
        self.rejected("json.self-cycle", "finite-json", self_cycle)

        def mutual_cycle(d):
            a: list[Any] = []; b: list[Any] = [a]; a.append(b); d["metadata"]["diagnostics"] = {"cycle": a}
        self.rejected("json.mutual-cycle", "finite-json", mutual_cycle)

        def shared(d):
            leaf = {"v": [1, 2, 3]}; d["metadata"]["diagnostics"] = {"a": leaf, "b": leaf}
        self.valid_case("json.shared-acyclic", "finite-json", shared)

        for depth, blocker in ((64, True), (256, True), (768, False), (1200, False)):
            def deep(d, depth=depth):
                x: Any = "leaf"
                for _ in range(depth): x = [x]
                d["metadata"]["diagnostics"] = {"deep": x}
            self.valid_case(f"json.deep-{depth}", "resource-depth", deep,
                            "declared-v1" if blocker else "bounded-runtime-robustness", blocker)

        for attack_id, raw in (("json.invalid-utf8", b"\xff"), ("json.duplicate-key", b'{"a":1,"a":2}'),
                               ("json.nonfinite-token", b'{"a":NaN}')):
            try:
                self.parser.parse_json_bytes(raw)
            except self.ContractDError as exc:
                self.record(attack_id, "parser", "declared-v1", "controlled rejection", type(exc).__name__, True, True, str(exc))
            except BaseException as exc:
                self.record(attack_id, "parser", "declared-v1", "controlled rejection", type(exc).__name__, False, True, str(exc))
            else:
                self.record(attack_id, "parser", "declared-v1", "rejection", "accepted", False)

    def canonical_identity(self) -> None:
        d = self.load("source-audit-clear.json")
        try:
            a = self.core.canonical_json_bytes(d)
            b = self.core.canonical_json_bytes(self.parser.parse_json_bytes(a))
            self.record("canon.roundtrip", "canonicalization", "declared-v1", "byte stable", "same" if a == b else "different", a == b)
            noisy = json.dumps(d, ensure_ascii=False, indent=3).encode()
            c = self.core.canonical_json_bytes(self.parser.parse_json_bytes(noisy))
            self.record("canon.whitespace-keyorder", "canonicalization", "declared-v1", "same canonical bytes", "same" if a == c else "different", a == c)
        except BaseException as exc:
            self.record("canon.roundtrip", "canonicalization", "declared-v1", "stable", type(exc).__name__, False, True, str(exc))

        a = self.load("source-audit-clear.json"); b = self.load("source-audit-clear.json")
        a["metadata"]["diagnostics"] = {"u": "é"}; b["metadata"]["diagnostics"] = {"u": "e\u0301"}
        same = self.core.semantic_identity(a) == self.core.semantic_identity(b)
        self.record("identity.metadata-unicode", "identity", "declared-v1", "same identity", "same" if same else "different", same)

        base = self.load("source-audit-clear.json"); base_id = self.core.semantic_identity(base)
        for name, mutate in (
            ("upstream-id", lambda x: x["input_authority"].__setitem__("id", x["input_authority"]["id"] + "-x")),
            ("policy-version", lambda x: x["policy"].__setitem__("version", x["policy"]["version"] + "-x")),
            ("target-id", lambda x: x["target"].__setitem__("id", x["target"]["id"] + "-x")),
        ):
            x = self.load("source-audit-clear.json"); mutate(x)
            try:
                changed = self.core.semantic_identity(x) != base_id
                self.record(f"identity.{name}", "identity", "declared-v1", "identity changes", "changed" if changed else "same", changed)
            except self.ContractDError:
                self.record(f"identity.{name}", "identity", "declared-v1", "identity changes or rejects", "rejected", True)

    def applicability(self) -> None:
        clear = self.load("source-audit-clear.json"); hold = self.load("completed-hold.json")
        for label, d in (("clear", clear), ("hold", hold)):
            out = self.consumer.consume(d, self.exp(d, op="task.dispatch"))["outcome"]
            self.record(f"apply.{label}.wrong-op", "applicability", "declared-v1", "not_applicable", out, out == "not_applicable")

        obj = self.load("source-audit-object-scope-clear.json")
        for label, params, wanted in (("absent", None, "candidate_for_authorization"), ("empty", {}, "candidate_for_authorization"),
                                      ("claim", {"scope": "claim"}, "not_applicable"), ("object", {"scope": "object"}, "candidate_for_authorization")):
            out = self.consumer.consume(obj, self.exp(obj, params=params))["outcome"]
            self.record(f"apply.params.{label}", "applicability", "declared-v1", wanted, out, out == wanted)

        for section, key in (("input_authority", "id"), ("policy", "version"), ("target", "id")):
            e = self.exp(clear); container = getattr(e, section if section != "input_authority" else "input_authority")
            container[key] = str(container[key]) + "-x"
            out = self.consumer.consume(clear, e)["outcome"]
            self.record(f"replay.{section}.{key}", "replay-substitution", "declared-v1", "not_applicable", out, out == "not_applicable")

        changes = [
            ("upstream", lambda e: e.input_authority.__setitem__("id", e.input_authority["id"] + "-x")),
            ("policy", lambda e: e.policy.__setitem__("version", e.policy["version"] + "-x")),
            ("target", lambda e: e.target.__setitem__("id", e.target["id"] + "-x")),
            ("operation", lambda e: setattr(e, "requested_operation", "task.dispatch")),
        ]
        for i in range(len(changes)):
            for j in range(i + 1, len(changes)):
                e = self.exp(clear); changes[i][1](e); changes[j][1](e)
                out = self.consumer.consume(clear, e)["outcome"]
                name = changes[i][0] + "+" + changes[j][0]
                self.record(f"combo.{name}", "combinatorial-applicability", "declared-v1", "not_applicable", out, out == "not_applicable")

    def unknowns_firewall(self) -> None:
        self.rejected("unknown.contract-version", "future-unknown", lambda d: d.__setitem__("contract_d_version", "999.0.0"))
        self.rejected("unknown.effect-param", "future-unknown", lambda d: d["effect"].setdefault("params", {}).__setitem__("future_param", True))
        self.rejected("firewall.authorization-top-level", "authorization-firewall", lambda d: d.__setitem__("authorization", {"actor": "root"}))

        a = self.load("source-audit-clear.json"); b = self.load("source-audit-clear.json")
        b["metadata"]["diagnostics"] = {"actor": "root", "approval": True, "delegation": "all"}
        same = self.core.semantic_identity(a) == self.core.semantic_identity(b)
        self.record("firewall.authorization-metadata", "authorization-firewall", "declared-v1", "identity invariant", "same" if same else "different", same)

    def seeded_mutants(self) -> None:
        def mutant(name: str, caught: bool, observed: str):
            self.record("mutant." + name, "seeded-mutant", "evaluator-assurance", "weak strategy contradicted", observed, caught)

        clear = self.load("source-audit-clear.json"); hold = self.load("completed-hold.json"); failed = self.load("evaluation-failed.json")
        mutant("disposition-only", self.consumer.consume(clear, self.exp(clear, op="task.dispatch"))["outcome"] == "not_applicable", "operation mismatch checked")
        e = self.exp(clear); e.target["kind"] = "task"; out = self.consumer.consume(clear, e)["outcome"]
        mutant("target-id-only", out == "not_applicable", out); mutant("target-ignore-kind-content", out == "not_applicable", out)
        out = self.consumer.consume(failed, self.exp(failed))["outcome"]; mutant("hold-failure-collapse", out == "evaluation_failed", out)
        d = self.load("source-audit-clear.json"); d["metadata"]["explanation"] = "task.dispatch"; out = self.consumer.consume(d, self.exp(d, op="task.dispatch"))["outcome"]
        mutant("reason-text-effect", out == "not_applicable", out)
        d = self.load("source-audit-clear.json"); d["effect"]["type"] = "future.effect"
        try: self.core.validate_decision(d); caught = False
        except self.ContractDError: caught = True
        mutant("unknown-effect-acceptance", caught, "rejected" if caught else "accepted")
        e = self.exp(clear); e.policy["version"] += "-x"; out = self.consumer.consume(clear, e)["outcome"]; mutant("policy-blind", out == "not_applicable", out)
        e = self.exp(clear); e.input_authority["id"] += "-x"; out = self.consumer.consume(clear, e)["outcome"]; mutant("upstream-blind", out == "not_applicable", out)
        obj = self.load("source-audit-object-scope-clear.json"); out = self.consumer.consume(obj, self.exp(obj, params=None))["outcome"]
        mutant("omitted-params-as-defaults", out == "candidate_for_authorization", out)
        out = self.consumer.consume(hold, self.exp(hold, op="task.dispatch"))["outcome"]; mutant("hold-before-applicability", out == "not_applicable", out)
        d = self.load("source-audit-clear.json"); d["metadata"]["diagnostics"] = {"bad": {1, 2}}
        try: self.core.validate_decision(d); caught = False
        except self.ContractDError: caught = True
        mutant("host-only-diagnostics", caught, "rejected" if caught else "accepted")
        d = self.load("source-audit-clear.json"); cyc: list[Any] = []; cyc.append(cyc); d["metadata"]["diagnostics"] = {"cycle": cyc}
        try: self.core.validate_decision(d); caught = False; obs = "accepted"
        except self.ContractDError: caught = True; obs = "controlled rejection"
        except BaseException as exc: caught = False; obs = type(exc).__name__
        mutant("cyclic-container", caught, obs)
        a = self.load("source-audit-clear.json"); b = self.load("source-audit-clear.json"); b["metadata"]["diagnostics"] = {"approval": True}
        same = self.core.semantic_identity(a) == self.core.semantic_identity(b); mutant("authorization-contaminated-identity", same, "same" if same else "different")

    def run(self) -> list[Finding]:
        self.finite_json(); self.canonical_identity(); self.applicability(); self.unknowns_firewall(); self.seeded_mutants()
        return self.findings


def write_reports(findings: list[Finding], outdir: Path) -> dict[str, Any]:
    outdir.mkdir(parents=True, exist_ok=True)
    payload = {"schema": "contract-d-adversarial-report-v1", "total": len(findings),
               "passes": sum(f.status == "PASS" for f in findings), "findings": sum(f.status == "FINDING" for f in findings),
               "promotion_blockers": sum(f.promotion_blocker for f in findings), "items": [asdict(f) for f in findings]}
    (outdir / "report.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    lines = ["# Contract D adversarial harness report", "", f"- total attacks: **{payload['total']}**",
             f"- passes: **{payload['passes']}**", f"- findings: **{payload['findings']}**",
             f"- promotion blockers: **{payload['promotion_blockers']}**", "",
             "| Attack | Category | Domain | Status | Blocker | Observed |", "|---|---|---|---|---:|---|"]
    for f in findings:
        lines.append(f"| `{f.attack_id}` | {f.category} | {f.domain} | {f.status} | {'YES' if f.promotion_blocker else 'NO'} | {f.observed} |")
    lines += ["", "## Finding details", ""]
    for f in findings:
        if f.status == "FINDING":
            lines += [f"### {f.attack_id}", "", f"Expected: `{f.expected}`  ", f"Observed: `{f.observed}`  ",
                      f"Domain: `{f.domain}`  ", f"Promotion blocker: `{'YES' if f.promotion_blocker else 'NO'}`", ""]
            if f.detail: lines += ["```text", f.detail[:3000], "```", ""]
    (outdir / "report.md").write_text("\n".join(lines) + "\n")
    return payload


def main() -> int:
    p = argparse.ArgumentParser(); p.add_argument("--target", type=Path, required=True); p.add_argument("--report-dir", type=Path, default=Path("attack-report")); p.add_argument("--gate", action="store_true")
    args = p.parse_args(); payload = write_reports(Harness(args.target).run(), args.report_dir)
    print(json.dumps({k: payload[k] for k in ("total", "findings", "promotion_blockers")}, sort_keys=True))
    return 2 if args.gate and payload["promotion_blockers"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
