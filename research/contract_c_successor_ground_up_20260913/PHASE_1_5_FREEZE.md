# Contract C successor Phase 1.5 freeze

**Classification:** Draft Research / Research Infrastructure.

This is an explicit successor record to the frozen Phase 0 obligation matrix at `e588e1295367a4b867d608342aaacaccb41850b8` and Phase 1 semantic corpus at `175246ae16932f2f34a399560d7f76013213bf97`. Those records are not rewritten. Where this record changes an `UNRESOLVED` Phase 0 disposition, the change is bounded to the current successor scope and is supported by the discriminating evidence below.

## Exact authority and execution

- Apparatus protected base remains `c3563cff66d2c85dcbf575c693056e2d8e4563d4`.
- CAL V1 RC1 semantic commit: `a902621e8baea3063dddd7f92ba975aade305464`.
- CAL engine blob: `636734fd1341d2ae721ae9697c7ac7652b89eecc`.
- CAL relation blob: `e9e9401c92ee11d25a50dbc36e80aeb4c4cd220d`.
- CAL frozen research projection blob, used only to preserve the #106 exporter falsifier and inspect current surface behavior: `9bc152275759304be03b84014c56bd434549a64a`.
- Preregistration commit: `ef1b5e21a1dc7e50744c726b3acadf31ce027b7d`.
- Immutable research policy resolver fixture commit: `43b571464734325277374ee81098553fb7c1b944`.
- Evaluator commit: `296e4abfb0fedd5be4833f0bebae52e0f0877da7`.
- Executed workflow head: `f540520d624bff40dda83848e6938848a15de36e`.
- GitHub Actions run: `34760312906`; job: `103731882252`; conclusion: `success`.
- Result artifact: `10318119402`; artifact ZIP digest: `sha256:f30df1aba0bec6190f010b672841de41f810adddfb0c2da4c31cbd0e9af7df52`.
- Preserved result file commit: `a79962255b6b6568c84ba163c8bcc6f23275676a`.
- Preserved `PHASE_1_5_RESULT.json` SHA-256: `e00f18a478284012fa442c39932faa533135d007334082839e89d533e90e6ee0`.

## Exact metamorphic inputs

All specimens use the qualified RC1 `STRICT_COMPARISON` proposition `Women had a higher rate than Men.` with `lhs_entity=Women`, `rhs_entity=Men`, and `comparison_direction=MORE_THAN`. The exact passage texts are:

- `S1`: `Women had a higher rate than Men.`
- `S2`: `Women had a greater rate than Men.`
- `R1` / `R2`: `Women had a lower rate than Men.` supplied as distinct admitted passages with distinct source identities.

No CAL semantic code was changed to manufacture these states.

### M1 / SP-04: two independently sufficient refutations

Observed ablations:

- `{R1,R2}` -> `contradicted`, relations `[REFUTES, REFUTES]`;
- `{R1}` -> `contradicted`;
- `{R2}` -> `contradicted`;
- empty -> `not_checkable / RELATION_UNRESOLVED`.

**Materialized oracle:** `MSC={{R1},{R2}}`.

### M2 / SP-11: symmetric alternative-joint mixed

Observed ablations:

- `{S1,R1,R2}` -> `not_checkable / MIXED_RELATIONS`;
- `{S1,R1}` -> `not_checkable / MIXED_RELATIONS`;
- `{S1,R2}` -> `not_checkable / MIXED_RELATIONS`;
- `{R1,R2}` -> `contradicted`, not the mixed result;
- `{S1}` -> `supported`, not mixed.

**Materialized oracle:** `MSC={{S1,R1},{S1,R2}}`.

### M3 / SP-10: preserve CAL #106

Observed ablations:

- `{S1,S2,R1}` -> `not_checkable / MIXED_RELATIONS`;
- `{S1,R1}` -> mixed;
- `{S2,R1}` -> mixed;
- `{S1,S2}` -> supported;
- `{R1}` -> contradicted.

**Materialized oracle:** `MSC={{S1,R1},{S2,R1}}`.

The old frozen projection still emits `jointly_sufficient` with all three members for the full case. Therefore CAL #106 remains a positive semantic specimen for this programme and a falsifier of the old flat exporter. The exporter was not patched or rewritten.

### M4 / SP-12

`(S1 OR S2) AND (R1 OR R2)` remains **`REPRESENTATION_STRESS_ONLY`**. Phase 1.5 makes no claim that current qualified CAL emits that exact state.

## Discriminator outcomes and explicit Phase 0 supersession

### D1: generic assessment slots

Legitimate current RC1 support, refutation, mixed, and unresolved results were projected. All four slots remained `state=not_performed`; no slot varied. Removing those slots from the reconstruction model preserved the tested distinctions using execution state, terminal verdict/reason, exact retained participation, causal structure, and exact producer/policy identity. No current legitimate consumer requirement was found that exercises a distinct generic-slot state.

Current-successor dispositions:

- `eligibility` -> **`ABLATE_FOR_CURRENT_SUCCESSOR_SCOPE`**;
- `semantic_validity` -> **`ABLATE_FOR_CURRENT_SUCCESSOR_SCOPE`**;
- `aperture_completeness` -> **`ABLATE_FOR_CURRENT_SUCCESSOR_SCOPE`**;
- `temporal_applicability` -> **`ABLATE_FOR_CURRENT_SUCCESSOR_SCOPE`**.

This does not assert that such state can never return in a later Contract C version. Reconsider if a legitimate producer varies one of these public states and a legitimate consumer cannot reconstruct the required distinction from the retained successor semantics.

### D2: public rule/state causal members

Across legitimate current RC1 support, refutation, mixed, and unresolved results, the only observed causal basis namespace was evidence contribution participation and `rule_roles` remained empty. Current Decision research evidence also does not require a separate public rule/state member. An opaque implementation branch, helper-local ID, or `state:<id>` is not accepted as normative public state.

Current-successor disposition: **`ABLATE_FOR_CURRENT_SUCCESSOR_SCOPE`** for a separate public rule/state causal-member surface. No normative public rule/state meaning survives this discriminator.

Reconsider only if a future legitimate producer result contains a typed non-evidence cause whose public meaning is required for reconstruction and is not recoverable from exact producer/policy identity, stable terminal reason, and evidence-level causal structure.

### D3: full policy payload

The exact current policy digest is `44ecc33519fa8911079595d322f5f0decbf0389af42e153ac32214931798e42c`. A frozen deterministic resolver keyed by exact CAL semantic implementation identity recovered the exact behaviorally relevant canonical policy and verified the digest. Wrong policy digest and unknown producer identity both failed closed. The experiment used no mutable `latest`, human config-name interpretation, or network lookup.

Current-successor disposition: **ablate the complete canonical policy payload from each Contract C result, while retaining exact immutable CAL implementation identity, exact policy digest, and a normatively bound immutable/deterministic policy resolution mechanism**.

The resolver fixture in this PR is research infrastructure, not a production release registry. A later production successor must define the authoritative immutable resolution mechanism before release.

### D4: repeated passage hash

The exact Contract-B binding `(contract_version, bundle_id, bundle_hash)` plus `(source_id, passage_id)` was tested against:

- same-ID passage mutation;
- different-world replay;
- stale bundle hash;
- coherently resealed/tampered B world presented under the old Contract C binding.

All mutations were rejected or became a different exact B world before any Contract-C-local passage hash was consulted. Historical exact-B index evidence remains anchored by blob `4de40713482a1fc5a075a230a61e19acc25afbd9`.

Current-successor disposition: **`ABLATE_REPEATED_PASSAGE_SHA256_RETAIN_EXACT_B_WORLD_BINDING`**.

This does not weaken Contract-B integrity or exact-world binding. It removes only the duplicate passage hash from Contract C.

### D5: separate contribution ID

A direct canonical participant identity over exact B-world binding + exact proposition binding + `(source_id, passage_id)` supported:

- complete and non-overlapping causal/residual partitioning;
- duplicate detection;
- deterministic canonical ordering;
- direct causal-basis membership.

The exact RC1 engine emits one passage trace per exact admitted passage, and the exact evidence-world verifier rejects duplicate passage IDs. The current qualified producer therefore did **not** demonstrate two semantically distinct public contributions from the same exact passage to the same proposition.

Current-successor disposition: **`ABLATE_SEPARATE_CONTRIBUTION_ID_FOR_CURRENT_SUCCESSOR_SCOPE`**.

Reconsider if a future qualified CAL producer legitimately emits multiple semantically distinct public contributions from the same exact passage to the same proposition. If that occurs, introduce the smallest semantic contribution identity needed; do not confuse evidence identity, semantic contribution identity, and causal-basis membership identity.

## Phase 1.5 disposition

**`SUPPORTED_PHASE_1_5_FREEZE_READY`**.

- M1, M2, M3 passed; M4 remains a bounded nonclaim.
- D1 through D5 resolved under the current successor scope.
- `apparatus_failures=[]`.
- `unresolved_questions=[]`.
- No genuinely normative unresolved choice blocks the representation bake-off.

Phase 2 may therefore proceed from this freeze using the exact same frozen abstract semantic specimens. The Phase 1 `MSC` notation remains an evaluator oracle only and is not selected as the wire representation by this record.

## Nonclaims and boundary

This freeze does not mutate released Contract C 1.0, assign a successor version, promote or release anything, change CAL production semantics, change Decision Engine production policy, touch Contract E or Authorization, authorize execution, or claim independent reproduction.