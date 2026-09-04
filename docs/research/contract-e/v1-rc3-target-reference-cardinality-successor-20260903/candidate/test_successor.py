from __future__ import annotations

import importlib.util
from copy import deepcopy
from pathlib import Path

import reference as e

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
PREDECESSOR_TEST_PATH = (
    REPO
    / "docs/research/contract-e/v1-rc3-exact-currentness-jcs-20260902/candidate/test_candidate.py"
)

_spec = importlib.util.spec_from_file_location(
    "contract_e_v1_rc3_predecessor_tests", PREDECESSOR_TEST_PATH
)
if _spec is None or _spec.loader is None:
    raise RuntimeError(f"cannot load predecessor tests: {PREDECESSOR_TEST_PATH}")
predecessor = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(predecessor)
predecessor.e = e


def expect(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(label)


def run_predecessor_controls() -> int:
    groups = {
        "JCS_REGRESSIONS": predecessor.test_canonicalization(),
        "EXACT_TIME_PRIMITIVES": predecessor.test_exact_time(),
        "FRACTIONAL_CURRENTNESS": predecessor.test_fractional_currentness(),
        "DUAL_STATE_IDENTITY": predecessor.test_dual_identity(),
        "AUTHORITY_BOUNDARIES": predecessor.test_authority_boundaries(),
        "REQUEST_AND_SUPPORT": predecessor.test_request_integrity_and_support(),
        "BLOCKERS": predecessor.test_blockers(),
        "SAFE_PRESERVATION": predecessor.test_preservation(),
    }
    total = sum(groups.values())
    expect(total == 62, f"predecessor control cardinality drifted: {total}")
    return total


def test_duplicate_valid_target_identities() -> None:
    state, target = predecessor.make_state()
    duplicate = deepcopy(target)
    duplicate["ref_id"] = "T2"
    req = predecessor.request(state, target, references=[target, duplicate])
    valid, errors = e.validate_request(req)
    expect(not valid, "duplicate valid target identities validated")
    expect(errors == ["target_reference_ambiguous"], f"unexpected duplicate-target classification: {errors}")
    expect(not e.evaluate(state, req)["authorized"], "duplicate valid target identities authorized")


def test_one_valid_plus_one_invalid_duplicate() -> None:
    state, target = predecessor.make_state()
    invalid = deepcopy(target)
    invalid["ref_id"] = "T2"
    # Same semantic target tuple, but a false supplied identity: it is not a
    # validated reference and therefore makes the request structurally invalid.
    invalid["identity_sha256"] = "sha256:" + "f" * 64
    req = predecessor.request(state, target, references=[target, invalid])
    valid, errors = e.validate_request(req)
    expect(not valid, "valid target plus invalid duplicate validated")
    expect(errors == ["malformed_request"], f"unexpected invalid-duplicate classification: {errors}")
    expect(not e.evaluate(state, req)["authorized"], "valid target plus invalid duplicate authorized")


def test_target_resolution_multiple_matches_among_other_refs() -> None:
    state, target = predecessor.make_state()
    duplicate = deepcopy(target)
    duplicate["ref_id"] = "T2"
    unrelated = predecessor.target("target:unrelated", "U")
    req = predecessor.request(
        state,
        target,
        references=[unrelated, target, duplicate],
    )
    valid, errors = e.validate_request(req)
    expect(not valid, "multiple target matches among unrelated references validated")
    expect(errors == ["target_reference_ambiguous"], f"unexpected multi-match classification: {errors}")
    expect(not e.evaluate(state, req)["authorized"], "multiple target matches authorized")


def main() -> None:
    predecessor_count = run_predecessor_controls()
    test_duplicate_valid_target_identities()
    test_one_valid_plus_one_invalid_duplicate()
    test_target_resolution_multiple_matches_among_other_refs()
    successor_count = 3
    print("CONTRACT_E_V1_RC3_TARGET_REFERENCE_CARDINALITY_SUCCESSOR_TESTS_PASS")
    print(f"PREDECESSOR_ASSERTED_CONTROLS={predecessor_count}")
    print(f"NEW_TARGET_CARDINALITY_CONTROLS={successor_count}")
    print(f"TOTAL_ASSERTED_CONTROLS={predecessor_count + successor_count}")


if __name__ == "__main__":
    main()
