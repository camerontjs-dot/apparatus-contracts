from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract-d-root", required=True)
    parser.add_argument("--contract-e-reference", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    d_root = Path(args.contract_d_root).resolve()
    e = load_module(Path(args.contract_e_reference).resolve(), "contract_e_rc2")
    out_path = Path(args.output).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    sys.path.insert(0, str(d_root))
    from validators.contract_d_consume import ApplicabilityExpectation, consume  # type: ignore
    from validators.contract_d_core import canonical_json_bytes, semantic_identity, validate_effect  # type: ignore

    fixtures = json.loads((d_root / "fixtures/contract-d/1.0.0/valid.json").read_text())["fixtures"]
    citation_clear = deepcopy(fixtures["citation-use-clear.json"])
    hold_decision = deepcopy(fixtures["completed-hold.json"])
    failed_decision = deepcopy(fixtures["evaluation-failed.json"])

    rows: list[dict[str, Any]] = []

    def record(case_id: str, family: str, expected: Any, observed: Any, note: str = "") -> None:
        passed = observed == expected
        rows.append({"id": case_id, "family": family, "expected": expected, "observed": observed, "pass": passed, "note": note})
        if not passed:
            raise AssertionError(f"{case_id}: expected {expected!r}; observed {observed!r}")

    def decision_digest(decision: dict[str, Any]) -> str:
        return "sha256:" + hashlib.sha256(canonical_json_bytes(decision)).hexdigest()

    def expectation_for(decision: dict[str, Any], **overrides: Any) -> ApplicabilityExpectation:
        effect = validate_effect(decision["effect"]) if "effect" in decision else None
        values = {
            "input_authority": deepcopy(decision["input_authority"]),
            "policy": deepcopy(decision["policy"]),
            "target": deepcopy(decision["target"]),
            "requested_operation": effect["type"] if effect else "knowledge.cite_as_evidence",
            "effect_params": deepcopy(effect["params"]) if effect else {},
        }
        values.update(overrides)
        return ApplicabilityExpectation(**values)

    def outcome(decision: Any, expected: Any) -> str:
        return consume(decision, expected)["outcome"]

    trusted_decision_binding = {
        "producer_id": "decision-engine:trusted-fixture-producer",
        "decision_sha256": decision_digest(citation_clear),
    }

    def trusted_decision(decision: dict[str, Any], binding: dict[str, str]) -> bool:
        return binding.get("producer_id") == "decision-engine:trusted-fixture-producer" and decision_digest(decision) == binding.get("decision_sha256")

    def weak_decision_binding(decision: dict[str, Any]) -> dict[str, str]:
        return {"producer_id": "decision-engine:trusted-fixture-producer", "decision_sha256": decision_digest(decision)}

    def adapter_ready(decision: dict[str, Any], expected: Any, binding: dict[str, str]) -> bool:
        return trusted_decision(decision, binding) and outcome(decision, expected) == "candidate_for_authorization"

    def make_ref(ref_id: str, kind: str, version: str | None, immutable_id: str) -> dict[str, Any]:
        return {"ref_id": ref_id, "kind": kind, "version": version, "immutable_id": immutable_id, "identity_sha256": e.reference_identity(kind, version, immutable_id)}

    def decision_ref(decision: dict[str, Any]) -> dict[str, Any]:
        return make_ref("decision", "contract-d-decision", "1.0.0", semantic_identity(decision))

    def action_target_ref(decision: dict[str, Any]) -> dict[str, Any]:
        return make_ref("action-target", "contract-d-target", "1", "decision-target:" + e.sha256_identity(decision["target"]))

    def seal_state(value: dict[str, Any]) -> dict[str, Any]:
        value = deepcopy(value)
        value["authority_state_id"] = e.authority_state_identity(value)
        return value

    def root_state(*, subject: str, domain: str, operation: str, scope: str, target: dict[str, Any], valid_from="2026-09-02T16:00:00Z", valid_until="2026-09-02T20:00:00Z", revoked_at=None) -> dict[str, Any]:
        return seal_state({
            "schema": e.STATE_SCHEMA,
            "authority_state_id": "sha256:" + "0" * 64,
            "records": [{
                "id": "authority-root",
                "basis_type": "grant",
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
            }],
        })

    def request(*, state: dict[str, Any], subject: str, domain: str, operation: str, scope: str, target: dict[str, Any], decision: dict[str, Any], evaluation_time="2026-09-02T18:00:00Z", conflicts=None, residues=None) -> dict[str, Any]:
        dref = decision_ref(decision)
        return {
            "schema": e.REQUEST_SCHEMA,
            "request_id": "request:1",
            "authority_state_id": state["authority_state_id"],
            "evaluation_time": evaluation_time,
            "subject_id": subject,
            "jurisdiction": {
                "domain": domain,
                "operation": operation,
                "scope": scope,
                "target_class": target["kind"],
                "target_ref": target["identity_sha256"],
            },
            "references": [deepcopy(target), dref],
            "supporting_artifacts": [{"id": "support:decision", "artifact_type": "contract-d-decision-candidate", "ref_id": "decision"}],
            "conflicts": deepcopy(conflicts or []),
            "residues": deepcopy(residues or []),
        }

    def trusted_state_binding(state: dict[str, Any]) -> dict[str, str]:
        return {"source_id": "authority-config:trusted", "authority_state_id": e.authority_state_identity(state)}

    def state_origin_valid(state: dict[str, Any], binding: dict[str, str]) -> bool:
        claimed = e.claimed_authority_state_identity(state)
        recomputed = e.recomputed_authority_state_identity(state)
        return (
            binding.get("source_id") == "authority-config:trusted"
            and claimed is not None
            and recomputed is not None
            and claimed == recomputed == binding.get("authority_state_id")
        )

    def exact_decision_support(decision: dict[str, Any], req: dict[str, Any]) -> bool:
        expected = decision_ref(decision)
        refs = [x for x in req.get("references", []) if x.get("ref_id") == "decision"]
        supports = [x for x in req.get("supporting_artifacts", []) if x.get("artifact_type") == "contract-d-decision-candidate" and x.get("ref_id") == "decision"]
        return refs == [expected] and len(supports) == 1

    def fresh_authorized(state: dict[str, Any], binding: dict[str, str], req: dict[str, Any]) -> bool:
        if not state_origin_valid(state, binding):
            return False
        receipt = e.evaluate(state, req)
        return (
            receipt.get("authorized") is True
            and receipt.get("authority_conferring") is False
            and receipt.get("claimed_authority_state_id") == receipt.get("recomputed_authority_state_id") == binding["authority_state_id"]
            and receipt.get("request_sha256") == e.sha256_identity(req)
        )

    citation_expected = expectation_for(citation_clear)
    hold_expected = expectation_for(hold_decision)
    failed_expected = expectation_for(failed_decision)

    # Exact Contract D applicability surface.
    record("D01-exact-clear", "contract-d", "candidate_for_authorization", outcome(citation_clear, citation_expected))
    record("D02-hold", "contract-d", "hold", outcome(hold_decision, hold_expected))
    record("D03-failed", "contract-d", "evaluation_failed", outcome(failed_decision, failed_expected))
    record("D04-operation", "contract-d", "not_applicable", outcome(citation_clear, expectation_for(citation_clear, requested_operation="knowledge.add_verified_tag")))
    record("D05-params", "contract-d", "not_applicable", outcome(citation_clear, expectation_for(citation_clear, effect_params={"scope": "claim"})))
    for i, (field, value) in enumerate([("kind", "claim"), ("id", "other"), ("content_sha256", "sha256:" + "9" * 64)], 6):
        target = deepcopy(citation_clear["target"]); target[field] = value
        record(f"D{i:02d}-target-{field}", "contract-d", "not_applicable", outcome(citation_clear, expectation_for(citation_clear, target=target)))
    for i, (field, value) in enumerate([("id", "other.policy"), ("version", "9")], 9):
        policy = deepcopy(citation_clear["policy"]); policy[field] = value
        record(f"D{i:02d}-policy-{field}", "contract-d", "not_applicable", outcome(citation_clear, expectation_for(citation_clear, policy=policy)))
    for i, (field, value) in enumerate([("kind", "other"), ("id", "other"), ("immutable_id", "other:immutable")], 11):
        upstream = deepcopy(citation_clear["input_authority"]); upstream[field] = value
        record(f"D{i:02d}-upstream-{field}", "contract-d", "not_applicable", outcome(citation_clear, expectation_for(citation_clear, input_authority=upstream)))
    record("D14-malformed-expectation", "contract-d", "cannot_establish", outcome(citation_clear, {}))
    malformed = deepcopy(citation_clear); malformed["contract_d_version"] = "9.9.9"
    record("D15-malformed-decision", "contract-d", "cannot_establish", outcome(malformed, citation_expected))

    # Decision trusted-origin attacks.
    record("O01-trusted-decision", "decision-origin", True, trusted_decision(citation_clear, trusted_decision_binding))
    forged = deepcopy(citation_clear); forged["target"]["id"] = "forged-target"
    forged_expected = expectation_for(forged)
    record("O02-forged-d-still-applicable-to-self-derived-expectation", "decision-origin", "candidate_for_authorization", outcome(forged, forged_expected))
    record("O03-forged-d-rejected-by-external-anchor", "decision-origin", False, trusted_decision(forged, trusted_decision_binding))
    record("O04-weak-derived-decision-anchor-is-fooled", "weak-control", True, trusted_decision(forged, weak_decision_binding(forged)))
    metadata = deepcopy(citation_clear); metadata["metadata"] = {"diagnostic": "changed"}
    record("O05-exact-byte-anchor-detects-metadata-change", "decision-origin", False, trusted_decision(metadata, trusted_decision_binding))

    # Human action profile.
    human = "human:operator-1"
    human_target = action_target_ref(citation_clear)
    human_state = root_state(subject=human, domain="knowledge", operation="knowledge.cite_as_evidence", scope=citation_clear["target"]["kind"], target=human_target)
    human_binding = trusted_state_binding(human_state)
    human_req = request(state=human_state, subject=human, domain="knowledge", operation="knowledge.cite_as_evidence", scope=citation_clear["target"]["kind"], target=human_target, decision=citation_clear)

    def human_accept(decision, expected, dbinding, state, sbinding, req):
        return adapter_ready(decision, expected, dbinding) and exact_decision_support(decision, req) and fresh_authorized(state, sbinding, req)

    record("H01-positive", "human", True, human_accept(citation_clear, citation_expected, trusted_decision_binding, human_state, human_binding, human_req))
    for i, (path, value) in enumerate([
        ("subject_id", "human:other"),
        ("jurisdiction.domain", "execution"),
        ("jurisdiction.operation", "other"),
        ("jurisdiction.scope", "other"),
        ("jurisdiction.target_class", "other"),
        ("jurisdiction.target_ref", make_ref("x", "other", "1", "other")["identity_sha256"]),
    ], 2):
        r = deepcopy(human_req)
        if "." in path:
            a, b = path.split("."); r[a][b] = value
        else:
            r[path] = value
        record(f"H{i:02d}-{path}", "human", False, human_accept(citation_clear, citation_expected, trusted_decision_binding, human_state, human_binding, r))
    r = deepcopy(human_req); r["supporting_artifacts"] = []
    record("H08-support-removed", "human", False, human_accept(citation_clear, citation_expected, trusted_decision_binding, human_state, human_binding, r))
    r = deepcopy(human_req); r["references"][1] = decision_ref(forged)
    record("H09-decision-reference-substitution", "human", False, human_accept(citation_clear, citation_expected, trusted_decision_binding, human_state, human_binding, r))
    r = deepcopy(human_req); r["conflicts"] = [{"id": "c", "relevant": True, "status": "unresolved"}]
    record("H10-conflict", "human", False, human_accept(citation_clear, citation_expected, trusted_decision_binding, human_state, human_binding, r))
    r = deepcopy(human_req); r["residues"] = [{"id": "r", "relevant": True, "status": "contested"}]
    record("H11-residue", "human", False, human_accept(citation_clear, citation_expected, trusted_decision_binding, human_state, human_binding, r))

    # AuthorityState external-origin attacks.
    record("A01-trusted-state", "authority-origin", True, state_origin_valid(human_state, human_binding))
    forged_state = root_state(subject=human, domain="knowledge", operation="knowledge.cite_as_evidence", scope=citation_clear["target"]["kind"], target=human_target, valid_until="2026-09-02T21:00:00Z")
    forged_req = request(state=forged_state, subject=human, domain="knowledge", operation="knowledge.cite_as_evidence", scope=citation_clear["target"]["kind"], target=human_target, decision=citation_clear)
    record("A02-forged-root-core-e-can-authorize", "authority-origin", True, e.evaluate(forged_state, forged_req)["authorized"])
    record("A03-forged-root-rejected-by-external-anchor", "authority-origin", False, state_origin_valid(forged_state, human_binding))
    record("A04-weak-derived-state-anchor-is-fooled", "weak-control", True, state_origin_valid(forged_state, trusted_state_binding(forged_state)))
    for i, (field, value) in enumerate([
        ("subject_id", "human:other"),
        ("domain", "other"),
        ("operation", "other"),
        ("scope", "other"),
        ("target_class", "other"),
        ("target_ref", make_ref("o", "other", "1", "other")["identity_sha256"]),
        ("valid_until", "2026-09-02T19:00:00Z"),
        ("revoked_at", "2026-09-02T19:00:00Z"),
    ], 5):
        s = deepcopy(human_state); s["records"][0][field] = value; s["authority_state_id"] = e.authority_state_identity(s)
        record(f"A{i:02d}-state-{field}-anchor-invalidated", "authority-origin", False, state_origin_valid(s, human_binding))
    mismatch_state = deepcopy(human_state); mismatch_state["authority_state_id"] = "sha256:" + "f" * 64
    mismatch_receipt = e.evaluate(mismatch_state, deepcopy(human_req))
    record("A13-claimed-recomputed-mismatch-denied", "authority-origin", False, mismatch_receipt["authorized"])
    record("A14-dual-identity-preserved", "authority-origin", True, mismatch_receipt["claimed_authority_state_id"] != mismatch_receipt["recomputed_authority_state_id"] and mismatch_receipt["recomputed_authority_state_id"] == human_binding["authority_state_id"])

    revoked = deepcopy(human_state); revoked["records"][0]["revoked_at"] = "2026-09-02T18:00:00Z"; revoked["authority_state_id"] = e.authority_state_identity(revoked)
    revoked_binding = trusted_state_binding(revoked)
    revoked_req = request(state=revoked, subject=human, domain="knowledge", operation="knowledge.cite_as_evidence", scope=citation_clear["target"]["kind"], target=human_target, decision=citation_clear)
    record("A15-revoked-current-trusted-state-denied-by-e", "authority-origin", False, fresh_authorized(revoked, revoked_binding, revoked_req))

    # Machine execution profile.
    EXEC_KEYS = {"decision_identity", "requested_operation", "requested_effect_params", "decision_target", "executor_subject", "executable_sha256", "entry_point", "arguments", "input_identities", "environment", "side_effect_target"}

    def intent(decision, subject):
        effect = validate_effect(decision["effect"])
        return {
            "decision_identity": semantic_identity(decision),
            "requested_operation": effect["type"],
            "requested_effect_params": deepcopy(effect["params"]),
            "decision_target": deepcopy(decision["target"]),
            "executor_subject": subject,
            "executable_sha256": "sha256:" + "a" * 64,
            "entry_point": "apply-effect",
            "arguments": ["--mode", "exact"],
            "input_identities": [semantic_identity(decision)],
            "environment": {"network": "disabled", "workspace": "ephemeral"},
            "side_effect_target": deepcopy(decision["target"]),
        }

    def intent_id(value):
        if set(value) != EXEC_KEYS:
            return None
        return e.sha256_identity(value)

    machine = "machine:executor-1"
    base_intent = intent(citation_clear, machine)
    intent_ref = make_ref("execution-intent", "execution-intent", "1", intent_id(base_intent))
    machine_state = root_state(subject=machine, domain="execution", operation="execute", scope="single-intent", target=intent_ref)
    machine_binding = trusted_state_binding(machine_state)
    machine_req = request(state=machine_state, subject=machine, domain="execution", operation="execute", scope="single-intent", target=intent_ref, decision=citation_clear)

    def machine_accept(decision, expected, dbinding, current_state, sbinding, req, current_intent):
        current_id = intent_id(current_intent)
        if current_id is None:
            return False
        if not adapter_ready(decision, expected, dbinding) or not exact_decision_support(decision, req):
            return False
        if current_intent["decision_identity"] != semantic_identity(decision):
            return False
        effect = validate_effect(decision["effect"])
        if current_intent["requested_operation"] != effect["type"] or current_intent["requested_effect_params"] != effect["params"] or current_intent["decision_target"] != decision["target"] or current_intent["executor_subject"] != req.get("subject_id"):
            return False
        if req.get("jurisdiction", {}).get("target_ref") != make_ref("execution-intent", "execution-intent", "1", current_id)["identity_sha256"]:
            return False
        return fresh_authorized(current_state, sbinding, req)

    record("M01-positive", "machine", True, machine_accept(citation_clear, citation_expected, trusted_decision_binding, machine_state, machine_binding, machine_req, base_intent))

    intent_mutators = [
        ("executable", lambda x, n: x.__setitem__("executable_sha256", "sha256:" + format(n, "064x")[-64:])),
        ("entry", lambda x, n: x.__setitem__("entry_point", f"other-{n}")),
        ("args", lambda x, n: x.__setitem__("arguments", ["--variant", str(n)])),
        ("inputs", lambda x, n: x.__setitem__("input_identities", [f"other:{n}"])),
        ("network", lambda x, n: x["environment"].__setitem__("network", f"mode-{n}")),
        ("workspace", lambda x, n: x["environment"].__setitem__("workspace", f"space-{n}")),
        ("operation", lambda x, n: x.__setitem__("requested_operation", f"other.operation.{n}")),
        ("params", lambda x, n: x.__setitem__("requested_effect_params", {"variant": n})),
        ("target", lambda x, n: x["decision_target"].__setitem__("id", f"other-{n}")),
        ("subject", lambda x, n: x.__setitem__("executor_subject", f"machine:other-{n}")),
        ("side-effect", lambda x, n: x["side_effect_target"].__setitem__("id", f"side-{n}")),
    ]
    case_no = 2
    for label, mutate in intent_mutators:
        for variant in range(1, 4):
            changed = deepcopy(base_intent); mutate(changed, variant)
            record(f"M{case_no:02d}-{label}-{variant}", "machine-intent-mutation", False, machine_accept(citation_clear, citation_expected, trusted_decision_binding, machine_state, machine_binding, machine_req, changed))
            case_no += 1

    bad_intent = deepcopy(base_intent); bad_intent["future"] = True
    record(f"M{case_no:02d}-unknown-intent-field", "machine", False, machine_accept(citation_clear, citation_expected, trusted_decision_binding, machine_state, machine_binding, machine_req, bad_intent)); case_no += 1
    r = deepcopy(machine_req); r["subject_id"] = "machine:other"
    record(f"M{case_no:02d}-request-subject", "machine", False, machine_accept(citation_clear, citation_expected, trusted_decision_binding, machine_state, machine_binding, r, base_intent)); case_no += 1
    r = deepcopy(machine_req); r["jurisdiction"]["operation"] = "dispatch"
    record(f"M{case_no:02d}-request-operation", "machine", False, machine_accept(citation_clear, citation_expected, trusted_decision_binding, machine_state, machine_binding, r, base_intent)); case_no += 1
    r = deepcopy(machine_req); r["jurisdiction"]["scope"] = "other"
    record(f"M{case_no:02d}-request-scope", "machine", False, machine_accept(citation_clear, citation_expected, trusted_decision_binding, machine_state, machine_binding, r, base_intent)); case_no += 1

    old_receipt = e.evaluate(machine_state, machine_req)
    revoked_machine = deepcopy(machine_state); revoked_machine["records"][0]["revoked_at"] = "2026-09-02T18:00:00Z"; revoked_machine["authority_state_id"] = e.authority_state_identity(revoked_machine)
    revoked_machine_binding = trusted_state_binding(revoked_machine)
    revoked_machine_req = deepcopy(machine_req); revoked_machine_req["authority_state_id"] = revoked_machine["authority_state_id"]
    record(f"M{case_no:02d}-old-receipt-was-authorized", "machine", True, old_receipt["authorized"]); case_no += 1
    record(f"M{case_no:02d}-fresh-revocation-blocks", "machine", False, machine_accept(citation_clear, citation_expected, trusted_decision_binding, revoked_machine, revoked_machine_binding, revoked_machine_req, base_intent)); case_no += 1

    # Receipt-origin attack and point-of-use defense.
    denied = e.evaluate(revoked_machine, revoked_machine_req)
    forged_receipt = deepcopy(denied)
    forged_receipt["authorized"] = True
    forged_receipt["authority_basis_id"] = "authority-root"
    projection = {k: deepcopy(v) for k, v in forged_receipt.items() if k not in {"receipt_id", "diagnostics"}}
    forged_receipt["receipt_id"] = e.sha256_identity(projection)

    def weak_receipt_only(receipt, req):
        projection = {k: deepcopy(v) for k, v in receipt.items() if k not in {"receipt_id", "diagnostics"}}
        return receipt.get("authorized") is True and receipt.get("request_sha256") == e.sha256_identity(req) and receipt.get("receipt_id") == e.sha256_identity(projection)

    record("R01-forged-receipt-fools-receipt-only", "weak-control", True, weak_receipt_only(forged_receipt, revoked_machine_req))
    record("R02-fresh-point-of-use-ignores-forged-receipt", "receipt-origin", False, machine_accept(citation_clear, citation_expected, trusted_decision_binding, revoked_machine, revoked_machine_binding, revoked_machine_req, base_intent))
    record("R03-dual-id-authorized-equality", "receipt", True, old_receipt["claimed_authority_state_id"] == old_receipt["recomputed_authority_state_id"] == machine_binding["authority_state_id"])
    changed_diag = deepcopy(old_receipt); changed_diag["diagnostics"] = ["x", "y"]
    record("R04-diagnostic-content-nonsemantic", "metamorphic", old_receipt["receipt_id"], e.sha256_identity({k: deepcopy(v) for k, v in changed_diag.items() if k not in {"receipt_id", "diagnostics"}}))
    changed_claim = deepcopy(old_receipt); changed_claim["claimed_authority_state_id"] = "sha256:" + "1" * 64
    record("R05-claimed-id-semantic", "metamorphic", False, e.sha256_identity({k: deepcopy(v) for k, v in changed_claim.items() if k not in {"receipt_id", "diagnostics"}}) == old_receipt["receipt_id"])
    changed_recomputed = deepcopy(old_receipt); changed_recomputed["recomputed_authority_state_id"] = "sha256:" + "2" * 64
    record("R06-recomputed-id-semantic", "metamorphic", False, e.sha256_identity({k: deepcopy(v) for k, v in changed_recomputed.items() if k not in {"receipt_id", "diagnostics"}}) == old_receipt["receipt_id"])

    # Supporting artifacts change request/receipt binding but cannot confer standing authority.
    invalid_state = {"schema": e.STATE_SCHEMA, "authority_state_id": "sha256:" + "0" * 64, "records": []}
    for i in range(1, 9):
        rr = deepcopy(human_req)
        extra = make_ref(f"extra-{i}", "support", "1", f"support:{i}")
        rr["references"].append(extra)
        rr["supporting_artifacts"].append({"id": f"support:{i}", "artifact_type": "nonconferring", "ref_id": f"extra-{i}"})
        rr["authority_state_id"] = invalid_state["authority_state_id"]
        record(f"S{i:02d}-support-cannot-confer", "metamorphic", False, e.evaluate(invalid_state, rr)["authorized"])

    # Bound field identity mutation always invalidates an existing external AuthorityState trust anchor.
    for idx, field in enumerate(["subject_id", "domain", "operation", "scope", "target_class", "target_ref", "valid_from", "valid_until", "revoked_at"], 1):
        for variant in range(1, 4):
            s = deepcopy(human_state)
            if field == "subject_id": value = f"human:v{variant}"
            elif field in {"domain", "operation", "scope", "target_class"}: value = f"other-{field}-{variant}"
            elif field == "target_ref": value = make_ref("m", "other", "1", f"m:{variant}")["identity_sha256"]
            elif field == "valid_from": value = f"2026-09-02T1{variant}:00:00Z"
            elif field == "valid_until": value = f"2026-09-02T2{variant}:00:00Z"
            else: value = f"2026-09-02T2{variant}:30:00Z"
            s["records"][0][field] = value
            s["authority_state_id"] = e.authority_state_identity(s)
            record(f"B{idx:02d}-{field}-{variant}", "state-binding-metamorphic", False, state_origin_valid(s, human_binding))

    # Require broad attack count and weak-control discrimination.
    weak_ids = [r["id"] for r in rows if r["family"] == "weak-control"]
    if len(rows) < 101:
        raise AssertionError(f"pressure matrix too small: {len(rows)}")
    if len(weak_ids) < 3:
        raise AssertionError("insufficient weak controls")

    result = {
        "status": "PASS",
        "case_count": len(rows),
        "passed": sum(1 for r in rows if r["pass"]),
        "failed_ids": [r["id"] for r in rows if not r["pass"]],
        "weak_control_ids": weak_ids,
        "trusted_decision_digest": trusted_decision_binding["decision_sha256"],
        "trusted_human_authority_state_id": human_binding["authority_state_id"],
        "trusted_machine_authority_state_id": machine_binding["authority_state_id"],
        "rows": rows,
    }
    out_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("status", "case_count", "passed", "failed_ids", "weak_control_ids")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
