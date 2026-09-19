# Configuration resolution map — explicit link successor

All current Fresh Full-Chain RC0 config identities verified against exact frozen authorities before retained-artifact creation. No new retained configuration artifacts required.

| Identity | Commitment | Authority / Producer | Recovery path | Verdict |
|---|---|---|---|---|
| `gate-implementation/run_gate_v1_rc3` | `git-commit c0da10e2e3b9aada5f66af9859cf27964fd3c5fc` | `camerontjs-dot/proposition-authoring@c0da…` + producer exact | `camerontjs-dot/proposition-authoring @ c0da10e2…`, object `GATE-V1-implementation` | RECOVERABLE |
| `eb-implementation/evidence-bundler-v1` | `git-commit 4e1f6fe00e7c350b28f52bfea14f1f8988847884` | `camerontjs-dot/evidence-bundler@4e1f…` + producer exact | `camerontjs-dot/evidence-bundler @ 4e1f6fe0…`, object `research/eb_v1_integration_candidate` | RECOVERABLE |
| `eb-profile/eb-v1-integration-10x3-rc0` | `sha256:5b10d0c29794e80d6876a99e26bcf6ec6a27a4c5165aee78054a6bc32759f4bc` | `camerontjs-dot/evidence-bundler @ 4e1f6fe0…` | path `research/eb_v1_integration_candidate/INTEGRATION_PROFILE.json`, field `config_sha256` equals attested value | RECOVERABLE Git-backed |
| `cal-policy/cal-rules-v1.2.0` | `other policy_sha256:44ecc335…` | `camerontjs-dot/claim-audit-lab @ 8204417f…` (producer) | path `research/contract_c2_current_cal_producer_conformance_rc0/materialize.py`, constant `POLICY_SHA256` | RECOVERABLE Git-backed |
| `cal-semantic/cal-v1-integration-candidate-v1` | `git-commit 847cc970…` | authority `claim-audit-lab semantic implementation` | `camerontjs-dot/claim-audit-lab @ 847cc970…`, object `src/claim_audit_lab/production_v1/semantic/engine.py` tree present | RECOVERABLE Git-backed (explicit path required; bare commit insufficient) |
| `c2-profile/contract-c-successor-candidate-a-rc2-research` | `git-commit b42c827…` | authority `apparatus-contracts C2 authority` | `camerontjs-dot/apparatus-contracts @ b42c827…`, path `schema/contract-c/2.0.0/reference/candidate_a_rc2.py` | RECOVERABLE Git-backed |
| `decision-policy/decision-engine.contract-c.supported-claim-verification@1.0.0` | `other policy:…` | `camerontjs-dot/decision-engine @ b1bcc33e…` (producer) | path `docs/DECISION_POLICY_SURFACE.md`, Policy 1 ID + version `1.0.0` | RECOVERABLE Git-backed |

Unresolved remains a valid typed outcome but blocks `reconstructable`. No behaviorally relevant unresolved remains in sidecars: all 8 (4 in declared-all-of) resolve Git-backed with full repo/commit/path. EB aliases preserved as pressure cases and resolve via explicit `artifact_id` + subset rule.
