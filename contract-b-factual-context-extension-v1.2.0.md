# Contract B Factual-Context Extension v1.2.0

**Status:** production promotion candidate
**Applies to:** Evidence Builder/Bundler → Claim Audit Lab (Contract B)
**Extension path:** `extensions/contract-b-factual-context-v1.json`

This document is an additive specification to the locked handoff contract. It does not rewrite the v1.0.0 contract body.

## 1. Purpose and authority

The optional extension carries evidence-world facts and preparation/audit history that CAL may need before proposition-specific assessment. It transports and validates state; it does not acquire CAL's semantic or decision authority.

The existing Contract B claim/source/passage files remain canonical for their existing identities and payloads. The extension references those records by ID and MUST NOT duplicate claim text, source bibliographic payloads, passage text, or passage hashes.

## 2. Presence states

An extension-aware consumer MUST expose exactly one discovery state:

- `legacy_absent`: the bundle declares Contract B 1.0.0 or 1.1.0 and the extension is absent;
- `absent`: the bundle declares Contract B 1.2.0 and the optional extension is absent;
- `present`: the extension exists and passes all integrity, schema, reference, and normalization checks.

A present but invalid extension is an intake failure, not an absence state. Absence never implies `false`, an empty history, a closed world, or any proposition-specific conclusion.

## 3. Physical JSON shape

The extension is one JSON object with exactly these members:

- `schema`, exact value `contract-b-factual-context-v1`;
- `history_complete`, exact value `true`;
- `claims`, array;
- `sources`, array;
- `passages`, array;
- `history`, array;
- `history_count_checks`, array;
- `aperture`, array.

Extra top-level fields are invalid.

### 3.1 Explicit known/unknown value

Fields that use explicit state have this shape:

```json
{"state":"known","value":"..."}
```

or:

```json
{"state":"unknown","value":null}
```

`known` requires a non-null JSON value. `unknown` requires `null`. Consumers MUST NOT replace unknown with a default.

### 3.2 Claims

Each `claims` item contains exactly:

- `claim_id`: reference to an existing canonical Contract B claim;
- `origin`: explicit known/unknown value preserving claim origin/lineage information;
- `atomicity`: explicit known/unknown value preserving source-declared or mechanically observed claim structure state.

No semantic relation or verdict is permitted.

### 3.3 Sources and factual context

Each `sources` item contains exactly:

- `source_id`: reference to an existing canonical Contract B source;
- `context_facts`: array of factual records.

Each factual record contains exactly:

- `fact_id`;
- `predicate`;
- `value`: a JSON factual value;
- `assertion_mode`;
- `provenance_passage_id`: reference to an existing canonical passage.

Predicates may describe version, effective date, validation date/status, supplier identity, or similar source/evidence facts. Their presence MUST NOT be interpreted by Contract B as proposition-specific applicability.

### 3.4 Passage representation anchors

Each `passages` item contains exactly:

- `passage_id`: reference to an existing canonical Contract B passage;
- `anchors`: array of objects with exactly `type` and `value`.

Anchors are representation coordinates, not semantic judgments.

### 3.5 Complete preparation history

`history_complete: true` means `history` is the complete nomination/admission/review ledger for the extension's evidence world. It does not mean the corpus, search universe, or proposition evidence is complete.

Each `history` item contains exactly:

- `link_id`: stable unique history identity;
- `claim_id`: existing canonical claim reference;
- `passage_id`: existing canonical passage reference;
- `nomination`: JSON object preserving nomination metadata;
- `review`: JSON object preserving review/admission metadata and containing `decision` equal to `accepted`, `rejected`, or `needs-review`.

Rejected candidates remain recoverable because every history passage reference must resolve to an existing canonical passage record.

Nomination and review metadata are audit-visible. They are not automatically semantic-measurement inputs.

### 3.6 Derived history-count checks

Each `history_count_checks` item contains exactly:

- `claim_id`;
- `candidate`;
- `reviewed`;
- `admitted`.

These are non-authoritative validation views. For each claim, consumers MUST derive:

- `candidate` = number of history links;
- `reviewed` = number whose review decision is not `needs-review`;
- `admitted` = number whose review decision is `accepted`.

If a supplied check differs from the derived values, intake fails closed. Consumers MUST derive semantic behavior from history rather than trusting these numbers.

### 3.7 Aperture observations

Each `aperture` item contains exactly:

- `claim_id`;
- `search_scope`: JSON object describing observed/supplied search scope;
- `outcome`: explicit known/unknown value;
- `limitations`: JSON array.

Aperture observations do not establish proposition-specific completeness.

## 4. Prohibited proposition-specific fields

No object anywhere in the extension may use these keys as authoritative fields:

- `support`;
- `refutation`;
- `proposition_specific_relation`;
- `semantic_validity`;
- `temporal_applicability`;
- `authority_applicability`;
- `supplier_applicability`;
- `completeness_conclusion`;
- `decision_participation`;
- `audit_support_verdict`;
- `verdict`;
- `abstention`.

Values such as `support_candidate` inside an allowed nomination field are historical retrieval hypotheses, not authoritative support judgments.

## 5. Canonical normalization and ordering

The extension is canonical UTF-8 JSON with:

- recursively sorted object keys;
- compact separators `,` and `:`;
- Unicode emitted directly rather than ASCII escapes;
- NaN and Infinity forbidden;
- exactly one trailing LF byte.

Before serialization, arrays are ordered as follows:

- `claims`: ascending `claim_id`;
- `sources`: ascending `source_id`;
- each source's `context_facts`: ascending `fact_id`;
- `passages`: ascending `passage_id`;
- each passage's `anchors`: ascending by `(type, canonical-json(value))`;
- `history`: ascending `link_id`;
- `history_count_checks`: ascending `claim_id`;
- `aperture`: ascending `claim_id`;
- each aperture `limitations`: ascending by canonical JSON representation.

Consumers MUST reject a present extension whose bytes are not in this canonical form. This gives independently implementable normalization rather than relying on producer insertion order.

## 6. Integrity binding

A present extension MUST:

1. be included in the C-B bundle-tree hash under its relative path;
2. have an exact entry in `SHA256SUMS`;
3. match the listed SHA-256 digest.

A present but unbound extension fails closed. Changing extension bytes without resealing the artifact fails closed.

## 7. CAL intake ledger versus semantic-measurement context

An extension-aware CAL consumer MUST retain the complete validated extension in an intake/audit view.

For semantic measurement, CAL constructs a narrower context containing only:

- referenced claim identity;
- admitted passage identities, where admission is derived from `history.review.decision == accepted`;
- source identities referenced by admitted passages;
- provenance-bound factual context for those admitted sources;
- representation anchors for admitted passages.

The semantic-measurement context MUST NOT contain nomination rank/score/hypothesized role, reviewer identity/notes, rejected candidates, history-count checks, or proposition-specific judgments. Changing nomination-only metadata must not change the normalized semantic context.

## 8. Compatibility

Contract B 1.2.0 is a MINOR capability expansion. Extension-aware validators and consumers continue accepting 1.0.0 and 1.1.0 artifacts. Untouched legacy artifacts require no migration.

The extension does not define Contract C or CAL result packaging.