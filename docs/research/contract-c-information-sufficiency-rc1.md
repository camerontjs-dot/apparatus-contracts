# Contract C Information-Sufficiency + Consumer-Diversity Program — RC1

**Status:** RESEARCH PREREGISTRATION, NOT LOCKED  
**Contract:** C — Claim Audit Lab → downstream decision systems  
**Production impact:** none  
**Required upstream baseline:** Contract B 1.2.0 locked production  
**Apparatus baseline:** `c314e53bd91c0736aa4370a364673b069aceb43e`  
**CAL production baseline:** `33a928db97316a3652d57df9cafb8ca240305233`  
**Decision Engine baseline:** `55f108c196ead020b5965c7d4d737464c92bc4a0`

---

## 1. Why RC1 exists

The earlier Contract-C RC0 work asked a useful but too narrow question:

> What is the smallest CAL projection the current Decision Engine Gate needs?

That risks defining Contract C around one provisional MainFrame promotion policy before either the Decision Engine or the destination decisions have been independently validated.

RC1 asks a prior question:

> **What is the smallest stable, decision-agnostic representation of CAL's epistemically meaningful result from which multiple materially different downstream decisions and human reports can be derived without reopening CAL internals, re-auditing raw evidence, or inventing missing state?**

The result package is the machine-authoritative evidence object. Human-readable reports and destination-specific decision inputs are derived views.

```text
Contract B evidence-world state
        ↓
       CAL
        ↓
Contract C semantic result package
        ├── render → full human audit report
        ├── render → compact/public report
        ├── project → MainFrame decision input
        ├── project → publication-claim decision input
        ├── project → SOP/requirement decision input
        └── project → investigation/deviation decision input
                            ↓
                     decision policy/runtime
                            ↓
                     decision receipt
```

Central invariant:

> **CAL's epistemic result is neither the rendered report nor the operational decision.**

---

## 2. What is observed versus hypothesized

### Observed

1. Contract B 1.2.0 is now the locked production Evidence Bundler → CAL evidence-world boundary.
2. CAL already has multiple output precedents:
   - structured audit/model state;
   - replay/audit traces;
   - audited Contract-B compatibility writeback;
   - Markdown and HTML report renderers.
3. Existing CAL report examples already render claim registers, evidence links, counterevidence, flags, limitations, and rewrite guidance from structured data.
4. Existing CAL research separates measurements, assessments, retained evidence/contributions, decision basis, unknowns, and final disposition more richly than the legacy audited-B projection.
5. Decision Engine `main` remains primarily a career select/rank tool, but its generic Gate head is a distinct primitive that evaluates named criteria with `pass | fail | unknown` and returns `promote | hold | reject` without applying external state.
6. The earlier Contract-C Decision Engine shadow hard-coded one MainFrame-facing audited-claim promotion policy. It is useful as a consumer probe, not evidence that the policy or C surface is canonical.
7. MainFrame already has a concrete upstream audit queue: `bin/audit-sweep` surfaces `needs-audit`/`needs-verification` knowledge items. MainFrame local rules also require verified statuses to be earned, preserve honest failure paths, and distinguish lifecycle mutation authority from evidence generation.

### Inference

A separate Contract-C result object is likely cleaner than treating a human report, a CAL implementation trace, or a resealed Contract-B derivative as the canonical downstream authority.

### Hypothesis under test

A bounded semantic result package can be sufficiently expressive for multiple unrelated downstream decisions while remaining independent of any single decision policy and excluding incidental CAL implementation telemetry.

### Unknown

- exact field-level minimum;
- exact receipt granularity;
- portability versus reference-only tradeoffs;
- whether run-level and proposition-level objects should share one package;
- which CAL uncertainty/confidence constructs are sufficiently validated to become stable contract surface;
- whether some downstream decisions legitimately require reopening Contract B rather than consuming C alone;
- whether a general-purpose Decision Engine adds value beyond a small policy runtime plus domain policy packs.

---

## 3. Prior work: what is already solved

This program must not claim novelty for generic decision tables, policy-as-code, or provenance modeling.

### Decision models

OMG Decision Model and Notation (DMN) already provides a standard for precise business decisions/rules and decision tables. See: <https://www.omg.org/dmn/>.

**Already solved:** representing explicit decision logic and decision dependencies in a standardized way.

### Policy decision/runtime separation

Open Policy Agent (OPA) already demonstrates a mature architecture in which applications provide structured input to a versioned policy engine, policy decisions are separated from enforcement, and decision logs bind decisions to input and policy/bundle identity. See:

- <https://www.openpolicyagent.org/docs>
- <https://www.openpolicyagent.org/docs/management-decision-logs>

**Already solved:** generic policy evaluation, policy distribution, and auditable decision logging.

### Provenance vocabulary

W3C PROV already models entities, activities, agents, derivation, collections, and provenance-of-provenance. See: <https://www.w3.org/TR/prov-overview/>.

**Already solved:** generic provenance concepts.

### Potentially different in this program

The open problem here is narrower and upstream of those systems:

> Can CAL expose a stable epistemic result that preserves evidence-relative audit meaning, explicit unknowns, decision basis, counterevidence, and attributable assessment state so that ordinary decision/policy systems do not need to reconstruct or silently redo CAL's audit?

Contract C should therefore compose with mature decision/policy concepts rather than replace them.

---

## 4. Regulatory-methodology reference, not a compliance claim

The 2025 draft EU/PIC/S GMP Annex 22 on Artificial Intelligence remains draft guidance as of this preregistration. Its document map includes intended use, acceptance criteria, test data, test-data independence, test execution, explainability, confidence, and operation. The European Commission consultation also highlights predefined performance metrics, test-data quality/management, ongoing monitoring, change control, and human review.

EMA held a further expert workshop on 30 June–1 July 2026 specifically because the draft treatment of dynamic, adaptive, probabilistic, GenAI, and LLM systems remains under reconsideration.

References:

- <https://health.ec.europa.eu/consultations/stakeholders-consultation-eudralex-volume-4-good-manufacturing-practice-guidelines-chapter-4-annex_en>
- <https://www.ema.europa.eu/events/good-manufacturing-practice-multistakeholder-workshop-expert-contributions-artificial-intelligence-guidance-development-annex-22>
- <https://picscheme.org/en/publications?tri=draft>

**Use here:** experimental discipline only. This research must not describe itself as Annex-22-compliant or validated for GMP use.

---

## 5. Candidate Contract-C semantic families

RC1 does **not** declare these all required. They are the starting field families for ablation.

### F1 — result identity and input binding

- result/run identity;
- exact Contract-B bundle ID/hash/version;
- exact audited proposition ID/text/hash;
- original/parent/decomposition lineage when supplied;
- CAL version;
- audit policy/config/rules/model/operator identities and hashes;
- result integrity root.

### F2 — evidence-state references

- admitted evidence IDs/hashes;
- support, counterevidence, unresolved, historical/non-deciding evidence references;
- source/passage provenance required to understand the result;
- evidence-history facts used by an assessment.

### F3 — measurements

- semantically meaningful claim/evidence observations;
- numeric/operator outputs when decision-relevant;
- deterministic checks;
- measurement receipt identity and implementation/operator identity sufficient for audit/replay.

Raw logits, retrieval scores, internal feature vectors, and debug telemetry are excluded unless testing proves a stable downstream need.

### F4 — assessments

- eligibility;
- semantic validity;
- temporal/lifecycle applicability;
- authority/supplier applicability;
- aperture/completeness;
- composition state where applicable;
- attributable assessment receipt and factual inputs.

### F5 — epistemic conclusion

- execution/disposition state: completed, limited, abstained, partial/failed;
- reported CAL result under a pinned policy;
- typed reason;
- exact decision basis;
- residual conflict/counterevidence state;
- explicit unknowns/blockers;
- non-deciding evidence and exclusion reason.

### F6 — resolution and reassessment state

- evidence requests / what would change the result;
- optional defensible-restatement candidate, explicitly non-authoritative;
- re-audit/supersession lineage;
- prior-result reference where applicable.

### F7 — execution, validation, and deviation state

- partial-run/failure status;
- deviations;
- validation/qualification state of relevant operators where meaningful;
- warnings that materially affect interpretation;
- timestamps only where semantically required.

---

## 6. Frozen representation variants

Use the same underlying CAL audit state for each variant.

### C0 — full CAL implementation-rich trace

Control condition. Includes internal trace/telemetry beyond the proposed stable seam.

### C1 — semantic Contract-C result package

Preferred hypothesis. Contains only stable, attributable, decision-agnostic result semantics plus the receipts/lineage required to interpret and audit them.

### C2 — thin destination-specific projection

A consumer-specific projection containing only fields that one chosen decision policy currently reads.

Purpose: detect overfitting to one consumer and measure information loss.

### C3 — rendered human report only

Markdown/HTML report without separate machine-authoritative C data.

Purpose: test the tempting alternative that a rich report alone is enough.

Expected result: C3 may be sufficient for many human reviews but should not become the machine contract unless it preserves deterministic structure, exact lineage, unknown state, and consumer reproducibility without report scraping.

---

## 7. Core consumer-diversity probes

Consumer policies must be preregistered before field-level ablation so fields are not retained merely because they are convenient to the current implementation.

### P1 — MainFrame durable-knowledge audit gate

Question:

> Given a `needs-audit` claim/note, what operational posture is justified after CAL?

Example destination policy outputs, provisional only:

- eligible for operator promotion review;
- hold for more evidence;
- human review required;
- not eligible as written.

MainFrame lifecycle mutation remains outside Decision Engine authority.

### P2 — publication / website claim gate

Question:

> Is this exact claim supportable for publication from the supplied evidence, or must it be reviewed, narrowed, caveated, or withheld?

This probe stresses claim wording, counterevidence, citation state, scope/causal overreach, and explicit uncertainty.

### P3 — SOP / controlled-requirement conformance gate

Question:

> For one explicit requirement and supplied operational records, is conformance supported, nonconformance supported, or is the state indeterminate?

This probe must preserve the distinction between:

- evidence that a requirement exists;
- evidence that an event/process occurred;
- evidence that the requirement applies;
- absence of evidence;
- evidence of absence/nonconformance.

No regulatory compliance claim is implied by a synthetic or research fixture.

### P4 — deviation / investigation decision-readiness gate

Question:

> Does the current evidence establish enough about the event, scope, causal claims, counterevidence, and unresolved questions to support the next procedural decision, or is further investigation required?

This probe stresses temporal facts, competing explanations, unresolved blockers, supersession, and evidence requests.

### Secondary probe P5 — evidence-acquisition prioritization

Question:

> Which unresolved evidence request would be most decision-relevant to resolve next?

This is intentionally secondary because expected-value-of-information logic introduces additional utility/cost assumptions not owned by CAL.

### Secondary probe P6 — vendor / regulated-AI evidence assurance

Question:

> Which product or validation claims are supported by the submitted evidence package strongly enough to pass a buyer/QA review gate, and which require qualification, missing evidence, or narrower wording?

This is valuable for external assurance work but should not be used to define C unless it adds a genuinely different information requirement.

---

## 8. Preregistered discriminating tests

### T1 — exact lineage preservation

Every legitimate consumer decision must identify the exact proposition, Contract-B input, CAL result, CAL policy/config, and destination policy used.

**Falsifier:** a decision can be reproduced while ambiguity remains about what CAL audited or which policy acted.

### T2 — report derivation / no dual authority

Render Markdown/HTML from C1.

**Pass:** report facts that purport to describe CAL state are derivable from C1 and do not introduce new epistemic judgments.

**Fail:** the report contains decision-relevant semantic state that cannot be reconstructed from C1, or C1 must scrape the report to recover it.

### T3 — consumer sufficiency

For each preregistered consumer, compare decisions from C0, C1, and an explicitly implemented reference policy.

**Pass:** C1 preserves every legitimate decision distinction that C0 enables, except distinctions attributable only to incidental implementation telemetry.

### T4 — thin-projection insufficiency control

Compare C2 against multiple consumers.

**Expected:** at least one legitimate consumer distinction should be lost if C2 was overfit to the first MainFrame Gate policy.

If C2 remains sufficient across all probes, the richer C1 hypothesis must be compressed.

### T5 — report-only control

Use C3 as the sole input for an independent machine consumer without privileged CAL access.

**Pass for C3 only if:** the consumer can deterministically recover all required structured state and lineage without heuristic text parsing.

Otherwise C3 remains a derived human view.

### T6 — same verdict, different evidence state

Construct pairs with identical headline CAL verdict but materially different:

- counterevidence;
- unresolved blockers;
- evidence quality/provenance;
- temporal applicability;
- decision basis;
- residual conflict.

**Pass:** any consumer that legitimately cares about the difference can distinguish them from C1.

### T7 — explicit unknown propagation

Remove or mark unknown one decision-relevant assessment at a time.

**Fail if:** absence silently becomes favorable or adverse state.

### T8 — policy orthogonality

Hold C1 bytes fixed while changing only destination policy/context.

**Pass:** different legitimate decisions may result, while C1 remains unchanged.

This demonstrates that C is audit state, not destination policy.

### T9 — telemetry invariance

Mutate raw NLI logits, retrieval scores/ranks, debug prose, internal feature ordering, and other non-contract telemetry while holding stable CAL semantics fixed.

**Pass:** C1 and all legitimate decisions remain invariant.

### T10 — field-family ablation

Remove F1–F7 one family at a time, then subfields within surviving families.

Classify each field as:

- required by stable semantics;
- required by one or more legitimate consumers;
- audit/debug only;
- render-only convenience;
- redundant/derivable;
- unsupported by evidence.

A field does not become required merely because an implementation currently emits it.

### T11 — hostile/malformed input

Tamper with claim identity, bundle/result hashes, receipt references, policy identity, unknown-state encoding, and enumeration values.

**Pass:** consumers fail closed without converting malformed state into a substantive negative finding.

### T12 — partial run / deviation preservation

Construct a run in which some propositions complete, one operator fails, and another result is limited.

**Pass:** completed results remain distinguishable from incomplete execution; the package does not fabricate a complete audit.

### T13 — re-audit / supersession

Audit the same proposition and B input under two pinned CAL policies, then audit a changed B input.

**Pass:** all results remain immutable and separately reconstructable; no old result silently migrates to a new evidence world or policy.

### T14 — independent consumer reproducibility

Build at least one consumer from the Contract-C specification and frozen artifacts without consulting CAL implementation code or the first consumer's implementation logic.

**Claim scope if passed:** bounded independent reproducibility on the frozen profile, not universal interoperability.

### T15 — real negative-control replay

After the synthetic matrix passes, replay preserved MainFrame incident/fabricated-source fixtures that predate this C design.

**Purpose:** reduce fixture-design leakage and test whether provenance/unknown/failure semantics survive a real failure history.

Do not alter the preserved incident fixture to make the pipeline pass.

---

## 9. Fixture strategy

Synthetic generation is useful for controlled mutations but must not be the only evidence.

### Already available

- CAL v1 frozen trace fixtures spanning support, contradiction, partial support, overstated, source-scope error, false caution, not-checkable reasons, numeric ambiguity, and inference cases;
- Contract-B 1.2 production fixtures and cross-repository acceptance artifacts;
- Decision Engine synthetic Contract-C/MainFrame fixtures;
- MainFrame's real audit queue/rules and preserved provenance-control history.

### Smallest additional fixture set worth obtaining

#### A. MainFrame knowledge packet

Prefer **8–12 real or safely sanitized notes/claims**, with their actual source/raw lineage where available:

- at least 2 strongly supported;
- 2 under-supported/overstated;
- 2 with explicit missing or unverifiable evidence;
- 1 with active counterevidence/conflict;
- 1 historical/temporal applicability case;
- preserved fabricated-source/incident cases as negative controls if safe to copy into a research fixture.

Gold need not prescribe the final decision. It should identify invariant facts such as which sources actually exist, which claim text was present, and which evidence was intentionally missing.

#### B. SOP / quality-system packet

One coherent mini-corpus is more valuable than many unrelated SOP snippets:

- 1–3 short controlled procedures or procedure excerpts;
- 20–40 explicit atomic requirements total;
- 6–12 associated records/events/log entries;
- examples of conforming, nonconforming, ambiguous, not-applicable, missing-record, and superseded-procedure cases;
- at least one temporal-version trap;
- at least one negative existential where missing evidence is not enough to prove failure.

Synthetic is acceptable if every requirement and record is internally coherent and the intended ground facts are frozen before execution.

#### C. Publication/vendor-claim packet

A small set of exact claims plus source material:

- factual numeric claim;
- causal overclaim;
- scope overclaim;
- claim with valid counterevidence;
- claim that is supportable only after narrowing;
- claim that should remain `not_checkable` from supplied evidence.

CAL's existing examples may already cover most of this probe; do not generate more unless a gap remains.

### Data-independence rule

Use separate agents/processes for fixture construction and consumer implementation when practical. Freeze fixture bytes and expected invariant facts before running the experimental consumer. Preserve failed controls and deviations.

---

## 10. Decision Engine implication to test, not assume

The generic Gate head may be the reusable core while the career select/rank engine remains a separate domain application.

Candidate future architecture:

```text
Decision Runtime
├── intake validation / canonicalization
├── policy pack loader
├── named criteria / decision tables
├── explicit PASS / FAIL / UNKNOWN semantics
├── deterministic evaluator
├── policy + input + result receipt
└── no external state mutation

Policy packs
├── mainframe-knowledge
├── publication-claim
├── sop-conformance
└── deviation-readiness
```

Research question:

> Is a small deterministic policy runtime sufficient, or is a bespoke generalized Decision Engine abstraction actually required?

Do not generalize the career weighted scorer until evidence shows that relative multi-option ranking is part of the common decision primitive.

---

## 11. Promotion gate for Contract C

Contract C is not supported for lock merely because one MainFrame happy path works.

A future promotion disposition requires at minimum:

1. C1 generated from actual CAL production/research result semantics without invented defaults;
2. report rendering proven to be a derived view, not a second authority;
3. at least three materially different consumer probes with preregistered policies;
4. C1 sufficiency versus C0 and C2 controls;
5. C3 report-only comparison;
6. same-verdict/different-evidence controls;
7. explicit unknown and partial-run handling;
8. field-family ablation/minimality evidence;
9. hostile mutation/fail-closed tests;
10. deterministic decision receipts bound to C + destination policy;
11. at least one independently implemented consumer;
12. at least one fixture/control set that predates the RC1 design.

Possible dispositions:

- `SUPPORTED FOR PROMOTION`
- `SUPPORTED WITH BOUNDED DEBT`
- `INCONCLUSIVE`
- `FALSIFIED`

The conclusion must state exactly which consumer classes and fixture families were demonstrated.

---

## 12. Explicit non-goals

This RC1 does not:

- implement Contract C;
- assign a Contract-C version;
- redesign Contract A;
- alter Contract B 1.2.0;
- claim CAL is validated for GMP use;
- claim Annex 22 compliance;
- choose final MainFrame lifecycle policy;
- choose final SOP/deviation policies;
- merge the career scoring engine with the Gate runtime;
- authorize autonomous MainFrame mutation;
- treat the Decision Engine as independently validated.

---

## 13. Next experimental sequence

1. Freeze this preregistration and exact repository SHAs.
2. Inventory actual CAL semantic output state and classify it into F1–F7 without changing code.
3. Specify C1 logical object and C0/C2/C3 mappings.
4. Freeze consumer policies P1–P4.
5. Obtain only the missing fixture packets identified above.
6. Implement producer projection and report rendering from C1 on research branches.
7. Implement consumers independently where possible.
8. Run conformance, mutation, metamorphic, ablation, and independent-consumer experiments.
9. Perform epistemic compression before any schema/version decision.

The experimental question is information sufficiency first, architecture second, production promotion last.
