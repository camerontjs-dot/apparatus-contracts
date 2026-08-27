# Candidate Contract B CAL Consumer Profile — RC0

**Status:** RESEARCH CANDIDATE, NOT LOCKED  
**Applies to:** Evidence Builder → Apparatus Contract B → Claim Audit Lab  
**Current locked contract:** Handoff Contract v1.0.0 with later v1.1.0 vocabulary amendment  
**Canonical design discussion:** apparatus-contracts#1  
**Evidence:** Claim Audit Lab research PR #1, Rungs 03–05; Evidence Bundler seam research PR #4  
**Version disposition:** intentionally unassigned until conformance tests complete

---

## 1. Purpose

This profile defines the **consumer-side semantics** of Contract B from Claim Audit Lab's perspective.

It does not replace the locked handoff contract and does not amend the canonical schema. It states what CAL may treat as a Contract-B fact, what CAL must measure or assess itself, what information must remain preserved, and what CAL must refuse to infer when the handoff does not establish a required state.

The core object remains:

> Given a supplied audit proposition and the admitted evidence bundle, what can CAL defensibly conclude from that evidence, and exactly why?

CAL is not proving the proposition true in reality. CAL is measuring and adjudicating the relationship between the supplied proposition and the supplied evidence under an explicit audit policy.

---

## 2. Contract-B role

Contract B is the measurement-ready handoff consumed by CAL.

The seam has three epistemic layers:

```text
Evidence Builder / Contract B
  evidence-world facts
  provenance
  admission + nomination history
  retrieval / coverage facts
            │
            ▼
CAL measurement
  claim ↔ passage semantic relations
            │
            ▼
CAL assessment + decision
  eligibility
  proposition-specific validity
  temporal applicability
  authority / supplier applicability
  aperture / completeness
  decision participation
  verdict / abstention
```

The contractual invariant is:

> Upstream metadata may inform a CAL judgment, but it must not silently become the judgment.

---

## 3. What CAL may assume after successful intake verification

After Contract-B integrity and compatibility verification succeeds, CAL may treat the following as **handoff facts**, subject to the exact values and uncertainty represented in the artifact:

### 3.1 Identity and lineage

- bundle identity and schema version;
- claim / audit-unit identity;
- exact supplied claim or proposition text;
- task / workflow identifiers carried through the apparatus;
- passage identity;
- source identity;
- passage-to-source lineage;
- content, passage, bundle, and configuration hashes;
- timestamps actually recorded by the upstream apparatus;
- provenance links actually recorded by the upstream apparatus.

### 3.2 Evidence content

- exact admitted passage text;
- section / location information when supplied;
- source-declared bibliographic and contextual metadata;
- source-declared system/version/effective-date information when supplied and provenance-bound;
- source-declared authority, jurisdiction, supplier identity, or role when supplied and provenance-bound.

### 3.3 Evidence-preparation history

CAL may retain, but must not silently promote into semantic truth:

- retrieval query / method / rank / score;
- EB nomination lane or role such as supporting, counterevidence, conditional, or insufficient;
- EB admission/review state;
- deduplication history;
- source class / type;
- `trust_level` vocabulary values;
- coverage/search/count facts;
- exclusion records and reasons;
- transformation records.

These fields are part of the apparatus record. They are not CAL verdicts.

---

## 4. What CAL must not inherit as semantic truth

The following equivalences are prohibited unless an explicit CAL policy or assessment stage produces them with a receipt:

```text
EB support nomination       ≠ CAL semantic support
EB counter nomination       ≠ CAL semantic refutation
primary source              ≠ automatically eligible
secondary source            ≠ automatically ineligible
background source           ≠ automatically low evidentiary value
source type                 ≠ proposition-specific authority
publication date            ≠ temporal applicability
supplier identity           ≠ supplier-control adequacy
retrieval coverage count    ≠ evidence completeness
scaffold support label      ≠ CAL verdict
absence of counterevidence  ≠ proof of no counterevidence
missing field               ≠ favorable default
missing field               ≠ adverse default
```

If CAL uses any upstream fact to derive a decision-relevant state, the transformation must be explicit and attributable.

---

## 5. CAL intake requirements

### 5.1 Fail closed before semantic processing

CAL must not begin semantic measurement until the required Contract-B integrity checks succeed.

At minimum, current v1 behavior verifies:

- contract/schema compatibility;
- bundle hash / SHA256SUMS consistency;
- audit-config hash consistency;
- controlled-vocabulary compatibility;
- required internal references and passage/source consistency.

A failed integrity check produces a deviation / intake failure, not a guessed repair.

### 5.2 Preserve the supplied audit record

The Contract-B input is immutable from CAL's perspective.

CAL may produce derived artifacts, views, and assessments. It must not rewrite the historical input to make the later decision appear inevitable.

### 5.3 Full admitted-passage measurement aperture

For each supplied audit proposition, every passage admitted to the CAL-facing evidence set must remain available to semantic measurement regardless of its upstream support/counter nomination lane.

Upstream nomination metadata may be retained for auditability but may not restrict CAL to a preselected semantic channel.

This reflects the verified CAL-v1 behavior from Rung 05.

---

## 6. CAL measurement contract

CAL owns the semantic measurement of each admitted claim/passage relationship.

The measurement layer must be conceptually separable from decision eligibility and source authority.

A measurement receipt should identify, at minimum:

- audit proposition ID;
- passage ID;
- measurement method / model / operator;
- method or model version;
- relevant frozen configuration hash;
- support/refutation/silence/ambiguity observation as represented by the implementation;
- score(s) or deterministic operator output where applicable;
- receipt hash / trace reference.

### 6.1 Blinded semantics

Semantic measurement must not change merely because an upstream field changes that is not part of the proposition or passage meaning.

Rung 05 established this metamorphic property for `trust_level`: changing `primary → secondary` left retrieval, entailment, and aggregate semantic measurement unchanged.

The same principle applies prospectively to retrieval nomination labels and similar preparation metadata.

---

## 7. CAL assessment contract

Decision-relevant judgments downstream of measurement are CAL-owned unless a future contract explicitly establishes another authority.

The candidate assessment families are:

### 7.1 Eligibility

Question:

> May this evidence contribution participate in this particular decision under the applicable CAL policy?

State:

```text
eligible | ineligible | unknown
```

`unknown` is not equivalent to ineligible and is not silently discarded.

### 7.2 Proposition-specific semantic validity

Question:

> Even if the passage bears a semantic relation to the language, is that relation meaningful for the supplied proposition or obligation?

Examples include entity, scope, operator, or proposition mismatch.

State:

```text
valid | invalid | unknown
```

### 7.3 Temporal / lifecycle applicability

Question:

> Does this evidence apply to the system, process, policy, or state actually under audit?

A valid historical record may remain in the ledger while becoming non-deciding for a current-state proposition.

### 7.4 Authority / supplier applicability

Question:

> Is the source or actor authorized / qualified to establish the particular proposition under the applicable decision policy?

Source class or `trust_level` may be inputs to such a policy. They are not themselves the conclusion.

### 7.5 Aperture / completeness

Question:

> Do the supplied corpus, search, retrieval, and evidence facts justify concluding that the relevant evidence aperture is complete enough for this decision?

Contract B / EB may supply coverage facts. CAL owns the proposition-specific completeness conclusion unless a future contract explicitly assigns otherwise.

### 7.6 Assessment receipts

Any assessment that can affect a verdict should identify:

- assessment family;
- status;
- proposition ID;
- affected contribution(s) / passage(s);
- factual inputs used;
- policy / operator ID and version;
- reason;
- receipt hash / trace reference.

---

## 8. Evidence preservation and non-destructive views

The retained evidence ledger is not the same object as the current decision basis.

CAL may derive views such as:

```text
raw / measured
eligible
valid
currently applicable
current decision basis
```

Those views are subsets or annotations over the retained record.

The following rule is normative for this candidate profile:

> **Non-deciding does not mean erased.**

A contribution may remain historically admitted while being:

- contradicted by another contribution;
- ineligible under a specific policy;
- invalid for a specific proposition;
- temporally stale;
- lower authority for the present decision;
- superseded for current-state use;
- unresolved;
- outside the current decision basis.

Its identity, content, provenance, measurements, assessments, and historical role remain reconstructable.

### 8.1 Reassessment

Later information creates a new assessment / decision trace.

It does not mutate the prior trace.

Rung 04 verified the desired sequence:

```text
unknown supplier status
→ new information
→ mixed evidence
→ remediation/current-state validation
→ supported current-state conclusion
```

while preserving the earlier validation and incident records throughout.

---

## 9. Decision contract

A CAL decision must be reconstructable from:

- verified Contract-B input identity;
- admitted evidence ledger;
- semantic measurement receipts;
- assessment receipts;
- aperture/completeness state;
- frozen CAL policy / rules version;
- explicit decision basis;
- final verdict or abstention reason.

### 9.1 Decision basis is a subset

The passages that justify the decision are a subset of the retained ledger, never a replacement for it.

### 9.2 Unknown remains first-class

Required unresolved state must produce an explicit abstention / unresolved outcome rather than a silent default.

### 9.3 Mixed evidence remains mixed

Valid support and valid refutation must remain simultaneously representable. CAL must not force one into disappearance merely because the other has a slightly higher score.

### 9.4 Composition supplied from upstream

This profile does not define automatic claim decomposition.

Where CAL receives a supplied obligation / proposition graph or explicit parent-child composition rule, CAL may evaluate the supplied atomic units and compose results according to that declared structure.

CAL must not silently invent decomposition or parent-child logic when the upstream apparatus has not supplied it.

See `claim-decomposition-boundary-notes.md` for the unresolved upstream design questions.

---

## 10. CAL result artifact

The semantic requirement is clear even though the physical packaging remains under test.

A CAL result must be an immutable, provenance-bound derivative tied to:

- input bundle ID and hash;
- proposition / claim ID and exact text hash;
- admitted passage IDs / hashes;
- CAL version;
- audit policy / rule version and hash;
- measurement receipts;
- assessment receipts;
- decision basis;
- verdict / abstention;
- creation timestamp;
- supersedes / prior-result reference when applicable.

### 10.1 Open packaging question

Two implementations remain plausible:

1. a resealed audited C-B derivative as current CAL v1 does; or
2. a separate immutable CAL result / receipt package bound to the original C-B input.

This candidate profile does not choose between them. The tri-repository conformance experiment must test whether a separate result artifact produces a cleaner, more reconstructable boundary without losing compatibility.

---

## 11. Explicitly out of scope for RC0

This profile does not define:

- claim extraction;
- automatic claim decomposition;
- automatic verification-obligation generation;
- retrieval algorithms;
- chunking algorithms;
- source-authenticity verification beyond supplied provenance/integrity checks;
- the correct general policy for primary/secondary/background evidence;
- automatic authority inference;
- automatic lifecycle inference;
- automatic causal inference;
- numeric operator semantics;
- the final controlled vocabulary for richer CAL abstention reasons;
- a Contract-B schema amendment.

---

## 12. Evidence behind the candidate profile

### CAL Rung 03

Supported preserving support/refutation relations rather than relying on one universal max-winner signal.

### CAL Rung 04

Supported non-destructive historical evidence preservation across a realistic evolving evidence bundle and exposed a missing decision-state interface.

### CAL Rung 05

Supported:

- v1 nomination-lane invariance;
- semantic measurement independence from trust tier;
- locating trust-dependent behavior at explicit CAL policy rule `P1_eligibility_suppressed`;
- explicit receipt-bound `eligible | ineligible | unknown` in the shadow decision model.

### Evidence Bundler seam research

Independently supports:

- preserving provenance/mechanical/context facts upstream;
- retaining nomination/admission history;
- blinding nomination metadata from semantic measurement;
- carrying search/coverage facts without making the completeness conclusion;
- keeping proposition-specific CAL judgments out of the minimal handoff.

---

## 13. Promotion rule

**Do not lock or version this profile as canonical Contract B until the conformance plan passes.**

The required next gate is the true tri-repository V0/V1/V2 consumer test described in `contract-b-cal-conformance-plan-rc0.md`.

After that result, classify the necessary canonical change:

- **documentation clarification only:** PATCH candidate;
- **new optional factual-context fields:** MINOR candidate, currently likely `1.2.0` because v1.1.0 already exists;
- **new required fields / incompatible semantics / breaking packaging change:** MAJOR candidate, likely `2.0.0`.

The test result, not preference, determines the version class.
