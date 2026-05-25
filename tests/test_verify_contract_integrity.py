"""Tests for ``validators.verify_contract_integrity``."""

from __future__ import annotations

from pathlib import Path

import yaml

from validators import verify_contract_integrity


def test_passing_against_real_ca_fixture(handoff_demo_ca: Path, capsys) -> None:
    """The real handoff-demo C-A should pass the full integrity check."""
    report = verify_contract_integrity.verify(handoff_demo_ca)
    assert report.errors == [], "\n".join(report.errors)
    assert report.artifact_type == "C-A"
    assert report.passed


def test_missing_contract_version_detected(ca_tree_copy: Path, capsys) -> None:
    """Removing CONTRACT_VERSION should produce a clean failure."""
    (ca_tree_copy / "CONTRACT_VERSION").unlink()
    report = verify_contract_integrity.verify(ca_tree_copy)
    assert not report.passed
    assert any("CONTRACT_VERSION file missing" in e for e in report.errors)


def test_invalid_contract_version_detected(ca_tree_copy: Path) -> None:
    """A bogus CONTRACT_VERSION value should be rejected."""
    (ca_tree_copy / "CONTRACT_VERSION").write_text("9.9.9\n", encoding="utf-8")
    report = verify_contract_integrity.verify(ca_tree_copy)
    assert not report.passed
    assert any("CONTRACT_VERSION is '9.9.9'" in e for e in report.errors)


def test_against_pin_mismatch(ca_tree_copy: Path) -> None:
    """--against-pin should fail when the artifact's pin differs."""
    # The demo ships at 1.0.0; pin against 1.1.0 to force a mismatch.
    report = verify_contract_integrity.verify(ca_tree_copy, against_pin="1.1.0")
    assert not report.passed
    assert any("--against-pin requires '1.1.0'" in e for e in report.errors)


def test_missing_sha256sums_detected(ca_tree_copy: Path) -> None:
    (ca_tree_copy / "SHA256SUMS").unlink()
    report = verify_contract_integrity.verify(ca_tree_copy)
    assert not report.passed
    assert any("SHA256SUMS file missing" in e for e in report.errors)


def test_tampered_file_detected_by_hash(ca_tree_copy: Path) -> None:
    """Appending a byte to a corpus file should trigger a SHA256SUMS mismatch."""
    target = ca_tree_copy / "claims.yaml"
    target.write_bytes(target.read_bytes() + b"# tampered\n")
    report = verify_contract_integrity.verify(ca_tree_copy)
    assert not report.passed
    assert any(
        "claims.yaml" in e and "hash mismatch" in e for e in report.errors
    ), report.errors


def test_invalid_vocabulary_value_rejected(ca_tree_copy: Path) -> None:
    """A workflow_condition value outside the controlled vocabulary should fail."""
    target = ca_tree_copy / "scaffold_run.yaml"
    data = yaml.safe_load(target.read_text(encoding="utf-8"))
    data["workflow_condition"] = "bogus_value"
    target.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    report = verify_contract_integrity.verify(ca_tree_copy)
    assert not report.passed
    # Either the model rejects it as a Literal violation, or the SHA256SUMS
    # check catches the file mutation. Both are valid failure paths.
    assert any(
        "workflow_condition" in e or "scaffold_run.yaml" in e
        for e in report.errors
    ), report.errors


def test_missing_required_field_rejected(ca_tree_copy: Path) -> None:
    """Dropping a required field should produce a schema validation error."""
    target = ca_tree_copy / "scaffold_run.yaml"
    data = yaml.safe_load(target.read_text(encoding="utf-8"))
    del data["task_id"]
    target.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    report = verify_contract_integrity.verify(ca_tree_copy)
    assert not report.passed
    assert any("task_id" in e for e in report.errors), report.errors


def test_unknown_artifact_type_reported(tmp_path: Path) -> None:
    """A directory with neither manifest should report 'unknown'."""
    empty = tmp_path / "empty-artifact"
    empty.mkdir()
    report = verify_contract_integrity.verify(empty)
    assert report.artifact_type == "unknown"
    assert not report.passed
