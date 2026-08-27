# Contract C conformance plan — RC0

**Status:** preregistered research plan  
**Contract:** C-C, Claim Audit Lab → Decision Engine  
**Required upstream gate:** Contract-B/CAL conformance

## Question

Can the minimal Contract-C candidate preserve every downstream decision-relevant CAL fact while excluding implementation details that should remain private to CAL?

## Frozen comparison variants

Use one identical audited claim and evidence lineage.

- **C0 — full CAL trace:** Decision Engine receives the implementation-rich CAL trace.
- **C1 — minimal Contract C:** Decision Engine receives only the RC0 candidate surface.
- **C2 — full result package:** C1 plus complete CAL measurement/assessment receipts.

C1 is the preferred candidate. C0 and C2 are controls.

## Rung 1 — lineage preservation

C1 must retain:

- exact claim ID/text/text hash;
- exact C-B bundle ID/hash;
- CAL version;
- rules version/hash;
- audit-config hash;
- CAL result hash.

**Fail if:** a downstream receipt cannot identify exactly what CAL audited.

## Rung 2 — irrelevant-telemetry invariance

Change only raw retrieval scores, raw NLI logits/probabilities, non-material explanation prose, and other implementation telemetry while keeping the final auditable state fixed.

**Pass:** C1 canonical representation is unchanged.

**Fail if:** an incidental CAL implementation value changes the stable decision surface.

## Rung 3 — decision-state sensitivity

Independently mutate:

- support verdict;
- abstention reason;
- audit flags;
- citation status;
- audit confidence;
- explicit unknowns;
- decision-basis identity;
- claim identity;
- C-B bundle identity.

**Pass:** each legitimate decision-relevant mutation is visible in C1.

## Rung 4 — abstention honesty

A `not_checkable` result must carry a reason. Missing reason fails validation. A valid abstention must not become a favorable/adverse default downstream.

## Rung 5 — no claim laundering

Use an `overstated` claim.

**Pass:** downstream policy may block or request review, but neither Contract C nor Decision Engine rewrites the proposition while keeping the original audit identity.

## Rung 6 — full-package equivalence

For decisions that legitimately depend only on RC0 fields, run the same frozen destination policy over C1 and C2.

**Pass:** disposition and material rule IDs match.

**Fail if:** C2 produces a different legitimate result because C1 omitted a decision-relevant audit fact.

## Rung 7 — MainFrame authority preservation

Use a frozen synthesized MainFrame note fixture plus raw/source lineage.

**Pass:** even the strongest positive Decision Engine result is a promotion candidate/receipt; no direct `stable` mutation occurs.

The eventual MainFrame lifecycle action must be separate and receipt-bound.

## Rung 8 — replay determinism

Repeat identical C1 + destination policy inputs.

**Pass:** canonical decision receipt is identical.

No clock, random number, network lookup, model call, or unordered-set artifact may control the decision.

## Cross-contract gate with Contract B

Do not interpret a C-C failure as a Decision Engine problem until Contract B has established that CAL received enough evidence-world state without inventing defaults.

Required sequence:

```text
EB C-B candidate
  -> apparatus validation
  -> real CAL audit
  -> C-C projection
  -> Decision Engine policy
```

If CAL must rediscover an objective fact that EB already had, fix C-B ownership first.

If Decision Engine needs a proposition-specific judgment CAL made but C-C omitted, fix C-C.

If Decision Engine wants to apply a destination preference inside CAL, keep it downstream and fix the consumer policy instead.

## Promotion criteria

C-C is ready for a version proposal only if all eight rungs pass and the minimal surface remains smaller than the full CAL trace without losing material decision state.

Any required-field addition after lock is a breaking change. Assign the version only after the observed conformance result determines whether C-C can stand as its own 1.0.0 family or must ship with a larger apparatus major-version alignment.
