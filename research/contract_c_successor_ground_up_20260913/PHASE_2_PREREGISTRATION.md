# Contract C successor Phase 2 representation bake-off preregistration

**Classification:** Draft Research / Research Infrastructure.

**Ordering:** Phase 2 begins only after the Phase 1.5 freeze commit `163d0d424777ef3c0a3b45dec2888c845634205d`. Frozen semantic authority remains Phase 1 `175246ae16932f2f34a399560d7f76013213bf97`, with M1/M2/M3 materialization and discriminator dispositions supplied by Phase 1.5. `MSC` remains evaluator notation only.

## Shared abstract oracle

Every candidate is scored against the same abstract model. The model contains exact:

- Contract-B world binding;
- producer implementation and policy-digest binding;
- proposition identity/semantic-content binding;
- result-set and proposition execution state;
- terminal epistemic state/reason when execution completed;
- every retained exact evidence participant with support/refute/non-polarized relation and causal/residual role;
- the mathematical family of minimal sufficient causal sets.

The evaluator contains one oracle table for SP-01 through SP-14 and EX-01 through EX-05. Candidate encoders consume that same table. Candidate parsers/interpreters are separate implementations and are compared only after reconstructing the abstract model.

SP-04, SP-10, and SP-11 use the Phase 1.5 materialized causal oracles. SP-12 remains representation-stress-only and is never reported as a current-CAL producer output.

## Candidate A: minimal sufficient basis groups

Wire hypothesis: retained participants are exact evidence references plus relation/terminal role. Causal truth is a canonical family of minimal sufficient sets of exact participant references.

The Candidate A interpreter must independently reject duplicate participants, duplicate members within one group, duplicate groups, non-minimal supersets, residual members in a causal group, incomplete causal coverage, proposition aliasing, and invented terminal semantics on failed/incomplete execution. Canonicalization sorts semantically unordered participants and groups and re-encodes from the reconstructed abstract semantics.

## Candidate B: typed causal expression

Wire hypothesis: retained participants are the same exact evidence references plus relation/terminal role. Causal truth is a recursive expression containing only:

- exact participant leaf;
- `all_of`;
- `any_of`.

The Candidate B interpreter is independent of Candidate A. It recursively expands the expression to its own family of sufficient sets, applies minimality reduction, reconstructs the abstract model, and only then compares to the oracle.

The evaluator will deliberately use factored Candidate B forms for SP-10, SP-11, and SP-12. It will also construct distributed equivalent expressions to test whether different Candidate B syntax reconstructs one semantic object. Candidate B is not scored by resemblance to Candidate A.

## Frozen scoring gates

For each candidate:

1. exact abstract reconstruction for all 19 SP/EX oracles;
2. all 15 frozen binding/integrity metamorphisms reject or become observably different as specified in Phase 1;
3. MA-01 and MA-02 cannot acquire public semantic authority by adding measurement/caller-stipulated fields; MA-03 remains representable;
4. permutations of semantically unordered structures canonicalize identically;
5. no arbitrary winner, false joint necessity, polarity laundering, causal/residual overlap, proposition aliasing, or execution/epistemic conflation;
6. external whole-object authority remains independent of locally recomputed content identity.

Comparative secondary measures:

- total canonical byte count over the fixed corpus;
- causal leaf-reference occurrence count;
- recursive grammar/equivalence machinery required;
- whether logically equivalent Candidate B factorizations have more than one syntax-canonical form;
- whether one semantic identity for Candidate B requires a semantic normalization step that expands/minimizes the expression.

Byte size is not selection authority by itself.

## Selection rule

A candidate that loses frozen semantics or integrity fails regardless of compactness. If both are lossless, prefer the smaller normative/equivalence surface for the current successor scope. Candidate B receives explicit credit for factorization/duplicate-reference savings; Candidate A receives explicit credit only if it directly provides the required semantic normal form without recursive Boolean-equivalence machinery.

Selection is a Draft Research representation preference only. It does not create a schema version, release, promotion, production producer/consumer authority, Decision policy, Contract E/Authorization semantics, or an independent-reproduction claim.