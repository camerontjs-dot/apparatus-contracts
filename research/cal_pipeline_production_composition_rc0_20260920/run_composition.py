from __future__ import annotations

import base64
import copy
import hashlib
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

A_ROOT = Path(os.environ["CONTRACT_A_ROOT"]).resolve()
EB_ROOT = Path(os.environ["EB_ROOT"]).resolve()
C_ROOT = Path(os.environ["CONTRACT_C_ROOT"]).resolve()
C2_ROOT = Path(os.environ["CONTRACT_C_RC2_ROOT"]).resolve()
RESOLVER_ROOT = Path(os.environ["CONTRACT_C_RESOLVER_ROOT"]).resolve()
CONSUMER_ROOT = Path(os.environ["CONSUMER_ROOT"]).resolve()
DE_ROOT = Path(os.environ["DECISION_ROOT"]).resolve()
D_ROOT = Path(os.environ["CONTRACT_D_ROOT"]).resolve()
CAL_CLI = Path(os.environ["CAL_PARENT_CLI"]).resolve()
PYTHON = os.environ.get("PYTHON", sys.executable)
NODE = os.environ.get("NODE", "node")
OUT_ROOT = Path(
    os.environ.get("COMPOSITION_ROOT", "/tmp/cal-pipeline-production-composition")
).resolve()
RESULT_PATH = Path(sys.argv[1]).resolve()

sys.path.insert(0, str(EB_ROOT / "src"))

from evidence_bundler.v1 import build_package  # noqa: E402
from evidence_bundler.v1.contract_a import (  # noqa: E402
    CONTRACT_A_RELEASE_COMMIT,
    CONTRACT_A_VALIDATOR_BLOB,
    CONTRACT_A_VERSION,
    compute_handoff_sha256,
    validate_contract_a,
)
from evidence_bundler.v1.contract_b import (  # noqa: E402
    CONTRACT_B_PRODUCTION_LOCK,
    CONTRACT_B_VERSION,
    INTEGRATION_CONFIG,
    INTEGRATION_CONFIG_SHA256,
    INTEGRATION_PROFILE_ID,
    load_compatibility_carrier,
    project_contract_b,
)

A_RELEASE = "529c92b49a34d5c610618551a8737f019f9fa332"
A_RC2_BLOB = "42e5f5b3bf38d677445e9d01ea130ba604e53409"
EB_COMMIT = "4e1f6fe00e7c350b28f52bfea14f1f8988847884"
B_LOCK = "c314e53bd91c0736aa4370a364673b069aceb43e"
CAL_COMMIT = "ddaf94551e38663920593cab89f9c60d43c1555f"
CAL_TREE = "1677a1de987a594f4ee8d2670d56943c5f189fbd"
CAL_SEMANTIC_IMPLEMENTATION = "847cc970642bb648dc994b929c2053b5c9d4648c"
C_FREEZE = "c5b1d757f3a0ad4f6e2c3f6dbdc2dd2d3c1403ec"
C_PROFILE = "contract-c-cal-v1-parent-recomposition-rc0"
C_RC2_COMMIT = "b42c827acb0a9fe65353354d709add0e27bab307"
RESOLVER_COMMIT = "1d33e0612befcf8016816197c90c062373796df9"
CONSUMER_COMMIT = "12e7e640b229619501960b1b89cf4716d8d985b3"
DE_COMMIT = "6cdb59c2ba41779ac954af56dd077574ba090013"
DE_TREE = "d4b75b63462451b5c258a13abf9ce2beb9e78098"
D_RELEASE = "298a1a0f7b7b6d7712e11200d04faec3e1ca169b"

C1_TEXT = "Alpha had a higher rate than Beta."
C1_REFUTE_TEXT = "Alpha had a lower rate than Beta."
C2_TEXT = "Alice reviewed dossier before Bob archived dossier."
ROOT_TEXT = (
    "Alpha had a higher rate than Beta, and "
    "Alice reviewed dossier before Bob archived dossier."
)
SOURCES = (
    ("S-C1-SUPPORT", C1_TEXT),
    ("S-C1-REFUTE", C1_REFUTE_TEXT),
    ("S-C2-SUPPORT", C2_TEXT),
    ("S-D01", "Alpha calibration records describe sampling frequency."),
    ("S-D02", "Beta calibration records describe sampling frequency."),
    ("S-D03", "Alice prepared the dossier for review."),
    ("S-D04", "Bob stored archival metadata for the dossier."),
    ("S-D05", "Gamma had a higher output than Delta."),
    ("S-D06", "Quality staff inspected batch documentation."),
    ("S-D07", "The archive contains unrelated maintenance notes."),
)


@dataclass(frozen=True)
class Case:
    case_id: str
    c1_source: str
    admit_c2: bool
    expected_parent: str
    expected_decision: str
    expected_consumer: str


CASES = (
    Case(
        "PIPE01",
        "S-C1-SUPPORT",
        True,
        "supported",
        "clear",
        "candidate_for_authorization",
    ),
    Case("PIPE02", "S-C1-REFUTE", True, "contradicted", "hold", "hold"),
    Case("PIPE03", "S-C1-SUPPORT", False, "not_checkable", "hold", "hold"),
)


def tagged_text(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def tagged_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        )
        + "\n"
    ).encode("utf-8")


def run_checked(
    args: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        args,
        cwd=cwd,
        env=env,
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise RuntimeError(
            f"command failed ({result.returncode}): {' '.join(args)}\n{detail}"
        )
    return result


def contract_a() -> dict[str, Any]:
    value: dict[str, Any] = {
        "schema": "contract-a-wire-candidate-rc2",
        "handoff_id": "cal-pipeline-production-composition-rc0",
        "producer": {
            "producer_id": "cal-pipeline-composition-apparatus",
            "producer_version": "rc0",
        },
        "work": {"work_id": "cal-pipeline-production-composition-rc0"},
        "root_proposition": {
            "proposition_id": "ROOT",
            "text": ROOT_TEXT,
            "text_sha256": tagged_text(ROOT_TEXT),
        },
        "decomposition": {
            "state": "declared",
            "decomposition_id": "D-PIPE-PROD-RC0",
            "operator": "all_of",
            "children": [
                {
                    "proposition_id": "C1",
                    "text": C1_TEXT,
                    "text_sha256": tagged_text(C1_TEXT),
                    "sequence": 1,
                },
                {
                    "proposition_id": "C2",
                    "text": C2_TEXT,
                    "text_sha256": tagged_text(C2_TEXT),
                    "sequence": 2,
                },
            ],
        },
        "sources": [
            {
                "source_id": source_id,
                "media_type": "text/plain; charset=utf-8",
                "content": text,
                "content_sha256": tagged_text(text),
            }
            for source_id, text in SOURCES
        ],
        "handoff_sha256": "sha256:" + "0" * 64,
    }
    value["handoff_sha256"] = compute_handoff_sha256(value)
    return value


def target(proposition_id: str) -> dict[str, Any]:
    if proposition_id == "C1":
        text = C1_TEXT
        family = "strict_comparison"
        fields = {
            "lhs_entity": "Alpha",
            "rhs_entity": "Beta",
            "comparison_direction": "MORE_THAN",
        }
    elif proposition_id == "C2":
        text = C2_TEXT
        family = "direct_event_order"
        fields = {
            "left_subject": "alice",
            "left_predicate": "review",
            "left_object": "dossier",
            "left_polarity": "positive",
            "temporal_relation": "BEFORE",
            "right_subject": "bob",
            "right_predicate": "archive",
            "right_object": "dossier",
            "right_polarity": "positive",
        }
    else:
        raise AssertionError(proposition_id)
    return {
        "claim_id": proposition_id,
        "proposition": {
            "proposition_id": proposition_id,
            "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "semantic_family": family,
            "fields": fields,
        },
    }


def retained_passage_id(
    package: dict[str, Any], proposition_id: str, source_id: str
) -> str:
    rows = [
        row
        for row in package["candidates"]
        if row["proposition_id"] == proposition_id
        and row["source_id"] == source_id
        and row["selection_state"] == "retained"
    ]
    if len(rows) != 1:
        observed = [
            (row["source_id"], row["nomination_rank"], row["selection_state"])
            for row in package["candidates"]
            if row["proposition_id"] == proposition_id
        ]
        raise RuntimeError(
            "preregistered decisive source was not uniquely retained: "
            f"{proposition_id}/{source_id}; observed={observed}"
        )
    return str(rows[0]["passage_id"])


def validate_with_released_a(path: Path) -> None:
    program = (
        "import json,sys; "
        "from validators.contract_a import validate_candidate; "
        "validate_candidate(json.load(open(sys.argv[1], encoding='utf-8')))"
    )
    env = os.environ.copy()
    env["PYTHONPATH"] = str(A_ROOT)
    run_checked([PYTHON, "-c", program, str(path)], cwd=A_ROOT, env=env)


def public_consumer_inputs(
    *,
    contract_a_value: dict[str, Any],
    package: dict[str, Any],
    contract_c: dict[str, Any],
    contract_c_sha256: str,
    child_result_bytes: dict[str, bytes],
) -> dict[str, Any]:
    inner = contract_c["rc2_result"]
    propositions = {
        str(row["proposition"]["proposition_id"]): {
            "content_sha256": str(row["proposition"]["content_sha256"])
        }
        for row in inner["propositions"]
    }
    seen: set[tuple[str, str]] = set()
    passages: list[dict[str, str]] = []
    for row in package["candidates"]:
        key = (str(row["source_id"]), str(row["passage_id"]))
        if key not in seen:
            seen.add(key)
            passages.append({"source_id": key[0], "passage_id": key[1]})

    decomp = contract_a_value["decomposition"]
    root = contract_a_value["root_proposition"]
    decomposition = {
        "state": decomp["state"],
        "decomposition_id": decomp["decomposition_id"],
        "operator": decomp["operator"],
        "root": {
            "proposition_id": root["proposition_id"],
            "text_sha256": root["text_sha256"],
        },
        "children": [
            {
                "sequence": row["sequence"],
                "proposition_id": row["proposition_id"],
                "text_sha256": row["text_sha256"],
            }
            for row in decomp["children"]
        ],
    }

    producer = inner["producer"]
    recomposition = contract_c["recomposition"]
    expected_authority = {
        "profile": inner["profile"],
        "cal_freeze_commit": recomposition["cal_freeze_commit"],
        "cal_semantic_source_commit": recomposition[
            "cal_semantic_source_commit"
        ],
        "semantic_implementation_sha": producer["semantic_implementation_sha"],
        "policy_sha256": producer["policy_sha256"],
        "policy_resolver_commit_sha": producer["policy_resolver_commit_sha"],
        "whole_object_sha256": contract_c_sha256,
    }
    return {
        "contract_b_index": {
            **inner["contract_b"],
            "propositions": propositions,
            "passages": passages,
        },
        "expected_authority": expected_authority,
        "contract_a_decomposition": decomposition,
        "native_child_results_b64": {
            key: base64.b64encode(value).decode("ascii")
            for key, value in child_result_bytes.items()
        },
    }


def consume_contract_d(
    *,
    decision_path: Path,
    expected_input_authority: dict[str, str],
    expected_policy: dict[str, str],
    expected_target: dict[str, str],
) -> dict[str, Any]:
    payload = {
        "decision_path": str(decision_path),
        "input_authority": expected_input_authority,
        "policy": expected_policy,
        "target": expected_target,
    }
    program = "\n".join(
        [
            "import json,sys",
            "from validators.contract_d_validate import require_canonical_bytes",
            "from validators.contract_d_consume import ApplicabilityExpectation, consume",
            "p=json.load(sys.stdin)",
            "raw=open(p['decision_path'],'rb').read()",
            "decision=require_canonical_bytes(raw)",
            "expected=ApplicabilityExpectation(",
            "  input_authority=p['input_authority'],",
            "  policy=p['policy'],",
            "  target=p['target'],",
            "  requested_operation='knowledge.add_verified_tag',",
            "  effect_params={'scope':'claim'},",
            ")",
            "print(json.dumps(consume(decision, expected), "
            "sort_keys=True, separators=(',',':')))",
        ]
    )
    env = os.environ.copy()
    env["PYTHONPATH"] = str(D_ROOT)
    result = run_checked(
        [PYTHON, "-c", program],
        cwd=D_ROOT,
        env=env,
        input_text=json.dumps(payload),
    )
    return json.loads(result.stdout)


def execute_case(case: Case, root: Path) -> dict[str, Any]:
    root.mkdir(parents=True, exist_ok=False)
    a = contract_a()
    a_path = root / "contract-a.json"
    a_path.write_bytes(canonical_json_bytes(a))

    validate_with_released_a(a_path)
    if validate_contract_a(copy.deepcopy(a)) != a:
        raise RuntimeError(
            "frozen EB Contract A consumer normalized or changed the released object"
        )
    if CONTRACT_A_VERSION != "2.0.0":
        raise RuntimeError(
            f"unexpected EB Contract A version: {CONTRACT_A_VERSION}"
        )
    if (
        CONTRACT_A_RELEASE_COMMIT != A_RELEASE
        or CONTRACT_A_VALIDATOR_BLOB != A_RC2_BLOB
    ):
        raise RuntimeError("EB Contract A authority pin drift")

    initial = build_package(contract_a=a, config=INTEGRATION_CONFIG)
    admission: dict[tuple[str, str], str] = {
        (
            "C1",
            retained_passage_id(initial, "C1", case.c1_source),
        ): "accepted"
    }
    if case.admit_c2:
        admission[
            ("C2", retained_passage_id(initial, "C2", "S-C2-SUPPORT"))
        ] = "accepted"

    package = build_package(
        contract_a=a,
        config=INTEGRATION_CONFIG,
        admission=admission,
    )
    if package["config_sha256"] != INTEGRATION_CONFIG_SHA256:
        raise RuntimeError("EB integration config drift")
    if INTEGRATION_PROFILE_ID != "eb-v1-integration-10x3-rc0":
        raise RuntimeError("EB integration profile drift")

    carrier = load_compatibility_carrier(
        EB_ROOT
        / "research/eb_v1_integration_candidate/contract_b_compatibility_carrier.json"
    )
    eb_dir = root / "eb"
    receipt = project_contract_b(
        package=package,
        compatibility_carrier=carrier,
        out_dir=eb_dir,
    )
    if receipt["contract_b_authority"] != {
        "version": "1.2.0",
        "production_lock": B_LOCK,
    }:
        raise RuntimeError("Contract B authority drift")
    if (
        CONTRACT_B_VERSION != "1.2.0"
        or CONTRACT_B_PRODUCTION_LOCK != B_LOCK
    ):
        raise RuntimeError("EB Contract B release pin drift")

    targets: dict[str, Path] = {}
    for proposition_id in ("C1", "C2"):
        path = root / f"{proposition_id}.target.json"
        path.write_bytes(canonical_json_bytes(target(proposition_id)))
        targets[proposition_id] = path

    cal_out = root / "cal"
    cal_args = [
        str(CAL_CLI),
        "run",
        str(a_path),
        str(eb_dir / "contract_b"),
        "--target",
        f"C1={targets['C1']}",
        "--target",
        f"C2={targets['C2']}",
        "--out-dir",
        str(cal_out),
        "--contract-c-root",
        str(C_ROOT),
        "--rc2-root",
        str(C2_ROOT),
        "--resolver-root",
        str(RESOLVER_ROOT),
    ]
    run_checked(cal_args)

    parent_bytes = (cal_out / "parent-result.json").read_bytes()
    parent = json.loads(parent_bytes)
    if parent["parent_conclusion"] != case.expected_parent:
        raise RuntimeError(
            f"{case.case_id}: expected parent {case.expected_parent}, "
            f"observed {parent['parent_conclusion']}"
        )
    if (
        parent["semantic_implementation_sha"]
        != CAL_SEMANTIC_IMPLEMENTATION
    ):
        raise RuntimeError("CAL semantic implementation drift")
    if parent["authorization"]["automatic_action_allowed"] is not False:
        raise RuntimeError("CAL unexpectedly authorized action")

    c_bytes = (cal_out / "contract-c.json").read_bytes()
    c_obj = json.loads(c_bytes)
    cal_manifest = json.loads(
        (cal_out / "manifest.json").read_text(encoding="utf-8")
    )
    c_sha = tagged_bytes(c_bytes)
    if cal_manifest["contract_c_sha256"] != c_sha:
        raise RuntimeError("CAL Contract C manifest whole-object mismatch")
    if c_obj["profile"] != C_PROFILE:
        raise RuntimeError("unexpected Contract C profile")

    child_bytes = {
        proposition_id: (
            cal_out / "children" / proposition_id / "result.json"
        ).read_bytes()
        for proposition_id in ("C1", "C2")
    }
    consumer_inputs = public_consumer_inputs(
        contract_a_value=a,
        package=package,
        contract_c=c_obj,
        contract_c_sha256=c_sha,
        child_result_bytes=child_bytes,
    )
    consumer_path = root / "consumer-inputs.json"
    consumer_path.write_bytes(canonical_json_bytes(consumer_inputs))

    target_root = {
        "kind": "claim",
        "id": a["root_proposition"]["proposition_id"],
        "content_sha256": a["root_proposition"]["text_sha256"],
    }
    target_path = root / "decision-target.json"
    target_path.write_bytes(canonical_json_bytes(target_root))

    d_path = root / "contract-d.json"
    de_args = [
        NODE,
        str(DE_ROOT / "scripts/decision-engine-parent-bound-evaluate.mjs"),
        "--contract-c",
        str(cal_out / "contract-c.json"),
        "--contract-c-sha256",
        c_sha,
        "--consumer-authority",
        str(CONSUMER_ROOT),
        "--consumer-inputs",
        str(consumer_path),
        "--contract-d-authority",
        str(D_ROOT),
        "--target",
        str(target_path),
        "--python",
        PYTHON,
    ]
    decision = run_checked(de_args)
    d_path.write_text(decision.stdout, encoding="utf-8")
    d_bytes = d_path.read_bytes()
    d_obj = json.loads(d_bytes)
    if d_obj["evaluation"]["state"] != "completed":
        raise RuntimeError(f"{case.case_id}: Decision did not complete")
    if d_obj["evaluation"]["disposition"] != case.expected_decision:
        raise RuntimeError(
            f"{case.case_id}: expected Decision {case.expected_decision}, "
            f"observed {d_obj['evaluation']['disposition']}"
        )

    consumed = consume_contract_d(
        decision_path=d_path,
        expected_input_authority=d_obj["input_authority"],
        expected_policy=d_obj["policy"],
        expected_target=d_obj["target"],
    )
    if consumed["outcome"] != case.expected_consumer:
        raise RuntimeError(
            f"{case.case_id}: expected Contract D consumer "
            f"{case.expected_consumer}, observed {consumed}"
        )

    record = {
        "case_id": case.case_id,
        "contract_a_handoff_sha256": a["handoff_sha256"],
        "eb_native_package_sha256": package["package_sha256"],
        "contract_b_bundle_id": receipt["bundle_id"],
        "contract_b_bundle_hash": receipt["bundle_hash"],
        "cal_parent_conclusion": parent["parent_conclusion"],
        "cal_parent_result_sha256": tagged_bytes(parent_bytes),
        "contract_c_sha256": c_sha,
        "decision_disposition": d_obj["evaluation"]["disposition"],
        "contract_d_sha256": tagged_bytes(d_bytes),
        "contract_d_consumer": consumed["outcome"],
        "authorization_performed": False,
        "execution_performed": False,
    }
    (root / "case-result.json").write_bytes(canonical_json_bytes(record))
    return {
        "record": record,
        "package": package,
        "receipt": receipt,
        "consumer_inputs": consumer_inputs,
        "consumer_path": consumer_path,
        "target_path": target_path,
        "cal_out": cal_out,
        "d_path": d_path,
        "parent_bytes": parent_bytes,
        "c_bytes": c_bytes,
        "d_bytes": d_bytes,
    }


def main() -> None:
    if OUT_ROOT.exists():
        raise RuntimeError(
            f"composition output already exists: {OUT_ROOT}"
        )
    OUT_ROOT.mkdir(parents=True)

    observed: dict[str, Any] = {}
    executions: dict[str, dict[str, Any]] = {}
    for case in CASES:
        execution = execute_case(case, OUT_ROOT / case.case_id)
        executions[case.case_id] = execution
        observed[case.case_id] = execution["record"]

    replay = execute_case(CASES[0], OUT_ROOT / "PIPE01-REPLAY")
    base = executions["PIPE01"]["record"]
    replay_record = replay["record"]
    deterministic_fields = (
        "contract_a_handoff_sha256",
        "eb_native_package_sha256",
        "contract_b_bundle_id",
        "contract_b_bundle_hash",
        "cal_parent_result_sha256",
        "contract_c_sha256",
        "contract_d_sha256",
    )
    deterministic = all(
        base[key] == replay_record[key] for key in deterministic_fields
    )
    deterministic = (
        deterministic
        and executions["PIPE01"]["parent_bytes"] == replay["parent_bytes"]
        and executions["PIPE01"]["c_bytes"] == replay["c_bytes"]
        and executions["PIPE01"]["d_bytes"] == replay["d_bytes"]
    )
    if not deterministic:
        raise RuntimeError("PIPE01 deterministic replay mismatch")

    attack_inputs = copy.deepcopy(executions["PIPE01"]["consumer_inputs"])
    source_inputs = executions["PIPE03"]["consumer_inputs"]
    common = next(
        (
            key
            for key in attack_inputs["native_child_results_b64"]
            if key in source_inputs["native_child_results_b64"]
        ),
        None,
    )
    if common is None:
        raise RuntimeError(
            "no common child identity for cross-run replay falsifier"
        )
    attack_inputs["native_child_results_b64"][common] = source_inputs[
        "native_child_results_b64"
    ][common]
    attack_path = OUT_ROOT / "replay-attack-consumer-inputs.json"
    attack_path.write_bytes(canonical_json_bytes(attack_inputs))

    pipe01 = executions["PIPE01"]
    attack_args = [
        NODE,
        str(DE_ROOT / "scripts/decision-engine-parent-bound-evaluate.mjs"),
        "--contract-c",
        str(pipe01["cal_out"] / "contract-c.json"),
        "--contract-c-sha256",
        pipe01["record"]["contract_c_sha256"],
        "--consumer-authority",
        str(CONSUMER_ROOT),
        "--consumer-inputs",
        str(attack_path),
        "--contract-d-authority",
        str(D_ROOT),
        "--target",
        str(pipe01["target_path"]),
        "--python",
        PYTHON,
    ]
    attack = subprocess.run(
        attack_args,
        text=True,
        capture_output=True,
        check=False,
    )
    replay_rejected = attack.returncode != 0 and not attack.stdout.strip()
    if not replay_rejected:
        raise RuntimeError(
            "cross-run replay false accept: "
            "Decision/Contract D output was emitted"
        )
    (OUT_ROOT / "replay-attack-stderr.txt").write_text(
        attack.stderr, encoding="utf-8"
    )

    result = {
        "schema": "cal-pipeline-production-composition-rc0-result-v1",
        "disposition": "SUPPORTED_THREE_CASE_PRODUCTION_SHAPED_COMPOSITION",
        "exact_subjects": {
            "contract_a_release": A_RELEASE,
            "evidence_bundler": EB_COMMIT,
            "contract_b_lock": B_LOCK,
            "cal_candidate": CAL_COMMIT,
            "cal_tree": CAL_TREE,
            "contract_c_freeze": C_FREEZE,
            "contract_c_rc2": C_RC2_COMMIT,
            "contract_c_resolver": RESOLVER_COMMIT,
            "contract_c_consumer": CONSUMER_COMMIT,
            "decision_candidate": DE_COMMIT,
            "decision_tree": DE_TREE,
            "contract_d_release": D_RELEASE,
        },
        "cases": observed,
        "deterministic_replay": {
            "case": "PIPE01",
            "passed": True,
            "fields": list(deterministic_fields),
            "byte_identical_parent_result": (
                executions["PIPE01"]["parent_bytes"]
                == replay["parent_bytes"]
            ),
            "byte_identical_contract_c": (
                executions["PIPE01"]["c_bytes"] == replay["c_bytes"]
            ),
            "byte_identical_contract_d": (
                executions["PIPE01"]["d_bytes"] == replay["d_bytes"]
            ),
        },
        "negative_controls": {
            "cross_run_native_child_replay": {
                "rejected_before_contract_d_output": True,
                "false_accepts": 0,
                "stderr_sha256": tagged_bytes(
                    attack.stderr.encode("utf-8")
                ),
            }
        },
        "cal_semantics_changed": False,
        "decision_policy_semantics_changed": False,
        "contract_d_changed": False,
        "authorization_performed": False,
        "execution_performed": False,
    }
    RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULT_PATH.write_bytes(canonical_json_bytes(result))
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
