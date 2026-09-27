#!/usr/bin/env python3
"""Execute the admitted current-subject A->D path twice and one source-substitution control.

This script starts from an already produced Gate Contract A and an independently reviewed
trusted-target manifest. It does not run ERS, infer target semantics, run Contract E, or write MainFrame.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any


def tagged_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def run_checked(args: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    cp = subprocess.run(args, cwd=cwd, env=env, input=input_text, text=True, capture_output=True, check=False)
    if cp.returncode:
        detail = (cp.stderr or cp.stdout).strip()
        raise RuntimeError(f"command failed ({cp.returncode}): {' '.join(args)}\n{detail}")
    return cp


def resolve_path(raw: str, anchor: Path) -> Path:
    p = Path(raw)
    if not p.is_absolute():
        p = anchor / p
    return p.resolve(strict=True)


def tree_digest(root: Path) -> str:
    h = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = path.relative_to(root).as_posix().encode("utf-8")
        data = path.read_bytes()
        h.update(len(rel).to_bytes(8, "big"))
        h.update(rel)
        h.update(len(data).to_bytes(8, "big"))
        h.update(data)
    return "sha256:" + h.hexdigest()


def validate_with_contract_a_authority(python: str, authority_root: Path, contract_a: Path) -> None:
    program = (
        "import json,sys; "
        "from validators.contract_a import validate_candidate; "
        "validate_candidate(json.load(open(sys.argv[1], encoding='utf-8')))"
    )
    env = os.environ.copy()
    env["PYTHONPATH"] = str(authority_root)
    run_checked([python, "-c", program, str(contract_a)], cwd=authority_root, env=env)


def reviewed_targets(review_path: Path, contract_a: dict[str, Any], contract_a_path: Path) -> dict[str, Path]:
    review = json.loads(review_path.read_text(encoding="utf-8"))
    if review.get("schema") != "cal-pipeline-trusted-target-review-v1":
        raise RuntimeError("target review schema mismatch")
    if review.get("contract_a_handoff_sha256") != contract_a.get("handoff_sha256"):
        raise RuntimeError("target review Contract A handoff mismatch")
    if review.get("contract_a_file_sha256") != tagged_bytes(contract_a_path.read_bytes()):
        raise RuntimeError("target review Contract A file hash mismatch")
    children = contract_a.get("decomposition", {}).get("children", [])
    expected = {row["proposition_id"]: row for row in children}
    rows = review.get("targets")
    if not isinstance(rows, list) or {row.get("proposition_id") for row in rows} != set(expected):
        raise RuntimeError("reviewed target ids must equal exact Contract A child ids")
    result: dict[str, Path] = {}
    for row in rows:
        pid = row["proposition_id"]
        if row.get("independent_review") is not True or row.get("semantic_fidelity_attested") is not True:
            raise RuntimeError(f"target {pid} has not passed independent semantic-fidelity review")
        author = row.get("target_author_context")
        reviewer = row.get("reviewer_context")
        if not author or not reviewer or author == reviewer:
            raise RuntimeError(f"target {pid} does not document distinct author/reviewer contexts")
        target_path = resolve_path(str(row.get("target_path") or ""), review_path.parent)
        raw = target_path.read_bytes()
        if tagged_bytes(raw) != row.get("target_sha256"):
            raise RuntimeError(f"target {pid} byte hash mismatch")
        target = json.loads(raw)
        prop = target.get("proposition", {})
        expected_cal_hash = str(expected[pid]["text_sha256"]).removeprefix("sha256:")
        if target.get("claim_id") != pid or prop.get("proposition_id") != pid:
            raise RuntimeError(f"target {pid} identity mismatch")
        if prop.get("text_sha256") != expected_cal_hash:
            raise RuntimeError(f"target {pid} does not bind exact child text hash")
        if prop.get("semantic_family") not in {"strict_comparison", "direct_event_order"}:
            raise RuntimeError(f"target {pid} family is outside qualified CAL #183 active families")
        result[pid] = target_path
    return result


def public_consumer_inputs(*, contract_a: dict[str, Any], package: dict[str, Any], contract_c: dict[str, Any], contract_c_sha256: str, child_result_bytes: dict[str, bytes]) -> dict[str, Any]:
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
    decomp = contract_a["decomposition"]
    root = contract_a["root_proposition"]
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
        "cal_semantic_source_commit": recomposition["cal_semantic_source_commit"],
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


def consume_contract_d(*, python: str, contract_d_root: Path, decision_path: Path, decision: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "decision_path": str(decision_path),
        "input_authority": decision["input_authority"],
        "policy": decision["policy"],
        "target": decision["target"],
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
            "print(json.dumps(consume(decision, expected), sort_keys=True, separators=(',',':')))",
        ]
    )
    env = os.environ.copy()
    env["PYTHONPATH"] = str(contract_d_root)
    cp = run_checked([python, "-c", program], cwd=contract_d_root, env=env, input_text=json.dumps(payload))
    return json.loads(cp.stdout)


def execute_once(args: argparse.Namespace, label: str, target_paths: dict[str, Path]) -> dict[str, Any]:
    root = args.out_root / label
    root.mkdir(parents=True, exist_ok=False)
    contract_a = json.loads(args.contract_a.read_text(encoding="utf-8"))

    eb_out = root / "eb"
    eb_cmd = [
        args.python,
        str(args.eb_root / "scripts/run_v1_integration_candidate.py"),
        str(args.contract_a),
        "--compatibility-carrier",
        str(args.eb_root / "config/eb_v1_slice/contract_b_compatibility_carrier.json"),
        "--out-dir",
        str(eb_out),
    ]
    if args.eb_admission is not None:
        eb_cmd.extend(["--admission", str(args.eb_admission)])
    run_checked(eb_cmd, cwd=args.eb_root)

    cal_out = root / "cal"
    cal_cmd = [
        str(args.cal_cli),
        "run",
        str(args.contract_a),
        str(eb_out / "contract_b"),
    ]
    for pid in [row["proposition_id"] for row in contract_a["decomposition"]["children"]]:
        cal_cmd.extend(["--target", f"{pid}={target_paths[pid]}"])
    cal_cmd.extend([
        "--out-dir", str(cal_out),
        "--contract-c-root", str(args.contract_c_root),
        "--rc2-root", str(args.rc2_root),
        "--resolver-root", str(args.resolver_root),
    ])
    run_checked(cal_cmd)

    package = json.loads((eb_out / "native_eb_v1_package.json").read_text(encoding="utf-8"))
    projection = json.loads((eb_out / "projection_receipt.json").read_text(encoding="utf-8"))
    parent_bytes = (cal_out / "parent-result.json").read_bytes()
    parent = json.loads(parent_bytes)
    if parent["authorization"]["automatic_action_allowed"] is not False:
        raise RuntimeError("CAL unexpectedly authorizes automatic action")
    c_bytes = (cal_out / "contract-c.json").read_bytes()
    c_obj = json.loads(c_bytes)
    c_sha = tagged_bytes(c_bytes)
    cal_manifest = json.loads((cal_out / "manifest.json").read_text(encoding="utf-8"))
    if cal_manifest.get("contract_c_sha256") != c_sha:
        raise RuntimeError("CAL manifest Contract C hash mismatch")

    child_ids = [row["proposition_id"] for row in contract_a["decomposition"]["children"]]
    child_bytes = {
        pid: (cal_out / "children" / pid / "result.json").read_bytes()
        for pid in child_ids
    }
    consumer_inputs = public_consumer_inputs(
        contract_a=contract_a,
        package=package,
        contract_c=c_obj,
        contract_c_sha256=c_sha,
        child_result_bytes=child_bytes,
    )
    consumer_path = root / "consumer-inputs.json"
    consumer_path.write_bytes(canonical_bytes(consumer_inputs))

    decision_target = {
        "kind": "claim",
        "id": contract_a["root_proposition"]["proposition_id"],
        "content_sha256": contract_a["root_proposition"]["text_sha256"],
    }
    target_path = root / "decision-target.json"
    target_path.write_bytes(canonical_bytes(decision_target))

    d_path = root / "contract-d.json"
    de_cmd = [
        args.node,
        str(args.decision_root / "scripts/decision-engine-parent-bound-evaluate.mjs"),
        "--contract-c", str(cal_out / "contract-c.json"),
        "--contract-c-sha256", c_sha,
        "--consumer-authority", str(args.consumer_root),
        "--consumer-inputs", str(consumer_path),
        "--contract-d-authority", str(args.contract_d_root),
        "--target", str(target_path),
        "--python", args.python,
    ]
    cp = run_checked(de_cmd, cwd=args.decision_root)
    d_path.write_text(cp.stdout, encoding="utf-8")
    d_bytes = d_path.read_bytes()
    decision = json.loads(d_bytes)
    if decision.get("evaluation", {}).get("state") != "completed":
        raise RuntimeError("Decision did not complete")
    consumed = consume_contract_d(
        python=args.python,
        contract_d_root=args.contract_d_root,
        decision_path=d_path,
        decision=decision,
    )

    return {
        "contract_a_sha256": tagged_bytes(args.contract_a.read_bytes()),
        "eb_native_package_sha256": tagged_bytes((eb_out / "native_eb_v1_package.json").read_bytes()),
        "eb_contract_b_tree_sha256": tree_digest(eb_out / "contract_b"),
        "eb_projection_receipt_sha256": tagged_bytes((eb_out / "projection_receipt.json").read_bytes()),
        "eb_accepted_relationships": projection["counts"]["accepted_relationships"],
        "cal_parent_conclusion": parent["parent_conclusion"],
        "cal_parent_result_sha256": tagged_bytes(parent_bytes),
        "contract_c_sha256": c_sha,
        "decision_disposition": decision["evaluation"]["disposition"],
        "contract_d_sha256": tagged_bytes(d_bytes),
        "contract_d_consumer_outcome": consumed["outcome"],
        "authorization_performed": False,
        "execution_performed": False,
    }


def substitution_control(args: argparse.Namespace) -> dict[str, Any]:
    control_root = args.out_root / "SUBSTITUTION-CONTROL"
    control_root.mkdir(parents=True, exist_ok=False)
    value = json.loads(args.contract_a.read_text(encoding="utf-8"))
    if not value.get("sources"):
        raise RuntimeError("Contract A has no source for substitution control")
    value["sources"][0]["content"] += "\nSUBSTITUTION_CONTROL"
    mutated = control_root / "contract-a-mutated.json"
    mutated.write_bytes(canonical_bytes(value))
    eb_out = control_root / "eb"
    cmd = [
        args.python,
        str(args.eb_root / "scripts/run_v1_integration_candidate.py"),
        str(mutated),
        "--compatibility-carrier",
        str(args.eb_root / "config/eb_v1_slice/contract_b_compatibility_carrier.json"),
        "--out-dir",
        str(eb_out),
    ]
    cp = subprocess.run(cmd, cwd=args.eb_root, text=True, capture_output=True, check=False)
    false_accept = cp.returncode == 0
    emitted = []
    if eb_out.exists():
        emitted = sorted(p.relative_to(eb_out).as_posix() for p in eb_out.rglob("*") if p.is_file())
    if false_accept or emitted:
        raise RuntimeError(
            f"source substitution control failed closed check: returncode={cp.returncode}, emitted={emitted}"
        )
    return {
        "control": "contract_a_source_byte_substitution_without_reseal",
        "rejected_before_artifact_emission": True,
        "returncode": cp.returncode,
        "stderr_sha256": tagged_bytes(cp.stderr.encode("utf-8")),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--contract-a", required=True, type=Path)
    ap.add_argument("--target-review", required=True, type=Path)
    ap.add_argument("--out-root", required=True, type=Path)
    ap.add_argument("--contract-a-root", required=True, type=Path)
    ap.add_argument("--eb-root", required=True, type=Path)
    ap.add_argument("--cal-cli", required=True, type=Path)
    ap.add_argument("--contract-c-root", required=True, type=Path)
    ap.add_argument("--rc2-root", required=True, type=Path)
    ap.add_argument("--resolver-root", required=True, type=Path)
    ap.add_argument("--consumer-root", required=True, type=Path)
    ap.add_argument("--decision-root", required=True, type=Path)
    ap.add_argument("--contract-d-root", required=True, type=Path)
    ap.add_argument("--eb-admission", type=Path)
    ap.add_argument("--python", default="python3")
    ap.add_argument("--node", default="node")
    args = ap.parse_args()

    args.contract_a = args.contract_a.resolve(strict=True)
    args.target_review = args.target_review.resolve(strict=True)
    args.out_root = args.out_root.resolve()
    for name in (
        "contract_a_root", "eb_root", "contract_c_root", "rc2_root", "resolver_root",
        "consumer_root", "decision_root", "contract_d_root"
    ):
        setattr(args, name, getattr(args, name).resolve(strict=True))
    args.cal_cli = args.cal_cli.resolve(strict=True)
    if args.eb_admission is not None:
        args.eb_admission = args.eb_admission.resolve(strict=True)
    if args.out_root.exists():
        raise SystemExit(f"refusing existing output root: {args.out_root}")

    validate_with_contract_a_authority(args.python, args.contract_a_root, args.contract_a)
    contract_a = json.loads(args.contract_a.read_text(encoding="utf-8"))
    target_paths = reviewed_targets(args.target_review, contract_a, args.contract_a)

    args.out_root.mkdir(parents=True)
    first = execute_once(args, "RUN1", target_paths)
    second = execute_once(args, "RUN2", target_paths)
    keys = [
        "contract_a_sha256",
        "eb_native_package_sha256",
        "eb_contract_b_tree_sha256",
        "eb_projection_receipt_sha256",
        "cal_parent_result_sha256",
        "contract_c_sha256",
        "contract_d_sha256",
    ]
    replay = {
        "keys_compared": keys,
        "byte_identity_equivalent": all(first[k] == second[k] for k in keys),
        "differences": {k: [first[k], second[k]] for k in keys if first[k] != second[k]},
    }
    if not replay["byte_identity_equivalent"]:
        raise RuntimeError(f"deterministic replay mismatch: {replay['differences']}")
    control = substitution_control(args)

    receipt = {
        "schema": "cal-pipeline-first-real-input-local-execution-receipt-v1",
        "status": "local_execution_observed",
        "run1": first,
        "run2": second,
        "replay": replay,
        "substitution_control": control,
        "authorization_performed": False,
        "execution_performed": False,
        "contract_e_invoked": False,
        "ers_write_performed": False,
        "nonclaims": [
            "This is not production authorization or release evidence.",
            "The observed decision disposition is not a claim of universal factual truth.",
            "Trusted target semantics depend on the recorded independent review.",
        ],
    }
    (args.out_root / "RUN-RECEIPT.json").write_bytes(canonical_bytes(receipt))
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
