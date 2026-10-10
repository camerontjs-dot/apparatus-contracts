# RC2 separate zero-model qualification protocol and preflight

The RC1 stopped outcome is immutable: first Q03 provider connection refusal,
no RC1 actor/inference, no later isolation controls. This RC2 is a distinct
scientific candidate based on the unchanged RC1 report commit
`39a6968f3fbc870272987e251cc049e4c456e071`.

**Before execution:** independently inspect live owner #173 and PR #178.
Use the existing authorized isolated repository clone and external controller
evidence directory. The only source changes allowed are under
`research/cal_fixed_ollama_launcher_rc2_20261010/`.
Keep external `PINS.json`, model blobs, host paths and receipt ledgers
out of the Git tree and worker file world.

The controller-only Ollama service must be reachable on **127.0.0.1:11434**,
bound to the expected existing installed binary, version 0.40.0 and current
model manifest. See `PRE-FREEZE-SERVICE.json`: the result was an independent
pre-freeze availability check, not a Q03 pass.

1. Parse/review all frozen-source code/JSON and the full Q01–Q13 protocol;
   preserve the exact Q03 expected prompt. Require immutable model/worker
   pins and exact controller-private pin SHA. No broad tool or browser access.
2. Commit the preparation only, leaving a clean worktree and exact parent.
3. Run explicit `prepare_freeze.py --pins-path EXTERNAL_PRIVATE_PINS
   --prepared-commit EXACT_PREPARATION_SHA --frozen-at UTC_TIMESTAMP` **before**
   any decisive provider render or Docker worker. Review that manifest.
4. Commit only `FREEZE.json` for the scientific candidate. Record its
   HEAD/tree and SHA-256 externally and preserve the prefreeze receipt.
5. Prepare one exact external `OPERATOR-REVIEW.json` by replacing the
   reviewed candidate SHA, freeze digest, fresh external receipt directory
   and ledger. No review is independent merely because it is written.
6. Execute **once**, with no model inference:

```sh
python3 -E -s -B qualify_once.py /EXTERNAL/FRESH/RC2-ATTEMPT   --candidate-commit FROZEN_RC2_COMMIT   --freeze-sha256 EXACT_FREEZE_SHA256   --operator-review /EXTERNAL/OPERATOR-REVIEW.json   --pins-path /EXTERNAL/PRIVATE/PINS.json
```

Required first stop or any unknown/NOT_RUN blocks Q13. Do not rerun, alter
expected outputs, start a different provider, or work around restrictions.
Post-stop read-only verification of receipts and exact-owned-resource state
is allowed, but does not count as completing skipped Q controls.

**After:** publish a separate sanitized retrospective sibling evidence
directory/commit. Never change frozen experiment code. Continue routine
engineering in a *new separately identified* candidate if the evidence
justifies it, never by silently rerunning this one.
