# Candidate Contract C: CAL to Decision Engine — RC0

**Status:** research candidate, not locked  
**Label:** Contract C / C-C  
**Producer:** Claim Audit Lab (CAL)  
**Consumer:** Decision Engine Gate head  
**Depends on:** Contract-B CAL consumer candidate and its conformance work

## Purpose

Contract C separates **CAL audit state** from **downstream decision policy**.

It answers a narrow question:

> What is the smallest provenance-bound CAL result a downstream policy needs to decide what may happen next, without re-running CAL or treating CAL as world truth?

The authority chain is:

```text
Evidence Bundler facts
  -> Contract B
  -> CAL audit judgment
  -> Contract C
  -> Decision Engine Gate/bar policy judgment
  -> downstream operator/system authority
```

Each arrow is an ownership boundary. Later artifacts do not become more truthful merely because they are later in the chain.

## RC0 handoff surface

```yaml
profile: contract-c-rc0
upstream:
  contract_b_bundle_id: string
  contract_b_bundle_sha256: string
claim:
  claim_id: string
  claim_text: string
  claim_text_sha256: string
audit:
  cal_version: string
  audit_config_hash: string
  rules_version: string
  rules_hash: string
  support_verdict: supported | partially_supported | unsupported | contradicted | not_checkable
  support_verdict_reason: string | null
  audit_flags: [string]
  citation_status: correct | partial | wrong_source | missing_needed | not_cited | not_applicable
  audit_confidence: high | medium | low
  rules_fired: [rule_id]
  explicit_unknowns: [state_id]
  decision_basis_passage_ids: [passage_id]
  decision_basis_passage_hashes: [sha256]
  assessment_receipt_hashes: [sha256]
integrity:
  cal_result_sha256: string
```

## Producer obligations

CAL must:

- bind the exact audited claim and upstream Contract-B bundle;
- identify CAL, rules, and audit configuration versions/hashes;
- preserve support degree separately from non-exclusive audit flags;
- preserve citation status and audit confidence;
- preserve an explicit reason for `not_checkable`;
- preserve decision-relevant unresolved state rather than inventing defaults;
- identify the decision basis and result integrity;
- never include a destination-specific promotion or lifecycle decision as if CAL made it.

## Consumer obligations

Decision Engine must:

- fail closed on malformed/incompatible input;
- verify identity/integrity before applying policy;
- treat C-C as a record of CAL's audit, not proof of reality;
- adapt C-C into a separately versioned Gate/bar policy rather than creating a second audit layer;
- preserve the Gate distinction between `fail` and `unknown`;
- never silently infer missing favorable or adverse state;
- never rewrite the audited claim while retaining the old audit identity;
- never re-run semantic audit from incidental CAL internals;
- bind its decision receipt back to claim, C-B bundle, CAL result, and Gate/bar version;
- preserve a human-review path.

## Excluded from the stable seam unless testing proves otherwise

RC0 does not require raw NLI logits, retrieval scores/ranks, per-passage softmax values, internal feature output, free-form explanation prose, UI state, or other incidental CAL telemetry.

The intended invariant is:

> If implementation telemetry changes but the final auditable state does not, Contract C does not change.

## Claim and evidence identity

Claim text is immutable across the audit identity. A revised claim requires a new claim identity/hash and a new audit.

The C-B bundle hash is also immutable lineage. A later evidence bundle does not inherit a prior C-C result automatically.

## Abstention and unknown state

If `support_verdict == not_checkable`, `support_verdict_reason` is required. Missing reason is an intake failure.

Decision-relevant unknown state remains first-class. `unknown` must never collapse into favorable or adverse default behavior merely because a field is missing.

For the current Gate consumer, an unresolved blocking criterion becomes a `hold`, not a fabricated `reject`.

## Decision basis preservation

The decision-basis passage IDs/hashes identify what CAL relied on for its current result. They do not replace or prune the retained Contract-B evidence record.

## Decision Engine Gate alignment

The first tested consumer is the generic Decision Engine Gate head.

Contract C is projected into an audited-claim Gate item and evaluated against a destination-specific bar. The bar may produce:

```text
promote | hold | reject
```

These are Gate recommendations, not Contract-C vocabulary and not CAL verdicts.

The distinction is deliberate:

- a known bar failure may produce `reject`;
- unresolved audit state may produce `hold`;
- advisory findings may remain caveats on a `promote` recommendation;
- the Gate may not reinterpret a CAL abstention as evidence of falsity.

## MainFrame implication

For the first MainFrame integration, a Gate `promote` result is only a recommendation to proceed to operator review. It must not directly set a `10_knowledge/` note to `stable`.

The intended sequence is:

```text
Contract C
  -> Decision Engine Gate receipt
  -> MainFrame/operator gate
  -> separate lifecycle mutation referencing the receipt
```

Raw evidence remains immutable.

The current structural shadow also composes the existing MainFrame note-promotion bar with one audited-claim Gate decision per supplied claim. Missing claim-audit coverage produces a hold rather than allowing a passing subset to stand in for the whole note.

## Contract-B alignment requirement

Contract C must not be locked on top of unresolved Contract-B semantics.

The current canonical apparatus vocabulary still reflects an older single-list audit verdict, while live CAL uses:

- support degree: `supported`, `partially_supported`, `unsupported`, `contradicted`, `not_checkable`;
- audit flags: `overstated`, `inferred`, `source_scope_error`, `false_caution`, `missed_counterevidence`, `coverage_loss`;
- citation status as an orthogonal field.

C-C must use the live semantic separation only after the Contract-B/CAL conformance work decides how that separation becomes canonical. Do not copy the older mixed vocabulary forward merely for compatibility.

## Promotion rule

Do not lock C-C until:

1. the Decision Engine Contract-C/Gate shadow passes;
2. Contract-B/CAL conformance establishes the upstream seam;
3. a real CAL result projects to C-C without invented defaults;
4. the minimal C-C and full CAL package produce the same downstream Gate disposition where they should;
5. irrelevant CAL telemetry is non-controlling;
6. decision-relevant state mutations are visible;
7. a real MainFrame note/source fixture preserves complete claim-audit coverage;
8. MainFrame integration preserves raw-source immutability and the operator promotion gate.

RC0 is a testable candidate, not production authority.
