# Contract E Authority-Chain Fresh Independent Reproduction RC1 — Post-Freeze Reveal Packet

## Classification

POST-FREEZE REVEAL AUTHORITY ONLY.

This packet is forbidden until the fresh implementation and prereveal tests have been durably frozen with the exact marker:

`FRESH_CONTRACT_E_AUTHORITY_CHAIN_RC1_FROZEN_BEFORE_REVEAL`

This packet does not authorize modification of the frozen implementation or prereveal tests.

## Exact reproduction identity

Fresh implementation repository:

`camerontjs-dot/research-scaffold-harness`

Clean base:

`548bfa81f65290eda15af658f647497679b840ef`

Execution branch:

`research/contract-e-authority-chain-fresh-reproduction-rc1-20260901`

Implementation:

`research/contract_e_authority_chain_fresh_rc1/authority_chain.py`

Prereveal tests:

`research/contract_e_authority_chain_fresh_rc1/test_authority_chain.py`

Freeze receipt:

`research/contract_e_authority_chain_fresh_rc1/FREEZE_RECEIPT.json`

Frozen pre-reveal aperture head:

`da3f7fd2664f9037452ca001b3c816a73ace79d7`

## Preconditions before reveal

Do not continue unless all are true:

1. the execution branch descends from the exact clean base;
2. the implementation and prereveal test file exist;
3. the implementation and prereveal tests are committed together or in a fixed pre-reveal implementation commit;
4. prereveal tests have passed without access to this packet or the sealed evaluator;
5. `FREEZE_RECEIPT.json` exists in a later metadata-only commit and contains exactly:

```json
{
  "schema": "contract-e-authority-chain-fresh-rc1-freeze-receipt-v1",
  "marker": "FRESH_CONTRACT_E_AUTHORITY_CHAIN_RC1_FROZEN_BEFORE_REVEAL",
  "clean_base": "548bfa81f65290eda15af658f647497679b840ef",
  "aperture_head": "da3f7fd2664f9037452ca001b3c816a73ace79d7",
  "aperture_contract_blob": "9a82515391beb8ca57fc5ab861c5c389b7750914",
  "aperture_contract_sha256": "f012826c1f2b54b534ddace6a38be270e5bd94bcf0fc539f024bcb12c62bf381",
  "aperture_bootstrap_blob": "ed59344c6471404d49bba3f9c4a5e362f875976e",
  "aperture_bootstrap_sha256": "7cf083daff12b05a08c1d04f4edc259b2e673ddf723e348b794ba996217a4372",
  "implementation_commit": "<exact implementation-and-tests commit>",
  "implementation_path": "research/contract_e_authority_chain_fresh_rc1/authority_chain.py",
  "implementation_blob": "<Git blob at implementation_commit>",
  "implementation_sha256": "<SHA-256 of frozen implementation bytes>",
  "test_path": "research/contract_e_authority_chain_fresh_rc1/test_authority_chain.py",
  "test_blob": "<Git blob at implementation_commit>",
  "test_sha256": "<SHA-256 of frozen test bytes>",
  "freeze_tree": "<tree of implementation_commit>",
  "prereveal_test_command": "python research/contract_e_authority_chain_fresh_rc1/test_authority_chain.py",
  "prereveal_test_result": "PASS",
  "contamination_status": "CLEAN_PRE_FREEZE_APERTURE",
  "deviations": [],
  "uncertainties": []
}
```

`deviations` and `uncertainties` may be non-empty, but they must be explicit arrays. Do not hide inconvenient prereveal observations.

6. the freeze receipt commit itself does not modify the implementation or prereveal test bytes.

If these preconditions are not satisfied, do not reveal the evaluator. Correct only prereveal bookkeeping while preserving the implementation/test freeze, or stop and report the exact blocker.

## Post-freeze information aperture

After the immutable freeze only, you are authorized to read exactly the following additional authority.

Repository:

`camerontjs-dot/apparatus-contracts`

Sealed evaluator final seal commit:

`396ffbb07d403032a45545d696046466a9ed2561`

Authorized sealed paths:

- `sealed/contract-e-authority-chain-fresh-rc1/reference.py`
  - blob `25cec740262b76738ccd9baeac964dc460ac4652`
  - SHA-256 `f3a06ddb73020da4879605a0fe75947c32a9b8d28cac6d6cbf1cc209622df25a`
- `sealed/contract-e-authority-chain-fresh-rc1/sealed_cases.py`
  - blob `4aef3e0673b74e3a681222ec395e2c47f880ebd9`
  - SHA-256 `faf7c03714f66871088e65c56d71181f6f3d3f15b12f355fd45916dd8b3f58bb`
- `sealed/contract-e-authority-chain-fresh-rc1/evaluate_fresh.py`
  - blob `d9c36fadef62737302ec800f44dd80fe5f7cd071`
  - SHA-256 `de092bc4d48264c437959dd7dfe9f2335935f70c2999dedbc863e303204426fe`
- `sealed/contract-e-authority-chain-fresh-rc1/EVALUATOR-CONTRACT.md`
  - blob `71b0c4873d4e38245793bc4724acbc93843dc93e`
  - SHA-256 `317f89f2d59e2059d686737d2d4ddbc65119ea3b9732fa11ca3383ce4c317691`
- `sealed/contract-e-authority-chain-fresh-rc1/qualification/QUALIFICATION.json`
  - blob `d89c1a5387b567dc2eaefb1c0be1aec56e0fc9a8`
- `sealed/contract-e-authority-chain-fresh-rc1/qualification/FINAL_SEAL_RECEIPT.json`

Accepted sealed qualification:

- run `33467464302`
- evidence commit `f8c71038f48e027ee956105f0c11b040fd78da24`
- artifact `9785351749`
- artifact digest `sha256:8b886e4445f47c6a63b1fefbb8e54b29600609b988ea81c3d68b034fc95af6de`
- 94 hidden cases
- 94/94 exact reference matches
- 30 expected positive / 64 expected negative
- 13 metamorphic pairs
- evaluator qualification failures: none

The final seal commit is metadata-only after the accepted evaluator evidence commit. The evaluator files above are unchanged between `f8c71038…` and `396ffbb…`.

The sealed evaluator history preserves four prerelease apparatus deviations before the accepted run. They occurred before any fresh implementation existed and do not alter the clean-room aperture. Do not erase them or reinterpret them as fresh-implementation evidence.

## Exact post-reveal workflow authority

Reveal-branch workflow template:

Repository:

`camerontjs-dot/apparatus-contracts`

Reveal branch:

`research/contract-e-authority-chain-fresh-reveal-rc1-20260901`

Template path:

`docs/research/contract-e/authority-chain-fresh-reproduction-rc1/POST_FREEZE_WORKFLOW.yml`

Template Git blob:

`e7a7c02181d31cff6d8d7981c59dde416874178e`

After reveal, copy that file **byte-for-byte** into the fresh implementation repository as:

`.github/workflows/research-contract-e-authority-chain-fresh-rc1-post-reveal.yml`

Do not redesign the comparison workflow.

Commit only the copied workflow and any Draft-PR metadata/bookkeeping needed for the fresh research record. Do not modify:

- `authority_chain.py`;
- `test_authority_chain.py`;
- the implementation commit;
- the frozen test expectations.

The copied workflow will mechanically:

1. verify the exact freeze receipt;
2. verify the frozen implementation/test blobs and SHA-256 values;
3. prove no post-freeze implementation/test diff exists;
4. rerun the frozen prereveal tests;
5. check out the exact sealed evaluator commit;
6. verify evaluator blobs/hashes and the accepted seal receipt;
7. run the 94-case differential comparison;
8. preserve every mismatch, exception, false permit, false reject, preservation failure, and metamorphic failure;
9. write `RESULTS.json`, `ROWS.json`, `REPORT.md`, `STDOUT.json`, `TERMINAL_RECEIPT.json`, and `TERMINAL_RECORD.md`;
10. upload a workflow artifact;
11. commit only terminal evidence under:
   `research/contract_e_authority_chain_fresh_rc1/post_reveal_results/`.

## Scientific scoring

The sealed evaluator is authoritative for this reproduction's bounded comparison only.

`INDEPENDENT_RECOVERABILITY_SUPPORTED` requires all:

- 94/94 exact contract matches;
- zero false permits;
- zero false rejects;
- zero exceptions;
- exact evidence preservation on 94/94 cases;
- all 13 metamorphic pairs pass.

Its primary research disposition is then:

`SUPPORTED_FOR_PROMOTION`

Anything less after a valid completed comparison yields:

`INDEPENDENT_RECOVERABILITY_FALSIFIED`

with primary research disposition:

`FALSIFIED`

If the exact sealed evaluator or exact copied workflow fails before scientific comparison for an apparatus reason, do not convert that into a scientific pass/fail. Preserve the failure and return:

`INCONCLUSIVE`

Do not alter the evaluator semantics or frozen implementation to rescue the run.

## Required execution posture

- Do not repair the frozen implementation after seeing hidden cases, reference behavior, expected outcomes, or comparison rows.
- Do not add a translation adapter between the frozen implementation and evaluator.
- Do not weaken exact reason matching, preservation matching, or metamorphic scoring.
- Do not discard disagreements or exceptions.
- Do not rerun with modified implementation and call the result independent agreement.
- Do not use surrounding conversation, memory, prior Contract E research, RC0/RC0B code, or other project state to explain away a disagreement.
- If a mismatch looks like an evaluator defect, preserve it as an evaluator challenge and keep the frozen implementation unchanged.

## Draft PR / evidence record

Once the implementation freeze is durable, open or maintain a Draft Research PR in `camerontjs-dot/research-scaffold-harness` from:

`research/contract-e-authority-chain-fresh-reproduction-rc1-20260901`

against `main`.

The PR is an evidence record only. It must remain Draft and unmerged during the experiment.

After the hosted comparison commits terminal evidence, update the PR body with exact:

- clean base;
- aperture head/blobs;
- implementation commit/blob/SHA-256;
- freeze receipt commit;
- sealed evaluator commit;
- accepted sealed qualification run/artifact/digest;
- post-reveal workflow run;
- terminal evidence commit;
- comparison artifact ID/digest;
- scientific state;
- primary research disposition;
- deviations;
- explicit non-authorization.

## Terminal return

Return only after the terminal evidence commit exists.

Report:

- thread state `TERMINAL`;
- primary research disposition;
- scientific state;
- exact immutable implementation/freeze identities;
- evaluator identities;
- accepted comparison run/artifact/digest;
- decisive mismatches if any;
- whether the frozen implementation changed after reveal (`must be false`);
- Draft PR;
- explicit statement that this does not authorize Contract E 1.0.0, production integration, merge, release, Authorization, or execution.

Do not stop for routine intermediate results after reveal. Carry the packet through terminal evidence unless a genuine apparatus blocker prevents scientific comparison.
