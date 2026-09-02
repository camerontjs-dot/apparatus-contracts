# Contract E Authority Evaluation Candidate RC1

Status: **research-only pre-promotion candidate**

Candidate identifier: `contract-e-authority-evaluation-candidate-rc1`

This specification is not a production Contract E release and does not authorize execution.

## 1. Purpose

Contract E is a cross-cutting authority/control-plane protocol. It answers one bounded question:

> Does the exact supplied standing authority state authorize this exact subject to perform this exact operation, in this exact jurisdiction, against this exact immutable target, at this exact evaluation time?

Contract E does not decide whether upstream evidence is true, CAL is correct, Decision policy is correct, an operation should occur, an operation occurred, or verification succeeded.

## 2. Normative object boundary

The candidate has two normative inputs and one audit output:

1. `AuthorityState` — immutable authority-bearing control-plane state supplied separately from the request.
2. `AuthorizationRequest` — transient request for an exact operation/target.
3. `AuthorizationReceipt` — deterministic non-conferring result of evaluating 1 against 2.

A request MUST NOT embed, manufacture, or override standing authority. AuthorityState provenance/legitimacy is an external trust/configuration boundary; this candidate validates its structure, identity, lineage, bounds, currentness, and applicability but does not cryptographically prove who was entitled to create the root grant/policy.

## 3. AuthorityState

Schema token: `contract-e-authority-state-candidate-rc1`.

An AuthorityState contains exactly one non-branching authority chain. This cardinality is intentional: v1 does not evaluate peer/surplus conferring alternatives and therefore does not choose the underdetermined quantifier identified by Contract E aggregation research.

### 3.1 Root

The first record MUST:

- have `basis_type` exactly `grant` or `policy`;
- contain a complete `subject_id`, `domain`, `operation`, `scope`, `target_class`, and `target_ref`;
- contain explicit `valid_from`, optional `valid_until`, and optional `revoked_at`;
- have `parent_id=null` and `delegated_by=null`.

### 3.2 Delegation

Every later record MUST:

- have `basis_type=delegation`;
- name the immediately preceding record by `parent_id`;
- set `delegated_by` exactly to the parent `subject_id`;
- contain a new explicit authorized `subject_id`;
- preserve `domain`, `operation`, `scope`, `target_class`, and `target_ref` exactly equal to the parent.

Delegation in candidate RC1 has no containment, inheritance, wildcard, alias, union, `any-of`, narrowing, or widening semantics. It may change the authorized subject only. A broader delegation model is outside v1.

All record IDs MUST be unique. Duplicate IDs, branching, skipped/non-immediate parent links, missing parents, or cycles invalidate the state.

### 3.3 Currentness and revocation

At `AuthorizationRequest.evaluation_time`, every record in the chain MUST satisfy:

- `evaluation_time >= valid_from`;
- if `valid_until` is present, `evaluation_time <= valid_until`;
- if `revoked_at` is present, `evaluation_time < revoked_at`.

Validity boundaries are inclusive. Revocation is effective at and after `revoked_at`.

No `current=true`, `status=established`, confidence, agreement count, or similar claim is accepted as a substitute for recomputation.

### 3.4 Canonical identity

AuthorityState identity is `sha256:` plus SHA-256 of deterministic canonical JSON of the AuthorityState excluding `authority_state_id` itself.

Canonical JSON is:

- finite JSON only;
- UTF-8;
- object keys sorted lexicographically;
- compact separators;
- Unicode preserved rather than ASCII-escaped;
- one trailing newline;
- non-finite numbers, host-only values, non-string keys, duplicate raw JSON member names, and cyclic decoded containers rejected.

The supplied `authority_state_id` MUST equal the recomputed identity.

Identity is an integrity binding, not proof that the root grant/policy is legitimate in the real world.

## 4. AuthorizationRequest

Schema token: `contract-e-authorization-request-candidate-rc1`.

The request MUST contain:

- `request_id`;
- exact `authority_state_id`;
- explicit UTC `evaluation_time`;
- exact `subject_id`;
- exact typed jurisdiction: `domain`, `operation`, `scope`, `target_class`, `target_ref`;
- immutable `references`;
- separate `supporting_artifacts`;
- explicit `conflicts` and `residues` arrays.

All authority-critical bindings are scalar exact-equality bindings. Missing or malformed fields fail closed. Exact candidate schemas reject unknown fields.

### 4.1 Immutable references

Each reference contains:

- local `ref_id`;
- opaque `kind`;
- optional `version`;
- opaque immutable identifier;
- deterministic `identity_sha256` over `{kind, version, immutable_id}`.

`jurisdiction.target_ref` is the immutable `identity_sha256`, not a mutable local alias.

Contract E treats referenced Contract A/B/C/D objects as opaque identities. It does not reinterpret their payloads or make their facts/verdicts/decisions into authority.

### 4.2 Supporting artifacts

Supporting artifacts are separate references and are always non-conferring. Examples include:

- Contract A declarations;
- Contract B factual/evidence state;
- Contract C CAL result state;
- Contract D `candidate_for_authorization` decisions;
- competence/qualification material;
- citations/warrants;
- execution reports;
- prior AuthorizationReceipts.

No supporting artifact can replace AuthorityState.

### 4.3 Conflicts and residues

A relevant conflict or residue in status `unresolved` or `contested` blocks ordinary authorization. Irrelevant items are preserved but do not block.

Candidate RC1 accepts no request-side `resolved_*_ids` or similar discharge claim. Such unknown fields make the request invalid. This prevents bare resolution-ID laundering.

Contract E may separately authorize a request whose exact jurisdiction is `domain=resolution`, `operation=resolve`, and whose target is an immutable conflict/residue reference. That result means only that the resolution operation is authorized. Applying the resolution, changing conflict/residue state, and proving that resolution occurred are outside this candidate.

## 5. Evaluation

A request is authorized only when all of the following are true:

1. AuthorityState is structurally valid and its identity matches its bytes.
2. AuthorizationRequest is structurally valid.
3. Request `authority_state_id` exactly matches the supplied AuthorityState.
4. No relevant unresolved/contested conflict or residue blocks the request.
5. Every AuthorityState record is current and unrevoked at `evaluation_time`.
6. The complete authority chain is valid and non-amplifying.
7. Terminal chain `subject_id` exactly equals request `subject_id`.
8. Terminal chain `domain`, `operation`, `scope`, `target_class`, and `target_ref` exactly equal request jurisdiction.
9. `target_ref` resolves to one of the request's validated immutable references.

There is no partial-record aggregation. There is no peer conferring alternative set. There is no Qualification predicate. There is no semantic comparison/composition/embedding interpretation.

## 6. AuthorizationReceipt

Schema token: `contract-e-authorization-receipt-candidate-rc1`.

The receipt contains at minimum:

- deterministic `receipt_id`;
- `authority_conferring=false`;
- `authorized` boolean;
- request and AuthorityState identities;
- exact evaluation time, subject, jurisdiction;
- terminal `authority_basis_id` when authorized, otherwise null;
- exact preserved copies of request references, supporting artifacts, conflicts, and residues;
- optional diagnostic codes.

The AuthorizationReceipt is evidence that an evaluation was performed. It is not standing authority and cannot itself be used as an AuthorityState record.

Receipt semantic identity is computed over the receipt excluding `receipt_id` and diagnostic codes. Diagnostic codes are intentionally non-authoritative, unordered observability information. Exact primary-reason precedence is not a v1 compatibility promise.

## 7. Pipeline boundary

Contract E references immutable A-D authority objects rather than modifying them.

- Contract A declaration/producer identity does not confer authority.
- Contract B evidence/facts do not confer authority.
- Contract C epistemic state or confidence does not confer authority.
- Contract D `candidate_for_authorization` does not confer execution permission.
- E authorization requires separate standing AuthorityState.
- Authorization does not establish execution occurrence.
- Execution occurrence/reporting does not establish verification.
- Verification requires its own exact authority evaluation and independent verification evidence outside E.

## 8. Explicit exclusions

Candidate RC1 does not define:

- Qualification subject binding;
- Qualification scope binding;
- competence as an authority predicate;
- multiple/surplus peer conferring-record quantification;
- cross-record partial authority synthesis;
- delegation domain/scope `any-of`, containment, inheritance, or narrowing;
- comparison-as-truth authority;
- composition or embedding authority ceilings;
- application/discharge of conflict or residue resolution;
- source legitimacy or cryptographic root-of-authority trust;
- operational execution;
- proof of execution occurrence;
- proof of verification;
- universal authority ontology.

These exclusions are deliberate boundaries, not convenient defaults.

## 9. Version behavior

`candidate-rc1` is a research identity, not a release version.

If this candidate survives the required conformance/adversarial and independent-reproduction gates, Contract E has no earlier canonical production version, so `1.0.0` is the natural proposed first public compatibility version. That production token MUST NOT be created merely by naming convention; promotion must prove the production transcription is semantically equivalent to this frozen candidate.

Unknown/future Contract E schema/version tokens fail closed. Referenced A-D versions are opaque exact identity fields and gain no authority merely by being newer.

## 10. Nonclaims

Passing this candidate's evaluator does not establish:

- correctness or truth of A-D payloads;
- Evidence Bundler retrieval quality/completeness;
- CAL semantic correctness;
- Decision Engine policy correctness;
- legitimacy of the configured root standing authority source;
- appropriateness of an authorized operation;
- execution occurrence or correctness;
- verification occurrence or correctness;
- production promotion or release authorization.
