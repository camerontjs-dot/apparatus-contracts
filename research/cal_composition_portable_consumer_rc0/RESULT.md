# CAL Composition Portable Consumer RC0 — Terminal Result

Date: 2026-09-18

Classification: Draft Research / independent cross-repository consumer.

## Disposition

**SUPPORTED_CAL_COMPOSITION_PORTABILITY_RC0.**

An independently written Apparatus Contracts consumer accepted the exact frozen CAL composition vectors without importing CAL code or producer-private Python objects.

## Frozen producer authority

- CAL producer PR: `camerontjs-dot/claim-audit-lab#175`
- exact producer head: `6eff362645da14eb49e1e5261c47cd03be5ce29f`
- vector-file SHA-256: `11818e585780ff70b5bf00fe519463fb487dba9d191abb7810946ad43afebf39`
- qualified CAL carrier candidate: `faf2825ee13fe0aea2fa68a520194d847f95f3ab`
- CAL carrier terminal result: `865bbeb30ae672c290be98f023b3c4711aba22a4`

## Independent consumer

- Apparatus base: `c3563cff66d2c85dcbf575c693056e2d8e4563d4`
- exact qualified consumer head: `cefd81878be8def8f103822506f13f391207bd42`
- decisive workflow run: `35363345978`

Observed on the decisive run:

- exact frozen vector-byte hash: PASS;
- all six vectors independently reconstructed: PASS;
- semantic-input digest recomputation: PASS;
- modifier-state digest recomputation: PASS;
- query digest recomputation: PASS;
- deterministic receipt-id recomputation: PASS;
- exact expected-receipt equality: PASS;
- every bound receipt-field mutation rejected: PASS;
- CAL import firewall: PASS;
- static checks: PASS.

The consumer uses only Python standard-library semantics plus test tooling.

## Preserved deviations

Two predecessor runs remain preserved:

1. run `35363078556`: the scientific verifier passed 4/4, but the CI import-firewall grep also searched the negative test assertions and therefore self-triggered;
2. run `35363190298`: the scientific verifier again passed 4/4, but the workflow file still contained the old grep command because the first textual workflow edit did not match the serialized line.

A subsequent workflow-only correction narrowed the firewall to actual import statements in the independent consumer.

Run `35363254291` then passed the scientific verifier and import firewall but failed only Ruff TRY004 on two invalid-type exception classes. The final correction changed those guards from `ValueError` to `TypeError`; no vector bytes, hashing logic, expected receipts, mutation cases, or acceptance semantics changed.

## Supported claim

The bounded composition receipt representation demonstrated in CAL PR #173 is portable across repositories under profile `CAL-CANONICAL-JSON-BOUNDED-1` for the frozen value domain and exact vectors.

This is sufficient evidence to proceed to an integrated CAL composition-registry prototype without requiring CAL-private object identity at the consumer boundary.

## Not established

This result does not establish:

- a final production wire schema;
- RFC 8785/JCS compatibility;
- floating-point canonicalization;
- Unicode normalization;
- arbitrary JSON portability;
- Contract C losslessness;
- Decision Engine compatibility;
- production CAL registration;
- merge or release authorization.
