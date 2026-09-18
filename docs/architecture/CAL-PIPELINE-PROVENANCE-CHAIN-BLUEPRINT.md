# CAL Pipeline Provenance Chain Blueprint

**Status:** reconstruction architecture supported under CAL Provenance RC1's tested five-run aperture. The provenance schemas remain research candidates. This document is **not** a Contract A, B, C, or D promotion; it does not modify any released wire contract, semantic policy, Decision policy, Authorization surface, or execution permission.

**Canonical owner:** `camerontjs-dot/apparatus-contracts`

**Date:** 2026-09-17

**RC1 qualification update:** `SUPPORTED_PROVENANCE_RECONSTRUCTION_V1_RC1`. A fresh/context-free reconstruction consumer reported all five externally rooted RC1 run packages reconstructable: 49/49 required artifacts recovered, 60/60 commitments verified, 12/12 attestations valid, and 38/38 artifact links resolved, with zero reconstruction gaps. Terminal research receipt: `research/cal-pipeline-provenance-rc1-terminal/TERMINAL-RECONSTRUCTION-RECEIPT.md`. This qualifies reconstruction capability under the tested aperture; it does not release the candidate schemas or qualify retrieval, ClaimGate coverage, CAL semantics, Decision correctness, Authorization, or production readiness.

## 1. Problem statement

The CAL Pipeline must be reconstructable later from durable artifacts. An independent auditor should be able to determine, without relying on operator memory or producer-private runtime state:

1. what exact claim and evidence bytes entered the run;
2. what exact object each apparatus received;
3. what exact implementation, configuration, policy, resolver, or other authority the apparatus operated under;
4. what the apparatus actually did and what exact immutable artifact it produced;
5. which inputs were causal, which were authority inputs, which were compatibility-only, which were observed context, and which were diagnostics;
6. where immutable bytes can be retrieved later;
7. whether the reconstructed bytes still match their recorded content identities;
8. how the final Decision can be walked backward to the exact evidence world and original run inputs.

The missing cross-cutting primitive is a continuous provenance chain. Existing contracts already preserve substantial state and integrity at their own boundaries. The new requirement is to connect those integrity islands with producer-originated attestations and a run-level reconstruction manifest.

## 2. Core separation

The pipeline should use three distinct record types.

### 2.1 Contract

A contract states the domain object being handed across an apparatus boundary.

Examples:

- ClaimGate / EvidenceGate V1 standardization outputs;
- Contract A;
- Contract B;
- Contract C;
- Contract D.

Contracts remain narrow and retain their existing authority boundaries. They must not become generic audit logs.

### 2.2 Apparatus attestation

An attestation states what an apparatus did to exact immutable inputs under exact machinery and what exact immutable outputs it produced.

An attestation does **not** create semantic truth merely by existing. It is a reconstruction and authentication record for the apparatus action.

### 2.3 Run manifest

A run manifest is the reconstruction index for one pipeline execution. It points to every required input artifact, contract object, native apparatus artifact, attestation, and final output by immutable identity plus one or more retrievable locators.

A locator is a retrieval hint, not an authority source. Authority comes from independently trusted commitments / producer authentication plus exact content verification.

## 3. Governing invariants

### P1. Producer-originated provenance

Each apparatus records its own action at the point the output is created. Downstream components should not reconstruct producer history from filenames, logs, or inference when an originating record can be emitted directly.

### P2. Every causal arrow is content-bound

Every material input and output referenced by an attestation must carry an immutable content identity. Where the governing contract defines its own semantic/content identity, retain that identity and additionally record the exact artifact digest required for byte reconstruction.

### P3. Input role is explicit

An attestation must distinguish at least:

- `causal_input`: state actually consumed in producing the output;
- `authority_input`: independently selected authority used to verify or constrain the action;
- `compatibility_input`: compatibility/carrier state needed to satisfy a downstream contract but not promoted into upstream or semantic authority;
- `observed_context`: recorded context visible to the apparatus but not causally consumed under the qualified path;
- `diagnostic_input`: diagnostic-only state that must not alter the authoritative output.

Mere visibility is not causal authority.

### P4. Contracts do not self-authenticate their trust roots

A contract may carry its declared upstream binding, for example Contract C carrying the Contract-B bundle hash. The independently trusted expected commitment must not be selected solely from the same object under evaluation.

### P5. Hashes prove identity, not preservation

A content hash can prove that recovered bytes are the expected bytes. It cannot recover bytes that were never retained. Every artifact necessary for later reconstruction must be durably retained or reproducibly retrievable by content identity.

### P6. Failure and abstention are first-class provenance

A legitimate ClaimGate abstention, CAL `not_checkable`, Decision HOLD, apparatus failure, incomplete run, or missing downstream output must remain reconstructable as that exact state. Absence of later artifacts must not be silently interpreted as a crash or as success.

### P7. Semantic authority remains where it belongs

Provenance does not move semantic ownership:

- ClaimGate owns claim standardization / authoritative declaration behavior within its contract;
- EvidenceGate owns evidence-world standardization observations within its contract;
- Evidence Bundler owns retrieval, nomination, selection, admission, and Contract B production;
- CAL owns proposition-relative semantic/epistemic assessment;
- Decision Engine owns Decision policy application;
- Authorization remains separate.

### P8. Reconstruction must be independently checkable

A reconstruction should not require producer-private Python objects, mutable databases, hidden caches, or unverifiable descriptions. Required reconstruction state must be represented as durable finite artifacts with deterministic identities.

## 4. End-to-end blueprint

```text
                         RAW RUN INPUT
              ┌──────────────────────────────┐
              │ exact claim bytes            │
              │ exact supplied source bytes  │
              │ work/run identity            │
              └──────────────┬───────────────┘
                             │
                   content-address + archive
                             │
                    RUN ROOT / MANIFEST
                             │
             ┌───────────────┴────────────────┐
             │                                │
             ▼                                ▼
      ┌─────────────┐                  ┌──────────────┐
      │ CLAIM GATE  │                  │ EVIDENCE GATE│
      └──────┬──────┘                  └──────┬───────┘
             │                                │
             │ ClaimGate V1                   │ EvidenceGate V1
             │ output                         │ output
             │                                │
             │ claim identity                 │ evidence_world_id
             │ claim hash                     │ source IDs/hashes
             │ category                       │ source provenance
             │ authoring state                │ corpus declarations
             │ decomposition lineage          │ coverage/gaps
             │ output hash                    │ output hash
             │                                │
             └──────────────┬─────────────────┘
                            │
                 ClaimGate attestation
                 EvidenceGate attestation
                            │
                            ▼
                      CONTRACT A 2.0
               ┌───────────────────────────┐
               │ producer/work identity    │
               │ exact root proposition    │
               │ proposition hash          │
               │ decomposition state       │
               │ exact supplied sources    │
               │ source content hashes     │
               │ handoff_sha256            │
               └────────────┬──────────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │ EVIDENCE BUNDLER │
                  └────────┬─────────┘
                           │
                 retrieval / nomination
                 selection / admission
                 evidence-world assembly
                           │
                           ▼
                     CONTRACT B 1.2
               ┌───────────────────────────┐
               │ exact claims             │
               │ sources                  │
               │ passages                 │
               │ passage/source hashes    │
               │ nomination history       │
               │ admission history        │
               │ aperture observations    │
               │ factual context          │
               │ SHA256SUMS               │
               │ whole bundle hash H(B)   │
               └────────────┬──────────────┘
                            │
                    EB ATTESTATION
               ┌───────────────────────────┐
               │ consumed A hash           │
               │ observed Gate hashes      │
               │ EB implementation         │
               │ retrieval config hash     │
               │ native package hash       │
               │ compatibility inputs      │
               │ produced B ID + H(B)      │
               └────────────┬──────────────┘
                            │
                            ▼
                       ┌─────────┐
                       │   CAL   │
                       └────┬────┘
                            │
                  validate exact B
                  derive admitted context
                  semantic measurement
                  warrant/relation/composition
                            │
                            ▼
                    CONTRACT C / C2
               ┌───────────────────────────┐
               │ exact B version/ID/hash   │
               │ CAL implementation        │
               │ CAL policy identity       │
               │ proposition identity      │
               │ evidence participants     │
               │ causal basis / residuals  │
               │ execution state           │
               │ terminal epistemic state  │
               │ result identity           │
               └────────────┬──────────────┘
                            │
                    CAL ATTESTATION
               ┌───────────────────────────┐
               │ consumed exact H(B)       │
               │ CAL implementation        │
               │ policy/resolver identity  │
               │ intake/context hashes     │
               │ native CAL result hash    │
               │ produced C hash           │
               │ terminal execution state  │
               └────────────┬──────────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │   DECISION ENGINE   │
                 └──────────┬──────────┘
                            │
                 verify provenance chain
                 verify C authenticity
                 verify B commitment
                 verify C participants ∈ B
                 verify CAL/policy authority
                 resolve exact target
                 execute fixed policy
                            │
                            ▼
                     CONTRACT D 1.0
               ┌───────────────────────────┐
               │ upstream authority        │
               │ policy ID/version         │
               │ exact target identity     │
               │ CLEAR/HOLD/FAILED         │
               │ typed candidate effect    │
               │ semantic identity         │
               └────────────┬──────────────┘
                            │
                    DE ATTESTATION
               ┌───────────────────────────┐
               │ consumed C hash           │
               │ B/C authority verified    │
               │ Decision implementation   │
               │ policy implementation     │
               │ exact target              │
               │ produced D hash           │
               └────────────┬──────────────┘
                            │
                            ▼
                       RUN MANIFEST
                  complete reconstruction
```

## 5. Existing contract-required state

This section records the current contract anchors that the provenance architecture must preserve. It does not supersede the normative specifications.

### 5.1 ClaimGate V1 candidate output

Current candidate top-level fields:

- `schema`;
- `version`;
- `implementation_identity`;
- `authoring`;
- `claim`;
- `lineage`;
- `contract_a_binding`;
- `authority`;
- `output_sha256`.

Required material state includes:

- exact authoring terminal state/reason;
- exact proposition ID;
- exact claim text;
- exact claim text SHA-256;
- bounded descriptive categories;
- exact handoff / producer / producer-version / work lineage;
- decomposition state/lineage;
- exact Contract-A handoff SHA-256 when present;
- whole-output integrity.

### 5.2 EvidenceGate V1 candidate output

Current candidate top-level fields:

- `schema`;
- `version`;
- `implementation_identity`;
- `root_id`;
- `evidence_world_id`;
- `source_count`;
- `sources`;
- `corpus`;
- `authority`;
- `output_sha256`.

Required material state includes:

- content-derived evidence-world identity from exact root plus sorted source/content-hash pairs;
- exact source IDs/media types/content hashes;
- provenance observations (`origin`, `issuer`, `source_role`, `authority_basis`) with known/unknown state and basis;
- document/evidence classification with explicit basis;
- temporal/jurisdiction/version/currency coverage declarations;
- corpus verification-world/scope/completeness declarations;
- explicit known-gap tri-state;
- whole-output integrity.

EvidenceGate state remains descriptive unless separately qualified for causal use by a downstream consumer.

### 5.3 Contract A 2.0.0

The canonical Contract A 2.0.0 authority already requires:

- frozen wire schema token;
- stable `handoff_id`;
- producer identity and immutable/versioned producer identity;
- upstream `work_id`;
- exact authoritative root proposition ID/text/SHA-256;
- explicit decomposition state: `not_decomposed | failed | unknown | declared`;
- for declared decomposition: decomposition ID, `all_of`, child proposition IDs/text/hashes and sequence;
- explicit source array;
- for each supplied source: exact source ID, media type, exact content bytes, content SHA-256;
- `handoff_sha256` over the entire canonical object excluding only the hash field.

### 5.4 Contract B core + 1.2 factual-context extension

The locked Contract-B family already establishes a sealed evidence bundle with:

- stable bundle identity/version;
- upstream run/contract/corpus lineage in the legacy core;
- Evidence Builder version/config/build metadata in the legacy core;
- claims, source profiles, passages, audit configuration and validation-set references;
- bundle counts, transformations, quality gates and whole-bundle hash in the legacy core;
- exact per-file checksums through `SHA256SUMS`;
- in Contract B 1.2 factual context: claim origin/atomicity state;
- provenance-bound source context facts;
- passage representation anchors;
- complete nomination/admission/review history for the represented evidence world;
- derived count checks;
- aperture observations;
- explicit known/unknown representation;
- extension inclusion in the bundle-tree hash and exact `SHA256SUMS` binding.

`history_complete: true` means the preparation ledger is complete for that evidence world. It does **not** mean the corpus/search universe is complete.

### 5.5 Contract C 1.0.0

Canonical Contract C 1.0.0 carries:

- `contract_c_version`;
- exact Contract-B version / bundle ID / bundle hash;
- exact CAL semantic implementation identity;
- behaviorally relevant CAL policy hash and canonical payload;
- result-set execution state;
- proposition-bound result records;
- exact proposition ID / text hash;
- retained contribution IDs/channels/exact B evidence refs;
- optional typed measurement and its basis contribution IDs;
- explicit assessment-stage states;
- proposition execution and epistemic completion state;
- reported verdict / terminal branch / causal form / basis members / residuals / rule roles;
- content-derived `result_set_id`;
- separate expected external whole-object SHA-256 at the handoff boundary.

### 5.6 Contract C2 research successor used by the first genuine run

The current C2 research profile used by the integration path has top-level:

- `profile`;
- `result_set_id`;
- `contract_b`;
- `producer`;
- `execution`;
- `propositions`.

Material C2 bindings include:

- exact B `contract_version`, `bundle_id`, `bundle_hash`;
- producer `semantic_implementation_sha`, `policy_sha256`, `policy_resolver_commit_sha`;
- proposition `proposition_id`, `content_sha256`;
- execution state/completion;
- terminal verdict/reason;
- participants with exact source/passage refs plus relation/role;
- minimal basis groups.

The canonical C2 verifier can additionally verify exact B participant references, independent policy-resolver authority, and an external whole-object digest when supplied independently.

### 5.7 Contract D 1.0.0

Contract D already requires:

- `contract_d_version`;
- exact `input_authority.kind`, logical `id`, immutable `immutable_id`;
- exact Decision `policy.id` and `policy.version`;
- exact target `kind`, logical `id`, immutable `content_sha256`;
- evaluation state and, when completed, `clear | hold`;
- registered typed/versioned effect and normalized parameters for completed decisions;
- optional non-authoritative metadata;
- content-derived Decision semantic identity under the Contract-D canonicalization rules.

Contract D remains upstream of operational Authorization and does not establish execution permission.

## 6. Proposed generic apparatus attestation v1

This is the proposed cross-cutting record. It is not yet a released contract.

### 6.1 Required top-level fields

Every attestation MUST contain exactly these conceptual families. A later schema qualification may choose exact names, but none of these categories should be silently omitted.

```json
{
  "attestation_schema": "cal-pipeline-apparatus-attestation-v1",
  "attestation_id": "attestation:sha256:<...>",
  "stage": {},
  "producer": {},
  "run": {},
  "inputs": [],
  "authorities": [],
  "configuration": {},
  "operation": {},
  "outputs": [],
  "execution": {},
  "retention": {},
  "authentication": {},
  "created_at_utc": "..."
}
```

`attestation_id` SHOULD be content-derived over the canonical attestation excluding only `attestation_id` itself.

### 6.2 `stage`

Required fields:

- `stage_id`: stable pipeline stage name;
- `apparatus_kind`: e.g. `claim_gate`, `evidence_gate`, `evidence_bundler`, `claim_audit_lab`, `decision_engine`;
- `stage_sequence`: stable ordinal or dependency position within the run;
- `attempt_id`: identity distinguishing retries/replays while retaining the same run.

### 6.3 `producer`

Required fields:

- `system_id`;
- `component_version` if a released/package version exists, else explicit null/unknown;
- `implementation_id` as an immutable implementation identity;
- `implementation_kind`: e.g. `git_commit`, `release_artifact`, `content_digest`;
- `repository` when Git-backed, else explicit null;
- `runtime_profile` or explicit null if no distinct runtime profile exists.

The implementation identity MUST be immutable and sufficient to distinguish behaviorally different machinery.

### 6.4 `run`

Required fields:

- `run_id`;
- `work_id`;
- `root_claim_id`;
- `parent_run_id` or explicit null;
- `replay_of_attestation_id` or explicit null.

The same `run_id` must be propagated through the complete pipeline reconstruction even when individual contracts use their own object IDs.

### 6.5 `inputs[]`

Each material input row MUST contain:

- `role`: one of `causal_input | compatibility_input | observed_context | diagnostic_input`;
- `kind`;
- logical `id`;
- immutable `sha256` of the exact artifact bytes or governing canonical bytes;
- governing `version` / profile where applicable;
- `semantic_identity` / contract identity when the object defines one, else explicit null;
- `producer_attestation_id` when known, else explicit null;
- `locator_refs`: zero or more locator IDs from `retention`; absence means identity is known but retrieval is not presently available.

Every input used to produce the authoritative output must be listed. Visibility alone does not imply causal use.

### 6.6 `authorities[]`

Each independently selected authority input MUST contain:

- `authority_kind`;
- `authority_id`;
- immutable `authority_digest` or immutable commit/release identity;
- `selection_basis`: how this authority was selected independently of the candidate object;
- `scope`: what the authority is allowed to establish;
- locator/reference if required for reconstruction.

Examples:

- exact Contract validator authority;
- producer-policy resolver authority;
- expected upstream artifact commitment;
- trusted producer key/profile when cryptographic producer signing is later introduced.

Caller-controlled values must not masquerade as independent authorities.

### 6.7 `configuration`

Required fields:

- `configuration_id` or explicit null;
- `configuration_sha256` over exact behaviorally relevant configuration bytes;
- `configuration_version` or explicit null;
- `configuration_artifact_ref` if the exact bytes are separately retained, else explicit null;
- `defaults_materialized`: boolean indicating whether all behaviorally relevant defaults are represented in the hashed configuration.

Any configuration difference capable of changing authoritative output should change the configuration identity.

### 6.8 `operation`

Required fields:

- `operation_id`: stable operation name;
- `operation_version`;
- `declared_scope`: concise machine/human-readable scope of what the apparatus claims to have done;
- `nonclaims`: explicit bounded list of what the operation does not establish.

This prevents a receipt for “retrieval completed” from being read later as “evidence completeness established.”

### 6.9 `outputs[]`

Each authoritative or reconstruction-required output MUST contain:

- `role`: `authoritative_output | reconstruction_artifact | diagnostic_output`;
- `kind`;
- logical `id`;
- exact `sha256`;
- governing version/profile;
- semantic/content identity if distinct from byte digest;
- retention locator refs;
- `required_for_reconstruction`: boolean.

Native apparatus artifacts that are needed to explain or reproduce the stage must be retained even when they are not downstream contracts.

### 6.10 `execution`

Required fields:

- `state`: `completed | abstained | failed | incomplete`;
- `terminal_reason`: stable reason code or explicit null;
- `started_at_utc`;
- `completed_at_utc` or explicit null;
- `exit_code` or explicit null where not meaningful;
- `deterministic_replay_status`: `not_run | equal | different | not_applicable`;
- `replay_attestation_id` or explicit null.

A semantic `not_checkable` within a completed CAL result is not an apparatus failure. That distinction remains in the contract plus execution fields.

### 6.11 `retention`

Required fields:

- `retention_state`: `retained | partially_retained | identity_only | unavailable`;
- `locators[]`.

Each locator row SHOULD contain:

- stable locator ID;
- locator kind (`content_addressed_store`, `git`, `github_artifact`, `filesystem`, `object_store`, other governed kind);
- locator value;
- expected SHA-256;
- privacy/access classification;
- durability class / expiry if known;
- whether the locator is authoritative for retrieval only or also independently authenticated.

A locator is never sufficient proof that retrieved bytes are correct. Recovered bytes must be rehashed.

### 6.12 `authentication`

Required fields:

- `mode`: initially one of `pipeline_manifest_commitment | producer_signature | trusted_store_record | none_research_only`;
- `authenticator_id` or explicit null;
- `authentication_material_ref` or explicit null;
- `authentication_scope`;
- `verified`: boolean at time of receipt creation where meaningful.

A first local V1 may use a trusted pipeline manifest/store rather than PKI. Signatures are a portability option, not an automatic requirement.

## 7. Proposed stage-specific attestation obligations

### 7.1 ClaimGate attestation

Must bind:

- raw claim artifact digest;
- exact ClaimGate implementation identity;
- ClaimGate V1 output digest;
- exact terminal authoring state/reason;
- Contract A digest if emitted;
- decomposition lineage state;
- any authority input that established authoring/decomposition;
- no Contract A output when abstained/failed, represented explicitly rather than omitted ambiguously.

### 7.2 EvidenceGate attestation

Must bind:

- exact supplied source artifact digests;
- exact EvidenceGate implementation identity;
- `evidence_world_id`;
- EvidenceGate V1 output digest;
- corpus declaration/gap state identity;
- explicit statement that the output is descriptive standardization and not retrieval or semantic authority unless separately qualified.

### 7.3 Evidence Bundler attestation

Must bind at minimum:

- exact Contract A hash as `causal_input`;
- any EvidenceGate object as `observed_context` unless particular fields have separately qualified causal use;
- exact EB implementation identity;
- exact retrieval configuration hash;
- exact native EB package identity/hash;
- exact query/retrieval/aperture identity carried by the native package;
- exact compatibility carrier digest as `compatibility_input` where required for Contract B;
- exact Contract B version/bundle ID/bundle hash;
- exact B tree / `SHA256SUMS` verification outcome;
- terminal retrieval/admission execution state;
- all reconstruction-required native receipts/artifacts.

The EB attestation is the natural producer-originated commitment for Contract B.

### 7.4 CAL attestation

Must bind at minimum:

- exact Contract B artifact commitment as `causal_input`;
- B validation / checksum result;
- exact admitted semantic-context identity/hash derived from B;
- exact CAL implementation identity;
- exact policy identity/hash;
- exact resolver/producer-authority identity when required by the current Contract C profile;
- exact native CAL result digest;
- exact Contract C/C2 object digest and its internal result identity;
- terminal CAL execution state;
- semantic outcome class (`assessed`, `not_checkable`, failure/incomplete) without reinterpreting it;
- reconstruction-required trace/receipt identities, while preserving the boundary against producer-private reasoning that is not part of the public epistemic record.

### 7.5 Decision Engine attestation

Must bind at minimum:

- exact Contract C/C2 digest as `causal_input`;
- expected upstream B commitment as independent `authority_input` when participant authority must be checked;
- exact B artifact digest used to reconstruct/verify participant membership;
- exact Contract C authority / validator identity;
- exact CAL resolver/producer authority identity;
- exact Decision Engine implementation identity;
- exact Decision policy implementation/id/version;
- exact resolved target identity;
- outcome of provenance/authority verification before policy evaluation;
- exact Contract D object digest and semantic identity;
- completed CLEAR/HOLD or failed evaluation state;
- no Authorization claim.

## 8. Proposed run manifest v1

A run manifest is required for a run that claims later reconstruction.

### 8.1 Required top-level fields

```json
{
  "manifest_schema": "cal-pipeline-run-manifest-v1",
  "manifest_id": "run-manifest:sha256:<...>",
  "run_id": "...",
  "work_id": "...",
  "root_inputs": [],
  "stages": [],
  "artifacts": [],
  "attestations": [],
  "authorities": [],
  "terminal": {},
  "reconstruction": {},
  "created_at_utc": "..."
}
```

### 8.2 `root_inputs[]`

Must identify:

- raw claim artifact;
- every supplied source/evidence artifact needed to reconstruct the initial evidence world;
- exact hashes;
- retention locators;
- privacy/access classification.

### 8.3 `stages[]`

For every stage, record:

- stage ID;
- attempt ID;
- attestation ID;
- predecessor stage IDs;
- exact terminal state;
- whether downstream execution occurred;
- if not, stable stop reason.

### 8.4 `artifacts[]`

Must enumerate every artifact required to reconstruct the run, including:

- Gate outputs;
- Contract A;
- EB native package;
- Contract B raw bundle;
- compatibility carriers that materially affected B construction;
- CAL intake/semantic-context reconstruction artifact or deterministic derivation identity;
- CAL native result;
- Contract C/C2;
- Decision target artifact if separate;
- Contract D;
- every stage attestation;
- exact governing validator/policy/resolver/config artifacts when not recoverable from immutable release/Git identities.

Each artifact row must carry logical ID, type, exact digest, required/optional reconstruction status, producer attestation and locators.

### 8.5 `authorities[]`

Must pin independently selected authority roots used across the run, such as:

- Contract A validator/release authority;
- Contract B validator/release authority;
- Contract C validator/release/profile authority;
- CAL producer-policy resolver authority;
- Contract D authority;
- producer authentication/trust roots when later introduced.

### 8.6 `terminal`

Must state:

- overall run terminal state;
- last completed authoritative stage;
- exact final output artifact if any;
- whether Authorization was attempted;
- whether execution was attempted;
- explicit promotion/release/production-authorization flags for research runs where relevant.

### 8.7 `reconstruction`

Must state:

- `reconstructable`: true/false/partial;
- missing required artifact identities;
- missing locators;
- expired locators;
- integrity checks performed;
- replay status if performed;
- reconstruction procedure/version.

## 9. Reconstruction walkback requirement

Starting from a final Contract D, a conforming audit package should permit this backward walk:

```text
Contract D
  -> DE attestation
  -> exact C/C2
  -> CAL attestation
  -> exact B
  -> EB attestation
  -> exact A + gate outputs
  -> original claim + original source bytes
```

At every arrow the auditor must be able to answer:

- which exact immutable object was consumed;
- whether recovered bytes match the expected digest;
- which producer attested to the object/action;
- which independent authority established the applicable validator/policy/trust root;
- whether the object played a causal, authority, compatibility, observed-context, or diagnostic role;
- whether the next artifact is the exact artifact originally produced.

## 10. First genuine pipeline run: observed issues and provenance impact

Frozen first-genuine record: `FIRST-GENUINE-B-SIDE-001`.

Observed end-to-end path:

- Evidence Bundler returned nine candidate relationships;
- three were retained;
- one passage was accepted/admitted;
- Contract-B integrity checks passed;
- CAL admitted one passage but returned `not_checkable` with `MEASUREMENT_MISS` / `UNRESOLVED`;
- Contract C2 completed `not_checkable / no_deciding_relation`;
- Decision Engine produced completed `hold`;
- primary and replay C2/D objects were byte- and hash-identical;
- no Authorization was inferred.

### 10.1 A/EB -> Contract B compatibility carrier

Observed issue: the EB V1 native package plus Contract A did not by themselves supply every legacy scalar/metadata field required by locked Contract B. The integration candidate therefore used an explicit compatibility carrier.

Provenance benefit:

- records Contract A as authoritative upstream claim/source input;
- records native EB package as retrieval/admission authority;
- records the compatibility carrier separately as `compatibility_input`;
- prevents compatibility state from being mistaken later for Contract-A authority, retrieval evidence, or CAL semantic authority.

Provenance does **not** prove the compatibility values are semantically appropriate. That remains a separate contract/conformance question.

### 10.2 CAL -> Contract C2 producer-authority blocker

Observed blocker before the genuine run: current CAL advertised semantic implementation `847cc970...`, while the then-authoritative resolver contained only an older CAL implementation mapping. Pipeline pressure stopped at `BLOCKED_AT_CAL_TO_CONTRACT_C2_PRODUCER_AUTHORITY` until producer conformance/resolver authority was addressed.

Provenance benefit:

- makes the exact CAL implementation, policy and resolver dependency explicit in the CAL attestation;
- makes a producer-authority mismatch diagnosable as an authority-chain break rather than generic downstream failure;
- preserves which exact producer mapping was used for any historical C object.

Provenance does **not** authorize a new CAL implementation. Independent conformance remains required.

### 10.3 Contract C2 -> Decision Engine authority aperture

Post-run pressure showed that validator-valid, coherently resealed C2 substitutions could reach the current Decision policy when participant and producer authority were not independently reconstructed. Canonical C2 verification rejected them when exact B-world and resolver authority inputs were held independently fixed.

Provenance benefit:

- EB attestation supplies an independently authenticated commitment to exact B;
- CAL attestation supplies exact C producer identity;
- DE can rehash presented B bytes against the independently selected B commitment;
- participant authority can be derived from verified B rather than caller-supplied indexes;
- policy/resolver authority can be independently pinned.

Research subsequently supported the narrower mechanism `trusted B commitment + presented raw B bytes -> recompute bundle commitment -> derive participant authority`, eliminating the need to trust artifact location itself for integrity.

### 10.4 Portable receipt lacked raw artifacts

The public first-genuine portable receipt deliberately records hashes/component commits/counts/disposition while omitting raw source passage, raw packets, execution logs, local paths and private runtime state.

Provenance benefit:

- a run manifest can retain privacy-safe content identities publicly while separately recording governed locators to private/raw artifacts;
- an auditor with appropriate access can recover the bytes and verify them against the public/portable commitments;
- raw artifacts need not be copied into every receipt.

Important boundary: if required bytes are not retained anywhere, the hash alone cannot reconstruct them.

### 10.5 CAL `MEASUREMENT_MISS`

The first semantic divergence in the genuine run was CAL `not_checkable / MEASUREMENT_MISS / UNRESOLVED`.

Provenance benefit:

- proves which exact B bundle and admitted passage CAL actually saw;
- proves which CAL implementation/policy/resolver produced the miss;
- distinguishes “CAL saw the evidence and could not establish a deciding relation” from “the evidence never reached CAL.”

Provenance does **not** change the semantic result and must not be used to manufacture support/refutation.

### 10.6 Bounded 10/3 retrieval

The genuine run used the frozen EB V1 integration profile with bounded candidate depth/retention.

Provenance benefit:

- preserves exact retrieval configuration and native package identity;
- preserves candidates, rank/selection/admission history and aperture observations;
- prevents later readers from treating the one admitted passage as proof of complete evidence discovery.

Provenance does **not** establish retrieval recall or corpus completeness.

### 10.7 Replay equality

Primary/replay C2 and D outputs were byte/hash equal.

Provenance benefit:

- upgrades replay evidence from “two outputs happened to match” toward reconstructable reproduction using exact input/config/authority identities;
- allows later independent replay to verify whether the same machinery and same inputs regenerate the same result.

Replay equality still does not establish semantic correctness.

### 10.8 Legitimate negative stops at the front door

ClaimGate testing already demonstrated legitimate abstention stops in which downstream pipeline stages never run.

Provenance benefit:

- records an explicit `abstained` stage outcome, reason and exact input claim;
- records that Contract A was not produced;
- permits the run manifest to mark downstream stages `not_run_due_to_upstream_stop` rather than leaving ambiguous missing artifacts.

## 11. Security / trust interpretation

The provenance chain is not secure merely because every object hashes itself.

The tested Decision Engine research established the following distinction:

```text
trusted expected commitment + presented bytes -> meaningful verification
caller-selected expected commitment + caller-presented bytes -> circular and unsafe
```

Therefore:

- expected commitments/trust roots must be selected independently of the object under evaluation;
- producer signatures, if adopted, require independently configured trusted keys;
- a trusted run controller/store may be sufficient for an initial local V1 without introducing PKI;
- signatures are attractive for cross-system portability but do not themselves establish semantic truth;
- mutable APIs/databases require explicit version/freshness/revocation semantics before they can serve as reconstructable authority.

## 12. Storage model

Recommended logical storage model:

```text
run/<run_id>/
  RUN-MANIFEST.json
  inputs/
  gates/
  contract-a/
  evidence-bundler/
    native/
    contract-b/
    ATTESTATION.json
  cal/
    intake/
    native-result/
    contract-c/
    ATTESTATION.json
  decision-engine/
    contract-d/
    ATTESTATION.json
  authorities/
```

This is a logical reconstruction package, not a required physical filesystem layout. A content-addressed store or object store may physically hold the bytes while the run manifest maps identities to locations.

## 13. Implementation order

Do not widen every contract at once.

Recommended sequence:

1. freeze this architecture as a cross-repo design requirement;
2. define and qualify the generic `ApparatusAttestation` schema against existing frozen artifacts;
3. define and qualify `RunManifest` reconstruction on the existing first-genuine run;
4. require complete retention of all artifacts needed to reconstruct that run;
5. make ClaimGate/EvidenceGate emit attestations without changing their current contract bytes;
6. make Evidence Bundler emit B attestation plus native-package/config/compatibility bindings;
7. make CAL emit B-consumption/C-production attestation;
8. make Decision Engine consume independently trusted B/C commitments and emit D attestation;
9. run an independent clean-room reconstruction from only the run manifest, retained artifacts and pinned authorities;
10. only then decide whether any released contract itself needs a schema addition.

## 14. Primary falsifiers

This architecture should be considered insufficient if any of the following are demonstrated:

1. a downstream result cannot be reconstructed because a material input was not retained or identified;
2. two materially different runs can produce the same claimed provenance identity;
3. an apparatus can omit a behaviorally relevant configuration change without changing its attestation identity;
4. caller-controlled data can select the trust root used to validate itself;
5. `observed_context` or `compatibility_input` silently changes authoritative output without being reclassified as causal input;
6. a stage can substitute a different upstream artifact while preserving the same accepted lineage;
7. an auditor cannot distinguish semantic `not_checkable`, apparatus failure, abstention, and downstream non-execution;
8. the run manifest requires mutable producer-private state to explain a historical output;
9. the attestation layer starts reinterpreting Contract A/B/C/D semantic meaning rather than recording apparatus action;
10. provenance storage becomes a competing source of contract truth rather than a content-addressed reconstruction index.

## 15. Current disposition

`SUPPORTED_PROVENANCE_RECONSTRUCTION_V1_RC1`

RC0 established that the candidate architecture discriminates retained/reconstructable runs from commitment-only historical records and that a self-hashed manifest cannot serve as its own trust root.

RC1 then exercised five heterogeneous run shapes with externally frozen expected manifest commitments and a fresh/context-free reconstruction consumer. The reported independent reconstruction recovered 49/49 required artifacts, verified 60/60 commitments, validated 12/12 attestations, resolved 38/38 artifact links, and found zero reconstruction gaps.

Therefore, the architecture's reconstruction capability is supported under the tested RC1 aperture.

This does **not** convert the candidate attestation or run-manifest schemas into released contracts. It does not qualify Evidence Bundler retrieval recall, ClaimGate coverage, CAL semantic correctness, Decision correctness, Authorization, production readiness, merge, release, or promotion.

Next work should be bounded to schema-normalization review, standard apparatus instrumentation without semantic-output change, and additional fresh complete downstream runs rather than repeating the already-passed reconstruction question.
