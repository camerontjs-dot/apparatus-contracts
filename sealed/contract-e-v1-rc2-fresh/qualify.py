from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import tempfile
from copy import deepcopy
from pathlib import Path

from evaluate_fresh import REFERENCE_PATH, compare

HERE = Path(__file__).resolve().parent
CANDIDATE_FREEZE_HEAD = "f616f6ed06bf922a53846d464dfc44838c55804d"
CANDIDATE_FREEZE_RECEIPT = "d48d24c791837bb64c9ef7ea5ae1771e13892a91"

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
_spec = importlib.util.spec_from_file_location("qual_reference_weak_rc2", _REF_PATH)
_ref = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ref)

def _permit(out, authority_state):
    out = deepcopy(out)
    out["authorized"] = True
    records = authority_state.get("records", []) if isinstance(authority_state, dict) else []
    out["authority_basis_id"] = records[-1].get("id") if records and isinstance(records[-1], dict) else "weak:synthetic"
    out["diagnostics"] = []
    return _ref._finalize_receipt(out)

def evaluate(authority_state, request):
    mode = os.environ.get("CONTRACT_E_RC2_QUAL_MUTANT")
    out = deepcopy(_ref.evaluate(authority_state, request))
    diagnostics = set(out.get("diagnostics", []))

    if mode == "claimed_only":
        out["authority_state_computed_id"] = out.get("authority_state_claimed_id")
        return _ref._finalize_receipt(out)

    if mode == "computed_only":
        out["authority_state_claimed_id"] = out.get("authority_state_computed_id")
        return _ref._finalize_receipt(out)

    if mode == "microsecond_truncator" and isinstance(request, dict) and isinstance(authority_state, dict):
        records = authority_state.get("records")
        if (
            isinstance(records, list) and records and isinstance(records[-1], dict)
            and records[-1].get("valid_until") == "2026-06-01T12:00:00.1234567Z"
            and request.get("evaluation_time") == "2026-06-01T12:00:00.1234568Z"
        ):
            return _permit(out, authority_state)

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

    if mode == "state_identity_blind" and "authority_state_identity_mismatch" in diagnostics:
        return _permit(out, authority_state)

    if mode == "request_state_blind" and "authority_state_mismatch" in diagnostics:
        return _permit(out, authority_state)

    if mode == "preservation_dropper":
        out["preserved"] = {{"references": [], "supporting_artifacts": [], "conflicts": [], "residues": []}}
        return _ref._finalize_receipt(out)

    return out
'''

MUTANTS = {
    "claimed_only": "normative_mismatch",
    "computed_only": "normative_mismatch",
    "microsecond_truncator": "false_permit",
    "subject_blind": "false_permit",
    "currentness_blind": "false_permit",
    "blocker_blind": "false_permit",
    "support_launderer": "false_permit",
    "state_identity_blind": "false_permit",
    "request_state_blind": "false_permit",
    "preservation_dropper": "preservation_failure",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compact(result: dict) -> dict:
    return {k: v for k, v in result.items() if k != "records"}


def _load_reference():
    spec = importlib.util.spec_from_file_location("rc2_qual_reference", REFERENCE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load RC2 reference")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    # Sanity check the exact-time discriminator directly before evaluator qualification.
    reference = _load_reference()
    target = {
        "ref_id": "target",
        "kind": "object",
        "version": "v1",
        "immutable_id": "obj-1",
        "identity_sha256": reference.reference_identity("object", "v1", "obj-1"),
    }
    state = {
        "schema": reference.STATE_SCHEMA,
        "authority_state_id": "sha256:" + "0" * 64,
        "records": [{
            "id": "root", "basis_type": "grant", "subject_id": "alice",
            "domain": "deploy", "operation": "release", "scope": "prod",
            "target_class": "artifact", "target_ref": target["identity_sha256"],
            "valid_from": "2026-01-01T00:00:00Z",
            "valid_until": "2026-06-01T12:00:00.1234567Z", "revoked_at": None,
            "parent_id": None, "delegated_by": None,
        }],
    }
    state["authority_state_id"] = reference.authority_state_identity(state)
    request = {
        "schema": reference.REQUEST_SCHEMA,
        "request_id": "precision-check",
        "authority_state_id": state["authority_state_id"],
        "evaluation_time": "2026-06-01T12:00:00.1234568Z",
        "subject_id": "alice",
        "jurisdiction": {"domain": "deploy", "operation": "release", "scope": "prod", "target_class": "artifact", "target_ref": target["identity_sha256"]},
        "references": [target], "supporting_artifacts": [], "conflicts": [], "residues": [],
    }
    if reference.evaluate(state, request)["authorized"] is not False:
        raise SystemExit("RC2 exact-time reference sanity check failed")

    with tempfile.TemporaryDirectory(prefix="contract-e-v1-rc2-qual-") as td:
        root = Path(td)
        passthrough = root / "passthrough.py"
        diagnostic = root / "diagnostic_variant.py"
        weak = root / "weak.py"
        passthrough.write_text(PASSTHROUGH, encoding="utf-8")
        diagnostic.write_text(DIAGNOSTIC_VARIANT, encoding="utf-8")
        weak.write_text(WEAK, encoding="utf-8")

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
            os.environ["CONTRACT_E_RC2_QUAL_MUTANT"] = name
            result = compare(weak)
            weak_results[name] = compact(result)
            if result["scientific_state"] != "FALSIFIED":
                raise SystemExit(f"weak control escaped evaluator: {name}")
            if expectation == "false_permit" and not result["false_permit_ids"]:
                raise SystemExit(f"weak control did not produce recorded false permit: {name}")
            if expectation == "preservation_failure" and not result["preservation_failure_ids"]:
                raise SystemExit(f"weak control did not produce preservation failure: {name}")
            if expectation == "normative_mismatch" and not result["normative_mismatch_ids"]:
                raise SystemExit(f"weak control did not produce normative mismatch: {name}")
        os.environ.pop("CONTRACT_E_RC2_QUAL_MUTANT", None)

        receipt = {
            "schema": "contract-e-v1-rc2-fresh-evaluator-qualification-v1",
            "qualification_state": "PASS",
            "fresh_implementation_existed_at_qualification": False,
            "candidate_freeze_head": CANDIDATE_FREEZE_HEAD,
            "candidate_freeze_receipt_commit": CANDIDATE_FREEZE_RECEIPT,
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
        (out / "QUALIFICATION_RECEIPT.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
