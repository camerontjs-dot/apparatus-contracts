from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MUTATE = ROOT / "scripts" / "mutate_contract_a_source.py"
VERIFY = ROOT / "scripts" / "verify_target_review.py"
CHECK_GATE = ROOT / "scripts" / "check_gate_output.py"


def tagged(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


class PortableControlTests(unittest.TestCase):
    def test_source_substitution_does_not_reseal_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            original = root / "a.json"
            mutated = root / "m.json"
            value = {
                "handoff_sha256": "sha256:" + "a" * 64,
                "sources": [
                    {
                        "source_id": "s1",
                        "content": "original",
                        "content_sha256": tagged(b"original"),
                    }
                ],
            }
            original.write_text(json.dumps(value), encoding="utf-8")
            cp = subprocess.run([sys.executable, str(MUTATE), str(original), str(mutated)], check=False)
            self.assertEqual(cp.returncode, 0)
            out = json.loads(mutated.read_text())
            self.assertNotEqual(out["sources"][0]["content"], "original")
            self.assertEqual(out["sources"][0]["content_sha256"], value["sources"][0]["content_sha256"])
            self.assertEqual(out["handoff_sha256"], value["handoff_sha256"])

    def test_target_review_requires_distinct_independent_reviewer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "target.json"
            text = "Alpha had a higher rate than Beta."
            text_hash = hashlib.sha256(text.encode()).hexdigest()
            target.write_text(
                json.dumps(
                    {
                        "claim_id": "C1",
                        "proposition": {
                            "proposition_id": "C1",
                            "text_sha256": text_hash,
                            "semantic_family": "strict_comparison",
                            "fields": {
                                "lhs_entity": "Alpha",
                                "rhs_entity": "Beta",
                                "comparison_direction": "MORE_THAN",
                            },
                        },
                    }
                ),
                encoding="utf-8",
            )
            contract_a = root / "a.json"
            a = {
                "handoff_sha256": "sha256:" + "b" * 64,
                "decomposition": {
                    "children": [
                        {
                            "proposition_id": "C1",
                            "text": text,
                            "text_sha256": "sha256:" + text_hash,
                            "sequence": 1,
                        }
                    ]
                },
            }
            contract_a.write_text(json.dumps(a), encoding="utf-8")
            review = root / "review.json"
            review.write_text(
                json.dumps(
                    {
                        "schema": "cal-pipeline-trusted-target-review-v1",
                        "contract_a_handoff_sha256": a["handoff_sha256"],
                        "contract_a_file_sha256": tagged(contract_a.read_bytes()),
                        "targets": [
                            {
                                "proposition_id": "C1",
                                "target_path": "target.json",
                                "target_sha256": tagged(target.read_bytes()),
                                "target_author_context": "same",
                                "reviewer_context": "same",
                                "independent_review": True,
                                "semantic_fidelity_attested": True,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            cp = subprocess.run(
                [sys.executable, str(VERIFY), "--review", str(review), "--contract-a", str(contract_a)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(cp.returncode, 0)
            self.assertIn("distinct", cp.stderr + cp.stdout)

    def test_non_all_of_is_preserved_as_stop_not_reroll(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            text = "Alpha had a higher rate than Beta."
            text_sha = "sha256:" + hashlib.sha256(text.encode()).hexdigest()
            source = "evidence"
            source_sha = tagged(source.encode())
            contract_a = root / "a.json"
            contract_a.write_text(
                json.dumps(
                    {
                        "handoff_sha256": "sha256:" + "c" * 64,
                        "root_proposition": {
                            "proposition_id": "claim-1",
                            "text": text,
                            "text_sha256": text_sha,
                        },
                        "decomposition": {"state": "not_needed"},
                        "sources": [
                            {
                                "source_id": "source-ref:1",
                                "content": source,
                                "content_sha256": source_sha,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            receipt = root / "adapter.json"
            receipt.write_text(
                json.dumps(
                    {
                        "claim_id": "claim-1",
                        "claim_text_sha256": text_sha,
                        "source_bindings": [
                            {
                                "source_ref_id": "source-ref:1",
                                "ers_content_identity": source_sha,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            target_review = root / "target-review.json"
            stop = root / "STOPPED.json"
            cp = subprocess.run(
                [
                    sys.executable,
                    str(CHECK_GATE),
                    "--contract-a",
                    str(contract_a),
                    "--adapter-receipt",
                    str(receipt),
                    "--out-target-review",
                    str(target_review),
                    "--stop-receipt",
                    str(stop),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(cp.returncode, 3)
            self.assertFalse(target_review.exists())
            stopped = json.loads(stop.read_text(encoding="utf-8"))
            self.assertEqual(stopped["terminal_state"], "STOPPED")
            self.assertEqual(stopped["stop_code"], "CONTRACT_A_NOT_DECLARED_ALL_OF")
            self.assertFalse(stopped["reroll_authorized"])


if __name__ == "__main__":
    unittest.main()
