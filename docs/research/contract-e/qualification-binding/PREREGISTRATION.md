# Contract E Qualification Binding Semantic-Closure Experiment — Preregistration

Status: **RESEARCH ONLY / no semantic amendment authorized**

## Question

Determine the smallest normatively defensible relation, if any, between a `Qualification` and the authority envelope before that Qualification may satisfy a domain competence requirement.

Primary questions:

1. Must `Qualification.subject_id` equal `envelope.subject.id`, participate in a richer explicit relationship, or remain unspecified?
2. Must `Qualification.scope` equal `envelope.jurisdiction.scope`, participate in a richer applicability relation, or remain unspecified?
3. What minimum array aggregation, if any, is required only to identify a qualifying item?
4. Do `qualification_subject_mismatch` and `qualification_scope_mismatch` have sufficiently specified predicates to be normative failure reasons?

## Live starting identities

Verified before material repository change:

- `camerontjs-dot/apparatus-contracts` PR #47: closed Draft Research PR, unmerged, head `b7fa5e3885bb75a21573f32268bf7c66d7428fdb`, disposition `TERMINAL — FALSIFIED`.
- PR #47 resolved Contract E SHA-256: `d883e5678aa7d39db6bd98d9607c94ee74ae68cd4c17a1def5cd00e6468634f9`.
- `camerontjs-dot/research-scaffold-harness` PR #12: closed Draft Research PR, head/comparison commit `a9e7c39fa08eeb72261a3e3ca47d9d48f6012847`, broad disposition FALSIFIED with a narrower recoverable core.
- Durable readers: Copilot PR #8, Grok PR #10, Gemini PR #11.
- Experiment branch base: apparatus-contracts `main` commit `6a45ab2de09370f3048ffb083e25b487f81117e4`.

PR #47 and its branch are frozen evidence and will not be modified or reopened.

## Frozen source authorities under examination

From PR #47's resolved-source set:

- RC3A authority/warrant spec blob `9c1090335d87eb5e4885a755542923b453c45317`.
- RC3A structural shapes blob `c3f293430ae6ddb87523d83ea6e5380b8b832136`.
- RC3B basis-binding spec blob `63c952c9c28f1be2173e69c79976c7dfe5880c10`.
- RC3C amendment blob `f05feac88128fd693cca2fb25a0b2951654377eb`.

Relevant observations already permitted before candidate evaluation:

- `Qualification` shape requires `type`, `id`, `subject_id`, `scope`, and `current`.
- Domains `numeric_relation`, `source_boundary`, and `outcome_verification` require a typed Qualification.
- The frozen structural shape does not state a subject/scope matching predicate analogous to authority-basis `matching_rules`.
- RC3A's frozen validator historically implemented exact subject and exact scope equality, but implementation behavior is compatibility/history evidence only.
- RC3A's preregistered qualification cases tested missing qualification and wrong type, but did not preregister subject-mismatch or scope-mismatch semantics.
- RC3C relisted `qualification_subject_mismatch` and `qualification_scope_mismatch` in a bounded reason contract while its preregistered repair scope explicitly targeted currentness, canonical wire/cardinality, delegation shape, and reason semantics rather than adding new qualification-binding semantics.
- Grok Reader PR #10 independently recorded before semantic-question reveal that fine-grained qualification subject/scope predicates were named by reasons but not spelled out as matching rules.

These observations are evidence inputs, not a candidate rule.

## Candidate models

### Subject

- S-A: exact equality, `Qualification.subject_id == envelope.subject.id`.
- S-B: explicit membership/delegation/principal relation.
- S-C: qualification may belong to another subject if another explicit applicability relation makes it usable.
- S-D: no unique subject-binding predicate is justified by the current source set.

### Scope

- P-A: exact equality, `Qualification.scope == envelope.jurisdiction.scope`.
- P-B: explicit containment/subscope relation.
- P-C: independent qualification scope plus an explicit applicability test.
- P-D: no unique scope-binding predicate is justified by the current source set.

No hierarchy or containment semantics will be invented for opaque strings.

## Load-bearing assumption

**A1:** the existence and normative relisting of `qualification_subject_mismatch` and `qualification_scope_mismatch` implies exact equality predicates.

A1 is falsified if any stronger authoritative evidence shows that the reason labels were relisted without defining their predicates, or if an authoritative source permits a non-equal but valid qualification relationship.

A1 is not established merely by historical validator behavior or fixtures that already encode equality.

## Minimal discriminating matrix

The experiment will freeze/evaluate only cases needed to distinguish the live models:

Subject:

1. exact subject match;
2. different subject;
3. multiple Qualifications, one same-subject and one different-subject;
4. another-principal/participant case only if the frozen model provides a normative relation capable of interpreting it.

Scope:

1. exact scope match;
2. clearly different opaque string scope;
3. narrower/broader only if source authority defines such structure;
4. multiple Qualifications with only one exact scope match.

Aggregation is limited to the minimum needed to ask whether at least one single Qualification can satisfy all required predicates. Independent per-field matching across different array elements is not presumed.

## Evidence hierarchy

1. frozen Contract E normative artifacts;
2. amendment provenance;
3. cross-repository producer/consumer expectations;
4. fresh reader interpretations frozen before question reveal;
5. fixtures as intended/exercised behavior only;
6. implementation behavior as compatibility/history evidence only.

## Explicit falsifiers

- F1: an authoritative source permits a Qualification for a nonmatching subject without an explicit transfer/delegation relation.
- F2: an authoritative source establishes scope applicability by a relation other than exact equality.
- F3: two independent consumers require incompatible predicates while both remain consistent with the frozen source set.
- F4: a candidate appears correct only because existing fixtures encode the assumption being tested.
- F5: applying the rule would reject currently supported valid authority structures without prior evidence that those structures were invalid.

Additional falsifier:

- F6: reason-token provenance shows that mismatch labels were normalized for diagnostics without a corresponding normative predicate.

## Safe behavior during the experiment

Until a binding predicate is justified, this experiment will not infer competence from a Qualification whose applicability cannot be established. It will also not manufacture a normative REJECT predicate merely from general fail-closed policy. Underdetermination remains a valid outcome.

## Exclusions

No authority-basis aggregation, warrant cardinality, supporting-artifact registry resolution, delegation redesign, propagation reauthorization, production authorization, or Contract E release work is in scope unless qualification binding cannot be evaluated independently.

## Allowed terminal dispositions

- `EXACT_BINDING_SUPPORTED`
- `PARTIAL_BINDING_SUPPORTED`
- `RICHER_BINDING_REQUIRED`
- `QUALIFICATION_BINDING_UNDERDETERMINED`
- `QUALIFICATION_MODEL_INCONSISTENT`
- `APPARATUS_DEFECT`

A green test is not a disposition.
