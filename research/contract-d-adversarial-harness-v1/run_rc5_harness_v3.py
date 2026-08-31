from __future__ import annotations

import argparse
import copy
import json
import struct
from pathlib import Path

from attack_contract_d import write_reports
from run_rc5_harness_v2 import CorrectedRC5Harness


def f64(hex_bits: str) -> float:
    return struct.unpack(">d", bytes.fromhex(hex_bits))[0]


class StandardsRC5Harness(CorrectedRC5Harness):
    def malformed_expectations(self) -> None:
        super().malformed_expectations()
        d = self.load("source-audit-clear.json")

        cases = []
        host_only = self.exp(d)
        object.__setattr__(host_only, "effect_params", {"scope": {"claim"}})
        cases.append(("host-only-effect-param", host_only))

        nonfinite = self.exp(d)
        object.__setattr__(nonfinite, "effect_params", {"scope": float("nan")})
        cases.append(("nonfinite-effect-param", nonfinite))

        surrogate_op = self.exp(d)
        object.__setattr__(surrogate_op, "requested_operation", "knowledge.add_verified_tag\ud800")
        cases.append(("surrogate-operation", surrogate_op))

        bad_hash = self.exp(d)
        bad_hash.target["content_sha256"] = "not-a-sha256"
        cases.append(("malformed-target-hash", bad_hash))

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

    def rfc_number_vectors(self) -> None:
        vectors = [
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
        ]
        failures = []
        for bits, expected in vectors:
            try:
                got = self.core.canonical_json_bytes({"n": f64(bits)})
                wanted = (f'{{"n":{expected}}}\n').encode()
                if got != wanted:
                    failures.append(f"{bits}: got={got!r} wanted={wanted!r}")
            except BaseException as exc:
                failures.append(f"{bits}: {type(exc).__name__}: {exc}")
        self.record(
            "rc5.rfc8785-appendix-b-vectors",
            "standards-conformance",
            "declared-v1",
            f"{len(vectors)}/{len(vectors)} exact",
            f"{len(vectors) - len(failures)}/{len(vectors)} exact",
            not failures,
            True,
            "\n".join(failures[:10]),
        )

    def byte_roundtrip(self) -> None:
        base = self.load("source-audit-clear.json")
        failures = []
        for label, number in (
            ("1e20", 1e20),
            ("two53", float(2**53)),
            ("two68", float(2**68)),
        ):
            d = copy.deepcopy(base)
            d["metadata"]["diagnostics"] = {"number": number}
            try:
                first = self.core.canonical_json_bytes(d)
                parsed = self.parser.require_canonical_bytes(first)
                second = self.core.canonical_json_bytes(parsed)
                if first != second:
                    failures.append(f"{label}: canonical bytes changed")
            except BaseException as exc:
                failures.append(f"{label}: {type(exc).__name__}: {exc}")
        self.record(
            "rc5.canonical-self-roundtrip-large-binary64",
            "canonicalization",
            "declared-v1",
            "3/3 stable",
            "3/3 stable" if not failures else f"{3-len(failures)}/3 stable",
            not failures,
            True,
            "\n".join(failures),
        )

        d = copy.deepcopy(base)
        d["metadata"]["diagnostics"] = {"number": 9007199254740993}
        raw = json.dumps(d, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        try:
            self.parser.parse_json_bytes(raw)
        except self.ContractDError as exc:
            self.record(
                "rc5.precision-losing-integer-token",
                "number-domain",
                "declared-v1",
                "non_interoperable_integer",
                exc.code,
                exc.code == "non_interoperable_integer",
            )
        except BaseException as exc:
            self.record(
                "rc5.precision-losing-integer-token",
                "number-domain",
                "declared-v1",
                "controlled non_interoperable_integer",
                type(exc).__name__,
                False,
                True,
                str(exc),
            )
        else:
            self.record(
                "rc5.precision-losing-integer-token",
                "number-domain",
                "declared-v1",
                "rejection",
                "accepted",
                False,
            )

    def run(self):
        super().run()
        self.rfc_number_vectors()
        self.byte_roundtrip()
        return self.findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--report-dir", type=Path, default=Path("attack-report-rc5"))
    parser.add_argument("--gate", action="store_true")
    args = parser.parse_args()

    payload = write_reports(StandardsRC5Harness(args.target).run(), args.report_dir)
    print(json.dumps({k: payload[k] for k in ("total", "findings", "promotion_blockers")}, sort_keys=True))
    return 2 if args.gate and payload["promotion_blockers"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
