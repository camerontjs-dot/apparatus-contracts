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


def make_state(*, subject="actor:operator", domain="authorization", operation="authorize", scope="pipeline:v1", target_class="contract-d-decision", target_ref=None, valid_from=PAST, valid_until=FUTURE, revoked_at=None, delegates=()):
    if target_ref is None:
        target_ref = released_refs()[-1]["identity_sha256"]
    records = [{
        "id": "auth:root",
        "basis_type": "policy",
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
    prev_id = "auth:root"
    prev_subject = subject
    for i, delegate in enumerate(delegates, 1):
        records.append({
            "id": f"auth:d:{i}",
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
        prev_id = f"auth:d:{i}"
        prev_subject = delegate
    state = {"schema": STATE_SCHEMA, "authority_state_id": "sha256:" + "0" * 64, "records": records}
    state["authority_state_id"] = authority_state_identity(state)
    return state


def make_request(state, *, subject=None, domain=None, operation=None, scope=None, target_class=None, target_ref=None, refs=None, supporting=None, conflicts=None, residues=None, at=NOW):
    leaf = state["records"][-1]
    refs = deepcopy(released_refs() if refs is None else refs)
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
        "references": refs,
        "supporting_artifacts": deepcopy(supporting or []),
        "conflicts": deepcopy(conflicts or []),
        "residues": deepcopy(residues or []),
    }


def denied(state, request):
    out = evaluate(state, request)
    assert out["authorized"] is False, out
    assert out["authority_conferring"] is False
    return out


def allowed(state, request):
    out = evaluate(state, request)
    assert out["authorized"] is True, out
    assert out["authority_conferring"] is False
    assert out["authority_basis_id"] == state["records"][-1]["id"]
    assert out["authority_state_claimed_id"] == state["authority_state_id"]
    assert out["authority_state_computed_id"] == state["authority_state_id"]
    return out


def dual_identity_cases():
    state = make_state()
    req = make_request(state)
    good = allowed(state, req)
    assert good["authority_state_claimed_id"] == good["authority_state_computed_id"]

    forged = deepcopy(state)
    computed = authority_state_identity(forged)
    forged["authority_state_id"] = "sha256:" + "1" * 64
    out = denied(forged, req)
    assert out["authority_state_claimed_id"] == forged["authority_state_id"]
    assert out["authority_state_computed_id"] == computed
    assert out["authority_state_claimed_id"] != out["authority_state_computed_id"]
    assert out["receipt_id"] == sha256_identity(_receipt_projection(out))

    malformed_claim = deepcopy(state)
    malformed_claim["authority_state_id"] = "sha256:dead"
    out = denied(malformed_claim, req)
    assert out["authority_state_claimed_id"] is None
    assert out["authority_state_computed_id"] == authority_state_identity(malformed_claim)

    support = [{"id": "sup:D", "artifact_type": "contract_d_candidate_for_authorization", "ref_id": "D"}]
    no_authority = {"schema": STATE_SCHEMA, "authority_state_id": "sha256:" + "2" * 64, "records": []}
    out = denied(no_authority, make_request(state, supporting=support))
    assert out["authority_state_claimed_id"] == no_authority["authority_state_id"]
    assert out["authority_state_computed_id"] == authority_state_identity(no_authority)


def exact_time_cases():
    state = make_state(valid_until="2026-09-02T12:00:00.1234567Z")
    allowed(state, make_request(state, at="2026-09-02T12:00:00.1234567Z"))
    denied(state, make_request(state, at="2026-09-02T12:00:00.1234568Z"))

    revoked = make_state(revoked_at="2026-09-02T12:00:00.1234567Z")
    allowed(revoked, make_request(revoked, at="2026-09-02T12:00:00.1234566Z"))
    denied(revoked, make_request(revoked, at="2026-09-02T12:00:00.1234567Z"))
    denied(state, make_request(state, at="2026-09-02T12:00:60Z"))


def authority_cases():
    state = make_state()
    req = make_request(state)
    base = allowed(state, req)
    assert [r["immutable_id"] for r in base["preserved"]["references"]] == [
        f"git:commit:{A_COMMIT}", f"git:commit:{B_COMMIT}", f"git:commit:{C_COMMIT}", f"git:commit:{D_COMMIT}"
    ]

    for kw in [
        {"subject": "actor:other"}, {"domain": "execution"}, {"operation": "execute"},
        {"scope": "pipeline:other"}, {"target_class": "other-class"},
    ]:
        denied(state, make_request(state, **kw))
    denied(state, make_request(state, target_ref=released_refs()[0]["identity_sha256"]))

    denied(make_state(valid_from=FUTURE, valid_until=None), make_request(make_state(valid_from=FUTURE, valid_until=None)))
    stale = make_state(valid_until="2026-08-01T00:00:00Z")
    denied(stale, make_request(stale))
    revoked = make_state(revoked_at="2026-09-02T11:59:59Z")
    denied(revoked, make_request(revoked))
    edge = make_state(valid_until=NOW)
    allowed(edge, make_request(edge))

    delegated = make_state(subject="owner", delegates=("delegate",))
    allowed(delegated, make_request(delegated))
    bad = deepcopy(delegated)
    bad["records"][1]["scope"] = "other"
    bad["authority_state_id"] = authority_state_identity(bad)
    denied(bad, make_request(bad))

    support = [{"id": "sup:D", "artifact_type": "contract_d_candidate_for_authorization", "ref_id": "D"}]
    allowed(state, make_request(state, supporting=support))
    denied(state, make_request(state, supporting=[{"id": "sup:X", "artifact_type": "x", "ref_id": "missing"}]))

    conflict = [{"id": "c", "relevant": True, "status": "unresolved"}]
    out = denied(state, make_request(state, conflicts=conflict))
    assert out["preserved"]["conflicts"] == conflict
    allowed(state, make_request(state, conflicts=[{"id": "i", "relevant": False, "status": "unresolved"}]))

    conflict_ref = ref("X", "conflict", None, "conflict:42")
    resolution_state = make_state(domain="resolution", operation="resolve", scope="case:42", target_class="conflict", target_ref=conflict_ref["identity_sha256"])
    allowed(resolution_state, make_request(resolution_state, refs=[conflict_ref]))
    denied(resolution_state, make_request(resolution_state, refs=[conflict_ref], conflicts=conflict))

    dup_ref = make_request(state)
    dup_ref["references"].append(deepcopy(dup_ref["references"][0]))
    denied(state, dup_ref)
    denied(state, make_request(state, supporting=[
        {"id": "s", "artifact_type": "a", "ref_id": "A"},
        {"id": "s", "artifact_type": "b", "ref_id": "B"},
    ]))
    denied(state, make_request(state, conflicts=[
        {"id": "c", "relevant": False, "status": "unresolved"},
        {"id": "c", "relevant": False, "status": "contested"},
    ]))

    malformed = make_request(state)
    malformed["conflicts"] = [{"id": "c", "relevant": True, "status": []}]
    out = denied(state, malformed)
    assert out["preserved"]["conflicts"] == []

    future = make_request(state)
    future["future_field"] = True
    denied(state, future)
    denied(base, req)

    for text in ['{"a":1,"a":2}', '{"x":NaN}']:
        try:
            strict_json_loads(text)
        except Exception:
            pass
        else:
            raise AssertionError(text)


def weak_controls():
    state = make_state()
    attacks = [
        make_request(state, target_ref=released_refs()[0]["identity_sha256"]),
        make_request(make_state(valid_until="2026-08-01T00:00:00Z")),
        make_request(state, domain="execution", operation="execute"),
        make_request(state, conflicts=[{"id": "c", "relevant": True, "status": "unresolved"}]),
    ]
    malformed = make_request(state)
    malformed["unknown"] = True
    attacks.append(malformed)
    for request in attacks:
        source_state = state
        if request["authority_state_id"] != state["authority_state_id"]:
            source_state = make_state(valid_until="2026-08-01T00:00:00Z")
        assert evaluate(source_state, request)["authorized"] is False

    support = [{"id": "sup:D", "artifact_type": "contract_d_candidate_for_authorization", "ref_id": "D"}]
    no_authority = {"schema": STATE_SCHEMA, "authority_state_id": "sha256:" + "4" * 64, "records": []}
    assert evaluate(no_authority, make_request(state, supporting=support))["authorized"] is False


def main():
    dual_identity_cases()
    exact_time_cases()
    authority_cases()
    weak_controls()
    print("CONTRACT_E_V1_RC2_CANDIDATE_TESTS_PASS")
    print("DUAL_STATE_IDENTITY_REGRESSIONS=4/4")
    print("EXACT_FRACTIONAL_CURRENTNESS_REGRESSIONS=5/5")
    print("SEEDED_WEAK_CONTROLS_CAUGHT=6/6")
    print("RELEASED_A_D_REFERENCE_IDENTITIES=4/4")


if __name__ == "__main__":
    main()
