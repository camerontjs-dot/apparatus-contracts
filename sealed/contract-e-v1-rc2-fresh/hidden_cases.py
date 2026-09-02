from __future__ import annotations

import copy
import hashlib
import json
import math

STATE_SCHEMA = "contract-e-authority-state-candidate-rc2"
REQUEST_SCHEMA = "contract-e-authorization-request-candidate-rc2"


def _canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def _identity(value):
    return "sha256:" + hashlib.sha256(_canonical(value)).hexdigest()


def _reference(ref_id="target", kind="object", version="v1", immutable_id="obj-1"):
    item = {
        "ref_id": ref_id,
        "kind": kind,
        "version": version,
        "immutable_id": immutable_id,
        "identity_sha256": "sha256:" + "0" * 64,
    }
    item["identity_sha256"] = _identity({"kind": kind, "version": version, "immutable_id": immutable_id})
    return item


def _state(
    target_ref,
    *,
    subject="alice",
    domain="deploy",
    operation="release",
    scope="prod",
    target_class="artifact",
    valid_from="2026-01-01T00:00:00Z",
    valid_until="2026-12-31T23:59:59Z",
    revoked_at=None,
    records=None,
):
    if records is None:
        records = [{
            "id": "root",
            "basis_type": "grant",
            "subject_id": subject,
            "domain": domain,
            "operation": operation,
            "scope": scope,
            "target_class": target_class,
            "target_ref": target_ref,
            "valid_from": valid_from,
            "valid_until": valid_until,
            "revoked_at": revoked_at,
            "parent_id": None,
            "delegated_by": None,
        }]
    state = {
        "schema": STATE_SCHEMA,
        "authority_state_id": "sha256:" + "0" * 64,
        "records": records,
    }
    state["authority_state_id"] = _identity({"schema": state["schema"], "records": state["records"]})
    return state


def _request(
    state,
    reference,
    *,
    subject=None,
    domain=None,
    operation=None,
    scope=None,
    target_class=None,
    target_ref=None,
    evaluation_time="2026-06-01T12:00:00Z",
    references=None,
    supporting=None,
    conflicts=None,
    residues=None,
):
    leaf = state.get("records", [{}])[-1] if isinstance(state.get("records"), list) and state.get("records") else {}
    return {
        "schema": REQUEST_SCHEMA,
        "request_id": "req-1",
        "authority_state_id": state.get("authority_state_id", "sha256:" + "0" * 64),
        "evaluation_time": evaluation_time,
        "subject_id": subject if subject is not None else leaf.get("subject_id", "alice"),
        "jurisdiction": {
            "domain": domain if domain is not None else leaf.get("domain", "deploy"),
            "operation": operation if operation is not None else leaf.get("operation", "release"),
            "scope": scope if scope is not None else leaf.get("scope", "prod"),
            "target_class": target_class if target_class is not None else leaf.get("target_class", "artifact"),
            "target_ref": target_ref if target_ref is not None else leaf.get("target_ref", reference["identity_sha256"]),
        },
        "references": copy.deepcopy(references if references is not None else [reference]),
        "supporting_artifacts": copy.deepcopy(supporting or []),
        "conflicts": copy.deepcopy(conflicts or []),
        "residues": copy.deepcopy(residues or []),
    }


def _case(case_id, family, state, request, *tags):
    return {"id": case_id, "family": family, "tags": list(tags), "state": state, "request": request}


def cases():
    out = []
    target = _reference()
    base = _state(target["identity_sha256"])
    req = _request(base, target)

    out.append(_case("POS-GRANT", "positive", copy.deepcopy(base), copy.deepcopy(req)))

    policy = copy.deepcopy(base)
    policy["records"][0]["basis_type"] = "policy"
    policy["authority_state_id"] = _identity({"schema": policy["schema"], "records": policy["records"]})
    out.append(_case("POS-POLICY", "positive", policy, _request(policy, target)))

    root = copy.deepcopy(base["records"][0])
    root["subject_id"] = "alice"
    delegated = copy.deepcopy(root)
    delegated.update({"id": "d1", "basis_type": "delegation", "subject_id": "bob", "parent_id": "root", "delegated_by": "alice"})
    dstate = _state(target["identity_sha256"], records=[root, delegated])
    out.append(_case("POS-DELEGATION", "delegation", dstate, _request(dstate, target, subject="bob")))

    for case_id, field, replacement in [
        ("NEG-SUBJECT", "subject_id", "mallory"),
        ("NEG-DOMAIN", "domain", "other-domain"),
        ("NEG-OPERATION", "operation", "other-operation"),
        ("NEG-SCOPE", "scope", "other-scope"),
        ("NEG-TARGET-CLASS", "target_class", "other-class"),
    ]:
        rq = copy.deepcopy(req)
        if field == "subject_id":
            rq[field] = replacement
        else:
            rq["jurisdiction"][field] = replacement
        out.append(_case(case_id, "binding", copy.deepcopy(base), rq))

    other = _reference(ref_id="other", immutable_id="obj-2")
    rq = copy.deepcopy(req)
    rq["references"].append(other)
    rq["jurisdiction"]["target_ref"] = other["identity_sha256"]
    out.append(_case("NEG-TARGET-REF", "binding", copy.deepcopy(base), rq))

    future = _state(target["identity_sha256"], valid_from="2026-07-01T00:00:00Z", valid_until=None)
    out.append(_case("NEG-FUTURE", "currentness", future, _request(future, target)))
    stale = _state(target["identity_sha256"], valid_until="2026-05-31T23:59:59Z")
    out.append(_case("NEG-STALE", "currentness", stale, _request(stale, target)))
    revoked = _state(target["identity_sha256"], revoked_at="2026-06-01T12:00:00Z")
    out.append(_case("NEG-REVOKED", "currentness", revoked, _request(revoked, target)))

    vf = _state(target["identity_sha256"], valid_from="2026-06-01T12:00:00Z", valid_until=None)
    out.append(_case("POS-VALID-FROM-EDGE", "currentness", vf, _request(vf, target)))
    vu = _state(target["identity_sha256"], valid_until="2026-06-01T12:00:00Z")
    out.append(_case("POS-VALID-UNTIL-EDGE", "currentness", vu, _request(vu, target)))
    rvf = _state(target["identity_sha256"], revoked_at="2026-06-01T12:00:00.0000001Z")
    out.append(_case("POS-REVOCATION-FUTURE", "currentness", rvf, _request(rvf, target)))

    frac_end = _state(target["identity_sha256"], valid_until="2026-06-01T12:00:00.1234567Z")
    out.append(_case("POS-FRACTION-VALID-UNTIL-EDGE", "fractional-currentness", frac_end, _request(frac_end, target, evaluation_time="2026-06-01T12:00:00.1234567Z"), "precision"))
    out.append(_case("NEG-FRACTION-AFTER-VALID-UNTIL", "fractional-currentness", copy.deepcopy(frac_end), _request(frac_end, target, evaluation_time="2026-06-01T12:00:00.1234568Z"), "precision", "false-permit-falsifier"))
    frac_revoke = _state(target["identity_sha256"], revoked_at="2026-06-01T12:00:00.1234567Z")
    out.append(_case("POS-FRACTION-BEFORE-REVOKE", "fractional-currentness", frac_revoke, _request(frac_revoke, target, evaluation_time="2026-06-01T12:00:00.1234566Z"), "precision"))
    out.append(_case("NEG-FRACTION-AT-REVOKE", "fractional-currentness", copy.deepcopy(frac_revoke), _request(frac_revoke, target, evaluation_time="2026-06-01T12:00:00.1234567Z"), "precision"))
    leap = copy.deepcopy(req)
    leap["evaluation_time"] = "2026-06-01T12:00:60Z"
    out.append(_case("NEG-LEAP-SECOND", "timestamp", copy.deepcopy(base), leap))

    for case_id, mutate in [
        ("NEG-DELEGATION-DOMAIN", lambda r: r.__setitem__("domain", "other")),
        ("NEG-DELEGATION-OPERATION", lambda r: r.__setitem__("operation", "other")),
        ("NEG-DELEGATION-SCOPE", lambda r: r.__setitem__("scope", "other")),
        ("NEG-DELEGATION-TARGET-CLASS", lambda r: r.__setitem__("target_class", "other")),
        ("NEG-DELEGATION-TARGET-REF", lambda r: r.__setitem__("target_ref", "sha256:" + "9" * 64)),
    ]:
        records = copy.deepcopy(dstate["records"])
        mutate(records[1])
        st = _state(records[0]["target_ref"], records=records)
        out.append(_case(case_id, "delegation", st, _request(st, target, subject="bob")))

    for case_id, mutate in [
        ("NEG-LINEAGE-PARENT", lambda rs: rs[1].__setitem__("parent_id", "missing")),
        ("NEG-LINEAGE-DELEGATED-BY", lambda rs: rs[1].__setitem__("delegated_by", "mallory")),
        ("NEG-LINEAGE-DUP-ID", lambda rs: rs[1].__setitem__("id", "root")),
        ("NEG-LINEAGE-NON-DELEGATION", lambda rs: rs[1].__setitem__("basis_type", "grant")),
    ]:
        records = copy.deepcopy(dstate["records"])
        mutate(records)
        st = _state(records[0]["target_ref"], records=records)
        out.append(_case(case_id, "lineage", st, _request(st, target, subject="bob")))

    forged = copy.deepcopy(base)
    forged["authority_state_id"] = "sha256:" + "1" * 64
    out.append(_case("NEG-STATE-ID-DIVERGENCE", "state-identity", forged, copy.deepcopy(req), "claimed-computed"))

    malformed_claim = copy.deepcopy(base)
    malformed_claim["authority_state_id"] = "not-a-sha256"
    out.append(_case("NEG-STATE-CLAIM-MALFORMED", "state-identity", malformed_claim, copy.deepcopy(req), "claimed-null", "computed-present"))

    uncanonical = copy.deepcopy(base)
    uncanonical["records"][0]["subject_id"] = "bad\ud800"
    out.append(_case("NEG-STATE-UNCANONICALIZABLE", "state-identity", uncanonical, copy.deepcopy(req), "computed-null"))

    rq = copy.deepcopy(req)
    rq["authority_state_id"] = "sha256:" + "2" * 64
    out.append(_case("NEG-REQUEST-STATE-ID", "state-identity", copy.deepcopy(base), rq))

    bad_ref = copy.deepcopy(req)
    bad_ref["references"][0]["identity_sha256"] = "sha256:" + "3" * 64
    bad_ref["jurisdiction"]["target_ref"] = bad_ref["references"][0]["identity_sha256"]
    bad_state = _state(bad_ref["jurisdiction"]["target_ref"])
    bad_ref["authority_state_id"] = bad_state["authority_state_id"]
    out.append(_case("NEG-REFERENCE-HASH", "reference", bad_state, bad_ref))

    missing_target = copy.deepcopy(req)
    missing_target["references"] = [other]
    out.append(_case("NEG-TARGET-REFERENCE-MISSING", "reference", copy.deepcopy(base), missing_target))

    dup_ref = copy.deepcopy(req)
    dup_ref["references"].append(copy.deepcopy(dup_ref["references"][0]))
    out.append(_case("NEG-DUPLICATE-REF-ID", "request-local-id", copy.deepcopy(base), dup_ref))

    support_ref = _reference(ref_id="support", kind="qualification", version=None, immutable_id="q-1")
    support_req = copy.deepcopy(req)
    support_req["references"].append(support_ref)
    support_req["supporting_artifacts"] = [{"id": "s1", "artifact_type": "qualification", "ref_id": "support"}]
    out.append(_case("POS-SUPPORT-NONCONFERRING", "support", copy.deepcopy(base), support_req))

    bad_support = copy.deepcopy(req)
    bad_support["supporting_artifacts"] = [{"id": "s1", "artifact_type": "qualification", "ref_id": "missing"}]
    out.append(_case("NEG-SUPPORT-UNKNOWN-REF", "support", copy.deepcopy(base), bad_support))

    dup_support = copy.deepcopy(support_req)
    dup_support["supporting_artifacts"].append({"id": "s1", "artifact_type": "other", "ref_id": "support"})
    out.append(_case("NEG-DUPLICATE-SUPPORT-ID", "request-local-id", copy.deepcopy(base), dup_support))

    no_authority = {"schema": STATE_SCHEMA, "authority_state_id": "sha256:" + "4" * 64, "records": []}
    support_only = _request(base, target, supporting=[{"id": "s1", "artifact_type": "contract_d_candidate_for_authorization", "ref_id": "target"}])
    out.append(_case("NEG-SUPPORT-CANNOT-CONFER", "support", no_authority, support_only, "laundering", "claimed-computed"))

    conflict = copy.deepcopy(req)
    conflict["conflicts"] = [{"id": "c1", "relevant": True, "status": "unresolved"}]
    out.append(_case("NEG-CONFLICT", "blocker", copy.deepcopy(base), conflict))
    contested_conflict = copy.deepcopy(req)
    contested_conflict["conflicts"] = [{"id": "c1", "relevant": True, "status": "contested"}]
    out.append(_case("NEG-CONFLICT-CONTESTED", "blocker", copy.deepcopy(base), contested_conflict))
    residue = copy.deepcopy(req)
    residue["residues"] = [{"id": "r1", "relevant": True, "status": "unresolved"}]
    out.append(_case("NEG-RESIDUE", "blocker", copy.deepcopy(base), residue))
    contested_residue = copy.deepcopy(req)
    contested_residue["residues"] = [{"id": "r1", "relevant": True, "status": "contested"}]
    out.append(_case("NEG-RESIDUE-CONTESTED", "blocker", copy.deepcopy(base), contested_residue))

    irrelevant = copy.deepcopy(req)
    irrelevant["conflicts"] = [{"id": "c1", "relevant": False, "status": "unresolved"}]
    irrelevant["residues"] = [{"id": "r1", "relevant": False, "status": "contested"}]
    out.append(_case("POS-IRRELEVANT-BLOCKERS", "blocker", copy.deepcopy(base), irrelevant, "preservation"))

    dup_conflict = copy.deepcopy(req)
    dup_conflict["conflicts"] = [
        {"id": "dup", "relevant": False, "status": "unresolved"},
        {"id": "dup", "relevant": False, "status": "contested"},
    ]
    out.append(_case("NEG-DUPLICATE-CONFLICT-ID", "request-local-id", copy.deepcopy(base), dup_conflict))
    dup_residue = copy.deepcopy(req)
    dup_residue["residues"] = [
        {"id": "dup", "relevant": False, "status": "unresolved"},
        {"id": "dup", "relevant": False, "status": "contested"},
    ]
    out.append(_case("NEG-DUPLICATE-RESIDUE-ID", "request-local-id", copy.deepcopy(base), dup_residue))

    conflict_ref = _reference(ref_id="conflict", kind="conflict", version=None, immutable_id="case-1:conflict-1")
    resolution_state = _state(
        conflict_ref["identity_sha256"], subject="resolver", domain="resolution", operation="resolve",
        scope="case-1", target_class="conflict", valid_until=None,
    )
    resolution_req = _request(
        resolution_state, conflict_ref, subject="resolver", domain="resolution", operation="resolve",
        scope="case-1", target_class="conflict", references=[conflict_ref],
    )
    out.append(_case("POS-RESOLUTION-NO-BLOCKER", "resolution", resolution_state, resolution_req))
    resolution_blocked = copy.deepcopy(resolution_req)
    resolution_blocked["conflicts"] = [{"id": "c1", "relevant": True, "status": "unresolved"}]
    out.append(_case("NEG-RESOLUTION-WITH-BLOCKER", "resolution", copy.deepcopy(resolution_state), resolution_blocked, "fail-closed"))

    for case_id, field in [
        ("NEG-UNKNOWN-REQUEST-FIELD", "future_field"),
        ("NEG-UNKNOWN-RESOLVED-CONFLICT-IDS", "resolved_conflict_ids"),
        ("NEG-UNKNOWN-RESOLVED-RESIDUE-IDS", "resolved_residue_ids"),
    ]:
        rq = copy.deepcopy(req)
        rq[field] = [] if "ids" in field else True
        out.append(_case(case_id, "future-field", copy.deepcopy(base), rq))

    future_schema = copy.deepcopy(req)
    future_schema["schema"] = "contract-e-authorization-request-candidate-rc99"
    out.append(_case("NEG-FUTURE-E-SCHEMA", "future-schema", copy.deepcopy(base), future_schema))

    status_launder = copy.deepcopy(req)
    status_launder["status"] = "established"
    out.append(_case("NEG-STATUS-ESTABLISHED", "laundering", copy.deepcopy(base), status_launder, "laundering"))

    missing_subject = copy.deepcopy(req)
    del missing_subject["subject_id"]
    out.append(_case("NEG-MISSING-SUBJECT", "malformed", copy.deepcopy(base), missing_subject))

    malformed_time = copy.deepcopy(req)
    malformed_time["evaluation_time"] = "2026-99-99T00:00:00Z"
    out.append(_case("NEG-MALFORMED-TIMESTAMP", "malformed", copy.deepcopy(base), malformed_time))

    malformed_conflict = copy.deepcopy(req)
    malformed_conflict["conflicts"] = [{"id": "c1", "relevant": True, "status": []}]
    out.append(_case("NEG-MALFORMED-CONFLICT-PRESERVATION", "malformed-preservation", copy.deepcopy(base), malformed_conflict, "preservation"))

    malformed_support = copy.deepcopy(req)
    malformed_support["supporting_artifacts"] = [{"id": "s1", "artifact_type": [], "ref_id": "target"}]
    out.append(_case("NEG-MALFORMED-SUPPORT-PRESERVATION", "malformed-preservation", copy.deepcopy(base), malformed_support, "preservation"))

    host_value = copy.deepcopy(req)
    host_value["subject_id"] = {"not": "a string"}
    out.append(_case("NEG-HOST-VALUE-REQUEST", "malformed", copy.deepcopy(base), host_value))

    nan_request = copy.deepcopy(req)
    nan_request["evaluation_time"] = math.nan
    out.append(_case("NEG-NONFINITE-REQUEST", "malformed", copy.deepcopy(base), nan_request))

    cyclic = copy.deepcopy(req)
    cyclic["future"] = cyclic
    out.append(_case("NEG-CYCLIC-REQUEST", "malformed", copy.deepcopy(base), cyclic))

    a_ref = _reference(ref_id="A", kind="contract_a", version="2.0.0", immutable_id="git:commit:529c92b49a34d5c610618551a8737f019f9fa332")
    b_ref = _reference(ref_id="B", kind="contract_b", version="1.2.0", immutable_id="git:commit:c314e53bd91c0736aa4370a364673b069aceb43e")
    c_ref = _reference(ref_id="C", kind="contract_c", version="1.0.0", immutable_id="git:commit:5fe55f9ed5d0ee9f026ca1b077e9d70ce0487ea1")
    d_ref = _reference(ref_id="D", kind="contract_d", version="1.0.0", immutable_id="git:commit:298a1a0f7b7b6d7712e11200d04faec3e1ca169b")
    opaque_state = _state(d_ref["identity_sha256"], target_class="contract-d-decision")
    opaque_req = _request(opaque_state, d_ref, references=[a_ref, b_ref, c_ref, d_ref], target_class="contract-d-decision")
    out.append(_case("POS-OPAQUE-RELEASED-A-D-REFS", "opaque-upstream", opaque_state, opaque_req, "A-D"))

    upstream_only = copy.deepcopy(opaque_req)
    upstream_only["supporting_artifacts"] = [
        {"id": "a", "artifact_type": "contract_a", "ref_id": "A"},
        {"id": "b", "artifact_type": "contract_b", "ref_id": "B"},
        {"id": "c", "artifact_type": "contract_c", "ref_id": "C"},
        {"id": "d", "artifact_type": "contract_d", "ref_id": "D"},
    ]
    out.append(_case("NEG-A-D-CANNOT-REPLACE-AUTHORITY", "opaque-upstream", no_authority, upstream_only, "laundering"))

    receipt_as_state = {
        "schema": "contract-e-authorization-receipt-candidate-rc2",
        "receipt_id": "sha256:" + "8" * 64,
        "authority_conferring": False,
        "authorized": True,
    }
    out.append(_case("NEG-RECEIPT-NOT-STANDING-AUTHORITY", "receipt-nonconferring", receipt_as_state, copy.deepcopy(req), "laundering"))

    return out
