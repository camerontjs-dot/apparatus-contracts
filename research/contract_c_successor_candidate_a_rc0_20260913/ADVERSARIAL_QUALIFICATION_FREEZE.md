# Contract C successor Candidate A RC0 adversarial qualification freeze

**Classification:** Draft Research / Research Infrastructure.

This record freezes the adversarial qualification of the exact Candidate A RC0 research contract. It is a successor record to the immutable Candidate A freeze and does not rewrite Phase 0, Phase 1, Phase 1.5, Phase 2, or the candidate bytes.

## Exact lineage

- protected Apparatus production base observed before the experiment: `c3563cff66d2c85dcbf575c693056e2d8e4563d4`;
- Phase 0 obligation freeze: `e588e1295367a4b867d608342aaacaccb41850b8`;
- Phase 1 semantic-corpus freeze: `175246ae16932f2f34a399560d7f76013213bf97`;
- Phase 1.5 discriminator freeze: `163d0d424777ef3c0a3b45dec2888c845634205d`;
- Phase 2 representation freeze: `f5337dedaad045aa290e80f69dc83ac1a0f73436`;
- exact Candidate A RC0 freeze: `9f1808c47503c884887dbf862e9cd8162b21b583`;
- adversarial preregistration: `2a3600719df8c0502bd265f63925dee9166c9ac1`;
- adversarial evaluator commit: `d06c1affdf5fb65cc1df235cb1a1ebb7af174adc`;
- executed workflow head: `fdbb235714bac53239be19a3cea651020a2d437a`.

The workflow independently verified the three candidate blobs before executing the cohort:

- `CANDIDATE_A_RC0.md`: `4fae55b156b0caea5a4815c2c665a816f39667d9`;
- `candidate_a_rc0.schema.json`: `ee89f25bfcef008c95cbb35adf696fb1b3e2dc20`;
- `candidate_a_rc0.py`: `fb0a05ca929fbcf8284799306e9861d992839aaa`.

Therefore the decisive cohort ran against the exact pre-reveal candidate. No post-freeze candidate repair occurred.

## Exact execution record

- GitHub Actions run: `34764954521`;
- job: `103744166486`;
- conclusion: `success`;
- result artifact: `10319849604` (`contract-c-successor-candidate-a-rc0-result`);
- artifact ZIP SHA-256: `871a0d2325a92a8415e46c61cf617ea649bee0b2ef6dadb3779eb0475c34c615`;
- `ADVERSARIAL_RESULT.json` SHA-256 after extracting the artifact: `13d2938f5a0b1e16ae88a3df4ddc5bf4d7880f7bc20f47d2de9e4e624fc5ba27`;
- compact preserved execution receipt: `ADVERSARIAL_RESULT_RECEIPT.json`.

The workflow log records the exact terminal counts and disposition emitted by the evaluator.

## Qualification result

The preregistered acceptance gates all passed:

- positive frozen semantic/execution specimens: **19/19**;
- unordered canonical-identity controls: **5/5**;
- preregistered attacks detected by the appropriate verification/oracle layer: **36/36**;
- deliberately weak controls shown vulnerable while the required stack caught the corresponding attack: **3/3**;
- `apparatus_failures=[]`.

The result preserves an important boundary rather than hiding it. Some mutations are intrinsically invalid under the closed candidate grammar and are rejected structurally. Others, including a fake joint basis over truly independent alternatives, artificial unique-winner selection, same-ID proposition-content replacement, coherent residual deletion, and other coherently resealed semantic changes, can form locally valid **different objects**. RC0 does not pretend local JSON validity can prove empirical causal truth. Those attacks were detected by the independently established whole-object handoff authority and/or exact comparison with the frozen semantic oracle.

The attacker-selected-digest control also behaved as intended: a replacement digest can of course match attacker-mutated bytes if a verifier blindly accepts that digest. The qualification therefore treats only the independently established pre-mutation handoff digest as authority. Self-selected replacement identity is not authority.

## Sensitivity controls

The harness was not accepted merely because every RC0 check returned green. Three seeded weak constructions had to fail visibly:

1. a local-reseal-only verifier accepted coherent residual deletion that the independent external authority rejected;
2. a consumer that laundered `non_polarized` causal participation into support incorrectly strengthened completed `not_checkable` to `supported`;
3. a basis checker that required only causal coverage accepted a fake joint `{S1,S2}` where the frozen truth was independent alternatives `{{S1},{S2}}`, while the exact semantic oracle rejected the rewrite.

This demonstrates sensitivity to the principal authority, neutrality, and causal-normal-form failure modes rather than a tautological all-green harness.

## Terminal research disposition

**`QUALIFIED_FOR_CAL_PRODUCER_CONFORMANCE_RESEARCH`**

This disposition means only that the exact frozen Candidate A RC0 representation survived the preregistered apparatus-level pressure test strongly enough to justify a separate research phase asking whether exact CAL producer semantics can construct it correctly without inventing new epistemic judgment.

The next legitimate gate is therefore **CAL producer-conformance research against this exact candidate freeze**. That future work must in particular prove that CAL derives the claimed minimal sufficient basis family from legitimate producer authority/ablation state, preserves exact public participants and stable terminal semantics, and emits RC0 without reintroducing the ablated C1 surfaces. A failure there would be evidence against producer conformance or, if it exposes a missing public semantic obligation, a falsifier requiring an explicit successor candidate record.

## Nonclaims and prohibited promotion

This qualification is not:

- production promotion or release;
- a successor SemVer assignment;
- proof of CAL producer conformance;
- independent-consumer reproduction or consumer conformance;
- a compatibility/versioning decision;
- a CAL production change;
- a Decision Engine production change;
- Contract E / Authorization work;
- operational execution authority.

PR #94 and the stacked Candidate A research PR remain Draft Research and must not be merged merely to tidy the branch stack.