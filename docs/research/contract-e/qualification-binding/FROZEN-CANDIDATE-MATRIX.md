# Contract E Qualification Binding — Frozen Candidate Matrix

Status: **FROZEN BEFORE MATRIX ADJUDICATION**

This matrix distinguishes exact equality, richer explicit relations, and source-set underdetermination. It does not encode expected Contract E answers.

## Candidate predicates

### Subject candidates

- `S-A EXACT`: Qualification satisfies subject binding iff `q.subject_id == envelope.subject.id`.
- `S-B RELATIONAL`: Qualification satisfies subject binding iff a source-defined membership/delegation/principal relation connects `q.subject_id` to `envelope.subject.id`.
- `S-C EXPLICIT-APPLICABILITY`: Qualification may belong to another subject if another explicit source-defined relation makes it applicable to the envelope subject.
- `S-D UNDERDETERMINED`: the source set does not define a unique subject predicate.

### Scope candidates

- `P-A EXACT`: Qualification satisfies scope binding iff `q.scope == envelope.jurisdiction.scope`.
- `P-B CONTAINMENT`: Qualification satisfies scope binding through a source-defined containment/subscope relation.
- `P-C EXPLICIT-APPLICABILITY`: Qualification scope is independent and another explicit source-defined applicability test connects it to jurisdiction.
- `P-D UNDERDETERMINED`: the source set does not define a unique scope predicate.

## Fixed base envelope

For all conceptual probes unless noted:

- authority domain: `outcome_verification`;
- operation: `outcome.verify`;
- subject id: `outcome-verifier`;
- jurisdiction scope: `research-task`;
- required Qualification type: `outcome_verifier`;
- Qualification currentness: `true`;
- authority basis and warrant are assumed independently valid so they do not decide this experiment.

No probe changes authority-basis aggregation, warrant cardinality, delegation semantics, propagation, or production authorization.

## Subject probes

| ID | Qualification set | S-A EXACT | S-B RELATIONAL | S-C EXPLICIT-APPLICABILITY | S-D UNDERDETERMINED | Discriminating observation required |
| --- | --- | --- | --- | --- | --- | --- |
| `SUBJ-1` | one q with `subject_id=outcome-verifier` | compatible | compatible | compatible | compatible | none; positive equality is non-discriminating |
| `SUBJ-2` | one q with `subject_id=other-verifier` | mismatch | depends on relation | depends on relation | no unique decision | authoritative rule for non-equal subject |
| `SUBJ-3` | two q of required type, one matching subject and one nonmatching | at least one candidate matching item exists | depends on relation + aggregation | depends on relation + aggregation | no unique decision | single-item aggregation rule plus subject predicate |
| `SUBJ-4` | q belongs to another participant/principal/delegate | mismatch unless equal | may match if source defines bridge | may match if source defines bridge | no unique decision | explicit Qualification-to-participant/delegation bridge |

`SUBJ-4` must not import delegation semantics merely because delegation exists elsewhere in Contract E.

## Scope probes

| ID | Qualification set | P-A EXACT | P-B CONTAINMENT | P-C EXPLICIT-APPLICABILITY | P-D UNDERDETERMINED | Discriminating observation required |
| --- | --- | --- | --- | --- | --- | --- |
| `SCOPE-1` | one q with `scope=research-task` | compatible | compatible | compatible | compatible | none; positive equality is non-discriminating |
| `SCOPE-2` | one q with `scope=other-task` | mismatch | depends on containment | depends on relation | no unique decision | authoritative rule for non-equal scope |
| `SCOPE-3` | one q with a lexical/narrative narrower or broader scope label | equality only if identical | depends on defined hierarchy | depends on defined applicability | no unique decision | normative structure for Qualification scope; lexical intuition is forbidden |
| `SCOPE-4` | two q of required type, only one exact scope match | at least one candidate matching item exists | depends on relation + aggregation | depends on relation + aggregation | no unique decision | single-item aggregation rule plus scope predicate |

Because Qualification and jurisdiction scope are scalar strings in the frozen wire, `SCOPE-3` has no containment semantics unless an authoritative source defines them.

## Minimum aggregation question

The matrix distinguishes two aggregation possibilities only if a subject/scope predicate is otherwise justified:

- `AGG-A SINGLE-ITEM`: at least one individual Qualification of the required type/currentness satisfies every required Qualification predicate.
- `AGG-B CROSS-ITEM`: different Qualification objects may separately satisfy currentness, subject, scope, or other predicates.

The historical RC3A validator exhibited `AGG-B`-compatible behavior through separate `some(...)` checks. That behavior is not normative evidence for this matrix.

If subject/scope predicates remain underdetermined, aggregation is deferred rather than independently solved.

## Adjudication rule

A candidate is supported only if authoritative evidence mechanically determines it. Compatibility with existing positive fixtures is insufficient. Historical implementation behavior is insufficient unless independently corroborated by normative source or consumer contract evidence.

If no candidate is uniquely supported, the terminal result is underdetermination rather than selection by architectural preference or fail-closed intuition.

## Frozen falsifiers carried forward

- F1 nonmatching subject explicitly valid without transfer/delegation relation.
- F2 scope applicability explicitly non-equality.
- F3 independent consumers require incompatible predicates while consistent with frozen sources.
- F4 candidate succeeds only because fixtures encode it.
- F5 candidate rejects supported structures without prior invalidity evidence.
- F6 mismatch reason labels were normalized without defining predicates.
