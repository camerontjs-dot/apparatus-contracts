# CAL polarity successor downstream Decision D

Disposition: `SUPPORTED_POLARITY_SUCCESSOR_DOWNSTREAM_DECISION_D_CONFORMANCE`

The exact CAL polarity product keeps a negative `MORE_THAN` relation through parent-bound Contract C, the maintained Decision Engine, and the released Contract D 1.0.0 consumer. Inherited PIPE01–PIPE03 keep the same downstream decisions. Their Contract C and Contract D bytes change with the successor producer identity.

## Executed identity

- Qualification head: `6399a866add04bb313fafa57cebc0a40315bbe37`
- Tree: `f8f9fa0c1bec7f9207d1a094f25b1d9ced6dcd10`
- Harness blob: `4ddba0b2deee8ee5e39cc42c7bd1b58d5f79c01e`
- Apparatus base: `c3563cff66d2c85dcbf575c693056e2d8e4563d4`
- CAL product: `64b6c7702696c851057c1cf0b2c105b1c81db543`
- Semantic implementation: `caa0048f8f511ec3c4aa1ce713766f2219a04bc1`
- Contract C candidate: `c183d2d12306ee30c509169a58db55e7430fe8c5`, blob `aeb50dee8d24bda5f62eb879654e80437a50912d`
- Resolver: `292168222f83c67a24190b4846eebe84392e3d04`, blob `b9297ba06beefe1de8488bc25a4c424b0e10e58b`
- RC2: `b42c827acb0a9fe65353354d709add0e27bab307`
- Decision: `cadef9e103edeba32f1247b99d81d5e25175bcd9`
- Contract D 1.0.0: `298a1a0f7b7b6d7712e11200d04faec3e1ca169b`

Hosted run [37158294608](https://github.com/camerontjs-dot/apparatus-contracts/actions/runs/37158294608) succeeded on that head. Artifact `11287000318` has digest `sha256:805251091248d9c6ed43e3a6058ae4186dda502549d9c3089ad3357c116e8b46`. The inner archive is `sha256:4b97cd87d610a07c201a7640060914d046926337e5884c93084e80571443de76`, 697 members, zero hash mismatches. Local and hosted `result.json` are the same bytes: `sha256:462f4d4890ccc074bdf8860860c4a4db63029bbe3d0b448f2106f11d2a4e8f87`.

## Preserved apparatus failures

Run 01, freeze `1d07193b743070f0eb4daa5db2d5d2ca65bb37a3`, harness blob `b506bc4155caf8a8d697470e6d051bee538f6448`, returned `BLOCKED_EXACT_SUBJECT_UNAVAILABLE` before any case. The orchestrator interpreter could not import the preserved constructor (`No module named 'yaml'`). Identity, the wheel, inspect, and clean-environment provenance had already passed.

Run 02, successor `b7912df29b03dfbbf77c7341b74cb3a8fc7b94df`, harness blob `672dde8b49506a08ff37c14affe7d4111525f695`, returned `FALSIFIED_POLARITY_SUCCESSOR_DOWNSTREAM_CONFORMANCE` on PIPE01. Parent `supported`, Decision `clear`, and consumer `candidate_for_authorization` had already matched. The residue diff was only the 40-hex semantic implementation id. I left that evaluator in place and taught the next one to treat exact 40-hex and 64-hex tokens as provenance, while still checking the unchanged recomposition freeze and semantic-source commits directly.

## Cases

| Case | Parent | Decision | D consumer | Successor Contract C |
|---|---|---|---|---|
| PIPE01 | supported | clear | candidate_for_authorization | `sha256:2c00903a09cac91e7ed4a74832b1703dafb45ee5af760a1c141ec652ecf2afb2` |
| PIPE02 | contradicted | hold | hold | `sha256:fc4dd6940cc384301f36deb45a67dbad75d56e8555eb7ade3fce2c4e4c4b0dc8` |
| PIPE03 | not_checkable | hold | hold | `sha256:d23057b7639992c4bbab13f0455500b5a3689da250c489d19775785d377bd87a` |
| POLARITY | contradicted | hold | hold | `sha256:9d38fbeaf267062e9fe06879abad5d07e3aad4dbd39b3fb0e5bb10dbe0ef9e17` |

PIPE01 repeat parent, Contract C, and Contract D bytes matched. PIPE01–PIPE03 Contract A, Evidence Bundler package, and Contract B bundle bytes matched the historical #158 arm. Successor Contract C bytes differed in each inherited case.

The polarity specimen used claim `Alpha had a higher rate than Beta.` and evidence `Alpha did not have a higher rate than Beta.` CAL kept relation `MORE_THAN`, assertion polarity `negative`, categorical relation `REFUTES`, instrument `strict-comparison-polarity-rc0`, and child conclusion `contradicted`, decided from source `S-C1-NEGATE`.

## Negative controls

- Replay substituted PIPE03 child `C1` into PIPE01 and rejected before Contract D stdout. Error `contract_c_validation_failed` / `NATIVE_RESULT_HASH_MISMATCH`. Zero false accepts.
- Structural validation accepted a C1 direction mutation to `LESS_THAN`. Target conformance exited 2. Observed stages stopped at `contract-a-validator`, `target-author`, `structural-weak`, `target-conformance`.
- The predecessor candidate rejected the new producer: `not frozen CAL V1`.
- The successor candidate rejected the predecessor resolver: `resolver mismatch`.
- Successor resolver membership accepted the predecessor semantic implementation. The successor candidate pin still rejected it: `not frozen CAL V1`.
- The predecessor resolver list rejected the new producer: `unknown or ambiguous implementation`.

## What this does not establish

Representative accuracy, promotion acceptance, a public interface or version, merge, release, consumer migration, Contract E, Authorization, and execution are all outside this result. `candidate_for_authorization` is a consumer label. No authorization or execution ran. Old and new Contract C byte identity was not required.

## Next gate

The next V1 gate is independent promotion review and operator acceptance, then a public interface and version decision, successor release lock, release-artifact custody, tag and release, and authorized consumer migration. Fresh blind accuracy is still unestablished. Parent-bound Contract C stays research-only. ERS pending review, Contract E, Authorization, and execution stay separate.
