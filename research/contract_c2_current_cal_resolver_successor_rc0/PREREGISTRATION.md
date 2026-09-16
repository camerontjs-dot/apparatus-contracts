# Contract C2 current-CAL resolver successor RC0

**Classification:** Draft Research / independent producer-policy authority qualification.

This experiment does not alter the immutable predecessor resolver, Contract C2 validators or wire semantics, CAL runtime semantics, Decision Engine, Contract E, Authorization, canonical Contract-C discovery, release state, or execution authority.

## Trigger

The CAL Pipeline pressure campaign reached a genuine scientific blocker:

`BLOCKED_AT_CAL_TO_CONTRACT_C2_PRODUCER_AUTHORITY`

CAL then independently requalified the exact current semantic implementation against the exact Contract C2 promotion subject.

Preferred CAL-side producer subject:

- CAL research head `c4974388e9a40a87661ed80af9271b9625b7c093`;
- semantic implementation `847cc970642bb648dc994b929c2053b5c9d4648c`;
- hard-bound producer materializer blob `ef32fa4fca52a2bb7fe2896b378f9b6fdef0dfde`;
- policy digest `44ecc33519fa8911079595d322f5f0decbf0389af42e153ac32214931798e42c`;
- producer-conformance RC1 workflow run `35053229507`, job `104657905279`;
- evidence artifact `10429439212`, digest `sha256:28e0c1eea76129164135f69388910f32f218101ebb656e131b0e4ddd657cb43b`;
- evaluation digest `sha256:673200cd89f5378083e17ca023c05498cc7ec00160576d28d8222f2fa2aece05`;
- disposition `SUPPORTED_FOR_APPARATUS_RESOLVER_SUCCESSOR_QUALIFICATION`.

The CAL-side gate also demonstrated that the immutable predecessor resolver correctly rejects `847cc970...`.

## Immutable predecessor authority

Predecessor resolver commit:

`43b571464734325277374ee81098553fb7c1b944`

Its sole frozen row is:

- semantic implementation `a902621e8baea3063dddd7f92ba975aade305464`;
- policy digest `44ecc33519fa8911079595d322f5f0decbf0389af42e153ac32214931798e42c`;
- canonical policy profile `cal-v1-candidate-2026-09`;
- semantics `typed-source-grounded-scoreless-categorical`;
- supported families `direct_event_order`, `strict_comparison`;
- projection blob `9bc152275759304be03b84014c56bd434549a64a`.

The predecessor commit and file must remain immutable. This RC0 may only create a **new** resolver candidate.

## Candidate resolver shape

The successor candidate must retain schema:

`contract-c-phase-1-5-policy-resolver-v1`

It must contain exactly two rows keyed by exact semantic implementation identity:

1. the predecessor `a902621...` row preserved byte-for-byte as a JSON value;
2. a current-CAL row with:
   - semantic implementation `847cc970642bb648dc994b929c2053b5c9d4648c`;
   - the same exact canonical policy payload and policy digest `44ecc335...`;
   - projection blob `ef32fa4fca52a2bb7fe2896b378f9b6fdef0dfde`.

The new projection blob is intentionally the CAL-side RC1 producer adapter whose semantic identity is runtime-bound and no longer caller-selectable. It is provenance plus reproducibility binding for the producer projection used to generate C2; it does not authorize CAL semantics by itself.

## Authority freeze rule

The commit that first contains the candidate resolver JSON, before evaluator/workflow/terminal files are added, becomes the exact **candidate resolver authority freeze**.

All Contract C2 objects evaluated in this RC0 must carry that exact freeze commit in `producer.policy_resolver_commit_sha`.

The evaluator must load resolver entries from a separate checkout of that exact freeze commit. Later branch-head commits are research/evaluator records and are not resolver authority.

## Independent evaluation obligations

The Apparatus evaluator must not accept CAL's producer-conformance classification as sufficient. It must independently exercise current CAL and Contract C2.

At minimum, independently construct and evaluate these current-CAL classes:

1. strict support;
2. strict refutation;
3. alternative-joint mixed basis `(S1 OR S2) AND R`;
4. irrelevant-only / public `no_deciding_relation`;
5. measurement-not-applicable / public `no_deciding_relation`;
6. negative-event `UNRESOLVED`;
7. support plus unresolved, where unresolved must prevent a support winner;
8. unsupported semantic family.

For every case:

- execute exact current CAL semantic code;
- materialize C2 using exact producer adapter blob `ef32fa4f...`;
- emit candidate resolver freeze commit as `policy_resolver_commit_sha`;
- exact C2 structural validation must pass;
- exact Contract-B reference verification must pass;
- `verify_policy_resolution()` against the independently selected candidate resolver freeze must pass;
- producer semantic identity and policy digest must match the candidate row exactly;
- canonical repeat must be deterministic.

## Required hostile controls

The evaluator must prove:

- the predecessor resolver `43b571...` still rejects current CAL;
- removing the `847cc...` row from the candidate makes current CAL resolution fail;
- changing current CAL's policy digest makes resolution fail;
- duplicating the `847cc...` row makes resolution fail as ambiguous;
- substituting another semantic implementation makes resolution fail;
- substituting the predecessor resolver commit into a current object fails against candidate-resolver selection;
- old `a902621...` objects still resolve under the preserved old row when their producer resolver commit is the new candidate freeze;
- the old row in the candidate is exactly equal to the predecessor row;
- semantic implementation keys are unique;
- candidate contains no mutable `latest`, network locator, or human-only policy alias as authority.

## Stop rule

Classify as one of:

- `SUPPORTED_CURRENT_CAL_C2_RESOLVER_SUCCESSOR`;
- `FALSIFIED_CURRENT_CAL_RESOLVER_SUCCESSOR`;
- `APPARATUS_FAILURE`.

Preserve the first result. Do not edit the frozen candidate resolver file after reveal. Any correction requires a new preregistered successor and a new resolver freeze commit.

A green result permits a final CAL producer gate and downstream pipeline requalification. It does not authorize Contract C2 merge/release or global discovery changes.
