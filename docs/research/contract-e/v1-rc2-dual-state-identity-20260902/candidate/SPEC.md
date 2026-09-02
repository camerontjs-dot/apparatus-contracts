# Contract E Authority Evaluation Candidate RC2

Status: **research-only pre-promotion successor candidate**

Candidate identifier: `contract-e-authority-evaluation-candidate-rc2`

RC2 is a successor to falsified RC1. It is not a production Contract E release and does not authorize execution.

## 1. Purpose

Contract E answers one bounded control-plane question:

> Does the exact supplied standing authority state authorize this exact subject to perform this exact operation, in this exact jurisdiction, against this exact immutable target, at this exact evaluation time?

Contract E does not decide whether upstream evidence is true, CAL is correct, Decision policy is correct, an operation should occur, an operation occurred, or verification succeeded.

## 2. Normative object boundary

The candidate has two normative inputs and one audit output:

1. `AuthorityState`: immutable authority-bearing control-plane state supplied separately from the request.
2. `AuthorizationRequest`: transient request for one exact operation/target.
3. `AuthorizationReceipt`: deterministic non-conferring result of evaluating 1 against 2.

A request MUST NOT embed, manufacture, repair, or override standing authority. AuthorityState provenance/legitimacy is an external trust/configuration boundary. RC2 validates structure, canonical identity, lineage, bounds, currentness, and exact applicability, but does not prove who was entitled to create a root grant/policy.

## 3. Canonical JSON and identities

RC2 uses one canonical JSON procedure wherever this specification calls for deterministic SHA-256 identity or hashing.

Canonical JSON is:

- finite JSON only;
- UTF-8;
- object keys sorted lexicographically;
- compact separators;
- Unicode preserved rather than ASCII-escaped;
- one trailing newline;
- non-finite numbers, host-only values, non-string keys, duplicate raw JSON member names, cyclic decoded containers, and UTF-8 encoding failures rejected.

Raw JSON ingestion MUST reject duplicate member names before producing a decoded object. An API that receives an already-decoded dictionary cannot recover duplicate raw members that a prior parser discarded; such an API may evaluate only the decoded object it actually received and MUST NOT claim it proved duplicate-free raw input.

The same canonicalization applies to:

- AuthorityState canonical identity;
- immutable-reference `identity_sha256`;
- `AuthorizationReceipt.request_sha256`;
- AuthorizationReceipt semantic identity / `receipt_id`.

## 4. AuthorityState

Schema token: `contract-e-authority-state-candidate-rc2`.

An AuthorityState contains exactly one non-branching authority chain. RC2 does not evaluate peer/surplus conferring alternatives and therefore does not choose a peer-record aggregation quantifier.

### 4.1 Root

The first record MUST:

- have `basis_type` exactly `grant` or `policy`;
- contain complete scalar `subject_id`, `domain`, `operation`, `scope`, `target_class`, and SHA-256 `target_ref`;
- contain explicit `valid_from`, optional `valid_until`, and optional `revoked_at`;
- have `parent_id=null` and `delegated_by=null`.

### 4.2 Delegation

Every later record MUST:

- have `basis_type=delegation`;
- name the immediately preceding record by `parent_id`;
- set `delegated_by` exactly to the parent `subject_id`;
- contain a new explicit authorized `subject_id`;
- preserve `domain`, `operation`, `scope`, `target_class`, and `target_ref` exactly equal to the parent.

Delegation may change only the authorized subject. It has no containment, inheritance, wildcard, alias, union, `any-of`, narrowing, or widening semantics.

All authority-record IDs MUST be unique. Duplicate IDs, branching, skipped/non-immediate parents, missing parents, cycles, or a non-delegation descendant invalidate the state.

### 4.3 Exact currentness and revocation

Timestamps use UTC `Z` form `YYYY-MM-DDTHH:MM:SS[.fraction]Z` and MUST be calendar-valid. Leap seconds are not accepted. Fractional seconds may have arbitrary positive precision and are compared exactly, without truncation to host datetime precision.

At `AuthorizationRequest.evaluation_time`, every record MUST satisfy:

- `evaluation_time >= valid_from`;
- if `valid_until` is present, `evaluation_time <= valid_until`;
- if `revoked_at` is present, `evaluation_time < revoked_at`.

Validity boundaries are inclusive. Revocation is effective at and after `revoked_at`.

No `current=true`, `status=established`, confidence, agreement count, or similar assertion substitutes for recomputation.

### 4.4 AuthorityState claimed and computed identities

`AuthorityState.authority_state_id` is the **claimed identity** supplied with the state.

The **computed identity** is `sha256:` plus SHA-256 of canonical JSON of the supplied AuthorityState excluding `authority_state_id` itself.

For a valid AuthorityState, the claimed identity MUST be syntactically valid SHA-256 and MUST equal the computed identity.

Identity is an integrity binding, not proof that the root grant/policy is legitimate in the real world.

## 5. AuthorizationRequest

Schema token: `contract-e-authorization-request-candidate-rc2`.

The request MUST contain exactly:

- `request_id`;
- exact SHA-256 `authority_state_id` expected by the request;
- explicit exact UTC `evaluation_time`;
- exact `subject_id`;
- exact typed jurisdiction: `domain`, `operation`, `scope`, `target_class`, `target_ref`;
- immutable `references`;
- separate `supporting_artifacts`;
- explicit `conflicts` and `residues` arrays.

Missing, malformed, or unknown fields fail closed. Authority-critical bindings are scalar exact-equality bindings.

### 5.1 Immutable references

Each reference contains exactly:

- local `ref_id`;
- opaque `kind`;
- optional `version`;
- opaque immutable identifier;
- deterministic `identity_sha256` over canonical JSON of `{kind, version, immutable_id}`.

`ref_id` values MUST be unique within `references`.

`jurisdiction.target_ref` is the immutable `identity_sha256`, not a mutable local alias, and MUST resolve to one validated request reference.

Referenced Contract A/B/C/D objects are opaque identities. Contract E does not reinterpret their payloads or turn their facts/verdicts/decisions into authority.

### 5.2 Supporting artifacts

Supporting artifacts are always non-conferring. Each item contains unique request-local `id`, `artifact_type`, and `ref_id`. Its `ref_id` MUST resolve to exactly one request `references[*].ref_id`.

Examples include Contract A declarations, Contract B factual/evidence state, Contract C result state, Contract D `candidate_for_authorization` decisions, competence/qualification material, citations/warrants, execution reports, and prior AuthorizationReceipts.

No supporting artifact can replace AuthorityState.

### 5.3 Conflicts and residues

Conflict IDs are unique within `conflicts`; residue IDs are unique within `residues`.

A relevant conflict or residue with status `unresolved` or `contested` blocks authorization. Irrelevant items are preserved but do not block.

This blocking rule applies to every request, including `domain=resolution`, `operation=resolve`. A resolution target is represented by its immutable target reference. The blocker arrays are not a discharge channel, and RC2 accepts no request-side `resolved_*_ids` or similar field.

RC2 may authorize an exact resolution operation when a matching resolution AuthorityState exists and no relevant blocker is supplied in that request. That result means only that the resolution operation is authorized. Applying the resolution, changing conflict/residue state, and proving that resolution occurred are outside RC2.

## 6. Evaluation

A request is authorized only when all of the following are true:

1. AuthorityState is structurally valid and claimed identity equals computed identity.
2. AuthorizationRequest is structurally valid.
3. Request `authority_state_id` exactly equals the supplied AuthorityState claimed/computed identity.
4. No relevant unresolved/contested conflict or residue is present.
5. Every AuthorityState record is current and unrevoked at exact `evaluation_time`.
6. The complete authority chain is valid and non-amplifying.
7. Terminal chain `subject_id` exactly equals request `subject_id`.
8. Terminal chain `domain`, `operation`, `scope`, `target_class`, and `target_ref` exactly equal request jurisdiction.
9. `target_ref` resolves to a validated immutable reference.
10. Every supporting-artifact `ref_id` resolves request-locally.

There is no partial-record aggregation, peer conferring alternative set, Qualification predicate, semantic composition, embedding inference, wildcard, or default allow.

## 7. AuthorizationReceipt

Schema token: `contract-e-authorization-receipt-candidate-rc2`.

The receipt contains exactly the schema-defined fields including:

- deterministic `receipt_id`;
- `authority_conferring=false`;
- `authorized` boolean;
- `request_id` and `request_sha256` when representable;
- `authority_state_claimed_id`;
- `authority_state_computed_id`;
- exact evaluation time, subject, and jurisdiction when individually representable;
- terminal `authority_basis_id` when authorized, otherwise null;
- preserved request lists;
- non-authoritative diagnostic codes.

### 7.1 Dual AuthorityState identity semantics

`authority_state_claimed_id` is the exact supplied `AuthorityState.authority_state_id` only when that value is a syntactically valid SHA-256 identity; otherwise null.

`authority_state_computed_id` is the canonical identity recomputed from the supplied AuthorityState excluding `authority_state_id` whenever the supplied state is a canonicalizable JSON object; otherwise null.

A valid state produces equal non-null values. An identity-tampered but canonicalizable state produces two different non-null values and authorization MUST be false.

Neither value confers authority. Their purpose is to preserve both the producer claim and the independently computed integrity observation.

### 7.2 Request hash and safe preservation

`request_sha256` is computed over the complete request whenever the request is canonicalizable finite JSON, even when structurally invalid; otherwise null.

For a structurally valid request, `preserved.references`, `preserved.supporting_artifacts`, `preserved.conflicts`, and `preserved.residues` are exact deep copies.

For a structurally invalid request, each preserved list is copied only if its top-level value is a list whose individual elements satisfy that list's item shape; otherwise that preserved list is empty. This keeps every emitted receipt representable by the receipt schema while preserving schema-valid observed list material where possible. Preservation never repairs an invalid request into an authorized request.

### 7.3 Receipt semantic identity

Receipt semantic identity is SHA-256 over canonical JSON of the receipt excluding `receipt_id` and `diagnostics`.

Both `authority_state_claimed_id` and `authority_state_computed_id` are normative semantic fields and therefore participate in `receipt_id`.

Diagnostics are non-authoritative, unordered observability information. Exact diagnostic wording or primary-reason precedence is not a compatibility promise.

The AuthorizationReceipt is evidence that evaluation occurred. It is not standing authority and cannot be used as an AuthorityState record.

## 8. Pipeline boundary

- Contract A declaration/producer identity does not confer E authority.
- Contract B evidence/facts do not confer E authority.
- Contract C epistemic state/confidence does not confer E authority.
- Contract D `candidate_for_authorization` does not confer execution permission.
- E authorization requires separate standing AuthorityState.
- Authorization does not establish execution occurrence.
- A prior authorized receipt is historical evidence, not a reusable execution permit; a point-of-use consumer requiring current authority must re-evaluate current AuthorityState.
- Execution occurrence/reporting does not establish verification.
- Verification requires its own exact authority evaluation and independent verification evidence outside E.

## 9. Explicit exclusions

RC2 does not define:

- Qualification subject/scope binding or competence as an authority predicate;
- multiple/surplus peer conferring-record quantification;
- cross-record partial authority synthesis;
- delegation containment, narrowing, widening, group, wildcard, alias, or `any-of` semantics;
- application/discharge of conflict or residue resolution;
- source legitimacy or cryptographic root-of-authority trust;
- reusable permits/leases;
- distributed execution locking or exactly-once execution;
- operational execution;
- proof of execution occurrence;
- proof of verification;
- universal authority ontology.

## 10. Version behavior and promotion

`candidate-rc2` is a research identity, not a release version. Unknown/future Contract E schema tokens fail closed. Referenced A-D versions remain opaque exact identity fields.

RC2 may be proposed as the semantic basis for a first production `1.0.0` only after its own frozen conformance/adversarial evidence and fresh independent reproduction are supported. Naming it RC2 does not authorize promotion.
