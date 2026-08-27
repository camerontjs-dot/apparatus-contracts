# Cross-instrument coordination brief

**Status:** Coordination note, non-normative
**Updated:** 2026-08-27
**Released contract:** Contract B v1.1.0 on [`main`](../../schema/.contract-version)

## Why this exists

The [Research Scaffold Harness](https://github.com/camerontjs-dot/research-scaffold-harness),
[Evidence Bundler](https://github.com/camerontjs-dot/evidence-bundler),
[Claim Audit Lab](https://github.com/camerontjs-dot/claim-audit-lab), and
[Decision Engine](https://github.com/camerontjs-dot/decision-engine) are separate
instruments. Their work can move in parallel, but the boundaries between them
cannot be left to whichever implementation thread happens to arrive first.

This note is the shared correspondence surface for those threads. It records the
smallest ownership rules that the private seam work has made explicit. It does
not change the locked contract, assign a production version, or authorize a
research branch to merge.

## Current public state

`main` remains the released Contract B v1.1.0 baseline. The public research
program is carried on separate branches:

- [Contract B RC1 promotion-gate research](https://github.com/camerontjs-dot/apparatus-contracts/tree/research/contract-b-promotion-gate-rc1)
  records a reproducible, code-isolated two-consumer baseline and a bounded
  promotion recommendation.
- [Contract B RC1 metamorphic controls](https://github.com/camerontjs-dot/apparatus-contracts/tree/research/contract-b-rc1-metamorphic-controls)
  records the tested mutation, unknown-state, ordering, integrity, and
  count-consistency controls.

Those results are evidence for a fresh production review. They are not a
production Contract B, are not a universal interoperability claim, and do not
start Contract C. The next production change must be reimplemented from the
reviewed boundary, with the existing legacy artifact path kept valid.

## Ownership rules across the pipeline

### C-A: preserve the original claim upstream

The Harness or a separately governed claim-formation step owns the original run
record, candidate claims, source and passage identity, and their provenance.

If a claim is decomposed, preserve the parent claim and the derived proposition
graph. A decomposition is a transformation, not a replacement. The artifact
must say who declared it and bind that declaration to a real source artifact.

In particular:

- a model-generated proposal must not be labelled `operator_declared` without
  the corresponding authority;
- `model_authored` is the honest provenance value when a model authored the
  structure;
- an atom provenance hash must bind a distinct source artifact, not the atom
  text itself; and
- Evidence Bundler and CAL must not infer or silently rewrite the decomposition
  from prose.

These are coordination requirements for the next C-A revision. They are not a
silent amendment to the released v1.1.0 schema.

### C-B: carry evidence-world facts, not CAL judgments

Evidence Bundler owns evidence preparation and integrity sealing. The C-B handoff
may carry provenance-bound source, passage, version, effective-date, search, and
representation facts, along with complete nomination and admission history.

The rule that keeps recurring in the private seam work is:

> If a fact can be declared at a seam, the contract carries it and no consumer
> re-derives it downstream.

That means `source_id`, `section`, and any declared `source_boundary` travel as
declared fields. A consumer must not recover them by parsing passage prose when
the handoff already carries them. Stored candidate/reviewed/admitted counts are
checkable views when complete history is present, not independent authority.

The C-B handoff must not become an upstream CAL result. It must not introduce
authoritative fields for semantic support, refutation, temporal applicability,
authority applicability, proposition completeness, decision participation, or
CAL verdict/abstention. Those assessments belong to CAL and require their own
trace.

### CAL: audit the supplied proposition and frozen evidence

CAL receives the proposition it is asked to audit and the immutable evidence
world supplied by C-B. It may apply its declared rules to that input, but it
must not silently invent atoms, promote EB nomination metadata into semantic
support, or accept a colocated upstream judgment as its own result.

The complete intake/audit history and the narrower semantic-measurement payload
are different views. Preparation history should remain reconstructable even when
it is intentionally excluded from the blinded semantic payload.

Older private design work also identified three fields that must not be quietly
collapsed during a future result-shape revision:

- `contradicted` is not the same outcome as `unsupported`;
- a confidence band is not the same quantity as a numeric margin or score; and
- `citation_status` should not be retained as a required fact if the evidence
  world cannot make it informative.

Those are downstream result-contract questions. They are deliberately not being
resolved by this coordination note or by the RC1 research profile.

### C-D / Contract C: CAL reports, Decision Engine decides

The Decision Engine consumes a typed CAL result and applies a declared decision
shape and tradeoff policy. It must not reconstruct a verdict from raw entailment
signals or silently map an abstention to rejection.

The handoff should retain the CAL instrument identity, rules/config hashes,
certainty information, close-call state, and the reason for an abstention. The
decision shape, constraints, and weights come from the decision caller; the
Decision Engine must not invent them from the audit result.

Contract C remains downstream of the Contract B production decision. The current
Decision Engine seam is a candidate design, not a released contract.

### C-0 and shortlist controls stay outside C-B

Source-eligibility and shortlist controls are useful control-plane experiments,
but they are not evidence-bundle semantics. They must not be smuggled into C-B
as if a shortlist receipt were a C-B artifact, and they do not authorize a
schema or version change here.

## Cross-instrument handoff table

| Instrument | Owns | Must preserve or emit | Stop condition |
| --- | --- | --- | --- |
| Research Scaffold Harness | Original run and candidate-claim record | run identity, model/config provenance, original claims, source/passage identity, declared claim structure | missing provenance, fabricated declaration authority, or hash that binds the wrong object |
| Evidence Bundler | Evidence preparation and C-B sealing | immutable C-A lineage, source/passage hashes, declared context, complete nomination/admission history | corpus or source mismatch, unlisted files, or a transformation that is not recorded |
| Claim Audit Lab | Proposition-level evidence assessment | its own rule/config identity, verdict, reasons, uncertainty, and result trace | missing supplied proposition, missing evidence-world fact, or upstream judgment treated as authoritative |
| Decision Engine | Policy-shaped decision over CAL output | decision shape, caller-declared constraints, consumed-result pointer, decision trace | raw-signal re-judgment, invented weights, or abstention silently treated as rejection |

## Minimum gate before a production Contract B extension

Before any `1.2.0` candidate is treated as a production change, the instrument
threads should converge on one clean, pinned cross-repo test:

1. Pin exact clean producer, contract, consumer, and downstream refs. A dirty
   overlay is an observation source, not a release candidate.
2. Run C-A through Evidence Bundler and verify that claim, atom, source, passage,
   and corpus identity survive the crossing without re-derivation.
3. Build the C-B intake ledger and semantic payload separately. Test nomination
   mutation, hostile downstream-judgment injection, explicit unknown versus
   absence, declared ordering, integrity corruption, and stored-count mismatch.
4. Run CAL against the frozen C-B input and retain its result as CAL-owned
   evidence. Do not reseal a new upstream truth into the original handoff.
5. Test the downstream CAL-to-DE shape only after the B result is typed. Confirm
   that DE reports a decision over CAL output instead of recomputing CAL.
6. Require cross-repo review, a machine-readable version decision, updated
   consumer copies, and a rendered receipt derived from the machine result.

If a gate fails, preserve the failure and its inputs as a deviation. Do not
change the expected result after seeing the output just to make the interface
appear stable.

## Open decisions, still explicit

- The exact production packaging and discovery rule for the optional Contract B
  extension.
- Whether a separately authored Consumer C is needed for the final promotion
  claim.
- How the C-A decomposition artifact is owned, versioned, and reviewed.
- The eventual Contract C result shape and its relationship to CAL output.
- Generalization beyond the current frozen evidence world.

The useful private information is now visible as boundary guidance. Private raw
receipts, local filesystem paths, generated probe outputs, C-0/shortlist code,
and unresolved candidate implementations remain outside this repository.
