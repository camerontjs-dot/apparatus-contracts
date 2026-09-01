# Contract E Authority-Basis Aggregation Semantic-Closure Experiment — Preregistration

Status: **RESEARCH ONLY / NOT A CONTRACT E AMENDMENT**

## Objective

Determine the smallest normatively defensible aggregation rule for a Contract E `authority_basis` array when it contains multiple authority-conferring references.

This experiment follows the terminal qualification-binding experiment (`apparatus-contracts#58`) and does not reopen or alter it.

The exact unresolved question is the pre-question reader gap `U-AUTHORITY-BASIS-COMBINATION`:

> If `authority_basis` contains multiple conferring references, must every item match, or does any one matching domain-eligible item suffice?

The goal is semantic closure, not evaluator agreement.

## Frozen starting authority

- apparatus-contracts terminal semantic audit PR #47: closed/unmerged, head `b7fa5e3885bb75a21573f32268bf7c66d7428fdb`
- resolved Contract E SHA-256: `d883e5678aa7d39db6bd98d9607c94ee74ae68cd4c17a1def5cd00e6468634f9`
- research-scaffold-harness cohort comparison PR #12: closed/unmerged, commit `a9e7c39fa08eeb72261a3e3ca47d9d48f6012847`
- qualification-binding semantic-closure PR #58: closed/unmerged, terminal head `63298a8b289fc768981e15ff3adfaa04b0a61b9e`
- RC3B basis-binding spec blob: `63c952c9c28f1be2173e69c79976c7dfe5880c10`
- RC3B frozen direct basis attacks blob: `c726fb0ef914a850620e545131a70d427f4027bd`
- RC3A frozen envelope cases blob: `85bc7805d02a04c5a10b48b43a5f5a89f4e2f32a`
- RC3C amendment blob: `f05feac88128fd693cca2fb25a0b2951654377eb`
- RC3D interface blob: `61f46b09d391e7da4aed2491e428ec2ed226fe93`
- experiment branch base: apparatus-contracts `main` at `6a45ab2de09370f3048ffb083e25b487f81117e4`

## Observed starting facts

1. RC3C freezes `authority_basis` as an array of `AuthorityReference` with `min_items: 1`.
2. RC3B defines binding predicates for a resolved basis record against envelope subject, domain, operation, scope, target, currentness, and validity interval.
3. RC3B does not state an explicit array-level quantifier or combination rule.
4. RC3B preregistration says an authority-basis reference has no operative authority unless **its own** resolved record covers the requested bindings.
5. The frozen RC3B direct attacks replace the canonical conferring reference rather than adding a second conferring reference.
6. The RC3B compatibility hardening replaces one conferring reference at a time; it does not test mixed multiple-conferring arrays.
7. Historical RC3B implementation uses an existential success rule among domain-eligible candidates. That is implementation/compatibility evidence only unless independently supported.
8. Supporting-artifact registry-resolution semantics remain a separate explicit/open gap and are excluded from this experiment except where a frozen supporting artifact is kept unchanged as a control.

## Candidate models

### M1 — existential complete-match

At least one domain-eligible authority-conferring reference must resolve to a record that **individually** satisfies every required binding. Once such a complete match exists, other conferring references do not invalidate the authority requirement merely because they do not match this envelope.

This resembles historical RC3B implementation behavior but is not assumed normative.

### M2 — universal conferring-match

Every authority-conferring reference present in `authority_basis` must individually satisfy the envelope binding predicates; at least one must also be domain-eligible for the domain requirement. A mismatching conferring reference therefore vetoes the envelope even when another complete match exists.

### M3 — universal domain-eligible-match

Every **domain-eligible** conferring reference must individually satisfy the envelope. Conferring references whose type is not in the domain's `any_of` list do not participate in satisfying the requirement and do not veto it merely by presence.

### M4 — single-conferring-reference constraint

The authority requirement permits one operative conferring basis only; multiple conferring references are invalid or semantically undefined even if one or more match.

### M5 — compositional/partial union

Multiple records may jointly satisfy different binding dimensions, for example subject from one and scope from another, without any single record satisfying all required predicates.

Pre-registration posture: **M5 is expected to be unsupported** because RC3B binds each reference to its own complete resolved record. This expectation will be tested rather than silently treated as proven.

### M6 — source set does not choose among M1–M4

The source set supports per-reference complete binding but does not determine the array-level treatment of surplus/mismatching conferring references.

## Narrow scientific questions

Q1. Does authoritative evidence establish that at least one **single** resolved record must individually satisfy all subject/domain/operation/scope/target/time bindings, ruling out cross-record partial composition?

Q2. When one complete domain-eligible match is present, does authoritative evidence determine whether a second mismatching conferring reference is ignored, vetoing, or forbidden by cardinality?

Q3. Does `domain_basis_requirements.*.any_of` define only acceptable **types** for a satisfying basis, or also an existential quantifier over array entries?

Q4. Do reason precedence and fail-closed rules determine array aggregation, or only the reason to return after an aggregation model has already identified the relevant failing reference(s)?

Q5. Can supporting artifacts remain outside this experiment without making Q1–Q4 untestable? If not, demonstrate the dependency rather than importing the supporting-artifact-resolution experiment.

## Load-bearing assumption

The highest-weight assumption is:

> Because the historical RC3B validator returns success when any considered candidate matches, the normative Contract E rule is existential.

This assumption is not accepted by default.

It is falsified if authoritative source/amendment provenance states that each/all conferring references must bind to the envelope, or if independent consumers consistent with the frozen source set recover a materially different quantifier.

A competing load-bearing assumption is:

> RC3B preregistration's phrase `binding each authority-basis reference` implies universal array semantics.

That assumption is falsified if the phrase only describes per-reference validation while frozen authority elsewhere permits mixed basis chains or explicitly treats one matched basis as sufficient.

## Minimal discriminating matrix

Use only resolvable authority-conferring records unless a supporting-artifact control is explicitly named. Do not depend on the open supporting-artifact registry-resolution question.

For one canonical envelope, freeze cases equivalent to:

1. one complete matching conferring reference;
2. two identical/independently complete matching conferring references;
3. one complete match + one resolvable wrong-subject conferring reference of a domain-eligible type;
4. one complete match + one resolvable wrong-scope conferring reference of a domain-eligible type;
5. one complete match + one resolvable wrong-domain conferring reference;
6. no complete match, two references that each satisfy only different subsets of required bindings;
7. two individually nonmatching references where neither is complete;
8. canonical citation/task envelope retaining its frozen supporting artifact plus one complete conferring match as a control.

The matrix must distinguish M1, M2, M3, M4, and M5 where mechanically possible.

## Evidence hierarchy

Prefer, in order:

1. frozen Contract E normative artifacts;
2. RC3B/RC3C/RC3D amendment provenance and preregistration;
3. independent consumer/reproduction behavior and pre-question semantic readers;
4. frozen fixtures as intended/exercised behavior, not automatic normative authority;
5. implementation behavior as compatibility/historical evidence only.

## Held-out rule

This preregistration is frozen **before** inspecting additional independent implementation/reproduction behavior specifically for multiple-conferring-reference aggregation, and before constructing/evaluating the new discriminating matrix against historical implementations.

Source artifacts and previously cited historical RC3B validator behavior used to motivate the candidate models are not held out.

## Falsifiers

F1. A frozen normative source explicitly states an existential (`any matching reference suffices`) or universal (`every conferring reference must match`) array quantifier.

F2. A frozen amendment/preregistration unambiguously defines surplus conferring references as invalid, establishing M4.

F3. A valid source allows authority dimensions to be composed across different records without one complete matching record, supporting M5.

F4. Two independent consumers recover incompatible aggregation predicates while both remain consistent with the same frozen normative source set.

F5. The apparent existential rule is found only in the historical reference validator and not in normative/amendment evidence.

F6. The apparent universal rule depends only on the phrase `each authority-basis reference` while all frozen tests exercise one conferring reference at a time.

F7. Existing fixtures cannot distinguish M1–M4 because they never contain multiple conferring references.

F8. A proposed rule changes the validity of frozen structures without evidence that the changed structures were normatively classified before the proposal.

## Safe posture

False authorization is more serious than abstention, but fail-closed posture is not permission to invent a universal-veto rule. Likewise historical permissive implementation is not permission to invent existential semantics.

Until aggregation is justified:

- do not combine partial records into authority;
- do not infer that one matching record necessarily cures another mismatching conferring record;
- do not infer that any surplus conferring record necessarily poisons the envelope;
- do not use supporting-artifact uncertainty to answer the conferring-reference question unless a direct dependency is demonstrated.

## Allowed terminal dispositions

- `EXISTENTIAL_COMPLETE_MATCH_SUPPORTED` — one individually complete domain-eligible record is sufficient and surplus conferring references do not veto merely by mismatch.
- `UNIVERSAL_CONFERRING_MATCH_SUPPORTED` — every conferring reference must individually bind to the envelope.
- `UNIVERSAL_ELIGIBLE_MATCH_SUPPORTED` — every domain-eligible conferring reference must bind; ineligible conferring types are nonparticipants rather than vetoes.
- `SINGLE_CONFERRING_REFERENCE_REQUIRED` — multiple conferring references are forbidden/invalid.
- `PARTIAL_AGGREGATION_CLOSURE` — non-compositional complete-record binding is supported, but surplus-reference quantification remains unresolved.
- `AUTHORITY_BASIS_AGGREGATION_UNDERDETERMINED` — the source set does not uniquely determine even the bounded aggregation rule.
- `AUTHORITY_BASIS_AGGREGATION_INCONSISTENT` — authoritative evidence imposes incompatible aggregation semantics.
- `APPARATUS_DEFECT` — prior evaluator/question behavior assumed an aggregation rule absent from Contract E.

## Promotion bound

No result in this experiment authorizes Contract E production readiness, release, semantic amendment, or evaluator repair. If a specific rule is supported, any amendment requires a separate governance action after terminal disposition.
