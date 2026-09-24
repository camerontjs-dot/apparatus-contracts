# Pre-freeze read-only identity-query attempt

An identity query for the ERS PR #14 receipt was mistakenly run against the apparatus-contracts clone:

    git rev-parse aa214666c9a68871c0d878a70b7f3833d49dbe9b:research/ers-contract-e-evaluation-transcript-rc6-receipt-contract-successor-20260923/FREEZE_RECEIPT.json

Git reported that the path does not exist in commit aa214666c9a68871c0d878a70b7f3833d49dbe9b. That commit belongs to the ERS repository; the query used the wrong repository object database. No repository state changed. The apparatus-side PR #146 receipt blob was correctly resolved as bc7d3938be9146dd6455ab5f9fda896f22a70274. The ERS receipt identity remains bound to the user-provided PR #14 commit/tree/blob and will be checked in a fresh ERS checkout before qualification.

A source-delta proof invocation was run from the successor subdirectory while passing --repo-root ., which resolved the runner path beneath the successor directory rather than the repository root. It failed before reading runner source with FileNotFoundError for /private/tmp/cal-ers05-runner-runtime-successor-20260924/repo/research/ers-contract-e-evaluation-provenance-20260924/runner-runtime-successor-rc0/research/ers-contract-e-evaluation-provenance-20260921/fixture-bound-identity-successor-rc0/reproduce_rc6_fixture_bound.py. No source was changed. The identical checker succeeds when run from the repository root; this is a setup invocation error, not a delta failure.
