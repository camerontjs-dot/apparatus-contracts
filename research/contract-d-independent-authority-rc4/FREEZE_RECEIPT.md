# Contract D RC4 Candidate Freeze Receipt

Status: research-only successor candidate. Not a production release.

## Frozen authority

- repository: camerontjs-dot/apparatus-contracts
- authority commit: ca9302243ed99e69c603d82b3c9abd424a5bb38a
- authority root tree: 6be92acf230feecea62801324a45a3bd47569f5e
- candidate subtree: c337d65321e9b678d5d346dd45aa3673d40100a4
- fixture corpus tree: 3977ba5b9a92c8b4aa10385408ec59cd7d8ec2a0
- version token: 0.3.0-rc4

## Public authority blobs

- candidate/SPEC.md: 42a9819651ab41efdb154240eab4f7d808887cd6
- candidate/schema.json: b17183038b75f3ee00804e63c2d9b8d7da476f2e
- candidate/effect-registry.json: 53df222ca439248a44029e02a662825235db892f
- candidate/fixtures/valid.json: f40364a4b0a4e02e60fc08f8d0038ad0cb531e58
- candidate/fixtures/invalid.json: 74ec69e79c8299d7e9d9ade6e19ee5a42424a7fc
- candidate/conformance-cases.json: 29825bfa89b2b91bfa9e457c001e2c869a3649a4

## Post-freeze reference blobs

- candidate/contract_d_core.py: ec0922c2821d89f24ca521be88725a92118b0ad9
- candidate/contract_d_validate.py: d9d621df1e817adbb5468be25ef65272c457e8cc
- candidate/contract_d_consume.py: ad5126922ea4dd8a38df6c08f53e3bc687f2c4d4
- candidate/tests/test_rc4.py: 56db533665f5205452fad77f1e8309fe5eca57be

## Hosted candidate receipt

GitHub Actions run 33343747118 completed successfully against authority commit ca9302243ed99e69c603d82b3c9abd424a5bb38a.

## Native producer

- repository: camerontjs-dot/decision-engine
- producer commit: e768cedc891fa0d3280dc55f54b578d149019555
- path: research/contract-d-rc4-producer-conformance/emit.mjs
- blob: 96d7856493c498080e3e34366654aeebd14db9f4

## Clean-room implementation surface

- repository: camerontjs-dot/research-scaffold-harness
- clean base: 548bfa81f65290eda15af658f647497679b840ef
- pre-created branch: research/contract-d-rc4-fresh-reproduction

The clean-room branch was created directly from the clean base and must remain at that base until the context-free executor begins.
