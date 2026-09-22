# ERS point-of-use context provenance result

## Disposition

`FALSIFIED_POINT_OF_USE_CONTEXT_EVALUATION_TIME_PROVENANCE`

The authentic RC5 path passed as a write-free shadow composition. The provenance hypothesis did not: after the frozen Contract E gate returned, changing only `authorization.request.evaluation_time` in its result caused the pinned observer to issue a fresh, validly signed receipt for the substituted time. RC5 accepted that receipt and returned `shadow_ready=true`. The consumer therefore checked that the supplied time was close to the observer's clock, but did not establish that it was the time Contract E actually evaluated.

No candidate source was repaired after freeze. This result does not authorize a pending-review write.

## Frozen apparatus

- ERS preregistration: `907a10dae0d3d1fc78acbfda3c26a164f3a4693b` ([ERS PR #8](https://github.com/camerontjs-dot/epistemic-research-system/pull/8)).
- ERS RC5 candidate: commit `099f84700f28e118734f1ca74feb977da1c4cf17`, tree `db84bae8bf070d03ce9b613ab9c35e6302f8dc0c`.
- Cross-repository preregistration/runner: apparatus commit `f5c356e`; diagnostic-safe runner successor `5035059809de9b595caab601140b8b0c2022024f`.
- Render-bound base: ERS RC4 `022fcb58e14864aa173f447fa0c18dd2362b41b0`; frozen ERS RC3 `319e325cdf678673fae645a70e3e34afb7dddef0`.
- Decision `816374379ba7eb23f5bfdadaf203b7e287c052db`; CAL v3 `ffc43d4e89f5b1f7748e9cde0fa1efc7db47b463`; released Contract D `298a1a0f7b7b6d7712e11200d04faec3e1ca169b`; Contract E profile `b153dcc4434cbe8a98616a9e410c6125378144c7`; Contract C consumer `12e7e640b229619501960b1b89cf4716d8d985b3`.

RC5 adds `ers-point-of-use-context-receipt-v1`, signed with Ed25519 by a separate qualification-only local supervisor process. The observer rereads a disposable authority-state fixture and reads its own OS UTC clock. Its receipt binds the intent identity, authority-state identity, Contract E request time, source identifiers, and consumer-generated challenge. The receipt signature and body identity were independently recomputed by the apparatus harness.

## Successful controlled path

The PIPE01 native Decision identity remained `decision:sha256:3427c5cb6692bf7358c13e47628ef7a91a0c53e78affc58f2ae60173daffcc15`. The unchanged render packet was `ers-pending-review-render-packet-v1`, identity `sha256:fc3ae075b85ebeb4a8d329453505b9a9cd3bb0ee5658e04f5f77b853cc2b2512`; its exact payload identity remained `sha256:f8d3a15fbf385a5846311b73a3e121bae92f7842d92dafb9ffc79612fd68f221`.

The RC5 execution intent kept `execution-intent-candidate-v1` and the existing five bindings: Decision, claim content, point-of-use pre-state, render packet, exact rendered payload. Contract E accepted the five-entry `input_identities` list without source changes. For the frozen run:

- execution-intent identity: `sha256:45e86d877a5882e3171108981ec52d4bc95ac2883cca4128e5f0ba300026152b`
- Contract E result identity: `sha256:d0abb0c004b87874dffb64e46db332001c489e0dd4dde9975d9c0f6331d76ac3`
- ERS shadow result identity: `sha256:419a1648a14aa55e2bdf3bc6df19dead41abb26141afd51a048b0cd05f389812`
- authentic context receipt identity: `sha256:c906c2ea98d4e8cb9082a8c4b161ca05df661682c139f9e7e282c59126668b4e`
- result: `shadow_ready=true`, `execution_occurred=false`
- sandbox entries before and after: `[]` / `[]`

The receipt's source identifiers accurately distinguish the authority fixture, the Contract E request's `evaluation_time`, and the observer's own clock. The positive receipt was fresh (about 0.05 seconds old at observation) and its signature verified independently.

## Falsifying observation

The harness copied the genuine Contract E result, changed only its request time from `2026-09-22T00:43:25.234368Z` to `2026-09-22T00:43:24.234368Z`, and sent it through the normal RC5 consumer. The original result identity was `sha256:d0abb0c004b87874dffb64e46db332001c489e0dd4dde9975d9c0f6331d76ac3`; the altered object's identity became `sha256:054b9e6abd5a861819d497a389a9aee49c203e60b1d763e143fe8b97747eccb8`.

The observer signed the altered time under the pinned key. The independent harness verified that receipt as `sha256:92bdd7ee640f69f1e1acdcfc56d15b68da3c3173b70eb9c31ccc7968f77770d3`. RC5 accepted it and again returned `shadow_ready=true`, `execution_occurred=false`. The receipt was authentic as an observer statement, but the observer had endorsed a caller-mutated Contract E field rather than independently sourcing the time Contract E evaluated. This is the experiment's falsifier; it is not a write or an execution.

## Regression and preservation checks

The frozen RC5 focused and inherited render-bound suite completed with **29 passed and 22 subtests passed**. It covers the authentic fresh receipt; unsigned and invalid-signature receipts; wrong issuer; copied challenge/receipt and replay; wrong intent, authority-state identity, and evaluation time; stale/future time; unavailable/unreadable observer sources; missing payload; render-packet and payload identity; existing Decision/executable/pre-state/target controls; deterministic rendering, ordering, and render-relevant mutations.

PIPE02 and PIPE03 remained HOLD and stopped before Contract E evaluation. The supported-claim output remained byte-compatible with the frozen fixture outputs. Released Contract D still rejected `epistemic_audit.stage_pending_review@1` as `unknown_effect_type`. Decision, CAL v3, Contract D, Contract E, RC3, and RC4 source bytes were unchanged.

Development failures remain in the frozen ERS RC5 slice as `FAILED_ATTEMPT_001.md` and `FAILED_ATTEMPT_002.md`. Apparatus reproduction attempt 001 is also preserved. Its raw local-only receipt has SHA-256 `fe842aa9ad8202ab7926814918d2bcceb58402a8decb9f058621c4f38af445a4`; it was not published because its Contract D traceback contained a local checkout path. The sanitized rerun is recorded in [RECEIPT.json](RECEIPT.json).

The publication leak scan found no absolute local paths or credentials in the current working tree. Its history scan still reports runner tracebacks in inherited apparatus commits `a28506015e3a00bb602a0aa088f1554d4e494814` and `778291f1c34432222f0f1377baa628575b17eee2`. Those commits are already part of the PR #128 base history and were not rewritten.

## Boundaries that remain open

The qualification issuer is a local test process; it does not establish same-user process isolation, trusted production clock, live authority-state provenance, or production key custody. The pipeline caller can still alter the evaluation-time field before the observer sees it. Released Contract D ERS effect registration, Contract E production authorization, real executor behavior, and filesystem write atomicity/recovery semantics remain open. No executor, pending-review write, real MainFrame mutation, effect registration, release, or promotion occurred.

The smallest next falsifier is to require the Contract E evaluation time to originate from an independently trusted observation and remain bound to the exact Contract E evaluation result. Replaying the one-second post-authorization mutation must then fail before `shadow_ready`.
