# Contract C successor Phase 2 representation bake-off freeze

**Classification:** Draft Research / Research Infrastructure.

This record freezes the bounded representation bake-off that follows, and does not rewrite, the Phase 1 schema-neutral corpus at `175246ae16932f2f34a399560d7f76013213bf97` or the Phase 1.5 discriminator freeze at `163d0d424777ef3c0a3b45dec2888c845634205d`.

The Phase 1 `MSC` notation remains an evaluator oracle. This freeze does **not** declare `MSC` syntax to be the eventual wire format.

## Exact execution record

- Phase 2 preregistration commit: `719fc47a8f1a7b72391459e8f6de430b9dbd34a3`.
- Bake-off evaluator commit: `c72c2384b44d0094fd5064f69b9698393d2c2b87`.
- Executed workflow head: `433dbe69d1aba52f7ab6c3cb4c7ed1cf0318ec06`.
- GitHub Actions run: `34760640798`; job: `103732753852`; conclusion: `success`.
- Result artifact: `10318608591`; ZIP digest: `sha256:3e73229a8729626f6ec877f18f84eb7ea72a95f07cd52f9c73906bb7e8f35bf2`.
- Preserved result commit: `721e26b5c12f678a66f67d93742bc5d4824db38f`.
- Preserved `PHASE_2_RESULT.json` SHA-256: `b70e259713e0f628798c8c976442b9196cca07d2e82c0495b83bca32b325713c`.

The evaluator uses one frozen abstract oracle table containing SP-01 through SP-14 and EX-01 through EX-05. Candidate A and Candidate B are encoded from that same table. They have separate causal parsers/interpreters and are compared only after reconstruction of the abstract semantic model.

## Shared model reconstructed by each candidate

Each interpreter must reconstruct:

- exact Contract-B world binding;
- exact producer implementation and policy-digest binding;
- exact proposition identity/semantic-content binding;
- result-set and proposition execution state;
- terminal epistemic verdict/reason when present;
- every retained exact evidence participant;
- support, refutation, or non-polarized relation;
- causal versus residual role;
- the mathematical family of minimal sufficient causal sets.

The current-scope wire hypotheses intentionally reflect the Phase 1.5 discriminator outcomes: they do not add the four generic assessment slots, a separate rule/state causal namespace, the complete repeated policy payload, a repeated passage hash, or a separate contribution ID.

For SP-05, the frozen joint-basis grammar requirement is exercised with two non-polarized exact participants after D2 ablated a separate public rule/state node for the current successor scope. This preserves the joint-causation discriminator without silently resurrecting an opaque rule/state surface.

## Candidate A

**Hypothesis:** a canonical family of minimal sufficient sets of exact participant references, with retained participant polarity and causal/residual role carried separately.

Observed:

- exact abstract-semantic reconstruction: **19/19** SP/EX specimens;
- binding/integrity metamorphisms: **15/15**;
- measurement/authority boundary checks MA-01..03: **3/3**;
- unordered permutation canonicalization: PASS;
- recursive causal grammar required: **no**;
- additional semantic-normalization layer required for identity: **no**;
- total canonical bytes over the fixed corpus: **17,274**;
- causal participant-reference occurrences in causal structure: **33**.

Candidate A directly carries the same minimal-sufficiency normal form that the evaluator reconstructs. Duplicate group members, duplicate groups, non-minimal supersets, residual members inside a causal group, incomplete causal coverage, proposition aliasing, and invented terminal state on failed/incomplete execution are rejected.

## Candidate B

**Hypothesis:** a recursive typed expression with exact participant leaves plus `all_of` and `any_of`.

Observed:

- exact abstract-semantic reconstruction: **19/19** SP/EX specimens;
- binding/integrity metamorphisms: **15/15**;
- measurement/authority boundary checks MA-01..03: **3/3**;
- unordered syntax permutation canonicalization: PASS;
- recursive causal grammar required: **yes**;
- semantic interpretation/minimality normalization required for a single semantic identity: **yes**;
- total syntax-canonical bytes over the fixed corpus: **17,079**;
- causal leaf-reference occurrences: **27**.

Candidate B therefore has a real compactness advantage on the fixed corpus: six fewer causal leaf-reference occurrences and 195 fewer aggregate syntax-canonical bytes. That advantage is preserved as positive evidence.

### Candidate B factorization/equivalence pressure

The evaluator intentionally compares a factored expression and a distributed expression for the same frozen semantics:

- SP-10: factored 1,150 bytes; distributed 1,213 bytes;
- SP-11: factored 1,149 bytes; distributed 1,212 bytes;
- SP-12: factored 1,307 bytes; distributed 1,533 bytes.

In all three cases:

- the two expressions reconstruct the same abstract semantics;
- raw syntax-canonical bytes remain different;
- a single semantic identity is recovered only by interpreting the recursive expression, distributing/combining sufficient sets as needed, and reducing to minimal sufficient basis semantics.

This does not semantically falsify Candidate B. It identifies an extra equivalence/canonical-identity layer that Candidate A does not need because A exposes that semantic normal form directly.

## Integrity and boundary controls

Both candidates passed the same frozen one-axis mutations:

1. Contract-B world substitution becomes observably different;
2. cross-world composition is structurally rejected;
3. same-ID proposition-content substitution is observable;
4. proposition-semantic/direction substitution is observable through exact proposition binding;
5. evidence-reference substitution rejects or changes the reconstructed object;
6. causal-member removal without causal update rejects;
7. residual-member removal changes reconstructed state;
8. causal/residual role movement rejects when inconsistent with causal structure;
9. non-polarized participation cannot be silently laundered into support;
10. support/refute polarity flips change the semantic object;
11. duplicate semantic members are rejected;
12. unordered permutations canonicalize identically;
13. local re-identification after semantic mutation cannot satisfy the old external object authority;
14. an attacker-selected replacement digest is not the independently established authority binding;
15. destination threshold/routing/Authorization-like injection is rejected as outside the result grammar.

Both candidates also reject measurement-only and caller-stipulated semantic additions as public CAL authority while preserving a warranted source-grounded result.

## Phase 2 disposition

**`PREFER_CANDIDATE_A_FOR_CURRENT_SUCCESSOR_SCOPE`**.

This is a bounded research preference, not a claim that Candidate B is semantically incapable. Candidate B is lossless on the frozen corpus and more compact on factorable cases. Candidate A is preferred because, for the current successor obligations, it carries the required causal semantic normal form directly and therefore has the smaller normative equivalence/canonicalization surface.

The preference is especially constrained by the evidence status of SP-12: its strongest factorization win is a representation-stress case, not a demonstrated current-CAL producer output. No claim is made that current CAL produces `(S1 OR S2) AND (R1 OR R2)`.

Candidate A may be used as the next **research candidate**. This freeze does not itself define the final field vocabulary, JSON schema, release version, producer promotion path, or production consumer policy.

## Nonclaims and boundary

No released Contract C 1.0 bytes were changed. No official successor version is assigned. Nothing is promoted or released. CAL production semantics and Decision Engine production policy are unchanged. Contract E and Authorization are untouched. No execution authority is created. This is not an independent-consumer reproduction.