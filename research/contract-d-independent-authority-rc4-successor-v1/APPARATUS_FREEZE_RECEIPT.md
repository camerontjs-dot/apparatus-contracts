# Contract D RC4 Successor v1 — Apparatus Freeze Receipt

## Status

Research apparatus successor only. This record does not authorize production promotion, release, Authorization behavior, execution, or downstream action.

## Purpose

Freeze the smallest successor apparatus after an authority-relevant finite-JSON fail-closed defect was observed in the prior frozen reference implementation. The public Contract D RC4 authority is intentionally unchanged byte-for-byte; only the hidden reference implementation and its regression tests are changed.

The Contract D semantic version token remains `0.3.0-rc4` because no public authority semantics, schema, effect registry, fixture corpus, conformance case, producer representation, or consumer outcome vocabulary was changed.

## Frozen identities

Repository: `camerontjs-dot/apparatus-contracts`

Successor branch: `research/contract-d-independent-authority-rc4-successor-v1`

Prior frozen RC4 apparatus commit: `ca9302243ed99e69c603d82b3c9abd424a5bb38a`

Successor frozen candidate commit: `fd6923115116b0ced0f9feb5c005099d2e51ea88`

Successor root tree: `a9ac54a04781c8d8f7aac59407a4cc3c4ab38e02`

Successor candidate subtree: `fe449f9ec27eeddb434276ded375f9dc16b48e29`

Fixture corpus tree: `3977ba5b9a92c8b4aa10385408ec59cd7d8ec2a0`

## Public authority blobs — unchanged

- `research/contract-d-independent-authority-rc4/candidate/SPEC.md`: `42a9819651ab41efdb154240eab4f7d808887cd6`
- `research/contract-d-independent-authority-rc4/candidate/schema.json`: `b17183038b75f3ee00804e63c2d9b8d7da476f2e`
- `research/contract-d-independent-authority-rc4/candidate/effect-registry.json`: `53df222ca439248a44029e02a662825235db892f`
- `research/contract-d-independent-authority-rc4/candidate/fixtures/valid.json`: `f40364a4b0a4e02e60fc08f8d0038ad0cb531e58`
- `research/contract-d-independent-authority-rc4/candidate/fixtures/invalid.json`: `74ec69e79c8299d7e9d9ade6e19ee5a42424a7fc`
- `research/contract-d-independent-authority-rc4/candidate/conformance-cases.json`: `29825bfa89b2b91bfa9e457c001e2c869a3649a4`

## Hidden reference blobs

- `research/contract-d-independent-authority-rc4/candidate/contract_d_core.py`: `589e3f1c31a21d305402e5750605d25be682a336`
- `research/contract-d-independent-authority-rc4/candidate/contract_d_validate.py`: `d9d621df1e817adbb5468be25ef65272c457e8cc`
- `research/contract-d-independent-authority-rc4/candidate/contract_d_consume.py`: `ad5126922ea4dd8a38df6c08f53e3bc687f2c4d4`
- `research/contract-d-independent-authority-rc4/candidate/tests/test_rc4.py`: `8bece62cc9d4734af0f6ebee75bb39a0221ce397`

## Exact bounded change

`contract_d_core.py` now tracks active recursive container identities while validating decoded host-language objects. A list/dict encountered again on the active traversal path fails closed with Contract D error code `non_json_value` and detail `cyclic_container`.

The active set is path-scoped rather than global, so shared but acyclic object identity remains valid and serializable.

The reference test suite adds three controls:

1. self-referential decoded container fails closed and `consume` returns `cannot_establish`;
2. mutually recursive decoded containers fail closed;
3. shared-but-acyclic decoded containers remain valid and authority-invariant.

No public authority file changed.

## Hosted receipt

Workflow: `Contract D RC4 research conformance`

Workflow blob on successor: `7f3c960ed6e34237c288fa4047c940460eab939e`

Run: `33345161102`

Job: `99347764398`

Exact tested head: `fd6923115116b0ced0f9feb5c005099d2e51ea88`

Exact command:

`python -m pytest -q research/contract-d-independent-authority-rc4/candidate/tests/test_rc4.py`

Observed result:

`27 passed in 0.06s`

Conclusion: `success`

## Clean-room successor bootstrap

Implementation repository: `camerontjs-dot/research-scaffold-harness`

Clean base: `548bfa81f65290eda15af658f647497679b840ef`

Pre-created successor branch: `research/contract-d-rc4-fresh-reproduction-v2`

The branch was verified by ref-only Git surface to point exactly to the clean base before launch-packet creation.

## Experimental posture

The next run must be context-free. The prior failure, this receipt, prior independent implementation, prior predictions, prior differential results, prior PR/workflow narrative, and all prior Contract D reproduction branches are answer-bearing and must remain unavailable before the new independent freeze.

The public RC4 authority itself remains the only Contract D semantic input before freeze.

## Smallest authorized next step

Execute the immutable Context-Free successor launch packet from a new isolated thread. Do not modify this frozen candidate subtree during that execution.
