from __future__ import annotations

import importlib.util
import json
from copy import deepcopy
from pathlib import Path

HERE = Path(__file__).resolve().parent
REFERENCE = HERE / "candidate" / "reference.py"

spec = importlib.util.spec_from_file_location("contract_e_rc2_frozen_reference", REFERENCE)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load frozen RC2 reference")
e = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e)


def target_ref() -> dict:
    kind = "test_target"
    version = "1"
    immutable_id = "fractional-currentness-target"
    return {
        "ref_id": "T",
        "kind": kind,
        "version": version,
        "immutable_id": immutable_id,
        "identity_sha256": e.reference_identity(kind, version, immutable_id),
    }


def state(*, valid_from: str, valid_until: str | None, revoked_at: str | None) -> tuple[dict, dict]:
    target = target_ref()
    out = {
        "schema": e.STATE_SCHEMA,
        "authority_state_id": "sha256:" + "0" * 64,
        "records": [
            {
                "id": "auth:root",
                "basis_type": "policy",
                "subject_id": "actor:operator",
                "domain": "knowledge",
                "operation": "knowledge.cite_as_evidence",
                "scope": "claim",
                "target_class": "test_target",
                "target_ref": target["identity_sha256"],
                "valid_from": valid_from,
                "valid_until": valid_until,
                "revoked_at": revoked_at,
                "parent_id": None,
                "delegated_by": None,
            }
        ],
    }
    out["authority_state_id"] = e.authority_state_identity(out)
    return out, target


def request(s: dict, target: dict, at: str) -> dict:
    return {
        "schema": e.REQUEST_SCHEMA,
        "request_id": "req:fractional-currentness",
        "authority_state_id": s["authority_state_id"],
        "evaluation_time": at,
        "subject_id": "actor:operator",
        "jurisdiction": {
            "domain": "knowledge",
            "operation": "knowledge.cite_as_evidence",
            "scope": "claim",
            "target_class": "test_target",
            "target_ref": target["identity_sha256"],
        },
        "references": [deepcopy(target)],
        "supporting_artifacts": [],
        "conflicts": [],
        "residues": [],
    }


def run_case(case_id: str, s: dict, target: dict, at: str, exact_expected: bool) -> dict:
    r = request(s, target, at)
    receipt = e.evaluate(s, r)
    observed = receipt.get("authorized") is True
    return {
        "id": case_id,
        "evaluation_time": at,
        "valid_from": s["records"][0]["valid_from"],
        "valid_until": s["records"][0]["valid_until"],
        "revoked_at": s["records"][0]["revoked_at"],
        "exact_expected_authorized": exact_expected,
        "observed_authorized": observed,
        "match": observed == exact_expected,
        "receipt_id": receipt.get("receipt_id"),
        "diagnostics": receipt.get("diagnostics"),
    }


def main() -> int:
    cases = []

    # The request is one 10^-7 second BEFORE valid_from. Exact ordering requires denial.
    s, t = state(
        valid_from="2026-09-02T18:00:00.1234568Z",
        valid_until="2026-09-02T19:00:00Z",
        revoked_at=None,
    )
    cases.append(run_case(
        "FRACTION-PRE-VALID-FROM",
        s,
        t,
        "2026-09-02T18:00:00.1234567Z",
        False,
    ))

    # The request is one 10^-7 second AFTER valid_until. Exact ordering requires denial.
    s, t = state(
        valid_from="2026-09-02T17:00:00Z",
        valid_until="2026-09-02T18:00:00.1234567Z",
        revoked_at=None,
    )
    cases.append(run_case(
        "FRACTION-POST-VALID-UNTIL",
        s,
        t,
        "2026-09-02T18:00:00.1234568Z",
        False,
    ))

    # The request is one 10^-7 second BEFORE revocation. Exact ordering requires authorization.
    s, t = state(
        valid_from="2026-09-02T17:00:00Z",
        valid_until="2026-09-02T19:00:00Z",
        revoked_at="2026-09-02T18:00:00.1234568Z",
    )
    cases.append(run_case(
        "FRACTION-PRE-REVOCATION",
        s,
        t,
        "2026-09-02T18:00:00.1234567Z",
        True,
    ))

    failures = [item["id"] for item in cases if not item["match"]]
    result = {
        "schema": "contract-e-rc2-fractional-currentness-discriminator-v1",
        "frozen_candidate_commit": "44c919ea7f571b9a01ccf420ac710822c29476e4",
        "frozen_reference_blob": "fda14bb18c66c51747b7b506abb8df8a55a8d166",
        "semantic_rule_under_test": "UTC fractional timestamps admitted by the schema are chronologically ordered at their stated precision without host-microsecond truncation",
        "case_count": len(cases),
        "match_count": len(cases) - len(failures),
        "mismatch_ids": failures,
        "cases": cases,
        "scientific_state": "SUPPORTED" if not failures else "FALSIFIED",
    }
    Path("RC2-FRACTIONAL-CURRENTNESS-DISCRIMINATOR.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
