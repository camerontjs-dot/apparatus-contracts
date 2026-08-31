# Contract D RC6 Candidate — Independent Consumption Authority

**Status:** research-only successor candidate; not a production release  
**Candidate version token:** `0.3.0-rc6`

## Normative basis

RC6 is the smallest successor to Contract D RC5 required by the terminal fresh independent reproduction recorded at `camerontjs-dot/research-scaffold-harness@39b75abb98b073517c12e08490640facaa764746`.

Except where this document explicitly replaces RC5 wording, RC6 incorporates the complete public Contract D RC5 specification at immutable blob `57fa4ca59efced5e35115551b1aa57dbbc7f6b2c` (`research/contract-d-independent-authority-rc5/candidate/SPEC.md` at candidate commit `f0f7a9684cf114159ca1cfe1c9f11b626a07e6c8`). That incorporated authority includes the Decision/Authorization separation, exact upstream/policy/target applicability, completed CLEAR/HOLD/failed distinctions, registered typed effects, interoperable finite JSON constraints, RFC 8785/JCS canonicalization, deterministic depth-128 processing, controlled failure behavior, metadata non-authority, and the RC5 consumer outcome vocabulary.

RC6 makes only two normative changes to that incorporated text:

1. every occurrence of the candidate version token `0.3.0-rc5` is replaced by `0.3.0-rc6` for RC6 objects and exact-version handling;
2. the normalized registered-effect representation is made explicit and total as specified below.

No other Decision meaning, applicability rule, Authorization boundary, effect vocabulary, resource bound, canonicalization rule, or consumer outcome is changed by RC6.

## Exact normalized registered-effect representation

For every valid completed RC6 Decision, normalization of the registered Decision effect MUST produce a JSON object with **exactly** these three properties:

- `type`: the registered effect type string;
- `version`: the registered effect version string;
- `params`: a JSON object containing the complete normalized machine-semantic parameter map after applying only registry-declared defaults.

The `params` property is always present in the normalized effect, even when the selected effect schema declares zero parameters. Therefore the normalized forms of both:

```json
{"type":"knowledge.cite_as_evidence","version":"1"}
```

and:

```json
{"type":"knowledge.cite_as_evidence","version":"1","params":{}}
```

are exactly:

```json
{"type":"knowledge.cite_as_evidence","version":"1","params":{}}
```

The same rule applies to `task.dispatch@1`, whose normalized empty parameter map is also exactly `"params": {}`.

For `knowledge.add_verified_tag@1`, the existing safe-default rule is unchanged: omitted `params`, `{}`, omitted `scope`, and explicit `"scope":"claim"` normalize to an effect whose `params` is exactly `{"scope":"claim"}`. Explicit `"scope":"object"` remains distinct.

This rule concerns the normalized **stored Decision effect** only. It does not change the external requested-parameter rule: absent external requested parameters or `{}` still mean that no external parameter constraint was requested, and registry defaults are not injected into the external request.

## Semantic projection and identity

For a completed RC6 Decision, the `effect` member of the semantic authority projection MUST be the exact normalized registered-effect object defined above, including an explicit empty `params` object for an empty parameter schema.

`semantic_identity` therefore hashes the canonical RC6 authority projection with that explicit total effect shape. Two otherwise equivalent completed RC6 Decisions that differ only by omission versus explicit `{}` in an empty-schema stored effect MUST have the same semantic identity.

Metadata remains excluded from the semantic projection. Failed evaluations still have no effect in the projection. Authorization-only context never changes Decision semantic identity.

## Rationale and evidence boundary

The RC5 fresh independent reproduction produced 101 agreements and two authority-relevant non-agreements out of 103 comparisons, with zero `AUTHORITY_RELEVANT_DISAGREEMENT`. Both non-agreements arose solely because RC5 public wording did not explicitly say whether an empty normalized parameter map was represented as an omitted property or as `params: {}`. The reference implementation used the latter while the independently frozen implementation chose the former. That result was correctly classified `PUBLIC_AUTHORITY_AMBIGUITY` and the RC5 disposition remains `INCONCLUSIVE`.

RC6 resolves that ambiguity by making the normalized representation mechanically recoverable. This document does not retroactively reclassify the RC5 result and does not authorize production promotion or release.

## Explicit non-claims

RC6 does not establish or carry actor identity, approval, delegation, autonomy, trust/profile state, execution permission, execution state, execution receipt, operational Authorization result, or reinterpretation of upstream epistemic semantics.

A successful RC6 conformance or independent-reproduction result is research evidence only. Production Contract D `1.0.0` promotion remains a separate bounded governance decision.
