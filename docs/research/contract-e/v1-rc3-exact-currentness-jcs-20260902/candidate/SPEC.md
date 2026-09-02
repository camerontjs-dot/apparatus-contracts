# Contract E Authority Evaluation Candidate RC3

Status: **research-only successor candidate**

Candidate identifier: `contract-e-authority-evaluation-candidate-rc3`

RC3 is a true successor to terminal RC1 and RC2 research candidates. Prior failures remain immutable evidence. This specification does not authorize production promotion, execution, or verification.

## 1. Purpose

Contract E answers one bounded control-plane question:

> Does the exact supplied standing AuthorityState authorize this exact subject to perform this exact operation, in this exact jurisdiction, against this exact immutable target, at this exact evaluation time?

Contract E does not decide whether upstream evidence is true, whether CAL or a Decision policy is correct, whether a root authority source is legitimate, whether an operation should occur, whether execution occurred, or whether verification succeeded.

## 2. Normative objects

RC3 has two normative inputs and one audit output:

1. `AuthorityState`: immutable authority-bearing state supplied separately from a request.
2. `AuthorizationRequest`: a transient request for one exact operation/target.
3. `AuthorizationReceipt`: deterministic, non-conferring evidence of evaluating 1 against 2.

A request MUST NOT embed, manufacture, repair, or override standing authority.

AuthorityState root provenance/legitimacy is an external trust/configuration boundary. RC3 validates structure, canonical identity, lineage, exact bounds, exact currentness, and exact applicability. A content hash is an integrity binding, not origin authentication.

## 3. Canonical bytes and deterministic identity

Every deterministic RC3 JSON hash or identity uses the same canonical-byte rule:

1. the value MUST be representable in the I-JSON domain accepted by RFC 8785 JSON Canonicalization Scheme (JCS);
2. serialize using RFC 8785 JCS exactly;
3. encode the JCS result as UTF-8;
4. append exactly one ASCII LF byte (`0x0A`).

Non-finite numbers, unsupported host-only values, non-string object keys, cyclic decoded containers, and values outside the JCS domain are rejected.

Raw JSON ingestion MUST reject duplicate member names before decoding. An API receiving an already-decoded dictionary cannot recover duplicate raw members discarded upstream and MUST NOT claim it proved duplicate-free raw input.

This canonical-byte rule applies to:

- AuthorityState computed identity;
- immutable reference identity;
- request SHA-256;
- AuthorizationReceipt semantic identity / `receipt_id`.

No implementation-local number rendering, key ordering, escaping, whitespace, or fallback serializer may substitute.

## 4. AuthorityState

Schema token: `contract-e-authority-state-candidate-rc3`.

An AuthorityState contains exactly one non-branching authority chain.

### 4.1 Root

The first record MUST:

- have `basis_type` exactly `grant` or `policy`;
- contain non-empty scalar `subject_id`, `domain`, `operation`, `scope`, `target_class`;
- contain SHA-256 `target_ref`;
- contain explicit `valid_from`, optional `valid_until`, optional `revoked_at`;
- have `parent_id=null` and `delegated_by=null`.

### 4.2 Delegation

Every later record MUST:

- have `basis_type=delegation`;
- name the immediately preceding record by `parent_id`;
- set `delegated_by` exactly to the parent `subject_id`;
- contain a new explicit `subject_id`;
- preserve `domain`, `operation`, `scope`, `target_class`, and `target_ref` exactly equal to the parent.

Delegation may change the authorized subject only. There is no containment, inheritance, wildcard, alias, group, union, `any-of`, narrowing, or widening semantics.

All authority-record IDs MUST be unique. Duplicate IDs, branching, skipped/non-immediate parent links, missing parents, cycles, or a non-delegation descendant invalidate the state.

RC3 does not evaluate peer/surplus conferring alternatives.

### 4.3 Exact timestamp grammar

Authority and request timestamps use UTC `Z` form:

`YYYY-MM-DDTHH:MM:SS[.fraction]Z`

The optional fraction contains one or more decimal digits and may have arbitrary positive precision.

Timestamps MUST be calendar-valid. Seconds are `00` through `59`; leap seconds are rejected.

Chronological comparison MUST preserve the exact stated fractional precision and MUST NOT truncate, round, or coerce to host datetime precision. Numerically equivalent fractions such as `.1`, `.10`, and `.100` represent the same instant.

At request `evaluation_time`, every authority record MUST satisfy:

- `evaluation_time >= valid_from`;
- if `valid_until` is present, `evaluation_time <= valid_until`;
- if `revoked_at` is present, `evaluation_time < revoked_at`.

`valid_from` and `valid_until` boundaries are inclusive. Revocation is effective at and after `revoked_at`.

No status string, confidence, agreement count, or cached currentness claim substitutes for recomputation.

### 4.4 Claimed and recomputed AuthorityState identity

`AuthorityState.authority_state_id` is the supplied claimed identity.

The recomputed identity is `sha256:` plus SHA-256 over RC3 canonical bytes of the supplied AuthorityState excluding `authority_state_id` itself.

For authorization, the claimed identity MUST be syntactically valid SHA-256, recomputation MUST succeed, and both identities MUST be equal.

## 5. AuthorizationRequest

Schema token: `contract-e-authorization-request-candidate-rc3`.

The request contains exactly:

- `schema`;
- non-empty `request_id`;
- SHA-256 `authority_state_id`;
- exact UTC `evaluation_time`;
- non-empty `subject_id`;
- exact jurisdiction object: `domain`, `operation`, `scope`, `target_class`, `target_ref`;
- `references`;
- `supporting_artifacts`;
- `conflicts`;
- `residues`.

Unknown, missing, or malformed fields fail closed.

### 5.1 Immutable references

Each reference contains exactly:

- unique request-local `ref_id`;
- non-empty opaque `kind`;
- optional non-empty `version` or null;
- non-empty opaque `immutable_id`;
- `identity_sha256` computed from RC3 canonical bytes of `{kind, version, immutable_id}`.

`jurisdiction.target_ref` is an immutable `identity_sha256` and MUST resolve to exactly one validated request reference.

Referenced Contract A/B/C/D objects remain opaque identities. Their payloads, facts, conclusions, or Decisions do not become standing Contract E authority.

### 5.2 Supporting artifacts

Each supporting artifact contains exactly unique request-local `id`, non-empty `artifact_type`, and `ref_id`. Its `ref_id` MUST resolve to one request reference.

Supporting artifacts are always non-conferring. They may include A/B/C/D objects, competence material, citations, execution reports, prior receipts, or provenance evidence. None can replace or repair AuthorityState.

### 5.3 Conflicts and residues

Conflict IDs are unique within `conflicts`; residue IDs are unique within `residues`.

Each blocker has status exactly `unresolved` or `contested` and explicit `relevant` boolean.

A relevant blocker blocks every supplied request, including a `domain=resolution`, `operation=resolve` request that carries that blocker.

RC3 accepts no request-side discharge or `resolved_*` field.

A separate resolution operation can be authorized only when its own request has no relevant blocker. Applying, proving, or persisting a resolution is outside RC3.

## 6. Evaluation predicate

A request is authorized only when all are true:

1. AuthorityState is structurally valid.
2. AuthorityState claimed identity is syntactically valid.
3. AuthorityState recomputed identity is available and equals the claimed identity.
4. AuthorizationRequest is structurally valid.
5. Request `authority_state_id` exactly equals the valid AuthorityState identity.
6. No relevant conflict or residue is supplied.
7. Every authority record is exactly current and unrevoked at request `evaluation_time`.
8. The complete authority chain is valid and non-amplifying.
9. Terminal `subject_id` exactly equals request `subject_id`.
10. Terminal `domain`, `operation`, `scope`, `target_class`, and `target_ref` exactly equal request jurisdiction.
11. Request target identity resolves to a validated reference.
12. Every supporting-artifact `ref_id` resolves request-locally.

There is no partial-record aggregation, peer conferring alternative set, Qualification predicate, semantic composition, embedding inference, wildcard, or default allow.

## 7. AuthorizationReceipt

Schema token: `contract-e-authorization-receipt-candidate-rc3`.

The receipt contains exactly the machine-schema fields including:

- deterministic `receipt_id` when its semantic projection is canonicalizable;
- `authority_conferring=false`;
- `authorized` boolean;
- request identity/hash when representable;
- `claimed_authority_state_id`;
- `recomputed_authority_state_id`;
- evaluation time, subject, and jurisdiction when individually representable;
- terminal `authority_basis_id` only when authorized;
- `preserved` request observations;
- diagnostic strings.

### 7.1 Dual AuthorityState identity

`claimed_authority_state_id` is the exact supplied AuthorityState `authority_state_id` only when it is syntactically valid SHA-256, otherwise null.

`recomputed_authority_state_id` is independently recomputed from the supplied AuthorityState excluding `authority_state_id` whenever that supplied state is a canonicalizable JSON object, even if the state later fails structural validation; otherwise null.

A valid state yields equal non-null values. A canonicalizable state with a forged claimed identity yields unequal non-null values and MUST be denied.

Both fields participate in receipt semantic identity. Neither field confers authority.

### 7.2 Request hash and safe preservation

`request_sha256` is computed over the complete request whenever that request is canonicalizable JSON, even if structurally invalid; otherwise null.

For a structurally valid request, all four preserved lists are exact deep copies.

For a structurally invalid request, a preserved list is copied only if its top-level value is a list and every element independently satisfies that list's schema item shape. Otherwise that preserved list is empty.

Cross-list semantic validity is not required merely to preserve an individually schema-shaped observation. Preservation never repairs authorization.

### 7.3 Receipt semantic identity

Receipt semantic identity is SHA-256 over RC3 canonical bytes of the receipt excluding only `receipt_id` and `diagnostics`.

Diagnostic vocabulary/order is non-authoritative. Diagnostics do not participate in `receipt_id`.

The receipt is evidence that evaluation occurred. It is not standing authority, origin authentication, a reusable execution permit, proof of execution, or proof of verification.

## 8. Pipeline and trusted-origin boundary

- Contract A declaration/producer identity does not confer E authority.
- Contract B evidence/facts do not confer E authority.
- Contract C epistemic state/confidence does not confer E authority.
- Contract D `candidate_for_authorization` does not confer execution permission.
- A Decision hash proves exact binding, not trusted Decision Engine origin.
- An AuthorityState hash proves exact binding, not root legitimacy.
- A prior receipt is historical evidence, not standing permission.
- A consumer requiring current authority must re-evaluate current AuthorityState at point of use.
- Authorization does not establish execution occurrence.
- Execution occurrence does not establish verification.

Trusted producer/root bindings are consuming-profile concerns outside the core RC3 predicate.

## 9. Explicit exclusions

RC3 does not define:

- Qualification subject/scope or competence as authority;
- surplus/multiple peer authority quantification;
- partial authority synthesis;
- delegation containment/narrowing/widening;
- signatures, PKI, attestation, or real-world root authentication;
- roles/groups/wildcards;
- reusable permits or leases;
- distributed locking/exactly-once execution;
- execution occurrence/proof;
- verification proof;
- a universal authority ontology.

## 10. Successor and promotion rule

RC3 intentionally preserves the lessons of prior failures:

- RC1's single receipt state identity is replaced by two separately named facts.
- RC2's RFC 8785 + LF canonicalization is preserved.
- RC2's host-microsecond currentness path is replaced by exact arbitrary-precision ordering.
- blocker behavior is explicitly fail-closed for every supplied request.

`candidate-rc3` is research identity, not a release version. Unknown/future schema tokens fail closed.

RC3 may be proposed as a semantic basis for production only after frozen adversarial evidence and fresh independent reproduction are supported. This specification does not authorize promotion, tag, or release.
