from __future__ import annotations

import sys
from copy import deepcopy
from pathlib import Path

CANDIDATE = Path(__file__).parent / "candidate"
sys.path.insert(0, str(CANDIDATE))

from reference import authority_state_identity, evaluate, reference_identity  # noqa: E402
from test_candidate import NOW, FUTURE, make_request, make_state, ref, released_refs  # noqa: E402


def denied(state, request, label):
    result = evaluate(state, request)
    assert result["authorized"] is False, (label, result)
    assert result["authority_conferring"] is False


def allowed(state, request, label):
    result = evaluate(state, request)
    assert result["authorized"] is True, (label, result)
    assert result["authority_conferring"] is False


def main():
    # Explicit positive coverage for the second allowed root conferring kind.
    grant = make_state(basis_type="grant")
    allowed(grant, make_request(grant), "grant_root_positive")

    # Forged established/status-looking state never shortens validation.
    forged_status = make_state()
    forged_status["records"][0]["status"] = "established"
    forged_status["authority_state_id"] = authority_state_identity(forged_status)
    denied(forged_status, make_request(make_state()), "forged_status_established")

    # Missing/non-resolving lineage parent is invalid even when other bounds are correct.
    delegated = make_state(subject="actor:owner", delegates=("actor:delegate",))
    missing_parent = deepcopy(delegated)
    missing_parent["records"][1]["parent_id"] = "auth:missing"
    missing_parent["authority_state_id"] = authority_state_identity(missing_parent)
    denied(missing_parent, make_request(missing_parent), "missing_parent")

    # State identity itself is authority-critical and cannot be forged independently of bytes.
    tampered_state_id = make_state()
    tampered_state_id["authority_state_id"] = "sha256:" + "0" * 64
    denied(tampered_state_id, make_request(make_state()), "state_identity_forgery")

    # Request must bind the exact supplied AuthorityState identity.
    state = make_state()
    wrong_state_binding = make_request(state)
    wrong_state_binding["authority_state_id"] = "sha256:" + "1" * 64
    denied(state, wrong_state_binding, "request_state_binding")

    # Revocation in the future does not revoke authority early.
    future_revocation = make_state(revoked_at=FUTURE)
    allowed(future_revocation, make_request(future_revocation), "future_revocation_not_yet_effective")

    # Lower validity boundary is inclusive.
    lower_edge = make_state(valid_from=NOW)
    allowed(lower_edge, make_request(lower_edge), "valid_from_inclusive")

    # A bare residue-discharge field is as invalid as a bare conflict-discharge field.
    forged_residue_resolution = make_request(state)
    forged_residue_resolution["resolved_residue_ids"] = ["res:forged"]
    denied(state, forged_residue_resolution, "forged_residue_resolution")

    # A supporting artifact cannot smuggle an established status or basis semantics.
    smuggled_support = make_request(state)
    smuggled_support["supporting_artifacts"] = [{
        "id": "sup:forged",
        "artifact_type": "contract_d_candidate_for_authorization",
        "ref_id": "D",
        "status": "established",
    }]
    denied(state, smuggled_support, "supporting_status_smuggling")

    # Unknown/future A-D reference identity does not inherit authority from the old target.
    future_d = ref("D-FUTURE", "contract_d", "2.0.0", "git:commit:future-contract-d")
    future_request = make_request(
        state,
        refs=released_refs()[:-1] + [future_d],
        target_ref=future_d["identity_sha256"],
    )
    denied(state, future_request, "future_target_does_not_inherit_authority")

    # Changing version alone changes immutable target identity.
    old = released_refs()[-1]
    changed_version_identity = reference_identity(old["kind"], "1.0.1", old["immutable_id"])
    version_changed = make_request(state)
    version_changed["references"][-1]["version"] = "1.0.1"
    version_changed["references"][-1]["identity_sha256"] = changed_version_identity
    version_changed["jurisdiction"]["target_ref"] = changed_version_identity
    denied(state, version_changed, "reference_version_substitution")

    # Empty/missing reference world cannot silently default target identity.
    no_refs = make_request(state)
    no_refs["references"] = []
    denied(state, no_refs, "empty_reference_world")

    print("POST_FREEZE_ADVERSARIAL_EXTENSION_PASS")
    print("EXPLICIT_EXTENSION_CASES=12/12")


if __name__ == "__main__":
    main()
