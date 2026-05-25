"""Loader for the canonical controlled vocabulary at ``schema/vocabulary.yaml``."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

# Resolved at runtime so the loader works from any cwd inside the asset.
_ASSET_ROOT = Path(__file__).resolve().parent.parent
CANONICAL_VOCAB_PATH: Path = _ASSET_ROOT / "schema" / "vocabulary.yaml"
CANONICAL_PIN_PATH: Path = _ASSET_ROOT / "schema" / ".contract-version"


@dataclass(frozen=True)
class CanonicalVocabulary:
    """In-memory representation of ``schema/vocabulary.yaml``."""

    contract_version: str
    locked_at_utc: str
    vocabularies: dict[str, list[str]]

    def values(self, name: str) -> list[str]:
        """Return the value list for one named vocabulary."""
        try:
            return list(self.vocabularies[name])
        except KeyError as exc:
            raise KeyError(f"Unknown vocabulary: {name!r}") from exc

    @property
    def names(self) -> list[str]:
        """Return the names of every vocabulary in declaration order."""
        return list(self.vocabularies)


def load_canonical(path: Path | None = None) -> CanonicalVocabulary:
    """Load and parse the canonical vocabulary YAML."""
    source = path if path is not None else CANONICAL_VOCAB_PATH
    raw: dict[str, Any] = yaml.safe_load(source.read_text(encoding="utf-8"))
    contract_version = str(raw["contract_version"])
    locked_at_utc = str(raw["locked_at_utc"])
    vocabularies_raw: dict[str, Any] = raw["vocabularies"]
    vocabularies: dict[str, list[str]] = {}
    for name, body in vocabularies_raw.items():
        values_raw = body.get("values", [])
        vocabularies[name] = [str(v) for v in values_raw]
    return CanonicalVocabulary(
        contract_version=contract_version,
        locked_at_utc=locked_at_utc,
        vocabularies=vocabularies,
    )


def read_pin(path: Path) -> str:
    """Read a ``.contract-version`` pin file and return the stripped string."""
    return path.read_text(encoding="utf-8").strip()
