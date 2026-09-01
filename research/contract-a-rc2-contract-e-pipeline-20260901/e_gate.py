#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "artifacts" / "contract-a-rc2-contract-e-gate"
E_ROOT = ROOT / "_external" / "e" / "docs" / "research" / "contract-e" / "epistemic-authority-propagation-rc0b"

from validators.contract_d_consume import ApplicabilityExpectation, consume
from validators.contract_d_core import canonical_json_bytes, validate_decision

EXPECTED_A = {
    "declared": "sha256:de23b0eb66b3316e85bd9fbc73f4dfe2b6525a1e73783fca8d6e1fbd9bb0189d",
    "not_decomposed": "sha256:2816c5e36d70fc4d7a48223500be8ff480fc535b6eac7a74c6f5f11057550148",
    "failed": "sha256:fe4c0ea6a3955594c74d9ea4d40cd4a0542baa836f53561332aa7f2108da39d4",
    "unknown": "sha256:ada57eddefb02c65f6af65394a9f5e43e7a08bde1c3f37453668aa7102788f25",
}


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


eproto = load_module("frozen_contract_e_authority_chain", E_ROOT / "authority_chain.py")


def H(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def basis(domain: str, operation: str, scope: str, target_class: str, *, subject: str, target: str, basis_type: str = "policy", authority_conferring: bool = True, current: bool = True, valid: bool = True, **extra):
    out = {
        "basis_type": basis_type,
        "authority_conferring": authority_conferring,
        "subject": subject,
        "domain": domain,
        "operation": operation,
        "scope": scope,
        "target_class": target_class,
        "target": target,
        "current": current,
        "valid": valid,
    }
    out.update(extra)
    return out


def lineage_case(row: dict, *, request_basis: dict | None, request_target: str | None = None, request_source_hash: str | None = None) -> dict:
    target = f"{row['contract_d']['target']['id']}@{row['contract_d']['target']['content_sha256']}"
    raw = json.dumps(
        {
            "a_handoff_id": row["a_handoff_id"],
            "a_handoff_sha256": row["a_handoff_sha256"],
            "c_sha256": row["c_sha256"],
            "d_target": row["contract_d"]["target"],
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    h = H(raw)
    subject = "pipeline-decision-consumer"
    observation = {
        "id": "o1",
        "authority_kind": "observation",
        "producer_type": "source_observer",
        "status": "established",
        "source_hash": h,
        "dependencies": [],
    }
    measurement = {
        "id": "m1",
        "authority_kind": "measurement",
        "producer_type": "language_instrument",
        "status": "established",
        "source_hash": h,
        "subject": subject,
        "domain": "measurement",
        "operation": "bind",
        "scope": "claim",
        "target_class": "contract_d_decision",
        "target": target,
        "dependencies": ["o1"],
        "basis": basis("measurement", "bind", "claim", "contract_d_decision", subject=subject, target=target),
    }
    proposal = {"id": "p1", "dimension": "role_binding", "atom": target}
    semantic = {
        "id": "s1",
        "authority_kind": "semantic",
        "producer_type": "semantic_validator",
        "status": "established",
        "source_hash": h,
        "subject": subject,
        "domain": "semantic",
        "operation": "interpret",
        "scope": "claim",
        "target_class": "contract_d_decision",
        "target": target,
        "dependencies": ["m1"],
        "proposal_id": "p1",
        "claim_level": "narrator_fact",
        "preserves_embedding": False,
        "promotion_source": "independent_semantic_validation",
        "basis": basis(
            "semantic",
            "interpret",
            "claim",
            "contract_d_decision",
            subject=subject,
            target=target,
            semantic_dimensions=["role_binding"],
            allowed_embeddings=[],
        ),
    }
    decision_receipt = {
        "id": "d1",
        "authority_kind": "decision",
        "producer_type": "decision_engine",
        "status": "established",
        "source_hash": h,
        "subject": subject,
        "domain": "decision",
        "operation": "decide",
        "scope": "claim",
        "target_class": "contract_d_decision",
        "target": target,
        "dependencies": ["s1"],
        "basis": basis("decision", "decide", "claim", "contract_d_decision", subject=subject, target=target),
    }
    request = {
        "authority_kind": "action",
        "producer_type": "action_authorizer",
        "source_hash": request_source_hash or h,
        "subject": subject,
        "domain": "decision_use",
        "operation": "authorize_use",
        "scope": "claim",
        "target_class": "contract_d_decision",
        "target": request_target or target,
        "dependencies": ["d1"],
        "basis": request_basis or {},
    }
    return {
        "id": "PIPELINE-E",
        "family": "contract_a_pipeline_authority_boundary",
        "raw_source": raw,
        "source_hash": h,
        "proposals": [proposal],
        "receipts": [observation, measurement, semantic, decision_receipt],
        "conflicts": [],
        "residues": [],
        "comparison_receipts": [],
        "request": request,
    }


def check_a_lineage(row: dict) -> None:
    state = row["a_state"]
    if row["a_handoff_sha256"] != EXPECTED_A[state]:
        raise AssertionError(f"stale/forged Contract A lineage for {row['case_name']}:{row['target']['proposition_id']}")
    if row["contract_d"]["target"]["id"] != row["target"]["proposition_id"]:
        raise AssertionError("Contract D target id no longer matches frozen A proposition")
    if row["contract_d"]["target"]["content_sha256"] != row["target"]["text_sha256"]:
        raise AssertionError("Contract D target hash no longer matches frozen A proposition")
    if row["contract_d"]["input_authority"]["immutable_id"] != row["c_sha256"]:
        raise AssertionError("Contract D no longer binds exact Contract C object")


def e_eval(case: dict) -> dict:
    return eproto.evaluate(copy.deepcopy(case))


def main() -> int:
    decision_doc = json.loads((OUT / "DECISIONS.json").read_text())
    results = []

    for row in decision_doc["rows"]:
        check_a_lineage(row)
        d = row["contract_d"]
        validate_decision(d)
        canonical_json_bytes(d)
        expectation = ApplicabilityExpectation(
            d["input_authority"],
            d["policy"],
            d["target"],
            d["effect"]["type"] if d.get("effect") else None,
            d["effect"]["params"] if d.get("effect") else None,
        )
        consumed = consume(d, expectation)
        if consumed["outcome"] not in {"clear", "hold", "failed", "candidate_for_authorization"}:
            raise AssertionError(f"unexpected Contract D consumer outcome: {consumed}")

        target = f"{d['target']['id']}@{d['target']['content_sha256']}"
        subject = "pipeline-decision-consumer"
        grant = basis(
            "decision_use",
            "authorize_use",
            "claim",
            "contract_d_decision",
            subject=subject,
            target=target,
            basis_type="grant",
            authority_domain="action",
        )
        positive = lineage_case(row, request_basis=grant)
        got_positive = e_eval(positive)
        assert got_positive["allowed"] is True, got_positive

        no_basis = lineage_case(row, request_basis={})
        got_no_basis = e_eval(no_basis)
        assert got_no_basis["allowed"] is False, got_no_basis

        a_only = basis(
            "decision_use",
            "authorize_use",
            "claim",
            "contract_d_decision",
            subject=subject,
            target=target,
            basis_type="supporting_artifact",
            authority_conferring=False,
            authority_domain="action",
            asserted_source="contract_a_producer_declaration",
        )
        got_a_only = e_eval(lineage_case(row, request_basis=a_only))
        assert got_a_only["allowed"] is False, got_a_only

        wrong_target = target + "#substituted"
        got_wrong_target = e_eval(lineage_case(row, request_basis=grant, request_target=wrong_target))
        assert got_wrong_target["allowed"] is False, got_wrong_target

        base_case = lineage_case(row, request_basis=grant)
        got_wrong_source = e_eval(lineage_case(row, request_basis=grant, request_source_hash="0" * 64))
        assert got_wrong_source["allowed"] is False, got_wrong_source

        forged = copy.deepcopy(row)
        forged["a_handoff_sha256"] = "sha256:" + "f" * 64
        forged_lineage_rejected = False
        try:
            check_a_lineage(forged)
        except AssertionError:
            forged_lineage_rejected = True
        assert forged_lineage_rejected

        results.append(
            {
                "case_name": row["case_name"],
                "a_state": row["a_state"],
                "proposition_id": row["target"]["proposition_id"],
                "contract_d_outcome": consumed["outcome"],
                "independent_e_grant_allowed": got_positive["allowed"],
                "no_e_basis_rejected": not got_no_basis["allowed"],
                "a_declaration_as_basis_rejected": not got_a_only["allowed"],
                "e_target_substitution_rejected": not got_wrong_target["allowed"],
                "e_source_lineage_mismatch_rejected": not got_wrong_source["allowed"],
                "forged_a_handoff_rejected_before_e": forged_lineage_rejected,
                "e_raw_source_preserved": got_positive["raw_source"] == base_case["raw_source"],
                "e_proposals_preserved": got_positive["proposals"] == base_case["proposals"],
            }
        )

    baseline = [r for r in results if r["case_name"] == "declared"]
    hostile = [r for r in results if r["case_name"] == "declared-hostile-excluded-metadata"]
    assert [(r["proposition_id"], r["independent_e_grant_allowed"], r["a_declaration_as_basis_rejected"]) for r in baseline] == [
        (r["proposition_id"], r["independent_e_grant_allowed"], r["a_declaration_as_basis_rejected"]) for r in hostile
    ]

    terminal = "SUPPORTED_FOR_PROMOTION"
    report = {
        "schema": "contract-a-rc2-contract-e-gate-results-v1",
        "terminal_gate": terminal,
        "results": results,
        "excluded_from_primary_score": {
            "qualification_subject_scope": "CONTRACT_E_UNDERDETERMINED",
            "surplus_multiple_conferring_records": "CONTRACT_E_UNDERDETERMINED",
        },
        "classifications": ["AGREEMENT", "CONTRACT_E_UNDERDETERMINED", "REPRESENTATION_ONLY_DIFFERENCE"],
    }
    (OUT / "GATE-RESULTS.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", "terminal_gate": terminal, "rows": len(results)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
