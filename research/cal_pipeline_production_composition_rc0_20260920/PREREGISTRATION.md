# CAL Pipeline production-shaped composition RC0 — preregistration

Date: 2026-09-20

Classification: bounded cross-repository integration qualification. This is an evidence record only. It does not merge, publish, version, retag, authorize, or execute any frozen component.

## Question

Do the exact qualified production-shaped candidates compose without semantic adaptation across:

```text
released Contract A 2.0.0
  -> frozen Evidence Bundler
  -> released Contract B 1.2.0
  -> qualified CAL V1 Slice 2
  -> frozen unversioned parent-bound Contract C
  -> qualified additive Decision Engine ingress
  -> released Contract D 1.0.0
```

while preserving exact external authority and stopping replay before Decision/Contract D materialization?

## Exact subjects

Contract A:
- release commit: `529c92b49a34d5c610618551a8737f019f9fa332`
- tag: `contract-a-v2.0.0`
- annotated tag object: `7d45a2bdcb7cda7cd08f1bac721557c8b8fd885d`
- RC2 validator blob: `42e5f5b3bf38d677445e9d01ea130ba604e53409`
- canonical entry blob: `42a3b032446dc7b9eed8adfb7e66954af2088772`

Evidence Bundler / Contract B:
- EB subject: `4e1f6fe00e7c350b28f52bfea14f1f8988847884`
- Contract B: `1.2.0`
- Contract B production lock: `c314e53bd91c0736aa4370a364673b069aceb43e`
- integration profile: `eb-v1-integration-10x3-rc0`
- compatibility carrier blob: `ddb16cd58baed833adfc4e81d7aef3745a5900f3`

CAL:
- candidate: `ddaf94551e38663920593cab89f9c60d43c1555f`
- tree: `1677a1de987a594f4ee8d2670d56943c5f189fbd`
- disposition: `QUALIFIED_FOR_CONTROLLED_LOCAL_PIPELINE_PARENT_BOUND_RUNS`
- frozen semantic implementation: `847cc970642bb648dc994b929c2053b5c9d4648c`
- DecompositionComposer blob: `268d0dc4dd22ddde3848141d62b7d719e48d374d`
- parent-bound runtime blob: `b6d281590d372729b968ae75fec470c7186d6bd6`
- parent CLI blob: `774178a12acce0ad7a453eb0ba85ec5e5b14fa1c`
- decisive qualification run: `35478782984`

Contract C:
- frozen candidate commit: `c5b1d757f3a0ad4f6e2c3f6dbdc2dd2d3c1403ec`
- candidate blob: `df6b6ed410f52cafaeadfe1578d770f480a34b09`
- profile: `contract-c-cal-v1-parent-recomposition-rc0`
- RC2 authority: `b42c827acb0a9fe65353354d709add0e27bab307`
- current-CAL resolver: `1d33e0612befcf8016816197c90c062373796df9`
- frozen independent consumer: `12e7e640b229619501960b1b89cf4716d8d985b3`
- consumer blob: `662e94c4445d2be9034e786711429394f217c0a6`

Decision Engine:
- candidate: `6cdb59c2ba41779ac954af56dd077574ba090013`
- tree: `d4b75b63462451b5c258a13abf9ce2beb9e78098`
- disposition: `QUALIFIED_ADDITIVE_PARENT_BOUND_INGRESS_FOR_CONTROLLED_LOCAL_PIPELINE_RUNS`
- ingress blob: `83ab34bce30f874111500ed91f2c01421be9f9a0`
- CLI blob: `4e5a85aa1179e815b5e23e6524e2b2a314aab7d0`
- protected V1 policy blob: `2225f73eb6eefd83609f0ba19e4786d1267dd527`
- protected materializer blob: `1562fb29da6679a0cf894e478cbdd4ae16e21a18`
- decisive qualification run: `35472881378`

Contract D:
- release commit: `298a1a0f7b7b6d7712e11200d04faec3e1ca169b`
- tag: `contract-d-v1.0.0`
- annotated tag object: `6eadd688b482f3c9fce2ce5e7a2841089d852096`
- core validator blob: `564dcde5677df5ac8f86f21dc0ffd1692f44c9f0`
- canonical validator blob: `c03ef6c6f059cd03addf5e69b01025bb9a6af8d2`
- independent consumer blob: `8b4ad5c9d6fc1145cf334d1416b5d52b9ed93c68`

## Three decisive cases

Use the already-qualified CAL integration specimen, but execute it through the maintained production-shaped candidates.

1. `PIPE01`
   - C1 decisive support admitted
   - C2 decisive event-order support admitted
   - expected parent: `supported`
   - expected Decision: `CLEAR`
   - expected Contract D consumer result: `candidate_for_authorization`

2. `PIPE02`
   - C1 decisive contradiction admitted
   - C2 decisive event-order support admitted
   - expected parent: `contradicted`
   - expected Decision: `HOLD`
   - expected Contract D consumer result: `hold`

3. `PIPE03`
   - C1 decisive support admitted
   - C2 has no admitted evidence
   - expected parent: `not_checkable`
   - expected Decision: `HOLD`
   - expected Contract D consumer result: `hold`

The Contract D `candidate_for_authorization` outcome is only evidence that CLEAR is eligible for a separately governed Authorization step. This experiment must not perform Authorization.

## Required path

For each case:

1. construct one exact released Contract A 2.0.0 object;
2. independently validate it with the released Apparatus Contract A validator;
3. build the exact frozen EB native package;
4. project exact released Contract B 1.2.0;
5. invoke the clean-installed `claim-audit-v1-parent` candidate with trusted/prevalidated child targets;
6. use the resulting exact frozen Contract C bytes and the exact native child-result bytes to construct only the public frozen-consumer inputs;
7. invoke the maintained Decision parent-bound file CLI;
8. require exact canonical Contract D 1.0.0 bytes;
9. use the released independent Contract D consumer to classify the result without Authorization.

No new semantic adapter may be inserted between stages.

## Negative control

Cross-run replay:

- start from PIPE01's exact frozen Contract C object and fixed external authority;
- replace one common native child result in the independent-consumer input with the corresponding native result from PIPE03;
- retain PIPE01's exact Contract C bytes and expected whole-object authority;
- Decision CLI must reject before emitting any Contract D bytes.

False accept count must be zero.

## Determinism

Re-run PIPE01 from the same exact Contract A/admission/target inputs into a separate output root. Require equality of:
- EB native package identity;
- Contract B bundle identity;
- CAL parent result bytes;
- Contract C bytes and whole-object hash;
- Contract D canonical bytes.

## Stop rules

Stop and preserve the counterexample if:
- the released Contract A validator and frozen EB disagree on the same A object;
- the production CAL candidate differs from its qualified parent conclusion or cannot emit the frozen Contract C representation;
- Decision requires policy/materializer changes;
- Contract D cannot validate the resulting state canonically;
- replay reaches Decision materialization / Contract D output;
- any stage requires discarding, relabeling, or privately smuggling richer state.

Harness/environment defects may be repaired only without changing the exact subjects, three expected outcomes, replay falsifier, or acceptance thresholds. Every failed exposed run remains preserved.

## Allowed terminal dispositions

- `SUPPORTED_THREE_CASE_PRODUCTION_SHAPED_COMPOSITION`
- `FALSIFIED_PRODUCTION_SHAPED_COMPOSITION`
- `INCONCLUSIVE_APPARATUS_INVALID`

A successful result qualifies only this exact composition of frozen/qualified candidates for controlled local-pipeline clearance. It does not merge or release Contract C, CAL, Decision Engine, or perform Authorization.
