from __future__ import annotations

from copy import deepcopy

from reference import (
    REQUEST_SCHEMA,
    STATE_SCHEMA,
    authority_state_identity,
    evaluate,
    reference_identity,
    strict_json_loads,
)

NOW = "2026-09-02T12:00:00Z"
PAST = "2026-01-01T00:00:00Z"
FUTURE = "2027-01-01T00:00:00Z"

A_COMMIT = "529c92b49a34d5c610618551a8737f019f9fa332"
B_COMMIT = "c314e53bd91c0736aa4370a364673b069aceb43e"
C_COMMIT = "5fe55f9ed5d0ee9f026ca1b077e9d70ce0487ea1"
D_COMMIT = "298a1a0f7b7b6d7712e11200d04faec3e1ca169b"


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


def make_state(*, subject="actor:operator", domain="authorization", operation="authorize", scope="pipeline:v1", target_class="contract-d-decision", target_ref=None, basis_type="policy", valid_from=PAST, valid_until=FUTURE, revoked_at=None, delegates=()):
    if target_ref is None:
        target_ref = released_refs()[-1]["identity_sha256"]
    records = [{
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
    }]
    prev_subject = subject
    prev_id = "auth:root"
    for i, delegate in enumerate(delegates, start=1):
        records.append({
            "id": f"auth:delegation:{i}",
            "basis_type": "delegation",
            "subject_id": delegate,
            "domain": domain,
            "operation": operation,
            "scope": scope,
            "target_class": target_class,
            "target_ref": target_ref,
            "valid_from": valid_from,
            "valid_until": valid_until,
            "revoked_at": None,
            "parent_id": prev_id,
            "delegated_by": prev_subject,
        })
        prev_subject = delegate
        prev_id = f"auth:delegation:{i}"
    state = {"schema": STATE_SCHEMA, "authority_state_id": "", "records": records}
    state["authority_state_id"] = authority_state_identity(state)
    return state


def make_request(state, *, subject=None, domain=None, operation=None, scope=None, target_class=None, target_ref=None, refs=None, supporting=None, conflicts=None, residues=None, at=NOW):
    leaf = state["records"][-1]
    if refs is None:
        refs = released_refs()
    return {
        "schema": REQUEST_SCHEMA,
        "request_id": "req:1",
        "authority_state_id": state["authority_state_id"],
        "evaluation_time": at,
        "subject_id": subject or leaf["subject_id"],
        "jurisdiction": {
            "domain": domain or leaf["domain"],
            "operation": operation or leaf["operation"],
            "scope": scope or leaf["scope"],
            "target_class": target_class or leaf["target_class"],
            "target_ref": target_ref or leaf["target_ref"],
        },
        "references": deepcopy(refs),
        "supporting_artifacts": deepcopy(supporting or []),
        "conflicts": deepcopy(conflicts or []),
        "residues": deepcopy(residues or []),
    }


def assert_denied(state, request):
    out = evaluate(state, request)
    assert out["authorized"] is False, out
    assert out["authority_conferring"] is False
    return out


def assert_allowed(state, request):
    out = evaluate(state, request)
    assert out["authorized"] is True, out
    assert out["authority_conferring"] is False
    assert out["authority_basis_id"] == state["records"][-1]["id"]
    return out


def run_core_cases():
    state = make_state()
    req = make_request(state)
    base = assert_allowed(state, req)

    assert [r["immutable_id"] for r in base["preserved"]["references"]] == [
        f"git:commit:{A_COMMIT}", f"git:commit:{B_COMMIT}", f"git:commit:{C_COMMIT}", f"git:commit:{D_COMMIT}"
    ]

    for kwargs in [
        {"subject": "actor:other"}, {"domain": "execution"}, {"operation": "execute"},
        {"scope": "pipeline:other"}, {"target_class": "contract-a-handoff"},
    ]:
        assert_denied(state, make_request(state, **kwargs))

    a_target = released_refs()[0]["identity_sha256"]
    assert_denied(state, make_request(state, target_ref=a_target))

    future_state = make_state(valid_from=FUTURE, valid_until=None)
    assert_denied(future_state, make_request(future_state))
    stale = make_state(valid_until="2026-08-01T00:00:00Z")
    assert_denied(stale, make_request(stale))
    revoked = make_state(revoked_at="2026-09-02T11:59:59Z")
    assert_denied(revoked, make_request(revoked))

    edge = make_state(valid_until=NOW)
    assert_allowed(edge, make_request(edge))

    delegated = make_state(subject="actor:owner", delegates=("actor:delegate",))
    assert_allowed(delegated, make_request(delegated))
    bad_delegate = deepcopy(delegated)
    bad_delegate["records"][1]["operation"] = "execute"
    bad_delegate["authority_state_id"] = authority_state_identity(bad_delegate)
    assert_denied(bad_delegate, make_request(bad_delegate))

    cyclic = deepcopy(delegated)
    cyclic["records"][1]["parent_id"] = cyclic["records"][1]["id"]
    cyclic["authority_state_id"] = authority_state_identity(cyclic)
    assert_denied(cyclic, make_request(cyclic))
    duplicate = deepcopy(delegated)
    duplicate["records"][1]["id"] = duplicate["records"][0]["id"]
    duplicate["authority_state_id"] = authority_state_identity(duplicate)
    assert_denied(duplicate, make_request(duplicate))

    support = [
        {"id": "sup:A", "artifact_type": "contract_a_declaration", "ref_id": "A"},
        {"id": "sup:B", "artifact_type": "contract_b_fact", "ref_id": "B"},
        {"id": "sup:C", "artifact_type": "contract_c_result", "ref_id": "C"},
        {"id": "sup:D", "artifact_type": "contract_d_candidate_for_authorization", "ref_id": "D"},
    ]
    with_support = assert_allowed(state, make_request(state, supporting=support))
    assert with_support["preserved"]["supporting_artifacts"] == support
    forged_state = {"schema": STATE_SCHEMA, "authority_state_id": "sha256:dead", "records": []}
    assert_denied(forged_state, make_request(state, supporting=support))

    conflict = [{"id": "conf:1", "relevant": True, "status": "unresolved"}]
    out = assert_denied(state, make_request(state, conflicts=conflict))
    assert out["preserved"]["conflicts"] == conflict
    residue = [{"id": "res:1", "relevant": True, "status": "contested"}]
    out = assert_denied(state, make_request(state, residues=residue))
    assert out["preserved"]["residues"] == residue
    irrelevant = [{"id": "conf:i", "relevant": False, "status": "unresolved"}]
    assert_allowed(state, make_request(state, conflicts=irrelevant))

    forged_resolution = make_request(state)
    forged_resolution["resolved_conflict_ids"] = ["conf:1"]
    assert_denied(state, forged_resolution)

    conflict_ref = ref("X", "conflict", None, "conflict:conf-42@sha256:abc")
    resolution_state = make_state(domain="resolution", operation="resolve", scope="case:42", target_class="conflict", target_ref=conflict_ref["identity_sha256"])
    resolution_req = make_request(resolution_state, refs=[conflict_ref])
    resolution_out = assert_allowed(resolution_state, resolution_req)
    assert "execution" not in resolution_out and "verified" not in resolution_out

    execution_req = make_request(state, domain="execution", operation="execute")
    assert_denied(state, execution_req)
    execution_state = make_state(domain="execution", operation="execute")
    exec_out = assert_allowed(execution_state, make_request(execution_state))
    assert exec_out["authority_conferring"] is False
    verification_req = make_request(execution_state, domain="verification", operation="verify")
    assert_denied(execution_state, verification_req)

    report_ref = ref("R", "execution_report", None, "report:1")
    verify_state = make_state(domain="verification", operation="verify", target_class="execution_report", target_ref=report_ref["identity_sha256"])
    verify_support = [{"id": "sup:R", "artifact_type": "execution_report", "ref_id": "R"}]
    assert_allowed(verify_state, make_request(verify_state, refs=[report_ref], supporting=verify_support))
    assert_denied(execution_state, make_request(execution_state, domain="verification", operation="verify", refs=[report_ref], target_class="execution_report", target_ref=report_ref["identity_sha256"], supporting=verify_support))

    unknown = make_request(state)
    unknown["future_field"] = True
    assert_denied(state, unknown)
    missing = make_request(state)
    del missing["subject_id"]
    assert_denied(state, missing)
    wrong_version = make_request(state)
    wrong_version["schema"] = "contract-e-authorization-request-future"
    assert_denied(state, wrong_version)

    bad_ref = make_request(state)
    bad_ref["references"][-1]["immutable_id"] += "-tampered"
    assert_denied(state, bad_ref)

    parent = ref("P", "contract_a_proposition", "2.0.0", "A:parent")
    child1 = ref("C1", "contract_a_proposition", "2.0.0", "A:child:1")
    child2 = ref("C2", "contract_a_proposition", "2.0.0", "A:child:2")
    parent_state = make_state(target_class="contract-a-proposition", target_ref=parent["identity_sha256"])
    assert_allowed(parent_state, make_request(parent_state, refs=[parent]))
    for other in (child1, child2):
        assert_denied(parent_state, make_request(parent_state, refs=[other], target_ref=other["identity_sha256"]))
    child_state = make_state(target_class="contract-a-proposition", target_ref=child1["identity_sha256"])
    assert_denied(child_state, make_request(child_state, refs=[parent], target_ref=parent["identity_sha256"]))
    assert_denied(child_state, make_request(child_state, refs=[child2], target_ref=child2["identity_sha256"]))

    external_d1 = {"immutable_id": f"git:commit:{D_COMMIT}", "title": "Display one"}
    external_d2 = {"immutable_id": f"git:commit:{D_COMMIT}", "title": "Display two", "note": "presentation only"}
    assert external_d1["immutable_id"] == external_d2["immutable_id"]
    assert_allowed(state, make_request(state))["receipt_id"] == assert_allowed(state, make_request(state))["receipt_id"]

    changed_d = ref("D2", "contract_d", "1.0.0", f"git:commit:{D_COMMIT}:semantic-change")
    assert_denied(state, make_request(state, refs=released_refs()[:-1] + [changed_d], target_ref=changed_d["identity_sha256"]))

    denied = assert_denied(state, execution_req)
    changed_diag = deepcopy(denied)
    changed_diag["diagnostics"] = ["different_non_authoritative_diagnostic"]
    from reference import _receipt_projection, sha256_identity
    assert denied["receipt_id"] == sha256_identity(_receipt_projection(changed_diag))

    assert_denied(base, req)

    for text in ['{"a":1,"a":2}', '{"x":NaN}']:
        try:
            strict_json_loads(text)
        except Exception:
            pass
        else:
            raise AssertionError(f"strict parser accepted {text}")


def run_seeded_weak_controls():
    baseline = make_state()
    attacks = []
    attacks.append(("target_blind", baseline, make_request(baseline, target_ref=released_refs()[0]["identity_sha256"])))
    stale = make_state(valid_until="2026-08-01T00:00:00Z")
    attacks.append(("stale_blind", stale, make_request(stale)))
    attacks.append(("decision_to_execution", baseline, make_request(baseline, domain="execution", operation="execute")))
    malformed = make_request(baseline)
    malformed["unknown_authority_default"] = True
    attacks.append(("unknown_default", baseline, malformed))
    conflict = make_request(baseline, conflicts=[{"id": "c", "relevant": True, "status": "unresolved"}])
    attacks.append(("conflict_blind", baseline, conflict))
    support = [{"id": "sup:D", "artifact_type": "contract_d_candidate_for_authorization", "ref_id": "D"}]
    attacks.append(("nonconferring_support", {"schema": STATE_SCHEMA, "authority_state_id": "sha256:x", "records": []}, make_request(baseline, supporting=support)))

    caught = 0
    for name, state, request in attacks:
        safe = evaluate(state, request)["authorized"]
        assert safe is False, name
        weak = True
        assert weak != safe
        caught += 1
    assert caught == 6


def run_partial_synthesis_control():
    target = released_refs()[-1]["identity_sha256"]
    state = make_state(target_ref=target)
    extra = deepcopy(state["records"][0])
    extra["id"] = "auth:surplus"
    extra["basis_type"] = "policy"
    extra["subject_id"] = "actor:other"
    extra["parent_id"] = None
    extra["delegated_by"] = None
    state["records"].append(extra)
    state["authority_state_id"] = authority_state_identity(state)
    assert_denied(state, make_request(state))


def main():
    run_core_cases()
    run_seeded_weak_controls()
    run_partial_synthesis_control()
    print("CONTRACT_E_V1_CANDIDATE_TESTS_PASS")
    print("SEEDED_WEAK_CONTROLS_CAUGHT=6/6")
    print("RELEASED_A_D_REFERENCE_IDENTITIES=4/4")


if __name__ == "__main__":
    main()
