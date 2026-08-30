# Contract D RC3 Candidate Freeze Receipt

**Freeze label:** `CONTRACT_D_RC3_CANDIDATE_FROZEN_FOR_INDEPENDENT_REPRODUCTION`  
**Freeze status:** research-only candidate, not a Contract D release  
**Freeze declared after:** hosted candidate conformance + native Decision Engine research-producer conformance

## Authority identities

- apparatus-contracts base: `00bdf9546a877f9f6c1d7fd227fd959e1d7aa99e`
- RC3 preregistration commit: `da0397ad0d948051f12e6511333c86168f2f4709`
- RC3 preregistration blob: `caeee206766b2b2055b550fe5b02c8d4a4070a18`
- **RC3 candidate freeze commit: `b24d06caf944facb970df5129ebdd48c21c25eec`**
- freeze commit tree: `0f8f97cba0846679665543800deb787741dc1254`
- candidate subtree: `62fc53527c57a1cf69d1b9f83ea0f738ab95d656`
- candidate version token: `0.3.0-rc3`

The candidate subtree at the freeze commit is immutable for RC3. Any modification to the candidate after this commit is RC4 or another explicitly versioned successor. Post-freeze result/receipt documents on the research branch do not alter the frozen candidate identity.

## Frozen candidate Git object identities

These are GitHub Git object identities. They identify the exact bytes/tree at the freeze commit; they are not presented as independent semantic-correctness evidence.

| Artifact | Git blob/tree identity |
| --- | --- |
| candidate subtree | `62fc53527c57a1cf69d1b9f83ea0f738ab95d656` |
| `SPEC.md` | `a91a9f171a3b5f3241b5970d7c0415e00f0477d7` |
| `schema.json` | `41481aa7941a789534c974ed7b368fddead6ce5a` |
| validator + registry semantics `contract_d_core.py` | `de46bb146b77fb34e721d16a51423ef83d23e675` |
| canonical-byte validator `contract_d_validate.py` | `d9d621df1e817adbb5468be25ef65272c457e8cc` |
| applicability oracle `contract_d_consume.py` | `37b03c8bf3be0ee183ab0369c01ec377a5265e69` |
| typed effect registry `effect-registry.json` | `53df222ca439248a44029e02a662825235db892f` |
| valid fixture corpus `fixtures/valid.json` | `f823936c9945ea551943c40bee1e956faf1d834d` |
| invalid/adversarial corpus `fixtures/invalid.json` | `06c03ebba98d7fb2a1a9b146152cca7f9f085ab6` |
| fixture corpus tree | `a53af5603118679330ec01326a8ed13a70959a9f` |
| consumer conformance cases `conformance-cases.json` | `229f2898f756f9ca078086cfc99d2a6a2edd2a73` |
| adversarial suite `tests/test_rc3.py` | `8aeb2aa2dbcb4042e5286a2dc8aee723327bda39` |
| conformance-test tree | `47dd7993da267958dfcbe768b3c34232859e29fe` |
| hosted RC3 workflow | `6a3623435fc8dd08c41b970c2460d1f85bcff1e7` |

### Requested hash/blob mapping

- spec blob identity: `a91a9f171a3b5f3241b5970d7c0415e00f0477d7`
- schema hash/blob: `41481aa7941a789534c974ed7b368fddead6ce5a`
- validator hash/blobs: `de46bb146b77fb34e721d16a51423ef83d23e675`, `d9d621df1e817adbb5468be25ef65272c457e8cc`
- canonicalizer / semantic-identity hash/blob: `de46bb146b77fb34e721d16a51423ef83d23e675`
- effect-registry hash/blob: `53df222ca439248a44029e02a662825235db892f`
- fixture-corpus hash: Git tree `a53af5603118679330ec01326a8ed13a70959a9f`
- conformance-suite hash: Git tree `47dd7993da267958dfcbe768b3c34232859e29fe`, test blob `8aeb2aa2dbcb4042e5286a2dc8aee723327bda39`
- consumer-case hash/blob: `229f2898f756f9ca078086cfc99d2a6a2edd2a73`

## Hosted candidate assurance receipt

Repository: `camerontjs-dot/apparatus-contracts`

- freeze commit under test: `b24d06caf944facb970df5129ebdd48c21c25eec`
- workflow: `Research Contract D RC3 Candidate`
- workflow run: `33323642846`
- job: `99289846820`
- result: `success`
- exact suite result: `30 passed in 0.07s`

The hosted suite covers valid controls, invalid/future machinery, target/upstream/policy substitutions, operation replay, effect parameter defaults/mutations, metadata invariance, Authorization-only invariance, field ablation, weak consumers, canonicalization/duplicate-key behavior, injection at Contract-D-owned surfaces, and the intentionally opaque non-authoritative diagnostics boundary.

## Cross-repository Decision Engine receipt

Repository: `camerontjs-dot/decision-engine`

Research-only producer PR: `#23`  
Base: `ff7a0f63e5f7075b192dff04064b950bf7255ffa`  
Final receipt head: `63b0245b03ea63d0248a5aced83fba6697697598`

Frozen apparatus candidate checked out by SHA in CI:

`b24d06caf944facb970df5129ebdd48c21c25eec`

Decision Engine research emitter:

- commit introducing emitter: `2930163b58d90ce6d5a097ff7ee5bbe4ff79e27b`
- emitter blob: `1745b74a61ba1a3321c52f384a166b7d9d3b0e1c`
- final cross-repo workflow blob: `3400afe7783aae20030f91ee4129636419f774ae`

Final hosted cross-repository run:

- workflow run: `33323789564`
- job: `99290243719`
- result: `success`

### Preserved pre-authority RC2 mismatch

The final cross-repository run first supplied the frozen RC2 native representation, mechanically transcribed from Decision Engine reference `run-rc2.mjs` at fixed reference head `6c1ddb5a6b6b1a5373261e41d64a4baee83e0efb`, blob `f4a722c60766e018131798426cb2fba489efc311`.

Native RC2 result under the frozen RC3 consumer:

`cannot_establish / missing_field`

This is expected negative evidence, not repaired conformance. RC2 uses the pre-authority representation (`contract_version: D-rc2`, no upstream immutable identity, `content_hash`, flat evaluation/disposition fields). RC3 was not changed to accept it.

Classification: **prior research implementation / representation artifact plus authority fields that RC3 now explicitly requires**. It is not counted as an RC3 candidate defect and is not erased from the predecessor record.

### Native research-only RC3 producer result

Without a translation adapter, Decision Engine research head emitted five RC3 objects and the exact frozen apparatus consumer produced:

- source-audit CLEAR: `candidate_for_authorization`
- citation-use CLEAR: `candidate_for_authorization`
- task-dispatch CLEAR: `candidate_for_authorization`
- completed HOLD: `hold`
- Decision evaluation failure: `evaluation_failed`

Recorded semantic identities:

- source audit: `decision:sha256:85bd84dc0fbe36d47cbe6325dfa65fc36ccbbd69aff510055b5891136ecbf4ac`
- citation use: `decision:sha256:f26789dc854d8583f923c4d600e493f910d60c721e861487307d6c64373b6679`
- task dispatch: `decision:sha256:9f389768439368165671360d08d16bc9f72f5768a5c468344ba27e9432b40eaf`
- completed HOLD: `decision:sha256:82460425b646110c11bc659a76230f5e4a88620e634f478fc8fc879e4ba93905`
- evaluation failure: `decision:sha256:6ed6155819124bc5fc205f84b21bc283a21eee1d937cf36aa1fc2d4aaef49cd9`

`candidate_for_authorization` remains an applicability result, not operational Authorization or execution permission.

## Deviations and pre-freeze changes

### Empty parameter-container ablation

The initial implementation hypothesis required an empty `effect.params` container even for effects with no explicit parameter values. Pre-freeze field-ablation testing showed that mandatory container presence added representation without adding authority.

RC3 therefore froze the smaller rule:

- `params` is optional;
- only registry-declared machine-semantic parameters matter;
- declared safe defaults are normalized into semantic identity;
- for `knowledge.add_verified_tag@1`, omitted params, empty params, omitted `scope`, and explicit `scope: claim` share the same machine semantics and semantic identity.

This correction occurred before the candidate freeze and is preserved as a minimality result rather than hidden as implementation cleanup.

### Structural schema versus semantic registry

`schema.json` constrains the common structural envelope. Effect type/version/parameter authority is intentionally enforced by the versioned effect registry plus normative validator rather than duplicated incompletely into JSON Schema. Independent consumers must implement the published registry semantics, not infer effect meaning from the structural schema alone.

## Unresolved questions at freeze

1. A genuinely isolated implementer has not yet reproduced RC3 from the package alone.
2. The three registered effect families are the currently evidenced research set; broader effect coverage is not established.
3. Future version compatibility is intentionally fail-closed and remains to be designed by a later version if needed.
4. The reference Python implementation and hosted suite are systems under test; their mutual agreement does not substitute for the successor independent reproduction.
5. No production Authorization profile/runtime is established by this freeze.

## Freeze interpretation

The frozen candidate has passed the preregistered local/hosted machinery checks and native cross-repository production/consumption check necessary to justify a fresh independent reproduction attempt.

It has **not** passed the future clean-room independent reproduction itself.

No Contract D release, promotion merge, production Decision Engine behavior, production Authorization behavior, or execution authority is created by this receipt.
