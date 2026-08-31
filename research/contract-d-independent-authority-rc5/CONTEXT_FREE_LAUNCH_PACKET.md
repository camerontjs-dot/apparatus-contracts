# Contract D RC5 — Fresh Independent Consumption Reproduction v1

## CONTEXT-FREE REQUIRED

Use this packet as the complete task input.

Do **not** retrieve, import, infer from, or ask for surrounding CAL Pipeline conversations, previous Contract D discussions, prior clean-room runs, prior RC3/RC4 reproduction results, adversarial-harness results, promotion decisions, user memory, project summaries, or other historical reasoning.

Information isolation is part of the validity claim.

The objective is to discover whether the frozen **public Contract D RC5 authority** is independently recoverable. Do not try to make the candidate pass. Preserve disagreement, ambiguity, evaluator weakness, and failure.

This task does not authorize production promotion, release, merge, Authorization behavior, execution behavior, or downstream mutation.

---

## 1. Exact clean execution workspace

Repository:

`camerontjs-dot/research-scaffold-harness`

Fresh execution branch:

`research/contract-d-rc5-fresh-reproduction-v1`

Required initial branch head:

`548bfa81f65290eda15af658f647497679b840ef`

Required initial tree:

`191976638bbf8b7153e3f2c94945a2f15cd640ad`

Before reading any Contract D authority file:

1. verify the branch head and tree exactly;
2. verify that the branch contains no `contract-d` implementation/reproduction material;
3. create a durable access ledger under:
   `research/contract-d-rc5-fresh-reproduction-v1/ACCESS_LEDGER.md`;
4. record every repository/path intentionally accessed after the clean-base check.

If the initial branch head or tree differs, stop and report `CLEAN_BASE_MISMATCH`.

---

## 2. Frozen candidate identity

Authoritative repository:

`camerontjs-dot/apparatus-contracts`

Frozen candidate commit:

`f0f7a9684cf114159ca1cfe1c9f11b626a07e6c8`

Frozen candidate subtree:

`f5db874db39c0c3bf863f4ba2cc1a3597369f3bf`

Candidate research token:

`0.3.0-rc5`

Do not use a moving branch as authority.

---

## 3. Pre-freeze information aperture

Before freezing your independent implementation, you may read **only** the following candidate files at the exact frozen candidate commit:

1. `research/contract-d-independent-authority-rc5/candidate/SPEC.md`
   - blob `57fa4ca59efced5e35115551b1aa57dbbc7f6b2c`
2. `research/contract-d-independent-authority-rc5/candidate/schema.json`
   - blob `fe4e74464a53f581d52baed02257dd9452e6bfe3`
3. `research/contract-d-independent-authority-rc5/candidate/effect-registry.json`
   - blob `53df222ca439248a44029e02a662825235db892f`
4. `research/contract-d-independent-authority-rc5/candidate/fixtures/valid.json`
   - blob `f03b16f41f119a8a485e0f7ac3dac30f509c40b9`
5. `research/contract-d-independent-authority-rc5/candidate/fixtures/invalid.json`
   - blob `8c3fd3370d7f96a7cb162d8acfeacb7b189b4d86`
6. `research/contract-d-independent-authority-rc5/candidate/conformance-cases.json`
   - blob `29825bfa89b2b91bfa9e457c001e2c869a3649a4`

You may use the publicly specified **RFC 8785 / JSON Canonicalization Scheme** as a normative external standard because the frozen SPEC explicitly incorporates it. If you consult it, record the exact source in the access ledger. Do not use web search beyond resolving the official standard or language/runtime documentation needed to implement that standard.

You may use ordinary language/runtime standard-library documentation. Record any nontrivial external source in the ledger.

### Explicitly forbidden before implementation freeze

Do not access:

- `contract_d_core.py`;
- `contract_d_validate.py`;
- `contract_d_consume.py`;
- `candidate/tests/**`;
- `candidate/requirements.txt`;
- `RC5_CHANGE_NOTE.md`;
- any Contract D RC3 or RC4 candidate/implementation/test/reproduction material;
- any prior Contract D final record;
- the Contract D adversarial harness, its PR, runs, artifacts, issues, or reports;
- Decision Engine Contract D implementation/producer code;
- Contract D promotion/EDR issues;
- broad repository search for Contract D implementation details;
- surrounding ChatGPT/project context, user memory, summaries, or prior-thread retrieval.

If denied material is observed accidentally, record exactly what was exposed and stop before counting the result as clean-room evidence unless the contamination is demonstrably non-answer-bearing.

---

## 4. Independent implementation objective

Build a fresh implementation from the allowed public authority only.

It must independently implement enough Contract D RC5 behavior to test at least:

- structural validation and exact-version behavior;
- interoperable finite-JSON validation;
- Unicode-scalar validity;
- deterministic container-depth handling;
- RFC 8785/JCS canonicalization plus Contract-D trailing LF framing;
- safe-default normalization for the registered effect vocabulary;
- semantic authority projection and `semantic_identity`;
- applicability binding for upstream authority, policy, target, requested operation, and explicitly supplied requested effect parameters;
- completed CLEAR, completed HOLD, failed evaluation, non-applicability, and cannot-establish outcomes;
- malformed applicability-expectation handling;
- Authorization/non-authority metadata firewall.

Prefer an implementation strategy that is genuinely independent rather than a transliteration of presumed reference code. A different language/runtime is welcome if practical, but not mandatory.

Do not inspect hidden/reference behavior to decide architecture or edge-case outputs.

---

## 5. Independent tests before reveal

Create your own tests from the public authority. Include positive, negative, sensitivity, invariance, and metamorphic controls.

Your prereveal suite must include, at minimum:

### Decision semantics

- exact-version acceptance and future/unknown-version rejection;
- source-audit CLEAR;
- citation-use CLEAR;
- task-dispatch CLEAR;
- completed HOLD distinct from failure;
- evaluation failure distinct from HOLD;
- wrong requested operation for CLEAR and HOLD;
- upstream, policy, and target substitution/replay;
- absent/empty/explicit requested effect parameters;
- metadata changes do not change semantic identity;
- Authorization-like data cannot become Decision authority.

### RC5 hardening semantics

- valid depths below the normative maximum;
- exact boundary behavior at depth 128 and rejection beyond it;
- self-cycle and mutual-cycle rejection;
- shared-but-acyclic structure acceptance;
- invalid UTF-8 and duplicate-key rejection at byte ingress;
- non-finite values rejected;
- unpaired Unicode surrogate rejection;
- non-BMP key ordering / canonicalization case;
- negative zero canonicalization;
- exponent and precision-edge number cases relevant to RFC 8785;
- unsafe or precision-losing integer-form token rejection;
- at least one valid canonical out-of-safe-integer RFC-8785 number round trip if the standard permits it;
- malformed expectation shapes: missing key, extra key, wrong type, malformed target hash, host-only/non-finite requested parameter;
- controlled fail-closed behavior rather than raw runtime recursion/encoding/canonicalizer exceptions for inputs inside the declared RC5 processing domain.

You may add more tests when they are motivated by the public authority, but do not use hidden expected outputs.

---

## 6. Mandatory pre-reveal freeze

Before any hidden/reference implementation, tests, or expected differential results are revealed:

1. finish the independent implementation;
2. finish the independent tests;
3. run the prereveal suite;
4. preserve failures rather than fixing them from hidden behavior;
5. commit all prereveal work;
6. record a freeze receipt at:
   `research/contract-d-rc5-fresh-reproduction-v1/FREEZE_RECEIPT.md`.

The freeze receipt must contain:

- clean base commit/tree;
- exact allowed authority commit/subtree and public blob identities;
- access-ledger path and contamination status;
- independent implementation path(s) and blob SHA(s);
- independent test path(s) and blob SHA(s);
- freeze commit SHA;
- freeze tree SHA;
- exact local/hosted prereveal test result;
- explicit statement that denied reference material was not intentionally accessed;
- unresolved prereveal uncertainties or predicted ambiguity, if any.

After the freeze commit, do not modify the frozen independent implementation or frozen prereveal tests and later count the modified version as independent agreement.

### Stop point

Once the freeze receipt is committed, stop and report only:

- `PRE_REVEAL_FREEZE_COMPLETE` or the applicable blocker;
- freeze commit;
- freeze tree;
- implementation/test blob identities;
- prereveal test result;
- contamination status;
- unresolved prereveal uncertainties.

Do not reveal or search for the reference implementation yourself. Wait for an explicit post-freeze reveal authorization packet.

---

## 7. Scientific disposition is not production authority

Even a perfect independent result later establishes only bounded reproducibility/conformance evidence for this frozen research candidate.

It does not authorize:

- Contract D `1.0.0` production promotion or release;
- actor approval/delegation/autonomy semantics;
- operational Authorization;
- execution permission or occurrence;
- MainFrame/operator mutation;
- correctness of upstream epistemic judgments;
- arbitrary future Contract D versions, producers, consumers, transports, or resource bounds.

Preserve that boundary in every record.