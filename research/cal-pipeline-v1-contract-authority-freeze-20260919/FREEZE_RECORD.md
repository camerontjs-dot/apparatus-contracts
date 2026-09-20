# CAL Pipeline V1 Apparatus Contracts Authority Freeze

Date: 2026-09-19

Classification: integration evidence / authority-slice freeze. Documentation only. This record does not change Contract A/B/C/D semantics, validators, schemas, fixtures, release identities, Contract E research, Authorization, execution, or production behavior.

Terminal local-slice status:

`QUALIFIED_FOR_LOCAL_PIPELINE_CONTRACT_AUTHORITY`

## Decision

Use one exact `apparatus-contracts` snapshot as the local CAL Pipeline contract-authority checkout for the already released surfaces:

```text
Contract A 2.0.0
    ->
Contract B 1.2.0
    ->
Contract C 1.0.0
    ->
Contract D 1.0.0
```

Contract E is deliberately excluded because no canonical production Contract E / authority control plane exists.

This is an authority slice, not a new contract release and not a new apparatus runtime.

## Governing conventions

This freeze applies two current Apparatus governance records:

- issue #100: freeze only state the current apparatus uniquely owns and a legitimate downstream consumer must be able to verify;
- Draft PR #111, head `7661748d5110b1cb00e5f4c0d8d007c9b7519a39`: reuse already-qualified production surfaces rather than rebuilding a new slice for symmetry; keep contracts separate; stop at a contract-sufficiency failure; keep Contract E research-only until its authority model converges.

PR #111 remains proposed Draft governance. This freeze uses it as the requested promotion-design convention; it does not treat the PR as merged contract authority.

## Frozen consolidated carrier

Repository:

`camerontjs-dot/apparatus-contracts`

Maintained production base / frozen carrier:

`c3563cff66d2c85dcbf575c693056e2d8e4563d4`

This commit is not a new compatibility version. It is a later repository snapshot that contains all four canonical released contract surfaces.

Machine-readable pointer manifest:

`research/cal-pipeline-v1-contract-authority-freeze-20260919/SLICE_MANIFEST.json`

## Released authority set

### Contract A 2.0.0

- immutable tag: `contract-a-v2.0.0`
- exact release commit: `529c92b49a34d5c610618551a8737f019f9fa332`
- production promotion merge: `b59c2fbe38bae78a3a35699362c0e67d17152e4b`
- canonical spec: `contract-a-v2.0.0.md`
- wire spec: `schema/contract-a/2.0.0/wire-spec.md`
- schema: `schema/contract-a/2.0.0/schema.json`
- canonical validator entry point: `validators/contract_a.py`
- frozen validation engine: `validators/contract_a_rc2.py`

Contract A freezes upstream producer/work identity, exact proposition/decomposition/source representation authority, and whole-object integrity. It does not own trust, retrieval, CAL, Decision, Authorization, or execution semantics.

### Contract B 1.2.0

- immutable tag: `contract-b-v1.2.0`
- exact production-lock/release commit: `c314e53bd91c0736aa4370a364673b069aceb43e`
- release-identity control-plane completion: `5056559dcff170bc7f7c71d4736eb32f8eeef019`
- canonical extension spec: `contract-b-factual-context-extension-v1.2.0.md`
- validator: `validators/contract_b_factual_context.py`
- integrity verifier: `validators/verify_contract_integrity.py`
- decisive pre-merge acceptance run: `33115839918`
- post-merge production lock run: `33116096988`
- acceptance artifact digest: `sha256:888eeae4e02bac724a234bb18bc3b50c0419e502cb650b7bf6e22b8e10933054`

Contract B freezes evidence-world facts/history/aperture and provenance-bound preparation state without acquiring proposition-specific CAL semantic authority.

### Contract C 1.0.0

- immutable tag: `contract-c-v1.0.0`
- exact release commit: `5fe55f9ed5d0ee9f026ca1b077e9d70ce0487ea1`
- production promotion merge: `b804958be9da841b7fb1541b0535767a933a2769`
- canonical spec: `contract-c-v1.0.0.md`
- schema: `schema/contract-c/1.0.0/schema.json`
- validator: `validators/contract_c.py`
- frozen canonical fixture SHA-256: `7a66583e332be4901d13ba9f2d7e12419938c77a41b83223a4b0946ad529b7a1`

Contract C freezes CAL-attributable result state and exact Contract-B/CAL/policy binding. It does not grant Decision policy or operational authority.

### Contract D 1.0.0

- immutable tag: `contract-d-v1.0.0`
- exact release commit: `298a1a0f7b7b6d7712e11200d04faec3e1ca169b`
- production promotion merge: `68d0cd82def0faaadd3ad5410fb40ec68675b8bd`
- canonical spec: `contract-d-v1.0.0.md`
- schema: `schema/contract-d/1.0.0/schema.json`
- effect registry: `schema/contract-d/1.0.0/effect-registry.json`
- validators: `validators/contract_d_core.py`, `validators/contract_d_validate.py`, `validators/contract_d_consume.py`

Contract D freezes exact upstream authority, Decision policy, target identity, evaluation state, typed normalized effect, and semantic Decision identity. Its strongest positive outcome is still only `candidate_for_authorization`.

## Consolidated-snapshot equivalence check

The important question was whether current `main` can be used as one local checkout without silently replacing a released authority.

I compared 22 behaviorally relevant spec/schema/registry/validator/version blobs on current `main` against their exact release commits:

- Contract A: 6/6 identical
- Contract B: 5/5 identical
- Contract C: 4/4 identical
- Contract D: 7/7 identical

Total:

`22 / 22 exact Git-blob identities preserved`

This check includes the primary canonical specs, schemas, validator surfaces, version registries/markers, and Contract D effect registry.

Observed: the checked normative authority bytes on `c3563cff...` are the same bytes carried by the exact A2/B1.2/C1/D1 release subjects.

Inference: `c3563cff...` is a suitable consolidated local authority checkout for those four released contract surfaces. No research branch needs to be copied into the local pipeline merely to assemble the contract layer.

This does not claim that every non-normative repository file is byte-identical to every earlier release tree.

## Local pipeline use

The local runner should pin this exact consolidated checkout, then use only the canonical released authority paths listed in `SLICE_MANIFEST.json`.

The runner should preserve at minimum:

- exact apparatus-contracts commit;
- exact contract version and immutable release tag/commit for each boundary exercised;
- exact validator/schema identity used;
- exact input artifact bytes/hash;
- validator result and controlled failure result;
- the first cross-boundary divergence.

Do not infer a contract from the current neighboring producer's populated object shape.

## Live C1 boundary

The authority slice includes canonical Contract C 1.0.0 because it is a real released contract.

That does **not** establish that the current richer CAL V1 local candidate can always be represented losslessly by C1.

Current CAL Slice 1 deliberately did not promote Contract C redesign or decomposition orchestration. The frozen Decision Engine local slice is also qualified only for exact Contract C 1.0.0.

Therefore the pipeline rule is:

1. use C1 only when the exact CAL result is authoritatively representable under C1;
2. never relabel a richer successor object as C1;
3. never discard parent/decomposition state merely to make Decision reachable;
4. if the CAL output requires state C1 cannot carry, preserve that as a Contract-C sufficiency stop and end the production route there.

That stop is evidence. It is not a reason to smuggle the missing state through producer-private fields or an adapter.

## Contract E exclusion

Contract E remains research-only. Open Contract E candidates, currentness/delegation work, ERS shadow-consumer experiments, and authority-control-plane research are excluded from this slice.

No Contract D result in this slice is execution permission.

## What this establishes

Observed:

- A2, B1.2, C1, and D1 are canonical released contract surfaces;
- their exact release identities are preserved;
- all 22 checked normative blobs are unchanged in the pinned consolidated snapshot;
- the released surfaces already have producer/consumer, independent-consumer, adversarial, or cross-repository evidence appropriate to their individual release histories.

Supported inference:

- one exact `apparatus-contracts@c3563cff...` checkout is the smallest justified contract-authority slice for staged local CAL Pipeline runs using released A2/B1.2/C1/D1 semantics.

## What this does not establish

This freeze does not establish:

- end-to-end compatibility of the current CAL V1 candidate through Contract C 1.0.0;
- a Contract C successor;
- Contract E / Authorization semantics;
- source legitimacy, corpus completeness, CAL semantic correctness, or Decision policy correctness outside each released contract's tested bounds;
- that open research branches are production authority;
- any new version, tag, release, merge, or production semantic change.

## Requalification triggers

Requalify this local authority slice if:

1. any canonical A/B/C/D version changes;
2. any pinned normative blob differs from the exact release authority;
3. richer CAL state requires a different Contract C authority;
4. Contract E or another Authorization surface becomes canonical;
5. a local pipeline run requires capability available only on an open research branch.

## Disposition

`QUALIFIED_FOR_LOCAL_PIPELINE_CONTRACT_AUTHORITY`

The next evidence should come from the real local CAL Pipeline consuming these exact authorities alongside the frozen Claim/Evidence Gate, Evidence Bundler, CAL, and Decision Engine slices.

No merge, tag, release, version bump, Contract E promotion, or Authorization change is justified by this freeze.
