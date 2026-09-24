# ERS-EVAL-TIME-PROV-20260922-05 runner/runtime successor preregistration

Status: preregistered before any runner edit or runtime construction. This file is the protocol; this commit changes no runner, ERS source, fixture, contract, or scientific control.

## Question and disposition boundary

Can a bounded successor of the frozen 05 runner consume the exact qualified ERS PR #14 receipt authority, and start under a newly frozen, reproducible runtime, without entering scientific execution?

A pass supports only that non-scientific launch boundary. It does not establish a PR #130 scientific result, Contract E correctness, evaluation-time provenance support, sandbox behavior, or release readiness. The PR #130 scientific matrix is out of scope and will not run.

## Frozen inputs and authorities

| Role | Exact identity |
| --- | --- |
| Preserved blocker | Apparatus PR #147, head `c054d2fb0822e61833cb9e8a5acb7072dbce6531`, base `cd465d798220daa3f45261d3e6f385cf67224a46`; disposition `BLOCKED_BEFORE_SCIENTIFIC_MATRIX` |
| Qualified predecessor | Apparatus PR #146, head `cd465d798220daa3f45261d3e6f385cf67224a46` |
| Scientific authority | Apparatus PR #130, head `dcdd10355e2f885273d843eef6e345bafca95faa` |
| Receipt contract | Apparatus PR #131, head `077ccf6d386526bda258b3e90bd43e153c4c04c5`; contract blob `92b029e6fb5e1a7c11a661911647e618594cd797`. GitHub currently reports this PR closed and unmerged; this exact immutable contract object remains the bound authority. |
| Qualified ERS 05 receipt | ERS PR #14, commit `aa214666c9a68871c0d878a70b7f3833d49dbe9b`, tree `1ad0bb7df9a6d836a5fdca7157173c60429619a3`, receipt blob `50c9493d3f0584de74399118da01b7b603c813e0` |
| ERS implementation | Commit `65f47d029fb734be1d5d506a135cbeba813f6be8`, tree `405bb622e0d7d0f69f3da7506a15fa0b2390e191` |
| Qualified receipt/source preflight | Blob `3314048d5904fa59fdb00e67a1ee108c167097aa` at `research/ers-contract-e-evaluation-provenance-20260921/fixture-bound-receipt-contract-successor-rc0/receipt_preflight_05_contract_compat.py` |
| Predecessor runner | Blob `d0f3b69949bdeedea87fe0ac82b6d3407eac1a67` at `research/ers-contract-e-evaluation-provenance-20260921/fixture-bound-identity-successor-rc0/reproduce_rc6_fixture_bound.py` |
| Fixture subject | `sha256:bebbb1b7973a962d59c92061e8e70283a2fb4b2b8c388705b8d80ce13000c7ad` |

Live GitHub inspection on 2026-09-24 confirmed these heads and object identities. PR #147 remains an open Draft with the specified base and head. PR #131's changed lifecycle state is recorded above; its specified head and contract blob are unchanged.

## Authorized runner delta

The successor starts from the exact predecessor runner blob and changes only:

1. `ERS_RECEIPT_RELATIVE_PATH` to `research/ers-contract-e-evaluation-transcript-rc6-receipt-contract-successor-20260923/FREEZE_RECEIPT.json` from ERS PR #14.
2. The PR #130 lookup from `apparatus.preregistration_head` to `apparatus.scientific_preregistration.commit`.

No other runner behavior is authorized. A mechanical check must show exactly these two source-line replacements and prove whole-AST equality after replacing the two authorized successor nodes with their predecessor values. The check must also verify both source blob identities. If that check cannot pass without another semantic runner change, stop `BLOCKED`; do not widen this protocol.

Protected surfaces remain byte-identical: PR #130 hypothesis, matrix cases, expected outcomes, fixture bytes and subject, Contract E, Contract D, Decision Engine, CAL, Contract C consumer, ERS implementation/runtime, transcript schema, issuer semantics, supervisor API, scientific mutation logic, and provenance-profile semantics. Do not restore obsolete receipt aliases.

## Runtime to freeze

This is a newly frozen successor runtime chosen from available evidence. It is not claimed to reconstruct an unknown historical matrix environment.

The target is Python `3.11.15` on macOS `27.0`, `arm64` (`aarch64-apple-darwin`). Direct package pins are:

- `rfc8785==0.1.4` — pinned by apparatus `pyproject.toml` blob `94396e082c521996c9ed6e39546b3dbb0be60772` in the PR #147 source tree.
- `jsonschema==4.26.0`
- `cryptography==50.0.1`

The latter two are the requested pins from prior ERS qualification evidence. Resolve and freeze the complete platform-specific transitive dependency graph with SHA-256 hashes after this preregistration commit. Do not use ambient site packages. Preserve an offline-installable wheelhouse/archive and bind its hash, every wheel hash, the lock hash, resolver/install commands, Python executable/version/platform, `pip check` or equivalent, imports, and package-version verification in the runtime manifest and qualification receipts. The existing `uv` resolver is `0.11.11`; record the exact resolver and installer identity used. Do not add unrelated packages to the runner environment.

Network may be used before freeze to resolve and download exact wheels; record those calls. Final qualification must install only from the frozen lock and package archive with package indexes disabled and network access denied. Use a fresh environment with system site packages disabled. Do not copy the signing private key; record only the public identity `sha256:e7f4581c2d58eecd0279f895cf3dd49df3098d092fa1e083731d802fcd1db259` and that the secure copy is managed in the local macOS Keychain, requiring the local user session.

## Non-scientific qualification

Use fresh isolated/detached checkouts after the runner/runtime freeze. First establish identity externally with Git, before candidate Python: clean checkout, exact commit/tree, and matching worktree and committed runner/preflight blobs. Do not create a scientific sandbox or supply matrix execution arguments.

Required positive checks:

1. The successor runner source/blob matches its freeze receipt.
2. The source/AST delta is exactly the two changes above.
3. The exact ERS #14 receipt path resolves and its blob matches.
4. `apparatus.scientific_preregistration.commit` resolves to PR #130.
5. The existing receipt/source preflight passes unchanged.
6. The frozen runtime installs offline from the package archive.
7. Every installed package matches the lock and recorded artifact hashes.
8. `pip check` or an equivalent dependency consistency check passes.
9. `jsonschema`, `rfc8785`, and `cryptography` imports and versions match the runtime manifest.
10. Harmless dependency-only checks exercise RFC 8785 canonicalization, JSON Schema validation, and Ed25519 sign/verify using generated test material.
11. The runner completes `--help` under an external guard without starting a supervisor, importing Contract E, processing PIPE cases, creating a sandbox, or making a network call.

Required negative controls must reject at the intended boundary, not an incidental error: predecessor ERS receipt path; obsolete-only `apparatus.preregistration_head`; wrong PR #130 value; wrong ERS receipt blob; wrong runner blob; an extra runner modification; wrong runtime-lock hash; one wrong direct package version; missing required package; altered package artifact/hash; and the old runner paired with the new 05 receipt.

## Counters and stop rule

Expected counters are Contract E evaluations `0`, supervisor launches `0`, PIPE matrix cases `0`, scientific mutations `0`, sandbox creations `0`, and final-qualification network calls `0`. Record the exact harmless imports of `jsonschema`, `rfc8785`, and `cryptography` performed by the dependency checks and runner `--help`; no other candidate-runtime imports are allowed.

After the exact successor is frozen, any required positive or negative qualification failure is preserved with its exact output and yields `BLOCKED` or `INCONCLUSIVE` as justified. Do not patch the frozen successor after observing a failure. If all checks pass, publish a Draft research successor and stop before the PR #130 matrix. Do not merge, promote, release, or run that matrix.

## Pre-registration reconnaissance errors

These read-only setup errors occurred before this protocol was committed. They did not mutate source, construct a runtime, import candidate code, or execute scientific behavior; corrected queries established the identities above. They are retained as provenance rather than treated as qualification outcomes:

- An unquoted GitHub tree URL containing `?recursive=1` was rejected by zsh with `no matches found`.
- A GitHub contents request passed unsupported `--ref` syntax and raised `CalledProcessError`.
- A static AST probe assumed the receipt-path assignment was a literal; `ast.literal_eval` rejected its `Path(...)` call.
- A follow-up read-only probe stopped on a misspelled Python variable (`NameError: name 'ers_repo' is not defined`).
- A read-only contents request asked the ERS repository for `pyproject.toml` at the implementation commit and received `gh: Not Found (HTTP 404)`; that file is in the apparatus repository, not the ERS implementation tree.
- The initial staged `git diff --check` rejected one extra blank line at end of file; it is removed before preregistration.
