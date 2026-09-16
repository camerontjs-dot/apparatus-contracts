from __future__ import annotations

import argparse
import copy
import hashlib
import importlib
import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

from claim_audit_lab.production_v1.semantic.engine import audit
from claim_audit_lab.production_v1.semantic.models import (
    AdmittedPassage,
    AuditContext,
    EvidenceWorld,
    SemanticFamily,
    TypedProposition,
)

RESOLVER_FREEZE = "1d33e0612befcf8016816197c90c062373796df9"
OLD_RESOLVER = "43b571464734325277374ee81098553fb7c1b944"
CURRENT_CAL = "847cc970642bb648dc994b929c2053b5c9d4648c"
OLD_CAL = "a902621e8baea3063dddd7f92ba975aade305464"
POLICY_SHA256 = "44ecc33519fa8911079595d322f5f0decbf0389af42e153ac32214931798e42c"
OLD_PROJECTION = "9bc152275759304be03b84014c56bd434549a64a"
CURRENT_PROJECTION = "ef32fa4fca52a2bb7fe2896b378f9b6fdef0dfde"

SUPPORT_A = "Women had a higher rate than Men."
SUPPORT_B = "Women had a greater rate than Men."
REFUTE = "Women had a lower rate than Men."
IRRELEVANT = "Cats had a higher rate than Dogs."


def _hex(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def _tagged(value: str) -> str:
    return "sha256:" + _hex(value)


def _aperture(label: str) -> dict[str, object]:
    return {
        "search_scope": {"corpus": label},
        "outcome": {"state": "unknown", "value": None},
        "limitations": [],
    }


def strict_context(rows: list[tuple[str, str]], label: str) -> AuditContext:
    passages = tuple(
        AdmittedPassage.create(pid, f"src-{pid.lower()}", text) for pid, text in rows
    )
    world = EvidenceWorld.create(
        "1.2.0",
        f"bundle-{label}",
        _tagged(f"bundle-{label}"),
        passages,
        _aperture(label),
    )
    proposition = TypedProposition.create(
        "Q1",
        SemanticFamily.STRICT_COMPARISON,
        {
            "lhs_entity": "Women",
            "rhs_entity": "Men",
            "comparison_direction": "MORE_THAN",
        },
        text_sha256=_hex(SUPPORT_A),
    )
    return AuditContext(SUPPORT_A, proposition, world)


def event_context(rows: list[tuple[str, str]], label: str) -> AuditContext:
    passages = tuple(
        AdmittedPassage.create(pid, f"src-{pid.lower()}", text) for pid, text in rows
    )
    world = EvidenceWorld.create(
        "1.2.0",
        f"bundle-{label}",
        _tagged(f"bundle-{label}"),
        passages,
        _aperture(label),
    )
    claim = "Alice reviewed dossier before Bob archived dossier."
    proposition = TypedProposition.create(
        "QE1",
        SemanticFamily.DIRECT_EVENT_ORDER,
        {
            "left_subject": "alice",
            "left_predicate": "review",
            "left_object": "dossier",
            "left_polarity": "positive",
            "temporal_relation": "BEFORE",
            "right_subject": "bob",
            "right_predicate": "archive",
            "right_object": "dossier",
            "right_polarity": "positive",
        },
        text_sha256=_hex(claim),
    )
    return AuditContext(claim, proposition, world)


def unsupported_context() -> AuditContext:
    text = "Alice may release dossier."
    passage = AdmittedPassage.create("U1", "src-u1", text)
    world = EvidenceWorld.create(
        "1.2.0",
        "bundle-unsupported",
        _tagged("bundle-unsupported"),
        (passage,),
        _aperture("unsupported"),
    )
    proposition = TypedProposition.create(
        "QU1",
        SemanticFamily.PERMISSION_EXCEPTION,
        {"actor": "alice"},
        text_sha256=_hex(text),
    )
    return AuditContext(text, proposition, world)


def _load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _load_c2(root: Path) -> ModuleType:
    sys.path.insert(0, str(root))
    try:
        return importlib.import_module("validators.contract_c_v2")
    finally:
        sys.path.pop(0)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _reject(fn, label: str) -> str:
    try:
        fn()
    except Exception as exc:  # noqa: BLE001 - deliberate negative boundary
        return f"{type(exc).__name__}: {exc}"
    raise AssertionError(f"negative control unexpectedly succeeded: {label}")


def _verify_b(c2: ModuleType, sealed: dict[str, Any], context: AuditContext) -> None:
    c2.verify_contract_b_references(
        sealed,
        exact_contract_b={
            "contract_version": context.evidence_world.contract_b_version,
            "bundle_id": context.evidence_world.bundle_id,
            "bundle_hash": context.evidence_world.bundle_hash,
        },
        evidence_index={
            (passage.source_id, passage.passage_id)
            for passage in context.evidence_world.admitted_passages
        },
    )


def evaluate(
    *,
    c2_root: Path,
    resolver_candidate_root: Path,
    predecessor_resolver_root: Path,
    cal_root: Path,
) -> dict[str, Any]:
    c2 = _load_c2(c2_root)
    materialize = _load_module(
        "current_cal_c2_hard_bound_materializer",
        cal_root / "research/contract_c2_current_cal_producer_conformance_rc1/materialize.py",
    )

    candidate_path = (
        resolver_candidate_root
        / "research/contract_c2_current_cal_resolver_successor_rc0/RESOLVER.json"
    )
    candidate_raw = candidate_path.read_text(encoding="utf-8")
    candidate = json.loads(candidate_raw)
    predecessor = _load_json(
        predecessor_resolver_root
        / "research/contract_c_successor_ground_up_20260913/PHASE_1_5_POLICY_RESOLVER.json"
    )

    if candidate.get("schema") != "contract-c-phase-1-5-policy-resolver-v1":
        raise AssertionError("candidate resolver schema drift")
    entries = candidate.get("entries")
    if not isinstance(entries, list) or len(entries) != 2:
        raise AssertionError("candidate resolver must contain exactly two rows")
    old_rows = [row for row in entries if row.get("semantic_implementation_sha") == OLD_CAL]
    current_rows = [row for row in entries if row.get("semantic_implementation_sha") == CURRENT_CAL]
    if len(old_rows) != 1 or len(current_rows) != 1:
        raise AssertionError("resolver semantic implementation cardinality invalid")
    if old_rows[0] != predecessor["entries"][0]:
        raise AssertionError("predecessor resolver row was not preserved exactly")
    current_row = current_rows[0]
    if current_row["policy_sha256"] != POLICY_SHA256:
        raise AssertionError("current policy digest drift")
    if current_row["policy"] != old_rows[0]["policy"]:
        raise AssertionError("current canonical policy payload differs from predecessor")
    if current_row["projection_blob"] != CURRENT_PROJECTION:
        raise AssertionError("current projection blob drift")
    if old_rows[0]["projection_blob"] != OLD_PROJECTION:
        raise AssertionError("old projection provenance drift")
    keys = [row["semantic_implementation_sha"] for row in entries]
    if len(keys) != len(set(keys)):
        raise AssertionError("candidate resolver has duplicate semantic implementation key")
    lowered = candidate_raw.lower()
    for forbidden in ("latest", "http://", "https://", "network"):
        if forbidden in lowered:
            raise AssertionError(f"mutable or network authority marker in resolver: {forbidden}")

    cases = {
        "strict_support": strict_context([("S1", SUPPORT_A)], "strict-support"),
        "strict_refutation": strict_context([("R1", REFUTE)], "strict-refutation"),
        "alternative_joint": strict_context(
            [("S1", SUPPORT_A), ("S2", SUPPORT_B), ("R1", REFUTE)],
            "alternative-joint",
        ),
        "irrelevant_only": strict_context([("N1", IRRELEVANT)], "irrelevant-only"),
        "measurement_not_applicable": strict_context(
            [("N1", "The report describes annual enrollment totals.")],
            "measurement-not-applicable",
        ),
        "negative_event_unresolved": event_context(
            [("E1", "Alice did not review dossier before Bob archived dossier.")],
            "negative-event-unresolved",
        ),
        "support_plus_unresolved": event_context(
            [
                ("E1", "Alice reviewed dossier before Bob archived dossier."),
                ("E2", "Alice did not review dossier before Bob archived dossier."),
            ],
            "support-plus-unresolved",
        ),
        "unsupported_family": unsupported_context(),
    }

    observations: dict[str, Any] = {}
    sealed_by_case: dict[str, dict[str, Any]] = {}
    failures: list[str] = []
    for case_id, context in cases.items():
        try:
            result = audit(context)
            unsealed = materialize.materialize_unsealed(
                context,
                result,
                policy_resolver_commit_sha=RESOLVER_FREEZE,
            )
            sealed = c2.seal(unsealed)
            c2.validate_object(sealed)
            _verify_b(c2, sealed, context)
            resolved = c2.verify_policy_resolution(
                sealed,
                independently_selected_resolver_commit_sha=RESOLVER_FREEZE,
                resolver_entries=entries,
            )
            repeat = c2.seal(
                materialize.materialize_unsealed(
                    context,
                    result,
                    policy_resolver_commit_sha=RESOLVER_FREEZE,
                )
            )
            if c2.canonical_bytes(repeat) != c2.canonical_bytes(sealed):
                raise AssertionError("deterministic repeat mismatch")
            if sealed["producer"]["semantic_implementation_sha"] != CURRENT_CAL:
                raise AssertionError("current producer semantic identity mismatch")
            if sealed["producer"]["policy_sha256"] != POLICY_SHA256:
                raise AssertionError("current producer policy digest mismatch")
            if resolved != current_row:
                raise AssertionError("resolver did not return exact current row")
            sealed_by_case[case_id] = sealed
            observations[case_id] = {
                "terminal": sealed["propositions"][0]["terminal"],
                "result_set_id": sealed["result_set_id"],
                "whole_object_sha256": c2.whole_object_sha256(sealed),
                "resolver_row": CURRENT_CAL,
                "deterministic_repeat": True,
            }
        except Exception as exc:  # noqa: BLE001 - terminal research result
            failures.append(f"{case_id}: {type(exc).__name__}: {exc}")

    negative: dict[str, str] = {}
    if "strict_support" in sealed_by_case:
        sample = sealed_by_case["strict_support"]
        sample_context = cases["strict_support"]
        sample_result = audit(sample_context)

        old_bound = c2.seal(
            materialize.materialize_unsealed(
                sample_context,
                sample_result,
                policy_resolver_commit_sha=OLD_RESOLVER,
            )
        )
        negative["predecessor_resolver_rejects_current_cal"] = _reject(
            lambda: c2.verify_policy_resolution(
                old_bound,
                independently_selected_resolver_commit_sha=OLD_RESOLVER,
                resolver_entries=predecessor["entries"],
            ),
            "predecessor resolver accepted current CAL",
        )

        without_current = [row for row in entries if row["semantic_implementation_sha"] != CURRENT_CAL]
        negative["missing_current_row_rejected"] = _reject(
            lambda: c2.verify_policy_resolution(
                sample,
                independently_selected_resolver_commit_sha=RESOLVER_FREEZE,
                resolver_entries=without_current,
            ),
            "candidate without current row accepted current CAL",
        )

        wrong_policy = copy.deepcopy(sample)
        wrong_policy["producer"]["policy_sha256"] = "0" * 64
        wrong_policy = c2.seal(wrong_policy)
        negative["wrong_policy_digest_rejected"] = _reject(
            lambda: c2.verify_policy_resolution(
                wrong_policy,
                independently_selected_resolver_commit_sha=RESOLVER_FREEZE,
                resolver_entries=entries,
            ),
            "wrong policy digest",
        )

        duplicated = [*entries, copy.deepcopy(current_row)]
        negative["duplicate_current_row_rejected"] = _reject(
            lambda: c2.verify_policy_resolution(
                sample,
                independently_selected_resolver_commit_sha=RESOLVER_FREEZE,
                resolver_entries=duplicated,
            ),
            "duplicate current resolver row",
        )

        unknown_impl = copy.deepcopy(sample)
        unknown_impl["producer"]["semantic_implementation_sha"] = "f" * 40
        unknown_impl = c2.seal(unknown_impl)
        negative["unknown_semantic_implementation_rejected"] = _reject(
            lambda: c2.verify_policy_resolution(
                unknown_impl,
                independently_selected_resolver_commit_sha=RESOLVER_FREEZE,
                resolver_entries=entries,
            ),
            "unknown semantic implementation",
        )

        predecessor_commit_object = c2.seal(
            materialize.materialize_unsealed(
                sample_context,
                sample_result,
                policy_resolver_commit_sha=OLD_RESOLVER,
            )
        )
        negative["predecessor_commit_substitution_rejected_by_candidate_authority"] = _reject(
            lambda: c2.verify_policy_resolution(
                predecessor_commit_object,
                independently_selected_resolver_commit_sha=RESOLVER_FREEZE,
                resolver_entries=entries,
            ),
            "predecessor resolver commit substituted under candidate authority",
        )

        old_compat = copy.deepcopy(sample)
        old_compat["producer"] = {
            "semantic_implementation_sha": OLD_CAL,
            "policy_sha256": POLICY_SHA256,
            "policy_resolver_commit_sha": RESOLVER_FREEZE,
        }
        old_compat = c2.seal(old_compat)
        resolved_old = c2.verify_policy_resolution(
            old_compat,
            independently_selected_resolver_commit_sha=RESOLVER_FREEZE,
            resolver_entries=entries,
        )
        if resolved_old != old_rows[0]:
            failures.append("preserved old row did not resolve exactly under candidate resolver")

    classification = (
        "SUPPORTED_CURRENT_CAL_C2_RESOLVER_SUCCESSOR"
        if not failures and len(observations) == 8 and len(negative) == 6
        else "FALSIFIED_CURRENT_CAL_RESOLVER_SUCCESSOR"
    )
    return {
        "schema": "contract-c2-current-cal-resolver-successor-rc0-result-v1",
        "classification": classification,
        "resolver_freeze": RESOLVER_FREEZE,
        "predecessor_resolver": OLD_RESOLVER,
        "current_cal": CURRENT_CAL,
        "policy_sha256": POLICY_SHA256,
        "current_projection_blob": CURRENT_PROJECTION,
        "old_row_preserved_exactly": old_rows[0] == predecessor["entries"][0],
        "current_row": current_row,
        "observations": observations,
        "negative_controls": negative,
        "failures": failures,
        "nonclaims": [
            "No Contract C2 merge, release, or canonical discovery switch is authorized.",
            "No Decision, Contract E, Authorization, or execution claim is established.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--c2", type=Path, required=True)
    parser.add_argument("--resolver-candidate", type=Path, required=True)
    parser.add_argument("--predecessor-resolver", type=Path, required=True)
    parser.add_argument("--cal", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = evaluate(
        c2_root=args.c2.resolve(),
        resolver_candidate_root=args.resolver_candidate.resolve(),
        predecessor_resolver_root=args.predecessor_resolver.resolve(),
        cal_root=args.cal.resolve(),
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"classification": result["classification"], "failures": result["failures"]}, sort_keys=True))
    return 0 if result["classification"] == "SUPPORTED_CURRENT_CAL_C2_RESOLVER_SUCCESSOR" else 1


if __name__ == "__main__":
    raise SystemExit(main())
