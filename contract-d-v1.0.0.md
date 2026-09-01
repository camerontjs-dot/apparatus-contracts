# Contract D v1.0.0

**Status:** canonical production contract; released only at the immutable `contract-d-v1.0.0` release identity after the Contract D v1.0.0 release gate completes.

## Purpose

Contract D records a Decision Engine policy conclusion about one exact target, bound to the exact upstream authority and exact Decision policy consumed. It is downstream of epistemic authority and upstream of operational Authorization.

Contract D does not contain actor identity, approval, delegation, autonomy posture, trust/profile state, execution permission, execution state, or execution receipts.

## Normative authority surface

A Contract D v1 object contains:

- `contract_d_version`: exactly `1.0.0`;
- `input_authority`: exact upstream authority `kind`, logical `id`, and immutable `immutable_id`;
- `policy`: exact Decision policy `id` and `version`;
- `target`: exact target `kind`, logical `id`, and immutable `content_sha256`;
- `evaluation`: state, and for completed evaluation the disposition;
- `effect`: for completed evaluation only, one registered typed/versioned effect with registered machine-semantic parameters;
- optional `metadata`: non-authoritative reason/explanation/diagnostic material.

A failed evaluation has no disposition and no effect. A completed evaluation has disposition exactly `clear` or `hold` and has an effect. HOLD is a completed policy conclusion, not evaluation failure.

## Version and unknown behavior

Only the exact JSON string `1.0.0` is interpreted as Contract D v1. Unknown, future, aliased, numeric, or case-varied versions cannot acquire v1 authority.

Unknown fields are rejected at every Contract-D-owned structural object: top level, `input_authority`, `policy`, `target`, `evaluation`, `effect`, effect `params`, and `metadata`.

Unknown evaluation states, dispositions, effect types, effect versions, and effect parameters fail closed.

## Interoperable finite JSON data model

Every accepted Contract D value, including `metadata.diagnostics`, must be genuine finite interoperable JSON data.

Contract D v1 adopts the RFC 8785 / JSON Canonicalization Scheme input constraints needed for deterministic cross-language canonicalization:

- object keys are strings containing valid Unicode scalar sequences;
- string values contain valid Unicode scalar sequences; unpaired UTF-16 surrogates are invalid;
- values are only object, array, string, number, boolean, or null;
- numbers are finite and interoperable with IEEE-754 binary64/JCS serialization;
- programmatically supplied host integer values must be in the inclusive safe-integer range `[-9007199254740991, 9007199254740991]`; larger exact integers should be represented as strings when integer semantics must be preserved;
- duplicate object keys are invalid when parsing JSON bytes;
- input bytes must be valid UTF-8;
- host-language-only values are invalid even inside diagnostics;
- cyclic decoded containers are invalid;
- shared-but-acyclic decoded containers remain valid;
- maximum object/array container nesting depth is **128**, counting the root object as depth 1. A value that would exceed depth 128 fails closed with `json_depth_exceeded`.

At JSON-byte ingress, an integer-form token outside the safe-integer range is interpreted only when it can enter the JCS binary64 domain without admitting an ambiguous precision-losing spelling. Such a token is accepted when either (a) the decimal integer is exactly representable as binary64, or (b) the token is already the RFC 8785/JCS canonical shortest-roundtrip decimal serialization of the binary64 value it maps to. A token such as `9007199254740993` satisfies neither condition and is rejected with `non_interoperable_integer`. Canonical RFC 8785 samples such as `295147905179352830000` remain valid.

The depth limit is a deterministic contract processing bound, not an authority-bearing field.

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

The authoritative registry is `schema/contract-d/1.0.0/effect-registry.json`, registry version `1`.

Contract D v1 contains:

- `knowledge.add_verified_tag@1`
- `knowledge.cite_as_evidence@1`
- `task.dispatch@1`

Known effect type + version selects one exact parameter schema.

For `knowledge.add_verified_tag@1`, optional `scope` has the declared safe default `"claim"`. Omitting params, supplying `{}`, omitting scope, and explicitly supplying `"scope":"claim"` normalize to the same Decision effect and semantic identity. Explicit `"scope":"object"` remains distinct. No undeclared default is permitted.

For every valid completed Decision, normalization of the registered effect produces a JSON object with **exactly** these three properties:

- `type`;
- `version`;
- `params`.

`params` is always present and contains the complete normalized machine-semantic parameter map after applying only registry-declared defaults. For `knowledge.cite_as_evidence@1` and `task.dispatch@1`, whose parameter schemas are empty, the normalized value is exactly `"params": {}`.

Safe-default normalization applies to the stored Decision effect. It does not invent constraints in the external requested-operation boundary.

## Requested-operation and requested-parameter applicability

The requested operation is external Authorization context and is not stored in Contract D.

For a completed Decision, including HOLD, the consumer must:

1. validate the Decision;
2. validate the external applicability expectation shape;
3. compare expected upstream authority, policy, and target;
4. normalize the registered Decision effect;
5. compare the external requested operation exactly to normalized `effect.type`;
6. if external requested machine-semantic parameters are supplied, treat only those supplied keys as constraints and compare them exactly to the normalized Decision effect parameters;
7. only after those applicability checks return `hold` for HOLD or `candidate_for_authorization` for CLEAR.

The external applicability expectation is a typed input boundary. Its upstream, policy, target, requested-operation, and requested-parameter values must be v1-valid interoperable finite JSON; its expected target `content_sha256` must have the same `sha256:` + 64 lowercase-hex shape required by the Decision target. Host-language-only values, non-finite/non-interoperable numbers, invalid Unicode scalars, malformed containers, missing/extra binding keys, or malformed target hashes make the expectation invalid rather than merely nonmatching.

Therefore a completed HOLD reused for a different requested operation or conflicting requested parameter is `not_applicable`, not `hold`.

If external requested effect parameters are absent or `{}`, that means **no parameter constraint was requested**. Registry defaults are not injected into the external request.

Malformed external applicability expectation containers or values produce `cannot_establish` with reason `invalid_expectation`.

A failed evaluation has no effect to match; after upstream/policy/target applicability succeeds, its outcome is `evaluation_failed`.

## Canonical JSON

Contract D v1 canonical JSON is **RFC 8785 JSON Canonicalization Scheme (JCS)** serialization of the accepted value, followed by exactly one LF byte (`0x0A`).

Consequences include:

- no insignificant whitespace;
- object property sorting recursively by raw UTF-16 code units as defined by RFC 8785;
- ECMAScript/JCS number serialization;
- Unicode strings preserved without normalization;
- invalid Unicode such as lone surrogates rejected;
- non-finite or non-interoperable numbers rejected;
- array order preserved;
- UTF-8 output;
- exactly one trailing newline added by Contract D after the JCS payload.

Canonical transport bytes and semantic identity remain distinct.

## Semantic identity

`semantic_identity` is `decision:sha256:` plus lowercase SHA-256 of Contract-D canonical JSON bytes for the normalized authority projection containing exactly:

- `contract_d_version`;
- `input_authority`;
- `policy`;
- `target`;
- `evaluation`;
- normalized registered `effect` for completed decisions.

The normalized effect in the projection has exactly `type`, `version`, and `params`, including explicit `params: {}` for an empty parameter schema. Two otherwise equivalent completed Decisions that differ only by omission versus explicit `{}` in an empty-schema stored effect have the same semantic identity.

Metadata is excluded. Failed decisions have no effect in the projection. Authorization-only context never changes Decision semantic identity.

## Metadata

Metadata may contain `reason_codes` (array of non-empty strings), `explanation` (non-empty string), and `diagnostics` (arbitrary v1-valid interoperable finite JSON within the deterministic depth bound). Metadata is non-authoritative and cannot create machine authority.

## Controlled failure boundary

A public validator/canonicalizer/consumer operation must not leak runtime recursion, Unicode encoding, or canonicalizer-specific exceptions for an in-domain Contract D v1 input. Such failures are translated into Contract-D fail-closed errors or `cannot_establish` outcomes.

This does not promise unlimited input size or immunity from process-level resource exhaustion. It requires the explicit depth and value-domain controls above to be enforced before authority-bearing outcomes are returned.

## Consumer outcomes

- `candidate_for_authorization`: valid completed CLEAR Decision with exact applicability;
- `hold`: valid completed HOLD Decision with exact applicability;
- `evaluation_failed`: valid failed Decision after upstream/policy/target applicability succeeds;
- `not_applicable`: valid Decision but required applicability binding does not match;
- `cannot_establish`: Decision or applicability expectation cannot be interpreted under exact v1 authority.

`candidate_for_authorization` is not Authorization or execution permission.

## Explicit exclusions

Contract D v1 does not establish or carry actor identity, requested operation as stored Decision state, approval, delegation, autonomy, trust/profile state, execution permission, execution state, execution receipt, operational Authorization result, or reinterpretation of upstream epistemic semantics.

## Promotion lineage

This proposed v1 surface is the production transcription authorized by EDR-003 after the terminal RC6 independent reproduction at `camerontjs-dot/research-scaffold-harness@1b51b421b96fb10f260f58a087c8376b35afdb5d`. Research RC identities remain evidence records and are not supported production versions.
