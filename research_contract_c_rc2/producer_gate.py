"""Research-only Contract-C RC2 producer information-sufficiency gate.

This apparatus deliberately sits outside the production package. It observes a
pinned real Contract-B -> CAL execution, derives only mechanically attributable
receipt state from public producer inputs/outputs, and challenges that receipt
with fail-closed, mutation, metamorphic, and weak-system controls.

It is not a Contract-C schema, version, exporter, or production implementation.
"""

from __future__ import annotations

import copy
import hashlib
import json
import shutil
from collections.abc import Iterable
from dataclasses import asdict
from pathlib import Path
from typing import Any

CAL_PRODUCTION_SHA = "33a928db97316a3652d57df9cafb8ca240305233"
EB_PRODUCTION_SHA = "c8189c31adbab11729c31430c2070126224a2d42"
APPARATUS_PRODUCTION_SHA = "c314e53bd91c0736aa4370a364673b069aceb43e"
CONTRACT_B_VERSION = "1.2.0"
RC2D_DECISIVE_SHA = "967fb164b7087a0d03bdd170b5b3a5b63568c6f7"
RC2D_RECEIPT_SHA256 = "a953a14b8bf9a5bd9cf9060e7fb58c868df9b15c8b578d88f13a1090c4eca5fa"
EXPECTED_POLICY_SHA256 = "88f007c96f3acf63a191556fe7fa46b80b37e9fcb5224ec1e90fb626a061104d"

# Frozen predecessor: CAL #16 workflow 33137053355 / artifact 9672432251 /
# artifact digest sha256:fd90160ec50f36f65ffd6a26bb1a7e6f1c7f584cb45cc36ee04a903e32f55994.
# This digest is over a deliberately timestamp-insensitive semantic projection
# of its immutable real-producer-boundary-capture.json, not over the artifact.
RC2A_PREDECESSOR_SEMANTIC_FINGERPRINT = (
    "82b8877bed73a842ae775163c1eb0853e67aa2470e99c9e893f5bef2f7c28b43"
)

PROFILE_ID = "contract-c-rc2-producer-candidate-research"
GENERIC_ASSESSMENTS = (
    "eligibility",
    "semantic_validity",
    "aperture_completeness",
    "temporal_applicability",
    "citation",
)

FORBIDDEN_DESTINATION_KEYS = {
    "authorization",
    "authority_profile",
    "autonomy_envelope",
    "causal_effect_prediction",
    "expected_utility",
    "forecast_probability",
    "future_state",
    "preference",
    "risk_tolerance",
    "utility",
    "workflow_route",
}
FORBIDDEN_TELEMETRY_KEYS = {
    "explanation",
    "limitations",
    "rationale",
    "rewrite_guidance",
    "risk_label",
    "source_url",
}
ALLOWED_CAUSAL_FORMS = {
    "single_necessary",
    "independent_sufficient_alternatives",
    "jointly_sufficient",
    "redundant_non_deciding",
}


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def stable_id(prefix: str, value: Any) -> str:
    return f"{prefix}:" + sha256_bytes(canonical_bytes(value))


def _date_text(value: Any) -> str | None:
    if value is None:
        return None
    iso = getattr(value, "isoformat", None)
    return iso() if callable(iso) else str(value)


def policy_object(policy: Any) -> dict[str, Any]:
    return asdict(policy)


def policy_hash(policy: Any) -> str:
    return sha256_bytes(canonical_bytes(policy_object(policy)))


def _walk_keys(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from _walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_keys(child)


def _file_manifest(root: Path) -> tuple[list[dict[str, Any]], str]:
    rows: list[dict[str, Any]] = []
    digest = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = path.relative_to(root).as_posix()
        raw = path.read_bytes()
        file_sha = sha256_bytes(raw)
        rows.append({"path": rel, "size": len(raw), "sha256": file_sha})
        rel_raw = rel.encode("utf-8")
        digest.update(len(rel_raw).to_bytes(8, "big"))
        digest.update(rel_raw)
        digest.update(len(raw).to_bytes(8, "big"))
        digest.update(raw)
    return rows, digest.hexdigest()


def _candidate_semantic_row(candidate: Any) -> dict[str, Any]:
    return {
        "source_id": candidate.source_id,
        "excerpt_id": candidate.excerpt_id,
        "score": candidate.score,
        "source_reliability": candidate.source_reliability,
        "source_date": _date_text(candidate.source_date),
        "source_url": candidate.source_url,
    }


def semantic_fingerprint(assessments: Iterable[Any], *, engine: str) -> str:
    """Fingerprint production semantics while excluding timestamp-bound B bytes."""

    claims = []
    for assessment in sorted(assessments, key=lambda row: row.claim.id):
        claims.append(
            {
                "claim_id": assessment.claim.id,
                "claim_text": assessment.claim.text,
                "claim_type": assessment.claim.claim_type,
                "support_label": assessment.support_label,
                "support_signal": assessment.support_signal,
                "support_candidates": [
                    _candidate_semantic_row(item) for item in assessment.candidate_evidence
                ],
                "counter_candidates": [
                    _candidate_semantic_row(item) for item in assessment.counterevidence
                ],
                "rule_codes": sorted(flag.code for flag in assessment.rule_flags),
            }
        )
    return sha256_bytes(canonical_bytes({"engine": engine, "claims": claims}))


def _terminal_branch(verdict: str, support_signal: float | None, policy: Any) -> str:
    """Branch identity derivable from public result state plus frozen policy."""

    if verdict == "not_checkable":
        return "unclassified_early_return"
    if verdict == "needs_source":
        return "needs_source_rule_family"
    if verdict == "overstated":
        return "overstated_rule_family"
    if verdict == "unsupported":
        return "support_below_partial_threshold"
    if verdict == "partially_supported":
        if support_signal is not None and support_signal < policy.sourced_support:
            return "support_between_thresholds"
        return "residual_or_counter_limit_branch"
    if verdict == "supported":
        return "supported_score_branch"
    return f"unresolved:{verdict}"


def _outcome(assessment: Any, policy: Any) -> dict[str, Any]:
    return {
        "final_verdict": assessment.support_label,
        "terminal_branch": _terminal_branch(
            assessment.support_label, assessment.support_signal, policy
        ),
        "support_signal": assessment.support_signal,
        "rule_codes": sorted(flag.code for flag in assessment.rule_flags),
        "rule_ids": sorted(flag.id for flag in assessment.rule_flags),
    }


def _contribution_ref(
    candidate: Any, passage_lookup: dict[tuple[str, str], Any]
) -> dict[str, Any]:
    key = (candidate.source_id, candidate.excerpt_id)
    passage = passage_lookup.get(key)
    if passage is None:
        return {
            "source_id": candidate.source_id,
            "excerpt_id": candidate.excerpt_id,
            "reference_state": "unresolved",
        }
    value = {
        "source_id": candidate.source_id,
        "passage_id": passage.passage_id,
        "passage_sha256": passage.passage_hash,
    }
    return value


def _contribution_id(
    proposition_id: str,
    channel: str,
    ref: dict[str, Any],
) -> str:
    return stable_id(
        "contribution",
        {"proposition_id": proposition_id, "channel": channel, "evidence_ref": ref},
    )


def _passage_lookup(contents: Any) -> dict[tuple[str, str], Any]:
    result: dict[tuple[str, str], Any] = {}
    for source_id, passages in contents.passages.items():
        for passage in passages:
            excerpt_id = f"{source_id}/{passage.passage_id}"
            result[(source_id, excerpt_id)] = passage
    return result


def _replace_candidate_reliability(candidate: Any, value: str) -> Any:
    return candidate.model_copy(update={"source_reliability": value})


def _replace_bundle_reliability(bundle: Any, value: str) -> Any:
    sources = [
        source.model_copy(update={"reliability": value}) for source in bundle.sources
    ]
    return bundle.model_copy(update={"sources": sources})


def _observe_production(
    claim: Any,
    evidence_bundle: Any,
    support: list[Any],
    counters: list[Any],
    audit_config: Any,
    policy: Any,
) -> Any:
    from claim_audit_lab.rules import assess_claim_support

    return assess_claim_support(
        claim,
        evidence_bundle,
        support,
        audit_config,
        counterevidence=counters,
        policy=policy,
    )


def _rule_role_controls(
    *,
    assessment: Any,
    evidence_bundle: Any,
    audit_config: Any,
    policy: Any,
) -> tuple[list[dict[str, Any]], list[str]]:
    """Classify real-run rule flags only through controlled public-input mutation."""

    rows: list[dict[str, Any]] = []
    unresolved: list[str] = []
    baseline = _outcome(assessment, policy)
    codes = sorted(flag.code for flag in assessment.rule_flags)

    for code in codes:
        if code != "low_reliability_only":
            unresolved.append(code)
            rows.append(
                {
                    "code": code,
                    "terminal_role": "unresolved",
                    "reason": "no preregistered public-input removal control for this real-run rule",
                }
            )
            continue

        high_support = [
            _replace_candidate_reliability(item, "high")
            for item in assessment.candidate_evidence
        ]
        high_counters = [
            _replace_candidate_reliability(item, "high")
            for item in assessment.counterevidence
        ]
        high_bundle = _replace_bundle_reliability(evidence_bundle, "high")
        mutated = _observe_production(
            assessment.claim,
            high_bundle,
            high_support,
            high_counters,
            audit_config,
            policy,
        )
        changed = mutated.support_label != assessment.support_label
        rows.append(
            {
                "code": code,
                "terminal_role": "causal" if changed else "residual",
                "control_id": f"rule-role:{assessment.claim.id}:{code}",
                "_control": {
                    "control": "replace_low_reliability_state_with_high",
                    "baseline": baseline,
                    "mutated": _outcome(mutated, policy),
                },
            }
        )
    return rows, unresolved


def _real_proposition_projection(
    *,
    assessment: Any,
    contents: Any,
    evidence_bundle: Any,
    audit_config: Any,
    policy: Any,
) -> tuple[dict[str, Any], list[str], dict[str, Any]]:
    """Project one real result using only public inputs/results and interventions."""

    passage_lookup = _passage_lookup(contents)
    support_rows: list[dict[str, Any]] = []
    counter_rows: list[dict[str, Any]] = []

    for candidate in assessment.candidate_evidence:
        ref = _contribution_ref(candidate, passage_lookup)
        support_rows.append(
            {
                "contribution_id": _contribution_id(
                    assessment.claim.id, "support", ref
                ),
                "channel": "support",
                "evidence_ref": ref,
                "_source_candidate": candidate,
            }
        )
    for candidate in assessment.counterevidence:
        ref = _contribution_ref(candidate, passage_lookup)
        counter_rows.append(
            {
                "contribution_id": _contribution_id(
                    assessment.claim.id, "counterevidence", ref
                ),
                "channel": "counterevidence",
                "evidence_ref": ref,
                "_source_candidate": candidate,
            }
        )

    all_rows = support_rows + counter_rows
    unresolved = [
        row["contribution_id"]
        for row in all_rows
        if row["evidence_ref"].get("reference_state") == "unresolved"
    ]
    baseline = _outcome(assessment, policy)

    support_scores = [row["_source_candidate"].score for row in support_rows]
    counter_scores = [row["_source_candidate"].score for row in counter_rows]
    max_support = max(support_scores, default=0.0)
    max_counter = max(counter_scores, default=0.0)
    measurement_basis = [
        row["contribution_id"]
        for row in support_rows
        if row["_source_candidate"].score == max_support
    ] + [
        row["contribution_id"]
        for row in counter_rows
        if row["_source_candidate"].score == max_counter and counter_rows
    ]

    removal_observations: dict[str, dict[str, Any]] = {}
    terminal_necessary: list[str] = []
    terminal_residual: list[str] = []

    support_source = list(assessment.candidate_evidence)
    counter_source = list(assessment.counterevidence)

    for index, row in enumerate(support_rows):
        mutated_support = support_source[:index] + support_source[index + 1 :]
        mutated = _observe_production(
            assessment.claim,
            evidence_bundle,
            mutated_support,
            counter_source,
            audit_config,
            policy,
        )
        cid = row["contribution_id"]
        removal_observations[cid] = _outcome(mutated, policy)
        if mutated.support_label != assessment.support_label:
            terminal_necessary.append(cid)
        else:
            terminal_residual.append(cid)

    for index, row in enumerate(counter_rows):
        mutated_counter = counter_source[:index] + counter_source[index + 1 :]
        mutated = _observe_production(
            assessment.claim,
            evidence_bundle,
            support_source,
            mutated_counter,
            audit_config,
            policy,
        )
        cid = row["contribution_id"]
        removal_observations[cid] = _outcome(mutated, policy)
        if mutated.support_label != assessment.support_label:
            terminal_necessary.append(cid)
        else:
            terminal_residual.append(cid)

    causal_form = "redundant_non_deciding"
    if len(terminal_necessary) == 1:
        causal_form = "single_necessary"
    elif len(terminal_necessary) > 1:
        # Distinguish independent alternatives from joint/co-sufficient bases by
        # production replay with each terminally necessary member isolated.
        isolated_target = []
        lookup_by_id = {row["contribution_id"]: row for row in all_rows}
        for member in terminal_necessary:
            row = lookup_by_id[member]
            if row["channel"] == "support":
                support = [row["_source_candidate"]]
                counters: list[Any] = []
            else:
                support = []
                counters = [row["_source_candidate"]]
            isolated = _observe_production(
                assessment.claim,
                evidence_bundle,
                support,
                counters,
                audit_config,
                policy,
            )
            isolated_target.append(isolated.support_label == assessment.support_label)
        if all(isolated_target):
            causal_form = "independent_sufficient_alternatives"
        elif not any(isolated_target):
            causal_form = "jointly_sufficient"
        else:
            causal_form = "unresolved_mixed_multiplicity"
            unresolved.append("terminal multiplicity does not fit supported causal forms")

    rule_roles_with_controls, unresolved_rules = _rule_role_controls(
        assessment=assessment,
        evidence_bundle=evidence_bundle,
        audit_config=audit_config,
        policy=policy,
    )
    unresolved.extend(f"rule:{code}" for code in unresolved_rules)
    rule_roles = [
        {key: value for key, value in row.items() if key != "_control"}
        for row in rule_roles_with_controls
    ]
    rule_controls = {
        row["control_id"]: row["_control"]
        for row in rule_roles_with_controls
        if "_control" in row
    }

    public_contributions = []
    for row in all_rows:
        public_contributions.append(
            {
                "contribution_id": row["contribution_id"],
                "channel": row["channel"],
                "evidence_ref": row["evidence_ref"],
                "terminal_role": (
                    "necessary"
                    if row["contribution_id"] in terminal_necessary
                    else "residual"
                ),
                "measurement_role": (
                    "co_maximal"
                    if row["contribution_id"] in measurement_basis
                    else "retained_non_max"
                ),
            }
        )

    generic = {name: {"state": "not_performed"} for name in GENERIC_ASSESSMENTS}

    branch = baseline["terminal_branch"]
    if branch.startswith("unresolved:"):
        unresolved.append(f"terminal branch unresolved: {branch}")

    result = {
        "proposition": {
            "proposition_id": assessment.claim.id,
            "text_sha256": sha256_bytes(assessment.claim.text.encode("utf-8")),
        },
        "contributions": public_contributions,
        "measurement": {
            "kind": "cal_v0_2_aggregate_support_signal",
            "value": assessment.support_signal,
            "basis_contribution_ids": measurement_basis,
        },
        "generic_assessments": generic,
        "conclusion": {
            "reported_verdict": assessment.support_label,
            "terminal_branch": branch,
            "causal_form": causal_form,
            "terminal_necessary_contribution_ids": sorted(terminal_necessary),
            "terminal_residual_contribution_ids": sorted(terminal_residual),
            "rule_roles": rule_roles,
        },
        "execution": {"state": "completed"},
        "reassessment": {"relation": "original", "prior_result_id": None},
    }
    control_record = {
        "proposition_id": assessment.claim.id,
        "baseline": baseline,
        "contribution_removal_observations": removal_observations,
        "rule_role_controls": rule_controls,
        "derived_terminal_necessary_contribution_ids": sorted(terminal_necessary),
        "derived_terminal_residual_contribution_ids": sorted(terminal_residual),
        "derived_causal_form": causal_form,
    }
    return result, unresolved, control_record


def _binding(
    contents: Any, bundle_dir: Path
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    files, artifact_sha = _file_manifest(bundle_dir)
    contract_version = (bundle_dir / "CONTRACT_VERSION").read_text(
        encoding="utf-8"
    ).strip()
    return (
        {
            "contract_version": contract_version,
            "bundle_id": contents.manifest.bundle_id,
            "bundle_hash": contents.manifest.bundle.bundle_hash,
            "artifact_sha256": artifact_sha,
            "sha256sums_sha256": sha256_bytes((bundle_dir / "SHA256SUMS").read_bytes()),
        },
        files,
    )


def _candidate_body(
    *,
    binding: dict[str, Any],
    policy: Any,
    engine: str,
    results: list[dict[str, Any]],
) -> dict[str, Any]:
    canonical_policy = policy_object(policy)
    return {
        "candidate_profile": PROFILE_ID,
        "input": {"contract_b": copy.deepcopy(binding)},
        "producer": {
            "name": "claim-audit-lab",
            "production_semantic_sha": CAL_PRODUCTION_SHA,
            "engine": engine,
            "policy": {
                "config_id": canonical_policy["config_id"],
                "canonical": canonical_policy,
                "sha256": policy_hash(policy),
            },
        },
        "execution": {
            "state": "completed",
            "execution_id": stable_id(
                "execution",
                {
                    "contract_b": binding,
                    "cal_sha": CAL_PRODUCTION_SHA,
                    "policy_sha256": policy_hash(policy),
                },
            ),
        },
        "propositions": results,
    }


def make_candidate(
    *,
    binding: dict[str, Any],
    policy: Any,
    engine: str,
    results: list[dict[str, Any]],
) -> dict[str, Any]:
    body = _candidate_body(
        binding=binding, policy=policy, engine=engine, results=results
    )
    candidate = copy.deepcopy(body)
    candidate["result_set_id"] = stable_id("result-set", body)
    return candidate


def validate_candidate(candidate: dict[str, Any]) -> list[str]:
    """Independent-of-CAL structural/semantic firewall for the frozen profile."""

    errors: list[str] = []
    if candidate.get("candidate_profile") != PROFILE_ID:
        errors.append("unexpected candidate profile")

    forbidden_destination = sorted(
        FORBIDDEN_DESTINATION_KEYS & set(_walk_keys(candidate))
    )
    if forbidden_destination:
        errors.append("destination-policy leakage: " + ",".join(forbidden_destination))
    forbidden_telemetry = sorted(
        FORBIDDEN_TELEMETRY_KEYS & set(_walk_keys(candidate))
    )
    if forbidden_telemetry:
        errors.append("unnecessary telemetry leakage: " + ",".join(forbidden_telemetry))

    binding = candidate.get("input", {}).get("contract_b", {})
    for key in (
        "contract_version",
        "bundle_id",
        "bundle_hash",
        "artifact_sha256",
        "sha256sums_sha256",
    ):
        if not binding.get(key):
            errors.append(f"missing Contract-B binding: {key}")
    if binding.get("contract_version") != CONTRACT_B_VERSION:
        errors.append("unexpected Contract-B version")

    producer = candidate.get("producer", {})
    if producer.get("production_semantic_sha") != CAL_PRODUCTION_SHA:
        errors.append("wrong CAL production semantic SHA")
    policy = producer.get("policy")
    if not isinstance(policy, dict):
        errors.append("producer policy missing")
    else:
        canonical = policy.get("canonical")
        if not isinstance(canonical, dict):
            errors.append("canonical policy state missing")
        else:
            observed = sha256_bytes(canonical_bytes(canonical))
            if policy.get("sha256") != observed:
                errors.append("policy hash mismatch")
            if policy.get("config_id") != canonical.get("config_id"):
                errors.append("policy config_id not bound to canonical state")
            if policy.get("sha256") != EXPECTED_POLICY_SHA256:
                errors.append("unexpected frozen policy identity")

    propositions = candidate.get("propositions")
    if not isinstance(propositions, list) or not propositions:
        errors.append("candidate has no proposition results")
        return errors

    seen_props: set[str] = set()
    for index, result in enumerate(propositions):
        proposition = result.get("proposition", {})
        pid = proposition.get("proposition_id")
        if not isinstance(pid, str) or not pid or pid in seen_props:
            errors.append(f"proposition[{index}] missing/duplicate identity")
        else:
            seen_props.add(pid)
        if not proposition.get("text_sha256"):
            errors.append(f"proposition[{index}] missing text hash")

        contribution_ids: set[str] = set()
        for row in result.get("contributions", []):
            cid = row.get("contribution_id")
            if not isinstance(cid, str) or not cid:
                errors.append(f"proposition[{index}] contribution identity missing")
                continue
            contribution_ids.add(cid)
            ref = row.get("evidence_ref", {})
            if not all(
                ref.get(key) for key in ("source_id", "passage_id", "passage_sha256")
            ):
                errors.append(f"proposition[{index}] unresolved evidence reference")
            if row.get("terminal_role") not in {"necessary", "residual"}:
                errors.append(f"proposition[{index}] invalid terminal contribution role")
            if row.get("measurement_role") not in {"co_maximal", "retained_non_max"}:
                errors.append(f"proposition[{index}] invalid measurement contribution role")

        measurement = result.get("measurement", {})
        if measurement.get("kind") != "cal_v0_2_aggregate_support_signal":
            errors.append(f"proposition[{index}] missing aggregate measurement identity")
        if measurement.get("value") is None:
            errors.append(f"proposition[{index}] aggregate measurement missing")
        for cid in measurement.get("basis_contribution_ids", []):
            if cid not in contribution_ids:
                errors.append(
                    f"proposition[{index}] measurement basis reference missing"
                )

        generic = result.get("generic_assessments", {})
        for name in GENERIC_ASSESSMENTS:
            item = generic.get(name)
            if not isinstance(item, dict):
                errors.append(f"proposition[{index}] generic assessment missing: {name}")
            elif item.get("state") != "not_performed":
                errors.append(
                    f"proposition[{index}] generic assessment must remain not_performed: {name}"
                )

        conclusion = result.get("conclusion", {})
        if not conclusion.get("reported_verdict"):
            errors.append(f"proposition[{index}] reported verdict missing")
        if not conclusion.get("terminal_branch"):
            errors.append(f"proposition[{index}] terminal branch missing")
        causal_form = conclusion.get("causal_form")
        if causal_form not in ALLOWED_CAUSAL_FORMS:
            errors.append(f"proposition[{index}] unsupported causal form: {causal_form}")
        necessary = conclusion.get("terminal_necessary_contribution_ids", [])
        residual = conclusion.get("terminal_residual_contribution_ids", [])
        if set(necessary) & set(residual):
            errors.append(f"proposition[{index}] contribution both necessary and residual")
        for cid in [*necessary, *residual]:
            if cid not in contribution_ids:
                errors.append(f"proposition[{index}] terminal basis reference missing")
        if causal_form == "single_necessary" and len(necessary) != 1:
            errors.append(
                f"proposition[{index}] single necessary basis is not singular"
            )
        if causal_form == "redundant_non_deciding" and necessary:
            errors.append(f"proposition[{index}] redundant basis has necessary members")

        for row in conclusion.get("rule_roles", []):
            if row.get("terminal_role") not in {"causal", "residual"}:
                errors.append(f"proposition[{index}] unresolved rule role")

        if result.get("execution", {}).get("state") != "completed":
            errors.append(f"proposition[{index}] execution state not completed")
        reassessment = result.get("reassessment", {})
        if reassessment.get("relation") == "original":
            if reassessment.get("prior_result_id") is not None:
                errors.append(f"proposition[{index}] original result has prior result")
        elif reassessment.get("relation") == "superseding":
            if not reassessment.get("prior_result_id"):
                errors.append(f"proposition[{index}] superseding result lacks prior id")
        else:
            errors.append(f"proposition[{index}] invalid reassessment relation")

    execution = candidate.get("execution", {})
    if execution.get("state") != "completed" or not execution.get("execution_id"):
        errors.append("run execution identity/state missing")

    body = copy.deepcopy(candidate)
    observed_id = body.pop("result_set_id", None)
    expected_id = stable_id("result-set", body)
    if observed_id != expected_id:
        errors.append("result-set identity mismatch")
    return errors


def rebuild_result_set_id(candidate: dict[str, Any]) -> dict[str, Any]:
    value = copy.deepcopy(candidate)
    value.pop("result_set_id", None)
    value["result_set_id"] = stable_id("result-set", value)
    return value


def weak_candidate_controls(candidate: dict[str, Any]) -> dict[str, list[str]]:
    """Intentionally weak/gaming candidates that a useful gate must reject."""

    controls: dict[str, dict[str, Any]] = {}

    config_only = copy.deepcopy(candidate)
    config_only["producer"]["policy"].pop("canonical", None)
    config_only["producer"]["policy"].pop("sha256", None)
    controls["config_id_only_policy"] = rebuild_result_set_id(config_only)

    missing_b = copy.deepcopy(candidate)
    missing_b["input"]["contract_b"].pop("bundle_hash", None)
    controls["missing_contract_b_binding"] = rebuild_result_set_id(missing_b)

    performed = copy.deepcopy(candidate)
    first = performed["propositions"][0]
    first["generic_assessments"]["eligibility"] = {
        "state": "performed",
        "value": "eligible",
    }
    controls["invented_generic_assessment"] = rebuild_result_set_id(performed)

    hidden = copy.deepcopy(candidate)
    hidden["propositions"][0]["explanation"] = "implementation debug prose"
    controls["telemetry_leak"] = rebuild_result_set_id(hidden)

    missing_basis = copy.deepcopy(candidate)
    missing_basis["propositions"][0]["conclusion"].pop("terminal_branch", None)
    controls["missing_terminal_basis"] = rebuild_result_set_id(missing_basis)

    return {name: validate_candidate(value) for name, value in controls.items()}


def field_justification_registry() -> list[dict[str, str]]:
    """Non-circular evidence basis for retained and excluded field families."""

    return [
        {
            "path": "input.contract_b.*",
            "classification": "directly available legitimate producer state",
            "source": "validated Contract-B manifest plus exact frozen bundle bytes",
            "reason": "immutable B->C lineage; CAL #15 showed trace-only projection lacks exact B binding",
        },
        {
            "path": "producer.production_semantic_sha",
            "classification": "exact provenance / identity / reconstruction",
            "source": "pinned CAL production-semantic commit",
            "reason": "binds the production behavior whose receipt is being serialized",
        },
        {
            "path": "producer.policy.canonical + sha256",
            "classification": "deterministically derivable without new epistemic judgment",
            "source": "public frozen CAL AuditPolicy object",
            "reason": "CAL #19/#21/#22 falsified config-name-only policy identity",
        },
        {
            "path": "propositions[].proposition",
            "classification": "directly available legitimate producer state",
            "source": "validated Contract-B claim identity plus deterministic text hash",
            "reason": "binds proposition result without duplicating claim text",
        },
        {
            "path": "propositions[].contributions[].evidence_ref",
            "classification": "directly available legitimate producer state",
            "source": "ClaimAssessment candidate refs mapped to validated Contract-B passages",
            "reason": "preserves deciding and non-deciding evidence without copying source payload",
        },
        {
            "path": "propositions[].measurement.value",
            "classification": "directly available legitimate producer state",
            "source": "ClaimAssessment.support_signal",
            "reason": "stable aggregate measurement used by current v0.2 terminal branches",
        },
        {
            "path": "propositions[].measurement.basis_contribution_ids",
            "classification": "deterministically derivable without new epistemic judgment",
            "source": "public candidate scores plus controlled production replay",
            "reason": "preserves all co-maxima rather than choosing an arbitrary winner",
        },
        {
            "path": "propositions[].generic_assessments.*.state",
            "classification": "deterministically derivable without new epistemic judgment",
            "source": "selected v0.2 production path plus CAL #17/#22",
            "reason": "records that generic stages were not performed; it is not an assessment value",
        },
        {
            "path": "propositions[].conclusion.terminal_branch",
            "classification": "deterministically derivable without new epistemic judgment",
            "source": "public verdict/support signal/rule state plus frozen public policy",
            "reason": "CAL #19/#21/#22 support branch receipt reconstruction",
        },
        {
            "path": "propositions[].conclusion terminal contribution/rule roles",
            "classification": "deterministically derivable without new epistemic judgment",
            "source": "controlled replay through public assess_claim_support over legitimate inputs",
            "reason": "interventions distinguish necessary, residual, tied, and co-sufficient state",
        },
        {
            "path": "propositions[].reassessment",
            "classification": "execution / failure / supersession interpretation",
            "source": "result-package bookkeeping only",
            "reason": "original versus superseding result must not be silent mutation",
        },
        {
            "path": "EvidenceCandidate.score",
            "classification": "transient derivation input; excluded from frozen candidate",
            "source": "direct ClaimAssessment state",
            "reason": "used to derive aggregate/co-maximal basis; raw per-candidate scalar is not retained once receipt is materialized",
        },
        {
            "path": "risk_label/explanation/rewrite_guidance/limitations/rationale/source_url",
            "classification": "presentation convenience or unnecessary telemetry",
            "source": "ClaimAssessment presentation/result-adjacent fields",
            "reason": "not required by the bounded attribution semantics under test",
        },
        {
            "path": "downstream authority/utility/forecast/workflow state",
            "classification": "downstream policy",
            "source": "Decision Engine/operator context",
            "reason": "outside CAL/Contract-C epistemic authority; excluded by semantic firewall",
        },
        {
            "path": "private direct_contexts/helper locals/feature ordering",
            "classification": "reconstructed only from implementation details; prohibited",
            "source": "not needed by this apparatus",
            "reason": "gate must fail or remain inconclusive rather than serialize hidden implementation telemetry",
        },
    ]


def targeted_ablation_matrix(candidate: dict[str, Any]) -> list[dict[str, Any]]:
    """Enforcement tests. Validator rejection is not treated as necessity evidence."""

    mutations = [
        (
            "input.contract_b.bundle_hash",
            lambda c: c["input"]["contract_b"].pop("bundle_hash", None),
        ),
        (
            "producer.policy.sha256",
            lambda c: c["producer"]["policy"].pop("sha256", None),
        ),
        (
            "propositions[0].generic_assessments.eligibility",
            lambda c: c["propositions"][0]["generic_assessments"].pop(
                "eligibility", None
            ),
        ),
        (
            "propositions[0].conclusion.terminal_branch",
            lambda c: c["propositions"][0]["conclusion"].pop("terminal_branch", None),
        ),
        (
            "propositions[0].proposition.text_sha256",
            lambda c: c["propositions"][0]["proposition"].pop("text_sha256", None),
        ),
    ]
    rows = []
    for path, mutate in mutations:
        trial = copy.deepcopy(candidate)
        mutate(trial)
        trial = rebuild_result_set_id(trial)
        errors = validate_candidate(trial)
        rows.append(
            {
                "removed_path": path,
                "validator_rejects": bool(errors),
                "errors": errors,
                "evidence_rule": (
                    "validator rejection is enforcement only; semantic necessity is justified "
                    "separately in field-justification-registry.json"
                ),
            }
        )
    return rows


def profile_controls_from_rc2d(
    suite: dict[str, Any],
    *,
    validate_suite: Any,
) -> dict[str, Any]:
    """Challenge multiplicity/not-performed/policy semantics with the frozen #22 oracle."""

    baseline_errors = validate_suite(suite)
    receipts = {
        item["family_id"]: item
        for item in suite.get("receipts", [])
        if isinstance(item, dict) and isinstance(item.get("family_id"), str)
    }
    controls: dict[str, list[str]] = {}

    tied = copy.deepcopy(suite)
    tied_row = next(
        item
        for item in tied["receipts"]
        if item.get("family_id") == "tied_independent_support"
    )
    tied_row["co_maximal_support_refs"] = tied_row["co_maximal_support_refs"][:1]
    controls["collapse_tied_alternatives"] = validate_suite(tied)

    joint = copy.deepcopy(suite)
    joint_row = next(
        item
        for item in joint["receipts"]
        if item.get("family_id") == "absolute_wording_joint"
    )
    joint_row["causal_claim"]["classification"] = "independent_sufficient_alternatives"
    controls["mislabel_joint_as_independent"] = validate_suite(joint)

    residual = copy.deepcopy(suite)
    residual_row = next(
        item
        for item in residual["receipts"]
        if item.get("family_id") == "low_reliability_residual"
    )
    residual_row["residual_non_deciding"] = []
    controls["erase_residual_state"] = validate_suite(residual)

    generic = copy.deepcopy(suite)
    generic["receipts"][0]["generic_assessments"]["eligibility"] = {
        "state": "performed"
    }
    controls["convert_not_performed_to_assessment"] = validate_suite(generic)

    policy = copy.deepcopy(suite)
    policy["receipts"][0]["policy"]["canonical"]["overstated_detection"] = not bool(
        policy["receipts"][0]["policy"]["canonical"]["overstated_detection"]
    )
    controls["same_config_policy_mutation_without_hash"] = validate_suite(policy)

    causal_forms = sorted(
        {
            item.get("causal_claim", {}).get("classification")
            for item in receipts.values()
            if item.get("causal_claim", {}).get("classification")
        }
    )
    required_families = {
        "threshold_no_rule",
        "credential_needs_source",
        "low_reliability_residual",
        "unclassified_not_checkable",
        "absolute_wording_joint",
        "tied_independent_support",
    }

    return {
        "baseline_validator_errors": baseline_errors,
        "receipt_families": sorted(receipts),
        "required_families_present": required_families <= set(receipts),
        "causal_forms": causal_forms,
        "weak_control_errors": controls,
        "all_weak_controls_rejected": all(bool(errors) for errors in controls.values()),
    }


def _telemetry_invariance(
    *,
    candidate: dict[str, Any],
    assessments: list[Any],
    rebuild: Any,
) -> dict[str, Any]:
    """Mutate only presentation/telemetry excluded by the profile."""

    mutated = []
    for assessment in assessments:
        raw = assessment.model_dump(mode="json")
        raw["risk_label"] = "high" if raw["risk_label"] != "high" else "low"
        raw["explanation"] = "presentation-only telemetry mutation"
        raw["rewrite_guidance"] = ["presentation-only mutation"]
        raw["limitations"] = ["presentation-only mutation"]
        for row in raw.get("candidate_evidence", []):
            row["rationale"] = "presentation-only rationale mutation"
            row["source_url"] = "https://example.invalid/presentation-only"
        for row in raw.get("counterevidence", []):
            row["rationale"] = "presentation-only rationale mutation"
            row["source_url"] = "https://example.invalid/presentation-only"
        mutated.append(type(assessment).model_validate(raw))

    mutated_candidate = rebuild(mutated)
    return {
        "invariant": canonical_bytes(mutated_candidate) == canonical_bytes(candidate),
        "mutated_fields": sorted(FORBIDDEN_TELEMETRY_KEYS),
        "candidate_sha256": sha256_bytes(canonical_bytes(candidate)),
        "mutated_candidate_sha256": sha256_bytes(canonical_bytes(mutated_candidate)),
    }


def _semantic_firewall(candidate: dict[str, Any]) -> dict[str, Any]:
    before = sha256_bytes(canonical_bytes(candidate))
    downstream_contexts = [
        {
            "authority_profile": "delegated_auto_action",
            "forecast_probability": 0.1,
            "workflow_route": "auto",
        },
        {
            "authority_profile": "named_human_required",
            "forecast_probability": 0.9,
            "workflow_route": "review",
        },
    ]
    # The contexts are deliberately observed but never merged into Contract C.
    after = sha256_bytes(canonical_bytes(candidate))
    return {
        "candidate_sha256_before": before,
        "candidate_sha256_after": after,
        "invariant": before == after,
        "downstream_contexts_observed_separately": downstream_contexts,
    }


def _tamper_control(bundle_dir: Path, out_dir: Path) -> dict[str, Any]:
    from claim_audit_lab.contracts.bundle_loader import BundleIntegrityError
    from claim_audit_lab.contracts.factual_context import (
        FactualContextIntakeError,
        load_contract_b_intake,
    )

    target = out_dir / "tampered-contract-b"
    shutil.copytree(bundle_dir, target)
    first_claim = min((target / "claims").glob("*.yaml"))
    first_claim.write_text(
        first_claim.read_text(encoding="utf-8") + "\n# rc2 producer-gate tamper\n",
        encoding="utf-8",
    )
    detected = False
    error = ""
    try:
        load_contract_b_intake(target, deviations_dir=out_dir / "tamper-deviations")
    except (BundleIntegrityError, FactualContextIntakeError) as exc:
        detected = True
        error = str(exc)
    return {"tamper_detected": detected, "error": error}


def run_experiment(
    *,
    eb_root: Path,
    fixture: Path,
    out_dir: Path,
    rc2d_suite_path: Path,
) -> dict[str, Any]:
    """Execute the bounded producer gate and emit its evidence record."""

    from claim_audit_lab import __version__ as cal_library_version
    from claim_audit_lab.auditor import audit_claims
    from claim_audit_lab.contracts.adapter import (
        adapt_bundle_to_pipeline,
        build_claim_evidence_scopes,
    )
    from claim_audit_lab.contracts.factual_context import load_contract_b_intake
    from claim_audit_lab.policy import CAL_RULES_V1_2_0
    from evidence_bundler.contracts.writer import build_retrieval_bundle
    from research_contract_c_rc2_d.validator import validate_suite

    out_dir = out_dir.resolve()
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    b_dir = out_dir / "real-contract-b-1.2.0"
    build_retrieval_bundle(fixture.resolve(), b_dir)
    intake = load_contract_b_intake(
        b_dir, deviations_dir=out_dir / "intake-deviations"
    )
    contents = intake.bundle

    binding, files = _binding(contents, b_dir)
    if binding["contract_version"] != CONTRACT_B_VERSION:
        raise AssertionError("fresh producer run did not produce Contract B 1.2.0")

    cal_claims, evidence_bundle, audit_config = adapt_bundle_to_pipeline(contents)
    scopes = build_claim_evidence_scopes(contents)
    assessments = audit_claims(
        cal_claims,
        evidence_bundle,
        audit_config,
        evidence_scopes=scopes,
    )

    engine = contents.audit_config.pipeline
    fingerprint = semantic_fingerprint(assessments, engine=engine)
    fingerprint_matches = fingerprint == RC2A_PREDECESSOR_SEMANTIC_FINGERPRINT

    policy_sha = policy_hash(CAL_RULES_V1_2_0)
    policy_matches = policy_sha == EXPECTED_POLICY_SHA256

    def build_from_assessments(
        items: list[Any],
    ) -> tuple[dict[str, Any], list[str], list[dict[str, Any]]]:
        results: list[dict[str, Any]] = []
        local_unresolved: list[str] = []
        controls: list[dict[str, Any]] = []
        for item in items:
            projected, item_unresolved, control = _real_proposition_projection(
                assessment=item,
                contents=contents,
                evidence_bundle=evidence_bundle,
                audit_config=audit_config,
                policy=CAL_RULES_V1_2_0,
            )
            results.append(projected)
            controls.append(control)
            local_unresolved.extend(
                f"{item.claim.id}:{value}" for value in item_unresolved
            )
        value = make_candidate(
            binding=binding,
            policy=CAL_RULES_V1_2_0,
            engine=engine,
            results=results,
        )
        return value, local_unresolved, controls

    candidate, unresolved, real_attribution_controls = build_from_assessments(
        assessments
    )
    candidate_errors = validate_candidate(candidate)

    reproduced, reproduced_unresolved, reproduced_controls = build_from_assessments(
        assessments
    )
    deterministic = (
        canonical_bytes(reproduced) == canonical_bytes(candidate)
        and reproduced_unresolved == unresolved
        and canonical_bytes(reproduced_controls)
        == canonical_bytes(real_attribution_controls)
    )

    telemetry = _telemetry_invariance(
        candidate=candidate,
        assessments=assessments,
        rebuild=lambda items: build_from_assessments(items)[0],
    )
    firewall = _semantic_firewall(candidate)
    tamper = _tamper_control(b_dir, out_dir)

    rc2d_raw = rc2d_suite_path.read_bytes()
    rc2d_sha = sha256_bytes(rc2d_raw)
    rc2d_suite = json.loads(rc2d_raw)
    profile_controls = profile_controls_from_rc2d(
        rc2d_suite,
        validate_suite=validate_suite,
    )
    rc2d_identity_matches = rc2d_sha == RC2D_RECEIPT_SHA256

    weak = weak_candidate_controls(candidate)
    weak_discrimination = all(bool(errors) for errors in weak.values())
    ablation = targeted_ablation_matrix(candidate)
    ablation_enforced = all(row["validator_rejects"] for row in ablation)

    scientific_blockers: list[str] = []
    apparatus_blockers: list[str] = []

    if unresolved:
        scientific_blockers.extend(unresolved)
    if candidate_errors:
        scientific_blockers.extend(candidate_errors)

    if not fingerprint_matches:
        apparatus_blockers.append(
            "fresh pinned real execution did not reproduce frozen RC2-A semantic fingerprint"
        )
    if not policy_matches:
        apparatus_blockers.append("frozen public policy identity mismatch")
    if not deterministic:
        apparatus_blockers.append("candidate projection is not deterministic")
    if not telemetry["invariant"]:
        apparatus_blockers.append(
            "excluded presentation telemetry changed candidate bytes"
        )
    if not firewall["invariant"]:
        scientific_blockers.append("downstream policy changed candidate bytes")
    if not tamper["tamper_detected"]:
        scientific_blockers.append("tampered Contract-B state did not fail closed")
    if not rc2d_identity_matches:
        apparatus_blockers.append(
            "rerun CAL #22 suite bytes differ from frozen decisive receipt"
        )
    if profile_controls["baseline_validator_errors"]:
        apparatus_blockers.append(
            "frozen CAL #22 receipt no longer passes its independent validator"
        )
    if not profile_controls["required_families_present"]:
        apparatus_blockers.append("CAL #22 required attribution families missing")
    if not profile_controls["all_weak_controls_rejected"]:
        apparatus_blockers.append(
            "CAL #22 validator failed a weak/gaming discrimination control"
        )
    if not weak_discrimination:
        apparatus_blockers.append(
            "producer candidate validator accepts a weak/gaming candidate"
        )
    if not ablation_enforced:
        apparatus_blockers.append("targeted missing-state ablation did not fail closed")

    gate = "SATISFIED"
    if scientific_blockers:
        gate = "FAILED"
    elif apparatus_blockers:
        gate = "INCONCLUSIVE"

    boundary_capture = {
        "pins": {
            "cal_production_semantic_sha": CAL_PRODUCTION_SHA,
            "evidence_bundler_production_sha": EB_PRODUCTION_SHA,
            "apparatus_production_sha": APPARATUS_PRODUCTION_SHA,
            "contract_b_version": CONTRACT_B_VERSION,
            "cal_rc2d_decisive_sha": RC2D_DECISIVE_SHA,
        },
        "contract_b_binding": binding,
        "contract_b_files": files,
        "factual_context_state": intake.extension_state,
        "engine": engine,
        "cal_library_version": cal_library_version,
        "semantic_fingerprint": fingerprint,
        "expected_predecessor_fingerprint": RC2A_PREDECESSOR_SEMANTIC_FINGERPRINT,
        "semantic_fingerprint_matches": fingerprint_matches,
        "claim_assessments": [
            item.model_dump(mode="json") for item in assessments
        ],
    }

    source_map = {
        "directly_available_legitimate_state": [
            "validated Contract-B manifest and exact bundle bytes",
            "ClaimAssessment proposition identity",
            "ClaimAssessment candidate/counterevidence refs and scores",
            "ClaimAssessment aggregate support_signal",
            "ClaimAssessment rule flags",
            "ClaimAssessment reported support_label",
            "public frozen AuditPolicy object",
        ],
        "deterministically_derivable_without_new_epistemic_judgment": [
            "proposition text hash",
            "exact policy hash",
            "co-maximal measurement basis",
            "terminal branch identity",
            "necessary/residual contribution roles from controlled production replay",
            "generic assessment execution state not_performed",
            "result/execution stable identities",
        ],
        "reconstructed_only_from_implementation_details": [],
        "downstream_policy": [
            "authority profile",
            "utility/preferences/risk tolerance",
            "workflow routing",
            "outcome forecast/future-state scenario",
        ],
        "unnecessary_telemetry": [
            "candidate rationale",
            "presentation explanation/guidance/limitations",
            "CAL risk_label",
            "source URL duplicated from Contract B",
            "private helper locals and feature ordering",
        ],
        "unknown": unresolved,
    }

    summary = {
        "producer_gate": gate,
        "scientific_blockers": scientific_blockers,
        "apparatus_blockers": apparatus_blockers,
        "candidate_sha256": sha256_bytes(canonical_bytes(candidate)),
        "candidate_result_set_id": candidate["result_set_id"],
        "semantic_fingerprint": fingerprint,
        "semantic_fingerprint_matches_predecessor": fingerprint_matches,
        "policy_sha256": policy_sha,
        "policy_identity_matches": policy_matches,
        "deterministic_reproduction": deterministic,
        "telemetry_invariance": telemetry["invariant"],
        "semantic_firewall_invariance": firewall["invariant"],
        "contract_b_tamper_fail_closed": tamper["tamper_detected"],
        "rc2d_receipt_sha256": rc2d_sha,
        "rc2d_identity_matches": rc2d_identity_matches,
        "rc2d_profile_controls_pass": (
            not profile_controls["baseline_validator_errors"]
            and profile_controls["required_families_present"]
            and profile_controls["all_weak_controls_rejected"]
        ),
        "weak_candidate_controls_rejected": weak_discrimination,
        "targeted_ablation_fail_closed": ablation_enforced,
        "non_claims": [
            "not an overall Contract-C promotion decision",
            "not a Contract-C version assignment",
            "not a production Contract-C exporter",
            "not Consumer B execution",
            "not a Contract-B reopening result",
            "not proof of universal CAL semantic correctness",
        ],
    }

    _write_json(out_dir / "producer-boundary-capture.json", boundary_capture)
    _write_json(out_dir / "real-attribution-controls.json", real_attribution_controls)
    _write_json(out_dir / "contract-c-rc2-producer-candidate.json", candidate)
    _write_json(out_dir / "field-source-map.json", source_map)
    _write_json(
        out_dir / "field-justification-registry.json", field_justification_registry()
    )
    _write_json(out_dir / "field-ablation-matrix.json", ablation)
    _write_json(out_dir / "telemetry-invariance.json", telemetry)
    _write_json(out_dir / "semantic-firewall.json", firewall)
    _write_json(out_dir / "contract-b-integrity-control.json", tamper)
    _write_json(out_dir / "rc2d-profile-controls.json", profile_controls)
    _write_json(out_dir / "weak-candidate-controls.json", weak)
    _write_json(out_dir / "summary.json", summary)
    return summary


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_bytes(value))
