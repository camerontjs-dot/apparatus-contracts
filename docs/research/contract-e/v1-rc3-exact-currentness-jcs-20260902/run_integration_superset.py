from __future__ import annotations

import sys
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import integration_profile as profile
import test_integration_profile as base


def expect_profile_error(case_id: str, mutate) -> None:
    intent = {
        "schema": "execution-intent-candidate-v1",
        "executable_sha256": "sha256:" + "a" * 64,
        "entry_point": "dispatch_exact_task",
        "arguments": ["--once"],
        "input_identities": ["decision:sha256:" + "b" * 64],
        "environment_constraints": {"network": "disabled"},
        "side_effect_targets": ["task:fixture"],
    }
    mutate(intent)
    try:
        profile.execution_intent_identity(intent)
    except profile.ProfileError:
        base.check(case_id, "execution-intent-shape", True)
    else:
        raise AssertionError(f"{case_id}: malformed intent accepted")


def main() -> None:
    # Eight real preregistered-adjacent shape controls. These run before the
    # original 112-case matrix, bringing the integration surface above 101
    # without relaxing or rewriting any original assertion.
    expect_profile_error("EXT-INTENT-UNKNOWN", lambda x: x.__setitem__("unknown", True))
    expect_profile_error("EXT-INTENT-MISSING", lambda x: x.pop("entry_point"))
    expect_profile_error("EXT-INTENT-SCHEMA", lambda x: x.__setitem__("schema", "future"))
    expect_profile_error("EXT-INTENT-EXE", lambda x: x.__setitem__("executable_sha256", "not-a-hash"))
    expect_profile_error("EXT-INTENT-ARGS", lambda x: x.__setitem__("arguments", "--once"))
    expect_profile_error("EXT-INTENT-INPUTS", lambda x: x.__setitem__("input_identities", [None]))
    expect_profile_error("EXT-INTENT-ENV", lambda x: x.__setitem__("environment_constraints", []))
    expect_profile_error("EXT-INTENT-SIDE", lambda x: x.__setitem__("side_effect_targets", [None]))

    base.main()


if __name__ == "__main__":
    main()
