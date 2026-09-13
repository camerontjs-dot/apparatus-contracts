from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Callable

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import candidate_a_rc1 as C

P0 = "e588e1295367a4b867d608342aaacaccb41850b8"
P1 = "175246ae16932f2f34a399560d7f76013213bf97"
P15 = "163d0d424777ef3c0a3b45dec2888c845634205d"
P2 = "f5337dedaad045aa290e80f69dc83ac1a0f73436"
P1_CORPUS_BLOB = "0ff4f66bca00924755d42ed7f944c4dae8d10f66"
P2_ORACLE_BLOB = "9f00cd332ad366b878f60d13440af639360928de"
CANDIDATE_FREEZE = "ba5f55b0fb6ca54e0461a688813b66fd81bf8c4c"
PREREG = "55b0fc12c7b884556e2d0d4dc7811665301326df"

P2_PATH = ROOT / "research" / "contract_c_successor_ground_up_20260913" / "phase2_bakeoff.py"
spec = importlib.util.spec_from_file_location("contract_c_phase2_frozen_oracle", P2_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"cannot load frozen Phase 2 oracle: {P2_PATH}")
P2M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(P2M)
ORACLE: dict[str, dict[str, Any]] = P2M.O

RESOLVER_ENTRIES = [{
    "semantic_implementation_sha": C.CAL_RC1_IMPLEMENTATION,
    "policy_sha256": C.CAL_RC1_POLICY_SHA256,
    "projection_blob": "9bc152275759304be03b84014c56bd434549a64a",
    "policy": {"profile": "cal-v1-candidate-2026-09", "semantics": "typed-source-grounded-scoreless-categorical", "supported_families": ["direct_event_order", "strict_comparison"]},
}]
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
        out["propositions"].append({
            "proposition": {"proposition_id": p["proposition_id"], "content_sha256": "sha256:" + p["proposition_sha256"]},
            "execution": {"state": p["execution"], "completion": p["completion"]},
            "terminal": copy.deepcopy(p["terminal"]),
            "participants": [{"evidence_ref": {"source_id": row["source_id"], "passage_id": row["passage_id"]}, "relation": REL_ENCODE[row["polarity"]], "role": row["role"]} for row in p["participants"]],
            "basis_groups": [[{"source_id": by[sym]["source_id"], "passage_id": by[sym]["passage_id"]} for sym in group] for group in p["msc"]],
        })
    return C.seal(out)


def project_to_phase2(value: dict[str, Any], *, validate: bool) -> dict[str, Any]:
    if validate:
        C.validate_object(value)
    props: list[dict[str, Any]] = []
    for p in value["propositions"]:
        participants = []
        symbol_by_key: dict[tuple[str, str], str] = {}
        for row in p["participants"]:
            key = (row["evidence_ref"]["source_id"], row["evidence_ref"]["passage_id"])
            symbol = row["evidence_ref"]["passage_id"]
            symbol_by_key[key] = symbol
            participants.append({"symbol": symbol, "source_id": key[0], "passage_id": key[1], "polarity": REL_DECODE.get(row["relation"], row["relation"]), "role": row["role"]})
        msc = [[symbol_by_key[(r["source_id"], r["passage_id"])] for r in group] for group in p["basis_groups"]]
        raw_hash = p["proposition"]["content_sha256"]
        if isinstance(raw_hash, str) and raw_hash.startswith("sha256:"):
            raw_hash = raw_hash[7:]
        props.append({"proposition_id": p["proposition"]["proposition_id"], "proposition_sha256": raw_hash, "execution": p["execution"]["state"], "completion": p["execution"]["completion"], "terminal": copy.deepcopy(p["terminal"]), "participants": participants, "msc": msc})
    return P2M.norm({"contract_b": copy.deepcopy(value["contract_b"]), "producer": {"semantic_implementation_sha": value["producer"]["semantic_implementation_sha"], "policy_sha256": value["producer"]["policy_sha256"]}, "result_execution": value["execution"]["state"], "propositions": props})


def evidence_index(o: dict[str, Any]) -> set[tuple[str, str]]:
    return {(row["source_id"], row["passage_id"]) for p in o["propositions"] for row in p["participants"]}


def verify_positive(name: str, value: dict[str, Any], o: dict[str, Any]) -> None:
    C.verify_candidate(value, exact_contract_b=o["contract_b"], evidence_index=evidence_index(o), independently_selected_resolver_commit_sha=C.POLICY_RESOLVER_FIXTURE_COMMIT, resolver_entries=RESOLVER_ENTRIES, expected_whole_object_sha256=C.whole_object_sha256(value))
    if project_to_phase2(value, validate=True) != P2M.norm(o):
        raise AssertionError(f"{name}: RC1 reconstruction differs from exact frozen Phase 2 oracle")


def reseal(value: dict[str, Any]) -> dict[str, Any]:
    x = copy.deepcopy(value); x.pop("result_set_id", None); return C.seal(x)

def p0(value: dict[str, Any]) -> dict[str, Any]: return value["propositions"][0]
def find_part(p: dict[str, Any], passage_id: str) -> dict[str, Any]: return next(row for row in p["participants"] if row["evidence_ref"]["passage_id"] == passage_id)
def find_ref(passage_id: str) -> dict[str, str]: return {"source_id": "src-" + passage_id.lower(), "passage_id": passage_id}

def mutate(name: str, f: Callable[[dict[str, Any]], None], *, reseal_after: bool = False) -> Callable[[dict[str, Any]], dict[str, Any]]:
    def apply(base: dict[str, Any]) -> dict[str, Any]:
        x = copy.deepcopy(base); f(x); return reseal(x) if reseal_after else x
    apply.__name__ = name; return apply


def attacks() -> list[dict[str, Any]]:
    A: list[dict[str, Any]] = []
    def add(i: int, label: str, specimen: str, mut: Callable[[dict[str, Any]], dict[str, Any]], expected: set[str]) -> None:
        A.append({"id": f"A{i:02d}", "label": label, "specimen": specimen, "mutate": mut, "expected_gates": expected})
    add(1, "wrong research profile", "SP-01-single-support", mutate("profile", lambda x: x.__setitem__("profile", "contract-c-successor-candidate-a-rc2-attacker")), {"structure_semantics"})
    add(2, "unknown top-level field", "SP-01-single-support", mutate("unknown", lambda x: x.__setitem__("extensions", {})), {"structure_semantics"})
    add(3, "destination routing injection", "SP-01-single-support", mutate("routing", lambda x: x.__setitem__("destination_policy", {"threshold": 0.5})), {"structure_semantics"})
    add(4, "Authorization injection", "SP-01-single-support", mutate("auth", lambda x: x.__setitem__("authorization", {"actor": "attacker"})), {"structure_semantics"})
    add(5, "generic assessment slot injection", "SP-01-single-support", mutate("assess", lambda x: p0(x).__setitem__("assessments", {"eligibility": "pass"})), {"structure_semantics"})
    add(6, "full policy payload injection", "SP-01-single-support", mutate("policy_payload", lambda x: x["producer"].__setitem__("policy", {"profile": "forged"})), {"structure_semantics"})
    add(7, "repeated passage hash injection", "SP-01-single-support", mutate("passage_hash", lambda x: find_part(p0(x), "S1")["evidence_ref"].__setitem__("passage_sha256", "sha256:" + "0"*64)), {"structure_semantics"})
    add(8, "separate contribution id injection", "SP-01-single-support", mutate("contrib", lambda x: find_part(p0(x), "S1").__setitem__("contribution_id", "c1")), {"structure_semantics"})
    add(9, "duplicate participant", "SP-01-single-support", mutate("dup_part", lambda x: p0(x)["participants"].append(copy.deepcopy(p0(x)["participants"][0]))), {"structure_semantics"})
    add(10, "duplicate equivalent group by permutation", "SP-09-minimal-mixed", mutate("dup_group", lambda x: p0(x)["basis_groups"].append(list(reversed(copy.deepcopy(p0(x)["basis_groups"][0]))))), {"structure_semantics"})
    add(11, "duplicate member in group", "SP-09-minimal-mixed", mutate("dup_member", lambda x: p0(x)["basis_groups"][0].append(copy.deepcopy(p0(x)["basis_groups"][0][0]))), {"structure_semantics"})
    add(12, "residual participant in basis", "SP-06-support-plus-neutral-residual", mutate("residual_basis", lambda x: p0(x)["basis_groups"].append([find_ref("N1")])), {"structure_semantics"})
    add(13, "uncovered causal participant", "SP-03-two-independent-supports", mutate("uncovered", lambda x: p0(x)["basis_groups"].pop()), {"structure_semantics"})
    add(14, "non-minimal strict-superset group", "SP-03-two-independent-supports", mutate("superset", lambda x: p0(x)["basis_groups"].append([find_ref("S1"), find_ref("S2")])), {"structure_semantics"})
    add(15, "fake joint over independent alternatives", "SP-03-two-independent-supports", mutate("fake_joint", lambda x: p0(x).__setitem__("basis_groups", [[find_ref("S1"), find_ref("S2")]]), reseal_after=True), {"external_authority", "oracle"})
    def unique_winner(x: dict[str, Any]) -> None:
        p = p0(x); p["basis_groups"] = [[find_ref("S1"), find_ref("R1")]]; find_part(p, "S2")["role"] = "residual"
    add(16, "artificial unique winner", "SP-10-alt-joint-mixed", mutate("unique_winner", unique_winner, reseal_after=True), {"external_authority", "oracle"})
    add(17, "neutral to support laundering", "SP-07-causal-neutral-unresolved", mutate("neutral_support", lambda x: find_part(p0(x), "U1").__setitem__("relation", "supports"), reseal_after=True), {"structure_semantics", "oracle"})
    add(18, "support/refute inversion", "SP-01-single-support", mutate("invert", lambda x: find_part(p0(x), "S1").__setitem__("relation", "refutes"), reseal_after=True), {"structure_semantics", "oracle"})
    add(19, "causal to residual role movement", "SP-06-support-plus-neutral-residual", mutate("role", lambda x: find_part(p0(x), "S1").__setitem__("role", "residual"), reseal_after=True), {"structure_semantics", "oracle"})
    add(20, "same-ID proposition content substitution", "SP-01-single-support", mutate("prop_content", lambda x: p0(x)["proposition"].__setitem__("content_sha256", "sha256:" + "a"*64), reseal_after=True), {"external_authority", "oracle"})
    add(21, "Contract-B world substitution", "SP-01-single-support", mutate("world", lambda x: x["contract_b"].__setitem__("bundle_hash", "sha256:" + "b"*64), reseal_after=True), {"exact_b", "external_authority", "oracle"})
    def unknown_ref(x: dict[str, Any]) -> None:
        p = p0(x); find_part(p, "S1")["evidence_ref"] = {"source_id": "src-x", "passage_id": "X"}; p["basis_groups"] = [[{"source_id": "src-x", "passage_id": "X"}]]
    add(22, "evidence ref absent from bound world", "SP-01-single-support", mutate("unknown_ref", unknown_ref, reseal_after=True), {"exact_b", "external_authority", "oracle"})
    add(23, "CAL implementation substitution", "SP-01-single-support", mutate("impl", lambda x: x["producer"].__setitem__("semantic_implementation_sha", "0"*40), reseal_after=True), {"policy_resolution", "external_authority", "oracle"})
    add(24, "policy digest substitution", "SP-01-single-support", mutate("policy", lambda x: x["producer"].__setitem__("policy_sha256", "0"*64), reseal_after=True), {"policy_resolution", "external_authority", "oracle"})
    add(25, "policy resolver authority substitution", "SP-01-single-support", mutate("resolver", lambda x: x["producer"].__setitem__("policy_resolver_commit_sha", "0"*40), reseal_after=True), {"policy_resolution", "external_authority"})
    def failed_to_completed(x: dict[str, Any]) -> None:
        replacement = encode(ORACLE["EX-05-completed-not-checkable"]); x["execution"] = copy.deepcopy(replacement["execution"]); x["propositions"] = copy.deepcopy(replacement["propositions"])
    add(26, "failed result-set to completed epistemic", "EX-01-result-set-failed", mutate("failed_completed", failed_to_completed, reseal_after=True), {"external_authority", "oracle"})
    def nc_to_failed(x: dict[str, Any]) -> None:
        x["execution"] = {"state": "failed"}; x["propositions"] = []
    add(27, "completed not_checkable to failed", "EX-05-completed-not-checkable", mutate("nc_failed", nc_to_failed, reseal_after=True), {"external_authority", "oracle"})
    add(28, "stale local result_set_id", "SP-01-single-support", mutate("stale", lambda x: x["contract_b"].__setitem__("bundle_id", "W-stale")), {"local_identity"})
    def delete_residual(x: dict[str, Any]) -> None:
        p = p0(x); p["participants"] = [row for row in p["participants"] if row["evidence_ref"]["passage_id"] != "N1"]
    add(29, "coherent reseal after residual deletion", "SP-06-support-plus-neutral-residual", mutate("delete_residual", delete_residual, reseal_after=True), {"external_authority", "oracle"})
    add(30, "attacker-selected replacement external digest", "SP-06-support-plus-neutral-residual", mutate("attacker_digest", delete_residual, reseal_after=True), {"external_authority", "oracle"})
    def cross_prop(x: dict[str, Any]) -> None:
        p = x["propositions"][0]; p["participants"][0]["evidence_ref"] = find_ref("P2R1"); p["basis_groups"] = [[find_ref("P2R1")]]
    add(31, "cross-proposition participant substitution", "SP-14-result-set-multi-proposition", mutate("cross_prop", cross_prop, reseal_after=True), {"external_authority", "oracle"})
    def cross_world(x: dict[str, Any]) -> None:
        p = p0(x); find_part(p, "S2")["evidence_ref"] = {"source_id": "src-w2", "passage_id": "S2-W2"}; p["basis_groups"] = [[find_ref("S1")], [{"source_id":"src-w2","passage_id":"S2-W2"}]]
    add(32, "cross-world member composition", "SP-03-two-independent-supports", mutate("cross_world", cross_world, reseal_after=True), {"exact_b", "external_authority", "oracle"})
    add(33, "producer-private terminal reason", "SP-07-causal-neutral-unresolved", mutate("private_reason", lambda x: p0(x)["terminal"].__setitem__("reason", "RELATION_UNRESOLVED"), reseal_after=True), {"structure_semantics", "oracle"})
    add(34, "measurement/score injection", "SP-01-single-support", mutate("measurement", lambda x: p0(x).__setitem__("measurement", {"score": 0.99})), {"structure_semantics"})
    add(35, "malformed terminal completion pairing", "SP-01-single-support", mutate("pairing", lambda x: p0(x)["execution"].__setitem__("completion", "not_checkable"), reseal_after=True), {"structure_semantics", "oracle"})
    def failed_terminal(x: dict[str, Any]) -> None:
        p = p0(x); p["terminal"] = {"verdict":"not_checkable","reason":"unresolved_categorical_relation"}
    add(36, "fabricated terminal on failed proposition", "EX-03-proposition-failed", mutate("failed_terminal", failed_terminal, reseal_after=True), {"structure_semantics", "oracle"})
    add(37, "MIXED_RELATIONS lowercase substitution", "SP-09-minimal-mixed", mutate("reason_case", lambda x: p0(x)["terminal"].__setitem__("reason", "mixed_relations"), reseal_after=True), {"structure_semantics", "oracle"})
    return A


def gate_results(mutant: dict[str, Any], base: dict[str, Any], o: dict[str, Any]) -> tuple[set[str], dict[str, str]]:
    caught: set[str] = set(); details: dict[str, str] = {}; structurally_valid = True
    try:
        C.validate_object(mutant)
    except Exception as exc:
        structurally_valid = False; msg = str(exc); gate = "local_identity" if "candidate.result_set_id: stale" in msg else "structure_semantics"; caught.add(gate); details[gate] = msg
    if structurally_valid:
        try: C.verify_contract_b_references(mutant, exact_contract_b=o["contract_b"], evidence_index=evidence_index(o))
        except Exception as exc: caught.add("exact_b"); details["exact_b"] = str(exc)
        try: C.verify_policy_resolution(mutant, independently_selected_resolver_commit_sha=C.POLICY_RESOLVER_FIXTURE_COMMIT, resolver_entries=RESOLVER_ENTRIES)
        except Exception as exc: caught.add("policy_resolution"); details["policy_resolution"] = str(exc)
        try: C.verify_external_authority(mutant, expected_whole_object_sha256=C.whole_object_sha256(base))
        except Exception as exc: caught.add("external_authority"); details["external_authority"] = str(exc)
    try:
        if project_to_phase2(mutant, validate=False) != P2M.norm(o):
            caught.add("oracle"); details["oracle"] = "representation projection differs from exact imported frozen Phase 2 oracle"
    except Exception as exc:
        caught.add("oracle"); details["oracle"] = f"oracle projection could not preserve equality: {exc}"
    return caught, details


def permutation_controls(encoded: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    controls=[]
    def check(label: str, name: str, mutate_fn: Callable[[dict[str, Any]], None]) -> None:
        base=encoded[name]; x=copy.deepcopy(base); mutate_fn(x); C.validate_object(x)
        ok=C.canonical_bytes(x)==C.canonical_bytes(base) and x["result_set_id"]==base["result_set_id"] and C.whole_object_sha256(x)==C.whole_object_sha256(base)
        if not ok: raise AssertionError(f"permutation {label} changed identity")
        controls.append({"id":label,"specimen":name,"pass":True})
    check("P01-participants", "SP-10-alt-joint-mixed", lambda x:p0(x)["participants"].reverse())
    check("P02-groups", "SP-10-alt-joint-mixed", lambda x:p0(x)["basis_groups"].reverse())
    check("P03-group-members", "SP-09-minimal-mixed", lambda x:p0(x)["basis_groups"][0].reverse())
    check("P04-propositions", "SP-14-result-set-multi-proposition", lambda x:x["propositions"].reverse())
    def combo(x: dict[str, Any]) -> None:
        x["propositions"].reverse()
        for p in x["propositions"]:
            p["participants"].reverse(); p["basis_groups"].reverse()
            for g in p["basis_groups"]: g.reverse()
    check("P05-combined", "SP-14-result-set-multi-proposition", combo)
    return controls


def weak_controls(encoded: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    out=[]
    base=encoded["SP-06-support-plus-neutral-residual"]
    x=copy.deepcopy(base); p0(x)["participants"]=[r for r in p0(x)["participants"] if r["evidence_ref"]["passage_id"]!="N1"]; x=reseal(x); C.validate_object(x)
    proper_rejects=False
    try: C.verify_external_authority(x, expected_whole_object_sha256=C.whole_object_sha256(base))
    except Exception: proper_rejects=True
    if not proper_rejects: raise AssertionError("weak local reseal control insensitive")
    out.append({"id":"W01-local-reseal-only","weak_vulnerable":True,"required_stack_catches":True})
    neutral=encoded["SP-07-causal-neutral-unresolved"]
    weak_verdict="supported" if any(r["role"]=="causal" and r["relation"] in {"supports","non_polarized"} for r in p0(neutral)["participants"]) else "not_checkable"
    if weak_verdict!="supported": raise AssertionError("weak neutral consumer did not expose vulnerability")
    out.append({"id":"W02-neutral-as-support","weak_vulnerable":True,"unsafe_output":weak_verdict,"required_terminal":"not_checkable"})
    base=encoded["SP-03-two-independent-supports"]
    fake=copy.deepcopy(base); p0(fake)["basis_groups"]=[[find_ref("S1"),find_ref("S2")]]; fake=reseal(fake); C.validate_object(fake)
    causal={r["evidence_ref"]["passage_id"] for r in p0(fake)["participants"] if r["role"]=="causal"}; covered={r["passage_id"] for g in p0(fake)["basis_groups"] for r in g}
    weak_accepts=causal==covered; oracle_rejects=project_to_phase2(fake,validate=False)!=P2M.norm(ORACLE["SP-03-two-independent-supports"])
    if not (weak_accepts and oracle_rejects): raise AssertionError("weak basis checker insensitive")
    out.append({"id":"W03-covering-joint-only","weak_vulnerable":True,"required_oracle_catches":True})
    base=encoded["SP-09-minimal-mixed"]
    lower=copy.deepcopy(base); p0(lower)["terminal"]["reason"]="mixed_relations"; lower=reseal(lower)
    exact_reason=ORACLE["SP-09-minimal-mixed"]["propositions"][0]["terminal"]["reason"]
    weak_normalized_accepts=p0(lower)["terminal"]["reason"].lower()==exact_reason.lower(); exact_rejects=p0(lower)["terminal"]["reason"]!=exact_reason; validator_rejects=False
    try: C.validate_object(lower)
    except Exception: validator_rejects=True
    if not (weak_normalized_accepts and exact_rejects and validator_rejects and exact_reason=="MIXED_RELATIONS"):
        raise AssertionError("weak copied/case-normalized reason oracle did not expose RC0 vulnerability")
    out.append({"id":"W04-case-normalized-reason-oracle","weak_vulnerable":True,"frozen_reason":exact_reason,"attacker_reason":"mixed_relations","required_stack_catches":True})
    return out


def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument("--out",required=True); args=ap.parse_args()
    expected_names={"SP-01-single-support","SP-02-single-refutation","SP-03-two-independent-supports","SP-04-two-independent-refutations","SP-05-joint-basis","SP-06-support-plus-neutral-residual","SP-07-causal-neutral-unresolved","SP-08-two-independent-unresolved","SP-09-minimal-mixed","SP-10-alt-joint-mixed","SP-11-symmetric-alt-joint-mixed","SP-12-alt-by-alt-mixed","SP-13-completed-no-deciding","SP-14-result-set-multi-proposition","EX-01-result-set-failed","EX-02-result-set-incomplete","EX-03-proposition-failed","EX-04-proposition-incomplete","EX-05-completed-not-checkable"}
    if set(ORACLE) != expected_names: raise AssertionError("frozen Phase 2 oracle specimen set changed")
    for name in ["SP-09-minimal-mixed","SP-10-alt-joint-mixed","SP-11-symmetric-alt-joint-mixed","SP-12-alt-by-alt-mixed"]:
        if ORACLE[name]["propositions"][0]["terminal"]["reason"] != "MIXED_RELATIONS": raise AssertionError(f"{name}: frozen oracle reason identity is not exact MIXED_RELATIONS")
    encoded={name:encode(o) for name,o in ORACLE.items()}; positive=[]
    for name,o in ORACLE.items():
        verify_positive(name,encoded[name],o); positive.append({"id":name,"pass":True,"whole_object_sha256":C.whole_object_sha256(encoded[name])})
    perms=permutation_controls(encoded); attack_rows=[]
    for a in attacks():
        base=encoded[a["specimen"]]; mutant=a["mutate"](base); caught,details=gate_results(mutant,base,ORACLE[a["specimen"]])
        if not caught: raise AssertionError(f"{a['id']} {a['label']}: undetected")
        if not (caught & a["expected_gates"]): raise AssertionError(f"{a['id']} {a['label']}: caught by {caught}, expected one of {a['expected_gates']}")
        if a["id"]=="A30":
            attacker_selected=C.whole_object_sha256(mutant); attacker_digest_would_match=True
            try: C.verify_external_authority(mutant,expected_whole_object_sha256=attacker_selected)
            except Exception: attacker_digest_would_match=False
            if not attacker_digest_would_match: raise AssertionError("A30 failed to demonstrate attacker-selected digest distinction")
            details["attacker_selected_digest_control"]="replacement digest matches mutated bytes if incorrectly trusted; qualification authority remains the independently frozen base digest"
        if a["id"]=="A37":
            details["frozen_oracle_reason"]=ORACLE[a["specimen"]]["propositions"][0]["terminal"]["reason"]; details["attacker_reason"]=p0(mutant)["terminal"]["reason"]
            if "oracle" not in caught: raise AssertionError("A37 exact frozen oracle did not detect case-substituted reason")
        attack_rows.append({"id":a["id"],"label":a["label"],"specimen":a["specimen"],"pass":True,"caught_by":sorted(caught),"expected_any":sorted(a["expected_gates"]),"details":details})
    weak=weak_controls(encoded)
    result={"schema":"contract-c-successor-candidate-a-rc1-adversarial-result-v1","classification":"Draft Research / Research Infrastructure","anchors":{"phase0":P0,"phase1":P1,"phase1_5":P15,"phase2":P2,"phase1_corpus_blob":P1_CORPUS_BLOB,"phase2_oracle_blob":P2_ORACLE_BLOB,"candidate_freeze":CANDIDATE_FREEZE,"preregistration":PREREG},"candidate_profile":C.PROFILE,"oracle_source":{"path":str(P2_PATH.relative_to(ROOT)),"mode":"direct_import","mixed_reason_exact":"MIXED_RELATIONS"},"counts":{"positive_passed":len(positive),"positive_total":19,"permutation_passed":len(perms),"permutation_total":5,"attacks_detected":len(attack_rows),"attacks_total":37,"weak_controls_sensitive":len(weak),"weak_controls_total":4},"positive":positive,"permutations":perms,"attacks":attack_rows,"weak_controls":weak,"candidate_freeze_blobs_expected":{"CANDIDATE_A_RC1.md":"0ab62b7ceea1d56d6bc3b7cf8528769dd440ab7c","candidate_a_rc1.schema.json":"0de83032e6d989225cf014d9a70035f634a5e003","candidate_a_rc1.py":"03dbb5b774af523d8e6235bca86b18af5ddad5b0"},"apparatus_failures":[],"disposition":"QUALIFIED_FOR_CAL_PRODUCER_CONFORMANCE_RESEARCH","nonclaims":["not production promotion","not SemVer assignment","not CAL producer conformance","not independent consumer conformance","not compatibility/version decision","not Contract E / Authorization","not execution authority"]}
    Path(args.out).write_text(json.dumps(result,indent=2,sort_keys=True,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result["counts"],sort_keys=True)); print(result["disposition"]); return 0

if __name__=="__main__": raise SystemExit(main())
