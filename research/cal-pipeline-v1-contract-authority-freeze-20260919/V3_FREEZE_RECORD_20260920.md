# CAL Pipeline v3 local handoff freeze record

Date: 2026-09-20

## Terminal state

**FROZEN_V3_READY_FOR_CONTROLLED_LOCAL_PIPELINE_RUNS**

This is a local-pipeline integration freeze, not a production release, merge authorization, Contract C successor release, Decision successor release, Contract E authorization, or execution permission.

## Exact frozen subject

Repository:

`camerontjs-dot/apparatus-contracts`

Frozen v3 subject:

`ffc43d4e89f5b1f7748e9cde0fa1efc7db47b463`

Frozen pointer branch:

`freeze/cal-pipeline-v3-local-handoff-20260920`

Machine-readable manifest:

`research/cal-pipeline-v1-contract-authority-freeze-20260919/SLICE_MANIFEST_V3.json`

Manifest Git blob:

`abb943c2096c0a30113773e17231a30730c05d3f`

The freeze receipt is intentionally committed after the subject was fixed. The receipt commit is an evidence carrier, not a replacement for the frozen subject.

## Historical preservation

V3 descends from v2 subject:

`79aa0527b52deaa748947514202c9a415b5f0e23`

The v3 candidate delta from v2 was exactly two additive files:

- `SLICE_MANIFEST_V3.json`
- `V3_PARENT_BOUND_COMPOSITION_UPDATE_20260920.md`

No v1/v2 file was edited.

Preserved historical blobs on the exact v3 subject:

- original `FREEZE_RECORD.md`: `01fafba3b4924bcd0394bfc5530c2d525eb6ba1e`
- v1 manifest: `b66702df8a1f0f272ef113d14897aa01778af0a2`
- v2 manifest: `a485b177b88322d3d8c03f0fb170fb57922fe59b`

V2 remains terminally preserved as:

`FALSIFIED_V2_SUCCESSOR_CURRENTNESS`

Pressure result:
- PR #122
- result head `3b38c21a22adfb0019352bb7e7cc30452e76cea1`
- result blob `7d183714178cdc6efa9d4e4e8928859ca29762cf`

## Released authority lane

Unchanged:

`Contract A 2.0.0 -> Contract B 1.2.0 -> Contract C 1.0.0 -> Contract D 1.0.0`

Exact v3 pressure rechecked all 22 behaviorally relevant normative pins against both the frozen v3 subject and their released authorities:

- Contract A 2.0.0: **6/6**
- Contract B 1.2.0: **5/5**
- Contract C 1.0.0: **4/4**
- Contract D 1.0.0: **7/7**

Total:

**22/22 PASS**

Contract C canonical discovery remains `1.0.0`.

The parent-bound Contract C candidate is not substituted into released shared authority.

## Controlled local composition lane

Frozen exact chain:

`A2 -> EB@4e1f6fe -> B1.2 -> CAL@ddaf945 -> parent-bound C@c5b1d757 -> independent consumer@12e7e640 -> Decision@6cdb59c2 -> D1`

This lane is qualified for controlled local pipeline runs only.

### CAL Slice 2

Exact subject:

`camerontjs-dot/claim-audit-lab@ddaf94551e38663920593cab89f9c60d43c1555f`

Tree:

`1677a1de987a594f4ee8d2670d56943c5f189fbd`

Key blob pressure:

- DecompositionComposer: `268d0dc4dd22ddde3848141d62b7d719e48d374d` — PASS
- parent-bound runtime: `b6d281590d372729b968ae75fec470c7186d6bd6` — PASS
- parent-bound CLI: `774178a12acce0ad7a453eb0ba85ec5e5b14fa1c` — PASS

Terminal disposition:

`QUALIFIED_FOR_CONTROLLED_LOCAL_PIPELINE_PARENT_BOUND_RUNS`

Decisive exact-head evidence:

- run `35478782984`
- job `105992635181`
- artifact `10595451542`
- artifact digest `sha256:a094195f74c803047097d2a4e446548a00060ba8d255d012e14cbdcd71e26eea`
- qualification-result digest `sha256:d4190bd4e42babf558cf12a4868a527a4fee7fa50c805ee443b5112668ec29a8`

Trusted/prevalidated child-target authoring remains an explicit external boundary.

### Frozen parent-bound Contract C

Exact freeze:

`c5b1d757f3a0ad4f6e2c3f6dbdc2dd2d3c1403ec`

Candidate blob:

`df6b6ed410f52cafaeadfe1578d770f480a34b09`

Freeze metadata verified:

- terminal state `FROZEN_CANDIDATE_READY_FOR_DOWNSTREAM_QUALIFICATION`
- SemVer assigned: false
- production release authorized: false
- freeze run `35469008440`: SUCCESS

Inner RC2 authority remains:

`b42c827acb0a9fe65353354d709add0e27bab307`

Current global Contract C discovery on that candidate remains:

- canonical `1.0.0`
- supported `1.0.0`
- canonical registry switch authorized: false
- promotion state: `pre_merge_candidate`

Resolver blob:

`1a408246fd3bef0758a958ae716b44ea74bc0689`

### Frozen independent consumer RC1

Corrected aperture:

`aab10774970c2f83af6f918396f9fa36d5d519b7`

Frozen consumer:

`12e7e640b229619501960b1b89cf4716d8d985b3`

Exact frozen blobs:

- consumer: `662e94c4445d2be9034e786711429394f217c0a6` — PASS
- tests: `50f3104650a946b834c3ff6415bafb347863e836` — PASS
- freeze receipt: `cb99cd2ee29d38e19c845771654898561b91552f` — PASS

Disposition:

`SUPPORTED_INDEPENDENT_CONSUMER_CONFORMANCE_RC1`

Evidence:

- prereveal 21/21 PASS
- real positive handoffs 4/4
- mutation/replay checks 49/49
- false accepts 0
- contamination CLEAN
- decisive run `35461341449`: SUCCESS
- artifact `10589539839`
- artifact digest `sha256:74dc44f76dabe0b5ae69dd6e00eab66d02f7936ed41d61b2f49d67c94bf57f9f`

The falsified RC0 aperture/consumer path remains preserved separately and is not rewritten.

### Decision controlled candidate

Exact subject:

`camerontjs-dot/decision-engine@6cdb59c2ba41779ac954af56dd077574ba090013`

Tree:

`d4b75b63462451b5c258a13abf9ce2beb9e78098`

Exact key blobs:

- parent-bound ingress: `83ab34bce30f874111500ed91f2c01421be9f9a0` — PASS
- file CLI: `4e5a85aa1179e815b5e23e6524e2b2a314aab7d0` — PASS
- protected V1 policy: `2225f73eb6eefd83609f0ba19e4786d1267dd527` — PASS
- protected V1 materializer: `1562fb29da6679a0cf894e478cbdd4ae16e21a18` — PASS
- protected released C1 ingress: `f57a8067dadc04afb459f1d0342b2b786ec775e6` — PASS

Disposition:

`QUALIFIED_ADDITIVE_PARENT_BOUND_INGRESS_FOR_CONTROLLED_LOCAL_PIPELINE_RUNS`

Decisive evidence:

- run `35472881378`: SUCCESS
- artifact `10593311036`
- artifact digest `sha256:22e5b4da1d80c1452f4eb33062c61801568fffac1dfdb27ed744f491dfe5209b`
- qualification receipt digest `sha256:5fdc5d1ad241c39ee144a0dc5df13702cd476afb254fdeec22e0910070dc23fc`

No successor Decision release version is assigned by this freeze.

## End-to-end production-shaped composition evidence

Exact tested Apparatus head:

`e68e5ab387e9779b0be62d92766b76e475964790`

Terminal disposition:

`SUPPORTED_THREE_CASE_PRODUCTION_SHAPED_COMPOSITION`

Decisive evidence:

- run `35479370533`: SUCCESS
- job `105994253383`
- artifact `10594929710`
- artifact digest `sha256:bab1e7522a69e404208d9e65d9edae89d860827ef08fd3da1ad01813554b0841`
- scientific result digest `sha256:2ef133c504cd33bf5b9912acb06e154b43d7060b967dd4230081d4a8ad4f9753`

Observed:

- PIPE01 supported -> CLEAR -> `candidate_for_authorization`
- PIPE02 contradicted -> HOLD -> `hold`
- PIPE03 not_checkable -> HOLD -> `hold`
- independent deterministic PIPE01 replay: PASS
- cross-run native-child replay rejected before Contract D output
- false accepts: 0
- Apparatus regression: 99 passed, 8 skipped
- Authorization performed: false
- execution performed: false

Preserved predecessor deviation:

`COMPOSITION_ARTIFACT_PACKAGING_FILENAME_DEFECT`

The succeeding evidence run changed artifact upload paths only. No semantic subject, acceptance criterion, expected outcome, or composition harness logic was widened to obtain the pass.

## V3 handoff mutation pressure

The exact v3 manifest blob was accepted by the strong handoff verifier.

Preregistered/adversarial authority-laundering mutations tested:

1. released lane relabelled to parent-bound Contract C
2. controlled lane marked released
3. Contract C2 marked canonical
4. parent-bound C marked SemVer-assigned
5. parent-bound C marked production-released
6. Decision successor marked released
7. Contract E inserted
8. Authorization inserted
9. execution inserted
10. CAL exact subject substituted
11. parent-bound Contract C freeze substituted
12. independent consumer substituted
13. Decision exact subject substituted
14. Contract B chain authority substituted
15. Contract D chain authority substituted
16. composition result digest substituted
17. cross-run replay relabelled accepted
18. cross-run false accept introduced
19. v2 currentness falsification erased

Strong verifier:

**19/19 rejected**

Missed mutations:

**0**

Deliberately weak JSON-only control:

**19/19 accepted**

This confirms that the mutation cohort was syntactically valid and that rejection depended on v3's authority invariants rather than JSON parse failure.

## Exact v3 repository acceptance

Exact frozen subject:

`ffc43d4e89f5b1f7748e9cde0fa1efc7db47b463`

Hosted Apparatus production acceptance:

- run `35479811272`
- job `105995463560`
- conclusion **SUCCESS**

All hosted steps passed, including:

- exact repository-head verification
- cross-repository production gates 1–17
- Apparatus production tests
- Evidence Bundler relevant production tests
- Claim Audit Lab relevant production tests
- canonical contract distribution byte/pin verification
- evidence upload

## Freeze conclusion

The smallest evidence-supported frozen v3 handoff is therefore:

### Released shared authority

`A2 -> B1.2 -> C1 -> D1`

### Controlled local pipeline composition

`A2 -> EB@4e1f6fe -> B1.2 -> CAL@ddaf945 -> parent-bound C@c5b1d757 -> independent consumer@12e7e640 -> Decision@6cdb59c2 -> D1`

Use only the exact frozen identities recorded above.

## Explicit nonclaims

This freeze does not establish or authorize:

- canonical/released Contract C 2.0.0
- a SemVer/release for the unversioned parent-bound Contract C
- a released Decision successor
- target authoring beyond CAL's trusted/prevalidated-target boundary
- Contract E
- Authorization
- execution
- a merge, tag, GitHub Release, or production deployment

Any change to those boundaries or any pinned subject requires a successor handoff/requalification rather than reinterpretation of this v3 freeze.
