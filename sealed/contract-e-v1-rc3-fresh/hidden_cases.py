from __future__ import annotations

from copy import deepcopy
from typing import Any


def _target(r, label: str = "target:hidden", ref_id: str = "T") -> dict[str, Any]:
    kind = "test_target"
    version = "1"
    return {
        "ref_id": ref_id,
        "kind": kind,
        "version": version,
        "immutable_id": label,
        "identity_sha256": r.reference_identity(kind, version, label),
    }


def _seal(r, state: dict[str, Any]) -> dict[str, Any]:
    out = deepcopy(state)
    out["authority_state_id"] = r.authority_state_identity(out)
    return out


def _state(
    r,
    *,
    subject: str = "actor:hidden",
    domain: str = "knowledge",
    operation: str = "knowledge.cite_as_evidence",
    scope: str = "claim",
    target_class: str = "test_target",
    target: dict[str, Any] | None = None,
    valid_from: str = "2026-09-02T17:00:00Z",
    valid_until: str | None = "2026-09-02T19:00:00Z",
    revoked_at: str | None = None,
    delegates: tuple[str, ...] = (),
) -> tuple[dict[str, Any], dict[str, Any]]:
    target = deepcopy(target or _target(r))
    records = [{
        "id": "authority:root",
        "basis_type": "policy",
        "subject_id": subject,
        "domain": domain,
        "operation": operation,
        "scope": scope,
        "target_class": target_class,
        "target_ref": target["identity_sha256"],
        "valid_from": valid_from,
        "valid_until": valid_until,
        "revoked_at": revoked_at,
        "parent_id": None,
        "delegated_by": None,
    }]
    parent_id = "authority:root"
    parent_subject = subject
    for index, child_subject in enumerate(delegates, 1):
        records.append({
            "id": f"authority:delegation:{index}",
            "basis_type": "delegation",
            "subject_id": child_subject,
            "domain": domain,
            "operation": operation,
            "scope": scope,
            "target_class": target_class,
            "target_ref": target["identity_sha256"],
            "valid_from": valid_from,
            "valid_until": valid_until,
            "revoked_at": revoked_at,
            "parent_id": parent_id,
            "delegated_by": parent_subject,
        })
        parent_id = f"authority:delegation:{index}"
        parent_subject = child_subject
    state = {
        "schema": r.STATE_SCHEMA,
        "authority_state_id": "sha256:" + "0" * 64,
        "records": records,
    }
    return _seal(r, state), target


def _request(
    r,
    state: dict[str, Any],
    target: dict[str, Any],
    *,
    at: str = "2026-09-02T18:00:00Z",
    subject: str | None = None,
    domain: str | None = None,
    operation: str | None = None,
    scope: str | None = None,
    target_class: str | None = None,
    target_identity: str | None = None,
    references: list[dict[str, Any]] | None = None,
    supporting: list[dict[str, Any]] | None = None,
    conflicts: list[dict[str, Any]] | None = None,
    residues: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    leaf = state["records"][-1] if state.get("records") else {
        "subject_id": "actor:hidden",
        "domain": "knowledge",
        "operation": "knowledge.cite_as_evidence",
        "scope": "claim",
        "target_class": "test_target",
        "target_ref": target["identity_sha256"],
    }
    return {
        "schema": r.REQUEST_SCHEMA,
        "request_id": "request:hidden",
        "authority_state_id": state["authority_state_id"],
        "evaluation_time": at,
        "subject_id": subject or leaf["subject_id"],
        "jurisdiction": {
            "domain": domain or leaf["domain"],
            "operation": operation or leaf["operation"],
            "scope": scope or leaf["scope"],
            "target_class": target_class or leaf["target_class"],
            "target_ref": target_identity or leaf["target_ref"],
        },
        "references": deepcopy(references if references is not None else [target]),
        "supporting_artifacts": deepcopy(supporting or []),
        "conflicts": deepcopy(conflicts or []),
        "residues": deepcopy(residues or []),
    }


def _add(out, case_id: str, family: str, tags: list[str], state: Any, request: Any) -> None:
    out.append({
        "id": case_id,
        "family": family,
        "tags": tags,
        "state": deepcopy(state),
        "request": deepcopy(request),
    })


def cases(r) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    base, target = _state(r)
    base_req = _request(r, base, target)

    _add(out, "POS-ROOT", "positive", ["root", "exact"], base, base_req)

    delegated, dtarget = _state(r, subject="actor:owner", delegates=("actor:delegate",))
    _add(out, "POS-DELEGATION", "positive", ["delegation"], delegated, _request(r, delegated, dtarget))

    for case_id, kwargs in [
        ("NEG-SUBJECT", {"subject": "actor:other"}),
        ("NEG-DOMAIN", {"domain": "execution"}),
        ("NEG-OPERATION", {"operation": "knowledge.add_verified_tag"}),
        ("NEG-SCOPE", {"scope": "object"}),
        ("NEG-TARGET-CLASS", {"target_class": "other_target"}),
    ]:
        _add(out, case_id, "binding", ["exact-binding"], base, _request(r, base, target, **kwargs))

    other = _target(r, "target:other", "O")
    _add(
        out,
        "NEG-TARGET-REF",
        "binding",
        ["target", "immutable"],
        base,
        _request(r, base, target, target_identity=other["identity_sha256"], references=[other]),
    )

    forged = deepcopy(base)
    forged["authority_state_id"] = "sha256:" + "1" * 64
    _add(out, "NEG-STATE-FORGED-CLAIM", "identity", ["dual-identity", "claimed-vs-recomputed"], forged, _request(r, forged, target))

    req_state_mismatch = deepcopy(base_req)
    req_state_mismatch["authority_state_id"] = "sha256:" + "2" * 64
    _add(out, "NEG-REQUEST-STATE-ID", "identity", ["request-binding"], base, req_state_mismatch)

    malformed_claim = deepcopy(base)
    malformed_claim["authority_state_id"] = "bad-identity"
    _add(out, "NEG-MALFORMED-CLAIM", "identity", ["dual-identity", "recomputed-preserved"], malformed_claim, base_req)

    structural = deepcopy(base)
    structural["unknown_state_field"] = True
    _add(out, "NEG-STATE-STRUCTURAL-JCS", "identity", ["recomputed-preserved", "structural"], structural, base_req)

    # Whole-second currentness controls.
    future, ft = _state(r, valid_from="2026-09-02T18:00:01Z")
    _add(out, "NEG-NOT-YET-VALID", "currentness", ["valid_from"], future, _request(r, future, ft))
    expired, et = _state(r, valid_until="2026-09-02T17:59:59Z")
    _add(out, "NEG-EXPIRED", "currentness", ["valid_until"], expired, _request(r, expired, et))
    revoked, rt = _state(r, revoked_at="2026-09-02T18:00:00Z")
    _add(out, "NEG-AT-REVOCATION", "currentness", ["revocation"], revoked, _request(r, revoked, rt))
    at_start, ast = _state(r, valid_from="2026-09-02T18:00:00Z")
    _add(out, "POS-AT-VALID-FROM", "currentness", ["inclusive"], at_start, _request(r, at_start, ast))
    at_end, aet = _state(r, valid_until="2026-09-02T18:00:00Z")
    _add(out, "POS-AT-VALID-UNTIL", "currentness", ["inclusive"], at_end, _request(r, at_end, aet))

    # Exact fractional cases, including all three RC2 terminal falsifiers.
    s, t = _state(r, valid_from="2026-09-02T18:00:00.1234568Z")
    _add(out, "FRACTION-PRE-VALID-FROM", "fractional-currentness", ["rc2-falsifier", "false-permit-sentinel"], s, _request(r, s, t, at="2026-09-02T18:00:00.1234567Z"))
    s, t = _state(r, valid_until="2026-09-02T18:00:00.1234567Z")
    _add(out, "FRACTION-POST-VALID-UNTIL", "fractional-currentness", ["rc2-falsifier", "false-permit-sentinel"], s, _request(r, s, t, at="2026-09-02T18:00:00.1234568Z"))
    s, t = _state(r, revoked_at="2026-09-02T18:00:00.1234568Z")
    _add(out, "FRACTION-PRE-REVOCATION", "fractional-currentness", ["rc2-falsifier", "false-reject-sentinel"], s, _request(r, s, t, at="2026-09-02T18:00:00.1234567Z"))
    s, t = _state(r, valid_from="2026-09-02T18:00:00.1234567Z")
    _add(out, "FRACTION-EQUAL-VALID-FROM", "fractional-currentness", ["inclusive", "trailing-zero"], s, _request(r, s, t, at="2026-09-02T18:00:00.123456700Z"))
    s, t = _state(r, valid_until="2026-09-02T18:00:00.1234567Z")
    _add(out, "FRACTION-EQUAL-VALID-UNTIL", "fractional-currentness", ["inclusive", "trailing-zero"], s, _request(r, s, t, at="2026-09-02T18:00:00.123456700Z"))
    s, t = _state(r, revoked_at="2026-09-02T18:00:00.1234567Z")
    _add(out, "FRACTION-EQUAL-REVOCATION", "fractional-currentness", ["revocation", "trailing-zero"], s, _request(r, s, t, at="2026-09-02T18:00:00.123456700Z"))
    s, t = _state(r, valid_until="2026-09-02T18:00:00.1000000000000000000Z")
    _add(out, "FRACTION-ULTRA-PRECISION-AFTER", "fractional-currentness", ["arbitrary-precision"], s, _request(r, s, t, at="2026-09-02T18:00:00.1000000000000000001Z"))

    bad_time = deepcopy(base_req)
    bad_time["evaluation_time"] = "2026-09-02T18:00:60Z"
    _add(out, "NEG-LEAP-SECOND", "timestamp-shape", ["leap-second"], base, bad_time)
    bad_time = deepcopy(base_req)
    bad_time["evaluation_time"] = "2026-02-30T18:00:00Z"
    _add(out, "NEG-INVALID-CALENDAR", "timestamp-shape", ["calendar"], base, bad_time)

    # Delegation lineage/boundary failures.
    for case_id, mutate in [
        ("NEG-DELEGATION-PARENT", lambda s: s["records"][1].__setitem__("parent_id", "missing")),
        ("NEG-DELEGATION-BY", lambda s: s["records"][1].__setitem__("delegated_by", "actor:other")),
        ("NEG-DELEGATION-BOUNDS", lambda s: s["records"][1].__setitem__("scope", "other")),
        ("NEG-DUPLICATE-RECORD-ID", lambda s: s["records"][1].__setitem__("id", "authority:root")),
        ("NEG-NONDELEGATION-CHILD", lambda s: s["records"][1].__setitem__("basis_type", "policy")),
    ]:
        bad = deepcopy(delegated)
        mutate(bad)
        bad = _seal(r, bad)
        _add(out, case_id, "delegation", ["lineage", "non-amplification"], bad, _request(r, bad, dtarget))

    surplus = deepcopy(base)
    peer = deepcopy(base["records"][0])
    peer["id"] = "authority:peer"
    peer["subject_id"] = "actor:peer"
    surplus["records"].append(peer)
    surplus = _seal(r, surplus)
    _add(out, "NEG-SURPLUS-PEER", "authority-shape", ["surplus-peer"], surplus, _request(r, surplus, target))

    # Immutable references and request-local uniqueness.
    bad_ref = deepcopy(base_req)
    bad_ref["references"][0]["immutable_id"] = "tampered"
    _add(out, "NEG-REF-IDENTITY", "request-integrity", ["reference-identity"], base, bad_ref)
    dup_ref = deepcopy(base_req)
    dup_ref["references"].append(deepcopy(dup_ref["references"][0]))
    _add(out, "NEG-DUPLICATE-REF-ID", "request-integrity", ["uniqueness", "preserve-shaped"], base, dup_ref)
    missing_ref = deepcopy(base_req)
    missing_ref["references"] = [_target(r, "target:different", "O")]
    _add(out, "NEG-MISSING-TARGET-REF", "request-integrity", ["target-resolution"], base, missing_ref)

    decision_ref = _target(r, "decision:hidden", "D")
    support = [{"id": "support:D", "artifact_type": "contract_d_candidate", "ref_id": "D"}]
    supported = _request(r, base, target, references=[target, decision_ref], supporting=support)
    _add(out, "POS-NONCONFERRING-SUPPORT", "support", ["support"], base, supported)
    dup_support = deepcopy(supported)
    dup_support["supporting_artifacts"].append(deepcopy(dup_support["supporting_artifacts"][0]))
    _add(out, "NEG-DUPLICATE-SUPPORT-ID", "support", ["uniqueness"], base, dup_support)
    unknown_support = _request(r, base, target, supporting=support)
    _add(out, "NEG-UNKNOWN-SUPPORT-REF", "support", ["local-resolution"], base, unknown_support)

    invalid_state = _seal(r, {"schema": r.STATE_SCHEMA, "authority_state_id": "sha256:" + "0" * 64, "records": []})
    support_req = deepcopy(supported)
    support_req["authority_state_id"] = invalid_state["authority_state_id"]
    _add(out, "NEG-SUPPORT-CANNOT-CONFER", "support", ["nonconferring", "false-permit-sentinel"], invalid_state, support_req)

    prior_ref = _target(r, "receipt:prior", "P")
    prior_support = [{"id": "support:P", "artifact_type": "prior_authorization_receipt", "ref_id": "P"}]
    prior_req = _request(r, base, target, references=[target, prior_ref], supporting=prior_support)
    prior_req["authority_state_id"] = invalid_state["authority_state_id"]
    _add(out, "NEG-PRIOR-RECEIPT-CANNOT-CONFER", "support", ["prior-receipt", "nonconferring"], invalid_state, prior_req)

    # Blockers, including explicit fail-closed resolution semantics.
    _add(out, "NEG-RELEVANT-CONFLICT", "blocker", ["conflict"], base, _request(r, base, target, conflicts=[{"id": "c1", "relevant": True, "status": "unresolved"}]))
    _add(out, "NEG-RELEVANT-RESIDUE", "blocker", ["residue"], base, _request(r, base, target, residues=[{"id": "r1", "relevant": True, "status": "contested"}]))
    _add(out, "POS-IRRELEVANT-BLOCKERS", "blocker", ["preservation"], base, _request(r, base, target, conflicts=[{"id": "c0", "relevant": False, "status": "unresolved"}], residues=[{"id": "r0", "relevant": False, "status": "contested"}]))

    resolution_target = _target(r, "conflict:hidden", "C")
    resolution_state, _ = _state(r, domain="resolution", operation="resolve", scope="case:hidden", target=resolution_target)
    _add(out, "NEG-RESOLUTION-BLOCKER-BYPASS", "blocker", ["resolution", "fail-closed"], resolution_state, _request(r, resolution_state, resolution_target, conflicts=[{"id": "c42", "relevant": True, "status": "unresolved"}]))
    _add(out, "POS-CLEAR-RESOLUTION", "blocker", ["resolution", "clear"], resolution_state, _request(r, resolution_state, resolution_target))

    dup_conflict = _request(r, base, target, conflicts=[{"id": "dup", "relevant": True, "status": "unresolved"}, {"id": "dup", "relevant": True, "status": "contested"}])
    _add(out, "NEG-DUPLICATE-CONFLICT-ID", "request-integrity", ["uniqueness"], base, dup_conflict)
    dup_residue = _request(r, base, target, residues=[{"id": "dup", "relevant": True, "status": "unresolved"}, {"id": "dup", "relevant": True, "status": "contested"}])
    _add(out, "NEG-DUPLICATE-RESIDUE-ID", "request-integrity", ["uniqueness"], base, dup_residue)

    unknown = deepcopy(base_req)
    unknown["future_field"] = True
    _add(out, "NEG-UNKNOWN-REQUEST-FIELD", "request-shape", ["exact-schema", "preservation"], base, unknown)
    resolved = deepcopy(base_req)
    resolved["resolved_conflict_ids"] = ["c1"]
    _add(out, "NEG-RESOLUTION-DISCHARGE-FIELD", "request-shape", ["no-discharge"], base, resolved)

    # Preservation cases on malformed requests.
    malformed_ref = deepcopy(base_req)
    malformed_ref["references"][0]["surprise"] = True
    _add(out, "PRESERVE-MALFORMED-REF-EMPTY", "preservation", ["safe-preservation"], base, malformed_ref)

    malformed_support = deepcopy(base_req)
    malformed_support["supporting_artifacts"] = [{"id": "x", "artifact_type": "a"}]
    _add(out, "PRESERVE-MALFORMED-SUPPORT-EMPTY", "preservation", ["safe-preservation"], base, malformed_support)

    semantically_bad_support = deepcopy(supported)
    semantically_bad_support["supporting_artifacts"][0]["ref_id"] = "missing"
    _add(out, "PRESERVE-SHAPED-UNKNOWN-SUPPORT", "preservation", ["shape-not-semantics"], base, semantically_bad_support)

    # JCS-sensitive malformed-but-canonicalizable observations. These are normative via recomputed id/request hash.
    jcs_state = deepcopy(base)
    jcs_state["numeric_probe"] = 1.0
    _add(out, "JCS-STATE-NUMBER-1", "canonicalization", ["jcs", "recomputed-state"], jcs_state, base_req)

    jcs_request = deepcopy(base_req)
    jcs_request["numeric_probe"] = -0.0
    _add(out, "JCS-REQUEST-NEGATIVE-ZERO", "canonicalization", ["jcs", "request-hash"], base, jcs_request)

    jcs_request = deepcopy(base_req)
    jcs_request["numeric_probe"] = 1e-7
    _add(out, "JCS-REQUEST-SMALL-EXPONENT", "canonicalization", ["jcs", "request-hash"], base, jcs_request)

    jcs_request = deepcopy(base_req)
    jcs_request["numeric_probe"] = 1e20
    _add(out, "JCS-REQUEST-LARGE-NUMBER", "canonicalization", ["jcs", "request-hash"], base, jcs_request)

    unicode_state, unicode_target = _state(r, subject="actor:é")
    _add(out, "POS-UNICODE-JCS", "canonicalization", ["jcs", "unicode"], unicode_state, _request(r, unicode_state, unicode_target))

    noncanonical = deepcopy(base_req)
    noncanonical["numeric_probe"] = 10 ** 400
    _add(out, "NEG-JCS-OUT-OF-DOMAIN", "canonicalization", ["jcs", "noncanonical"], base, noncanonical)

    return out
