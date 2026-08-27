"""Research-only Contract B optional-extension + minimality probe.

This experiment treats the completed V0/V1/V2 conformance result as prior evidence.
It does not modify canonical Contract B models or assign a production schema version.

The probe asks two distinct questions:
1. Can the V1 factual capabilities be carried by a backward-compatible optional
   companion extension while untouched legacy C-B artifacts remain valid?
2. Which V1 capability families can be ablated without losing a preregistered
   consumer, provenance, reconstruction, or auditability property?

A hash-bound companion ledger is tested as a packaging hypothesis so that
capability necessity is not confused with inline-field necessity.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any, Literal, Mapping

from pydantic import BaseModel, ConfigDict, ValidationError

ROOT = Path(__file__).resolve().parents[1]
EB_ROOT = Path(os.environ["EB_ROOT"]).resolve()
CAL_ROOT = Path(os.environ["CAL_ROOT"]).resolve()
RESULTS_DIR = Path(os.environ.get("RESULTS_DIR", ROOT / "experiment-results"))
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(EB_ROOT / "src"))

from evidence_bundler.experiments.contract_b_seam_probe import (  # noqa: E402
    build_cal_measurement_view,
    build_handoff_variant,
    canonical_hash,
    find_audit_judgment_keys,
    load_fixture,
)
from validators.verify_contract_integrity import verify  # noqa: E402

FIXTURE_PATH = EB_ROOT / "examples" / "contract-b-seam" / "tri-repo-fixture.yaml"
LEGACY_CB_PATH = CAL_ROOT / "tests" / "fixtures" / "cb" / "evidence-bundle-minimal"
PRIOR_REPORT_SHA = "f4ee2dbd853821ba54328156bbab1c71235fae55"
EXPECTED_EB_SHA = "b4ca9111f5957ef7e7955e2c5024f2280ee19eb5"
EXPECTED_CAL_SHA = "6acc3462dad73959ccec6bccf8407215f5274cf6"
EXPECTED_CANDIDATE_SHA = "63e8506396132a44ebc0e6c2312047e99b1125eb"
PROFILE = "contract-b-factual-context-research-v1"
LEDGER_LOCATION = "companion:evidence-world-ledger"

PROPOSITION_SPECIFIC_KEYS = {
    "proposition_specific_relation",
    "semantic_validity",
    "temporal_applicability",
    "authority_applicability",
    "decision_participation",
    "completeness_conclusion",
    "verdict",
}

REQUIRED_MECHANICAL_FACTS = {
    "fact-old-validation-version",
    "fact-old-validation-date",
    "fact-incident-version",
    "fact-incident-date",
    "fact-supplier-identity",
    "fact-supplier-qualification-status",
    "fact-current-validation-version",
    "fact-current-validation-date",
    "fact-current-validation-status",
}


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class LedgerDigest(StrictModel):
    algorithm: Literal["sha256"]
    digest: str
    location: str


class OptionalFactualContextExtension(StrictModel):
    """Research representation of an optional Contract-B extension binding.

    This is deliberately a capability-binding model, not a proposed production
    file or field name.
    """

    profile: Literal["contract-b-factual-context-research-v1"]
    evidence_world_ledger: LedgerDigest


def _git_sha(path: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(path), "rev-parse", "HEAD"], text=True
    ).strip()


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def _hash(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _tree_digest(path: Path) -> str:
    entries: list[tuple[str, str]] = []
    for item in sorted(p for p in path.rglob("*") if p.is_file()):
        rel = item.relative_to(path).as_posix()
        entries.append((rel, hashlib.sha256(item.read_bytes()).hexdigest()))
    return _hash(entries)


def _known_bool(value: bool) -> dict[str, Any]:
    return {"state": "known", "value": value}


def _decode_bool_state(value: Any) -> tuple[str, bool | None]:
    if not isinstance(value, Mapping):
        return "missing", None
    state = value.get("state")
    if state == "known" and isinstance(value.get("value"), bool):
        return "known", bool(value["value"])
    if state == "unknown" and "value" not in value:
        return "unknown", None
    return "invalid", None


def extract_capability_ledger(v1: Mapping[str, Any]) -> dict[str, Any]:
    """Translate V1 object shape into semantic capability families first."""
    claim = deepcopy(dict(v1["claim"]))
    sources = deepcopy(list(v1["sources"]))
    passages = deepcopy(list(v1["passages"]))
    links = deepcopy(list(v1["links"]))
    coverage = deepcopy(dict(v1["coverage"]))

    closed_world = coverage["search_scope"]["closed_world"]
    coverage["search_scope"]["closed_world"] = _known_bool(bool(closed_world))

    return {
        "profile": PROFILE,
        "claim_identity_origin_atomicity": claim,
        "provenance_bound_sources_and_context": sources,
        "representation_bound_passages": passages,
        "retrieval_nomination_and_admission_history": links,
        "coverage_and_aperture_observations": coverage,
    }


def build_extension_ref(ledger: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "profile": PROFILE,
        "evidence_world_ledger": {
            "algorithm": "sha256",
            "digest": _hash(ledger),
            "location": LEDGER_LOCATION,
        },
    }


def validate_extension_ref(ref: Mapping[str, Any], ledger: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    try:
        parsed = OptionalFactualContextExtension.model_validate(ref)
    except ValidationError as exc:
        return [f"extension_validation:{err['loc']}:{err['msg']}" for err in exc.errors()]
    if parsed.evidence_world_ledger.digest != _hash(ledger):
        errors.append("ledger_hash_mismatch")
    if parsed.evidence_world_ledger.location != LEDGER_LOCATION:
        errors.append("ledger_location_mismatch")
    leaked = find_audit_judgment_keys(ledger)
    if leaked:
        errors.append("proposition_specific_semantic_leak:" + ",".join(sorted(leaked)))
    return errors


def legacy_projection(v0: Mapping[str, Any]) -> dict[str, Any]:
    """Remove V1-only claim context from the generous V0 research projection.

    The real locked ClaimAuditUnit has claim_id/text but no general origin or
    atomicity surface. Stripping those two keys prevents the V0 fixture helper
    from accidentally donating extension information to the candidate probe.
    """
    out = deepcopy(dict(v0))
    claim = out.get("claim")
    if isinstance(claim, dict):
        claim.pop("origin", None)
        claim.pop("atomicity", None)
    return out


def _records_by_id(records: Any, key: str) -> dict[str, dict[str, Any]]:
    if not isinstance(records, list):
        return {}
    result: dict[str, dict[str, Any]] = {}
    for record in records:
        if isinstance(record, dict) and isinstance(record.get(key), str):
            result[record[key]] = record
    return result


def _admitted_v0_passages(v0: Mapping[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for key in ("evidence_passages", "counterevidence_passages"):
        raw = v0.get(key, [])
        if isinstance(raw, list):
            records.extend(deepcopy([r for r in raw if isinstance(r, dict)]))
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for item in records:
        pid = item.get("passage_id")
        if isinstance(pid, str) and pid not in seen:
            seen.add(pid)
            unique.append(item)
    return sorted(unique, key=lambda x: str(x.get("passage_id")))


def _derive_counts_from_history(ledger: Mapping[str, Any]) -> dict[str, int] | None:
    links = ledger.get("retrieval_nomination_and_admission_history")
    if not isinstance(links, list) or not links:
        return None
    candidate_count = 0
    reviewed_count = 0
    admitted_count = 0
    for link in links:
        if not isinstance(link, Mapping):
            return None
        candidate_count += 1
        review = link.get("review")
        if not isinstance(review, Mapping):
            return None
        decision = review.get("decision")
        if decision != "needs-review":
            reviewed_count += 1
        if decision == "accepted":
            admitted_count += 1
    return {
        "candidate_count": candidate_count,
        "reviewed_count": reviewed_count,
        "admitted_count": admitted_count,
    }


def consume(
    v0: Mapping[str, Any],
    extension_ref: Mapping[str, Any] | None,
    ledger: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Fail-closed research CAL intake over V0 + optional bound capability ledger."""
    if extension_ref is None:
        return {
            "status": "limited",
            "absence_semantics": "legacy_absent",
            "unknowns": [
                "claim_origin",
                "claim_atomicity",
                "source_context_facts",
                "representation_anchors",
                "coverage_counts",
                "search_scope",
                "limitations",
            ],
            "derived_fields": [],
            "fabricated_defaults": [],
            "measurement_view": None,
        }
    if ledger is None:
        return {
            "status": "limited",
            "absence_semantics": "extension_present_ledger_unavailable",
            "unknowns": ["evidence_world_ledger"],
            "derived_fields": [],
            "fabricated_defaults": [],
            "measurement_view": None,
        }

    ref_errors = validate_extension_ref(extension_ref, ledger)
    if ref_errors:
        return {
            "status": "rejected",
            "absence_semantics": "extension_present_invalid",
            "unknowns": [],
            "derived_fields": [],
            "fabricated_defaults": [],
            "errors": ref_errors,
            "measurement_view": None,
        }

    unknowns: list[str] = []
    derived: list[str] = []
    claim = deepcopy(dict(v0.get("claim", {})))
    claim_cap = ledger.get("claim_identity_origin_atomicity")
    if isinstance(claim_cap, Mapping):
        for key in ("origin", "atomicity"):
            if key in claim_cap:
                claim[key] = deepcopy(claim_cap[key])
            else:
                unknowns.append(f"claim.{key}")
    else:
        unknowns.extend(["claim.origin", "claim.atomicity"])

    admitted_v0 = _admitted_v0_passages(v0)
    admitted_ids = [str(p["passage_id"]) for p in admitted_v0 if "passage_id" in p]
    source_ids = sorted(
        {str(p["source_id"]) for p in admitted_v0 if isinstance(p.get("source_id"), str)}
    )

    sources_by_id = _records_by_id(
        ledger.get("provenance_bound_sources_and_context"), "source_id"
    )
    source_view: list[dict[str, Any]] = []
    for sid in source_ids:
        source = sources_by_id.get(sid)
        if source is None:
            unknowns.append(f"source.{sid}")
            continue
        entry: dict[str, Any] = {"source_id": sid}
        for field in ("title", "source_type", "content_hash", "context_facts"):
            if field in source:
                entry[field] = deepcopy(source[field])
            else:
                unknowns.append(f"source.{sid}.{field}")
        source_view.append(entry)

    passages_by_id = _records_by_id(ledger.get("representation_bound_passages"), "passage_id")
    passage_view: list[dict[str, Any]] = []
    for base in admitted_v0:
        pid = str(base.get("passage_id"))
        cap = passages_by_id.get(pid)
        entry: dict[str, Any] = {
            "passage_id": pid,
            "source_id": base.get("source_id"),
            "text": base.get("text"),
        }
        if cap is None:
            unknowns.extend([f"passage.{pid}.passage_hash", f"passage.{pid}.anchors"])
        else:
            for field in ("passage_hash", "anchors"):
                if field in cap:
                    entry[field] = deepcopy(cap[field])
                else:
                    unknowns.append(f"passage.{pid}.{field}")
        passage_view.append(entry)

    coverage_cap = ledger.get("coverage_and_aperture_observations")
    coverage_view: dict[str, Any] = {}
    if isinstance(coverage_cap, Mapping):
        if "claim_id" in coverage_cap:
            coverage_view["claim_id"] = coverage_cap["claim_id"]
        else:
            unknowns.append("coverage.claim_id")

        derived_counts = _derive_counts_from_history(ledger)
        for field in ("candidate_count", "reviewed_count", "admitted_count"):
            if field in coverage_cap:
                coverage_view[field] = coverage_cap[field]
            elif derived_counts is not None:
                coverage_view[field] = derived_counts[field]
                derived.append(f"coverage.{field}:derived_from_complete_review_history")
            else:
                unknowns.append(f"coverage.{field}")

        if "outcome" in coverage_cap:
            coverage_view["outcome"] = coverage_cap["outcome"]
        else:
            unknowns.append("coverage.outcome")

        search_scope = coverage_cap.get("search_scope")
        if isinstance(search_scope, Mapping):
            scope_out: dict[str, Any] = {}
            for field in ("source_ids", "source_selection_basis"):
                if field in search_scope:
                    scope_out[field] = deepcopy(search_scope[field])
                else:
                    unknowns.append(f"coverage.search_scope.{field}")
            state, value = _decode_bool_state(search_scope.get("closed_world"))
            if state == "known":
                scope_out["closed_world"] = value
            elif state == "unknown":
                unknowns.append("coverage.search_scope.closed_world:explicit_unknown")
            else:
                unknowns.append("coverage.search_scope.closed_world")
            coverage_view["search_scope"] = scope_out
        else:
            unknowns.append("coverage.search_scope")

        if "limitations" in coverage_cap:
            coverage_view["limitations"] = deepcopy(coverage_cap["limitations"])
        else:
            unknowns.append("coverage.limitations")
    else:
        unknowns.append("coverage")

    measurement_view = {
        "bundle_id": v0.get("bundle_id"),
        "claim": claim,
        "sources": source_view,
        "admitted_passages": passage_view,
        "coverage": coverage_view,
    }
    return {
        "status": "ready" if not unknowns else "limited",
        "absence_semantics": "extension_present",
        "unknowns": sorted(set(unknowns)),
        "derived_fields": derived,
        "fabricated_defaults": [],
        "measurement_view": measurement_view,
        "measurement_view_hash": canonical_hash(measurement_view),
        "admitted_passage_ids": admitted_ids,
    }


def capability_properties(ledger: Mapping[str, Any]) -> dict[str, bool]:
    claim = ledger.get("claim_identity_origin_atomicity")
    claim_origin = isinstance(claim, Mapping) and "origin" in claim
    atomicity = isinstance(claim, Mapping) and "atomicity" in claim

    sources = ledger.get("provenance_bound_sources_and_context")
    source_records = sources if isinstance(sources, list) else []
    source_provenance = bool(source_records) and all(
        isinstance(s, Mapping)
        and all(k in s for k in ("source_id", "content_hash", "source_trust_level"))
        for s in source_records
    )
    fact_ids: set[str] = set()
    fact_provenance_ok = True
    for source in source_records:
        if not isinstance(source, Mapping):
            fact_provenance_ok = False
            continue
        facts = source.get("context_facts")
        if not isinstance(facts, list):
            fact_provenance_ok = False
            continue
        for fact in facts:
            if not isinstance(fact, Mapping):
                fact_provenance_ok = False
                continue
            fid = fact.get("fact_id")
            if isinstance(fid, str):
                fact_ids.add(fid)
            prov = fact.get("provenance")
            if not isinstance(prov, Mapping) or not isinstance(prov.get("passage_id"), str):
                fact_provenance_ok = False

    passages = ledger.get("representation_bound_passages")
    passage_records = passages if isinstance(passages, list) else []
    passage_hashes = bool(passage_records) and all(
        isinstance(p, Mapping) and isinstance(p.get("passage_hash"), str)
        for p in passage_records
    )
    typed_anchors = bool(passage_records) and all(
        isinstance(p, Mapping)
        and isinstance(p.get("anchors"), list)
        and bool(p["anchors"])
        and all(
            isinstance(a, Mapping)
            and isinstance(a.get("type"), str)
            and "value" in a
            for a in p["anchors"]
        )
        for p in passage_records
    )

    links = ledger.get("retrieval_nomination_and_admission_history")
    link_records = links if isinstance(links, list) else []
    nomination = bool(link_records) and all(
        isinstance(link, Mapping) and isinstance(link.get("nomination"), Mapping)
        for link in link_records
    )
    review = bool(link_records) and all(
        isinstance(link, Mapping) and isinstance(link.get("review"), Mapping)
        for link in link_records
    )
    rejected_reconstructable = False
    if review:
        passage_ids = {
            str(p.get("passage_id"))
            for p in passage_records
            if isinstance(p, Mapping) and isinstance(p.get("passage_id"), str)
        }
        for link in link_records:
            if not isinstance(link, Mapping):
                continue
            rv = link.get("review")
            if isinstance(rv, Mapping) and rv.get("decision") == "rejected":
                rejected_reconstructable = str(link.get("passage_id")) in passage_ids

    coverage = ledger.get("coverage_and_aperture_observations")
    explicit_counts = isinstance(coverage, Mapping) and all(
        k in coverage for k in ("candidate_count", "reviewed_count", "admitted_count")
    )
    derived_counts = _derive_counts_from_history(ledger)
    counts_reconstructable = explicit_counts or derived_counts is not None
    search_scope = isinstance(coverage, Mapping) and isinstance(coverage.get("search_scope"), Mapping)
    limitations = isinstance(coverage, Mapping) and "limitations" in coverage
    closed_world_state_ok = False
    if search_scope:
        state, _ = _decode_bool_state(coverage["search_scope"].get("closed_world"))
        closed_world_state_ok = state in {"known", "unknown"}

    trust_metadata = bool(source_records) and all(
        isinstance(s, Mapping) and "source_trust_level" in s for s in source_records
    )

    return {
        "claim_origin_provenance": claim_origin,
        "claim_atomicity_known": atomicity,
        "source_provenance_bound": source_provenance,
        "required_mechanical_facts_present": REQUIRED_MECHANICAL_FACTS <= fact_ids,
        "context_fact_provenance_valid": fact_provenance_ok and bool(fact_ids),
        "passage_hashes_present": passage_hashes,
        "typed_representation_anchors_present": typed_anchors,
        "nomination_history_reconstructable": nomination,
        "admission_review_history_reconstructable": review,
        "rejected_candidate_reconstructable": rejected_reconstructable,
        "coverage_counts_explicit": explicit_counts,
        "coverage_counts_reconstructable": counts_reconstructable,
        "search_scope_present": search_scope,
        "closed_world_state_explicit": closed_world_state_ok,
        "limitations_explicit": limitations,
        "source_trust_fact_preserved": trust_metadata,
        "no_proposition_specific_cal_semantics": not bool(find_audit_judgment_keys(ledger)),
    }


BROKEN_PROPERTIES = {
    "claim_origin_provenance",
    "source_provenance_bound",
    "context_fact_provenance_valid",
    "passage_hashes_present",
    "typed_representation_anchors_present",
    "nomination_history_reconstructable",
    "admission_review_history_reconstructable",
    "rejected_candidate_reconstructable",
}
DEGRADED_PROPERTIES = {
    "claim_atomicity_known",
    "required_mechanical_facts_present",
    "coverage_counts_reconstructable",
    "search_scope_present",
    "closed_world_state_explicit",
    "limitations_explicit",
    "source_trust_fact_preserved",
}


def classify(
    baseline_props: Mapping[str, bool],
    ablated_props: Mapping[str, bool],
    baseline_consume: Mapping[str, Any],
    ablated_consume: Mapping[str, Any],
) -> tuple[str, list[str]]:
    if ablated_props.get("no_proposition_specific_cal_semantics") is False:
        return "SEMANTIC LEAK", ["proposition_specific_cal_semantics_entered_upstream"]
    if ablated_consume.get("fabricated_defaults"):
        return "SEMANTIC LEAK", ["consumer_fabricated_defaults"]

    lost = sorted(
        key for key, was_true in baseline_props.items() if was_true and not ablated_props.get(key, False)
    )
    if any(prop in BROKEN_PROPERTIES for prop in lost):
        return "BROKEN", lost
    if any(prop in DEGRADED_PROPERTIES for prop in lost):
        return "HONESTLY DEGRADED", lost
    if ablated_consume.get("status") == "limited" and baseline_consume.get("status") == "ready":
        return "HONESTLY DEGRADED", lost or list(ablated_consume.get("unknowns", []))
    return "EQUIVALENT", lost


def ablate(ledger: Mapping[str, Any], family: str) -> dict[str, Any]:
    out = deepcopy(dict(ledger))
    claim = out.get("claim_identity_origin_atomicity")
    sources = out.get("provenance_bound_sources_and_context")
    passages = out.get("representation_bound_passages")
    links = out.get("retrieval_nomination_and_admission_history")
    coverage = out.get("coverage_and_aperture_observations")

    if family == "claim_origin_atomicity":
        if isinstance(claim, dict):
            claim.pop("origin", None)
            claim.pop("atomicity", None)
    elif family == "claim_origin":
        if isinstance(claim, dict):
            claim.pop("origin", None)
    elif family == "claim_atomicity":
        if isinstance(claim, dict):
            claim.pop("atomicity", None)
    elif family == "source_provenance":
        if isinstance(sources, list):
            for source in sources:
                if isinstance(source, dict):
                    for key in ("title", "source_type", "content_hash", "source_trust_level"):
                        source.pop(key, None)
    elif family == "source_trust_level":
        if isinstance(sources, list):
            for source in sources:
                if isinstance(source, dict):
                    source.pop("source_trust_level", None)
    elif family == "context_facts":
        if isinstance(sources, list):
            for source in sources:
                if isinstance(source, dict):
                    source["context_facts"] = []
    elif family == "typed_representation_anchors":
        if isinstance(passages, list):
            for passage in passages:
                if isinstance(passage, dict):
                    passage.pop("anchors", None)
    elif family == "passage_hashes":
        if isinstance(passages, list):
            for passage in passages:
                if isinstance(passage, dict):
                    passage.pop("passage_hash", None)
    elif family == "nomination_history":
        if isinstance(links, list):
            for link in links:
                if isinstance(link, dict):
                    link.pop("nomination", None)
    elif family == "admission_review_history":
        if isinstance(links, list):
            for link in links:
                if isinstance(link, dict):
                    link.pop("review", None)
    elif family == "coverage_counts":
        if isinstance(coverage, dict):
            for key in ("candidate_count", "reviewed_count", "admitted_count"):
                coverage.pop(key, None)
    elif family in {"candidate_count", "reviewed_count", "admitted_count"}:
        if isinstance(coverage, dict):
            coverage.pop(family, None)
    elif family == "search_scope":
        if isinstance(coverage, dict):
            coverage.pop("search_scope", None)
    elif family == "limitations_explicit_unknown":
        if isinstance(coverage, dict):
            coverage.pop("limitations", None)
    else:
        raise ValueError(f"unknown ablation family: {family}")
    return out


def main() -> int:
    pins = {
        "apparatus_experiment": _git_sha(ROOT),
        "evidence_bundler": _git_sha(EB_ROOT),
        "claim_audit_lab": _git_sha(CAL_ROOT),
        "prior_report": PRIOR_REPORT_SHA,
        "candidate_profile_base": EXPECTED_CANDIDATE_SHA,
    }
    pin_errors: list[str] = []
    if pins["evidence_bundler"] != EXPECTED_EB_SHA:
        pin_errors.append("evidence_bundler_head_mismatch")
    if pins["claim_audit_lab"] != EXPECTED_CAL_SHA:
        pin_errors.append("claim_audit_lab_head_mismatch")
    try:
        subprocess.check_call(
            ["git", "merge-base", "--is-ancestor", PRIOR_REPORT_SHA, pins["apparatus_experiment"]],
            cwd=ROOT,
        )
        subprocess.check_call(
            ["git", "merge-base", "--is-ancestor", EXPECTED_CANDIDATE_SHA, pins["apparatus_experiment"]],
            cwd=ROOT,
        )
    except subprocess.CalledProcessError:
        pin_errors.append("apparatus_expected_ancestor_missing")

    fixture = load_fixture(FIXTURE_PATH)
    v0_raw = build_handoff_variant(fixture, "current_cb")
    v0 = legacy_projection(v0_raw)
    v1 = build_handoff_variant(fixture, "minimal_context")
    prior_view = build_cal_measurement_view(v1)
    prior_view_hash = canonical_hash(prior_view)

    ledger = extract_capability_ledger(v1)
    extension_ref = build_extension_ref(ledger)
    extension_errors = validate_extension_ref(extension_ref, ledger)

    # C1: untouched, previously-qualified real legacy C-B artifact remains valid.
    legacy_digest_before = _tree_digest(LEGACY_CB_PATH)
    legacy_report = verify(LEGACY_CB_PATH)
    legacy_digest_after = _tree_digest(LEGACY_CB_PATH)
    c1 = {
        "legacy_path": str(LEGACY_CB_PATH),
        "existing_verifier_passed": legacy_report.passed,
        "errors": legacy_report.errors,
        "tree_digest_before": legacy_digest_before,
        "tree_digest_after": legacy_digest_after,
        "untouched": legacy_digest_before == legacy_digest_after,
        "extension_state": "legacy_absent",
    }

    # C2: V1 capabilities cross only through an optional hash-bound companion ledger.
    baseline_consume = consume(v0, extension_ref, ledger)
    c2 = {
        "extension_validation_errors": extension_errors,
        "consumer_status": baseline_consume.get("status"),
        "candidate_measurement_view_hash": baseline_consume.get("measurement_view_hash"),
        "prior_v1_measurement_view_hash": prior_view_hash,
        "measurement_equivalent": baseline_consume.get("measurement_view_hash") == prior_view_hash,
        "proposition_specific_keys_in_ledger": sorted(find_audit_judgment_keys(ledger)),
    }

    # C3: known false, explicit unknown, and pre-extension absence stay distinct.
    false_ledger = deepcopy(ledger)
    false_scope = false_ledger["coverage_and_aperture_observations"]["search_scope"]
    false_scope["closed_world"] = _known_bool(False)
    false_state = _decode_bool_state(false_scope["closed_world"])

    unknown_ledger = deepcopy(ledger)
    unknown_scope = unknown_ledger["coverage_and_aperture_observations"]["search_scope"]
    unknown_scope["closed_world"] = {"state": "unknown"}
    unknown_state = _decode_bool_state(unknown_scope["closed_world"])

    legacy_state = ("legacy_absent", None)
    c3 = {
        "present_false": {"state": false_state[0], "value": false_state[1]},
        "present_unknown": {"state": unknown_state[0], "value": unknown_state[1]},
        "legacy_absent": {"state": legacy_state[0], "value": legacy_state[1]},
        "distinct": len({str(false_state), str(unknown_state), str(legacy_state)}) == 3,
    }

    # C4: no extension means explicit limitation, never a factual default.
    legacy_consume = consume(v0, None, None)
    c4 = {
        "status": legacy_consume["status"],
        "absence_semantics": legacy_consume["absence_semantics"],
        "unknowns": legacy_consume["unknowns"],
        "fabricated_defaults": legacy_consume["fabricated_defaults"],
        "passes": legacy_consume["status"] == "limited"
        and legacy_consume["absence_semantics"] == "legacy_absent"
        and not legacy_consume["fabricated_defaults"],
    }

    baseline_props = capability_properties(ledger)
    families = [
        "claim_origin_atomicity",
        "source_provenance",
        "context_facts",
        "typed_representation_anchors",
        "passage_hashes",
        "nomination_history",
        "admission_review_history",
        "coverage_counts",
        "search_scope",
        "limitations_explicit_unknown",
    ]
    micro_ablations = [
        "claim_origin",
        "claim_atomicity",
        "source_trust_level",
        "candidate_count",
        "reviewed_count",
        "admitted_count",
    ]

    ablation_rows: list[dict[str, Any]] = []
    for family in families + micro_ablations:
        candidate = ablate(ledger, family)
        candidate_ref = build_extension_ref(candidate)
        consumed = consume(v0, candidate_ref, candidate)
        props = capability_properties(candidate)
        outcome, lost = classify(baseline_props, props, baseline_consume, consumed)
        ablation_rows.append(
            {
                "family": family,
                "scope": "required_family" if family in families else "micro_ablation",
                "outcome": outcome,
                "lost_properties": lost,
                "consumer_status": consumed.get("status"),
                "measurement_hash": consumed.get("measurement_view_hash"),
                "measurement_equivalent": consumed.get("measurement_view_hash")
                == baseline_consume.get("measurement_view_hash"),
                "unknowns": consumed.get("unknowns", []),
                "derived_fields": consumed.get("derived_fields", []),
                "fabricated_defaults": consumed.get("fabricated_defaults", []),
            }
        )

    equivalent = [r["family"] for r in ablation_rows if r["outcome"] == "EQUIVALENT"]
    degraded = [r["family"] for r in ablation_rows if r["outcome"] == "HONESTLY DEGRADED"]
    broken = [r["family"] for r in ablation_rows if r["outcome"] == "BROKEN"]
    leaks = [r["family"] for r in ablation_rows if r["outcome"] == "SEMANTIC LEAK"]

    hard_falsifiers = {
        "legacy_invalidated": not (c1["existing_verifier_passed"] and c1["untouched"]),
        "new_fields_cannot_be_optional": not (c2["measurement_equivalent"] and not extension_errors),
        "existing_fields_require_incompatible_reinterpretation": False,
        "legacy_absence_collapses_false_unknown": not c3["distinct"],
        "cal_fabricates_defaults_without_extension": bool(c4["fabricated_defaults"]),
        "mandatory_new_packaging_required": False,
        "substantial_v1_fields_removable_without_property_loss": bool(equivalent),
        "proposition_specific_cal_semantics_required_upstream": bool(
            c2["proposition_specific_keys_in_ledger"]
        ),
    }

    # Capability minimality distinguishes capability removal from representation
    # redundancy. Count *fields* may be derivable while the coverage-accounting
    # capability survives.
    capability_minimality_supported = all(
        row["outcome"] != "EQUIVALENT"
        for row in ablation_rows
        if row["scope"] == "required_family" and row["family"] != "coverage_counts"
    ) and not leaks
    count_representation_redundant = any(
        row["family"] == "coverage_counts" and row["outcome"] == "EQUIVALENT"
        for row in ablation_rows
    )

    overall_pass = (
        not pin_errors
        and c1["existing_verifier_passed"]
        and c1["untouched"]
        and c2["measurement_equivalent"]
        and not extension_errors
        and c3["distinct"]
        and c4["passes"]
        and not leaks
    )

    result = {
        "experiment": "Contract B Optional-Extension + Minimality",
        "status": "research_only",
        "pins": pins,
        "pin_errors": pin_errors,
        "prior_evidence": {
            "prior_report_sha": PRIOR_REPORT_SHA,
            "prior_v1_measurement_view_hash": prior_view_hash,
            "fixture_sha256": "sha256:4d5a900232cd243d82fffdc6a5422d32287e9496f3e9728ae684e1ef04fdc7cf",
        },
        "capability_extraction": {
            "ledger_hash": _hash(ledger),
            "families": list(ledger.keys()),
            "proposition_specific_keys": sorted(find_audit_judgment_keys(ledger)),
            "baseline_properties": baseline_props,
        },
        "compatibility": {"C1": c1, "C2": c2, "C3": c3, "C4": c4},
        "ablations": ablation_rows,
        "summary": {
            "equivalent": equivalent,
            "honestly_degraded": degraded,
            "broken": broken,
            "semantic_leaks": leaks,
            "capability_minimality_supported_for_required_families_except_derived_counts": capability_minimality_supported,
            "coverage_count_representation_redundant_for_fixture": count_representation_redundant,
            "hard_falsifiers": hard_falsifiers,
            "overall_probe_pass": overall_pass,
        },
        "packaging_observation": {
            "optional_hash_bound_companion_works": c2["measurement_equivalent"],
            "canonical_inline_v1_fields_required_by_this_probe": False,
            "companion_ledger_required_when_extension_present": True,
            "legacy_artifacts_require_companion": False,
        },
        "limits": [
            "Single synthetic evidence world cannot prove universal field-level minimality.",
            "Coverage-count derivability depends on the fixture invariant that complete candidate/review history is retained.",
            "The probe establishes optional companion compatibility structurally; it does not choose production file names or a final schema version.",
            "A hash binding proves identity/integrity only when the companion ledger remains available to the consumer.",
        ],
    }

    out_json = RESULTS_DIR / "result.json"
    out_json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Contract B Optional-Extension + Minimality Probe Output",
        "",
        f"- Apparatus experiment SHA: `{pins['apparatus_experiment']}`",
        f"- Evidence Bundler SHA: `{pins['evidence_bundler']}`",
        f"- Claim Audit Lab SHA: `{pins['claim_audit_lab']}`",
        f"- Prior report SHA: `{PRIOR_REPORT_SHA}`",
        f"- Prior V1 measurement view: `{prior_view_hash}`",
        f"- Candidate ledger hash: `{_hash(ledger)}`",
        "",
        "## Compatibility",
        "",
        f"- C1 legacy unchanged + valid: `{c1['existing_verifier_passed'] and c1['untouched']}`",
        f"- C2 V1-capable optional ledger equivalence: `{c2['measurement_equivalent']}`",
        f"- C3 false / unknown / legacy absence distinct: `{c3['distinct']}`",
        f"- C4 legacy CAL fail-closed: `{c4['passes']}`",
        "",
        "## Ablation matrix",
        "",
        "| Family | Scope | Outcome | Measurement equivalent | Lost property | Derived / unknown |",
        "|---|---|---|---:|---|---|",
    ]
    for row in ablation_rows:
        detail = "; ".join(row["derived_fields"] or row["unknowns"])
        lost = ", ".join(row["lost_properties"])
        lines.append(
            f"| {row['family']} | {row['scope']} | {row['outcome']} | "
            f"{row['measurement_equivalent']} | {lost} | {detail} |"
        )
    lines.extend(
        [
            "",
            "## Machine interpretation",
            "",
            f"- Required-family capability minimality (except derivable count representation): `{capability_minimality_supported}`",
            f"- Coverage-count representation redundant in this fixture: `{count_representation_redundant}`",
            f"- Semantic leaks: `{leaks}`",
            f"- Probe pass: `{overall_pass}`",
            "",
            "See `result.json` for the complete property vectors and hard-falsifier record.",
        ]
    )
    (RESULTS_DIR / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(result["summary"], indent=2, sort_keys=True))
    return 0 if overall_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
