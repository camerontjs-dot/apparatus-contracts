from __future__ import annotations

import hashlib
import json
from copy import deepcopy

STATE_SCHEMA = "contract-e-authority-state-candidate-rc1"
REQUEST_SCHEMA = "contract-e-authorization-request-candidate-rc1"
NOW = "2026-09-02T12:00:00Z"
PAST = "2026-01-01T00:00:00Z"
FUTURE = "2027-01-01T00:00:00Z"

A_COMMIT = "529c92b49a34d5c610618551a8737f019f9fa332"
B_COMMIT = "c314e53bd91c0736aa4370a364673b069aceb43e"
C_COMMIT = "5fe55f9ed5d0ee9f026ca1b077e9d70ce0487ea1"
D_COMMIT = "298a1a0f7b7b6d7712e11200d04faec3e1ca169b"


def ident(value):
    raw = (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def ref(ref_id, kind, version, immutable_id):
    value = {"kind": kind, "version": version, "immutable_id": immutable_id}
    return {"ref_id": ref_id, **value, "identity_sha256": ident(value)}


def refs():
    return [
        ref("A", "contract_a", "2.0.0", f"git:commit:{A_COMMIT}"),
        ref("B", "contract_b", "1.2.0", f"git:commit:{B_COMMIT}"),
        ref("C", "contract_c", "1.0.0", f"git:commit:{C_COMMIT}"),
        ref("D", "contract_d", "1.0.0", f"git:commit:{D_COMMIT}"),
    ]


def state_identity(state):
    return ident({k: deepcopy(v) for k, v in state.items() if k != "authority_state_id"})


def state(*, basis="policy", subject="actor:operator", domain="authorization", operation="authorize", scope="pipeline:v1", target_class="contract-d-decision", target_ref=None, valid_from=PAST, valid_until=FUTURE, revoked_at=None, delegates=()):
    target_ref = target_ref or refs()[-1]["identity_sha256"]
    records = [{
        "id": "auth:root", "basis_type": basis, "subject_id": subject,
        "domain": domain, "operation": operation, "scope": scope,
        "target_class": target_class, "target_ref": target_ref,
        "valid_from": valid_from, "valid_until": valid_until, "revoked_at": revoked_at,
        "parent_id": None, "delegated_by": None,
    }]
    parent_id, parent_subject = "auth:root", subject
    for index, delegated_subject in enumerate(delegates, 1):
        records.append({
            "id": f"auth:delegation:{index}", "basis_type": "delegation", "subject_id": delegated_subject,
            "domain": domain, "operation": operation, "scope": scope,
            "target_class": target_class, "target_ref": target_ref,
            "valid_from": valid_from, "valid_until": valid_until, "revoked_at": None,
            "parent_id": parent_id, "delegated_by": parent_subject,
        })
        parent_id, parent_subject = f"auth:delegation:{index}", delegated_subject
    out = {"schema": STATE_SCHEMA, "authority_state_id": "", "records": records}
    out["authority_state_id"] = state_identity(out)
    return out


def request(s, *, subject=None, domain=None, operation=None, scope=None, target_class=None, target_ref=None, references=None, supporting=None, conflicts=None, residues=None, at=NOW):
    leaf = s["records"][-1] if s.get("records") else {}
    return {
        "schema": REQUEST_SCHEMA,
        "request_id": "req:sealed",
        "authority_state_id": s.get("authority_state_id", "sha256:" + "0" * 64),
        "evaluation_time": at,
        "subject_id": subject or leaf.get("subject_id", "actor:operator"),
        "jurisdiction": {
            "domain": domain or leaf.get("domain", "authorization"),
            "operation": operation or leaf.get("operation", "authorize"),
            "scope": scope or leaf.get("scope", "pipeline:v1"),
            "target_class": target_class or leaf.get("target_class", "contract-d-decision"),
            "target_ref": target_ref or leaf.get("target_ref", refs()[-1]["identity_sha256"]),
        },
        "references": deepcopy(references if references is not None else refs()),
        "supporting_artifacts": deepcopy(supporting or []),
        "conflicts": deepcopy(conflicts or []),
        "residues": deepcopy(residues or []),
    }


def case(case_id, family, s, r, tags=()):
    return {"id": case_id, "family": family, "state": s, "request": r, "tags": list(tags)}


def cases():
    out = []
    base = state()
    out += [
        case("POS-POLICY", "positive", base, request(base)),
        case("POS-GRANT", "positive", state(basis="grant"), request(state(basis="grant"))),
    ]
    delegated = state(subject="actor:owner", delegates=("actor:delegate",))
    out.append(case("POS-DELEGATION", "delegation", delegated, request(delegated)))

    for name, kwargs in [
        ("NEG-SUBJECT", {"subject": "actor:other"}),
        ("NEG-DOMAIN", {"domain": "execution"}),
        ("NEG-OPERATION", {"operation": "execute"}),
        ("NEG-SCOPE", {"scope": "pipeline:other"}),
        ("NEG-TARGET-CLASS", {"target_class": "contract-a-proposition"}),
        ("NEG-TARGET-REF", {"target_ref": refs()[0]["identity_sha256"]}),
    ]:
        out.append(case(name, "binding", base, request(base, **kwargs)))

    for name, s in [
        ("NEG-FUTURE", state(valid_from=FUTURE, valid_until=None)),
        ("NEG-STALE", state(valid_until="2026-08-01T00:00:00Z")),
        ("NEG-REVOKED", state(revoked_at="2026-09-02T12:00:00Z")),
    ]:
        out.append(case(name, "currentness", s, request(s)))
    s = state(valid_from=NOW)
    out.append(case("POS-VALID-FROM-EDGE", "currentness", s, request(s)))
    s = state(valid_until=NOW)
    out.append(case("POS-VALID-UNTIL-EDGE", "currentness", s, request(s)))
    s = state(revoked_at=FUTURE)
    out.append(case("POS-REVOCATION-FUTURE", "currentness", s, request(s)))

    for key, value in [("domain", "other"), ("operation", "other"), ("scope", "other"), ("target_class", "other"), ("target_ref", refs()[0]["identity_sha256"])]:
        s = deepcopy(delegated)
        s["records"][1][key] = value
        s["authority_state_id"] = state_identity(s)
        out.append(case(f"NEG-DELEGATION-{key.upper()}", "delegation", s, request(s)))
    for label, mutate in [
        ("PARENT", lambda s: s["records"][1].__setitem__("parent_id", "auth:missing")),
        ("DELEGATED-BY", lambda s: s["records"][1].__setitem__("delegated_by", "actor:other")),
        ("DUP-ID", lambda s: s["records"][1].__setitem__("id", "auth:root")),
        ("NON-DELEGATION", lambda s: s["records"][1].__setitem__("basis_type", "policy")),
    ]:
        s = deepcopy(delegated); mutate(s); s["authority_state_id"] = state_identity(s)
        out.append(case(f"NEG-LINEAGE-{label}", "lineage", s, request(s)))

    support = [
        {"id": "sup:A", "artifact_type": "contract_a_declaration", "ref_id": "A"},
        {"id": "sup:B", "artifact_type": "contract_b_fact", "ref_id": "B"},
        {"id": "sup:C", "artifact_type": "contract_c_result", "ref_id": "C"},
        {"id": "sup:D", "artifact_type": "contract_d_candidate_for_authorization", "ref_id": "D"},
    ]
    out.append(case("POS-SUPPORT-NONCONFERRING", "support", base, request(base, supporting=support)))
    bad = {"schema": STATE_SCHEMA, "authority_state_id": "sha256:" + "0" * 64, "records": []}
    out.append(case("NEG-SUPPORT-CANNOT-CONFER", "support", bad, request(base, supporting=support)))

    for name, kwargs in [
        ("NEG-CONFLICT", {"conflicts": [{"id": "c1", "relevant": True, "status": "unresolved"}]}),
        ("NEG-RESIDUE", {"residues": [{"id": "r1", "relevant": True, "status": "contested"}]}),
    ]:
        out.append(case(name, "blocker", base, request(base, **kwargs)))
    out.append(case("POS-IRRELEVANT-CONFLICT", "blocker", base, request(base, conflicts=[{"id": "ci", "relevant": False, "status": "unresolved"}])))
    out.append(case("POS-IRRELEVANT-RESIDUE", "blocker", base, request(base, residues=[{"id": "ri", "relevant": False, "status": "contested"}])))

    for field in ("resolved_conflict_ids", "resolved_residue_ids", "future_field"):
        r = request(base); r[field] = ["x"] if field.startswith("resolved") else True
        out.append(case(f"NEG-UNKNOWN-{field.upper()}", "malformed", base, r))
    r = request(base); del r["subject_id"]
    out.append(case("NEG-MISSING-SUBJECT", "malformed", base, r))
    r = request(base); r["schema"] = "contract-e-authorization-request-future"
    out.append(case("NEG-FUTURE-E-SCHEMA", "malformed", base, r))
    s = deepcopy(base); s["records"][0]["status"] = "established"; s["authority_state_id"] = state_identity(s)
    out.append(case("NEG-STATUS-ESTABLISHED", "malformed", s, request(base), ("laundering",)))

    r = request(base); r["authority_state_id"] = "sha256:" + "1" * 64
    out.append(case("NEG-STATE-BINDING", "identity", base, r))
    s = deepcopy(base); s["authority_state_id"] = "sha256:" + "2" * 64
    out.append(case("NEG-STATE-ID", "identity", s, request(base)))
    r = request(base); r["references"][-1]["immutable_id"] += ":tampered"
    out.append(case("NEG-REFERENCE-HASH", "identity", base, r))
    r = request(base); r["references"] = []
    out.append(case("NEG-REFERENCE-MISSING", "identity", base, r))

    parent = ref("P", "contract_a_proposition", "2.0.0", "A:parent")
    child1 = ref("C1", "contract_a_proposition", "2.0.0", "A:child:1")
    child2 = ref("C2", "contract_a_proposition", "2.0.0", "A:child:2")
    s = state(target_class="contract-a-proposition", target_ref=parent["identity_sha256"])
    out.append(case("POS-PARENT", "target_lineage", s, request(s, references=[parent])))
    out.append(case("NEG-PARENT-TO-CHILD", "target_lineage", s, request(s, references=[child1], target_ref=child1["identity_sha256"])))
    s = state(target_class="contract-a-proposition", target_ref=child1["identity_sha256"])
    out.append(case("NEG-CHILD-TO-PARENT", "target_lineage", s, request(s, references=[parent], target_ref=parent["identity_sha256"])))
    out.append(case("NEG-SIBLING", "target_lineage", s, request(s, references=[child2], target_ref=child2["identity_sha256"])))

    conflict_ref = ref("X", "conflict", None, "conflict:42")
    s = state(domain="resolution", operation="resolve", scope="case:42", target_class="conflict", target_ref=conflict_ref["identity_sha256"])
    out.append(case("POS-RESOLUTION-AUTH", "resolution", s, request(s, references=[conflict_ref])))

    s = state(domain="execution", operation="execute")
    out.append(case("POS-EXECUTION-AUTH", "boundary", s, request(s)))
    out.append(case("NEG-EXECUTION-NOT-VERIFICATION", "boundary", s, request(s, domain="verification", operation="verify")))
    out.append(case("NEG-DECISION-NOT-EXECUTION", "boundary", base, request(base, domain="execution", operation="execute")))

    report = ref("R", "execution_report", None, "report:1")
    support_report = [{"id": "sup:R", "artifact_type": "execution_report", "ref_id": "R"}]
    s = state(domain="verification", operation="verify", target_class="execution_report", target_ref=report["identity_sha256"])
    out.append(case("POS-VERIFICATION-SEPARATE", "boundary", s, request(s, references=[report], supporting=support_report)))

    # Surplus peer root is structurally invalid instead of selecting a quantifier.
    s = deepcopy(base); extra = deepcopy(s["records"][0]); extra["id"] = "auth:surplus"; extra["subject_id"] = "actor:other"; s["records"].append(extra); s["authority_state_id"] = state_identity(s)
    out.append(case("NEG-SURPLUS-PEER", "aggregation", s, request(s)))

    return out
