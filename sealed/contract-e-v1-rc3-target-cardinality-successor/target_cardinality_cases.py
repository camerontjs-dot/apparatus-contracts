from __future__ import annotations

import importlib.util
from copy import deepcopy
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PREDECESSOR_HIDDEN_PATH = REPO / "sealed/contract-e-v1-rc3-fresh/hidden_cases.py"


def _load_predecessor_hidden():
    spec = importlib.util.spec_from_file_location(
        "contract_e_v1_rc3_predecessor_hidden_for_cardinality", PREDECESSOR_HIDDEN_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load predecessor hidden cases: {PREDECESSOR_HIDDEN_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def extra_cases(r) -> list[dict[str, Any]]:
    h = _load_predecessor_hidden()
    out: list[dict[str, Any]] = []
    state, target = h._state(r)

    duplicate = deepcopy(target)
    duplicate["ref_id"] = "T2"
    h._add(
        out,
        "NEG-TARGET-DUPLICATE-VALID-IDENTITY",
        "target-reference-cardinality",
        ["target-resolution", "exactly-one", "cardinality-falsifier"],
        state,
        h._request(r, state, target, references=[target, duplicate]),
    )

    invalid_duplicate = deepcopy(target)
    invalid_duplicate["ref_id"] = "T2"
    invalid_duplicate["identity_sha256"] = "sha256:" + "f" * 64
    h._add(
        out,
        "NEG-TARGET-VALID-PLUS-INVALID-DUPLICATE",
        "target-reference-cardinality",
        ["target-resolution", "validated-reference", "structural-invalidity"],
        state,
        h._request(r, state, target, references=[target, invalid_duplicate]),
    )

    unrelated = h._target(r, "target:unrelated", "U")
    duplicate_among_others = deepcopy(target)
    duplicate_among_others["ref_id"] = "T2"
    h._add(
        out,
        "NEG-TARGET-MULTIPLE-MATCHES",
        "target-reference-cardinality",
        ["target-resolution", "exactly-one", "multiple-matches", "cardinality-falsifier"],
        state,
        h._request(
            r,
            state,
            target,
            references=[unrelated, target, duplicate_among_others],
        ),
    )

    return out
