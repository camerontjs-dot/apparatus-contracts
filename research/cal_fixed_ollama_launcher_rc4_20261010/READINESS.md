# RC4 one frozen zero-model qualification handoff

The frozen RC3 first Q08 failure remains a result, not a pass.
RC4 is a separately identified source-informed research-infrastructure candidate.

Prior to freeze:
1. Inspect live apparatus #173, #137 and Draft #180; confirm ancestor
   `d9ac7505531369221fe89ea239645b09f886f6a3`.
2. Verify the new actual per-interface sysfs flags/operstate and IPv6 address
   observation plus pure fail-closed validator source and the frozen 17
   synthetic development controls. These do NOT qualify worker isolation.
3. Verify exactly inherited Q03 request/expected render, two-function adapter,
   Q01–Q07 and Q09–Q12 logic, except the explicitly added Q08 link-validation
   receipt obligation. No private paths or raw pins enter Git.
4. Preserve source, freeze and report from RC3 without re-exposure. Confirm
   controller-private PINS.json hash, active same loopback-only provider and
   pinned model/image identities. Availability preflight is not Q03 acceptance.
5. Commit the new preparation. Only the RC4 source directory may change.
6. At clean prep commit, explicitly generate then separately commit only
   `FREEZE.json` using `prepare_freeze.py`, bound to external pins,
   exact prep SHA and UTC freeze time.
7. Create exact controller-private operator one-attempt review, distinct
   receipt directory and unused freeze-hash ledger slot. Invoke once:

```sh
python3 -E -s -B qualify_once.py EXTERNAL_RC4_FIRST_RECEIPTS   --candidate-commit RC4_FROZEN_SHA   --freeze-sha256 RC4_FREEZE_HASH   --operator-review EXTERNAL_RC4_REVIEW.json   --pins-path EXTERNAL_CONTROLLER_PRIVATE_PINS.json
```

8. On first failure/unknown, stop all later measurement, record original
   streams, leave frozen bytes untouched, and clean only known task-owned
   resources. On bounded zero-model passes, Q13 stays pending explicit
   exact-profile owner review. No model actor is admitted automatically.
9. Reconcile issue #173 and #137 with sanitized retrospective findings
   stored **outside the frozen subtree** in a new report commit; raw paths
   and receipts stay external. No G89 detour, release, merge or CAL pilot.
