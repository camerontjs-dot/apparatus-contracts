from __future__ import annotations

import copy
import hashlib
import importlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import candidate_rc0 as candidate  # noqa: E402

CAL_ROOT = Path(os.environ["CAL_ROOT"]).resolve()
CAL_FIXTURE_ROOT = Path(os.environ["CAL_FIXTURE_ROOT"]).resolve()
EB_ROOT = Path(os.environ["EB_ROOT"]).resolve()
C2_ROOT = Path(os.environ["C2_ROOT"]).resolve()
RESOLVER_JSON = Path(os.environ["RESOLVER_JSON"]).resolve()

sys.path.insert(0, str(CAL_ROOT / "src"))
sys.path.insert(0, str(EB_ROOT / "src"))
sys.path.insert(0, str(C2_ROOT))

rc2 = importlib.import_module("validators.contract_c_rc2")
POLICY_RESOLVER_COMMIT = candidate.POLICY_RESOLVER_COMMIT

OLD_CANDIDATE_PATH = (
    HERE.parent
    / "contract_c_cal_v1_parent_recomposition_rc0_20260919"
    / "candidate_rc0.py"
)
_old_spec = importlib.util.spec_from_file_location(
    "contract_c_parent_old_candidate", OLD_CANDIDATE_PATH
)
if _old_spec is None or _old_spec.loader is None:
    raise RuntimeError(f"unable to load frozen old candidate: {OLD_CANDIDATE_PATH}")
old_candidate = importlib.util.module_from_spec(_old_spec)
_old_spec.loader.exec_module(old_candidate)

OLD_SEMANTIC = "847cc970642bb648dc994b929c2053b5c9d4648c"
NEW_SEMANTIC = "caa0048f8f511ec3c4aa1ce713766f2219a04bc1"
OLD_RESOLVER_COMMIT = "1d33e0612befcf8016816197c90c062373796df9"
OLD_PROJECTION_BLOB = "ef32fa4fca52a2bb7fe2896b378f9b6fdef0dfde"
PROJECTION_ROOT = Path(os.environ["PROJECTION_ROOT"]).resolve()
RESOLVER_ROOT = Path(os.environ["RESOLVER_ROOT"]).resolve()
OLD_RESOLVER_JSON = Path(os.environ["OLD_RESOLVER_JSON"]).resolve()
OLD_PROJECTION_PATH = (
    PROJECTION_ROOT
    / "research/contract_c_polarity_projection_authority_rc0_20261003/projection_old.py"
)
NEW_PROJECTION_PATH = (
    PROJECTION_ROOT
    / "research/contract_c_polarity_projection_authority_rc0_20261003/projection_successor.py"
)


def _load_integration_module() -> Any:
    path = CAL_FIXTURE_ROOT / "tests" / "research" / "test_cal_v1_a2_eb_b_parent_integration_rc0.py"
    spec = importlib.util.spec_from_file_location("frozen_cal_parent_integration", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load frozen integration harness: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _tagged_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _public_terminal(record: dict[str, Any]) -> tuple[str, str]:
    result = record["result"]
    conclusion = result["conclusion"]
    failure = result["failure_code"]
    if conclusion == "supported":
        return "supported", "categorical_support"
    if conclusion == "contradicted":
        return "contradicted", "categorical_refutation"
    if failure == "MIXED_RELATIONS":
        return "not_checkable", "MIXED_RELATIONS"
    if failure == "UNSUPPORTED_SEMANTIC_FAMILY":
        return "not_checkable", "UNSUPPORTED_SEMANTIC_FAMILY"
    if failure == "RELATION_UNRESOLVED":
        has_unresolved = any(
            trace.get("relation") is not None
            and trace["relation"].get("categorical_relation") == "UNRESOLVED"
            for trace in result["traces"]
        )
        return (
            ("not_checkable", "unresolved_categorical_relation")
            if has_unresolved
            else ("not_checkable", "no_deciding_relation")
        )
    if failure == "NO_DECIDING_RELATION":
        return "not_checkable", "no_deciding_relation"
    raise ValueError(f"UNREPRESENTABLE_RC2_TERMINAL:{conclusion}:{failure}")


def _participant_rows(
    record: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[list[dict[str, str]]]]:
    traces = record["result"]["traces"]
    deciding = set(record["result"]["deciding_passage_ids"])
    participants: list[dict[str, Any]] = []
    support_refs: list[dict[str, str]] = []
    refute_refs: list[dict[str, str]] = []
    unresolved_refs: list[dict[str, str]] = []

    for trace in traces:
        relation = trace.get("relation")
        authority = trace.get("authority")
        if relation is None or authority is None:
            continue
        atom = authority.get("atom") or {}
        ref = {
            "source_id": str(atom["source_id"]),
            "passage_id": str(trace["passage_id"]),
        }
        category = relation["categorical_relation"]
        if category == "SUPPORTS":
            label = "supports"
            support_refs.append(ref)
        elif category == "REFUTES":
            label = "refutes"
            refute_refs.append(ref)
        else:
            label = "non_polarized"
            unresolved_refs.append(ref)
        participants.append(
            {
                "evidence_ref": ref,
                "relation": label,
                "role": "causal" if trace["passage_id"] in deciding else "residual",
            }
        )

    verdict, reason = _public_terminal(record)
    if verdict == "supported":
        groups = [
            [ref]
            for ref in support_refs
            if any(
                p["evidence_ref"] == ref and p["role"] == "causal"
                for p in participants
            )
        ]
    elif verdict == "contradicted":
        groups = [
            [ref]
            for ref in refute_refs
            if any(
                p["evidence_ref"] == ref and p["role"] == "causal"
                for p in participants
            )
        ]
    elif reason == "MIXED_RELATIONS":
        groups = [[s, r] for s in support_refs for r in refute_refs]
        causal = {
            (x["source_id"], x["passage_id"]) for group in groups for x in group
        }
        for row in participants:
            key = (
                row["evidence_ref"]["source_id"],
                row["evidence_ref"]["passage_id"],
            )
            row["role"] = "causal" if key in causal else "residual"
    elif reason == "unresolved_categorical_relation":
        groups = [[ref] for ref in unresolved_refs]
        causal = {
            (x["source_id"], x["passage_id"]) for group in groups for x in group
        }
        for row in participants:
            key = (
                row["evidence_ref"]["source_id"],
                row["evidence_ref"]["passage_id"],
            )
            row["role"] = "causal" if key in causal else "residual"
    else:
        groups = []
        for row in participants:
            row["role"] = "residual"
            if reason in {"no_deciding_relation", "UNSUPPORTED_SEMANTIC_FAMILY"}:
                row["relation"] = "non_polarized"
    return participants, groups


def _rc2_prop(record: dict[str, Any]) -> dict[str, Any]:
    verdict, reason = _public_terminal(record)
    participants, groups = _participant_rows(record)
    completion = (
        "assessed" if verdict in {"supported", "contradicted"} else "not_checkable"
    )
    return {
        "proposition": {
            "proposition_id": record["proposition"]["proposition_id"],
            "content_sha256": "sha256:" + record["proposition"]["proposition_sha256"],
        },
        "execution": {"state": "completed", "completion": completion},
        "terminal": {"verdict": verdict, "reason": reason},
        "participants": participants,
        "basis_groups": groups,
    }


def _contract_b_from_record(record: dict[str, Any]) -> dict[str, str]:
    row = record["input"]["contract_b"]
    return {
        "contract_version": str(row["version"]),
        "bundle_id": str(row["bundle_id"]),
        "bundle_hash": str(row["bundle_hash"]),
    }


def _evidence_index(package: dict[str, Any]) -> set[tuple[str, str]]:
    return {
        (str(row["source_id"]), str(row["passage_id"]))
        for row in package["candidates"]
    }


def _recomposition_authority(
    result: dict[str, Any], rc2_obj: dict[str, Any]
) -> dict[str, Any]:
    contract_a = result["contract_a"]
    declaration = contract_a["decomposition"]
    root = contract_a["root_proposition"]
    by_id = {
        row["proposition"]["proposition_id"]: row["proposition"]["content_sha256"]
        for row in rc2_obj["propositions"]
    }
    outcomes = {
        result["c1"].proposition_id: result["c1"],
        result["c2"].proposition_id: result["c2"],
    }
    native = {
        result["c1"].proposition_id: _tagged_bytes(result["c1_bytes"]),
        result["c2"].proposition_id: _tagged_bytes(result["c2_bytes"]),
    }
    return {
        "cal_freeze_commit": candidate.CAL_FREEZE_COMMIT,
        "cal_semantic_source_commit": candidate.CAL_SEMANTIC_SOURCE_COMMIT,
        "root": {
            "proposition_id": str(root["proposition_id"]),
            "text_sha256": str(root["text_sha256"]),
        },
        "decomposition_id": str(declaration["decomposition_id"]),
        "operator": str(declaration["operator"]),
        "ordered_children": [
            {
                "sequence": int(row["sequence"]),
                "proposition_id": str(row["proposition_id"]),
                "text_sha256": str(row["text_sha256"]),
                "contract_c_content_sha256": by_id[str(row["proposition_id"])],
                "native_result_sha256": native[str(row["proposition_id"])],
                "cal_result_id": outcomes[str(row["proposition_id"])].result_id,
                "conclusion": outcomes[str(row["proposition_id"])].conclusion.value,
            }
            for row in declaration["children"]
        ],
        "decomposition_receipt_id": result["parent"].receipt.receipt_id,
        "parent_conclusion": result["parent"].conclusion.value,
    }


def _build_case(
    result: dict[str, Any], resolver: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any]]:
    p1 = _rc2_prop(result["c1_record"])
    p2 = _rc2_prop(result["c2_record"])
    cb1 = _contract_b_from_record(result["c1_record"])
    cb2 = _contract_b_from_record(result["c2_record"])
    if cb1 != cb2:
        raise ValueError("child results do not share exact Contract B world")
    inner = rc2.seal(
        {
            "profile": rc2.PROFILE,
            "contract_b": cb1,
            "producer": {
                "semantic_implementation_sha": candidate.CAL_SEMANTIC_IMPLEMENTATION,
                "policy_sha256": candidate.POLICY_SHA256,
                "policy_resolver_commit_sha": candidate.POLICY_RESOLVER_COMMIT,
            },
            "execution": {"state": "completed"},
            "propositions": [p1, p2],
        }
    )
    inner_expected = rc2.whole_object_sha256(inner)
    rc2.verify_candidate(
        inner,
        exact_contract_b=cb1,
        evidence_index=_evidence_index(result["package"]),
        independently_selected_resolver_commit_sha=POLICY_RESOLVER_COMMIT,
        resolver_entries=resolver["entries"],
        expected_whole_object_sha256=inner_expected,
    )

    authority = _recomposition_authority(result, inner)
    outer = candidate.seal(
        {
            "profile": candidate.PROFILE,
            "rc2_result": inner,
            "recomposition": authority,
        }
    )
    candidate.validate_object(outer, rc2_validator=rc2)
    candidate.verify_recomposition_authority(
        outer, exact_recomposition=authority, rc2_validator=rc2
    )
    return outer, authority


def _expect_reject(fn: Any) -> bool:
    try:
        fn()
    except Exception:
        return True
    return False


def _mutations(
    base: dict[str, Any], authority: dict[str, Any]
) -> dict[str, bool]:
    expected_whole = candidate.whole_object_sha256(base, rc2_validator=rc2)
    checks: dict[str, bool] = {}

    def authority_reject(mutator: Any) -> bool:
        x = copy.deepcopy(base)
        mutator(x)
        x.pop("result_set_id", None)
        x = candidate.seal(x)
        return _expect_reject(
            lambda: candidate.verify_recomposition_authority(
                x, exact_recomposition=authority, rc2_validator=rc2
            )
        )

    checks["wrong_child_result_id"] = authority_reject(
        lambda x: x["recomposition"]["ordered_children"][0].__setitem__(
            "cal_result_id", "cal-child-result:" + "0" * 64
        )
    )
    checks["changed_native_result_hash"] = authority_reject(
        lambda x: x["recomposition"]["ordered_children"][0].__setitem__(
            "native_result_sha256", "sha256:" + "1" * 64
        )
    )

    omitted = copy.deepcopy(base)
    omitted["recomposition"]["ordered_children"] = omitted["recomposition"][
        "ordered_children"
    ][:1]
    omitted.pop("result_set_id", None)
    omitted = candidate.seal(omitted)
    checks["omitted_child"] = _expect_reject(
        lambda: candidate.validate_object(omitted, rc2_validator=rc2)
    )

    checks["semantic_sequence_change"] = authority_reject(
        lambda x: (
            x["recomposition"]["ordered_children"][0].__setitem__("sequence", 2),
            x["recomposition"]["ordered_children"][1].__setitem__("sequence", 1),
        )
    )
    checks["wrong_root"] = authority_reject(
        lambda x: x["recomposition"]["root"].__setitem__(
            "text_sha256", "sha256:" + "2" * 64
        )
    )
    checks["stale_receipt"] = authority_reject(
        lambda x: x["recomposition"].__setitem__(
            "decomposition_receipt_id", "3" * 64
        )
    )
    checks["parent_conclusion_mutation"] = authority_reject(
        lambda x: x["recomposition"].__setitem__(
            "parent_conclusion",
            "contradicted"
            if x["recomposition"]["parent_conclusion"] != "contradicted"
            else "supported",
        )
    )

    opaque = copy.deepcopy(base)
    opaque["recomposition"]["ordered_children"][0]["cal_result_id"] = (
        "state:private-codec"
    )
    opaque.pop("result_set_id", None)
    opaque = candidate.seal(opaque)
    checks["opaque_private_codec_rejected"] = _expect_reject(
        lambda: candidate.validate_object(opaque, rc2_validator=rc2)
    )

    permuted = copy.deepcopy(base)
    permuted["recomposition"]["ordered_children"].reverse()
    permuted.pop("result_set_id", None)
    permuted = candidate.seal(permuted)
    checks["array_permutation_canonical"] = (
        candidate.canonical_bytes(permuted, rc2_validator=rc2)
        == candidate.canonical_bytes(base, rc2_validator=rc2)
    )

    inner_mutated = copy.deepcopy(base)
    inner_mutated["rc2_result"]["propositions"][0]["proposition"][
        "content_sha256"
    ] = "sha256:" + "4" * 64
    inner_mutated["rc2_result"].pop("result_set_id", None)
    inner_mutated["rc2_result"] = rc2.seal(inner_mutated["rc2_result"])
    inner_mutated.pop("result_set_id", None)
    inner_mutated = candidate.seal(inner_mutated)
    checks["inner_rc2_child_content_substitution"] = _expect_reject(
        lambda: candidate.validate_object(inner_mutated, rc2_validator=rc2)
    )

    coherent = copy.deepcopy(base)
    coherent["recomposition"]["ordered_children"][0][
        "native_result_sha256"
    ] = "sha256:" + "5" * 64
    coherent.pop("result_set_id", None)
    coherent = candidate.seal(coherent)
    candidate.validate_object(coherent, rc2_validator=rc2)
    checks["coherent_reseal_rejected_by_fixed_authority"] = _expect_reject(
        lambda: candidate.verify_recomposition_authority(
            coherent, exact_recomposition=authority, rc2_validator=rc2
        )
    )
    checks["external_whole_object_replay_mismatch"] = _expect_reject(
        lambda: candidate.verify_external_authority(
            coherent,
            expected_whole_object_sha256=expected_whole,
            rc2_validator=rc2,
        )
    )
    return checks


def _load_path_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load projection module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _git_blob(root: Path, path: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), "hash-object", str(path)],
        text=True,
    ).strip()


def _projection_audit(evidence_text: str) -> tuple[Any, Any]:
    from claim_audit_lab.production_v1.semantic.engine import audit
    from claim_audit_lab.production_v1.semantic.models import (
        AdmittedPassage,
        AuditContext,
        EvidenceWorld,
        SemanticFamily,
        TypedProposition,
    )

    claim = "Alpha had a higher rate than Beta."
    proposition = TypedProposition.create(
        "C1",
        SemanticFamily.STRICT_COMPARISON,
        {
            "lhs_entity": "Alpha",
            "rhs_entity": "Beta",
            "comparison_direction": "MORE_THAN",
        },
        text_sha256=hashlib.sha256(claim.encode("utf-8")).hexdigest(),
    )
    passage = AdmittedPassage.create(
        "p1",
        "s1",
        evidence_text,
        "sha256:" + hashlib.sha256(b"authority-successor-source").hexdigest(),
    )
    world = EvidenceWorld.create(
        "1.2.0",
        "contract-c-polarity-authority-successor",
        "sha256:" + hashlib.sha256(b"contract-c-polarity-authority-successor").hexdigest(),
        (passage,),
        {
            "contract_b_factual_context_state": "present",
            "observation": {"scope": "contract-c-polarity-authority-successor"},
        },
    )
    context = AuditContext(claim, proposition, world)
    return context, audit(context)


def _authority_controls(resolver: dict[str, Any]) -> dict[str, Any]:
    old_raw = OLD_PROJECTION_PATH.read_text(encoding="utf-8")
    new_raw = NEW_PROJECTION_PATH.read_text(encoding="utf-8")
    old_blob = _git_blob(PROJECTION_ROOT, OLD_PROJECTION_PATH)
    new_blob = _git_blob(PROJECTION_ROOT, NEW_PROJECTION_PATH)
    projection_source_exact = (
        old_blob == OLD_PROJECTION_BLOB
        and old_raw.count(OLD_SEMANTIC) == 1
        and new_raw == old_raw.replace(OLD_SEMANTIC, NEW_SEMANTIC)
    )

    old_resolver = json.loads(OLD_RESOLVER_JSON.read_text(encoding="utf-8"))
    old_entries = old_resolver["entries"]
    new_entries = resolver["entries"]
    old_reference = next(
        entry for entry in old_entries
        if entry["semantic_implementation_sha"] == OLD_SEMANTIC
        and entry["policy_sha256"] == candidate.POLICY_SHA256
    )
    expected_entry = copy.deepcopy(old_reference)
    expected_entry["semantic_implementation_sha"] = NEW_SEMANTIC
    expected_entry["projection_blob"] = new_blob
    resolver_exact = (
        resolver.get("schema") == old_resolver.get("schema")
        and new_entries[:-1] == old_entries
        and len(new_entries) == len(old_entries) + 1
        and new_entries[-1] == expected_entry
    )
    old_has_new = [
        entry for entry in old_entries
        if entry.get("semantic_implementation_sha") == NEW_SEMANTIC
        and entry.get("policy_sha256") == candidate.POLICY_SHA256
    ]
    new_has_new = [
        entry for entry in new_entries
        if entry.get("semantic_implementation_sha") == NEW_SEMANTIC
        and entry.get("policy_sha256") == candidate.POLICY_SHA256
    ]

    resolver_head = subprocess.check_output(
        ["git", "-C", str(RESOLVER_ROOT), "rev-parse", "HEAD"],
        text=True,
    ).strip()
    resolver_commit_exact = candidate.POLICY_RESOLVER_COMMIT == resolver_head

    old_projection = _load_path_module(OLD_PROJECTION_PATH, "cal_old_projection_authority")
    new_projection = _load_path_module(NEW_PROJECTION_PATH, "cal_new_projection_authority")

    projection_cases: dict[str, Any] = {}
    for case_id, evidence_text, expected in (
        ("positive", "Alpha had a higher rate than Beta.", "supported"),
        ("negative", "Alpha did not have a higher rate than Beta.", "contradicted"),
    ):
        context, result = _projection_audit(evidence_text)
        old_rejected = _expect_reject(
            lambda c=context, r=result: old_projection.materialize_unsealed(
                c,
                r,
                policy_resolver_commit_sha=candidate.POLICY_RESOLVER_COMMIT,
            )
        )
        unsealed = new_projection.materialize_unsealed(
            context,
            result,
            policy_resolver_commit_sha=candidate.POLICY_RESOLVER_COMMIT,
        )
        terminal = unsealed["propositions"][0]["terminal"]["verdict"]
        producer = unsealed["producer"]
        sealed = rc2.seal(unsealed)
        expected_whole = rc2.whole_object_sha256(sealed)
        rc2.verify_candidate(
            sealed,
            exact_contract_b=unsealed["contract_b"],
            evidence_index={("s1", "p1")},
            independently_selected_resolver_commit_sha=candidate.POLICY_RESOLVER_COMMIT,
            resolver_entries=new_entries,
            expected_whole_object_sha256=expected_whole,
        )
        projection_cases[case_id] = {
            "old_projection_rejected": old_rejected,
            "terminal": terminal,
            "expected_terminal": expected,
            "producer_semantic": producer["semantic_implementation_sha"],
            "producer_policy": producer["policy_sha256"],
            "producer_resolver": producer["policy_resolver_commit_sha"],
            "rc2_verified": True,
        }

    return {
        "old_projection_blob": old_blob,
        "successor_projection_blob": new_blob,
        "projection_source_exact": projection_source_exact,
        "resolver_exact_one_entry": resolver_exact,
        "old_resolver_has_new_binding": len(old_has_new),
        "successor_resolver_new_binding_count": len(new_has_new),
        "resolver_commit_exact": resolver_commit_exact,
        "projection_cases": projection_cases,
    }



def main() -> None:
    out = Path(sys.argv[1])
    out.parent.mkdir(parents=True, exist_ok=True)
    resolver = json.loads(RESOLVER_JSON.read_text(encoding="utf-8"))
    integration = _load_integration_module()
    authority_controls = _authority_controls(resolver)

    observations: dict[str, Any] = {}
    built: dict[str, tuple[dict[str, Any], dict[str, Any]]] = {}
    representability_failures: list[dict[str, Any]] = []
    old_candidate_rejections: dict[str, bool] = {}

    old_raw = OLD_CANDIDATE_PATH.read_text(encoding="utf-8")
    new_raw = (HERE / "candidate_rc0.py").read_text(encoding="utf-8")
    expected_candidate = old_raw.replace(OLD_SEMANTIC, NEW_SEMANTIC).replace(
        OLD_RESOLVER_COMMIT,
        candidate.POLICY_RESOLVER_COMMIT,
    )
    authority_only_candidate_diff = new_raw == expected_candidate
    if old_raw.count(OLD_SEMANTIC) != 1:
        raise RuntimeError("old candidate semantic identity occurrence count changed")
    if old_raw.count(OLD_RESOLVER_COMMIT) != 1:
        raise RuntimeError("old candidate resolver identity occurrence count changed")
    if new_raw.count(NEW_SEMANTIC) != 1:
        raise RuntimeError("successor semantic identity occurrence count invalid")
    if new_raw.count(candidate.POLICY_RESOLVER_COMMIT) != 1:
        raise RuntimeError("successor resolver identity occurrence count invalid")

    for case in integration.CASES:
        result = integration._execute_case(case, out.parent / "cal-runs")
        child_failures: list[dict[str, Any]] = []
        for label, record in (
            ("C1", result["c1_record"]),
            ("C2", result["c2_record"]),
        ):
            try:
                terminal = _public_terminal(record)
            except ValueError as exc:
                terminal = None
                child_failures.append(
                    {
                        "child": label,
                        "conclusion": record["result"]["conclusion"],
                        "failure_code": record["result"]["failure_code"],
                        "error": str(exc),
                    }
                )
            observations[f"{case.case_id}:{label}"] = {
                "conclusion": record["result"]["conclusion"],
                "failure_code": record["result"]["failure_code"],
                "rc2_terminal": terminal,
            }
        if child_failures:
            representability_failures.append(
                {"case": case.case_id, "children": child_failures}
            )
            continue
        built_case = _build_case(result, resolver)
        built[case.case_id] = built_case
        old_candidate_rejections[case.case_id] = _expect_reject(
            lambda obj=built_case[0]: old_candidate.validate_object(obj, rc2_validator=rc2)
        )

    if representability_failures:
        result = {
            "schema": "contract-c-cal-v1-parent-recomposition-rc0-result-v1",
            "disposition": "FALSIFIED_RC2_PLUS_BINDING_INSUFFICIENT",
            "stop_rule": "RC2_GRAMMAR_SUFFICIENCY",
            "exact_subjects": {
                "cal_freeze": candidate.CAL_FREEZE_COMMIT,
                "cal_semantic_source": candidate.CAL_SEMANTIC_SOURCE_COMMIT,
                "cal_semantic_implementation": candidate.CAL_SEMANTIC_IMPLEMENTATION,
                "rc2": "b42c827acb0a9fe65353354d709add0e27bab307",
            },
            "representability_failures": representability_failures,
            "observations": observations,
            "mutation_pressure_executed": False,
            "production_promotion_authorized": False,
        }
        out.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(json.dumps(result, sort_keys=True))
        raise SystemExit(2)

    mutation_results: dict[str, dict[str, bool]] = {}
    failures: list[str] = []
    if not authority_only_candidate_diff:
        failures.append("candidate_diff:not_authority_only")
    if not authority_controls["projection_source_exact"]:
        failures.append("projection:not_identity_guard_only")
    if not authority_controls["resolver_exact_one_entry"]:
        failures.append("resolver:not_exact_one_entry")
    if authority_controls["old_resolver_has_new_binding"] != 0:
        failures.append("resolver:old_unexpectedly_has_new_binding")
    if authority_controls["successor_resolver_new_binding_count"] != 1:
        failures.append("resolver:new_binding_not_unique")
    if not authority_controls["resolver_commit_exact"]:
        failures.append("resolver:commit_identity_mismatch")
    for case_id, row in authority_controls["projection_cases"].items():
        if not row["old_projection_rejected"]:
            failures.append(f"projection:{case_id}:old_did_not_reject")
        if row["terminal"] != row["expected_terminal"]:
            failures.append(f"projection:{case_id}:terminal_mismatch")
        if row["producer_semantic"] != NEW_SEMANTIC:
            failures.append(f"projection:{case_id}:semantic_identity_mismatch")
        if row["producer_policy"] != candidate.POLICY_SHA256:
            failures.append(f"projection:{case_id}:policy_mismatch")
        if row["producer_resolver"] != candidate.POLICY_RESOLVER_COMMIT:
            failures.append(f"projection:{case_id}:resolver_mismatch")
        if not row["rc2_verified"]:
            failures.append(f"projection:{case_id}:rc2_not_verified")
    failures.extend(
        f"{case_id}:old_candidate_did_not_reject"
        for case_id, rejected in old_candidate_rejections.items()
        if not rejected
    )
    for case_id, (obj, authority) in built.items():
        checks = _mutations(obj, authority)
        mutation_results[case_id] = checks
        failures.extend(
            f"{case_id}:{name}" for name, ok in checks.items() if not ok
        )

    # Preregistered cross-run replay: PIPE01 and PIPE03 share a supported C1
    # proposition/conclusion but arise from distinct exact evidence worlds.
    # A replayed child identity must remain structurally legible yet fail
    # against PIPE01's independently fixed recomposition authority.
    replay_base, replay_authority = built["PIPE01"]
    _, replay_source_authority = built["PIPE03"]
    replay = copy.deepcopy(replay_base)
    source_child = replay_source_authority["ordered_children"][0]
    target_child = replay["recomposition"]["ordered_children"][0]
    target_child["native_result_sha256"] = source_child["native_result_sha256"]
    target_child["cal_result_id"] = source_child["cal_result_id"]
    replay.pop("result_set_id", None)
    replay = candidate.seal(replay)
    replay_structurally_valid = True
    try:
        candidate.validate_object(replay, rc2_validator=rc2)
    except Exception:
        replay_structurally_valid = False
    replay_authority_rejected = _expect_reject(
        lambda: candidate.verify_recomposition_authority(
            replay,
            exact_recomposition=replay_authority,
            rc2_validator=rc2,
        )
    )
    replay_ok = replay_structurally_valid and replay_authority_rejected
    mutation_results["PIPE01"]["cross_run_child_replay"] = replay_ok
    if not replay_ok:
        failures.append("PIPE01:cross_run_child_replay")

    disposition = (
        "SUPPORTED_AUTHORITY_ONLY_CONTRACT_C_POLARITY_SUCCESSOR"
        if not failures
        else "FALSIFIED_AUTHORITY_ONLY_CONTRACT_C_SUCCESSOR"
    )
    result = {
        "schema": "contract-c-cal-v1-parent-recomposition-rc0-result-v1",
        "disposition": disposition,
        "stop_rule": None if not failures else "PARENT_BINDING_PRESSURE",
        "exact_subjects": {
            "cal_freeze": candidate.CAL_FREEZE_COMMIT,
            "cal_semantic_source": candidate.CAL_SEMANTIC_SOURCE_COMMIT,
            "cal_semantic_implementation": candidate.CAL_SEMANTIC_IMPLEMENTATION,
            "rc2": "b42c827acb0a9fe65353354d709add0e27bab307",
            "resolver": candidate.POLICY_RESOLVER_COMMIT,
        },
        "observations": observations,
        "authority_only_candidate_diff": authority_only_candidate_diff,
        "authority_controls": authority_controls,
        "old_candidate_rejections": old_candidate_rejections,
        "mutation_pressure_executed": True,
        "mutation_results": mutation_results,
        "failures": failures,
        "independent_consumer_established": False,
        "production_promotion_authorized": False,
    }
    out.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, sort_keys=True))
    if failures:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
