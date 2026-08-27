"""Shared test fixtures."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

ASSET_ROOT = Path(__file__).resolve().parent.parent
HANDOFF_DEMO_CA = (
    ASSET_ROOT.parent
    / "evidence-bundler"
    / "examples"
    / "handoff-demo"
    / "scaffold-run-bm25-handoff-demo"
)


@pytest.fixture
def asset_root() -> Path:
    """Path to ``live-asset/apparatus-contracts/``."""
    return ASSET_ROOT


@pytest.fixture
def canonical_vocab_path() -> Path:
    return ASSET_ROOT / "schema" / "vocabulary.yaml"


@pytest.fixture
def canonical_pin_path() -> Path:
    return ASSET_ROOT / "schema" / ".contract-version"


@pytest.fixture
def spec_path() -> Path:
    return ASSET_ROOT / "handoff-contract-v1.0.0.md"


@pytest.fixture
def handoff_demo_ca() -> Path:
    """Real, committed C-A fixture from Evidence Bundler examples."""
    if not HANDOFF_DEMO_CA.exists():
        pytest.skip(f"handoff-demo fixture not present at {HANDOFF_DEMO_CA}")
    return HANDOFF_DEMO_CA


@pytest.fixture
def ca_tree_copy(handoff_demo_ca: Path, tmp_path: Path) -> Path:
    """A tmp copy of the handoff-demo C-A tree, safe to mutate per test."""
    dest = tmp_path / handoff_demo_ca.name
    shutil.copytree(handoff_demo_ca, dest)
    return dest


@pytest.fixture
def consumer_layout(
    tmp_path: Path,
    canonical_vocab_path: Path,
    canonical_pin_path: Path,
) -> Path:
    """Build a tmp sibling layout with consumers matching the canonical pin.

    Returns the sibling-root path. Inside it: ``apparatus-contracts/`` mirrors
    canonical and each consumer directory carries a byte-identical
    ``vocabulary.yaml`` plus a matching ``.contract-version``.
    """
    sibling_root = tmp_path / "live-asset"
    sibling_root.mkdir()

    pin_bytes = canonical_pin_path.read_bytes()
    ac_root = sibling_root / "apparatus-contracts"
    (ac_root / "schema").mkdir(parents=True)
    shutil.copy(canonical_vocab_path, ac_root / "schema" / "vocabulary.yaml")
    (ac_root / "schema" / ".contract-version").write_bytes(pin_bytes)

    for name in ("claim-audit-lab", "evidence-bundler", "research-scaffold-harness"):
        schema_dir = sibling_root / name / "schema"
        schema_dir.mkdir(parents=True)
        shutil.copy(canonical_vocab_path, schema_dir / "vocabulary.yaml")
        (schema_dir / ".contract-version").write_bytes(pin_bytes)
    return ac_root
