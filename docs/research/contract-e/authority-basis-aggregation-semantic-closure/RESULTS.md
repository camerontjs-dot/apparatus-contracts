# Contract E Authority-Basis Aggregation Semantic Closure — Results

Status: **TERMINAL SCIENTIFIC RESULT PENDING REPOSITORY RECONCILIATION**

Preregistration: `14250a13534a04ab51f511e9f68cdce711d01dcc`
Frozen candidate matrix: `70af1961b85974f3c59212bf5dc651faa9f1a1f6`
Evidence adjudication: `b82fa54af5a74cd0f77d6d979b49f6d54e1a64ea`

## Primary disposition

**PARTIAL_AGGREGATION_CLOSURE**

Contract E's frozen authority-basis source set supports one bounded aggregation property:

> A satisfying authority basis must include at least one **single resolved authority record whose own declared bounds satisfy all applicable RC3B binding predicates for the exercise**. Authority may not be synthesized by combining partial subject/domain/operation/scope/target/time coverage from multiple individually insufficient records.

The source set does **not** determine the array-level treatment of additional authority-conferring references once one complete satisfying record exists.

Therefore none of these stronger rules is currently justified as normative Contract E semantics:

- `EXISTENTIAL_COMPLETE_MATCH_SUPPORTED` in the strong sense that surplus mismatching conferring references are normatively irrelevant;
- `UNIVERSAL_CONFERRING_MATCH_SUPPORTED`;
- `UNIVERSAL_ELIGIBLE_MATCH_SUPPORTED`;
- `SINGLE_CONFERRING_REFERENCE_REQUIRED`.

## Scientific questions

### Q1 — must one record be complete?

**SUPPORTED: YES.**

RC3B binds an authority-basis reference to its own resolved record and requires that record to cover subject, authority domain, operation, jurisdiction scope, target class/identity where constrained, currentness, and validity interval.

The frozen source defines no cross-record union relation. The preregistered C06 pair (`grant:task-wrong-subject` + `grant:task-wrong-scope`) therefore cannot jointly satisfy the authority requirement: neither resolved record individually covers every required binding.

This closes the M5 partial-composition hypothesis negatively.

### Q2 — does one complete match cure or coexist with another mismatching conferring entry?

**UNDERDETERMINED.**

No frozen normative source states whether a surplus mismatching conferring reference:

- is ignored after one satisfying record exists;
- vetoes the envelope;
- vetoes only when it is domain-eligible; or
- makes multiple-conferring input itself invalid.

The frozen RC3B attacks and compatibility hardening do not discriminate these models because they replace one conferring reference at a time.

### Q3 — does domain `any_of` supply the quantifier?

**NO UNIQUE ARRAY-LEVEL RULE RECOVERED.**

`domain_basis_requirements.*.any_of` identifies accepted basis types. The source does not say that the key name also means existential quantification across the `authority_basis` array.

Historical/reference and two fresh Grok implementations interpret it existentially. A fresh Gemini implementation checks all entries universally. The first fresh Grok preregistration explicitly classified the choice as an implementation assumption because the source is silent.

### Q4 — can reason precedence close aggregation?

**NO.**

RC3B reason precedence orders binding failures. It does not specify whether a failed reference remains relevant after another reference succeeds. Applying precedence therefore presupposes an aggregation model and cannot choose that model without circularity.

### Q5 — is supporting-artifact resolution a dependency?

**NO.**

The decisive C03-C08 cases can be built entirely from frozen authority-conferring records. Supporting artifacts remain a separate source-set question.

## Candidate model dispositions

| Model | Disposition | Basis |
| --- | --- | --- |
| M1 existential complete-match | **PLAUSIBLE / NOT NORMATIVELY CLOSED** | historical RC3B + two fresh Grok implementations converge, but one fresh preregistration explicitly labels it an assumption and source has no quantifier |
| M2 universal conferring-match | **PLAUSIBLE / NOT NORMATIVELY CLOSED** | compatible with literal per-entry checking and independently implemented by fresh Gemini, but no explicit universal rule |
| M3 universal domain-eligible-match | **PLAUSIBLE / NOT NORMATIVELY CLOSED** | mechanically distinguishable from M2 at C08, but no source text chooses it |
| M4 single-conferring-reference required | **UNSUPPORTED** | no maximum-cardinality or uniqueness rule; C02 is previously unlabeled |
| M5 compositional partial union | **NOT SUPPORTED** | conflicts with the complete per-record binding structure; no union relation exists |
| M6 source does not choose M1-M4 | **SUPPORTED** | explicit pre-question gap + non-discriminating frozen fixtures + independent implementation divergence |

## Held-out / independent evidence

### Semantic reader

Grok semantic-recoverability pre-question interpretation froze `U-AUTHORITY-BASIS-COMBINATION` before semantic-question reveal and stated that the source gives no conjunction/disjunction rule among array items.

### Fresh implementation 1 — Grok RC3B reproduction

- preregistration commit: `9d2b6345c8387de8615375495a16cfcb3e67c503`
- frozen implementation: `8987bf2fa183e7a00c40e256694b0d9de007a566`

The preregistration explicitly listed all-vs-any-vs-exactly-one as competing readings and selected existential behavior only as local assumption `B1`.

### Fresh implementation 2 — Grok RC3C successor

- frozen pre-reveal head: `b3dcaa5764827d8d167327ea41daf1aac43b8a3b`
- frozen implementation commit: `310a44182a13dc9df9321bc2900bf3c60b4c87b5`

Its pre-implementation interpretation and frozen validator use existential complete-match aggregation.

### Fresh implementation 3 — Gemini RC3D reproduction

- preregistration commit: `68c50b3230369d9ddd5dc6df371ce78ae8cc8738`
- immutable pre-reveal head: `5364837007fe18f9e05eb39e0aa1031e28561290`
- frozen consumer blob: `a1275e1e2ddd6c4509ca8b7769b5651c19749f85`

Its consumer iterates every presented authority-basis entry and rejects on a mismatching entry. The reproduction had an independent supporting-artifact-resolution defect, so this behavior is evidence of recoverable alternative semantics, not evidence that universal aggregation is correct.

### Historical reference

RC3B historical validator uses existential success among considered domain-eligible candidates. This is compatibility evidence, not normative authority.

## False-permit / false-reject findings

**Not normatively measurable for the mixed-conferring cases.**

C03/C04/C05/C08 have no authoritative expected decision. Calling an existential acceptance a false permit would assume universal semantics; calling a universal rejection a false reject would assume existential semantics.

The only safe classification is disagreement among candidate/consumer semantics.

For C06/C07, all inspected implementations reject and the complete-record source structure supports rejection. No false-permit evidence was observed for cross-record partial composition.

## Load-bearing assumption outcome

The assumption:

> historical RC3B existential implementation behavior establishes normative existential aggregation

is **rejected**.

It is weakened by:

1. absence of an array quantifier in the normative spec;
2. first fresh Grok preregistration explicitly labeling B1 as an assumption;
3. semantic-reader pre-question underdetermination;
4. fresh Gemini's independently different aggregation behavior;
5. frozen RC3B tests never exercising a valid conferring reference beside a mismatching conferring reference.

The competing assumption that `binding each authority-basis reference` establishes universal semantics is also **rejected as unsupported** because the phrase is compatible with per-reference predicate definition and the frozen tests do not exercise surplus conferring references.

## Falsifier outcomes

- F1 explicit existential/universal quantifier: **not found**.
- F2 explicit single-conferring constraint: **not found**.
- F3 partial cross-record composition allowed: **not found; contradicted by complete-record binding structure**.
- F4 incompatible independent consumer predicates: **observed as underdetermination evidence**, not Contract E inconsistency.
- F5 existential only in historical reference: **not strictly true**, but independent existential convergence remains non-normative because it was preregistered as an assumption.
- F6 universal interpretation rests on ambiguous `each` wording without mixed-reference frozen tests: **supported**.
- F7 existing frozen fixtures do not distinguish M1-M4: **supported**.
- F8 choosing M1-M4 would newly classify previously unlabeled mixed structures: **supported**.

## Deviations

1. Candidate-model structure was preregistered before held-out independent-consumer inspection. Exact existing registry record IDs used to instantiate those case classes were selected afterward and are explicitly marked as such in the matrix.
2. No new hosted evaluator was run. A hosted evaluator would require embedding a candidate normative answer or comparing implementations against unlabeled cases, neither of which would establish semantics.
3. The candidate matrix's implementation columns are code/text-derived behavioral classifications, not newly executed conformance results.
4. Fresh Gemini's universal behavior coexists with a separately demonstrated supporting-artifact resolution defect; it is used only as evidence that a universal array interpretation can arise independently from the source set.

## Semantic amendment

**No array-level semantic amendment is justified by this experiment.**

The complete-record non-composition property is already the smallest recoverable consequence of RC3B's per-reference binding structure. It does not need to be reinvented as a new rule here.

Choosing how surplus mismatching conferring references behave would be a new normative decision. Existing evidence does not justify choosing M1, M2, M3, or M4 as recovered Contract E semantics.

## Terminal scientific state

**PARTIAL_AGGREGATION_CLOSURE**

Supported:

- one complete resolved record must individually satisfy the authority binding;
- partial cross-record union cannot confer authority.

Unresolved:

- surplus/multiple-conferring quantifier after a complete match exists.

This is a scientifically valid negative/partial result and does not authorize Contract E production readiness.
