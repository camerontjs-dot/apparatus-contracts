# Contract B RC1 Metamorphic Controls — Deviation 001

**Date:** 2026-08-27  
**Run:** GitHub Actions `33088001635`  
**Classification:** apparatus-only pre-execution failure  
**System under test changed:** no  
**Fixtures/acceptance criteria changed:** no

## Observed failure

The first workflow run stopped at `Verify frozen RC1 consumers unchanged from parent` before Python/Node setup or any preregistered control executed.

The workflow attempted:

```text
git rev-parse aa016bcebd57dd09870a9cd4cc129ea7f7f5fc43:experiments/contract_b_rc1_consumer_a.py
```

The Apparatus checkout used the default `fetch-depth: 1`, so the parent commit object was not available locally. Git reported that the path existed on disk but not in the unresolved parent revision.

## Why this does not update the research result

No experimental mutation, normalization, semantic projection, or failure control executed. The run therefore contains no evidence for or against the RC1 claim.

The exact pinned EB and CAL heads were verified successfully before the apparatus failure.

## Correction

Replace the parent-revision lookup with direct checks of the current consumer Git blob IDs against the already frozen blob IDs at the RC1 parent:

- Consumer A blob: `2df5419ce8ca138f27ac381e246e864411bb8587`
- Consumer B blob: `230c86dd2d84d1d2618cbf4f92291d6da596e597`

This tests the intended invariant, byte-identical consumer files, without requiring additional Git history.

No consumer code, fixture, mutation, expected result, threshold, or falsifier is changed.

## Validity

Run `33088001635` remains preserved as a failed apparatus run and is not counted as a decisive execution. The corrected workflow may proceed as the first decisive execution if the consumer-byte guard and all preregistered setup checks pass.