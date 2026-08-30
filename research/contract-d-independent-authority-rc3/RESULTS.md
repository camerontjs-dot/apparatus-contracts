# Contract D RC3 — Independent Consumption Authority Hardening Results

## Terminal research state

Primary disposition: **INCONCLUSIVE**  
Secondary Contract D finding: **READY_FOR_FRESH_INDEPENDENT_REPRODUCTION**

`INCONCLUSIVE` is deliberate. RC3 established a mechanically explicit candidate and native reference-producer conformance, but the preregistered strongest question, whether an implementation created independently from the published apparatus package alone derives the same authority-relevant behavior, requires the separate Context-Free successor. RC3 does not substitute self-conformance for that experiment.

`READY_FOR_FRESH_INDEPENDENT_REPRODUCTION` means only that the candidate is frozen, self-contained enough to expose to a clean-room implementer, and has passed the preconditions for that test. It is not a Contract D promotion recommendation and does not predict that the fresh reproduction will succeed.

## 1. Exact repositories and identities inspected

### apparatus-contracts

- live main/base: `00bdf9546a877f9f6c1d7fd227fd959e1d7aa99e`
- Contract D coordination: issue #22
- RC3 preregistration: `da0397ad0d948051f12e6511333c86168f2f4709`
- **candidate freeze: `b24d06caf944facb970df5129ebdd48c21c25eec`**
- candidate tree: `62fc53527c57a1cf69d1b9f83ea0f738ab95d656`
- research PR: #24

### decision-engine

- live main/base: `ff7a0f63e5f7075b192dff04064b950bf7255ffa`
- promoted Decision/Authorization boundary: `f7c3759dfac7ee4be45879b8266b5eb1440530ee`
- frozen RC2 research reference: `6c1ddb5a6b6b1a5373261e41d64a4baee83e0efb`
- RC2 reference implementation blob: `f4a722c60766e018131798426cb2fba489efc311`
- research-only RC3 producer PR: #23
- RC3 producer emitter: `2930163b58d90ce6d5a097ff7ee5bbe4ff79e27b`, blob `1745b74a61ba1a3321c52f384a166b7d9d3b0e1c`
- final cross-repository receipt head: `63b0245b03ea63d0248a5aced83fba6697697598`

### research-scaffold-harness predecessor

- main/base: `548bfa81f65290eda15af658f647497679b840ef`
- predecessor preregistration: `3b63269b29488b7ffe45d2933eab0fec0279c5b4`
- predecessor independent freeze: `43f3acc4e2c8a456e38723ee7031d89e75086529`
- post-reveal comparison: `0a50f01c288634e115091bafa85284672b9f8c43`
- terminal results: `0ad80dbecca43dc3a057d015617914d742f32d23`
- preserved predecessor disposition: `CROSS_REPOSITORY_CONFORMANCE_FAILED`

## 2. Predecessor evidence preserved

### Observed

The prior independent implementation substantially recovered the semantic core but native cross-repository interchange failed. The preserved disagreement set included version/serialization, exact canonicalization/identity projection, unknown-field handling, effect registry/version/parameter semantics, and downstream applicability checks. The RC2 reference consumer also lacked target-kind and external upstream/policy applicability checks.

The predecessor freeze, tests, comparison, and negative result were not rewritten.

### Inference

The evidence supported hardening shared authority rather than redesigning the Decision/Authorization seam.

### RC3 hypothesis

One exact versioned representation plus strict evolution rules, typed effect registry, explicit applicability binding, deterministic canonicalization, and authority-only semantic identity would remove the demonstrated specification ambiguity without importing Authorization state.

### Unknown

Whether a fresh implementer can reproduce all of those semantics from the frozen package alone remains untested until the Context-Free successor.

## 3. Observed semantic core

RC3 retains only authority elements with demonstrated behavioral function:

1. exact Contract D version;
2. upstream authority kind/id/immutable identity;
3. Decision policy id/version;
4. target kind/id/immutable content identity;
5. evaluation state;
6. completed policy disposition;
7. typed/versioned effect plus registered machine-semantic parameters;
8. deterministic semantic identity over normalized authority state.

Reason codes, explanation, diagnostics, actor, approval, delegation, autonomy, and execution state are not Decision authority.

## 4. Specification gaps investigated and chosen rules

### Contract/version representation

Chosen: exact string `0.3.0-rc3`. Unknown/future/numeric/aliased versions fail closed.

Rejected: permissive aliases and implicit forward compatibility, because they permit unsupported semantics to inherit current authority.

### Disposition vocabulary

Chosen: `evaluation.state = completed|failed`; completed disposition `clear|hold`; failed evaluation has no disposition/effect.

This preserves completed non-clear conclusion versus failure to establish a policy conclusion.

### Typed effect registry

Chosen: versioned registry with exact type/version/parameter definitions, declared defaults, and rejection of unknown types/versions/parameters.

Current evidenced entries:

- `knowledge.add_verified_tag@1`
- `knowledge.cite_as_evidence@1`
- `task.dispatch@1`

Reason text never supplies machine effect semantics.

### Target binding

Chosen: exact kind + id + `content_sha256`.

Independent mutations of all three are discriminated. Cross-kind replay fails even when id/content otherwise match.

### Upstream authority binding

Chosen: exact kind + id + immutable identity. The consumer compares identity and never reinterprets upstream epistemic semantics.

### Decision policy binding

Chosen: exact policy id/version against an independently supplied applicability expectation.

### Unknown structural fields

Chosen: strict rejection at exact-version Contract-D-owned structural locations. `metadata.diagnostics` is the sole explicitly opaque diagnostic container and is excluded from identity/applicability.

### Canonicalization

Chosen: UTF-8, sorted object keys, compact JSON, Unicode preserved, finite numbers, one trailing newline, duplicate keys invalid.

### Semantic identity

Chosen: SHA-256 over canonical bytes of the normalized authority projection only. Metadata is excluded. Registered safe defaults are normalized before hashing. No stored `decision_id` is required.

## 5. Discriminating tests and outcomes

Frozen hosted suite at candidate freeze:

- run `33323642846`
- job `99289846820`
- result `success`
- `30 passed in 0.07s`

The suite covers positive controls, future/unknown machinery, target/upstream/policy substitutions, effect/action replay, parameter mutations/default normalization, metadata and Authorization-only invariance, field ablation, injection, canonicalization, duplicate-key rejection, and weak-consumer controls.

No preregistered weak consumer survived as a conforming implementation.

## 6. Field/minimality ablation

Removing any of the following destroys validation or a demonstrated authority capability:

- contract version;
- upstream kind/id/immutable identity;
- policy id/version;
- target kind/id/content identity;
- evaluation state;
- disposition for completed evaluation;
- effect type/version for completed evaluation.

Machine-semantic effect parameters matter according to their registry entry.

One pre-freeze correction was required: mandatory presence of an empty `effect.params` container had no authority-relevant effect. RC3 therefore makes the container optional and normalizes declared safe defaults. This is recorded as a minimality result.

Metadata can be removed or changed without changing semantic identity or applicability.

## 7. Effect-registry result

The registry resolves the predecessor's shared-vocabulary failure for the current evidenced effects. Unknown effect/type/version/parameter does not acquire authority. Safe default normalization is explicit rather than inferred.

This does not establish that the current three effects are a universal vocabulary.

## 8. Canonicalization and identity result

Transport canonicalization and Decision semantic identity are explicitly separate.

Authority-bearing mutations change semantic identity. Metadata mutations can change transport bytes while leaving semantic identity unchanged. Authorization-only context is external and cannot alter Decision semantic identity.

## 9. Target/upstream/policy applicability result

The consumer oracle requires exact target kind/id/content, upstream kind/id/immutable identity, and policy id/version. Requested operation is supplied externally and must match the typed effect. Machine-semantic requested parameters must match the normalized registered effect.

A match yields `candidate_for_authorization`, not permission to execute.

## 10. Evaluator assurance and weak controls

The suite rejects:

- generic CLEAR/eligible-only consumer;
- target-id-only consumer;
- target consumer ignoring kind/content;
- HOLD/failure collapse;
- reason-text effect inference;
- unknown effect acceptance;
- policy-blind consumer;
- upstream-blind consumer;
- identity contaminated by Authorization context.

The intentionally opaque diagnostics container was also attacked with actor, requested-operation, approval, delegation, autonomy, execution-permission/state/receipt payloads. They remained diagnostic only and did not change semantic identity/applicability.

## 11. Decision Engine conformance result

The original RC2 native representation remains non-conforming under RC3:

`cannot_establish / missing_field`

This negative control is preserved as a prior representation/authority artifact, not repaired by making RC3 permissive.

A separate research-only Decision Engine RC3 emitter then produced native RC3 objects. Final hosted run:

- Decision Engine head: `63b0245b03ea63d0248a5aced83fba6697697598`
- run: `33323789564`
- job: `99290243719`
- result: `success`

The workflow checked out apparatus freeze `b24d06caf944facb970df5129ebdd48c21c25eec` directly and used no translation adapter.

Observed outcomes:

- source-audit CLEAR -> `candidate_for_authorization`
- citation-use CLEAR -> `candidate_for_authorization`
- task-dispatch CLEAR -> `candidate_for_authorization`
- completed HOLD -> `hold`
- evaluation failure -> `evaluation_failed`

## 12. Unresolved disagreements

No authority-relevant disagreement remains between the frozen RC3 package and the research-only RC3 reference producer in the tested corpus.

The consequential unresolved question is independent recoverability: a clean-room implementation has not yet tested whether the package alone eliminates hidden assumptions.

## 13. Falsifiers

Not triggered in the current apparatus/reference tests:

- target kind/id/content binding failure;
- reason-dependent effect authority;
- actionable unknown effect/version;
- Authorization-only identity mutation;
- downstream Contract C reinterpretation;
- HOLD/failure collapse;
- hidden canonicalization assumption inside the published package;
- acceptance of the preregistered weak consumers;
- retained normative field with no demonstrated behavioral effect after the `params` correction.

Not yet testable/closed in this run:

- two reasonable independent consumers still deriving different authority behavior;
- fresh implementation needing prior research results despite the package.

Those are the direct purpose of the successor clean-room experiment.

## 14. Exact RC3 freeze identity

`camerontjs-dot/apparatus-contracts@b24d06caf944facb970df5129ebdd48c21c25eec`

Candidate tree:

`62fc53527c57a1cf69d1b9f83ea0f738ab95d656`

See `FREEZE_RECEIPT.md` for exact blob/tree identities.

## 15. CI/artifact receipts

- apparatus candidate suite: run `33323642846`, job `99289846820`, 30 passed
- Decision Engine final native cross-repository run: `33323789564`, job `99290243719`, success
- predecessor failure remains preserved separately and is not overwritten by these receipts

## 16. Terminal research disposition

Primary: **INCONCLUSIVE**  
Secondary: **READY_FOR_FRESH_INDEPENDENT_REPRODUCTION**

The candidate is ready to be tested independently, not promoted.

## 17. What is explicitly not established

RC3 does not establish:

- successful independent reproduction;
- Contract D production readiness;
- a Contract D release/version promotion;
- production Decision Engine behavior;
- production Authorization profiles or runtime;
- automatic execution or mutation;
- universal effect coverage;
- that every future Decision use case fits this envelope.

## 18. Smallest justified next step

Run one separate Context-Free clean-room reproduction from the frozen RC3 public authority only. Freeze the independent implementation before revealing apparatus reference code, Decision Engine reference producer code, predecessor implementation/results, or prior Contract D reasoning.

If it reproduces all authority-relevant behavior and consumes native frozen RC3 objects without translation, the result may support the smallest separate promotion review. If it disagrees, preserve the disagreement as the next precise Contract D specification defect.
