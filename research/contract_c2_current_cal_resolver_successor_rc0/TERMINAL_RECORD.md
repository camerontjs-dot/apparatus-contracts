# Contract C2 current-CAL resolver successor RC0 — terminal record

## Disposition

`SUPPORTED_CURRENT_CAL_C2_RESOLVER_SUCCESSOR`

This is a bounded independent resolver-authority qualification. It does not authorize Contract C2 merge/release, canonical discovery, Decision release, Contract E production use, Authorization, or execution.

## Exact authority subject

Candidate resolver authority freeze:

`1d33e0612befcf8016816197c90c062373796df9`

Resolver JSON blob:

`1a408246fd3bef0758a958ae716b44ea74bc0689`

The resolver authority is the freeze commit above, not the later evaluator branch head.

## Exact execution

- evaluator head: `52b4207c4497ae78f4b35d5ff6eb33a7602c55b4`;
- Contract C2 exact head: `b42c827acb0a9fe65353354d709add0e27bab307`;
- current CAL producer subject: `c4974388e9a40a87661ed80af9271b9625b7c093`;
- current CAL semantic implementation: `847cc970642bb648dc994b929c2053b5c9d4648c`;
- hard-bound CAL projection blob: `ef32fa4fca52a2bb7fe2896b378f9b6fdef0dfde`;
- predecessor resolver: `43b571464734325277374ee81098553fb7c1b944`;
- policy digest: `44ecc33519fa8911079595d322f5f0decbf0389af42e153ac32214931798e42c`;
- workflow run: `35053521021`;
- job: `104658761304`;
- artifact: `10429876786`;
- artifact digest: `sha256:e7c9f2c482f7fa71ff46ee5df03ed407250d47c57149889d1f8fcb1d353717d7`;
- evaluation digest: `sha256:ae569fe3dea04b19383585b735b41e08d765be13cdb3d66db858899ed155638e`;
- failures: `[]`.

## Resolver contents

The candidate contains exactly two exact semantic-implementation rows.

The predecessor row for `a902621...` is exactly equal to the immutable predecessor resolver row, including:

- policy digest `44ecc335...`;
- canonical policy payload;
- projection blob `9bc152275759304be03b84014c56bd434549a64a`.

The new row binds:

- semantic implementation `847cc970642bb648dc994b929c2053b5c9d4648c`;
- the same canonical policy payload and digest `44ecc335...`;
- projection blob `ef32fa4fca52a2bb7fe2896b378f9b6fdef0dfde`.

## Independent positive coverage

Apparatus independently constructed and executed current-CAL cases for:

- strict support;
- strict refutation;
- alternative-joint mixed causality;
- irrelevant-only no-deciding relation;
- measurement-not-applicable no-deciding relation;
- negative-event unresolved relation;
- support plus unresolved precedence;
- unsupported semantic family.

For every case:

- current CAL executed at the exact pinned subject;
- hard-bound CAL C2 projection executed;
- exact Contract C2 validation passed;
- exact Contract-B reference validation passed;
- `verify_policy_resolution()` against the separately checked-out resolver freeze passed;
- current producer identity and policy digest resolved to the exact new row;
- deterministic repeat passed.

## Hostile controls

All six required mutations were rejected:

1. predecessor resolver rejected current CAL as unknown/ambiguous;
2. deleting the current row from the candidate caused resolution failure;
3. wrong policy digest caused resolution failure;
4. duplicate current rows caused ambiguous resolution failure;
5. unknown semantic implementation caused resolution failure;
6. predecessor resolver-commit substitution under candidate authority failed with wrong resolver authority.

The preserved old row also resolved exactly under the new candidate resolver.

## Next gate

CAL may now consume the independently selected resolver freeze `1d33e061...` in a final producer-authority binding check. After that, downstream Decision and full-pipeline pressure must rerun against C2 objects containing the new resolver commit, because those exact C2 bytes and hashes differ from predecessor-resolver objects.
