# Contract E Qualification Binding — Evidence Record

Status: **RESEARCH EVIDENCE / no semantic amendment**

This record separates observed source authority, historical implementation behavior, inference, and unknowns.

## E1 — Qualification structure is normative, but its matching predicate is absent

**OBSERVED**

Frozen RC3A `SPEC-SHAPES.json` blob `c3f293430ae6ddb87523d83ea6e5380b8b832136` defines:

- `Qualification.required = [type, id, subject_id, scope, current]`;
- `current_required_for_new_exercise = true`;
- `qualification_is_not_authority_basis_by_itself = true`.

The same blob declares typed Qualification requirements for `numeric_relation`, `source_boundary`, and `outcome_verification`.

It does not define any predicate equivalent to:

- `Qualification.subject_id == envelope.subject.id`;
- `Qualification.scope == envelope.jurisdiction.scope`;
- membership, containment, principal/delegate, or another applicability relation.

By contrast, frozen RC3B `BASIS-BINDING-SPEC.json` blob `63c952c9c28f1be2173e69c79976c7dfe5880c10` contains explicit `matching_rules` for authority-basis subject, domain, operation, scope, and target binding.

**INFERENCE**

The omission is semantically material because the source set demonstrates how to state an explicit matching predicate when one is intended.

## E2 — Qualification fields were introduced without explanatory matching provenance

**OBSERVED**

`SPEC-SHAPES.json` was introduced in commit `0bb9d8eef52b671021306a282a1fa80103791779` (`research: complete RC3A authority/warrant structural shapes`). The commit adds `subject_id` and `scope` as required Qualification fields but adds no subject/scope comparison rule.

No earlier revision of that file exists in the RC3A branch history.

**UNKNOWN**

The commit message and patch do not provide a separate semantic rationale explaining whether those fields were intended for exact equality, a richer relation, provenance only, or future applicability logic.

## E3 — RC3A preregistration required competence/jurisdiction separation, not exact Qualification binding

**OBSERVED**

RC3A preregistration stated the competence firewall: competence/qualification does not imply mandate/jurisdiction, and mandate/jurisdiction does not imply competence when a domain requires qualification. It preregistered:

- qualified actor with no mandate;
- mandated actor with missing/expired required qualification;
- wrong-operation/target credential use as a broader adversarial category.

It did not state an exact Qualification subject equality or scope equality predicate.

**INFERENCE**

The preregistered scientific claim required independence of competence and jurisdiction, not a specific relation between their identifiers.

## E4 — Frozen RC3A cases encode equality only in positive baselines

**OBSERVED**

Frozen RC3A cases blob `85bc7805d02a04c5a10b48b43a5f5a89f4e2f32a`, frozen at commit `c21454ad474a3beefa4bd7bd5baaf29f75188419`, uses positive Qualification examples where:

- `qualification.subject_id` equals `envelope.subject.id`;
- `qualification.scope` equals `jurisdiction.scope`.

The preregistered negative Qualification cases are:

- missing required Qualification;
- wrong Qualification type.

No frozen case mutates Qualification subject or scope.

**INFERENCE**

The baselines are compatible with exact equality but do not discriminate equality from richer applicability or an unstated relationship. Treating them as proof of equality would trigger falsifier F4: the candidate appears correct because fixtures encode the assumption under test.

## E5 — Exact equality first appears in the historical RC3A validator after case freeze

**OBSERVED**

RC3A's case/spec freeze predates validator implementation.

- frozen cases commit: `c21454ad474a3beefa4bd7bd5baaf29f75188419`;
- freeze receipt parent of validator: `f640294b69f91508b3b300ce6a9bca5a762c1549`;
- validator implementation commit: `430ac2b87f4ccc251d0b7b84a70906ef07116021`.

Historical `validate.mjs` implemented:

- reject unless some required-type Qualification has `q.subject_id === e.subject.id`;
- reject unless some required-type Qualification has `q.scope === e.jurisdiction.scope`.

**CLASSIFICATION**

Historical implementation / compatibility evidence only. The RC3A preregistration explicitly froze specification and fixtures before validator implementation, so the validator cannot retroactively create missing source semantics.

**IMPORTANT APPARATUS OBSERVATION**

The validator checks currentness, subject, and scope with separate `some(...)` calls over the required-type subset. Therefore different Qualification objects could satisfy different predicates. This is historical implementation behavior, not a normative aggregation rule, and is not imported into this experiment.

## E6 — RC3C made reason classes normative without adding Qualification predicates

**OBSERVED**

RC3C preregistration commit `a8e949a77fd4f6813ce6c0a4156d4df50bc15998` bounded its repair to predecessor failures involving:

1. authority currentness composition;
2. canonical Qualification cardinality;
3. canonical delegation cardinality;
4. reason semantics.

Its explicit non-targets preserved competence-vs-jurisdiction separation and did not authorize new qualification-binding semantics.

Frozen RC3C amendment blob `f05feac88128fd693cca2fb25a0b2951654377eb`:

- declares `competence` as an array;
- declares `Qualification.scope` as a scalar string;
- lists `qualification_subject_mismatch` and `qualification_scope_mismatch` in whole-envelope reason precedence;
- states that canonical primary reasons are normative only when explicitly listed by RC3C or RC3B.

It does not state what comparison predicate makes either mismatch reason true.

**INFERENCE**

RC3C establishes that these are recognized diagnostic/rejection reason classes when their underlying condition is established. It does not mechanically establish exact equality as that underlying condition.

This supports Alternative A / F6: reason-token normativity can exist while predicate normativity remains incomplete.

## E7 — Fresh readers did not independently recover one explicit predicate

**OBSERVED**

Grok Reader PR #10, frozen before semantic-question reveal, explicitly recorded that `qualification_subject_mismatch` and `qualification_scope_mismatch` are listed while fine-grained subject/scope matching predicates are not spelled out like authority-basis matching rules.

Copilot Reader PR #8 described Qualification as needing to "match the subject/scope and currentness rules" but did not identify a source-defined exact predicate.

Gemini Reader PR #11 recovered required type/currentness and the non-authority nature of Qualification but did not state subject or scope matching rules in its Qualification interpretation.

All three later returned REJECT on Q-QUAL-04. The terminal cohort record correctly classified that agreement as insufficient because the different-subject rejection requires an unstated subject-binding assumption.

**INFERENCE**

Reader agreement on a plausible answer is weaker evidence than the pre-question divergence over whether a matching predicate was actually present.

## E8 — No cross-repository producer/consumer predicate was found in the bounded search

**OBSERVED**

Targeted code searches of the default branches of:

- `camerontjs-dot/evidence-bundler`;
- `camerontjs-dot/claim-audit-lab`;
- `camerontjs-dot/decision-engine`;

found no `qualification_subject_mismatch`, no Qualification `subject_id/scope/current` contract surface, and no `competence Qualification` predicate.

**BOUNDARY**

This is a narrow negative search result, not proof that no historical branch or external consumer has ever encoded such behavior.

**INFERENCE**

No current cross-repository evidence upgrades the historical RC3A equality behavior into a live Contract E normative rule.

## E9 — Richer subject or scope relations are not presently defined

**OBSERVED**

The frozen Contract E source set contains delegation relations and delegation subset rules, but no normative bridge says Qualification subject applicability follows delegation, participant identity, principal membership, or another subject relation.

`Qualification.scope` and `jurisdiction.scope` are scalar strings. The source set defines set/subset semantics for delegation `scope` arrays, but does not apply those semantics to Qualification scope strings.

**INFERENCE**

A richer relation remains architecturally possible but is not currently mechanically evaluable. Importing delegation subset semantics into Qualification would be a new semantic rule.

## Load-bearing assumption result

Assumption A1:

> The existence and normative relisting of `qualification_subject_mismatch` and `qualification_scope_mismatch` implies exact equality predicates.

**RESULT: NOT ESTABLISHED.**

The strongest counterevidence is the provenance sequence:

1. shape fields were frozen without predicates;
2. frozen qualification cases did not test subject/scope mismatches;
3. exact equality appeared later in implementation;
4. RC3C relisted reason classes under a repair scope that did not add qualification-binding semantics;
5. a fresh reader independently noticed the missing predicates before question reveal.

No authoritative evidence found in the bounded aperture converts that sequence into an exact-equality rule.
