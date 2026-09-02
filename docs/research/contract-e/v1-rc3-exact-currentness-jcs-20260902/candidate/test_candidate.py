from __future__ import annotations

from copy import deepcopy

import rfc8785

import reference as e


def expect(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(label)


def target(label: str = "target:1", ref_id: str = "T") -> dict:
    kind = "test_target"
    version = "1"
    return {
        "ref_id": ref_id,
        "kind": kind,
        "version": version,
        "immutable_id": label,
        "identity_sha256": e.reference_identity(kind, version, label),
    }


def seal(state: dict) -> dict:
    out = deepcopy(state)
    out["authority_state_id"] = e.authority_state_identity(out)
    return out


def make_state(
    *,
    subject: str = "actor:operator",
    domain: str = "knowledge",
    operation: str = "knowledge.cite_as_evidence",
    scope: str = "claim",
    target_class: str = "test_target",
    ref: dict | None = None,
    valid_from: str = "2026-09-02T17:00:00Z",
    valid_until: str | None = "2026-09-02T19:00:00Z",
    revoked_at: str | None = None,
    delegates: tuple[str, ...] = (),
) -> tuple[dict, dict]:
    ref = deepcopy(ref or target())
    records = [{
        "id": "auth:root",
        "basis_type": "policy",
        "subject_id": subject,
        "domain": domain,
        "operation": operation,
        "scope": scope,
        "target_class": target_class,
        "target_ref": ref["identity_sha256"],
        "valid_from": valid_from,
        "valid_until": valid_until,
        "revoked_at": revoked_at,
        "parent_id": None,
        "delegated_by": None,
    }]
    parent_id = "auth:root"
    parent_subject = subject
    for index, delegated_subject in enumerate(delegates, 1):
        records.append({
            "id": f"auth:delegation:{index}",
            "basis_type": "delegation",
            "subject_id": delegated_subject,
            "domain": domain,
            "operation": operation,
            "scope": scope,
            "target_class": target_class,
            "target_ref": ref["identity_sha256"],
            "valid_from": valid_from,
            "valid_until": valid_until,
            "revoked_at": revoked_at,
            "parent_id": parent_id,
            "delegated_by": parent_subject,
        })
        parent_id = f"auth:delegation:{index}"
        parent_subject = delegated_subject
    state = {
        "schema": e.STATE_SCHEMA,
        "authority_state_id": "sha256:" + "0" * 64,
        "records": records,
    }
    return seal(state), ref


def request(
    state: dict,
    ref: dict,
    *,
    at: str = "2026-09-02T18:00:00Z",
    subject: str | None = None,
    domain: str | None = None,
    operation: str | None = None,
    scope: str | None = None,
    target_class: str | None = None,
    target_ref: str | None = None,
    references: list[dict] | None = None,
    support: list[dict] | None = None,
    conflicts: list[dict] | None = None,
    residues: list[dict] | None = None,
) -> dict:
    leaf = state["records"][-1]
    return {
        "schema": e.REQUEST_SCHEMA,
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
        "references": deepcopy(references if references is not None else [ref]),
        "supporting_artifacts": deepcopy(support or []),
        "conflicts": deepcopy(conflicts or []),
        "residues": deepcopy(residues or []),
    }


def test_canonicalization() -> int:
    count = 0
    for value in [
        {"x": 1.0},
        {"x": -0.0},
        {"x": 1e-6},
        {"x": 1e20},
        {"é": "unicode", "a": 1},
    ]:
        expect(e.canonical_bytes(value) == rfc8785.dumps(value) + b"\n", f"JCS mismatch: {value!r}")
        count += 1
    for bad in [{"x": float("nan")}, {"x": float("inf")}, {"x": 10 ** 400}]:
        try:
            e.canonical_bytes(bad)
        except Exception:
            pass
        else:
            raise AssertionError(f"JCS domain accepted invalid value: {bad!r}")
        count += 1
    try:
        e.strict_json_loads('{"x":1,"x":2}')
    except e.InvalidCanonicalJSON:
        pass
    else:
        raise AssertionError("duplicate raw member was not rejected")
    count += 1
    return count


def test_exact_time() -> int:
    pairs = [
        ("2026-09-02T18:00:00.1234567Z", "2026-09-02T18:00:00.1234568Z", -1),
        ("2026-09-02T18:00:00.1Z", "2026-09-02T18:00:00.100Z", 0),
        ("2026-09-02T18:00:00.1000000000000000001Z", "2026-09-02T18:00:00.1Z", 1),
        ("2026-09-02T17:59:59.9999999999999999999Z", "2026-09-02T18:00:00Z", -1),
    ]
    for left, right, expected in pairs:
        observed = e._compare_time(left, right)
        expect(observed == expected, f"time compare {left} {right}: {observed} != {expected}")
    for bad in [
        "2026-02-30T00:00:00Z",
        "2026-09-02T18:00:60Z",
        "2026-09-02T24:00:00Z",
        "2026-09-02T18:00:00.Z",
        "2026-09-02T18:00:00+00:00",
    ]:
        expect(not e._safe_time(bad), f"invalid timestamp accepted: {bad}")
    return len(pairs) + 5


def test_fractional_currentness() -> int:
    count = 0
    s, t = make_state(valid_from="2026-09-02T18:00:00.1234568Z")
    expect(not e.evaluate(s, request(s, t, at="2026-09-02T18:00:00.1234567Z"))["authorized"], "pre-valid-from false permit")
    count += 1
    s, t = make_state(valid_until="2026-09-02T18:00:00.1234567Z")
    expect(not e.evaluate(s, request(s, t, at="2026-09-02T18:00:00.1234568Z"))["authorized"], "post-valid-until false permit")
    count += 1
    s, t = make_state(revoked_at="2026-09-02T18:00:00.1234568Z")
    expect(e.evaluate(s, request(s, t, at="2026-09-02T18:00:00.1234567Z"))["authorized"], "pre-revocation false reject")
    count += 1
    s, t = make_state(valid_from="2026-09-02T18:00:00.1234567Z")
    expect(e.evaluate(s, request(s, t, at="2026-09-02T18:00:00.123456700Z"))["authorized"], "equal valid_from rejected")
    count += 1
    s, t = make_state(valid_until="2026-09-02T18:00:00.1234567Z")
    expect(e.evaluate(s, request(s, t, at="2026-09-02T18:00:00.123456700Z"))["authorized"], "equal valid_until rejected")
    count += 1
    s, t = make_state(revoked_at="2026-09-02T18:00:00.1234567Z")
    expect(not e.evaluate(s, request(s, t, at="2026-09-02T18:00:00.123456700Z"))["authorized"], "equal revocation permitted")
    count += 1
    return count


def test_dual_identity() -> int:
    count = 0
    s, t = make_state()
    r = request(s, t)
    receipt = e.evaluate(s, r)
    expect(receipt["authorized"], "baseline not authorized")
    expect(receipt["claimed_authority_state_id"] == s["authority_state_id"], "claimed valid identity lost")
    expect(receipt["recomputed_authority_state_id"] == s["authority_state_id"], "computed valid identity wrong")
    count += 1

    forged = deepcopy(s)
    forged["authority_state_id"] = "sha256:" + "1" * 64
    rr = request(forged, t)
    denied = e.evaluate(forged, rr)
    expect(not denied["authorized"], "forged state permitted")
    expect(denied["claimed_authority_state_id"] == forged["authority_state_id"], "forged claim not preserved")
    expect(denied["recomputed_authority_state_id"] == s["authority_state_id"], "computed identity not independently retained")
    expect(denied["claimed_authority_state_id"] != denied["recomputed_authority_state_id"], "dual identity collapsed")
    count += 1

    malformed = deepcopy(s)
    malformed["authority_state_id"] = "not-a-sha"
    denied = e.evaluate(malformed, r)
    expect(denied["claimed_authority_state_id"] is None, "malformed claim reported as valid")
    expect(denied["recomputed_authority_state_id"] == s["authority_state_id"], "computed identity lost for malformed claim")
    count += 1

    structural = deepcopy(s)
    structural["future_field"] = True
    denied = e.evaluate(structural, r)
    expect(not denied["authorized"], "structurally invalid state permitted")
    expect(denied["recomputed_authority_state_id"] is not None, "computed identity lost on canonicalizable structural invalidity")
    count += 1

    base_receipt = deepcopy(receipt)
    base_receipt["receipt_id"] = None
    base_receipt["diagnostics"] = []
    a = deepcopy(base_receipt)
    b = deepcopy(base_receipt)
    a["claimed_authority_state_id"] = "sha256:" + "2" * 64
    b["claimed_authority_state_id"] = "sha256:" + "3" * 64
    e._finalize_receipt(a)
    e._finalize_receipt(b)
    expect(a["receipt_id"] != b["receipt_id"], "claimed identity absent from receipt identity")
    c = deepcopy(base_receipt)
    d = deepcopy(base_receipt)
    c["recomputed_authority_state_id"] = "sha256:" + "4" * 64
    d["recomputed_authority_state_id"] = "sha256:" + "5" * 64
    e._finalize_receipt(c)
    e._finalize_receipt(d)
    expect(c["receipt_id"] != d["receipt_id"], "computed identity absent from receipt identity")
    count += 2
    return count


def test_authority_boundaries() -> int:
    count = 0
    s, t = make_state()
    expect(e.evaluate(s, request(s, t))["authorized"], "positive policy failed")
    count += 1
    for label, kwargs in [
        ("subject", {"subject": "actor:other"}),
        ("domain", {"domain": "other"}),
        ("operation", {"operation": "other"}),
        ("scope", {"scope": "other"}),
        ("target_class", {"target_class": "other"}),
    ]:
        expect(not e.evaluate(s, request(s, t, **kwargs))["authorized"], f"{label} substitution permitted")
        count += 1
    other = target("target:other", "O")
    expect(not e.evaluate(s, request(s, t, target_ref=other["identity_sha256"], references=[other]))["authorized"], "target substitution permitted")
    count += 1

    delegated, dt = make_state(subject="actor:owner", delegates=("actor:delegate",))
    expect(e.evaluate(delegated, request(delegated, dt))["authorized"], "valid delegation rejected")
    count += 1
    for label, mutator in [
        ("parent", lambda x: x["records"][1].__setitem__("parent_id", "missing")),
        ("delegated_by", lambda x: x["records"][1].__setitem__("delegated_by", "actor:other")),
        ("bounds", lambda x: x["records"][1].__setitem__("scope", "other")),
        ("duplicate_id", lambda x: x["records"][1].__setitem__("id", "auth:root")),
        ("nondelegation", lambda x: x["records"][1].__setitem__("basis_type", "policy")),
    ]:
        bad = deepcopy(delegated)
        mutator(bad)
        bad = seal(bad)
        expect(not e.evaluate(bad, request(bad, dt))["authorized"], f"delegation defect permitted: {label}")
        count += 1

    surplus = deepcopy(s)
    extra = deepcopy(surplus["records"][0])
    extra["id"] = "auth:peer"
    extra["subject_id"] = "actor:other"
    surplus["records"].append(extra)
    surplus = seal(surplus)
    expect(not e.evaluate(surplus, request(surplus, t))["authorized"], "surplus peer permitted")
    count += 1
    return count


def test_request_integrity_and_support() -> int:
    count = 0
    s, t = make_state()
    support_ref = target("decision:1", "D")
    support = [{"id": "support:D", "artifact_type": "contract_d_candidate", "ref_id": "D"}]
    r = request(s, t, references=[t, support_ref], support=support)
    expect(e.evaluate(s, r)["authorized"], "nonconferring support blocked valid authority")
    count += 1

    invalid_state = {"schema": e.STATE_SCHEMA, "authority_state_id": "sha256:" + "0" * 64, "records": []}
    expect(not e.evaluate(invalid_state, r)["authorized"], "support conferred authority")
    count += 1

    bad = request(s, t)
    bad["references"][0]["immutable_id"] = "tampered"
    expect(not e.evaluate(s, bad)["authorized"], "bad reference identity permitted")
    count += 1
    bad = request(s, t)
    bad["references"].append(deepcopy(bad["references"][0]))
    expect(not e.evaluate(s, bad)["authorized"], "duplicate ref_id permitted")
    count += 1
    bad = request(s, t, references=[t, support_ref], support=support)
    bad["supporting_artifacts"].append(deepcopy(bad["supporting_artifacts"][0]))
    expect(not e.evaluate(s, bad)["authorized"], "duplicate support ID permitted")
    count += 1
    bad = request(s, t, references=[t], support=support)
    expect(not e.evaluate(s, bad)["authorized"], "unknown support ref permitted")
    count += 1
    bad = request(s, t)
    bad["future_field"] = True
    expect(not e.evaluate(s, bad)["authorized"], "unknown request field permitted")
    count += 1
    return count


def test_blockers() -> int:
    count = 0
    s, t = make_state()
    for key, item in [
        ("conflicts", {"id": "c", "relevant": True, "status": "unresolved"}),
        ("residues", {"id": "r", "relevant": True, "status": "contested"}),
    ]:
        kwargs = {key: [item]}
        expect(not e.evaluate(s, request(s, t, **kwargs))["authorized"], f"relevant {key} did not block")
        count += 1
    expect(e.evaluate(s, request(s, t, conflicts=[{"id": "c", "relevant": False, "status": "unresolved"}]))["authorized"], "irrelevant conflict blocked")
    count += 1

    conflict_ref = target("conflict:42", "C")
    rs, _ = make_state(domain="resolution", operation="resolve", scope="case:42", target_class="test_target", ref=conflict_ref)
    blocked = request(rs, conflict_ref, conflicts=[{"id": "c42", "relevant": True, "status": "unresolved"}])
    expect(not e.evaluate(rs, blocked)["authorized"], "resolution request bypassed supplied blocker")
    count += 1
    clear = request(rs, conflict_ref)
    expect(e.evaluate(rs, clear)["authorized"], "clear exact resolution request rejected")
    count += 1

    dup = request(s, t, conflicts=[{"id": "x", "relevant": True, "status": "unresolved"}, {"id": "x", "relevant": True, "status": "contested"}])
    expect(not e.evaluate(s, dup)["authorized"], "duplicate blocker ID permitted")
    count += 1
    return count


def test_preservation() -> int:
    count = 0
    s, t = make_state()
    r = request(s, t)
    r["future_field"] = True
    out = e.evaluate(s, r)
    expect(out["preserved"]["references"] == r["references"], "schema-valid refs lost on malformed request")
    expect(out["preserved"]["supporting_artifacts"] == [], "support preservation wrong")
    count += 2

    malformed = request(s, t)
    malformed["references"][0]["surprise"] = True
    out = e.evaluate(s, malformed)
    expect(out["preserved"]["references"] == [], "malformed reference emitted into receipt")
    count += 1

    shaped_duplicate = request(s, t)
    shaped_duplicate["references"].append(deepcopy(shaped_duplicate["references"][0]))
    out = e.evaluate(s, shaped_duplicate)
    expect(out["preserved"]["references"] == shaped_duplicate["references"], "individually shaped duplicate observations not preserved")
    count += 1

    bad_support = request(s, t)
    bad_support["supporting_artifacts"] = [{"id": "x", "artifact_type": "a"}]
    out = e.evaluate(s, bad_support)
    expect(out["preserved"]["supporting_artifacts"] == [], "malformed support emitted into receipt")
    count += 1
    return count


def main() -> None:
    groups = {
        "JCS_REGRESSIONS": test_canonicalization(),
        "EXACT_TIME_PRIMITIVES": test_exact_time(),
        "FRACTIONAL_CURRENTNESS": test_fractional_currentness(),
        "DUAL_STATE_IDENTITY": test_dual_identity(),
        "AUTHORITY_BOUNDARIES": test_authority_boundaries(),
        "REQUEST_AND_SUPPORT": test_request_integrity_and_support(),
        "BLOCKERS": test_blockers(),
        "SAFE_PRESERVATION": test_preservation(),
    }
    total = sum(groups.values())
    print("CONTRACT_E_V1_RC3_CANDIDATE_TESTS_PASS")
    for key, value in groups.items():
        print(f"{key}={value}")
    print(f"TOTAL_ASSERTED_CONTROLS={total}")


if __name__ == "__main__":
    main()
