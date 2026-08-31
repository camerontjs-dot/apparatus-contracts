# Contract D finite-JSON depth hardening v1 — result

## Status

**Research result: iterative container hardening supported for a new frozen Contract-D candidate.**

**Production promotion remains PAUSED.**

This result does not modify or supersede the frozen RC4 candidate or its successful clean-room record. It answers the narrower successor question triggered by the adversarial depth counterexample.

## Frozen predecessor

- repository: `camerontjs-dot/apparatus-contracts`
- commit: `fd6923115116b0ced0f9feb5c005099d2e51ea88`
- candidate subtree: `fe449f9ec27eeddb434276ded375f9dc16b48e29`
- `contract_d_core.py`: `589e3f1c31a21d305402e5750605d25be682a336`
- `contract_d_validate.py`: `d9d621df1e817adbb5468be25ef65272c457e8cc`
- `contract_d_consume.py`: `ad5126922ea4dd8a38df6c08f53e3bc687f2c4d4`

The experiment branch preserves that candidate subtree byte-for-byte.

## Trigger

Adversarial run `33347963184` showed that finite, acyclic nested data under non-authoritative `metadata.diagnostics` can cross the frozen Python implementation's recursion boundary.

At depth 990 on Python 3.12/3.13, the reference could still validate and canonicalize the Decision but `semantic_identity()` and `consume()` escaped `RecursionError`. The exact frozen independent implementation also hit recursion limits, with slightly different validation/canonicalization thresholds.

The public RC4 specification states that diagnostics may contain arbitrary finite JSON, metadata is non-authoritative, and an object that cannot be interpreted under exact RC4 authority has the `cannot_establish` consumer outcome. It declares no maximum nesting depth.

## Competing repairs tested

### Catch-only

Keep recursive traversal but convert `RecursionError` into a controlled Contract-D error / fail-closed outcome.

This removes uncontrolled exception escape but preserves an accidental interpreter-dependent acceptance boundary.

### Iterative container hardening

Replace recursive finite-JSON traversal and canonical container traversal with explicit-stack implementations while keeping:

- the same JSON type/cycle rules;
- the same finite-number rules;
- the same safe-default/effect logic;
- the same object/field validation;
- the same canonical UTF-8/sorted-key/compact/Unicode-preserving primitive lexical behavior;
- the same authority projection and semantic identity definition;
- the same consumer applicability semantics.

Primitive lexical encoding still delegates to the standard library; only container traversal becomes iterative.

## Hosted discriminator

Workflow run: `33348519662`

Predecessor-identity verification passed in every successful matrix job.

An earlier run, `33348487547`, failed before the experiment because a depth-1 checkout did not contain the predecessor commit needed by an ancestry check. That harness failure is preserved and was corrected by verifying the inherited candidate tree/blob identities directly.

### Python 3.11.16

Artifact: `9742801008`  
ZIP SHA-256: `61c112549a73ed3d1ad36dc941d1ca3e231b06c5ddf46770414ecf7018d565aa`

- ordinary frozen corpus equivalence under iterative handling: **PASS**;
- reference recursive path: escapes by depth 990;
- catch-only: converts the depth failure into controlled `resource_recursion_limit`;
- iterative decoded validation/canonicalization/identity/consume: **PASS through depth 4000**;
- semantic identity at every passing deep case remains `decision:sha256:9f8a43651f0de365a26161f7951493f9e01370dcca46b6e24ea80d1a9636152f`;
- consumer outcome remains `candidate_for_authorization`;
- raw-byte reparsing at depth >=990 returns controlled `invalid_json` on this runtime rather than escaping.

### Python 3.12.14

Artifact: `9742802198`  
ZIP SHA-256: `a2c479f8e2962112f2480853af1ec54d48dad717fb4bde33011cf3c1eff6d529`

- ordinary frozen corpus equivalence under iterative handling: **PASS**;
- reference identity/consume escape at depth 990, broader recursive traversal shortly above it;
- catch-only: controlled failure;
- iterative decoded validation/canonicalization/identity/consume: **PASS through depth 4000**;
- semantic identity remains exactly the ordinary metadata-free identity;
- consumer outcome remains `candidate_for_authorization`;
- tested iterative canonical bytes reparsed successfully through depth 4000 on this runtime.

### Python 3.13.15

Artifact: `9742800995`  
ZIP SHA-256: `87c3b43d176bada118a9b112131601ad2ba89efe0652c5d34ed14a161a3e707e`

- ordinary frozen corpus equivalence under iterative handling: **PASS**;
- reference identity/consume escape at depth 990, validation/canonicalization by depth 992;
- catch-only: controlled failure;
- iterative decoded validation/canonicalization/identity/consume: **PASS through depth 4000**;
- semantic identity remains exactly the ordinary metadata-free identity;
- consumer outcome remains `candidate_for_authorization`;
- tested iterative canonical bytes reparsed successfully through depth 4000 on this runtime.

## Ordinary-domain equivalence

On all three Python runtimes, the iterative variant preserved the frozen ordinary corpus exactly:

- every public valid fixture remains valid;
- every public invalid fixture remains rejected with the same Contract-D error code;
- every public conformance case has the same consumer outcome;
- every tested valid fixture has byte-identical canonical JSON to the frozen reference algorithm;
- every tested valid fixture has the same semantic identity;
- cyclic containers remain rejected;
- shared-but-acyclic aliases remain accepted.

This is the strongest discriminator in this experiment: the iterative change removes the recursion cliff without changing observed ordinary Contract-D semantics.

## Interpretation

### Observed

1. The frozen recursive implementation has runtime-sensitive recursion thresholds.
2. The exact frozen independent implementation also has a recursion threshold and disagrees with the reference about validation/canonicalization at depth 990 on some runtimes.
3. Catch-only handling can convert escaped recursion into a controlled failure but leaves that runtime-dependent acceptance boundary intact.
4. Explicit-stack finite-JSON and canonical container traversal preserve all tested ordinary semantics and eliminate the decoded-object recursion cliff through depth 4000 on Python 3.11/3.12/3.13.
5. Raw JSON parsing may still encounter runtime/parser resource limits, but Python 3.11 converts the tested deep parser limit to controlled `invalid_json`; no authority is granted.

### Inference

The observed recursion cliff is **not inherent to the frozen Contract-D authority semantics**. It is an avoidable implementation artifact in decoded-object validation/canonical traversal.

A numeric public maximum depth tied to CPython recursion limits is not justified by this evidence.

However, the public contract should not leave resource exhaustion behavior implicit. Independent implementations need a common fail-closed rule even if their parser/memory limits differ.

### Supported successor direction

The smallest defensible successor candidate should:

1. use non-recursive/explicit-stack handling for Contract-D-owned decoded finite-JSON validation and canonical container traversal, or an equivalently demonstrated mechanism that is not bounded by ordinary language recursion depth;
2. preserve the existing JSON/cycle/canonical/identity/applicability semantics;
3. explicitly require implementation/resource exhaustion to fail closed and never grant Contract-D authority;
4. ensure the consumer maps interpretation/resource failure to `cannot_establish` rather than allowing recursion/resource exceptions to escape;
5. avoid specifying an arbitrary numeric nesting limit unless later evidence establishes one as part of the compatibility promise;
6. preserve raw-parser resource rejection as a separate ingress concern when it is controlled and non-authoritative.

Because item 3/4 makes the fail-closed resource behavior explicit in the public authority, this should be treated as a **new candidate authority**, not a silent post-reveal repair to RC4.

## Falsifiers for the successor

A successor is not supported if:

- ordinary frozen validity/conformance/canonical bytes/identity change without an explicit justified semantic change;
- cycle rejection or shared-acyclic acceptance changes;
- metadata can change semantic identity for an accepted Decision;
- deep finite decoded metadata can cause an uncontrolled recursion/resource exception in the tested supported runtimes;
- resource exhaustion can yield an authority-bearing outcome;
- a legitimate independent implementation cannot recover the new fail-closed resource rule from the public authority;
- native Decision Engine objects require a translation adapter after the hardening.

## Next step

Freeze a new Contract-D research candidate with the smallest public resource/fail-closed clarification and iterative reference hardening, then run the existing adversarial harness and a new context-free independent reproduction.

Do not reopen production promotion until that successor survives both.