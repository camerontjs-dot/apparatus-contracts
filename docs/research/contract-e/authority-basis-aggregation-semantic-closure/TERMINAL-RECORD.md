# Contract E Authority-Basis Aggregation Semantic Closure — Terminal Record

Status: **TERMINAL**

Primary disposition: **PARTIAL_AGGREGATION_CLOSURE**

## Exact authority identities

- apparatus-contracts semantic-recoverability audit PR #47: closed/unmerged, frozen head `b7fa5e3885bb75a21573f32268bf7c66d7428fdb`
- resolved Contract E SHA-256: `d883e5678aa7d39db6bd98d9607c94ee74ae68cd4c17a1def5cd00e6468634f9`
- research-scaffold-harness cohort comparison PR #12: closed/unmerged, commit `a9e7c39fa08eeb72261a3e3ca47d9d48f6012847`
- prior qualification-binding PR #58: closed/unmerged, terminal head `63298a8b289fc768981e15ff3adfaa04b0a61b9e`
- experiment base: apparatus-contracts `main` `6a45ab2de09370f3048ffb083e25b487f81117e4`
- experiment branch: `research/contract-e-authority-basis-aggregation-20260901`
- Draft Research PR: `#59`

## Experiment identities

- preregistration commit: `14250a13534a04ab51f511e9f68cdce711d01dcc`
- frozen candidate matrix commit: `70af1961b85974f3c59212bf5dc651faa9f1a1f6`
- evidence-adjudication commit: `b82fa54af5a74cd0f77d6d979b49f6d54e1a64ea`
- results commit: `1e78f86c5067fb9f2d4dc39208171912c04abbf3`

No new hosted evaluator/run/artifact was created because mixed-conferring cases have no normative expected labels. Executing an evaluator against a candidate rule would test the evaluator against its own chosen semantics rather than determine Contract E semantics.

## Exact scientific result

### Complete-record requirement

**SUPPORTED.**

A Contract E authority exercise cannot obtain one authority binding by composing partial coverage from multiple individually insufficient resolved records.

At least one single resolved authority record must itself satisfy all applicable RC3B binding dimensions for the exercise.

This closes the compositional-partial-union model negatively.

### Surplus-conferring quantifier

**UNDERDETERMINED.**

Once a complete satisfying record exists, the frozen source set does not decide whether another mismatching authority-conferring reference:

1. is ignored;
2. vetoes the envelope;
3. vetoes only when domain-eligible; or
4. makes multiple-conferring input invalid.

Therefore the experiment does not promote existential, universal-conferring, universal-eligible, or single-conferring semantics.

## Discriminating evidence

### Strong normative evidence

RC3B requires the resolved record associated with an authority-basis reference to cover subject, domain, operation, scope, target, currentness, and validity. No cross-record union relation exists.

### Missing normative evidence

Neither RC3B nor RC3C/RC3D states an array-level quantifier over multiple authority-conferring references.

### Frozen test limitation

RC3B direct attacks and the 9 x 15 hardening matrix replace one conferring reference at a time. They never test a complete conferring reference beside a mismatching conferring reference.

### Independent-reader evidence

- semantic-recoverability Grok pre-question reader: explicitly recorded `U-AUTHORITY-BASIS-COMBINATION` as underdetermined;
- first fresh Grok RC3B preregistration: explicitly listed all/any/exactly-one as competing readings and selected existential behavior only as Assumption B1;
- later fresh Grok RC3C preregistration/implementation: independently selected existential complete-match;
- fresh Gemini RC3D implementation: independently checked all presented basis entries and therefore encodes universal behavior on the narrow mixed-conferring question.

The implementation split is evidence that the absent quantifier matters. It is not authority for choosing by majority vote.

## Candidate matrix result

The preregistered matrix uses only existing frozen registry records for its primary mixed-conferring cases.

- C06 (`wrong-subject` + `wrong-scope`) decisively demonstrates that partial records cannot be unioned into authority.
- C03/C04/C05 distinguish existential from universal behavior but remain normatively unlabeled.
- C08 distinguishes universal-conferring from universal-domain-eligible behavior but remains normatively unlabeled.
- C02 tests a single-conferring constraint but no source supplies a maximum cardinality.

## False-permit / false-reject findings

- **Cross-record partial composition:** no false-permit evidence observed; all inspected implementations reject and the normative per-record structure supports rejection.
- **Complete-plus-mismatch cases:** false-permit and false-reject rates are **not measurable** without circularly choosing the aggregation rule first.

## Falsifiers

- explicit source quantifier: not found;
- explicit single-conferring constraint: not found;
- source authorization of partial composition: not found and inconsistent with complete-record binding structure;
- independent aggregation divergence: observed;
- historical-reference-only existential behavior: false, because fresh Grok reproductions also chose existential semantics, but one explicitly labeled it an assumption;
- frozen fixture discrimination of mixed conferring entries: absent;
- reason precedence as an aggregation rule: rejected as circular.

## Preserved alternatives

1. **Existential complete-match** remains plausible and has the most implementation convergence.
2. **Universal conferring-match** remains plausible from per-entry validation and has an independent Gemini implementation witness.
3. **Universal domain-eligible-match** remains plausible and is not distinguished by source text.
4. **Single conferring record** remains possible as an intended-but-unwritten constraint, but no source evidence establishes it.
5. **Partial cross-record union** is not supported.

## Load-bearing assumption

The assumption carrying the most weight was that historical RC3B `any matching candidate succeeds` behavior was the intended normative rule.

Disposition: **not justified as normative authority**.

Its strongest falsifier is the first fresh Grok preregistration itself: after reading only the frozen public source, it explicitly preserved the aggregation rule as ambiguous and marked existential behavior as an implementation assumption.

## Supporting-artifact dependency

None. The primary discriminating matrix uses only authority-conferring records. The separate supporting-artifact registry-resolution question remains untouched.

## Deviations

1. Candidate models and matrix case classes were preregistered before held-out independent-consumer inspection.
2. Exact frozen registry IDs used to instantiate those preregistered case classes were selected after preregistration and are explicitly marked in the matrix.
3. No new executable evaluator was created because no authoritative answer key exists for the unresolved mixed-conferring cases.
4. Behavioral matrix columns for existing implementations are derived from immutable source code/pre-freeze interpretation rather than a new hosted run.
5. Fresh Gemini's universal implementation also has a separate supporting-artifact-resolution defect; its mixed-conferring behavior is retained only as independent alternative-reading evidence.

## Semantic amendment

**No semantic amendment is authorized or scientifically justified here.**

The complete-record rule is already recoverable from RC3B per-reference binding and does not require a new normative default.

The surplus-conferring quantifier requires an explicit normative choice if Contract E needs to classify those structures. Existing evidence cannot choose that policy without importing preference.

## Decision boundary

Further work on the unresolved M1/M2/M3/M4 quantifier is **not another evidence-producing repetition of this experiment** unless new authoritative evidence is introduced. With the current source set, choosing among those models is a normative/operator design decision.

## Smallest next research experiment

The next independently surfaced Contract E gap that can still be tested as a scientific question is:

**Delegation-as-domain-basis eligibility semantic closure** (`U-DELEGATION-AS-DOMAIN-ANY-OF`).

Question: when `delegation` is an authority-conferring type but every domain `any_of` list names only `grant` and/or `policy`, can a delegation satisfy the domain basis requirement via its parent/root authority type, or does it require an explicit domain-level eligibility rule?

Do not start that experiment inside this thread without separate continuation authority.

## Nonclaims

No Contract E 1.0.0, production authorization, production registry, universal authority evaluator, implementation correctness, release, merge, or production readiness is established.

## Thread state

**TERMINAL — PARTIAL_AGGREGATION_CLOSURE.**
