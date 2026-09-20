from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

SLICE_SHA = "79aa0527b52deaa748947514202c9a415b5f0e23"
CARRIER_SHA = "c3563cff66d2c85dcbf575c693056e2d8e4563d4"
C2_SHA = "b42c827acb0a9fe65353354d709add0e27bab307"
PARENT_TERMINAL_SHA = "7aafa6e9235e76f0703a394ee42b799f09136846"
RSH_APERTURE_SHA = "52869e08f98ebaaf4acd31dd5955874f7fdaec81"
V1_RECORD_BLOB = "01fafba3b4924bcd0394bfc5530c2d525eb6ba1e"
V1_MANIFEST_BLOB = "b66702df8a1f0f272ef113d14897aa01778af0a2"

ROOT = Path(__file__).resolve().parents[2]
FREEZE_DIR = ROOT / "research" / "cal-pipeline-v1-contract-authority-freeze-20260919"
V1 = FREEZE_DIR / "SLICE_MANIFEST.json"
V2 = FREEZE_DIR / "SLICE_MANIFEST_V2.json"
C2 = ROOT / "_pressure" / "c2"
PARENT = ROOT / "_pressure" / "parent"
RSH = ROOT / "_pressure" / "rsh"
RSH_APERTURE = RSH / "research" / "contract_c_cal_v1_parent_consumer_aperture_20260919"


def run(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(args, cwd=cwd, text=True).strip()


def git_blob(path: Path) -> str:
    return run("git", "hash-object", str(path), cwd=ROOT)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate_handoff(m: dict[str, Any]) -> None:
    require(m["schema_version"] == "apparatus-contracts-local-pipeline-authority-slice/2", "wrong v2 schema")
    require(m["status"] == "QUALIFIED_FOR_LOCAL_PIPELINE_CONTRACT_AUTHORITY", "released authority status changed")
    require(m["supersedes_for_local_handoff"]["prior_manifest_blob"] == V1_MANIFEST_BLOB, "v1 manifest identity changed")
    require(m["authority_lane"]["status"] == "unchanged", "authority lane no longer unchanged")
    require(
        m["authority_lane"]["supported_authority_chain"]
        == "Contract A 2.0.0 -> Contract B 1.2.0 -> Contract C 1.0.0 -> Contract D 1.0.0",
        "authority lane widened",
    )
    require(m["contracts"]["contract_c"]["version"] == "1.0.0", "released C1 entry rewritten")
    require(m["contracts"]["contract_e"]["included"] is False, "Contract E entered authority slice")

    lane = m["successor_lanes"]["contract_c_v2_parent_recomposition"]
    require(lane["admitted_to_authority_lane"] is False, "C2 silently admitted")
    require(lane["current_disposition"] == "SUPPORTED_FOR_INDEPENDENT_CONSUMER_APERTURE", "successor disposition drift")
    require(lane["production_candidate"]["exact_head"] == C2_SHA, "C2 head substitution")
    require(lane["production_candidate"]["canonical_discovery_remains"] == "Contract C 1.0.0", "C2 canonical-discovery laundering")
    require(lane["parent_recomposition_binding_rc0"]["terminal_record_commit"] == PARENT_TERMINAL_SHA, "parent-binding terminal record drift")
    require(lane["parent_recomposition_binding_rc0"]["disposition"] == "SUPPORTED_FOR_INDEPENDENT_CONSUMER_APERTURE", "parent-binding disposition upgraded")
    gate = lane["independent_consumer_gate"]
    require(gate["frozen_aperture_commit"] == RSH_APERTURE_SHA, "aperture identity drift")
    require(gate["status"] == "APERTURE_FROZEN_CONSUMER_NOT_YET_EXECUTED", "independent-consumer state laundering")
    require(gate["blocks_authority_admission"] is True, "independent-consumer block cleared")
    require("STOP" in lane["local_route"]["required_stop"], "successor hard stop removed")


def mutation_matrix(m: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    out: list[tuple[str, dict[str, Any]]] = []

    def add(name: str, fn) -> None:
        x = copy.deepcopy(m)
        fn(x)
        out.append((name, x))

    add("authority_lane_to_c2", lambda x: x["authority_lane"].__setitem__(
        "supported_authority_chain",
        "Contract A 2.0.0 -> Contract B 1.2.0 -> Contract C 2.0.0 -> Contract D 1.0.0",
    ))
    add("c2_admitted", lambda x: x["successor_lanes"]["contract_c_v2_parent_recomposition"].__setitem__("admitted_to_authority_lane", True))
    add("canonical_discovery_to_c2", lambda x: x["successor_lanes"]["contract_c_v2_parent_recomposition"]["production_candidate"].__setitem__("canonical_discovery_remains", "Contract C 2.0.0"))
    add("consumer_block_cleared", lambda x: x["successor_lanes"]["contract_c_v2_parent_recomposition"]["independent_consumer_gate"].__setitem__("blocks_authority_admission", False))
    add("consumer_state_laundered", lambda x: x["successor_lanes"]["contract_c_v2_parent_recomposition"]["independent_consumer_gate"].__setitem__("status", "PASS"))
    add("parent_disposition_upgraded", lambda x: x["successor_lanes"]["contract_c_v2_parent_recomposition"]["parent_recomposition_binding_rc0"].__setitem__("disposition", "SUPPORTED_FOR_PROMOTION"))
    add("c2_head_substituted", lambda x: x["successor_lanes"]["contract_c_v2_parent_recomposition"]["production_candidate"].__setitem__("exact_head", "0" * 40))
    add("contract_e_included", lambda x: x["contracts"]["contract_e"].__setitem__("included", True))
    add("v1_manifest_substituted", lambda x: x["supersedes_for_local_handoff"].__setitem__("prior_manifest_blob", "0" * 40))
    add("hard_stop_removed", lambda x: x["successor_lanes"]["contract_c_v2_parent_recomposition"]["local_route"].__setitem__("required_stop", "continue to Decision"))
    add("successor_lane_removed", lambda x: x.__setitem__("successor_lanes", {}))
    add("released_c_relabelled", lambda x: x["contracts"]["contract_c"].__setitem__("version", "2.0.0"))
    return out


def collect_path_blobs(node: Any) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    if isinstance(node, dict):
        if isinstance(node.get("path"), str) and isinstance(node.get("git_blob"), str):
            found.append((node["path"], node["git_blob"]))
        for v in node.values():
            found.extend(collect_path_blobs(v))
    elif isinstance(node, list):
        for v in node:
            found.extend(collect_path_blobs(v))
    return found


def main() -> int:
    v1 = json.loads(V1.read_text())
    v2 = json.loads(V2.read_text())

    require(run("git", "rev-parse", f"{SLICE_SHA}:research/cal-pipeline-v1-contract-authority-freeze-20260919/FREEZE_RECORD.md") == V1_RECORD_BLOB, "historical FREEZE_RECORD changed at exact slice head")
    require(run("git", "rev-parse", f"{SLICE_SHA}:research/cal-pipeline-v1-contract-authority-freeze-20260919/SLICE_MANIFEST.json") == V1_MANIFEST_BLOB, "historical v1 manifest changed at exact slice head")
    require(git_blob(FREEZE_DIR / "FREEZE_RECORD.md") == V1_RECORD_BLOB, "pressure branch changed historical FREEZE_RECORD")
    require(git_blob(V1) == V1_MANIFEST_BLOB, "pressure branch changed historical v1 manifest")

    release_checks = 0
    for key in ("contract_a", "contract_b", "contract_c", "contract_d"):
        contract = v1["contracts"][key]
        release = contract["release_commit"]
        for path, blob in collect_path_blobs(contract):
            actual_release = run("git", "rev-parse", f"{release}:{path}")
            actual_carrier = run("git", "rev-parse", f"{CARRIER_SHA}:{path}")
            require(actual_release == blob, f"{key} release blob mismatch: {path}")
            require(actual_carrier == blob, f"{key} carrier blob mismatch: {path}")
            release_checks += 1
    require(release_checks == 22, f"expected 22 released normative pins, got {release_checks}")

    validate_handoff(v2)

    c2_lane = v2["successor_lanes"]["contract_c_v2_parent_recomposition"]["production_candidate"]
    require(run("git", "rev-parse", "HEAD", cwd=C2) == C2_SHA, "C2 checkout identity mismatch")
    for path, expected in c2_lane["exact_blobs"].items():
        actual = run("git", "hash-object", path, cwd=C2)
        require(actual == expected, f"C2 blob mismatch: {path}")

    versions = json.loads((C2 / "schema/contract-c/versions.json").read_text())
    require(versions == {"canonical_version": "1.0.0", "supported_versions": ["1.0.0"]}, "C2 branch changed global canonical discovery")
    require(run("git", "hash-object", "schema/contract-c/versions.json", cwd=C2) == "6e805e274f8b1f491bf0c10735a46962ab91d2d4", "C2 global versions blob drift")
    promotion = json.loads((C2 / "schema/contract-c/2.0.0/promotion-version.json").read_text())
    require(promotion["candidate_compatibility_version"] == "2.0.0", "C2 candidate version drift")
    require(promotion["canonical_registry_switch_authorized"] is False, "canonical switch already authorized")
    require(promotion["promotion_status"] == "pre_merge_candidate", "C2 promotion status drift")

    require(run("git", "rev-parse", "HEAD", cwd=PARENT) == PARENT_TERMINAL_SHA, "parent-binding checkout identity mismatch")
    parent_dir = "research/contract_c_cal_v1_parent_recomposition_rc0_20260919"
    require(run("git", "rev-parse", f"HEAD:{parent_dir}/candidate_rc0.py", cwd=PARENT) == "df6b6ed410f52cafaeadfe1578d770f480a34b09", "parent candidate blob drift")
    require(run("git", "rev-parse", f"HEAD:{parent_dir}/evaluate.py", cwd=PARENT) == "dd279c8bff695bfb09cac2f782f39be1300a0cdd", "parent evaluator blob drift")
    terminal = (PARENT / parent_dir / "TERMINAL_RECORD.md").read_text()
    require("SUPPORTED_FOR_INDEPENDENT_CONSUMER_APERTURE" in terminal, "parent terminal disposition missing")
    require("49/49 true" in terminal, "parent pressure result missing")

    require(run("git", "rev-parse", "HEAD", cwd=RSH) == RSH_APERTURE_SHA, "RSH aperture checkout identity mismatch")
    allowed = {
        "AUTHORITIES.json",
        "INNER_RC2_SPEC.md",
        "MANIFEST.json",
        "PARENT_BINDING_SPEC.md",
        "PRE_FREEZE_TASK.md",
    }
    actual = {p.name for p in RSH_APERTURE.iterdir() if p.is_file()}
    require(actual == allowed, f"aperture file set changed: {sorted(actual)}")
    require(not (RSH_APERTURE / "candidate").exists(), "candidate output contaminated aperture")
    aperture_manifest = json.loads((RSH_APERTURE / "MANIFEST.json").read_text())
    require(aperture_manifest["real_producer_handoffs_in_aperture"] is False, "real handoff leaked into aperture")
    require(aperture_manifest["post_freeze_evaluator_in_aperture"] is False, "evaluator leaked into aperture")
    require(aperture_manifest["producer_candidate_implementation_in_aperture"] is False, "producer implementation leaked into aperture")
    require(aperture_manifest["prior_consumer_implementation_in_aperture"] is False, "prior consumer leaked into aperture")

    mutants = mutation_matrix(v2)
    rejected: list[str] = []
    weak_accepted: list[str] = []
    for name, mutant in mutants:
        json.loads(json.dumps(mutant))
        weak_accepted.append(name)
        try:
            validate_handoff(mutant)
        except (AssertionError, KeyError):
            rejected.append(name)
    require(len(rejected) == len(mutants), f"strong verifier missed mutations: {sorted(set(n for n, _ in mutants) - set(rejected))}")
    require(len(weak_accepted) == len(mutants), "weak JSON consumer unexpectedly rejected a syntactically valid mutation")

    result = {
        "schema": "apparatus-contracts-authority-slice-v2-pressure/1",
        "slice_subject": SLICE_SHA,
        "released_normative_pin_checks": release_checks,
        "honest_manifest": "accepted",
        "mutations_total": len(mutants),
        "strong_verifier_rejected": len(rejected),
        "weak_json_consumer_accepted": len(weak_accepted),
        "c2_head": C2_SHA,
        "c2_global_canonical_version": versions["canonical_version"],
        "c2_canonical_registry_switch_authorized": promotion["canonical_registry_switch_authorized"],
        "parent_binding_terminal": "SUPPORTED_FOR_INDEPENDENT_CONSUMER_APERTURE",
        "rsh_aperture": RSH_APERTURE_SHA,
        "rsh_candidate_output_present": False,
        "decision_qualification_attempted": False,
        "contract_e_attempted": False,
        "result": "PASS",
    }
    out = ROOT / "build" / "authority-slice-v2-pressure"
    out.mkdir(parents=True, exist_ok=True)
    (out / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
