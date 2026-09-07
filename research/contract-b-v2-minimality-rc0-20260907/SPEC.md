# Contract B v2 Minimality RC0

**Class:** Research / Draft / non-production candidate  
**Exact base:** `c3563cff66d2c85dcbf575c693056e2d8e4563d4`  
**Primary trigger:** Evidence Bundler PR #53 `NEGATIVE_INTERFACE_COUNTEREXAMPLE`

## Question

Can a breaking Contract B successor consume Contract A 2.0 authority exactly while preserving the minimum evidence-world state needed by legitimate CAL consumers, without reviving legacy scaffold judgments or acquiring CAL semantic authority?

This RC0 tests a candidate interface. It does not promote Contract B 2.0.0 and does not authorize an Evidence Bundler or CAL production migration.

## Frozen authorities under comparison

- Contract A `2.0.0`, released authority: exact root proposition, explicit decomposition state / declared `all_of` lineage, supplied UTF-8 source representations, producer/work identity and whole-object integrity.
- Contract B `1.2.0`, locked authority: legacy v1 core plus additive factual-context/history extension.
- Repository-wide contract/apparatus separation invariant: contract sufficiency, producer conformance and consumer conformance are distinct questions.

## Observed incompatibility being repaired

Contract A 2.0 deliberately excludes upstream support labels, confidence, claim strength, extraction fidelity, counterevidence/downgrade state and similar scaffold judgments from Contract A authority. Contract B 1.2 retains a v1 core that requires legacy fields described as C-A-derived and immutable. The additive v1.2 extension cannot replace that core.

A Contract B major-version candidate is therefore justified for research because the current legitimate producer/consumer boundary cannot be represented without invented legacy state.

## Candidate authority boundary

Contract B v2 RC0 carries only:

1. bundle identity and Evidence Bundler producer identity;
2. immutable preparation-profile identity/hash;
3. exact binding to one Contract A 2.0 handoff;
4. an exact mechanical copy of the Contract A root proposition and decomposition authority needed to recover primary audit targets;
5. exact source-representation identity/hash for every supplied Contract A source, without copying raw source content;
6. exact candidate passage text, text hash and UTF-8 byte coordinates into the bound Contract A source representation;
7. typed retrieval executions, exact queries, candidate limits, searched source IDs and execution state;
8. one proposition-passage candidate link preserving every retrieval nomination/rank plus explicit selection and review/admission state;
9. explicit per-target search-aperture execution state and limitations;
10. optional provenance-bound source context facts and optional passage anchors retained from the supported Contract B 1.2 factual-context capability;
11. complete preparation-history declaration and whole-object integrity.

Contract B v2 RC0 does not carry a CAL result or an upstream semantic opinion about proposition support.

## Primary audit targets

Primary targets are mechanically derived from Contract A 2.0 authority:

- `decomposition.state == declared`: exact declared children, in sequence order;
- `not_decomposed`, `failed`, or `unknown`: exact root proposition.

RC0 retrieval/history/aperture records may reference only these primary targets. This is deliberately narrower than allowing supplemental root retrieval for a declared `all_of`; such a capability must justify itself separately rather than widening this minimum candidate.

## Candidate object shape

Top-level exact members:

- `schema`: exact `contract-b-v2-candidate-rc0`;
- `bundle_id`;
- `producer`: `producer_id`, `producer_version`;
- `preparation_profile`: `profile_id`, `profile_sha256`;
- `source_contract_a`: public version `2.0.0`, `handoff_id`, `handoff_sha256`;
- `declaration`: exact `root_proposition` and exact `decomposition` copied mechanically from Contract A;
- `sources`;
- `passages`;
- `retrievals`;
- `candidate_links`;
- `aperture`;
- `history_complete`: exact `true`;
- `bundle_sha256`.

### Sources

Each source contains:

- `source_id`;
- `media_type`;
- `content_sha256`;
- `context_facts` array.

The source set must correspond exactly to the Contract A source set by ID/media type/content hash. Raw source content is not duplicated into B2.

A context fact contains `fact_id`, `predicate`, factual JSON `value`, `assertion_mode`, and `provenance_passage_id`. Contract B does not turn that fact into proposition-specific applicability.

### Passages

Each passage contains:

- `passage_id`;
- `source_id`;
- `start_utf8_byte` inclusive;
- `end_utf8_byte` exclusive;
- exact `text`;
- `text_sha256`;
- optional `anchors`.

Cross-A conformance requires the UTF-8 bytes at `[start_utf8_byte:end_utf8_byte]` in the bound Contract A source content to equal `text.encode("utf-8")`. This makes passage provenance independently falsifiable without depending on language-specific character indexing.

### Retrievals

Each retrieval contains:

- `retrieval_id`;
- `proposition_id`;
- `lane_kind` as a non-empty opaque lane type;
- `implementation_id` as a non-empty immutable/versioned profile or implementation identity;
- `query`: `query_id`, exact `text`, `text_sha256`, and `origin`;
- `candidate_limit`;
- exact `search_source_ids`;
- `execution_state`: `completed`, `partial`, or `failed`;
- `limitations` array.

Query origin is one of `exact_proposition_text`, `producer_derived`, `operator_supplied`, or `unknown`. When `exact_proposition_text`, the query bytes must equal the exact target proposition text.

Rank is retained in candidate nominations. Raw retrieval scores are intentionally ablated in RC0 because the bounded target materializes candidate membership, rank, selection and admission directly; no current required distinction depends on score magnitude. A counterexample requiring score magnitude falsifies this ablation.

### Candidate links

There is at most one link per `(proposition_id, passage_id)`.

Each link contains:

- `link_id`;
- `proposition_id`;
- `passage_id`;
- non-empty `nominations`, each with `retrieval_id` and positive `rank`;
- `selection`: `state` = `selected` or `not_selected`, plus positive contiguous `order` for selected links and `null` otherwise;
- `review`: `state` = `not_reviewed`, `accepted`, `rejected`, or `needs_review`.

Consistency rules:

- `not_selected` requires `review.state == not_reviewed`;
- `accepted`, `rejected`, and `needs_review` require selection;
- admitted evidence is derived only from `review.state == accepted`;
- nomination rank/lanes never become proposition support/refutation.

### Aperture

Exactly one aperture record exists per primary target and contains:

- `proposition_id`;
- `execution_state`: `complete`, `partial`, `failed`, or `not_run`;
- exact `search_source_ids` observed for the target;
- `limitations` array.

`complete` means only that the preparation profile's intended search execution completed for the recorded scope. It does not mean the corpus, search universe, or proposition evidence is complete.

## Explicit non-authority

No object in the candidate may introduce Contract B authority for:

- support or refutation;
- proposition-specific semantic relation;
- semantic validity;
- temporal, authority or supplier applicability;
- proposition-specific completeness;
- decision participation;
- CAL verdict, confidence, abstention or audit result;
- operational Decision or Authorization.

Legacy scaffold support/strength/fidelity/counterevidence/downgrade fields are not part of the B2 RC0 shape.

## Deliberate B1.2 ablations

RC0 removes or does not reproduce these legacy/B1.2 fields unless a test demonstrates a lost legitimate distinction:

- legacy scaffold semantic-looking claim fields;
- mutable/null `audit.*` writeback fields, because canonical Contract C now owns CAL output;
- `counterevidence_passages` as an upstream semantic classification;
- source `trust_level` as direct semantic input;
- `history_count_checks`, because candidate/review/admission counts are derived from the complete ledger;
- separate `atomicity`, because Contract A 2.0 now preserves explicit decomposition state and lineage and no bounded RC0 consumer distinction yet requires a second atomicity claim;
- raw retrieval scores, because rank and fully materialized selection/admission preserve the tested failure distinctions.

Each is an ablation hypothesis, not a universal claim.

## Falsifiers

Revise or reject RC0 if any of the following is demonstrated:

1. a valid Contract A 2.0 root/decomposition/source state cannot be represented without invention or loss;
2. root/child identity, order or decomposition state can be substituted without detection in A2→B2 conformance;
3. a B2 passage can claim provenance that does not reconstruct exactly from the bound A2 source representation;
4. candidate-recall, selection, review/admission and aperture failures cannot be distinguished from the B2 ledger;
5. a legitimate CAL pre-assessment consumer requires one of the ablated legacy fields to reconstruct a supported distinction;
6. a prohibited upstream semantic judgment can alter normalized admitted semantic input without changing proposition text, admitted passage text/context, or admission state;
7. context facts or anchors cannot retain the already-supported B1.2 factual-context distinctions;
8. whole-object identity or canonicalization admits stale/substituted content;
9. a materially smaller representation preserves every tested distinction and invariant;
10. the candidate requires CAL semantics to validate.

## Required pressure-test families

- A2 declared/non-declared/failed/unknown target recovery;
- root/child reorder, omission, invention, ID/text/hash substitution;
- source omission/addition/hash substitution;
- UTF-8 passage anchor tamper/off-by-one/cross-source substitution;
- retrieval query hash and exact-proposition-origin mutation;
- unknown/failed/partial retrieval states;
- duplicate retrieval rank and cross-proposition nomination controls;
- selection-order contiguity and review/admission consistency;
- rejected-candidate recoverability;
- aperture state/scope controls;
- prohibited semantic-field injection;
- canonical permutation/metamorphic controls;
- whole-object hash stale/tamper/reseal controls;
- field-family ablation checks for counts, atomicity and raw score magnitude;
- ordinary repository regression.

## Stop boundary

This RC0 may support only a later frozen B2 candidate / independent-consumer experiment. It must not merge, release, tag, change canonical version routing, modify production validators, alter Evidence Bundler/CAL production, or call CAL semantics.
