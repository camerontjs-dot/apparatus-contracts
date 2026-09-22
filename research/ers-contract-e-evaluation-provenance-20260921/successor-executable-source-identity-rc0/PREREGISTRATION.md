# RC6 successor: executable-source identity gate

**Successor experiment ID:** `ERS-EVAL-TIME-PROV-20260922-04`

**Classification:** Draft Research apparatus-integrity successor.

This successor does not change the scientific hypothesis or decisive matrix frozen in apparatus-contracts PR #130. It does not change the receipt-field contract frozen in PR #131 except to add an execution-source identity gate before that receipt preflight may qualify anything.

## Why this successor exists

The PR #132 attempt stopped `INCONCLUSIVE` before Contract E evaluation because the preflight process executed bytes that differed from the preflight blob named in the freeze receipt. The runner worktree bytes also differed from the frozen runner blob.

The recorded 54/54 PASS therefore cannot qualify the frozen candidate.

No scientific control ran. Contract E evaluation count remained zero.

## Preserved authorities

Scientific authority remains:

- apparatus-contracts PR #130
- exact scientific preregistration: `dcdd10355e2f885273d843eef6e345bafca95faa`

Receipt-contract authority remains:

- apparatus-contracts PR #131
- exact receipt-contract preregistration: `077ccf6d386526bda258b3e90bd43e153c4c04c5`

Preserved inconclusive evidence:

- apparatus-contracts PR #132
- exact preserved result head: `f1cd38145ca0a525b35452298360f5dba6b69eb3`
- ERS PR #11

Do not rewrite or rerun the prior frozen candidates in place.

## New property under test before receipt comparison

Before the receipt-consistency preflight may run, establish that the actual executable preflight and runner files are byte-identical to the Git blobs frozen for the successor candidate.

This source-identity gate is outside the scientific PR #130 matrix.

A failure here is a harness-integrity failure, not a scientific result.

## Trust boundary

Do not rely on the candidate Python preflight to establish its own source identity.

Use Git object identity plus a fresh detached checkout as the authority boundary.

The local operator must:

1. create a brand-new detached Git worktree for apparatus-contracts at the exact frozen successor commit;
2. before executing candidate Python, establish externally:
   - detached `HEAD` equals the frozen successor commit;
   - `HEAD^{tree}` equals the frozen successor tree;
   - `git status --porcelain` is empty;
   - the preflight path exists;
   - the runner path exists;
   - `git hash-object <preflight path>` equals the preflight blob frozen in the receipt;
   - `git hash-object <runner path>` equals the runner blob frozen in the receipt;
   - `git rev-parse HEAD:<preflight path>` equals that same preflight blob;
   - `git rev-parse HEAD:<runner path>` equals that same runner blob.
3. record those externally obtained values in an immutable source-identity receipt before Python preflight execution;
4. execute the preflight path from that exact detached checkout;
5. execute the runner path from that exact detached checkout only after the preflight qualifies.

No candidate Python file may be edited, copied from another worktree, patched, regenerated, or executed from an untracked path after the external identity receipt is captured.

If the detached worktree becomes dirty before execution, stop.

## Required source-identity receipt

The successor must preserve a machine-readable `EXECUTABLE_SOURCE_IDENTITY.json` generated before candidate Python execution.

At minimum it must contain:

- successor experiment ID;
- repository;
- detached checkout absolute path;
- frozen source commit;
- observed HEAD;
- frozen source tree;
- observed HEAD tree;
- clean status result;
- preflight relative path;
- frozen preflight blob;
- observed worktree preflight blob via `git hash-object`;
- observed commit-path preflight blob via `git rev-parse HEAD:<path>`;
- runner relative path;
- frozen runner blob;
- observed worktree runner blob via `git hash-object`;
- observed commit-path runner blob via `git rev-parse HEAD:<path>`;
- timestamp;
- explicit `candidate_python_executed_before_identity_gate: false`.

All four blob comparisons must agree exactly.

The external identity gate must complete before receipt-preflight output exists.

## Required ordering

The qualification order is frozen as:

1. prepare candidate source and ordinary development tests;
2. commit candidate source;
3. prepare freeze receipt naming exact commit/tree/preflight blob/runner blob;
4. create a fresh detached checkout at that exact source/freeze subject as specified by the successor implementation;
5. externally verify and record executable source identity;
6. only if step 5 passes, run the non-evaluating receipt-consistency preflight from that exact checkout;
7. verify Contract E evaluations = 0, supervisor launches = 0, candidate-runtime imports = 0 during preflight;
8. freeze/preserve the qualifying preflight receipt as required by the successor implementation;
9. re-check the detached checkout is still clean and both executable blobs still match immediately before matrix launch;
10. only then run the complete PR #130 matrix unchanged.

If the implementation needs a source commit followed by a receipt-only freeze commit, the receipt must explicitly distinguish the source commit/tree/blobs from the later receipt commit. The executed Python files must match the frozen source blobs, not merely the branch tip.

## No hidden repair rule

After the executable-source identity receipt is captured:

- do not edit preflight;
- do not edit runner;
- do not apply an uncommitted patch;
- do not copy in a newer file;
- do not use a different worktree copy;
- do not rerun from modified bytes.

Any required source change creates a new source commit and requires a new freeze and fresh detached checkout before qualification.

## Allowed changes

Only changes needed to:

- incorporate the already-observed PR #132 worktree delta into a new committed successor source if those changes are still desired;
- add source-identity recording/verification support outside the candidate Python execution path;
- make successor-specific receipt/result identifiers and paths;
- preserve and qualify the receipt-contract preflight from PR #131.

Do not alter the PR #130 scientific matrix.

Keep ERS supervisor, transcript schema, transcript verification algorithm, Contract E invocation semantics, render-bound consumer semantics, and decisive controls unchanged except for already-preserved qualification issuer pin state from ERS PR #11.

## Scientific launch

Only after both gates qualify:

A. executable-source identity gate;
B. non-evaluating receipt-consistency preflight;

may the unchanged PR #130 matrix begin.

The scientific dispositions remain those in PR #130:

- preregistered false accept -> `FALSIFIED`;
- frozen scientific evaluator defect -> `INCONCLUSIVE`;
- missing authority/dependency -> `BLOCKED`;
- complete unchanged matrix -> bounded support only.

## Non-claims

This successor does not establish production trust in Git, same-user adversarial resistance, host integrity, production key custody, production authority-state provenance, Contract E production authorization, Contract D effect registration, executor correctness, filesystem write recovery, or real MainFrame write authorization.

No release, merge, effect registration, executor, or production promotion is authorized.
