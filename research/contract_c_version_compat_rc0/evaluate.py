"""Execute Contract C version compatibility RC0."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any, Callable

from validators import contract_c as released
from research.contract_c_non_deciding_shadow_rc0.shadow import validate_shadow_bytes

from .compatibility import (
    RELEASED_PROFILE,
    SUCCESSOR_PROFILE,
    CompatibilityError,
    canonical_materialize,
    provenance_fingerprint,
    safe_downgrade_to_1_0,
    unsafe_drop_non_deciding_to_1_0,
    unsafe_map_channel_to_1_0,
    validate_bound_profile,
)

RELEASED_FIXTURE_SHA = "sha256:7a66583e332be4901d13ba9f2d7e12419938c77a41b83223a4b0946ad529b7a1"
SUCCESSOR_SHA = "sha256:325962ebcdbf6af836bb6193a451524ccd40b4d10f2394ff9f703fbfce1ec1e3"


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected object: {path}")
    return value


def _expect_compat_error(fragment: str, fn: Callable[[], Any]) -> bool:
    try:
        fn()
    except CompatibilityError as exc:
        if fragment not in str(exc):
            raise AssertionError(f"expected {fragment!r} in {exc!r}") from exc
        return True
    raise AssertionError(f"expected CompatibilityError containing {fragment!r}")


def _validate_released(raw: bytes, index: dict[str, Any]) -> list[str]:
    return released.validate_contract_c_bytes(raw, contract_b_index=index)


def _downgrade_observation(
    label: str,
    source: dict[str, Any],
    transform: Callable[[dict[str, Any]], dict[str, Any]],
    index: dict[str, Any],
    source_fingerprint: list[dict[str, Any]],
) -> dict[str, Any]:
    value = transform(source)
    raw = canonical_materialize(value)
    parsed = released.parse_json_bytes(raw)
    errors = _validate_released(raw, index)
    fingerprint = provenance_fingerprint(parsed)
    original_digest_rejects = bool(released.validate_whole_object_hash(raw, SUCCESSOR_SHA))
    return {
        "label": label,
        "released_1_0_validator_accepts": not errors,
        "released_validation_errors": errors,
        "sha256": "sha256:" + released.sha256_hex(raw),
        "result_set_id": parsed["result_set_id"],
        "provenance_fingerprint_equal_to_successor": fingerprint == source_fingerprint,
        "provenance_fingerprint": fingerprint,
        "original_successor_digest_rejects_transformed_bytes": original_digest_rejects,
    }


def run(repo_root: Path, out_dir: Path) -> dict[str, Any]:
    released_raw = (repo_root / "fixtures/contract-c/1.0.0/valid-canonical.json").read_bytes()
    released_index = _load(repo_root / "fixtures/contract-c/1.0.0/contract-b-index.json")
    successor_root = repo_root / "research/contract_c_non_deciding_shadow_rc0/handoff"
    successor_raw = (successor_root / "valid-shadow.json").read_bytes()
    successor_index = _load(successor_root / "contract-b-index.json")
    successor = released.parse_json_bytes(successor_raw)

    assert "sha256:" + released.sha256_hex(released_raw) == RELEASED_FIXTURE_SHA
    assert "sha256:" + released.sha256_hex(successor_raw) == SUCCESSOR_SHA

    released_strict_errors = released.validate_contract_c_bytes(
        released_raw,
        expected_sha256=RELEASED_FIXTURE_SHA,
        contract_b_index=released_index,
    )
    legacy_rejects_successor_errors = released.validate_contract_c_bytes(
        successor_raw,
        expected_sha256=SUCCESSOR_SHA,
        contract_b_index=successor_index,
    )
    successor_errors = validate_shadow_bytes(
        successor_raw,
        expected_sha256=SUCCESSOR_SHA,
        contract_b_index=successor_index,
    )

    released_bound = validate_bound_profile(
        released_raw,
        expected_profile=RELEASED_PROFILE,
        expected_sha256=RELEASED_FIXTURE_SHA,
        contract_b_index=released_index,
    )
    successor_bound = validate_bound_profile(
        successor_raw,
        expected_profile=SUCCESSOR_PROFILE,
        expected_sha256=SUCCESSOR_SHA,
        contract_b_index=successor_index,
    )

    successor_under_released_rejected = _expect_compat_error(
        "profile_version_mismatch",
        lambda: validate_bound_profile(
            successor_raw,
            expected_profile=RELEASED_PROFILE,
            expected_sha256=SUCCESSOR_SHA,
            contract_b_index=successor_index,
        ),
    )
    released_under_successor_rejected = _expect_compat_error(
        "profile_version_mismatch",
        lambda: validate_bound_profile(
            released_raw,
            expected_profile=SUCCESSOR_PROFILE,
            expected_sha256=RELEASED_FIXTURE_SHA,
            contract_b_index=released_index,
        ),
    )

    safe_downgrade_refused = _expect_compat_error(
        "lossless_downgrade_unavailable",
        lambda: safe_downgrade_to_1_0(successor),
    )

    source_fingerprint = provenance_fingerprint(successor)
    downgrades = [
        _downgrade_observation(
            "map_non_deciding_to_support",
            successor,
            lambda value: unsafe_map_channel_to_1_0(value, "support"),
            successor_index,
            source_fingerprint,
        ),
        _downgrade_observation(
            "map_non_deciding_to_counterevidence",
            successor,
            lambda value: unsafe_map_channel_to_1_0(value, "counterevidence"),
            successor_index,
            source_fingerprint,
        ),
        _downgrade_observation(
            "drop_non_deciding_and_repair_basis",
            successor,
            unsafe_drop_non_deciding_to_1_0,
            successor_index,
            source_fingerprint,
        ),
    ]

    validator_valid_semantic_laundering = [
        item["label"]
        for item in downgrades
        if item["released_1_0_validator_accepts"]
        and not item["provenance_fingerprint_equal_to_successor"]
    ]

    successor_version_rewrite = copy.deepcopy(successor)
    successor_version_rewrite["contract_c_version"] = "1.0.0"
    successor_version_rewrite["result_set_id"] = released.result_set_identity(successor_version_rewrite)
    version_only_raw = released.canonical_bytes(successor_version_rewrite)
    version_only_breaks_original_digest = bool(
        released.validate_whole_object_hash(version_only_raw, SUCCESSOR_SHA)
    )

    checks = {
        "released_1_0_fixture_valid_unchanged": not released_strict_errors,
        "released_strict_1_0_rejects_successor_unchanged": bool(legacy_rejects_successor_errors),
        "successor_shadow_valid_unchanged": not successor_errors,
        "parallel_profile_released_accepts_exact_released": (
            released_bound["profile_id"] == RELEASED_PROFILE
            and released_bound["whole_object_sha256"] == RELEASED_FIXTURE_SHA
        ),
        "parallel_profile_successor_accepts_exact_successor": (
            successor_bound["profile_id"] == SUCCESSOR_PROFILE
            and successor_bound["whole_object_sha256"] == SUCCESSOR_SHA
        ),
        "successor_under_released_profile_rejected": successor_under_released_rejected,
        "released_under_successor_profile_rejected": released_under_successor_rejected,
        "safe_downgrade_refuses_non_deciding": safe_downgrade_refused,
        "at_least_one_validator_valid_semantic_laundering_downgrade_exists": bool(
            validator_valid_semantic_laundering
        ),
        "all_validator_valid_downgrades_change_successor_semantics": all(
            not item["provenance_fingerprint_equal_to_successor"]
            for item in downgrades
            if item["released_1_0_validator_accepts"]
        ),
        "every_tested_downgrade_changes_original_immutable_digest": all(
            item["original_successor_digest_rejects_transformed_bytes"] for item in downgrades
        ),
        "version_only_rewrite_changes_original_immutable_digest": version_only_breaks_original_digest,
        "external_profile_not_artifact_version_selects_validator": (
            successor_under_released_rejected and released_under_successor_rejected
        ),
    }

    old_consumer_breaks = checks["released_strict_1_0_rejects_successor_unchanged"]
    translation_unsafe = (
        checks["safe_downgrade_refuses_non_deciding"]
        and checks["at_least_one_validator_valid_semantic_laundering_downgrade_exists"]
        and checks["all_validator_valid_downgrades_change_successor_semantics"]
    )
    parallel_supported = (
        checks["parallel_profile_released_accepts_exact_released"]
        and checks["parallel_profile_successor_accepts_exact_successor"]
        and checks["external_profile_not_artifact_version_selects_validator"]
    )

    if all(checks.values()) and old_consumer_breaks and translation_unsafe and parallel_supported:
        disposition = "SUPPORTED_PARALLEL_VERSIONING_AND_BREAKING_CHANGE_SIGNAL"
    elif not old_consumer_breaks and any(
        item["released_1_0_validator_accepts"]
        and item["provenance_fingerprint_equal_to_successor"]
        for item in downgrades
    ):
        disposition = "SUPPORTED_LOSSLESS_BACKWARD_COMPATIBILITY"
    else:
        disposition = "INCONCLUSIVE_VERSION_COMPATIBILITY_APPARATUS_INVALID"

    result = {
        "research_disposition": disposition,
        "observed_compatibility": {
            "released_1_0_accepts_released_1_0": not released_strict_errors,
            "released_1_0_accepts_successor": not legacy_rejects_successor_errors,
            "successor_accepts_successor": not successor_errors,
            "existing_strict_1_0_consumer_breaks_on_successor": old_consumer_breaks,
            "validator_valid_semantic_laundering_downgrades": validator_valid_semantic_laundering,
            "lossless_downgrade_available_in_tested_normative_vocabulary": False,
            "safe_migration_pattern": "parallel_exact_version_authority_no_downgrade",
        },
        "semver_evidence": {
            "breaking_for_existing_strict_1_0_consumers": old_consumer_breaks,
            "project_governance_signal_if_later_promoted": "MAJOR" if old_consumer_breaks else "UNRESOLVED",
            "official_version_assigned": False,
        },
        "checks": checks,
        "source_successor_provenance_fingerprint": source_fingerprint,
        "downgrades": downgrades,
        "legacy_successor_rejection_sample": legacy_rejects_successor_errors[:8],
        "interpretation": {
            "translation_adapter_authorized": False,
            "canonical_successor_version_selected": False,
            "released_1_0_mutated": False,
            "production_promotion_authorized": False,
            "contract_e_authorization_evaluated": False,
        },
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "EVALUATION.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (out_dir / "SUCCESSOR.json").write_bytes(successor_raw)
    (out_dir / "SUCCESSOR_CONTRACT_B_INDEX.json").write_bytes(
        released.canonical_bytes(successor_index)
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.repo_root.resolve(), args.out.resolve())
    print(json.dumps({
        "research_disposition": result["research_disposition"],
        "validator_valid_semantic_laundering_downgrades": result["observed_compatibility"]["validator_valid_semantic_laundering_downgrades"],
        "semver_signal": result["semver_evidence"]["project_governance_signal_if_later_promoted"],
    }, sort_keys=True))
    return 0 if result["research_disposition"] == "SUPPORTED_PARALLEL_VERSIONING_AND_BREAKING_CHANGE_SIGNAL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
