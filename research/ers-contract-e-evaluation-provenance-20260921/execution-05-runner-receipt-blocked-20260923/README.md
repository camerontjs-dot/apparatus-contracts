# 05 runner/receipt block before scientific execution

The PR #130 scientific matrix did not start. The unchanged receipt/source preflight passed 86 comparisons, then static review found that the frozen runner reads the ERS 04 receipt path and an obsolete PR #130 field. The ERS 05 receipt at PR #14 uses a different path and the canonical `apparatus.scientific_preregistration.commit` field.

The runner was not invoked. The recorded Python 3.11.15 environment also lacks its top-level `jsonschema`, `rfc8785`, and `cryptography` imports; the exact complete package lock is unknown. No packages were installed and no environment was adapted.

## Frozen identities

- Scientific authority: apparatus PR #130 at `dcdd10355e2f885273d843eef6e345bafca95faa`.
- Qualified receipt/preflight successor: apparatus PR #146 at `cd465d798220daa3f45261d3e6f385cf67224a46`.
- Scientific runner: `d0f3b69949bdeedea87fe0ac82b6d3407eac1a67`.
- Apparatus freeze receipt: `af3385cab18789450d1e02c00a0e07a84ffcfcc9`, blob `bc7d3938be9146dd6455ab5f9fda896f22a70274`.
- ERS PR #14 receipt: `aa214666c9a68871c0d878a70b7f3833d49dbe9b`, blob `50c9493d3f0584de74399118da01b7b603c813e0`.
- ERS implementation source: `65f47d029fb734be1d5d506a135cbeba813f6be8`, tree `405bb622e0d7d0f69f3da7506a15fa0b2390e191`.
- Fixture subject: `sha256:bebbb1b7973a962d59c92061e8e70283a2fb4b2b8c388705b8d80ce13000c7ad`.

## Qualification record

`RECEIPT_SOURCE_PREFLIGHT_REDACTED.json` preserves the 86-check PASS with only the local absolute checkout prefix replaced; the exact source output hash is recorded in `SNAPSHOT_REFERENCE.json`. `STATIC_RUNNER_RECEIPT_REVIEW.json` records the runner’s receipt-path and field mismatch without invoking it. `PRESERVATION_VERIFICATION.json` and `SNAPSHOT_REFERENCE.json` identify the locally preserved exact sources and fixture archive.

Instrumentation from the receipt/source preflight: zero Contract E evaluation calls, zero supervisor launches, no candidate runtime imports, and zero network attempts. No sandbox was created. Matrix cases run: zero.

This disposition establishes no result about evaluation-time provenance. It is a pre-scientific setup block. The next step is a preregistered runner successor and pinned dependency environment, followed by a fresh non-evaluating gate. The earlier results in PRs #143–#146 and ERS #13–#14 remain unchanged.
