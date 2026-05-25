"""Spec/canonical vocabulary cross-check verifier.

Parses the controlled-vocabulary table in ``handoff-contract-v1.0.0.md`` and
asserts that each vocabulary's value set is identical to the corresponding list
in ``schema/vocabulary.yaml``.

The table is identified by section header (case-insensitive prefix match on
"Controlled Vocabulary Summary"). Within the table each row carries:

- column 1: the vocabulary field name in backticks, e.g. \\`workflow_condition\\`
- column 2: a comma-separated list of backtick-quoted values

Exit codes:
    0 - spec table and canonical YAML agree on every vocabulary
    1 - any divergence (missing vocabulary, missing values, extra values)
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from ._vocabulary import CANONICAL_VOCAB_PATH, load_canonical

# Section heading that introduces the controlled-vocabulary table.
_TABLE_HEADING_PATTERN = re.compile(
    r"^#{2,4}\s+Controlled\s+Vocabulary\s+Summary",
    re.IGNORECASE,
)
# Tokens like `workflow_condition` or `baseline` inside a table cell.
_BACKTICK_TOKEN = re.compile(r"`([a-z][a-z0-9_]*)`")


@dataclass(frozen=True)
class SpecVocabulary:
    """One row of the spec's controlled-vocabulary table."""

    name: str
    values: list[str]


def parse_spec_table(spec_text: str) -> dict[str, list[str]]:
    """Return ``{vocab_name: [values]}`` parsed from the spec markdown table."""
    lines = spec_text.splitlines()
    table_start = None
    for idx, line in enumerate(lines):
        if _TABLE_HEADING_PATTERN.match(line.strip()):
            table_start = idx
            break
    if table_start is None:
        raise ValueError(
            "Could not locate '## Controlled Vocabulary Summary' heading in spec"
        )

    table: dict[str, list[str]] = {}
    in_table = False
    saw_separator = False
    for line in lines[table_start + 1 :]:
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            in_table = True
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if len(cells) < 2:
                continue
            # Header row: "| Field | Values |" — cells = ["Field", "Values"].
            # Separator row: "|---|---|" — cells contain only dashes.
            if not saw_separator and all(set(c) <= set("-:") for c in cells):
                saw_separator = True
                continue
            if not saw_separator:
                continue  # header row before separator
            name_matches = _BACKTICK_TOKEN.findall(cells[0])
            if not name_matches:
                continue  # not a vocabulary row (e.g., empty or prose row)
            name = name_matches[0]
            values = _BACKTICK_TOKEN.findall(cells[1])
            table[name] = values
        elif in_table:
            # End of table — first non-pipe line after the table body.
            break
    return table


@dataclass(frozen=True)
class Divergence:
    vocab_name: str
    only_in_spec: list[str]
    only_in_yaml: list[str]


def compare(
    spec_table: dict[str, list[str]],
    canonical: dict[str, list[str]],
) -> list[Divergence]:
    """Return per-vocabulary divergences between spec and canonical."""
    divergences: list[Divergence] = []
    names = set(spec_table) | set(canonical)
    for name in sorted(names):
        spec_values = set(spec_table.get(name, []))
        yaml_values = set(canonical.get(name, []))
        if spec_values == yaml_values:
            continue
        divergences.append(
            Divergence(
                vocab_name=name,
                only_in_spec=sorted(spec_values - yaml_values),
                only_in_yaml=sorted(yaml_values - spec_values),
            )
        )
    return divergences


def run(
    *,
    spec_path: Path | None = None,
    vocab_path: Path | None = None,
) -> int:
    """Execute the verifier and return the exit code."""
    asset_root = Path(__file__).resolve().parent.parent
    spec = spec_path or (asset_root / "handoff-contract-v1.0.0.md")
    vocab = vocab_path or CANONICAL_VOCAB_PATH

    spec_table = parse_spec_table(spec.read_text(encoding="utf-8"))
    canonical = load_canonical(vocab)

    divergences = compare(spec_table, canonical.vocabularies)
    if not divergences:
        print(
            "spec/canonical vocabulary parity: OK "
            f"({len(canonical.vocabularies)} vocabularies)"
        )
        return 0

    print("spec/canonical vocabulary parity: FAIL")
    for div in divergences:
        print(f"  {div.vocab_name}:")
        if div.only_in_spec:
            print(f"    only in spec markdown: {div.only_in_spec}")
        if div.only_in_yaml:
            print(f"    only in vocabulary.yaml: {div.only_in_yaml}")
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="verify-spec-vocabulary",
        description="Cross-check the spec markdown's controlled-vocabulary "
        "table against schema/vocabulary.yaml.",
    )
    parser.add_argument("--spec", type=Path, default=None, help="Path to spec markdown")
    parser.add_argument(
        "--vocabulary", type=Path, default=None, help="Path to canonical vocabulary.yaml"
    )
    args = parser.parse_args(argv)
    return run(spec_path=args.spec, vocab_path=args.vocabulary)


if __name__ == "__main__":
    sys.exit(main())
