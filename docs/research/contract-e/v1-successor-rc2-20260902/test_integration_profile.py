from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CANDIDATE = ROOT / "candidate"
for path in (ROOT, CANDIDATE):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import integration_profile as profile
import reference as e

COUNT = 0
FAMILIES: dict[str, int] = {}


def check(case_id: str, family: str, condition: bool, detail=""):
    global COUNT
    if not condition:
        raise AssertionError(f"{case_id}: {detail}")
    COUNT += 1
    FAMILIES[family] = FAMILIES.get(family, 0) + 1


def expect_error(case_id: str, family: str, code: str, fn):
    try:
        fn()
    except profile.ProfileError as exc:
        check(case_id, family, str(exc).startswith(code), str(exc))
    else:
        raise AssertionError(f"{case_id}: expected {code}")


def seal_state(state):
    state = deepcopy(state)
    state["authority_state_id"] = e.authority_state_identity(state)
    return state


def make_state(*, subject, domain, operation, scope, target_class, target_ref, valid_from="2026-09-02T16:00:00Z", valid_until="2026-09-02T20:00:00Z", revoked_at=None):
    return seal_state(
        {
            "schema": e.STATE_SCHEMA,
            "authority_state_id": "sha256:" + "0" * 64,
            "records": [
                {
                    "id": "authority-root",
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
                }
            ],
        }
    )


def expectation_for(decision, consume_mod, core, **overrides):
    effect = core.validate_effect(decision["effect"]) if "effect" in decision else None
    values = {
        "input_authority": deepcopy(decision["input_authority"]),
        "policy": deepcopy(decision["policy"]),
        "target": deepcopy(decision["target"]),
        "requested_operation": effect["type"] if effect else "knowledge.cite_as_evidence",
        "effect_params": deepcopy(effect["params"]) if effect else {},
    }
    values.update(overrides)
    return consume_mod.ApplicabilityExpectation(**values)


def make_intent(decision_identity):
    return {
        "schema": "execution-intent-candidate-v1",
        "executable_sha256": "sha256:" + "a" * 64,
        "entry_point": "dispatch_exact_task",
        "arguments": ["--mode", "exact", "--once"],
        "input_identities": [decision_identity, "sha256:" + "b" * 64],
        "environment_constraints": {
            "network": "disabled",
            "workspace": "ephemeral",
            "max_seconds": 30,
        },
        "side_effect_targets": ["task:fixture"],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract-d-root", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()

    d_root = Path(args.contract_d_root).resolve()
    sys.path.insert(0, str(d_root))
    from validators import contract_d_core as core
    from validators import contract_d_consume as consume_mod

    fixtures = json.loads((d_root / "fixtures/contract-d/1.0.0/valid.json").read_text())["fixtures"]
    source_clear = deepcopy(fixtures["source-audit-clear.json"])
    citation_clear = deepcopy(fixtures["citation-use-clear.json"])
    task_clear = deepcopy(fixtures["task-dispatch-clear.json"])
    hold = deepcopy(fixtures["completed-hold.json"])
    failed = deepcopy(fixtures["evaluation-failed.json"])

    source_expected = expectation_for(source_clear, consume_mod, core)
    citation_expected = expectation_for(citation_clear, consume_mod, core)
    task_expected = expectation_for(task_clear, consume_mod, core)
    hold_expected = expectation_for(hold, consume_mod, core)
    failed_expected = expectation_for(failed, consume_mod, core)

    # Contract D boundary, including exact operation/params and state distinctions.
    check("D-01", "contract-d", consume_mod.consume(source_clear, source_expected)["outcome"] == "candidate_for_authorization")
    check("D-02", "contract-d", consume_mod.consume(citation_clear, citation_expected)["outcome"] == "candidate_for_authorization")
    check("D-03", "contract-d", consume_mod.consume(task_clear, task_expected)["outcome"] == "candidate_for_authorization")
    check("D-04", "contract-d", consume_mod.consume(hold, hold_expected)["outcome"] == "hold")
    check("D-05", "contract-d", consume_mod.consume(failed, failed_expected)["outcome"] == "evaluation_failed")

    expected_mutations = []
    for field in ("kind", "id", "immutable_id"):
        changed = deepcopy(source_clear["input_authority"])
        changed[field] += ":other"
        expected_mutations.append((f"input-{field}", {"input_authority": changed}))
    for field in ("id", "version"):
        changed = deepcopy(source_clear["policy"])
        changed[field] += ":other"
        expected_mutations.append((f"policy-{field}", {"policy": changed}))
    for field in ("kind", "id"):
        changed = deepcopy(source_clear["target"])
        changed[field] += ":other"
        expected_mutations.append((f"target-{field}", {"target": changed}))
    changed = deepcopy(source_clear["target"])
    changed["content_sha256"] = "sha256:" + "9" * 64
    expected_mutations.append(("target-content", {"target": changed}))
    expected_mutations.append(("operation", {"requested_operation": "knowledge.cite_as_evidence"}))
    expected_mutations.append(("param-value", {"effect_params": {"scope": "object"}}))

    for index, (name, override) in enumerate(expected_mutations):
        expected = expectation_for(source_clear, consume_mod, core, **override)
        check(f"D-M-{index:02d}", "contract-d-mutation", consume_mod.consume(source_clear, expected)["outcome"] == "not_applicable", name)

    # Pairwise mismatch combinations must still fail applicability.
    pair_index = 0
    for left in range(len(expected_mutations)):
        for right in range(left + 1, len(expected_mutations)):
            if pair_index >= 24:
                break
            merged = {}
            merged.update(expected_mutations[left][1])
            merged.update(expected_mutations[right][1])
            expected = expectation_for(source_clear, consume_mod, core, **merged)
            check(f"D-P-{pair_index:02d}", "contract-d-pairwise", consume_mod.consume(source_clear, expected)["outcome"] == "not_applicable")
            pair_index += 1
        if pair_index >= 24:
            break

    # Metadata is non-authoritative under Contract D semantic identity.
    meta = deepcopy(source_clear)
    meta["metadata"] = {"explanation": "different presentation", "diagnostics": {"trace": [1, 2, 3]}}
    check("D-META", "metamorphic", core.semantic_identity(meta) == core.semantic_identity(source_clear))

    # Human baseline.
    human_subject = "human:operator-1"
    human_decision_id = core.semantic_identity(source_clear)
    human_target = profile.immutable_ref(
        "TARGET",
        "contract-d-target",
        "1",
        e.sha256_identity(source_clear["target"]),
    )
    human_j = {
        "domain": "knowledge",
        "operation": source_expected.requested_operation,
        "scope": "claim",
        "target_class": "contract-d-target",
        "target_ref": human_target["identity_sha256"],
    }
    human_state = make_state(
        subject=human_subject,
        domain=human_j["domain"],
        operation=human_j["operation"],
        scope=human_j["scope"],
        target_class=human_j["target_class"],
        target_ref=human_j["target_ref"],
    )
    human_trusted = profile.TrustedBindings(human_decision_id, e.authority_state_identity(human_state))
    human_kwargs = dict(
        decision=source_clear,
        expected=source_expected,
        trusted=human_trusted,
        contract_d_root=str(d_root),
        authority_state=human_state,
        subject_id=human_subject,
        evaluation_time="2026-09-02T18:00:00Z",
        jurisdiction=human_j,
        target_reference=human_target,
    )
    handoff = profile.human_handoff(**human_kwargs)
    check("H-BASE", "human", handoff["handoff_created"] is True)
    check("H-NONCONF", "human", handoff["authority_conferring"] is False)

    # Exact actor/jurisdiction mutations. Operation mismatch is stopped before E; others fail E.
    for index, (field, value) in enumerate(
        [
            ("subject", "human:other"),
            ("domain", "other-domain"),
            ("scope", "other-scope"),
            ("target_class", "other-class"),
        ]
    ):
        kwargs = deepcopy(human_kwargs)
        if field == "subject":
            kwargs["subject_id"] = value
            result = profile.human_handoff(**kwargs)
            check(f"H-B-{index}", "human-binding", result["handoff_created"] is False)
        else:
            kwargs["jurisdiction"][field] = value
            result = profile.human_handoff(**kwargs)
            check(f"H-B-{index}", "human-binding", result["handoff_created"] is False)

    wrong_op = deepcopy(human_kwargs)
    wrong_op["jurisdiction"]["operation"] = "task.dispatch"
    expect_error("H-OP", "human-binding", "decision_operation_authorization_mismatch", lambda: profile.human_handoff(**wrong_op))

    wrong_target_ref = deepcopy(human_kwargs)
    other_target = profile.immutable_ref("TARGET", "contract-d-target", "1", "other-target")
    wrong_target_ref["target_reference"] = other_target
    wrong_target_ref["jurisdiction"]["target_ref"] = other_target["identity_sha256"]
    result = profile.human_handoff(**wrong_target_ref)
    check("H-TARGET", "human-binding", result["handoff_created"] is False)

    # Blocker behavior through the profile.
    blocked = dict(human_kwargs)
    blocked["conflicts"] = [{"id": "c", "relevant": True, "status": "unresolved"}]
    check("H-CONFLICT", "blocker", profile.human_handoff(**blocked)["handoff_created"] is False)
    blocked = dict(human_kwargs)
    blocked["residues"] = [{"id": "r", "relevant": True, "status": "contested"}]
    check("H-RESIDUE", "blocker", profile.human_handoff(**blocked)["handoff_created"] is False)
    irrelevant = dict(human_kwargs)
    irrelevant["conflicts"] = [{"id": "c", "relevant": False, "status": "unresolved"}]
    check("H-IRRELEVANT", "blocker", profile.human_handoff(**irrelevant)["handoff_created"] is True)

    # Trusted Decision identity defeats valid-but-different Decision forgery.
    forged_decision = deepcopy(hold)
    forged_decision["evaluation"] = {"state": "completed", "disposition": "clear"}
    forged_expected = expectation_for(forged_decision, consume_mod, core)
    check("AUTH-D-PRE", "authenticity", consume_mod.consume(forged_decision, forged_expected)["outcome"] == "candidate_for_authorization")
    forged_kwargs = deepcopy(human_kwargs)
    forged_kwargs["decision"] = forged_decision
    forged_kwargs["expected"] = forged_expected
    expect_error("AUTH-D", "authenticity", "untrusted_decision_identity", lambda: profile.human_handoff(**forged_kwargs))

    # Valid but fabricated root is locally authorizing but rejected by external trusted binding.
    fabricated_state = deepcopy(human_state)
    fabricated_state["records"][0]["id"] = "fabricated-root"
    fabricated_state["authority_state_id"] = e.authority_state_identity(fabricated_state)
    direct_request = e.evaluate(
        fabricated_state,
        profile.build_authorization_request(
            authority_state=fabricated_state,
            decision_identity=human_decision_id,
            subject_id=human_subject,
            evaluation_time="2026-09-02T18:00:00Z",
            jurisdiction=human_j,
            target_reference=human_target,
        ),
    )
    check("AUTH-ROOT-PRE", "authenticity", direct_request["authorized"] is True)
    fabricated_kwargs = deepcopy(human_kwargs)
    fabricated_kwargs["authority_state"] = fabricated_state
    expect_error("AUTH-ROOT", "authenticity", "untrusted_authority_state_identity", lambda: profile.human_handoff(**fabricated_kwargs))

    # AuthorityState mutations are rejected with old trust, and fail E semantics when explicitly re-trusted.
    state_mutations = [
        ("domain", "other-domain"),
        ("operation", "other-operation"),
        ("scope", "other-scope"),
        ("target_class", "other-class"),
        ("target_ref", profile.immutable_ref("X", "x", None, "other")["identity_sha256"]),
    ]
    for index, (field, value) in enumerate(state_mutations):
        changed = deepcopy(human_state)
        changed["records"][0][field] = value
        changed["authority_state_id"] = e.authority_state_identity(changed)
        old_trust = deepcopy(human_kwargs)
        old_trust["authority_state"] = changed
        expect_error(f"STATE-TRUST-{index}", "trusted-state", "untrusted_authority_state_identity", lambda k=old_trust: profile.human_handoff(**k))
        new_trust = deepcopy(human_kwargs)
        new_trust["authority_state"] = changed
        new_trust["trusted"] = profile.TrustedBindings(human_decision_id, e.authority_state_identity(changed))
        if field == "operation":
            # D operation remains exact, so the E state cannot silently widen it.
            check(f"STATE-E-{index}", "trusted-state", profile.human_handoff(**new_trust)["handoff_created"] is False)
        else:
            check(f"STATE-E-{index}", "trusted-state", profile.human_handoff(**new_trust)["handoff_created"] is False)

    # Currentness/revocation with exact newly trusted current state.
    currentness = [
        ("future", {"valid_from": "2026-09-02T19:00:00Z", "valid_until": None, "revoked_at": None}, False),
        ("stale", {"valid_from": "2026-09-02T16:00:00Z", "valid_until": "2026-09-02T17:00:00Z", "revoked_at": None}, False),
        ("revoked", {"valid_from": "2026-09-02T16:00:00Z", "valid_until": "2026-09-02T20:00:00Z", "revoked_at": "2026-09-02T18:00:00Z"}, False),
        ("from-edge", {"valid_from": "2026-09-02T18:00:00Z", "valid_until": "2026-09-02T20:00:00Z", "revoked_at": None}, True),
        ("until-edge", {"valid_from": "2026-09-02T16:00:00Z", "valid_until": "2026-09-02T18:00:00Z", "revoked_at": None}, True),
    ]
    for index, (name, times, expected_allow) in enumerate(currentness):
        changed = make_state(
            subject=human_subject,
            domain=human_j["domain"],
            operation=human_j["operation"],
            scope=human_j["scope"],
            target_class=human_j["target_class"],
            target_ref=human_j["target_ref"],
            **times,
        )
        kwargs = deepcopy(human_kwargs)
        kwargs["authority_state"] = changed
        kwargs["trusted"] = profile.TrustedBindings(human_decision_id, e.authority_state_identity(changed))
        check(f"TIME-{index}-{name}", "currentness", profile.human_handoff(**kwargs)["handoff_created"] is expected_allow)

    # Machine baseline uses the exact D operation, while target is the immutable ExecutionIntent.
    machine_subject = "machine:runner-1"
    task_decision_id = core.semantic_identity(task_clear)
    intent = make_intent(task_decision_id)
    intent_id = profile.execution_intent_identity(intent)
    intent_ref = profile.immutable_ref("TARGET", "execution_intent", "1", intent_id)
    machine_j = {
        "domain": "task",
        "operation": task_expected.requested_operation,
        "scope": "single-intent",
        "target_class": "execution_intent",
        "target_ref": intent_ref["identity_sha256"],
    }
    machine_state = make_state(
        subject=machine_subject,
        domain=machine_j["domain"],
        operation=machine_j["operation"],
        scope=machine_j["scope"],
        target_class=machine_j["target_class"],
        target_ref=machine_j["target_ref"],
    )
    machine_trusted = profile.TrustedBindings(task_decision_id, e.authority_state_identity(machine_state))
    machine_kwargs = dict(
        execution_intent=intent,
        decision=task_clear,
        expected=task_expected,
        trusted=machine_trusted,
        contract_d_root=str(d_root),
        authority_state=machine_state,
        subject_id=machine_subject,
        evaluation_time="2026-09-02T18:00:00Z",
        jurisdiction=machine_j,
        target_reference=intent_ref,
    )
    gate = profile.machine_gate(**machine_kwargs)
    check("M-BASE", "machine", gate["execution_permitted"] is True)
    check("M-NO-OCCURRENCE", "machine", gate["execution_occurred"] is False)

    # Generic execute cannot be substituted for exact task.dispatch.
    execute_kwargs = deepcopy(machine_kwargs)
    execute_kwargs["jurisdiction"]["operation"] = "execute"
    expect_error("M-NO-INFLATION", "machine", "decision_operation_authorization_mismatch", lambda: profile.machine_gate(**execute_kwargs))

    # Material intent mutations all change identity and cannot use old authorization target.
    intent_mutators = []
    for field, value in [
        ("executable_sha256", "sha256:" + "c" * 64),
        ("entry_point", "other_entry"),
    ]:
        intent_mutators.append((field, lambda x, f=field, v=value: x.__setitem__(f, v)))
    intent_mutators.extend(
        [
            ("arguments-add", lambda x: x["arguments"].append("--other")),
            ("arguments-reorder", lambda x: x.__setitem__("arguments", list(reversed(x["arguments"])))),
            ("inputs-add", lambda x: x["input_identities"].append("sha256:" + "d" * 64)),
            ("inputs-change", lambda x: x["input_identities"].__setitem__(0, "decision:sha256:" + "e" * 64)),
            ("env-network", lambda x: x["environment_constraints"].__setitem__("network", "enabled")),
            ("env-time", lambda x: x["environment_constraints"].__setitem__("max_seconds", 31)),
            ("side-effect-add", lambda x: x["side_effect_targets"].append("task:other")),
            ("side-effect-change", lambda x: x["side_effect_targets"].__setitem__(0, "task:other")),
        ]
    )
    for index, (name, mutate) in enumerate(intent_mutators):
        changed = deepcopy(intent)
        mutate(changed)
        changed_id = profile.execution_intent_identity(changed)
        check(f"INTENT-ID-{index}", "execution-intent", changed_id != intent_id, name)
        kwargs = deepcopy(machine_kwargs)
        kwargs["execution_intent"] = changed
        result = profile.machine_gate(**kwargs)
        check(f"INTENT-GATE-{index}", "execution-intent", result["execution_permitted"] is False, name)

    # Cross-subject and cross-track replay fail.
    wrong_machine_subject = deepcopy(machine_kwargs)
    wrong_machine_subject["subject_id"] = human_subject
    check("TRACK-SUBJECT", "cross-track", profile.machine_gate(**wrong_machine_subject)["execution_permitted"] is False)

    human_receipt = handoff["authorization"]["receipt"]
    machine_with_human_receipt = deepcopy(machine_kwargs)
    machine_with_human_receipt["prior_receipts"] = [human_receipt]
    check("TRACK-RECEIPT", "cross-track", profile.machine_gate(**machine_with_human_receipt)["execution_permitted"] is True)
    # The prior human receipt is preserved only as non-conferring support; removing current machine authority still denies.
    revoked_machine = deepcopy(machine_state)
    revoked_machine["records"][0]["revoked_at"] = "2026-09-02T18:00:00Z"
    revoked_machine["authority_state_id"] = e.authority_state_identity(revoked_machine)
    stale_kwargs = deepcopy(machine_with_human_receipt)
    stale_kwargs["authority_state"] = revoked_machine
    stale_kwargs["trusted"] = profile.TrustedBindings(task_decision_id, e.authority_state_identity(revoked_machine))
    check("TRACK-REVOKED", "cross-track", profile.machine_gate(**stale_kwargs)["execution_permitted"] is False)

    # Forge an authorization receipt into authorized=true with a valid self-hash. Fresh E still controls.
    denied = deepcopy(human_receipt)
    denied["authorized"] = False
    denied["authority_basis_id"] = None
    denied["receipt_id"] = e.sha256_identity(e._receipt_projection(denied))
    forged_receipt = deepcopy(denied)
    forged_receipt["authorized"] = True
    forged_receipt["authority_basis_id"] = "forged-basis"
    forged_receipt["receipt_id"] = e.sha256_identity(e._receipt_projection(forged_receipt))
    check("RECEIPT-FORGE-HASH", "authenticity", forged_receipt["receipt_id"] == e.sha256_identity(e._receipt_projection(forged_receipt)))

    fresh_blocked = deepcopy(human_kwargs)
    fresh_blocked["prior_receipts"] = [forged_receipt]
    fresh_blocked["conflicts"] = [{"id": "fresh", "relevant": True, "status": "unresolved"}]
    check("RECEIPT-FORGE-FRESH", "authenticity", profile.human_handoff(**fresh_blocked)["handoff_created"] is False)

    # Old receipt before revocation is historical evidence only.
    old_receipt = handoff["authorization"]["receipt"]
    revoked_human = deepcopy(human_state)
    revoked_human["records"][0]["revoked_at"] = "2026-09-02T18:00:00Z"
    revoked_human["authority_state_id"] = e.authority_state_identity(revoked_human)
    revoked_kwargs = deepcopy(human_kwargs)
    revoked_kwargs["authority_state"] = revoked_human
    revoked_kwargs["trusted"] = profile.TrustedBindings(human_decision_id, e.authority_state_identity(revoked_human))
    revoked_kwargs["prior_receipts"] = [old_receipt]
    check("TOCTOU-REVOCATION", "point-of-use", profile.human_handoff(**revoked_kwargs)["handoff_created"] is False)

    # If trusted binding is not updated when state changes, fail even earlier.
    stale_trust = deepcopy(human_kwargs)
    stale_trust["authority_state"] = revoked_human
    expect_error("TOCTOU-TRUST", "point-of-use", "untrusted_authority_state_identity", lambda: profile.human_handoff(**stale_trust))

    # D metadata mutation with same semantic identity remains acceptable under same trust.
    meta_kwargs = deepcopy(human_kwargs)
    meta_kwargs["decision"] = meta
    meta_kwargs["expected"] = expectation_for(meta, consume_mod, core)
    check("META-HANDOFF", "metamorphic", profile.human_handoff(**meta_kwargs)["handoff_created"] is True)

    # Decision semantic mutations all fail old trusted identity even if structurally valid.
    valid_decision_mutations = []
    changed = deepcopy(source_clear); changed["target"]["id"] += ":other"; valid_decision_mutations.append(changed)
    changed = deepcopy(source_clear); changed["target"]["content_sha256"] = "sha256:" + "8" * 64; valid_decision_mutations.append(changed)
    changed = deepcopy(source_clear); changed["policy"]["id"] += ":other"; valid_decision_mutations.append(changed)
    changed = deepcopy(source_clear); changed["policy"]["version"] += ":other"; valid_decision_mutations.append(changed)
    changed = deepcopy(source_clear); changed["input_authority"]["id"] += ":other"; valid_decision_mutations.append(changed)
    changed = deepcopy(source_clear); changed["input_authority"]["immutable_id"] += ":other"; valid_decision_mutations.append(changed)
    changed = deepcopy(source_clear); changed["evaluation"]["disposition"] = "hold"; valid_decision_mutations.append(changed)
    for index, changed in enumerate(valid_decision_mutations):
        expected = expectation_for(changed, consume_mod, core)
        kwargs = deepcopy(human_kwargs)
        kwargs["decision"] = changed
        kwargs["expected"] = expected
        expect_error(f"DEC-TRUST-{index}", "trusted-decision", "untrusted_decision_identity", lambda k=kwargs: profile.human_handoff(**k))

    # Supporting artifacts cannot manufacture root trust in Contract E core.
    invalid_state = {"schema": e.STATE_SCHEMA, "authority_state_id": "sha256:" + "6" * 64, "records": []}
    req = profile.build_authorization_request(
        authority_state=invalid_state,
        decision_identity=human_decision_id,
        subject_id=human_subject,
        evaluation_time="2026-09-02T18:00:00Z",
        jurisdiction=human_j,
        target_reference=human_target,
        prior_receipts=[forged_receipt],
    )
    check("SUPPORT-NONCONFERRING", "authenticity", e.evaluate(invalid_state, req)["authorized"] is False)

    # Identity facts are explicit on the formerly ambiguous invalid-state case.
    mismatch_state = deepcopy(human_state)
    real_state_id = mismatch_state["authority_state_id"]
    mismatch_state["authority_state_id"] = "sha256:" + "7" * 64
    mismatch_req = profile.build_authorization_request(
        authority_state=mismatch_state,
        decision_identity=human_decision_id,
        subject_id=human_subject,
        evaluation_time="2026-09-02T18:00:00Z",
        jurisdiction=human_j,
        target_reference=human_target,
    )
    mismatch_receipt = e.evaluate(mismatch_state, mismatch_req)
    check("RC1-AMB-CLAIMED", "rc1-successor", mismatch_receipt["claimed_authority_state_id"] == "sha256:" + "7" * 64)
    check("RC1-AMB-RECOMPUTED", "rc1-successor", mismatch_receipt["recomputed_authority_state_id"] == real_state_id)
    check("RC1-AMB-DENY", "rc1-successor", mismatch_receipt["authorized"] is False)

    # Ensure pressure surface exceeds prior 101 cases while covering the same families.
    check("MATRIX-SIZE", "apparatus", COUNT >= 120, f"count before sentinel={COUNT}")

    result = {
        "status": "PASS",
        "case_count": COUNT,
        "families": dict(sorted(FAMILIES.items())),
        "trusted_decision_binding": True,
        "trusted_authority_state_binding": True,
        "fresh_point_of_use_evaluation": True,
        "execution_intent_binding": True,
        "generic_execute_inflation_rejected": True,
        "forged_receipt_nonconferring": True,
        "rc1_dual_identity_ambiguity_resolved_in_reference": True,
    }
    text = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
