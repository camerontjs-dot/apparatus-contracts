"""Tests for ``validators.verify_vocabulary``."""

from __future__ import annotations

from pathlib import Path

from validators import verify_vocabulary


def test_passing_against_real_consumers(asset_root: Path, capsys) -> None:
    """The real portfolio layout (CAL + EB at 1.1.0) should verify clean."""
    rc = verify_vocabulary.run(asset_root=asset_root)
    captured = capsys.readouterr().out
    assert rc == 0, f"unexpected failure:\n{captured}"
    assert "vocabulary verification passed." in captured


def test_passing_against_synthetic_layout(consumer_layout: Path, capsys) -> None:
    """A clean synthetic sibling layout should pass."""
    rc = verify_vocabulary.run(asset_root=consumer_layout)
    captured = capsys.readouterr().out
    assert rc == 0, captured


def test_drift_detected_on_mutated_consumer(consumer_layout: Path, capsys) -> None:
    """Mutating a consumer's vocabulary.yaml should produce a DRIFT report."""
    target = consumer_layout.parent / "claim-audit-lab" / "schema" / "vocabulary.yaml"
    body = target.read_text(encoding="utf-8")
    target.write_text(body + "\n# tampered\n", encoding="utf-8")

    rc = verify_vocabulary.run(asset_root=consumer_layout)
    captured = capsys.readouterr().out
    assert rc == 1
    assert "[DRIFT]" in captured
    assert "claim-audit-lab" in captured


def test_pin_mismatch_detected(consumer_layout: Path, capsys) -> None:
    """A wrong .contract-version pin should produce a PIN-DIFF report."""
    target = (
        consumer_layout.parent / "evidence-bundler" / "schema" / ".contract-version"
    )
    target.write_text("1.0.0\n", encoding="utf-8")

    rc = verify_vocabulary.run(asset_root=consumer_layout)
    captured = capsys.readouterr().out
    assert rc == 1
    assert "evidence-bundler" in captured
    assert "1.0.0" in captured  # the wrong pin value


def test_absent_consumer_silent_without_strict(consumer_layout: Path, capsys) -> None:
    """A missing consumer should not fail by default."""
    schema_dir = (
        consumer_layout.parent / "research-scaffold-harness" / "schema"
    )
    (schema_dir / "vocabulary.yaml").unlink()
    (schema_dir / ".contract-version").unlink()

    rc = verify_vocabulary.run(asset_root=consumer_layout)
    captured = capsys.readouterr().out
    assert rc == 0
    assert "[absent]" in captured


def test_absent_consumer_fails_with_strict(consumer_layout: Path, capsys) -> None:
    """A missing consumer should fail when ``strict=True``."""
    schema_dir = (
        consumer_layout.parent / "research-scaffold-harness" / "schema"
    )
    (schema_dir / "vocabulary.yaml").unlink()
    (schema_dir / ".contract-version").unlink()

    rc = verify_vocabulary.run(asset_root=consumer_layout, strict=True)
    captured = capsys.readouterr().out
    assert rc == 1
    assert "[MISSING]" in captured
