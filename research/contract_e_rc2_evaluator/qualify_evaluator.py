from __future__ import annotations

import argparse
import json
import textwrap
from pathlib import Path
from tempfile import TemporaryDirectory

from evaluate_fresh import evaluate_module


WEAK_BODIES = {
    "claimed_only_receipt_identity": """
out = ref.evaluate(state, request)
out["recomputed_authority_state_id"] = out["claimed_authority_state_id"]
return reseal(out)
""",
    "recomputed_only_receipt_identity": """
out = ref.evaluate(state, request)
out["claimed_authority_state_id"] = out["recomputed_authority_state_id"]
return reseal(out)
""",
    "ordinary_json_number_canonicalization": """
out = ref.evaluate(state, request)
if isinstance(state, dict) and "future_numeric_field" in state:
    payload = {k: copy.deepcopy(v) for k, v in state.items() if k != "authority_state_id"}
    try:
        raw = (json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\\n").encode()
        out["recomputed_authority_state_id"] = "sha256:" + hashlib.sha256(raw).hexdigest()
    except Exception:
        pass
return reseal(out)
""",
    "supporting_artifact_confers": """
out = ref.evaluate(state, request)
if isinstance(request, dict) and request.get("supporting_artifacts") and not out.get("authorized"):
    out["authorized"] = True
    out["authority_basis_id"] = "support:weak"
return reseal(out)
""",
    "status_established_confers": """
out = ref.evaluate(state, request)
records = state.get("records", []) if isinstance(state, dict) else []
if any(isinstance(r, dict) and r.get("status") == "established" for r in records):
    out["authorized"] = True
    out["authority_basis_id"] = "status:weak"
return reseal(out)
""",
    "subject_blind": """
out = ref.evaluate(state, request)
records = state.get("records", []) if isinstance(state, dict) else []
if records and isinstance(request, dict) and request.get("subject_id") != records[-1].get("subject_id"):
    out["authorized"] = True
    out["authority_basis_id"] = records[-1].get("id")
return reseal(out)
""",
    "operation_blind": """
out = ref.evaluate(state, request)
records = state.get("records", []) if isinstance(state, dict) else []
try:
    if records and request["jurisdiction"]["operation"] != records[-1]["operation"]:
        out["authorized"] = True
        out["authority_basis_id"] = records[-1].get("id")
except Exception:
    pass
return reseal(out)
""",
    "target_blind": """
out = ref.evaluate(state, request)
records = state.get("records", []) if isinstance(state, dict) else []
try:
    leaf = records[-1]
    j = request["jurisdiction"]
    if j["target_class"] != leaf["target_class"] or j["target_ref"] != leaf["target_ref"]:
        out["authorized"] = True
        out["authority_basis_id"] = leaf.get("id")
except Exception:
    pass
return reseal(out)
""",
    "blocker_blind": """
out = ref.evaluate(state, request)
try:
    if any(x.get("relevant") for x in request.get("conflicts", []) + request.get("residues", [])):
        out["authorized"] = True
        records = state.get("records", [])
        out["authority_basis_id"] = records[-1].get("id") if records else "weak"
except Exception:
    pass
return reseal(out)
""",
    "revocation_blind": """
out = ref.evaluate(state, request)
records = state.get("records", []) if isinstance(state, dict) else []
if records and any(r.get("revoked_at") is not None for r in records) and not out.get("authorized"):
    out["authorized"] = True
    out["authority_basis_id"] = records[-1].get("id")
return reseal(out)
""",
    "authority_conferring_receipt": """
out = ref.evaluate(state, request)
out["authority_conferring"] = True
return reseal(out)
""",
    "drop_recomputed_identity_on_denial": """
out = ref.evaluate(state, request)
if not out.get("authorized"):
    out["recomputed_authority_state_id"] = None
return reseal(out)
""",
    "diagnostics_affect_semantic_identity": """
out = ref.evaluate(state, request)
if out.get("diagnostics"):
    payload = {k: copy.deepcopy(v) for k, v in out.items() if k != "receipt_id"}
    out["receipt_id"] = ref.sha256_identity(payload)
return out
""",
    "surplus_peer_any_authorizes": """
out = ref.evaluate(state, request)
records = state.get("records", []) if isinstance(state, dict) else []
if len(records) > 1 and not out.get("authorized"):
    out["authorized"] = True
    out["authority_basis_id"] = records[0].get("id") if isinstance(records[0], dict) else "weak"
return reseal(out)
""",
}


def wrapper_source(reference_path: str, body: str, diagnostics_only: bool = False) -> str:
    if diagnostics_only:
        body = """
out = ref.evaluate(state, request)
out["diagnostics"] = ["arbitrary non-normative diagnostic", "another diagnostic"]
return out
"""
    indented = textwrap.indent(textwrap.dedent(body).strip(), "    ")
    return f'''from __future__ import annotations
import copy
import hashlib
import importlib.util
import json

spec = importlib.util.spec_from_file_location("wrapped_ref", {reference_path!r})
ref = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ref)

def reseal(out):
    try:
        out["receipt_id"] = ref.sha256_identity(ref._receipt_projection(out))
    except Exception:
        out["receipt_id"] = None
    return out

def evaluate(state, request):
{indented}
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", required=True)
    parser.add_argument("--hidden-cases", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    baseline = evaluate_module(args.reference, args.reference, args.hidden_cases)
    if baseline["scientific_state"] != "SUPPORTED":
        raise SystemExit("reference did not pass evaluator")

    caught = {}
    with TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        diagnostic_wrapper = tmp / "diagnostic_wrapper.py"
        diagnostic_wrapper.write_text(wrapper_source(args.reference, "", diagnostics_only=True))
        diagnostic_result = evaluate_module(str(diagnostic_wrapper), args.reference, args.hidden_cases)
        diagnostic_invariance = diagnostic_result["scientific_state"] == "SUPPORTED"

        for name, body in WEAK_BODIES.items():
            path = tmp / f"weak_{name}.py"
            path.write_text(wrapper_source(args.reference, body))
            result = evaluate_module(str(path), args.reference, args.hidden_cases)
            caught[name] = {
                "caught": result["scientific_state"] == "FALSIFIED",
                "false_permits": result["false_permit_ids"],
                "false_rejects": result["false_reject_ids"],
                "normative_mismatches": result["normative_mismatch_ids"],
                "exceptions": result["exception_ids"],
            }

    all_caught = all(item["caught"] for item in caught.values())
    result = {
        "status": "PASS" if all_caught and diagnostic_invariance else "FAIL",
        "reference_case_count": baseline["case_count"],
        "reference_normative_exact_matches": baseline["normative_exact_matches"],
        "reference_cross_case_dual_identity_ok": baseline["cross_case_dual_identity_ok"],
        "diagnostic_content_invariance": diagnostic_invariance,
        "weak_control_count": len(caught),
        "weak_controls_caught": sum(1 for x in caught.values() if x["caught"]),
        "weak_controls": caught,
    }
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
