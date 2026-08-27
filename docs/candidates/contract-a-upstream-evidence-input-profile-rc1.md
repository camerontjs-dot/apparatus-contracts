# Contract A Upstream Evidence-Input Profile RC1

**Status:** Research candidate only
**Canonical version:** none assigned by this document
**Production impact:** none

## Purpose

Define a candidate typed boundary from an upstream task/claim construction stage into Evidence Bundler.

The candidate exists to make experimental questions concrete. It is not a proposal to promote all listed fields.

## Candidate chain

```text
original task / claim source
        ↓
claim-intake / decomposition process
        ↓
Contract A RC1
  exact work object + lineage + upstream provenance
        ↓
Evidence Bundler
  retrieval / evidence-world construction / admission history
        ↓
Contract B 1.2.0
        ↓
CAL
```

## Core invariant

> Contract A records what upstream presented to Evidence Bundler and how that work object came to exist. It does not certify that the claim, decomposition, source, or upstream support label is semantically correct.

## Candidate logical object families

### 1. Handoff identity

- Contract-A profile/version identity;
- artifact/run ID;
- creation timestamp;
- producer identity/version;
- integrity manifest/tree hash;
- explicit parent/supersedes linkage for revised handoffs.

### 2. Original work object

- original task/question ID;
- original claim text and stable content hash where a claim exists;
- source of the original claim/task: human, dataset, upstream agent, imported record, or explicit unknown;
- task/domain/context facts that are genuinely upstream inputs rather than inferred judgments.

### 3. Audit proposition set

For each proposition presented to EB:

- proposition ID;
- exact text;
- parent/original claim ID;
- role such as original, decomposed child, retrieval seed, or explicit derived proposition;
- immutable proposition hash;
- explicit state indicating whether decomposition occurred.

The role vocabulary remains experimental.

### 4. Decomposition lineage, when present

- decomposition artifact ID;
- parent/child graph;
- decomposition method;
- producer/model/operator identity;
- configuration/prompt/template identity and hash where material;
- timestamp;
- optional attributable rationale/notes;
- explicit failure/partial/unknown state.

Contract A does not claim that a decomposition is meaning-preserving merely because it records it.

### 5. Upstream source/representation state

Where sources already exist before EB:

- source ID;
- canonical locator or local representation identity;
- content hash;
- media/representation type;
- version/effective/publication/access facts where directly supplied or mechanically observed;
- acquisition provenance;
- exact frozen bytes or an integrity-bound path/reference when the experiment permits external storage.

### 6. Upstream spans/anchors, when present

- source ID;
- passage/span/anchor ID;
- representation-bound coordinates;
- text preview only as convenience, never identity;
- reason upstream selected the span, marked as upstream provenance rather than EB admission truth.

### 7. Upstream retrieval/query history, when present

Candidate only. Experiments must determine whether these belong canonically in A or should remain producer-specific attachments:

- query text/hash;
- target proposition IDs;
- retrieval method/provider;
- rank/score as upstream observations;
- search timestamp;
- search scope/bounds;
- explicit unsuccessful searches.

EB must remain free to run its own retrieval. Upstream rank/role cannot silently become EB or CAL relevance/support truth.

### 8. Upstream assertions/heuristics

Legacy A contains scaffold-authored fields such as support status, confidence-like values, downgrade state, and trust level. RC1 treats any retained equivalents as **attributable upstream assertions**, not authoritative evidence facts.

Candidate representation should preserve:

- assertion name/type;
- value;
- asserting producer/policy;
- basis/reference where available;
- explicit unknown state.

The candidate should make it possible for EB to ignore these fields without losing the record that they existed.

## Explicitly forbidden authority promotion

Presence in Contract A must never automatically establish:

- proposition truth;
- support/refutation relation;
- source reliability/authority for the proposition;
- semantic validity;
- temporal applicability;
- corpus completeness;
- evidence admission fitness;
- CAL eligibility/decision participation;
- CAL verdict/abstention;
- downstream operational decision.

## Missing-state semantics

Unknown, absent, not-run, not-applicable, and failed-to-produce must remain distinguishable where the distinction matters.

Do not use false, empty collection, zero, or default confidence as a substitute for missing state.

## Candidate packaging questions

Not yet decided:

- single manifest versus integrity-bound companion files;
- whether raw source bytes live inside A or are referenced by immutable content-addressed objects;
- whether decomposition is core A or an optional extension;
- whether upstream search history is core A or an optional extension;
- whether legacy A 1.0 can be extended compatibly or must be superseded;
- whether one A artifact may contain multiple audit propositions from one original claim;
- whether multi-claim task/run packaging belongs in A or in a higher-level container.

## Minimum pre-promotion evidence

Do not assign a canonical version until the research program demonstrates:

1. real EB intake requirements from production code;
2. retrieval/aperture benchmark behavior;
3. decomposition sensitivity or invariance;
4. field-family ablation/minimality;
5. explicit missing-state behavior;
6. hostile upstream-judgment isolation;
7. independent consumer reproducibility;
8. real upstream producer -> A -> EB -> Contract B 1.2.0 conformance;
9. compatibility class against legacy A where compatibility is claimed.

## Reconsideration trigger

Any evidence that EB requires a proposition-specific judgment merely to construct its evidence world should reopen the boundary rather than causing that judgment to be smuggled into Contract A as a fact.
