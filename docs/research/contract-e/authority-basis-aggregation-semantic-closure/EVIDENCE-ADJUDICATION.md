# Contract E Authority-Basis Aggregation Semantic Closure — Evidence Adjudication

Status: **RESEARCH EVIDENCE / NO SEMANTIC AMENDMENT**

Preregistration: `14250a13534a04ab51f511e9f68cdce711d01dcc`
Frozen candidate matrix: `70af1961b85974f3c59212bf5dc651faa9f1a1f6`

## 1. Evidence classes

This record separates:

- **NORMATIVE SOURCE** — frozen Contract E source/amendment text;
- **PRE-FREEZE INTERPRETATION** — independent reading frozen before implementation or semantic-question reveal;
- **FROZEN FIXTURE** — intended/exercised behavior, not automatic normative authority;
- **IMPLEMENTATION OBSERVATION** — historical or independent executable behavior;
- **INFERENCE** — conclusion supported by the above but not directly stated;
- **UNKNOWN** — source set does not mechanically decide.

## 2. Normative-source observations

### N1 — `authority_basis` is plural, but no array quantifier is stated

RC3C canonical wire makes `authority_basis` an array of `AuthorityReference` with `min_items: 1`.

RC3B `BASIS-BINDING-SPEC.json` defines per-reference/per-record matching rules but contains no `all`, `every`, `any`, existential, universal, uniqueness, or surplus-reference rule for multiple authority-conferring entries.

Classification: **NORMATIVE SOURCE**.

### N2 — one resolved record must itself cover the requested bindings

RC3B preregistration states that an authority-basis reference has no operative authority unless it resolves to an authoritative basis record whose declared bounds cover the requested subject, domain, operation, scope, target class/identity, and current time.

The frozen RC3B matching rules apply all listed binding predicates to the resolved record corresponding to a reference.

This supports a **complete-record requirement**: the source does not authorize assembling subject, domain, operation, scope, target, or time coverage by unioning fields from different incomplete records.

Classification: **NORMATIVE SOURCE + INFERENCE**.

### N3 — `domain_basis_requirements.*.any_of` is a type set, not an explicit array quantifier

The source maps each domain to an `any_of` list of accepted basis types, for example grant/policy or policy-only. Nothing in the frozen source says that this key changes the array-level aggregation semantics from per-record checking to a particular quantifier across `authority_basis` entries.

Classification: **NORMATIVE SOURCE / UNKNOWN array quantifier**.

### N4 — reason precedence does not define which references must participate

RC3B freezes basis failure precedence. It does not specify whether a failure from one conferring reference remains dispositive when another reference completely satisfies the authority requirement.

Therefore reason precedence can select a reason after candidate failures are identified, but it does not itself define the array-level aggregation model.

Classification: **NORMATIVE SOURCE + INFERENCE**.

## 3. Frozen-fixture coverage

### FZ1 — direct basis attacks are single-conferring substitutions

The frozen RC3B direct attacks replace the canonical conferring reference with one wrong reference. They do not add a wrong conferring reference beside a valid one.

Result: they test **per-record binding**, not surplus-conferring aggregation.

### FZ2 — 9 x 15 hardening matrix is also replacement-only

The compatibility hardening preregistration replaces the one canonical conferring reference with each frozen authority-conferring record. It retains supporting artifacts but does not create arrays containing two authority-conferring records.

Result: 135 successful matrix classifications do not distinguish existential, universal, eligible-universal, or single-conferring models.

Classification: **FROZEN FIXTURE**.

## 4. Pre-freeze independent interpretations

### I1 — fresh Grok RC3B reproduction explicitly preserved the ambiguity

The pre-implementation preregistration independently asked:

> How are multiple `authority_basis` entries combined?

It listed three live readings:

1. all entries independently satisfy;
2. any one conferring match suffices;
3. exactly one conferring entry is allowed.

It then chose existential semantics only as **Assumption B1**, explicitly labeling the point a specification gap rather than source authority.

Classification: **PRE-FREEZE INTERPRETATION**.

### I2 — semantic-recoverability Grok reader independently surfaced the same gap

Before semantic-question reveal, the reader recorded `U-AUTHORITY-BASIS-COMBINATION`:

> If `authority_basis` contains multiple conferring references, must every item match, or does any one matching domain-eligible item suffice?

Its explanation was that the canonical wire requires an array with `min_items: 1` but states no conjunction/disjunction rule among items.

Classification: **PRE-FREEZE INTERPRETATION**.

### I3 — later fresh Grok RC3C successor independently chose existential semantics

A later fresh pre-implementation preregistration states that at least one successfully bound conferring record with an allowed type is sufficient, and that additional failing conferring references are ignored if one record satisfies the requirement.

This is independent corroboration of a plausible reading, but it does not erase I1/I2's source-gap observation.

Classification: **PRE-FREEZE INTERPRETATION**.

## 5. Implementation observations

### H1 — historical RC3B reference implementation is existential

The historical validator:

1. filters considered conferring candidates;
2. checks each candidate against all per-record binding predicates;
3. returns success when any considered outcome accepts;
4. evaluates failure precedence only when no candidate succeeds.

Classification: **IMPLEMENTATION OBSERVATION**.

### H2 — first fresh Grok implementation is existential

The frozen implementation evaluates each basis entry and returns success when any conferring record fully matches and satisfies domain eligibility. It records the local note `B1-any-matching-conferring-suffices`.

Classification: **IMPLEMENTATION OBSERVATION**, backed by a preregistered assumption rather than claimed source closure.

### H3 — second fresh Grok RC3C implementation is existential

The frozen successor collects successful bindings and returns no basis failure when any successful record has an allowed domain type.

Classification: **IMPLEMENTATION OBSERVATION**.

### H4 — fresh Gemini RC3D implementation is universal over presented entries

The frozen Gemini consumer iterates every `authority_basis` entry and immediately rejects on each entry's resolution/type/currentness/subject/domain/operation/scope/target mismatch. A valid first reference does not suppress a later mismatch.

The reproduction later showed an independent supporting-artifact resolution defect, so this consumer is not evidence that universal semantics are correct. However, on the narrow multiple-conferring quantifier, it demonstrates an independently recoverable alternative that the frozen normative source does not mechanically exclude.

Classification: **IMPLEMENTATION OBSERVATION**.

## 6. Candidate-matrix adjudication

The frozen matrix does not carry normative expected labels. It is used to show where candidate models diverge and what the observed implementations would do.

| Case | M1 existential | M2 universal conferring | M3 universal eligible | M4 single-conferring | Historical RC3B | Fresh Grok RC3B | Fresh Grok RC3C | Fresh Gemini RC3D |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C01 single complete | accept | accept | accept | accept | accept | accept | accept | accept |
| C02 duplicate complete | accept | accept | accept | reject | accept | accept | accept | accept |
| C03 complete + wrong subject | accept | reject | reject | reject | accept | accept | accept | reject |
| C04 complete + wrong scope | accept | reject | reject | reject | accept | accept | accept | reject |
| C05 complete + wrong domain | accept | reject | reject | reject | accept | accept | accept | reject |
| C06 partial subject/scope union | reject | reject | reject | reject | reject | reject | reject | reject |
| C07 two nonmatching | reject | reject | reject | reject | reject | reject | reject | reject |
| C08 decision policy match + type-ineligible grant | accept | reject | accept | reject | accept | accept | accept | reject |

The table is a code/text-derived behavioral classification, not a new hosted evaluator result.

### C06 is the decisive non-composition case

`grant:task-wrong-subject` and `grant:task-wrong-scope` are existing frozen records. One has the correct scope but wrong subject; the other has the correct subject but wrong scope. Neither individually satisfies all RC3B bindings.

No normative source permits combining them into one synthetic authority. RC3B instead requires the resolved record for an authority-basis reference to cover the requested bindings.

Disposition for compositional partial union (M5): **NOT SUPPORTED / FALSIFIED BY THE COMPLETE-RECORD REQUIREMENT**.

### C03/C04/C05/C08 expose the unresolved quantifier

These cases contain one complete match plus a second conferring reference that fails a binding or domain-type condition.

- M1 accepts.
- M2 rejects.
- M3 rejects C03-C05 but accepts C08.
- M4 rejects all multi-conferring cases.
- Frozen source text does not assign a label.
- Existing frozen RC3B fixtures do not exercise these structures.
- Independent consumers disagree.

Disposition for surplus-conferring quantification: **UNDERDETERMINED**.

## 7. Alternative explanations

### A — implementation lineage explains existential convergence

The historical reference and two Grok implementations may converge because existential semantics are a natural implementation choice for `any_of`, not because the normative source states it. This remains live because the first fresh Grok preregistration explicitly marked B1 as an assumption.

### B — `binding each authority-basis reference` implies universal validation

RC3B preregistration uses the phrase `binding each authority-basis reference`, which can motivate M2. But the same experiment's frozen tests exercise only one conferring reference at a time, so the phrase does not mechanically settle whether a surplus failing reference vetoes an otherwise complete match.

### C — multiple references are intended only for one conferring basis plus supporting artifacts

Canonical citation/task fixtures contain a conferring reference plus a supporting artifact. This could explain why the wire is plural without implying multiple conferring authorities are valid. However, no frozen source imposes a `max_conferring_items: 1` rule, so M4 remains unsupported rather than established.

### D — domain `any_of` implies existential array semantics

The name `any_of` strongly suggests disjunction, but the object is a list of accepted **basis types** for a domain. Treating its name alone as an array-level existential quantifier would be the same kind of reason-name overreach rejected in the qualification-binding experiment.

## 8. Falsifier status

- **F1 explicit source quantifier:** NOT OBSERVED. No frozen normative source states existential or universal array quantification.
- **F2 explicit single-conferring constraint:** NOT OBSERVED. M4 unsupported.
- **F3 source permits cross-record partial composition:** FALSIFIED. Per-reference complete-record binding supplies the opposite structure; no union rule exists.
- **F4 independent consumers require incompatible predicates:** OBSERVED AS AMBIGUITY EVIDENCE. Fresh Grok implementations choose existential; fresh Gemini implements universal checking. This is not a Contract E inconsistency because neither array quantifier is explicitly normative.
- **F5 existential exists only in historical reference:** NOT STRICTLY MET. Existential behavior also appears independently. However, the first independent reader labels it an assumption, so independent convergence does not establish normativity.
- **F6 universal rule inferred only from `each` wording while tests are single-reference:** SUPPORTED as a warning against claiming M2.
- **F7 frozen fixtures fail to distinguish M1-M4:** SUPPORTED.
- **F8 proposed rule changes previously unlabeled mixed structures:** SUPPORTED. Any M1-M4 choice would newly classify structures the frozen normative corpus never labeled.

## 9. Scientific conclusion from this evidence

### Supported closure

A satisfying authority basis cannot be synthesized from partial coverage distributed across multiple incomplete records. At least one **single resolved authority record** must individually satisfy the RC3B binding dimensions relevant to the exercise.

This is not a new semantic choice; it is the smallest recoverable consequence of the frozen per-reference binding rules.

### Unresolved closure

The source set does not decide whether, after one complete satisfying record exists:

- other mismatching conferring records are ignored;
- all conferring records must also match;
- all domain-eligible conferring records must match; or
- multiple conferring records are forbidden.

Implementation votes are insufficient to create that missing quantifier.

## 10. Supporting-artifact dependency

No direct dependency prevents this conclusion. C03-C08 use only authority-conferring records. The separate supporting-artifact registry-resolution question therefore remains outside scope and does not need to be solved to close the non-composition result or preserve surplus-conferring underdetermination.
