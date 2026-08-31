from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

from contract_d_core import semantic_identity, semantic_projection, validate_effect

VALID = json.loads((HERE / "fixtures" / "valid.json").read_text())["fixtures"]


def load(name: str):
    return copy.deepcopy(VALID[name])


@pytest.mark.parametrize(
    ("fixture_name", "effect_type"),
    [
        ("citation-use-clear.json", "knowledge.cite_as_evidence"),
        ("task-dispatch-clear.json", "task.dispatch"),
    ],
)
def test_empty_schema_effect_normalizes_to_total_three_key_shape(fixture_name, effect_type):
    decision = load(fixture_name)
    omitted = copy.deepcopy(decision)
    explicit = copy.deepcopy(decision)
    explicit["effect"]["params"] = {}

    expected = {"type": effect_type, "version": "1", "params": {}}

    assert validate_effect(omitted["effect"]) == expected
    assert validate_effect(explicit["effect"]) == expected
    assert set(validate_effect(omitted["effect"])) == {"type", "version", "params"}
    assert semantic_projection(omitted)["effect"] == expected
    assert semantic_projection(explicit)["effect"] == expected
    assert semantic_identity(omitted) == semantic_identity(explicit)


def test_defaulted_effect_also_has_total_three_key_shape():
    decision = load("source-audit-clear.json")
    omitted = copy.deepcopy(decision)
    omitted["effect"].pop("params")
    explicit_empty = copy.deepcopy(decision)
    explicit_empty["effect"]["params"] = {}
    explicit_default = copy.deepcopy(decision)
    explicit_default["effect"]["params"] = {"scope": "claim"}

    expected = {
        "type": "knowledge.add_verified_tag",
        "version": "1",
        "params": {"scope": "claim"},
    }

    for candidate in (omitted, explicit_empty, explicit_default):
        normalized = validate_effect(candidate["effect"])
        assert normalized == expected
        assert set(normalized) == {"type", "version", "params"}
        assert semantic_projection(candidate)["effect"] == expected

    identities = {semantic_identity(x) for x in (omitted, explicit_empty, explicit_default)}
    assert len(identities) == 1


def test_explicit_object_scope_remains_semantically_distinct():
    claim = load("source-audit-clear.json")
    obj = load("source-audit-object-scope-clear.json")
    assert semantic_projection(claim)["effect"]["params"] == {"scope": "claim"}
    assert semantic_projection(obj)["effect"]["params"] == {"scope": "object"}
    assert semantic_identity(claim) != semantic_identity(obj)
