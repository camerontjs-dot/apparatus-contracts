# Contract C 2.0 parent-bound convergence promotion

## Objective / decision

Prepare the smallest canonical Contract C 2.0 production candidate justified by the completed Contract C successor and CAL Pipeline composition evidence.

The proposed public compatibility class is **MAJOR / 2.0.0** relative to released Contract C 1.0.0.

This setup commit does not merge, release, tag, switch canonical discovery, or authorize downstream action.

## Authority

Live production base at setup:

- Apparatus Contracts `main`: `c3563cff66d2c85dcbf575c693056e2d8e4563d4`
- released Contract C 1.0.0 remains canonical and unchanged.

Frozen parent-bound subject:

- PR #121 / commit `c5b1d757f3a0ad4f6e2c3f6dbdc2dd2d3c1403ec`
- candidate blob `df6b6ed410f52cafaeadfe1578d770f480a34b09`
- profile `contract-c-cal-v1-parent-recomposition-rc0`
- inner Candidate A RC2 authority `b42c827acb0a9fe65353354d709add0e27bab307`

Predecessor C2 production-transcription evidence:

- Draft PR #98 / `b42c827acb0a9fe65353354d709add0e27bab307`
- EDR-005 / issue #97.

Later evidence that must not be collapsed into #98:

- #121: exact parent-bound freeze;
- RSH #42: corrected fresh independent consumer, 4/4 legitimate handoffs accepted, 49/49 mutation/replay checks rejected, 0 false accepts;
- Decision #85/#86: frozen Decision policy/materializer core works unchanged behind an additive parent-bound ingress;
- Apparatus #123/#124: three-case production-shaped semantic composition;
- Apparatus #153: separate ERS-free real-source transport/integrity baseline.

## Promoted surface

Promote only the combination already demonstrated:

1. exact Candidate A RC2 child-result semantics;
2. exact tested typed parent recomposition binding for declared `all_of`;
3. exact child native-result / CAL-result bindings;
4. exact decomposition receipt and root/child sequence binding;
5. exact frozen CAL semantic/resolver authority binding;
6. deterministic canonicalization and independent whole-object authority.

Do not add:

- new CAL semantic families;
- new composition operators;
- target-authoring semantics;
- downstream Decision policy;
- Contract D changes;
- Contract E / Authorization / execution semantics;
- a C2 -> C1 semantic downgrade.

## Protected released authorities

Must remain unchanged:

- Contract A 2.0.0;
- Contract B 1.2.0;
- Contract C 1.0.0 files/tag/release;
- Contract D 1.0.0.

Global Contract C discovery remains C1 until the exact C2 promotion head passes every pre-merge gate.

## Required production transcription

Construct the production surface from current `main`; do not merge the research stacks wholesale.

Reuse exact frozen Candidate A RC2 bytes from #98 where they remain the inner authority. Add only the smallest production representation of the frozen #121 parent binding.

Research tokens may remain integrity-bearing when renaming would create different object identities. Public compatibility/version metadata may expose `2.0.0` externally, but any identity transcription must be mechanically proven equivalent rather than assumed.

## Pre-merge gates

All must pass on one exact promotion head.

### 1. Production transcription equivalence

- schema/spec/validator/reference agree;
- exact #98 RC2 obligations preserved;
- exact #121 parent-bound obligations preserved;
- no extra public semantic obligation appears;
- C1 discovery/validator behavior unchanged.

### 2. Producer conformance

Use the current clean CAL V1 convergence candidate derived from #183/#184 once frozen.

Required property: legitimate CAL state produces canonical C2 without any new CAL epistemic judgment.

### 3. Independent consumer conformance

Re-exercise an implementation/consumer that does not require producer-private state against the exact canonical C2 bytes.

Changing profile/version/canonical bytes means old consumer evidence is lineage, not a substitute for this exact-head gate.

### 4. Compatibility matrix

Mechanically establish:

- C1 -> C1 valid;
- strict C1 rejects exact C2;
- exact C2 accepts C2;
- wrong version/profile/cross-object substitution rejects;
- no claimed C2 -> C1 downgrade passes while preserving the tested parent/RC2 semantics.

### 5. Adversarial / discrimination gate

Retain meaningful replay, stale authority, wrong B world, producer/policy/resolver substitution, participant role/relation, basis, execution-state, parent/child/decomposition, native-result, reseal, unknown-field and version self-selection attacks.

Include at least one plausible weak consumer/validator that fails a meaningful gate for the intended reason.

### 6. Pipeline conformance

Reproduce the bounded semantic routing demonstrated by #123 on the exact canonical C2 head:

- supported -> CLEAR;
- contradicted -> HOLD;
- not_checkable -> HOLD;
- cross-world replay rejected before D1 output;
- Contract D 1.0.0 unchanged.

Treat #153 separately as real-source transport/integrity evidence. Do not use its zero-admission outcome as positive semantic-discrimination evidence.

### 7. Packaging / release

Before merge/release:

- full Apparatus regression;
- supported Python matrix;
- leak/private-path checks;
- build/install or direct artifact smoke appropriate to this contract;
- exact promotion receipt;
- compatibility/migration notes.

After merge, require a post-merge release-lock before immutable `contract-c-v2.0.0` tag/GitHub Release.

## Stop conditions

Stop rather than widen the production PR if:

- canonical transcription changes a demonstrated semantic obligation;
- a legitimate CAL producer requires a new semantic judgment;
- an independent consumer requires CAL-private state;
- a C1/C2 compatibility result contradicts the MAJOR classification;
- a new in-domain adversarial mutation survives;
- Decision integration requires importing destination policy into Contract C.

Preserve the failure and return to the smallest discriminating experiment.

## Current disposition

`PROMOTION_SETUP_ONLY`

This file authorizes implementation of the bounded production transcription and its gates. It does not authorize merge, canonical discovery switch, tag, release, Contract E, Authorization, or execution.
