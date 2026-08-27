# Contract B/C chain alignment — RC0

**Status:** research alignment note  
**Scope:** Evidence Bundler → C-B → CAL → C-C → Decision Engine

## Why this note exists

The downstream Contract-C work depends on Contract B being semantically clean. The current repositories expose a real version/meaning mismatch that must not be hidden by the new contract.

## Observed state

The locked canonical vocabulary in `apparatus-contracts` still describes `audit_support_verdict` as one list containing support degrees and failure modes such as `overstated` and `needs_source`.

The live CAL v1 model has moved to a separated record:

```text
support_verdict:
  supported | partially_supported | unsupported | contradicted | not_checkable

audit_flags:
  overstated | inferred | source_scope_error | false_caution |
  missed_counterevidence | coverage_loss

citation_status:
  correct | partial | wrong_source | missing_needed | not_cited | not_applicable
```

CAL also carries explicit `not_checkable` reasons and audit confidence.

This is not a cosmetic naming drift. It changes the semantics available to downstream consumers.

## Alignment rule

Do **not** repair the mismatch by flattening live CAL back into the old single-axis vocabulary for Contract C.

Do **not** update the locked canonical C-B vocabulary merely because CAL code is newer.

Instead:

1. finish the current C-B conformance experiment;
2. decide the correct C-B evidence/assessment packaging;
3. explicitly version the canonical audit-result semantics;
4. then freeze Contract C against that result surface.

## Shared invariants for B and C

### Invariant 1 — preparation is not semantic audit

```text
EB nomination/admission metadata ≠ CAL support/refutation judgment
```

### Invariant 2 — audit is not downstream policy

```text
CAL support/flags/citation state ≠ Decision Engine promotion policy
```

### Invariant 3 — unknown stays unknown

Missing upstream fact, missing CAL assessment, and CAL abstention must not silently become favorable or adverse defaults at either seam.

### Invariant 4 — history is non-destructive

Evidence that becomes non-deciding remains in the retained C-B record. A CAL result that is later superseded remains reconstructable. A Decision Engine block does not delete the claim/source history.

### Invariant 5 — exact identity crosses both seams

C-B must identify the evidence world supplied to CAL. C-C must identify the exact C-B bundle and exact proposition CAL audited.

### Invariant 6 — each layer owns its policy

- EB owns evidence preparation/admission policy.
- CAL owns audit measurement/assessment/rules.
- Decision Engine owns destination decision policy.
- MainFrame owns durable lifecycle mutation in the first integration profile.

No layer should make the next layer's judgment in advance.

## Required Contract-B result before Contract C can lock

The C-B conformance work must establish, at minimum:

- what evidence-world/context facts cross;
- how admitted evidence remains available without support/counter lane bias controlling CAL;
- how retrieval/admission/aperture facts remain distinct from completeness judgment;
- how proposition-specific CAL assessments are represented and preserved;
- whether the CAL result is a resealed C-B derivative or a separate immutable result package;
- which controlled vocabulary/version becomes canonical.

## Required Contract-C result

Once that is stable, C-C must prove that Decision Engine can consume a minimal audit-result projection without reaching back into raw CAL telemetry or re-opening C-B evidence to recreate CAL's judgment.

## Practical versioning consequence

The existing global apparatus pin should not be bumped by guesswork.

If the C-B result semantics require incompatible required fields or replace the old mixed verdict vocabulary, the eventual canonical change is likely major for the existing contract family. Contract C may still have its own first released version, but its compatibility declaration must name the exact C-B/CAL result profile it consumes.

## Current disposition

- Contract-B seam: **supported candidate, real cross-repository conformance still required**.
- Contract-C seam: **structural shadow now defined in Decision Engine**.
- Old single-axis audit vocabulary: **do not propagate downstream**.
- Canonical version bump: **defer until tests classify the change**.
