"""Check controller observations, never candidate-authored success claims.

Source-only v1. Observations here come from an explicitly fake runtime. This
module cannot attest real execution, isolation, causal use, or actor admission.
It imports neither the adapter nor a candidate/evaluator implementation.
"""
from __future__ import annotations


class EvidenceFailure(ValueError):
    pass


def check_execution(request: dict, events: tuple[dict, ...]) -> dict:
    common = {key: request[key] for key in (
        "run_id", "profile_sha256", "candidate_sha256", "evaluator_sha256", "observer_sha256")}
    expected = [{**common, "event": "evaluator_started",
                 "consumed_candidate_sha256": request["candidate_sha256"]}]
    for case in request["cases"]:
        expected.extend((
            {**common, "event": "case_started", "case_id": case},
            {**common, "event": "case_finished", "case_id": case, "passed": True},
        ))
    expected.append({**common, "event": "evaluator_finished", "exit_code": 0})
    if len(events) != len(expected):
        raise EvidenceFailure("EXECUTION_OBSERVATIONS_MISSING_OR_EXTRA")
    for actual, wanted in zip(events, expected):
        # Python True == 1; type equality matters for booleans and exit codes.
        if (type(actual) is not dict or set(actual) != set(wanted) or
                any(type(actual[k]) is not type(v) or actual[k] != v
                    for k, v in wanted.items())):
            raise EvidenceFailure("EXECUTION_OBSERVATIONS_MISMATCH_OR_FAILED_CASE")
    return {"status": "OFFLINE_DEV_TESTS_PASS",
            "evidence_layer": "SYNTHETIC_FAKE_RUNTIME",
            "run_id": request["run_id"], "cases_observed": len(request["cases"]),
            "candidate_sha256": request["candidate_sha256"],
            "observer_sha256": request["observer_sha256"],
            "evaluator_sha256": request["evaluator_sha256"]}
