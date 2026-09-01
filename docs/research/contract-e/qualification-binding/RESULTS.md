# Contract E Qualification Binding Semantic-Closure Experiment — Results

Status: **TERMINAL SCIENTIFIC RESULT PENDING REPOSITORY RECONCILIATION**

Primary disposition: **QUALIFICATION_BINDING_UNDERDETERMINED**

This result does not amend Contract E. It determines that the presently authoritative source set does not justify one unique Qualification subject/scope binding predicate.

## 1. Question-level dispositions

### Q1 — Subject binding

**Disposition: UNDERDETERMINED.**

The source set establishes that `Qualification.subject_id` is a required Qualification field and that `qualification_subject_mismatch` is a recognized RC3C primary-reason class. It does not establish the predicate that makes the field match or mismatch the envelope subject.

Candidate adjudication:

- **S-A exact equality**: historically implemented, but not normatively specified. Not supported as the unique rule.
- **S-B membership/delegation-aware relation**: no Qualification-to-membership/delegation bridge exists in the frozen normative sources. Not supported.
- **S-C explicit other-subject applicability**: architecturally possible, but no such relation is defined. Not supported.
- **S-D underdetermined**: supported by the absence of a predicate, provenance chronology, and prereveal reader evidence.

The bounded evidence therefore does not authorize either acceptance or rejection solely because `Qualification.subject_id != envelope.subject.id`.

### Q2 — Scope binding

**Disposition: UNDERDETERMINED.**

The source set establishes that `Qualification.scope` and `jurisdiction.scope` are scalar strings on the canonical wire and that `qualification_scope_mismatch` is a recognized RC3C primary-reason class. It does not establish how those two strings are normatively related.

Candidate adjudication:

- **P-A exact equality**: historically implemented, but not normatively specified. Not supported as the unique rule.
- **P-B containment/subscope**: no Qualification scope hierarchy or containment semantics exist. Delegation's array subset rule is scoped to delegation and cannot be imported.
- **P-C explicit applicability**: architecturally possible, but no such applicability relation exists in the frozen sources.
- **P-D underdetermined**: supported.

Because scope is an opaque scalar string, equality is the smallest mechanically expressible comparison without adding structure. That does **not** establish that equality was intended.

### Q3 — Qualification aggregation

**Disposition: DEFERRED; not required to answer Q1/Q2.**

`competence` is normatively an array, but the source set does not define whether one Qualification object must satisfy every applicable Qualification predicate or whether different objects may satisfy different checks.

Historical RC3A implementation used separate `some(...)` checks for currentness, subject, and scope, which can allow different objects to satisfy different checks. That is apparatus behavior only and is not imported as normative aggregation semantics.

Because the subject and scope predicates themselves remain underdetermined, aggregation does not need to be chosen in this experiment. A future specification should not silently inherit cross-item satisfaction from the historical validator.

### Q4 — Failure semantics

**Disposition: REASON CLASSES EXIST; TRUTH CONDITIONS UNDER-SPECIFIED.**

RC3C makes `qualification_subject_mismatch` and `qualification_scope_mismatch` recognized primary-reason classes by relisting them. The amendment does not define their underlying predicates.

Therefore:

- the reason tokens are not deleted or treated as meaningless;
- they cannot currently be used as independent authority to infer exact equality;
- a consumer cannot normatively emit either mismatch reason solely from inequality unless a separate authoritative predicate establishes that inequality constitutes mismatch.

This is a semantic-closure defect, not permission to manufacture a fail-closed equality rule.

## 2. Frozen candidate-matrix adjudication

The candidate matrix was frozen at commit `6a796e4de49448391a70b5cdb07f52b8cd1e5c4a` before the held-out RC3C case corpus was inspected for this experiment.

### Subject probes

| Probe | Observation | Result |
| --- | --- | --- |
| `SUBJ-1` exact match | Compatible with exact, relational, explicit-applicability, and underdetermined models | Non-discriminating |
| `SUBJ-2` different subject | No authoritative truth condition says equality, membership, delegation, or another relation decides validity | Underdetermined |
| `SUBJ-3` two Qualifications, one equal and one non-equal | Array shape is known; same-item/cross-item aggregation is not | Does not rescue a subject predicate |
| `SUBJ-4` another participant/principal/delegate | Contract E has delegation relations, but no rule connects those relations to Qualification applicability | Richer relation cannot be evaluated without new semantics |

### Scope probes

| Probe | Observation | Result |
| --- | --- | --- |
| `SCOPE-1` exact match | Compatible with all live models | Non-discriminating |
| `SCOPE-2` clearly different string | No authoritative truth condition says inequality itself is mismatch | Underdetermined |
| `SCOPE-3` putatively narrower/broader string | No hierarchy exists for Qualification scalar scope strings | Containment model not mechanically evaluable |
| `SCOPE-4` two Qualifications, only one exact scope | Array shape known; aggregation and predicate unresolved | Does not rescue a scope predicate |

## 3. Post-freeze held-out check

After freezing the candidate matrix, this experiment inspected frozen RC3C successor cases blob:

`17d45524125814478b987bb8e91d23f545fb514e`

The corpus was itself frozen before the RC3C successor validator.

Qualification-related RC3C cases test:

- `competence` is an array;
- singular `competence` is malformed;
- Qualification `scope` as an array is malformed because canonical Qualification scope is scalar.

The RC3C held-out corpus contains **no** semantic case in which:

- Qualification subject differs from envelope subject; or
- a scalar Qualification scope differs from jurisdiction scope.

The RC3C `reason_cases` likewise contain no qualification subject/scope mismatch reason probe.

**Result:** RC3C's successful held-out hardening establishes Qualification wire/cardinality behavior and bounded reason-list normativity, but it does not establish a hidden exact-binding predicate. This independently strengthens the reason-name-overreach explanation.

## 4. Alternative explanations

### Alternative A — reason-name overreach

**Preserved and best-supported explanation.**

The mismatch reason names were inherited/relisted while their predicates remained unstated. The provenance chronology and held-out corpus are consistent with diagnostic vocabulary surviving without semantic closure.

### Alternative B — implicit conventional exact binding

**Not established.**

Evidence compatible with this explanation exists:

- positive RC3A fixtures use equal subject and scope values;
- historical RC3A validator implements exact equality;
- later readers found a REJECT outcome natural for a different-subject Qualification.

But none of those mechanically upgrades equality into normative source text. The strongest evidence against treating this as sufficient is that specification and cases were frozen before the validator, and the frozen cases did not test either mismatch predicate.

### Alternative C — richer relation

**Possible but unsupported.**

Contract E contains participant and delegation relations, but no frozen rule makes those relations Qualification applicability rules. Delegation scope subset semantics cannot be transferred to scalar Qualification scope without a new normative rule.

### Alternative D — apparatus defect only

**Partially supported as a consequence, not the primary model disposition.**

`Q-QUAL-04` presumed that a different-subject Qualification can be assigned a determinate REJECT outcome from the frozen resolved artifact. The terminal semantic-recoverability audit already showed that this assumption was unsupported.

Qualification itself remains meaningful as a typed, current competence object. Therefore the better primary classification is `QUALIFICATION_BINDING_UNDERDETERMINED`, with `Q-QUAL-04` preserved as an apparatus-defect example caused by the missing predicate.

## 5. Load-bearing assumption

A1:

> The existence of `qualification_subject_mismatch` and `qualification_scope_mismatch` implies corresponding exact-equality predicates.

**Adjudication: NOT SUPPORTED.**

The most weight-bearing evidence is chronological:

1. Qualification fields were introduced in frozen structural specification without matching predicates.
2. Frozen RC3A cases encoded equality only in positive baselines and did not test subject/scope mismatches.
3. Exact equality then appeared in the historical validator after specification/case freeze.
4. RC3C later relisted reason classes under an amendment explicitly scoped to currentness, wire/cardinality, delegation shape, and bounded reason semantics.
5. RC3C's own frozen held-out corpus did not add a Qualification subject/scope semantic mismatch test.
6. Grok independently noticed the missing predicates before semantic-question reveal.

A reason label therefore cannot carry the missing normative relation by itself.

## 6. Falsifiers

### F1

> A valid authoritative source permits a Qualification for a nonmatching subject without an explicit transfer/delegation relation.

**Not observed.** This would falsify exact equality if found, but the experiment did not need it because exact equality was never established in the first place.

### F2

> A valid authoritative source establishes scope applicability by a relation other than exact equality.

**Not observed.** No Qualification scope hierarchy/applicability relation was found.

### F3

> Two independent consumers require incompatible predicates while both remain consistent with the frozen source set.

**Not demonstrated.** Current bounded cross-repository searches did not identify live producer/consumer Qualification predicates. Reader interpretations differed in explicitness, but that is not a cross-repository consumer incompatibility result.

### F4

> The candidate only appears correct because existing fixtures encode the assumption being tested.

**Triggered as a material warning against exact equality.** Positive RC3A Qualification fixtures use equal subject/scope, while no frozen negative fixture discriminates the equality hypothesis. Fixture compatibility cannot establish the rule.

### F5

> Applying the rule would reject currently supported valid authority structures without prior evidence that those structures were invalid.

**Not directly measurable.** No authoritative corpus labels non-equal Qualification structures as valid or invalid. This absence is itself why a new reject predicate cannot be justified.

### F6

> Mismatch reason labels were normalized without defining predicates.

**Supported by provenance.** RC3C's bounded reason relisting and frozen held-out cases establish reason vocabulary without a Qualification mismatch truth-condition test or matching-rules object.

## 7. False-permit / false-reject findings

**Not measurable for the disputed subject/scope cases.**

There is no authoritative labeled cohort for non-equal Qualification subject/scope relationships. Any numeric false-permit or false-reject rate would therefore circularly assume the predicate under test.

The historical equality validator cannot serve as the answer key because it is one of the compatibility observations whose normativity is being tested.

## 8. Cross-repository check

A bounded search of current default branches for Evidence Bundler, Claim Audit Lab, and Decision Engine found no live Qualification subject/scope predicate or matching reason implementation that independently closes the rule.

This negative search is evidence of absence within the bounded aperture only. It is not an exhaustive claim about every historical branch or external system.

## 9. Semantic amendment disposition

**No specific subject/scope semantic amendment is justified by existing evidence.**

In particular, this experiment does not justify adding:

- exact subject equality;
- exact scope equality;
- delegation-aware Qualification subject inheritance;
- scope containment;
- cross-item aggregation.

Any such rule would be a new normative design choice rather than recovery of an already-supported Contract E semantic relation.

A future amendment can be justified only after a separate experiment supplies authoritative discriminating evidence or an explicit operator-authorized normative choice with its own falsifiers and independent reproduction gate.

## 10. Scientific terminal disposition

**QUALIFICATION_BINDING_UNDERDETERMINED**

- Subject-binding disposition: `UNDERDETERMINED`.
- Scope-binding disposition: `UNDERDETERMINED`.
- Aggregation dependency: `DEFERRED; NOT REQUIRED TO REACH Q1/Q2 DISPOSITION`.
- Failure semantics: mismatch reason classes are recognized, predicates are under-specified.
- Q-QUAL-04: preserved as an apparatus-defect example; not repaired.
- Contract E production readiness: **NOT CLAIMED**.

The smallest next independent research question is the already-surfaced **authority-basis aggregation gap**. It is not executed in this thread.
