from __future__ import annotations

from copy import deepcopy

from reference import (
    REQUEST_SCHEMA,
    STATE_SCHEMA,
    _receipt_projection,
    authority_state_identity,
    evaluate,
    reference_identity,
    sha256_identity,
    strict_json_loads,
)

NOW = "2026-09-02T12:00:00Z"
PAST = "2026-01-01T00:00:00Z"
FUTURE = "2027-01-01T00:00:00Z"

A_COMMIT = "529c92b49a34d5c610618551a8737f019f9fa332"
B_COMMIT = "c314e53bd91c0736aa4370a364673b069aceb43e"
C_COMMIT = "5fe55f9ed5d0ee9f026ca1b077e9d70ce0487ea1"
D_COMMIT = "298a1a0f7b7b6d7712e11200d04faec3e1ca169b"

COUNT = 0


def passed():
    global COUNT
    COUNT += 1


def ref(ref_id, kind, version, immutable_id):
    return {
        "ref_id": ref_id,
        "kind": kind,
        "version": version,
        "immutable_id": immutable_id,
        "identity_sha256": reference_identity(kind, version, immutable_id),
    }


def released_refs():
    return [
        ref("A", "contract_a", "2.0.0", f"git:commit:{A_COMMIT}"),
        ref("B", "contract_b", "1.2.0", f"git:commit:{B_COMMIT}"),
        ref("C", "contract_c", "1.0.0", f"git:commit:{C_COMMIT}"),
        ref("D", "contract_d", "1.0.0", f"git:commit:{D_COMMIT}"),
    ]


def make_state(
    *,
    subject="actor:operator",
    domain="authorization",
    operation="authorize",
    scope="pipeline:v1",
    target_class="contract-d-decision",
    target_ref=None,
    basis_type="policy",
    valid_from=PAST,
    valid_until=FUTURE,
    revoked_at=None,
    delegates=(),
):
    target_ref = target_ref or released_refs()[-1]["identity_sha256"]
    records = [
        {
            "id": "auth:root",
            "basis_type": basis_type,
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
        }
    ]
    previous_id = "auth:root"
    previous_subject = subject
    for index, delegated_subject in enumerate(delegates, 1):
        records.append(
            {
                "id": f"auth:delegation:{index}",
                "basis_type": "delegation",
                "subject_id": delegated_subject,
                "domain": domain,
                "operation": operation,
                "scope": scope,
                "target_class": target_class,
                "target_ref": target_ref,
                "valid_from": valid_from,
                "valid_until": valid_until,
                "revoked_at": None,
                "parent_id": previous_id,
                "delegated_by": previous_subject,
            }
        )
        previous_id = f"auth:delegation:{index}"
        previous_subject = delegated_subject
    state = {"schema": STATE_SCHEMA, "authority_state_id": "", "records": records}
    state["authority_state_id"] = authority_state_identity(state)
    return state


def make_request(
    state,
    *,
    subject=None,
    domain=None,
    operation=None,
    scope=None,
    target_class=None,
    target_ref=None,
    refs=None,
    supporting=None,
    conflicts=None,
    residues=None,
    at=NOW,
):
    leaf = state["records"][-1] if state.get("records") else {}
    refs = released_refs() if refs is None else refs
    return {
        "schema": REQUEST_SCHEMA,
        "request_id": "req:1",
        "authority_state_id": state.get("authority_state_id", "sha256:" + "0" * 64),
        "evaluation_time": at,
        "subject_id": subject or leaf.get("subject_id", "actor:operator"),
        "jurisdiction": {
            "domain": domain or leaf.get("domain", "authorization"),
            "operation": operation or leaf.get("operation", "authorize"),
            "scope": scope or leaf.get("scope", "pipeline:v1"),
            "target_class": target_class or leaf.get("target_class", "contract-d-decision"),
            "target_ref": target_ref or leaf.get("target_ref", refs[-1]["identity_sha256"]),
        },
        "references": deepcopy(refs),
        "supporting_artifacts": deepcopy(supporting or []),
        "conflicts": deepcopy(conflicts or []),
        "residues": deepcopy(residues or []),
    }


def allow(state, request):
    out = evaluate(state, request)
    assert out["authorized"] is True, out
    assert out["authority_conferring"] is False
    assert out["claimed_authority_state_id"] == state["authority_state_id"]
    assert out["recomputed_authority_state_id"] == state["authority_state_id"]
    passed()
    return out


def deny(state, request):
    out = evaluate(state, request)
    assert out["authorized"] is False, out
    assert out["authority_conferring"] is False
    passed()
    return out


def test_positive_and_binding():
    state = make_state()
    base = allow(state, make_request(state))
    assert base["authority_basis_id"] == "auth:root"

    grant = make_state(basis_type="grant")
    allow(grant, make_request(grant))

    delegated = make_state(subject="actor:owner", delegates=("actor:delegate",))
    allow(delegated, make_request(delegated))

    for kwargs in (
        {"subject": "actor:other"},
        {"domain": "execution"},
        {"operation": "execute"},
        {"scope": "pipeline:other"},
        {"target_class": "other"},
        {"target_ref": released_refs()[0]["identity_sha256"]},
    ):
        deny(state, make_request(state, **kwargs))


def test_currentness():
    for state in (
        make_state(valid_from=FUTURE, valid_until=None),
        make_state(valid_until="2026-08-01T00:00:00Z"),
        make_state(revoked_at=NOW),
    ):
        deny(state, make_request(state))

    edge_from = make_state(valid_from=NOW)
    allow(edge_from, make_request(edge_from))
    edge_until = make_state(valid_until=NOW)
    allow(edge_until, make_request(edge_until))
    future_revoke = make_state(revoked_at=FUTURE)
    allow(future_revoke, make_request(future_revoke))


def test_delegation_lineage():
    base = make_state(subject="actor:owner", delegates=("actor:delegate",))
    for field, value in (
        ("domain", "other"),
        ("operation", "other"),
        ("scope", "other"),
        ("target_class", "other"),
        ("target_ref", released_refs()[0]["identity_sha256"]),
    ):
        state = deepcopy(base)
        state["records"][1][field] = value
        state["authority_state_id"] = authority_state_identity(state)
        deny(state, make_request(state))

    mutations = (
        lambda s: s["records"][1].__setitem__("parent_id", "auth:missing"),
        lambda s: s["records"][1].__setitem__("delegated_by", "actor:other"),
        lambda s: s["records"][1].__setitem__("id", "auth:root"),
        lambda s: s["records"][1].__setitem__("basis_type", "policy"),
    )
    for mutate in mutations:
        state = deepcopy(base)
        mutate(state)
        state["authority_state_id"] = authority_state_identity(state)
        deny(state, make_request(state))

    surplus = deepcopy(make_state())
    extra = deepcopy(surplus["records"][0])
    extra["id"] = "auth:surplus"
    extra["subject_id"] = "actor:other"
    surplus["records"].append(extra)
    surplus["authority_state_id"] = authority_state_identity(surplus)
    deny(surplus, make_request(surplus))


def test_support_blockers_and_resolution():
    state = make_state()
    support = [
        {"id": "sup:A", "artifact_type": "contract_a_declaration", "ref_id": "A"},
        {"id": "sup:B", "artifact_type": "contract_b_fact", "ref_id": "B"},
        {"id": "sup:C", "artifact_type": "contract_c_result", "ref_id": "C"},
        {"id": "sup:D", "artifact_type": "contract_d_candidate_for_authorization", "ref_id": "D"},
    ]
    out = allow(state, make_request(state, supporting=support))
    assert out["preserved"]["supporting_artifacts"] == support

    invalid_state = {
        "schema": STATE_SCHEMA,
        "authority_state_id": "sha256:" + "0" * 64,
        "records": [],
    }
    out = deny(invalid_state, make_request(state, supporting=support))
    assert out["claimed_authority_state_id"] == "sha256:" + "0" * 64
    assert out["recomputed_authority_state_id"] == authority_state_identity(invalid_state)
    assert out["claimed_authority_state_id"] != out["recomputed_authority_state_id"]

    conflict = [{"id": "c", "relevant": True, "status": "unresolved"}]
    residue = [{"id": "r", "relevant": True, "status": "contested"}]
    deny(state, make_request(state, conflicts=conflict))
    deny(state, make_request(state, residues=residue))
    allow(state, make_request(state, conflicts=[{"id": "ci", "relevant": False, "status": "unresolved"}]))
    allow(state, make_request(state, residues=[{"id": "ri", "relevant": False, "status": "contested"}]))

    forged = make_request(state)
    forged["resolved_conflict_ids"] = ["c"]
    deny(state, forged)

    conflict_ref = ref("X", "conflict", None, "conflict:42")
    resolution_state = make_state(
        domain="resolution",
        operation="resolve",
        scope="case:42",
        target_class="conflict",
        target_ref=conflict_ref["identity_sha256"],
    )
    allow(resolution_state, make_request(resolution_state, refs=[conflict_ref]))


def test_identity_and_reference_controls():
    state = make_state()

    request_mismatch = make_request(state)
    request_mismatch["authority_state_id"] = "sha256:" + "1" * 64
    deny(state, request_mismatch)

    forged_id_state = deepcopy(state)
    correct = forged_id_state["authority_state_id"]
    forged_id_state["authority_state_id"] = "sha256:" + "2" * 64
    out = deny(forged_id_state, make_request(forged_id_state))
    assert out["claimed_authority_state_id"] == "sha256:" + "2" * 64
    assert out["recomputed_authority_state_id"] == correct
    assert out["claimed_authority_state_id"] != out["recomputed_authority_state_id"]

    other_forged = deepcopy(forged_id_state)
    other_forged["authority_state_id"] = "sha256:" + "3" * 64
    other = deny(other_forged, make_request(other_forged))
    assert other["recomputed_authority_state_id"] == correct
    assert other["receipt_id"] != out["receipt_id"]

    bad_ref = make_request(state)
    bad_ref["references"][-1]["immutable_id"] += ":tampered"
    deny(state, bad_ref)

    missing_ref = make_request(state)
    missing_ref["references"] = missing_ref["references"][:-1]
    deny(state, missing_ref)

    duplicate_ref = make_request(state)
    duplicate_ref["references"].append(deepcopy(duplicate_ref["references"][0]))
    deny(state, duplicate_ref)


def test_target_lineage_and_stage_boundaries():
    parent = ref("P", "contract_a_proposition", "2.0.0", "A:parent")
    child1 = ref("C1", "contract_a_proposition", "2.0.0", "A:child:1")
    child2 = ref("C2", "contract_a_proposition", "2.0.0", "A:child:2")

    parent_state = make_state(target_class="contract-a-proposition", target_ref=parent["identity_sha256"])
    allow(parent_state, make_request(parent_state, refs=[parent]))
    deny(parent_state, make_request(parent_state, refs=[child1], target_ref=child1["identity_sha256"]))

    child_state = make_state(target_class="contract-a-proposition", target_ref=child1["identity_sha256"])
    deny(child_state, make_request(child_state, refs=[parent], target_ref=parent["identity_sha256"]))
    deny(child_state, make_request(child_state, refs=[child2], target_ref=child2["identity_sha256"]))

    decision_state = make_state()
    deny(decision_state, make_request(decision_state, domain="execution", operation="execute"))

    exec_ref = ref("E", "execution_intent", None, "intent:1")
    execution_state = make_state(
        domain="execution",
        operation="execute",
        target_class="execution_intent",
        target_ref=exec_ref["identity_sha256"],
    )
    allow(execution_state, make_request(execution_state, refs=[exec_ref]))
    deny(execution_state, make_request(execution_state, refs=[exec_ref], domain="verification", operation="verify"))

    report = ref("R", "execution_report", None, "report:1")
    verification_state = make_state(
        domain="verification",
        operation="verify",
        target_class="execution_report",
        target_ref=report["identity_sha256"],
    )
    allow(verification_state, make_request(verification_state, refs=[report]))


def test_malformed_and_receipt_semantics():
    state = make_state()
    for mutate in (
        lambda r: r.__setitem__("future_field", True),
        lambda r: r.pop("subject_id"),
        lambda r: r.__setitem__("schema", "contract-e-authorization-request-future"),
    ):
        request = make_request(state)
        mutate(request)
        deny(state, request)

    status_state = deepcopy(state)
    status_state["records"][0]["status"] = "established"
    status_state["authority_state_id"] = authority_state_identity(status_state)
    deny(status_state, make_request(state))

    denied = deny(state, make_request(state, domain="execution", operation="execute"))
    changed = deepcopy(denied)
    changed["diagnostics"] = ["different diagnostic text"]
    assert sha256_identity(_receipt_projection(changed)) == denied["receipt_id"]
    passed()

    for text in ('{"a":1,"a":2}', '{"x":NaN}'):
        try:
            strict_json_loads(text)
        except Exception:
            passed()
        else:
            raise AssertionError(text)

    cyclic = []
    cyclic.append(cyclic)
    malformed_state = {"schema": STATE_SCHEMA, "authority_state_id": "sha256:" + "4" * 64, "records": cyclic}
    out = deny(malformed_state, make_request(state))
    assert out["claimed_authority_state_id"] == "sha256:" + "4" * 64
    assert out["recomputed_authority_state_id"] is None


def test_weak_identity_controls():
    state = make_state()
    forged = deepcopy(state)
    correct = forged["authority_state_id"]
    forged["authority_state_id"] = "sha256:" + "5" * 64
    out = evaluate(forged, make_request(forged))
    assert out["authorized"] is False

    claimed_only = out["claimed_authority_state_id"]
    recomputed_only = out["recomputed_authority_state_id"]
    assert claimed_only == "sha256:" + "5" * 64
    assert recomputed_only == correct
    assert claimed_only != recomputed_only
    passed()


def main():
    test_positive_and_binding()
    test_currentness()
    test_delegation_lineage()
    test_support_blockers_and_resolution()
    test_identity_and_reference_controls()
    test_target_lineage_and_stage_boundaries()
    test_malformed_and_receipt_semantics()
    test_weak_identity_controls()
    print(f"CONTRACT_E_RC2_CORE_PASS={COUNT}")
    assert COUNT >= 50, COUNT


if __name__ == "__main__":
    main()
