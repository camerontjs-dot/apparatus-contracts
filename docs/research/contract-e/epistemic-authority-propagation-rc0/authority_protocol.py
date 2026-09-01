from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Iterable

PRODUCER_ALLOWED = {
    "source_observer": {"observation"},
    "language_instrument": {"measurement"},
    "comparison_engine": {"comparison"},
    "semantic_validator": {"semantic"},
    "composition_governor": {"composition"},
    "decision_engine": {"decision"},
    "action_authorizer": {"action"},
    "outcome_verifier": {"verification"},
    "executor_reporter": {"measurement"},
}

EMBEDDINGS = {
    "quantifier", "modality", "probability", "permission", "conditional",
    "attribution", "temporal", "quantitative", "exception", "negation",
}

COMPARISON_RELATIONS = {
    "EXACT_AGREEMENT", "SEMANTIC_EQUIVALENCE", "COMPATIBLE_PARTIAL_OVERLAP",
    "COMPLEMENTARY_ORTHOGONAL", "GRANULARITY_MISMATCH",
    "SLOT_BOUNDARY_DISAGREEMENT", "SCOPE_ATTACHMENT_DISAGREEMENT",
    "ROLE_BINDING_DISAGREEMENT", "OPERATOR_VALUE_DISAGREEMENT",
    "POLARITY_DISAGREEMENT", "JURISDICTION_DISAGREEMENT",
    "PROVENANCE_OR_VISIBILITY_DISAGREEMENT", "CONTRADICTION", "INCOMMENSURABLE",
}


def _receipt_index(case: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {r["id"]: r for r in case.get("receipts", [])}


def _dep_receipts(case: Dict[str, Any], request: Dict[str, Any]) -> list[Dict[str, Any]]:
    idx = _receipt_index(case)
    return [idx[d] for d in request.get("dependencies", []) if d in idx]


def _basis_complete(basis: Dict[str, Any]) -> bool:
    required = ("subject", "domain", "operation", "scope", "target_class", "current", "valid")
    return all(k in basis for k in required) and basis.get("current") is True and basis.get("valid") is True


def _basis_matches(request: Dict[str, Any], basis: Dict[str, Any]) -> bool:
    if not _basis_complete(basis):
        return False
    for key in ("subject", "domain", "operation", "scope", "target_class"):
        req = request.get(key)
        if req is not None and basis.get(key) != req:
            return False
    target = request.get("target")
    exact = basis.get("target")
    if exact is not None and target != exact:
        return False
    return True


def _unresolved_relevant(case: Dict[str, Any], request: Dict[str, Any]) -> list[str]:
    resolved = set(request.get("resolved_residue_ids", []))
    return [
        r["id"] for r in case.get("residues", [])
        if r.get("relevant", True) and r.get("status") in {"unresolved", "contested"} and r["id"] not in resolved
    ]


def _unresolved_conflicts(case: Dict[str, Any], request: Dict[str, Any]) -> list[str]:
    resolved = set(request.get("resolved_conflict_ids", []))
    return [
        c["id"] for c in case.get("conflicts", [])
        if c.get("relevant", True) and c.get("status") in {"unresolved", "contested"} and c["id"] not in resolved
    ]


def _result(case: Dict[str, Any], allowed: bool, status: str, reason: str, request: Dict[str, Any]) -> Dict[str, Any]:
    # Preservation is explicit and mechanically testable: evaluation returns untouched evidence snapshots.
    return {
        "allowed": allowed,
        "status": status,
        "reason": reason,
        "authority_kind": request.get("authority_kind") if allowed else None,
        "subject_id": request.get("subject_id"),
        "raw_source": deepcopy(case.get("raw_source")),
        "proposals": deepcopy(case.get("proposals", [])),
        "conflicts": deepcopy(case.get("conflicts", [])),
        "residues": deepcopy(case.get("residues", [])),
        "comparison_receipts": deepcopy(case.get("comparison_receipts", [])),
    }


def evaluate(case: Dict[str, Any]) -> Dict[str, Any]:
    request = case["request"]
    desired = request["authority_kind"]
    producer = request["producer_type"]

    # Source/provenance must remain present and exact when a source hash is declared.
    raw = case.get("raw_source")
    if raw is None:
        return _result(case, False, "insufficient_authority", "missing_raw_source", request)
    if case.get("source_hash") and request.get("source_hash") != case.get("source_hash"):
        return _result(case, False, "prohibited", "source_identity_mismatch", request)

    # Authority ceilings are capabilities, not confidence/majority scores.
    if desired not in PRODUCER_ALLOWED.get(producer, set()):
        return _result(case, False, "prohibited", "producer_authority_ceiling", request)

    deps = _dep_receipts(case, request)
    if len(deps) != len(request.get("dependencies", [])):
        return _result(case, False, "insufficient_authority", "missing_dependency", request)
    if any(d.get("status") != "established" for d in deps):
        return _result(case, False, "contested", "dependency_not_established", request)

    # Relevant unresolved residue/conflict is sticky across authority transitions.
    if desired in {"semantic", "composition", "decision", "action", "verification"}:
        if _unresolved_relevant(case, request):
            return _result(case, False, "unresolved", "relevant_residue_unresolved", request)
        if _unresolved_conflicts(case, request):
            return _result(case, False, "contested", "relevant_conflict_unresolved", request)

    basis = request.get("basis", {})

    if desired == "observation":
        return _result(case, True, "established", "source_observed", request)

    if desired == "measurement":
        if not any(d.get("authority_kind") == "observation" for d in deps):
            return _result(case, False, "insufficient_authority", "measurement_requires_observation", request)
        if not _basis_matches(request, basis):
            return _result(case, False, "insufficient_authority", "measurement_basis_mismatch", request)
        return _result(case, True, "established", "measurement_authority_established", request)

    if desired == "comparison":
        if len(deps) < 2 or any(d.get("authority_kind") != "measurement" for d in deps):
            return _result(case, False, "insufficient_authority", "comparison_requires_measurements", request)
        if request.get("relation") not in COMPARISON_RELATIONS:
            return _result(case, False, "insufficient_authority", "comparison_relation_unknown", request)
        # This receipt authorizes only a relation between measurements, never source truth.
        return _result(case, True, "established", "measurement_relation_established", request)

    if desired == "semantic":
        if not any(d.get("authority_kind") == "measurement" for d in deps):
            return _result(case, False, "insufficient_authority", "semantic_requires_measurement", request)
        if request.get("promotion_source") == "comparison_agreement":
            return _result(case, False, "prohibited", "agreement_has_no_truth_authority", request)
        if not _basis_matches(request, basis):
            return _result(case, False, "insufficient_authority", "semantic_basis_mismatch", request)
        proposal_id = request.get("proposal_id")
        proposals = {p["id"]: p for p in case.get("proposals", [])}
        if proposal_id not in proposals:
            return _result(case, False, "insufficient_authority", "semantic_proposal_missing", request)
        p = proposals[proposal_id]
        embedding = p.get("embedding")
        if embedding in EMBEDDINGS:
            if request.get("claim_level") == "narrator_fact":
                return _result(case, False, "prohibited", "embedding_scope_laundering", request)
            if not request.get("preserves_embedding", False):
                return _result(case, False, "prohibited", "embedding_scope_laundering", request)
            if embedding not in set(basis.get("allowed_embeddings", [])):
                return _result(case, False, "insufficient_authority", "embedding_not_covered_by_basis", request)
        dimension = p.get("dimension")
        if dimension not in set(basis.get("semantic_dimensions", [])):
            return _result(case, False, "insufficient_authority", "semantic_dimension_not_covered", request)
        return _result(case, True, "established", "semantic_authority_established", request)

    if desired == "composition":
        sem = [d for d in deps if d.get("authority_kind") in {"semantic", "composition"}]
        if len(sem) != len(deps) or not sem:
            return _result(case, False, "insufficient_authority", "composition_requires_semantics", request)
        if not _basis_matches(request, basis):
            return _result(case, False, "insufficient_authority", "composition_basis_mismatch", request)
        needed = set(request.get("component_dimensions", []))
        if needed != set(basis.get("component_dimensions", [])):
            return _result(case, False, "insufficient_authority", "composition_dimensions_not_covered", request)
        if not basis.get("composition_rule"):
            return _result(case, False, "insufficient_authority", "composition_rule_missing", request)
        return _result(case, True, "established", "composition_authority_established", request)

    if desired == "decision":
        if not any(d.get("authority_kind") in {"semantic", "composition"} for d in deps):
            return _result(case, False, "insufficient_authority", "decision_requires_semantic_authority", request)
        if not _basis_matches(request, basis):
            return _result(case, False, "insufficient_authority", "decision_basis_mismatch", request)
        return _result(case, True, "established", "decision_authority_established", request)

    if desired == "action":
        if not any(d.get("authority_kind") == "decision" for d in deps):
            return _result(case, False, "insufficient_authority", "action_requires_decision_dependency", request)
        # Decision dependency is necessary but never sufficient: independent action basis is mandatory.
        if not _basis_matches(request, basis):
            return _result(case, False, "insufficient_authority", "action_basis_mismatch", request)
        if basis.get("authority_domain") not in {"execution", "action"}:
            return _result(case, False, "prohibited", "decision_does_not_confer_execution_authority", request)
        return _result(case, True, "established", "action_authority_established", request)

    if desired == "verification":
        if not any(d.get("authority_kind") == "observation" for d in deps):
            return _result(case, False, "insufficient_authority", "verification_requires_outcome_observation", request)
        if any(d.get("producer_type") == "executor_reporter" for d in deps):
            return _result(case, False, "prohibited", "executor_report_not_verification_authority", request)
        if not _basis_matches(request, basis):
            return _result(case, False, "insufficient_authority", "verification_basis_mismatch", request)
        if basis.get("authority_domain") != "verification":
            return _result(case, False, "prohibited", "verification_domain_mismatch", request)
        return _result(case, True, "established", "verification_authority_established", request)

    return _result(case, False, "prohibited", "unsupported_authority_kind", request)


def transitive_control(case: Dict[str, Any]) -> Dict[str, Any]:
    """Intentionally unsafe: any established upstream receipt promotes any requested authority."""
    request = case["request"]
    deps = _dep_receipts(case, request)
    allowed = bool(deps) and all(d.get("status") == "established" for d in deps)
    return _result(case, allowed, "established" if allowed else "insufficient_authority", "transitive_control", request)


def agreement_control(case: Dict[str, Any]) -> Dict[str, Any]:
    """Intentionally unsafe: two matching proposals can authorize semantic truth."""
    request = case["request"]
    if request.get("authority_kind") != "semantic":
        return evaluate(case)
    atoms = [p.get("atom") for p in case.get("proposals", []) if p.get("atom") is not None]
    allowed = any(atoms.count(a) >= 2 for a in set(atoms))
    return _result(case, allowed, "established" if allowed else "insufficient_authority", "agreement_control", request)


def stage_local_control(case: Dict[str, Any]) -> Dict[str, Any]:
    """Intentionally unsafe: validates only a local basis and ignores inherited ceiling/residue/conflict/scope."""
    request = case["request"]
    allowed = bool(request.get("basis"))
    return _result(case, allowed, "established" if allowed else "insufficient_authority", "stage_local_control", request)
