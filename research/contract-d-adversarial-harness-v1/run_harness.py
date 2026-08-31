from __future__ import annotations

import argparse
import json
from dataclasses import replace
from pathlib import Path

from attack_contract_d import Harness, write_reports


class CorrectedHarness(Harness):
    """Additive correction for baseline run 33347839365.

    The original pairwise probe tried to mutate the frozen ApplicabilityExpectation
    dataclass and failed before producing a report. This override changes only attack
    construction. Target code, expected outcomes, and finding classification are
    unchanged.
    """

    def applicability(self) -> None:
        clear = self.load("source-audit-clear.json")
        hold = self.load("completed-hold.json")

        for label, decision in (("clear", clear), ("hold", hold)):
            out = self.consumer.consume(decision, self.exp(decision, op="task.dispatch"))["outcome"]
            self.record(
                f"apply.{label}.wrong-op", "applicability", "declared-v1",
                "not_applicable", out, out == "not_applicable",
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
                f"apply.params.{label}", "applicability", "declared-v1",
                wanted, out, out == wanted,
            )

        for section, key in (("input_authority", "id"), ("policy", "version"), ("target", "id")):
            expectation = self.exp(clear)
            container = getattr(expectation, section)
            container[key] = str(container[key]) + "-x"
            out = self.consumer.consume(clear, expectation)["outcome"]
            self.record(
                f"replay.{section}.{key}", "replay-substitution", "declared-v1",
                "not_applicable", out, out == "not_applicable",
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
                    f"combo.{name}", "combinatorial-applicability", "declared-v1",
                    "not_applicable", out, out == "not_applicable",
                )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--report-dir", type=Path, default=Path("attack-report"))
    parser.add_argument("--gate", action="store_true")
    args = parser.parse_args()

    payload = write_reports(CorrectedHarness(args.target).run(), args.report_dir)
    print(json.dumps({k: payload[k] for k in ("total", "findings", "promotion_blockers")}, sort_keys=True))
    return 2 if args.gate and payload["promotion_blockers"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
