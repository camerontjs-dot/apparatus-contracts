# CAL Pipeline v3 local handoff update

Date: 2026-09-20

## Classification

Integration evidence / local-pipeline handoff successor. This record does not alter any released Contract A/B/C/D semantics, assign a Contract C successor version, release a Decision successor, authorize Contract E, or authorize execution.

## Why v3 exists

V2 remains preserved but was pressure-falsified for successor currentness as `FALSIFIED_V2_SUCCESSOR_CURRENTNESS` on Apparatus PR #122. Its released A2/B1.2/C1/D1 authority core survived; the stale element was the claim that the Contract C parent-binding independent consumer had not yet executed.

That state moved through a corrected clean-room aperture, a frozen independent consumer, a frozen parent-bound Contract C subject, controlled CAL and Decision candidates, and a successful cross-repository production-shaped composition.

V3 records that newer state without rewriting v1 or v2.

## Released authority lane

Unchanged:

`Contract A 2.0.0 -> Contract B 1.2.0 -> Contract C 1.0.0 -> Contract D 1.0.0`

The 22 previously frozen normative release pins remain inherited unchanged.

Contract C canonical discovery remains `1.0.0`.

## Controlled local composition lane

Qualified exact chain:

`A2 -> EB@4e1f6fe -> B1.2 -> CAL@ddaf945 -> parent-bound C@c5b1d757 -> independent consumer@12e7e640 -> Decision@6cdb59c2 -> D1`

This lane is a controlled local-pipeline candidate composition, not released shared Contract C/Decision authority.

### CAL Slice 2

- PR #183
- exact commit `ddaf94551e38663920593cab89f9c60d43c1555f`
- tree `1677a1de987a594f4ee8d2670d56943c5f189fbd`
- disposition `QUALIFIED_FOR_CONTROLLED_LOCAL_PIPELINE_PARENT_BOUND_RUNS`
- exact DecompositionComposer blob `268d0dc4dd22ddde3848141d62b7d719e48d374d`
- parent-bound runtime blob `b6d281590d372729b968ae75fec470c7186d6bd6`
- parent CLI blob `774178a12acce0ad7a453eb0ba85ec5e5b14fa1c`
- decisive artifact digest `sha256:a094195f74c803047097d2a4e446548a00060ba8d255d012e14cbdcd71e26eea`

Its trusted/prevalidated-target boundary remains explicit.

### Parent-bound Contract C freeze

- Apparatus PR #121
- freeze `c5b1d757f3a0ad4f6e2c3f6dbdc2dd2d3c1403ec`
- candidate blob `df6b6ed410f52cafaeadfe1578d770f480a34b09`
- exact freeze run `35469008440`: success
- no SemVer assigned
- no production release authorized

### Independent consumer RC1

- corrected aperture `aab10774970c2f83af6f918396f9fa36d5d519b7`
- freeze `12e7e640b229619501960b1b89cf4716d8d985b3`
- consumer blob `662e94c4445d2be9034e786711429394f217c0a6`
- disposition `SUPPORTED_INDEPENDENT_CONSUMER_CONFORMANCE_RC1`
- 21/21 prereveal PASS
- 4/4 real positive handoffs
- 49/49 mutation/replay checks
- 0 false accepts
- contamination CLEAN

RC0 aperture/fresh-consumer failure remains preserved and is not rewritten.

### Decision controlled candidate

- PR #86
- exact commit `6cdb59c2ba41779ac954af56dd077574ba090013`
- tree `d4b75b63462451b5c258a13abf9ce2beb9e78098`
- parent-bound ingress blob `83ab34bce30f874111500ed91f2c01421be9f9a0`
- file CLI blob `4e5a85aa1179e815b5e23e6524e2b2a314aab7d0`
- disposition `QUALIFIED_ADDITIVE_PARENT_BOUND_INGRESS_FOR_CONTROLLED_LOCAL_PIPELINE_RUNS`
- released V1 policy/materializer/C1 ingress remain byte-identical
- no successor release version assigned

### Cross-repository composition

Apparatus PR #123 exact tested head:

`e68e5ab387e9779b0be62d92766b76e475964790`

Terminal disposition:

`SUPPORTED_THREE_CASE_PRODUCTION_SHAPED_COMPOSITION`

Evidence:

- run `35479370533`
- job `105994253383`
- artifact `10594929710`
- artifact digest `sha256:bab1e7522a69e404208d9e65d9edae89d860827ef08fd3da1ad01813554b0841`
- result digest `sha256:2ef133c504cd33bf5b9912acb06e154b43d7060b967dd4230081d4a8ad4f9753`

Observed:
- supported -> CLEAR -> `candidate_for_authorization`
- contradicted -> HOLD -> `hold`
- not_checkable -> HOLD -> `hold`
- deterministic PIPE01 replay
- cross-run native-child replay rejected before Contract D output
- 0 false accepts
- no Authorization
- no execution

The first run's artifact-packaging filename defect remains preserved. The successful successor changed only artifact transport paths.

## V3 ceiling

V3 may support controlled local CAL Pipeline runs against these exact pinned candidates.

It does not establish:
- canonical/released Contract C 2.0.0;
- a released or SemVer-assigned parent-bound Contract C;
- a released Decision successor;
- Contract E;
- Authorization;
- execution;
- trusted target authoring beyond CAL's explicit prevalidated-target boundary.

Any such change requires a new handoff/requalification rather than reinterpretation of v3.
