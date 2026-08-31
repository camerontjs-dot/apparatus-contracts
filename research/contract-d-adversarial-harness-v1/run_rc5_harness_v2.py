from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from attack_contract_d import write_reports
from run_rc5_harness import RC5Harness, nested_lists


class CorrectedRC5Harness(RC5Harness):
    """Correct evaluator defect preserved in run 33354603157.

    RC5 explicitly defines max container depth 128. The first RC5 attack lane
    inherited RC4's assertion that depth 256 remained valid, causing a false
    promotion blocker even though the RC5-specific depth probes correctly
    observed controlled json_depth_exceeded. This override removes only that
    stale RC4 expectation; target code and RC5 expectations are unchanged.
    """

    def finite_json(self) -> None:
        self.rejected(
            "json.host-set",
            "finite-json",
            lambda d: d["metadata"].__setitem__("diagnostics", {"x": {1, 2}}),
        )
        self.rejected(
            "json.non-string-key",
            "finite-json",
            lambda d: d["metadata"].__setitem__("diagnostics", {1: "x"}),
        )
        self.rejected(
            "json.nan",
            "finite-json",
            lambda d: d["metadata"].__setitem__("diagnostics", {"n": math.nan}),
        )
        self.rejected(
            "json.inf",
            "finite-json",
            lambda d: d["metadata"].__setitem__("diagnostics", {"n": math.inf}),
        )

        def self_cycle(d):
            x: list[Any] = []
            x.append(x)
            d["metadata"]["diagnostics"] = {"cycle": x}

        self.rejected("json.self-cycle", "finite-json", self_cycle)

        def mutual_cycle(d):
            a: list[Any] = []
            b: list[Any] = [a]
            a.append(b)
            d["metadata"]["diagnostics"] = {"cycle": a}

        self.rejected("json.mutual-cycle", "finite-json", mutual_cycle)

        def shared(d):
            leaf = {"v": [1, 2, 3]}
            d["metadata"]["diagnostics"] = {"a": leaf, "b": leaf}

        self.valid_case("json.shared-acyclic", "finite-json", shared)

        # Positive controls below the explicit RC5 bound.
        for depth in (16, 64, 120):
            def deep(d, depth=depth):
                d["metadata"]["diagnostics"] = {"deep": nested_lists(depth)}

            self.valid_case(
                f"rc5.depth-valid-{depth}",
                "resource-depth",
                deep,
                "declared-v1",
                True,
            )

        # Negative controls above the explicit RC5 bound.
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

        for attack_id, raw in (
            ("json.invalid-utf8", b"\xff"),
            ("json.duplicate-key", b'{"a":1,"a":2}'),
            ("json.nonfinite-token", b'{"a":NaN}'),
        ):
            try:
                self.parser.parse_json_bytes(raw)
            except self.ContractDError as exc:
                self.record(
                    attack_id,
                    "parser",
                    "declared-v1",
                    "controlled rejection",
                    type(exc).__name__,
                    True,
                    True,
                    str(exc),
                )
            except BaseException as exc:
                self.record(
                    attack_id,
                    "parser",
                    "declared-v1",
                    "controlled rejection",
                    type(exc).__name__,
                    False,
                    True,
                    str(exc),
                )
            else:
                self.record(
                    attack_id,
                    "parser",
                    "declared-v1",
                    "rejection",
                    "accepted",
                    False,
                )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--report-dir", type=Path, default=Path("attack-report-rc5"))
    parser.add_argument("--gate", action="store_true")
    args = parser.parse_args()

    payload = write_reports(CorrectedRC5Harness(args.target).run(), args.report_dir)
    print(json.dumps({k: payload[k] for k in ("total", "findings", "promotion_blockers")}, sort_keys=True))
    return 2 if args.gate and payload["promotion_blockers"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
