# Apparatus Contracts North Stars

**Status:** research/design audit; non-canonical  
**Scope:** repository-level purpose plus current Contract A–E boundaries  
**Base reviewed:** `c3563cff66d2c85dcbf575c693056e2d8e4563d4`

## Why this exists

The repository already has strong specifications and a Contract / Apparatus Separation Invariant. What has been less explicit is the shortest durable statement of **why each contract exists**.

This document makes that purpose visible without changing any canonical contract semantics.

A North Star is not a schema, version, implementation plan, or promotion decision. It is a boundary test:

> If a proposed field, rule, or behavior does not help the contract do its one job, or causes it to inherit authority owned by another layer, it should require separate evidence rather than entering by convenience.

The exercise is also useful in reverse. If two adjacent North Stars leave a necessary responsibility unowned, that is a candidate architectural gap worth testing.

---

# Repository North Star

> **Apparatus Contracts exists to make every cross-apparatus handoff carry exactly the minimum authority a legitimate downstream consumer may rely on, with immutable identity, explicit unknowns, and explicit exclusions, so no apparatus has to reconstruct producer-private state or silently inherit authority that belongs to another layer.**

The repository is therefore not trying to make one universal pipeline object.

Its job is to preserve **separation of authority** across boundaries:

```text
producer apparatus
    ↓
governing contract
    ↓
consumer apparatus
```

A good contract should make four things inspectable:

1. **What the producer uniquely owns.**
2. **What exact state the downstream consumer is allowed to rely on.**
3. **What remains unknown or belongs to a later authority domain.**
4. **What immutable identity binds the handoff so substitution is detectable.**

This restates the accepted separation invariant in decision-seeking form. It does not replace `APPARATUS-CONTRACT-SEPARATION.md`.

---

# Contract A

## North Star

> **Contract A freezes the exact upstream work declaration and supplied source representations needed to begin evidence construction without importing retrieval, evidence judgment, epistemic, decision, or authorization semantics.**

## Question Contract A answers

> What exact work object, proposition structure, and source representations did the upstream producer hand to the evidence-construction layer?

## Owns

- producer/work identity;
- authoritative root proposition identity and content binding;
- explicit decomposition state and declared lineage where supported;
- exact supplied source representations;
- whole-object integrity.

## Does not own

- source trust or legitimacy;
- retrieval;
- relevance or support/refutation;
- CAL judgments;
- Decision policy;
- operational authorization or execution.

## Boundary test

If Evidence Bundler can legitimately begin evidence construction without the proposed field, and the field instead expresses a later judgment about evidence or authority, it probably does not belong in Contract A.

**Live basis:** canonical Contract A 2.0.0 purpose and explicit non-authority rules.

---

# Contract B

## North Star

> **Contract B freezes the evidence world and preparation history presented to CAL so CAL can perform proposition-specific assessment without reconstructing Evidence Bundler internals, while keeping evidence facts, nomination, admission, and aperture observations distinct from semantic judgments.**

## Question Contract B answers

> What exact evidence-world state and preparation history was CAL given to assess?

## Owns

- canonical claim/source/passage identities already defined by Contract B;
- provenance-bound evidence-world facts;
- representation anchors;
- nomination/admission/review history;
- explicit known/unknown factual state;
- aperture/search-scope observations;
- integrity and reference validity for the handoff.

## Does not own

- proposition-specific support/refutation;
- eligibility or applicability judgments;
- completeness conclusions merely from retrieval counts;
- CAL verdicts;
- Decision policy;
- authorization.

## Boundary test

A field belongs in Contract B when CAL needs the **fact that it was observed or supplied** in order to do its own work. It does not belong there merely because Evidence Bundler can cheaply compute a proposition-specific judgment for CAL.

**Live basis:** canonical Contract B 1.2.0 factual-context/history extension and repository evidence-world/semantic-judgment separation.

---

# Contract C

## North Star

> **Contract C freezes CAL-attributable epistemic/result state, bound to the exact Contract-B evidence world and exact CAL/policy identity, so a downstream decision consumer can use what CAL established without rerunning CAL, reconstructing producer-private reasoning, or rewriting upstream evidence facts.**

## Question Contract C answers

> Given this exact evidence world and CAL/policy identity, what epistemic/result state did CAL actually establish?

## Owns

- exact Contract-B world binding;
- exact CAL semantic implementation and behaviorally relevant policy identity;
- proposition/result execution state;
- CAL-owned measurements and assessments where supported;
- retained evidence participation/contribution state;
- terminal basis, residual/non-deciding state, explicit unknowns and failures;
- deterministic result identity.

## Does not own

- duplicated Contract-B source/evidence payload;
- Decision Engine materiality, utility, risk tolerance, routing, or action selection;
- operational authorization;
- producer-private reasoning traces that are not part of the public epistemic result.

## Boundary test

If a legitimate downstream decision policy could reach a different decision from the state while still respecting CAL's result, that state belongs in Contract C rather than being compressed into one upstream verdict. If the field exists only to tell Decision Engine what action to choose, it belongs downstream.

**Live basis:** canonical Contract C 1.0.0 purpose plus the live C2 successor programme, which is expanding representation while preserving the same decision-agnostic responsibility.

---

# Contract D

## North Star

> **Contract D freezes the Decision Engine's policy conclusion and typed requested effect for an exact upstream authority and exact target, so an authorization consumer can determine applicability without consulting Decision Engine internals or importing actor, permission, or execution state.**

## Question Contract D answers

> What exact operational effect did this exact Decision policy select for this exact target and upstream authority?

## Owns

- exact upstream authority binding;
- Decision policy identity/version;
- exact target identity/content binding;
- Decision evaluation state and disposition;
- typed/versioned requested effect and normalized machine-semantic parameters;
- deterministic Decision identity.

## Does not own

- actor identity;
- grants/delegations/approvals;
- standing authority;
- permission to execute;
- execution occurrence or execution receipts;
- verification of the downstream effect.

## Boundary test

Contract D may say **what effect the Decision selected**. It must not answer **who is allowed to carry it out** or **whether it happened**.

A CLEAR Decision reaches `candidate_for_authorization`, not permission.

**Live basis:** canonical Contract D 1.0.0 and EDR-003 / issue #28.

---

# Contract E

## Proposed North Star

Contract E remains research-only. The following is therefore a **design statement**, not canonical contract authority.

> **Contract E binds separately governed current authority to an exact operational intent at the point of use, allowing a consumer to determine whether that exact subject may perform that exact action on that exact immutable target now, while neither re-deciding upstream policy nor performing or verifying the action.**

## Question Contract E answers

> Is this exact subject authorized, under the current supplied AuthorityState, to perform this exact operation in this exact jurisdiction against this exact immutable target at this exact evaluation time?

## Owns, if the research programme ultimately supports it

- structural and identity validity of supplied AuthorityState;
- exact authority-chain/delegation applicability;
- exact currentness and revocation evaluation;
- exact subject/jurisdiction/operation/target matching;
- binding to the exact point-of-use request / immutable intent;
- deterministic non-conferring AuthorizationReceipt.

## Does not own

- whether upstream evidence is true;
- whether CAL was correct;
- whether Decision policy was correct;
- real-world legitimacy of the AuthorityState root merely because its bytes hash correctly;
- action selection;
- execution occurrence;
- execution success;
- post-execution verification.

## Critical invariant

> **A Decision proposes an effect. Contract D identifies that requested effect. Contract E establishes point-of-use authority. Only the executor can establish that execution occurred.**

An AuthorizationReceipt is evidence that an evaluation occurred. It is not standing authority or a reusable bearer permit.

**Live basis:** frozen RC3 candidate semantics, Contract E × ERS point-of-use composition evidence, issue #74, and the unresolved evaluation-time / authority-provenance programme.

---

# End-to-end authority progression

The North Stars imply this progression:

```text
Upstream declaration
    │
    ▼
Contract A
"What exact work and source representations were supplied?"
    │
    ▼
Evidence construction
    │
    ▼
Contract B
"What exact evidence world was CAL given?"
    │
    ▼
CAL
    │
    ▼
Contract C
"What did CAL establish from that world?"
    │
    ▼
Decision Engine
    │
    ▼
Contract D
"What exact effect did policy select?"
    │
    ▼
[ intent / action materialization ? ]
    │
    ▼
Contract E
"May this exact subject perform this exact action on this target now?"
    │
    ▼
Executor
    │
    ▼
[ execution / verification evidence ? ]
```

The brackets are deliberate. They identify responsibilities that the current A–E naming does not yet make canonical.

---

# What this audit appears to reveal

These are **hypotheses**, not new contract decisions.

## H1 — The Decision-effect → executable-intent seam is not yet canonically owned

**Observed:**

- Contract D deliberately stops at a typed requested effect and `candidate_for_authorization`.
- Contract E research authorizes an exact operation/target and the ERS point-of-use work uses an immutable `ExecutionIntent`.
- The successful bounded composition explicitly included an ERS-generated execution intent between D and E.
- No canonical A–E contract currently defines the general transformation from a requested Decision effect into an exact executable action including executable identity, arguments, side-effect target, environment constraints, and target pre-state.

**Inference:**

There may be a missing apparatus/contract boundary between **policy-selected effect** and **point-of-use authorization**.

The likely question is not “do we need Contract F?” yet. The smaller question is:

> Does a legitimate authorization consumer need a canonical immutable intent object that can be constructed independently of Contract E and bound back to Contract D?

**Falsifier:** if every supported downstream effect can be authorized correctly and reconstructably from Contract D + E-owned request state without an independently governed intent representation, a new shared boundary may be unnecessary.

## H2 — Post-execution evidence is intentionally outside Contract E but not yet represented in the contract spine

**Observed:**

- Contract D discovery explicitly preserved execution as downstream and said execution produces its own receipt.
- Contract E explicitly does not establish execution occurrence or verification.
- The CAL Pipeline North Star ultimately wants decisions and actions to remain reconstructable.

**Inference:**

A future executor may need a separately governed execution/result boundary carrying what was attempted, what actually changed, and what was verified. This may belong outside Apparatus Contracts if execution is owned by MainFrame/Conduit or another system, but the authority handoff should be explicit either way.

**Falsifier:** if the downstream executor already has a canonical, independently consumable receipt contract that provides this evidence, the apparent gap is only a navigation/documentation gap.

## H3 — Trusted authority origin is a separate boundary, not a missing Contract-E predicate

**Observed:**

Contract E research repeatedly distinguishes content integrity from origin legitimacy. Hashing AuthorityState proves exact bytes, not that the root is an authentic source of authority.

**Inference:**

The unresolved problem is likely **where trustworthy point-of-use AuthorityState, time, actor/workload identity, and target observation come from**, rather than another semantic rule inside E.

This could resolve as trusted configuration, a local mediator, an authority-source apparatus, or another mechanism. Do not create a contract until a legitimate consumer need and threat model discriminate among those choices.

## H4 — The pre-retrieval evidence-world freeze may be a separate authority seam

Issue #100 already identifies a possible EvidenceGate / pre-retrieval freeze containing source provenance, issuer/role, temporal/jurisdictional coverage, conflict/supersession state, corpus-scope declarations, and explicit unknowns before Evidence Bundler retrieval.

That state is deliberately earlier than Contract B nomination/admission history and richer than Contract A's supplied source representation boundary.

The North-Star test exposes the question cleanly:

> Is there state a legitimate Evidence Bundler must be able to rely on before retrieval that neither Contract A nor Contract B can own without violating their existing purposes?

If yes, that is a genuine candidate boundary. If no, keep it out rather than filling every conceptual gap with another contract.

---

# Design rule for future contract work

Before adding or changing a contract field, ask:

1. Which North Star requires this state?
2. Which apparatus uniquely owns the fact or judgment?
3. What legitimate downstream consumer needs it?
4. Could the consumer reconstruct it from the existing governing contract without producer-private knowledge?
5. Would placing it here steal authority from an earlier or later layer?
6. What exact unknown/failure state exists when the information is unavailable?
7. What immutable identity must change when this state changes?
8. What adversarial or independent-consumer test would falsify the proposed boundary?

If none of the current North Stars owns a necessary responsibility, do not immediately stretch the nearest contract. Record the gap and test whether a new boundary is actually required.

---

# Current disposition

The A–D North Stars are summaries of already canonical purpose/boundary semantics.

The Contract E North Star is a proposed compression of the current research programme and must remain non-canonical until the Contract E evidence programme supports a promotion decision.

H1–H4 are architectural hypotheses exposed by the cross-contract audit. They authorize investigation, not new contract letters, schemas, versions, or production behavior.
