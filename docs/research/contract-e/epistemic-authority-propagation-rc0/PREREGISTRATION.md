# Contract E Epistemic Authority Propagation RC0 — Preregistration

## Class

Normal-context Research / Draft. This is not a Contract E semantic amendment, not Contract E 1.0.0, not production authorization, and not a context-free reproduction.

## Live lineage fixed before candidate

Primary Contract E source/audit head: `b7fa5e3885bb75a21573f32268bf7c66d7428fdb` (Draft PR #47).

The six frozen public Contract E normative blobs remain unmodified:

- `SPEC-CANDIDATE.json` `9c1090335d87eb5e4885a755542923b453c45317`
- `SPEC-SHAPES.json` `c3f293430ae6ddb87523d83ea6e5380b8b832136`
- `SPEC-PARTICIPANT-BOUNDARY.json` `8b1d292a240300388949d502e7b656e7a23a0b8e`
- `BASIS-BINDING-SPEC.json` `63c952c9c28f1be2173e69c79976c7dfe5880c10`
- `RC3C-SPEC.json` `f05feac88128fd693cca2fb25a0b2951654377eb`
- `RC3D-INTERFACE-SPEC.json` `61f46b09d391e7da4aed2491e428ec2ed226fe93`

Resolved Contract E semantic view SHA-256: `d883e5678aa7d39db6bd98d9607c94ee74ae68cd4c17a1def5cd00e6468634f9`.

Historical Contract E cross-stage Authority Control Plane evidence: apparatus-contracts PR #23 / Decision Engine terminal evidence `ae44fc001d1157b0ad5af4312833f1d39a41356c`. That work supported a standing cross-cutting authority model and named adapter truthfulness as the strongest remaining falsifier.

New motivating CAL evidence is external and remains immutable:

- RC7E heterogeneous language-instrument terminal evidence: `camerontjs-dot/claim-audit-lab@34e9bcafad2c63c9b0761ffc456532344bc75b88`, accepted run `33448511982`, disposition `MORE_NON_LLM_INSTRUMENT_RESEARCH_JUSTIFIED`.
- RC7E showed that heterogeneous instruments increased proposal-dimension recall while unsafe authorization also increased; correctly observed predicate/argument structure was repeatedly promoted beyond its embedding/scope authority.
- Semantic Measurement Comparison Calibration RC1: `camerontjs-dot/claim-audit-lab@94d3f7f5f1c261199fc6875e289a2398e8a9616e` (Draft PR #64). It preserves typed agreement/disagreement relations without winner selection or semantic-authority promotion.

## Research question

Can a small cross-cutting authority-propagation protocol prevent epistemic authority laundering across observation, measurement, semantic interpretation, comparison, composition, decision, execution, and verification while preserving the raw source, every proposal, every disagreement, every rejection, and every unresolved residue?

The experiment does **not** ask whether CAL language instruments are correct. It assumes typed observations/proposals are supplied and tests only what authority those objects may legally acquire or confer.

## Candidate hypothesis

A bounded authority protocol can make authority a property carried with epistemic objects and transitions rather than a serialized pipeline stage if it enforces all of the following:

1. **No authority from nowhere.** Every authoritative object traces to explicit source/provenance, producing operation, jurisdiction, warrants, and authority dependencies.
2. **Authority ceilings.** A producer has a declared maximum authority kind. Agreement, multiplicity, confidence, or downstream convenience cannot exceed it.
3. **Non-transitivity by default.** Authority does not flow to descendants unless an explicit transition rule permits the exact subject/domain/operation/scope/target transformation.
4. **Proposal preservation.** Rejection or insufficient authority never deletes the raw source or native proposal.
5. **Comparison narrowness.** Agreement/disagreement receipts may establish facts about measurement relationships only; they may not establish source truth by themselves.
6. **Sticky conflict/residue.** Authority-relevant unresolved residue or conflict propagates to descendants until an explicitly authorized resolver discharges it.
7. **Embedding/scope firewall.** Structural content observed inside quantifier, modality, permission, conditional, attribution, temporal, or quantitative scope cannot silently become narrator-level semantic fact.
8. **Composition requires authority.** Individually established semantics do not automatically compose; an explicit composition grant/rule covering the relevant dimensions is required.
9. **Decision is not execution.** A valid decision does not itself confer execution authority.
10. **Execution is not verification.** An execution report does not itself establish authoritative outcome state.
11. **Correct outcome through invalid authority chain still fails.** Scientific scoring is on authority validity, not merely final-label correctness.

## Candidate authority kinds

The candidate will distinguish at minimum:

- `observation`
- `measurement`
- `semantic`
- `comparison`
- `composition`
- `decision`
- `action`
- `verification`

Statuses will include at minimum:

- `established`
- `contested`
- `unresolved`
- `insufficient_authority`
- `prohibited`

The candidate may use more granular internal states, but it may not collapse these distinctions after held-out cases are observed.

## Adversarial surfaces

After the candidate is frozen, build fresh typed cases covering at least:

- exact agreement among multiple wrong measurements;
- disagreement with exactly one correct measurement;
- disagreement where none of the current readings is correct;
- complementary orthogonal measurements;
- jurisdiction/coverage disagreement;
- scope-attachment disagreement;
- valid structural observation embedded under quantifier/modality/permission/conditional/attribution/quantitative scope;
- semantic assertion with unresolved relevant residue;
- valid semantics with irrelevant residue;
- valid individual semantics with invalid composition;
- valid composition with correct explicit rule;
- decision with no execution basis;
- execution report with no verification basis;
- competence/warrant without authority-conferring basis;
- current basis relabeled across authority domain;
- stale/revoked basis;
- supporting artifact substituted for authority-conferring basis;
- confidence/result payload mutation with authority fields fixed;
- stage-local authority relabeling;
- correct final decision reached through an invalid authority chain;
- attempts to turn agreement count into a higher authority ceiling;
- attempts to erase rejected proposals or unresolved residue.

The evaluator may also replay historical Contract E / RC7D / RC7E failure *classes* as diagnostics, but primary terminal state must be based on fresh post-candidate cases.

## Primary metrics

- raw-source preservation rate;
- proposal preservation rate;
- conflict/residue preservation rate;
- unsafe authority promotions;
- false authority rejects;
- ceiling violations;
- illegal transitive promotions;
- agreement-to-truth laundering permits;
- scope/embedding laundering permits;
- invalid composition permits;
- decision-to-action laundering permits;
- execution-to-verification laundering permits;
- correct authority grants / valid cases;
- exact reason-class agreement where preregistered;
- metamorphic authority invariance when semantic/result payload changes without authority changes;
- metamorphic authority change when an authority-relevant field alone changes.

## Terminal states

### `AUTHORITY_PROTOCOL_SUPPORTED_WITH_BOUNDS`

Requires all:

- raw-source preservation = `1.000`;
- proposal preservation = `1.000`;
- conflict/residue preservation = `1.000` where relevant;
- unsafe authority promotions = `0`;
- ceiling violations = `0`;
- illegal transitive promotions = `0`;
- agreement-to-truth laundering permits = `0`;
- scope/embedding laundering permits = `0`;
- invalid composition permits = `0`;
- decision-to-action laundering permits = `0`;
- execution-to-verification laundering permits = `0`;
- valid authority grant recall >= `0.95`;
- metamorphic authority invariance >= `0.95`;
- authority-sensitive mutation accuracy >= `0.95`.

### `AUTHORITY_PROTOCOL_OVERBLOCKS`

Safety conditions above hold, but valid authority grant recall is below `0.95`.

### `AUTHORITY_PROTOCOL_LAUNDERS`

Any unsafe authority promotion, ceiling violation, illegal transitive promotion, scope/embedding laundering permit, invalid composition permit, decision-to-action permit without independent authority, or execution-to-verification permit without independent verification authority occurs.

### `AUTHORITY_PROTOCOL_INCONCLUSIVE`

The apparatus runs but evidence is insufficient or mixed in a way not covered by the states above.

### `AUTHORITY_PROTOCOL_APPARATUS_INVALID`

Freeze guards, evaluator controls, source/proposal preservation controls, case identity, or scoring logic fail.

## Negative controls

At least three intentionally weak controls must be scored on the same cases:

1. `TRANSITIVE_CONTROL`: authority inherits automatically from upstream established objects.
2. `AGREEMENT_CONTROL`: two-or-more agreeing measurements may promote semantic authority.
3. `STAGE_LOCAL_CONTROL`: each stage validates only its local object and ignores inherited unresolved conflicts/residue and authority ceilings.

For the experiment to support the candidate, at least one weak control must fail unsafely in each of the following families where applicable: agreement, scope/embedding, cross-stage propagation, and execution/verification.

## Freeze order

1. preregistration;
2. candidate protocol/specification + executable reference implementation;
3. evaluator contract and adversarial controls, without held-out case values;
4. fresh held-out case corpus;
5. workflow / immutable run;
6. results / receipt / terminal evidence.

The candidate implementation may not change after the fresh held-out case corpus is observed and still count as the same experiment.

## Nonclaims

This experiment does not establish Contract E 1.0.0, a production registry, universal authority ontology, production CAL behavior, Decision Engine policy, execution permission, autonomous action, cryptographic trust roots, or independent recoverability. A positive result would support only a bounded Contract E successor-hardening candidate and later independent/fresh testing.