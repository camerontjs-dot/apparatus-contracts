# CAL context-free packet: macOS synthetic-control successor RC1

**Research infrastructure only.** Owner: [Apparatus #173](https://github.com/camerontjs-dot/apparatus-contracts/issues/173). This is a **separate successor** to [Draft PR #174](https://github.com/camerontjs-dot/apparatus-contracts/pull/174) at original immutable head `7d9df68eff5d83d93aa6f07434d2f2e0d7fc2244`. It does not amend or rerun the RC0 macOS attempt that stopped with 18 passes and one fixture-setup error.

The successor builds on the same offline exact-file packet staging protocol. It fixes the test's macOS directory permissions, rejects case-folded ambient-store names and conflicting case-fold path prefixes, and adds a distinct stdlib checker that **does not import RC0's verifier**. This is *code separation*, not an independently authored or blind evaluator.

## Exact frozen object and result

- `FREEZE.json` pins all five `candidate/` file hashes and the external controller's `run_first.py` hash **before the first RC1 run**.
- `FIRST_RUN_TESTS.txt` is the first-run unittest stderr, including the executed test names and 34/34 `OK`.
- `RESULT-PUBLIC.json` is a sanitized derivative of the controller's original external receipt. The raw original receipt is retained locally with SHA-256 `c8dfa2d221de400e49d317aa63cb918df608e5bf1dd726c846399659ca466f25`.
- `FINDINGS.md` explains what passed, the negative controls, and the remaining boundary.

The exact first-run return code was 0, Python 3.14.4, macOS 27.0 / arm64. Candidate SHA-256 identities were identical before and after. The first-run stderr SHA-256 is `c3307afb3aec3873dca949fb3f22c89eec4976b5db3ff8fbea3114179bd45957`, matching the published text bytes.

For a new *separate* reproduction from a fresh copy of this directory, use Python 3.14 on a compatible macOS host and run `python3 -B controller/run_first.py`. Do not describe a new execution as the original frozen first run. No agent, Docker container, host-MCP tool or network capability is exercised by the test suite.

## Scope

This candidate supports **bounded macOS offline packet custody** with public synthetic inputs, an independently coded (same-controller-authored) checker and a physically executed copy-all weak baseline. It does not support actor admission, complete model-visible inventory, Docker isolation, external credential hygiene, fresh model context, hidden-gold independence, CAL model accuracy, contract changes, or production release.

Original and successor experiments have separate identities. Keep the original failure, this Draft and the actor launcher Q03-Q13 state separate. The earlier G89 safety-denied operation remains outside this route.
