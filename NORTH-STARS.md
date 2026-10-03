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


---

# Follow-up live triage — 2026-10-03

This section records the first attempt to falsify H1–H4 against live repository state after the initial North-Star audit. It narrows the questions; it does not promote new contract authority.

## H1 status — NARROWED; no new shared contract justified yet

Additional live evidence:

- Decision Engine's promoted Decision/Authorization EDR already assigns the requested operation to Authorization and execution to a later executor/receipt.
- Cross-use-case RC1 safely authorized source-audit, citation, and task-dispatch Decisions by binding a requested action directly to the typed Decision effect. It did not require a shared `ExecutionIntent` contract.
- Contract D 1.0.0 currently registers `knowledge.add_verified_tag@1`, `knowledge.cite_as_evidence@1`, and `task.dispatch@1`. The first has only `scope`; the latter two have no effect parameters.
- The Contract E × ERS point-of-use experiment did require a richer immutable `ExecutionIntent` containing executable identity, entry point, arguments, input identities, environment constraints, side-effect targets, and target pre-state binding.
- Contract E can authorize an opaque immutable target reference without owning the target object's internal schema.

**Refined inference:** action materialization is real, but present evidence does not show that it must be a universal shared contract. A consumer/executor may own an immutable intent object and present its identity to Contract E. A new shared contract becomes justified only if legitimate independent producers/consumers must reconstruct or validate the same intent semantics across an apparatus boundary.

**Next discriminator:** hold one Contract-D effect fixed and compare at least two materially different concrete action materializations. Ask whether Contract E can safely authorize them using an opaque immutable intent identity plus effect/target binding, and whether an independent consumer needs more than that identity to verify the authorized action.

**Local-work threshold:** no local execution is required to design/freeze this discriminator. Local work is needed only when testing a real executor whose executable identity, environment, side-effect target, or pre-state must be observed from the machine.

## H2 status — NARROWED; receipt machinery exists, cross-pipeline binding remains open

Additional live evidence from `camerontjs-dot/mainframe-live@dbff8c39790ce70961de2310809e1bd737ccb7a9`:

- the workstation control plane has persisted command receipts with idempotency key, task/project, command type, actor, authority class, source/contract identities, requested/accepted/completed timestamps, terminal state, result, result SHA-256, errors, and receipt events;
- live dispatch revalidates task authority at approval time;
- a successful live result records adapter/profile/task category, `applied=true`, outcome, changed files, verification, evidence-receipt pointer, and rollback availability;
- a non-passing verifier produces a failed receipt rather than being treated as successful execution;
- the task-status projection explicitly distinguishes run success from independent verification.

**Refined inference:** the architecture does not lack execution receipts in general. MainFrame already contains a useful domain-specific receipt mechanism. The unresolved CAL-Pipeline question is whether a downstream execution receipt must bind the exact Contract-D Decision, Contract-E authorization evaluation/receipt, and any immutable execution intent strongly enough that a later reviewer can reconstruct **what was authorized versus what was actually attempted/applied**.

Current MainFrame command receipts are task/packet/control-plane oriented. The inspected surface does not establish a generic D/E/intent binding.

**Next discriminator:** define a schema-neutral execution-receipt obligation matrix and test the existing MainFrame receipt projection against it. The minimum candidate obligations are: exact authorization basis, exact action/intent identity, actor, target/pre-state, attempt identity, idempotency/replay state, start/end, applied/not-applied outcome, post-state or changed-state evidence, verification status/evidence, and failure/unknown state. Add fields only where reconstruction actually fails.

**Local-work threshold:** static obligation/conformance analysis can be completed from GitHub. Local work begins only when a frozen candidate must be exercised against a real mutation to establish pre/post state, idempotency, rollback, or verifier behavior.

## H3 status — CONFIRMED AS AN EXTERNAL TRUST BOUNDARY; current provenance experiment covers only part of it

Contract E's frozen research semantics intentionally distinguish integrity from origin legitimacy. The point-of-use trust problem decomposes into at least four independently sourced inputs:

1. **AuthorityState origin:** the root/configuration source that is allowed to define standing authority.
2. **Evaluation time:** time supplied by the trusted runtime boundary, not by the caller asking for permission.
3. **Subject/workload identity:** the actual actor/runtime identity, not an arbitrary caller string.
4. **Target observation:** the current target/pre-state observed at point of use, not a stale caller assertion.

The current evaluation-time provenance preregistration in Apparatus PR #130 already tests an important subset: a supervisor sources evaluation time, invokes Contract E itself, and binds the exact request/result transcript so caller-supplied time/result substitution cannot reach `shadow_ready`. PR #150 stopped before the matrix; the preserved successor question remains valid.

MainFrame's current task-dispatch path is evidence that a local control plane can own some analogous responsibilities: it revalidates a reviewed authority source at approval time, sources its own timestamps, persists an actor/authority-bound receipt, and refuses when source authority is lost. That is a useful pattern, not proof that it is the Contract-E production mediator.

**Refined inference:** do not add another Contract-E semantic predicate for trusted origin. The production integration needs a trusted point-of-use mediator/profile that obtains these inputs from configured/runtime-owned sources and then invokes E. Root legitimacy remains configuration/governance authority; E verifies the supplied state's applicability and integrity.

**Next discriminator:** finish the already-preregistered fresh-process evaluation-time/request/result binding experiment first. Only after that passes is it useful to test concrete sources for AuthorityState, workload identity, clock, and target observation.

**Local-work threshold:** the next matrix itself can be run in an isolated hosted environment if its exact frozen artifacts are available there. Machine-local work becomes necessary when the claim depends on OS/user identity, local keychain or credential ownership, local filesystem/current target observation, local clock boundary, or Conduit/MainFrame process identity.

## H4 status — EXISTING APPARATUS CONFIRMED; shared-contract question deferred

Live `camerontjs-dot/proposition-authoring@96efd44e9d6d2325b9bccc6d6ebdcdad9c8411b1` now states an explicit product responsibility:

> EvidenceGate deterministically standardizes the exact evidence representations supplied with the claim: source identity, content and representation identity, provenance, declared classification/coverage, corpus declarations, explicit unknowns, and integrity. It does not decide whether evidence supports or refutes the claim.

Gate V1.0.0 therefore already occupies the pre-retrieval evidence-world apparatus role that H4 initially described.

Evidence Bundler issue #91 separately defines the downstream firewall: Gate hints may describe evidence/verification shape, while EB owns every causal translation into query construction, retrieval, selection, and admission. It explicitly forbids causal Gate→EB behavior until relevant upstream fields have `QUALIFIED_HINT` authority and a separate EB experiment is frozen.

**Refined inference:** H4 is not a missing-apparatus problem. It is a future **cross-repository contract-placement** question. There is currently no need to create a new Apparatus Contract merely because EvidenceGate emits a standardized profile.

A shared pre-retrieval contract becomes worth considering only when:

1. at least one Gate field is separately qualified for downstream hint use;
2. Evidence Bundler has a legitimate causal need for that field before retrieval;
3. the value cannot be safely reconstructed from Contract A or another already-governing input;
4. an independent EB consumer should be able to validate/use it without importing proposition-authoring internals.

If those conditions are met, Contract A is probably the wrong home because its North Star intentionally excludes evidence-world trust/coverage characterization, and Contract B is temporally too late because it is emitted after EB work. That would be evidence for a distinct Gate→EB boundary, but not yet for any particular letter or schema.

**Local-work threshold:** none for the current design question. The next evidence is repository/hosted experimental work: qualify specific fields and test frozen-pool EB consumption. Local work is needed only if a later retrieval experiment depends on machine-local corpus/index/runtime behavior that hosted execution cannot reproduce.

## Revised programme order

The North-Star audit now suggests this order:

1. finish the existing Contract-E provenance discriminator rather than widening E;
2. run the H1 intent-materialization representation discriminator without assuming a new contract;
3. perform H2 execution-receipt obligation/conformance analysis against the existing MainFrame receipt;
4. let the existing Gate/EB field-qualification programme decide whether H4 ever crosses the threshold for a shared contract;
5. only then decide whether the contract alphabet needs to grow.

This order prefers elimination and reuse over filling conceptual whitespace with new schemas.
