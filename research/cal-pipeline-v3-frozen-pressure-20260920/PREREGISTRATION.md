# CAL Pipeline v3 frozen handoff pressure test

Date: 2026-09-20

## Classification

Research / integration assurance against an already frozen local-pipeline handoff.

This branch MUST NOT modify the frozen v3 subject, any released contract, CAL/EB/Decision runtime, parent-bound Contract C subject, independent consumer, or any upstream/downstream semantic authority.

## Exact frozen subject

`camerontjs-dot/apparatus-contracts@ffc43d4e89f5b1f7748e9cde0fa1efc7db47b463`

Frozen pointer:

`freeze/cal-pipeline-v3-local-handoff-20260920`

Expected v3 manifest blob:

`abb943c2096c0a30113773e17231a30730c05d3f`

## Questions

1. Does the exact frozen subject still preserve every released A2/B1.2/C1/D1 normative byte?
2. Do all controlled-lane candidate commits, trees, blobs, receipts, and artifact digests still resolve exactly?
3. Can the v3 manifest distinguish released authority from controlled local qualification under stronger structural and authority-laundering mutations?
4. Can the exact frozen A→D composition be reproduced from clean exact checkouts with no semantic adapter and the same terminal behavior?
5. Does cross-world native-child replay still fail before Contract D output?
6. Has any live pinned PR/branch drifted such that v3 is no longer a faithful current handoff?

## Frozen positive expectations

Released authority:
- A2/B1.2/C1/D1 normative pins: 22/22 exact.

Controlled lane:
- EB `4e1f6fe00e7c350b28f52bfea14f1f8988847884`
- CAL `ddaf94551e38663920593cab89f9c60d43c1555f`, tree `1677a1de987a594f4ee8d2670d56943c5f189fbd`
- parent-bound C `c5b1d757f3a0ad4f6e2c3f6dbdc2dd2d3c1403ec`
- independent consumer `12e7e640b229619501960b1b89cf4716d8d985b3`
- Decision `6cdb59c2ba41779ac954af56dd077574ba090013`, tree `d4b75b63462451b5c258a13abf9ce2beb9e78098`
- D1 `298a1a0f7b7b6d7712e11200d04faec3e1ca169b`

Frozen composition expectation:
- PIPE01 supported -> CLEAR -> candidate_for_authorization
- PIPE02 contradicted -> HOLD -> hold
- PIPE03 not_checkable -> HOLD -> hold
- deterministic replay true
- cross-run native-child replay rejected before Contract D output
- Authorization false
- execution false

## Structural mutation cohort

The strong v3 verifier must reject all of the following while a weak JSON-only consumer accepts them:

1. released lane changed to parent-bound C
2. local lane promoted to released authority
3. C2 made canonical
4. parent-bound C assigned SemVer
5. parent-bound C marked released
6. Decision successor marked released
7. Contract E inserted
8. Authorization inserted
9. execution inserted
10. CAL commit substituted
11. CAL tree substituted
12. parent-bound C freeze substituted
13. independent consumer substituted
14. Decision commit substituted
15. Decision tree substituted
16. Contract B authority substituted
17. Contract D authority substituted
18. EB subject substituted
19. composition result digest substituted
20. composition artifact digest substituted
21. CAL qualification artifact digest substituted
22. consumer artifact digest substituted
23. Decision qualification artifact digest substituted
24. deterministic replay cleared
25. cross-run replay relabelled accepted
26. one cross-run false accept introduced
27. v2 falsification erased
28. trusted/prevalidated-target boundary removed
29. controlled chain stage omitted
30. controlled chain stage duplicated
31. controlled chain order changed
32. controlled chain repository substituted
33. controlled authority class promoted from candidate to released
34. composition terminal disposition upgraded to production authorization
35. release posture object removed

## Falsifiers

Terminal pressure failure if:
- any exact identity/pin fails;
- any current pinned PR head drifts from the frozen commit;
- frozen branch no longer points at the frozen subject;
- any structural mutation above is accepted by the strong verifier;
- clean exact composition changes terminal behavior;
- replay attack reaches Contract D output;
- Contract E, Authorization, or execution appears;
- the pressure apparatus must alter a frozen semantic subject to pass.

## Interpretation ceiling

A pass establishes only that the exact v3 handoff remains internally pinned, externally resolvable, mutation-resistant under this cohort, and reproducible for the three frozen production-shaped cases.

It does not establish broad production readiness, canonical Contract C2, released Decision successor, trusted target authoring, Contract E, Authorization, execution, or a production deployment.
