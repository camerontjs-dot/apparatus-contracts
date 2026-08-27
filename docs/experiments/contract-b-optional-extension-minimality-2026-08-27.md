# Contract B Optional-Extension + Minimality Experiment

**Date:** 2026-08-27  
**Status:** Completed research experiment. Noncanonical.  
**Disposition:** **FALSIFIED** for the conjunctive claim under review.  
**Version implication:** **UNRESOLVED**.  
**Scope stop:** Contract B only. No Contract C work was performed.

## Claim under review

> The factual capabilities demonstrated by V1 can be represented as a backward-compatible optional Contract B extension, and the proposed field set contains no capability that can be removed without losing a required consumer or auditability property.

The result separates the two clauses:

1. **Optional-extension compatibility:** supported by the observed controls.
2. **V1 field-level minimality:** falsified. The explicit stored coverage counts are redundant when V1's preregistered complete retrieval/admission ledger is retained.

Because the claim is conjunctive, failure of the minimality clause makes the overall disposition **FALSIFIED** even though the compatibility clause survived.

This experiment does not modify canonical Contract B, merge research work, release anything, assign a production schema, or assign a final semantic version.

---

## Exact research state and pins

### Prior evidence

The completed V0/V1/V2 conformance experiment was treated as prior evidence rather than rerun as a new experiment.

- Prior Apparatus report commit: `f4ee2dbd853821ba54328156bbab1c71235fae55`
- Prior V1 CAL pre-assessment measurement-view hash: `sha256:b18715b861343a541fd8317d38cfa3b4f6acf2efdcb9578fac55313bf721f8db`
- Frozen seam fixture hash recorded by the prior experiment: `sha256:4d5a900232cd243d82fffdc6a5422d32287e9496f3e9728ae684e1ef04fdc7cf`

The prior experiment established V1 sufficiency, not field-level minimality, optional-schema compatibility, or final versioning.

### Repository heads inspected before execution

No expected research branch had advanced, so no substitution was required.

| Repository / surface | Exact SHA used | Observation |
|---|---|---|
| Evidence Bundler `research/contract-b-seam-shadow` | `b4ca9111f5957ef7e7955e2c5024f2280ee19eb5` | Same pinned seam head as prior experiment |
| Claim Audit Lab `research/obligation-composition-shadow` | `6acc3462dad73959ccec6bccf8407215f5274cf6` | Same pinned consumer-research head as prior experiment |
| Apparatus `research/contract-b-cal-consumer-candidate` | `63e8506396132a44ebc0e6c2312047e99b1125eb` | Same candidate/profile head as prior experiment |
| Apparatus prior conformance report | `f4ee2dbd853821ba54328156bbab1c71235fae55` | Experimental parent |
| Tightened optional-extension / ablation execution | `8a9d30871e54a60b4e39e79a27a500474b5e51d2` | Research-only experiment head used for final evidence |

The canonical `main` branches were older than these research heads. The seam work had not silently entered the released Contract B surface.

---

## Phase 1: Capability extraction

V1 was translated into semantic capabilities before designing an extension. Its object shape was not copied into canonical Contract B.

The V1 preregistration explicitly describes a **complete retrieval/admission ledger**, coverage/search facts, provenance-bound context facts, and immutable identities, while excluding proposition-specific CAL judgments.

### Candidate capability families and prior justification

| Capability family | Prior observation justifying inclusion | Ownership interpretation |
|---|---|---|
| Claim identity / origin / atomicity state | V1 preserved claim context unavailable in the current-C-B-shaped projection; the prior CAL measurement view consumed that state | Evidence-world / handoff metadata, not a support judgment |
| Provenance-bound source/context facts | Prior Rung 1 and Rung 3 required mechanically supplied facts and showed CAL should not rediscover them | Upstream factual state |
| Representation-bound passage anchors / provenance | V1 preserved passage identity, exact representation anchors, and passage hashes; V0 lacked the generalized representation context | Upstream factual/provenance state |
| Retrieval nomination history | Prior nomination mutations changed the auditable V1 handoff while leaving CAL semantic measurement invariant | Audit provenance only, not semantic authority |
| Admission / review history | Prior non-destructive filtering and rejected-candidate recoverability required retention of preparation history | Audit/reconstruction state, not CAL verdict state |
| Coverage / aperture observations | Prior V1 carried candidate/review/admission observations and search-scope facts without an upstream completeness conclusion | Evidence aperture facts |
| Search scope | Prior V1 distinguished search/corpus observations from proposition-specific completeness | Evidence aperture facts |
| Explicit limitations / unknown / absence state | Prior experiment required fail-closed handling rather than invented defaults | Epistemic state |

### Explicitly excluded from the candidate extension

No authoritative upstream field was introduced for:

- support or refutation;
- semantic validity;
- temporal applicability judgment;
- authority or supplier applicability judgment;
- completeness conclusion;
- decision participation;
- verdict or abstention.

The executed capability ledger contained no proposition-specific CAL judgment keys.

---

## Phase 2: Optional-extension compatibility probe

The research candidate used an **optional hash-bound companion capability ledger**, not new inline fields in the strict canonical claim/source/passage models.

This packaging hypothesis was chosen for testing because current Contract B already behaves as a multi-file artifact and the locked integrity verifier checks files named in `SHA256SUMS`. The hypothesis was then tested rather than assumed.

### C1: Untouched legacy artifact

**Result: PASS**

A real legacy Contract-B fixture from the pinned CAL research tree was run through the existing locked Apparatus verifier.

- Existing verifier: passed.
- Artifact tree digest before verification: `sha256:bc195d8b7f1cb4c8a422eed30b4b2e329404576d9c69e57194ae0563da921159`
- Artifact tree digest after verification: identical.
- No extension file or synthetic field was added.

Observation: a current legacy C-B artifact can remain valid and unchanged.

### C2: V1-capable artifact

**Result: PASS**

The research consumer loaded legacy C-B state plus an optional companion ledger containing the extracted V1 factual capabilities.

- Candidate capability-ledger hash: `sha256:f322abf653b7fd14386eb21491868aec8eae6f6f31f2f686e43ca34992311f1a`
- Extension validation errors: none.
- Proposition-specific CAL keys in the extension: none.
- Reconstructed CAL pre-assessment measurement-view hash: `sha256:b18715b861343a541fd8317d38cfa3b4f6acf2efdcb9578fac55313bf721f8db`
- Prior V1 measurement-view hash: identical.

Observation: the demonstrated V1 evidence-world state can be carried through an optional companion without changing the legacy inline payload shape.

### C3: Legacy absence semantics

**Result: PASS**

The probe represented and observed three distinct states:

| Condition | Research semantic state |
|---|---|
| Field present with known false | `state=known, value=false` |
| Field present but value unknown | `state=unknown, value=null` |
| Extension absent because artifact predates extension | `state=legacy_absent, value=null` |

These states did not collapse.

### C4: Fail-closed legacy CAL consumption

**Result: PASS**

When the optional extension was absent, the research CAL intake returned:

- status: `limited`;
- absence semantics: `legacy_absent`;
- explicit unknowns for missing extension capabilities;
- fabricated defaults: none.

The unknown list included claim origin, claim atomicity, source context facts, representation anchors, coverage state, search scope, and limitations.

Observation: legacy absence does not force CAL to fabricate factual values.

---

## Packaging control: inline payload versus bound provenance ledger

A second control tightened the first run by exercising an actual Contract-B artifact through the locked verifier.

### Negative control: unbound companion

An extra companion file was placed beside the canonical artifact but was not listed in `SHA256SUMS`.

- Canonical payload files unchanged: yes.
- Existing verifier accepted the artifact: yes.
- Companion integrity was not covered by the artifact checksum index.

Interpretation: mere colocated presence is not an acceptable auditability binding.

### Bound companion

The same research companion was added and listed in `SHA256SUMS`.

- Canonical payload files unchanged: yes.
- Existing verifier accepted the artifact: yes.
- Companion SHA-256: `cfb9ef3cfbd1bd6022155df67ec12dfc8931e65e9322f2e320ed006eb4c21b69`
- Companion was explicitly listed in the integrity index: yes.

### Tamper control

The checksum-bound companion was then changed without updating `SHA256SUMS`.

- Existing verifier rejected the artifact.
- The verifier reported a hash mismatch for the extension file.
- Tampered digest observed: `c2dda4564179e3b62dc1288aa14fa63daab668ae1695261b4d44aa9f363cc9bf`

**Observed packaging result:** a checksum-bound additive companion can be carried by the existing artifact-integrity mechanism without rewriting canonical inline payloads. An unbound companion cannot provide the same integrity property.

This proves additive carriage and integrity binding. It does **not** prove a final extension filename, discovery protocol, production schema, or semantic version.

---

## Phase 3: Ablation matrix

The baseline froze all other V1 capabilities while removing one family at a time.

`Measurement equivalent` below means equality with the prior successful V1 CAL pre-assessment measurement-view hash. It is deliberately not treated as the only success criterion.

| Ablated capability family | Outcome | Measurement equivalent | Required property lost |
|---|---|---:|---|
| Claim origin / atomicity | **BROKEN** | No | Claim-origin provenance and known atomicity state |
| Provenance-bound source metadata | **BROKEN** | No | Source identity/provenance binding used for reconstruction |
| Context facts | **BROKEN** | No | Required mechanical facts and provenance for those facts |
| Typed representation anchors | **BROKEN** | No | Exact representation-bound anchor reconstruction |
| Passage hashes | **BROKEN** | No | Passage-level integrity / exact representation binding |
| Nomination history | **BROKEN** | **Yes** | Nomination provenance and reconstruction of how a candidate entered the aperture |
| Admission / review history | **BROKEN** | **Yes** | Review/admission reconstruction and rejected-candidate recoverability |
| Coverage counts as stored fields | **EQUIVALENT** | **Yes** | Only redundant explicit count representation; counts remained derivable from complete history |
| Search scope | **HONESTLY DEGRADED** | No | Search/aperture scope and explicit closed-world state become unknown |
| Limitations / explicit unknown state | **HONESTLY DEGRADED** | No | Explicit limitation statement becomes unknown |

No required-family ablation produced **SEMANTIC LEAK**.

### Micro-ablations used to localize the result

| Micro-ablation | Outcome | Observation |
|---|---|---|
| Claim origin only | **BROKEN** | Claim-origin provenance is lost |
| Claim atomicity only | **HONESTLY DEGRADED** | CAL can remain fail-closed with atomicity explicitly unknown |
| `candidate_count` only | **EQUIVALENT** | Derived from complete review history |
| `reviewed_count` only | **EQUIVALENT** | Derived from complete review history |
| `admitted_count` only | **EQUIVALENT** | Derived from complete review history |

An exploratory `source_trust_level` micro-ablation was also run, but its classifier coupled trust metadata to the broader source-provenance property. Its machine label is therefore **not used in the disposition**. Prior CAL evidence already showed trust does not alter the semantic measurement path, and current Contract B already carries trust metadata. Whether trust belongs in any future extension remains outside what this experiment proved.

---

## What the ablations establish

### Capabilities proven necessary for the preregistered property set

The experiment provides direct evidence that the following capabilities cannot be removed while preserving the full preregistered consumer + auditability property set:

1. claim-origin provenance;
2. provenance-bound mechanical/source-declared context facts;
3. source/passage identity and integrity binding;
4. representation-bound typed anchors;
5. complete nomination history;
6. complete admission/review history, including recoverability of rejected-candidate records;
7. search/aperture scope if full V1 pre-assessment context is required;
8. explicit limitations/unknown state if full V1 pre-assessment context is required.

Claim atomicity is weaker evidence: removing it caused an honest degradation rather than fabrication or loss of ledger reconstruction. A minimal extension can therefore make the value optional and explicitly unknown, rather than requiring every producer to know it.

### Fields proven removable

The following V1 stored fields were removable without loss of any preregistered property in the tested V1 semantics:

- `candidate_count`;
- `reviewed_count`;
- `admitted_count`.

The values were reconstructed exactly from the complete retrieval/admission/review ledger.

This is not merely an accidental convenience of the frozen fixture. The V1 preregistration itself specifies a **complete retrieval/admission ledger**. Under that invariant the explicit counts duplicate information already present in the retained history.

The empirical result is still based on one frozen evidence world, so the generality of the count-derivation rule should be stress-tested before production design.

### Capabilities required for auditability but not semantic measurement

Two ablations are especially discriminating:

- Removing nomination history left the CAL semantic measurement hash unchanged but destroyed nomination reconstruction.
- Removing admission/review history also left the semantic measurement hash unchanged but destroyed admission/review reconstruction and rejected-candidate recoverability.

These are direct demonstrations that semantic-measurement invariance is not a sufficient minimality criterion.

Claim/source/passage lineage and integrity data also carry primarily provenance/reproducibility value even when a particular NLI-style measurement would not react to them.

### Capabilities used by CAL semantic/pre-assessment intake

The prior V1 measurement view and this ablation probe support retaining:

- provenance-bound mechanical context facts;
- admitted evidence references and exact representation anchors;
- search/aperture observations;
- explicit limitation/unknown state;
- claim context sufficient to avoid rediscovery or invention.

Nomination scores/roles/history and admission history remain auditable but must not become semantic evidence weights merely because they cross the seam.

---

## Phase 4: Minimal candidate capability set

The experiment does not justify copying the V1 research object into production. It supports a smaller capability delta that reuses facts already present in current Contract B and carries only missing state.

### Existing Contract-B capabilities that should be referenced, not duplicated

Current C-B already has important identifiers/provenance, including claim IDs/text, source IDs/content hashes/trust metadata, passage IDs/text/hashes/character offsets, and passage provenance.

A minimal extension should bind to those existing records rather than introduce duplicate source or passage payloads solely to recreate the V1 object shape.

### Exact proposed capability delta, not a production schema

1. **Optional extension presence and discovery state**
   - Extension absent on a legacy artifact must mean `legacy_absent`, not known false and not explicit unknown.
   - When present, the extension must be integrity-bound to the C-B artifact.

2. **Claim lineage/context capability**
   - A stable claim-origin / lineage reference sufficient to reconstruct where the claim came from.
   - Atomicity/structure state may be supplied when known; absence inside an extension must remain explicit unknown rather than a fabricated default.

3. **Provenance-bound factual-context capability**
   - Mechanically extracted or source-declared factual records needed downstream.
   - Each fact must retain source/passage provenance and its representation/value basis.
   - No proposition-specific applicability, validity, support, or verdict semantics.

4. **Representation-anchor capability**
   - Typed anchors that can identify page, section, table, row, sheet, or equivalent representation coordinates where simple character offsets are insufficient.
   - Anchor records should bind to existing passage IDs/hashes rather than duplicate canonical passage text or hashes.

5. **Complete nomination / admission / review ledger capability**
   - Candidate identity/reference.
   - Nomination provenance sufficient to reconstruct how the candidate entered the aperture.
   - Review/admission decision and basis.
   - Recoverable record/reference/hash for rejected candidates.
   - A declared completeness invariant for the ledger itself.
   - Nomination metadata remains audit provenance and is blinded from CAL semantic measurement.

6. **Search/aperture observation capability**
   - Search/source scope and selection basis.
   - Explicit closed-world knowledge state that can distinguish known true, known false, and unknown.
   - Explicit limitations / unknowns.
   - `candidate_count`, `reviewed_count`, and `admitted_count` are derived views when the complete ledger invariant holds, not required stored facts.

7. **Integrity binding capability**
   - The optional companion must be bound by `SHA256SUMS` or a semantically equivalent C-B integrity mechanism.
   - An unbound colocated sidecar is insufficient for the auditability property demonstrated here.

### Where the evidence favors a bound ledger over inline canonical fields

The observed data favor keeping history-heavy state outside the strict canonical inline claim/source/passage payloads when a checksum-bound extension ledger is available, especially:

- nomination history;
- admission/review history;
- rejected-candidate reconstruction records;
- provenance-bound context-fact catalogue;
- aperture/search observations and limitations.

This is an evidence-driven packaging preference, not a final schema decision. The companion remained optional for legacy artifacts and preserved integrity when present.

---

## Hard falsifiers

| Hard falsifier | Triggered? | Evidence |
|---|---:|---|
| 1. Unchanged legacy C-B artifacts cannot remain valid | No | C1 passed unchanged |
| 2. Required new fields cannot honestly be optional | No | Legacy absence fail-closed; V1 companion optional |
| 3. Existing fields require incompatible reinterpretation | No observed evidence | Candidate reused legacy payload and added separate capability state |
| 4. Legacy absence becomes indistinguishable from false/unknown | No | C3 preserved all three states |
| 5. CAL must fabricate defaults when extension absent | No | C4 fabricated none |
| 6. Correct preservation requires mandatory new packaging | No | Optional checksum-bound companion worked while untouched legacy remained valid |
| 7. V1 contains substantial fields removable with no loss of preregistered property | **YES** | All three explicit coverage counts were equivalent when derived from complete history |
| 8. Candidate requires proposition-specific CAL semantics upstream | No | No such keys entered the extension |

Hard falsifier 7 is sufficient to reject the original field-level minimality hypothesis and therefore the conjunctive claim.

---

## Observed evidence

1. The prior successful V1 measurement view was reproduced exactly from legacy C-B plus an optional factual capability ledger.
2. Untouched legacy C-B remained byte-for-byte unchanged and passed the locked verifier.
3. Known false, explicit unknown, and legacy absence remained distinct states.
4. CAL research intake failed closed on legacy absence and invented no defaults.
5. A checksum-bound companion passed the existing artifact-integrity verifier without modifying canonical payload files.
6. Tampering with the bound companion was detected by the existing checksum mechanism.
7. An unbound companion was accepted but not integrity-protected, demonstrating why binding is a required part of the packaging hypothesis.
8. Removing nomination or admission/review history did not affect semantic measurement but did destroy preregistered reconstruction properties.
9. Removing stored coverage counts did not lose consumer, auditability, provenance, or reconstruction properties because complete review history deterministically reconstructed them.
10. No required-family ablation forced proposition-specific CAL semantics upstream.

---

## Inference

The strongest supported architectural inference is narrower than the original V1 shape:

- **An optional Contract-B factual-context extension is feasible in principle without invalidating legacy artifacts.**
- **A hash-bound companion ledger is sufficient for the tested packaging and integrity properties, so the evidence does not require placing all V1 state inline in canonical C-B payloads.**
- **The original V1 representation is not minimal because explicit coverage counts duplicate information in the preregistered complete history ledger.**
- **History that is irrelevant to semantic measurement can still be mandatory for audit reconstruction.**

The experiment therefore reduces the candidate surface rather than simply confirming V1.

---

## Falsified hypotheses

1. **Original V1 field-level minimality:** falsified by the coverage-count ablations.
2. **Semantic-measurement invariance implies a capability is unnecessary:** falsified by nomination-history and admission/review-history ablations.
3. **A colocated sidecar is sufficient audit packaging without explicit integrity binding:** falsified by the unbound-companion negative control.

The optional-extension compatibility hypothesis was not falsified by the executed controls.

---

## Remaining unknowns

1. Whether coverage counts remain safely derivable across multiple evidence worlds involving deduplication, re-review, partial runs, interrupted retrieval, or deliberately incomplete history.
2. What exact invariant establishes that a nomination/review ledger is complete enough for count derivation.
3. Whether rejected candidate **content** must cross the seam or whether a bound record/hash/reference is sufficient. This experiment establishes history recoverability, not full rejected-content carriage.
4. Whether claim atomicity deserves a standard extension field or should remain an optional explicitly-known/unknown observation.
5. Whether source trust belongs only in existing C-B metadata, in downstream policy receipts, or in any extension. This experiment does not resolve that ownership question.
6. The final discovery mechanism for an extension-aware consumer. The old verifier can integrity-bind an additional file, but it does not understand the file's semantics.
7. Whether standardizing an optional companion artifact path/discovery contract can be done without a packaging/version rule that changes the semantic-version implication.
8. Whether generic typed factual predicates or a smaller set of dedicated context structures produces the better stable contract.
9. Whether the optional-extension result survives multiple independent consumers rather than only the research CAL adapter.

---

## Disposition

### Overall claim

**FALSIFIED**

Reason: the optional-extension clause is supported, but the no-removable-capability / original V1 minimality clause is false under the preregistered complete-ledger semantics. Hard falsifier 7 fired.

### Optional-extension subclaim

**SUPPORTED within the bounds of this experiment**

Legacy artifacts remained valid; the V1 evidence-world state was recovered exactly from an optional companion; absence semantics remained explicit; CAL failed closed; checksum binding provided artifact integrity.

### Minimality subclaim

**FALSIFIED for the original V1 field representation**

The stored coverage-count fields are redundant under the complete-history invariant.

---

## Version implication

**UNRESOLVED**

The previous provisional intuition that an optional factual-context extension might be a MINOR change remains plausible for a **reduced** extension surface, but this experiment does not support assigning MINOR to the original V1 field set.

Why the result stops at UNRESOLVED:

- one hard falsifier forced the candidate delta to change;
- the current verifier's ability to carry an extra checksum-bound file is not itself a semantic-versioning proof;
- the final extension discovery and validation semantics have not been tested across old and new consumers;
- production packaging rules have intentionally not been changed.

No PATCH, MINOR, or MAJOR version is assigned here.

---

## Failed runs and deviations preserved

### Execution environment deviation

The live Conduit tunnel was unavailable during the experiment, and a direct local clone path did not have working GitHub network resolution. No completion claim was inferred from those failures.

The experiment was executed instead through GitHub Actions against exact pinned public SHAs. This changed the execution surface, not the experimental inputs.

### Initial packaging-probe limitation

The first successful optional-extension run, GitHub Actions run `33072203598`, tested extension validation and consumer reconstruction but did not yet place the companion inside a real C-B artifact and run that package through the locked verifier.

That run was preserved as preliminary evidence rather than silently overwritten.

The limitation was corrected with:

- tightened optional-extension / ablation run `33072532042`;
- bound-companion packaging control run `33072532129`.

Both completed successfully at research execution head `8a9d30871e54a60b4e39e79a27a500474b5e51d2`.

### Exploratory source-trust ablation limitation

The source-trust micro-ablation reused a broader source-provenance property and therefore cannot isolate the trust field cleanly. Its classification is excluded from the final disposition. A dedicated trust-ownership experiment would be required if that question becomes decision-relevant.

---

## Next discriminating experiment

### Contract B reduced-extension round trip across multiple evidence worlds

Do **not** proceed to Contract C yet.

The next experiment should test the reduced candidate itself, especially the count-derivation and extension-discovery assumptions that now carry the most weight.

Use at least three frozen C-B evidence worlds:

1. **Complete mixed-decision ledger:** multiple accepted and rejected candidates, with deterministic candidate/review/admission count derivation.
2. **Interrupted or explicitly incomplete ledger:** the extension must declare ledger incompleteness and CAL must treat derived counts/aperture as unknown rather than silently calculating misleading totals.
3. **Deduplication / re-review world:** repeated nominations, deduplicated passages, and at least one review state transition to test whether the ledger semantics still determine counts unambiguously.

Build a research-only extension-aware loader/validator that:

- accepts untouched legacy artifacts unchanged;
- discovers the companion only when present;
- requires integrity binding for a present companion;
- distinguishes legacy absence from explicit unknown/false;
- validates the complete-ledger invariant;
- derives coverage counts rather than requiring them;
- rejects or flags any optional stored count that disagrees with the ledger;
- feeds CAL without semantic leakage or fabricated defaults.

### Discriminating falsifiers for the next experiment

Revise the reduced candidate if any of the following occur:

- candidate/review/admission totals cannot be derived unambiguously from the ledger semantics;
- declaring ledger incompleteness still allows a consumer to mistake partial counts for complete aperture facts;
- extension discovery requires reinterpretation of legacy canonical fields;
- old artifacts cannot remain valid while new extension-aware consumers fail closed;
- integrity binding requires a mandatory packaging change after all;
- a second independent consumer cannot reconstruct the same factual pre-assessment state.

That experiment should be the next Contract B gate. This report intentionally stops here.
