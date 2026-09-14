from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import candidate_a_rc2 as C  # noqa: E402

RC1_DIR = ROOT / "research" / "contract_c_successor_candidate_a_rc1_20260913"
P2_PATH = ROOT / "research" / "contract_c_successor_ground_up_20260913" / "phase2_bakeoff.py"
RESOLVER_PATH = ROOT / "research" / "contract_c_successor_ground_up_20260913" / "PHASE_1_5_POLICY_RESOLVER.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


RC1 = load_module("candidate_a_rc1_for_rc2_qualification", RC1_DIR / "candidate_a_rc1.py")
P2 = load_module("phase2_oracle_for_rc2_qualification", P2_PATH)
ORACLE: dict[str, dict[str, Any]] = P2.O
RESOLVER = json.loads(RESOLVER_PATH.read_text())
REL_ENCODE = {"support": "supports", "refute": "refutes", "non_polarized": "non_polarized"}
REL_DECODE = {v: k for k, v in REL_ENCODE.items()}


def encode(o: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {
        "profile": C.PROFILE,
        "contract_b": copy.deepcopy(o["contract_b"]),
        "producer": {
            "semantic_implementation_sha": o["producer"]["semantic_implementation_sha"],
            "policy_sha256": o["producer"]["policy_sha256"],
            "policy_resolver_commit_sha": C.POLICY_RESOLVER_FIXTURE_COMMIT,
        },
        "execution": {"state": o["result_execution"]},
        "propositions": [],
    }
    for p in o["propositions"]:
        by = {row["symbol"]: row for row in p["participants"]}
        out["propositions"].append(
            {
                "proposition": {
                    "proposition_id": p["proposition_id"],
                    "content_sha256": "sha256:" + p["proposition_sha256"],
                },
                "execution": {
                    "state": p["execution"],
                    "completion": p["completion"],
                },
                "terminal": copy.deepcopy(p["terminal"]),
                "participants": [
                    {
                        "evidence_ref": {
                            "source_id": row["source_id"],
                            "passage_id": row["passage_id"],
                        },
                        "relation": REL_ENCODE[row["polarity"]],
                        "role": row["role"],
                    }
                    for row in p["participants"]
                ],
                "basis_groups": [
                    [
                        {
                            "source_id": by[symbol]["source_id"],
                            "passage_id": by[symbol]["passage_id"],
                        }
                        for symbol in group
                    ]
                    for group in p["msc"]
                ],
            }
        )
    return C.seal(out)


def project_to_phase2(value: dict[str, Any]) -> dict[str, Any]:
    C.validate_object(value)
    props: list[dict[str, Any]] = []
    for p in value["propositions"]:
        participants: list[dict[str, Any]] = []
        symbol_by_key: dict[tuple[str, str], str] = {}
        for row in p["participants"]:
            key = (
                row["evidence_ref"]["source_id"],
                row["evidence_ref"]["passage_id"],
            )
            symbol = row["evidence_ref"]["passage_id"]
            symbol_by_key[key] = symbol
            participants.append(
                {
                    "symbol": symbol,
                    "source_id": key[0],
                    "passage_id": key[1],
                    "polarity": REL_DECODE[row["relation"]],
                    "role": row["role"],
                }
            )
        msc = [
            [
                symbol_by_key[(ref["source_id"], ref["passage_id"])]
                for ref in group
            ]
            for group in p["basis_groups"]
        ]
        raw_hash = p["proposition"]["content_sha256"]
        props.append(
            {
                "proposition_id": p["proposition"]["proposition_id"],
                "proposition_sha256": raw_hash[7:],
                "execution": p["execution"]["state"],
                "completion": p["execution"]["completion"],
                "terminal": copy.deepcopy(p["terminal"]),
                "participants": participants,
                "msc": msc,
            }
        )
    return P2.norm(
        {
            "contract_b": copy.deepcopy(value["contract_b"]),
            "producer": {
                "semantic_implementation_sha": value["producer"]["semantic_implementation_sha"],
                "policy_sha256": value["producer"]["policy_sha256"],
            },
            "result_execution": value["execution"]["state"],
            "propositions": props,
        }
    )


def evidence_index(o: dict[str, Any]) -> set[tuple[str, str]]:
    return {
        (row["source_id"], row["passage_id"])
        for p in o["propositions"]
        for row in p["participants"]
    }


def verify_positive(value: dict[str, Any], o: dict[str, Any]) -> None:
    C.verify_candidate(
        value,
        exact_contract_b=o["contract_b"],
        evidence_index=evidence_index(o),
        independently_selected_resolver_commit_sha=C.POLICY_RESOLVER_FIXTURE_COMMIT,
        resolver_entries=RESOLVER["entries"],
        expected_whole_object_sha256=C.whole_object_sha256(value),
    )
    if project_to_phase2(value) != P2.norm(o):
        raise AssertionError("RC2 reconstruction differs from exact frozen Phase 2 oracle")


def reseal(value: dict[str, Any]) -> dict[str, Any]:
    x = copy.deepcopy(value)
    x.pop("result_set_id", None)
    return C.seal(x)


def expect_reject(value: dict[str, Any]) -> bool:
    try:
        C.validate_object(value)
    except Exception:
        return True
    return False


def unsupported_fixture() -> dict[str, Any]:
    return C.seal(
        {
            "profile": C.PROFILE,
            "contract_b": {
                "contract_version": "1.2.0",
                "bundle_id": "W-unsupported",
                "bundle_hash": "sha256:" + "1" * 64,
            },
            "producer": {
                "semantic_implementation_sha": C.CAL_RC1_IMPLEMENTATION,
                "policy_sha256": C.CAL_RC1_POLICY_SHA256,
                "policy_resolver_commit_sha": C.POLICY_RESOLVER_FIXTURE_COMMIT,
            },
            "execution": {"state": "completed"},
            "propositions": [
                {
                    "proposition": {
                        "proposition_id": "Q-unsupported",
                        "content_sha256": "sha256:" + "2" * 64,
                    },
                    "execution": {
                        "state": "completed",
                        "completion": "not_checkable",
                    },
                    "terminal": {
                        "verdict": "not_checkable",
                        "reason": C.UNSUPPORTED_REASON,
                    },
                    "participants": [
                        {
                            "evidence_ref": {
                                "source_id": "src-u1",
                                "passage_id": "U1",
                            },
                            "relation": "non_polarized",
                            "role": "residual",
                        }
                    ],
                    "basis_groups": [],
                }
            ],
        }
    )


def no_deciding_twin(unsupported: dict[str, Any]) -> dict[str, Any]:
    twin = copy.deepcopy(unsupported)
    twin.pop("result_set_id", None)
    twin["propositions"][0]["terminal"]["reason"] = "no_deciding_relation"
    return C.seal(twin)


def rc1_form(value: dict[str, Any]) -> dict[str, Any]:
    x = copy.deepcopy(value)
    x.pop("result_set_id", None)
    x["profile"] = RC1.PROFILE
    return RC1.seal(x)


def schema_delta_ok() -> bool:
    rc1 = json.loads((RC1_DIR / "candidate_a_rc1.schema.json").read_text())
    rc2 = json.loads((HERE / "candidate_a_rc2.schema.json").read_text())

    def semantic_projection(schema: dict[str, Any]) -> dict[str, Any]:
        x = copy.deepcopy(schema)
        for key in ("$id", "title", "$comment"):
            x.pop(key, None)
        return x

    a = semantic_projection(rc1)
    b = semantic_projection(rc2)
    a_profile = a["properties"]["profile"].pop("const")
    b_profile = b["properties"]["profile"].pop("const")
    a_reasons = set(
        a["$defs"]["propositionResult"]["properties"]["terminal"]["oneOf"][1]["properties"]["reason"]["enum"]
    )
    b_reasons = set(
        b["$defs"]["propositionResult"]["properties"]["terminal"]["oneOf"][1]["properties"]["reason"]["enum"]
    )
    a["$defs"]["propositionResult"]["properties"]["terminal"]["oneOf"][1]["properties"]["reason"]["enum"] = []
    b["$defs"]["propositionResult"]["properties"]["terminal"]["oneOf"][1]["properties"]["reason"]["enum"] = []
    return (
        a == b
        and a_profile == RC1.PROFILE
        and b_profile == C.PROFILE
        and b_reasons == a_reasons | {C.UNSUPPORTED_REASON}
    )


def evaluate() -> dict[str, Any]:
    checks: dict[str, bool] = {}
    observations: dict[str, Any] = {}

    checks["exact_schema_delta"] = schema_delta_ok()

    inherited_failures: list[str] = []
    for name, oracle in ORACLE.items():
        encoded = encode(oracle)
        try:
            verify_positive(encoded, oracle)
        except Exception as exc:
            inherited_failures.append(f"{name}: {exc}")
    checks["inherited_phase2_semantics_19_of_19"] = inherited_failures == [] and len(ORACLE) == 19
    observations["inherited_failures"] = inherited_failures

    unsupported = unsupported_fixture()
    C.validate_object(unsupported)
    C.verify_candidate(
        unsupported,
        exact_contract_b=unsupported["contract_b"],
        evidence_index={("src-u1", "U1")},
        independently_selected_resolver_commit_sha=C.POLICY_RESOLVER_FIXTURE_COMMIT,
        resolver_entries=RESOLVER["entries"],
        expected_whole_object_sha256=C.whole_object_sha256(unsupported),
    )
    checks["unsupported_exact_positive"] = True

    rc1_rejected = False
    try:
        RC1.validate_object(rc1_form(unsupported))
    except Exception:
        rc1_rejected = True
    checks["rc1_discriminator_valid"] = rc1_rejected

    twin = no_deciding_twin(unsupported)
    C.validate_object(twin)
    checks["unsupported_distinct_from_no_deciding"] = (
        unsupported["result_set_id"] != twin["result_set_id"]
        and C.canonical_bytes(unsupported) != C.canonical_bytes(twin)
        and C.whole_object_sha256(unsupported) != C.whole_object_sha256(twin)
    )
    observations["terminal_identity_distinction"] = {
        "unsupported_result_set_id": unsupported["result_set_id"],
        "no_deciding_result_set_id": twin["result_set_id"],
        "unsupported_whole_object": C.whole_object_sha256(unsupported),
        "no_deciding_whole_object": C.whole_object_sha256(twin),
    }

    attacks: dict[str, bool] = {}

    def attacked(mutator) -> bool:
        x = copy.deepcopy(unsupported)
        x.pop("result_set_id", None)
        mutator(x)
        try:
            y = C.seal(x)
            C.validate_object(y)
        except Exception:
            return True
        return False

    attacks["assessed_completion"] = attacked(
        lambda x: x["propositions"][0]["execution"].__setitem__("completion", "assessed")
    )
    attacks["supported_verdict"] = attacked(
        lambda x: x["propositions"][0]["terminal"].__setitem__("verdict", "supported")
    )
    attacks["causal_nonpolarized"] = attacked(
        lambda x: x["propositions"][0]["participants"][0].__setitem__("role", "causal")
    )
    attacks["support_laundering"] = attacked(
        lambda x: x["propositions"][0]["participants"][0].__setitem__("relation", "supports")
    )
    attacks["basis_injection"] = attacked(
        lambda x: x["propositions"][0]["basis_groups"].append(
            [{"source_id": "src-u1", "passage_id": "U1"}]
        )
    )
    attacks["lowercase_reason"] = attacked(
        lambda x: x["propositions"][0]["terminal"].__setitem__(
            "reason", "unsupported_semantic_family"
        )
    )
    attacks["unknown_field"] = attacked(
        lambda x: x["propositions"][0].__setitem__("explanation", "forbidden")
    )
    attacks["wrong_profile"] = attacked(
        lambda x: x.__setitem__("profile", "contract-c-successor-candidate-a-rc3-attacker")
    )
    checks["focused_semantic_attacks_8_of_8"] = len(attacks) == 8 and all(attacks.values())
    observations["focused_attacks"] = attacks

    stale = copy.deepcopy(unsupported)
    stale["contract_b"]["bundle_id"] = "W-mutated-with-stale-id"
    checks["stale_local_identity_rejected"] = expect_reject(stale)

    wrong_b_rejected = False
    try:
        C.verify_contract_b_references(
            unsupported,
            exact_contract_b={**unsupported["contract_b"], "bundle_id": "other-world"},
            evidence_index={("src-u1", "U1")},
        )
    except Exception:
        wrong_b_rejected = True
    checks["wrong_exact_b_rejected"] = wrong_b_rejected

    wrong_resolver_rejected = False
    try:
        C.verify_policy_resolution(
            unsupported,
            independently_selected_resolver_commit_sha="0" * 40,
            resolver_entries=RESOLVER["entries"],
        )
    except Exception:
        wrong_resolver_rejected = True
    checks["wrong_resolver_rejected"] = wrong_resolver_rejected

    old_digest = C.whole_object_sha256(unsupported)
    mutated_reason = no_deciding_twin(unsupported)
    external_rejected = False
    try:
        C.verify_external_authority(
            mutated_reason,
            expected_whole_object_sha256=old_digest,
        )
    except Exception:
        external_rejected = True
    checks["old_external_authority_rejects_reason_reseal"] = external_rejected

    permuted = copy.deepcopy(encode(ORACLE["SP-10-alt-joint-mixed"]))
    permuted.pop("result_set_id", None)
    p = permuted["propositions"][0]
    p["participants"].reverse()
    p["basis_groups"].reverse()
    for group in p["basis_groups"]:
        group.reverse()
    permuted = C.seal(permuted)
    baseline = encode(ORACLE["SP-10-alt-joint-mixed"])
    checks["canonical_permutation_invariant"] = C.canonical_bytes(permuted) == C.canonical_bytes(baseline)

    weak_alias = no_deciding_twin(unsupported)
    checks["weak_reason_alias_control_killed"] = (
        weak_alias["propositions"][0]["terminal"] != unsupported["propositions"][0]["terminal"]
        and weak_alias["result_set_id"] != unsupported["result_set_id"]
    )

    required = [
        "exact_schema_delta",
        "inherited_phase2_semantics_19_of_19",
        "unsupported_exact_positive",
        "rc1_discriminator_valid",
        "unsupported_distinct_from_no_deciding",
        "focused_semantic_attacks_8_of_8",
        "stale_local_identity_rejected",
        "wrong_exact_b_rejected",
        "wrong_resolver_rejected",
        "old_external_authority_rejects_reason_reseal",
        "canonical_permutation_invariant",
        "weak_reason_alias_control_killed",
    ]
    failures = [name for name in required if not checks.get(name, False)]
    disposition = (
        "QUALIFIED_FOR_CAL_PRODUCER_CONFORMANCE_RESEARCH"
        if not failures
        else "FALSIFIED_REQUIRES_SUCCESSOR_CANDIDATE"
    )
    return {
        "schema": "contract-c-successor-candidate-a-rc2-qualification-v1",
        "research_disposition": disposition,
        "candidate_profile": C.PROFILE,
        "parent_rc1_freeze": C.PROFILE_ANCHOR,
        "checks": checks,
        "failures": failures,
        "observations": observations,
        "interpretation": {
            "causal_architecture_reopened": False,
            "semantic_delta": ["research_profile_identity", C.UNSUPPORTED_REASON],
            "production_promotion_authorized": False,
            "official_contract_c_version_assigned": False,
        },
    }


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: qualify.py <output-json>")
    result = evaluate()
    output = Path(sys.argv[1])
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
