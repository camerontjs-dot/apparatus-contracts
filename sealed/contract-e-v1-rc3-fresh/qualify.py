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
_spec = importlib.util.spec_from_file_location("rc3_qual_reference", _REF_PATH)
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
_spec = importlib.util.spec_from_file_location("rc3_qual_reference_diag", _REF_PATH)
_ref = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ref)
def evaluate(authority_state, request):
    out = deepcopy(_ref.evaluate(authority_state, request))
    out["diagnostics"] = ["alternate_non_normative_diagnostic"]
    return out
'''

WEAK = f'''\
from __future__ import annotations
import hashlib
import importlib.util
import json
import os
from copy import deepcopy
from datetime import datetime
from pathlib import Path
_REF_PATH = Path({str(REFERENCE_PATH)!r})
_spec = importlib.util.spec_from_file_location("rc3_qual_reference_weak", _REF_PATH)
_ref = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ref)

def _permit(out, authority_state):
    out = deepcopy(out)
    out["authorized"] = True
    records = authority_state.get("records", []) if isinstance(authority_state, dict) else []
    out["authority_basis_id"] = records[-1].get("id") if records and isinstance(records[-1], dict) else "weak:synthetic"
    out["diagnostics"] = []
    return _ref._finalize_receipt(out)

def _deny(out):
    out = deepcopy(out)
    out["authorized"] = False
    out["authority_basis_id"] = None
    out["diagnostics"] = ["weak_host_currentness"]
    return _ref._finalize_receipt(out)

def _ordinary_hash(value):
    raw = (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\\n").encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()

def _host_dt(value):
    return datetime.fromisoformat(value[:-1] + "+00:00")

def _host_current(authority_state, request):
    at = _host_dt(request["evaluation_time"])
    for record in authority_state["records"]:
        if at < _host_dt(record["valid_from"]):
            return False
        if record["valid_until"] is not None and at > _host_dt(record["valid_until"]):
            return False
        if record["revoked_at"] is not None and at >= _host_dt(record["revoked_at"]):
            return False
    return True

def _has_duplicate(items, key):
    if not isinstance(items, list):
        return False
    values = [x.get(key) for x in items if isinstance(x, dict)]
    return len(values) != len(set(values))

def evaluate(authority_state, request):
    mode = os.environ.get("CONTRACT_E_RC3_QUAL_MUTANT")
    out = deepcopy(_ref.evaluate(authority_state, request))
    diagnostics = set(out.get("diagnostics", []))

    if mode == "claimed_only":
        out["recomputed_authority_state_id"] = out.get("claimed_authority_state_id")
        return _ref._finalize_receipt(out)

    if mode == "recomputed_only":
        out["claimed_authority_state_id"] = out.get("recomputed_authority_state_id")
        return _ref._finalize_receipt(out)

    if mode == "microsecond_truncator":
        try:
            state_ok, _ = _ref.validate_authority_state(authority_state)
            request_ok, _ = _ref.validate_request(request)
            if state_ok and request_ok:
                exact_current = all(_ref._record_current(record, request["evaluation_time"]) for record in authority_state["records"])
                host_current = _host_current(authority_state, request)
                if exact_current != host_current:
                    if host_current and diagnostics == {{"authority_not_current"}}:
                        return _permit(out, authority_state)
                    if exact_current and out.get("authorized") is True:
                        return _deny(out)
        except Exception:
            pass
        return out

    if mode == "ordinary_json_canonicalizer":
        if isinstance(request, dict):
            try:
                out["request_sha256"] = _ordinary_hash(request)
            except Exception:
                pass
        if isinstance(authority_state, dict):
            try:
                payload = {{k: deepcopy(v) for k, v in authority_state.items() if k != "authority_state_id"}}
                out["recomputed_authority_state_id"] = _ordinary_hash(payload)
            except Exception:
                pass
        return _ref._finalize_receipt(out)

    if mode == "subject_blind" and diagnostics == {{"subject_mismatch"}}:
        return _permit(out, authority_state)

    if mode == "currentness_blind" and diagnostics == {{"authority_not_current"}}:
        return _permit(out, authority_state)

    if mode == "blocker_blind" and diagnostics and diagnostics.issubset({{"relevant_conflict_unresolved", "relevant_residue_unresolved"}}):
        return _permit(out, authority_state)

    if mode == "resolution_blocker_bypass" and isinstance(request, dict):
        j = request.get("jurisdiction", {{}})
        if isinstance(j, dict) and j.get("domain") == "resolution" and j.get("operation") == "resolve":
            if diagnostics and diagnostics.issubset({{"relevant_conflict_unresolved", "relevant_residue_unresolved"}}):
                return _permit(out, authority_state)

    if mode == "support_launderer" and isinstance(request, dict) and request.get("supporting_artifacts") and not out.get("authorized"):
        return _permit(out, authority_state)

    if mode == "state_identity_blind" and "authority_state_identity_mismatch" in diagnostics:
        remaining = diagnostics - {{"authority_state_identity_mismatch"}}
        if not remaining:
            return _permit(out, authority_state)

    if mode == "reference_identity_blind" and isinstance(request, dict):
        repaired = deepcopy(request)
        changed = False
        refs = repaired.get("references")
        if isinstance(refs, list):
            for item in refs:
                if isinstance(item, dict) and all(k in item for k in ("kind", "version", "immutable_id", "identity_sha256")):
                    try:
                        expected = _ref.reference_identity(item["kind"], item["version"], item["immutable_id"])
                    except Exception:
                        continue
                    if item["identity_sha256"] != expected:
                        old = item["identity_sha256"]
                        item["identity_sha256"] = expected
                        j = repaired.get("jurisdiction")
                        if isinstance(j, dict) and j.get("target_ref") == old:
                            j["target_ref"] = expected
                        changed = True
        if changed:
            repaired_out = _ref.evaluate(authority_state, repaired)
            if repaired_out.get("authorized") is True:
                return _permit(out, authority_state)

    if mode == "surplus_peer_permitter" and isinstance(authority_state, dict):
        records = authority_state.get("records")
        if isinstance(records, list) and len(records) > 1:
            peer = records[1]
            if isinstance(peer, dict) and peer.get("basis_type") in {{"grant", "policy"}} and peer.get("parent_id") is None:
                return _permit(out, authority_state)

    if mode == "request_uniqueness_blind" and isinstance(request, dict):
        duplicate = (
            _has_duplicate(request.get("references"), "ref_id")
            or _has_duplicate(request.get("supporting_artifacts"), "id")
            or _has_duplicate(request.get("conflicts"), "id")
            or _has_duplicate(request.get("residues"), "id")
        )
        if duplicate:
            return _permit(out, authority_state)

    if mode == "preservation_dropper":
        out["preserved"] = {{"references": [], "supporting_artifacts": [], "conflicts": [], "residues": []}}
        return _ref._finalize_receipt(out)

    return out
'''

MUTANTS = {
    "claimed_only": "normative",
    "recomputed_only": "normative",
    "microsecond_truncator": "fractional_currentness",
    "ordinary_json_canonicalizer": "canonicalization",
    "subject_blind": "false_permit",
    "currentness_blind": "false_permit",
    "blocker_blind": "false_permit",
    "resolution_blocker_bypass": "false_permit",
    "support_launderer": "false_permit",
    "state_identity_blind": "false_permit",
    "reference_identity_blind": "false_permit",
    "surplus_peer_permitter": "false_permit",
    "request_uniqueness_blind": "false_permit",
    "preservation_dropper": "preservation",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compact(result: dict) -> dict:
    return {key: value for key, value in result.items() if key != "records"}


def require_mutant_failure(name: str, expectation: str, result: dict) -> None:
    if result["scientific_state"] != "FALSIFIED":
        raise SystemExit(f"weak control escaped evaluator: {name}")
    if expectation == "normative" and not result["normative_mismatch_ids"]:
        raise SystemExit(f"weak control produced no normative mismatch: {name}")
    if expectation == "fractional_currentness":
        if not result["fractional_currentness_failure_ids"]:
            raise SystemExit("microsecond truncator escaped fractional hidden cases")
        if not (result["false_permit_ids"] or result["false_reject_ids"]):
            raise SystemExit("microsecond truncator produced no authorization error")
    if expectation == "canonicalization" and not result["canonicalization_failure_ids"]:
        raise SystemExit("ordinary JSON canonicalizer escaped JCS-sensitive hidden cases")
    if expectation == "false_permit" and not result["false_permit_ids"]:
        raise SystemExit(f"weak control did not produce recorded false permit: {name}")
    if expectation == "preservation" and not result["preservation_failure_ids"]:
        raise SystemExit(f"weak control did not produce preservation failure: {name}")


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="contract-e-v1-rc3-qual-") as td:
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
            os.environ["CONTRACT_E_RC3_QUAL_MUTANT"] = name
            result = compare(weak)
            weak_results[name] = compact(result)
            require_mutant_failure(name, expectation, result)
        os.environ.pop("CONTRACT_E_RC3_QUAL_MUTANT", None)

        receipt = {
            "schema": "contract-e-v1-rc3-fresh-evaluator-qualification-v1",
            "qualification_state": "PASS",
            "fresh_independent_implementation_existed_at_qualification": False,
            "candidate_freeze_head": "72f44d206f4f7e64d6993ac85e2fe2f086afb381",
            "candidate_freeze_receipt_commit": "51431b7423040c924c34b78a6c97cc6c7605ba8a",
            "candidate_reference_sha256": sha256(REFERENCE_PATH),
            "hidden_case_count": baseline["case_count"],
            "reference_normative_exact_matches": baseline["normative_exact_matches"],
            "fractional_hidden_cases": len([x for x in baseline["records"] if x["family"] == "fractional-currentness"]),
            "canonicalization_hidden_cases": len([x for x in baseline["records"] if x["family"] == "canonicalization"]),
            "diagnostic_variant_state": diag["scientific_state"],
            "diagnostic_content_is_normative": False,
            "weak_controls_required": len(MUTANTS),
            "weak_controls_caught": len(weak_results),
            "weak_controls": weak_results,
            "qualification_failures": [],
            "production_authorization": False,
        }
        out = HERE / "qualification"
        out.mkdir(exist_ok=True)
        (out / "QUALIFICATION_RECEIPT.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
