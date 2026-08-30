# Contract D RC3 Candidate — Independent Consumption Authority

**Status:** research-only candidate; not a production release  
**Candidate version token:** `0.3.0-rc3`

## Purpose

Contract D records a Decision Engine policy conclusion about one exact target, bound to the exact upstream authority and exact Decision policy that were consumed.

Contract D is downstream of epistemic authority and upstream of operational Authorization.

It does not contain actor identity, approval, delegation, autonomy posture, execution permission, execution state, or execution receipts. Those remain downstream Authorization/execution state.

## Normative authority surface

A Contract D RC3 object contains:

- `contract_d_version`: exactly `0.3.0-rc3`;
- `input_authority`: exact upstream authority `kind`, logical `id`, and immutable `immutable_id`;
- `policy`: exact Decision policy `id` and `version`;
- `target`: exact target `kind`, logical `id`, and immutable `content_sha256`;
- `evaluation`: Decision evaluation state, and for completed evaluation the policy disposition;
- `effect`: for completed evaluation only, one registered typed/versioned effect with registered machine-semantic parameters;
- optional `metadata`: non-authoritative reason/explanation/diagnostic material.

A failed Decision evaluation has no `disposition` and no `effect`. A completed evaluation has disposition exactly `clear` or `hold` and has an effect. `hold` is a completed policy conclusion and is not evaluation failure.

## Version rule

The only supported RC3 candidate version is the exact JSON string `0.3.0-rc3`.

Unknown, future, aliased, numeric, or case-varied versions are not interpreted as RC3 and cannot acquire RC3 authority.

## Unknown-field rule

For an object declaring `0.3.0-rc3`, unknown fields are rejected at every Contract-D-owned structural object:

- top level;
- `input_authority`;
- `policy`;
- `target`;
- `evaluation`;
- `effect`;
- effect `params`;
- `metadata`.

`metadata.diagnostics` is intentionally opaque JSON diagnostic content. Its contents are never projected into Decision semantic identity or machine applicability. Authorization/execution-looking fields placed inside diagnostics remain diagnostic strings/data only.

## Upstream binding

`input_authority` is identity/applicability state, not downstream reinterpretation of upstream semantics.

A consumer may require an expected upstream authority and compare `kind`, `id`, and `immutable_id` exactly. It must not infer epistemic meaning from those strings.

For a Contract C input, `immutable_id` should be the exact immutable Contract C result-set/content identity the producer consumed.

## Target binding

Decision applicability binds all three independently:

1. `target.kind`;
2. `target.id`;
3. `target.content_sha256`.

Same-id replay after content change, or cross-kind replay under the same id/content, is not applicable.

## Policy binding

Decision applicability binds both `policy.id` and `policy.version`.

An independent consumer receives its expected Decision policy identity from its own configured applicability boundary, not from undocumented Decision Engine knowledge.

## Disposition and evaluation vocabulary

`evaluation.state` is exactly:

- `completed`;
- `failed`.

If `completed`, `evaluation.disposition` is exactly:

- `clear`;
- `hold`.

If `failed`, `evaluation.disposition` is absent and `effect` is absent.

A completed `hold` object records an established non-clear policy conclusion. A failed evaluation records that no policy conclusion was established.

## Effect registry

Machine authority is never inferred from `metadata.reason_codes`, explanation, or diagnostics.

The authoritative RC3 registry is `effect-registry.json`.

Known effect type + version selects one exact parameter schema. Unknown effect types, effect versions, and unknown parameters fail closed.

The registry is versioned independently as `effect_registry_version: "1"`.

RC3 contains three evidence-supported effect entries:

- `knowledge.add_verified_tag@1`
- `knowledge.cite_as_evidence@1`
- `task.dispatch@1`

The registry mechanism is not limited to those three entries. Adding a new type/version requires a later explicitly versioned registry/candidate decision.

### Safe defaults

`knowledge.add_verified_tag@1` has optional `scope` with the declared safe default `"claim"`.

Omitting `params`, supplying `{}`, omitting `scope`, and explicitly supplying `"scope": "claim"` normalize to the same machine-semantic effect and therefore the same Decision semantic identity.

No undeclared default is permitted.

## Requested-operation applicability

Contract D does not contain the requested operation as an Authorization field.

An independent consumer compares the external requested operation to the registered Decision `effect.type`, and compares any requested machine-semantic parameters to the normalized registered effect parameters.

A mismatch is non-applicable, not permission.

Actor, approval, delegation, trust/profile and other Authorization context can change a later Authorization result without modifying Contract D semantic identity.

## Canonical JSON

Normative canonical JSON bytes use:

1. UTF-8;
2. lexicographically sorted object keys;
3. compact separators `,` and `:`;
4. Unicode preserved rather than ASCII escaped;
5. finite JSON numbers only;
6. exactly one trailing newline.

Duplicate JSON object keys are invalid.

Array order is preserved.

Canonical transport bytes and semantic identity are related but not identical concepts: semantic identity hashes the normalized authority projection described below.

## Semantic identity

`semantic_identity` is:

`decision:sha256:` + lowercase SHA-256 of the canonical JSON bytes of the normalized authority projection.

The authority projection contains exactly:

- `contract_d_version`;
- `input_authority`;
- `policy`;
- `target`;
- `evaluation`;
- normalized registered `effect` for completed decisions.

It excludes `metadata`.

For a failed evaluation the projection contains no effect.

The normalized effect includes declared safe defaults. Therefore explicit safe defaults and their valid omission have the same semantic identity.

A stored `decision_id` is not part of RC3. Independent consumers derive semantic identity from the normative projection.

## Metadata

`metadata` may contain:

- `reason_codes`: array of non-empty strings;
- `explanation`: non-empty string;
- `diagnostics`: arbitrary finite JSON diagnostic content.

Metadata is non-authoritative. Mutating or removing it must not change semantic identity or applicability.

## Consumer outcomes

The reference applicability oracle returns one of:

- `candidate_for_authorization`: valid completed CLEAR Decision, exact applicability match;
- `hold`: valid completed HOLD Decision;
- `evaluation_failed`: valid failed Decision;
- `not_applicable`: valid Decision but target/upstream/policy/effect/request does not match;
- `cannot_establish`: object cannot be interpreted under exact RC3 authority, including unknown/future/malformed machinery.

`candidate_for_authorization` is not Authorization or execution permission.

## Evolution rule

An RC3 consumer only interprets the exact supported Contract D version and exact registered effect versions.

Unknown future Contract D versions, unknown effects, and unknown effect versions return `cannot_establish` or validation failure. They never inherit current authority.

A future candidate/version may explicitly define compatibility. RC3 defines no implicit forward compatibility.

## Explicit exclusions

Contract D RC3 does not establish or carry:

- actor identity;
- requested operation as stored Decision state;
- approval state;
- delegation state;
- autonomy mode;
- trust/profile state;
- execution permission;
- execution state;
- execution receipt;
- operational Authorization result;
- reinterpretation of Contract C epistemic semantics.

Those exclusions are authority boundaries, not missing convenience fields.
