"""Static checks for the preserved PR #132 source corrections.

These checks parse candidate source without importing or executing it.
"""

import ast
import unittest
from pathlib import Path


EXPERIMENT = Path(__file__).resolve().parents[1]
PREFLIGHT = EXPERIMENT / "receipt_preflight.py"
RUNNER = EXPERIMENT / "reproduce_rc6.py"


def _function(path: Path, name: str) -> ast.FunctionDef:
    module = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return next(
        node
        for node in ast.walk(module)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == name
    )


class Pr132DeltaStaticTests(unittest.TestCase):
    def test_preflight_receipt_path_is_scoped_to_this_successor(self) -> None:
        module = ast.parse(
            PREFLIGHT.read_text(encoding="utf-8"), filename=str(PREFLIGHT)
        )
        assignment = next(
            node
            for node in module.body
            if isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name)
                and target.id == "APP_RECEIPT_RELATIVE_PATH"
                for target in node.targets
            )
        )
        self.assertIn(
            "successor-executable-source-identity-rc0/FREEZE_RECEIPT.json",
            ast.unparse(assignment.value),
        )
        self.assertNotIn(
            "successor-receipt-contract-rc0/FREEZE_RECEIPT.json",
            ast.unparse(assignment.value),
        )

    def test_preflight_rejects_noncanonical_receipt_path_before_reads(self) -> None:
        function = _function(PREFLIGHT, "build_preflight")
        guard = next(node for node in function.body if isinstance(node, ast.If))

        self.assertEqual(
            ast.unparse(guard.test),
            "apparatus_freeze_receipt.resolve() != "
            "(apparatus_root / APP_RECEIPT_RELATIVE_PATH).resolve()",
        )
        self.assertIsInstance(guard.body[0], ast.Raise)
        self.assertEqual(
            ast.unparse(guard.body[0].exc),
            "PreflightError('apparatus_freeze_receipt_path_not_canonical')",
        )

        first_receipt_read_line = min(
            node.lineno
            for node in ast.walk(function)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in {"git_text", "read_json"}
        )
        self.assertLess(guard.lineno, first_receipt_read_line)

    def test_runner_result_names_receipt_contract_authority(self) -> None:
        function = _function(RUNNER, "run_matrix")
        authority_subject = next(
            node
            for node in ast.walk(function)
            if isinstance(node, ast.Dict)
            and any(
                isinstance(key, ast.Constant)
                and key.value == "receipt_contract_preregistration"
                for key in node.keys
            )
        )

        subjects = {
            key.value: value
            for key, value in zip(authority_subject.keys, authority_subject.values)
            if isinstance(key, ast.Constant) and isinstance(key.value, str)
        }
        self.assertEqual(
            ast.unparse(subjects["receipt_contract_preregistration"]),
            "RECEIPT_CONTRACT_PREREG",
        )
