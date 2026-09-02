# Contract E v1 Semantic Obligation Matrix

This matrix classifies the smallest currently plausible Contract E capability surface. Every listed capability has exactly one v1 disposition.

| Capability | v1 classification | Bounded obligation / exclusion |
|---|---|---|
| Standing authority state | `CORE_V1` | Authority must come from a separately supplied immutable AuthorityState, not from the semantic/request payload. |
| Typed jurisdiction | `CORE_V1` | Scalar `domain`, `operation`, `scope`, `target_class`, `target_ref`; exact matching only. |
| Participant declarations | `CORE_V1` | Explicit authorized `subject_id`; delegation additionally declares `delegated_by`. |
| Subject binding | `CORE_V1` | Request subject must equal terminal authority-chain subject. No Qualification subject predicate is implied. |
| Domain binding | `CORE_V1` | Exact scalar equality through the complete chain and request. No aliases/sets/inheritance. |
| Operation binding | `CORE_V1` | Exact scalar equality through the complete chain and request. Decision authority cannot substitute for execution/verification. |
| Scope binding | `CORE_V1` | Exact scalar equality for the v1 AuthorityState/request protocol. This is not a recovered Qualification-scope predicate. |
| Target binding | `CORE_V1` | Exact `target_class` + immutable `target_ref`. Substitution changes applicability. |
| Currentness / validity interval | `CORE_V1` | Evaluation time must be within every chain record's inclusive validity interval. Missing/invalid times fail closed. |
| Revocation | `CORE_V1` | Any chain record with `revoked_at <= evaluation_time` is unusable. |
| Qualification | `OUT_OF_SCOPE_V1` | #58 remains underdetermined. No Qualification object participates in the authority predicate. |
| Competence | `OUT_OF_SCOPE_V1` | Competence may be referenced only as a non-conferring supporting artifact; it has no v1 authority predicate. |
| Delegation | `CORE_V1` | Linear, explicit, non-amplifying delegation only. Bounds must remain exactly equal to parent; only subject may change. |
| Authority-conferring basis discrimination | `CORE_V1` | AuthorityState chain records are the only conferring input. Request/supporting artifacts cannot confer. |
| `grant | policy | delegation` | `CORE_V1` | Root is exactly one `grant` or `policy`; descendants are `delegation` only. |
| Supporting/non-conferring artifacts | `CORE_V1` | Separate opaque references; preserved but ignored by authority predicate. |
| Recursive authority lineage | `CORE_V1` | Entire linear chain revalidated on every evaluation; no status shortcut. |
| Cycle rejection | `CORE_V1` | Duplicate IDs, non-immediate parent links, loops, branching, or missing parents invalidate state. |
| Authorized conflict/residue resolution | `OPTIONAL_V1` | E can authorize a distinct `resolution/resolve` operation against an exact target, but applying/discharging resolution is outside v1. Relevant blockers on ordinary requests remain blocking. |
| Comparison narrowness | `OUT_OF_SCOPE_V1` | E does not interpret comparison semantics or agreement. Comparison objects may only be non-conferring references. |
| Composition/embedding ceilings | `OUT_OF_SCOPE_V1` | E does not interpret semantic composition/embedding. Those stage semantics remain owned upstream. |
| Rejected/conflicting/residual information preservation | `CORE_V1` | AuthorizationReceipt binds the entire request and preserves exact reference/support/conflict/residue snapshots; relevant unresolved/contested items block. |
| Decision/action distinction | `CORE_V1` | Exact operation/domain binding prevents Decision authority from becoming action/execution authority. |
| Authorization distinction | `CORE_V1` | AuthorizationReceipt is a transient evaluation record with `authority_conferring=false`; it is not standing authority. |
| Execution/verification distinction | `CORE_V1` | Execution and verification are separate exact operations; neither implies the other. Execution report/supporting state is non-conferring. |
| Immutable referenced A-D object identity | `CORE_V1` | A/B/C/D are opaque immutable references. E binds their exact reference identities and does not rewrite their semantics. |
| Reason semantics | `OPTIONAL_V1` | Diagnostic codes are non-authoritative, unordered, excluded from semantic receipt identity, and not a primary-reason compatibility promise. |
| Unknown/missing/malformed state | `CORE_V1` | Fail closed. Exact candidate wire rejects unknown fields and versions; no defaults for authority-critical state. |
| Canonicalization and authority-bearing identity | `CORE_V1` | AuthorityState has deterministic canonical bytes and content identity; AuthorizationReceipt also has deterministic identity but remains non-conferring. |
| Multiple/surplus conferring records | `FALSIFIED_OR_REMOVE` | The v1 representation has exactly one linear conferring chain. Cross-record partial synthesis and surplus-conferring quantification are not representable. |
| Delegation domain/scope `any-of` | `FALSIFIED_OR_REMOVE` | Not representable in v1. Delegation bounds are scalar and must exactly equal parent bounds. |
| Bare resolved-conflict/residue ID discharge | `FALSIFIED_OR_REMOVE` | Request-side claims that IDs are resolved are forbidden; unknown such fields fail closed. |
| Authority from `status=established` or similar status strings | `FALSIFIED_OR_REMOVE` | Status is never a conferring input. Authority is recomputed from immutable AuthorityState and complete bindings. |
| Automatic operational execution | `OUT_OF_SCOPE_V1` | An authorized operation is not proof that execution occurred and does not execute anything. |
| Automatic verification from execution occurrence | `OUT_OF_SCOPE_V1` | Verification requires its own separate authority evaluation and evidence outside E. |

## Known underdeterminations avoided by construction

### Qualification subject/scope binding (#58)

The v1 candidate does not contain Qualification as an authority-bearing capability. No equality, containment, inheritance, or other Qualification predicate is selected.

### Surplus/multiple authority-conferring records (#59)

The v1 AuthorityState contains exactly one linear chain and the request names exactly that state. There is no array of peer conferring alternatives, so the unresolved complete-plus-mismatch quantifier is not evaluated.

### Delegation-as-domain-any-of

The candidate provides no `any-of` domain or scope representation. A delegation changes subject only; all authority bounds remain exactly equal to the parent. The unresolved broader delegation semantic is therefore not material to this v1 claim.
