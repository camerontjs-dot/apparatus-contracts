# Contract E → ERS evaluation-time provenance successor RC0

**Experiment ID:** `ERS-EVAL-TIME-PROV-20260921-02`

**Classification:** Draft Research preregistration. No production mutation, release, effect registration, Contract D/Contract E semantic change, or executor authorization.

## Decision

Determine whether the frozen Contract E → ERS shadow composition can bind an **independently sourced evaluation time to the exact Contract E invocation and exact Contract E result** such that post-evaluation substitution is rejected before `shadow_ready`.

This is the direct successor to the falsified RC5 hypothesis recorded in apparatus-contracts PR #129 and ERS PR #9.

## Frozen subjects

- apparatus predecessor/result: `fe9ea89bd9d7d6ecd8aa20f92dd84ab892a6931b`
- Contract E profile/source: `b153dcc4434cbe8a98616a9e410c6125378144c7`
- ERS RC5: `099f84700f28e118734f1ca74feb977da1c4cf17`
- ERS RC4 render-bound predecessor: `022fcb58e14864aa173f447fa0c18dd2362b41b0`
- frozen Decision successor: `816374379ba7eb23f5bfdadaf203b7e287c052db`
- CAL Pipeline v3: `ffc43d4e89f5b1f7748e9cde0fa1efc7db47b463`
- released Contract D: `298a1a0f7b7b6d7712e11200d04faec3e1ca169b`
- provenance explicit-link research profile: `3934423b1a97ad1b099057c40fe8014e5dd08c97`
- provenance independent-root freeze: `8f762f0d02d2f5a32d85c6b1c721782198422239`

The provenance profile remains research-only and is not promoted by this experiment. Its independent reconstruction remains a separate open question.

## Primary hypothesis

A qualification-only supervisor can own the Contract E evaluation boundary such that:

1. the caller supplies no evaluation time;
2. the supervisor reads its own OS UTC clock at the point of evaluation;
3. the supervisor constructs the exact Contract E request using that time;
4. the supervisor invokes the exact frozen Contract E evaluator itself;
5. the supervisor captures the exact request bytes and exact result bytes;
6. the supervisor signs a transcript binding the execution-intent identity, authority-state identity, independently sourced evaluation time, exact Contract E request SHA-256, exact Contract E result SHA-256, exact Contract E implementation identity, and a fresh ERS challenge;
7. ERS independently verifies the signature, challenge, freshness, exact result bytes, exact intent, exact authority state, and all inherited RC4/RC5 bindings before `shadow_ready`.

The supervisor MUST NOT expose an API that accepts caller-supplied `evaluation_time`, caller-supplied Contract E result bytes, or a request to “sign this result.” It must produce the result by invoking Contract E inside the supervised operation.

## Controlled boundary

Keep unchanged:

- generic `execution-intent-candidate-v1`;
- the five RC4/RC5 bound identities: Decision, claim content, point-of-use pre-state, render packet, exact rendered payload;
- Contract E source bytes at the pinned commit;
- Decision/CAL/Contract D semantics;
- PIPE02/PIPE03 HOLD behavior;
- no pending-review write;
- no real MainFrame mutation;
- no effect registration;
- no production issuer/key claim.

Authority-state provenance remains bounded to the same qualification-only local fixture model unless a separate experiment changes it. This experiment does not claim production authority-state provenance.

## Required transcript

The decisive run must emit a `contract-e-evaluation-transcript-rc0` object conforming to the frozen research schema in this directory.

The signed body must bind at least:

- exact Contract E repository + commit;
- exact execution-intent identity;
- exact authority-state identity;
- independently sourced `evaluation_time`;
- exact canonical Contract E request SHA-256;
- exact Contract E result SHA-256;
- Contract E result identity where the result exposes one;
- fresh consumer-generated challenge;
- issuer/key identity;
- observation/issue time.

Signing/canonicalization must be deterministic and documented. A qualification-only Ed25519 key may reuse the RC5 key if the matching private key is still available. Otherwise one new key may be generated **before the decisive matrix**, its public-key identity must be frozen in the local freeze receipt, and it must not rotate during the experiment.

## Primary acceptance matrix

### Positive control

Authentic PIPE01 must:

- obtain time from the supervisor, not the caller;
- invoke exact Contract E at `b153dcc...`;
- produce a signed transcript over the exact request/result;
- pass independent ERS transcript/result verification;
- retain all five inherited intent bindings;
- return `shadow_ready=true`;
- return `execution_occurred=false`;
- leave the sandbox byte-for-byte empty before and after.

### Decisive falsifier: post-evaluation +1 second mutation

After Contract E has returned and the authentic transcript is frozen:

1. mutate only the evaluation-time field in the presented Contract E result by exactly +1 second;
2. do not rerun Contract E;
3. do not issue a new authentic supervisor transcript.

ERS MUST reject before `shadow_ready`.

If the mutated result can be re-signed through the normal supervisor interface without rerunning Contract E, the hypothesis is falsified even if ERS later rejects some other mutation.

### Mismatched-evaluation replay

Run a second authentic supervised Contract E evaluation of the same intent at a later time. Pair result from evaluation A with transcript from evaluation B, and vice versa. Both pairings MUST reject before `shadow_ready`.

### Exact-result mutation

One-byte mutation to the Contract E result with the authentic transcript MUST reject before `shadow_ready`.

### Wrong intent / authority state

A valid transcript for a different execution intent or authority-state identity MUST reject before `shadow_ready`.

### Wrong issuer

A correctly shaped transcript signed by a non-pinned Ed25519 key MUST reject before `shadow_ready`.

### Stale/replayed transcript

Retain the existing bounded freshness and fresh-challenge controls. A stale transcript or replayed challenge MUST reject before `shadow_ready`.

### Caller-time injection control

The public supervised-evaluation API MUST have no caller-supplied evaluation-time field. If a caller can choose the timestamp that the trusted transcript later attests without compromising the supervisor boundary, the primary hypothesis is falsified.

## Provenance sidecars

For the authentic positive run, also generate research-only provenance sidecars using the exact explicit-link profile at `3934423...`:

- one Contract E apparatus attestation;
- one ERS apparatus attestation;
- one run manifest indexing the exact execution intent, authority-state fixture, Contract E request/result, signed evaluation transcript, render packet, payload, and ERS shadow result.

Validate these sidecars with the exact profile validator. Record exact artifact IDs and commitments.

These sidecars are **evidence capture**, not the primary oracle. Failure of the research provenance profile must be classified separately unless it prevents establishing the exact objects needed by the primary mutation test. Do not silently repair #112/#114 during this experiment.

## Required pre-run freeze receipt

Before the decisive matrix, record:

- implementation branch/commit/tree for the ERS successor;
- any apparatus reproducer commit/tree;
- exact transcript schema blob;
- exact supervisor/consumer/test blobs;
- Contract E/ERS/provenance pins;
- issuer public-key identity;
- exact public supervisor API shape;
- environment/tool versions materially affecting the run;
- sandbox location and pre-run digest/listing;
- confirmation that no decisive result has been observed before freeze.

Once this freeze is recorded, do not modify the supervisor, ERS verifier, transcript schema, or decisive test matrix. A defect in the frozen evaluator produces `INCONCLUSIVE` and a new successor, not repair-in-place.

## Stop rules

Stop with **FALSIFIED** if any preregistered substitution reaches `shadow_ready=true`, or if the normal supervisor interface can attest a caller-mutated timestamp/result without performing the bound Contract E evaluation.

Stop with **INCONCLUSIVE** if the evaluator/harness cannot distinguish the property because of an apparatus defect, unavailable dependency, contaminated freeze, or ambiguous identity linkage.

Stop with **BLOCKED** if an exact frozen subject or required local authority/environment cannot be established.

Only an unchanged frozen apparatus completing the full matrix may support the bounded hypothesis.

## Non-claims

Even a successful result does not establish:

- production issuer/key provenance or custody;
- resistance to arbitrary same-user host compromise;
- trusted host-clock correctness;
- production authority-state provenance;
- Contract E production authorization;
- released Contract D registration for the ERS effect;
- executor correctness;
- filesystem atomicity/recovery;
- real MainFrame write authorization;
- independent reconstruction of the provenance profile in PR #112/#114.

No production write is authorized by this experiment.
