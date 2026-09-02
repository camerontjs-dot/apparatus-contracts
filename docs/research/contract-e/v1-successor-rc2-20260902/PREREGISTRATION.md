# Contract E RC2 successor experiment — preregistration

Status: **FROZEN BEFORE RC2 IMPLEMENTATION**

Issues: #74 (scientific programme), #75 (evaluator / clean-room infrastructure)

Successor base: `2036d559609fed3aa05d81610c574e2c2ad2f16a`

Production `main` observed before branch creation: `c3563cff66d2c85dcbf575c693056e2d8e4563d4`.

RC1 remains immutable. Nothing in this experiment may rewrite RC1 candidate/evaluator/reproduction evidence.

## 1. Triggering evidence

RC1 fresh reproduction terminated `FALSIFIED` with 48/50 normative exact matches, zero false permits and zero false rejects. Both mismatches were one semantic ambiguity: on invalid/forged AuthorityState input, should the denial receipt's single AuthorityState identity mean the supplied/claimed ID or the recomputed canonical identity?

The D→E authorization-consumer pressure experiment then passed 101/101 preregistered structural/replay/metamorphic cases across Python 3.11/3.12/3.13 but was terminal `FALSIFIED` by a stronger provenance observation: self-consistent semantic/content hashes bind bytes but do not authenticate producer/root/evaluator origin.

## 2. Frozen hypotheses

### H1 — RC2 dual identity is sufficient to remove the RC1 normative ambiguity

Replace the ambiguous single receipt fact with two separately named facts:

- `claimed_authority_state_id`: the exact supplied `authority_state_id` when syntactically recoverable, otherwise null;
- `recomputed_authority_state_id`: the canonical identity recomputed from the supplied AuthorityState when canonicalization succeeds, otherwise null.

The authorization predicate itself MUST remain RC1-equivalent. Valid states have equal claimed and recomputed IDs. Invalid mismatch states deny and preserve both facts.

**Falsifier:** any RC1 authority-bearing positive/negative case changes authorization direction without an explicit RC2 reason, either identity fact cannot be deterministically recovered, the two prior RC1 mismatch cases remain normatively ambiguous, or a weak identity-collapsing implementation passes the evaluator.

### H2 — Trusted-origin binding belongs outside Contract E core and can close the forged-origin attacks

The integration profile receives caller/configuration-supplied trusted bindings. It MUST NOT infer origin trust from SHA-256 or from Contract D/Contract E structural validity.

Minimum trusted bindings under test:

- exact trusted Contract D Decision semantic/content identity;
- exact trusted AuthorityState recomputed identity (or exact configured root-state identity);
- exact expected subject/jurisdiction/target derived by the application profile.

A forged-but-valid Decision with a new hash must fail if it is not the trusted Decision identity. A fabricated self-consistent AuthorityState must fail if its recomputed identity is not the configured trusted AuthorityState identity.

**Falsifier:** a forged-but-valid Decision/root passes by self-consistency alone, or the profile requires Contract E to reinterpret Contract D payload semantics beyond opaque supporting identity.

### H3 — Fresh point-of-use E evaluation closes receipt-forgery and stale-authority replay

Human handoff creation and machine execution gates must evaluate current AuthorityState + exact AuthorizationRequest at point of use. A prior `authorized=true` receipt is evidence only and MUST NOT be sufficient by itself.

**Falsifier:** a forged/rehashed receipt or a receipt created before revocation can cause current handoff/execution without a fresh successful E evaluation.

### H4 — Immutable ExecutionIntent remains sufficient machine-target binding for the tested execution profile

Machine execution authority targets the immutable identity of an `ExecutionIntent` rather than embedding script/runtime fields into Contract E core. Material mutations to executable identity, entry point, arguments, input identities, relevant environment constraints, or side-effect target bindings must change the intent identity and invalidate old authorization.

**Falsifier:** any preregistered material ExecutionIntent mutation remains executable under the old authorization.

## 3. RC2 core semantic delta

Only the following public RC2 semantic delta is authorized before experiment results:

1. schema tokens advance from `candidate-rc1` to `candidate-rc2`;
2. AuthorizationReceipt replaces ambiguous `authority_state_id` with both `claimed_authority_state_id` and `recomputed_authority_state_id`;
3. receipt semantic identity includes both fields;
4. all RC1 authorization-state, request, delegation, blocker, currentness, target-reference, and non-conferring semantics remain unchanged unless a test exposes an unavoidable contradiction.

No Qualification, roles/groups/wildcards, peer authority aggregation, narrowing/containment, signatures/PKI, reusable permit/token, execution occurrence, or verification semantics are added.

## 4. Integration profile v2 boundary

The integration profile is test machinery / candidate downstream architecture, not Contract E core.

It must implement this order:

1. validate exact Contract D 1.0.0 Decision;
2. require caller-supplied trusted Decision identity to equal the exact supplied Decision identity;
3. apply exact released Contract D applicability against application-supplied expected upstream/policy/target/requested operation/effect constraints;
4. require applicability outcome `candidate_for_authorization` before constructing an E request;
5. require caller/configuration-supplied trusted AuthorityState identity to equal the recomputed supplied AuthorityState identity;
6. construct an exact E request whose supporting artifacts preserve the exact D reference but do not confer E authority;
7. evaluate E fresh at point of use;
8. human path emits only a non-conferring handoff package when current E evaluation authorizes the exact human subject/action/target;
9. machine path permits only the exact ExecutionIntent identity authorized for the exact machine subject, and emits an execution-gate decision rather than proof of execution occurrence.

## 5. Required attack families

### RC1 regression

Replay all 50 sealed RC1 case families, including:

- positive policy/grant/delegation;
- exact subject/domain/operation/scope/target binding;
- future/stale/revoked and boundary times;
- delegation amplification/lineage defects;
- support non-conferring;
- relevant/irrelevant conflict and residue behavior;
- malformed/unknown/future fields;
- AuthorityState identity mismatch;
- reference hash/missing reference;
- parent/child/sibling target substitution;
- resolution operation boundary;
- Decision/action/execution/verification distinction;
- surplus peer rejection.

The two RC1 mismatch families must specifically assert both receipt identity facts.

### D→E integration replay / mutation

Replay or supersede the prior 101-case matrix, including:

- D CLEAR/HOLD/failed boundaries;
- requested-operation/effect-parameter mismatch;
- D target/policy/upstream substitution;
- E subject/jurisdiction/target/currentness/delegation mutations;
- blocker laundering;
- human↔machine cross-subject replay;
- request/receipt/AuthorityState substitution;
- point-of-use revocation;
- ExecutionIntent mutations;
- metamorphic invariances for non-authoritative diagnostics/presentation state.

### Authenticity/provenance

At minimum:

1. valid but fabricated D CLEAR is rejected when its exact identity is not trusted;
2. valid fabricated AuthorityState root is rejected when its recomputed identity is not configured/trusted;
3. forged `authorized=true` receipt with recomputed self-hash is insufficient without fresh E evaluation;
4. old authorized receipt after revocation is insufficient;
5. trusted-binding metadata itself cannot be smuggled through request supporting artifacts to confer authority.

## 6. Seeded weak controls

A promotion-critical evaluator must catch at least:

- `claimed_only_receipt_identity`;
- `recomputed_only_receipt_identity`;
- `decision_structural_validity_implies_trust`;
- `authority_state_self_hash_implies_root_trust`;
- `receipt_hash_implies_authorization_origin`;
- `receipt_authorized_boolean_only`;
- `skip_point_of_use_re_evaluation`;
- `subject_blind`;
- `operation_blind`;
- `target_blind`;
- `blocker_blind`;
- `revocation_blind`;
- `execution_intent_id_only_without_recomputed_content_binding`.

If any required weak control survives, evaluator qualification fails even if the reference is green.

## 7. Cross-runtime requirement

Run normal-context candidate/adversarial gates on Python 3.11, 3.12, and 3.13 where GitHub runners support them. Runtime agreement is supporting evidence, not independent reproduction.

## 8. Decision rule

Normal-context terminal state:

- `SUPPORTED_FOR_FRESH_REPRODUCTION` only if all preregistered normal-context cases pass, no false permit/reject is preserved, exact frozen checkouts remain unmodified, and the newly qualified evaluator catches every required weak control;
- `FALSIFIED` for a valid in-domain counterexample or normative contradiction;
- `INCONCLUSIVE` for apparatus failure/evaluator defect that prevents a valid discrimination.

Even `SUPPORTED_FOR_FRESH_REPRODUCTION` is **not** `SUPPORTED FOR PROMOTION`.

Promotion support requires a separate fresh context-free independent implementation against the frozen RC2 public aperture and sealed evaluator. The current normal-context agent cannot supply that independence.

## 9. Nonclaims

No result here establishes real-world root legitimacy, Decision Engine policy correctness, universal authorization ontology, execution occurrence/correctness, verification, cryptographic identity, organization/role semantics, reusable permits, or production release readiness.
