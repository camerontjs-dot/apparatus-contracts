from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "_subjects" / "v3" / "research" / "cal-pipeline-v1-contract-authority-freeze-20260919" / "SLICE_MANIFEST_V3.json"

EXPECTED = {
    "cal": "ddaf94551e38663920593cab89f9c60d43c1555f",
    "cal_tree": "1677a1de987a594f4ee8d2670d56943c5f189fbd",
    "contract_c": "c5b1d757f3a0ad4f6e2c3f6dbdc2dd2d3c1403ec",
    "consumer": "12e7e640b229619501960b1b89cf4716d8d985b3",
    "decision": "6cdb59c2ba41779ac954af56dd077574ba090013",
    "decision_tree": "d4b75b63462451b5c258a13abf9ce2beb9e78098",
    "eb": "4e1f6fe00e7c350b28f52bfea14f1f8988847884",
    "b": "c314e53bd91c0736aa4370a364673b069aceb43e",
    "d": "298a1a0f7b7b6d7712e11200d04faec3e1ca169b",
    "composition_result": "sha256:2ef133c504cd33bf5b9912acb06e154b43d7060b967dd4230081d4a8ad4f9753",
    "composition_artifact": "sha256:bab1e7522a69e404208d9e65d9edae89d860827ef08fd3da1ad01813554b0841",
    "cal_artifact": "sha256:a094195f74c803047097d2a4e446548a00060ba8d255d012e14cbdcd71e26eea",
    "consumer_artifact": "sha256:74dc44f76dabe0b5ae69dd6e00eab66d02f7936ed41d61b2f49d67c94bf57f9f",
    "decision_artifact": "sha256:22e5b4da1d80c1452f4eb33062c61801568fffac1dfdb27ed744f491dfe5209b",
}

STAGES = [
    "contract_a",
    "evidence_bundler",
    "contract_b",
    "cal_slice_2",
    "parent_bound_contract_c",
    "independent_contract_c_consumer",
    "decision_parent_bound_ingress",
    "contract_d",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def chain_map(m: dict[str, Any]) -> dict[str, dict[str, Any]]:
    chain = m["controlled_local_composition_lane"]["chain"]
    require([x["stage"] for x in chain] == STAGES, "controlled chain stage/order mismatch")
    require(len({x["stage"] for x in chain}) == len(STAGES), "duplicate chain stage")
    return {x["stage"]: x for x in chain}


def validate(m: dict[str, Any]) -> None:
    require(m["schema_version"] == "apparatus-contracts-local-pipeline-authority-slice/3", "schema")
    require(m["status"] == "QUALIFIED_FOR_CONTROLLED_LOCAL_PIPELINE_HANDOFF_V3", "status")
    require(m["authority_lane"]["status"] == "unchanged", "authority lane status")
    require(
        m["authority_lane"]["supported_authority_chain"]
        == "Contract A 2.0.0 -> Contract B 1.2.0 -> Contract C 1.0.0 -> Contract D 1.0.0",
        "released authority lane changed",
    )
    require(m["authority_lane"]["contract_c_canonical_discovery"] == "1.0.0", "C canonical discovery")
    require(m["contracts"]["contract_e"]["included"] is False, "Contract E included")
    require(
        m["supersedes_for_local_handoff"]["prior_v2_pressure"]["disposition"]
        == "FALSIFIED_V2_SUCCESSOR_CURRENTNESS",
        "v2 falsification erased",
    )

    lane = m["controlled_local_composition_lane"]
    require(lane["admitted_to_released_authority_lane"] is False, "controlled lane promoted")
    require(
        lane["terminal_disposition"] == "SUPPORTED_THREE_CASE_PRODUCTION_SHAPED_COMPOSITION",
        "composition disposition drift",
    )

    cal = lane["cal_slice_2"]
    require(cal["exact_commit"] == EXPECTED["cal"], "CAL commit")
    require(cal["exact_tree"] == EXPECTED["cal_tree"], "CAL tree")
    require(
        cal["disposition"] == "QUALIFIED_FOR_CONTROLLED_LOCAL_PIPELINE_PARENT_BOUND_RUNS",
        "CAL disposition",
    )
    require(cal["artifact_digest"] == EXPECTED["cal_artifact"], "CAL artifact digest")
    require(
        "trusted/prevalidated" in cal["boundary"],
        "trusted/prevalidated-target boundary removed",
    )

    c = lane["parent_bound_contract_c"]
    require(c["freeze_commit"] == EXPECTED["contract_c"], "Contract C freeze")
    require(c["semver_assigned"] is False, "Contract C SemVer assigned")
    require(c["production_release_authorized"] is False, "Contract C released")

    consumer = lane["independent_consumer"]
    require(consumer["freeze_commit"] == EXPECTED["consumer"], "consumer commit")
    require(
        consumer["disposition"] == "SUPPORTED_INDEPENDENT_CONSUMER_CONFORMANCE_RC1",
        "consumer disposition",
    )
    require(consumer["artifact_digest"] == EXPECTED["consumer_artifact"], "consumer artifact digest")
    require(consumer["false_accepts"] == 0, "consumer false accept")

    de = lane["decision_candidate"]
    require(de["exact_commit"] == EXPECTED["decision"], "Decision commit")
    require(de["exact_tree"] == EXPECTED["decision_tree"], "Decision tree")
    require(
        de["disposition"]
        == "QUALIFIED_ADDITIVE_PARENT_BOUND_INGRESS_FOR_CONTROLLED_LOCAL_PIPELINE_RUNS",
        "Decision disposition",
    )
    require(de["artifact_digest"] == EXPECTED["decision_artifact"], "Decision artifact digest")
    require(de["released_successor_version_assigned"] is False, "Decision released")

    composition = lane["composition_qualification"]
    require(
        composition["disposition"] == "SUPPORTED_THREE_CASE_PRODUCTION_SHAPED_COMPOSITION",
        "composition qualification disposition",
    )
    require(composition["result_sha256"] == EXPECTED["composition_result"], "composition result digest")
    require(composition["artifact_digest"] == EXPECTED["composition_artifact"], "composition artifact digest")
    obs = composition["observations"]
    require(obs["deterministic_PIPE01_replay"] is True, "determinism cleared")
    require(
        obs["cross_run_native_child_replay"] == "rejected before Contract D output",
        "cross-run replay acceptance",
    )
    require(obs["cross_run_false_accepts"] == 0, "cross-run false accept")
    require(obs["authorization_performed"] is False, "Authorization performed")
    require(obs["execution_performed"] is False, "execution performed")

    posture = lane["release_posture"]
    require(posture["contract_c_canonical_discovery"] == "1.0.0", "posture C canonical")
    require(posture["parent_bound_contract_c_semver_assigned"] is False, "posture C SemVer")
    require(posture["parent_bound_contract_c_released"] is False, "posture C release")
    require(posture["decision_successor_released"] is False, "posture Decision release")
    require(posture["contract_e_included"] is False, "posture E")
    require(posture["authorization_included"] is False, "posture Authorization")
    require(posture["execution_included"] is False, "posture execution")

    cm = chain_map(m)
    require(cm["evidence_bundler"]["commit"] == EXPECTED["eb"], "EB chain subject")
    require(cm["contract_b"]["commit"] == EXPECTED["b"], "B chain subject")
    require(cm["cal_slice_2"]["commit"] == EXPECTED["cal"], "CAL chain subject")
    require(cm["cal_slice_2"]["tree"] == EXPECTED["cal_tree"], "CAL chain tree")
    require(cm["parent_bound_contract_c"]["commit"] == EXPECTED["contract_c"], "C chain subject")
    require(cm["independent_contract_c_consumer"]["commit"] == EXPECTED["consumer"], "consumer chain subject")
    require(cm["decision_parent_bound_ingress"]["commit"] == EXPECTED["decision"], "Decision chain subject")
    require(cm["decision_parent_bound_ingress"]["tree"] == EXPECTED["decision_tree"], "Decision chain tree")
    require(cm["contract_d"]["commit"] == EXPECTED["d"], "D chain subject")
    require(cm["contract_a"]["repository"] == "camerontjs-dot/apparatus-contracts", "A repo")
    require(cm["evidence_bundler"]["repository"] == "camerontjs-dot/evidence-bundler", "EB repo")
    require(cm["cal_slice_2"]["repository"] == "camerontjs-dot/claim-audit-lab", "CAL repo")
    require(cm["independent_contract_c_consumer"]["repository"] == "camerontjs-dot/research-scaffold-harness", "consumer repo")
    require(cm["decision_parent_bound_ingress"]["repository"] == "camerontjs-dot/decision-engine", "Decision repo")
    require(cm["cal_slice_2"]["authority_class"] == "qualified controlled candidate", "CAL authority class")
    require(cm["decision_parent_bound_ingress"]["authority_class"] == "qualified controlled candidate", "Decision authority class")


def mutate(m: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    out: list[tuple[str, dict[str, Any]]] = []

    def add(name: str, fn) -> None:
        x = copy.deepcopy(m)
        fn(x)
        out.append((name, x))

    add("released_lane_to_parent_bound_c", lambda x: x["authority_lane"].__setitem__(
        "supported_authority_chain",
        "Contract A 2.0.0 -> Contract B 1.2.0 -> parent-bound Contract C -> Contract D 1.0.0",
    ))
    add("local_lane_promoted", lambda x: x["controlled_local_composition_lane"].__setitem__("admitted_to_released_authority_lane", True))
    add("c2_canonicalized", lambda x: x["authority_lane"].__setitem__("contract_c_canonical_discovery", "2.0.0"))
    add("parent_c_semver", lambda x: x["controlled_local_composition_lane"]["parent_bound_contract_c"].__setitem__("semver_assigned", True))
    add("parent_c_released", lambda x: x["controlled_local_composition_lane"]["parent_bound_contract_c"].__setitem__("production_release_authorized", True))
    add("decision_released", lambda x: x["controlled_local_composition_lane"]["decision_candidate"].__setitem__("released_successor_version_assigned", True))
    add("contract_e_inserted", lambda x: x["contracts"]["contract_e"].__setitem__("included", True))
    add("authorization_inserted", lambda x: x["controlled_local_composition_lane"]["release_posture"].__setitem__("authorization_included", True))
    add("execution_inserted", lambda x: x["controlled_local_composition_lane"]["release_posture"].__setitem__("execution_included", True))
    add("cal_commit_substitution", lambda x: x["controlled_local_composition_lane"]["cal_slice_2"].__setitem__("exact_commit", "0" * 40))
    add("cal_tree_substitution", lambda x: x["controlled_local_composition_lane"]["cal_slice_2"].__setitem__("exact_tree", "0" * 40))
    add("c_freeze_substitution", lambda x: x["controlled_local_composition_lane"]["parent_bound_contract_c"].__setitem__("freeze_commit", "0" * 40))
    add("consumer_substitution", lambda x: x["controlled_local_composition_lane"]["independent_consumer"].__setitem__("freeze_commit", "0" * 40))
    add("decision_commit_substitution", lambda x: x["controlled_local_composition_lane"]["decision_candidate"].__setitem__("exact_commit", "0" * 40))
    add("decision_tree_substitution", lambda x: x["controlled_local_composition_lane"]["decision_candidate"].__setitem__("exact_tree", "0" * 40))
    add("b_substitution", lambda x: next(y for y in x["controlled_local_composition_lane"]["chain"] if y["stage"] == "contract_b").__setitem__("commit", "0" * 40))
    add("d_substitution", lambda x: next(y for y in x["controlled_local_composition_lane"]["chain"] if y["stage"] == "contract_d").__setitem__("commit", "0" * 40))
    add("eb_substitution", lambda x: next(y for y in x["controlled_local_composition_lane"]["chain"] if y["stage"] == "evidence_bundler").__setitem__("commit", "0" * 40))
    add("composition_result_digest", lambda x: x["controlled_local_composition_lane"]["composition_qualification"].__setitem__("result_sha256", "sha256:" + "0" * 64))
    add("composition_artifact_digest", lambda x: x["controlled_local_composition_lane"]["composition_qualification"].__setitem__("artifact_digest", "sha256:" + "0" * 64))
    add("cal_artifact_digest", lambda x: x["controlled_local_composition_lane"]["cal_slice_2"].__setitem__("artifact_digest", "sha256:" + "0" * 64))
    add("consumer_artifact_digest", lambda x: x["controlled_local_composition_lane"]["independent_consumer"].__setitem__("artifact_digest", "sha256:" + "0" * 64))
    add("decision_artifact_digest", lambda x: x["controlled_local_composition_lane"]["decision_candidate"].__setitem__("artifact_digest", "sha256:" + "0" * 64))
    add("determinism_cleared", lambda x: x["controlled_local_composition_lane"]["composition_qualification"]["observations"].__setitem__("deterministic_PIPE01_replay", False))
    add("replay_accepted", lambda x: x["controlled_local_composition_lane"]["composition_qualification"]["observations"].__setitem__("cross_run_native_child_replay", "accepted"))
    add("replay_false_accept", lambda x: x["controlled_local_composition_lane"]["composition_qualification"]["observations"].__setitem__("cross_run_false_accepts", 1))
    add("v2_falsification_erased", lambda x: x["supersedes_for_local_handoff"]["prior_v2_pressure"].__setitem__("disposition", "SUPPORTED"))
    add("trusted_target_boundary_removed", lambda x: x["controlled_local_composition_lane"]["cal_slice_2"].__setitem__("boundary", "all targets accepted"))
    add("stage_omitted", lambda x: x["controlled_local_composition_lane"]["chain"].pop(5))
    add("stage_duplicated", lambda x: x["controlled_local_composition_lane"]["chain"].insert(5, copy.deepcopy(x["controlled_local_composition_lane"]["chain"][4])))
    add("stage_order_changed", lambda x: x["controlled_local_composition_lane"]["chain"].__setitem__(3, x["controlled_local_composition_lane"]["chain"].pop(4)))
    add("repo_substitution", lambda x: next(y for y in x["controlled_local_composition_lane"]["chain"] if y["stage"] == "decision_parent_bound_ingress").__setitem__("repository", "camerontjs-dot/apparatus-contracts"))
    add("authority_class_promoted", lambda x: next(y for y in x["controlled_local_composition_lane"]["chain"] if y["stage"] == "decision_parent_bound_ingress").__setitem__("authority_class", "released"))
    add("terminal_disposition_upgraded", lambda x: x["controlled_local_composition_lane"].__setitem__("terminal_disposition", "AUTHORIZED_FOR_PRODUCTION"))
    add("release_posture_removed", lambda x: x["controlled_local_composition_lane"].pop("release_posture"))
    return out


def main() -> int:
    m = json.loads(MANIFEST.read_text())
    validate(m)
    mutants = mutate(m)
    rejected: list[str] = []
    missed: list[str] = []
    weak_accepted: list[str] = []
    for name, mutant in mutants:
        json.loads(json.dumps(mutant))
        weak_accepted.append(name)
        try:
            validate(mutant)
            missed.append(name)
        except (AssertionError, KeyError, StopIteration):
            rejected.append(name)

    require(not missed, f"strong verifier missed: {missed}")
    require(len(rejected) == 35, f"expected 35 rejected mutations, got {len(rejected)}")
    require(len(weak_accepted) == 35, "weak JSON control failed unexpectedly")

    result = {
        "schema": "cal-pipeline-v3-manifest-pressure/1",
        "honest_manifest": "accepted",
        "mutations_total": len(mutants),
        "strong_rejected": len(rejected),
        "strong_missed": missed,
        "weak_json_consumer_accepted": len(weak_accepted),
        "result": "PASS",
    }
    out = ROOT / "build" / "v3-pressure"
    out.mkdir(parents=True, exist_ok=True)
    (out / "manifest-pressure.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
