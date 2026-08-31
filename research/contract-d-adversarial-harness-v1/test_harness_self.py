from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from attack_contract_d import Finding, write_reports


class HarnessSelfTest(unittest.TestCase):
    def test_report_preserves_blocking_and_nonblocking_findings(self):
        findings = [
            Finding("a", "semantic", "declared-v1", "reject", "accepted", "FINDING", True, "in-domain"),
            Finding("b", "resource", "bounded-runtime-robustness", "complete", "RecursionError", "FINDING", False, "resource"),
            Finding("c", "control", "evaluator-assurance", "caught", "caught", "PASS", False, ""),
        ]
        with tempfile.TemporaryDirectory() as td:
            payload = write_reports(findings, Path(td))
            self.assertEqual(payload["promotion_blockers"], 1)
            self.assertEqual(payload["findings"], 2)
            persisted = json.loads((Path(td) / "report.json").read_text())
            self.assertTrue(persisted["items"][0]["promotion_blocker"])
            self.assertFalse(persisted["items"][1]["promotion_blocker"])
            self.assertIn("bounded-runtime-robustness", (Path(td) / "report.md").read_text())


if __name__ == "__main__":
    unittest.main()
