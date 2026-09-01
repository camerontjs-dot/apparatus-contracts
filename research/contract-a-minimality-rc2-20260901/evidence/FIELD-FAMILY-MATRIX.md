# Contract A RC2 Field-Family Minimality Matrix

Status: Research evidence record. This file is outside the candidate authority subtree.

Evidence basis:

- Contract A RC2 candidate tree: `54e5cfc659c574a1520ebc119d66e93d4f71ce34`
- Reference experiment tree: `18b9cec2bc3063ecad17d12d55e49ea4dcb61ff8`
- Evaluator tree: `5d7eb3e3a9a98ba1626118a5e06a018c02fa81ec`
- Successful normal-context workflow: `33471728968`
- Successful evidence artifact: `9786765413`
- Artifact ZIP SHA-256: `82f07a926b351916a5f3eddedac54ac96b959fd39d3d4186c26d766662fb7454`

The buckets classify **Contract A authority**, not whether a field exists somewhere in the current legacy compatibility path. `LEGACY_ONLY` and `FORBIDDEN_AUTHORITY` fields may still be carried separately when the existing strict Evidence Bundler / Contract B 1.2 machinery requires them.

| # | Field family | Classification | Observed discriminator | Contract-A rule |
|---|---|---|---|---|
| 1 | handoff identity / integrity | `CORE_CANONICAL` | Removing `handoff_id` fails candidate validation; identity substitution changes the whole-object binding. | Carry stable handoff identity, producer identity/version, and whole-object SHA-256 binding. |
| 2 | original work-object identity / text | `CORE_CANONICAL` | Removing `work_id` fails. A separate duplicate task prompt was not required by the real path. | Carry `work_id`; the root proposition is the exact audited work text for this one-root-per-object candidate. |
| 3 | authoritative proposition identity / text | `CORE_CANONICAL` | Removing proposition ID fails closed; parent/child identity substitution changes binding; CAL source-contract atoms retain these IDs/texts. | Carry exact stable root ID/text/hash and declared child ID/text/hash. |
| 4 | parent / child decomposition lineage | `CORE_CANONICAL` | Removing declared children fails; PR #44/#45 evidence and real CAL path require first-class child identity rather than query-only lineage. | When declared, root is the parent and ordered children are first-class authority. |
| 5 | composition relation | `CORE_CANONICAL` | Removing operator fails; unsupported `any_of` rejects; current evidence demonstrates only `all_of`. | Standardize only `all_of`; do not invent a general operator vocabulary. |
| 6 | decomposition producer / provenance | `REMOVE` | Adding a duplicate `decomposition_producer` is rejected. Handoff producer + decomposition ID + bound declaration already reconstruct the declarer. | Do not duplicate producer authority inside decomposition. |
| 7 | source identity / content representation | `CORE_CANONICAL` | Removing a supplied source ID fails; source substitution changes binding; explicit empty `sources` is valid and EB invents no source. | Carry each supplied UTF-8 representation by source ID + exact bytes + content hash. Empty supplied-source set is explicit and valid. |
| 8 | source acquisition provenance | `LEGACY_ONLY` | Hostile access-date mutation leaves EB evidence signature, CAL request hash, and CAL explicit semantic result unchanged; current legacy B path still requires access/source provenance fields. | Keep only in the compatibility carrier while old machinery requires it; no A authority. |
| 9 | upstream-selected passages / spans | `PRODUCER_SPECIFIC_ATTACHMENT` | Mutating legacy `source_refs`/selected passage state leaves EB production retrieval evidence and CAL explicit semantics unchanged. | May be retained as attributable producer history outside canonical A; EB constructs its own evidence world. |
| 10 | upstream retrieval / query history | `LEGACY_ONLY` | Hostile query-history mutation is invariant downstream; current legacy source profile requires retrieval metadata. | Compatibility baggage only; never proposition authority. |
| 11 | retrieval query / rank / score | `LEGACY_ONLY` | Query/rank mutations are downstream-invariant; current legacy writer requires query/rank. No score field is demonstrated as necessary. | Query/rank may remain in compatibility carrier. Scores have no demonstrated A-level need and should not be added to the canonical candidate. |
| 12 | upstream support labels | `FORBIDDEN_AUTHORITY` | `support_status` is structurally invalid inside the candidate; hostile `unsupported` mutation leaves EB evidence and CAL explicit semantics unchanged. | May be retained only as attributable historical/legacy state; must never establish downstream support truth. |
| 13 | upstream confidence / claim strength | `FORBIDDEN_AUTHORITY` | Hostile claim-strength mutation leaves EB evidence, CAL request, and CAL explicit result unchanged. | Never downstream semantic authority. |
| 14 | extraction-fidelity fields | `LEGACY_ONLY` | Hostile extraction-fidelity mutation is invariant; current strict legacy claim shape requires it. | Preserve only for measured legacy compatibility. |
| 15 | counterevidence flags | `FORBIDDEN_AUTHORITY` | Hostile counterevidence mutation is invariant through EB/CAL explicit path. | Must not establish counterevidence truth or CAL semantics. |
| 16 | downgrade status / reason | `FORBIDDEN_AUTHORITY` | Hostile downgrade mutation is invariant through the real path. | Attributable legacy history only; no semantic authority. |
| 17 | trust / source-level heuristics | `FORBIDDEN_AUTHORITY` | Hostile trust mutation is invariant; current Contract B base records still require legacy trust labels. | Never source reliability/authority for a proposition merely because upstream asserted it. |
| 18 | model / prompt / config identity | `LEGACY_ONLY` | Hostile model/prompt/config mutation is invariant; current legacy C-A parser requires scaffold/model/config structures. | Keep in compatibility carrier while needed; canonical A needs only producer ID/version. |
| 19 | task / workflow-condition state | `LEGACY_ONLY` | Hostile workflow-condition mutation is invariant; current legacy B claim shape still requires it. | Compatibility-only, not proposition authority. |
| 20 | timestamps / history / supersession metadata | `PRODUCER_SPECIFIC_ATTACHMENT` | Hostile timestamp mutation is invariant. No general history/supersession datum was required by the bounded A promise. | Keep producer history outside canonical A. Individual timestamps required by old strict schemas may remain in the legacy compatibility carrier. |

## Bucket totals

- `CORE_CANONICAL`: 6 families: 1, 2, 3, 4, 5, 7.
- `OPTIONAL_CANONICAL`: none. Optionality that matters is represented by explicit state/cardinality inside core families rather than a new optional field family.
- `PRODUCER_SPECIFIC_ATTACHMENT`: 2 families: 9, 20.
- `LEGACY_ONLY`: 5 families: 8, 10, 11, 14, 18, 19. (Six numbered rows because 11 intentionally notes that scores have no demonstrated need.)
- `FORBIDDEN_AUTHORITY`: 5 families: 12, 13, 15, 16, 17.
- `REMOVE`: 1 family: 6, plus retrieval score as a subfield of family 11.

## Minimality conclusion

The normal-context evidence supports a smaller stable semantic surface than legacy Contract A. The current production writer still has structural dependencies on legacy observations, but hostile mutation shows those observations need not control Evidence Bundler evidence identity or CAL source-contract proposition authority. They therefore do not justify expanding the Contract A canonical semantic surface.
