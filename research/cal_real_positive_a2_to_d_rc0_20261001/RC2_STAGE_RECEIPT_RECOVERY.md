# RC2 stage-receipt apparatus recovery

This successor preserves the fixed real BLS / A2-to-D scientific subject from RC0 and RC1.

## Predecessor terminal state

RC1 PR #156 is `INCONCLUSIVE_APPARATUS_AFTER_PARTIAL_SCIENTIFIC_EXPOSURE`.

Its decisive first run `36949720436` reached EB, CAL and parent-bound Contract C for RUN1, then Decision refused the Contract D authority checkout because the workflow had the exact D1 release commit but not the annotated `contract-d-v1.0.0` tag object.

The EB/CAL values were not durably captured before that late failure, so no positive or negative semantic result is inferred.

## Exact recovery delta

Only two apparatus changes are authorized:

1. checkout released D1 by exact annotated tag `contract-d-v1.0.0` with full tag history, while verifying:
   - tag object `6eadd688b482f3c9fce2ce5e7a2841089d852096`;
   - peeled release commit `298a1a0f7b7b6d7712e11200d04faec3e1ca169b`;
2. write an append-only `PRE-DECISION.json` checkpoint after EB/CAL/Contract C production and before Decision invocation, so any later downstream apparatus stop cannot erase the observed front-half result.

The stage checkpoint does not feed any consumer and cannot alter pipeline behavior.

## Protected scientific state

Unchanged:
- source representation/provenance;
- Contract A object / handoff / children;
- target authoring authority and canonical target bytes;
- EB #120 default admission, with no override;
- CAL semantics and target families;
- parent-bound Contract C;
- independent consumer;
- Decision policy/materializer;
- Contract D 1.0.0 semantics;
- acceptance criteria and terminal dispositions.

No reroll or outcome-dependent semantic change is permitted.

## Decisive run rule

Only the first RC2 workflow execution on the final RC2 head is the decisive attempt. The workflow uses PR/manual triggers only, not branch-push triggering, to avoid duplicate simultaneous exposures.

If the exact case reaches a semantic negative result, preserve it. If another apparatus failure occurs, retain any stage checkpoints and classify from the strongest actually observed evidence.
