# Contract A Wire Candidate RC2

Status: **frozen-candidate authority only after a freeze receipt names these exact bytes**. Until then this is Research / Draft.

Canonical Contract A version: **none assigned**.

## 1. Bounded promise

This candidate carries only the upstream authority Evidence Bundler needs to begin evidence construction for one original audit proposition:

1. which upstream producer emitted the handoff;
2. which upstream work object is being handed off;
3. the exact authoritative root proposition identity and text;
4. declared `all_of` child proposition identity, text, order, and lineage when decomposition exists;
5. explicit decomposition state when no declared decomposition is available;
6. the exact UTF-8 source representations supplied to Evidence Bundler, identified and content-bound; and
7. an integrity binding over the complete candidate object.

It does **not** certify proposition truth, decomposition correctness, source trustworthiness, retrieval quality, evidence relevance, semantic support/refutation, CAL eligibility, or downstream decision authority.

One candidate object represents one root audit proposition. A producer run containing multiple independent root propositions emits multiple Contract A objects. This avoids inventing a higher-level multi-claim container before one is required.

## 2. Canonical object

A candidate object is canonical JSON using UTF-8 and this logical shape:

```json
{
  "schema": "contract-a-wire-candidate-rc2",
  "handoff_id": "stable producer-scoped identifier",
  "producer": {
    "producer_id": "stable producer identifier",
    "producer_version": "producer version or immutable build identity"
  },
  "work": {
    "work_id": "stable upstream work/original-claim identifier"
  },
  "root_proposition": {
    "proposition_id": "stable root proposition identifier",
    "text": "exact proposition text",
    "text_sha256": "sha256:<64 lowercase hex>"
  },
  "decomposition": {
    "state": "not_decomposed | failed | unknown | declared"
  },
  "sources": [],
  "handoff_sha256": "sha256:<64 lowercase hex>"
}
```

All object keys are closed. Unknown fields fail validation. Fields that are not in this surface cannot silently acquire Contract A authority merely by appearing in producer state.

### 2.1 Handoff and producer

`handoff_id`, `producer.producer_id`, and `producer.producer_version` are required non-blank strings.

The candidate does not standardize model ID, prompt/template ID, model parameters, operator notes, run timestamps, or workflow-condition state. Those may remain producer records, but they are not required to consume Contract A.

### 2.2 Work identity

`work.work_id` is required and identifies the upstream original-claim/work item from which the root proposition is authoritative.

The candidate deliberately does not duplicate a broader task prompt when the object being handed to Evidence Bundler is already the audit proposition. The exact root proposition text is carried once under `root_proposition`.

### 2.3 Root proposition

The root proposition is always authoritative upstream state and is required even when decomposition is declared or failed.

Required fields:

- `proposition_id`;
- exact `text`;
- `text_sha256 = sha256(UTF8(text))`.

A missing ID, blank text, or hash mismatch fails closed.

### 2.4 Decomposition state

`decomposition` is always present so absence cannot be confused with an explicit upstream state.

Supported states are deliberately narrow:

- `not_decomposed`: the producer explicitly supplies the root proposition without a decomposition;
- `failed`: an upstream decomposition attempt materially failed; the authoritative root remains usable and no child set may be fabricated;
- `unknown`: the producer/compatibility path cannot establish whether decomposition was supplied or attempted;
- `declared`: the producer explicitly declares an `all_of` decomposition.

No `not_applicable`, `partial`, generic Boolean, empty-decomposition convention, or universal operator vocabulary is introduced because current evidence does not require it.

For `not_decomposed`, `failed`, and `unknown`, `state` is the only allowed decomposition field.

For `declared`, these fields are required:

```json
{
  "state": "declared",
  "decomposition_id": "stable declaration identifier",
  "operator": "all_of",
  "children": [
    {
      "proposition_id": "stable child proposition identifier",
      "text": "exact child proposition text",
      "text_sha256": "sha256:<64 lowercase hex>",
      "sequence": 1
    }
  ]
}
```

A declared `all_of` decomposition requires at least two children. Child IDs, texts, and sequence values are unique. Sequence is exactly contiguous `1..N` in list order. A child ID may not equal the root proposition ID. Each child text hash must match its exact text.

The root proposition is the parent by construction, so a duplicated `parent_proposition_id` field is unnecessary. The handoff-level producer is the declaration authority by construction, so a duplicated decomposition-producer field is unnecessary. `decomposition_id`, root identity, child identities/order/text, operator, producer identity, and the whole-object integrity binding together reconstruct who declared what.

Contract A records the declaration. It does not certify that the children preserve the meaning of the root.

### 2.5 Supplied source representations

`sources` is required and may be an explicitly empty array. A missing `sources` field is invalid. An empty array means the producer supplied no source representation to Evidence Bundler; it is not equivalent to an unknown or omitted field.

Each supplied source has exactly:

```json
{
  "source_id": "stable source identifier",
  "media_type": "text/plain; charset=utf-8",
  "content": "exact UTF-8 representation consumed by Evidence Bundler",
  "content_sha256": "sha256:<64 lowercase hex>"
}
```

`media_type` must identify a UTF-8 text representation. `content_sha256 = sha256(UTF8(content))`.

Source IDs are unique. The content hash is the immutable representation identity, so a separate representation ID is not required by current evidence. The candidate does not standardize bibliographic metadata, acquisition history, trust labels, upstream retrieval rank, or upstream-selected passages.

A future source-reference mode is not part of RC2. Current real Evidence Bundler machinery needs recoverable text to construct its evidence world; a hash or locator without recoverable representation bytes is therefore insufficient for this bounded candidate.

### 2.6 Whole-object integrity

`handoff_sha256` binds the complete candidate payload.

To compute it:

1. remove only the top-level `handoff_sha256` member;
2. serialize the remaining object as JSON with keys sorted lexicographically, separators `,` and `:`, UTF-8, no ASCII escaping requirement beyond normal JSON validity, and no NaN/Infinity values;
3. compute SHA-256 of those UTF-8 bytes;
4. encode as `sha256:<64 lowercase hex>`.

Changing any bound producer, work, proposition, decomposition, source identity, source bytes, or state therefore changes the handoff binding.

## 3. Consumer semantics

Evidence Bundler may mechanically consume this candidate as follows without becoming semantic author:

- `not_decomposed`, `failed`, or `unknown`: retrieve for the exact root proposition text and retain the supplied state in provenance;
- `declared`: retrieve independently for each exact declared child proposition text, retaining the root/decomposition/sequence lineage; the root remains upstream authority;
- use only the supplied source representations as the initial evidence construction corpus for this handoff;
- do not treat upstream metadata outside this surface as relevance, support, trust, completeness, or verdict authority.

Contract B remains the evidence-world handoff. Retrieval/query metadata must not be promoted into first-class proposition authority there.

For CAL explicit-proposition intake:

- undecomposed/root-only maps to CAL operator `single`, with the exact root proposition as the one atom;
- declared decomposition maps to CAL operator `all_of`, with exact declared children in sequence order;
- CAL provenance origin is `source_contract`;
- provenance reference IDs and hashes must bind the corresponding Contract A declaration, not an Evidence Bundler-invented proposition.

A mechanical representation adapter may change serialization shape. It may not mint a new proposition, child, operator, source, semantic label, or missing-state default.

## 4. Explicit non-authority

The following are outside the stable Contract A semantic authority surface in RC2:

- upstream-selected passages/spans;
- upstream retrieval/query history, rank, score, or query text;
- upstream support/unsupported labels;
- confidence or claim-strength values;
- extraction-fidelity values;
- counterevidence flags;
- downgrade status/reason;
- trust/source-level heuristics;
- model, prompt, template, or generation configuration identity beyond the required producer identity/version;
- workflow-condition state;
- timestamps, run history, supersession history, or acquisition history.

Some may remain producer-specific or legacy records. If preserved, they remain attributable observations only. They cannot silently establish Evidence Bundler or CAL semantic truth.

## 5. Legacy compatibility rule

A legacy Contract A 1.0.0 object may be mechanically projected into this surface only when the projection can preserve the required root proposition, work identity, producer identity, and exact source representations. Because legacy A does not establish decomposition lineage, such a projection must use `decomposition.state = "unknown"`, never `not_decomposed` by default.

The projection may compute missing SHA-256 bindings mechanically from exact bytes. It may not infer decomposition, support, trust, evidence relevance, or other semantic state.

The reverse direction is not assumed compatible. A new candidate object does not contain the semantic-looking legacy fields required by old strict consumers, and a declared decomposition has no faithful legacy representation.

## 6. Contract E boundary

This object records what the identified producer declared and supplied. It does not assert that the producer was authorized to make, use, delegate, or execute that declaration. Future authority machinery may reference `handoff_id` and `handoff_sha256` externally without changing Contract A ownership.

## 7. Nonclaims

RC2 does not claim:

- retrieval completeness;
- decomposition correctness;
- universal decomposition operators;
- source authenticity beyond the bytes and identifiers supplied by the producer;
- standing authorization, jurisdiction, delegation, approval, execution, or autonomy;
- canonical Contract A release status;
- independent recoverability until a separate fresh reproduction succeeds.
