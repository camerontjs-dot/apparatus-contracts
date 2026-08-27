# ADR: Contract B v1.2 optional factual-context extension

**Date:** 2026-08-27
**Status:** Accepted for production promotion
**PR class:** Promotion / Production
**Compatibility:** MINOR, candidate `1.2.0`

## Decision

Promote one optional, integrity-bound Contract B factual-context extension. The extension preserves upstream evidence-world context and audit/preparation history needed by Claim Audit Lab before proposition-specific assessment, while leaving the existing canonical Contract B claim/source/passage payloads authoritative for their existing fields.

The extension is a separate JSON member of the sealed C-B artifact at:

`extensions/contract-b-factual-context-v1.json`

It is included in the artifact tree hash and `SHA256SUMS`. Contract B 1.0/1.1 artifacts remain valid and are interpreted as `legacy_absent`. Contract B 1.2 artifacts may omit the extension, in which case an extension-aware consumer records `absent`; it must not invent defaults.

## Evidence basis

This decision is bounded by the completed Contract B research program:

- V0/V1/V2 conformance: `f4ee2dbd853821ba54328156bbab1c71235fae55`
- optional-extension + field-family ablation: `4fb5dcde81c3ae0a9a99133f6a3f721aeab639dc`
- original independent-consumer negative result, preserved as NOT REPRODUCIBLE: `40349629c289a340c95735510cf04b1926d200d0`
- temporal/version applicability: `41627c9a313ffd2c73d9b8ea54f1e018e2d676e7`
- RC1 explicit normalization + reproducibility: `aa016bcebd57dd09870a9cd4cc129ea7f7f5fc43`
- RC1 metamorphic/control suite: `b41191eab97f0e33e19cb8e195d6197e26ce15e2`
- decisive control run: `33088093642`, artifact `9653086317`, artifact digest `sha256:d6485dfe7ff833470e21bf96879bb31101cf3e37c6b074fe65f54d0903392ad7`

The failed control run `33088001635` and Deviation 001 remain part of the evidence record. The correction changed the frozen-consumer identity guard and recorded the deviation; it did not change consumers, fixture, falsifiers, or acceptance criteria.

## Promoted capability families

The extension may carry only the demonstrated upstream capability families:

- claim origin/lineage state;
- explicit known/unknown claim atomicity/structure state;
- provenance-bound factual context;
- typed representation anchors;
- complete nomination/admission/review history, including rejected-candidate recoverability;
- explicit history-completeness declaration;
- search/aperture observations and limitations;
- explicit known/unknown values;
- optional derived history-count checks that MUST equal counts recomputed from complete history.

Claim/source/passage text, hashes, identity, and other already-canonical Contract B payloads are referenced by identifier rather than copied into the extension.

## Authority boundary

The extension MUST NOT contain authoritative upstream fields for proposition-specific:

- support or refutation;
- semantic validity;
- temporal/lifecycle applicability;
- authority or supplier applicability;
- completeness conclusions;
- decision participation;
- verdict;
- abstention.

Version, effective-date, validation-date, supplier identity, and similar values may cross only as provenance-bound factual context. CAL owns any proposition-specific applicability judgment derived from those facts.

## Normalization and integrity

The extension uses the canonicalization rules in `contract-b-factual-context-extension-v1.2.0.md`: recursively sorted object keys, deterministic array ordering, compact UTF-8 JSON, direct Unicode, no NaN/Infinity, and one trailing newline. An extension that is present but unlisted in `SHA256SUMS`, malformed, non-canonical, reference-inconsistent, count-inconsistent, or contaminated with prohibited judgment fields fails closed.

## Count semantics

`candidate`, `reviewed`, and `admitted` counts are not independent evidence facts when history is declared complete. If supplied in `history_count_checks`, they are validation views only. Consumers recompute them from history and reject disagreement.

## CAL view separation

An extension-aware CAL consumer keeps two views:

1. a complete intake/audit ledger, preserving nomination metadata, rejected candidates, review metadata, context facts, aperture observations, and limitations;
2. a semantic-measurement context containing only admitted claim/source/passage references plus factual context and representation anchors.

Nomination rank/score/hypothesized role, reviewer identity/notes, rejected candidates, and upstream trust metadata do not enter the semantic-measurement context merely because they crossed Contract B.

## Version decision

This is a backward-compatible optional capability expansion, so the supported compatibility class is MINOR. Canonical version advances from `1.1.0` to `1.2.0`, while new validators/consumers continue accepting 1.0.0 and 1.1.0 artifacts.

## Explicit non-claims / evidence debt

This promotion does not establish universal field-level minimality, universal interoperability, corpus completeness, source legitimacy, CAL result packaging, or Contract C semantics. RC1 demonstrated deterministic cross-language reproduction by two code-isolated implementations on a frozen evidence world; both shared supervisory context. A fully isolated third consumer remains residual evidence debt, not a prerequisite for this bounded promotion.

Contract C remains a separate downstream research concern.