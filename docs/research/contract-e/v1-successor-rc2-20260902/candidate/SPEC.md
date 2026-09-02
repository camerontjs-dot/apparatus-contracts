# Contract E Authority Evaluation Candidate RC2

Status: **research-only successor candidate**

Candidate identifier: `contract-e-authority-evaluation-candidate-rc2`

RC2 is a true successor to the terminal-falsified RC1 candidate. RC1 remains immutable evidence.

This specification does not authorize production promotion, execution, or verification.

## 1. Purpose

Contract E answers one bounded question:

> Does the exact supplied standing authority state authorize this exact subject to perform this exact operation, in this exact jurisdiction, against this exact immutable target, at this exact evaluation time?

Contract E does not decide whether upstream evidence is true, CAL is correct, a Decision policy is correct, an operation should occur, an operation occurred, or verification succeeded.

## 2. Normative object boundary

The candidate has two normative inputs and one audit output:

1. `AuthorityState` — immutable authority-bearing control-plane state supplied separately from the request.
2. `AuthorizationRequest` — transient request for an exact operation/target.
3. `AuthorizationReceipt` — deterministic non-conferring result of evaluating 1 against 2.

A request MUST NOT embed, manufacture, or override standing authority.

AuthorityState provenance/legitimacy is an **external trust/configuration boundary**. RC2 validates AuthorityState structure, canonical identity, lineage, bounds, currentness, and applicability. A self-consistent content hash does not prove who was entitled to create a root grant or policy.

## 3. AuthorityState

Schema token: `contract-e-authority-state-candidate-rc2`.

An AuthorityState contains exactly one non-branching authority chain.

### 3.1 Root

The first record MUST:

- have `basis_type` exactly `grant` or `policy`;
- contain complete `subject_id`, `domain`, `operation`, `scope`, `target_class`, and `target_ref`;
- contain explicit `valid_from`, optional `valid_until`, and optional `revoked_at`;
- have `parent_id=null` and `delegated_by=null`.

### 3.2 Delegation

Every later record MUST:

- have `basis_type=delegation`;
- name the immediately preceding record by `parent_id`;
- set `delegated_by` exactly to the parent `subject_id`;
- contain a new explicit authorized `subject_id`;
- preserve `domain`, `operation`, `scope`, `target_class`, and `target_ref` exactly equal to the parent.

Delegation may change the authorized subject only. RC2 has no containment, inheritance, wildcard, alias, union, `any-of`, narrowing, or widening semantics.

All record IDs MUST be unique. Duplicate IDs, branching, skipped/non-immediate parent links, missing parents, or cycles invalidate the state.

### 3.3 Currentness and revocation

At `AuthorizationRequest.evaluation_time`, every record MUST satisfy:

- `evaluation_time >= valid_from`;
- if `valid_until` is present, `evaluation_time <= valid_until`;
- if `revoked_at` is present, `evaluation_time < revoked_at`.

Validity boundaries are inclusive. Revocation is effective at and after `revoked_at`.

No status string, confidence, agreement count, or cached `current=true` claim substitutes for recomputation.

### 3.4 Canonical identity

AuthorityState canonical identity is `sha256:` plus SHA-256 of the canonical bytes of the supplied AuthorityState excluding `authority_state_id` itself.

RC2 canonical bytes are defined exactly as:

1. the JSON value MUST be representable in the I-JSON domain accepted by RFC 8785 JSON Canonicalization Scheme (JCS); non-finite numbers, unsupported host-only values, non-string object keys, duplicate raw JSON member names, cyclic decoded containers, and values outside that canonicalization domain are rejected;
2. serialize the value using **RFC 8785 JCS** exactly;
3. encode the RFC 8785 result as UTF-8;
4. append **exactly one ASCII LF byte (`0x0A`)**.

No implementation-local JSON-number formatting, key-ordering rule, whitespace rule, Unicode escaping policy, or fallback serializer may substitute for RFC 8785.

This clarification is evidence-driven. A pre-freeze discriminator showed that the earlier RC2 wording produced different canonical bytes for malformed numeric AuthorityState input under Python's ordinary sorted compact JSON serialization versus RFC 8785, even though valid-state bytes agreed. Because `recomputed_authority_state_id` is preserved on canonicalizable invalid state and participates in receipt semantic identity, an underspecified number grammar would recreate the exact class of independent-recoverability ambiguity RC2 is intended to eliminate.

For a valid AuthorityState, the supplied `authority_state_id` MUST equal the recomputed canonical identity.

Identity is an integrity binding, not origin authentication.

## 4. AuthorizationRequest

Schema token: `contract-e-authorization-request-candidate-rc2`.

The request MUST contain:

- `request_id`;
- exact `authority_state_id` claimed by the request;
- explicit UTC `evaluation_time`;
- exact `subject_id`;
- exact typed jurisdiction: `domain`, `operation`, `scope`, `target_class`, `target_ref`;
- immutable `references`;
- separate `supporting_artifacts`;
- explicit `conflicts` and `residues` arrays.

Authority-critical bindings are scalar exact-equality bindings. Missing, malformed, unknown, or future RC2 fields fail closed.

### 4.1 Immutable references

Each reference contains local `ref_id`, opaque `kind`, optional `version`, opaque immutable identifier, and deterministic `identity_sha256` over `{kind, version, immutable_id}` using the same RC2 RFC 8785 + LF canonical-byte rule.

`jurisdiction.target_ref` is an immutable `identity_sha256` and MUST resolve to a validated request reference.

Referenced Contract A/B/C/D objects are opaque identities. Their payloads, conclusions, or Decisions do not become standing Contract E authority.

### 4.2 Supporting artifacts

Supporting artifacts are always non-conferring. Examples include A declarations, B factual state, C epistemic state, D `candidate_for_authorization` Decisions, competence material, citations, execution reports, and prior AuthorizationReceipts.

No supporting artifact can replace AuthorityState, repair an invalid AuthorityState, or confer root legitimacy.

### 4.3 Conflicts and residues

A relevant conflict or residue in status `unresolved` or `contested` blocks ordinary authorization. Irrelevant items are preserved but do not block.

Request-side `resolved_*_ids` or equivalent discharge claims are not accepted. A separate exact `resolution/resolve` request may itself be authorized, but applying a resolution is outside RC2.

## 5. Evaluation

A request is authorized only when all are true:

1. AuthorityState is structurally valid and its supplied identity matches its recomputed canonical identity.
2. AuthorizationRequest is structurally valid.
3. Request `authority_state_id` exactly matches the valid supplied AuthorityState identity.
4. No relevant unresolved/contested conflict or residue blocks the ordinary request.
5. Every AuthorityState record is current and unrevoked at `evaluation_time`.
6. The complete authority chain is valid and non-amplifying.
7. Terminal chain `subject_id` exactly equals request `subject_id`.
8. Terminal chain `domain`, `operation`, `scope`, `target_class`, and `target_ref` exactly equal request jurisdiction.
9. Request `target_ref` resolves to a validated immutable reference.

There is no partial-record aggregation, peer conferring alternative set, Qualification predicate, semantic comparison/composition/embedding interpretation, or trusted-origin inference from content hashes.

## 6. AuthorizationReceipt

Schema token: `contract-e-authorization-receipt-candidate-rc2`.

The receipt contains:

- deterministic `receipt_id`;
- `authority_conferring=false`;
- `authorized` boolean;
- request identity/state;
- **`claimed_authority_state_id`** — the exact supplied AuthorityState `authority_state_id` when it is a syntactically valid `sha256:<64-lowercase-hex>` value, otherwise null;
- **`recomputed_authority_state_id`** — the deterministic RFC 8785 + LF canonical identity recomputed from the supplied AuthorityState excluding `authority_state_id` whenever that supplied object is canonicalizable under the RC2 rule, otherwise null;
- exact evaluation time, subject, and jurisdiction when recoverable;
- terminal `authority_basis_id` only when authorized;
- preserved request references, supporting artifacts, conflicts, and residues;
- diagnostic codes.

### 6.1 Dual-identity invariant

For every valid AuthorityState:

`claimed_authority_state_id == recomputed_authority_state_id`.

For an identity-mismatch denial, both facts are preserved and differ.

These are deliberately separate audit facts. Neither field is allowed to overwrite, normalize, or stand in for the other.

### 6.2 Receipt identity

Receipt semantic identity is computed over the receipt excluding `receipt_id` and `diagnostics`, using the same RC2 RFC 8785 + LF canonical-byte rule. Both AuthorityState identity facts therefore participate in receipt semantic identity.

Diagnostics are non-authoritative, unordered observability information and do not change `receipt_id`.

The receipt is evidence that an evaluation was performed. It is not standing authority, origin authentication, an execution permit, or proof that the operation occurred.

## 7. Pipeline boundary

- A declaration/producer identity does not confer E authority.
- B evidence/facts do not confer E authority.
- C epistemic state/confidence does not confer E authority.
- D `candidate_for_authorization` does not confer execution permission.
- E authorization requires separately supplied standing AuthorityState.
- Trusted Decision producer origin and AuthorityState root legitimacy remain external boundaries for a consuming application/profile.
- Authorization does not establish execution occurrence.
- Execution occurrence/reporting does not establish verification.

A downstream consumer that requires origin authentication MUST provide and validate its own trusted-origin binding. It MUST NOT reinterpret RC2 hashes as authentication.

## 8. Explicit exclusions

RC2 does not define Qualification subject/scope binding, competence as an authority predicate, peer/surplus authority quantification, partial authority synthesis, delegation containment/narrowing, signatures/PKI/attestations, roles/groups/wildcards, reusable authorization permits, execution, execution proof, verification proof, or a universal authority ontology.

## 9. RC1 successor statement

RC2 intentionally changes the receipt schema and semantic identity because RC1's single AuthorityState receipt identity was underdetermined on invalid input. RC2 does not relabel RC1 as passing and does not repair the frozen RC1 implementation.

The RFC 8785 canonicalization clarification is a second pre-freeze evidence-driven correction inside the RC2 experiment. It was added only after the preregistered successor surface exposed that the broader recomputed-invalid-state identity domain made ordinary implementation-local JSON number rendering non-recoverable.

## 10. Version behavior and nonclaims

`candidate-rc2` is research identity, not a public release version. Unknown/future Contract E schema tokens fail closed.

Passing RC2 normal-context gates cannot establish independent recoverability, production promotion, root legitimacy, Decision policy correctness, execution occurrence/correctness, or verification. A fresh context-free independent reproduction remains required before promotion support.
