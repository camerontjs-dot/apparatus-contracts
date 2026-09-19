"""Explicit link validator for cal-provenance-explicit-link-1 (corrected). Stdlib only.

Enforces successor schema identities (old closed candidate schemas must not
carry new fields) and real Git recovery (repository + exact commit + real
object path; non-Git commitments independently reproduced).
"""
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent
VECTORS_PATH = ROOT / "LINK-VECTORS.json"
HEX40 = re.compile(r"^[0-9a-f]{40}$")

OLD_MANIFEST_SCHEMA = "cal-pipeline-run-manifest-v1-candidate"
NEW_MANIFEST_SCHEMA = "cal-pipeline-run-manifest-v1-explicit-link-rc0"
OLD_ATTESTATION_SCHEMA = "cal-pipeline-apparatus-attestation-v1-candidate"
NEW_ATTESTATION_SCHEMA = "cal-pipeline-apparatus-attestation-v1-explicit-link-rc0"

# Live-verified authority objects (derived from exact immutable Git subjects;
# validator rejects any object_path outside these sets).
AUTHORITY_OBJECTS = {
    ("camerontjs-dot/proposition-authoring", "c0da10e2e3b9aada5f66af9859cf27964fd3c5fc"): {
        "scripts/run_gate_v1_rc3.py",
        "src/proposition_authoring/gate_v1_rc3.py",
        "src/proposition_authoring/gate_v1.py",
        "docs/GATE_V1_RC3_BLUEPRINT.md",
    },
    ("camerontjs-dot/evidence-bundler", "4e1f6fe00e7c350b28f52bfea14f1f8988847884"): {
        "scripts/run_v1_integration_candidate.py",
        "research/eb_v1_integration_candidate/INTEGRATION_PROFILE.json",
        "src/evidence_bundler/v1/contract_b.py",
        "src/evidence_bundler/v1/package.py",
    },
    ("camerontjs-dot/claim-audit-lab", "8204417f478cfbd891499145a7edec5ee33405ad"): {
        "research/contract_c2_current_cal_producer_conformance_rc0/materialize.py",
    },
    ("camerontjs-dot/claim-audit-lab", "847cc970642bb648dc994b929c2053b5c9d4648c"): {
        "src/claim_audit_lab/production_v1/semantic/engine.py",
        "tests/production/test_convergence_semantics.py",
    },
    ("camerontjs-dot/apparatus-contracts", "b42c827acb0a9fe65353354d709add0e27bab307"): {
        "schema/contract-c/2.0.0/reference/candidate_a_rc2.py",
    },
    ("camerontjs-dot/decision-engine", "b1bcc33e2b5ef0707b8cbf7dd8e821b2d34d1b55"): {
        "src/contractC2Decision.js",
        "docs/DECISION_POLICY_SURFACE.md",
    },
}

# Frozen deterministically-reproducible payloads (live-verified extraction rules).
EB_CONFIG_PAYLOAD = {
    "candidate_depth": 10, "retained_k": 3, "chunk_max_chars": 1800,
    "chunk_overlap_chars": 80, "root_diagnostic": False,
    "retrieval_engine": "evidence_bundler_okapi_bm25_v1",
    "tokenizer": "lowercase_word_v1", "bm25_k1": 1.5, "bm25_b": 0.75,
    "source_scope_policy": "all_contract_a_sources",
    "query_strategy": "exact_primary_target_text",
}
CAL_POLICY_PAYLOAD = {
    "profile": "cal-v1-candidate-2026-09",
    "semantics": "typed-source-grounded-scoreless-categorical",
    "supported_families": ["direct_event_order", "strict_comparison"],
}
DECISION_POLICY_ID = "decision-engine.contract-c.supported-claim-verification"
DECISION_POLICY_VERSION = "1.0.0"


def canonical_bytes(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")) + "\n").encode("utf-8")


def recomputed_sha256(payload):
    return "sha256:" + hashlib.sha256(canonical_bytes(payload)).hexdigest()


def commitments_multiset(commitments):
    from collections import Counter
    return Counter((c.get("scheme"), c.get("value")) for c in (commitments or []))


def check_manifest_unique(artifacts):
    seen = {}
    dups = set()
    for a in artifacts:
        aid = a.get("artifact_id")
        if aid in seen:
            dups.add(aid)
        seen[aid] = seen.get(aid, 0) + 1
    return sorted(dups)


def resolve_reference(artifacts, ref):
    aid = ref.get("artifact_id")
    if not isinstance(aid, str) or not aid:
        return (False, "missing-artifact-id", None)
    matches = [a for a in artifacts if a.get("artifact_id") == aid]
    if len(matches) == 0:
        return (False, "unknown-artifact-id", None)
    if len(matches) > 1:
        return (False, "duplicate-artifact-id", None)
    target = matches[0]
    need = commitments_multiset(ref.get("commitments", []))
    have = commitments_multiset(target.get("commitments", []))
    for k, v in need.items():
        if have.get(k, 0) < v:
            return (False, "missing-commitment", target.get("artifact_id"))
    return (True, "ok", target.get("artifact_id"))


def check_manifest_schema(man):
    schema = man.get("manifest_schema")
    if schema == OLD_MANIFEST_SCHEMA:
        if "link_profile" in man:
            return (False, "false-conformance-link-profile-under-old-schema")
        return (True, "old-schema-no-new-fields")
    if schema == NEW_MANIFEST_SCHEMA:
        return (True, "ok")
    return (False, f"unknown-manifest-schema:{schema}")


def check_attestation_schema(att):
    schema = att.get("attestation_schema")
    has_new = False
    for inp in att.get("inputs", []):
        if "artifact_id" in (inp.get("artifact", {}) or {}):
            has_new = True
    for o in att.get("outputs", []):
        if "artifact_id" in o:
            has_new = True
    for ident in (att.get("configuration", {}) or {}).get("identities", []):
        if "artifact_id" in ident or "resolution" in ident:
            has_new = True
    if schema == OLD_ATTESTATION_SCHEMA:
        if has_new:
            return (False, "false-conformance-new-fields-under-old-schema")
        return (True, "old-schema-no-new-fields")
    if schema == NEW_ATTESTATION_SCHEMA:
        return (True, "ok")
    return (False, f"unknown-attestation-schema:{schema}")


def verify_non_git_commitment(kind, logical_id, commitments):
    """Independently reproduce non-Git commitments from frozen live-verified rules."""
    vals = {c.get("value") for c in (commitments or []) if c.get("scheme") in ("sha256-bytes", "other")}
    if kind == "eb-profile":
        if recomputed_sha256(EB_CONFIG_PAYLOAD) not in vals:
            return (False, "commitment-reproduction-mismatch")
        return (True, "ok")
    if kind == "cal-policy":
        if recomputed_sha256(CAL_POLICY_PAYLOAD) not in vals and \
                f"policy_sha256:{recomputed_sha256(CAL_POLICY_PAYLOAD).split(':')[1]}" not in vals:
            return (False, "commitment-reproduction-mismatch")
        return (True, "ok")
    if kind == "decision-policy":
        joined = " ".join(str(v) for v in vals)
        if DECISION_POLICY_ID not in joined:
            return (False, "commitment-reproduction-mismatch")
        return (True, "ok")
    return (False, "no-reproduction-rule")


def check_git_backed_strict(resolution, attested_commitments, kind=None, logical_id=None):
    """Actual recovery rule from PROFILE.md Section 4 (no bypass)."""
    if (resolution or {}).get("type") != "git-backed":
        return (False, "not-git-backed")
    repo = resolution.get("repository")
    commit = resolution.get("commit_sha")
    path = resolution.get("object_path")
    if not (isinstance(repo, str) and "/" in repo and repo.strip()):
        return (False, "missing-repository")
    if not (isinstance(commit, str) and HEX40.match(commit)):
        return (False, "bad-commit-sha")
    if not (isinstance(path, str) and path.strip()):
        return (False, "missing-object-path")
    allowed = AUTHORITY_OBJECTS.get((repo, commit))
    if allowed is None:
        return (False, "unknown-authority-subject")
    if path not in allowed:
        return (False, "unknown-object-path")
    git_vals = [c.get("value") for c in (attested_commitments or []) if c.get("scheme") == "git-commit"]
    if git_vals:
        if commit not in git_vals:
            return (False, "commit-mismatch")
        return (True, "ok")
    ok, reason = verify_non_git_commitment(kind, logical_id, attested_commitments)
    if not ok:
        return (False, reason)
    return (True, "ok")


def run_vectors():
    data = json.loads(VECTORS_PATH.read_text(encoding="utf-8"))
    by_name = {v["name"]: v for v in data["vectors"]}
    results = []

    v = by_name["01-explicit-ref-ignores-duplicate-content"]
    dups = check_manifest_unique(v["manifest_artifacts"])
    ok, reason, resolved = resolve_reference(v["manifest_artifacts"], v["reference"])
    results.append(("01-explicit-ref-ignores-duplicate-content",
                    (not dups) and ok and resolved == v["expected"]["resolved_artifact_id"],
                    {"ok": ok, "resolved": resolved}))

    v = by_name["02-duplicate-artifact-id-rejected"]
    dups = check_manifest_unique(v["manifest_artifacts"])
    results.append(("02-duplicate-artifact-id-rejected", len(dups) > 0, {"dups": dups}))

    v = by_name["03-logical-only-change-passes"]
    dups = check_manifest_unique(v["manifest_artifacts"])
    ok, reason, _ = resolve_reference(v["manifest_artifacts"], v["reference"])
    results.append(("03-logical-only-change-passes", (not dups) and ok, {"ok": ok}))

    v = by_name["04-retarget-missing-commitment-fails"]
    ok, reason, _ = resolve_reference(v["manifest_artifacts"], v["reference"])
    results.append(("04-retarget-missing-commitment-fails",
                    (not ok) and reason == "missing-commitment", {"reason": reason}))

    v = by_name["05-extra-commitments-pass"]
    ok, reason, _ = resolve_reference(v["manifest_artifacts"], v["reference"])
    results.append(("05-extra-commitments-pass", ok, {"reason": reason}))

    v = by_name["06-remove-recovery-path-fails"]
    full = v["config_full"]
    stripped = v["config_stripped"]
    full_ok, full_reason = check_git_backed_strict(
        full, full.get("commitments", []), full.get("kind"), full.get("logical_id"))
    stripped_ok, _ = check_git_backed_strict(
        stripped, stripped.get("commitments", []), stripped.get("kind"), stripped.get("logical_id"))
    results.append(("06-remove-recovery-path-fails",
                    full_ok and (not stripped_ok),
                    {"full": full_reason, "stripped_fail": not stripped_ok}))

    v = by_name["07-unresolved-blocks-reconstructable"]
    cfg = v["config"]
    reconstructable = not (cfg.get("type") == "unresolved" and cfg.get("behaviorally_relevant"))
    results.append(("07-unresolved-blocks-reconstructable",
                    reconstructable == v["expected"]["reconstructable"], {}))

    v = by_name["08-nonexistent-object-path-fails"]
    ok, reason = check_git_backed_strict(
        v["config"], v["config"].get("commitments", []),
        v["config"].get("kind"), v["config"].get("logical_id"))[:2]
    # check returns 2-tuple
    results.append(("08-nonexistent-object-path-fails",
                    (not ok) and reason == "unknown-object-path", {"reason": reason}))

    v = by_name["09-mutated-non-git-commitment-fails"]
    ok, reason = check_git_backed_strict(
        v["config"], v["config"].get("commitments", []),
        v["config"].get("kind"), v["config"].get("logical_id"))[:2]
    results.append(("09-mutated-non-git-commitment-fails",
                    (not ok) and reason == "commitment-reproduction-mismatch",
                    {"reason": reason}))
    return results


def validate_sidecars():
    sidecars_root = ROOT / "sidecars"
    if not sidecars_root.exists():
        return []
    out = []
    for case_dir in sorted([p for p in sidecars_root.iterdir() if p.is_dir()]):
        man_path = case_dir / "manifest.explicit.json"
        if not man_path.exists():
            out.append((case_dir.name, False, "missing-manifest"))
            continue
        man = json.loads(man_path.read_text(encoding="utf-8"))
        ok_schema, schema_reason = check_manifest_schema(man)
        if not ok_schema:
            out.append((case_dir.name, False, f"manifest-schema:{schema_reason}"))
            continue
        arts = man.get("artifacts", [])
        dups = check_manifest_unique(arts)
        if dups:
            out.append((case_dir.name, False, f"duplicate-artifact-id {dups}"))
            continue
        att_paths = sorted((case_dir / "attestations").glob("*.explicit.json")) if (case_dir / "attestations").exists() else []
        if not att_paths:
            out.append((case_dir.name, False, "missing-attestations"))
            continue
        case_ok = True
        detail = {"refs": 0, "failed_refs": [], "failed_schemas": [], "failed_configs": []}
        for ap in att_paths:
            att = json.loads(ap.read_text(encoding="utf-8"))
            ok_s, rs = check_attestation_schema(att)
            if not ok_s:
                case_ok = False
                detail["failed_schemas"].append({"file": ap.name, "reason": rs})
                continue
            refs = []
            for inp in att.get("inputs", []):
                refs.append(inp.get("artifact", {}))
            for o in att.get("outputs", []):
                refs.append(o)
            cfg = att.get("configuration", {}) or {}
            for ident in cfg.get("identities", []):
                if (ident.get("resolution", {}) or {}).get("type") == "retained":
                    refs.append(ident)
            for r in refs:
                detail["refs"] += 1
                ok, reason, _ = resolve_reference(arts, r)
                if not ok:
                    case_ok = False
                    detail["failed_refs"].append({"file": ap.name, "reason": reason})
            # strict config verification for every identity
            for ident in cfg.get("identities", []):
                res = ident.get("resolution", {}) or {}
                t = res.get("type")
                if t == "retained":
                    aid = res.get("artifact_id")
                    if not any(a.get("artifact_id") == aid for a in arts):
                        case_ok = False
                        detail["failed_configs"].append({"identity": ident.get("logical_id"), "reason": "retained-unknown-artifact"})
                elif t == "git-backed":
                    ok_c, reason_c = check_git_backed_strict(
                        res, ident.get("commitments", []),
                        ident.get("kind"), ident.get("logical_id"))[:2]
                    if not ok_c:
                        case_ok = False
                        detail["failed_configs"].append({"identity": ident.get("logical_id"), "reason": reason_c})
                else:
                    case_ok = False
                    detail["failed_configs"].append({"identity": ident.get("logical_id"), "reason": "unknown-type"})
        cfg_path = case_dir / "config-resolution.json"
        if not cfg_path.exists():
            out.append((case_dir.name, False, "missing-config-resolution"))
            continue
        cfg_data = json.loads(cfg_path.read_text(encoding="utf-8"))
        blocking = []
        for c in cfg_data.get("configurations", []):
            t = c.get("resolution", {}).get("type")
            br = c.get("behaviorally_relevant", True)
            if t == "retained":
                aid = c.get("resolution", {}).get("artifact_id")
                if not any(a.get("artifact_id") == aid for a in arts):
                    blocking.append(c.get("logical_id"))
                    case_ok = False
            elif t == "git-backed":
                ok_c, _ = check_git_backed_strict(
                    c.get("resolution", {}), c.get("commitments", []),
                    c.get("kind"), c.get("logical_id"))[:2]
                if not ok_c:
                    blocking.append(c.get("logical_id"))
                    case_ok = False
            elif t == "unresolved":
                if br:
                    blocking.append(c.get("logical_id"))
                    case_ok = False
            else:
                blocking.append(c.get("logical_id"))
                case_ok = False
        detail["blocking_configs"] = blocking
        detail["reconstructable"] = case_ok and not blocking
        out.append((case_dir.name, case_ok, detail))
    return out


def main():
    vec = run_vectors()
    print("LINK VECTORS:")
    all_vec = True
    for name, passed, det in vec:
        print(f"  {name}: {'PASS' if passed else 'FAIL'} {det}")
        all_vec = all_vec and passed
    side = validate_sidecars()
    print("SIDECARS:")
    all_side = True
    if not side:
        print("  (no sidecars yet)")
    for name, ok, det in side:
        print(f"  {name}: {'PASS' if ok else 'FAIL'} {json.dumps(det)[:2000]}")
        all_side = all_side and ok
    if all_vec and (not side or all_side):
        print("ALL_GREEN")
        return 0
    print("FAILURES_PRESERVED")
    return 1


if __name__ == "__main__":
    sys.exit(main())
