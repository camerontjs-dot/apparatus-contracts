# Contract B Promotion-Gate Epistemic Compression

**Date:** 2026-08-27  
**Status:** supervisory promotion decision  
**Disposition:** **SUPPORTED FOR PROMOTION**  
**Production code changed by this review:** no  
**Research branches authorized for direct merge:** none  
**Contract C work:** prohibited

## Decision question

> Is there now enough evidence to move Contract B from research candidate to SUPPORTED FOR PROMOTION, and if so what is the smallest production change actually justified?

## Evidence reviewed

This disposition considers the evidence program as a sequence rather than treating the latest green run as sufficient by itself:

1. V0/V1/V2 conformance, report commit `f4ee2dbd853821ba54328156bbab1c71235fae55`.
2. Optional-extension + field-family ablation, report head `4fb5dcde81c3ae0a9a99133f6a3f721aeab639dc`.
3. Independent-consumer negative baseline, report head `40349629c289a340c95735510cf04b1926d200d0`.
4. Temporal/version applicability, execution head `41627c9a313ffd2c73d9b8ea54f1e018e2d676e7` including preserved failed CI and corrected final run.
5. RC1 explicit physical/normalization profile and code-isolated A/B baseline, report head `aa016bcebd57dd09870a9cd4cc129ea7f7f5fc43`.
6. RC1 preregistered metamorphic controls, decisive execution `15f9c45e973bfa80938a35bf98886e19335c1b78`, plus preserved apparatus-only failed run `33088001635` and Deviation 001.

Canonical production `main` remains at `17f13e77081816da809550154af2b9e2b72eb776`. No research result has silently entered the released contract.

## Observed evidence

### O1 — Current Contract-B-shaped state is insufficient for the tested CAL pre-assessment seam

V0 failed closed rather than constructing the required pre-assessment view. V1 supplied the missing evidence-world context and produced the required CAL measurement view without upstream proposition-specific CAL judgments.

### O2 — V1's original stored shape was larger than necessary

Field-family ablation falsified original V1 field-level minimality. `candidate_count`, `reviewed_count`, and `admitted_count` were redundant stored values when a complete nomination/admission/review history is retained and checked.

Nomination and review history could not be dropped merely because semantic measurement was invariant: removing those histories destroyed audit reconstruction properties.

### O3 — Additive optional carriage is feasible against the existing artifact mechanism

An unchanged legacy Contract-B artifact remained valid. A companion factual-context ledger could be added without rewriting the legacy inline payload and could be integrity-bound through the existing checksum mechanism. Tampering with a bound companion was rejected. An unbound colocated sidecar did not provide the required integrity property.

Legacy absence, explicit unknown, and known false were kept distinct in the compatibility probe, and legacy consumption failed closed without fabricated defaults.

### O4 — The first independent-consumer attempt falsified RC0 interface reproducibility

A genuinely frozen Consumer B, defined before reading Consumer A implementation logic, could not consume the same hash-matched V1 because RC0 failed to define physical shape, normalized-ledger target, canonicalization, absence/unknown encoding, and integrity envelope precisely enough.

That negative result is retained. It is not superseded as historical evidence; it identifies the defect the next revision had to repair.

### O5 — RC1 repairs the identified interface ambiguity on the frozen evidence world

RC1 explicitly fixes the research V1 root, distinguishes the full non-destructive intake ledger from the blinded semantic payload, specifies field inclusion/exclusion, ordering/canonicalization, unknown normalization, count derivation, and the B/CAL ownership boundary.

Two code-isolated implementations in different languages then produced byte-identical full ledgers and byte-identical semantic payloads from the same frozen V1.

Observed baseline hashes:

- V1: `sha256:a861eeafe9a360e9280e2d2c092bd2bbcdee6661c55412802be6fecbf8c7b2d7`
- normalized intake ledger: `sha256:5e168cf01e3e187280a3ea3cca9fe8b88741e3e015616aca50f6043a4a310c57`
- blinded semantic payload: `sha256:814d5966f876a26bca40e2fc189134ea3921736b5a92e8bd6ec30a3a392b54dc`

### O6 — RC1 survived the previously deferred metamorphic controls

The preregistered RC1 control suite passed all checks after one preserved pre-execution harness failure and a narrowly documented apparatus correction.

Observed properties include:

- nomination rank/score/role mutation changed auditable history but left semantic payload invariant;
- hostile downstream CAL judgment injection entered neither canonical B ledger nor semantic payload;
- missing and explicit-null atomicity both normalized to explicit unknown;
- declared unordered collection permutations normalized away;
- hash corruption failed closed before output;
- inconsistent stored coverage counts failed closed against complete history.

The decisive evidence artifact is `9653086317`, ZIP SHA-256 `sha256:d6485dfe7ff833470e21bf96879bb31101cf3e37c6b074fe65f54d0903392ad7`.

### O7 — Temporal/version ownership is behaviorally separable

The temporal/version experiment showed that provenance-bound version/effective/context facts can cross Contract B while CAL derives proposition-specific current/stale/applicability state downstream. A source-context conflict with unchanged semantic payload caused the CAL-side research assessment to refuse rather than silently accept contradictory upstream metadata.

### O8 — Production governance classifies the candidate as additive, not a documentation-only fix

Canonical Contract governance states:

- new required field → MAJOR;
- new optional field → MINOR;
- vocabulary addition → MINOR;
- documentation-only clarification → PATCH.

The current machine-readable contract pin is `1.1.0`.

## Inference

The accumulated evidence is now sufficient to promote a **bounded capability/interface change**, not the research implementation.

The decision is supported because the principal promotion-risk claims have been attacked independently enough to discriminate the architecture:

- semantic sufficiency was tested against weaker/stronger handoffs;
- unnecessary V1 surface was removed by ablation;
- additive compatibility and integrity were tested with positive and negative controls;
- an upfront frozen independent consumer produced a real failure that exposed specification ambiguity;
- the revised specification repaired exactly those ambiguities;
- separately coded consumers converged afterward;
- mutation/metamorphic controls tested boundary invariants rather than only the happy path;
- temporal ownership was tested with counterfactual worlds and a conflict control;
- failed apparatus runs and corrections remain visible.

The strongest possible independent-authorship test, a new Consumer C built in a separately isolated supervisory context from RC1 alone, remains unexecuted. That limits the claim to the tested interface and first-party ecosystem. It is **not treated as a hard promotion blocker**, because the evidence already contains a legitimately frozen pre-inspection Consumer B failure, code-isolated cross-language convergence after specification repair, and the relevant metamorphic controls. Promotion must not be described as universal interoperability.

## Minimum demonstrated Contract B capability set

The production delta should preserve only capabilities supported by the evidence, reusing existing Contract-B claim/source/passage identities rather than duplicating payloads:

1. **Optional extension presence/discovery state**
   - legacy absence is explicitly distinguishable from an extension-aware unknown value;
   - when present, the extension is integrity-bound to the Contract-B artifact.

2. **Claim lineage/context**
   - stable origin/lineage sufficient for reconstruction;
   - atomicity/structure may be known or explicit unknown, and must not be fabricated.

3. **Provenance-bound factual context**
   - source-declared or mechanically extracted facts needed downstream;
   - each fact retains value basis and source/passage provenance;
   - version/effective-date facts may be included as factual context.

4. **Typed representation anchors**
   - page/section/table/row/sheet or equivalent coordinates where existing offsets are insufficient;
   - bind to existing passage identity/integrity rather than duplicate passage content.

5. **Complete nomination/admission/review history**
   - candidate reference;
   - nomination provenance;
   - review/admission outcome and basis;
   - recoverable rejected-candidate record/reference;
   - explicit completeness invariant for the history;
   - history is non-authoritative for CAL semantic measurement.

6. **Search/aperture observations and limitations**
   - search/source scope and selection basis;
   - closed-world knowledge state with explicit known/unknown semantics;
   - explicit limitations/unknowns;
   - candidate/reviewed/admitted counts are derived/checkable views, not independent canonical facts when complete-history invariant holds.

7. **Canonical normalization rules for the CAL intake boundary**
   - deterministic field inclusion/exclusion;
   - deterministic ordering for declared unordered collections;
   - canonical serialization/hash rules;
   - full audit/intake ledger separated from the narrower semantic-measurement payload.

## What Contract B must not own

Promotion must not introduce authoritative upstream fields for:

- proposition-specific support/refutation;
- semantic validity;
- temporal/lifecycle applicability judgment;
- authority/supplier applicability judgment;
- proposition-specific completeness conclusion;
- decision participation;
- CAL verdict or abstention.

Factual inputs to those assessments may cross B with provenance. The judgment remains CAL-owned.

## Backward compatibility decision

**Supported for the bounded additive strategy, conditional on the fresh production PR reproducing the existing controls.**

The evidence supports an optional, integrity-bound companion/capability surface that leaves legacy inline Contract-B payloads valid and permits extension-unaware legacy behavior to remain fail-closed/limited rather than fabricated.

This does not establish compatibility with every possible third-party consumer. The production claim should be:

> Backward-compatible additive Contract-B extension for the tested legacy verifier and first-party consumer behavior, with legacy artifacts remaining valid.

Do not claim universal ecosystem compatibility.

## Independent-consumer decision

The research history contains two distinct facts:

1. RC0 was **NOT REPRODUCIBLE** by an upfront frozen Consumer B without hidden conventions.
2. RC1 is **deterministically reproducible across two code-isolated, cross-language implementations** on the frozen V1 and remains equivalent across the preregistered mutation suite.

A fully separately authored Consumer C is still an unknown. This is recorded as residual evidence debt, not erased and not upgraded into a completed independent-reproduction claim.

## Temporal/version decision

**Supported.**

Contract B owns provenance-bound temporal/version observations and contradictions. CAL owns proposition-specific applicability/current/stale/refusal assessments.

## Contract C / CAL result artifact decision

A separate CAL result artifact is **not required to promote Contract B**.

The earlier research comparison provides evidence that a separate immutable-B-bound CAL result may produce cleaner semantic ownership than resealing B, but canonicalizing CAL output is a downstream Contract-C decision. Starting it now would enlarge the B promotion surface without evidence that B requires it.

Therefore Contract C remains explicitly out of scope.

## Version decision

**MINOR.**

The current contract pin is `1.1.0`; therefore the smallest production version candidate is **`1.2.0`**.

Reason:

- PATCH is insufficient because the supported change creates a new optional contract/interface surface, not documentation-only clarification.
- MAJOR is not justified because the tested strategy preserves legacy artifacts and does not require reinterpretation of existing required fields.
- MINOR matches the canonical governance rule for additive optional fields/capabilities.

The release number remains a candidate until the fresh production PR passes its required cross-repo conformance and compatibility checks.

## Falsified alternatives

The evidence now rejects, within tested scope:

1. Current/V0 Contract-B state is already sufficient for the CAL pre-assessment seam.
2. V1 should be promoted wholesale.
3. Stored candidate/reviewed/admitted counts are necessary canonical facts.
4. Semantic-measurement invariance is enough to declare nomination/review history unnecessary.
5. An unbound sidecar is sufficient audit packaging.
6. Proposition-specific CAL judgments need to cross B.
7. Temporal applicability should be decided upstream.
8. RC0 prose semantics already defined a reproducible interface.
9. Hidden implementation conventions are unavoidable once the interface is made explicit.
10. Research branches themselves are production-ready artifacts.

## Remaining hypotheses and unknowns

1. A separately authored Consumer C will reproduce the promoted interface from spec alone.
2. The complete-history/count-derivation invariant will hold across interrupted retrieval, re-review, deduplication, partial runs, and deliberately incomplete histories.
3. The exact production extension filename/discovery syntax has not been empirically selected. This is an implementation/ADR choice constrained by the proven optional + integrity-bound properties.
4. Third-party ecosystem compatibility is unknown.
5. Generalization beyond the tested evidence worlds remains to be accumulated through future producer/consumer use.

None of these unknowns currently requires expanding the production capability set.

## Promotion disposition

# SUPPORTED FOR PROMOTION

This means:

- the **bounded Contract-B capability change** is supported;
- the research implementations and branches are **not** authorized for direct merge;
- a fresh production branch/PR from canonical `main` is justified;
- the production PR should be smaller than the research history and contain only the supported contract/interface delta plus its verification surfaces.

## Exact next production action

Create a fresh branch from canonical `main` using the production-governance class, e.g.:

`promotion/contract-b-factual-context-extension-v1.2`

The production PR should implement **one optional, integrity-bound Contract-B factual-context/audit-history extension surface** plus its normative schema/profile, discovery rule, explicit absence/unknown semantics, canonicalization rules, and verifier tests.

It must:

- reuse existing claim/source/passage identities rather than copy the research V1 object wholesale;
- omit stored coverage counts as independent facts when complete history is present;
- prohibit proposition-specific CAL judgment keys;
- define version/effective-date values as factual provenance only;
- distinguish full audit/intake normalization from blinded semantic input;
- keep legacy artifacts valid unchanged;
- bind the extension into `SHA256SUMS` or the canonical equivalent;
- add positive legacy/new-artifact controls and tamper/unknown/count-consistency/semantic-blinding tests;
- update the ADR/DECISIONS record before or with implementation;
- update the machine-readable contract version from `1.1.0` to candidate `1.2.0` only as part of this bounded promotion;
- run producer → contract → consumer conformance across Evidence Bundler, Apparatus Contracts, and Claim Audit Lab before merge/release.

Do not copy or merge the research branch into `main`. Re-implement the supported semantics cleanly from this disposition and the normative RC1 evidence.

Do not begin Contract A redesign or Contract C until Contract B production promotion is completed and its repo/PR evidence is reconciled.