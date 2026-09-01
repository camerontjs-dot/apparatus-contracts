#!/usr/bin/env python3
"""Successor runner for the RC2 cross-repository conformance experiment.

Successor reason
----------------
`run_conformance.py` assumed that the normalized supplier proposition was a
literal byte substring of the RSH Markdown source. The pinned source wraps the
same proposition across Markdown lines. Run 33471190603 therefore failed before
any scientific gate executed.

This successor changes only the source-correspondence precondition: boundary and
line-wrap whitespace are normalized for the comparison. The Contract A
proposition bytes, candidate hashes, source bytes, EB queries, compatibility
mutations, Contract B artifacts, and CAL requests remain exactly those produced
by the original experiment.
"""

from __future__ import annotations

import run_conformance as rc2


def _normalized_ws(value: str) -> str:
    return " ".join(value.split())


def _candidate_sources_with_explicit_representation_normalization() -> list[dict[str, str]]:
    packet = rc2.load_source_packet(rc2.PILOT)
    fictional = next(
        source
        for source in packet.sources
        if source.source_id == "src-fictional-compliance-review-note"
    )
    assert _normalized_ws(rc2.PARENT_TEXT) in _normalized_ws(fictional.text), (
        "real RSH pilot source no longer contains the declared root proposition "
        "after line-wrap whitespace normalization"
    )
    return [
        {
            "source_id": source.source_id,
            "media_type": "text/markdown; charset=utf-8",
            "content": source.text,
            "content_sha256": rc2.htext(source.text),
        }
        for source in packet.sources
    ]


# Patch only the failed representation-correspondence precondition. This is
# deliberately visible rather than silently editing the failed runner in place.
rc2._candidate_sources = _candidate_sources_with_explicit_representation_normalization


if __name__ == "__main__":
    print(
        "DEVIATION successor=v2 reason=RSH Markdown line-wrap whitespace "
        "normalized only for source/proposition correspondence"
    )
    raise SystemExit(rc2.main())
