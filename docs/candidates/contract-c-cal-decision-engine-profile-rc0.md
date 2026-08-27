# Candidate Contract C — CAL → Decision Engine Profile RC0

**Status:** RESEARCH CANDIDATE, NOT LOCKED  
**Producer:** Claim Audit Lab (CAL)  
**Consumer:** Decision Engine  
**Upstream binding:** Contract B (Evidence Builder → CAL)  
**Canonical apparatus:** Contract A → Contract B → candidate Contract C  
**Version disposition:** intentionally unassigned until conformance tests complete

---

## 1. Purpose

Contract C is the proposed epistemic-result handoff from Claim Audit Lab to the Decision Engine.

Its purpose is to answer:

> What did CAL establish, fail to establish, contradict, or leave unresolved about the supplied audit proposition from the supplied evidence, and what exact evidence and policy produced that result?

Contract C does **not** answer:

> What should the organization do?

That question belongs to the Decision Engine, which may combine the CAL result with materiality, requirements, constraints, risk tolerance, costs, alternatives, accountability, and decision authority.

The core boundary is:

```text
Contract B
  supplied proposition + admitted evidence
          ↓
CAL
  measurements + assessments + epistemic conclusion
          ↓
Contract C
  immutable audit-result package
          ↓
Decision Engine
  decision context + requirements + risk + authority
          ↓
operational decision / action
```

The contractual invariant is:

> **An epistemic conclusion is not an operational authorization.**

A CAL result of `supported`, `contradicted`, `mixed`, or `unknown` must never silently become `approve`, `reject`, `escalate`, or any other operational decision.

---

## 2. Why Contract C should be separate from Contract B

Contract B records the evidence-preparation world handed to CAL. CAL's output introduces new measurements and judgments that did not exist at the B boundary.

A separate output artifact provides cleaner ownership:

- Contract B remains immutable evidence/preparation history;
- Contract C records CAL's derived epistemic state;
- re-auditing can produce a new Contract C without rewriting Contract B;
- different CAL policies can produce separate result artifacts against the same input;
- the Decision Engine can identify exactly which CAL result it consumed;
- CAL results do not acquire operational authority merely because they are written into an upstream evidence artifact.

This candidate therefore prefers a separate Contract-C result package over in-place mutation. The existing CAL audited-C-B writeback remains a compatibility path until conformance testing compares both packaging models.

---

## 3. Contract-C epistemic categories

Contract C must keep at least four categories distinct.

### 3.1 Observed / inherited facts

Facts copied or referenced from the verified Contract-B input, such as:

- supplied proposition identity and text;
- Contract-B bundle ID/hash;
- admitted passage/source IDs and hashes;
- provenance/context facts needed to reconstruct CAL's audit;
- upstream claim/decomposition lineage when supplied.

These are not reclassified as CAL findings merely because Contract C references them.

### 3.2 CAL measurements

Machine or deterministic observations produced during audit, for example:

- claim/passage support, refutation, silence, or ambiguity measurements;
- NLI scores/probabilities;
- numeric/operator outputs;
- retrieval or matching observations produced inside CAL;
- deterministic checks.

Measurements are observations, not decisions.

### 3.3 CAL assessments

Proposition-specific judgments produced under an explicit CAL policy/operator, for example:

- eligibility;
- semantic validity;
- temporal/lifecycle applicability;
- authority/supplier applicability;
- aperture/completeness;
- composition status where supplied structure requires it.

Every decision-relevant assessment must be attributable and receipt-bound.

### 3.4 CAL conclusion

The final epistemic conclusion CAL is justified in reporting under the stated policy.

A conclusion must identify its decision basis and unresolved blockers. It must not erase contrary or non-deciding evidence.

---

## 4. Candidate package layout

The exact serialization is not locked. RC0 proposes the following logical structure:

```text
cal-result-{result_id}/
  result_manifest.yaml
  claims/
    {audit_unit_id}.yaml
  measurements/
    {audit_unit_id}.yaml
  assessments/
    {audit_unit_id}.yaml
  receipts/
    ...
  CONTRACT_VERSION
  SHA256SUMS
```

A compact single-file representation may be equivalent if it preserves the same semantics, integrity, and reconstruction properties.

---

## 5. `result_manifest` minimum semantics

A Contract-C artifact should identify at minimum:

```yaml
result_id: <immutable unique result identifier>
schema_version: <Contract-C version>
created_at_utc: <timestamp>

producer:
  system: claim-audit-lab
  version: <CAL version>
  engine: <engine / pipeline ID>

input_binding:
  contract_b_bundle_id: <bundle ID>
  contract_b_bundle_hash: <hash>
  contract_b_schema_version: <version>

policy_binding:
  audit_policy_id: <policy ID>
  audit_policy_hash: <hash>
  audit_config_version: <version>
  audit_config_hash: <hash>
  validation_set_version: <if applicable>

result_integrity:
  result_hash: <hash>
```

A result that cannot identify the exact Contract-B input and exact CAL policy/config that produced it is not decision-engine-ready.

---

## 6. Audit-unit result

Each audited proposition should have a stable result record.

Candidate logical fields:

```yaml
audit_unit_id: <stable ID>

proposition:
  proposition_id: <ID>
  proposition_text: <exact supplied text>
  original_claim_ref: <optional parent/original claim reference>
  decomposition_ref: <optional immutable decomposition artifact reference>
  parent_composition_ref: <optional>

input_evidence:
  admitted_passage_ids: [...]
  admitted_passage_hashes: {...}
  contract_b_claim_ref: <source audit-unit reference>

conclusion:
  disposition: decided | abstained | limited
  reported_verdict: <CAL-policy controlled vocabulary>
  reason_code: <typed reason>
  decision_basis_contribution_ids: [...]
  policy_id: <policy>
  policy_receipt: <receipt>

state_summary:
  support_contribution_ids: [...]
  refutation_contribution_ids: [...]
  unresolved_contribution_ids: [...]
  non_deciding_contribution_ids: [...]
  conflict_present: <bool>

unresolved:
  - blocker_id: <ID>
    family: eligibility | validity | temporal | authority | aperture | composition | operator | conflict | other
    status: unknown | incomplete | ambiguous
    reason: <text>
    affected_contribution_ids: [...]
    receipt_ref: <optional>

citations:
  - contribution_id: <ID>
    passage_id: <ID>
    source_id: <ID>
    passage_hash: <hash>
```

`reported_verdict` is intentionally not frozen to one universal vocabulary in RC0 because CAL's decision semantics are still under active validation. The stable contract surface is the combination of disposition, policy/version, reason, evidence state, decision basis, and unresolved blockers.

---

## 7. Full-ledger preservation

Contract C must not provide only the evidence that won the final conclusion.

The consumer must be able to reconstruct:

- every contribution CAL admitted into its audit state;
- its measured semantic relation;
- all decision-relevant assessments;
- whether it participated in the final decision;
- why it did or did not participate;
- contradictory and mixed evidence;
- explicit unknowns;
- historical evidence rendered non-deciding by current-state applicability;
- the final decision basis as a subset of the retained audit ledger.

A thin summary that says only `supported: 0.87` is not Contract-C-complete.

---

## 8. Measurement receipts

For each claim/passage or operator measurement that can matter downstream, Contract C should carry or reference a receipt containing enough information to reproduce or audit the observation.

Candidate minimum:

- audit proposition ID;
- passage/contribution IDs;
- measurement/operator type;
- model or deterministic implementation ID/version;
- frozen configuration hash;
- raw observation/score/output used by CAL;
- receipt hash or trace reference.

The Decision Engine may use these receipts for traceability but must not recompute CAL's semantics implicitly unless it explicitly performs a new audit.

---

## 9. Assessment receipts

Decision-relevant assessments should be distinct from measurements.

A candidate receipt contains:

```yaml
assessment_id: <ID>
family: eligibility | validity | temporal | authority | aperture | composition
status: <family-specific state>
proposition_id: <ID>
contribution_ids: [...]
factual_inputs: [...]
policy_or_operator_id: <ID>
policy_or_operator_version: <version>
reason: <text>
receipt_hash: <hash>
```

An upstream fact such as `trust_level=secondary` may appear in `factual_inputs`. It does not become `eligibility=ineligible` unless a CAL assessment explicitly makes that transformation.

---

## 10. Unknowns and honest failure paths

Contract C must treat unresolved states as complete outputs, not malformed results.

Examples:

```text
eligibility_unknown
semantic_validity_unknown
aperture_unknown
aperture_incomplete
operator_unavailable
composition_incomplete
mixed_valid_evidence
conflict_unresolved
temporal_applicability_unknown
authority_applicability_unknown
```

The exact vocabulary remains subject to CAL validation, but the contract must preserve the class of failure and affected evidence.

This aligns with MainFrame's epistemic rule that a documented gap is a finished result and must not be laundered into apparent compliance or certainty.

---

## 11. Counterevidence and conflict

Contract C must never make counterevidence disappear merely because CAL ultimately reports support.

For any final conclusion, the Decision Engine must be able to tell:

- whether valid counterevidence existed;
- whether it was resolved, superseded, temporally inapplicable, ineligible, or still active;
- whether the result is mixed/conflicted;
- which evidence the final result depended on.

This prevents two CAL outputs with the same headline verdict but radically different residual risk from appearing equivalent downstream.

---

## 12. Optional claim-repair / defensible-restatement output

CAL may eventually produce a narrower statement that is better supported than the original claim.

If present, this must be explicitly represented as a **derived candidate**, never as a rewritten original claim.

Example:

```yaml
defensible_restatement:
  status: candidate
  original_proposition_id: C-17
  candidate_text: "Recorded average investigation duration was approximately 40% lower following deployment."
  basis_contribution_ids: [...]
  omitted_or_weakened_elements:
    - causal attribution
  receipt_ref: <trace>
```

The Decision Engine must not treat a CAL-generated restatement as the original asserted claim.

This field remains optional and experimental until claim-repair behavior is separately validated.

---

## 13. Evidence requests / what would change the conclusion

CAL may expose the highest-value unresolved evidence request when the current conclusion is limited.

Candidate form:

```yaml
resolution_requests:
  - request_id: <ID>
    blocker_id: <ID>
    requested_evidence: <description>
    expected_update: <what assessment could change if supplied>
```

These are epistemic requests, not operational instructions. The Decision Engine may decide whether gathering that evidence is worth the cost or delay.

---

## 14. What the Decision Engine may assume

After successful Contract-C integrity verification, the Decision Engine may treat as CAL-owned facts:

- that CAL audited the exact bound Contract-B input under the exact stated policy/config;
- that the measurements and assessments recorded are CAL's actual outputs;
- that the stated conclusion follows from CAL's recorded decision procedure, subject to CAL's declared validation status and known limitations;
- that the cited evidence/contribution IDs bind back to the recorded Contract-B input.

The Decision Engine may **not** treat Contract C as proof that the claim is true in reality, or that a particular operational action is authorized.

---

## 15. What the Decision Engine must add itself

The following are downstream decision-engine concerns and should not be fabricated by CAL merely to make the package decision-ready:

- the operational decision/question;
- materiality;
- applicable organizational/regulatory requirements for the decision;
- risk tolerance / risk appetite;
- consequences of false positive / false negative decisions;
- cost, timing, and reversibility;
- alternative actions/options;
- escalation criteria;
- accountable decision maker;
- human or institutional approval authority;
- chosen action and rationale;
- enforcement/implementation status.

This reflects the distinction between evidence assurance and decision authority.

---

## 16. Prohibited downstream equivalences

Without an explicit Decision Engine rule/context, the following transformations are prohibited:

```text
CAL supported       ≠ approve
CAL contradicted    ≠ reject
CAL abstained       ≠ stop
CAL mixed           ≠ escalate
high CAL confidence ≠ low operational risk
primary source      ≠ regulatory approval
no active refutation ≠ safe to act
```

A Decision Engine may deliberately implement a rule such as `if CAL abstains on a critical safety prerequisite, escalate`, but that is a **Decision Engine policy** and must be recorded there.

---

## 17. Decision Engine traceability requirement

Any durable decision consuming Contract C should bind back to:

```text
operational decision
    ↓
Decision Engine rule/context
    ↓
Contract-C result ID/hash
    ↓
CAL conclusion + assessment receipts
    ↓
Contract-B bundle ID/hash
    ↓
passages / sources / provenance
```

The desired property is that a reviewer can reconstruct why an action occurred without treating any intermediate summary as the evidence itself.

This aligns with MainFrame's decision-record pattern: context, decision, rationale, alternatives, consequences, enforcement, and explicit non-authorization should remain separable.

---

## 18. Re-audit and supersession

Contract-C artifacts are immutable.

If any of the following changes:

- Contract-B evidence bundle;
- CAL version;
- audit policy;
- audit configuration;
- assessment policy;
- newly established context facts;
- decomposition/proposition graph;

CAL emits a **new Contract-C artifact**.

The new result may declare:

```yaml
supersedes_result_id: <prior result>
supersession_reason: <reason>
```

The prior result remains available and reconstructable.

The Decision Engine must be able to distinguish the result it actually consumed from newer results generated later.

---

## 19. Claim decomposition neutrality

Contract C does not decide whether claim decomposition occurs before retrieval, after retrieval, iteratively, or not at all.

It requires only that the exact audit proposition CAL evaluated be identifiable and that, when decomposition exists, lineage to the original claim and any parent composition relationship remain explicit.

Therefore the output contract should remain valid across future decomposition experiments.

A change in decomposition should create a new proposition/decomposition identity and, where it changes the audit object, a new CAL result rather than silently rewriting the earlier result.

---

## 20. Validation status

Contract C must expose enough metadata to prevent an experimental CAL result from being mistaken for a validated assurance result.

Candidate fields:

```yaml
validation:
  engine_status: experimental | validated_for_scope | deprecated
  validation_set_version: <optional>
  validation_scope: <optional>
  known_limitations_ref: <optional>
```

The exact controlled vocabulary requires separate review. RC0's rule is simpler:

> CAL's validation status must survive the handoff.

---

## 21. What RC0 does not lock

RC0 intentionally does not lock:

- CAL's final verdict vocabulary;
- one universal confidence score;
- claim decomposition timing;
- claim-repair algorithms;
- the correct authority/eligibility policy;
- the exact measurement model;
- Decision Engine decision policies;
- a universal risk model;
- serialization format;
- whether all evidence text is embedded or referenced by immutable Contract-B IDs;
- whether current audited-C-B writeback is retained as a compatibility export.

These remain experiment-dependent.

---

## 22. Candidate acceptance principle

A Contract-C design is acceptable only if a Decision Engine can make different operational decisions from two epistemically different CAL results **without needing to inspect CAL's private internal implementation**, while still being able to reconstruct every decision-relevant fact back to Contract B.

If the handoff collapses evidence state into a headline verdict or confidence number and therefore loses distinctions that matter to the Decision Engine, the candidate fails.