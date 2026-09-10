# Contract C attribution sidecar RC1 — preregistration

**Classification:** Draft Research Infrastructure / alternative representation experiment. No canonical Contract C change, validator change, schema release, version assignment, Decision Engine production change, CAL production change, Contract E Authorization, merge, release, tag, promotion, or production-default change.

## Exact base

- protected Apparatus `main`: `c3563cff66d2c85dcbf575c693056e2d8e4563d4`
- exact base branch: `research/contract-c-attribution-sidecar-rc1-base-20260910`
- released Contract C 1.0 authority: `5fe55f9ed5d0ee9f026ca1b077e9d70ce0487ea1`
- released validator blob: `9c75ccfbf2223578a8d1a7bf0c39673b394fbea4`
- released schema blob: `b0369de9b5c156322d6787261bbc7658a3b33781`

## External evidence motivating this test

CAL Draft PR #100, head `aa5f0f1313e65e6d31493095214c76d743ca6d89`, pressure-tested four unresolved-provenance representations. Its original Candidate D sidecar bound exact Contract C identity, proposition, state ID and evidence references, but contained only `role=causal_non_deciding`; it supplied no evidence-level multiplicity operator. The frozen multiplicity consumer therefore returned `not_reconstructable_at_evidence_level` for Candidate D.

The same CAL run `34506201889` established by ablation that two separately warranted unresolved relations were independent sufficient alternatives for the terminal unresolved abstention. The in-band neutral-contribution candidate preserved that relation and was the sole survivor in that frozen four-candidate comparison.

Subsequent Apparatus Draft PR #85 showed that an in-band `non_deciding` contribution channel can preserve this state with only a two-leaf research shadow delta. Decision Engine Draft PR #67 showed cross-repository consumption without laundering neutral evidence. Apparatus Draft PR #86 then established that a promoted in-band successor would carry a MAJOR compatibility signal and that semantic downgrades to Contract C 1.0 can be validator-valid while wrong.

This experiment does not assume that the in-band successor is therefore necessary.

## Strongest remaining alternative

Leave canonical Contract C 1.0 bytes unchanged and pair them with a separately immutable, Contract-C-bound attribution receipt that adds only the missing evidence-level causal relation among neutral unresolved contributors.

The smallest tested sidecar shape must bind:

1. exact Contract C version, result-set identity and whole-object SHA-256;
2. exact proposition ID and proposition text hash;
3. exact opaque Contract C `state:` basis identity;
4. attribution role `causal_non_deciding`;
5. one explicit evidence-level `causal_form`;
6. explicit causal members, each carrying a stable member identity and exact Contract-B evidence reference;
7. a content-derived receipt identity.

The sidecar must not relabel unresolved evidence as `support` or `counterevidence`.

## Carrier fixture

The apparatus will construct a released-1.0-valid, counterexample-derived carrier proposition with terminal state:

- result-set execution: `completed`;
- proposition execution: `completed / not_checkable`;
- conclusion verdict: `not_checkable`;
- terminal branch: `unresolved_categorical_relation`;
- one opaque `state:` causal basis member;
- no contribution object capable of naming the unresolved evidence.

The two admitted evidence references are derived from the CAL PR #100 multiplicity scenario:

- `U1`: `Alice did not review dossier before Bob archived dossier.`
- `U2`: `Alice did not review dossier after Bob archived dossier.`

This apparatus tests representation and authority, not the CAL semantic judgment itself. The upstream `U1/U2 -> independent sufficient unresolved alternatives` observation is treated as frozen external experimental ground truth from run `34506201889`; it is not recomputed here.

## Sidecar candidate under test

Research schema sentinel: `cal-producer-attribution-sidecar-rc1-v1`.

One attribution record binds one exact Contract C state basis to:

- `role=causal_non_deciding`;
- `causal_form=independent_sufficient_alternatives` for the two-member counterexample;
- sorted causal members, each with a content-derived `member_id` and exact `source_id`, `passage_id`, `passage_sha256`.

Member array order is non-semantic. Canonical sidecar generation sorts by `member_id`; a non-canonical wire order is rejected rather than silently reinterpreted.

## Required positives

P1. The carrier Contract C bytes validate unchanged under released Contract C 1.0 and exact whole-object hash binding.

P2. The carrier Contract C alone cannot reconstruct `U1` and `U2`; only the opaque state basis is present.

P3. The sidecar binds the exact carrier Contract C version, result-set ID, whole-object SHA, proposition ID/text hash and state basis ID.

P4. The sidecar independently validates both exact Contract-B evidence references.

P5. An independent consumer using only released Contract C + Contract-B index + sidecar reconstructs both `U1` and `U2` without CAL imports or semantic re-audit.

P6. The consumer reconstructs evidence-level `independent_sufficient_alternatives`, not merely a bag of two refs.

P7. The sidecar preserves `causal_non_deciding`; no support/counterevidence channel exists in the sidecar.

P8. Reversing builder input order for `U1/U2` produces identical canonical sidecar bytes and receipt identity.

P9. Released Contract C 1.0 bytes and identity are bit-for-bit unchanged by sidecar creation and consumption.

P10. Released Contract C regression remains green.

## Hard falsifiers

F1. Wrong Contract C whole-object SHA, result-set ID or version must fail.

F2. Wrong proposition ID/text hash or wrong state basis ID must fail.

F3. Wrong/missing Contract-B passage, source or passage hash must fail.

F4. Duplicate sidecar member identity or duplicate exact evidence ref must fail.

F5. Unknown sidecar role or causal form must fail.

F6. `single_necessary` with other than one member must fail.

F7. `independent_sufficient_alternatives` or `jointly_sufficient` with fewer than two members must fail.

F8. A member whose content-derived `member_id` does not match its evidence ref must fail.

F9. A receipt whose content-derived `receipt_id` is stale must fail.

F10. Non-canonical member ordering must fail at wire validation; reversed builder input must canonicalize to the same bytes before wire emission.

F11. Any requirement to alter released Contract C schema/validator or to map neutral evidence into support/counterevidence falsifies the bounded sidecar claim.

F12. Any consumer need to reopen CAL semantic code or re-read source prose to infer multiplicity falsifies the bounded sidecar claim.

## Competing interpretation to preserve

Even if the sidecar passes technically, Contract C 1.0 by itself remains insufficient for this demonstrated CAL-attributable causal provenance. Contract C's stated purpose is to carry CAL-attributable epistemic/result state required by legitimate downstream consumers. Therefore technical sidecar sufficiency does not automatically establish architectural preference.

The result must distinguish:

- **technical necessity:** whether a Contract C wire revision is required to preserve the missing information at all;
- **boundary fitness:** whether putting that information outside Contract C violates the intended Contract C ownership boundary enough to reject the sidecar despite technical success.

## Allowed outcomes

- `SUPPORTED_RICHER_SIDECAR_TECHNICALLY_SUFFICIENT`
- `FALSIFIED_RICHER_SIDECAR`
- `INCONCLUSIVE_SIDECAR_APPARATUS_INVALID`

A supported result falsifies only the claim that an in-band Contract C wire revision is technically necessary for this exact counterexample. It does not select the sidecar as the canonical architecture.
