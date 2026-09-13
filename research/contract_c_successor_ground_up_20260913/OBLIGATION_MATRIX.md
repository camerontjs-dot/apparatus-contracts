# Contract C successor Phase 0 obligation matrix

**Classification:** Draft Research / Research Infrastructure.

**Freeze rule:** this matrix is frozen before any successor wire/schema implementation. Later evidence may supersede a row only through an explicit new research record that cites the falsifier. Contract C 1.0.0 is not modified.

**Evidence anchor:** `LIVE_STATE_PREFLIGHT.md` on this branch. Primary programme record: `camerontjs-dot/apparatus-contracts#93`.

## Classification meanings

- `RETAIN`: current evidence demonstrates a public semantic/integrity obligation. The exact old field name or nesting is not automatically retained.
- `RE-DERIVE`: a real obligation remains, but the Contract C 1.0 representation, vocabulary, identity rule, or placement is not safe to copy mechanically.
- `ABLATE`: current evidence gives no legitimate successor-core reconstruction/integrity/interoperability need for this Contract C 1.0 surface, or later evidence places it outside the public result boundary. A stated falsifier can reopen it.
- `UNRESOLVED`: current evidence does not discriminate safely. It must be pressure-tested before candidate freeze.

Statuses in the rationale distinguish `OBSERVED`, `INFERENCE`, `HYPOTHESIS`, `UNRESOLVED CHOICE`, and `PRODUCTION AUTHORITY`.

## Frozen matrix

| Contract C 1.0 field / family | Class | Successor obligation and evidence reason |
| --- | --- | --- |
| `contract_c_version` | `RE-DERIVE` | **OBSERVED:** strict 1.0 consumers reject the widened research profile and unsafe downgrade is possible (#86). A consumer needs independently selected exact contract authority, but no successor SemVer is authorized. Re-derive an authority/profile discriminator only after representation compatibility is known. |
| `input` / `input.contract_b` family | `RETAIN` | **OBSERVED:** cross-world composition/projection was falsified in CAL #97/#98; #99 reconstruction also assumes one exact bound evidence world. Retain exact Contract-B world binding, never Contract-B payload ownership. |
| `input.contract_b.contract_version` | `RETAIN` | **INFERENCE from observed interoperability:** the bundle must be interpreted under exact Contract-B authority, not caller guesswork. |
| `input.contract_b.bundle_id` | `RETAIN` | **OBSERVED:** same proposition semantics across different evidence worlds must remain distinguishable and replay-resistant. |
| `input.contract_b.bundle_hash` | `RETAIN` | **OBSERVED:** exact world integrity is required to prevent same-ID/tampered-world substitution. Contract C still does not duplicate the evidence world. |
| `producer` family | `RETAIN` | **PRODUCTION AUTHORITY + programme objective:** CAL owns epistemic semantics, so a public result must identify the producer semantics that generated it. |
| `producer.semantic_implementation_sha` | `RETAIN` | **OBSERVED:** research and production records repeatedly pin exact CAL semantics; replay/qualification depends on exact implementation identity. |
| `producer.policy.sha256` | `RETAIN` | **OBSERVED:** behaviorally relevant producer policy is part of CAL semantic identity and must not be inferred from a human label. |
| `producer.policy.canonical` full payload | `UNRESOLVED` | **UNRESOLVED CHOICE:** Contract C 1.0 explicitly retained the payload because a separately immutable producer release was not yet sufficient. The successor must test whether exact immutable CAL artifact identity plus policy digest makes the full in-band payload redundant without weakening reproduction. |
| result-set `execution.state` | `RETAIN` | **OBSERVED:** execution failure/incompleteness is not the same state as a completed epistemic abstention. This separation is a hard programme acceptance criterion. |
| `propositions` result collection | `RETAIN` | **OBSERVED:** #89 found proposition identity required on multi-proposition carriers. A result set may carry more than one proposition result. Array layout/order is not retained by this row. |
| `proposition.proposition_id` | `RETAIN` | **OBSERVED:** same-claim/proposition substitution was a demonstrated seam in CAL #97 and is rejected in RC1 qualification. |
| `proposition.text_sha256` | `RETAIN` | **OBSERVED:** same-ID proposition-content substitution must fail closed; RC1 qualification exercises proposition substitution controls. |
| proposition `execution.state` | `RETAIN` | **OBSERVED:** proposition execution status is distinct from its terminal subject-matter result. |
| proposition `execution.completion` (`assessed` vs `not_checkable`) | `RETAIN` | **OBSERVED:** Decision safely distinguishes completed `not_checkable` from supported assessed results; #98 and #72 exercise this boundary. Exact vocabulary may be normalized only if the distinction remains lossless. |
| `assessments` family as four generic slots | `UNRESOLVED` | **UNRESOLVED CHOICE:** EDR-002 justified these for the bounded 1.0 producer, but current CAL evidence now has measurement, authority, relation, and composition boundaries that do not map cleanly onto the old four names. No current successor consumer need has yet demonstrated that the generic slot family itself is required. Do not remove merely because current fixtures may say `not_performed`; run a targeted ablation/reconstruction test. |
| `assessments.eligibility` | `UNRESOLVED` | Same as assessment-family row. Need a concrete public reconstruction need, not historical presence. |
| `assessments.semantic_validity` | `UNRESOLVED` | Same as assessment-family row. Current semantic authority is producer-owned and may instead be captured by terminal public state/reason. |
| `assessments.aperture_completeness` | `UNRESOLVED` | Same as assessment-family row. Contract B owns the evidence world; Contract C must not acquire evidence-completeness ownership by analogy. |
| `assessments.temporal_applicability` | `UNRESOLVED` | Same as assessment-family row. Temporal work in #95-#99 supplies stronger typed evidence but does not yet prove a generic public stage slot is required. |
| generic assessment `state` / `value` vocabulary | `RE-DERIVE` | **INFERENCE:** if any generic assessment survives, its state model must be derived from current CAL semantics and reconstruction need. The 1.0 enum is not inherited automatically. |
| `contributions` family | `RE-DERIVE` | **OBSERVED:** exact retained evidence participation is mandatory (#99, #100, #89), but “contribution object” is only one possible carrier. Re-derive the smallest public participant representation from the semantic corpus. |
| `contribution_id` | `UNRESOLVED` | **OBSERVED counter-pressure:** #89 falsified the need for a second sidecar-specific member ID and showed exact evidence refs plus externally authorized object identity were enough in that vessel. Existing Contract C IDs may still help compact causal references. Test ablation before retaining a separate derived ID. |
| `contribution.channel = support|counterevidence` | `RE-DERIVE` | **OBSERVED:** support/refutation polarity is required, but #99/#100 prove legitimate non-polarized/non-deciding evidence also participates. The old two-value enum is insufficient. Re-derive a public relation/polarity vocabulary that includes an explicit non-polarized state without laundering it. |
| exact evidence participation | `RETAIN` | **OBSERVED:** #99 is a direct counterexample to any object that preserves terminal state but omits the exact causal evidence edge. A legitimate consumer must recover every retained participant without CAL internals or re-audit. |
| `evidence_ref.source_id` | `RETAIN` | **OBSERVED:** exact source/passages must be distinguishable inside the bound Contract-B world. |
| `evidence_ref.passage_id` | `RETAIN` | **OBSERVED:** #99/#100 reconstruction is specifically about exact admitted passage identity. |
| `evidence_ref.passage_sha256` repeated in Contract C | `UNRESOLVED` | **OBSERVED counter-pressure:** #89 found duplicated source/hash bindings conditionally required because an exact bound Contract B can recover them. With `bundle_hash` plus source/passage identity, a repeated passage hash may be redundant. Test same-ID/tampered-B controls before ablation. |
| support/refutation polarity | `RETAIN` | **OBSERVED:** current CAL and Decision controls distinguish support, refutation, inversion, and mixed results. Polarity is CAL epistemic state, not Decision policy. |
| non-polarized / `non_deciding` participation | `RETAIN` | **OBSERVED:** #99 shows provenance loss without it; #100 shows neutral contribution was the only frozen repair preserving exact unresolved provenance plus independent multiplicity; #67/#72 show a consumer can preserve it without mapping it to support or CLEAR. The name `non_deciding` is not frozen as the final vocabulary. |
| causal versus residual role | `RETAIN` | **OBSERVED:** #89 classifies this as required semantic state; #72 reconstructs causal-neutral versus residual-neutral evidence distinctly. Every retained participant must be classified without overlap or omission. |
| `measurement` family | `ABLATE` | **OBSERVED + INFERENCE:** CAL #95 makes measurement explicitly observation, not warrant or verdict. The successor objective is the smallest public epistemic/result object, not a transport for all producer observations. Exact evidence participation and causal structure must carry the public result without requiring private measurement telemetry. **Reopen only if a legitimate consumer cannot reconstruct required epistemic state from the public result without the exact measurement receipt/value.** |
| `measurement.kind` | `ABLATE` | Follows measurement-family boundary. Instrument identity remains CAL-side research/producer provenance unless a concrete public reconstruction need is demonstrated. |
| `measurement.value` | `ABLATE` | **BOUNDARY:** arbitrary scalar/confidence/score semantics are explicitly excluded. C1’s typed finite aggregate is not automatically a successor obligation, and #95 separates measurements from semantic authority. |
| `measurement.basis_contribution_ids` | `ABLATE` | Its information must not be lost, but it belongs in the re-derived public causal/evidence-participation structure rather than a measurement receipt. Keeping the old duplicate basis would create two potentially divergent causal carriers. |
| `conclusion` public terminal-result family | `RETAIN` | **OBSERVED:** downstream consumers require CAL-attributable terminal epistemic state independently of destination policy. |
| `conclusion.reported_verdict` | `RETAIN` | **OBSERVED:** supported, contradicted and completed-not-checkable states change legitimate downstream policy behavior. Contract C records CAL’s result only, not the downstream decision. |
| `conclusion.terminal_branch` | `RE-DERIVE` | **OBSERVED need, representation concern:** `not_checkable` can arise from materially different public reasons such as mixed relations, unresolved relation, or no deciding relation. Preserve a stable public terminal reason identity, but do not expose implementation-control-flow branch names merely because C1 did. |
| `conclusion.causal_form` flat enum | `RE-DERIVE` | **DIRECT FALSIFIER:** CAL #106 proves one global `single/alternatives/joint/...` label plus one flat basis cannot truthfully express `(S1 OR S2) AND R`; a three-member `jointly_sufficient` label overstates necessity. Causal structure remains required, but this encoding is insufficient. |
| `conclusion.basis_members` flat list | `RE-DERIVE` | **DIRECT FALSIFIER:** #106 requires preservation of co-maximal alternative joint bases without arbitrary winner selection. Phase 2 must compare at least minimal sufficient basis groups with a small typed causal expression. |
| `basis_member.namespace=contribution` concept | `RE-DERIVE` | Exact evidence causes remain required, but the successor may reference exact evidence participants directly rather than carry C1 contribution IDs. |
| `basis_member.namespace=rule` concept | `UNRESOLVED` | **UNRESOLVED CHOICE:** C1 carried stable rule-role identities, but current evidence has not yet shown a legitimate consumer needs rule nodes in addition to exact producer/policy identity, public terminal reason, and evidence-level causal structure. Test rule-mediated specimen ablation. |
| `basis_member.namespace=state` concept / opaque `state:` IDs | `RE-DERIVE` | **DIRECT NEGATIVE EVIDENCE:** #99 proves an opaque state basis ID is not a sufficient substitute for the exact evidence edge. If non-evidence public state is genuinely causal, it must be re-derived as an explicit typed public semantic member with a concrete reconstruction reason, not an opaque producer-private token. |
| `conclusion.residual_contribution_ids` | `RE-DERIVE` | Residual classification is required, but a separate ID array is only one layout. Candidate must preserve a complete, non-overlapping causal/residual partition of all retained participants. |
| `conclusion.rule_roles` family | `UNRESOLVED` | Current evidence has not yet demonstrated that separate public rule IDs/codes and causal/residual roles are necessary once producer/policy identity, terminal public reason and evidence causal structure are present. Do not silently drop them; use a targeted rule-mediated specimen/falsifier. |
| `rule_role.rule_id` | `UNRESOLVED` | Same as rule-role family. A stable public semantic rule identity may be needed, but current proof is insufficient. |
| `rule_role.code` | `UNRESOLVED` | Same as rule-role family. Human/internal branch labels are not public obligations without consumer evidence. |
| `rule_role.terminal_role` | `UNRESOLVED` | Same as rule-role family. If rule members survive, their causal/residual role must be explicit and non-overlapping. |
| `result_set_id` content-derived internal identity | `RE-DERIVE` | **OBSERVED:** self-consistent object identity is useful for references/replay, but #89 shows self-consistency is not authority. The hash recipe depends on the successor canonical form and must be derived after representation choice. |
| external expected whole-object SHA-256 / immutable handoff binding | `RETAIN` | **OBSERVED:** #89’s corrected discriminator shows an attacker-selected/recomputed digest is not authority; an independently established expected exact-object identity is required at handoff. This remains separate from local structural validity. |
| deterministic canonicalization | `RE-DERIVE` | **OBSERVED need:** deterministic repeat and cross-language reproduction are hard requirements. C1’s exact byte rules are not automatically inherited because the successor may contain mathematical sets/groups/expressions whose arbitrary array ordering must not invent semantic identity. |
| C1 rule “array order is always byte identity” | `ABLATE` | **INFERENCE from minimality/canonical semantics:** for semantically unordered evidence sets, basis groups, alternatives and proposition collections, arbitrary insertion order must not create a distinct semantic object. Each collection must declare whether order is semantic; unordered collections require one deterministic canonical order. Reopen only for a collection where sequence itself carries CAL semantics. |
| exact-version unknown-field rejection | `RE-DERIVE` | **OBSERVED integrity/interoperability need:** silent unknown semantics must not enter an exact profile, but the exact successor profile/version is intentionally unassigned. Re-establish closed-world validation when a candidate representation exists. |

## Cross-cutting obligations frozen independently of field layout

1. **Exact world binding:** every proposition result and every causal participant belongs to one exact Contract-B evidence world. Cross-world composition fails closed.
2. **Exact producer semantics:** exact CAL implementation and behaviorally relevant policy identity are public bindings.
3. **Exact proposition binding:** proposition identity and content binding fail closed under substitution.
4. **Execution/epistemic separation:** failed/incomplete execution is never inferred from a completed epistemic abstention, or vice versa.
5. **Complete retained participation:** all retained evidence participants are reconstructable and classified as causal or residual, with support/refutation/non-polarized relation state preserved.
6. **Truthful causal grammar:** public causal structure may not overstate necessity, erase co-maximal alternatives, or select an arbitrary winner. The #106 `(S1 OR S2) AND R` case is mandatory.
7. **Stable public terminal state:** terminal verdict plus a stable public reason must be reconstructable without producer-private control flow.
8. **No measurement/authority laundering:** an observation or scalar measurement does not become public semantic authority merely because CAL measured it.
9. **No Decision/Authorization semantics:** no destination thresholds, routing, actor/delegation/approval, operational authorization, or execution occurrence.
10. **Two integrity layers:** local deterministic/content identity plus independently established whole-object authority at the handoff boundary.

## Phase 0 falsifiers carried forward

- **F0-01 unresolved provenance:** if two same-world/same-proposition unresolved executions using different passages cannot be distinguished and attributed exactly, the representation fails (#99).
- **F0-02 alternative-joint causality:** if `(S1 OR S2) AND R` is flattened to all-three-joint or to one arbitrarily selected pair, the representation fails (#106).
- **F0-03 common-world replay:** support/refute from different Contract-B worlds must not compose (#97/#98).
- **F0-04 neutral laundering:** non-polarized evidence must never become support, counterevidence, CLEAR, scalar winner, or Authorization (#67/#72).
- **F0-05 proposition substitution:** same-ID or direction/content substitution must fail under exact proposition binding (#97/#105).
- **F0-06 execution conflation:** execution failure/incomplete and completed `not_checkable` must remain distinguishable.
- **F0-07 canonical permutation:** permutations of semantically unordered participants/groups must canonicalize to one semantic representation and identity; duplicate members must fail.
- **F0-08 opaque-state compression:** an opaque `state:` member cannot stand in for causal evidence when exact evidence participation is required (#99).
- **F0-09 measurement authority laundering:** a measurement result/receipt alone cannot grant warrant, verdict, downstream decision or Authorization (#95/#96).
- **F0-10 sidecar necessity:** a candidate that makes a second attribution object mandatory for reconstruction of Contract C’s own core epistemic obligation is architecturally suspect even if the sidecar is technically sufficient (#87/#89). A sidecar may remain a research vessel or transport receipt, not an automatic semantic escape hatch.

## Phase 0 conclusion

**OBSERVED:** the successor cannot be “Contract C 1.0 plus `non_deciding`”. That candidate preserves an important missing relation category but inherits a flat causal grammar falsified by legitimate CAL state.

**INFERENCE:** the smallest stable core is likely organized around exact bindings, a complete typed evidence-participation set, terminal public epistemic state/reason, and a general-enough causal structure over retained public members. This is not yet a representation selection.

**UNRESOLVED CHOICE:** Phase 1 must freeze schema-neutral semantics and ablation oracles before Phase 2 compares basis-group, typed-expression, or any other concrete representation.
