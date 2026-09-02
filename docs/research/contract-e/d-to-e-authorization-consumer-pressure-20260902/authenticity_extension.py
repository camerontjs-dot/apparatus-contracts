from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any


def load_contract_e(reference_path: Path):
    spec = importlib.util.spec_from_file_location("contract_e_rc1_reference_authenticity", reference_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Contract E reference")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract-d-root", required=True)
    parser.add_argument("--contract-e-root", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    d_root = Path(args.contract_d_root).resolve()
    e_root = Path(args.contract_e_root).resolve()
    out_path = Path(args.output).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    sys.path.insert(0, str(d_root))
    from validators.contract_d_consume import ApplicabilityExpectation, consume  # type: ignore
    from validators.contract_d_core import semantic_identity, validate_effect, validate_decision  # type: ignore

    e = load_contract_e(
        e_root / "docs/research/contract-e/v1-closure-20260902/candidate/reference.py"
    )

    fixtures = json.loads(
        (d_root / "fixtures/contract-d/1.0.0/valid.json").read_text(encoding="utf-8")
    )["fixtures"]

    rows: list[dict[str, Any]] = []

    def record(case_id: str, expected: Any, observed: Any, implication: str) -> None:
        rows.append(
            {
                "id": case_id,
                "expected": expected,
                "observed": observed,
                "pass": observed == expected,
                "implication": implication,
            }
        )
        if observed != expected:
            raise AssertionError(f"{case_id}: expected {expected!r}, observed {observed!r}")

    def expectation_for(decision: dict[str, Any]) -> ApplicabilityExpectation:
        effect = validate_effect(decision["effect"])
        return ApplicabilityExpectation(
            input_authority=deepcopy(decision["input_authority"]),
            policy=deepcopy(decision["policy"]),
            target=deepcopy(decision["target"]),
            requested_operation=effect["type"],
            effect_params=deepcopy(effect["params"]),
        )

    def make_ref(ref_id: str, kind: str, version: str | None, immutable_id: str) -> dict[str, Any]:
        return {
            "ref_id": ref_id,
            "kind": kind,
            "version": version,
            "immutable_id": immutable_id,
            "identity_sha256": e.reference_identity(kind, version, immutable_id),
        }

    def seal_state(state: dict[str, Any]) -> dict[str, Any]:
        state = deepcopy(state)
        state["authority_state_id"] = e.authority_state_identity(state)
        return state

    def receipt_self_consistent_for_request(receipt: dict[str, Any], request: dict[str, Any]) -> bool:
        if receipt.get("authorized") is not True:
            return False
        if receipt.get("authority_conferring") is not False:
            return False
        if receipt.get("request_id") != request.get("request_id"):
            return False
        if receipt.get("request_sha256") != e.sha256_identity(request):
            return False
        for key in ("authority_state_id", "evaluation_time", "subject_id", "jurisdiction"):
            if receipt.get(key) != request.get(key):
                return False
        projection = {
            key: deepcopy(value)
            for key, value in receipt.items()
            if key not in {"receipt_id", "diagnostics"}
        }
        return receipt.get("receipt_id") == e.sha256_identity(projection)

    # F1: internally valid forged Contract D CLEAR is structurally consumable.
    forged_d = deepcopy(fixtures["completed-hold.json"])
    forged_d["evaluation"]["disposition"] = "clear"
    validate_decision(forged_d)
    forged_d_result = consume(forged_d, expectation_for(forged_d))
    record(
        "F1-forged-valid-contract-d-clear",
        "candidate_for_authorization",
        forged_d_result["outcome"],
        "Contract D validation/semantic identity establish internal validity and exact binding, not trusted producer origin.",
    )

    # F2: a fabricated self-consistent root AuthorityState is accepted by the candidate by design.
    target = make_ref("target", "knowledge", "1", "fabricated-target")
    fabricated_state = seal_state(
        {
            "schema": e.STATE_SCHEMA,
            "authority_state_id": "sha256:" + "0" * 64,
            "records": [
                {
                    "id": "fabricated-root-grant",
                    "basis_type": "grant",
                    "subject_id": "attacker:subject",
                    "domain": "knowledge",
                    "operation": "knowledge.cite_as_evidence",
                    "scope": "knowledge",
                    "target_class": "knowledge",
                    "target_ref": target["identity_sha256"],
                    "valid_from": "2026-09-02T16:00:00Z",
                    "valid_until": "2026-09-02T20:00:00Z",
                    "revoked_at": None,
                    "parent_id": None,
                    "delegated_by": None,
                }
            ],
        }
    )
    fabricated_request = {
        "schema": e.REQUEST_SCHEMA,
        "request_id": "fabricated-request",
        "authority_state_id": fabricated_state["authority_state_id"],
        "evaluation_time": "2026-09-02T18:00:00Z",
        "subject_id": "attacker:subject",
        "jurisdiction": {
            "domain": "knowledge",
            "operation": "knowledge.cite_as_evidence",
            "scope": "knowledge",
            "target_class": "knowledge",
            "target_ref": target["identity_sha256"],
        },
        "references": [target],
        "supporting_artifacts": [],
        "conflicts": [],
        "residues": [],
    }
    fabricated_receipt = e.evaluate(fabricated_state, fabricated_request)
    record(
        "F2-fabricated-root-authority-state",
        True,
        fabricated_receipt["authorized"],
        "Expected candidate boundary: root grant legitimacy/provenance is external to Contract E RC1.",
    )

    # F3: unkeyed deterministic receipt identity does not authenticate evaluator origin.
    denied_request = deepcopy(fabricated_request)
    denied_request["request_id"] = "denied-request"
    denied_request["subject_id"] = "other:subject"
    denied_receipt = e.evaluate(fabricated_state, denied_request)
    if denied_receipt["authorized"] is not False:
        raise AssertionError("denied control unexpectedly authorized")

    forged_receipt = deepcopy(denied_receipt)
    forged_receipt["authorized"] = True
    forged_receipt["authority_basis_id"] = "fabricated-root-grant"
    forged_receipt["diagnostics"] = []
    projection = {
        key: deepcopy(value)
        for key, value in forged_receipt.items()
        if key not in {"receipt_id", "diagnostics"}
    }
    forged_receipt["receipt_id"] = e.sha256_identity(projection)

    record(
        "F3-forged-authorized-receipt-self-hashes",
        True,
        receipt_self_consistent_for_request(forged_receipt, denied_request),
        "A request-binding + self-hash-only consumer cannot authenticate who performed the evaluation.",
    )

    # F4: fresh point-of-use evaluation defeats the forged receipt.
    fresh = e.evaluate(fabricated_state, denied_request)
    record(
        "F4-fresh-evaluation-defeats-forged-receipt",
        False,
        fresh["authorized"],
        "Point-of-use re-evaluation uses actual AuthorityState/request semantics rather than trusting forged receipt bytes.",
    )

    # F5: diagnostics are explicitly non-authoritative and excluded from receipt semantic identity.
    diagnostic_mutation = deepcopy(fabricated_receipt)
    original_id = diagnostic_mutation["receipt_id"]
    diagnostic_mutation["diagnostics"] = ["changed", "observability-only"]
    record(
        "F5-diagnostics-do-not-change-receipt-identity",
        original_id,
        diagnostic_mutation["receipt_id"],
        "Diagnostics are observability only; consumers must not use diagnostic text as authority.",
    )

    failures = [row for row in rows if not row["pass"]]
    result = {
        "experiment": "contract-d-to-e-authenticity-extension-20260902",
        "status": "PASS" if not failures else "FAIL",
        "case_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "fail_count": len(failures),
        "failed_case_ids": [row["id"] for row in failures],
        "finding": "PROVENANCE_AUTHENTICITY_BOUNDARY_REQUIRED" if not failures else "UNRESOLVED",
        "trusted_origin_requirements_supported": {
            "contract_d_decision_origin": True,
            "authority_state_root_origin": True,
            "authorization_receipt_evaluator_origin_or_fresh_reevaluation": True,
        },
        "cryptographic_scheme_selected": False,
        "rows": rows,
    }
    out_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("status", "case_count", "finding", "failed_case_ids")}))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
