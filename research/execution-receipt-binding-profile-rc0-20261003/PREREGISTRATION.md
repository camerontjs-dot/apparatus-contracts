# Existing execution receipt + CAL Pipeline binding profile RC0

**Classification:** Draft Research preregistration. Representation/conformance experiment only.

**Parent:** apparatus-contracts issue #168 and North-Star audit PR #165.

## Decision

Determine whether the existing MainFrame command-receipt carrier can represent the minimum post-Contract-E CAL-Pipeline execution evidence by adding a bounded cross-pipeline binding profile, or whether the carrier itself lacks a load-bearing semantic distinction that requires a separate shared execution-result contract.

Do not redesign MainFrame first.

## Frozen live source basis

Static source inspected before this preregistration:

- `camerontjs-dot/mainframe-live@dbff8c39790ce70961de2310809e1bd737ccb7a9`;
- `workstation/server/control-plane.mjs` blob `075b899e844a11b628862169a9a21ec2b3b82d2c`;
- `workstation/server/task-authority.mjs` blob `b8d1e56c595674e9243d8ca564737dc6187952d3`;
- `workstation/server/db/schema.sql` blob `0c7341244f0d4733da0de2c5b748561ebf86814a`;
- `workstation/server/db/repository.mjs` blob `2e7403f2b8945a3c7511300cfeb051f683ad864b`.

Observed carrier capabilities include durable receipt identity, unique idempotency key, actor/authority class, packet/source/contract identity, requested/accepted/completed times, append-only transitions, terminal result SHA-256, explicit refused/failed/interrupted states, `applied`, changed files, verification/evidence pointers and rollback availability.

## Missing cross-pipeline binding family from static inspection

The generic receipt does not currently establish named bindings for:

1. exact Contract-D Decision identity;
2. exact Contract-E evaluation/receipt identity;
3. exact immutable action/intent identity;
4. exact target pre-state identity;
5. exact target post-state identity where applicable;
6. exact verifier identity/evidence identity when verification is claimed.

## Competing representations

### R0 — existing receipt only

Intentionally weak for CAL-Pipeline reconstruction. A consumer checks only generic receipt lifecycle/result integrity and `completed + applied=true`.

### R1 — existing receipt + external binding sidecar

Keep the native MainFrame receipt unchanged. Add a deterministic sidecar bound to exact receipt ID and exact terminal result SHA-256 carrying the six cross-pipeline identities.

### R2 — inline binding extension

Copy the same six binding fields into an extended receipt representation. This tests whether physical inclusion inside the carrier adds discrimination beyond R1.

## Required properties

A valid CAL-Pipeline execution evidence package must let an independent consumer reconstruct, without MainFrame-private state:

- which exact Decision requested the effect;
- which exact point-of-use authorization permitted the attempt;
- which exact action/intent was authorized;
- the target pre-state;
- whether the exact action was actually applied;
- target post-state where meaningful;
- which verifier/evidence supports a verification claim.

The carrier must retain its own lifecycle distinctions. The binding profile must not convert a failed/refused/interrupted receipt into success.

## Frozen mutations

The cases committed before implementation include:

- each required binding missing;
- Decision substitution;
- Contract-E authorization substitution;
- intent substitution;
- pre-state substitution;
- post-state substitution;
- verifier/evidence substitution;
- terminal result mutation without result-hash update;
- receipt-ID cross-pairing;
- a failed/interrupted carrier presented with otherwise valid bindings.

## Weak-control requirement

R0 must false-accept at least one cross-pipeline substitution. Otherwise the experiment does not discriminate the intended property and is `INCONCLUSIVE`.

## Acceptance / interpretation

- If R1 rejects all frozen substitutions and preserves all valid carrier lifecycle states required by the profile, a sidecar binding profile is representationally sufficient on the frozen cases.
- If R2 has identical discrimination to R1, inline mutation of the MainFrame receipt is not justified by this experiment.
- If R1 cannot express/reject a load-bearing case that R2 can, inline/shared receipt semantics gain bounded support.
- If neither can represent a necessary distinction, record `SHARED_EXECUTION_RECEIPT_BOUNDARY_REQUIRED_WITH_BOUNDS`.

## Nonclaims

A pass cannot establish:

- real execution correctness;
- actual filesystem pre/post observation;
- rollback correctness;
- independent verifier correctness;
- production MainFrame integration;
- production Contract E readiness;
- universal execution-receipt semantics.

## Local-work threshold

This representation experiment is synthetic and hosted-capable.

Local work is required only after a candidate representation is frozen and the claim requires a real action, real pre/post target state, real rollback, local workload identity, or local verifier observation.
