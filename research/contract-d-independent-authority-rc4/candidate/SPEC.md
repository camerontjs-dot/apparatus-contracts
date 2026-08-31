# Contract D RC4 Candidate — Independent Consumption Authority

**Status:** research-only candidate; not a production release  
**Candidate version token:** `0.3.0-rc4`

## Purpose

Contract D records a Decision Engine policy conclusion about one exact target, bound to the exact upstream authority and exact Decision policy consumed. It is downstream of epistemic authority and upstream of operational Authorization.

Contract D does not contain actor identity, approval, delegation, autonomy posture, execution permission, execution state, or execution receipts.

## Normative authority surface

A Contract D RC4 object contains:

- `contract_d_version`: exactly `0.3.0-rc4`;
- `input_authority`: exact upstream authority `kind`, logical `id`, and immutable `immutable_id`;
- `policy`: exact Decision policy `id` and `version`;
- `target`: exact target `kind`, logical `id`, and immutable `content_sha256`;
- `evaluation`: state, and for completed evaluation the disposition;
- `effect`: for completed evaluation only, one registered typed/versioned effect with registered machine-semantic parameters;
- optional `metadata`: non-authoritative reason/explanation/diagnostic material.

A failed evaluation has no disposition and no effect. A completed evaluation has disposition exactly `clear` or `hold` and has an effect. HOLD is a completed policy conclusion, not evaluation failure.

## Version and unknown behavior

Only the exact JSON string `0.3.0-rc4` is interpreted as RC4. Unknown, future, aliased, numeric, or case-varied versions cannot acquire RC4 authority.

For an RC4 object, unknown fields are rejected at every Contract-D-owned structural object: top level, `input_authority`, `policy`, `target`, `evaluation`, `effect`, effect `params`, and `metadata`.

Unknown evaluation states, dispositions, effect types, effect versions, and effect parameters fail closed.

## JSON data model and ingress

Every accepted Contract D value, including `metadata.diagnostics`, must be genuine finite JSON data:

- object keys are strings;
- values are only object, array, string, number, boolean, or null;
- numbers are finite;
- duplicate object keys are invalid when parsing JSON bytes;
- input bytes must be valid UTF-8.

Host-language-only values are invalid even inside diagnostics. Diagnostics are opaque for authority, but they are still JSON.

## Upstream, policy, and target binding

Applicability binds exactly:

- upstream `kind`, `id`, and `immutable_id`;
- policy `id` and `version`;
- target `kind`, `id`, and `content_sha256`.

Same-id replay after immutable content changes, cross-kind replay, upstream substitution, policy substitution, and policy-version substitution are non-applicable.

## Evaluation vocabulary

`evaluation.state` is exactly `completed` or `failed`.

If completed, `evaluation.disposition` is exactly `clear` or `hold` and `effect` is required.

If failed, disposition and effect are absent.

## Effect registry and safe defaults

The authoritative registry is `effect-registry.json`, version `1`.

RC4 contains:

- `knowledge.add_verified_tag@1`
- `knowledge.cite_as_evidence@1`
- `task.dispatch@1`

Known effect type + version selects one exact parameter schema.

For `knowledge.add_verified_tag@1`, optional `scope` has the declared safe default `"claim"`. Omitting params, supplying `{}`, omitting scope, and explicitly supplying `"scope":"claim"` normalize to the same Decision effect and semantic identity. No undeclared default is permitted.

Safe-default normalization applies to the stored Decision effect. It does **not** invent constraints in the external requested-operation boundary.

## Requested-operation and requested-parameter applicability

The requested operation is external Authorization context and is not stored in Contract D.

For a completed Decision, including HOLD, the consumer must:

1. validate the Decision;
2. compare expected upstream authority, policy, and target;
3. normalize the registered Decision effect;
4. compare the external requested operation exactly to normalized `effect.type`;
5. if external requested machine-semantic parameters are supplied, treat only those supplied keys as constraints and compare them exactly to the normalized Decision effect parameters;
6. only after those applicability checks return `hold` for HOLD or `candidate_for_authorization` for CLEAR.

Therefore a completed HOLD reused for a different requested operation or conflicting requested parameter is `not_applicable`, not `hold`.

If external requested effect parameters are absent or `{}`, that means **no parameter constraint was requested**. Registry defaults are not injected into the external request. For example, a Decision effect normalized to `{"scope":"object"}` remains applicable when the caller supplies no requested effect parameters, but is non-applicable when the caller explicitly requests `{"scope":"claim"}`.

A failed evaluation has no effect to match; after upstream/policy/target applicability succeeds, its outcome is `evaluation_failed`.

## Canonical JSON

Normative canonical JSON bytes use UTF-8, lexicographically sorted object keys, compact separators, Unicode preserved rather than ASCII escaped, finite JSON numbers only, array order preserved, and exactly one trailing newline.

Canonical transport bytes and semantic identity are distinct.

## Semantic identity

`semantic_identity` is `decision:sha256:` plus lowercase SHA-256 of canonical JSON bytes for the normalized authority projection containing exactly:

- `contract_d_version`;
- `input_authority`;
- `policy`;
- `target`;
- `evaluation`;
- normalized registered `effect` for completed decisions.

Metadata is excluded. Failed decisions have no effect in the projection.

Authorization-only context never changes Decision semantic identity.

## Metadata

Metadata may contain `reason_codes` (array of non-empty strings), `explanation` (non-empty string), and `diagnostics` (arbitrary finite JSON). Metadata is non-authoritative and cannot create machine authority.

## Consumer outcomes

- `candidate_for_authorization`: valid completed CLEAR Decision with exact applicability;
- `hold`: valid completed HOLD Decision with exact applicability;
- `evaluation_failed`: valid failed Decision after upstream/policy/target applicability succeeds;
- `not_applicable`: valid Decision but required applicability binding does not match;
- `cannot_establish`: object cannot be interpreted under exact RC4 authority.

`candidate_for_authorization` is not Authorization or execution permission.

## Explicit exclusions

RC4 does not establish or carry actor identity, requested operation as stored Decision state, approval, delegation, autonomy, trust/profile state, execution permission, execution state, execution receipt, operational Authorization result, or reinterpretation of upstream epistemic semantics.
