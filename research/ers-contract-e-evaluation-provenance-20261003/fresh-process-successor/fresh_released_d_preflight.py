#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

TAG_OBJECT = "6eadd688b482f3c9fce2ce5e7a2841089d852096"
PEELED_COMMIT = "298a1a0f7b7b6d7712e11200d04faec3e1ca169b"
REGISTRY_BLOB = "a40f4f4447470654bdc16d852f5927189ae30cc5"
ERS_EFFECT = "epistemic_audit.stage_pending_review"


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract-d-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    root = args.contract_d_root.resolve()
    output = args.output.resolve()
    if output.exists():
        raise SystemExit("preflight_output_exists")
    if git(root, "rev-parse", "HEAD") != PEELED_COMMIT:
        raise SystemExit("wrong_released_contract_d_head")
    if git(root, "status", "--porcelain=v1", "--untracked-files=all"):
        raise SystemExit("dirty_released_contract_d_checkout")
    if git(root, "rev-parse", "refs/tags/contract-d-v1.0.0") != TAG_OBJECT:
        raise SystemExit("wrong_contract_d_tag_object")
    if git(root, "rev-parse", "refs/tags/contract-d-v1.0.0^{}") != PEELED_COMMIT:
        raise SystemExit("wrong_contract_d_peeled_commit")
    registry = git(
        root, "rev-parse",
        f"{PEELED_COMMIT}:schema/contract-d/1.0.0/effect-registry.json",
    )
    if registry != REGISTRY_BLOB:
        raise SystemExit("wrong_contract_d_registry_blob")

    core_path = root / "validators" / "contract_d_core.py"
    spec = importlib.util.spec_from_file_location(
        "fresh_released_contract_d_preflight_core", core_path
    )
    if spec is None or spec.loader is None:
        raise SystemExit("released_contract_d_import_unavailable")
    core = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = core
    spec.loader.exec_module(core)

    if ERS_EFFECT in core.REGISTRY.get("effects", {}):
        raise SystemExit("ers_effect_present_in_fresh_released_registry")

    fixtures = json.loads(
        (root / "fixtures" / "contract-d" / "1.0.0" / "valid.json").read_text(
            encoding="utf-8"
        )
    )["fixtures"]
    decision = copy.deepcopy(fixtures["source-audit-clear.json"])
    decision["policy"] = {
        "id": "mainframe.epistemic-audit.pending-review",
        "version": "rc2",
    }
    decision["target"] = {
        "kind": "epistemic_claim",
        "id": "claim-fixture-1",
        "content_sha256": "sha256:" + "1" * 64,
    }
    decision["effect"] = {
        "type": ERS_EFFECT,
        "version": "1",
        "params": {},
    }

    observed = "accepted"
    try:
        core.validate_decision(decision)
    except core.ContractDError as exc:
        observed = exc.code

    if observed != "unknown_effect_type":
        raise SystemExit(f"released_d_discriminator_failed:{observed}")

    result = {
        "schema": "ers-05-fresh-released-d-preflight/1",
        "result": "PASS",
        "tag_object": TAG_OBJECT,
        "peeled_commit": PEELED_COMMIT,
        "effect_registry_blob": REGISTRY_BLOB,
        "ers_effect_present": False,
        "research_effect_decision_outcome": observed,
        "research_profile_imported": False,
        "contract_e_imported": False,
        "ers_candidate_imported": False,
    }
    output.write_text(
        json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
