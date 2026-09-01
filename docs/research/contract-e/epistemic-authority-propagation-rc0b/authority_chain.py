from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Tuple

CONFERRING_BASIS_TYPES = {"grant", "policy", "delegation"}
PRODUCER_ALLOWED = {
    "source_observer": {"observation"},
    "language_instrument": {"measurement"},
    "semantic_validator": {"semantic"},
    "comparison_engine": {"comparison"},
    "authority_resolver": {"resolution"},
    "composition_governor": {"composition"},
    "decision_engine": {"decision"},
    "action_authorizer": {"action"},
    "outcome_verifier": {"verification"},
    "executor_reporter": {"measurement"},
}
EMBEDDINGS = {"quantifier", "modality", "probability", "permission", "conditional", "attribution", "temporal", "quantitative", "exception", "negation"}
COMPARISON_RELATIONS = {
    "EXACT_AGREEMENT", "SEMANTIC_EQUIVALENCE", "COMPATIBLE_PARTIAL_OVERLAP", "COMPLEMENTARY_ORTHOGONAL",
    "GRANULARITY_MISMATCH", "SLOT_BOUNDARY_DISAGREEMENT", "SCOPE_ATTACHMENT_DISAGREEMENT",
    "ROLE_BINDING_DISAGREEMENT", "OPERATOR_VALUE_DISAGREEMENT", "POLARITY_DISAGREEMENT",
    "JURISDICTION_DISAGREEMENT", "PROVENANCE_OR_VISIBILITY_DISAGREEMENT", "CONTRADICTION", "INCOMMENSURABLE",
}


def _idx(case: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {r["id"]: r for r in case.get("receipts", [])}


def _basis_complete_and_conferring(basis: Dict[str, Any]) -> bool:
    required = {"basis_type", "authority_conferring", "subject", "domain", "operation", "scope", "target_class", "current", "valid"}
    return required.issubset(basis) and basis.get("basis_type") in CONFERRING_BASIS_TYPES and basis.get("authority_conferring") is True and basis.get("current") is True and basis.get("valid") is True


def _basis_matches(node: Dict[str, Any], basis: Dict[str, Any]) -> bool:
    if not _basis_complete_and_conferring(basis):
        return False
    for key in ("subject", "domain", "operation", "scope", "target_class"):
        if node.get(key) is not None and basis.get(key) != node.get(key):
            return False
    if basis.get("target") is not None and basis.get("target") != node.get("target"):
        return False
    return True


def _dep_nodes(case: Dict[str, Any], node: Dict[str, Any]):
    idx = _idx(case)
    ids = list(node.get("dependencies", []))
    deps = [idx[x] for x in ids if x in idx]
    return deps, len(deps) == len(ids)


def _validate_receipt(case: Dict[str, Any], rid: str, memo: Dict[str, Tuple[bool, str]], stack: set[str]):
    if rid in memo:
        return memo[rid]
    if rid in stack:
        return False, "authority_lineage_cycle"
    node = _idx(case).get(rid)
    if node is None:
        return False, "authority_lineage_missing_dependency"
    next_stack = set(stack)
    next_stack.add(rid)
    result = _validate_node(case, node, memo, next_stack)
    memo[rid] = result
    return result


def _validate_deps(case: Dict[str, Any], node: Dict[str, Any], memo, stack):
    deps, complete = _dep_nodes(case, node)
    if not complete:
        return False, "authority_lineage_missing_dependency", []
    for dep in deps:
        ok, why = _validate_receipt(case, dep["id"], memo, stack)
        if not ok:
            return False, why, deps
    return True, "dependencies_valid", deps


def _validate_node(case: Dict[str, Any], node: Dict[str, Any], memo, stack):
    kind = node.get("authority_kind")
    producer = node.get("producer_type")
    if kind not in PRODUCER_ALLOWED.get(producer, set()):
        return False, "producer_authority_ceiling"
    if node.get("source_hash") != case.get("source_hash"):
        return False, "source_identity_mismatch"

    if kind == "observation":
        if producer != "source_observer":
            return False, "observation_root_not_independent"
        if node.get("dependencies"):
            return False, "observation_root_has_dependencies"
        return True, "observation_lineage_valid"

    ok, why, deps = _validate_deps(case, node, memo, stack)
    if not ok:
        return False, why

    if kind == "comparison":
        if len(deps) < 2 or any(d.get("authority_kind") != "measurement" for d in deps):
            return False, "comparison_requires_measurements"
        if node.get("relation") not in COMPARISON_RELATIONS:
            return False, "comparison_relation_unknown"
        return True, "comparison_lineage_valid"

    basis = node.get("basis", {})
    if not _basis_matches(node, basis):
        return False, "authority_conferring_basis_invalid"

    if kind == "measurement":
        if not deps or any(d.get("authority_kind") != "observation" for d in deps):
            return False, "measurement_requires_observation"
        return True, "measurement_lineage_valid"

    if kind == "semantic":
        if not deps or any(d.get("authority_kind") != "measurement" for d in deps):
            return False, "semantic_requires_measurement"
        if node.get("promotion_source") == "comparison_agreement":
            return False, "agreement_has_no_truth_authority"
        proposal = {p["id"]: p for p in case.get("proposals", [])}.get(node.get("proposal_id"))
        if proposal is None:
            return False, "semantic_proposal_missing"
        dim = proposal.get("dimension")
        if dim not in set(basis.get("semantic_dimensions", [])):
            return False, "semantic_dimension_not_covered"
        emb = proposal.get("embedding")
        if emb in EMBEDDINGS:
            if node.get("claim_level") == "narrator_fact" or not node.get("preserves_embedding", False):
                return False, "embedding_scope_laundering"
            if emb not in set(basis.get("allowed_embeddings", [])):
                return False, "embedding_not_covered_by_basis"
        return True, "semantic_lineage_valid"

    if kind == "resolution":
        if producer != "authority_resolver":
            return False, "resolver_producer_invalid"
        if basis.get("domain") != "resolution" or basis.get("operation") != "resolve":
            return False, "resolver_basis_mismatch"
        if not node.get("resolves_ids"):
            return False, "resolver_targets_missing"
        if not deps or any(d.get("authority_kind") not in {"measurement", "semantic", "comparison"} for d in deps):
            return False, "resolution_dependency_invalid"
        return True, "resolution_lineage_valid"

    if kind == "composition":
        if not deps or any(d.get("authority_kind") not in {"semantic", "composition"} for d in deps):
            return False, "composition_requires_semantics"
        if set(node.get("component_dimensions", [])) != set(basis.get("component_dimensions", [])):
            return False, "composition_dimensions_not_covered"
        if not basis.get("composition_rule"):
            return False, "composition_rule_missing"
        return True, "composition_lineage_valid"

    if kind == "decision":
        if not deps or any(d.get("authority_kind") not in {"semantic", "composition"} for d in deps):
            return False, "decision_requires_semantics"
        return True, "decision_lineage_valid"

    if kind == "action":
        if not deps or any(d.get("authority_kind") != "decision" for d in deps):
            return False, "action_requires_decision"
        if basis.get("authority_domain") not in {"action", "execution"}:
            return False, "decision_does_not_confer_execution_authority"
        return True, "action_lineage_valid"

    if kind == "verification":
        if not deps or any(d.get("authority_kind") != "observation" for d in deps):
            return False, "verification_requires_observation"
        if any(d.get("producer_type") == "executor_reporter" for d in deps):
            return False, "executor_report_not_verification_authority"
        if basis.get("authority_domain") != "verification":
            return False, "verification_domain_mismatch"
        return True, "verification_lineage_valid"

    return False, "unsupported_authority_kind"


def _authorized_resolutions(case: Dict[str, Any], request: Dict[str, Any], memo):
    resolved = set()
    for rid in request.get("resolver_receipt_ids", []):
        ok, _ = _validate_receipt(case, rid, memo, set())
        if ok:
            r = _idx(case)[rid]
            if r.get("authority_kind") == "resolution":
                resolved.update(r.get("resolves_ids", []))
    return resolved


def _blocking(case, resolved):
    residues = [r["id"] for r in case.get("residues", []) if r.get("relevant", True) and r.get("status") in {"unresolved", "contested"} and r["id"] not in resolved]
    conflicts = [c["id"] for c in case.get("conflicts", []) if c.get("relevant", True) and c.get("status") in {"unresolved", "contested"} and c["id"] not in resolved]
    return residues, conflicts


def _snapshot(case, allowed, reason, request):
    return {
        "allowed": allowed,
        "status": "established" if allowed else "insufficient_authority",
        "reason": reason,
        "authority_kind": request.get("authority_kind") if allowed else None,
        "raw_source": deepcopy(case.get("raw_source")),
        "proposals": deepcopy(case.get("proposals", [])),
        "conflicts": deepcopy(case.get("conflicts", [])),
        "residues": deepcopy(case.get("residues", [])),
        "comparison_receipts": deepcopy(case.get("comparison_receipts", [])),
    }


def evaluate(case: Dict[str, Any]):
    request = dict(case["request"])
    request.setdefault("id", "__request__")
    memo = {}
    resolved = _authorized_resolutions(case, request, memo)
    blocking_residues, blocking_conflicts = _blocking(case, resolved)
    if request.get("authority_kind") in {"semantic", "composition", "decision", "action", "verification"}:
        if blocking_residues:
            return _snapshot(case, False, "relevant_residue_unresolved", request)
        if blocking_conflicts:
            return _snapshot(case, False, "relevant_conflict_unresolved", request)
    ok, why = _validate_node(case, request, memo, set())
    return _snapshot(case, ok, f"{request['authority_kind']}_authority_established" if ok else why, request)


def status_flag_control(case: Dict[str, Any]):
    req = case["request"]
    idx = _idx(case)
    deps = [idx.get(x) for x in req.get("dependencies", [])]
    allowed = bool(deps) and all(d and d.get("status") == "established" for d in deps)
    return _snapshot(case, allowed, "status_flag_control", req)


def bare_resolution_id_control(case: Dict[str, Any]):
    req = dict(case["request"])
    bare = set(req.get("resolved_residue_ids", [])) | set(req.get("resolved_conflict_ids", []))
    residues, conflicts = _blocking(case, bare)
    if residues or conflicts:
        return _snapshot(case, False, "bare_resolution_id_control", req)
    idx = _idx(case)
    deps = [idx.get(x) for x in req.get("dependencies", [])]
    allowed = (not req.get("dependencies") or all(d and d.get("status") == "established" for d in deps)) and bool(req.get("basis", {}))
    return _snapshot(case, allowed, "bare_resolution_id_control", req)


def any_basis_control(case: Dict[str, Any]):
    req = case["request"]
    b = req.get("basis", {})
    required = {"subject", "domain", "operation", "scope", "target_class", "current", "valid"}
    allowed = required.issubset(b) and b.get("current") is True and b.get("valid") is True
    return _snapshot(case, allowed, "any_basis_control", req)
