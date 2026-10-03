# D → E execution-intent boundary bake-off RC0

**Classification:** Draft Research preregistration. Representation experiment only.

**Parent:** apparatus-contracts issue #167 and North-Star audit PR #165.

## Decision

Determine whether the tested post-Contract-D action-materialization boundary requires a universal shared execution-intent representation, or whether an effect/domain-specific intent profile with immutable identity is sufficient.

Do not assume that a new Apparatus Contract is required.

## Live evidence frozen before implementation

Repository production base:

`camerontjs-dot/apparatus-contracts@c3563cff66d2c85dcbf575c693056e2d8e4563d4`

Observed source domains:

1. **MainFrame task dispatch**
   - live source inspected at `camerontjs-dot/mainframe-live@dbff8c39790ce70961de2310809e1bd737ccb7a9`;
   - task authority exposes reviewed packet identity, executor/profile/task class, file-scope and verification constraints, workdir/timeout/mode and source/contract hashes;
   - control plane revalidates authority before live dispatch.

2. **ERS pending-review shadow**
   - Contract E × ERS result `b153dcc4434cbe8a98616a9e410c6125378144c7`;
   - action materialization uses an immutable `execution-intent-candidate-v1` carrying executable identity, entry point, arguments, input identities, environment constraints and side-effect targets.

Contract D release authority remains `298a1a0f7b7b6d7712e11200d04faec3e1ca169b`, with effect-registry blob `a40f4f4447470654bdc16d852f5927189ae30cc5`.

## Competing representations

### R0 — weak effect/target-only binder

Bind only exact Decision identity, effect type/version and logical target.

This is an intentionally weak control. It should accept at least one materially different concrete action under the same D effect/target.

### R1 — universal common envelope only

Represent common action-materialization categories:

- exact Decision identity;
- effect identity;
- target identity;
- implementation identity;
- material input identity;
- environment/constraint identity;
- side-effect-scope identity;
- pre-state identity where applicable;
- whole intent identity.

No domain/effect-specific semantic validator is allowed.

### R2 — opaque native intent + effect/domain profile

The native domain object remains owned by its consumer/executor. A profile-specific validator:

- validates the native object's domain semantics;
- recomputes its immutable identity;
- binds it to exact D Decision/effect/target.

Contract E would need only the resulting immutable reference and exact jurisdiction/operation binding.

### R3 — common envelope + effect/domain profile

Use the R1 common envelope, but require the same profile-specific semantic validation as R2.

## Frozen attack classes

The case file committed before implementation defines attacks across both domains including:

- executor/executable substitution;
- material argument/input substitution;
- side-effect-scope widening;
- environment/network relaxation;
- stale/pre-state substitution;
- cross-domain/profile substitution;
- unknown profile/version;
- self-consistent native payload mutation with recomputed identity.

Every attack remains within the same broad D effect/target where the case says so, so a weak effect/target-only binder has a chance to fail meaningfully.

## Acceptance / discrimination

The purpose is not to make every candidate pass.

Record for each representation:

- false accepts;
- false rejects;
- exact attack IDs accepted/rejected;
- whether rejection required profile-specific semantics.

### Interpretation

- If R1 alone rejects all material attacks for the intended reason, a minimal shared common envelope gains support.
- If R1 admits self-consistent semantic attacks while R2 rejects them, profile-specific validation is load-bearing and a universal envelope alone is insufficient.
- If R2 and R3 have identical discrimination, the common envelope has not demonstrated additional authorization value in this experiment.
- If only R3 can preserve a legitimate independent-consumer requirement that R2 cannot, a shared envelope gains bounded support.
- If the missing properties are Decision-owned rather than execution-owned, stop with `CONTRACT_D_SEMANTIC_GAP`.

## Weak-control requirement

R0 must false-accept at least one preregistered attack for a semantic reason. If it does not, the apparatus does not discriminate the intended boundary and the result is `INCONCLUSIVE`.

## Nonclaims

This experiment cannot establish:

- universal execution-intent semantics;
- production Contract E readiness;
- a need for Contract F or any other contract letter;
- correctness of MainFrame or ERS execution;
- real filesystem/process containment;
- production authorization.

## Stop rule

The cases and expected materiality are frozen before implementation. Do not revise them after observing candidate results. If the evaluator cannot distinguish common structural validity from domain semantic validity, stop `INCONCLUSIVE`.
