#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "artifacts" / "contract-a-rc2-contract-e-gate"
LANE = ROOT / "research" / "contract-a-rc2-contract-e-pipeline-20260901"
sys.path.insert(0, str(LANE))
import pipeline_gate as pg  # type: ignore  # noqa: E402

rc2 = pg.rc2


def sha256_id(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def mechanical_write_input(candidate: dict, template, propositions: list[dict]):
    claims = [
        rc2.ScaffoldClaim(
            claim_id=p["proposition_id"],
            claim_type="extracted_claim",
            claim_text=p["text"],
            support_status="uncertain",
            claim_strength=0.5,
            extraction_fidelity=0.5,
            source_refs=[],
            counterevidence_checked=False,
            counterevidence_found=False,
            downgraded=False,
            downgrade_reason=None,
        )
        for p in propositions
    ]
    registry = rc2.ClaimsRegistry(
        schema_version=template.claims.schema_version,
        run_id=template.claims.run_id,
        generated_at_utc=template.claims.generated_at_utc,
        claims=claims,
    )
    return rc2.CAWriteInput(
        manifest=template.manifest,
        claims=registry,
        sources=template.sources,
        intermediates=None,
    )


def build_projection(candidate: dict, template, name: str, propositions: list[dict]) -> dict:
    work = OUT / "pressure-work" / name
    work.mkdir(parents=True, exist_ok=True)
    legacy_parent = work / "legacy"
    legacy_parent.mkdir()
    write_input = mechanical_write_input(candidate, template, propositions)
    legacy_dir = rc2.write_scaffold_run(write_input, legacy_parent)
    intake = rc2.verify_intake(legacy_dir)
    assert intake.valid and intake.artifact is not None, intake.errors

    bundle_dir = work / "bundle"
    report_path = work / "retrieval.yaml"
    rc2.build_retrieval_bundle(
        legacy_dir,
        bundle_dir,
        config=rc2.RetrievalConfig(retrieval_method="bm25", top_k=5, lexical_score_floor=0.0),
        report_out=report_path,
    )
    assert not rc2.validate_bundle_tree(bundle_dir), rc2.validate_bundle_tree(bundle_dir)
    apparatus = rc2.apparatus_verify(bundle_dir, against_pin="1.2.0")
    assert apparatus.passed, apparatus.errors

    cal_contents = pg.load_bundle(bundle_dir, deviations_dir=work / "cal-deviations")
    claims, evidence_bundle, audit_config = pg.adapt_bundle_to_pipeline(cal_contents)
    assessments = pg.audit_claims(
        claims,
        evidence_bundle,
        audit_config,
        evidence_scopes=pg.build_claim_evidence_scopes(cal_contents),
    )
    c_raw = pg.export_contract_c_bytes(
        contents=cal_contents,
        assessments=assessments,
        evidence_bundle=evidence_bundle,
        audit_config=audit_config,
    )
    c_obj = json.loads(c_raw)
    c_props = {row["proposition"]["proposition_id"]: row for row in c_obj["propositions"]}
    expected = {p["proposition_id"]: p for p in propositions}
    assert set(c_props) == set(expected)
    for pid, p in expected.items():
        assert c_props[pid]["proposition"]["text_sha256"] == p["text_sha256"].removeprefix("sha256:")

    c_path = OUT / f"pressure-contract-c-{name}.json"
    c_path.write_bytes(c_raw)
    return {
        "projection": name,
        "a_handoff_id": candidate["handoff_id"],
        "a_handoff_sha256": candidate["handoff_sha256"],
        "a_work_id": candidate["work"]["work_id"],
        "c_path": str(c_path.relative_to(ROOT)),
        "c_sha256": sha256_id(c_raw),
        "c_result_set_id": c_obj["result_set_id"],
        "b_binding": {
            "contract_version": cal_contents.manifest.schema_version,
            "bundle_id": cal_contents.manifest.bundle_id,
            "bundle_hash": cal_contents.manifest.bundle.bundle_hash,
        },
        "targets": [
            {
                "proposition_id": p["proposition_id"],
                "text": p["text"],
                "text_sha256": p["text_sha256"],
                "role": "parent" if p["proposition_id"] == candidate["root_proposition"]["proposition_id"] else "atom",
                "sequence": p.get("sequence"),
            }
            for p in propositions
        ],
    }


def resealed_reorder(candidate: dict) -> dict:
    changed = json.loads(json.dumps(candidate))
    children = list(reversed(changed["decomposition"]["children"]))
    for index, child in enumerate(children, start=1):
        child["sequence"] = index
    changed["decomposition"]["children"] = children
    changed["handoff_sha256"] = rc2.compute_handoff_sha256(changed)
    rc2.validate_candidate(changed)
    assert changed["handoff_sha256"] != candidate["handoff_sha256"]
    return {
        "original_handoff_sha256": candidate["handoff_sha256"],
        "resealed_handoff_sha256": changed["handoff_sha256"],
        "original_order": [c["proposition_id"] for c in candidate["decomposition"]["children"]],
        "resealed_order": [c["proposition_id"] for c in changed["decomposition"]["children"]],
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    candidate = rc2.make_candidate("declared")
    rc2.validate_candidate(candidate)
    template = rc2.build_fixture_write_input(rc2.PILOT, "baseline")
    parent = candidate["root_proposition"]
    atoms = list(candidate["decomposition"]["children"])
    projections = [
        build_projection(candidate, template, "declared-parent-only", [parent]),
        build_projection(candidate, template, "declared-atoms-only", atoms),
        build_projection(candidate, template, "declared-parent-plus-atoms", [parent, *atoms]),
    ]

    ids = {
        row["projection"]: [t["proposition_id"] for t in row["targets"]]
        for row in projections
    }
    assert ids["declared-parent-only"] == [parent["proposition_id"]]
    assert ids["declared-atoms-only"] == [a["proposition_id"] for a in atoms]
    assert ids["declared-parent-plus-atoms"] == [parent["proposition_id"], *[a["proposition_id"] for a in atoms]]

    report = {
        "schema": "contract-a-rc2-parent-atom-pressure-projections-v1",
        "a_handoff_sha256": candidate["handoff_sha256"],
        "projections": projections,
        "resealed_reorder_control": resealed_reorder(candidate),
        "nonclaim": "These are mechanical research projections of existing A root/child propositions, not new Contract A or Contract E semantics.",
    }
    path = OUT / "PRESSURE-PROJECTIONS.json"
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", "projections": len(projections), "sha256": sha256_id(path.read_bytes())}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
