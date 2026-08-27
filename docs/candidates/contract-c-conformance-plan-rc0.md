# Contract C CAL → Decision Engine Conformance Plan RC0

**Status:** PRE-LOCK TEST PLAN  
**Candidate profile:** `contract-c-cal-decision-engine-profile-rc0.md`  
**Producer under test:** Claim Audit Lab  
**Consumer under test:** Decision Engine  
**Canonical discussion:** apparatus-contracts#1 plus future Contract-C issue

## Purpose

Determine whether the proposed Contract-C handoff preserves enough epistemic state for a Decision Engine to act on CAL results without reverse-engineering CAL internals or mistaking an audit verdict for an operational decision.

No schema is locked merely because the candidate is coherent.

## Test philosophy

The output seam should be tested with **metamorphic decision-context pairs** and **epistemic-state pairs**.

Two opposite invariants matter:

1. **Same CAL result, different decision context may legitimately produce different operational decisions.**
2. **Same decision context, materially different CAL epistemic state must remain distinguishable to the Decision Engine.**

If either invariant cannot be represented, the handoff is too lossy or responsibilities are incorrectly coupled.

## Pinned inputs

Before execution, record exact SHAs for:

- Apparatus Contracts candidate Contract C branch;
- CAL research branch carrying the relation-preserving/consumer-seam work;
- Decision Engine implementation branch used for the consumer probe;
- Contract-B fixture / EB fixture used as upstream evidence input.

## Rung C1 — Export completeness

Build a Contract-C candidate from one known CAL shadow trace containing:

- valid support;
- valid counterevidence;
- at least one non-deciding historical contribution;
- one explicit unknown or incomplete state;
- a receipt-bound decision basis.

Assert that the exported artifact retains:

- all contribution IDs;
- all passage/source bindings;
- semantic measurements;
- assessments;
- decision basis;
- unresolved blockers;
- policy/config bindings;
- Contract-B identity/hash.

**Falsifier:** any information needed to reconstruct why the CAL conclusion occurred exists only inside an internal CAL object and disappears from Contract C.

## Rung C2 — Counterevidence preservation

Create two CAL traces with the same headline reported verdict:

- C2-A: clean support with no valid refutation;
- C2-B: support after resolving or rendering historical refutation non-deciding.

The Decision Engine consumer must be able to distinguish them without parsing free-text notes.

**Falsifier:** both artifacts collapse to the same decision-relevant state merely because the headline verdict matches.

## Rung C3 — Honest unknown propagation

Use a CAL result with an unresolved eligibility/aperture/authority blocker.

Assert:

- the blocker survives Contract C;
- its family/reason/affected evidence are machine-readable;
- the Decision Engine can distinguish `unknown` from `false`, `absent`, and `ineligible`;
- no default action is implied by Contract C.

**Falsifier:** abstention becomes a missing field, low confidence number, or implicit rejection.

## Rung C4 — Epistemic result ≠ operational decision

Feed **the exact same Contract-C artifact** into two decision contexts.

Example:

```text
Context A: low-stakes reversible internal experiment
Context B: irreversible regulated production release
```

The Decision Engine should be permitted to choose different actions while preserving the same CAL result reference.

Conversely, CAL must not encode either action into Contract C.

**Falsifier:** changing decision context requires altering the CAL artifact or CAL output directly dictates the action.

## Rung C5 — Same decision context, different evidence state

Hold the decision context fixed and compare:

- supported / clean;
- supported / residual historical conflict;
- mixed valid evidence;
- abstained because aperture unknown;
- contradicted.

The Decision Engine must receive enough structured state to implement a policy that differentiates these cases.

**Falsifier:** the consumer must inspect CAL's internal trace files or parse prose to distinguish them.

## Rung C6 — Decision authority separation

Attempt adversarial transformations:

```text
supported → approve
contradicted → reject
abstained → stop
mixed → escalate
```

Contract-C validation should not contain such mappings. If a Decision Engine chooses to implement them, they must appear as Decision Engine policy/rules with their own rationale and authority.

**Falsifier:** Contract C itself carries an operational authorization field populated by CAL.

## Rung C7 — Claim/decomposition lineage

Run the output exporter against:

- an atomic supplied proposition;
- a derived proposition with an original parent claim reference;
- the same original claim under a different decomposition identity.

Assert:

- exact proposition audited is always identifiable;
- parent/original claim lineage survives when supplied;
- changing decomposition creates a distinguishable result identity;
- Contract C does not assert which decomposition timing or algorithm is correct.

This test intentionally does not resolve whether decomposition should happen before retrieval.

## Rung C8 — Restatement identity

If CAL outputs a defensible-restatement candidate, assert:

- original proposition remains unchanged;
- candidate is explicitly derived;
- basis and weakened/omitted elements are machine-readable;
- Decision Engine cannot confuse the candidate with the original claim ID.

If claim repair is not implemented, this rung remains deferred rather than simulated.

## Rung C9 — Re-audit immutability

Audit the same Contract-B input under two different CAL policies or assessment states.

Assert:

- two Contract-C result IDs/hashes exist;
- prior result is unchanged;
- optional supersession linkage is explicit;
- Decision Engine records which result it actually used.

**Falsifier:** the later audit overwrites the earlier result or Decision Engine cannot identify which version informed its decision.

## Rung C10 — Provenance round trip

Starting from a durable decision record, reconstruct:

```text
decision
→ Decision Engine rule/context
→ Contract-C result
→ CAL conclusion and receipts
→ Contract-B bundle
→ passage
→ source/provenance
```

The round trip must not rely on filenames or human memory as the only join keys.

## Rung C11 — Output packaging comparison

Compare:

1. current CAL resealed audited-C-B derivative;
2. separate Contract-C artifact bound to immutable Contract B.

Measure:

- semantic ownership clarity;
- duplicate data volume;
- reconstruction completeness;
- append-only audit history;
- consumer complexity;
- risk of confusing evidence-preparation facts with CAL judgments;
- ability to bind a Decision Engine decision to a specific CAL result.

Do not lock the packaging choice until this comparison is run.

## Rung C12 — Minimality / ablation

Starting with the complete candidate Contract-C artifact, remove one field family at a time:

- measurement ledger;
- assessment receipts;
- non-deciding contributions;
- unresolved blockers;
- policy/config binding;
- Contract-B hash binding;
- citations/provenance references;
- validation status.

For each ablation, ask whether a Decision Engine can still reproduce the intended decision-relevant distinction and whether an auditor can still reconstruct the result.

This determines which fields are genuinely contractual versus merely convenient.

## Candidate consumer acceptance tests

The eventual Decision Engine should fail closed when:

- Contract-C integrity verification fails;
- referenced Contract-B input cannot be identified where required;
- policy/config identity is missing for a result that depends on it;
- the result uses an unsupported Contract-C major version;
- required epistemic disposition is absent.

It should not fail merely because CAL abstained. Abstention is a valid result.

## Falsification criteria

Revise or reject RC0 if:

1. a scalar verdict + confidence reproduces every tested Decision Engine distinction with no information loss;
2. the Decision Engine repeatedly needs CAL-private trace internals not represented in Contract C;
3. Contract C cannot remain decision-neutral in practice;
4. non-deciding/counterevidence history is irrelevant across realistic downstream decisions;
5. a separate output artifact introduces duplication without improving ownership, history, or traceability over audited-C-B writeback;
6. the proposed receipt structure is too implementation-specific to survive reasonable CAL architecture changes;
7. decomposition lineage cannot be represented without locking decomposition policy prematurely;
8. a simpler artifact passes the same reconstruction and decision-separation tests.

## Lock gate

Do not lock Contract C until all of the following exist:

- at least one working Decision Engine consumer;
- executable CAL exporter / adapter;
- reproducible C1–C7, C9–C12 results (C8 may defer with claim repair);
- explicit adversarial/falsification attempts;
- pinned CAL, Decision Engine, Contract-B, and Apparatus SHAs;
- output-packaging comparison;
- schema/vocabulary proposal based on measured minimum fields;
- migration/compatibility statement;
- validation-status semantics;
- cross-repo review.

## Version selection

Because Contract C is new, its first canonical version should be **v1.0.0 only after the lock gate passes**.

RC0 and subsequent RCs are research candidates, not semantic versions of the locked apparatus contract.