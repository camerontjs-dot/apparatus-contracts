from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any

from validators import contract_c as released

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CANDIDATE_DIR = ROOT / "research" / "contract_c_successor_candidate_rc0"
sys.path.insert(0, str(CANDIDATE_DIR))
import validator as candidate  # noqa: E402

MANIFEST = json.loads((HERE / "EVIDENCE_MANIFEST.json").read_text())
RAW = (CANDIDATE_DIR / "fixtures" / "valid-shadow.json").read_bytes()
INDEX = json.loads((CANDIDATE_DIR / "fixtures" / "contract-b-index.json").read_text())


def _rebind(value: dict[str, Any]) -> bytes:
    obj = copy.deepcopy(value)
    obj["result_set_id"] = released.result_set_identity(obj)
    return released.canonical_bytes(obj)


def _released_valid(raw: bytes) -> tuple[bool, list[str]]:
    errors = released.validate_contract_c_bytes(raw, contract_b_index=INDEX)
    return not errors, errors


def _candidate_valid(raw: bytes) -> tuple[bool, list[str]]:
    errors = candidate.validate_candidate_bytes(raw, contract_b_index=INDEX)
    return not errors, errors


def _downgrade_relabel(channel: str) -> tuple[bytes, dict[str, Any]]:
    obj = released.parse_json_bytes(RAW)
    obj["contract_c_version"] = "1.0.0"
    changed: list[str] = []
    for contribution in obj["propositions"][0]["contributions"]:
        if contribution["channel"] == "non_deciding":
            changed.append(contribution["contribution_id"])
            contribution["channel"] = channel
    return _rebind(obj), {
        "translation": f"non_deciding_to_{channel}",
        "changed_contribution_ids": changed,
        "semantic_loss": bool(changed),
        "loss_reason": "neutral/non-deciding classification is replaced by a polarized channel",
    }


def _downgrade_drop() -> tuple[bytes, dict[str, Any]]:
    obj = released.parse_json_bytes(RAW)
    obj["contract_c_version"] = "1.0.0"
    proposition = obj["propositions"][0]
    dropped = [
        contribution["contribution_id"]
        for contribution in proposition["contributions"]
        if contribution["channel"] == "non_deciding"
    ]
    dropped_passages = [
        contribution["evidence_ref"]["passage_id"]
        for contribution in proposition["contributions"]
        if contribution["channel"] == "non_deciding"
    ]
    proposition["contributions"] = [
        contribution
        for contribution in proposition["contributions"]
        if contribution["channel"] != "non_deciding"
    ]
    proposition["conclusion"]["basis_members"] = [
        member
        for member in proposition["conclusion"]["basis_members"]
        if not (member["namespace"] == "contribution" and member["id"] in dropped)
    ]
    proposition["conclusion"]["residual_contribution_ids"] = [
        cid
        for cid in proposition["conclusion"]["residual_contribution_ids"]
        if cid not in dropped
    ]
    if not proposition["conclusion"]["basis_members"]:
        proposition["conclusion"]["causal_form"] = "redundant_non_deciding"
    return _rebind(obj), {
        "translation": "drop_non_deciding_and_repair_basis",
        "dropped_contribution_ids": dropped,
        "dropped_passage_ids": dropped_passages,
        "semantic_loss": bool(dropped),
        "loss_reason": "exact retained neutral contribution identity/evidence provenance and demonstrated causal membership are removed",
    }


def evaluate() -> dict[str, Any]:
    checks: dict[str, bool] = {}
    observations: dict[str, Any] = {}

    base_schema = candidate.load_released_schema()
    candidate_schema = candidate.build_candidate_schema(base_schema)
    semantic_delta = candidate.semantic_schema_delta(base_schema, candidate_schema)
    checks["exact_two_leaf_candidate_delta"] = semantic_delta == candidate.expected_semantic_delta()
    observations["semantic_delta"] = semantic_delta

    checks["candidate_profile_is_non_release_sentinel"] = (
        candidate.CANDIDATE_VERSION == "research-non-deciding-rc0"
        and MANIFEST["official_version_assigned"] is False
    )

    checks["released_registry_remains_1_0_only"] = (
        json.loads((ROOT / "schema/contract-c/versions.json").read_text())
        == {"canonical_version": "1.0.0", "supported_versions": ["1.0.0"]}
    )

    candidate_ok, candidate_errors = _candidate_valid(RAW)
    checks["exact_successor_handoff_validates_directly"] = candidate_ok
    observations["candidate_errors"] = candidate_errors

    model = candidate.CandidateContractCResultSet.model_validate(released.parse_json_bytes(RAW))
    observed_channels = [
        contribution.channel for contribution in model.propositions[0].contributions
    ]
    checks["non_deciding_preserved_without_relabelling"] = observed_channels == [
        "non_deciding",
        "non_deciding",
    ]
    observations["candidate_channels"] = observed_channels

    released_ok, released_errors = _released_valid(RAW)
    checks["strict_released_1_0_rejects_exact_successor"] = not released_ok
    observations["released_1_0_errors_on_successor"] = released_errors

    contribution_schema = base_schema["$defs"]["contribution"]
    released_channels = contribution_schema["properties"]["channel"]["enum"]
    checks["released_1_0_has_no_neutral_channel"] = (
        released_channels == ["support", "counterevidence"]
    )
    checks["released_1_0_contribution_is_strict"] = (
        contribution_schema.get("additionalProperties") is False
    )
    observations["released_1_0_channels"] = released_channels

    downgrade_results: list[dict[str, Any]] = []
    for make in (
        lambda: _downgrade_relabel("support"),
        lambda: _downgrade_relabel("counterevidence"),
        _downgrade_drop,
    ):
        raw, record = make()
        valid, errors = _released_valid(raw)
        record["released_1_0_valid"] = valid
        record["released_1_0_errors"] = errors
        downgrade_results.append(record)
    observations["downgrade_attempts"] = downgrade_results
    checks["downgrade_attempts_validate_only_with_semantic_loss"] = all(
        row["released_1_0_valid"] and row["semantic_loss"]
        for row in downgrade_results
    )

    legacy_channel_results: dict[str, bool] = {}
    for channel in ("support", "counterevidence"):
        obj = released.parse_json_bytes(RAW)
        obj["propositions"][0]["contributions"][0]["channel"] = channel
        raw = _rebind(obj)
        legacy_channel_results[channel] = _candidate_valid(raw)[0]
    observations["legacy_candidate_channels"] = legacy_channel_results
    checks["candidate_retains_legacy_channel_acceptance"] = all(legacy_channel_results.values())

    producer_status = MANIFEST["producer_conformance"]["status"]
    consumer_status = MANIFEST["consumer_conformance"]["status"]
    checks["bounded_consumer_conformance_recorded"] = consumer_status == "ESTABLISHED_BOUNDED"
    checks["producer_conformance_established"] = producer_status == "ESTABLISHED_FOR_EXACT_SUCCESSOR"
    observations["producer_conformance_status"] = producer_status
    observations["consumer_conformance_status"] = consumer_status

    compatibility_breaking = (
        checks["strict_released_1_0_rejects_exact_successor"]
        and checks["released_1_0_has_no_neutral_channel"]
        and checks["released_1_0_contribution_is_strict"]
        and checks["downgrade_attempts_validate_only_with_semantic_loss"]
    )
    version_class = "MAJOR" if compatibility_breaking else "UNRESOLVED"

    semantic_required = [
        "exact_two_leaf_candidate_delta",
        "candidate_profile_is_non_release_sentinel",
        "released_registry_remains_1_0_only",
        "exact_successor_handoff_validates_directly",
        "non_deciding_preserved_without_relabelling",
        "strict_released_1_0_rejects_exact_successor",
        "released_1_0_has_no_neutral_channel",
        "released_1_0_contribution_is_strict",
        "downgrade_attempts_validate_only_with_semantic_loss",
        "candidate_retains_legacy_channel_acceptance",
        "bounded_consumer_conformance_recorded",
    ]
    semantic_failure = [name for name in semantic_required if not checks[name]]

    if semantic_failure:
        disposition = "FALSIFIED"
        blockers = semantic_failure
    elif not checks["producer_conformance_established"]:
        disposition = "INCONCLUSIVE"
        blockers = ["maintained_or_promotion_ready_producer_conformance_for_exact_successor_not_established"]
    else:
        disposition = "SUPPORTED FOR PROMOTION"
        blockers = []

    return {
        "schema": "contract-c-successor-promotion-qualification-result-v1",
        "parent_candidate_head": MANIFEST["parent_candidate"]["head"],
        "research_disposition": disposition,
        "version_class_if_promoted": version_class,
        "official_version_assigned": False,
        "promotion_executed": False,
        "checks": checks,
        "observations": observations,
        "blockers": blockers,
        "interpretation": {
            "parallel_exact_version_authority_required": compatibility_breaking,
            "safe_automatic_1_0_downgrade_established": False,
            "new_edr_required_for_eventual_promotion": True,
            "actual_release_still_requires_separate_promotion_pr": True,
        },
    }


def main() -> None:
    result = evaluate()
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "QUALIFICATION_RESULT.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps(result, sort_keys=True))
    if result["research_disposition"] == "FALSIFIED":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
