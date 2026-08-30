# Contract E Brainstorm — RC1 Participant Binding Evidence Update

Status: research correspondence / non-authoritative

This note records the terminal result of Decision Engine Contract E Participant Binding / Adapter Truthfulness RC1. It updates the Contract E brainstorm without defining a canonical Contract E schema.

## Terminal source evidence

Decision Engine PR #21:

- terminal result commit: `d0bca744d9b8fc7e2b22189dcd61c395ed88b89d`
- disposition: **SUPPORTED FOR PROMOTION, WITH REQUIRED PARTICIPANT-DOMAIN BOUNDARY**
- primary result artifact: `research/contract-e-participant-binding-rc1/RESULTS.md`
- frozen RC0 jurisdiction evaluator Git blob retained exactly: `5012f6398f6953e458de87179a318bc45d1df456`

## Answer learned by RC1

For the seven tested boundaries, the authority/jurisdiction evaluator did not need to understand domain semantics if a separate Contract E-style participant layer established what counts as a truthful authority request.

The supported conceptual split is:

```text
Participant declaration / binding
  determines whether actor + operation + target truthfully represent
  the authoritative artifact and the participant's responsibility domain

Standing Authority / Jurisdiction
  determines whether that truthful request is permitted now
```

Neither layer safely replaces the other.

A broad standing authority profile can permit a syntactically valid request that is semantically or structurally mis-bound to the upstream authority. Conversely, a perfectly truthful typed Decision/effect does not itself grant the actor permission to exercise it.

## Preserved failure materially changed the Contract E candidate

The first frozen RC1 declaration surface failed.

The global Decision-effect registry correctly mapped:

- `cite_as_evidence` -> citation use;
- `dispatch_task` -> task dispatch.

But participant declarations did not say which effect domain each participant was responsible for consuming.

As a result:

- citation participant accepted a task Decision as structurally truthful;
- task participant accepted a citation Decision as structurally truthful.

The failure showed:

> Exact field/effect mapping is insufficient unless the participant declaration also constrains the finite effect/operation domain the participant may consume.

The smallest repaired shape added participant-specific accepted effects. The same substitution attacks then failed as `participant_effect_out_of_scope`.

This is now a required candidate property of Contract E.

## Seven tested authority-sensitive boundaries

RC1 exercised one common authority protocol across:

1. source access;
2. evidence passage admission;
3. CAL assessment issuance;
4. Decision issuance;
5. citation/use;
6. task execution;
7. outcome verification.

For each stage, removing only its standing actor/operation grant while keeping the semantic/transport request fixed caused jurisdiction to become `OUT_OF_JURISDICTION`.

This is evidence that the artifact itself did not self-authorize the stage.

## Upstream authority before / around Evidence Bundler

RC1 supports distinguishing at least two upstream authority relations:

### Source access authority

Question:

> May this actor/system read, retrieve, copy, or process this source?

The research fixture represented this as an operator-root sidecar grant bound to exact source URL/content hash and allowed operations.

### Evidence-admission authority

Question:

> May this exact source/passage be admitted into the evidence aperture supplied downstream?

The research fixture bound this to exact bundle/source/passage identity and passage hash plus the authority sidecar.

RC1 demonstrated that these relations can vary independently without interpreting passage relevance, support, source trust, or CAL epistemic semantics.

- `source.read` only -> access valid; admission rejected;
- `evidence.admit_passage` only -> access rejected; admission binding valid in the research representation.

The second case is a separability probe, not a recommended production policy. A production profile may define access as a prerequisite to admission.

### Important unresolved representation choice

RC1 does **not** establish whether operator authority should be granted:

- over an entire corpus/aperture, allowing Evidence Bundler to select passages within that scope;
- per source;
- per passage;
- through a standing policy/rule;
- through a capability/token;
- through a one-time approval receipt;
- through platform-native permissions.

For low-human-intervention operation, a bounded corpus/source aperture delegated to Evidence Bundler is currently a plausible hypothesis. Exact passage-by-passage approval would be more restrictive but potentially recreate a mandatory human stage.

Contract E should be expressive enough to represent either posture without deciding passage relevance itself.

## Why `authorized_for_use: true` remains insufficient

The tests reinforce that a generic boolean could hide different authorities:

```text
source may be read
passage may be admitted
CAL may assess admitted bundle
artifact may be cited in a context
Decision effect may be executed
outcome may be authoritatively verified
```

These are separate operations with separate actor/target/currentness scopes.

A Contract E candidate should therefore bind authority to a typed operation and exact target rather than carry a generic `authorized` bit.

## CAL-specific implication

CAL can plausibly consume authority references that establish the exact admitted Contract B aperture and whether CAL itself has mandate to issue an assessment over that authority.

But Contract E must not cause CAL to treat those authority references as evidence that a passage:

- is relevant;
- supports the proposition;
- contradicts the proposition;
- is complete;
- is reliable in the epistemic sense;
- changes the CAL verdict.

RC1 mutated positive/negative-looking scaffold support, trust, and related semantic projections while authority binding remained stable.

Therefore candidate CAL responsibility remains approximately:

```text
Contract E / authority:
  Is CAL authorized to assess this exact admitted input authority?

CAL semantics:
  What does that admitted evidence actually justify?
```

Those questions must remain separate.

## Citation-specific implication

RC1 constructed a citation-shaped request from Contract C semantic conclusion alone.

The broad standing authority profile would have permitted the syntactically plausible citation request.

The Contract E participant-binding layer rejected it because the exact typed citation Decision/effect/target was absent.

Therefore:

```text
CAL conclusion != citation authority
```

A downstream citation/use boundary requires both:

1. an authoritative artifact/policy output that actually exposes the citation effect or equivalent typed use authority; and
2. standing jurisdiction for the actor to exercise that effect in the requested target/context.

The exact policy owner for citation remains an open architecture question.

## Typed Decision effect is also not self-authorizing

With an exact valid citation or task Decision held fixed, removing the actor/operation grant caused jurisdiction to become non-permitting.

Therefore:

```text
Decision effect != authority to exercise effect
```

Contract D can expose what policy decided without gaining responsibility for actor delegation.

## Revised candidate Contract E shape

Evidence now supports Contract E as a cross-cutting **Authority Interface Contract** with two required layers.

### E1 — Common jurisdiction protocol

Candidate concerns:

- authority profile / policy identity and currentness;
- actor/principal identity;
- typed operation;
- target identity/class/current state;
- scope/batch/budget/context;
- delegation/approval references;
- jurisdiction outcome and reason;
- revocation/expiry;
- local enforcement obligation.

### E2 — Participant responsibility/binding declaration

Each participant must declare at least:

- participant identity;
- semantic responsibilities owned;
- semantic responsibilities explicitly excluded;
- authoritative upstream artifact(s) consumed;
- authority-sensitive operations exposed;
- participant-specific accepted effect/operation domain;
- exact actor binding source;
- exact operation/effect mapping source;
- exact target identity/currentness binding source;
- required upstream authority receipts/currentness where applicable;
- semantic fields forbidden from manufacturing authority;
- behavior on missing/unknown/stale/revoked authority;
- enforcement/escalation responsibility;
- output receipt/record responsibility where required.

The participant-specific accepted effect domain is required by observed failure, not architectural preference.

## Candidate stage responsibility map after RC1

Names remain research labels only.

| Boundary | Authority relation | Domain semantics Contract E must not absorb |
|---|---|---|
| source acquisition | actor may read exact source/aperture | relevance/trustworthiness as evidence |
| evidence admission | actor may admit exact source/passage/bundle | support/contradiction/retrieval quality |
| CAL assessment | CAL has mandate over exact Contract B authority | entailment, completeness, verdict, epistemic state |
| Decision issuance | policy actor has mandate over exact Contract C/target | operational policy conclusion itself |
| citation/use | actor may exercise exact citation/use effect | whether underlying evidence actually supports claim |
| execution | actor may exercise exact typed Decision effect | correctness of Decision |
| verification | verifier has mandate over exact execution/post-state | correctness of original Decision |

## Current strongest residual risk

**Producer-native conformance.**

RC1 reconstructed all requests and validated declarations in a single Decision Engine research harness from pinned real/frozen artifacts.

That harness could become a hidden central adapter that knows everyone's binding rules.

The next test must move declaration/descriptor emission and consumption into the repositories that actually own the stages while keeping semantic logic unchanged.

## Next experiment

Contract E Producer-Native Conformance RC2 should freeze:

- repaired participant-declaration requirements;
- participant-specific accepted effect domains;
- frozen jurisdiction evaluator;
- existing substitution vectors.

Then research-only implementations in Evidence Bundler, CAL, Decision Engine, and downstream consumers should independently emit/consume the authority binding descriptors.

Required controls include:

- source/aperture authority removal;
- stale/revoked source/admission receipts;
- Contract B/C identity substitution;
- effect/operation/target relabeling;
- citation/task cross-use substitution;
- semantic-label laundering;
- authority-profile changes with semantic artifacts byte-identical;
- independent consumer reconstruction where practical.

Do not define Contract E 1.0.0 until that producer-native conformance test succeeds or exposes the remaining boundary failures.

## Non-claims

This evidence update does not establish:

- canonical Contract E field names;
- that Contract E is serialized after Contract D;
- that every source or passage requires human approval;
- that Evidence Bundler owns final admission policy;
- that CAL should embed authority fields directly in Contract B/C;
- production citation policy;
- production access-control implementation;
- production Authority Control Plane topology;
- automatic MainFrame mutation.
