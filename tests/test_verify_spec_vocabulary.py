"""Tests for ``validators.verify_spec_vocabulary``."""

from __future__ import annotations

from pathlib import Path

import pytest

from validators import verify_spec_vocabulary


def test_passing_against_real_spec(spec_path: Path, canonical_vocab_path: Path, capsys) -> None:
    """Real spec markdown and canonical YAML should agree after the v1.1.0 amendment."""
    rc = verify_spec_vocabulary.run(spec_path=spec_path, vocab_path=canonical_vocab_path)
    captured = capsys.readouterr().out
    assert rc == 0, f"unexpected failure:\n{captured}"
    assert "OK" in captured


def test_divergence_detected_when_value_dropped_from_yaml(
    spec_path: Path, canonical_vocab_path: Path, tmp_path: Path, capsys
) -> None:
    """Removing a value from the canonical YAML should produce a divergence."""
    tampered = tmp_path / "vocabulary.yaml"
    body = canonical_vocab_path.read_text(encoding="utf-8")
    # Drop the `format_only` line wholesale; the spec's table still lists it.
    mutated = body.replace("      - format_only", "      # removed")
    assert mutated != body, "expected to find format_only in canonical YAML"
    tampered.write_text(mutated, encoding="utf-8")

    rc = verify_spec_vocabulary.run(spec_path=spec_path, vocab_path=tampered)
    captured = capsys.readouterr().out
    assert rc == 1
    assert "workflow_condition" in captured
    assert "format_only" in captured


def test_divergence_detected_when_value_dropped_from_spec(
    spec_path: Path, canonical_vocab_path: Path, tmp_path: Path, capsys
) -> None:
    """Removing a value from the spec table should produce a divergence."""
    tampered_spec = tmp_path / "spec.md"
    body = spec_path.read_text(encoding="utf-8")
    # Remove `not_checkable` from the spec's audit_support_verdict row.
    mutated = body.replace(", `not_checkable`", "")
    assert mutated != body, "expected to find `not_checkable` reference in spec"
    tampered_spec.write_text(mutated, encoding="utf-8")

    rc = verify_spec_vocabulary.run(spec_path=tampered_spec, vocab_path=canonical_vocab_path)
    captured = capsys.readouterr().out
    assert rc == 1
    assert "audit_support_verdict" in captured


def test_parse_table_finds_known_vocabularies(spec_path: Path) -> None:
    """The parser should recover every vocabulary name from the table."""
    table = verify_spec_vocabulary.parse_spec_table(spec_path.read_text(encoding="utf-8"))
    expected = {
        "workflow_condition",
        "claim_type",
        "support_status",
        "audit_support_verdict",
        "source_type",
        "trust_level",
        "extraction_method",
        "deviation_type",
    }
    assert expected.issubset(set(table.keys())), table.keys()


def test_parse_table_raises_on_missing_heading(tmp_path: Path) -> None:
    """The parser should fail loudly when the expected heading is absent."""
    spec = tmp_path / "spec.md"
    spec.write_text("# No table here\n\nJust prose.", encoding="utf-8")
    with pytest.raises(ValueError):
        verify_spec_vocabulary.parse_spec_table(spec.read_text(encoding="utf-8"))
