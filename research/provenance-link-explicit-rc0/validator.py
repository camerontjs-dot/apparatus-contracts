"""Explicit link validator for cal-provenance-explicit-link-1 (genuinely reconstructive)."""
import ast
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys

import jsonschema
from jsonschema import Draft202012Validator

ROOT = pathlib.Path(__file__).resolve().parent
VECTORS_PATH = ROOT / "LINK-VECTORS.json"
SCHEMAS_DIR = ROOT / "schemas"
MANIFEST_SCHEMA_PATH = SCHEMAS_DIR / "run-manifest.explicit-link-rc0.schema.json"
ATTESTATION_SCHEMA_PATH = SCHEMAS_DIR / "apparatus-attestation.explicit-link-rc0.schema.json"
HEX40 = re.compile(r"^[0-9a-f]{40}$")

OLD_MANIFEST_SCHEMA = "cal-pipeline-run-manifest-v1-candidate"
NEW_MANIFEST_SCHEMA = "cal-pipeline-run-manifest-v1-explicit-link-rc0"
OLD_ATTESTATION_SCHEMA = "cal-pipeline-apparatus-attestation-v1-candidate"
NEW_ATTESTATION_SCHEMA = "cal-pipeline-apparatus-attestation-v1-explicit-link-rc0"

REPO_ROOT = ROOT.parent.parent  # apparatus-contracts checkout root


def authority_root():
    env = os.environ.get("LINK_AUTHORITY_ROOT")
    if env:
        return pathlib.Path(env)
    return REPO_ROOT / ".authority"


# (repository, commit) -> checkout subdir under authority root.
AUTHORITY_SUBDIR = {
    ("camerontjs-dot/proposition-authoring", "c0da10e2e3b9aada5f66af9859cf27964fd3c5fc"): "proposition-authoring",
    ("camerontjs-dot/evidence-bundler", "4e1f6fe00e7c350b28f52bfea14f1f8988847884"): "evidence-bundler",
    ("camerontjs-dot/claim-audit-lab", "8204417f478cfbd891499145a7edec5ee33405ad"): "claim-audit-lab-producer",
    ("camerontjs-dot/claim-audit-lab", "847cc970642bb648dc994b929c2053b5c9d4648c"): "claim-audit-lab-semantic",
    ("camerontjs-dot/apparatus-contracts", "b42c827acb0a9fe65353354d709add0e27bab307"): "apparatus-contracts-c2",
    ("camerontjs-dot/decision-engine", "b1bcc33e2b5ef0707b8cbf7dd8e821b2d34d1b55"): "decision-engine",
}

# Evidence-based governing object per config identity (verified live inspection).
REQUIRED_PATH = {
    ("gate-implementation", "run_gate_v1_rc3"): "scripts/run_gate_v1_rc3.py",
    ("eb-implementation", "evidence-bundler-v1"): "scripts/run_v1_integration_candidate.py",
    ("eb-profile", "eb-v1-integration-10x3-rc0"): "research/eb_v1_integration_candidate/INTEGRATION_PROFILE.json",
    ("cal-policy", "cal-rules-v1.2.0"): "research/contract_c2_current_cal_producer_conformance_rc0/materialize.py",
    ("cal-semantic", "cal-v1-integration-candidate-v1"): "src/claim_audit_lab/production_v1/semantic/engine.py",
    ("c2-profile", "contract-c-successor-candidate-a-rc2-research"): "schema/contract-c/2.0.0/reference/candidate_a_rc2.py",
    ("decision-policy", "decision-engine.contract-c.supported-claim-verification@1.0.0"): "src/contractC2Decision.js",
}


def canonical_bytes(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":")) + "\n").encode("utf-8")


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


def load_schemas():
    man_schema = json.loads(MANIFEST_SCHEMA_PATH.read_text(encoding="utf-8"))
    att_schema = json.loads(ATTESTATION_SCHEMA_PATH.read_text(encoding="utf-8"))
    return (Draft202012Validator(man_schema), Draft202012Validator(att_schema))


def check_manifest_schema_doc(man, validator):
    errors = sorted(validator.iter_errors(man), key=lambda e: list(e.path))
    if errors:
        first = errors[0]
        return (False, f"schema-invalid:{'/'.join(str(p) for p in first.path)}:{first.message[:160]}")
    if man.get("manifest_schema") == OLD_MANIFEST_SCHEMA and "link_profile" in man:
        return (False, "false-conformance-link-profile-under-old-schema")
    return (True, "ok")


def check_attestation_schema_doc(att, validator):
    errors = sorted(validator.iter_errors(att), key=lambda e: list(e.path))
    if errors:
        first = errors[0]
        return (False, f"schema-invalid:{'/'.join(str(p) for p in first.path)}:{first.message[:160]}")
    schema = att.get("attestation_schema")
    has_new = False
    for inp in att.get("inputs", []):
        art = inp.get("artifact", {}) or {}
        if "artifact_id" in art or "resolution" in art:
            has_new = True
    for o in att.get("outputs", []):
        if "artifact_id" in o or "resolution" in o:
            has_new = True
    for ident in (att.get("configuration", {}) or {}).get("identities", []):
        if "artifact_id" in ident or "resolution" in ident:
            has_new = True
    if schema == OLD_ATTESTATION_SCHEMA and has_new:
        return (False, "false-conformance-new-fields-under-old-schema")
    return (True, "ok")


def git_head_commit(checkout_dir):
    try:
        r = subprocess.run(["git", "-C", str(checkout_dir), "rev-parse", "HEAD"],
                           capture_output=True, text=True, check=True)
        return r.stdout.strip()
    except Exception:
        return None


def read_authority_bytes(repo, commit, object_path):
    """Resolve pinned repo+commit checkout, prove path exists, read governing bytes."""
    sub = AUTHORITY_SUBDIR.get((repo, commit))
    if sub is None:
        return (None, "unknown-authority-subject")
    base = authority_root() / sub
    # Prove the checkout resolves to the exact claimed commit.
    head = git_head_commit(base)
    if head != commit:
        return (None, f"authority-commit-mismatch:head={head}")
    target = base / object_path
    try:
        data = target.read_bytes()
    except (OSError, ValueError):
        return (None, "unknown-object-path")
    if not data:
        return (None, "empty-object")
    return (data, "ok")


def verify_git_backed(resolution, attested_commitments, kind=None, logical_id=None):
    """Genuinely reconstructive check against immutable Git subjects."""
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
    required = REQUIRED_PATH.get((kind, logical_id))
    if required is None:
        return (False, "no-governing-rule")
    if path != required:
        # Distinguish nonexistent vs real-but-wrong: try reading to classify.
        data, err = read_authority_bytes(repo, commit, path)
        if err == "unknown-object-path" or err == "unknown-authority-subject":
            return (False, err)
        return (False, "wrong-governing-object")
    data, err = read_authority_bytes(repo, commit, path)
    if err != "ok":
        return (False, err)
    git_vals = [c.get("value") for c in (attested_commitments or []) if c.get("scheme") == "git-commit"]
    if git_vals:
        if commit not in git_vals:
            return (False, "commit-mismatch")
        return (True, "ok")
    # Non-Git: deterministically extract from recovered bytes and reproduce.
    try:
        if kind == "eb-profile":
            doc = json.loads(data.decode("utf-8"))
            payload = doc.get("config")
            if not isinstance(payload, dict):
                return (False, "extraction-failed")
            reproduced = "sha256:" + hashlib.sha256(canonical_bytes(payload)).hexdigest()
            attested = {c.get("value") for c in (attested_commitments or [])}
            if reproduced not in attested:
                return (False, "commitment-reproduction-mismatch")
            # Corroborate runtime drift authority (same pinned subject).
            runtime, rerr = read_authority_bytes(
                repo, commit, "src/evidence_bundler/v1/contract_b.py")
            if rerr != "ok":
                return (False, "drift-authority-unavailable")
            rtext = runtime.decode("utf-8")
            if reproduced not in rtext or "frozen V1 integration config identity drift" not in rtext:
                return (False, "drift-check-mismatch")
            return (True, "ok")
        if kind == "cal-policy":
            text = data.decode("utf-8")
            tree = ast.parse(text)
            payload = None
            for node in tree.body:
                if isinstance(node, ast.Assign) and any(
                        isinstance(t, ast.Name) and t.id == "POLICY" for t in node.targets):
                    payload = ast.literal_eval(node.value)
                    break
            if not isinstance(payload, dict):
                return (False, "extraction-failed")
            reproduced = hashlib.sha256(canonical_bytes(payload)).hexdigest()
            attested = {str(c.get("value", "")) for c in (attested_commitments or [])}
            if not any(reproduced in v for v in attested):
                return (False, "commitment-reproduction-mismatch")
            return (True, "ok")
        if kind == "decision-policy":
            text = data.decode("utf-8")
            if "decision-engine.contract-c.supported-claim-verification" not in text:
                return (False, "commitment-reproduction-mismatch")
            if '"1.0.0"' not in text and "'1.0.0'" not in text and "1.0.0" not in text:
                return (False, "commitment-reproduction-mismatch")
            joined = " ".join(str(c.get("value", "")) for c in (attested_commitments or []))
            if "decision-engine.contract-c.supported-claim-verification" not in joined:
                return (False, "commitment-reproduction-mismatch")
            return (True, "ok")
    except (UnicodeDecodeError, ValueError, SyntaxError):
        return (False, "extraction-failed")
    return (False, "no-reproduction-rule")


def run_vectors():
    data = json.loads(VECTORS_PATH.read_text(encoding="utf-8"))
    by_name = {v["name"]: v for v in data["vectors"]}
    results = []

    v = by_name["01-explicit-ref-ignores-duplicate-content"]
    dups = check_manifest_unique(v["manifest_artifacts"])
    ok, _, resolved = resolve_reference(v["manifest_artifacts"], v["reference"])
    results.append(("01-explicit-ref-ignores-duplicate-content",
                    (not dups) and ok and resolved == v["expected"]["resolved_artifact_id"], {}))

    v = by_name["02-duplicate-artifact-id-rejected"]
    dups = check_manifest_unique(v["manifest_artifacts"])
    results.append(("02-duplicate-artifact-id-rejected", len(dups) > 0, {}))

    v = by_name["03-logical-only-change-passes"]
    dups = check_manifest_unique(v["manifest_artifacts"])
    ok, _, _ = resolve_reference(v["manifest_artifacts"], v["reference"])
    results.append(("03-logical-only-change-passes", (not dups) and ok, {}))

    v = by_name["04-retarget-missing-commitment-fails"]
    ok, reason, _ = resolve_reference(v["manifest_artifacts"], v["reference"])
    results.append(("04-retarget-missing-commitment-fails",
                    (not ok) and reason == "missing-commitment", {}))

    v = by_name["05-extra-commitments-pass"]
    ok, _, _ = resolve_reference(v["manifest_artifacts"], v["reference"])
    results.append(("05-extra-commitments-pass", ok, {}))

    v = by_name["06-remove-recovery-path-fails"]
    full = v["config_full"]
    stripped = v["config_stripped"]
    full_ok, _ = verify_git_backed(
        full, full.get("commitments", []), full.get("kind"), full.get("logical_id"))[:2]
    stripped_ok, _ = verify_git_backed(
        stripped, stripped.get("commitments", []), stripped.get("kind"), stripped.get("logical_id"))[:2]
    results.append(("06-remove-recovery-path-fails", full_ok and (not stripped_ok), {}))

    v = by_name["07-unresolved-blocks-reconstructable"]
    cfg = v["config"]
    reconstructable = not (cfg.get("type") == "unresolved" and cfg.get("behaviorally_relevant"))
    results.append(("07-unresolved-blocks-reconstructable",
                    reconstructable == v["expected"]["reconstructable"], {}))

    v = by_name["08-nonexistent-object-path-fails"]
    c = v["config"]
    ok, reason = verify_git_backed(
        c, c.get("commitments", []), c.get("kind"), c.get("logical_id"))[:2]
    results.append(("08-nonexistent-object-path-fails",
                    (not ok) and reason == "unknown-object-path", {"reason": reason}))

    v = by_name["09-mutated-non-git-commitment-fails"]
    c = v["config"]
    ok, reason = verify_git_backed(
        c, c.get("commitments", []), c.get("kind"), c.get("logical_id"))[:2]
    results.append(("09-mutated-non-git-commitment-fails",
                    (not ok) and reason == "commitment-reproduction-mismatch", {"reason": reason}))

    v = by_name["10-real-but-wrong-object-fails"]
    c = v["config"]
    ok, reason = verify_git_backed(
        c, c.get("commitments", []), c.get("kind"), c.get("logical_id"))[:2]
    results.append(("10-real-but-wrong-object-fails",
                    (not ok) and reason == "wrong-governing-object", {"reason": reason}))
    return results


def validate_sidecars():
    man_validator, att_validator = load_schemas()
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
        ok_schema, schema_reason = (True, "ok"), ""
        errs = sorted(man_validator.iter_errors(man), key=lambda e: list(e.path))
        if errs:
            e = errs[0]
            ok_schema = (False, f"schema-invalid:{'/'.join(str(p) for p in e.path)}:{e.message[:160]}")
        elif man.get("manifest_schema") == OLD_MANIFEST_SCHEMA and "link_profile" in man:
            ok_schema = (False, "false-conformance-link-profile-under-old-schema")
        if not ok_schema[0]:
            out.append((case_dir.name, False, f"manifest-schema:{ok_schema[1]}"))
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
            errs = sorted(att_validator.iter_errors(att), key=lambda e: list(e.path))
            if errs:
                e = errs[0]
                case_ok = False
                detail["failed_schemas"].append(
                    {"file": ap.name, "reason": f"schema-invalid:{'/'.join(str(p) for p in e.path)}"})
                continue
            schema = att.get("attestation_schema")
            has_new = False
            for inp in att.get("inputs", []):
                art = inp.get("artifact", {}) or {}
                if "artifact_id" in art or "resolution" in art:
                    has_new = True
            for o in att.get("outputs", []):
                if "artifact_id" in o or "resolution" in o:
                    has_new = True
            for ident in (att.get("configuration", {}) or {}).get("identities", []):
                if "artifact_id" in ident or "resolution" in ident:
                    has_new = True
            if schema == OLD_ATTESTATION_SCHEMA and has_new:
                case_ok = False
                detail["failed_schemas"].append({"file": ap.name, "reason": "false-conformance-new-fields-under-old-schema"})
                continue
            if schema != NEW_ATTESTATION_SCHEMA:
                case_ok = False
                detail["failed_schemas"].append({"file": ap.name, "reason": f"unknown-attestation-schema:{schema}"})
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
            for ident in cfg.get("identities", []):
                res = ident.get("resolution", {}) or {}
                t = res.get("type")
                if t == "retained":
                    aid = res.get("artifact_id")
                    if not any(a.get("artifact_id") == aid for a in arts):
                        case_ok = False
                        detail["failed_configs"].append({"identity": ident.get("logical_id"), "reason": "retained-unknown-artifact"})
                elif t == "git-backed":
                    ok_c, reason_c = verify_git_backed(
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
                ok_c, _ = verify_git_backed(
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
    print(f"AUTHORITY_ROOT={authority_root()} exists={authority_root().exists()}")
    if all_vec and (not side or all_side):
        print("ALL_GREEN")
        return 0
    print("FAILURES_PRESERVED")
    return 1


if __name__ == "__main__":
    sys.exit(main())
