#!/usr/bin/env python3
"""Self-contained conformance checks for the public RC2 candidate authority."""

from __future__ import annotations

import copy
import json
from pathlib import Path

from validate import CandidateValidationError, compute_handoff_sha256, validate_candidate

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _expect_invalid(value: dict, label: str) -> None:
    try:
        validate_candidate(value)
    except CandidateValidationError:
        return
    raise AssertionError(f"expected invalid candidate: {label}")


def main() -> int:
    valid = sorted(FIXTURES.glob("valid-*.json"))
    invalid = sorted(FIXTURES.glob("invalid-*.json"))
    assert valid, "no valid fixtures"
    assert invalid, "no invalid fixtures"

    for path in valid:
        validate_candidate(_load(path))
        print(f"PASS valid fixture {path.name}")
    for path in invalid:
        _expect_invalid(_load(path), path.name)
        print(f"PASS invalid fixture rejected {path.name}")

    undecomposed = _load(FIXTURES / "valid-undecomposed.json")
    all_of = _load(FIXTURES / "valid-all-of.json")

    explicit_empty = copy.deepcopy(undecomposed)
    explicit_empty["handoff_id"] = "handoff-explicit-empty-sources"
    explicit_empty["sources"] = []
    explicit_empty["handoff_sha256"] = compute_handoff_sha256(explicit_empty)
    validate_candidate(explicit_empty)
    print("PASS explicitly empty sources is distinct valid state")

    omitted_sources = copy.deepcopy(explicit_empty)
    del omitted_sources["sources"]
    _expect_invalid(omitted_sources, "omitted sources")
    print("PASS omitted required sources fails closed")

    missing_state = copy.deepcopy(undecomposed)
    missing_state["decomposition"] = {}
    _expect_invalid(missing_state, "missing decomposition state")
    print("PASS missing decomposition state fails closed")

    not_decomposed = copy.deepcopy(undecomposed)
    failed = _load(FIXTURES / "valid-failed-decomposition.json")
    unknown = _load(FIXTURES / "valid-unknown-decomposition.json")
    assert len({
        not_decomposed["handoff_sha256"],
        failed["handoff_sha256"],
        unknown["handoff_sha256"],
    }) == 3
    print("PASS not_decomposed, failed, and unknown have distinct immutable bindings")

    unsupported_operator = copy.deepcopy(all_of)
    unsupported_operator["decomposition"]["operator"] = "any_of"
    unsupported_operator["handoff_sha256"] = compute_handoff_sha256(unsupported_operator)
    _expect_invalid(unsupported_operator, "unsupported operator")
    print("PASS unsupported composition relation rejected")

    one_child = copy.deepcopy(all_of)
    one_child["decomposition"]["children"] = one_child["decomposition"]["children"][:1]
    one_child["handoff_sha256"] = compute_handoff_sha256(one_child)
    _expect_invalid(one_child, "all_of with one child")
    print("PASS all_of requires at least two children")

    sequence_gap = copy.deepcopy(all_of)
    sequence_gap["decomposition"]["children"][1]["sequence"] = 3
    sequence_gap["handoff_sha256"] = compute_handoff_sha256(sequence_gap)
    _expect_invalid(sequence_gap, "sequence gap")
    print("PASS child sequence must be exact and contiguous")

    parent_substitution = copy.deepcopy(all_of)
    before = parent_substitution["handoff_sha256"]
    parent_substitution["root_proposition"]["proposition_id"] = "different-parent"
    after = compute_handoff_sha256(parent_substitution)
    assert before != after
    parent_substitution["handoff_sha256"] = before
    _expect_invalid(parent_substitution, "parent identity substitution without reseal")
    print("PASS parent identity substitution changes immutable binding")

    child_substitution = copy.deepcopy(all_of)
    before = child_substitution["handoff_sha256"]
    child_substitution["decomposition"]["children"][0]["proposition_id"] = "different-child"
    after = compute_handoff_sha256(child_substitution)
    assert before != after
    child_substitution["handoff_sha256"] = before
    _expect_invalid(child_substitution, "child identity substitution without reseal")
    print("PASS child identity substitution changes immutable binding")

    source_substitution = copy.deepcopy(undecomposed)
    before = source_substitution["handoff_sha256"]
    source_substitution["sources"][0]["source_id"] = "different-source"
    after = compute_handoff_sha256(source_substitution)
    assert before != after
    source_substitution["handoff_sha256"] = before
    _expect_invalid(source_substitution, "source identity substitution without reseal")
    print("PASS source identity substitution changes immutable binding")

    work_substitution = copy.deepcopy(undecomposed)
    before = work_substitution["handoff_sha256"]
    work_substitution["work"]["work_id"] = "different-work"
    after = compute_handoff_sha256(work_substitution)
    assert before != after
    work_substitution["handoff_sha256"] = before
    _expect_invalid(work_substitution, "work identity substitution without reseal")
    print("PASS work-object identity substitution changes immutable binding")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
