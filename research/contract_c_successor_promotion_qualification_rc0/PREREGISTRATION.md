# Contract C minimal in-band successor promotion qualification RC0

**Classification:** stacked Draft Research qualification over exact successor candidate `242351af7214c23dce76edd06299f55c038cd3f0`. This is not a Promotion / Production PR, official version assignment, release, tag, merge, CAL production mutation, Decision production mutation, Contract E change, or operational authorization.

## Parent dependency

This qualification is intentionally stacked on:

- parent Draft PR #91;
- exact parent head: `242351af7214c23dce76edd06299f55c038cd3f0`;
- parent candidate profile: `research-non-deciding-rc0`;
- parent decisive construction run: `34726240904` / job `103640731461`;
- parent artifact: `10307728263`;
- parent artifact digest: `sha256:9b1167c1eefb77fd6e9238fd9272fc8a23970f1560da66df105a6e5ca352afc9`.

If the parent candidate changes, this qualification is superseded unless rebuilt/re-run against the new exact head.

## Question

Does the exact parent candidate have enough evidence to justify a minimal Promotion / Production PR, and what SemVer class would that promoted change require under the project release rules?

This asks two separate questions:

1. **promotion evidence sufficiency**;
2. **version class if promoted**.

A version class may be knowable even if promotion evidence remains incomplete.

## Required promotion predicates

The qualification may return `SUPPORTED FOR PROMOTION` only if all applicable predicates below are established for the exact candidate.

### P1. Candidate exactness and minimality

- exact candidate head is the frozen parent;
- released Contract C 1.0 spec/schema/validator/version registry remain byte-identical;
- candidate semantic schema delta is exactly the two preregistered leaves;
- exact frozen non-deciding handoff validates without semantic relabelling;
- no sidecar-only, scalar/winner, policy/action or authorization surface is introduced.

### P2. Semantic compatibility classification

- legitimate strict Contract C 1.0 validation rejects the exact successor object unchanged;
- candidate validation preserves legacy `support` and `counterevidence` behavior;
- `non_deciding` cannot be represented losslessly as an in-band Contract C 1.0 contribution because 1.0 requires every retained contribution channel to be `support` or `counterevidence` and forbids undeclared fields;
- attempted 1.0 translations that relabel or drop neutral contribution state may become structurally valid only by losing/changing the demonstrated semantic state;
- no safe automatic downgrade is claimed.

Under post-1.0 governance, if those observations hold, the version class **if promoted** is `MAJOR`. Do not assign the numeric release version in this research PR.

### P3. Consumer conformance

At least one independent consumer must reproduce the exact handoff boundary without producer-private implementation knowledge.

Pinned evidence:

- Research Scaffold Harness candidate final commit `07e60447fae17369be5676f013c187b9fd0bfd98`;
- implementation freeze `c1c31885f5802d4ea710dea7bcec214e977b9f03`;
- consumer blob `7c4e15855dfba57bdc2a23e98960e0d79d272aa6`;
- tests blob `9000b495fd5d15f16dc82e662abe6764dc2b02f1`;
- clean receipt blob `a2f75dff9ef4f1820a91331ee43e5ceb13d3a76e`;
- post-freeze comparison run `34717144897`, job `103616318296`;
- disposition `SUPPORTED_CONTEXT_FREE_CONSUMER_B_REPRODUCTION`.

The qualification workflow should rerun the frozen consumer tests and directly feed it the exact parent-candidate handoff where practical.

### P4. Producer conformance

A legitimate producer-boundary implementation must deterministically emit or project the exact successor semantics without adding a new epistemic judgment.

Research-only candidate generation is not sufficient by itself for this release gate.

Current records to discriminate:

- CAL PR #100 selected `non_deciding` as the unique multiplicity-preserving repair within its frozen comparison, but explicitly remained research-only and stated no canonical Contract C revision was established;
- CAL RC1 PR #104 is independently qualified for its bounded semantic engine claim, but explicitly states that canonical downstream Contract C authority and production support remain unresolved and that no Contract C mutation/promotion is established.

If no maintained or promotion-ready CAL producer/exporter conformance exists for the exact successor candidate, P4 is **not established** and the overall qualification must not return `SUPPORTED FOR PROMOTION`.

### P5. Fail-closed and integrity controls

Exact Contract-B binding, proposition/evidence refs, contribution classification closure, causal/residual non-overlap, causal cardinality, result identity, policy identity and whole-object binding must remain fail-closed within the tested scope.

### P6. Migration / parallel-version posture

Because strict 1.0 consumers reject the successor and lossless downgrade is not established, the supported migration posture must be parallel exact-version authority. No silent downgrade, auto-coercion or reuse of 1.0 identity is allowed.

### P7. Release-governance remainder

Even if research disposition becomes `SUPPORTED FOR PROMOTION`, an actual release still requires a later minimal Promotion / Production PR with:

- exact official version;
- schema/spec/validator agreement in canonical paths;
- producer and consumer conformance bound to that official version;
- compatibility/migration notes;
- changelog/version metadata;
- production CI and release acceptance;
- new or updated EDR for the consequential semantic/compatibility change;
- immutable tag/release only after merge and acceptance.

## Explicit falsifiers

The candidate is not supported for promotion if any of these are observed:

- the parent candidate differs semantically from its two-leaf claim;
- released 1.0 artifacts have drifted or were mutated by the candidate;
- the exact neutral handoff cannot validate directly;
- independent consumer conformance fails;
- neutral state can be silently normalized without observable semantic loss;
- a required release predicate is contradicted;
- version evidence supports a class other than the recorded class.

Missing required evidence is `INCONCLUSIVE`, not success and not necessarily candidate falsification.

## Allowed terminal dispositions

Use exactly one:

- `SUPPORTED FOR PROMOTION`
- `FALSIFIED`
- `INCONCLUSIVE`
- `SUPERSEDED`

The terminal record must separately report `version_class_if_promoted` as `MAJOR`, `MINOR`, `PATCH`, or `UNRESOLVED`.
