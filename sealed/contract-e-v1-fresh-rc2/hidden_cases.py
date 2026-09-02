from __future__ import annotations

import hashlib
import json
from copy import deepcopy

STATE_SCHEMA = "contract-e-authority-state-candidate-rc2"
REQUEST_SCHEMA = "contract-e-authorization-request-candidate-rc2"
NOW = "2026-09-02T12:00:00Z"
PAST = "2026-01-01T00:00:00Z"
FUTURE = "2027-01-01T00:00:00Z"


def ident(value):
    raw = (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def ref(ref_id, kind, version, immutable_id):
    payload = {"kind": kind, "version": version, "immutable_id": immutable_id}
    return {"ref_id": ref_id, **payload, "identity_sha256": ident(payload)}


def base_target(suffix="base"):
    return ref("T", "target", "1", f"target:{suffix}")


def state_identity(value):
    return ident({k: deepcopy(v) for k, v in value.items() if k != "authority_state_id"})


def state(*, basis="policy", subject="actor:operator", domain="authorization", operation="authorize", scope="pipeline:v1", target=None, valid_from=PAST, valid_until=FUTURE, revoked_at=None, delegates=()):
    target = target or base_target()
    records = [{
        "id": "auth:root",
        "basis_type": basis,
        "subject_id": subject,
        "domain": domain,
        "operation": operation,
        "scope": scope,
        "target_class": target["kind"],
        "target_ref": target["identity_sha256"],
        "valid_from": valid_from,
        "valid_until": valid_until,
        "revoked_at": revoked_at,
        "parent_id": None,
        "delegated_by": None,
    }]
    parent_id, parent_subject = "auth:root", subject
    for index, delegated_subject in enumerate(delegates, 1):
        records.append({
            "id": f"auth:delegation:{index}",
            "basis_type": "delegation",
            "subject_id": delegated_subject,
            "domain": domain,
            "operation": operation,
            "scope": scope,
            "target_class": target["kind"],
            "target_ref": target["identity_sha256"],
            "valid_from": valid_from,
            "valid_until": valid_until,
            "revoked_at": revoked_at,
            "parent_id": parent_id,
            "delegated_by": parent_subject,
        })
        parent_id, parent_subject = f"auth:delegation:{index}", delegated_subject
    out = {"schema": STATE_SCHEMA, "authority_state_id": "sha256:" + "0" * 64, "records": records}
    out["authority_state_id"] = state_identity(out)
    return out, target


def request(s, target, *, subject=None, domain=None, operation=None, scope=None, target_class=None, target_ref=None, references=None, supporting=None, conflicts=None, residues=None, at=NOW):
    leaf = s["records"][-1] if isinstance(s, dict) and s.get("records") else {}
    return {
        "schema": REQUEST_SCHEMA,
        "request_id": "req:hidden",
        "authority_state_id": s.get("authority_state_id", "sha256:" + "0" * 64) if isinstance(s, dict) else "sha256:" + "0" * 64,
        "evaluation_time": at,
        "subject_id": subject or leaf.get("subject_id", "actor:operator"),
        "jurisdiction": {
            "domain": domain or leaf.get("domain", "authorization"),
            "operation": operation or leaf.get("operation", "authorize"),
            "scope": scope or leaf.get("scope", "pipeline:v1"),
            "target_class": target_class or leaf.get("target_class", target["kind"]),
            "target_ref": target_ref or leaf.get("target_ref", target["identity_sha256"]),
        },
        "references": deepcopy(references if references is not None else [target]),
        "supporting_artifacts": deepcopy(supporting or []),
        "conflicts": deepcopy(conflicts or []),
        "residues": deepcopy(residues or []),
    }


def case(case_id, family, s, r, tags=()):
    return {"id": case_id, "family": family, "state": s, "request": r, "tags": list(tags)}


def cases():
    out = []
    base, target = state()
    out.append(case("POS-POLICY", "positive", base, request(base, target)))
    grant, gt = state(basis="grant")
    out.append(case("POS-GRANT", "positive", grant, request(grant, gt)))
    delegated, dt = state(subject="actor:owner", delegates=("actor:delegate",))
    out.append(case("POS-DELEGATION", "delegation", delegated, request(delegated, dt)))

    for name, kwargs in [
        ("NEG-SUBJECT", {"subject": "actor:other"}),
        ("NEG-DOMAIN", {"domain": "execution"}),
        ("NEG-OPERATION", {"operation": "execute"}),
        ("NEG-SCOPE", {"scope": "other"}),
        ("NEG-TARGET-CLASS", {"target_class": "other"}),
    ]:
        out.append(case(name, "binding", base, request(base, target, **kwargs)))
    other = ref("O", "other", "1", "other:1")
    out.append(case("NEG-TARGET-REF", "binding", base, request(base, target, references=[other], target_ref=other["identity_sha256"])))

    for name, st in [
        ("NEG-FUTURE", state(valid_from=FUTURE, valid_until=None)),
        ("NEG-STALE", state(valid_until="2026-08-01T00:00:00Z")),
        ("NEG-REVOKED", state(revoked_at=NOW)),
    ]:
        s, t = st
        out.append(case(name, "currentness", s, request(s, t)))
    s, t = state(valid_from=NOW); out.append(case("POS-VALID-FROM-EDGE", "currentness", s, request(s, t)))
    s, t = state(valid_until=NOW); out.append(case("POS-VALID-UNTIL-EDGE", "currentness", s, request(s, t)))
    s, t = state(revoked_at=FUTURE); out.append(case("POS-REVOCATION-FUTURE", "currentness", s, request(s, t)))

    for field, value in [("domain", "other"), ("operation", "other"), ("scope", "other"), ("target_class", "other"), ("target_ref", other["identity_sha256"])]:
        s = deepcopy(delegated); s["records"][1][field] = value; s["authority_state_id"] = state_identity(s)
        out.append(case(f"NEG-DELEGATION-{field.upper()}", "delegation", s, request(s, dt)))
    for label, mutate in [
        ("PARENT", lambda s: s["records"][1].__setitem__("parent_id", "missing")),
        ("DELEGATED-BY", lambda s: s["records"][1].__setitem__("delegated_by", "actor:other")),
        ("DUP-ID", lambda s: s["records"][1].__setitem__("id", "auth:root")),
        ("NON-DELEGATION", lambda s: s["records"][1].__setitem__("basis_type", "policy")),
    ]:
        s = deepcopy(delegated); mutate(s); s["authority_state_id"] = state_identity(s)
        out.append(case(f"NEG-LINEAGE-{label}", "lineage", s, request(s, dt)))

    dref = ref("D", "contract-d", "1.0.0", "decision:hidden")
    support = [{"id": "sup:D", "artifact_type": "contract_d_candidate_for_authorization", "ref_id": "D"}]
    r = request(base, target); r["references"].append(dref); r["supporting_artifacts"] = deepcopy(support)
    out.append(case("POS-SUPPORT-NONCONFERRING", "support", base, r))
    invalid = {"schema": STATE_SCHEMA, "authority_state_id": "sha256:" + "0" * 64, "records": []}
    r = request(invalid, target, references=[target, dref], supporting=support)
    out.append(case("NEG-SUPPORT-CANNOT-CONFER", "support", invalid, r, ("rc1-disagreement-regression",)))

    out.append(case("NEG-CONFLICT", "blocker", base, request(base, target, conflicts=[{"id": "c", "relevant": True, "status": "unresolved"}])))
    out.append(case("NEG-RESIDUE", "blocker", base, request(base, target, residues=[{"id": "r", "relevant": True, "status": "contested"}])))
    out.append(case("POS-IRRELEVANT-CONFLICT", "blocker", base, request(base, target, conflicts=[{"id": "c", "relevant": False, "status": "unresolved"}])))
    out.append(case("POS-IRRELEVANT-RESIDUE", "blocker", base, request(base, target, residues=[{"id": "r", "relevant": False, "status": "contested"}])))

    for field in ("resolved_conflict_ids", "resolved_residue_ids", "future_field"):
        r = request(base, target); r[field] = [] if field.startswith("resolved") else True
        out.append(case(f"NEG-UNKNOWN-{field.upper()}", "malformed", base, r))
    r = request(base, target); del r["subject_id"]; out.append(case("NEG-MISSING-SUBJECT", "malformed", base, r))
    r = request(base, target); r["schema"] = "contract-e-authorization-request-future"; out.append(case("NEG-FUTURE-E-SCHEMA", "malformed", base, r))
    s = deepcopy(base); s["records"][0]["status"] = "established"; s["authority_state_id"] = state_identity(s); out.append(case("NEG-STATUS-ESTABLISHED", "malformed", s, request(s, target), ("laundering",)))

    r = request(base, target); r["authority_state_id"] = "sha256:" + "1" * 64; out.append(case("NEG-STATE-BINDING", "identity", base, r))
    s = deepcopy(base); s["authority_state_id"] = "sha256:" + "2" * 64; out.append(case("NEG-STATE-ID", "identity", s, request(s, target), ("rc1-disagreement-regression", "dual-identity")))
    r = request(base, target); r["references"][0]["immutable_id"] = "tampered"; out.append(case("NEG-REFERENCE-HASH", "identity", base, r))
    r = request(base, target); r["references"] = []; out.append(case("NEG-REFERENCE-MISSING", "identity", base, r))

    parent = ref("P", "contract-a-proposition", "2.0.0", "A:parent")
    child1 = ref("C1", "contract-a-proposition", "2.0.0", "A:child:1")
    child2 = ref("C2", "contract-a-proposition", "2.0.0", "A:child:2")
    ps, _ = state(target=parent); out.append(case("POS-PARENT", "target-lineage", ps, request(ps, parent)))
    out.append(case("NEG-PARENT-TO-CHILD", "target-lineage", ps, request(ps, parent, references=[child1], target_ref=child1["identity_sha256"])))
    cs, _ = state(target=child1)
    out.append(case("NEG-CHILD-TO-PARENT", "target-lineage", cs, request(cs, child1, references=[parent], target_ref=parent["identity_sha256"])))
    out.append(case("NEG-SIBLING", "target-lineage", cs, request(cs, child1, references=[child2], target_ref=child2["identity_sha256"])))

    conflict = ref("X", "conflict", None, "conflict:42")
    rs, _ = state(domain="resolution", operation="resolve", scope="case:42", target=conflict)
    out.append(case("POS-RESOLUTION-AUTH", "resolution", rs, request(rs, conflict, conflicts=[{"id": "c", "relevant": True, "status": "unresolved"}])))
    ex, et = state(domain="execution", operation="execute"); out.append(case("POS-EXECUTION-AUTH", "boundary", ex, request(ex, et)))
    out.append(case("NEG-EXECUTION-NOT-VERIFICATION", "boundary", ex, request(ex, et, domain="verification", operation="verify")))
    out.append(case("NEG-DECISION-NOT-EXECUTION", "boundary", base, request(base, target, domain="execution", operation="execute")))
    vr = ref("R", "execution-report", "1", "report:1"); vs, _ = state(domain="verification", operation="verify", target=vr)
    out.append(case("POS-VERIFICATION-SEPARATE", "boundary", vs, request(vs, vr)))

    surplus = deepcopy(base); extra = deepcopy(surplus["records"][0]); extra["id"] = "auth:surplus"; extra["subject_id"] = "actor:other"; surplus["records"].append(extra); surplus["authority_state_id"] = state_identity(surplus)
    out.append(case("NEG-SURPLUS-PEER", "aggregation", surplus, request(surplus, target)))

    # RC2-specific hidden identity cases.
    s = deepcopy(base); s["authority_state_id"] = "sha256:" + "3" * 64
    out.append(case("RC2-DUAL-ID-FORGED-CLAIM", "dual-identity", s, request(s, target), ("dual-identity",)))

    s = deepcopy(base); s["authority_state_id"] = "not-a-sha"
    r = request(base, target); r["authority_state_id"] = "sha256:" + "4" * 64
    out.append(case("RC2-MALFORMED-CLAIM-RECOMPUTABLE", "dual-identity", s, r, ("dual-identity",)))

    out.append(case("RC2-NONOBJECT-STATE", "dual-identity", ["not", "state"], request(base, target), ("dual-identity",)))

    r = request(base, target); r["schema"] = "contract-e-authorization-request-candidate-rc1"
    out.append(case("RC2-REJECT-RC1-REQUEST", "version", base, r))

    s = deepcopy(base); s["schema"] = "contract-e-authority-state-candidate-rc1"; s["authority_state_id"] = state_identity(s)
    out.append(case("RC2-REJECT-RC1-STATE", "version", s, request(s, target)))

    # Multiple claimed-ID values over identical payload prove claimed identity is an independent receipt fact.
    for index, digit in enumerate(("5", "6", "7", "8"), 1):
        s = deepcopy(base); s["authority_state_id"] = "sha256:" + digit * 64
        out.append(case(f"RC2-CLAIMED-ID-VARIANT-{index}", "dual-identity", s, request(s, target), ("dual-identity",)))

    # Multiple payload mutations with stale claimed ID prove recomputed identity is independently visible.
    for index, field in enumerate(("subject_id", "domain", "operation", "scope"), 1):
        s = deepcopy(base); s["records"][0][field] = f"mutated-{field}-{index}"
        # Deliberately keep original claimed ID stale.
        out.append(case(f"RC2-RECOMPUTED-ID-VARIANT-{index}", "dual-identity", s, request(s, target), ("dual-identity",)))

    return out
