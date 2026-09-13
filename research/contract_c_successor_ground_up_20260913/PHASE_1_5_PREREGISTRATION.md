# Contract C successor Phase 1.5 preregistration

**Classification:** Draft Research / Research Infrastructure.

**Frozen parents:** Phase 0 obligation matrix `e588e1295367a4b867d608342aaacaccb41850b8`; Phase 1 semantic corpus `175246ae16932f2f34a399560d7f76013213bf97`. Neither frozen file is modified by this phase.

**Exact CAL semantic authority under test:** frozen CAL V1 RC1 commit `a902621e8baea3063dddd7f92ba975aade305464`, engine blob `636734fd1341d2ae721ae9697c7ac7652b89eecc`, relation blob `e9e9401c92ee11d25a50dbc36e80aeb4c4cd220d`, projection blob `9bc152275759304be03b84014c56bd434549a64a`.

## Metamorphic specimens

Use only the existing RC1 `audit()` semantic machinery. Do not patch CAL or the old exporter.

- **M1 / SP-04:** two independently sufficient strict-comparison refutations. Required observations: full `{R1,R2}` contradicted; either singleton contradicted; empty not contradicted. If so, oracle `MSC={{R1},{R2}}` is materialized.
- **M2 / SP-11:** one support plus two alternative refutations. Required observations: full and each `{S1,Ri}` are `NOT_CHECKABLE / MIXED_RELATIONS`; `{R1,R2}` is not that mixed result; `{S1}` is not mixed. If so, oracle `MSC={{S1,R1},{S1,R2}}` is materialized.
- **M3 / SP-10:** preserve CAL #106 without exporter repair. Full `{S1,S2,R1}` and each `{Si,R1}` remain mixed, while support-only/refute-only controls do not. Oracle remains `MSC={{S1,R1},{S2,R1}}` and the old flat exporter remains falsified.
- **M4 / SP-12:** no producer claim is made. Keep `(S1 OR S2) AND (R1 OR R2)` representation-stress-only in this phase.

## Five discriminators

### D1 generic assessment slots

Run legitimate support, refutation, mixed and unresolved RC1 results through the existing research projection and test whether all four generic slots vary. Separately test whether terminal state/reason, exact retained participation, causal/residual role, and exact producer/policy identity preserve the distinctions exercised by current legitimate consumers. If no slot varies and no current consumer question requires it, classify each slot `ABLATE_FOR_CURRENT_SUCCESSOR_SCOPE`.

### D2 public rule/state causal members

Inspect legitimate RC1 outputs for any non-evidence causal member or normative public rule/state role. Compare an evidence-only public reconstruction with a hypothetical reconstruction that adds a typed rule/state member. A private branch name, opaque `state:<id>`, helper-local rule ID, or producer trace is not sufficient. If no required distinction is lost, classify public rule/state causal members `ABLATE_FOR_CURRENT_SUCCESSOR_SCOPE` with an explicit future reconsideration trigger.

### D3 full policy payload

Compare per-result full canonical policy payload against exact CAL implementation identity + policy digest + a deterministic immutable resolver keyed only by exact implementation identity. Resolver lookup must reject unknown producer IDs and wrong policy digests and must not use mutable `latest`, a human config name, or network ambiguity. If exact policy bytes are recovered and verified, classify the repeated in-band full payload redundant while retaining the digest and resolver obligation.

### D4 repeated passage hash

Use exact Contract-B world binding `(contract_version,bundle_id,bundle_hash)` plus `(source_id,passage_id)` resolution. Exercise same-ID passage mutation, different-world replay, stale bundle hash, and coherent reseal/tamper. If every mutation is already rejected or becomes a different exact B world before a Contract-C-local passage hash is consulted, classify repeated `passage_sha256` redundant. Exact B-world binding is not weakened.

### D5 separate contribution ID

Use direct canonical participant identity from exact B world + proposition binding + `(source_id,passage_id)` and exercise duplicate detection, causal/residual partition, canonical ordering, and basis membership. Also test whether RC1 can legitimately emit more than one trace/contribution for the same exact admitted passage to the same proposition. If not, classify a separate contribution ID not justified in current scope and record semantic multiplicity from one passage as a future evolution trigger.

## Stop rule

Freeze exact inputs, outputs, discriminator dispositions, apparatus failures and unresolved questions in a successor record before any Candidate A or Candidate B implementation is committed. No production mutation, version assignment, release, promotion, Decision policy change, Contract E change, Authorization, or independent-reproduction claim is permitted.