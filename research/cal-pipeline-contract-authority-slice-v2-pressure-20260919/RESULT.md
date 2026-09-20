# CAL Pipeline contract-authority slice v2 pressure result

Date: 2026-09-19

## Terminal disposition

**FALSIFIED**

Secondary classification:

`FALSIFIED_V2_SUCCESSOR_CURRENTNESS`

The released authority core carried by the slice was not falsified. The failure is narrower: `SLICE_MANIFEST_V2.json` no longer describes the current Contract C successor state.

## Exact subject

Pressure subject:

`camerontjs-dot/apparatus-contracts@79aa0527b52deaa748947514202c9a415b5f0e23`

Historical v1 freeze preserved at that subject:

- `FREEZE_RECORD.md` blob `01fafba3b4924bcd0394bfc5530c2d525eb6ba1e`
- `SLICE_MANIFEST.json` blob `b66702df8a1f0f272ef113d14897aa01778af0a2`

The v2 update was exactly two additive evidence files relative to prior frozen head `bc05809953bae4010ff54e1e3d28c49be9fd5507`.

## Controls that passed

### Released authority lane

All 22 preregistered normative pins still matched both their exact release commits and consolidated carrier `c3563cff66d2c85dcbf575c693056e2d8e4563d4`:

- Contract A 2.0.0: 6/6
- Contract B 1.2.0: 5/5
- Contract C 1.0.0: 4/4
- Contract D 1.0.0: 7/7

No released A/B/C1/D authority drift was observed.

### Contract C2 candidate identity

All 9 pinned C2 production-shaped candidate blobs matched exact PR #98 head:

`b42c827acb0a9fe65353354d709add0e27bab307`

Global discovery on that candidate still remains:

- canonical: `1.0.0`
- supported: `1.0.0`
- `canonical_registry_switch_authorized=false`

PR #98 remains Draft/open/unmerged.

### Parent-recomposition producer evidence

PR #118 exact terminal subject remained intact:

- terminal head `7aafa6e9235e76f0703a394ee42b799f09136846`
- candidate blob `df6b6ed410f52cafaeadfe1578d770f480a34b09`
- evaluator blob `dd279c8bff695bfb09cac2f782f39be1300a0cdd`
- preregistration blob `40a9e9e0b40bfbc9bf9f9f7e6643e63c2a254bf5`
- workflow blob `07de7803e8b82f9a1bf0c0313c92d9d1b8a4b5ad`
- preserved disposition `SUPPORTED_FOR_INDEPENDENT_CONSUMER_APERTURE`
- producer pressure result 49/49 true

### Manifest authority-laundering matrix

The honest v2 manifest was accepted.

A strong handoff verifier rejected 12/12 preregistered semantic mutations while a deliberately weak JSON-only consumer accepted 12/12:

1. released authority lane changed from C1 to C2;
2. C2 marked admitted to authority lane;
3. C2 marked canonical;
4. independent-consumer authority block removed;
5. independent-consumer state relabelled PASS;
6. parent-binding disposition upgraded;
7. C2 head substituted;
8. Contract E marked included;
9. historical v1 manifest identity substituted;
10. successor STOP removed;
11. successor lane removed;
12. released Contract C entry relabelled 2.0.0.

This supports the internal discriminating power of the v2 handoff. It does not rescue its stale live-state claim.

## Falsifier reached: independent-consumer state moved

The v2 manifest pins RC0 clean-room aperture:

`camerontjs-dot/research-scaffold-harness@52869e08f98ebaaf4acd31dd5955874f7fdaec81`

and labels its state:

`APERTURE_FROZEN_CONSUMER_NOT_YET_EXECUTED`

That is no longer current.

Post-freeze evidence established that the RC0 aperture itself contained a source-level wire defect: it specified native CAL `proposition.text_sha256` in tagged `sha256:<hex>` form, while exact frozen CAL V1 emits the native field as untagged 64 lowercase hex. The RC0 fresh consumer faithfully implemented the supplied rule and false-rejected all four legitimate PIPE01–PIPE04 handoffs at `NATIVE_TEXT_HASH`.

The defect and RC0 false rejects remain preserved. They were not patched in place.

Corrected RC1 evidence then advanced the programme:

- corrected aperture: RSH PR #41 at `aab10774970c2f83af6f918396f9fa36d5d519b7`
- frozen independent consumer: `12e7e640b229619501960b1b89cf4716d8d985b3`
- consumer blob: `662e94c4445d2be9034e786711429394f217c0a6`
- prereveal: 21/21 PASS
- contamination: CLEAN
- decisive consumer run: `35461341449`
- artifact: `10589539839`
- artifact digest: `sha256:74dc44f76dabe0b5ae69dd6e00eab66d02f7936ed41d61b2f49d67c94bf57f9f`
- disposition: `SUPPORTED_INDEPENDENT_CONSUMER_CONFORMANCE_RC1`
- real positive handoffs: 4/4
- mutation/replay checks: 49/49
- false accepts: 0

Therefore the v2 statement that the consumer had not yet executed is false as a statement of current successor state.

## Downstream evidence also moved

Apparatus PR #121 froze the exact parent-bound Contract C downstream-qualification subject at:

`c5b1d757f3a0ad4f6e2c3f6dbdc2dd2d3c1403ec`

with terminal state:

`FROZEN_CANDIDATE_READY_FOR_DOWNSTREAM_QUALIFICATION`

Its exact-head freeze workflow `35469008440` passed and pins the corrected RC1 independent consumer above.

Decision Engine then independently qualified its frozen policy/materialization core against that exact subject in PR #85. Exact-head run `35469302834` passed, and the research disposition used by the subsequent production candidate is:

`SUPPORTED_FROZEN_DECISION_CORE_WITH_ADDITIVE_PARENT_BOUND_INGRESS`

Decision Engine PR #86 now carries the additive production-shaped ingress candidate at:

`6cdb59c2ba41779ac954af56dd077574ba090013`

Its exact-head promotion qualification `35472883514`, ordinary CI `35472883508`, and V1 exact-head qualification `35472883515` all completed successfully. The PR remains Draft/open/unmerged; green CI is not treated here as release authority.

## Production-shaped composition discriminator

Apparatus PR #123 tested the exact chain:

`A2 -> EB -> B1.2 -> CAL candidate -> frozen parent-bound C -> independent consumer -> Decision candidate -> D1`

Exact composition subject at first run:

`517d0eee8d7ea05b4e2cf4c43a9c6d22a1bc4bd5`

Run `35479259240` reached and passed:

- exact immutable-subject verification;
- clean candidate runtime preparation;
- frozen composition harness compilation;
- three-case production-shaped composition;
- replay falsifier;
- no-Authorization/no-execution check;
- ordinary Apparatus regression: 99 passed, 8 skipped;
- exact evidence-receipt generation.

The generated scientific receipt reported:

`SUPPORTED_THREE_CASE_PRODUCTION_SHAPED_COMPOSITION`

with result SHA-256:

`sha256:2ef133c504cd33bf5b9912acb06e154b43d7060b967dd4230081d4a8ad4f9753`

The workflow itself concluded failure only at artifact upload because one legitimate generated passage filename contained `:`, which GitHub artifact upload rejects for cross-filesystem portability. This is an **evidence transport defect after the scientific discriminator**, not a semantic pass for the hosted evidence package. Preserve the failed run and repair only transport before using the composition run as terminal packaged evidence.

## Preserved earlier apparatus failures

PR #119 run `35445510257` remains preserved as two pre-discriminator apparatus defects:

- Gate CLI launched under a path shape where its fetched frozen predecessor vendor directory was not found;
- Decision's shallow Contract C checkout omitted immutable release tag `contract-c-v1.0.0`, causing its authority check to fail closed.

Neither is rewritten as a contract falsifier or a pass.

## Conclusion

The v2 slice is internally well pinned, but it is no longer a current successor handoff.

What survives:

`released A2 -> B1.2 -> C1 -> D1 authority lane`

What is falsified:

`v2 successor status / stop rationale as the current live state`

Do not edit v2 in place. Preserve it as the snapshot that was true before RC0 was falsified and RC1/downstream qualification landed.

## Smallest successor

Before creating v3, repair only the PR #123 artifact-transport defect and rerun the exact frozen composition subject. If the semantic receipt remains byte-equivalent and the evidence package uploads successfully, v3 can pin:

- released A2/B1.2/C1/D1 historical authority unchanged;
- parent-bound Contract C freeze `c5b1d757...`;
- corrected independent consumer `12e7e640...`;
- exact qualified Decision ingress candidate `6cdb59c2...`;
- the terminal production-shaped composition receipt;
- no Contract C SemVer/canonical discovery promotion;
- no Contract E/Authorization/execution.

