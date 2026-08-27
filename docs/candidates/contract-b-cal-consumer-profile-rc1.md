# Candidate Contract B CAL Consumer Profile — RC1

**Status:** RESEARCH CANDIDATE, NORMATIVE FOR THIS EXPERIMENT ONLY  
**Canonical Contract B changed:** no  
**Production version assigned:** no  
**Contract C work:** prohibited  

## 1. Evidence basis and pins

RC1 is an epistemic-compression candidate derived from the completed Contract B research program, not from a production implementation.

Evidence pins:

- V0/V1/V2 conformance report: `f4ee2dbd853821ba54328156bbab1c71235fae55`
- Optional-extension + ablation disposition: `4fb5dcde81c3ae0a9a99133f6a3f721aeab639dc`
- Independent-consumer negative result: `40349629c289a340c95735510cf04b1926d200d0`
- Temporal/version applicability result: `41627c9a313ffd2c73d9b8ea54f1e018e2d676e7`
- Frozen Evidence Bundler V1 producer/evidence world: `b4ca9111f5957ef7e7955e2c5024f2280ee19eb5`
- Frozen CAL research context: `6acc3462dad73959ccec6bccf8407215f5274cf6`

RC1 intentionally does not copy the V1 research object into a proposed production schema. It freezes only enough physical and normalization semantics to test whether the demonstrated Contract B ownership model can become an independently reproducible interface.

## 2. Contract boundary

Contract B carries evidence-world state needed by CAL before proposition-specific assessment. It may carry provenance-bound version, effective-date, identity, search, preparation, and representation facts.

Contract B MUST NOT carry an authoritative proposition-specific CAL judgment for:

- semantic support or refutation;
- semantic validity;
- temporal/lifecycle applicability;
- authority/supplier applicability;
- proposition-specific completeness;
- decision participation;
- verdict or abstention.

Upstream facts may later be inputs to those judgments. They are not the judgments.

## 3. Minimum demonstrated capability families

An extension-aware Contract B input MUST be capable of preserving:

1. claim origin/lineage;
2. optional claim atomicity/structure state, with unknown preserved explicitly;
3. provenance-bound factual context;
4. source and passage identity plus integrity binding;
5. typed representation anchors;
6. complete nomination history;
7. complete admission/review history including recoverability of rejected candidates;
8. search/aperture observations;
9. explicit limitations and unknown states.

Stored `candidate_count`, `reviewed_count`, and `admitted_count` are NOT normative facts when complete history is present. They are derived views.

Existing canonical C-B claim/source/passage payloads should be referenced rather than duplicated by any later production extension. That production packaging decision is not made by RC1.

## 4. Research V1 physical input profile

For this reproducibility experiment only, the verified V1 input is one JSON object with these top-level members:

- `variant`, exactly `minimal_context`;
- `bundle_id`, string;
- `claim`, object;
- `sources`, array;
- `passages`, array;
- `links`, array;
- `coverage`, object.

No enclosing `bundle` object exists in V1. Consumers MUST NOT infer one.

### 4.1 Claim

`claim` MUST contain `claim_id` and `claim_text`. `claim_form`, `origin`, and `atomicity` are evidence-world claim-context fields when present.

For normalization:

- a present non-null optional value is `{state:"known", value:<value>}`;
- a present null value is `{state:"unknown", value:null}`;
- an absent optional value inside an extension-aware input is `{state:"unknown", value:null}`;
- absence of the entire future optional Contract B capability extension on a legacy artifact is `legacy_absent`, not `unknown` and not `false`.

The legacy-extension case is not exercised by this baseline, but the semantic distinction is normative.

### 4.2 Sources and context facts

Each source is identified by `source_id`. Source records may carry `title`, `source_type`, `content_hash`, and `source_trust_level` as evidence/apparatus facts.

`context_facts` contains factual records. Each fact MUST preserve:

- `fact_id`;
- `predicate`;
- `value`;
- `assertion_mode`;
- provenance passage identity.

A factual predicate such as `system_version`, `validation_date`, or `validation_status` does not itself assert temporal applicability.

### 4.3 Passages and representation anchors

Each passage MUST preserve `passage_id`, `source_id`, exact `text`, `passage_hash`, and typed `anchors` when supplied.

Anchors are evidence representation coordinates, not semantic judgments.

### 4.4 Nomination and review history

Every `links` record is non-authoritative preparation history. It MUST preserve its stable `link_id`, claim and passage references, nomination metadata, and review/admission record.

Nomination roles/scores MUST NOT alter the semantic-measurement payload merely because they cross Contract B.

The RC1 frozen V1 profile declares the `links` array to be the complete candidate/admission ledger for this evidence world. A future production extension would need an explicit completeness declaration rather than relying on this research-profile assertion.

### 4.5 Search/aperture observations

`coverage.search_scope`, `coverage.outcome`, and `coverage.limitations` are evidence-aperture observations.

The stored count fields in V1 MUST be checked for consistency when present but MUST NOT enter the canonical RC1 ledger as independent facts. Canonical counts are derived from `links`:

- candidate count = number of links;
- reviewed count = links whose review decision is not `needs-review`;
- admitted count = links whose review decision is `accepted`.

## 5. Integrity gate

The experiment input MUST canonicalize as UTF-8 JSON with:

- recursively sorted object keys;
- compact separators `,` and `:`;
- Unicode emitted directly rather than ASCII escaping;
- no NaN/Infinity values.

The SHA-256 of those bytes MUST equal the frozen V1 value:

`sha256:a861eeafe9a360e9280e2d2c092bd2bbcdee6661c55412802be6fecbf8c7b2d7`

A consumer MUST fail before ledger projection if this condition is not met.

This is a research integrity gate. It is not proposed as the production integrity envelope.

## 6. Canonical normalized CAL intake ledger

Both consumers MUST derive exactly one object with this shape:

```text
{
  profile,
  input_identity,
  claim,
  sources,
  passages,
  preparation_history,
  aperture
}
```

### 6.1 `profile`

Exact string: `contract-b-cal-intake-ledger-rc1`.

### 6.2 `input_identity`

Contains exactly:

- `bundle_id`;
- `input_sha256`.

### 6.3 `claim`

Contains exactly:

- `claim_id`;
- `claim_text`;
- `claim_form` as explicit known/unknown state;
- `origin` as explicit known/unknown state;
- `atomicity` as explicit known/unknown state.

### 6.4 `sources`

Contains every source, sorted ascending by `source_id`, with exactly:

- `source_id`;
- `title`;
- `source_type`;
- `content_hash`;
- `source_trust_level` as explicit known/unknown state;
- `context_facts` sorted ascending by `fact_id`.

Each normalized context fact contains exactly `fact_id`, `predicate`, `value`, `assertion_mode`, and `provenance_passage_id`.

### 6.5 `passages`

Contains every passage sorted ascending by `passage_id`, with exactly `passage_id`, `source_id`, `text`, `passage_hash`, and `anchors`.

Anchors are sorted by the tuple `(type, canonical-json(value))` and contain exactly `type` and `value`.

### 6.6 `preparation_history`

Contains:

- `ledger_complete: true` for this frozen RC1 V1 evidence world;
- `links`, sorted ascending by `link_id`;
- `derived_counts`.

Each link contains exactly:

- `link_id`, `claim_id`, `passage_id`;
- `nomination`, copied as evidence history with object keys canonicalized;
- `review`, copied as evidence history with object keys canonicalized.

`derived_counts` contains exactly `candidate`, `reviewed`, and `admitted` from the derivation rule in §4.5.

### 6.7 `aperture`

Contains exactly:

- `search_scope`, copied from V1;
- `outcome` as explicit known/unknown state;
- `limitations` as an array sorted lexicographically by canonical JSON representation.

## 7. Canonical semantic-measurement payload

The normalized intake ledger preserves audit history. CAL semantic measurement receives a deliberately narrower payload.

It contains exactly:

- `bundle_id`;
- `claim_id`;
- `claim_text`;
- `admitted_sources`;
- `admitted_passages`.

An admitted passage is one whose link review decision is `accepted`.

`admitted_sources` is the unique set of source records referenced by admitted passages, sorted by `source_id`, and contains exactly `source_id`, `title`, `source_type`, `content_hash`, and normalized `context_facts`.

`admitted_passages` is sorted by `passage_id` and contains exactly `passage_id`, `source_id`, `text`, `passage_hash`, and sorted typed anchors.

The semantic payload MUST NOT contain nomination rank, score, hypothesized role, reviewer identity/notes, rejected candidates, `source_trust_level`, or downstream CAL judgments.

## 8. Output canonicalization

The normalized ledger and semantic payload use the same canonical JSON rule as §5. Their reported hashes are `sha256:` followed by lowercase hexadecimal SHA-256.

Two consumers conform at baseline only if:

1. both independently accept the frozen V1 integrity gate;
2. their normalized intake-ledger bytes are identical;
3. their intake-ledger hashes are identical;
4. their semantic-measurement payload bytes are identical;
5. their semantic-measurement hashes are identical.

A mismatch is evidence against RC1 reproducibility. Consumers MUST NOT be patched after observing each other's output during the baseline run.

## 9. Promotion boundary

RC1 passing this experiment would establish reproducibility of this reduced research interface on the frozen evidence world. It would NOT by itself:

- promote Contract B;
- prove general field-level minimality;
- assign PATCH/MINOR/MAJOR;
- make a research branch production;
- define Contract C;
- define the final CAL result artifact.

A later promotion review must combine this result with the prior compatibility, ablation, and temporal evidence.