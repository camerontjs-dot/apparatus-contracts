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


if __name__ == "__main__":
    unittest.main()
