"""Execute the preregistered Contract C non-deciding shadow RC0 cohort."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from validators import contract_c as released

from .shadow import (
    SHADOW_VERSION,
    build_shadow_schema,
    canonical_shadow,
    expected_semantic_delta,
    semantic_schema_delta,
    validate_shadow_bytes,
    validate_shadow_object,
)


def _canonical_json(value: Any) -> bytes:
    return released.canonical_bytes(value)


def _contribution_id(channel: str, evidence_ref: dict[str, str]) -> str:
    payload = {"channel": channel, "evidence_ref": evidence_ref}
    return "contribution:" + hashlib.sha256(_canonical_json(payload)).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _reidentity(value: dict[str, Any]) -> dict[str, Any]:
    return canonical_shadow(value)


def _base_shadow(base: dict[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(base)
    first = out["propositions"][0]
    refs = [copy.deepcopy(row["evidence_ref"]) for row in first["contributions"]]
    neutral = [
        {
            "channel": "non_deciding",
            "contribution_id": _contribution_id("non_deciding", ref),
            "evidence_ref": ref,
        }
        for ref in refs
    ]
    first["execution"] = {"state": "completed", "completion": "not_checkable"}
    first["contributions"] = neutral
    first["measurement"] = None
    first["conclusion"] = {
        "reported_verdict": "not_checkable",
        "terminal_branch": "unresolved_categorical_relation",
        "causal_form": "independent_sufficient_alternatives",
        "basis_members": [
            {"namespace": "contribution", "id": row["contribution_id"]} for row in neutral
        ],
        "residual_contribution_ids": [],
        "rule_roles": [],
    }
    return _reidentity(out)


def _errors(value: dict[str, Any], index: dict[str, Any]) -> list[str]:
    return validate_shadow_object(_reidentity(value), contract_b_index=index)


def _expect_rejected(value: dict[str, Any], index: dict[str, Any]) -> bool:
    return bool(_errors(value, index))


def run(repo_root: Path, out_dir: Path) -> dict[str, Any]:
    schema_path = repo_root / "schema/contract-c/1.0.0/schema.json"
    fixture_path = repo_root / "fixtures/contract-c/1.0.0/valid-canonical.json"
    index_path = repo_root / "fixtures/contract-c/1.0.0/contract-b-index.json"
    released_schema = _load(schema_path)
    base = _load(fixture_path)
    index = _load(index_path)

    shadow_schema = build_shadow_schema(released_schema)
    delta = semantic_schema_delta(released_schema, shadow_schema)
    exact_two_leaf_delta = delta == expected_semantic_delta()

    valid = _base_shadow(base)
    valid_raw = released.canonical_bytes(valid)
    valid_sha = released.sha256_hex(valid_raw)
    shadow_errors = validate_shadow_bytes(
        valid_raw,
        expected_sha256=valid_sha,
        contract_b_index=index,
    )
    released_errors = released.validate_contract_c_bytes(valid_raw, contract_b_index=index)

    first = valid["propositions"][0]
    ids = [row["contribution_id"] for row in first["contributions"]]

    one_causal = copy.deepcopy(valid)
    p = one_causal["propositions"][0]
    p["conclusion"]["causal_form"] = "single_necessary"
    p["conclusion"]["basis_members"] = [{"namespace": "contribution", "id": ids[0]}]
    p["conclusion"]["residual_contribution_ids"] = [ids[1]]
    one_causal = _reidentity(one_causal)

    mixed_legacy_channels = copy.deepcopy(valid)
    second = mixed_legacy_channels["propositions"][1]
    second["contributions"][0]["channel"] = "counterevidence"
    mixed_legacy_channels = _reidentity(mixed_legacy_channels)

    bad_unknown_basis = copy.deepcopy(valid)
    bad_unknown_basis["propositions"][0]["conclusion"]["basis_members"][0]["id"] = (
        "contribution:" + "0" * 64
    )

    bad_ref = copy.deepcopy(valid)
    bad_ref["propositions"][0]["contributions"][0]["evidence_ref"]["passage_id"] = "absent-passage"

    bad_single_two = copy.deepcopy(valid)
    bad_single_two["propositions"][0]["conclusion"]["causal_form"] = "single_necessary"

    bad_independent_one = copy.deepcopy(one_causal)
    bad_independent_one["propositions"][0]["conclusion"]["causal_form"] = (
        "independent_sufficient_alternatives"
    )

    bad_overlap = copy.deepcopy(valid)
    bad_overlap["propositions"][0]["conclusion"]["residual_contribution_ids"] = [ids[0]]

    bad_unclassified = copy.deepcopy(one_causal)
    bad_unclassified["propositions"][0]["conclusion"]["residual_contribution_ids"] = []

    bad_extra = copy.deepcopy(valid)
    bad_extra["propositions"][0]["contributions"][0]["producer_hint"] = "forbidden"

    bad_channel = copy.deepcopy(valid)
    bad_channel["propositions"][0]["contributions"][0]["channel"] = "neutralish"

    bad_result_id = copy.deepcopy(valid)
    bad_result_id["result_set_id"] = "result-set:" + "0" * 64

    wrong_hash = "0" * 64 if valid_sha != "0" * 64 else "1" * 64
    whole_hash_rejected = bool(
        validate_shadow_bytes(valid_raw, expected_sha256=wrong_hash, contract_b_index=index)
    )

    widened_schema = copy.deepcopy(shadow_schema)
    widened_schema["$defs"]["assessment_state"]["oneOf"].append({"type": "null"})
    unrelated_relaxation_visible = semantic_schema_delta(released_schema, widened_schema) != expected_semantic_delta()

    checks = {
        "exact_two_leaf_semantic_schema_delta": exact_two_leaf_delta,
        "shadow_valid": not shadow_errors,
        "released_1_0_rejects_shadow": bool(released_errors),
        "released_rejection_mentions_version_or_channel": any(
            "contract_c_version" in err or "channel" in err for err in released_errors
        ),
        "two_neutral_basis_members_preserved": (
            len(first["conclusion"]["basis_members"]) == 2
            and first["conclusion"]["causal_form"] == "independent_sufficient_alternatives"
            and all(row["channel"] == "non_deciding" for row in first["contributions"])
        ),
        "single_causal_plus_residual_neutral_valid": not validate_shadow_object(
            one_causal, contract_b_index=index
        ),
        "legacy_support_and_counterevidence_remain_valid": not validate_shadow_object(
            mixed_legacy_channels, contract_b_index=index
        ),
        "unknown_basis_rejected": _expect_rejected(bad_unknown_basis, index),
        "wrong_contract_b_evidence_ref_rejected": _expect_rejected(bad_ref, index),
        "single_necessary_two_basis_rejected": _expect_rejected(bad_single_two, index),
        "independent_alternatives_one_basis_rejected": _expect_rejected(bad_independent_one, index),
        "causal_residual_overlap_rejected": _expect_rejected(bad_overlap, index),
        "unclassified_retained_contribution_rejected": _expect_rejected(bad_unclassified, index),
        "unknown_additional_field_rejected": _expect_rejected(bad_extra, index),
        "unknown_channel_rejected": _expect_rejected(bad_channel, index),
        "result_set_identity_tamper_rejected": bool(
            validate_shadow_object(bad_result_id, contract_b_index=index)
        ),
        "whole_object_hash_tamper_rejected": whole_hash_rejected,
        "unrelated_schema_relaxation_detectable": unrelated_relaxation_visible,
        "canonical_round_trip_stable": released.canonical_bytes(
            released.parse_json_bytes(valid_raw)
        ) == valid_raw,
        "shadow_version_is_noncanonical_research_sentinel": valid["contract_c_version"] == SHADOW_VERSION,
    }

    critical = list(checks.values())
    if all(critical):
        disposition = "SUPPORTED_BOUNDED_TWO_LEAF_SHADOW_DELTA"
    elif exact_two_leaf_delta:
        disposition = "FALSIFIED_MINIMAL_SHADOW_DELTA"
    else:
        disposition = "INCONCLUSIVE_SHADOW_VALIDATOR_INVALID"

    result = {
        "research_disposition": disposition,
        "exact_base": "c3563cff66d2c85dcbf575c693056e2d8e4563d4",
        "released_contract_c_validator_blob": "9c75ccfbf2223578a8d1a7bf0c39673b394fbea4",
        "released_contract_c_schema_blob": "b0369de9b5c156322d6787261bbc7658a3b33781",
        "cal_pr100_pressure_head": "aa5f0f1313e65e6d31493095214c76d743ca6d89",
        "cal_candidate_blob": "a7934b3c242dcf1c33a28121b3b141c9c6adc203",
        "semantic_schema_delta": delta,
        "shadow_sha256": f"sha256:{valid_sha}",
        "shadow_result_set_id": valid["result_set_id"],
        "checks": checks,
        "released_1_0_rejection_sample": released_errors[:6],
        "interpretation": {
            "canonical_contract_c_version_selected": False,
            "released_contract_c_1_0_mutated": False,
            "production_promotion_authorized": False,
            "decision_engine_conformance_established": False,
        },
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "SHADOW_SCHEMA.json").write_bytes(released.canonical_bytes(shadow_schema))
    (out_dir / "VALID_SHADOW.json").write_bytes(valid_raw)
    (out_dir / "CONTRACT_B_INDEX.json").write_bytes(released.canonical_bytes(index))
    (out_dir / "EVALUATION.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.repo_root.resolve(), args.out.resolve())
    print(json.dumps(result, sort_keys=True))
    return 0 if result["research_disposition"] == "SUPPORTED_BOUNDED_TWO_LEAF_SHADOW_DELTA" else 1


if __name__ == "__main__":
    raise SystemExit(main())
