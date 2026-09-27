"""Claim quality filters — prevent trivial one-liner claim spam."""

from __future__ import annotations

import re
from typing import Any

# Common-knowledge fragments that add noise without domain value.
_TRIVIAL_PATTERNS = (
    re.compile(r"^the sky is blue\.?$", re.I),
    re.compile(r"^water boils at \d+", re.I),
    re.compile(r"^python is a programming language\.?$", re.I),
)


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def filter_claims(
    claims: list[dict[str, Any]],
    *,
    min_text_length: int = 40,
    max_claims: int = 15,
    drop_trivial: bool = True,
) -> tuple[list[dict[str, Any]], list[str]]:
    """Return (kept_claims, reject_reasons).

    - Drops claims shorter than min_text_length (after strip).
    - Deduplicates by normalized text.
    - Drops known trivial patterns.
    - Caps at max_claims (keeps first N after filtering).
    """
    kept: list[dict[str, Any]] = []
    reasons: list[str] = []
    seen: set[str] = set()

    for claim in claims:
        text = (claim.get("text") or "").strip()
        if not text:
            reasons.append("empty text")
            continue
        if len(text) < min_text_length:
            reasons.append(f"too short ({len(text)} < {min_text_length}): {text[:50]}")
            continue
        if drop_trivial and any(p.match(text) for p in _TRIVIAL_PATTERNS):
            reasons.append(f"trivial: {text[:50]}")
            continue
        norm = _normalize(text)
        if norm in seen:
            reasons.append(f"duplicate: {text[:50]}")
            continue
        seen.add(norm)
        kept.append(claim)
        if len(kept) >= max_claims:
            reasons.append(f"cap reached at {max_claims} claims")
            break

    # Re-assign sequential IDs
    for i, claim in enumerate(kept):
        claim["id"] = f"claim-{i+1:03d}"

    return kept, reasons