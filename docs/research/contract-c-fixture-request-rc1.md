# Contract C RC1 Fixture Request

**Status:** preregistered fixture requirements, not execution  
**Goal:** ask for only the additional evidence needed to discriminate Contract-C hypotheses.

## Do not generate yet unless these are unavailable

CAL already has extensive frozen claim-audit traces and report fixtures. Decision Engine already has synthetic MainFrame/Contract-C fixtures. Those should be exhausted before generating more generic examples.

## Packet A — MainFrame held-out knowledge audit

Preferred: 8–12 real or safely sanitized claim/note cases with preserved source/raw lineage.

Coverage:

- 2 strongly supported claims;
- 2 under-supported or overstated claims;
- 2 with genuinely missing/unverifiable evidence;
- 1 with active counterevidence or unresolved conflict;
- 1 temporal/version-applicability case;
- additional cases only if they expose a distinct semantic state.

If safe, include preserved fabricated-source/incident material that predates RC1.

**Important:** keep incident-derived cases held out during Contract-C schema design. Use them only after the synthetic/construction suite is frozen. Do not edit the negative control to fit the system.

Gold should freeze observable facts, not prescribe the desired Decision Engine outcome. Examples: exact claim text, which source existed, which source did not, exact dates/versions, and which material was intentionally withheld.

## Packet B — coherent SOP / quality-system mini-corpus

Preferred:

- 1–3 short controlled procedures or excerpts;
- 20–40 atomic requirements total;
- 6–12 associated records/events/logs;
- known-good, known-bad, ambiguous, not-applicable, missing-record, and superseded-procedure cases;
- at least one temporal/version trap;
- at least one negative-existential case where failure to find evidence does not by itself establish nonconformance.

Synthetic is acceptable. Internal coherence matters more than realism or corpus size.

Freeze separately:

1. source/procedure bytes;
2. requirement decomposition or authoritative requirement IDs if already available;
3. record/event bytes;
4. observable ground facts;
5. any intended hidden/held-out material.

Do not label the final CAL verdict or Decision Engine action unless that label is independently justified. The experiment is partly testing those layers.

## Packet C — publication/vendor claims

Generate only if existing CAL fixtures prove insufficient.

Minimum gaps, if needed:

- one exact numeric claim;
- one causal overclaim;
- one scope overclaim;
- one claim with live counterevidence;
- one supportable only after narrowing;
- one legitimately not-checkable claim.

## Independence rule

Where practical, fixture construction and consumer implementation should be done by different agents/processes. Freeze hashes before execution. Preserve discarded cases, failed controls, and deviations.
