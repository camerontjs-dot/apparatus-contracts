from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from copy import deepcopy
from pathlib import Path


def load(path: str, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", required=True)
    parser.add_argument("--reference", required=True)
    parser.add_argument("--contract-d-root", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    profile = load(args.profile, "frozen_integration_profile")
    ref = load(args.reference, "frozen_e_reference")
    droot = str(Path(args.contract_d_root).resolve())
    sys.path.insert(0, droot)
    from validators import contract_d_core as core
    from validators import contract_d_consume as consume_mod

    fixtures = json.loads((Path(droot) / "fixtures/contract-d/1.0.0/valid.json").read_text())["fixtures"]
    clear = deepcopy(fixtures["source-audit-clear.json"])
    hold = deepcopy(fixtures["completed-hold.json"])

    def expected(decision):
        effect = core.validate_effect(decision["effect"])
        return consume_mod.ApplicabilityExpectation(
            input_authority=deepcopy(decision["input_authority"]),
            policy=deepcopy(decision["policy"]),
            target=deepcopy(decision["target"]),
            requested_operation=effect["type"],
            effect_params=deepcopy(effect["params"]),
        )

    exp = expected(clear)
    decision_id = core.semantic_identity(clear)
    target = profile.immutable_ref("TARGET", "contract-d-target", "1", ref.sha256_identity(clear["target"]))
    jurisdiction = {
        "domain": "knowledge",
        "operation": exp.requested_operation,
        "scope": "claim",
        "target_class": "contract-d-target",
        "target_ref": target["identity_sha256"],
    }

    def make_state(subject="human:1", revoked_at=None):
        state = {
            "schema": ref.STATE_SCHEMA,
            "authority_state_id": "",
            "records": [{
                "id": "root",
                "basis_type": "grant",
                "subject_id": subject,
                "domain": jurisdiction["domain"],
                "operation": jurisdiction["operation"],
                "scope": jurisdiction["scope"],
                "target_class": jurisdiction["target_class"],
                "target_ref": jurisdiction["target_ref"],
                "valid_from": "2026-01-01T00:00:00Z",
                "valid_until": "2027-01-01T00:00:00Z",
                "revoked_at": revoked_at,
                "parent_id": None,
                "delegated_by": None,
            }],
        }
        state["authority_state_id"] = ref.authority_state_identity(state)
        return state

    state = make_state()
    trusted = profile.TrustedBindings(decision_id, ref.authority_state_identity(state))
    kwargs = dict(
        decision=clear,
        expected=exp,
        trusted=trusted,
        contract_d_root=droot,
        authority_state=state,
        subject_id="human:1",
        evaluation_time="2026-09-02T18:00:00Z",
        jurisdiction=jurisdiction,
        target_reference=target,
    )
    baseline = profile.human_handoff(**kwargs)
    assert baseline["handoff_created"] is True

    controls = {}

    # Weak: any structurally valid Decision is treated as trusted.
    forged = deepcopy(hold)
    forged["evaluation"] = {"state": "completed", "disposition": "clear"}
    forged_exp = expected(forged)
    precondition = consume_mod.consume(forged, forged_exp)["outcome"] == "candidate_for_authorization"
    forged_kwargs = deepcopy(kwargs); forged_kwargs["decision"] = forged; forged_kwargs["expected"] = forged_exp
    try:
        profile.human_handoff(**forged_kwargs)
    except profile.ProfileError as exc:
        correct_reject = str(exc).startswith("untrusted_decision_identity")
    else:
        correct_reject = False
    controls["decision_structural_validity_implies_trust"] = precondition and correct_reject

    # Weak: a self-consistent AuthorityState hash is treated as root legitimacy.
    fabricated = deepcopy(state)
    fabricated["records"][0]["id"] = "fabricated-root"
    fabricated["authority_state_id"] = ref.authority_state_identity(fabricated)
    direct_req = profile.build_authorization_request(
        authority_state=fabricated,
        decision_identity=decision_id,
        subject_id="human:1",
        evaluation_time="2026-09-02T18:00:00Z",
        jurisdiction=jurisdiction,
        target_reference=target,
    )
    precondition = ref.evaluate(fabricated, direct_req)["authorized"] is True
    fabricated_kwargs = deepcopy(kwargs); fabricated_kwargs["authority_state"] = fabricated
    try:
        profile.human_handoff(**fabricated_kwargs)
    except profile.ProfileError as exc:
        correct_reject = str(exc).startswith("untrusted_authority_state_identity")
    else:
        correct_reject = False
    controls["authority_state_self_hash_implies_root_trust"] = precondition and correct_reject

    # Weak: receipt hash / authorized boolean is treated as current permission.
    receipt = deepcopy(baseline["authorization"]["receipt"])
    receipt["authorized"] = True
    receipt["authority_basis_id"] = "forged"
    receipt["receipt_id"] = ref.sha256_identity(ref._receipt_projection(receipt))
    weak_receipt_accepts = receipt["authorized"] and receipt["receipt_id"] == ref.sha256_identity(ref._receipt_projection(receipt))
    controls["receipt_hash_implies_authorization_origin"] = bool(weak_receipt_accepts)
    controls["receipt_authorized_boolean_only"] = bool(receipt["authorized"])

    # Weak: skip point-of-use evaluation after authority is revoked.
    revoked = make_state(revoked_at="2026-09-02T18:00:00Z")
    revoked_kwargs = deepcopy(kwargs)
    revoked_kwargs["authority_state"] = revoked
    revoked_kwargs["trusted"] = profile.TrustedBindings(decision_id, ref.authority_state_identity(revoked))
    revoked_kwargs["prior_receipts"] = [baseline["authorization"]["receipt"]]
    current = profile.human_handoff(**revoked_kwargs)
    controls["skip_point_of_use_re_evaluation"] = baseline["authorization"]["receipt"]["authorized"] is True and current["handoff_created"] is False

    # Weak: actor / operation / target blind consumption.
    wrong_subject = deepcopy(kwargs); wrong_subject["subject_id"] = "human:other"
    controls["subject_blind"] = profile.human_handoff(**wrong_subject)["handoff_created"] is False

    wrong_operation = deepcopy(kwargs); wrong_operation["jurisdiction"]["operation"] = "task.dispatch"
    try:
        profile.human_handoff(**wrong_operation)
    except profile.ProfileError as exc:
        controls["operation_blind"] = str(exc).startswith("decision_operation_authorization_mismatch")
    else:
        controls["operation_blind"] = False

    other_target = profile.immutable_ref("TARGET", "contract-d-target", "1", "other")
    wrong_target = deepcopy(kwargs); wrong_target["target_reference"] = other_target; wrong_target["jurisdiction"]["target_ref"] = other_target["identity_sha256"]
    controls["target_blind"] = profile.human_handoff(**wrong_target)["handoff_created"] is False

    blocker = deepcopy(kwargs); blocker["conflicts"] = [{"id": "c", "relevant": True, "status": "unresolved"}]
    controls["blocker_blind"] = profile.human_handoff(**blocker)["handoff_created"] is False

    # Weak: trust stale target ID instead of recomputing ExecutionIntent content.
    task = deepcopy(fixtures["task-dispatch-clear.json"])
    task_exp = expected(task)
    task_id = core.semantic_identity(task)
    intent = {
        "schema": "execution-intent-candidate-v1",
        "executable_sha256": "sha256:" + "a" * 64,
        "entry_point": "dispatch",
        "arguments": ["--once"],
        "input_identities": [task_id],
        "environment_constraints": {"network": "disabled"},
        "side_effect_targets": ["task:fixture"],
    }
    intent_id = profile.execution_intent_identity(intent)
    intent_target = profile.immutable_ref("TARGET", "execution_intent", "1", intent_id)
    machine_j = {"domain": "task", "operation": task_exp.requested_operation, "scope": "single", "target_class": "execution_intent", "target_ref": intent_target["identity_sha256"]}
    mstate = {
        "schema": ref.STATE_SCHEMA,
        "authority_state_id": "",
        "records": [{"id": "mroot", "basis_type": "grant", "subject_id": "machine:1", "domain": "task", "operation": task_exp.requested_operation, "scope": "single", "target_class": "execution_intent", "target_ref": intent_target["identity_sha256"], "valid_from": "2026-01-01T00:00:00Z", "valid_until": "2027-01-01T00:00:00Z", "revoked_at": None, "parent_id": None, "delegated_by": None}],
    }
    mstate["authority_state_id"] = ref.authority_state_identity(mstate)
    mkwargs = dict(execution_intent=intent, decision=task, expected=task_exp, trusted=profile.TrustedBindings(task_id, ref.authority_state_identity(mstate)), contract_d_root=droot, authority_state=mstate, subject_id="machine:1", evaluation_time="2026-09-02T18:00:00Z", jurisdiction=machine_j, target_reference=intent_target)
    assert profile.machine_gate(**mkwargs)["execution_permitted"] is True
    mutated = deepcopy(intent); mutated["arguments"].append("--other")
    weak_stale_id_would_accept = intent_target["identity_sha256"] == mstate["records"][0]["target_ref"]
    changed_kwargs = deepcopy(mkwargs); changed_kwargs["execution_intent"] = mutated
    correct = profile.machine_gate(**changed_kwargs)
    controls["execution_intent_id_only_without_recomputed_content_binding"] = weak_stale_id_would_accept and correct["execution_permitted"] is False

    all_caught = all(controls.values())
    result = {
        "status": "PASS" if all_caught else "FAIL",
        "control_count": len(controls),
        "controls_caught": sum(1 for value in controls.values() if value),
        "controls": controls,
    }
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, sort_keys=True))
    return 0 if all_caught else 1


if __name__ == "__main__":
    raise SystemExit(main())
