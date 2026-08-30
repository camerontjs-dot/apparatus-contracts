# CONTEXT-FREE REQUIRED

# Contract D RC3 — Fresh Independent Consumption Reproduction

Use this packet as the complete task input. Do not import the surrounding CAL Pipeline conversation or other Contract D summaries.

## 1. Exact objective

Independently implement and test the frozen Contract D RC3 consumption authority using only the authorized pre-freeze information aperture below.

Determine whether a competent implementation created from the frozen RC3 apparatus authority alone independently agrees on all authority-relevant behavior and can natively consume Contract D RC3 objects without a bespoke translation adapter.

Do not try to make the reproduction pass. Preserve every disagreement.

This is not authorization to promote Contract D, modify production Decision Engine behavior, modify production Authorization machinery, merge a Contract D release, or execute downstream actions.

## 2. Frozen Contract D authority

Authoritative repository:

`camerontjs-dot/apparatus-contracts`

Frozen RC3 candidate commit:

`b24d06caf944facb970df5129ebdd48c21c25eec`

Frozen candidate subtree:

`62fc53527c57a1cf69d1b9f83ea0f738ab95d656`

Candidate version token:

`0.3.0-rc3`

Pre-freeze source access must be path-and-ref constrained. Do not browse the RC3 research PR, issue narrative, other commits, sibling research files, GitHub search results, or adjacent branches for orientation.

## 3. Durable governance files allowed pre-freeze

Only these durable project governance/protocol files may be used in addition to the frozen Contract D authority below:

- `CONTEXT-FREE-EXECUTION-PROTOCOL(1).md`
- `GITHUB-AND-PR-GOVERNANCE(3).md`
- `EPISTEMIC-RECORD-CONVENTIONS(3).md`
- `PROJECT-STATE-LOCATION-POLICY(3).md`
- `Bounded Continuation and Operator Escalation.txt`

If one is unavailable, do not compensate by importing surrounding project conversation. Continue with the narrower aperture when possible or record `BLOCKED` if the missing file is necessary to preserve execution validity.

## 4. Pre-freeze allowlist

At `camerontjs-dot/apparatus-contracts@b24d06caf944facb970df5129ebdd48c21c25eec`, the executor may open only:

1. `research/contract-d-independent-authority-rc3/candidate/SPEC.md`
   - blob `a91a9f171a3b5f3241b5970d7c0415e00f0477d7`
2. `research/contract-d-independent-authority-rc3/candidate/schema.json`
   - blob `41481aa7941a789534c974ed7b368fddead6ce5a`
3. `research/contract-d-independent-authority-rc3/candidate/effect-registry.json`
   - blob `53df222ca439248a44029e02a662825235db892f`
4. `research/contract-d-independent-authority-rc3/candidate/fixtures/valid.json`
   - blob `f823936c9945ea551943c40bee1e956faf1d834d`
5. `research/contract-d-independent-authority-rc3/candidate/fixtures/invalid.json`
   - blob `06c03ebba98d7fb2a1a9b146152cca7f9f085ab6`
6. `research/contract-d-independent-authority-rc3/candidate/conformance-cases.json`
   - blob `229f2898f756f9ca078086cfc99d2a6a2edd2a73`

Fixture corpus tree:

`a53af5603118679330ec01326a8ed13a70959a9f`

No other apparatus-contracts path is authorized before the independent freeze.

The candidate specification itself is the canonicalization and semantic-identity specification. Do not open the reference canonicalizer/validator implementation before freeze.

## 5. Pre-freeze denylist

Before the independent implementation freeze, do not inspect, search, retrieve, summarize, or use:

### Apparatus reference implementation / answer-bearing RC3 material

- `research/contract-d-independent-authority-rc3/candidate/contract_d_core.py`
- `research/contract-d-independent-authority-rc3/candidate/contract_d_validate.py`
- `research/contract-d-independent-authority-rc3/candidate/contract_d_consume.py`
- `research/contract-d-independent-authority-rc3/candidate/tests/test_rc3.py`
- `research/contract-d-independent-authority-rc3/PREREGISTRATION.md`
- `research/contract-d-independent-authority-rc3/FREEZE_RECEIPT.md`
- `research/contract-d-independent-authority-rc3/RESULTS.md`
- apparatus-contracts PR #24 body/comments/reviews
- apparatus-contracts issue #22 body/comments

### Decision Engine answer-bearing material

- all Contract D `run*.mjs` implementations
- all Contract D RC0/RC1/RC2/RC3 reference outputs beyond the frozen public fixtures expressly allowed above
- Decision Engine PR #19 body/comments/diff/results
- Decision Engine PR #23 body/comments/diff
- `research/contract-d-rc3-producer-conformance/emit.mjs`
- Decision Engine hosted workflow logs/artifacts for RC3

### Prior independent reproduction material

In `camerontjs-dot/research-scaffold-harness`, do not inspect before freeze:

- prior Contract D fresh-reproduction branch/tree;
- prior `contract_d.py`;
- prior tests;
- prior fixtures;
- prior `PREDICTIONS.md`;
- prior field-ablation predictions;
- prior `REFERENCE_COMPARISON.md`;
- prior `RESULTS.md`;
- prior freeze manifest/receipt except for the clean starting base identity explicitly supplied below;
- PR #1 body/comments/diff.

### Conversation/history

Do not use:

- this conversation;
- CAL Pipeline Contract D conversation history;
- summaries of earlier Contract D conclusions;
- GitHub search snippets or PR/issue narrative that reveals prior expected disagreements or answers.

Do not perform repository-wide GitHub search before freeze.

## 6. Required isolated implementation target

Use:

`camerontjs-dot/research-scaffold-harness`

Clean starting commit:

`548bfa81f65290eda15af658f647497679b840ef`

Create a new branch from exactly that commit:

`research/contract-d-rc3-fresh-reproduction`

Create the independent implementation only under a new directory:

`research/contract-d-rc3-fresh-reproduction/`

Do not enumerate or open other repository branches or PRs before freeze. The previous independent Contract D implementation is not present in the supplied base tree and is forbidden material on other refs.

If the target branch already exists with prior work, do not reuse it. Record `BLOCKED` and require a new isolated branch/surface rather than risking contamination.

## 7. Required implementation

From the allowed RC3 specification/schema/registry/fixtures only, independently implement:

- exact-version Contract D parser/validator;
- unknown-field behavior;
- typed effect registry consumption and parameter/default handling;
- deterministic canonicalization;
- semantic authority projection;
- semantic Decision identity;
- independent consumer/applicability evaluation over:
  - expected upstream authority;
  - expected policy;
  - expected target;
  - external requested operation;
  - requested machine-semantic effect parameters.

Do not copy source architecture, function names, error codes, or internal structure from the reference implementation because it is not available before freeze.

Internal architecture and language-level organization need not match the reference.

## 8. Required independent tests before freeze

The independent suite must test at least:

### Positive/state controls

- source-audit/knowledge effect;
- citation-use effect;
- task-dispatch effect;
- completed CLEAR;
- completed HOLD;
- Decision evaluation failure;
- HOLD distinct from evaluation failure.

### Authority sensitivity

Independently mutate and test:

- Contract D version;
- upstream authority kind;
- upstream authority id;
- upstream immutable identity;
- policy id;
- policy version;
- target kind;
- target id;
- target immutable content;
- evaluation state;
- disposition;
- effect type;
- effect version;
- every machine-semantic effect parameter.

### Authority invariance

Mutate without changing Decision semantic identity/applicability authority:

- reason codes;
- explanation;
- diagnostics.

Also demonstrate that external Authorization-only changes such as actor/profile/approval/delegation/context do not modify the Decision object or its semantic identity.

### Replay/substitution

- effect reused for different requested operation;
- Decision used for another target id;
- same id with changed content;
- same id/content under different target kind;
- upstream substitution;
- policy substitution/version substitution.

### Future/unknown

- unknown Contract D version;
- unknown evaluation state;
- unknown disposition;
- unknown effect type;
- unknown effect version;
- unknown effect parameter;
- unknown structural field.

No unknown item may acquire current-version authority.

### Injection

Attempt actor, requested operation, approval, delegation, autonomy, execution permission, execution state, and execution receipt at plausible Contract-D-owned locations.

### Canonicalization/identity

Test key ordering, nested ordering, formatting, duplicate keys, safe-default normalization, metadata mutation, and authority-bearing mutation.

### Evaluator assurance

Construct intentionally weak plausible consumers, at minimum:

- CLEAR/disposition-only;
- target-id-only;
- target consumer ignoring kind/content;
- HOLD/failure collapse;
- reason-text effect inference;
- unknown-effect acceptance;
- policy-blind;
- upstream-blind;
- Decision identity contaminated by Authorization context.

The independent suite must reject those weak controls for the intended invariant.

Do not limit testing to replaying the supplied public fixtures. Generate additional mutation/metamorphic cases from the published rules.

## 9. Freeze point

Freeze the independent implementation, tests, self-generated fixtures/cases, and predictions **before** opening any pre-freeze-denied material.

The freeze must be a Git commit on the isolated branch.

Required pre-reveal freeze receipt:

- starting base commit;
- branch;
- implementation freeze commit and tree;
- exact implementation blob identities;
- exact test blob identities;
- fixture/case tree hashes;
- allowed pre-freeze sources actually opened, with exact refs/blobs;
- statement that denied surfaces were not opened;
- hosted/local test receipt;
- any deviations;
- explicit timestamp/order showing freeze precedes reveal.

After the freeze, do not modify the implementation/tests/fixtures in response to reference behavior. Repairs require a separately versioned successor reproduction.

## 10. Contamination stop rule

If any pre-freeze-denied material is exposed before the implementation freeze:

1. stop the independence claim immediately;
2. record exactly what was exposed and when;
3. freeze/preserve the contamination receipt if useful;
4. do not continue and later relabel the same implementation independent;
5. terminal secondary state is `CONTAMINATED`;
6. use primary research disposition `INCONCLUSIVE` unless the contamination independently establishes another allowed disposition;
7. only start a fresh successor if separately authorized.

## 11. Post-freeze reveal permissions

Only after the independent freeze may the executor reveal the following for comparison.

### Frozen apparatus reference implementation

At `camerontjs-dot/apparatus-contracts@b24d06caf944facb970df5129ebdd48c21c25eec`:

- `research/contract-d-independent-authority-rc3/candidate/contract_d_core.py`
  - blob `de46bb146b77fb34e721d16a51423ef83d23e675`
- `research/contract-d-independent-authority-rc3/candidate/contract_d_validate.py`
  - blob `d9d621df1e817adbb5468be25ef65272c457e8cc`
- `research/contract-d-independent-authority-rc3/candidate/contract_d_consume.py`
  - blob `37b03c8bf3be0ee183ab0369c01ec377a5265e69`
- `research/contract-d-independent-authority-rc3/candidate/tests/test_rc3.py`
  - blob `8aeb2aa2dbcb4042e5286a2dc8aee723327bda39`

### Decision Engine native RC3 producer

At `camerontjs-dot/decision-engine@63b0245b03ea63d0248a5aced83fba6697697598`:

- `research/contract-d-rc3-producer-conformance/emit.mjs`
  - blob `1745b74a61ba1a3321c52f384a166b7d9d3b0e1c`

The frozen Decision Engine producer object must be supplied directly to the frozen independent consumer. Do not insert a bespoke translation adapter.

The final native comparison must include the three clear effect classes, completed HOLD, and evaluation failure.

### Optional historical reveal after primary RC3 comparison

Only after the primary frozen RC3 comparison is complete may the executor inspect the older Decision Engine RC2 representation or prior independent reproduction material for historical diagnosis. Historical material must not be used to repair the frozen independent implementation.

## 12. Frozen successor success criterion

Success requires that the independent implementation created from the authorized RC3 apparatus inputs alone independently agrees on all authority-relevant behavior, including:

- accepted/rejected object classes;
- completed/HOLD/failure distinction;
- target kind/id/content binding;
- upstream authority kind/id/immutable binding;
- policy id/version binding;
- effect type/version/parameter meaning and safe defaults;
- future/unknown handling;
- authority versus explanation distinction;
- canonicalization and semantic identity behavior;
- Authorization-only invariance;
- requested-operation applicability;
- native cross-repository consumption.

Critically:

`Decision Engine -> frozen Contract D RC3 object -> frozen independent consumer`

must work without a bespoke translation adapter.

The independent implementation need not share source code, internal architecture, error-code spelling, or incidental formatting unless canonical serialization itself is normative.

If translation is necessary, preserve the native failure first and classify exactly why.

Do not change the success criterion after observing the result.

## 13. Allowed terminal dispositions

Use exactly one project primary research disposition:

- `SUPPORTED FOR PROMOTION`
- `FALSIFIED`
- `INCONCLUSIVE`
- `SUPERSEDED`

Use a secondary execution/finding label where useful:

- `INDEPENDENT_REPRODUCTION_SUCCEEDED`
- `CROSS_REPOSITORY_CONFORMANCE_FAILED`
- `CONTRACT_AUTHORITY_STILL_UNDERSPECIFIED`
- `REFERENCE_IMPLEMENTATION_DEFECT`
- `CONTAMINATED`
- `BLOCKED`

`SUPPORTED FOR PROMOTION` is justified only if the frozen independent implementation agrees on the bounded authority semantics and native cross-repository consumption with no unresolved authority-relevant disagreement. It still authorizes only a separate minimal promotion review, not a Contract D release in this run.

A disagreement must not be repaired post-reveal and counted as independent conformance.

## 14. Required final receipts

Return to the normal CAL Pipeline project with a durable record containing:

1. repository, branch, base and final SHAs;
2. every pre-freeze source actually opened;
3. implementation/test/fixture freeze identities;
4. local/hosted test receipts;
5. contamination statement;
6. post-freeze sources opened and their identities;
7. native Decision Engine -> RC3 -> independent-consumer result;
8. complete disagreement table;
9. classification of every disagreement;
10. falsifiers triggered/not triggered;
11. primary and secondary terminal disposition;
12. what is explicitly not established;
13. smallest justified next step.

Preserve the frozen implementation even if it disagrees.
