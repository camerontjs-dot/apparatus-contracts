#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "artifacts" / "contract-a-rc2-contract-e-gate"
LANE = ROOT / "research" / "contract-a-rc2-contract-e-pipeline-20260901"
sys.path.insert(0, str(LANE))
import e_gate as eg  # type: ignore  # noqa: E402

from validators.contract_d_consume import ApplicabilityExpectation, consume  # noqa: E402
from validators.contract_d_core import canonical_json_bytes, validate_decision  # noqa: E402


def exact_grant(row: dict) -> dict:
    d = row["contract_d"]
    target = f"{d['target']['id']}@{d['target']['content_sha256']}"
    return eg.basis(
        "decision_use",
        "authorize_use",
        "claim",
        "contract_d_decision",
        subject="pipeline-decision-consumer",
        target=target,
        basis_type="grant",
        authority_domain="action",
    )


def row_as_gate_shape(row: dict) -> dict:
    return {
        "case_name": row["projection"],
        "a_state": "declared",
        "a_handoff_id": "contract-a-rc2-rsh-supplier-declared",
        "a_handoff_sha256": row["a_handoff_sha256"],
        "a_work_id": row["a_work_id"],
        "c_sha256": row["c_sha256"],
        "target": row["target"],
        "contract_d": row["contract_d"],
    }


def main() -> int:
    doc = json.loads((OUT / "PRESSURE-DECISIONS.json").read_text())
    projections = json.loads((OUT / "PRESSURE-PROJECTIONS.json").read_text())
    rows = doc["rows"]
    by_key = {(r["projection"], r["target"]["proposition_id"]): r for r in rows}

    parent_id = next(
        t["proposition_id"]
        for p in projections["projections"]
        if p["projection"] == "declared-parent-only"
        for t in p["targets"]
    )
    atom_ids = [
        t["proposition_id"]
        for p in projections["projections"]
        if p["projection"] == "declared-atoms-only"
        for t in p["targets"]
    ]

    results = []
    for row in rows:
        shaped = row_as_gate_shape(row)
        eg.check_a_lineage(shaped)
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

        grant = exact_grant(row)
        pos = eg.e_eval(eg.lineage_case(shaped, request_basis=grant))
        neg = eg.e_eval(eg.lineage_case(shaped, request_basis={}))
        a_only = eg.basis(
            "decision_use",
            "authorize_use",
            "claim",
            "contract_d_decision",
            subject="pipeline-decision-consumer",
            target=f"{d['target']['id']}@{d['target']['content_sha256']}",
            basis_type="supporting_artifact",
            authority_conferring=False,
            authority_domain="action",
            asserted_source="contract_a_declaration",
        )
        a_only_result = eg.e_eval(eg.lineage_case(shaped, request_basis=a_only))
        assert pos["allowed"] is True
        assert neg["allowed"] is False
        assert a_only_result["allowed"] is False
        results.append(
            {
                "projection": row["projection"],
                "proposition_id": row["target"]["proposition_id"],
                "role": row["target"]["role"],
                "contract_d_outcome": consumed["outcome"],
                "exact_independent_grant_allowed": pos["allowed"],
                "no_basis_rejected": not neg["allowed"],
                "a_only_rejected": not a_only_result["allowed"],
            }
        )

    parent_alone = by_key[("declared-parent-only", parent_id)]
    parent_joint = by_key[("declared-parent-plus-atoms", parent_id)]
    assert parent_alone["target"] == parent_joint["target"]
    for atom_id in atom_ids:
        atom_alone = by_key[("declared-atoms-only", atom_id)]
        atom_joint = by_key[("declared-parent-plus-atoms", atom_id)]
        assert atom_alone["target"] == atom_joint["target"]

    parent_shape = row_as_gate_shape(parent_joint)
    parent_grant = exact_grant(parent_joint)
    cross_use = []
    for atom_id in atom_ids:
        atom_joint = by_key[("declared-parent-plus-atoms", atom_id)]
        atom_shape = row_as_gate_shape(atom_joint)
        parent_on_atom = eg.e_eval(eg.lineage_case(atom_shape, request_basis=parent_grant))
        assert parent_on_atom["allowed"] is False
        atom_grant = exact_grant(atom_joint)
        atom_on_parent = eg.e_eval(eg.lineage_case(parent_shape, request_basis=atom_grant))
        assert atom_on_parent["allowed"] is False
        cross_use.append(
            {
                "atom_id": atom_id,
                "parent_grant_on_atom_rejected": True,
                "atom_grant_on_parent_rejected": True,
            }
        )

    atom_cross_use = []
    for source_atom_id in atom_ids:
        source_row = by_key[("declared-parent-plus-atoms", source_atom_id)]
        source_grant = exact_grant(source_row)
        for target_atom_id in atom_ids:
            if target_atom_id == source_atom_id:
                continue
            target_shape = row_as_gate_shape(by_key[("declared-parent-plus-atoms", target_atom_id)])
            got = eg.e_eval(eg.lineage_case(target_shape, request_basis=source_grant))
            assert got["allowed"] is False
            atom_cross_use.append(
                {
                    "source_atom_id": source_atom_id,
                    "target_atom_id": target_atom_id,
                    "cross_atom_grant_rejected": True,
                }
            )

    assert all(r["a_only_rejected"] for r in results)

    reorder = projections["resealed_reorder_control"]
    assert reorder["resealed_handoff_sha256"] != reorder["original_handoff_sha256"]
    forged = copy.deepcopy(parent_shape)
    forged["a_handoff_sha256"] = reorder["resealed_handoff_sha256"]
    old_binding_rejected = False
    try:
        eg.check_a_lineage(forged)
    except AssertionError:
        old_binding_rejected = True
    assert old_binding_rejected

    report = {
        "schema": "contract-a-rc2-contract-e-parent-atom-pressure-results-v1",
        "terminal_gate": "SUPPORTED_FOR_PROMOTION",
        "results": results,
        "cross_use": cross_use,
        "atom_cross_use": atom_cross_use,
        "projection_invariance": {
            "parent_identity_same_alone_and_joint": True,
            "atom_identity_same_alone_and_joint": True,
            "no_synthetic_parent_authorization_from_atoms": True,
            "no_synthetic_atom_authorization_from_parent": True,
        },
        "resealed_reorder": {
            **reorder,
            "old_a_binding_rejected": old_binding_rejected,
        },
        "excluded_from_primary_score": {
            "qualification_subject_scope": "CONTRACT_E_UNDERDETERMINED",
            "surplus_multiple_conferring_records": "CONTRACT_E_UNDERDETERMINED",
        },
        "nonclaims": [
            "No composition rule is inferred from E authority outcomes.",
            "Parent and atoms are compared as separate exact targets; their authorizations are not unioned.",
            "No Contract E production authority or Contract A promotion occurs in this run.",
        ],
    }
    (OUT / "PRESSURE-RESULTS.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", "terminal_gate": report["terminal_gate"], "rows": len(results)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
