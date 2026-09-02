from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from reference import (
    STATE_SCHEMA,
    REQUEST_SCHEMA,
    RECEIPT_SCHEMA,
    authority_state_identity,
    evaluate,
    reference_identity,
    sha256_identity,
)

NOW = "2026-09-02T12:00:00Z"
PAST = "2026-01-01T00:00:00Z"
FUTURE = "2027-01-01T00:00:00Z"


def ref(ref_id="T", kind="target", version="1", immutable_id="target:1"):
    return {
        "ref_id": ref_id,
        "kind": kind,
        "version": version,
        "immutable_id": immutable_id,
        "identity_sha256": reference_identity(kind, version, immutable_id),
    }


def state(
    *,
    basis="policy",
    subject="actor:operator",
    domain="authorization",
    operation="authorize",
    scope="pipeline:v1",
    target=None,
    valid_from=PAST,
    valid_until=FUTURE,
    revoked_at=None,
    delegates=(),
):
    target = target or ref()
    records = [
        {
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
        }
    ]
    parent_id = "auth:root"
    parent_subject = subject
    for i, delegated_subject in enumerate(delegates, 1):
        records.append(
            {
                "id": f"auth:delegation:{i}",
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
            }
        )
        parent_id = f"auth:delegation:{i}"
        parent_subject = delegated_subject
    out = {"schema": STATE_SCHEMA, "authority_state_id": "sha256:" + "0" * 64, "records": records}
    out["authority_state_id"] = authority_state_identity(out)
    return out, target


def request(s, target, **overrides):
    leaf = s["records"][-1] if s.get("records") else {}
    r = {
        "schema": REQUEST_SCHEMA,
        "request_id": "req:1",
        "authority_state_id": s.get("authority_state_id", "sha256:" + "0" * 64),
        "evaluation_time": NOW,
        "subject_id": leaf.get("subject_id", "actor:operator"),
        "jurisdiction": {
            "domain": leaf.get("domain", "authorization"),
            "operation": leaf.get("operation", "authorize"),
            "scope": leaf.get("scope", "pipeline:v1"),
            "target_class": leaf.get("target_class", target["kind"]),
            "target_ref": leaf.get("target_ref", target["identity_sha256"]),
        },
        "references": [deepcopy(target)],
        "supporting_artifacts": [],
        "conflicts": [],
        "residues": [],
    }
    for key, value in overrides.items():
        if key.startswith("jurisdiction__"):
            r["jurisdiction"][key.split("__", 1)[1]] = value
        else:
            r[key] = value
    return r


def check(case_id, s, r, expected, records, extra=None):
    receipt = evaluate(s, r)
    ok = receipt["authorized"] is expected and receipt["schema"] == RECEIPT_SCHEMA and receipt["authority_conferring"] is False
    if extra is not None:
        ok = ok and bool(extra(receipt))
    records.append({"id": case_id, "expected_authorized": expected, "observed_authorized": receipt["authorized"], "pass": ok})
    assert ok, (case_id, json.dumps(receipt, sort_keys=True))
    return receipt


def main():
    records = []

    base, target = state()
    check("POS-POLICY", base, request(base, target), True, records)
    grant, gt = state(basis="grant")
    check("POS-GRANT", grant, request(grant, gt), True, records)
    delegated, dt = state(subject="actor:owner", delegates=("actor:delegate",))
    check("POS-DELEGATION", delegated, request(delegated, dt), True, records)

    for name, kwargs in [
        ("NEG-SUBJECT", {"subject_id": "actor:other"}),
        ("NEG-DOMAIN", {"jurisdiction__domain": "execution"}),
        ("NEG-OPERATION", {"jurisdiction__operation": "execute"}),
        ("NEG-SCOPE", {"jurisdiction__scope": "other"}),
        ("NEG-TARGET-CLASS", {"jurisdiction__target_class": "other"}),
    ]:
        check(name, base, request(base, target, **kwargs), False, records)
    other = ref("O", "other", "1", "other:1")
    check("NEG-TARGET-REF", base, request(base, target, references=[other], jurisdiction__target_ref=other["identity_sha256"]), False, records)

    for name, st in [
        ("NEG-FUTURE", state(valid_from=FUTURE, valid_until=None)),
        ("NEG-STALE", state(valid_until="2026-08-01T00:00:00Z")),
        ("NEG-REVOKED", state(revoked_at=NOW)),
    ]:
        s, t = st
        check(name, s, request(s, t), False, records)
    s, t = state(valid_from=NOW)
    check("POS-VALID-FROM-EDGE", s, request(s, t), True, records)
    s, t = state(valid_until=NOW)
    check("POS-VALID-UNTIL-EDGE", s, request(s, t), True, records)
    s, t = state(revoked_at=FUTURE)
    check("POS-REVOCATION-FUTURE", s, request(s, t), True, records)

    for field, value in [
        ("domain", "other"),
        ("operation", "other"),
        ("scope", "other"),
        ("target_class", "other"),
        ("target_ref", other["identity_sha256"]),
    ]:
        s = deepcopy(delegated)
        s["records"][1][field] = value
        s["authority_state_id"] = authority_state_identity(s)
        check(f"NEG-DELEGATION-{field.upper()}", s, request(s, dt), False, records)

    for label, mut in [
        ("PARENT", lambda s: s["records"][1].__setitem__("parent_id", "missing")),
        ("DELEGATED-BY", lambda s: s["records"][1].__setitem__("delegated_by", "actor:other")),
        ("DUP-ID", lambda s: s["records"][1].__setitem__("id", "auth:root")),
        ("NON-DELEGATION", lambda s: s["records"][1].__setitem__("basis_type", "policy")),
    ]:
        s = deepcopy(delegated)
        mut(s)
        s["authority_state_id"] = authority_state_identity(s)
        check(f"NEG-LINEAGE-{label}", s, request(s, dt), False, records)

    dref = ref("D", "contract-d", "1.0.0", "decision:trusted")
    support = [{"id": "sup:D", "artifact_type": "contract_d_candidate_for_authorization", "ref_id": "D"}]
    r = request(base, target)
    r["references"].append(dref)
    r["supporting_artifacts"] = deepcopy(support)
    check("POS-SUPPORT-NONCONFERRING", base, r, True, records)

    invalid = {"schema": STATE_SCHEMA, "authority_state_id": "sha256:" + "0" * 64, "records": []}
    r = request(base, target)
    r["references"].append(dref)
    r["supporting_artifacts"] = deepcopy(support)
    r["authority_state_id"] = invalid["authority_state_id"]
    receipt_support = check(
        "NEG-SUPPORT-CANNOT-CONFER",
        invalid,
        r,
        False,
        records,
        lambda x: x["claimed_authority_state_id"] == invalid["authority_state_id"]
        and x["recomputed_authority_state_id"] not in (None, invalid["authority_state_id"]),
    )

    check("NEG-CONFLICT", base, request(base, target, conflicts=[{"id": "c", "relevant": True, "status": "unresolved"}]), False, records)
    check("NEG-RESIDUE", base, request(base, target, residues=[{"id": "r", "relevant": True, "status": "contested"}]), False, records)
    check("POS-IRRELEVANT-CONFLICT", base, request(base, target, conflicts=[{"id": "c", "relevant": False, "status": "unresolved"}]), True, records)
    check("POS-IRRELEVANT-RESIDUE", base, request(base, target, residues=[{"id": "r", "relevant": False, "status": "contested"}]), True, records)

    for field in ("resolved_conflict_ids", "resolved_residue_ids", "future_field"):
        r = request(base, target)
        r[field] = [] if field.startswith("resolved") else True
        check(f"NEG-UNKNOWN-{field.upper()}", base, r, False, records)
    r = request(base, target); del r["subject_id"]
    check("NEG-MISSING-SUBJECT", base, r, False, records)
    r = request(base, target); r["schema"] = "contract-e-authorization-request-future"
    check("NEG-FUTURE-E-SCHEMA", base, r, False, records)
    s = deepcopy(base); s["records"][0]["status"] = "established"; s["authority_state_id"] = authority_state_identity(s)
    check("NEG-STATUS-ESTABLISHED", s, request(s, target), False, records)

    r = request(base, target); r["authority_state_id"] = "sha256:" + "1" * 64
    check("NEG-STATE-BINDING", base, r, False, records)
    s = deepcopy(base); claimed = "sha256:" + "2" * 64; s["authority_state_id"] = claimed
    receipt_state_id = check(
        "NEG-STATE-ID",
        s,
        request(s, target),
        False,
        records,
        lambda x: x["claimed_authority_state_id"] == claimed
        and x["recomputed_authority_state_id"] == authority_state_identity(base),
    )

    r = request(base, target); r["references"][0]["immutable_id"] = "tampered"
    check("NEG-REFERENCE-HASH", base, r, False, records)
    r = request(base, target); r["references"] = []
    check("NEG-REFERENCE-MISSING", base, r, False, records)

    parent = ref("P", "contract-a-proposition", "2.0.0", "A:parent")
    child1 = ref("C1", "contract-a-proposition", "2.0.0", "A:child:1")
    child2 = ref("C2", "contract-a-proposition", "2.0.0", "A:child:2")
    ps, _ = state(target=parent)
    check("POS-PARENT", ps, request(ps, parent), True, records)
    check("NEG-PARENT-TO-CHILD", ps, request(ps, parent, references=[child1], jurisdiction__target_ref=child1["identity_sha256"]), False, records)
    cs, _ = state(target=child1)
    check("NEG-CHILD-TO-PARENT", cs, request(cs, child1, references=[parent], jurisdiction__target_ref=parent["identity_sha256"]), False, records)
    check("NEG-SIBLING", cs, request(cs, child1, references=[child2], jurisdiction__target_ref=child2["identity_sha256"]), False, records)

    conflict = ref("X", "conflict", None, "conflict:42")
    rs, _ = state(domain="resolution", operation="resolve", scope="case:42", target=conflict)
    check("POS-RESOLUTION-AUTH", rs, request(rs, conflict, conflicts=[{"id": "c", "relevant": True, "status": "unresolved"}]), True, records)
    ex, et = state(domain="execution", operation="execute")
    check("POS-EXECUTION-AUTH", ex, request(ex, et), True, records)
    check("NEG-EXECUTION-NOT-VERIFICATION", ex, request(ex, et, jurisdiction__domain="verification", jurisdiction__operation="verify"), False, records)
    check("NEG-DECISION-NOT-EXECUTION", base, request(base, target, jurisdiction__domain="execution", jurisdiction__operation="execute"), False, records)
    vr = ref("R", "execution-report", "1", "report:1")
    vs, _ = state(domain="verification", operation="verify", target=vr)
    check("POS-VERIFICATION-SEPARATE", vs, request(vs, vr), True, records)

    surplus = deepcopy(base)
    extra = deepcopy(surplus["records"][0]); extra["id"] = "auth:surplus"; extra["subject_id"] = "other"
    surplus["records"].append(extra); surplus["authority_state_id"] = authority_state_identity(surplus)
    check("NEG-SURPLUS-PEER", surplus, request(surplus, target), False, records)

    # RC2-specific identity obligations.
    good = evaluate(base, request(base, target))
    assert good["claimed_authority_state_id"] == good["recomputed_authority_state_id"] == base["authority_state_id"]
    records.append({"id": "RC2-VALID-DUAL-ID", "pass": True})

    malformed_claim = deepcopy(base); malformed_claim["authority_state_id"] = "not-a-sha"
    r = request(base, target); r["authority_state_id"] = "sha256:" + "0" * 64
    rec = check("RC2-MALFORMED-CLAIM", malformed_claim, r, False, records, lambda x: x["claimed_authority_state_id"] is None and x["recomputed_authority_state_id"] is not None)

    nonobject = ["not", "a", "state"]
    rec = check("RC2-NONOBJECT", nonobject, request(base, target), False, records, lambda x: x["claimed_authority_state_id"] is None and x["recomputed_authority_state_id"] is None)

    r = request(s, target); r["authority_state_id"] = claimed
    check("RC2-REQUEST-CANNOT-OVERRIDE-ID-MISMATCH", s, r, False, records)
    assert good["claimed_authority_state_id"] is not None and good["recomputed_authority_state_id"] is not None
    records.append({"id": "RC2-AUTHORIZED-DUAL-ID-INVARIANT", "pass": True})

    # Semantic receipt identity binds both dual fields and excludes diagnostics.
    semantic = deepcopy(receipt_state_id)
    semantic["diagnostics"] = ["arbitrary", "changed"]
    semantic["receipt_id"] = sha256_identity({k: deepcopy(v) for k, v in semantic.items() if k not in {"receipt_id", "diagnostics"}})
    assert semantic["receipt_id"] == receipt_state_id["receipt_id"]
    records.append({"id": "RC2-DIAGNOSTIC-INVARIANCE", "pass": True})

    changed_claim = deepcopy(receipt_state_id)
    changed_claim["claimed_authority_state_id"] = "sha256:" + "3" * 64
    changed_claim_id = sha256_identity({k: deepcopy(v) for k, v in changed_claim.items() if k not in {"receipt_id", "diagnostics"}})
    assert changed_claim_id != receipt_state_id["receipt_id"]
    records.append({"id": "RC2-CLAIMED-ID-BINDS-RECEIPT", "pass": True})

    changed_recomputed = deepcopy(receipt_state_id)
    changed_recomputed["recomputed_authority_state_id"] = "sha256:" + "4" * 64
    changed_recomputed_id = sha256_identity({k: deepcopy(v) for k, v in changed_recomputed.items() if k not in {"receipt_id", "diagnostics"}})
    assert changed_recomputed_id != receipt_state_id["receipt_id"]
    records.append({"id": "RC2-RECOMPUTED-ID-BINDS-RECEIPT", "pass": True})

    assert receipt_support["claimed_authority_state_id"] != receipt_support["recomputed_authority_state_id"]
    records.append({"id": "RC2-NO-IDENTITY-ALIAS", "pass": True})

    old = deepcopy(request(base, target)); old["schema"] = "contract-e-authorization-request-candidate-rc1"
    check("RC2-RC1-SCHEMA-REJECTED", base, old, False, records)

    output = {
        "status": "PASS",
        "case_count": len(records),
        "passed": sum(1 for r in records if r.get("pass")),
        "failed": [r["id"] for r in records if not r.get("pass")],
        "records": records,
    }
    Path("RESULTS.json").write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: output[k] for k in ("status", "case_count", "passed", "failed")}, sort_keys=True))


if __name__ == "__main__":
    main()
