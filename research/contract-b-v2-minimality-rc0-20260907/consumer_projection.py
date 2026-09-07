"""Research-only pre-assessment projection for Contract B v2 RC0.

This file records a correction found before the pressure-test freeze: a target
with zero admitted passages must remain present. The first draft helper in
``candidate.py`` iterated only targets with accepted evidence and therefore
collapsed "zero admitted evidence" into "no proposition". Tests consume this
corrected projection and preserve that pre-freeze defect as research history.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from candidate import Bundle, Passage


def _targets(bundle: Bundle) -> list[dict[str, Any]]:
    decomposition = bundle.declaration.decomposition
    if decomposition["state"] == "declared":
        return [
            {
                "proposition_id": child["proposition_id"],
                "text": child["text"],
                "text_sha256": child["text_sha256"],
            }
            for child in sorted(decomposition["children"], key=lambda item: item["sequence"])
        ]
    return [bundle.declaration.root_proposition.model_dump(mode="json")]


def semantic_measurement_context(bundle: Bundle) -> dict[str, Any]:
    """Return the narrow, order-preserving pre-assessment semantic input.

    Retrieval lane, rank, selection metadata, rejected candidates, aperture and
    reviewer/history metadata are deliberately absent. Every primary target is
    retained even when ``accepted_passages`` is empty.
    """

    source_by_id = {source.source_id: source for source in bundle.sources}
    passage_by_id = {passage.passage_id: passage for passage in bundle.passages}
    accepted_by_target: dict[str, list[Passage]] = defaultdict(list)
    for link in bundle.candidate_links:
        if link.review.state == "accepted":
            accepted_by_target[link.proposition_id].append(passage_by_id[link.passage_id])

    projected_targets: list[dict[str, Any]] = []
    for proposition in _targets(bundle):
        proposition_id = proposition["proposition_id"]
        passages: list[dict[str, Any]] = []
        for passage in sorted(
            accepted_by_target.get(proposition_id, []), key=lambda item: item.passage_id
        ):
            source = source_by_id[passage.source_id]
            passages.append(
                {
                    "passage_id": passage.passage_id,
                    "source_id": passage.source_id,
                    "text": passage.text,
                    "text_sha256": passage.text_sha256,
                    "anchors": [anchor.model_dump(mode="json") for anchor in passage.anchors],
                    "source_context_facts": [
                        fact.model_dump(mode="json") for fact in source.context_facts
                    ],
                }
            )
        projected_targets.append(
            {
                "proposition": proposition,
                "accepted_passages": passages,
            }
        )
    return {"targets": projected_targets}
