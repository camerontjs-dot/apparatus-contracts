# Contract A RC2 Preserved Deviations and Negative Controls

Status: Research evidence record. None of these results is erased by the successful successor run.

## D1 — shallow-checkout provenance failure

Workflow run: `33470198733`.

The first RC2 workflow attempted an exact ancestry check against production base `6a45ab2de09370f3048ffb083e25b487f81117e4`, but the pull-request checkout contained only GitHub's synthetic merge commit at depth 1. `git merge-base` therefore could not address the named base.

Classification: **HARNESS / TOOLING DEVIATION**.

Scientific gates executed: no.

Successor change: fetch full Apparatus history before ancestry verification. Candidate bytes were not changed.

## D2 — omitted CAL import dependency

Workflow run: `33471104360`.

Candidate conformance passed, but importing CAL v1 explicit-claim machinery failed because the deliberately bounded CI environment omitted `spacy` (and subsequently the needed lightweight quantitative import dependency).

Classification: **HARNESS DEPENDENCY DEVIATION**.

Scientific cross-repository gates executed: no.

Successor change: install the dependencies required by the pinned CAL import surface. Candidate bytes were not changed.

## D3 — Markdown line-wrap correspondence assumption

Workflow run: `33471190603`.

The reference harness asserted that the normalized root proposition was a literal byte substring of the pinned RSH Markdown source. The source wraps the same sentence across Markdown lines, so the assertion failed before the downstream experiment.

Classification: **REPRESENTATION-ADAPTER ASSUMPTION FAILURE**.

Successor change: normalize whitespace only for the source/proposition correspondence check. The source bytes, Contract A proposition bytes, proposition hashes, EB queries, and downstream objects were unchanged.

This normalization remains explicit evidence and is not counted as semantic rewriting.

## D4 — positive-hit evaluator assumption falsified

Workflow run: `33471423473`.

The direct auxiliary EB probe represented each of the two supplied sources as one whole-document chunk. Real `BM25Retriever` returned zero positive-score hits for the root and both declared children.

Observed exact result:

- `clm-supplier-qualification`: `[]`;
- `clm-supplier-qualification-a`: `[]`;
- `clm-supplier-qualification-b`: `[]`.

Classification: **EVALUATOR ASSUMPTION FALSIFIED**.

The failed assumption was: proving that EB consumed the exact declared proposition requires this auxiliary coarse representation to produce a positive BM25 hit.

Successor change: exact-query execution remains required and recorded, but positive hits in this auxiliary probe are observations rather than a Contract A gate. The actual production EB loader/chunker/retrieval writer remains required and did retrieve evidence for both children in the successful successor.

This zero-hit result remains negative evidence about retrieval sensitivity. It is not repaired into a pass.

## D5 — current Contract B 1.2 compatibility carrier

Observed in live pinned models and the successful V3 path.

Current strict Evidence Bundler / Contract B 1.2 machinery still requires scaffold-era fields including support/confidence/fidelity/counterevidence/downgrade/workflow state and source trust/query/rank/provenance metadata.

Classification: **REAL COMPATIBILITY DEBT**.

Hostile mutations of those observations were invariant for:

- EB production retrieval evidence signature;
- CAL explicit request hash;
- CAL explicit semantic aggregation result.

Therefore their current parser/writer necessity does not demonstrate Contract A semantic ownership. RC2 keeps them outside the canonical authority surface and uses a separately attributable compatibility projection for the current production path.

## D6 — no faithful old-surface representation for declared decomposition

Observed compatibility result:

- declared `all_of` has no faithful legacy Contract A representation;
- direct RC2 candidate cannot be parsed as the current legacy scaffold claim object;
- an undecomposed legacy object can be projected to RC2 only with decomposition state `unknown`, not `not_decomposed`.

Classification: **REPRESENTATIONAL INCOMPATIBILITY**.

Version consequence: major-class if the RC2 authority eventually supersedes legacy Contract A 1.0.0. This research lane assigns no canonical version.

## D7 — CAL semantic-quality scope limitation

The successful real-path experiment exercises real CAL Contract B intake and real explicit-claim request/orchestration/aggregation, but injects a deterministic stub atomic auditor.

Classification: **BOUNDED NONCLAIM / EVALUATOR SCOPE**.

It proves that source-contract identity and declared `single` / `all_of` composition can reach CAL without semantic-authority leakage. It does not evaluate NLI accuracy or establish that the resulting `partially_supported` control verdict is scientifically correct.

## Strongest remaining falsifier after normal-context hardening

The strongest remaining test is independent recoverability:

> A genuinely fresh implementer, given only the frozen public Contract A authority aperture, should independently recover a consumer that agrees on canonical validation, missing-state behavior, immutable identity binding, undecomposed handling, and declared `all_of` lineage without seeing the reference validator, reference evaluator, ablation results, compatibility conclusions, or this research history.

A genuine independent disagreement will falsify or narrow the recoverability claim and must not be repaired after reference reveal and then counted as agreement.
