# Contract D RC5 — Post-Freeze Reveal / Differential Comparison v1

## POST-FREEZE REVEAL AUTHORIZED

This packet applies only to the already-frozen fresh independent implementation below.

Do not restart the independent implementation. Do not modify the frozen implementation or prereveal tests and then count the modified result as independent agreement. Preserve every disagreement.

This packet does not authorize production promotion, release, merge, Decision Engine policy changes, Authorization behavior, execution behavior, or downstream mutation.

---

## 1. Verified independent freeze

Repository:

`camerontjs-dot/research-scaffold-harness`

Branch:

`research/contract-d-rc5-fresh-reproduction-v1`

Immutable prereveal freeze:

- freeze commit: `54c78823e289a3d0d490189d1ffafc25d127d585`
- freeze tree: `6a691a691ed56c95616bae1595137daf1a96b86f`
- independent implementation: `research/contract-d-rc5-fresh-reproduction-v1/contract_d_rc5.js`
- implementation blob: `e60d3a15da98e32a732f1860808b8dda7ba7f3ee`
- independent tests: `research/contract-d-rc5-fresh-reproduction-v1/test_contract_d_rc5.js`
- test blob: `102327e348364c62454369d2614ca98ce80d94c5`
- prereveal result: `24 passed, 0 failed, 0 skipped, 0 cancelled, 0 todo`
- runtime: Node.js `v22.16.0`
- contamination status: `NON_ANSWER_BEARING_METADATA_EXPOSURE_ONLY`

Durable freeze receipt commit:

`45115f39b5d07e20fed44c6765a5953593fb5678`

Receipt path:

`research/contract-d-rc5-fresh-reproduction-v1/FREEZE_RECEIPT.md`

The receipt commit was created after the immutable implementation/test freeze so it could name the already-frozen commit/tree. It does not modify the frozen implementation or tests.

Before reveal work, verify the frozen implementation and test blobs still match the identities above. If either differs, stop with `FROZEN_IMPLEMENTATION_MOVED`.

---

## 2. Frozen RC5 reference authority

Authoritative repository:

`camerontjs-dot/apparatus-contracts`

Frozen candidate commit:

`f0f7a9684cf114159ca1cfe1c9f11b626a07e6c8`

Frozen candidate subtree:

`f5db874db39c0c3bf863f4ba2cc1a3597369f3bf`

Research token:

`0.3.0-rc5`

The six public authority files already used prereveal remain authoritative.

---

## 3. Newly authorized post-freeze reveal files

You may now read only the following previously denied reference files at the exact frozen candidate commit:

1. `research/contract-d-independent-authority-rc5/candidate/contract_d_core.py`
   - blob `6c3fbe3e6ac6effe0a4ed66f17145ffd32705edf`
2. `research/contract-d-independent-authority-rc5/candidate/contract_d_validate.py`
   - blob `8cc6d81515d7c5b0a86df163a38d1c12931f897f`
3. `research/contract-d-independent-authority-rc5/candidate/contract_d_consume.py`
   - blob `42536aaac5acd953f150a87891a70e9c194b7aaf`
4. `research/contract-d-independent-authority-rc5/candidate/requirements.txt`
   - blob `9bc3e4b733b2963a79a756a696eeafc92b532634`
5. `research/contract-d-independent-authority-rc5/candidate/tests/test_rc5.py`
   - blob `1f8470b4f6efea5bec3260cd575a626e8242c045`
6. `research/contract-d-independent-authority-rc5/candidate/tests/test_rc5_expectation_hardening.py`
   - blob `9d02b269fe83ba79ded16d154f59fed0267e87c5`
7. `research/contract-d-independent-authority-rc5/candidate/tests/test_rc5_jcs_vectors.py`
   - blob `35a01f918fc4b993e5367d7878e5b11a90bcd428`

You may install the exact dependency declared by `requirements.txt` and an ordinary test runner needed to execute the frozen reference suite.

Do not use a moving branch.

### Still forbidden for this comparison

Do not access unless a later packet explicitly authorizes it:

- `RC5_CHANGE_NOTE.md`;
- prior RC3/RC4 candidates, implementations, tests, or reproduction records;
- the Contract D adversarial harness, its PR/issues/runs/artifacts/reports;
- Contract D promotion/EDR records;
- Decision Engine Contract D producer/reference code;
- surrounding ChatGPT/project context, user memory, summaries, or prior-thread retrieval;
- broad GitHub or web search for Contract D behavior.

The purpose is to compare the already-frozen independent implementation against the exact frozen RC5 reference, not to import the wider research history.

---

## 4. Mandatory reference verification

After reveal:

1. fetch each newly authorized file at the exact candidate commit;
2. verify each Git blob identity against the values above;
3. record the reveal accesses in `ACCESS_LEDGER.md` as post-freeze accesses;
4. materialize the exact reference implementation in a separate temporary directory;
5. run the complete frozen reference test suite without changing the reference files;
6. record the exact runtime, dependency version, command, and pass/fail result.

If any revealed blob differs, stop with `REFERENCE_BLOB_MISMATCH`.

Do not modify the frozen independent JS implementation or frozen prereveal test file.

Post-freeze comparison scripts and reports may be added under a separate path such as:

`research/contract-d-rc5-fresh-reproduction-v1/post_reveal/`

---

## 5. Differential comparison objective

Determine whether the frozen independent implementation and frozen reference implementation agree on the authority-relevant RC5 behavior.

Comparison must include at least:

### A. Structural and state behavior

- valid public fixtures;
- invalid public fixtures;
- exact version handling;
- completed CLEAR;
- completed HOLD;
- failed evaluation;
- effect validation/default normalization;
- upstream/policy/target applicability;
- requested-operation applicability;
- requested-effect-parameter applicability;
- malformed applicability expectations;
- Authorization/non-authoritative metadata firewall.

### B. RC5 interoperability hardening

- UTF-8 ingress;
- duplicate keys;
- Unicode scalar validity;
- self/mutual cycles;
- shared acyclic structures;
- exact depth-128 boundary and rejection beyond it;
- finite/binary64/JCS number-domain behavior;
- unsafe/precision-losing integer behavior;
- RFC 8785/JCS canonicalization, including UTF-16 property ordering;
- negative zero and exponent/precision-edge cases;
- canonical transport bytes where authority-relevant;
- semantic identity.

### C. Frozen prereveal uncertainties

Score these explicitly rather than silently resolving them:

1. Empty-schema registered effects: whether omitted `params` and `{}` normalize identically and whether an empty normalized `params` object is present or absent in the semantic authority projection/identity.
2. Unknown but otherwise JSON-valid externally requested effect-parameter keys: whether the outcome is `not_applicable` or malformed expectation / `cannot_establish`.
3. Candidate-subtree verification posture: the prereveal implementation relied on the packet-pinned subtree identity while independently verifying all six public blobs; do not retroactively classify that deliberate aperture choice as contamination.

If the reference reveals a different answer from the frozen independent prediction, preserve the disagreement. Do not patch the independent implementation before scoring it.

---

## 6. What counts as agreement

Authority-relevant agreement includes:

- acceptance versus controlled rejection;
- consumer outcome (`candidate_for_authorization`, `hold`, `evaluation_failed`, `not_applicable`, `cannot_establish`);
- required applicability distinctions;
- canonical bytes where the contract makes bytes normative;
- semantic identity;
- normalized machine-semantic effect behavior;
- fail-closed behavior inside the declared RC5 processing domain.

Do not require implementation-private exception wording, stack shape, internal helper structure, or other non-authoritative details to match unless the public authority explicitly makes them normative.

Classify every tested difference as exactly one of:

- `AUTHORITY_RELEVANT_DISAGREEMENT`;
- `NON_AUTHORITY_IMPLEMENTATION_VARIANCE`;
- `PUBLIC_AUTHORITY_AMBIGUITY`;
- `OUT_OF_DECLARED_DOMAIN_VARIANCE`;
- `EVALUATOR_OR_HARNESS_DEFECT`;
- `UNKNOWN`.

Do not erase a disagreement merely because the reference is internally consistent.

---

## 7. Differential corpus construction

Use the public fixtures/conformance cases plus cases exposed by the newly revealed reference tests.

You may author post-reveal adapters/runners to feed identical logical cases to the Python reference and frozen Node implementation. These adapters must not alter the frozen implementation semantics.

Where Python and Node host representations differ, compare the Contract-D-level meaning and normative canonical bytes, not incidental host-language object identity.

For generated JCS/number cases, record the generation rule and preserve exact inputs/outputs used in the comparison.

At minimum report:

- total authority-relevant comparisons;
- agreements;
- disagreements;
- ambiguity classifications;
- out-of-domain variances;
- exact case identifiers for every disagreement.

---

## 8. Independent-evidence integrity rule

The frozen independent implementation remains the object being evaluated.

After reveal you may:

- inspect reference code/tests;
- write comparison adapters;
- write differential evaluators;
- write reports;
- run additional cases against the frozen implementation.

You may not:

- edit the frozen independent implementation/test files and count the edited result as prereveal independent agreement;
- discard prereveal predictions after observing the reference;
- tune the comparison corpus only to cases that agree;
- redefine a public authority obligation merely to make the result pass.

If a post-reveal repair would be useful engineering, record it separately as follow-up. It does not change the independent-reproduction score.

---

## 9. Terminal record

Commit a durable final record at:

`research/contract-d-rc5-fresh-reproduction-v1/FINAL_RECORD.md`

The final record must contain:

- verified clean base;
- contamination statement;
- freeze commit/tree and frozen implementation/test blobs;
- reveal packet identity;
- all revealed reference blob identities;
- exact frozen reference-suite result;
- differential comparison counts and classifications;
- explicit treatment of all three prereveal uncertainties;
- preserved failures/deviations;
- exact scope/non-claims;
- smallest justified next step.

Choose the terminal scientific disposition from:

- `SUPPORTED FOR PROMOTION`;
- `FALSIFIED`;
- `INCONCLUSIVE`.

Also record independent-reproduction status as one of:

- `INDEPENDENT_REPRODUCTION_SUCCEEDED`;
- `INDEPENDENT_REPRODUCTION_FAILED`;
- `INDEPENDENT_REPRODUCTION_INCONCLUSIVE`.

A `SUPPORTED FOR PROMOTION` result still does not itself authorize production promotion or release.

If an authority-relevant disagreement is caused by a genuine ambiguity in the public RC5 authority rather than a clearly incorrect independent implementation, preserve that as `PUBLIC_AUTHORITY_AMBIGUITY` and use it when deciding `FALSIFIED` versus `INCONCLUSIVE`.

End the final record with `TERMINAL` once no further reference-comparison step is needed.

---

## 10. Stop point

When the final record is committed, return:

- primary scientific disposition;
- independent-reproduction status;
- terminal state;
- final-record commit;
- final-record blob;
- frozen reference-suite result;
- authority-relevant agreement/disagreement counts;
- the disposition of each prereveal uncertainty;
- any preserved deviation or blocker.

Do not open or merge a production Contract-D PR. Production promotion remains a separate operator/governance decision after this terminal evidence is reconciled.