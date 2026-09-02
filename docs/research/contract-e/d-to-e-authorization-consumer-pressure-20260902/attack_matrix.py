from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable


def load_contract_e(reference_path: Path):
    spec = importlib.util.spec_from_file_location("contract_e_rc1_reference", reference_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load Contract E reference")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical_obj(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract-d-root", required=True)
    parser.add_argument("--contract-e-root", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    d_root = Path(args.contract_d_root).resolve()
    e_root = Path(args.contract_e_root).resolve()
    out_path = Path(args.output).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    sys.path.insert(0, str(d_root))
    from validators.contract_d_consume import ApplicabilityExpectation, consume  # type: ignore
    from validators.contract_d_core import semantic_identity, validate_effect  # type: ignore

    e = load_contract_e(
        e_root / "docs/research/contract-e/v1-closure-20260902/candidate/reference.py"
    )

    fixture_doc = json.loads(
        (d_root / "fixtures/contract-d/1.0.0/valid.json").read_text(encoding="utf-8")
    )
    fixtures = fixture_doc["fixtures"]
    citation_clear = deepcopy(fixtures["citation-use-clear.json"])
    source_clear = deepcopy(fixtures["source-audit-clear.json"])
    hold_decision = deepcopy(fixtures["completed-hold.json"])
    failed_decision = deepcopy(fixtures["evaluation-failed.json"])

    rows: list[dict[str, Any]] = []

    def record(case_id: str, family: str, expected: Any, observed: Any, note: str = "") -> None:
        passed = observed == expected
        rows.append(
            {
                "id": case_id,
                "family": family,
                "expected": expected,
                "observed": observed,
                "pass": passed,
                "note": note,
            }
        )
        if not passed:
            raise AssertionError(f"{case_id}: expected {expected!r}, observed {observed!r}")

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

    def d_outcome(decision: Any, expected: Any) -> str:
        return consume(decision, expected)["outcome"]

    def make_ref(ref_id: str, kind: str, version: str | None, immutable_id: str) -> dict[str, Any]:
        return {
            "ref_id": ref_id,
            "kind": kind,
            "version": version,
            "immutable_id": immutable_id,
            "identity_sha256": e.reference_identity(kind, version, immutable_id),
        }

    def decision_ref(decision: dict[str, Any]) -> dict[str, Any]:
        return make_ref(
            "decision",
            "contract-d-decision",
            "1.0.0",
            semantic_identity(decision),
        )

    def decision_target_ref(decision: dict[str, Any]) -> dict[str, Any]:
        immutable = "decision-target:" + e.sha256_identity(decision["target"])
        return make_ref("action-target", "contract-d-target", "1", immutable)

    def seal_state(state: dict[str, Any]) -> dict[str, Any]:
        state = deepcopy(state)
        state["authority_state_id"] = e.authority_state_identity(state)
        return state

    def root_state(
        *,
        subject: str,
        domain: str,
        operation: str,
        scope: str,
        target_class: str,
        target_ref: str,
        valid_from: str = "2026-09-02T16:00:00Z",
        valid_until: str | None = "2026-09-02T20:00:00Z",
        revoked_at: str | None = None,
    ) -> dict[str, Any]:
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

    def request(
        *,
        state: dict[str, Any],
        subject: str,
        domain: str,
        operation: str,
        scope: str,
        target_class: str,
        target_ref: dict[str, Any],
        dref: dict[str, Any],
        evaluation_time: str = "2026-09-02T18:00:00Z",
        conflicts: list[dict[str, Any]] | None = None,
        residues: list[dict[str, Any]] | None = None,
        extra_refs: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        refs = [deepcopy(target_ref), deepcopy(dref)]
        if extra_refs:
            refs.extend(deepcopy(extra_refs))
        return {
            "schema": e.REQUEST_SCHEMA,
            "request_id": "request-1",
            "authority_state_id": state["authority_state_id"],
            "evaluation_time": evaluation_time,
            "subject_id": subject,
            "jurisdiction": {
                "domain": domain,
                "operation": operation,
                "scope": scope,
                "target_class": target_class,
                "target_ref": target_ref["identity_sha256"],
            },
            "references": refs,
            "supporting_artifacts": [
                {
                    "id": "support-decision",
                    "artifact_type": "contract-d-decision-candidate",
                    "ref_id": dref["ref_id"],
                }
            ],
            "conflicts": deepcopy(conflicts or []),
            "residues": deepcopy(residues or []),
        }

    def adapter_ready(decision: Any, expected: Any) -> bool:
        return d_outcome(decision, expected) == "candidate_for_authorization"

    def exact_decision_support_present(decision: dict[str, Any], req: dict[str, Any]) -> bool:
        expected_ref = decision_ref(decision)
        refs = [r for r in req.get("references", []) if r.get("ref_id") == "decision"]
        if refs != [expected_ref]:
            return False
        supports = [
            s
            for s in req.get("supporting_artifacts", [])
            if s.get("artifact_type") == "contract-d-decision-candidate"
            and s.get("ref_id") == "decision"
        ]
        return len(supports) == 1

    def verify_receipt_for_request(receipt: dict[str, Any], req: dict[str, Any]) -> bool:
        if receipt.get("schema") != e.RECEIPT_SCHEMA:
            return False
        if receipt.get("authority_conferring") is not False or receipt.get("authorized") is not True:
            return False
        if receipt.get("request_id") != req.get("request_id"):
            return False
        if receipt.get("request_sha256") != e.sha256_identity(req):
            return False
        for key in ("authority_state_id", "evaluation_time", "subject_id", "jurisdiction"):
            if receipt.get(key) != req.get(key):
                return False
        projection = {
            key: deepcopy(value)
            for key, value in receipt.items()
            if key not in {"receipt_id", "diagnostics"}
        }
        return receipt.get("receipt_id") == e.sha256_identity(projection)

    def human_bundle_valid(decision: dict[str, Any], expected: Any, req: dict[str, Any]) -> bool:
        if not adapter_ready(decision, expected):
            return False
        if not exact_decision_support_present(decision, req):
            return False
        effect = validate_effect(decision["effect"])
        target = decision_target_ref(decision)
        j = req.get("jurisdiction", {})
        return (
            j.get("domain") == "knowledge"
            and j.get("operation") == effect["type"]
            and j.get("scope") == decision["target"]["kind"]
            and j.get("target_class") == decision["target"]["kind"]
            and j.get("target_ref") == target["identity_sha256"]
        )

    EXECUTION_INTENT_KEYS = {
        "decision_identity",
        "requested_operation",
        "requested_effect_params",
        "decision_target",
        "executor_subject",
        "executable_sha256",
        "entry_point",
        "arguments",
        "input_identities",
        "environment",
    }

    def intent_identity(intent: dict[str, Any]) -> str:
        if set(intent) != EXECUTION_INTENT_KEYS:
            raise ValueError("invalid execution intent shape")
        return e.sha256_identity(intent)

    def execution_intent(decision: dict[str, Any], subject: str) -> dict[str, Any]:
        effect = validate_effect(decision["effect"])
        return {
            "decision_identity": semantic_identity(decision),
            "requested_operation": effect["type"],
            "requested_effect_params": deepcopy(effect["params"]),
            "decision_target": deepcopy(decision["target"]),
            "executor_subject": subject,
            "executable_sha256": "sha256:" + "a" * 64,
            "entry_point": "apply-knowledge-effect",
            "arguments": ["--mode", "exact"],
            "input_identities": [semantic_identity(decision)],
            "environment": {"network": "disabled", "workspace": "ephemeral"},
        }

    def intent_ref(intent: dict[str, Any]) -> dict[str, Any]:
        return make_ref("execution-intent", "execution-intent", "1", intent_identity(intent))

    def machine_bundle_valid(
        decision: dict[str, Any], expected: Any, req: dict[str, Any], intent: dict[str, Any]
    ) -> bool:
        if not adapter_ready(decision, expected):
            return False
        if not exact_decision_support_present(decision, req):
            return False
        effect = validate_effect(decision["effect"])
        if set(intent) != EXECUTION_INTENT_KEYS:
            return False
        if intent["decision_identity"] != semantic_identity(decision):
            return False
        if intent["requested_operation"] != effect["type"]:
            return False
        if intent["requested_effect_params"] != effect["params"]:
            return False
        if intent["decision_target"] != decision["target"]:
            return False
        if intent["executor_subject"] != req.get("subject_id"):
            return False
        expected_ref = intent_ref(intent)
        j = req.get("jurisdiction", {})
        return (
            j.get("domain") == "execution"
            and j.get("operation") == "execute"
            and j.get("scope") == "single-intent"
            and j.get("target_class") == "execution-intent"
            and j.get("target_ref") == expected_ref["identity_sha256"]
        )

    def strong_human_accept(
        decision: dict[str, Any], expected: Any, state: dict[str, Any], req: dict[str, Any]
    ) -> bool:
        if not human_bundle_valid(decision, expected, req):
            return False
        receipt = e.evaluate(state, req)
        return verify_receipt_for_request(receipt, req)

    def strong_machine_accept(
        decision: dict[str, Any],
        expected: Any,
        current_state: dict[str, Any],
        req: dict[str, Any],
        intent: dict[str, Any],
    ) -> bool:
        if not machine_bundle_valid(decision, expected, req, intent):
            return False
        fresh = e.evaluate(current_state, req)
        return verify_receipt_for_request(fresh, req)

    citation_expected = expectation_for(citation_clear)
    source_expected = expectation_for(source_clear)
    hold_expected = expectation_for(hold_decision)
    failed_expected = expectation_for(failed_decision)

    # Contract D applicability boundary.
    record("D01-clear-exact", "contract-d", "candidate_for_authorization", d_outcome(citation_clear, citation_expected))
    record("D02-hold", "contract-d", "hold", d_outcome(hold_decision, hold_expected))
    record("D03-failed", "contract-d", "evaluation_failed", d_outcome(failed_decision, failed_expected))

    bad = expectation_for(citation_clear, requested_operation="knowledge.add_verified_tag")
    record("D04-operation-substitution", "contract-d", "not_applicable", d_outcome(citation_clear, bad))
    bad = expectation_for(citation_clear, effect_params={"scope": "claim"})
    record("D05-param-substitution", "contract-d", "not_applicable", d_outcome(citation_clear, bad))

    for case_id, field, replacement in [
        ("D06-target-kind", "kind", "claim"),
        ("D07-target-id", "id", "other"),
        ("D08-target-content", "content_sha256", "sha256:" + "9" * 64),
    ]:
        target = deepcopy(citation_clear["target"])
        target[field] = replacement
        record(case_id, "contract-d", "not_applicable", d_outcome(citation_clear, expectation_for(citation_clear, target=target)))

    policy = deepcopy(citation_clear["policy"]); policy["id"] = "other.policy"
    record("D09-policy-id", "contract-d", "not_applicable", d_outcome(citation_clear, expectation_for(citation_clear, policy=policy)))
    policy = deepcopy(citation_clear["policy"]); policy["version"] = "2"
    record("D10-policy-version", "contract-d", "not_applicable", d_outcome(citation_clear, expectation_for(citation_clear, policy=policy)))

    for case_id, field, replacement in [
        ("D11-upstream-kind", "kind", "other"),
        ("D12-upstream-id", "id", "other"),
        ("D13-upstream-immutable", "immutable_id", "other:immutable"),
    ]:
        upstream = deepcopy(citation_clear["input_authority"]); upstream[field] = replacement
        record(case_id, "contract-d", "not_applicable", d_outcome(citation_clear, expectation_for(citation_clear, input_authority=upstream)))

    record("D14-malformed-expectation", "contract-d", "cannot_establish", d_outcome(citation_clear, {}))
    tampered = deepcopy(citation_clear); tampered["contract_d_version"] = "9.9.9"
    record("D15-malformed-decision", "contract-d", "cannot_establish", d_outcome(tampered, citation_expected))

    # Contract D metadata-only invariance.
    citation_meta = deepcopy(citation_clear)
    citation_meta["metadata"] = {"explanation": "diagnostic-only"}
    record("M01-d-metadata-semantic-identity", "metamorphic", semantic_identity(citation_clear), semantic_identity(citation_meta))

    # Human positive bundle.
    human = "human:operator-1"
    dref = decision_ref(citation_clear)
    href = decision_target_ref(citation_clear)
    human_state = root_state(
        subject=human,
        domain="knowledge",
        operation="knowledge.cite_as_evidence",
        scope=citation_clear["target"]["kind"],
        target_class=citation_clear["target"]["kind"],
        target_ref=href["identity_sha256"],
    )
    human_req = request(
        state=human_state,
        subject=human,
        domain="knowledge",
        operation="knowledge.cite_as_evidence",
        scope=citation_clear["target"]["kind"],
        target_class=citation_clear["target"]["kind"],
        target_ref=href,
        dref=dref,
    )
    human_receipt = e.evaluate(human_state, human_req)
    record("H01-human-positive", "human", True, strong_human_accept(citation_clear, citation_expected, human_state, human_req))
    record("R01-receipt-nonconferring", "receipt", False, human_receipt["authority_conferring"])
    record("R02-receipt-binds-request", "receipt", True, verify_receipt_for_request(human_receipt, human_req))

    # Adapter cannot cross non-candidate D outcomes.
    record("A01-hold-does-not-cross", "adapter", False, adapter_ready(hold_decision, hold_expected))
    record("A02-failed-does-not-cross", "adapter", False, adapter_ready(failed_decision, failed_expected))
    record("A03-nonapplicable-does-not-cross", "adapter", False, adapter_ready(citation_clear, bad))
    record("A04-cannot-establish-does-not-cross", "adapter", False, adapter_ready(tampered, citation_expected))

    no_support = deepcopy(human_req); no_support["supporting_artifacts"] = []
    record("A05-decision-support-required", "adapter", False, human_bundle_valid(citation_clear, citation_expected, no_support))
    swapped_support = deepcopy(human_req)
    swapped_support["references"] = [href, decision_ref(source_clear)]
    record("A06-decision-support-substitution", "adapter", False, human_bundle_valid(citation_clear, citation_expected, swapped_support))

    # E alone may still authorize without the D support because support is deliberately non-conferring;
    # the integration adapter, not Contract E, owns that requirement.
    record("A07-e-does-not-use-d-support-as-authority", "adapter", True, e.evaluate(human_state, no_support)["authorized"])

    # Contract D candidate/support alone cannot replace AuthorityState.
    empty_state: dict[str, Any] = {}
    record("E01-d-candidate-not-authority", "contract-e", False, e.evaluate(empty_state, human_req)["authorized"])

    prior_receipt_ref = make_ref("prior-receipt", "contract-e-receipt", "candidate-rc1", human_receipt["receipt_id"])
    receipt_support_req = deepcopy(human_req)
    receipt_support_req["references"].append(prior_receipt_ref)
    receipt_support_req["supporting_artifacts"].append({"id": "support-receipt", "artifact_type": "prior-authorization-receipt", "ref_id": "prior-receipt"})
    record("E02-prior-receipt-not-standing-authority", "contract-e", False, e.evaluate(empty_state, receipt_support_req)["authorized"])

    # Exact subject/jurisdiction attacks.
    for case_id, mutator in [
        ("E03-subject-swap", lambda r: r.__setitem__("subject_id", "machine:service-1")),
        ("E04-wildcard-subject", lambda r: r.__setitem__("subject_id", "*")),
        ("E05-domain", lambda r: r["jurisdiction"].__setitem__("domain", "execution")),
        ("E06-operation", lambda r: r["jurisdiction"].__setitem__("operation", "knowledge.add_verified_tag")),
        ("E07-scope", lambda r: r["jurisdiction"].__setitem__("scope", "object")),
        ("E08-target-class", lambda r: r["jurisdiction"].__setitem__("target_class", "execution-intent")),
    ]:
        req2 = deepcopy(human_req); mutator(req2)
        record(case_id, "contract-e", False, e.evaluate(human_state, req2)["authorized"])

    other_target = make_ref("other-target", "contract-d-target", "1", "decision-target:" + "sha256:" + "3" * 64)
    req2 = deepcopy(human_req); req2["references"].append(other_target); req2["jurisdiction"]["target_ref"] = other_target["identity_sha256"]
    record("E09-target-ref", "contract-e", False, e.evaluate(human_state, req2)["authorized"])

    state2 = deepcopy(human_state); state2["records"][0]["scope"] = "mutated-without-reseal"
    record("E10-state-identity-tamper", "contract-e", False, e.evaluate(state2, human_req)["authorized"])
    req2 = deepcopy(human_req); req2["authority_state_id"] = "sha256:" + "4" * 64
    record("E11-request-state-id-mismatch", "contract-e", False, e.evaluate(human_state, req2)["authorized"])

    future_state = root_state(subject=human, domain="knowledge", operation="knowledge.cite_as_evidence", scope="knowledge", target_class="knowledge", target_ref=href["identity_sha256"], valid_from="2026-09-02T19:00:00Z")
    req2 = request(state=future_state, subject=human, domain="knowledge", operation="knowledge.cite_as_evidence", scope="knowledge", target_class="knowledge", target_ref=href, dref=dref, evaluation_time="2026-09-02T18:00:00Z")
    record("E12-not-yet-valid", "currentness", False, e.evaluate(future_state, req2)["authorized"])

    expired_state = root_state(subject=human, domain="knowledge", operation="knowledge.cite_as_evidence", scope="knowledge", target_class="knowledge", target_ref=href["identity_sha256"], valid_until="2026-09-02T17:59:59Z")
    req2 = request(state=expired_state, subject=human, domain="knowledge", operation="knowledge.cite_as_evidence", scope="knowledge", target_class="knowledge", target_ref=href, dref=dref)
    record("E13-expired", "currentness", False, e.evaluate(expired_state, req2)["authorized"])

    revoked_state = root_state(subject=human, domain="knowledge", operation="knowledge.cite_as_evidence", scope="knowledge", target_class="knowledge", target_ref=href["identity_sha256"], revoked_at="2026-09-02T17:00:00Z")
    req2 = request(state=revoked_state, subject=human, domain="knowledge", operation="knowledge.cite_as_evidence", scope="knowledge", target_class="knowledge", target_ref=href, dref=dref)
    record("E14-revoked-before", "currentness", False, e.evaluate(revoked_state, req2)["authorized"])

    at_revoke = root_state(subject=human, domain="knowledge", operation="knowledge.cite_as_evidence", scope="knowledge", target_class="knowledge", target_ref=href["identity_sha256"], revoked_at="2026-09-02T18:00:00Z")
    req2 = request(state=at_revoke, subject=human, domain="knowledge", operation="knowledge.cite_as_evidence", scope="knowledge", target_class="knowledge", target_ref=href, dref=dref)
    record("E15-at-revocation", "currentness", False, e.evaluate(at_revoke, req2)["authorized"])

    at_start = root_state(subject=human, domain="knowledge", operation="knowledge.cite_as_evidence", scope="knowledge", target_class="knowledge", target_ref=href["identity_sha256"], valid_from="2026-09-02T18:00:00Z")
    req2 = request(state=at_start, subject=human, domain="knowledge", operation="knowledge.cite_as_evidence", scope="knowledge", target_class="knowledge", target_ref=href, dref=dref, evaluation_time="2026-09-02T18:00:00Z")
    record("P01-inclusive-valid-from", "positive", True, e.evaluate(at_start, req2)["authorized"])

    at_end = root_state(subject=human, domain="knowledge", operation="knowledge.cite_as_evidence", scope="knowledge", target_class="knowledge", target_ref=href["identity_sha256"], valid_until="2026-09-02T18:00:00Z")
    req2 = request(state=at_end, subject=human, domain="knowledge", operation="knowledge.cite_as_evidence", scope="knowledge", target_class="knowledge", target_ref=href, dref=dref, evaluation_time="2026-09-02T18:00:00Z")
    record("P02-inclusive-valid-until", "positive", True, e.evaluate(at_end, req2)["authorized"])

    # Delegation controls.
    delegated_state = deepcopy(human_state)
    root = delegated_state["records"][0]
    root["subject_id"] = "human:owner"
    delegated_state["records"].append({
        **deepcopy(root),
        "id": "authority-delegated",
        "basis_type": "delegation",
        "subject_id": human,
        "parent_id": "authority-root",
        "delegated_by": "human:owner",
    })
    delegated_state = seal_state(delegated_state)
    delegated_req = request(state=delegated_state, subject=human, domain="knowledge", operation="knowledge.cite_as_evidence", scope="knowledge", target_class="knowledge", target_ref=href, dref=dref)
    record("P03-valid-delegation", "delegation", True, e.evaluate(delegated_state, delegated_req)["authorized"])

    for case_id, mutate_state in [
        ("E16-broken-parent", lambda s: s["records"][1].__setitem__("parent_id", "missing")),
        ("E17-wrong-delegated-by", lambda s: s["records"][1].__setitem__("delegated_by", "other")),
        ("E18-delegation-bounds-change", lambda s: s["records"][1].__setitem__("scope", "object")),
        ("E19-duplicate-record-id", lambda s: s["records"][1].__setitem__("id", "authority-root")),
        ("E20-nondelegation-child", lambda s: s["records"][1].__setitem__("basis_type", "grant")),
    ]:
        st = deepcopy(delegated_state); mutate_state(st); st = seal_state(st)
        rq = deepcopy(delegated_req); rq["authority_state_id"] = st["authority_state_id"]
        record(case_id, "delegation", False, e.evaluate(st, rq)["authorized"])

    # Request structural/reference attacks.
    structural_cases: list[tuple[str, Callable[[dict[str, Any]], None]]] = []
    structural_cases.append(("E21-duplicate-ref-id", lambda r: r["references"].append(deepcopy(r["references"][0]))))
    structural_cases.append(("E22-bad-ref-identity", lambda r: r["references"][0].__setitem__("identity_sha256", "sha256:" + "5" * 64)))
    structural_cases.append(("E23-missing-target-ref", lambda r: r["references"].pop(0)))
    structural_cases.append(("E24-duplicate-support-id", lambda r: r["supporting_artifacts"].append(deepcopy(r["supporting_artifacts"][0]))))
    structural_cases.append(("E25-support-unknown-ref", lambda r: r["supporting_artifacts"][0].__setitem__("ref_id", "missing")))
    structural_cases.append(("E26-unknown-request-field", lambda r: r.__setitem__("surprise", True)))
    structural_cases.append(("E27-forbidden-resolved-field", lambda r: r.__setitem__("resolved_conflict_ids", ["c1"])))
    for case_id, mutator in structural_cases:
        rq = deepcopy(human_req); mutator(rq)
        record(case_id, "request-shape", False, e.evaluate(human_state, rq)["authorized"])

    # Blockers and preservation.
    irrelevant_conflict = [{"id": "c-irrelevant", "relevant": False, "status": "unresolved"}]
    irrelevant_residue = [{"id": "r-irrelevant", "relevant": False, "status": "contested"}]
    rq = request(state=human_state, subject=human, domain="knowledge", operation="knowledge.cite_as_evidence", scope="knowledge", target_class="knowledge", target_ref=href, dref=dref, conflicts=irrelevant_conflict, residues=irrelevant_residue)
    rr = e.evaluate(human_state, rq)
    record("P04-irrelevant-blockers", "blockers", True, rr["authorized"])
    record("P05-irrelevant-blockers-preserved", "blockers", {"conflicts": irrelevant_conflict, "residues": irrelevant_residue}, {"conflicts": rr["preserved"]["conflicts"], "residues": rr["preserved"]["residues"]})

    blocker_cases = [
        ("E28-relevant-unresolved-conflict", [{"id": "c1", "relevant": True, "status": "unresolved"}], []),
        ("E29-relevant-contested-conflict", [{"id": "c1", "relevant": True, "status": "contested"}], []),
        ("E30-relevant-unresolved-residue", [], [{"id": "r1", "relevant": True, "status": "unresolved"}]),
        ("E31-relevant-contested-residue", [], [{"id": "r1", "relevant": True, "status": "contested"}]),
    ]
    for case_id, conflicts, residues in blocker_cases:
        rq = request(state=human_state, subject=human, domain="knowledge", operation="knowledge.cite_as_evidence", scope="knowledge", target_class="knowledge", target_ref=href, dref=dref, conflicts=conflicts, residues=residues)
        record(case_id, "blockers", False, e.evaluate(human_state, rq)["authorized"])

    rq = deepcopy(human_req); rq["conflicts"] = [{"id": "dup", "relevant": True, "status": "unresolved"}, {"id": "dup", "relevant": True, "status": "contested"}]
    record("E32-duplicate-conflict-id", "request-shape", False, e.evaluate(human_state, rq)["authorized"])
    rq = deepcopy(human_req); rq["residues"] = [{"id": "dup", "relevant": True, "status": "unresolved"}, {"id": "dup", "relevant": True, "status": "contested"}]
    record("E33-duplicate-residue-id", "request-shape", False, e.evaluate(human_state, rq)["authorized"])

    # Machine profile positive.
    machine = "machine:service-1"
    intent = execution_intent(citation_clear, machine)
    iref = intent_ref(intent)
    machine_state = root_state(subject=machine, domain="execution", operation="execute", scope="single-intent", target_class="execution-intent", target_ref=iref["identity_sha256"])
    machine_req = request(state=machine_state, subject=machine, domain="execution", operation="execute", scope="single-intent", target_class="execution-intent", target_ref=iref, dref=dref)
    machine_receipt = e.evaluate(machine_state, machine_req)
    record("X01-machine-positive", "machine", True, strong_machine_accept(citation_clear, citation_expected, machine_state, machine_req, intent))

    # ExecutionIntent key ordering invariance.
    reordered = {key: deepcopy(intent[key]) for key in reversed(list(intent.keys()))}
    record("M02-intent-key-order-invariance", "metamorphic", intent_identity(intent), intent_identity(reordered))

    # Every authority-relevant intent mutation changes immutable identity and stale authority no longer applies.
    intent_mutations: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
        ("X02-script-digest", lambda x: x.__setitem__("executable_sha256", "sha256:" + "b" * 64)),
        ("X03-entry-point", lambda x: x.__setitem__("entry_point", "other-entry")),
        ("X04-arguments", lambda x: x.__setitem__("arguments", ["--mode", "other"])),
        ("X05-input", lambda x: x.__setitem__("input_identities", ["sha256:" + "c" * 64])),
        ("X06-environment", lambda x: x.__setitem__("environment", {"network": "enabled", "workspace": "ephemeral"})),
        ("X07-executor", lambda x: x.__setitem__("executor_subject", "machine:service-2")),
        ("X08-requested-operation", lambda x: x.__setitem__("requested_operation", "knowledge.add_verified_tag")),
        ("X09-effect-params", lambda x: x.__setitem__("requested_effect_params", {"scope": "claim"})),
        ("X10-decision-identity", lambda x: x.__setitem__("decision_identity", semantic_identity(source_clear))),
        ("X11-decision-target", lambda x: x.__setitem__("decision_target", deepcopy(source_clear["target"]))),
    ]
    for case_id, mutator in intent_mutations:
        x = deepcopy(intent); mutator(x)
        changed = intent_identity(x) != intent_identity(intent)
        record(case_id + "-identity-flips", "execution-intent", True, changed)
        # Reusing the stale request/authority with the mutated intent must fail profile binding.
        record(case_id + "-stale-authority-rejects", "execution-intent", False, machine_bundle_valid(citation_clear, citation_expected, machine_req, x))

    # Receipt replay / cross-track confusion.
    mutated_req = deepcopy(human_req); mutated_req["request_id"] = "request-mutated"
    record("R03-mutated-request-replay", "receipt", False, verify_receipt_for_request(human_receipt, mutated_req))
    record("R04-human-receipt-machine-request", "receipt", False, verify_receipt_for_request(human_receipt, machine_req))
    record("R05-machine-receipt-human-request", "receipt", False, verify_receipt_for_request(machine_receipt, human_req))

    target_changed = deepcopy(human_req); target_changed["jurisdiction"]["target_ref"] = other_target["identity_sha256"]; target_changed["references"].append(other_target)
    record("R06-target-change-replay", "receipt", False, verify_receipt_for_request(human_receipt, target_changed))
    op_changed = deepcopy(human_req); op_changed["jurisdiction"]["operation"] = "knowledge.add_verified_tag"
    record("R07-operation-change-replay", "receipt", False, verify_receipt_for_request(human_receipt, op_changed))

    # TOCTOU: old receipt remains historical, but current state revocation blocks point-of-use.
    old_machine_receipt = deepcopy(machine_receipt)
    current_revoked = deepcopy(machine_state)
    current_revoked["records"][0]["revoked_at"] = "2026-09-02T18:00:00Z"
    current_revoked = seal_state(current_revoked)
    record("T01-old-receipt-historical-still-self-consistent", "toctou", True, verify_receipt_for_request(old_machine_receipt, machine_req))
    record("T02-current-revocation-blocks-machine-gate", "toctou", False, strong_machine_accept(citation_clear, citation_expected, current_revoked, machine_req, intent))

    changed_state_req = deepcopy(machine_req); changed_state_req["authority_state_id"] = current_revoked["authority_state_id"]
    record("R08-old-receipt-new-state-request", "receipt", False, verify_receipt_for_request(old_machine_receipt, changed_state_req))

    # Weak control discrimination. These are intentionally unsafe strategies.
    weak_results: dict[str, dict[str, Any]] = {}

    def weak_clear_is_authorization(decision: dict[str, Any]) -> bool:
        return decision.get("evaluation") == {"state": "completed", "disposition": "clear"}

    def weak_receipt_only(receipt: dict[str, Any]) -> bool:
        return receipt.get("authorized") is True

    def weak_subject_blind(receipt: dict[str, Any], _request: dict[str, Any]) -> bool:
        return receipt.get("authorized") is True

    def weak_target_blind(receipt: dict[str, Any], _request: dict[str, Any]) -> bool:
        return receipt.get("authorized") is True

    def weak_support_laundering(decision: dict[str, Any], req: dict[str, Any]) -> bool:
        return adapter_ready(decision, citation_expected) and bool(req.get("supporting_artifacts"))

    weak_attacks = {
        "CLEAR-is-authorization": [
            ("no-authority-state", weak_clear_is_authorization(citation_clear), False),
        ],
        "receipt-only-machine-gate": [
            ("revoked-after-old-receipt", weak_receipt_only(old_machine_receipt), False),
        ],
        "subject-blind-consumer": [
            ("human-receipt-for-machine", weak_subject_blind(human_receipt, machine_req), False),
        ],
        "target-blind-consumer": [
            ("human-receipt-target-swap", weak_target_blind(human_receipt, target_changed), False),
        ],
        "supporting-artifact-laundering": [
            ("decision-support-without-authority", weak_support_laundering(citation_clear, human_req), False),
        ],
    }
    for name, attacks in weak_attacks.items():
        false_permits = [attack_id for attack_id, observed, expected in attacks if observed is True and expected is False]
        weak_results[name] = {"false_permits": false_permits, "caught": len(false_permits) > 0}
        record("W-" + name, "weak-control", True, weak_results[name]["caught"], note=",".join(false_permits))

    # Source-audit effect normalization/default sanity so the adapter logic is not accidentally citation-only.
    src_effect = validate_effect(source_clear["effect"])
    record("D16-source-audit-default-normalized", "contract-d", {"type": "knowledge.add_verified_tag", "version": "1", "params": {"scope": "claim"}}, src_effect)
    record("D17-source-audit-exact", "contract-d", "candidate_for_authorization", d_outcome(source_clear, source_expected))

    failures = [row for row in rows if not row["pass"]]
    result = {
        "experiment": "contract-d-to-e-authorization-consumer-pressure-20260902",
        "status": "PASS" if not failures else "FAIL",
        "scientific_target_reached": True,
        "case_count": len(rows),
        "pass_count": sum(1 for row in rows if row["pass"]),
        "fail_count": len(failures),
        "failed_case_ids": [row["id"] for row in failures],
        "weak_controls": weak_results,
        "observed_bounds": {
            "contract_e_candidate": "research-only candidate RC1",
            "production_authorization_established": False,
            "execution_performed": False,
            "root_authority_legitimacy_established": False,
        },
        "rows": rows,
    }
    out_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("status", "case_count", "pass_count", "fail_count", "failed_case_ids")}))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
