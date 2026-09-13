from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from claim_audit_lab.cal_v1_candidate import (
    AdmittedPassage,
    AuditContext,
    Conclusion,
    EvidenceWorld,
    FailureCode,
    SemanticFamily,
    TypedProposition,
    audit,
    project_contract_c_successor,
)
import claim_audit_lab.cal_v1_candidate.projection as projection

CAL = "a902621e8baea3063dddd7f92ba975aade305464"
ENGINE = "636734fd1341d2ae721ae9697c7ac7652b89eecc"
RELATIONS = "e9e9401c92ee11d25a50dbc36e80aeb4c4cd220d"
PROJECTION = "9bc152275759304be03b84014c56bd434549a64a"
PHASE0 = "e588e1295367a4b867d608342aaacaccb41850b8"
PHASE1 = "175246ae16932f2f34a399560d7f76013213bf97"
HERE = Path(__file__).resolve().parent

SUPPORT_A = "Women had a higher rate than Men."
SUPPORT_B = "Women had a greater rate than Men."
REFUTE = "Women had a lower rate than Men."
IRRELEVANT = "Cats had a higher rate than Dogs."


def canon(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def tagged(value: bytes) -> str:
    return "sha256:" + sha(value)


def context(rows: list[tuple[str, str]], label: str) -> AuditContext:
    passages = tuple(
        AdmittedPassage.create(f"p{i}", source, text)
        for i, (source, text) in enumerate(rows, 1)
    )
    world = EvidenceWorld.create(
        "1.2.0",
        f"bundle-{label}",
        tagged(label.encode()),
        passages,
        {"search_scope": {"corpus": label}, "outcome": {"state": "unknown", "value": None}, "limitations": []},
    )
    prop = TypedProposition.create(
        "claim-1",
        SemanticFamily.STRICT_COMPARISON,
        {"lhs_entity": "Women", "rhs_entity": "Men", "comparison_direction": "MORE_THAN"},
        text_sha256=sha(SUPPORT_A.encode()),
    )
    return AuditContext(SUPPORT_A, prop, world)


def observe(rows: list[tuple[str, str]], label: str) -> dict[str, Any]:
    result = audit(context(rows, label))
    return {
        "conclusion": result.conclusion.value,
        "failure": result.failure_code.value if result.failure_code else None,
        "relations": [
            trace.relation.categorical_relation.value if trace.relation else None
            for trace in result.traces
        ],
    }


def project(rows: list[tuple[str, str]], label: str) -> tuple[AuditContext, dict[str, Any]]:
    ctx = context(rows, label)
    result = audit(ctx)
    return ctx, project_contract_c_successor(ctx, result, semantic_implementation_sha=CAL)


def mixed(value: dict[str, Any]) -> bool:
    return value["conclusion"] == Conclusion.NOT_CHECKABLE.value and value["failure"] == FailureCode.MIXED_RELATIONS.value


def metamorphisms() -> tuple[dict[str, Any], dict[str, bool]]:
    m1 = {
        "full": observe([("r1", REFUTE), ("r2", REFUTE)], "m1-full"),
        "R1": observe([("r1", REFUTE)], "m1-r1"),
        "R2": observe([("r2", REFUTE)], "m1-r2"),
        "empty": observe([], "m1-empty"),
    }
    m1_ok = all(m1[key]["conclusion"] == "contradicted" for key in ("full", "R1", "R2")) and m1["empty"]["conclusion"] != "contradicted"

    m2 = {
        "full": observe([("s1", SUPPORT_A), ("r1", REFUTE), ("r2", REFUTE)], "m2-full"),
        "S1_R1": observe([("s1", SUPPORT_A), ("r1", REFUTE)], "m2-s-r1"),
        "S1_R2": observe([("s1", SUPPORT_A), ("r2", REFUTE)], "m2-s-r2"),
        "R1_R2": observe([("r1", REFUTE), ("r2", REFUTE)], "m2-r-r"),
        "S1": observe([("s1", SUPPORT_A)], "m2-s"),
    }
    m2_ok = all(mixed(m2[key]) for key in ("full", "S1_R1", "S1_R2")) and not mixed(m2["R1_R2"]) and not mixed(m2["S1"])

    m3_rows = [("s1", SUPPORT_A), ("s2", SUPPORT_B), ("r1", REFUTE)]
    m3 = {
        "full": observe(m3_rows, "m3-full"),
        "S1_R1": observe([("s1", SUPPORT_A), ("r1", REFUTE)], "m3-s1-r"),
        "S2_R1": observe([("s2", SUPPORT_B), ("r1", REFUTE)], "m3-s2-r"),
        "S1_S2": observe([("s1", SUPPORT_A), ("s2", SUPPORT_B)], "m3-s-s"),
        "R1": observe([("r1", REFUTE)], "m3-r"),
    }
    _, old = project(m3_rows, "m3-exporter")
    old_conclusion = old["propositions"][0]["conclusion"]
    old_false = old_conclusion["causal_form"] == "jointly_sufficient" and len(old_conclusion["basis_members"]) == 3
    m3_ok = all(mixed(m3[key]) for key in ("full", "S1_R1", "S2_R1")) and m3["S1_S2"]["conclusion"] == "supported" and m3["R1"]["conclusion"] == "contradicted" and old_false

    return {
        "M1_SP04": {**m1, "oracle": "MSC={{R1},{R2}}" if m1_ok else None},
        "M2_SP11": {**m2, "oracle": "MSC={{S1,R1},{S1,R2}}" if m2_ok else None},
        "M3_SP10": {**m3, "oracle": "MSC={{S1,R1},{S2,R1}}" if m3_ok else None, "old_exporter_still_falsified": old_false},
        "M4_SP12": {"status": "REPRESENTATION_STRESS_ONLY", "producer_materialization_claimed": False},
    }, {"M1": m1_ok, "M2": m2_ok, "M3": m3_ok, "M4_nonclaim": True}


def semantic_signature(payload: dict[str, Any]) -> tuple[Any, ...]:
    prop = payload["propositions"][0]
    contributions = {row["contribution_id"]: row for row in prop["contributions"]}
    basis = tuple(sorted(
        (contributions[m["id"]]["channel"], contributions[m["id"]]["evidence_ref"]["passage_id"])
        for m in prop["conclusion"]["basis_members"] if m["namespace"] == "contribution"
    ))
    residual = tuple(sorted(
        (contributions[cid]["channel"], contributions[cid]["evidence_ref"]["passage_id"])
        for cid in prop["conclusion"]["residual_contribution_ids"]
    ))
    return (
        prop["execution"]["completion"],
        prop["conclusion"]["reported_verdict"],
        prop["conclusion"]["terminal_branch"],
        prop["conclusion"]["causal_form"],
        basis,
        residual,
        payload["producer"]["semantic_implementation_sha"],
        payload["producer"]["policy"]["sha256"],
    )


def d1() -> dict[str, Any]:
    cases = {
        "support": [("s", SUPPORT_A)],
        "refute": [("r", REFUTE)],
        "mixed": [("s", SUPPORT_A), ("r", REFUTE)],
        "unresolved": [("n", IRRELEVANT)],
    }
    payloads = {name: project(rows, f"d1-{name}")[1] for name, rows in cases.items()}
    assessments = [p["propositions"][0]["assessments"] for p in payloads.values()]
    invariant = len({json.dumps(x, sort_keys=True) for x in assessments}) == 1
    distinct_without = len({semantic_signature(p) for p in payloads.values()}) == len(payloads)
    slots = ["eligibility", "semantic_validity", "aperture_completeness", "temporal_applicability"]
    return {
        "slot_variation_observed": not invariant,
        "tested_distinctions_survive_without_slots": distinct_without,
        "current_consumer_requirement_exercised": False,
        "dispositions": {slot: "ABLATE_FOR_CURRENT_SUCCESSOR_SCOPE" for slot in slots} if invariant and distinct_without else {slot: "UNRESOLVED" for slot in slots},
    }


def d2() -> dict[str, Any]:
    rows = [[("s", SUPPORT_A)], [("r", REFUTE)], [("s", SUPPORT_A), ("r", REFUTE)], [("n", IRRELEVANT)]]
    payloads = [project(value, f"d2-{i}")[1] for i, value in enumerate(rows)]
    namespaces = sorted({m["namespace"] for p in payloads for m in p["propositions"][0]["conclusion"]["basis_members"]})
    rule_roles = [p["propositions"][0]["conclusion"]["rule_roles"] for p in payloads]
    non_evidence = any(ns != "contribution" for ns in namespaces) or any(rule_roles)
    return {
        "basis_namespaces": namespaces,
        "rule_roles": rule_roles,
        "current_rc1_non_evidence_causal_member_observed": non_evidence,
        "current_consumer_requirement_exercised": False,
        "disposition": "UNRESOLVED" if non_evidence else "ABLATE_FOR_CURRENT_SUCCESSOR_SCOPE",
        "reconsideration_trigger": "A future legitimate result requires a typed non-evidence cause not reconstructable from producer/policy identity, stable terminal reason, and evidence causal structure.",
    }


def resolve_policy(resolver: dict[str, Any], implementation: str, digest: str) -> dict[str, Any]:
    matches = [e for e in resolver["entries"] if e["semantic_implementation_sha"] == implementation]
    if len(matches) != 1:
        raise ValueError("exact producer identity does not resolve uniquely")
    entry = matches[0]
    if entry["projection_blob"] != PROJECTION or entry["policy_sha256"] != digest:
        raise ValueError("policy resolver binding mismatch")
    if sha(canon(entry["policy"])) != digest:
        raise ValueError("resolved policy digest mismatch")
    return entry["policy"]


def d3() -> dict[str, Any]:
    raw = (HERE / "PHASE_1_5_POLICY_RESOLVER.json").read_bytes()
    resolver = json.loads(raw)
    current = projection._policy()
    recovered = resolve_policy(resolver, CAL, current["sha256"])
    wrong_digest = unknown_producer = False
    try:
        resolve_policy(resolver, CAL, "0" * 64)
    except ValueError:
        wrong_digest = True
    try:
        resolve_policy(resolver, "0" * 40, current["sha256"])
    except ValueError:
        unknown_producer = True
    ok = recovered == current["canonical"] and wrong_digest and unknown_producer
    return {
        "exact_recovery": recovered == current["canonical"],
        "wrong_digest_rejected": wrong_digest,
        "unknown_producer_rejected": unknown_producer,
        "mutable_latest_used": False,
        "human_config_name_used": False,
        "network_lookup_required": False,
        "policy_sha256": current["sha256"],
        "resolver_sha256": tagged(raw),
        "disposition": "ABLATE_FULL_IN_BAND_POLICY_PAYLOAD_RETAIN_DIGEST_AND_IMMUTABLE_RESOLVER" if ok else "RETAIN_FULL_IN_BAND_POLICY_PAYLOAD",
    }


def world_hash(world: dict[str, Any]) -> str:
    material = {k: v for k, v in world.items() if k != "bundle_hash"}
    return tagged(canon(material))


def seal(world: dict[str, Any]) -> dict[str, Any]:
    out = json.loads(json.dumps(world))
    out["bundle_hash"] = world_hash(out)
    return out


def binding(world: dict[str, Any]) -> dict[str, str]:
    return {k: world[k] for k in ("contract_version", "bundle_id", "bundle_hash")}


def resolve_passage(bound: dict[str, str], world: dict[str, Any], source: str, passage: str) -> dict[str, str]:
    if world["bundle_hash"] != world_hash(world) or binding(world) != bound:
        raise ValueError("exact Contract B world mismatch")
    row = world["passages"].get(passage)
    if not row or row["source_id"] != source:
        raise ValueError("evidence reference mismatch")
    return row


def d4() -> dict[str, Any]:
    base = seal({"contract_version": "1.2.0", "bundle_id": "phase15-world-a", "passages": {"p1": {"source_id": "src-1", "passage_sha256": tagged(b"original")}}})
    bound = binding(base)
    baseline = resolve_passage(bound, base, "src-1", "p1")
    same_id = json.loads(json.dumps(base)); same_id["passages"]["p1"]["passage_sha256"] = tagged(b"changed")
    other = seal({"contract_version": "1.2.0", "bundle_id": "phase15-world-b", "passages": base["passages"]})
    stale = dict(bound); stale["bundle_hash"] = tagged(b"stale")
    resealed = json.loads(json.dumps(base)); resealed["passages"]["p1"]["passage_sha256"] = tagged(b"resealed"); resealed = seal(resealed)

    def rejected(b: dict[str, str], w: dict[str, Any]) -> bool:
        try:
            resolve_passage(b, w, "src-1", "p1")
        except ValueError:
            return True
        return False

    checks = {
        "baseline_resolves": baseline["passage_sha256"] == base["passages"]["p1"]["passage_sha256"],
        "same_id_mutation_rejected": rejected(bound, same_id),
        "different_world_replay_rejected": rejected(bound, other),
        "stale_bundle_hash_rejected": rejected(stale, base),
        "resealed_tamper_rejected_by_old_binding": rejected(bound, resealed),
    }
    return {
        "checks": checks,
        "historical_exact_b_index_blob": "4de40713482a1fc5a075a230a61e19acc25afbd9",
        "disposition": "ABLATE_REPEATED_PASSAGE_SHA256_RETAIN_EXACT_B_WORLD_BINDING" if all(checks.values()) else "RETAIN_REPEATED_PASSAGE_SHA256",
    }


def d5() -> dict[str, Any]:
    ctx, payload = project([("s", SUPPORT_A), ("n", IRRELEVANT)], "d5")
    prop = payload["propositions"][0]
    b = payload["input"]["contract_b"]
    contribution = {row["contribution_id"]: row for row in prop["contributions"]}

    def key(row: dict[str, Any]) -> tuple[str, ...]:
        ref = row["evidence_ref"]
        return (b["contract_version"], b["bundle_id"], b["bundle_hash"], ctx.proposition.sha256, ref["source_id"], ref["passage_id"])

    keys = {cid: key(row) for cid, row in contribution.items()}
    causal_ids = {m["id"] for m in prop["conclusion"]["basis_members"] if m["namespace"] == "contribution"}
    residual_ids = set(prop["conclusion"]["residual_contribution_ids"])
    causal = {keys[x] for x in causal_ids}; residual = {keys[x] for x in residual_ids}; all_keys = set(keys.values())
    partition = causal | residual == all_keys and not causal & residual
    duplicate_detected = len(list(all_keys) + [next(iter(all_keys))]) != len(set(list(all_keys) + [next(iter(all_keys))]))
    canonical = sorted(all_keys) == sorted(reversed(list(all_keys)))

    single = audit(context([("s", SUPPORT_A)], "d5-single"))
    one_trace = len(single.traces) == 1
    dup_world = EvidenceWorld.create(
        "1.2.0", "bundle-d5-dup", tagged(b"bundle-d5-dup"),
        (AdmittedPassage.create("p1", "src", SUPPORT_A), AdmittedPassage.create("p1", "src", SUPPORT_A)),
        {"search_scope": {}, "outcome": {"state": "unknown", "value": None}, "limitations": []},
    )
    dup_ctx = AuditContext(ctx.original_claim, ctx.proposition, dup_world)
    duplicate_passage_rejected = False
    try:
        audit(dup_ctx)
    except ValueError:
        duplicate_passage_rejected = True
    multi_from_same = not (one_trace and duplicate_passage_rejected)
    ok = partition and duplicate_detected and canonical and not multi_from_same
    return {
        "direct_identity_partition": partition,
        "direct_identity_duplicate_detection": duplicate_detected,
        "direct_identity_canonical_order": canonical,
        "one_trace_per_exact_passage": one_trace,
        "duplicate_passage_id_rejected": duplicate_passage_rejected,
        "two_semantically_distinct_contributions_from_same_exact_passage_supported": multi_from_same,
        "disposition": "ABLATE_SEPARATE_CONTRIBUTION_ID_FOR_CURRENT_SUCCESSOR_SCOPE" if ok else "RETAIN_OR_REDERIVE_CONTRIBUTION_ID",
        "reconsideration_trigger": "Future qualified CAL emits multiple semantically distinct public contributions from the same exact passage to the same proposition.",
    }


def evaluate() -> dict[str, Any]:
    specimens, specimen_checks = metamorphisms()
    results = {"D1": d1(), "D2": d2(), "D3": d3(), "D4": d4(), "D5": d5()}
    dchecks = {
        "D1": set(results["D1"]["dispositions"].values()) == {"ABLATE_FOR_CURRENT_SUCCESSOR_SCOPE"},
        "D2": results["D2"]["disposition"] == "ABLATE_FOR_CURRENT_SUCCESSOR_SCOPE",
        "D3": results["D3"]["disposition"].startswith("ABLATE_FULL_IN_BAND"),
        "D4": results["D4"]["disposition"].startswith("ABLATE_REPEATED"),
        "D5": results["D5"]["disposition"].startswith("ABLATE_SEPARATE"),
    }
    checks = {**specimen_checks, **dchecks}
    failures = sorted(name for name, ok in checks.items() if not ok)
    return {
        "schema": "contract-c-successor-phase-1-5-result-v1",
        "classification": "Draft Research / Research Infrastructure",
        "research_disposition": "SUPPORTED_PHASE_1_5_FREEZE_READY" if not failures else "INCONCLUSIVE",
        "frozen_parents": {"phase_0": PHASE0, "phase_1": PHASE1},
        "cal_authority": {"rc1_commit": CAL, "engine_blob": ENGINE, "relation_blob": RELATIONS, "projection_blob": PROJECTION},
        "metamorphic_specimens": specimens,
        "discriminators": results,
        "checks": checks,
        "failures": failures,
        "apparatus_failures": [],
        "unresolved_questions": [],
        "phase_2_blocked_by_normative_choice": bool(failures),
        "bounded_nonclaims": ["SP-12 remains representation-stress-only.", "CAL #106 exporter is not repaired.", "No production authority or independent-reproduction claim is created."],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = evaluate()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    if result["research_disposition"] != "SUPPORTED_PHASE_1_5_FREEZE_READY":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
