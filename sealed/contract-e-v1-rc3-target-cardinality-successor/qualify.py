from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path

from evaluate_fresh import (
    PREDECESSOR_REFERENCE_PATH,
    REFERENCE_PATH,
    compare,
    predecessor_reference_regression,
)

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PREDECESSOR_QUALIFIER_PATH = REPO / "sealed/contract-e-v1-rc3-fresh/qualify.py"

PASSTHROUGH = f'''\
from __future__ import annotations
import importlib.util
from pathlib import Path
_REF_PATH = Path({str(REFERENCE_PATH)!r})
_spec = importlib.util.spec_from_file_location("rc3_cardinality_qual_reference", _REF_PATH)
_ref = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ref)
def evaluate(authority_state, request):
    return _ref.evaluate(authority_state, request)
'''

DIAGNOSTIC_VARIANT = f'''\
from __future__ import annotations
import importlib.util
from copy import deepcopy
from pathlib import Path
_REF_PATH = Path({str(REFERENCE_PATH)!r})
_spec = importlib.util.spec_from_file_location("rc3_cardinality_qual_reference_diag", _REF_PATH)
_ref = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ref)
def evaluate(authority_state, request):
    out = deepcopy(_ref.evaluate(authority_state, request))
    out["diagnostics"] = ["alternate_non_normative_diagnostic"]
    return out
'''

CARDINALITY_WEAK = f'''\
from __future__ import annotations
import importlib.util
from pathlib import Path
_REF_PATH = Path({str(PREDECESSOR_REFERENCE_PATH)!r})
_spec = importlib.util.spec_from_file_location("rc3_cardinality_membership_only", _REF_PATH)
_ref = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ref)
def evaluate(authority_state, request):
    return _ref.evaluate(authority_state, request)
'''


def _load_predecessor_weak_apparatus():
    """Reuse the exact 14 predecessor mutant definitions without importing its evaluator."""

    source = PREDECESSOR_QUALIFIER_PATH.read_text(encoding="utf-8")
    source = source.replace(
        "from evaluate_fresh import REFERENCE_PATH, compare\n",
        "",
        1,
    )
    namespace = {
        "__name__": "contract_e_rc3_predecessor_qualifier_constants",
        "__file__": str(PREDECESSOR_QUALIFIER_PATH),
        "REFERENCE_PATH": PREDECESSOR_REFERENCE_PATH,
        "compare": None,
    }
    exec(compile(source, str(PREDECESSOR_QUALIFIER_PATH), "exec"), namespace)  # noqa: S102
    predecessor_weak = namespace["WEAK"]
    adapted_weak = predecessor_weak.replace(
        str(PREDECESSOR_REFERENCE_PATH), str(REFERENCE_PATH)
    )
    return adapted_weak, dict(namespace["MUTANTS"]), namespace["require_mutant_failure"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compact(result: dict) -> dict:
    return {key: value for key, value in result.items() if key != "records"}


def main() -> None:
    weak_source, predecessor_mutants, predecessor_require_failure = (
        _load_predecessor_weak_apparatus()
    )
    if len(predecessor_mutants) != 14:
        raise SystemExit(
            f"predecessor weak-control cardinality drifted: {len(predecessor_mutants)}"
        )

    regression = predecessor_reference_regression()
    if regression["state"] != "PASS":
        raise SystemExit(
            f"successor changed predecessor normative cases: {regression}"
        )
    if regression["case_count"] != 59 or regression["normative_exact_matches"] != 59:
        raise SystemExit(f"predecessor hidden corpus cardinality drifted: {regression}")

    with tempfile.TemporaryDirectory(prefix="contract-e-v1-rc3-target-cardinality-qual-") as td:
        root = Path(td)
        passthrough = root / "passthrough.py"
        diagnostic = root / "diagnostic_variant.py"
        weak = root / "weak.py"
        cardinality_weak = root / "target_cardinality_blind.py"
        passthrough.write_text(PASSTHROUGH, encoding="utf-8")
        diagnostic.write_text(DIAGNOSTIC_VARIANT, encoding="utf-8")
        weak.write_text(weak_source, encoding="utf-8")
        cardinality_weak.write_text(CARDINALITY_WEAK, encoding="utf-8")

        baseline = compare(passthrough)
        if baseline["scientific_state"] != "SUPPORTED":
            raise SystemExit(f"reference passthrough failed evaluator wiring: {compact(baseline)}")
        if baseline["case_count"] != 62:
            raise SystemExit(f"successor hidden case count drifted: {baseline['case_count']}")
        if baseline["predecessor_case_count"] != 59:
            raise SystemExit(
                f"predecessor hidden case count drifted: {baseline['predecessor_case_count']}"
            )
        if baseline["target_cardinality_case_count"] != 3:
            raise SystemExit(
                f"target-cardinality case count drifted: {baseline['target_cardinality_case_count']}"
            )
        if baseline["normative_exact_matches"] != baseline["case_count"]:
            raise SystemExit("reference passthrough was not exact on every successor hidden case")

        diag = compare(diagnostic)
        if diag["scientific_state"] != "SUPPORTED":
            raise SystemExit(f"diagnostic-only invariant failed: {compact(diag)}")

        predecessor_weak_results = {}
        for name, expectation in predecessor_mutants.items():
            os.environ["CONTRACT_E_RC3_QUAL_MUTANT"] = name
            result = compare(weak)
            predecessor_weak_results[name] = compact(result)
            predecessor_require_failure(name, expectation, result)
        os.environ.pop("CONTRACT_E_RC3_QUAL_MUTANT", None)

        cardinality_result = compare(cardinality_weak)
        if cardinality_result["scientific_state"] != "FALSIFIED":
            raise SystemExit("target-cardinality-blind weak control escaped evaluator")
        if not cardinality_result["target_cardinality_failure_ids"]:
            raise SystemExit("cardinality weak control produced no target-cardinality mismatch")
        cardinality_false_permits = [
            case_id
            for case_id in cardinality_result["false_permit_ids"]
            if case_id.startswith("NEG-TARGET-")
        ]
        if not cardinality_false_permits:
            raise SystemExit(
                "target-cardinality-blind weak control produced no cardinality false permit"
            )

        receipt = {
            "schema": "contract-e-v1-rc3-target-cardinality-evaluator-qualification-v1",
            "qualification_state": "PASS",
            "production_authorization": False,
            "preregistration_commit": "6d33124a90b29668cc534765859a3cdd75e46ea6",
            "candidate_freeze_head": "30dd929b310727737488192af1579729b2d4dd3e",
            "candidate_freeze_receipt_commit": "e4b47d4b73998c30a09722e9e1ee93d8f00b66a9",
            "predecessor_candidate_head": "72f44d206f4f7e64d6993ac85e2fe2f086afb381",
            "predecessor_evaluator_seal": "3943dd9e5e0711c894356fd4dfef25fd45507d91",
            "successor_reference_sha256": sha256(REFERENCE_PATH),
            "hidden_case_count": baseline["case_count"],
            "predecessor_hidden_cases": baseline["predecessor_case_count"],
            "target_cardinality_hidden_cases": baseline["target_cardinality_case_count"],
            "reference_normative_exact_matches": baseline["normative_exact_matches"],
            "predecessor_reference_regression": regression,
            "diagnostic_variant_state": diag["scientific_state"],
            "diagnostic_content_is_normative": False,
            "predecessor_weak_controls_required": len(predecessor_mutants),
            "predecessor_weak_controls_caught": len(predecessor_weak_results),
            "predecessor_weak_controls": predecessor_weak_results,
            "new_weak_controls_required": 1,
            "new_weak_controls_caught": 1,
            "target_cardinality_blind_result": compact(cardinality_result),
            "weak_controls_required_total": len(predecessor_mutants) + 1,
            "weak_controls_caught_total": len(predecessor_weak_results) + 1,
            "qualification_failures": [],
            "fresh_independent_recoverability_established": False,
        }
        out = HERE / "qualification"
        out.mkdir(exist_ok=True)
        (out / "QUALIFICATION_RECEIPT.json").write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
