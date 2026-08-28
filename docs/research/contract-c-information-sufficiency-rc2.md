# Contract C RC2-A — Real Producer Boundary + Semantic Minimality

**Status:** PREREGISTERED PRODUCER-SIDE RESEARCH  
**Production impact:** none  
**Decision supported:** whether a frozen producer-side Contract-C RC2 candidate is ready to be handed unchanged to a genuinely independent consumer.

## Frozen live baseline

Verified before this branch was created:

- Apparatus `main`: `c314e53bd91c0736aa4370a364673b069aceb43e`
- Evidence Bundler `main`: `c8189c31adbab11729c31430c2070126224a2d42`
- CAL `main`: `33a928db97316a3652d57df9cafb8ca240305233`
- Contract B: `1.2.0`
- Apparatus RC1 PR #11 head: `ba4ab7462fda440698f3e853b1ec9385aa2c1725`
- CAL RC1 PR #15 head: `c7f4ad6949967538c35386ddc2a3c6c7f245c53c`

RC1 remains frozen predecessor evidence. RC2 starts from production `main`, not from an RC1 research branch.

## Primary claim

> A real current-production CAL execution can expose enough legitimate boundary state to construct a decision-agnostic semantic result bound exactly to its validated Contract-B input, while excluding destination policy and unnecessary implementation telemetry and preserving every semantic distinction demonstrated necessary by prior experiments.

## Competing explanations kept live

1. current CAL boundary already exposes everything necessary;
2. required information exists but is split across legitimate boundary objects;
3. CAL lacks some required attributable state;
4. proposed Contract-C semantics include unnecessary information;
5. RC1 was bloated mainly by duplicated run/proposition facts;
6. the apparent minimality problem is primarily a serialization/byte-count artifact rather than semantic redundancy.

## Evaluator correction

Semantic minimality is the primary criterion. Byte size is diagnostic only.

Every retained field/subfield must be classified as one of:

- CAL-attributable semantic meaning;
- exact provenance / identity / reconstruction;
- legitimate preregistered consumer need;
- execution / failure / supersession interpretation;
- conditionally necessary;
- redundant / derivable;
- presentation convenience;
- implementation telemetry;
- unresolved.

A hard-coded validator requirement is not evidence of semantic necessity.

## Frozen execution plan

### A. Real Contract-B -> CAL capture

Use Evidence Bundler production `build_retrieval_bundle(...)` at the pinned EB SHA over an existing frozen multi-proposition fixture. Consume the resulting Contract-B 1.2.0 bundle through CAL production intake at the pinned CAL SHA. Record exact bundle bytes/tree identity, manifest bundle ID/hash, source/passage/proposition identities, audit configuration/policy identity, CAL output and trace state, and boundary objects available before/after audit.

No Contract-B identity may be synthesized from an `AuditTrace` or inferred from filenames/array position.

### B. RC2 semantic candidate

Build a research-only representation from demonstrated obligations rather than copying RC1 C1. Factor run-level input/producer/config identity once. Proposition results retain only attributable semantic state and references needed to interpret exact basis, residual evidence, explicit assessment/execution states, and conditional reassessment lineage.

### C. F2/F3 compression

Test whether raw scalar/intermediate measurement telemetry can remain private when retained contribution/receipt state preserves stable measurement identity/type/outcome and exact basis.

### D. Frozen semantic falsifiers

Re-run, without weakening:

- same verdict / different counterevidence;
- eligibility, semantic-validity, aperture/completeness and temporal/applicability distinctions;
- exact decision basis and non-deciding evidence;
- completed abstention vs not-performed;
- execution failure vs adverse subject finding;
- supersession/reassessment vs mutation;
- malformed reference/integrity failure;
- telemetry invariance;
- deterministic report derivation;
- fixed C state under changed destination policy.

### E. Semantic firewalls

Hold exact Contract-C bytes fixed while separately changing:

1. downstream authorization policy;
2. external outcome forecast/scenario.

Contract C must not absorb destination objectives, utility/preferences, risk tolerance, authority delegation, autonomy state, workflow routing, expected utility, causal/outcome predictions, or simulated future state unless CAL itself performed a specifically typed epistemic assessment within its established mandate.

### F. Subfield ablation and factoring

For each removed field/substructure record the affected semantic invariant, consumer/report/reconstruction/provenance consequence, whether failure is only a harness expectation, and final classification. Measure run-level vs proposition-level duplication and replace duplicated payloads with stable references where portability is preserved.

### G. Diagnostics

Compare frozen RC1 controls, the real production-boundary run, and the multi-proposition run across C0, RC1 C1 and RC2:

- canonical bytes;
- structural field count;
- repeated facts/values;
- run-level overhead;
- proposition marginal overhead;
- semantic assertion count where practical.

No byte threshold is a promotion gate.

## Producer gate

Only one result is allowed:

- **SATISFIED** — real producer boundary plus frozen semantically justified RC2 candidate is ready unchanged for Consumer B;
- **FAILED** — leading producer/representation claim contradicted;
- **INCONCLUSIVE** — apparatus does not discriminate sufficiently.

This is not an overall Contract-C disposition and cannot be reported as `SUPPORTED FOR PROMOTION` merely because Consumer B is next.

## Hard stop

Do not implement a production Contract-C exporter, change CAL production semantics, change Contract B, change Decision Engine production, assign a Contract-C version, run the held-out pre-RC1 MainFrame negative control, or mutate the frozen RC2 profile after handoff.

## Predecessor evidence

- Apparatus #11, Contract-C RC1 information sufficiency / consumer diversity
- CAL #15, Contract-C RC1 producer/result package
- locked Contract-B production lineage

RC1 failures and negative evidence remain intact and are not rewritten by this branch.
