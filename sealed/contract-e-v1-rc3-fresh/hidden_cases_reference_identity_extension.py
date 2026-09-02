from __future__ import annotations

from copy import deepcopy

from hidden_cases import _request, _state, _target


def extra_cases(r):
    """One minimal case added after the first pre-seal qualification failure.

    The first qualification run showed that a reference-identity-blind mutant
    escaped because the existing bad reference was also the authority target.
    Repairing that target changed the request jurisdiction away from the frozen
    AuthorityState and therefore still denied. This case corrupts a non-target
    supporting reference instead, so ignoring/repairing the bad identity can
    produce a false permit while the authority target remains unchanged.
    """
    state, target = _state(r)
    decision_ref = _target(r, "decision:hidden-reference-blind", "D")
    corrupted = deepcopy(decision_ref)
    corrupted["identity_sha256"] = "sha256:" + "9" * 64
    supporting = [
        {
            "id": "support:D",
            "artifact_type": "contract_d_candidate",
            "ref_id": "D",
        }
    ]
    request = _request(
        r,
        state,
        target,
        references=[target, corrupted],
        supporting=supporting,
    )
    return [
        {
            "id": "NEG-SUPPORT-REF-IDENTITY",
            "family": "request-integrity",
            "tags": ["reference-identity", "support", "false-permit-sentinel", "qualification-repair-1"],
            "state": deepcopy(state),
            "request": deepcopy(request),
        }
    ]
