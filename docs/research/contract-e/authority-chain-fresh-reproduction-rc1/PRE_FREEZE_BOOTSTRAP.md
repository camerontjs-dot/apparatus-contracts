# Contract E Authority-Chain Fresh Independent Reproduction RC1 — Pre-Freeze Bootstrap

## Classification

CONTEXT-FREE REQUIRED.

This file and `AUTHORITY-CHAIN-CONTRACT-v1.json` are the complete pre-freeze task authority. Do not retrieve surrounding CAL Pipeline context, prior Contract E research, RC0/RC0B results, reference implementations, evaluators, hidden cases, prior reproductions, conversation memory, personal context, broad GitHub search, or repository-wide code search.

## Objective

Independently implement the normative authority-chain evaluator defined by `AUTHORITY-CHAIN-CONTRACT-v1.json`.

The purpose is to test independent recoverability, not to make the candidate pass. Preserve ambiguity, implementation difficulty, failed tests, deviations, and suspected contract defects.

## Exact target repository

`camerontjs-dot/research-scaffold-harness`

Exact clean base:

`548bfa81f65290eda15af658f647497679b840ef`

Execution branch:

`research/contract-e-authority-chain-fresh-reproduction-rc1-20260901`

Implementation directory:

`research/contract_e_authority_chain_fresh_rc1/`

Required implementation entrypoint:

`research/contract_e_authority_chain_fresh_rc1/authority_chain.py`

Required callable:

```python
def evaluate(case: dict) -> dict:
    ...
```

## Allowed pre-freeze information aperture

Repository:

`camerontjs-dot/apparatus-contracts`

Exact aperture commit is supplied in the launch prompt.

You may read only:

- `docs/research/contract-e/authority-chain-fresh-reproduction-rc1/AUTHORITY-CHAIN-CONTRACT-v1.json`
- `docs/research/contract-e/authority-chain-fresh-reproduction-rc1/PRE_FREEZE_BOOTSTRAP.md`
- the exact clean target repository base/branch named above
- files you yourself create on the fresh execution branch

Do not inspect sibling files, commit parents beyond verifying the exact supplied commit, PR bodies, issues, Actions logs from other branches, code search results, repository history for Contract E, or other repositories before freeze.

## Required pre-reveal work

1. Verify the exact aperture commit and Git blobs/hashes supplied in the launch prompt.
2. Verify the execution branch starts at the exact clean base.
3. Implement the evaluator independently from the contract.
4. Write your own prereveal tests derived only from the normative contract. Include at least:
   - valid recursive lineage;
   - missing dependency;
   - cycle;
   - producer ceiling;
   - nonconferring basis;
   - source mismatch;
   - comparison narrowness;
   - embedding/scope preservation;
   - authorized versus bare resolution;
   - composition;
   - decision/action separation;
   - execution/verification separation;
   - exact evidence preservation.
5. Do not attempt to predict hidden evaluator cases.
6. Commit the implementation and prereveal tests.
7. Create a freeze receipt containing:
   - clean base;
   - aperture commit and allowed blob identities;
   - implementation commit;
   - implementation file Git blob and SHA-256;
   - test files and hashes;
   - exact tree;
   - test command/results;
   - contamination declaration;
   - deviations/uncertainties;
   - the marker below.

Required marker:

`FRESH_CONTRACT_E_AUTHORITY_CHAIN_RC1_FROZEN_BEFORE_REVEAL`

8. After the freeze commit exists, do not edit the frozen implementation or prereveal tests.

## Stop/reveal rule

Before the immutable implementation freeze, the post-freeze reveal packet and sealed evaluator are forbidden.

After the freeze is durable, continue without asking for routine confirmation by reading only the exact post-freeze reveal packet commit/path/blob supplied in the launch prompt. Treat that packet as the complete authority for the remainder of the run.

Do not repair the frozen implementation after seeing hidden cases/reference behavior and count the repaired result as independent agreement.

## Terminal disposition

The post-freeze packet will define exact scoring and terminal-state mechanics.

No result from this reproduction authorizes production Contract E, merge, release, CAL production changes, Decision Engine changes, Authorization, or execution.
