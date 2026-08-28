# Contract C RC1 Apparatus Deviations and Failed Attempts

## D1 - Disposition vocabulary conflict

The existing RC1 preregistration listed `SUPPORTED WITH BOUNDED DEBT` as one possible disposition. The supervisory execution prompt instead requires exactly one of `SUPPORTED FOR PROMOTION`, `NEEDS ITERATION`, `INCONCLUSIVE`, or `FALSIFIED`.

**Handling:** the preregistration was not rewritten. This execution uses the supervisory vocabulary and records the mismatch here. Scientific acceptance/falsification criteria were not relaxed.

## D2 - Clean-room independent consumer could not be launched

A MainFrame Conduit launch was attempted to obtain a consumer context that had not inspected CAL implementation. The connector returned an MCP tunnel HTTP 404 before projects/adapters could be used.

The current execution context had already inspected CAL implementation and therefore is contaminated for a clean-room independence claim.

**Effect:** T14 / independent-consumer reproducibility is **NOT ESTABLISHED**. No substitute same-context implementation is relabeled as independent.

## D3 - Initial report test omitted PDF

An exploratory harness iteration tested Markdown and HTML derivation but not PDF. The user protocol explicitly required Markdown/HTML/PDF.

**Correction before final decisive run:** add a deterministic PDF renderer derived only from C1 and use invariant metadata. No report parser or hidden machine payload was added. The final PDF was structurally inspected and rendered to an image successfully.

## D4 - Partial/supersession fixture semantics were tightened before final decisive run

An exploratory fixture represented partial/unknown/failure cases as independent examples and included a reverse `superseded_by` convenience on an old result. That was weaker than the requested test and awkward under immutable-result semantics.

**Correction before final decisive run:** freeze one coherent partial result set containing completed, abstained, and failed proposition results against the same Contract-B bundle. Recompute a separate claim under (a) changed CAL policy with B fixed, then (b) changed B with policy fixed. Supersession is now forward-linked from the newer result only.

The exploratory suite is not used for the final conclusion.

## D5 - No production CAL Contract-C projector exists in this execution

The final harness works from synthetic, controlled semantic objects grounded in current CAL production/research types. It does not prove that current production CAL can project C1 without invented defaults or lossy adaptation.

**Effect:** producer-realism remains a promotion blocker.

## D6 - Held-out MainFrame incident/fabricated-source controls intentionally not run

Those cases were kept out of schema tuning as requested.

**Effect:** they remain a valuable external negative control, but promotion cannot claim the pre-existing-control gate yet.

## D7 - `not_evaluated` is a research convenience, not a locked Contract-C enum

Failure/not-started fixtures need to distinguish an assessment that was never performed from one that was performed and remained `unknown`. The synthetic suite uses `not_evaluated` for that distinction.

**Effect:** the behavioral distinction is demonstrated as useful; the final spelling/location of that state remains unresolved. It may be derivable from execution state rather than belong in each assessment enum.