# RC3 freeze and execution handoff

RC3 is a **new subject** descended from the exact frozen RC2 Q04 checker-stop
report. The original RC2 attempt's first failure and receipts remain unchanged.
Do not claim Q04 pass from the prefreeze schema discriminator.

Prepare in a separate clean branch/isolated local repository clone:
1. Inspect live apparatus #173 and PR #179, verify base head
   `81bc96b72aeff5267d07c354a8a01f9fe1ade94b`.
2. Confirm `PRE-FREEZE-SCHEMA-CHECK.json` catches the old `freeze["pins"]`
   bug and has no missing referenced freeze fields for the candidate.
   Confirm private pin SHA-256, immutable image ID and exact Ollama model
   binary/manifest unchanged. A listener preflight is **not** Q03 acceptance.
3. Verify all source code parses, JSON parses, and fixed source/expectation
   bytes other than the surgical Q04 correction are unchanged.
4. Commit preparation; require exactly this new RC3 directory in changed paths.
5. Generate `FREEZE.json` only at a clean preparation commit:
   `python3 -E -s -B prepare_freeze.py --pins-path EXTERNAL_PINS.json
   --prepared-commit PREP_COMMIT --frozen-at UTC_ISO`.
   Freeze must hash all public files plus the exact #175 packet modules, and
   must carry external pin SHA only, never private host paths.
6. Commit **only** `FREEZE.json` and record full candidate commit, tree and
   freeze SHA. The preexisting RC2 one-shot ledger must not be reused.
7. Under the operator-authorized **one** zero-model public-synthetic task
   and an external exact review record, execute once:

```sh
python3 -E -s -B qualify_once.py EXTERNAL_FRESH_RC3_RECEIPTS   --candidate-commit RC3_FROZEN_COMMIT   --freeze-sha256 RC3_FREEZE_SHA256   --operator-review EXTERNAL_RC3_OPERATOR_REVIEW.json   --pins-path EXTERNAL_CONTROLLER_PRIVATE_PINS.json
```

8. Stop at the first failure. Preserve exact raw stdout/stderr/HTTP/worker
   receipts and one-shot ledger. Teardown only recorded owned resources.
   Do not relabel cleanup-only as Q12 full reset.
9. Publish sanitized retrospective evidence **outside the frozen subtree**,
   reconciling #173/#137. Do not merge/release or infer Q13 actor admission.

Scope limits: source-informed same-controller checker, no independent blinded
authorship; no actual model generation or CAL scientific pilot. Green model-
request/custody/worker controls would justify only a *bounded zero-model
infrastructure candidate*, pending owner review and later model fitness.
