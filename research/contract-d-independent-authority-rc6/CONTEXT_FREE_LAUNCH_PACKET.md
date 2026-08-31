# Contract D RC6 — Fresh Independent Consumption Reproduction v1

## CONTEXT-FREE REQUIRED

Use this packet as the complete task input.

Do **not** retrieve, import, infer from, or ask for surrounding CAL Pipeline conversations, previous Contract D discussions, prior clean-room runs, RC3/RC4/RC5 reproduction results, adversarial-harness results, promotion decisions, user memory, project summaries, or other historical reasoning.

Information isolation is part of the validity claim.

The objective is to discover whether the frozen **public Contract D RC6 authority** is independently recoverable after the smallest public clarification prompted by the terminal RC5 ambiguity. Do not try to make the candidate pass. Preserve disagreement, ambiguity, evaluator weakness, and failure.

This task does not authorize production promotion, release, merge, Authorization behavior, execution behavior, or downstream mutation.

---

## 1. Exact clean execution workspace

Repository:

`camerontjs-dot/research-scaffold-harness`

Fresh execution branch:

`research/contract-d-rc6-fresh-reproduction-v1`

Required initial branch head:

`548bfa81f65290eda15af658f647497679b840ef`

Required initial tree:

`191976638bbf8b7153e3f2c94945a2f15cd640ad`

Before reading any Contract D authority file:

1. verify the branch ref resolves exactly to the required head;
2. verify that commit has exactly the required tree;
3. inspect only that exact tree for path names and verify it contains no `contract-d` implementation/reproduction material;
4. create a durable access ledger under:
   `research/contract-d-rc6-fresh-reproduction-v1/ACCESS_LEDGER.md`;
5. record every repository/path intentionally accessed after the clean-base check.

Prefer the exact branch-ref endpoint or exact commit/tree endpoints. Do **not** enumerate repository branches merely to verify this branch. If the exact branch ref cannot be verified without branch-list enumeration, stop and report `CLEAN_BASE_VERIFICATION_BLOCKED` rather than exposing prior reproduction branch metadata.

If the initial branch head or tree differs, stop and report `CLEAN_BASE_MISMATCH`.

---

## 2. Frozen candidate identity

Authoritative repository:

`camerontjs-dot/apparatus-contracts`

Frozen candidate commit:

`bb656fc50806c344fda1ddeaf08a9878f5cb460e`

Frozen candidate subtree:

`5151e2c30235784d4ae594db454ac24c1e3868b4`

Candidate research token:

`0.3.0-rc6`

Do not use a moving branch as authority.

---

## 3. Pre-freeze information aperture

Before freezing your independent implementation, you may read **only** the following public authority files at the exact immutable identities below.

### RC6 authority

1. `research/contract-d-independent-authority-rc6/candidate/SPEC.md`
   - at candidate commit `bb656fc50806c344fda1ddeaf08a9878f5cb460e`
   - blob `6ff21ae57b4ae57f1d76ba34c41052b7966df7c5`
2. `research/contract-d-independent-authority-rc6/candidate/schema.json`
   - blob `c7c9f6b7a5874e08cbe3b3ce06c126a2b889e900`
3. `research/contract-d-independent-authority-rc6/candidate/effect-registry.json`
   - blob `53df222ca439248a44029e02a662825235db892f`
4. `research/contract-d-independent-authority-rc6/candidate/fixtures/valid.json`
   - blob `14c9259ce327f6a52f4a0d5e14260c0f92ad5fa2`
5. `research/contract-d-independent-authority-rc6/candidate/fixtures/invalid.json`
   - blob `08b69594e94cae6573e2afd882ef78d9c70629dc`
6. `research/contract-d-independent-authority-rc6/candidate/conformance-cases.json`
   - blob `29825bfa89b2b91bfa9e457c001e2c869a3649a4`

### Explicitly incorporated inherited public authority

RC6's public SPEC normatively incorporates the complete RC5 public SPEC except where RC6 explicitly replaces it. Therefore you may also read exactly:

7. `research/contract-d-independent-authority-rc5/candidate/SPEC.md`
   - candidate commit `f0f7a9684cf114159ca1cfe1c9f11b626a07e6c8`
   - blob `57fa4ca59efced5e35115551b1aa57dbbc7f6b2c`

This inherited SPEC is public authority, not prior reproduction evidence. Do not read any other RC5 file prereveal.

You may use the publicly specified **RFC 8785 / JSON Canonicalization Scheme** as a normative external standard because the inherited public SPEC incorporates it. If consulted, record the exact source in the access ledger. Do not use web search beyond resolving the official standard or ordinary language/runtime documentation required to implement it.

You may use ordinary language/runtime standard-library documentation. Record nontrivial external sources in the ledger.

### Explicitly forbidden before implementation freeze

Do not access:

- `research/contract-d-independent-authority-rc6/RC6_CHANGE_NOTE.md`;
- RC6 `contract_d_core.py`;
- RC6 `contract_d_validate.py`;
- RC6 `contract_d_consume.py`;
- RC6 `candidate/tests/**`;
- RC6 `candidate/requirements.txt`;
- any RC5 file other than the exact public SPEC explicitly authorized above;
- any RC3/RC4 candidate/implementation/test/reproduction material;
- any prior Contract D final record, including RC5;
- the Contract D adversarial harness, its PR, runs, artifacts, issues, or reports;
- Decision Engine Contract D implementation/producer code;
- Contract D promotion/EDR issues;
- broad repository search for Contract D implementation details;
- surrounding ChatGPT/project context, user memory, summaries, or prior-thread retrieval.

If denied material is observed accidentally, record exactly what was exposed and stop before counting the result as clean-room evidence unless the exposure is demonstrably non-answer-bearing.

---

## 4. Independent implementation objective

Build a fresh implementation from the allowed public authority only.

It must independently implement enough Contract D RC6 behavior to test at least:

- structural validation and exact-version behavior;
- interoperable finite-JSON validation;
- Unicode-scalar validity;
- deterministic container-depth handling;
- RFC 8785/JCS canonicalization plus Contract-D trailing-LF framing;
- registered effect validation and safe-default normalization;
- the RC6 total normalized registered-effect shape;
- semantic authority projection and `semantic_identity`;
- applicability binding for upstream authority, policy, target, requested operation, and explicitly supplied requested effect parameters;
- completed CLEAR, completed HOLD, failed evaluation, non-applicability, and cannot-establish outcomes;
- malformed applicability-expectation handling;
- Authorization/non-authority metadata firewall.

The RC6 clarification is specifically part of the independence question: the implementation must derive from public authority whether normalized effects with empty parameter schemas contain an explicit empty `params` object and how that representation participates in semantic identity. Do not import that answer from prior reproduction history.

Prefer an implementation strategy genuinely independent from the Python reference. A different language/runtime is welcome if practical but is not mandatory.

Do not inspect hidden/reference behavior to decide architecture or edge-case outputs.

---

## 5. Independent tests before reveal

Create your own tests from public authority. Include positive, negative, sensitivity, invariance, and metamorphic controls.

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

### RC5 inherited hardening semantics

- valid depths below the normative maximum;
- exact depth-128 boundary and rejection beyond it;
- self-cycle and mutual-cycle rejection;
- shared-but-acyclic structure acceptance;
- invalid UTF-8 and duplicate-key rejection at byte ingress;
- non-finite values rejected;
- unpaired Unicode surrogate rejection;
- non-BMP key ordering/canonicalization;
- negative zero canonicalization;
- exponent and precision-edge number cases relevant to RFC 8785;
- unsafe or precision-losing integer-form token rejection;
- controlled fail-closed behavior rather than raw runtime recursion/encoding/canonicalizer exceptions inside the declared processing domain.

### RC6 clarification controls

For both `knowledge.cite_as_evidence@1` and `task.dispatch@1`:

- stored effect with omitted `params`;
- stored effect with explicit `params: {}`;
- both normalize to the same total registered-effect object;
- normalized effect has exactly `type`, `version`, and `params`;
- normalized `params` is exactly `{}`;
- semantic projection contains that exact normalized effect;
- omission versus explicit `{}` yields identical `semantic_identity`.

For `knowledge.add_verified_tag@1`, verify the inherited default behavior remains stable and explicit `scope: object` remains distinct.

Also verify that the RC6 stored-effect clarification does **not** inject registry defaults or synthetic keys into the external requested-parameter constraint object.

You may add more tests motivated by public authority, but do not use hidden expected outputs.

---

## 6. Mandatory pre-reveal freeze

Before any hidden/reference implementation, tests, dependency file, change note, prior result, or expected differential outputs are revealed:

1. finish the independent implementation;
2. finish the independent tests;
3. run the prereveal suite;
4. preserve failures rather than fixing them from hidden behavior;
5. commit all prereveal implementation/test work;
6. record the immutable implementation/test freeze commit and tree;
7. commit a durable freeze receipt afterward at:
   `research/contract-d-rc6-fresh-reproduction-v1/FREEZE_RECEIPT.md`.

The receipt may be committed immediately after the immutable implementation/test freeze so it can name that already-frozen commit/tree. It must not modify the frozen implementation or prereveal tests.

The freeze receipt must contain:

- clean base commit/tree;
- exact allowed authority commit/subtree and all public blob identities;
- access-ledger path and contamination status;
- independent implementation path(s) and blob SHA(s);
- independent test path(s) and blob SHA(s);
- immutable implementation/test freeze commit SHA;
- freeze tree SHA;
- receipt commit SHA if known after creation;
- exact local/hosted prereveal test result;
- explicit statement that denied reference material was not intentionally accessed;
- unresolved prereveal uncertainties or predicted ambiguity, if any.

After the implementation/test freeze commit, do not modify those frozen files and later count the modified version as independent agreement.

### Stop point

Once the freeze receipt is committed, stop and report only:

- `PRE_REVEAL_FREEZE_COMPLETE` or the applicable blocker;
- immutable implementation/test freeze commit;
- freeze tree;
- durable receipt commit;
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