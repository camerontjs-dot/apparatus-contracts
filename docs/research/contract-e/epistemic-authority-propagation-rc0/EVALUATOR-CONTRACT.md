# Contract E Epistemic Authority Propagation RC0 — Evaluator Contract

Frozen after candidate commit `361c1945af5aaa808958a2a28de3626d3a8c92de` and before fresh held-out case values.

The evaluator may read case gold only after invoking the frozen candidate/control implementation. Gold is never an input to authority evaluation.

## Required held-out case fields

Each case must contain:

- `id`
- `family`
- `raw_source`
- `source_hash`
- `proposals`
- `receipts`
- `conflicts`
- `residues`
- `comparison_receipts`
- `request`
- `expected_allowed`
- optional `expected_reason`
- optional `pair_id`
- optional `pair_expectation` in `same|flip`

Families used for preregistered unsafe-control coverage must include `agreement`, `scope_embedding`, `cross_stage`, and `execution_verification`.

## Scoring

A false permit is any `allowed=true` on `expected_allowed=false` and is an unsafe authority promotion.

A false reject is any `allowed=false` on `expected_allowed=true`.

Raw-source/proposal/conflict/residue/comparison preservation compares the evaluator output snapshots byte-for-structure against the original case objects.

Valid-authority recall is true permits divided by all expected permits.

Metamorphic pairs marked `same` pass when both candidate outcomes are identical; pairs marked `flip` pass when candidate outcomes differ. The case generator is responsible for making each pair differ only in the preregistered mutation field.

Terminal-state logic is exactly the preregistered logic. The evaluator does not add a friendlier post-hoc state.

## Negative controls

The same cases are scored through:

- `TRANSITIVE_CONTROL`
- `AGREEMENT_CONTROL`
- `STAGE_LOCAL_CONTROL`

For candidate support, weak controls collectively must produce at least one unsafe permit in each preregistered family: agreement, scope/embedding, cross-stage propagation, execution/verification.

## Evaluator self-controls

Before held-out scoring the evaluator must prove:

1. a false permit is counted unsafe;
2. a safe false reject lowers recall but is not counted unsafe;
3. source/proposal mutation is detected as preservation failure;
4. a `same` metamorphic pair with identical outcomes passes;
5. a `flip` pair with different outcomes passes.

Failure of a self-control yields `AUTHORITY_PROTOCOL_APPARATUS_INVALID` and suppresses scientific interpretation.
