# Contract C polarity identity successor RC0

Issue: #161

## Decision

Determine whether the CAL polarity successor can cross the frozen parent-bound Contract C seam through an identity-only authority successor, with no Contract C representation or recomposition semantic change.

## Exact subjects

- old Contract C freeze: `c5b1d757f3a0ad4f6e2c3f6dbdc2dd2d3c1403ec`
- old candidate blob: `df6b6ed410f52cafaeadfe1578d770f480a34b09`
- old CAL semantic identity: `847cc970642bb648dc994b929c2053b5c9d4648c`
- CAL polarity qualification subject: `86b60022420a006358fde38b20a204ffe4df1a96`
- CAL polarity scientific implementation: `caa0048f8f511ec3c4aa1ce713766f2219a04bc1`
- frozen CAL integration fixture source: `e24e405f5336ee024674f39dba97255bb58a2dd9`
- RC2 authority: `b42c827acb0a9fe65353354d709add0e27bab307`
- resolver: `1d33e0612befcf8016816197c90c062373796df9`

## Hypothesis

The #192 stop is caused only by the exact producer semantic-identity binding. A successor whose candidate bytes differ from the frozen #121 candidate only at `CAL_SEMANTIC_IMPLEMENTATION` should preserve every existing parent-bound semantic and adversarial property.

## Protected boundary

After evaluator freeze, the candidate may change exactly one semantic value:

`847cc970642bb648dc994b929c2053b5c9d4648c -> caa0048f8f511ec3c4aa1ce713766f2219a04bc1`

No other candidate code, schema, RC2 validator, CAL code, resolver, policy, Contract C representation, canonicalization, recomposition field, or expected result may change.

## Evaluator

The evaluator is derived mechanically from the exact frozen #121 evaluator:

`research/contract_c_cal_v1_parent_recomposition_rc0_20260919/evaluate.py`

The only apparatus adaptations before candidate exposure are:

1. use the frozen e24e integration fixture file while importing CAL runtime code from exact polarity subject `86b600…`;
2. load the old #121 candidate independently and require it to reject every legitimate polarity-successor object accepted by the successor candidate because of the old semantic identity;
3. report the old-candidate rejection count.

The inherited four-case observations, representation mapping, mutation controls, cross-run replay control, and disposition logic remain unchanged.

## Acceptance

Support requires:
- candidate byte diff from #121 candidate is only the one semantic identity value;
- four inherited PIPE cases remain representable;
- all inherited mutation/replay controls pass;
- old candidate rejects all legitimate successor objects;
- new candidate accepts them;
- no other protected object changes.

## Falsification

Any additional Contract C semantic/shape change, weakened identity check, changed expected conclusion, or lost mutation/replay discrimination falsifies the identity-only hypothesis.

## Dispositions

- `SUPPORTED_IDENTITY_ONLY_CONTRACT_C_POLARITY_SUCCESSOR`
- `FALSIFIED_IDENTITY_ONLY_CONTRACT_C_SUCCESSOR`
- `INCONCLUSIVE_APPARATUS_INVALID`
