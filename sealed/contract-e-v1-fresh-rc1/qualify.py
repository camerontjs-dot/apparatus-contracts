from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path

from evaluate_fresh import REFERENCE_PATH, compare

HERE = Path(__file__).resolve().parent

PASSTHROUGH = f'''\
from __future__ import annotations
import importlib.util
from pathlib import Path
_REF_PATH = Path({str(REFERENCE_PATH)!r})
_spec = importlib.util.spec_from_file_location("qual_reference", _REF_PATH)
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
_spec = importlib.util.spec_from_file_location("qual_reference_diag", _REF_PATH)
_ref = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ref)
def evaluate(authority_state, request):
    out = deepcopy(_ref.evaluate(authority_state, request))
    out["diagnostics"] = ["alternate_non_normative_diagnostic"]
    return out
'''

WEAK = f'''\
from __future__ import annotations
import importlib.util
import os
from copy import deepcopy
from pathlib import Path
_REF_PATH = Path({str(REFERENCE_PATH)!r})
_spec = importlib.util.spec_from_file_location("qual_reference_weak", _REF_PATH)
_ref = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ref)

def _permit(out, authority_state):
    out = deepcopy(out)
    out["authorized"] = True
    records = authority_state.get("records", []) if isinstance(authority_state, dict) else []
    out["authority_basis_id"] = records[-1].get("id") if records else "weak:synthetic"
    out["diagnostics"] = []
    return _ref._finalize_receipt(out)

def evaluate(authority_state, request):
    mode = os.environ.get("CONTRACT_E_QUAL_MUTANT")
    out = deepcopy(_ref.evaluate(authority_state, request))
    diagnostics = set(out.get("diagnostics", []))

    if mode == "subject_blind" and "subject_mismatch" in diagnostics:
        return _permit(out, authority_state)

    if mode == "currentness_blind" and "authority_not_current" in diagnostics:
        return _permit(out, authority_state)

    if mode == "blocker_blind" and diagnostics.intersection({{"relevant_conflict_unresolved", "relevant_residue_unresolved"}}):
        remaining = diagnostics - {{"relevant_conflict_unresolved", "relevant_residue_unresolved"}}
        if not remaining:
            return _permit(out, authority_state)

    if mode == "support_launderer" and isinstance(request, dict) and request.get("supporting_artifacts") and not out.get("authorized"):
        return _permit(out, authority_state)

    if mode == "identity_blind" and isinstance(request, dict):
        refs = request.get("references")
        if isinstance(refs, list):
            for item in refs:
                if isinstance(item, dict) and all(k in item for k in ("kind", "version", "immutable_id", "identity_sha256")):
                    if item["identity_sha256"] != _ref.reference_identity(item["kind"], item["version"], item["immutable_id"]):
                        return _permit(out, authority_state)

    if mode == "surplus_peer_permitter" and isinstance(authority_state, dict):
        records = authority_state.get("records")
        if isinstance(records, list) and len(records) > 1:
            peer = records[1]
            if isinstance(peer, dict) and peer.get("basis_type") in {{"grant", "policy"}} and peer.get("parent_id") is None:
                return _permit(out, authority_state)

    if mode == "preservation_dropper":
        out["preserved"] = {{"references": [], "supporting_artifacts": [], "conflicts": [], "residues": []}}
        return _ref._finalize_receipt(out)

    return out
'''

MUTANTS = {
    "subject_blind": "false_permit",
    "currentness_blind": "false_permit",
    "blocker_blind": "false_permit",
    "support_launderer": "false_permit",
    "identity_blind": "false_permit",
    "surplus_peer_permitter": "false_permit",
    "preservation_dropper": "preservation_failure",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compact(result: dict) -> dict:
    return {k: v for k, v in result.items() if k != "records"}


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="contract-e-v1-qual-") as td:
        root = Path(td)
        passthrough = root / "passthrough.py"
        diagnostic = root / "diagnostic_variant.py"
        weak = root / "weak.py"
        passthrough.write_text(PASSTHROUGH)
        diagnostic.write_text(DIAGNOSTIC_VARIANT)
        weak.write_text(WEAK)

        baseline = compare(passthrough)
        if baseline["scientific_state"] != "SUPPORTED":
            raise SystemExit(f"reference passthrough failed evaluator wiring: {compact(baseline)}")
        if baseline["normative_exact_matches"] != baseline["case_count"]:
            raise SystemExit("reference passthrough was not exact on every hidden case")

        diag = compare(diagnostic)
        if diag["scientific_state"] != "SUPPORTED":
            raise SystemExit(f"diagnostic-only invariant failed: {compact(diag)}")

        weak_results = {}
        for name, expectation in MUTANTS.items():
            os.environ["CONTRACT_E_QUAL_MUTANT"] = name
            result = compare(weak)
            weak_results[name] = compact(result)
            if result["scientific_state"] != "FALSIFIED":
                raise SystemExit(f"weak control escaped evaluator: {name}")
            if expectation == "false_permit" and not result["false_permit_ids"]:
                raise SystemExit(f"weak control did not produce recorded false permit: {name}")
            if expectation == "preservation_failure" and not result["preservation_failure_ids"]:
                raise SystemExit(f"weak control did not produce preservation failure: {name}")
        os.environ.pop("CONTRACT_E_QUAL_MUTANT", None)

        receipt = {
            "schema": "contract-e-v1-fresh-evaluator-qualification-v1",
            "qualification_state": "PASS",
            "fresh_implementation_existed_at_qualification": False,
            "candidate_freeze_commit": "8876b7bcc2afa1a4902400b0cc507cf2ef02e6e7",
            "candidate_reference_sha256": sha256(REFERENCE_PATH),
            "hidden_case_count": baseline["case_count"],
            "reference_normative_exact_matches": baseline["normative_exact_matches"],
            "diagnostic_variant_state": diag["scientific_state"],
            "diagnostic_content_is_normative": False,
            "weak_controls_required": len(MUTANTS),
            "weak_controls_caught": len(weak_results),
            "weak_controls": weak_results,
            "qualification_failures": [],
        }
        out = HERE / "qualification"
        out.mkdir(exist_ok=True)
        (out / "QUALIFICATION_RECEIPT.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
        print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
