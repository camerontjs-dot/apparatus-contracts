from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

APPARATUS_PR127_BASE = "bb8ff5c5d9fd3e221b0dea76e4748fe85be30796"
DECISION_SUCCESSOR = "816374379ba7eb23f5bfdadaf203b7e287c052db"
CAL_V3 = "ffc43d4e89f5b1f7748e9cde0fa1efc7db47b463"
CONTRACT_D = "298a1a0f7b7b6d7712e11200d04faec3e1ca169b"
CONTRACT_E = "b153dcc4434cbe8a98616a9e410c6125378144c7"
ERS_RC3 = "319e325cdf678673fae645a70e3e34afb7dddef0"
ERS_SUCCESSOR = "022fcb58e14864aa173f447fa0c18dd2362b41b0"

CLAIM_TEXT = (
    "Alpha had a higher rate than Beta, and Alice reviewed dossier before Bob "
    "archived dossier."
)
CLAIM_CONTENT_ID = "sha256:fe9a393b0c31f7e2f200cbefc08d9293e364f8a0810865a73003ec3502c387d0"
PIPE01_DECISION_ID = "decision:sha256:3427c5cb6692bf7358c13e47628ef7a91a0c53e78affc58f2ae60173daffcc15"
PIPE01_RUN_ID = "PIPE01"
RENDER_DATE = "2026-09-21"
EVALUATION_TIME = "2026-09-21T12:00:00Z"
AUTHORITY_STATE_ID = "sha256:" + "a" * 64


def check(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(label)


def sha256_identity(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def independent_canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
        + b"\n"
    )


def independent_object_identity(value: Any) -> str:
    return sha256_identity(independent_canonical_bytes(value))


def git_text(path: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(path), *args], text=True
    ).strip()


def git_head(path: Path) -> str:
    return git_text(path, "rev-parse", "HEAD")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot_load:{path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def fixture_snapshot() -> dict[str, Any]:
    return {
        "run_id": PIPE01_RUN_ID,
        "render_date": RENDER_DATE,
        "claim": {
            "id": "ROOT",
            "content_sha256": CLAIM_CONTENT_ID,
            "text": CLAIM_TEXT,
            "project_tag": "cal",
            "confidence": 0.91,
            "credibility": 0.88,
            "updated_at": "2026-09-20T09:30:00Z",
        },
        # Deliberately scrambled: the frozen ERS successor must own order.
        "evidence": [
            {
                "id": "e2",
                "source_path": "/disposable/S-C1-SUPPORT.md",
                "source_name": "S-C1-SUPPORT.md",
                "source_uri": "file:///disposable/S-C1-SUPPORT.md",
                "passage_anchor": "chars:0-34",
                "relation": "supports",
                "weight": 0.90,
                "extracted_by": "fixture-extractor",
            },
            {
                "id": "e1",
                "source_path": "/disposable/S-D01.md",
                "source_name": "S-D01.md",
                "source_uri": "file:///disposable/S-D01.md",
                "passage_anchor": None,
                "relation": "qualifies",
                "weight": 0.45,
                "extracted_by": "fixture-extractor",
            },
            {
                "id": "e3",
                "source_path": "/disposable/S-C1-SUPPORT.md",
                "source_name": "S-C1-SUPPORT.md",
                "source_uri": "file:///disposable/S-C1-SUPPORT.md",
                "passage_anchor": "chars:35-60",
                "relation": "supports",
                "weight": 0.80,
                "extracted_by": "fixture-extractor",
            },
        ],
        "contradictions": [
            {
                "id": "c2",
                "claim_a_id": "ROOT",
                "claim_b_id": "other-2",
                "detected_at": "2026-09-19T01:00:00Z",
                "detected_by": "fixture-detector",
                "resolution": "dismissed",
                "resolved_at": "2026-09-20T01:00:00Z",
                "resolution_reason": "background-only",
            },
            {
                "id": "c1",
                "claim_a_id": "ROOT",
                "claim_b_id": "other-1",
                "detected_at": "2026-09-18T01:00:00Z",
                "detected_by": "fixture-detector",
                "resolution": None,
                "resolved_at": None,
                "resolution_reason": None,
            },
        ],
        "revisions": [
            {
                "id": "r2",
                "changed_at": "2026-09-20T10:00:00Z",
                "field_changed": "confidence",
                "old_value": "0.80",
                "new_value": "0.91",
                "changed_by": "fixture-auditor",
                "reason": "new evidence",
            },
            {
                "id": "r1",
                "changed_at": "2026-09-19T10:00:00Z",
                "field_changed": "text",
                "old_value": "Alpha rate claim",
                "new_value": CLAIM_TEXT,
                "changed_by": "fixture-auditor",
                "reason": None,
            },
        ],
    }


def independent_render(packet: dict[str, Any]) -> bytes:
    """Qualification-harness renderer, separate from the ERS implementation."""

    render = packet["render"]
    claim = packet["claim"]
    evidence = packet["evidence"]
    unresolved = [row for row in packet["contradictions"] if row["resolution"] is None]
    unique_sources: list[str] = []
    source_by_key: dict[str, dict[str, Any]] = {}
    for row in evidence:
        if row["relation"] != "supports" or row["source_key"] in source_by_key:
            continue
        source_by_key[row["source_key"]] = row
        unique_sources.append(row["source_key"])
    source_links = [
        f"[{source_by_key[key]['source_name']}]({source_by_key[key]['source_uri']})"
        for key in unique_sources
    ]

    content = [
        "---",
        f"title: \"Claim review: {claim['text'][:60]}...\"",
        f"domain: {render['domain']}",
        'type: "note"',
        f"status: \"{render['status']}\"",
        f"source: {render['run_id']}",
        f"claim_id: {claim['id']}",
        f"confidence: {claim['confidence']}",
        f"credibility: {claim['credibility']}",
        f"evidence_count: {len(evidence)}",
        f"contradiction_count: {len(unresolved)}",
        f"audited_at: \"{claim['updated_at']}\"",
        f"tags: {json.dumps(render['tags'])}",
        "---",
        "",
        f"# Claim: {claim['text']}",
        "",
        f"**Status:** Pending operator review (auditor confidence: {claim['confidence']})  ",
        f"**Audited:** {render['render_date']}  ",
        "**Promotion:** Not stable — requires human verification per EPISTEMIC_STANCE.md  ",
    ]
    content.append(
        f"**Sources:** {', '.join(source_links)}" if source_links else "**Sources:** None cited"
    )
    content.extend(["", "## Evidence"])
    if evidence:
        for row in evidence:
            anchor = f" ({row['passage_anchor']})" if row["passage_anchor"] else ""
            content.append(
                f"- [{row['source_name']}]({row['source_uri']}){anchor} "
                f"[{row['relation']}] (weight {row['weight']}, extracted by {row['extracted_by']})"
            )
    else:
        content.append("- No supporting or qualifying evidence links recorded.")
    content.extend(["", "## Audit history"])
    if packet["revisions"]:
        for row in packet["revisions"]:
            reason = f" ({row['reason']})" if row["reason"] else ""
            content.append(
                f"- {row['changed_at'].split('T')[0]}: {row['field_changed'].capitalize()} updated from "
                f"'{row['old_value']}' to '{row['new_value']}' by {row['changed_by']}{reason}"
            )
    else:
        content.append(
            f"- {render['render_date']}: Claim indexed by research run {render['run_id']}."
        )
    content.append("")
    return "\n".join(content).encode("utf-8")


def run_decision_successor(
    *, decision_root: Path, fixtures: Path, consumer_root: Path, contract_d_root: Path
) -> dict[str, Any]:
    """Run the exact Decision successor without writing a script to disk."""

    decision_module = (decision_root / "src/parentBoundPolicyDispatch.js").as_uri()
    contract_d_module = (decision_root / "src/contractDCanonicalOutput.js").as_uri()
    node_program = f"""
import {{ readFileSync }} from "node:fs";
import {{ createHash }} from "node:crypto";
import {{ isDeepStrictEqual }} from "node:util";
import {{
  decideParentBoundPolicy,
  EPISTEMIC_AUDIT_STAGE_PENDING_REVIEW_POLICY,
}} from "{decision_module}";
import {{
  decideParentBoundContractCToContractD,
}} from "{(decision_root / 'src/parentBoundContractCDecision.js').as_uri()}";
import {{ SUPPORTED_CLAIM_VERIFICATION_POLICY }} from "{(decision_root / 'src/contractCDecision.js').as_uri()}";
import {{ canonicalizeContractDWithAuthority }} from "{contract_d_module}";

const fixtureRoot = process.env.ERS_RENDER_FIXTURES;
const consumerRoot = process.env.ERS_RENDER_CONSUMER;
const contractDRoot = process.env.ERS_RENDER_CONTRACT_D;
const cases = ["PIPE01", "PIPE02", "PIPE03"];
const digest = (raw) => "sha256:" + createHash("sha256").update(raw).digest("hex");
const load = (caseId) => {{
  const raw = readFileSync(`${{fixtureRoot}}/${{caseId}}/cal/contract-c.json`);
  return {{
    raw,
    sha: digest(raw),
    inputs: JSON.parse(readFileSync(`${{fixtureRoot}}/${{caseId}}/consumer-inputs.json`, "utf8")),
    target: JSON.parse(readFileSync(`${{fixtureRoot}}/${{caseId}}/decision-target.json`, "utf8")),
  }};
}};
const context = (policy, target) => ({{
  policy: {{ id: policy.id, version: policy.version }},
  target,
}});
const decide = (policy, loaded) => decideParentBoundPolicy({{
  contractCBytes: loaded.raw,
  expectedContractCSha256: loaded.sha,
  consumerRoot,
  consumerInputs: loaded.inputs,
  decisionContext: context(policy, loaded.target),
}});

const out = {{ cases: {{}} }};
for (const caseId of cases) {{
  const loaded = load(caseId);
  const frozen = decideParentBoundContractCToContractD({{
    contractCBytes: loaded.raw,
    expectedContractCSha256: loaded.sha,
    consumerRoot,
    consumerInputs: loaded.inputs,
    decisionContext: {{ target: loaded.target }},
  }});
  const supported = decide(SUPPORTED_CLAIM_VERIFICATION_POLICY, loaded);
  const ers = decide(EPISTEMIC_AUDIT_STAGE_PENDING_REVIEW_POLICY, loaded);
  const supportedCanonical = canonicalizeContractDWithAuthority({{
    decision: supported,
    contractDAuthorityRoot: contractDRoot,
  }});
  let released = null;
  try {{
    canonicalizeContractDWithAuthority({{ decision: ers, contractDAuthorityRoot: contractDRoot }});
    released = {{ accepted: true }};
  }} catch (error) {{
    released = {{ accepted: false, code: error?.code ?? null, message: String(error?.message ?? error) }};
  }}
  out.cases[caseId] = {{
    contract_c_sha256: loaded.sha,
    target: loaded.target,
    frozen,
    supported,
    ers,
    supported_equals_frozen: isDeepStrictEqual(supported, frozen),
    supported_canonical_b64: supportedCanonical.toString("base64"),
    released_ers_contract_d: released,
  }};
}}
process.stdout.write(JSON.stringify(out));
"""
    env = os.environ.copy()
    env.update(
        {
            "ERS_RENDER_FIXTURES": str(fixtures),
            "ERS_RENDER_CONSUMER": str(consumer_root),
            "ERS_RENDER_CONTRACT_D": str(contract_d_root),
        }
    )
    result = subprocess.run(
        ["node", "--input-type=module"],
        input=node_program,
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"decision_successor_failed:{result.stderr.strip()}")
    return json.loads(result.stdout)


def error_code(exc: BaseException) -> str:
    code = getattr(exc, "code", None)
    if isinstance(code, str):
        return code
    return str(exc)


def expect_reject(
    label: str,
    fn: Callable[[], Any],
    negative: dict[str, Any],
    expected: str | None = None,
) -> str:
    try:
        value = fn()
    except Exception as exc:  # noqa: BLE001 - the harness records the boundary
        code = error_code(exc)
        if expected is not None:
            check(expected in code, f"{label}:unexpected_error:{code}")
        negative[label] = {"rejected": True, "error": code}
        return code
    negative[label] = {
        "rejected": False,
        "returned": value if isinstance(value, (str, int, float, bool)) else type(value).__name__,
    }
    raise AssertionError(f"{label}:accepted")


def fake_permit(ers: Any, intent: dict[str, Any]) -> dict[str, Any]:
    intent_id = ers.execution_intent_identity(intent)
    return {
        "execution_permitted": True,
        "execution_occurred": False,
        "execution_intent_identity": intent_id,
        "authorization": {
            "permitted": True,
            "decision_identity": intent["input_identities"][0],
            "request": {
                "authority_state_id": AUTHORITY_STATE_ID,
                "evaluation_time": EVALUATION_TIME,
                "subject_id": ers.PRINCIPAL,
                "jurisdiction": {
                    "domain": ers.DOMAIN,
                    "operation": ers.OPERATION,
                    "scope": ers.SCOPE,
                    "target_class": ers.TARGET_CLASS,
                    "target_ref": ers.target_reference_identity(intent),
                },
            },
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ers-root", required=True, type=Path)
    parser.add_argument("--decision-root", required=True, type=Path)
    parser.add_argument("--contract-e-root", required=True, type=Path)
    parser.add_argument("--contract-d-root", required=True, type=Path)
    parser.add_argument("--consumer-root", required=True, type=Path)
    parser.add_argument("--fixtures", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    ers_root = args.ers_root.resolve()
    decision_root = args.decision_root.resolve()
    contract_e_root = args.contract_e_root.resolve()
    contract_d_root = args.contract_d_root.resolve()
    consumer_root = args.consumer_root.resolve()
    fixtures = args.fixtures.resolve()

    # Direct authority checks: the candidate may add only its own successor
    # evidence; the existing PR #127 record and frozen sources are not edited.
    check(git_head(decision_root) == DECISION_SUCCESSOR, "wrong_decision_successor")
    check(git_head(contract_e_root) == CONTRACT_E, "wrong_contract_e_profile")
    check(git_head(contract_d_root) == CONTRACT_D, "wrong_contract_d_authority")
    check(git_head(consumer_root) == "12e7e640b229619501960b1b89cf4716d8d985b3", "wrong_contract_c_consumer")
    check(git_head(ers_root) == ERS_SUCCESSOR, "wrong_ers_successor")
    check(
        git_text(ers_root, "rev-parse", f"{ERS_RC3}:pipeline_slices/contract-e-shadow-rc3/harness/contract_e_shadow.py")
        == git_text(ers_root, "rev-parse", "HEAD:harness/contract_e_shadow.py"),
        "frozen_rc3_source_changed",
    )
    check(
        not subprocess.run(
            ["git", "-C", str(ers_root), "diff", "--quiet", ERS_RC3, "--", "pipeline_slices/contract-e-shadow-rc3"],
            check=False,
        ).returncode,
        "frozen_rc3_slice_changed",
    )
    check((ROOT / "research/parent-bound-ers-shadow-composition-20260921/RESULT.md").exists(), "pr127_record_missing")
    check(git_text(ROOT, "show", f"{APPARATUS_PR127_BASE}:research/parent-bound-ers-shadow-composition-20260921/RESULT.md") != "", "pr127_base_not_live")
    check(git_text(ROOT, "cat-file", "-t", CAL_V3) == "commit", "cal_v3_object_missing")
    check(
        git_text(contract_d_root, "rev-parse", "HEAD:validators/contract_d_core.py")
        == "564dcde5677df5ac8f86f21dc0ffd1692f44c9f0",
        "contract_d_core_blob_changed",
    )
    check(
        git_text(contract_d_root, "rev-parse", "HEAD:schema/contract-d/1.0.0/effect-registry.json")
        == "a40f4f4447470654bdc16d852f5927189ae30cc5",
        "contract_d_registry_blob_changed",
    )
    check(
        git_text(contract_e_root, "rev-parse", "HEAD:docs/research/contract-e/ers-point-of-use-crossrepo-rc2-20260919/contract_e_profile.py")
        == "4d68eb6da30118ef67485af70871edacf9edcf23",
        "contract_e_profile_blob_changed",
    )

    # Verify that the disposable composition inputs are the exact case bytes
    # recorded by the supported PR #127 receipt.
    pr127_receipt = json.loads(
        (ROOT / "research/parent-bound-ers-shadow-composition-20260921/RECEIPT.json").read_text(encoding="utf-8")
    )
    for case_id in ("PIPE01", "PIPE02", "PIPE03"):
        c_path = fixtures / case_id / "cal/contract-c.json"
        d_path = fixtures / case_id / "contract-d.json"
        check(sha256_identity(c_path.read_bytes()) == pr127_receipt["cases"][case_id]["contract_c_sha256"], f"{case_id}:cal_v3_contract_c_changed")
        check(sha256_identity(d_path.read_bytes()) == pr127_receipt["cases"][case_id]["supported_contract_d_sha256"], f"{case_id}:cal_v3_contract_d_changed")

    # The exact compatibility discriminator is rerun against the frozen E
    # profile before it is used for composition.
    profile_path = contract_e_root / "docs/research/contract-e/ers-point-of-use-crossrepo-rc2-20260919/contract_e_profile.py"
    profile = load_module("ers_render_bound_contract_e_profile", profile_path)
    compatibility_probe = {
        "schema": "execution-intent-candidate-v1",
        "executable_sha256": "sha256:" + "1" * 64,
        "entry_point": "harness.render_bound_shadow:stage_pending_review",
        "arguments": ["--mode", "shadow-render-bound"],
        "input_identities": ["decision:sha256:" + "2" * 64] + ["sha256:" + str(i) * 64 for i in range(3, 7)],
        "environment_constraints": {"mutation": "forbidden"},
        "side_effect_targets": ["20_live/epistemic-audit/pending-review/example.md"],
    }
    compatibility_identity = profile.integration_profile.execution_intent_identity(compatibility_probe)

    sys.path.insert(0, str(ers_root / "pipeline_slices/contract-e-shadow-rc4-render-bound"))
    sys.path.insert(1, str(ers_root))
    from harness import render_bound_shadow as ers  # noqa: E402
    from harness import render_packet  # noqa: E402

    decision_result = run_decision_successor(
        decision_root=decision_root,
        fixtures=fixtures,
        consumer_root=consumer_root,
        contract_d_root=contract_d_root,
    )

    # Install only the in-memory research effect extension used by the frozen
    # Contract E profile. Released Contract D is never changed.
    core, consume_mod = profile.install_research_effect_profile(contract_d_root)
    negative: dict[str, Any] = {}
    cases: dict[str, Any] = {}

    for case_id in ("PIPE01", "PIPE02", "PIPE03"):
        node_case = decision_result["cases"][case_id]
        stored_d = (fixtures / case_id / "contract-d.json").read_bytes()
        supported_canonical = base64.b64decode(node_case["supported_canonical_b64"])
        check(node_case["supported_equals_frozen"], f"{case_id}:supported_policy_changed")
        check(supported_canonical == stored_d, f"{case_id}:supported_contract_d_not_byte_compatible")
        check(node_case["released_ers_contract_d"]["accepted"] is False, f"{case_id}:released_contract_d_accepted_ers")
        check("unknown_effect_type" in node_case["released_ers_contract_d"]["message"], f"{case_id}:released_contract_d_code_changed")
        cases[case_id] = {
            "parent_conclusion": node_case["ers"]["metadata"]["diagnostics"]["parent_conclusion"],
            "ers_disposition": node_case["ers"]["evaluation"]["disposition"],
            "ers_decision_identity": core.semantic_identity(node_case["ers"]),
            "supported_canonical_sha256": sha256_identity(supported_canonical),
            "supported_matches_frozen_v3": True,
            "released_contract_d_rejection": node_case["released_ers_contract_d"]["message"],
        }

    pipe01 = decision_result["cases"]["PIPE01"]
    decision_id = core.semantic_identity(pipe01["ers"])
    check(decision_id == PIPE01_DECISION_ID, "pipe01_decision_identity_changed")
    check(pipe01["target"]["content_sha256"] == CLAIM_CONTENT_ID, "pipe01_claim_identity_changed")

    packet = render_packet.freeze_render_packet(fixture_snapshot())
    payload = render_packet.render_pending_review(packet)
    independent_payload = independent_render(packet)
    check(payload == independent_payload, "independent_render_disagrees")
    packet_id = render_packet.render_packet_identity(packet)
    payload_id = render_packet.rendered_payload_identity(packet)
    check(packet_id == independent_object_identity(packet), "packet_identity_independent_check_failed")
    check(payload_id == sha256_identity(payload), "payload_identity_independent_check_failed")
    check(payload.endswith(b"\n"), "payload_missing_terminal_newline")

    packet_replay = render_packet.freeze_render_packet(copy.deepcopy(fixture_snapshot()))
    payload_replay = render_packet.render_pending_review(packet_replay)
    check(packet == packet_replay, "packet_replay_changed")
    check(payload == payload_replay, "payload_replay_changed")
    check(packet_id == render_packet.render_packet_identity(packet_replay), "packet_replay_identity_changed")
    check(payload_id == render_packet.rendered_payload_identity(packet_replay), "payload_replay_identity_changed")

    reordered = fixture_snapshot()
    reordered["evidence"] = list(reversed(reordered["evidence"]))
    reordered["contradictions"] = list(reversed(reordered["contradictions"]))
    reordered["revisions"] = list(reversed(reordered["revisions"]))
    reordered_packet = render_packet.freeze_render_packet(reordered)
    check(packet == reordered_packet, "nondeterministic_row_order_changed_packet")
    check(payload == render_packet.render_pending_review(reordered_packet), "nondeterministic_row_order_changed_payload")

    render_mutation_results: dict[str, bool] = {}
    for label, mutate in {
        "claim_text": lambda value: value["claim"].update(text=CLAIM_TEXT + " Changed."),
        "claim_project_tag": lambda value: value["claim"].update(project_tag="research"),
        "claim_confidence": lambda value: value["claim"].update(confidence=0.92),
        "claim_credibility": lambda value: value["claim"].update(credibility=0.89),
        "claim_updated_at": lambda value: value["claim"].update(updated_at="2026-09-21T09:30:00Z"),
        "run_id": lambda value: value.update(run_id="PIPE01-mutated"),
        "render_date": lambda value: value.update(render_date="2026-09-22"),
        "evidence_source_name": lambda value: value["evidence"][0].update(source_name="other.md"),
        "evidence_source_uri": lambda value: value["evidence"][0].update(source_uri="file:///other.md"),
        "evidence_anchor": lambda value: value["evidence"][0].update(passage_anchor="chars:1-2"),
        "evidence_relation": lambda value: value["evidence"][0].update(relation="refutes"),
        "evidence_weight": lambda value: value["evidence"][0].update(weight=0.44),
        "evidence_extractor": lambda value: value["evidence"][0].update(extracted_by="other"),
        "evidence_count": lambda value: value["evidence"].append(copy.deepcopy(value["evidence"][0])),
        "contradiction_resolution": lambda value: value["contradictions"][1].update(resolution="accepted"),
        "revision_changed_at": lambda value: value["revisions"][0].update(changed_at="2026-09-21T10:00:00Z"),
        "revision_field": lambda value: value["revisions"][0].update(field_changed="credibility"),
        "revision_old": lambda value: value["revisions"][0].update(old_value="0.70"),
        "revision_new": lambda value: value["revisions"][0].update(new_value="0.92"),
        "revision_actor": lambda value: value["revisions"][0].update(changed_by="other-auditor"),
        "revision_reason": lambda value: value["revisions"][0].update(reason="changed reason"),
    }.items():
        changed_snapshot = fixture_snapshot()
        mutate(changed_snapshot)
        changed_packet = render_packet.freeze_render_packet(changed_snapshot)
        render_mutation_results[label] = (
            render_packet.render_packet_identity(changed_packet) != packet_id
            or render_packet.rendered_payload_identity(changed_packet) != payload_id
        )
        check(render_mutation_results[label], f"render_mutation_not_observable:{label}")

    pre_state: dict[str, Any]
    intent: dict[str, Any]
    contract_e_result: dict[str, Any]
    shadow_result: dict[str, Any]
    sandbox_before: list[str]
    sandbox_after: list[str]
    with tempfile.TemporaryDirectory(prefix="ers-render-bound-sandbox-", dir="/private/tmp") as td:
        sandbox = Path(td)
        sandbox_before = sorted(str(path.relative_to(sandbox)) for path in sandbox.rglob("*"))
        pre_state = ers._base.observe_pre_state(sandbox, packet["render"]["target_relative_path"])
        executable_id = sha256_identity(
            (ers_root / "pipeline_slices/contract-e-shadow-rc4-render-bound/harness/render_bound_shadow.py").read_bytes()
        )
        intent = ers.build_execution_intent(
            decision_identity=decision_id,
            executable_sha256=executable_id,
            claim_id="ROOT",
            claim_content_sha256=CLAIM_CONTENT_ID,
            pre_state=pre_state,
            relative_path=packet["render"]["target_relative_path"],
            render_packet=packet,
        )
        check(intent["input_identities"][:3] == [decision_id, CLAIM_CONTENT_ID, pre_state["state_sha256"]], "existing_intent_bindings_changed")
        check(intent["input_identities"][3] == packet_id, "packet_identity_not_in_intent")
        check(intent["input_identities"][4] == payload_id, "payload_identity_not_in_intent")
        check(profile.integration_profile.execution_intent_identity(intent) == ers.execution_intent_identity(intent), "contract_e_and_ers_intent_identity_disagree")

        target_reference = profile.target_reference_for_intent(intent)
        authority_state = profile.make_authority_state(
            target_reference,
            valid_until="2026-09-22T00:00:00Z",
        )
        expected = profile.expectation_for(pipe01["ers"], core, consume_mod)
        contract_e_result = profile.shadow_gate(
            contract_d_root=contract_d_root,
            decision=pipe01["ers"],
            expected=expected,
            authority_state=authority_state,
            execution_intent=intent,
            evaluation_time=EVALUATION_TIME,
        )
        check(contract_e_result["execution_permitted"] is True, "contract_e_did_not_permit_pipe01")
        check(contract_e_result["execution_occurred"] is False, "contract_e_execution_occurred")
        shadow_result = ers.stage_pending_review(
            contract_e_result,
            intent,
            expected_relative_path=packet["render"]["target_relative_path"],
            mainframe_root=sandbox,
            current_authority_state_id=authority_state["authority_state_id"],
            current_evaluation_time=EVALUATION_TIME,
            expected_executable_sha256=executable_id,
            render_packet=packet,
            payload=payload,
        )
        sandbox_after = sorted(str(path.relative_to(sandbox)) for path in sandbox.rglob("*"))

    check(shadow_result["shadow_ready"] is True, "pipe01_not_shadow_ready")
    check(shadow_result["execution_occurred"] is False, "pipe01_execution_occurred")
    check(sandbox_before == [], "sandbox_not_empty_before")
    check(sandbox_after == [], "sandbox_mutated_after")
    check(shadow_result["render_packet_sha256"] == packet_id, "shadow_packet_identity_changed")
    check(shadow_result["rendered_payload_sha256"] == payload_id, "shadow_payload_identity_changed")

    # Payload and packet boundary falsifiers. These use the exact authorized
    # intent/result shape and change only the candidate at point of use.
    negative["missing_payload"] = {}
    with tempfile.TemporaryDirectory(prefix="ers-render-bound-negative-", dir="/private/tmp") as td:
        root = Path(td)
        expect_reject(
            "missing_payload",
            lambda: ers.stage_pending_review(
                contract_e_result,
                intent,
                expected_relative_path=packet["render"]["target_relative_path"],
                mainframe_root=root,
                current_authority_state_id=authority_state["authority_state_id"],
                current_evaluation_time=EVALUATION_TIME,
                expected_executable_sha256=sha256_identity((ers_root / "pipeline_slices/contract-e-shadow-rc4-render-bound/harness/render_bound_shadow.py").read_bytes()),
                render_packet=packet,
                payload=None,
            ),
            negative,
            "missing_candidate_payload",
        )
        mutated_payload = payload[:-1] + (b"X" if payload[-1:] != b"X" else b"Y")
        expect_reject(
            "one_byte_payload_mutation",
            lambda: ers.stage_pending_review(
                contract_e_result,
                intent,
                expected_relative_path=packet["render"]["target_relative_path"],
                mainframe_root=root,
                current_authority_state_id=authority_state["authority_state_id"],
                current_evaluation_time=EVALUATION_TIME,
                expected_executable_sha256=sha256_identity((ers_root / "pipeline_slices/contract-e-shadow-rc4-render-bound/harness/render_bound_shadow.py").read_bytes()),
                render_packet=packet,
                payload=mutated_payload,
            ),
            negative,
            "rendered_payload_identity_mismatch",
        )
        other_snapshot = fixture_snapshot()
        other_snapshot["render_date"] = "2026-09-22"
        other_packet = render_packet.freeze_render_packet(other_snapshot)
        expect_reject(
            "different_valid_packet_payload",
            lambda: ers.stage_pending_review(
                contract_e_result,
                intent,
                expected_relative_path=packet["render"]["target_relative_path"],
                mainframe_root=root,
                current_authority_state_id=authority_state["authority_state_id"],
                current_evaluation_time=EVALUATION_TIME,
                expected_executable_sha256=sha256_identity((ers_root / "pipeline_slices/contract-e-shadow-rc4-render-bound/harness/render_bound_shadow.py").read_bytes()),
                render_packet=packet,
                payload=render_packet.render_pending_review(other_packet),
            ),
            negative,
            "rendered_payload_identity_mismatch",
        )
        changed_packet_intent = copy.deepcopy(intent)
        changed_packet_intent["input_identities"][3] = "sha256:" + "9" * 64
        expect_reject(
            "mutated_render_packet_identity",
            lambda: ers.stage_pending_review(
                fake_permit(ers, changed_packet_intent),
                changed_packet_intent,
                expected_relative_path=packet["render"]["target_relative_path"],
                mainframe_root=root,
                current_authority_state_id=AUTHORITY_STATE_ID,
                current_evaluation_time=EVALUATION_TIME,
                expected_executable_sha256=sha256_identity((ers_root / "pipeline_slices/contract-e-shadow-rc4-render-bound/harness/render_bound_shadow.py").read_bytes()),
                render_packet=packet,
                payload=payload,
            ),
            negative,
            "render_packet_identity_mismatch",
        )
        changed_payload_intent = copy.deepcopy(intent)
        changed_payload_intent["input_identities"][4] = "sha256:" + "9" * 64
        expect_reject(
            "mutated_payload_identity",
            lambda: ers.stage_pending_review(
                fake_permit(ers, changed_payload_intent),
                changed_payload_intent,
                expected_relative_path=packet["render"]["target_relative_path"],
                mainframe_root=root,
                current_authority_state_id=AUTHORITY_STATE_ID,
                current_evaluation_time=EVALUATION_TIME,
                expected_executable_sha256=sha256_identity((ers_root / "pipeline_slices/contract-e-shadow-rc4-render-bound/harness/render_bound_shadow.py").read_bytes()),
                render_packet=packet,
                payload=payload,
            ),
            negative,
            "rendered_payload_identity_mismatch",
        )

        wrong_decision = copy.deepcopy(intent)
        wrong_decision["input_identities"][0] = "decision:sha256:" + "4" * 64
        wrong_decision_result = fake_permit(ers, wrong_decision)
        wrong_decision_result["authorization"]["decision_identity"] = decision_id
        expect_reject(
            "wrong_decision_identity",
            lambda: ers.stage_pending_review(
                wrong_decision_result,
                wrong_decision,
                expected_relative_path=packet["render"]["target_relative_path"],
                mainframe_root=root,
                current_authority_state_id=AUTHORITY_STATE_ID,
                current_evaluation_time=EVALUATION_TIME,
                expected_executable_sha256=sha256_identity((ers_root / "pipeline_slices/contract-e-shadow-rc4-render-bound/harness/render_bound_shadow.py").read_bytes()),
                render_packet=packet,
                payload=payload,
            ),
            negative,
            "decision_identity_binding_mismatch",
        )
        expect_reject(
            "wrong_executable_identity",
            lambda: ers.stage_pending_review(
                contract_e_result,
                intent,
                expected_relative_path=packet["render"]["target_relative_path"],
                mainframe_root=root,
                current_authority_state_id=authority_state["authority_state_id"],
                current_evaluation_time=EVALUATION_TIME,
                expected_executable_sha256="sha256:" + "8" * 64,
                render_packet=packet,
                payload=payload,
            ),
            negative,
            "unexpected_executable_identity",
        )
        wrong_pre = copy.deepcopy(intent)
        wrong_pre["input_identities"][2] = "sha256:" + "7" * 64
        expect_reject(
            "wrong_pre_state",
            lambda: ers.stage_pending_review(
                fake_permit(ers, wrong_pre),
                wrong_pre,
                expected_relative_path=packet["render"]["target_relative_path"],
                mainframe_root=root,
                current_authority_state_id=AUTHORITY_STATE_ID,
                current_evaluation_time=EVALUATION_TIME,
                expected_executable_sha256=sha256_identity((ers_root / "pipeline_slices/contract-e-shadow-rc4-render-bound/harness/render_bound_shadow.py").read_bytes()),
                render_packet=packet,
                payload=payload,
            ),
            negative,
            "point_of_use_pre_state_mismatch",
        )
        expect_reject(
            "altered_target",
            lambda: ers.stage_pending_review(
                contract_e_result,
                intent,
                expected_relative_path=packet["render"]["target_relative_path"].replace("PIPE01", "PIPE02"),
                mainframe_root=root,
                current_authority_state_id=authority_state["authority_state_id"],
                current_evaluation_time=EVALUATION_TIME,
                expected_executable_sha256=sha256_identity((ers_root / "pipeline_slices/contract-e-shadow-rc4-render-bound/harness/render_bound_shadow.py").read_bytes()),
                render_packet=packet,
                payload=payload,
            ),
            negative,
            "side_effect_target_mismatch",
        )
        expect_reject(
            "stale_authority_state",
            lambda: ers.stage_pending_review(
                contract_e_result,
                intent,
                expected_relative_path=packet["render"]["target_relative_path"],
                mainframe_root=root,
                current_authority_state_id="sha256:" + "b" * 64,
                current_evaluation_time=EVALUATION_TIME,
                expected_executable_sha256=sha256_identity((ers_root / "pipeline_slices/contract-e-shadow-rc4-render-bound/harness/render_bound_shadow.py").read_bytes()),
                render_packet=packet,
                payload=payload,
            ),
            negative,
            "stale_authority_state",
        )

    # PIPE02 and PIPE03 are held by the native Decision successor. Wrap the
    # frozen Contract E evaluator to prove no evaluation occurs for either.
    evaluation_calls: list[dict[str, Any]] = []
    original_evaluate = profile.integration_profile.evaluate

    def counted_evaluate(*call_args: Any, **call_kwargs: Any):
        evaluation_calls.append({"args": len(call_args), "kwargs": sorted(call_kwargs)})
        return original_evaluate(*call_args, **call_kwargs)

    profile.integration_profile.evaluate = counted_evaluate
    hold_codes: dict[str, str] = {}
    try:
        for case_id in ("PIPE02", "PIPE03"):
            node_case = decision_result["cases"][case_id]
            hold_core, hold_consume = profile.integration_profile.load_contract_d(str(contract_d_root))
            hold_expected = profile.expectation_for(node_case["ers"], hold_core, hold_consume)
            try:
                profile.shadow_gate(
                    contract_d_root=contract_d_root,
                    decision=node_case["ers"],
                    expected=hold_expected,
                    authority_state=authority_state,
                    execution_intent=intent,
                    evaluation_time=EVALUATION_TIME,
                )
            except Exception as exc:  # noqa: BLE001
                hold_codes[case_id] = error_code(exc)
            else:
                raise AssertionError(f"{case_id}:hold_reached_contract_e")
    finally:
        profile.integration_profile.evaluate = original_evaluate
    check(all(code == "decision_not_candidate:hold" for code in hold_codes.values()), "pipe02_pipe03_hold_code_changed")
    check(evaluation_calls == [], "pipe02_pipe03_evaluate_called")

    # Source/identity receipts for the exact frozen successor and the generic
    # Contract E profile are captured after all behavior has passed.
    successor_tree = git_text(ers_root, "rev-parse", "HEAD^{tree}")
    successor_blobs = {}
    for path in (
        "pipeline_slices/contract-e-shadow-rc4-render-bound/README.md",
        "pipeline_slices/contract-e-shadow-rc4-render-bound/SLICE_MANIFEST.json",
        "pipeline_slices/contract-e-shadow-rc4-render-bound/harness/render_packet.py",
        "pipeline_slices/contract-e-shadow-rc4-render-bound/harness/render_bound_shadow.py",
        "pipeline_slices/contract-e-shadow-rc4-render-bound/harness/test_render_bound_shadow.py",
    ):
        successor_blobs[path] = git_text(ers_root, "rev-parse", f"HEAD:{path}")

    receipt = {
        "schema": "ers-render-bound-shadow-composition-receipt/1",
        "date": "2026-09-21",
        "disposition": "SUPPORTED_FOR_CONTROLLED_LOCAL_RENDER_BOUND_ERS_SHADOW_COMPOSITION",
        "subjects": {
            "apparatus_pr127_base": APPARATUS_PR127_BASE,
            "cal_pipeline_v3": CAL_V3,
            "decision_successor": DECISION_SUCCESSOR,
            "contract_d": CONTRACT_D,
            "contract_e_profile": CONTRACT_E,
            "ers_rc3_preserved": ERS_RC3,
            "ers_successor": ERS_SUCCESSOR,
            "ers_successor_tree": successor_tree,
            "ers_successor_blobs": successor_blobs,
        },
        "compatibility": {
            "execution_intent_schema": "execution-intent-candidate-v1",
            "variable_length_input_identities": 5,
            "contract_e_result_identity": compatibility_identity,
            "contract_e_source_changed": False,
        },
        "claim": {
            "claim_id": "ROOT",
            "claim_content_sha256": CLAIM_CONTENT_ID,
            "claim_text_sha256_verified": sha256_identity(CLAIM_TEXT.encode("utf-8")),
        },
        "render_packet": {
            "schema": packet["schema"],
            "identity": packet_id,
            "canonical_bytes_sha256": packet_id,
            "canonical_byte_length": len(render_packet.canonical_packet_bytes(packet)),
            "target_relative_path": packet["render"]["target_relative_path"],
            "explicit_render_date": packet["render"]["render_date"],
            "ordered_collections": ["evidence", "contradictions", "revisions"],
            "independent_replay": True,
            "independent_row_reordering": True,
            "mutation_results": render_mutation_results,
        },
        "payload": {
            "identity": payload_id,
            "byte_length": len(payload),
            "terminal_newline": payload.endswith(b"\n"),
            "independent_renderer_match": True,
            "deterministic_replay": True,
        },
        "pipe01": {
            "decision_semantic_identity": decision_id,
            "execution_intent_identity": ers.execution_intent_identity(intent),
            "contract_e_execution_intent_identity": profile.integration_profile.execution_intent_identity(intent),
            "contract_e_result_identity": profile.integration_profile.sha256_identity(contract_e_result),
            "contract_e_execution_permitted": contract_e_result["execution_permitted"],
            "contract_e_execution_occurred": contract_e_result["execution_occurred"],
            "ers_shadow_result_identity": ers._base.sha256_identity(shadow_result),
            "ers_shadow_ready": shadow_result["shadow_ready"],
            "ers_execution_occurred": shadow_result["execution_occurred"],
            "pre_state_identity": pre_state["state_sha256"],
            "executable_identity": intent["executable_sha256"],
            "input_identities": intent["input_identities"],
            "sandbox_before": sandbox_before,
            "sandbox_after": sandbox_after,
        },
        "cases": cases,
        "hold_cases": {
            "PIPE02": {"error": hold_codes["PIPE02"], "contract_e_evaluate_calls": 0},
            "PIPE03": {"error": hold_codes["PIPE03"], "contract_e_evaluate_calls": 0},
        },
        "negative_controls": negative,
        "upstream_bytes_changed": {
            "decision_successor": False,
            "cal_pipeline_v3": False,
            "released_contract_d": False,
            "contract_e_profile": False,
            "frozen_ers_rc3_slice": False,
        },
        "execution": {
            "executor_included": False,
            "executor_invoked": False,
            "pending_review_write": False,
            "real_mainframe_mutation": False,
            "contract_d_effect_registered": False,
            "release_or_promotion": False,
        },
        "open_blockers": [
            "trusted point-of-use authority-state provenance",
            "trusted evaluation-time provenance",
            "released Contract D ERS effect registration",
            "Contract E production authorization",
            "real executor behavior",
            "filesystem write atomicity and recovery semantics",
        ],
    }

    if args.output:
        args.output.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
