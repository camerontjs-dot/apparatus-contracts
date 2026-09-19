# CAL Provenance Explicit Link Profile 1

**Profile ID:** `cal-provenance-explicit-link-1`

**Status:** Draft Research, stacked on digest-profile head `43f65ccfa70fb3d42aa4c6974e1ace472d7508a2`. Does not release or modify `research/provenance-chain-v1-candidate` schemas. Does not normalize existing EB aliases. Does not authorize production use.

**Base:** candidate schemas at `1a5929295e735e351320cbd8c966dc43afed2859` plus digest profile `cal-provenance-canonical-json-bounded-1` for identity derivation. This profile adds link and configuration-resolution rules only.

## 1. Explicit artifact references

For research sidecars, every attestation artifact reference in `inputs[].artifact`, `outputs[]`, and retained-type `configuration.identities[]` MUST contain `artifact_id` naming a manifest `artifactEntry`.

- `artifact_id` is the link authority.
- `kind` and `logical_id` remain inspectable metadata; mismatch does not break a resolved link.
- Existing EB aliases (`contract-b-compatibility-carrier` vs `compatibility-carrier`, `contract-b` vs `contract-b-snapshot`, `contract-b.snapshot.zip` label reuse) are preserved as pressure cases and MUST still resolve via explicit `artifact_id`.

## 2. Manifest uniqueness

Manifest `artifact_id` values MUST be unique. Duplicate `artifact_id` is rejected regardless of content equality.

Duplicate content under a different `artifact_id` MUST NOT confuse an explicit reference: resolution follows the named `artifact_id` only.

## 3. Commitment subset rule

Let R be the reference commitment set and T the resolved manifest artifact commitment set, each as multisets of `(scheme,value)`.

- Every commitment in R MUST exist in T (R ⊆ T).
- T MAY carry additional commitments (e.g. manifest `contract-b-snapshot` carries `sha256-bytes` plus `contract-b-bundle-hash` while the attestation ref asserts only `sha256-bytes`).
- Retargeting `artifact_id` to an artifact missing any asserted commitment FAILS.
- Additional valid commitments on T do NOT break the link.

Full-set equality is explicitly NOT required.

## 4. Typed configuration resolution

Every behaviorally relevant configuration identity MUST resolve as one of:

- `retained`: names a manifest `artifact_id` via Section 1–3 rules;
- `git-backed`: provides `repository`, `commit_sha`, plus `object_path` and either `embedded_digest_field` or `file_sha256` sufficient to recover the exact governing bytes without private convention. A bare label or unexplained commit alone is INSUFFICIENT;
- `unresolved`: no recoverable bytes demonstrated.

Verified Git-backed recoveries for Fresh Full-Chain RC0 (exact authorities inspected before retained-artifact creation):

- `gate-implementation/run_gate_v1_rc3 git c0da10e2…` → `camerontjs-dot/proposition-authoring @ c0da10e2e3b9aada5f66af9859cf27964fd3c5fc` (authority + producer exact)
- `eb-implementation/evidence-bundler-v1 git 4e1f6fe0…` → `camerontjs-dot/evidence-bundler @ 4e1f6fe00e7c350b28f52bfea14f1f8988847884` (authority + producer exact)
- `eb-profile/eb-v1-integration-10x3-rc0 sha256 5b10d0c2…` → `camerontjs-dot/evidence-bundler @ 4e1f6fe0…` path `research/eb_v1_integration_candidate/INTEGRATION_PROFILE.json` field `config_sha256` equals attested value
- `cal-policy/cal-rules-v1.2.0 other policy_sha256:44ecc3…` → `camerontjs-dot/claim-audit-lab @ 8204417f478cfbd891499145a7edec5ee33405ad` path `research/contract_c2_current_cal_producer_conformance_rc0/materialize.py` constant `POLICY_SHA256`
- `cal-semantic/cal-v1-integration-candidate-v1 git 847cc970…` → `camerontjs-dot/claim-audit-lab @ 847cc970642bb648dc994b929c2053b5c9d4648c` authority `claim-audit-lab semantic implementation`, object `src/claim_audit_lab/production_v1/semantic/engine.py` tree present at that commit
- `c2-profile/contract-c-successor-candidate-a-rc2-research git b42c827…` → `camerontjs-dot/apparatus-contracts @ b42c827acb0a9fe65353354d709add0e27bab307` path `schema/contract-c/2.0.0/reference/candidate_a_rc2.py` present at that commit
- `decision-policy/decision-engine.contract-c.supported-claim-verification@1.0.0 other policy:…` → `camerontjs-dot/decision-engine @ b1bcc33e2b5ef0707b8cbf7dd8e821b2d34d1b55` path `docs/DECISION_POLICY_SURFACE.md` Policy 1 `decision-engine.contract-c.supported-claim-verification` version `1.0.0`

No new retained configuration artifacts were required: all current config identities are Git-backed recoverable with explicit paths. `unresolved` remains a valid typed outcome but is behaviorally blocking per Section 5.

## 5. Reconstructable

`reconstructable` requires:

- every required manifest artifact resolves via Sections 1–3;
- every behaviorally relevant configuration resolves as `retained` or `git-backed` with complete recovery information;
- any behaviorally relevant `unresolved` configuration PREVENTS `reconstructable` (must report `partial` or `not_reconstructable`, never `reconstructable`).

Removing an immutable configuration recovery path while keeping its semantic label FAILS reconstruction.

## 6. Nonclaims

This profile does not change digest preimages, repair run packages, normalize aliases, release schemas, or authorize production. It defines link authority and configuration typing for research sidecars only.
