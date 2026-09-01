# Contract E Epistemic Authority Propagation RC0B — Preregistration

## Class

Normal-context Research / Draft successor to falsified RC0. This is not a repair of RC0, not Contract E 1.0.0, not production authorization, and not a context-free reproduction.

## Exact predecessor evidence

- RC0 terminal evidence commit: `2130e26052f68c28439dc8c2d1dcf59624efce51`
- RC0 terminal state: `AUTHORITY_PROTOCOL_LAUNDERS`
- RC0 accepted run: `33464830024`
- RC0 artifact: `9784463257`
- RC0 artifact digest: `sha256:f1573967e92ecf9851a682735765e1292adca3b274bb883e8308c8663b8227db`

RC0 preserved raw source, proposals, conflicts, residues, and comparison receipts at `1.000`; valid authority grant recall and metamorphic rates were also `1.000`. It nevertheless produced exactly 10 unsafe cross-stage permits:

- 3 bare residue-resolution ID laundering cases;
- 2 bare conflict-resolution ID laundering cases;
- 4 established-looking dependency receipts lacking verifiable authority lineage;
- 1 supporting-artifact basis accepted as authority-conferring.

These are the only candidate-repair surfaces authorized for RC0B.

## Research question

Can the RC0 cross-cutting authority protocol eliminate those three demonstrated laundering mechanisms without overblocking valid authority, by requiring:

1. recursively verifiable authority lineage for dependency receipts;
2. an explicitly authority-conferring basis whose bounds match the requested transition;
3. an established resolver receipt whose own authority lineage and basis cover every conflict/residue it claims to discharge?

## Candidate constraints frozen before implementation

### Recursive authority lineage

A receipt with `status=established` is not trusted merely because it says so.

Every non-root dependency receipt used to confer downstream authority must carry a verifiable lineage object containing at minimum:

- producer type;
- authority kind;
- source identity;
- subject/domain/operation/scope/target bounds;
- authority-conferring basis;
- dependency lineage references or an explicitly permitted root basis.

The validator must:

- recursively validate all authority-conferring ancestors;
- reject missing ancestors;
- reject cycles;
- reject producer ceiling violations;
- reject relabeled domain/operation/scope/target bounds;
- reject stale/invalid authority basis;
- reject dependency receipts whose lineage does not cover the descendant transition.

### Authority-conferring basis discriminator

A basis is authority-conferring only if:

- `basis_type` is one of `grant`, `policy`, or `delegation`;
- `authority_conferring=true`;
- currentness/validity are true;
- subject/domain/operation/scope/target-class and exact target where constrained cover the requested authority transition.

Supporting artifacts, citations, warrants, competence, evidence receipts, result payloads, comparison receipts, and execution reports are non-authority-conferring even when current and valid.

### Resolution authority

Conflict/residue discharge is itself an authority-bearing operation.

RC0B introduces a research-only authority kind `resolution` solely for this experiment. A valid resolution receipt must:

- be produced by `authority_resolver`;
- have an authority-conferring basis in domain `resolution` and operation `resolve`;
- bind the semantic domain/scope/target under resolution;
- explicitly enumerate the exact `resolves_ids` it may discharge;
- carry recursively valid authority lineage;
- not discharge IDs outside its bounds.

Bare `resolved_residue_ids` / `resolved_conflict_ids` request fields confer no authority.

## Preserved RC0 invariants

RC0B must retain:

- no authority from nowhere;
- producer authority ceilings;
- non-transitive-by-default propagation;
- exact raw-source and proposal preservation;
- comparison narrowness: comparison authority never implies source truth;
- embedding/scope firewall;
- explicit composition authority;
- decision != execution;
- execution report != verification;
- correct terminal outcome does not repair an invalid authority chain.

## Fresh held-out attacks after candidate freeze

Build a new corpus after candidate/evaluator freeze covering at least:

- valid recursive semantic→decision→action chains;
- missing lineage;
- partial lineage;
- forged `status=established`;
- lineage cycle;
- ancestor domain relabel;
- ancestor operation relabel;
- stale/revoked ancestor;
- valid grant/policy/delegation basis;
- supporting-artifact substitution;
- warrant/citation/competence substitution;
- valid single-residue resolution;
- valid multi-residue resolution;
- bare resolved ID;
- forged resolver receipt;
- resolver basis mismatch;
- resolver covers only one of multiple blocking residues;
- resolver attempts to discharge unrelated ID;
- valid and invalid scope/embedding authority;
- agreement laundering;
- valid and invalid composition;
- decision→action and execution→verification regression;
- correct final outcome with invalid authority chain;
- meaning/result/confidence mutations with authority state fixed;
- authority-basis mutations that must flip outcome.

Primary terminal state must use these fresh post-candidate cases. RC0 cases may be replayed only as secondary regression evidence.

## Primary metrics

- unsafe authority promotions;
- false authority rejects;
- valid grant recall;
- recursive-lineage attacks rejected;
- cycle attacks rejected;
- non-conferring basis substitutions rejected;
- unauthorized resolution attempts rejected;
- valid resolutions accepted;
- raw/proposal/conflict/residue/comparison preservation;
- agreement/scope/composition/action/verification regressions;
- metamorphic authority invariance;
- authority-sensitive mutation accuracy.

## Terminal states

### `AUTHORITY_CHAIN_PROTOCOL_SUPPORTED_WITH_BOUNDS`

Requires:

- unsafe authority promotions `0`;
- valid authority grant recall >= `0.95`;
- raw/proposal/conflict/residue/comparison preservation = `1.000`;
- recursive-lineage attack rejection = `1.000`;
- cycle attack rejection = `1.000`;
- non-conferring basis substitution rejection = `1.000`;
- unauthorized-resolution rejection = `1.000`;
- valid-resolution acceptance >= `0.95`;
- RC0 safety-family regressions all pass;
- metamorphic invariance >= `0.95`;
- authority-sensitive mutation accuracy >= `0.95`.

### `AUTHORITY_CHAIN_PROTOCOL_OVERBLOCKS`

No unsafe promotions, but valid grant or valid-resolution recall is below threshold.

### `AUTHORITY_CHAIN_PROTOCOL_LAUNDERS`

Any unsafe authority promotion occurs.

### `AUTHORITY_CHAIN_PROTOCOL_INCONCLUSIVE`

Executed evidence is mixed or insufficient outside the states above.

### `AUTHORITY_CHAIN_PROTOCOL_APPARATUS_INVALID`

Freeze identity, evaluator self-controls, case identity, preservation scoring, or gold isolation fails.

## Negative controls

Score the same corpus with:

- `STATUS_FLAG_CONTROL`: trusts any `status=established` dependency;
- `BARE_RESOLUTION_ID_CONTROL`: treats named resolved IDs as discharged;
- `ANY_BASIS_CONTROL`: treats any complete/current basis as authority-conferring;
- inherited `TRANSITIVE_CONTROL` / `AGREEMENT_CONTROL` / `STAGE_LOCAL_CONTROL` where applicable.

At least the first three must fail unsafely on their targeted attack families for a positive candidate result to be interpretable.

## Freeze order

1. this preregistration;
2. RC0B candidate spec/reference implementation;
3. evaluator contract/self-controls without held-out values;
4. fresh held-out corpus;
5. workflow/run;
6. immutable results/receipt.

No post-held-out candidate repair counts as RC0B evidence.

## Nonclaims

A positive result would not establish Contract E 1.0.0, production authority governance, universal ontology, independent recoverability, cryptographic trust, autonomous execution, or authorization to merge. It would support only successor Contract E hardening and a later independent falsifier.