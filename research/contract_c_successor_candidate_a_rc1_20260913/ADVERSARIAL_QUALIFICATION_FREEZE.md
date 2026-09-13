# Contract C successor Candidate A RC1 adversarial qualification freeze

**Classification:** Draft Research / Research Infrastructure.

This record freezes the qualification of exact Candidate A RC1 and explicitly supersedes the RC0 terminal disposition without modifying or deleting RC0 evidence.

## Exact lineage

- protected Apparatus production base observed at programme reconciliation: `c3563cff66d2c85dcbf575c693056e2d8e4563d4`;
- Phase 0 obligation freeze: `e588e1295367a4b867d608342aaacaccb41850b8`;
- Phase 1 semantic-corpus freeze: `175246ae16932f2f34a399560d7f76013213bf97`;
- Phase 1.5 discriminator freeze: `163d0d424777ef3c0a3b45dec2888c845634205d`;
- Phase 2 representation freeze: `f5337dedaad045aa290e80f69dc83ac1a0f73436`;
- RC0 exact freeze: `9f1808c47503c884887dbf862e9cd8162b21b583`;
- RC0 post-qualification falsifier: `a0ddca1f1301a5d3dc11104b4fd1f6944f9967f6`;
- exact RC1 candidate freeze: `ba5f55b0fb6ca54e0461a688813b66fd81bf8c4c`;
- RC1 adversarial preregistration: `55b0fc12c7b884556e2d0d4dc7811665301326df`;
- RC1 evaluator commit: `0bca118695eff88a7e5c3f86f3bcca2f85afd96b`;
- executed RC1 workflow head: `4ab8db03968862a1eb9b79fcb4b1ca9de9b3ee0c`.

## Why RC1 exists

The independent post-RC0 audit found that the frozen Phase 1/2 programme preserves `MIXED_RELATIONS` as an exact stable public terminal reason while RC0 and its copied evaluator table both used lowercase `mixed_relations`. That falsified RC0 and exposed a qualification-apparatus independence failure.

RC1 did not reopen the Phase 2 representation architecture. It made the smallest successor repair:

1. preserve exact `MIXED_RELATIONS` and reject lowercase substitution;
2. require the qualification workflow to verify the exact inherited Phase 1/2 oracle blobs;
3. require the evaluator to consume the frozen Phase 2 oracle directly rather than duplicate its terminal semantics.

## Frozen authority and candidate checks

Before executing the cohort, GitHub Actions verified:

- Phase 1 corpus blob `0ff4f66bca00924755d42ed7f944c4dae8d10f66`;
- Phase 2 oracle blob `9f00cd332ad366b878f60d13440af639360928de`;
- `CANDIDATE_A_RC1.md` blob `0ab62b7ceea1d56d6bc3b7cf8528769dd440ab7c`;
- `candidate_a_rc1.schema.json` blob `0de83032e6d989225cf014d9a70035f634a5e003`;
- `candidate_a_rc1.py` blob `03dbb5b774af523d8e6235bca86b18af5ddad5b0`.

The decisive evaluator imported `research/contract_c_successor_ground_up_20260913/phase2_bakeoff.py` directly. Representation-only translation mapped Phase 2 `support|refute|non_polarized` to RC1 `supports|refutes|non_polarized` and added the already-frozen immutable policy-resolver binding. Terminal reason values were not copied, normalized, or case-folded.

## Exact execution record

- GitHub Actions run: `34765492356`;
- job: `103745597200`;
- conclusion: `success`;
- result artifact: `10320486422` (`contract-c-successor-candidate-a-rc1-result`);
- artifact ZIP SHA-256: `de815a41966dd59671a5b56067db7dee07144c25050436560fe8b716327b8ec5`;
- extracted `ADVERSARIAL_RESULT.json` SHA-256: `02ee02b98c451acd749e55c5fe73628b1f5f960223920e8f4c2318dea9d8bb28`;
- compact preserved receipt: `ADVERSARIAL_RESULT_RECEIPT.json`.

The job log records the terminal counts and disposition emitted by the directly oracle-anchored evaluator.

## Qualification result

All preregistered RC1 acceptance gates passed with the frozen candidate bytes unchanged:

- exact Phase 2 semantic/execution specimens: **19/19** reconstructed from the directly imported frozen oracle;
- canonical permutation controls: **5/5**;
- preregistered attacks: **37/37** detected by the appropriate structural, authority, exact-B, policy-resolution, and/or exact frozen-oracle layer;
- weak-control sensitivity demonstrations: **4/4**;
- `apparatus_failures=[]`.

The new regression attack A37 changed exact `MIXED_RELATIONS` to lowercase `mixed_relations`, coherently resealed the object, and was caught both by RC1 structural semantics and by direct comparison with the imported frozen Phase 2 oracle.

The new weak control W04 reproduced the RC0 failure mechanism: a case-normalizing copied oracle would accept the lowercase value, while the exact frozen oracle retained `MIXED_RELATIONS` and the RC1 stack rejected the substitution. This demonstrates sensitivity to the specific false-green that falsified RC0.

The other preserved sensitivity controls continued to distinguish independent handoff authority from local reseal, neutral participation from support, and exact minimal-basis truth from a merely covering fake joint.

## Terminal research disposition

**`QUALIFIED_FOR_CAL_PRODUCER_CONFORMANCE_RESEARCH`**

This disposition applies to **exact frozen RC1 at `ba5f55b0fb6ca54e0461a688813b66fd81bf8c4c`**, not to RC0.

RC0 remains preserved with superseding disposition `FALSIFIED_REQUIRES_SUCCESSOR_CANDIDATE`. Its successful workflow is negative apparatus evidence showing that a self-consistent duplicated oracle can produce a false green. It is not qualification authority for RC1.

RC1 qualification means only that this exact Candidate A representation survived the corrected apparatus-level pressure test strongly enough to justify a separate CAL producer-conformance research phase. That later phase must prove exact CAL producer semantics can derive and emit the claimed minimal sufficient basis family, exact public participants, exact stable terminal state/reason, and producer/policy bindings without inventing a new epistemic judgment or restoring ablated C1 surfaces.

## Nonclaims and prohibited promotion

This is not:

- production promotion or release;
- a successor SemVer assignment;
- proof of CAL producer conformance;
- independent-consumer reproduction/conformance;
- compatibility/versioning authority;
- a CAL production change;
- a Decision Engine production change;
- Contract E / Authorization work;
- operational execution authority.

PR #94 and the stacked Candidate A research PR remain Draft Research and must not be merged merely for tidiness.