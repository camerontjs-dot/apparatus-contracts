from __future__ import annotations

from copy import deepcopy

import rfc8785
import hashlib

STATE_SCHEMA = "contract-e-authority-state-candidate-rc2"
REQUEST_SCHEMA = "contract-e-authorization-request-candidate-rc2"
NOW = "2026-09-02T18:00:00Z"
PAST = "2026-01-01T00:00:00Z"
FUTURE = "2027-01-01T00:00:00Z"


def ident(value):
    return "sha256:" + hashlib.sha256(rfc8785.dumps(value) + b"\n").hexdigest()


def ref(ref_id, kind, version, immutable_id):
    payload = {"kind": kind, "version": version, "immutable_id": immutable_id}
    return {"ref_id": ref_id, **payload, "identity_sha256": ident(payload)}


def target_ref(label="target:1"):
    return ref("T", "test_target", "1", label)


def state_identity(state):
    payload = {k: deepcopy(v) for k, v in state.items() if k != "authority_state_id"}
    return ident(payload)


def make_state(
    *,
    basis="policy",
    subject="actor:operator",
    domain="knowledge",
    operation="knowledge.cite_as_evidence",
    scope="claim",
    target_class="test_target",
    target=None,
    valid_from=PAST,
    valid_until=FUTURE,
    revoked_at=None,
    delegates=(),
):
    target = target or target_ref()
    records = [{
        "id": "auth:root",
        "basis_type": basis,
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
    parent_id = "auth:root"
    parent_subject = subject
    for i, delegated_subject in enumerate(delegates, 1):
        records.append({
            "id": f"auth:delegation:{i}",
            "basis_type": "delegation",
            "subject_id": delegated_subject,
            "domain": domain,
            "operation": operation,
            "scope": scope,
            "target_class": target_class,
            "target_ref": target["identity_sha256"],
            "valid_from": valid_from,
            "valid_until": valid_until,
            "revoked_at": None,
            "parent_id": parent_id,
            "delegated_by": parent_subject,
        })
        parent_id = f"auth:delegation:{i}"
        parent_subject = delegated_subject
    out = {"schema": STATE_SCHEMA, "authority_state_id": "", "records": records}
    out["authority_state_id"] = state_identity(out)
    return out, target


def request(
    s,
    target,
    *,
    subject=None,
    domain=None,
    operation=None,
    scope=None,
    target_class=None,
    target_ref_value=None,
    refs=None,
    support=None,
    conflicts=None,
    residues=None,
    at=NOW,
):
    leaf = s["records"][-1] if isinstance(s, dict) and s.get("records") else {}
    refs = deepcopy(refs if refs is not None else [target])
    return {
        "schema": REQUEST_SCHEMA,
        "request_id": "req:hidden",
        "authority_state_id": s.get("authority_state_id", "sha256:" + "0" * 64) if isinstance(s, dict) else "sha256:" + "0" * 64,
        "evaluation_time": at,
        "subject_id": subject or leaf.get("subject_id", "actor:operator"),
        "jurisdiction": {
            "domain": domain or leaf.get("domain", "knowledge"),
            "operation": operation or leaf.get("operation", "knowledge.cite_as_evidence"),
            "scope": scope or leaf.get("scope", "claim"),
            "target_class": target_class or leaf.get("target_class", "test_target"),
            "target_ref": target_ref_value or leaf.get("target_ref", target["identity_sha256"]),
        },
        "references": refs,
        "supporting_artifacts": deepcopy(support or []),
        "conflicts": deepcopy(conflicts or []),
        "residues": deepcopy(residues or []),
    }


def c(case_id, family, s, r, tags=()):
    return {"id": case_id, "family": family, "state": s, "request": r, "tags": list(tags)}


def cases():
    out = []
    base, t = make_state()
    out.append(c("POS-POLICY", "positive", base, request(base, t)))
    grant, gt = make_state(basis="grant")
    out.append(c("POS-GRANT", "positive", grant, request(grant, gt)))
    delegated, dt = make_state(subject="actor:owner", delegates=("actor:delegate",))
    out.append(c("POS-DELEGATION", "delegation", delegated, request(delegated, dt)))

    for name, kwargs in [
        ("NEG-SUBJECT", {"subject": "actor:other"}),
        ("NEG-DOMAIN", {"domain": "other"}),
        ("NEG-OPERATION", {"operation": "task.dispatch"}),
        ("NEG-SCOPE", {"scope": "object"}),
        ("NEG-TARGET-CLASS", {"target_class": "other"}),
    ]:
        out.append(c(name, "binding", base, request(base, t, **kwargs)))
    other = target_ref("target:other")
    out.append(c("NEG-TARGET-REF", "binding", base, request(base, t, refs=[other], target_ref_value=other["identity_sha256"])))

    future, ft = make_state(valid_from=FUTURE, valid_until=None)
    stale, st = make_state(valid_until="2026-08-01T00:00:00Z")
    revoked, rt = make_state(revoked_at=NOW)
    out += [
        c("NEG-FUTURE", "currentness", future, request(future, ft)),
        c("NEG-STALE", "currentness", stale, request(stale, st)),
        c("NEG-REVOKED", "currentness", revoked, request(revoked, rt)),
    ]
    edge_from, eft = make_state(valid_from=NOW)
    edge_until, eut = make_state(valid_until=NOW)
    rev_future, rft = make_state(revoked_at=FUTURE)
    out += [
        c("POS-VALID-FROM-EDGE", "currentness", edge_from, request(edge_from, eft)),
        c("POS-VALID-UNTIL-EDGE", "currentness", edge_until, request(edge_until, eut)),
        c("POS-REVOCATION-FUTURE", "currentness", rev_future, request(rev_future, rft)),
    ]

    for field, value in [
        ("domain", "other"),
        ("operation", "other"),
        ("scope", "other"),
        ("target_class", "other"),
        ("target_ref", other["identity_sha256"]),
    ]:
        s = deepcopy(delegated)
        s["records"][1][field] = value
        s["authority_state_id"] = state_identity(s)
        out.append(c(f"NEG-DELEGATION-{field.upper()}", "delegation", s, request(s, dt)))

    for label, mutate in [
        ("PARENT", lambda s: s["records"][1].__setitem__("parent_id", "missing")),
        ("DELEGATED-BY", lambda s: s["records"][1].__setitem__("delegated_by", "actor:other")),
        ("DUP-ID", lambda s: s["records"][1].__setitem__("id", "auth:root")),
        ("NON-DELEGATION", lambda s: s["records"][1].__setitem__("basis_type", "policy")),
    ]:
        s = deepcopy(delegated)
        mutate(s)
        s["authority_state_id"] = state_identity(s)
        out.append(c(f"NEG-LINEAGE-{label}", "lineage", s, request(s, dt)))

    support_ref = ref("D", "contract_d_decision", "1.0.0", "decision:trusted")
    support = [{"id": "support:D", "artifact_type": "contract_d_candidate_for_authorization", "ref_id": "D"}]
    out.append(c("POS-SUPPORT-NONCONFERRING", "support", base, request(base, t, refs=[t, support_ref], support=support)))
    invalid_empty = {"schema": STATE_SCHEMA, "authority_state_id": "sha256:" + "0" * 64, "records": []}
    out.append(c("NEG-SUPPORT-CANNOT-CONFER", "support", invalid_empty, request(base, t, refs=[t, support_ref], support=support), ("rc1-mismatch-successor",)))

    out.append(c("NEG-CONFLICT", "blocker", base, request(base, t, conflicts=[{"id": "c", "relevant": True, "status": "unresolved"}])))
    out.append(c("NEG-RESIDUE", "blocker", base, request(base, t, residues=[{"id": "r", "relevant": True, "status": "contested"}])))
    out.append(c("POS-IRRELEVANT-CONFLICT", "blocker", base, request(base, t, conflicts=[{"id": "ci", "relevant": False, "status": "unresolved"}])))
    out.append(c("POS-IRRELEVANT-RESIDUE", "blocker", base, request(base, t, residues=[{"id": "ri", "relevant": False, "status": "contested"}])))

    for field in ("resolved_conflict_ids", "resolved_residue_ids", "future_field"):
        r = request(base, t)
        r[field] = ["x"] if field.startswith("resolved") else True
        out.append(c(f"NEG-UNKNOWN-{field.upper()}", "malformed", base, r))
    r = request(base, t); del r["subject_id"]
    out.append(c("NEG-MISSING-SUBJECT", "malformed", base, r))
    r = request(base, t); r["schema"] = "contract-e-authorization-request-future"
    out.append(c("NEG-FUTURE-REQUEST-SCHEMA", "malformed", base, r))
    s = deepcopy(base); s["records"][0]["status"] = "established"; s["authority_state_id"] = state_identity(s)
    out.append(c("NEG-STATUS-ESTABLISHED", "malformed", s, request(base, t), ("laundering",)))

    r = request(base, t); r["authority_state_id"] = "sha256:" + "1" * 64
    out.append(c("NEG-STATE-REQUEST-BINDING", "identity", base, r))
    s = deepcopy(base); correct = s["authority_state_id"]; s["authority_state_id"] = "sha256:" + "2" * 64
    out.append(c("NEG-STATE-ID", "identity", s, request(s, t), ("rc1-mismatch-successor",)))
    s2 = deepcopy(base); s2["authority_state_id"] = "not-a-sha"
    r2 = request(base, t); r2["authority_state_id"] = "sha256:" + "0" * 64
    out.append(c("NEG-CLAIMED-ID-MALFORMED", "identity", s2, r2))

    r = request(base, t); r["references"][0]["immutable_id"] += ":tampered"
    out.append(c("NEG-REFERENCE-HASH", "identity", base, r))
    r = request(base, t); r["references"] = []
    out.append(c("NEG-REFERENCE-MISSING", "identity", base, r))
    r = request(base, t); r["references"].append(deepcopy(r["references"][0]))
    out.append(c("NEG-REFERENCE-DUP", "identity", base, r))

    parent = ref("P", "proposition", "1", "parent")
    child1 = ref("C1", "proposition", "1", "child:1")
    child2 = ref("C2", "proposition", "1", "child:2")
    ps, _ = make_state(target_class="proposition", target=parent)
    out.append(c("POS-PARENT", "target-lineage", ps, request(ps, parent, refs=[parent])))
    out.append(c("NEG-PARENT-CHILD", "target-lineage", ps, request(ps, parent, refs=[child1], target_ref_value=child1["identity_sha256"])))
    cs, _ = make_state(target_class="proposition", target=child1)
    out.append(c("NEG-CHILD-PARENT", "target-lineage", cs, request(cs, child1, refs=[parent], target_ref_value=parent["identity_sha256"])))
    out.append(c("NEG-SIBLING", "target-lineage", cs, request(cs, child1, refs=[child2], target_ref_value=child2["identity_sha256"])))

    conflict_ref = ref("X", "conflict", None, "conflict:42")
    rs, _ = make_state(domain="resolution", operation="resolve", scope="case:42", target_class="conflict", target=conflict_ref)
    out.append(c("POS-RESOLUTION", "resolution", rs, request(rs, conflict_ref, refs=[conflict_ref])))

    exec_ref = ref("E", "execution_intent", "1", "intent:1")
    es, _ = make_state(domain="task", operation="task.dispatch", scope="single", target_class="execution_intent", target=exec_ref)
    out.append(c("POS-EXECUTION-AUTH", "stage-boundary", es, request(es, exec_ref, refs=[exec_ref])))
    out.append(c("NEG-EXECUTION-VERIFY", "stage-boundary", es, request(es, exec_ref, refs=[exec_ref], domain="verification", operation="verify")))
    out.append(c("NEG-DECISION-EXECUTION-INFLATION", "stage-boundary", es, request(es, exec_ref, refs=[exec_ref], operation="execute")))

    surplus = deepcopy(base)
    extra = deepcopy(surplus["records"][0]); extra["id"] = "auth:surplus"; extra["subject_id"] = "actor:other"
    surplus["records"].append(extra); surplus["authority_state_id"] = state_identity(surplus)
    out.append(c("NEG-SURPLUS-PEER", "aggregation", surplus, request(surplus, t)))

    # New RC2 recoverability surface: malformed but JCS-canonicalizable numeric states.
    for label, number in [
        ("ONE-POINT-ZERO", 1.0),
        ("NEGATIVE-ZERO", -0.0),
        ("SMALL-EXPONENT", 1e-6),
        ("LARGE-INTEGER-FLOAT", 1e20),
    ]:
        s = deepcopy(base)
        s["future_numeric_field"] = number
        out.append(c(f"NEG-JCS-{label}", "canonicalization", s, request(base, t), ("jcs",)))

    # Canonicalization fails entirely: recomputed identity must be null.
    s = deepcopy(base); s["future_numeric_field"] = float("nan")
    out.append(c("NEG-NONFINITE-STATE", "canonicalization", s, request(base, t), ("jcs",)))
    s = deepcopy(base); s["future_numeric_field"] = 10 ** 400
    out.append(c("NEG-JCS-OUT-OF-RANGE", "canonicalization", s, request(base, t), ("jcs",)))

    # Request malformed while AuthorityState remains valid: both state identities remain available and equal.
    r = request(base, t); r["future_numeric_field"] = 1.0
    out.append(c("NEG-MALFORMED-REQUEST-VALID-STATE-IDS", "receipt-audit", base, r))

    # Non-object AuthorityState: neither claimed nor recomputed state identity is recoverable.
    out.append(c("NEG-NONOBJECT-STATE", "receipt-audit", [], request(base, t)))

    # Same recomputed bytes with different forged claims must yield distinct semantic receipts.
    s = deepcopy(base); s["authority_state_id"] = "sha256:" + "3" * 64
    out.append(c("NEG-FORGED-CLAIM-A", "receipt-audit", s, request(s, t), ("dual-id",)))
    s = deepcopy(base); s["authority_state_id"] = "sha256:" + "4" * 64
    out.append(c("NEG-FORGED-CLAIM-B", "receipt-audit", s, request(s, t), ("dual-id",)))

    return out
