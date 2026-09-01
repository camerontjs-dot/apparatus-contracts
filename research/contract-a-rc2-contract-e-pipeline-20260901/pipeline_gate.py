#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "artifacts" / "contract-a-rc2-contract-e-gate"
A_ROOT = ROOT / "_external" / "a"
REF = A_ROOT / "research" / "contract-a-minimality-rc2-20260901" / "reference"
sys.path.insert(0, str(REF))
import run_conformance_v3 as v3  # type: ignore  # noqa: E402

rc2 = v3.rc2

from claim_audit_lab.auditor import audit_claims  # noqa: E402
from claim_audit_lab.contracts.adapter import adapt_bundle_to_pipeline, build_claim_evidence_scopes  # noqa: E402
from claim_audit_lab.contracts.bundle_loader import load_bundle  # noqa: E402
from claim_audit_lab.contracts.contract_c import export_contract_c_bytes  # noqa: E402

EXPECTED_HANDOFFS = {
    "declared": "sha256:de23b0eb66b3316e85bd9fbc73f4dfe2b6525a1e73783fca8d6e1fbd9bb0189d",
    "not_decomposed": "sha256:2816c5e36d70fc4d7a48223500be8ff480fc535b6eac7a74c6f5f11057550148",
    "failed": "sha256:fe4c0ea6a3955594c74d9ea4d40cd4a0542baa836f53561332aa7f2108da39d4",
    "unknown": "sha256:ada57eddefb02c65f6af65394a9f5e43e7a08bde1c3f37453668aa7102788f25",
}


def sha256_id(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def props(candidate: dict) -> dict[str, dict]:
    return {row["proposition_id"]: row for row in rc2.semantic_propositions(candidate)}


def build_case(state: str, name: str, observations: dict, template) -> dict:
    candidate = rc2.make_candidate(state)
    assert candidate["handoff_sha256"] == EXPECTED_HANDOFFS[state]
    rc2.validate_candidate(candidate)

    work = OUT / "work" / name
    work.mkdir(parents=True, exist_ok=True)
    contents, _legacy, _factual = rc2.build_b_variant(
        name=name,
        candidate=candidate,
        template=template,
        observations=observations,
        tmp=work,
    )
    bundle_dir = work / f"bundle-{name}"
    a_props = props(candidate)
    b_claims = {row.claim_id: row for row in contents.claims}
    assert set(b_claims) == set(a_props)
    for pid, a_prop in a_props.items():
        assert b_claims[pid].claim_text == a_prop["text"]

    cal_contents = load_bundle(bundle_dir, deviations_dir=work / "cal-deviations")
    claims, evidence_bundle, audit_config = adapt_bundle_to_pipeline(cal_contents)
    assessments = audit_claims(
        claims,
        evidence_bundle,
        audit_config,
        evidence_scopes=build_claim_evidence_scopes(cal_contents),
    )
    c_raw = export_contract_c_bytes(
        contents=cal_contents,
        assessments=assessments,
        evidence_bundle=evidence_bundle,
        audit_config=audit_config,
    )
    c_obj = json.loads(c_raw)
    c_props = {row["proposition"]["proposition_id"]: row for row in c_obj["propositions"]}
    assert set(c_props) == set(a_props)
    for pid, a_prop in a_props.items():
        assert c_props[pid]["proposition"]["text_sha256"] == a_prop["text_sha256"].removeprefix("sha256:")

    c_path = OUT / f"contract-c-{name}.json"
    c_path.write_bytes(c_raw)
    sig = rc2._bundle_semantic_signature(contents)
    evidence_source_ids = sorted({sid for claim in sig.values() for sid, _passage, _text in claim["evidence"] + claim["counterevidence"]})
    source_ids = [row["source_id"] for row in candidate["sources"]]
    assert set(evidence_source_ids).issubset(set(source_ids))

    return {
        "name": name,
        "state": state,
        "a_handoff_id": candidate["handoff_id"],
        "a_handoff_sha256": candidate["handoff_sha256"],
        "a_work_id": candidate["work"]["work_id"],
        "a_producer": candidate["producer"],
        "a_source_ids": source_ids,
        "a_source_hashes": {row["source_id"]: row["content_sha256"] for row in candidate["sources"]},
        "b_binding": {
            "contract_version": cal_contents.manifest.schema_version,
            "bundle_id": cal_contents.manifest.bundle_id,
            "bundle_hash": cal_contents.manifest.bundle.bundle_hash,
        },
        "b_evidence_source_ids": evidence_source_ids,
        "c_path": str(c_path.relative_to(ROOT)),
        "c_sha256": sha256_id(c_raw),
        "c_result_set_id": c_obj["result_set_id"],
        "targets": [
            {
                "proposition_id": pid,
                "text": row["text"],
                "text_sha256": row["text_sha256"],
                "sequence": row.get("sequence"),
            }
            for pid, row in a_props.items()
        ],
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    template = rc2.build_fixture_write_input(rc2.PILOT, "baseline")
    cases = [
        build_case(state, state, rc2._compat_observations(), template)
        for state in ("not_decomposed", "failed", "unknown", "declared")
    ]
    hostile = rc2._compat_observations(
        support_status="unsupported",
        claim_strength=0.01,
        extraction_fidelity=0.01,
        counterevidence_checked=True,
        counterevidence_found=True,
        downgraded=True,
        downgrade_reason="excluded compatibility observation",
        source_refs=True,
        trust_level="background",
        retrieval_query="hostile upstream query text",
        retrieval_rank=99,
        access_date_utc="1999-01-01T00:00:00Z",
        model_prompt_config=True,
        workflow_condition="format_only",
        timestamp_utc="1999-01-01T00:00:00Z",
    )
    hostile_case = build_case("declared", "declared-hostile-excluded-metadata", hostile, template)
    baseline = next(row for row in cases if row["state"] == "declared")
    assert hostile_case["a_handoff_sha256"] == baseline["a_handoff_sha256"]
    assert hostile_case["targets"] == baseline["targets"]
    cases.append(hostile_case)

    receipt = {
        "schema": "contract-a-rc2-contract-e-pipeline-predecision-v1",
        "preregistration_commit": "b13ba252bb2a48336402baebbdf854f7874f52b7",
        "cases": cases,
    }
    path = OUT / "PREDECISION.json"
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", "cases": len(cases), "receipt_sha256": sha256_id(path.read_bytes())}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
