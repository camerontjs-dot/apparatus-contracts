from __future__ import annotations

import argparse
import copy
import json
import random
import subprocess
from dataclasses import replace
from pathlib import Path
from typing import Any

from attack_contract_d import Finding, Harness, write_reports


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


def node_canonical(value: Any) -> bytes:
    raw = json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")
    proc = subprocess.run(
        ["node", "-e", NODE_CANON],
        input=raw,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode:
        raise RuntimeError(proc.stderr.decode("utf-8", "replace"))
    return proc.stdout


def nested_lists(count: int) -> Any:
    value: Any = "leaf"
    for _ in range(count):
        value = [value]
    return value


class RC5Harness(Harness):
    def applicability(self) -> None:
        clear = self.load("source-audit-clear.json")
        hold = self.load("completed-hold.json")

        for label, decision in (("clear", clear), ("hold", hold)):
            out = self.consumer.consume(decision, self.exp(decision, op="task.dispatch"))["outcome"]
            self.record(
                f"apply.{label}.wrong-op",
                "applicability",
                "declared-v1",
                "not_applicable",
                out,
                out == "not_applicable",
            )

        obj = self.load("source-audit-object-scope-clear.json")
        cases = (
            ("absent", None, "candidate_for_authorization"),
            ("empty", {}, "candidate_for_authorization"),
            ("claim", {"scope": "claim"}, "not_applicable"),
            ("object", {"scope": "object"}, "candidate_for_authorization"),
        )
        for label, params, wanted in cases:
            out = self.consumer.consume(obj, self.exp(obj, params=params))["outcome"]
            self.record(
                f"apply.params.{label}",
                "applicability",
                "declared-v1",
                wanted,
                out,
                out == wanted,
            )

        for section, key in (("input_authority", "id"), ("policy", "version"), ("target", "id")):
            expectation = self.exp(clear)
            container = getattr(expectation, section)
            container[key] = str(container[key]) + "-x"
            out = self.consumer.consume(clear, expectation)["outcome"]
            self.record(
                f"replay.{section}.{key}",
                "replay-substitution",
                "declared-v1",
                "not_applicable",
                out,
                out == "not_applicable",
            )

        def upstream(e):
            e.input_authority["id"] += "-x"
            return e

        def policy(e):
            e.policy["version"] += "-x"
            return e

        def target(e):
            e.target["id"] += "-x"
            return e

        def operation(e):
            return replace(e, requested_operation="task.dispatch")

        changes = (("upstream", upstream), ("policy", policy), ("target", target), ("operation", operation))
        for i in range(len(changes)):
            for j in range(i + 1, len(changes)):
                expectation = changes[i][1](self.exp(clear))
                expectation = changes[j][1](expectation)
                out = self.consumer.consume(clear, expectation)["outcome"]
                name = changes[i][0] + "+" + changes[j][0]
                self.record(
                    f"combo.{name}",
                    "combinatorial-applicability",
                    "declared-v1",
                    "not_applicable",
                    out,
                    out == "not_applicable",
                )

    def finite_json(self) -> None:
        super().finite_json()
        # RC5 deliberately rejects values beyond the deterministic depth bound.
        for depth in (129, 256, 768, 1200):
            d = self.load("source-audit-clear.json")
            d["metadata"]["diagnostics"] = {"deep": nested_lists(depth)}
            try:
                self.core.validate_decision(d)
            except self.ContractDError as exc:
                passed = exc.code == "json_depth_exceeded"
                self.record(
                    f"rc5.depth-{depth}",
                    "resource-depth",
                    "declared-v1",
                    "controlled json_depth_exceeded",
                    exc.code,
                    passed,
                    True,
                    str(exc),
                )
            except BaseException as exc:
                self.record(
                    f"rc5.depth-{depth}",
                    "resource-depth",
                    "declared-v1",
                    "controlled json_depth_exceeded",
                    type(exc).__name__,
                    False,
                    True,
                    f"escaped exception: {exc}",
                )
            else:
                self.record(
                    f"rc5.depth-{depth}",
                    "resource-depth",
                    "declared-v1",
                    "controlled json_depth_exceeded",
                    "accepted",
                    False,
                )

    def rc5_unicode_numbers(self) -> None:
        base = self.load("source-audit-clear.json")

        surrogate = copy.deepcopy(base)
        surrogate["metadata"]["diagnostics"] = {"bad": "\ud800"}
        raw = json.dumps(surrogate, ensure_ascii=True, separators=(",", ":")).encode("ascii")
        try:
            self.parser.parse_json_bytes(raw)
        except self.ContractDError as exc:
            self.record(
                "rc5.unpaired-surrogate",
                "unicode-scalar",
                "declared-v1",
                "invalid_unicode_scalar",
                exc.code,
                exc.code == "invalid_unicode_scalar",
            )
        except BaseException as exc:
            self.record(
                "rc5.unpaired-surrogate",
                "unicode-scalar",
                "declared-v1",
                "controlled rejection",
                type(exc).__name__,
                False,
                True,
                str(exc),
            )
        else:
            self.record(
                "rc5.unpaired-surrogate",
                "unicode-scalar",
                "declared-v1",
                "rejection",
                "accepted",
                False,
            )

        unsafe = copy.deepcopy(base)
        unsafe["metadata"]["diagnostics"] = {"n": 9007199254740992}
        try:
            self.core.validate_decision(unsafe)
        except self.ContractDError as exc:
            self.record(
                "rc5.unsafe-integer",
                "number-domain",
                "declared-v1",
                "non_interoperable_integer",
                exc.code,
                exc.code == "non_interoperable_integer",
            )
        else:
            self.record("rc5.unsafe-integer", "number-domain", "declared-v1", "rejection", "accepted", False)

        canonical_cases = (
            ("negative-zero", -0.0),
            ("one-e-minus-7", 1e-7),
            ("one-e-minus-6", 1e-6),
            ("one-e20", 1e20),
            ("one-e21", 1e21),
            ("precision-edge", 333333333.33333329),
            ("safe-int-max", 9007199254740991),
        )
        for label, number in canonical_cases:
            value = {"n": number}
            try:
                py = self.core.canonical_json_bytes(value)
                js = node_canonical(value)
                same = py == js
                self.record(
                    f"rc5.jcs-number.{label}",
                    "cross-language-canonicalization",
                    "declared-v1",
                    "Python == ECMAScript bytes",
                    "same" if same else f"different: py={py!r} node={js!r}",
                    same,
                )
            except BaseException as exc:
                self.record(
                    f"rc5.jcs-number.{label}",
                    "cross-language-canonicalization",
                    "declared-v1",
                    "matching bytes",
                    type(exc).__name__,
                    False,
                    True,
                    str(exc),
                )

        key_value = {"\uffff": 1, "\U0001f4a9": 2}
        try:
            py = self.core.canonical_json_bytes(key_value)
            js = node_canonical(key_value)
            same = py == js
            self.record(
                "rc5.jcs-nonbmp-key-order",
                "cross-language-canonicalization",
                "declared-v1",
                "Python == ECMAScript bytes",
                "same" if same else f"different: py={py!r} node={js!r}",
                same,
            )
        except BaseException as exc:
            self.record(
                "rc5.jcs-nonbmp-key-order",
                "cross-language-canonicalization",
                "declared-v1",
                "matching bytes",
                type(exc).__name__,
                False,
                True,
                str(exc),
            )

    def generated_jcs(self) -> None:
        rng = random.Random(8785)
        atoms: list[Any] = [None, True, False, "alpha", "é", "💩", -0.0, 0, 1, -1, 1e-7, 1e-6, 1e20, 1e21]
        key_pool = ["a", "z", "é", "e\u0301", "\uffff", "\U0001f4a9"]
        mismatches = []
        for i in range(100):
            keys = rng.sample(key_pool, rng.randint(1, 4))
            value: dict[str, Any] = {}
            for key in keys:
                atom = copy.deepcopy(rng.choice(atoms))
                if rng.random() < 0.25:
                    atom = [atom, copy.deepcopy(rng.choice(atoms))]
                value[key] = atom
            try:
                py = self.core.canonical_json_bytes(value)
                js = node_canonical(value)
            except BaseException as exc:
                mismatches.append(f"case {i} exception {type(exc).__name__}: {exc}")
                continue
            if py != js:
                mismatches.append(f"case {i}: py={py!r} node={js!r} value={value!r}")
        self.record(
            "rc5.generated-jcs-100",
            "cross-language-canonicalization",
            "declared-v1",
            "100/100 match",
            "100/100 match" if not mismatches else f"{len(mismatches)} mismatches",
            not mismatches,
            True,
            "\n".join(mismatches[:10]),
        )

    def malformed_expectations(self) -> None:
        d = self.load("source-audit-clear.json")
        cases = []

        extra = self.exp(d)
        extra.target["extra"] = "x"
        cases.append(("extra-target-key", extra))

        missing = self.exp(d)
        missing.policy.pop("version")
        cases.append(("missing-policy-version", missing))

        nonstring = self.exp(d)
        nonstring.input_authority["id"] = 4  # type: ignore[assignment]
        cases.append(("nonstring-upstream-id", nonstring))

        effect_list = self.exp(d)
        object.__setattr__(effect_list, "effect_params", [])
        cases.append(("list-effect-params", effect_list))

        for label, expectation in cases:
            try:
                got = self.consumer.consume(d, expectation)
                outcome = got.get("outcome")
                reason = got.get("reason")
                passed = outcome == "cannot_establish" and reason == "invalid_expectation"
                self.record(
                    f"rc5.expectation.{label}",
                    "external-api-shape",
                    "declared-v1",
                    "cannot_establish/invalid_expectation",
                    f"{outcome}/{reason}",
                    passed,
                )
            except BaseException as exc:
                self.record(
                    f"rc5.expectation.{label}",
                    "external-api-shape",
                    "declared-v1",
                    "controlled invalid_expectation",
                    type(exc).__name__,
                    False,
                    True,
                    str(exc),
                )

    def new_seeded_mutants(self) -> None:
        # These are deliberately weak serializer/consumer strategies. A PASS means
        # the harness distinguishes the weak strategy from RC5-required behavior.
        def mutant(name: str, caught: bool, observed: str):
            self.record(
                "mutant.rc5." + name,
                "seeded-mutant",
                "evaluator-assurance",
                "weak strategy contradicted",
                observed,
                caught,
            )

        # Python-native JSON is not JCS for these values.
        native = (json.dumps({"n": -0.0}, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()
        correct = self.core.canonical_json_bytes({"n": -0.0})
        mutant("python-native-number-format", native != correct, f"native={native!r} correct={correct!r}")

        # Code-point key ordering is wrong for this pair under JCS's UTF-16 ordering.
        native_keys = (json.dumps({"\uffff": 1, "\U0001f4a9": 2}, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()
        correct_keys = self.core.canonical_json_bytes({"\uffff": 1, "\U0001f4a9": 2})
        mutant("codepoint-key-sort", native_keys != correct_keys, "different" if native_keys != correct_keys else "same")

        d = self.load("source-audit-clear.json")
        d["metadata"]["diagnostics"] = {"bad": "\ud800"}
        try:
            self.core.validate_decision(d)
            surrogate_caught = False
        except self.ContractDError as exc:
            surrogate_caught = exc.code == "invalid_unicode_scalar"
        mutant("lone-surrogate-acceptance", surrogate_caught, "rejected" if surrogate_caught else "accepted")

        deep = self.load("source-audit-clear.json")
        deep["metadata"]["diagnostics"] = {"deep": nested_lists(1200)}
        try:
            self.core.validate_decision(deep)
            depth_caught = False
            depth_obs = "accepted"
        except self.ContractDError as exc:
            depth_caught = exc.code == "json_depth_exceeded"
            depth_obs = exc.code
        except BaseException as exc:
            depth_caught = False
            depth_obs = type(exc).__name__
        mutant("runtime-recursion-leak", depth_caught, depth_obs)

        malformed = self.exp(self.load("source-audit-clear.json"))
        object.__setattr__(malformed, "effect_params", [])
        got = self.consumer.consume(self.load("source-audit-clear.json"), malformed)
        mutant(
            "malformed-expectation-truthiness",
            got.get("outcome") == "cannot_establish" and got.get("reason") == "invalid_expectation",
            f"{got.get('outcome')}/{got.get('reason')}",
        )

    def run(self) -> list[Finding]:
        self.finite_json()
        self.canonical_identity()
        self.applicability()
        self.unknowns_firewall()
        self.seeded_mutants()
        self.rc5_unicode_numbers()
        self.generated_jcs()
        self.malformed_expectations()
        self.new_seeded_mutants()
        return self.findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--report-dir", type=Path, default=Path("attack-report-rc5"))
    parser.add_argument("--gate", action="store_true")
    args = parser.parse_args()

    payload = write_reports(RC5Harness(args.target).run(), args.report_dir)
    print(json.dumps({k: payload[k] for k in ("total", "findings", "promotion_blockers")}, sort_keys=True))
    return 2 if args.gate and payload["promotion_blockers"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
