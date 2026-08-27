# Contract A Modernization RC1

**PR class:** Research
**Production impact:** None
**Base:** `apparatus-contracts` production `main` at `c314e53bd91c0736aa4370a364673b069aceb43e`

## Decision this research supports

Decide whether legacy Contract A 1.0.0 remains adequate for the current Evidence Bundler pipeline, requires a backward-compatible extension, or requires a new incompatible contract surface.

Do not assign a new canonical Contract-A version until producer/consumer behavior and compatibility class are observed.

## Current observed evidence

- Legacy Contract A was designed as `Scaffold Harness -> Evidence Builder` and carries scaffold run state, claims, source corpus, used passages, retrieval linkage, and several scaffold-authored confidence/support fields.
- Contract B 1.2.0 is now promoted on production `main`, making the upstream Evidence Bundler boundary the next unresolved typed interface.
- Evidence Bundler's ability to produce Contract B does not establish that its current upstream inputs are minimal, semantically clean, or reproducible.

## Main research questions

1. What does Evidence Bundler actually require from upstream to build the evidence world it now hands to Contract B 1.2.0?
2. Which legacy Contract-A fields are factual/provenance state versus upstream interpretations that EB must not silently treat as truth?
3. Does claim decomposition materially change retrieval, and therefore need first-class identity/lineage in A?
4. Are retrieval queries part of the upstream contract, EB-owned derived state, or both under explicit provenance?
5. Which source representation facts must be frozen before EB processing?
6. Can A distinguish original task/claim, audit proposition, retrieval seed, decomposition artifact, and upstream assertion without collapsing them?
7. Can an independent EB consumer implement legitimate intake behavior from the specification and frozen artifacts alone?
8. What compatibility class is actually demonstrated by old/new producer-consumer tests?

## Legacy fields requiring explicit re-evaluation

Do not remove or preserve these by intuition. Test whether each is necessary and what authority it legitimately carries:

- `support_status`;
- `claim_strength`;
- `extraction_fidelity`;
- `counterevidence_checked`;
- `counterevidence_found`;
- `downgraded` / `downgrade_reason`;
- `trust_level`;
- `retrieved_for`;
- retrieval query and rank;
- scaffold-used passage spans;
- model/prompt/config identity;
- task and workflow-condition state.

A field may be useful provenance even when EB must ignore it for semantic judgment.

## Candidate boundary hypothesis

Contract A should describe **the upstream work object and the exact state presented to Evidence Bundler**, not a pre-audited evidence verdict.

Leading candidate families, pending experiments:

- original task/question/claim identity;
- exact audit proposition(s);
- explicit decomposition state and lineage where decomposition occurred;
- producer/model/operator/config identity;
- source/representation identity and hashes;
- source acquisition/retrieval provenance already known upstream;
- upstream-used spans/anchors when they exist, marked as upstream observations/selections;
- explicit upstream assertions/heuristics with named provenance, never silently promoted into EB or CAL truth;
- explicit unknown/missing state;
- immutable handoff identity and integrity binding.

## Boundary constraints

Contract A must not silently establish:

- claim truth;
- proposition-specific support/refutation;
- source authority for the proposition;
- semantic validity;
- temporal applicability;
- corpus completeness;
- final evidence admission;
- CAL verdict;
- Decision Engine policy or authorization.

## Evidence program before lock

### Experiment 1 — EB input/gap audit
Inspect production EB intake and trace every consumed upstream datum to either legacy A, EB configuration, or an implicit/default assumption.

### Experiment 2 — Retrieval/aperture assurance
Use the frozen known-answer corpus on the sibling EB branch to learn which upstream state is actually needed for reliable evidence construction.

### Experiment 3 — Decomposition sensitivity
Hold corpus and EB fixed while varying original-claim/decomposition representation. Determine whether decomposition needs immutable identity/lineage in A.

### Experiment 4 — Field-family ablation
Remove legacy/candidate A field families one at a time and measure whether EB can still produce the same legitimate evidence-world semantics without invented defaults.

### Experiment 5 — Independent consumer
Implement a clean-room A consumer from the candidate spec + frozen artifacts without consulting the reference intake implementation.

### Experiment 6 — Real producer -> A -> EB -> B conformance
Use an actual upstream producer artifact, candidate Contract A validation, real EB intake/output, and Contract B 1.2.0 validation.

## Required controls

- untouched legacy A artifact where compatibility is claimed;
- missing-state cases;
- hostile upstream semantic labels;
- provenance tamper;
- decomposition-order invariance;
- meaning-changing decomposition sensitivity;
- source-order invariance;
- representation/version mutation sensitivity;
- unbound sidecar/extension rejection if an extension packaging approach is tested.

## Allowed dispositions

Exactly one when evidence is sufficient:

- `SUPPORTED FOR PROMOTION`
- `FALSIFIED`
- `INCONCLUSIVE`
- `SUPERSEDED`

## Promotion rule

If supported, open a new minimal Promotion/Production branch from the then-current `main`. Do not merge this research branch as the canonical Contract A implementation.
