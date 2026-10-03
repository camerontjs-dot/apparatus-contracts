# Contract C CAL polarity authority successor RC0

Issue: #163

## Decision

Determine whether the CAL polarity successor needs only a producer-authority transcription across Contract C: new semantic implementation identity, identity-guarded projection blob, and immutable resolver binding, with Contract C/RC2 representation and parent-recomposition semantics unchanged.

## Frozen predecessor evidence

- CAL qualification subject: `86b60022420a006358fde38b20a204ffe4df1a96`
- CAL scientific implementation: `caa0048f8f511ec3c4aa1ce713766f2219a04bc1`
- old parent-bound Contract C freeze: `c5b1d757f3a0ad4f6e2c3f6dbdc2dd2d3c1403ec`
- old outer candidate blob: `df6b6ed410f52cafaeadfe1578d770f480a34b09`
- old resolver: `1d33e0612befcf8016816197c90c062373796df9`
- old projection blob for `847cc970…`: `ef32fa4fca52a2bb7fe2896b378f9b6fdef0dfde`
- exact RC2 authority: `b42c827acb0a9fe65353354d709add0e27bab307`
- #161 identity-only first run: `37141735256`, falsified by missing resolver binding.

## Allowed successor bytes

Before decisive execution, freeze:

1. a CAL research projection copy whose source equals old projection blob `ef32fa4…` except for exactly one semantic-identity guard substitution `847cc970… -> caa0048f…`;
2. a resolver JSON equal to the old resolver plus exactly one entry for `caa0048f…`, preserving the exact old policy object and policy SHA and naming the exact successor projection blob;
3. an outer parent-bound candidate equal to #121 except for:
   - `CAL_SEMANTIC_IMPLEMENTATION` -> `caa0048f…`;
   - `POLICY_RESOLVER_COMMIT` -> the exact commit freezing the successor resolver.

No other semantic, schema, canonicalization, basis, terminal, or recomposition change is allowed.

## Evaluator

Freeze evaluator before the projection, resolver, or outer successor candidate is created.

Required controls:

- old projection blob identity is exact;
- old projection fails closed under new CAL identity;
- successor projection differs only at the guard and runs on positive and frozen-polarity negative comparison cases;
- successor projection emits exact new producer identity and unchanged policy digest;
- old resolver rejects new producer binding;
- successor resolver accepts it;
- resolver differs by one exact entry only;
- outer candidate differs by the two authority constants only;
- inherited four-case parent-bound observations remain representable;
- all inherited mutation and cross-run replay controls continue to reject;
- old #121 outer candidate rejects all legitimate successor objects.

## Dispositions

- `SUPPORTED_AUTHORITY_ONLY_CONTRACT_C_POLARITY_SUCCESSOR`
- `FALSIFIED_AUTHORITY_ONLY_CONTRACT_C_SUCCESSOR`
- `INCONCLUSIVE_APPARATUS_INVALID`
