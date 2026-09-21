# ERS render-bound shadow composition result

## Disposition

`SUPPORTED_FOR_CONTROLLED_LOCAL_RENDER_BOUND_ERS_SHADOW_COMPOSITION`

This result extends the supported PR #127 composition without adding an executor or widening Contract D, Contract E, Decision, or CAL semantics. It proves only that a write-free ERS shadow intent is bound to one exact deterministic pending-review payload.

## Frozen successor

- ERS successor commit: `022fcb58e14864aa173f447fa0c18dd2362b41b0`
- ERS successor tree: `c76334314f2d520190fc6c7c57cd4714501682ac`
- README blob: `2dcb7d2945b7dc5ffaa20739f83cfc94a9ac45ec`
- manifest blob: `7f55fca71236eed99b6c946cbfe8fefeedb9999a`
- render-packet blob: `f3af62c893ca95f23cdc2050862c16898f417b41`
- render-bound shadow blob: `990be0957b76c14e7f3de68b322c8b13fed38882`
- tests blob: `aaff1193f2ce56b8a0d5b6785189feed5381755a`

The first frozen attempt was preserved separately rather than repaired in place: commit `3de1835885a22147d8e930e03448df402661fc3`, tree `f176b9663b28913d81e04b24fac955ec42b3c63a`. Its cross-repository receipt exposed an unsupported numeric informational field in the inherited identity canonicalizer (`unsupported_identity_value`); no authorization, write, or executor occurred. The successor changes that field to a string and was frozen as the commit above.

The frozen ERS RC3 slice remains unchanged at `319e325cdf678673fae645a70e3e34afb7dddef0` and its pre-existing tree/blob state is unchanged.

## Render packet and payload

- Packet schema: `ers-pending-review-render-packet-v1`
- Packet identity: `sha256:fc3ae075b85ebeb4a8d329453505b9a9cd3bb0ee5658e04f5f77b853cc2b2512`
- Packet canonical bytes: `2211`
- Explicit render date: `2026-09-21`
- Payload identity: `sha256:f8d3a15fbf385a5846311b73a3e121bae92f7842d92dafb9ffc79612fd68f221`
- Payload bytes: `1325`
- Payload terminal newline: `true`

The packet contains the live promoter-derived render dependencies: claim content and metadata, run/target data, evidence, contradictions, revision history, tags/status/domain, source display name and URI, and explicit render date. Unspecified database retrieval order is normalized before packet identity. The renderer is pure and produces exact UTF-8 pending-review bytes with deterministic ordering, date rendering, newlines, and terminal-newline behavior; it performs no database, network, filesystem, clock, authorization, or execution operation.

Repeated rendering was byte-identical with the same packet and produced the same payload identity. Reordering nondeterministically retrieved source rows produced the same canonical packet and payload. The independent qualification renderer matched the candidate bytes. All 22 tested render-relevant mutations changed the packet and/or payload identity as expected, including claim fields, run/date, evidence fields/count, contradiction resolution, and every revision field.

## Composition identities

- Decision successor: `816374379ba7eb23f5bfdadaf203b7e287c052db`
- Decision semantic identity: `decision:sha256:3427c5cb6692bf7358c13e47628ef7a91a0c53e78affc58f2ae60173daffcc15`
- Contract E profile: `b153dcc4434cbe8a98616a9e410c6125378144c7`
- Contract E schema: `execution-intent-candidate-v1`
- Contract E variable-list compatibility: accepted five input identities; source bytes unchanged
- Execution-intent identity: `sha256:1c66c881959644193760b8456dc587cfb0cc491a11a73276292ad90df9866147`
- Contract E result identity: `sha256:39e913c46396c9c93a5d3a4e63e36c88c3b177f8397d04d16afc9930f8ebd1e8`
- ERS shadow result identity: `sha256:95853057fd06b2e57277b0fc14f23fea94ae51f2152472aa3a71f8a8759022f1`
- `shadow_ready=true`
- `execution_occurred=false`

The intent binds, in order: Decision semantic identity, PIPE01 claim-content SHA-256 `sha256:fe9a393b0c31f7e2f200cbefc08d9293e364f8a0810865a73003ec3502c387d0`, point-of-use pre-state `sha256:8427056c02e99784c5f915d43b6b96ee4808a85e713056652a4c23fabcfe5903`, render-packet identity, and rendered-payload identity. The consumer independently hashes the supplied packet and payload, independently re-renders the packet, and fails closed for absent or mismatched bytes; it never writes them.

## Qualification and falsification

The following all failed closed: missing payload, one-byte payload mutation, payload from another valid packet, mutated render-packet identity, mutated payload identity, wrong Decision identity, wrong executable identity, wrong pre-state, altered target, and stale authority state. PIPE02 and PIPE03 remained HOLD and stopped before Contract E evaluation. The released Contract D at `298a1a0f7b7b6d7712e11200d04faec3e1ca169b` remained unchanged and rejected `epistemic_audit.stage_pending_review@1` as `unknown_effect_type`.

No sandbox file, real MainFrame mutation, pending-review write, executor, Contract D effect registration, release, or production promotion occurred. Frozen upstream bytes were unchanged: Decision `816374379ba7eb23f5bfdadaf203b7e287c052db`, CAL v3 `ffc43d4e89f5b1f7748e9cde0fa1efc7db47b463`, released Contract D `298a1a0f7b7b6d7712e11200d04faec3e1ca169b`, Contract E profile `b153dcc4434cbe8a98616a9e410c6125378144c7`, and ERS RC3 `319e325cdf678673fae645a70e3e34afb7dddef0` all remained byte-identical.

The smallest remaining falsifier is trusted point-of-use provenance: demonstrate, through released authority, that the point-of-use authority state and evaluation-time state are trusted and current while retaining the exact render-packet and payload binding. Other explicitly open blockers are released Contract D ERS effect registration, Contract E production authorization, real executor behavior, and filesystem write atomicity/recovery semantics.

The machine-readable receipt, including the complete acceptance/falsification matrix and before/after sandbox state (`[]` / `[]`), is `RECEIPT.json` in this directory.
