# Contract E RC3D — Consumer Request Surface Hardening Preregistration

Status: **RESEARCH ONLY / successor to RC3C fresh reproduction falsification**

## Question

Can the remaining Contract E RC3C fresh-reproduction mismatches be removed by freezing the public consumer request surface and evaluator materialization boundary, without changing the authority semantics that independently survived?

## Parent evidence

RC3C candidate lineage:

- RC3C terminal research head: `6d49615acd85ca6439f9ae723570dde1fdb8dcae`
- RC3C amendment blob: `f05feac88128fd693cca2fb25a0b2951654377eb`
- RC3C hidden case blob: `17d45524125814478b987bb8e91d23f545fb514e`
- RC3C fresh Grok pre-reveal freeze: `b3dcaa5764827d8d167327ea41daf1aac43b8a3b`
- RC3C post-freeze comparison: `6da342a0bf3d724b24530518cbd2b97b92be1e77`
- RC3C fresh disposition: **FALSIFIED**

The falsification must remain preserved. It must not be retroactively upgraded by post-reveal diagnostics.

## Post-falsification diagnostic evidence

A diagnostic-only branch in `camerontjs-dot/research-scaffold-harness` tested whether the residual mismatches were caused by fixture/evaluator vocabulary rather than authority semantics.

Hosted diagnostic:

- run `33394259514`
- job `99494877811`
- artifact `9758671196`
- artifact ZIP SHA-256 `48f8b569afbe76cb51af304b9303d86aea051fe2a601802f610a0dc0f70c6766`

The diagnostic workflow proved `src/` and `tests/contract_e_rc3c/` were unchanged from the pre-reveal freeze.

Across 18 targeted comparisons:

- original outcome mismatches: 4
- diagnostic canonicalized outcome mismatches: 0
- diagnostic canonicalized RC3C-normative reason mismatches: 0

Original mismatch IDs:

- `PROP-N01-semantic-authority`
- `DEL-P01-narrower-child`
- `DELWIRE-P01-canonical`
- `HIST-P01-prior-valid-later-revoked`

Diagnostic signal:

`RESIDUAL_FAILURES_EXPLAINED_BY_DIALECT_OR_UNFROZEN_INTERFACE_SHAPE`

These results are causal evidence only. They are not independent-conformance evidence.

## Observed gaps RC3D is allowed to address

1. **Propagation request vocabulary**
   - inherited fixture DSL uses `requested_fields`;
   - normative propagation shape requires `fields`;
   - passing fixture DSL directly let an unknown authority-sensitive field escape the intended check.

2. **Delegation parent representation**
   - RC3C defined a Delegation child shape but the comparison implicitly treated the parent as the same shape;
   - inherited positive parent fixtures are better characterized as an upstream authority record with id/domain/operations/scope/current/expiry, not necessarily another delegation;
   - the public parent-authority request shape and linkage rule were never frozen.

3. **Historical evaluation vocabulary**
   - inherited fixture DSL uses `historical_record` as a mode label;
   - the fresh consumer independently chose `historical_inspection` as the semantic operation;
   - no canonical consumer mode token was frozen.

4. **Registry document consumption**
   - the frozen registry artifact is a document wrapper `{schema, records: map}`;
   - the fresh consumer natively accepted a record map but the comparison extracted the map from the wrapper;
   - this adaptation did not cause a result mismatch but remains a known native-consumption deviation.

5. **Fixture DSL versus native wire authority**
   - frozen test-case construction syntax was treated as if it were the contract's public request syntax;
   - evaluator materialization needs its own frozen authority and must not silently redefine consumer wire.

## Explicit non-targets

RC3D must not alter, unless a direct contradiction makes the candidate incoherent:

- authority domains;
- participant boundaries;
- subject/domain/operation/scope/target authority-basis binding;
- authority-reference and resolved-record currentness composition;
- qualification cardinality and competence semantics;
- warrant semantics;
- semantic result opacity;
- default non-transitive authority propagation;
- delegation subset/amplification semantics themselves;
- historical fact non-rewrite by later revocation;
- RC3B registry contents;
- production trust roots, cryptography, actor delegation topology, or Contract E 1.0.0.

## Candidate hypotheses

### H1 — canonical evaluation wrapper

A native consumer request has one explicit `kind` from:

- `envelope`
- `propagation`
- `delegation`
- `historical`

Unknown kinds reject rather than defaulting to another evaluation surface.

### H2 — propagation request uses `fields`

The canonical propagation request is:

- `mode`: `none | identity_provenance_only | explicit`
- `fields`: array of strings, required for `explicit`, optional otherwise
- `separately_reauthorized`: optional boolean

`requested_fields` is not native consumer wire. It belongs only to inherited fixture construction DSL. A native request containing `requested_fields` without canonical `fields` must reject rather than silently ignore it.

### H3 — delegation parent is an authority record, child is a Delegation

For delegation evaluation:

`parent` is a `ParentAuthorityRecord` with at least:

- `id`
- `authority_domain`
- `operations[]`
- `scope[]`
- `current`
- optional `valid_until`

`child` is a `Delegation` with the RC3C canonical child fields:

- `id`
- `delegator`
- `delegate`
- `authority_domain`
- `operations[]`
- `scope[]`
- `current`
- `parent_authority_id`
- optional `valid_until`

Required linkage:

`child.parent_authority_id == parent.id`

Then apply existing domain, operation subset, scope subset, currentness, and expiry non-amplification rules.

RC3D does not infer an additional `delegator == parent subject` rule because no authoritative parent-principal field has yet been established.

### H4 — historical modes are explicit

Canonical historical request modes are exactly:

- `historical_inspection`
- `new_exercise`

`historical_record` is a fixture DSL token, not a native mode.

Unknown modes reject rather than silently default.

`historical_inspection` may establish the stored historical fact without rewriting it from later revocation/currentness.

`new_exercise` does not authorize from historical validity alone and still requires current authority.

### H5 — registry document is natively consumable

The cross-repository registry artifact is a canonical `RegistryDocument`:

- `schema`: string
- `records`: object mapping id to resolved basis record

The consumer must accept this wrapper natively. A bare record map may remain an implementation-internal resolver representation, but comparison must not require extracting `records` from the canonical artifact before calling the consumer.

### H6 — fixture materialization is evaluator authority, not contract authority

The hidden vector corpus may use construction-DSL tokens such as `requested_fields` or historical case labels.

A frozen evaluator materialization specification must map those fixture forms into the canonical request surface **before** comparison.

That mapping must itself be frozen before any fresh independent implementation begins and denied pre-freeze to the independent implementer unless the mapping is also part of the public contract.

## Falsifiers

RC3D is falsified internally if any of the following occurs:

- a native propagation request carrying forbidden semantic/authority fields can be accepted because an unknown alias is ignored;
- canonical `fields` cannot reproduce the inherited propagation safety outcomes;
- a canonical positive parent-authority + child-delegation pair false-rejects before subset semantics;
- delegation operation/scope/expiry amplification no longer rejects with the relisted reasons;
- historical inspection and new exercise remain ambiguous or silently default from unknown mode tokens;
- the canonical registry document wrapper cannot be consumed without extracting/repacking its record map;
- evaluator materialization changes domain semantics rather than only request representation;
- semantic result payload mutations change authority behavior;
- inherited RC3B/RC3C authority regressions appear;
- the successor fresh implementation requires knowledge of hidden fixture DSL to implement the public consumer.

## Internal hardening required before fresh reproduction

Before decisive execution freeze:

- RC3D public interface amendment;
- frozen evaluator vector-materialization specification;
- RC3D successor hidden cases;
- RC3D reference validator/hardening apparatus;
- workflow hash guards.

Hosted execution must include:

- inherited RC3B validator suite unchanged;
- inherited 9 x 15 basis compatibility matrix unchanged;
- inherited RC3C successor suite unchanged;
- full inherited RC3A/RC3C vectors materialized through the frozen evaluator mapping;
- RC3D native request-surface cases;
- semantic-result metamorphic invariance;
- negative controls for alias acceptance, unknown-kind defaulting, unknown-mode defaulting, parent-link mismatch, and registry wrapper extraction.

## Fresh reproduction gate

If internal hardening survives, the next fresh reproduction should use a different model family.

Preferred local route for this project: **Antigravity / Gemini**, in a fresh workspace and fresh context.

The fresh implementer may see the inherited normative five blobs plus the RC3D public interface amendment. It must not see:

- RC3C Grok implementations or PRs #2/#3/#4;
- diagnostic reasoning/results;
- RC3D preregistration;
- vector materializer;
- hidden cases;
- reference validators/results;
- expected outcomes.

## Promotion bound

Even a complete RC3D internal pass and fresh Gemini reproduction would support only the next bounded research gate. It does not establish production Contract E authority or Contract E 1.0.0.