"""Executable negative controls that reproduce two RC0 information-loss gaps.

These tests pass only when the RC0 weakness remains reproducible. They are not
acceptance tests for a successor candidate.
"""

from __future__ import annotations

import sys
from copy import deepcopy
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from candidate import seal, validate_bundle  # noqa: E402
from test_candidate import _add_second_candidate, _base_bundle, _load  # noqa: E402


def test_rc0_accepts_silent_planned_lane_omission_after_reseal() -> None:
    a = _load("valid-undecomposed.json")
    b = _base_bundle(a)

    omitted_id = "ret-1-dense"
    b["retrievals"] = [r for r in b["retrievals"] if r["retrieval_id"] != omitted_id]
    for link in b["candidate_links"]:
        link["nominations"] = [n for n in link["nominations"] if n["retrieval_id"] != omitted_id]

    mutated = seal(b)
    parsed = validate_bundle(mutated, a)
    assert all(r.retrieval_id != omitted_id for r in parsed.retrievals)
    assert parsed.aperture[0].execution_state == "complete"


def test_rc0_accepts_silent_tail_candidate_truncation_after_reseal() -> None:
    a = _load("valid-undecomposed.json")
    b = _add_second_candidate(_base_bundle(a))

    second_link = next(link for link in b["candidate_links"] if link["link_id"].endswith("-second"))
    second_passage_id = second_link["passage_id"]
    b["candidate_links"] = [link for link in b["candidate_links"] if link is not second_link]
    b["passages"] = [p for p in b["passages"] if p["passage_id"] != second_passage_id]

    mutated = seal(b)
    parsed = validate_bundle(mutated, a)
    assert all(r.candidate_limit == 2 for r in parsed.retrievals)
    assert len(parsed.candidate_links) == 1
