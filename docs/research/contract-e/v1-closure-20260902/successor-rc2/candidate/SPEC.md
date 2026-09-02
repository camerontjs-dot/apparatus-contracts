# Contract E Authority Evaluation Candidate RC2

Status: **research-only successor candidate**

Candidate identifier: `contract-e-authority-evaluation-candidate-rc2`

This specification is not a production Contract E release and does not authorize execution.

## 1. Successor scope

RC2 is a deliberately narrow successor to falsified candidate RC1.

RC1 fresh independent reproduction produced 48/50 normative exact matches with zero false permits and zero false rejects. Both mismatches arose from one public-spec ambiguity: for an invalid or forged AuthorityState, the single receipt AuthorityState identity field did not determine whether it represented the supplied/claimed identity or the recomputed canonical identity.

RC2 changes only that receipt identity boundary. It preserves both facts as separately named fields. The authorization predicate, exact jurisdiction model, linear non-amplifying delegation, currentness/revocation semantics, blocker behavior, supporting-artifact non-conferral, and execution/verification exclusions remain unchanged unless this specification says otherwise.

## 2. Purpose

Contract E answers one bounded question:

> Does the exact supplied standing authority state authorize this exact subject to perform this exact operation, in this exact jurisdiction, against this exact immutable target, at this exact evaluation time?

Contract E does not decide whether upstream evidence is true, CAL is correct, a Decision policy is correct, a root authority source is legitimate, an operation should occur, an operation occurred, or verification succeeded.

## 3. Normative object boundary

The candidate has two normative inputs and one audit output:

1. `AuthorityState` — immutable authority-bearing control-plane state supplied separately from the request.
2. `AuthorizationRequest` — transient request for an exact operation/target.
3. `AuthorizationReceipt` — deterministic non-conferring result of evaluating 1 against 2.

A request MUST NOT embed, manufacture, or override standing authority.

AuthorityState provenance/legitimacy remains an external trust/configuration boundary. Candidate RC2 validates structure, claimed identity, recomputed identity, lineage, bounds, currentness, and applicability, but does not cryptographically prove who was entitled to create the root grant or policy.

## 4. AuthorityState

Schema token: `contract-e-authority-state-candidate-rc2`.

An AuthorityState contains exactly one non-branching authority chain.

### 4.1 Root

The first record MUST:

- have `basis_type` exactly `grant` or `policy`;
- contain complete `subject_id`, `domain`, `operation`, `scope`, `target_class`, and `target_ref`;
- contain explicit `valid_from`, optional `valid_until`, and optional `revoked_at`;
- have `parent_id=null` and `delegated_by=null`.

### 4.2 Delegation

Every later record MUST:

- have `basis_type=delegation`;
- name the immediately preceding record by `parent_id`;
- set `delegated_by` exactly to the parent `subject_id`;
- contain a new explicit authorized `subject_id`;
- preserve `domain`, `operation`, `scope`, `target_class`, and `target_ref` exactly equal to the parent.

Delegation may change the authorized subject only. RC2 has no containment, inheritance, wildcard, alias, union, `any-of`, narrowing, or widening semantics.

All record IDs MUST be unique. Duplicate IDs, branching, skipped/non-immediate parent links, missing parents, or cycles invalidate the state.

### 4.3 Currentness and revocation

At `AuthorizationRequest.evaluation_time`, every record in the chain MUST satisfy:

- `evaluation_time >= valid_from`;
- if `valid_until` is present, `evaluation_time <= valid_until`;
- if `revoked_at` is present, `evaluation_time < revoked_at`.

Validity boundaries are inclusive. Revocation is effective at and after `revoked_at`.

No status string, confidence value, agreement count, or cached `current=true` claim substitutes for recomputation.

### 4.4 Canonical identity

AuthorityState canonical identity is `sha256:` plus SHA-256 of deterministic canonical JSON of the AuthorityState excluding `authority_state_id` itself.

Canonical JSON is finite JSON only, UTF-8, lexicographically sorted object keys, compact separators, preserved Unicode, and exactly one trailing newline. Non-finite numbers, host-only values, non-string keys, duplicate raw JSON member names, and cyclic decoded containers are rejected.

The supplied `authority_state_id` is the **claimed AuthorityState identity**.

The evaluator independently computes the **recomputed AuthorityState identity** whenever the supplied value is a canonicalizable JSON object, even if other structural validation later fails.

Authorization can succeed only when:

- the claimed identity is syntactically valid;
- recomputation succeeds; and
- claimed identity exactly equals recomputed identity.

Identity is an integrity binding, not proof that the root grant/policy is legitimate in the real world.

## 5. AuthorizationRequest

Schema token: `contract-e-authorization-request-candidate-rc2`.

The request MUST contain:

- `request_id`;
- exact `authority_state_id` naming the claimed AuthorityState identity;
- explicit UTC `evaluation_time`;
- exact `subject_id`;
- exact typed jurisdiction: `domain`, `operation`, `scope`, `target_class`, `target_ref`;
- immutable `references`;
- separate `supporting_artifacts`;
- explicit `conflicts` and `residues` arrays.

All authority-critical bindings use scalar exact equality. Missing or malformed fields fail closed. Exact candidate schemas reject unknown fields.

### 5.1 Immutable references

Each reference contains:

- local `ref_id`;
- opaque `kind`;
- optional `version`;
- opaque immutable identifier;
- deterministic `identity_sha256` over `{kind, version, immutable_id}`.

`jurisdiction.target_ref` is the immutable `identity_sha256`, not a mutable alias.

Referenced A/B/C/D objects remain opaque to Contract E. Their payloads, facts, verdicts, Decisions, content hashes, or producer names do not become standing E authority.

### 5.2 Supporting artifacts

Supporting artifacts are separate references and always non-conferring. They may include A/B/C/D objects, competence material, citations, execution reports, previous AuthorizationReceipts, or external provenance evidence.

No supporting artifact can replace AuthorityState.

### 5.3 Conflicts and residues

A relevant conflict or residue in status `unresolved` or `contested` blocks ordinary authorization. Irrelevant items are preserved but do not block.

RC2 accepts no request-side `resolved_*_ids` discharge claim. Unknown such fields make the request invalid.

Contract E may separately authorize an exact `domain=resolution`, `operation=resolve` request against an immutable conflict/residue target. That means only that the resolution operation is authorized. Applying or proving the resolution is outside Contract E.

## 6. Evaluation

A request is authorized only when all of the following are true:

1. AuthorityState is structurally valid.
2. Claimed AuthorityState identity is syntactically valid.
3. Recomputed AuthorityState identity is available and exactly equals the claimed identity.
4. AuthorizationRequest is structurally valid.
5. Request `authority_state_id` exactly equals the claimed AuthorityState identity.
6. No relevant unresolved/contested conflict or residue blocks the request.
7. Every AuthorityState record is current and unrevoked at `evaluation_time`.
8. The complete authority chain is valid and non-amplifying.
9. Terminal `subject_id` exactly equals request `subject_id`.
10. Terminal `domain`, `operation`, `scope`, `target_class`, and `target_ref` exactly equal request jurisdiction.
11. `target_ref` resolves to one validated immutable reference in the request.

There is no partial-record aggregation, peer conferring alternative set, Qualification predicate, semantic comparison authority, or composition/embedding interpretation.

## 7. AuthorizationReceipt

Schema token: `contract-e-authorization-receipt-candidate-rc2`.

The receipt contains exactly the candidate schema fields, including:

- deterministic `receipt_id`;
- `authority_conferring=false`;
- `authorized` boolean;
- `request_id` and `request_sha256` when establishable;
- `claimed_authority_state_id` — the supplied AuthorityState `authority_state_id` only when it is a syntactically valid `sha256:` identity, otherwise `null`;
- `recomputed_authority_state_id` — the canonical identity recomputed from the supplied AuthorityState object excluding `authority_state_id` whenever canonicalization succeeds, otherwise `null`;
- exact evaluation time, subject, and jurisdiction when establishable from a canonicalizable request;
- terminal `authority_basis_id` when authorized, otherwise `null`;
- preserved request references, supporting artifacts, conflicts, and residues where structurally preservable;
- diagnostic codes.

The two AuthorityState identity fields are distinct audit facts. They MUST NOT be collapsed, aliased, substituted, or treated as interchangeable when they differ.

For every authorized receipt, both fields MUST be non-null and exactly equal.

For a denial caused by AuthorityState identity failure, the evaluator SHOULD preserve both values when both can be established so the receipt records what was claimed and what the bytes actually identify as.

The AuthorizationReceipt is evidence that an evaluation was performed. It is not standing authority and cannot itself be used as an AuthorityState record.

Receipt semantic identity is computed over the receipt excluding only `receipt_id` and `diagnostics`. Therefore both claimed and recomputed AuthorityState identities participate in `receipt_id`.

Diagnostic strings are non-authoritative, unordered observability information. Exact diagnostic vocabulary or primary-reason precedence is not a compatibility promise.

## 8. Pipeline and trusted-origin boundary

Contract E references immutable A-D objects rather than modifying or authenticating them.

- Contract A declaration/producer identity does not confer E authority.
- Contract B evidence/facts do not confer E authority.
- Contract C epistemic state or confidence does not confer E authority.
- Contract D `candidate_for_authorization` does not confer execution permission.
- A Contract D content hash proves exact content binding, not trusted Decision Engine origin.
- AuthorityState content identity proves exact content binding, not legitimacy of its configured root authority source.
- AuthorizationReceipt content identity proves exact receipt content binding, not trusted evaluator origin.
- Operational consumers that require those origins must establish them through a separate trusted-origin/configuration boundary.
- E authorization does not establish execution occurrence.
- Execution occurrence/reporting does not establish verification.

The companion D→E trusted-origin profile freezes the bounded integration assumptions used by the RC2 experiment. Those profile assumptions are not silently imported into core Contract E semantics.

## 9. Explicit exclusions

RC2 does not define:

- Qualification subject/scope binding;
- competence as an authority predicate;
- multiple/surplus peer conferring-record quantification;
- cross-record partial authority synthesis;
- delegation containment/inheritance/`any-of`/narrowing;
- source legitimacy or a cryptographic root-of-authority scheme;
- Decision producer authentication protocol;
- evaluator authentication protocol;
- signatures, PKI, attestations, reusable permits, leases, or replay ledgers;
- wildcard/group/role authorization;
- operational execution;
- proof of execution occurrence;
- proof of verification;
- universal authority ontology.

## 10. Version behavior

`candidate-rc2` is a research identity, not a release version.

RC2 cannot inherit RC1's failed independent-recoverability evidence. It requires its own adversarial evaluation, independently qualified/sealed evaluator, and fresh independent reproduction before any production promotion is supported.

Unknown/future Contract E schema/version tokens fail closed.

## 11. Nonclaims

Passing RC2 tests would not establish correctness of A-D payloads, CAL correctness, Decision policy correctness, legitimacy of a configured root authority source, appropriateness of an authorized operation, execution occurrence/correctness, verification occurrence/correctness, or production promotion/release authorization.