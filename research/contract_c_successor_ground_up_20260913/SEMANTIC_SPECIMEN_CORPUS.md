# Contract C successor Phase 1 schema-neutral semantic specimen corpus

**Classification:** Draft Research / Research Infrastructure.

**Ordering guarantee:** Phase 0 obligation matrix was frozen first at commit `e588e1295367a4b867d608342aaacaccb41850b8`. This corpus selects no JSON shape, schema vocabulary, causal wire grammar, version, or promotion path.

The notation below is an evaluator oracle, not a proposed contract representation. A candidate based on basis groups, a typed causal expression, or another smaller representation must all reconstruct the same semantics.

## Schema-neutral semantic vocabulary

Every legitimate specimen binds one exact:

- Contract-B evidence world `W`;
- CAL semantic implementation `I` and behaviorally relevant policy `P`; and
- proposition identity/content `Q`.

Evidence participant symbols denote exact admitted Contract-B evidence references inside `W`:

- `S1`, `S2`, ...: CAL-attributable `SUPPORTS` participation;
- `R1`, `R2`, ...: CAL-attributable `REFUTES` participation;
- `U1`, `U2`, ...: non-polarized/unresolved participation that is causal for the terminal public result;
- `N1`, `N2`, ...: non-polarized participation retained as residual/non-causal terminal state.

A participant may not silently change polarity or terminal role. `U`/`N` are never support, counterevidence, a scalar winner, Decision CLEAR, Authorization, or execution occurrence.

For each specimen, `MSC` means the mathematical family of **minimal sufficient causal member sets observed or required by the frozen ablation oracle**. `MSC` is test notation only. It does not require the eventual wire format to be a list of lists.

Example: `MSC = {{S1,R1},{S2,R1}}` means either pair is sufficient for the same terminal result and no proper subset of either pair is sufficient. A representation that says `{S1,S2,R1}` is one jointly required set is false because it overstates necessity. A representation that chooses only `{S1,R1}` is also false because it invents a unique winner.

## Provenance grades

- `CURRENT_CAL_OBSERVED`: directly supported by current CAL research evidence inspected in #95-#106.
- `RELEASED_C1_CONFORMANCE`: a semantic distinction preserved by released Contract C 1.0 production conformance, useful as historical positive evidence but not automatically inherited as layout.
- `REQUIRED_METAMORPHIC`: required symmetry/generalization control to materialize against exact CAL before Phase 2 scoring; it is not claimed as already observed current-CAL output.
- `REPRESENTATION_STRESS_ONLY`: synthetic causal-grammar stress case. It is not a claim that current CAL produces this state. It tests whether a candidate is merely hard-coded to already-seen arities.

## Positive semantic specimens

| ID | Grade / evidence source | Retained participants and roles | Terminal semantic truth | Frozen causal oracle |
| --- | --- | --- | --- | --- |
| `SP-01-single-support` | `CURRENT_CAL_OBSERVED`; CAL #106 single deciding support control | `S1` causal | completed + assessed + supported | `MSC={{S1}}`. Removing `S1` must change the terminal result away from supported. |
| `SP-02-single-refutation` | `CURRENT_CAL_OBSERVED`; CAL #105 strict-comparison/event-order refutation controls | `R1` causal | completed + assessed + contradicted/refuted | `MSC={{R1}}`. Removing `R1` must change the terminal result away from contradicted. |
| `SP-03-two-independent-supports` | `CURRENT_CAL_OBSERVED`; CAL #106 C4 | `S1`,`S2` causal | completed + assessed + supported | `MSC={{S1},{S2}}`. Full result supported; ablate either one and the remaining support is still sufficient. No arbitrary winner. |
| `SP-04-two-independent-refutations` | `REQUIRED_METAMORPHIC`; support/refute symmetry pressure from current CAL relation semantics | `R1`,`R2` causal | completed + assessed + contradicted | Required `MSC={{R1},{R2}}`. Must be materialized from exact CAL RC1 or successor producer semantics before representation scoring. A candidate cannot pass only because alternatives were tested on support polarity. |
| `SP-05-joint-basis` | `RELEASED_C1_CONFORMANCE`; released `test_causal_multiplicity_and_co_maximal_basis_are_losslessly_representable` preserves a jointly-required state/rule family | two public causal members `J1`,`J2`; polarity may be non-evidence typed public state | one terminal result for which both are required | `MSC={{J1,J2}}`. Removing either changes the terminal result. This specimen exists to prevent an alternatives-only grammar. Whether rule/state members remain successor obligations is separately unresolved by Phase 0. |
| `SP-06-support-plus-neutral-residual` | `CURRENT_CAL_OBSERVED`; CAL #106 C3 | `S1` causal; `N1` residual non-polarized | completed + assessed + supported | `MSC={{S1}}`; retained residual set `{N1}`. Dropping `N1`, moving it into the causal basis, or relabeling it support/refute changes public retained state. |
| `SP-07-causal-neutral-unresolved` | `CURRENT_CAL_OBSERVED`; CAL #99/#100 | `U1` causal non-polarized | completed + not-checkable + stable unresolved public reason | `MSC={{U1}}`. Exact evidence ref for `U1` must be reconstructable. An opaque state token without the evidence edge fails. |
| `SP-08-two-independent-unresolved` | `CURRENT_CAL_OBSERVED`; CAL #100 multiplicity pressure | `U1`,`U2` causal non-polarized | completed + not-checkable + unresolved | `MSC={{U1},{U2}}`. Exact refs and independent-alternative multiplicity must both survive. |
| `SP-09-minimal-mixed` | `CURRENT_CAL_OBSERVED`; CAL #106 C5 | `S1`,`R1` causal | completed + not-checkable + `MIXED_RELATIONS` | `MSC={{S1,R1}}`. Ablating either changes the terminal result away from mixed. This is a legitimate joint basis with opposite polarities. |
| `SP-10-alt-joint-mixed` | `CURRENT_CAL_OBSERVED`; decisive CAL #106 falsifier | `S1`,`S2`,`R1` causal | completed + not-checkable + `MIXED_RELATIONS` | `MSC={{S1,R1},{S2,R1}}`, equivalently semantic shape `(S1 OR S2) AND R1`. Ablating either support alone preserves mixed; ablating `R1` removes mixed. Flat all-three joint and arbitrary pair selection both fail. |
| `SP-11-symmetric-alt-joint-mixed` | `REQUIRED_METAMORPHIC`; symmetry control required by issue #93 | `S1`,`R1`,`R2` causal | completed + not-checkable + `MIXED_RELATIONS` | Required `MSC={{S1,R1},{S1,R2}}`, equivalently `S1 AND (R1 OR R2)`. Must be materialized before Phase 2 scoring. |
| `SP-12-alt-by-alt-mixed` | `REPRESENTATION_STRESS_ONLY` | `S1`,`S2`,`R1`,`R2` causal | same mixed-style terminal target for the stress oracle | `MSC={{S1,R1},{S1,R2},{S2,R1},{S2,R2}}`, equivalent to `(S1 OR S2) AND (R1 OR R2)`. No claim that current CAL emits this exact state. Candidate should not require a schema redesign merely because both sides have alternatives. |
| `SP-13-completed-no-deciding` | `CURRENT_CAL_OBSERVED`; CAL #97/#98 irrelevant-only/no-deciding family | non-polarized retained participants may be residual; no causal support/refute | completed + not-checkable + stable no-deciding public reason | Causal oracle has no evidence member sufficient for support/refutation. Exact retained residual participation still reconstructs if CAL retains it. Must not be conflated with execution failure. |
| `SP-14-result-set-multi-proposition` | `CURRENT_CAL_OBSERVED` requirement from Apparatus #89 plus C1 production multi-proposition surface | at least two proposition results with distinct `Q` bindings | each proposition has its own execution/terminal/participation state under one result-set execution | Cross-proposition participants/bases must not alias. Proposition substitution or accidental cross-composition fails. |

## Execution-state specimens

These are semantic specimens even when they have no terminal epistemic conclusion.

| ID | Execution truth | Required distinction |
| --- | --- | --- |
| `EX-01-result-set-failed` | result-set execution failed | Must not be represented as completed `not_checkable`, unsupported, contradicted, or no-deciding. |
| `EX-02-result-set-incomplete` | result-set execution incomplete | Distinct from failed and completed. |
| `EX-03-proposition-failed` | result set may exist, one proposition execution failed | The failed proposition carries no invented subject-matter terminal conclusion. |
| `EX-04-proposition-incomplete` | one proposition execution incomplete | Distinct from failure and completed epistemic abstention. |
| `EX-05-completed-not-checkable` | proposition execution completed and CAL returned an epistemic abstention | Must remain distinct from `EX-03`/`EX-04`; may carry causal evidence and stable public reason, as in `SP-07` through `SP-10`. |

## Binding and integrity metamorphisms

A valid representation of any positive specimen must fail closed or become observably different under the following one-axis mutations:

1. replace Contract-B world identity while leaving proposition/evidence-looking IDs unchanged;
2. compose participants from two Contract-B worlds;
3. substitute proposition content under the same proposition ID;
4. substitute proposition direction while reusing stale producer/authority state;
5. substitute an evidence passage/source reference;
6. remove one retained causal participant without updating causal truth;
7. remove one retained residual participant;
8. move one participant from causal to residual or residual to causal;
9. relabel `U`/`N` as support or refutation;
10. relabel support as refutation or vice versa;
11. duplicate one participant inside a semantic set/group/expression;
12. permute semantically unordered participants, alternatives, groups and proposition records;
13. recompute a locally self-consistent content identity after semantic mutation while presenting the old externally authorized exact-object identity;
14. provide an attacker-selected replacement external digest instead of an independently established authority binding;
15. inject destination threshold/routing, actor/delegation/approval, Authorization, or execution-occurrence state into the CAL result object.

Mutation 12 is a **semantic equality** control: a pure permutation of an unordered semantic structure must not produce a different semantic object. A canonical byte format may choose one deterministic order, but insertion order is not a causal fact.

## Measurement/authority boundary specimens

These are carried from CAL #95/#96 and are deliberately outside the positive causal-evidence notation above.

`MA-01`: same exact audit context, valid measurement receipt, authority `NOT_EVALUATED`. A candidate must not infer a proposition verdict merely from the measurement.

`MA-02`: source-contradicting but internally self-consistent caller-stipulated measurement/semantic fields that a weak authority constructor would accept. The successor must not encode this as CAL-attributable warranted terminal state unless the CAL authority boundary actually warranted it.

`MA-03`: valid source-grounded completion + warranted relation + exact proposition binding. This may participate in the terminal epistemic result. The public Contract C obligation starts at the CAL-attributable warranted/result semantics and exact retained participation, not at every private measurement step.

## Rule/state ablation discriminator required before candidate freeze

Phase 0 leaves public rule/state basis concepts unresolved or re-derived. Before Phase 2 may freeze a candidate, construct at least one legitimate result where a non-evidence public rule/state fact is claimed to be causally necessary, then compare:

- evidence participants + terminal public reason + exact producer/policy identity; versus
- the same plus an explicit public typed rule/state causal member.

If a legitimate consumer can reconstruct all required public epistemic and causal distinctions without the extra member, the extra rule/state node is ablated. If not, the surviving typed semantics must be specified explicitly. An opaque `state:<id>` with no normative public meaning does not satisfy this discriminator because CAL #99 already falsified opaque state as an evidence-provenance substitute.

## Generic-assessment ablation discriminator required before candidate freeze

For each old generic slot (`eligibility`, `semantic_validity`, `aperture_completeness`, `temporal_applicability`), freeze paired legitimate semantic states that differ only in the slot if current CAL can genuinely produce that distinction. Ask whether a downstream audit/reconstruction consumer can recover a required public distinction from terminal state/reason, evidence participation and producer identity without the slot.

If no current legitimate CAL state or consumer requirement exercises a slot, that is evidence for ablation, not permission to invent synthetic producer execution state. The test must distinguish “not demonstrated” from “impossible”.

## Full-policy-payload ablation discriminator required before candidate freeze

Compare two consumers of the exact same CAL result:

- one receives exact immutable CAL implementation/release identity + exact policy digest/resolution authority;
- one additionally receives the full canonical policy payload in Contract C.

If the first can resolve and verify the exact behaviorally relevant policy without network ambiguity or mutable lookup, the duplicated in-band payload is not required for reconstruction. If not, retain the payload. A human config name is never sufficient.

## Passage-hash and contribution-ID ablation discriminators

**Passage hash:** test exact bound Contract-B bundle hash + `(source_id, passage_id)` against same-ID passage mutation and cross-world replay. Retain `passage_sha256` in Contract C only if it closes a real integrity/interoperability gap not already closed by exact Contract-B binding.

**Contribution ID:** test whether direct references to exact evidence participants can support causal structure, residual partitioning, duplicate detection and deterministic canonicalization without a second derived identifier. Retain a separate contribution ID only if it materially improves a required invariant rather than mirroring the same identity twice.

## Phase 1 freeze criterion

No representation may enter Phase 2 unless it declares how it will be scored against every observed specimen above and the required metamorphic/materialization controls. `SP-10` is the minimum non-negotiable falsifier for flat causal attribution. `SP-11` is the required symmetry check. `SP-12` is a generalization stress test, not an asserted CAL production fact.

This corpus does not establish an official successor version, candidate schema, canonical causal grammar, producer promotion, Decision policy, Authorization, or execution.
