# Contract E RC2 Successor Experiment Preregistration

Status: **FROZEN BEFORE RC2 REFERENCE IMPLEMENTATION**

Date: 2026-09-02

## Scientific question

Does the smallest RC2 successor remove the exact RC1 receipt-identity underdetermination while preserving the bounded authorization safety predicate, and does the companion D→E trusted-origin profile close the provenance holes exposed by the terminal 101-case pressure experiment without inventing broader authority semantics?

## Authorities and predecessor evidence

- RC1 frozen candidate: `8876b7bcc2afa1a4902400b0cc507cf2ef02e6e7`
- RC1 fresh evaluator seal: `ee47670104776f627b7c337c6235dabafe03c874`
- RC1 fresh reproduction terminal: `d1e3c6998b20db845cdce8b4b39df90485c27e7d`
- RC1 result: 48/50 normative exact matches, zero false permits, zero false rejects; terminal `FALSIFIED`
- RC1 mismatch IDs: `NEG-SUPPORT-CANNOT-CONFER`, `NEG-STATE-ID`
- D→E pressure terminal record: `ca188a8b6f6235caf426ce6a5ace11470dcc3934`
- D→E preregistered mutation/metamorphic matrix: 101/101 passed across Python 3.11/3.12/3.13 before the stronger provenance extension falsified the original profile
- released Contract D authority remains `298a1a0f7b7b6d7712e11200d04faec3e1ca169b`

## Frozen RC2 semantic delta

Only the RC1 receipt AuthorityState identity ambiguity is changed in Contract E core:

- replace ambiguous receipt `authority_state_id` with `claimed_authority_state_id` and `recomputed_authority_state_id`;
- preserve both whenever establishable;
- authorization requires both non-null and exactly equal;
- both participate in receipt semantic identity;
- authorization predicate otherwise remains RC1-equivalent.

The companion trusted-origin profile adds external Decision and AuthorityState trust bindings plus fresh point-of-use E evaluation. Those are integration constraints, not Contract E core conferring semantics.

## Phase A — RC2 core candidate matrix

The reference candidate must be attacked with all RC1 semantic families, adapted only for RC2 schema tokens and receipt projection:

1. positive policy root;
2. positive grant root;
3. positive linear delegation;
4. subject mismatch;
5. domain mismatch;
6. operation mismatch;
7. scope mismatch;
8. target-class mismatch;
9. target-ref mismatch;
10. future authority;
11. stale authority;
12. revoked authority at the exact boundary;
13. valid-from inclusive edge;
14. valid-until inclusive edge;
15. future revocation positive;
16-20. delegation mutation of each bound field;
21-24. broken lineage parent/delegated-by/duplicate-id/non-delegation;
25. supporting artifacts remain non-conferring when valid standing authority exists;
26. supporting artifacts cannot confer when standing AuthorityState is invalid;
27-28. relevant conflict/residue block;
29-30. irrelevant conflict/residue do not block;
31-33. unknown resolved/future fields fail closed;
34. missing subject fails closed;
35. future E schema fails closed;
36. status-establishment laundering fails closed;
37. request AuthorityState binding mismatch fails closed;
38. forged/supplied AuthorityState identity mismatch fails closed;
39. reference identity mismatch fails closed;
40. target reference missing fails closed;
41-44. parent/child/sibling immutable target substitution behavior;
45. exact resolution authorization is distinct from resolution occurrence;
46. execution authorization positive;
47. execution does not imply verification;
48. Decision/authorization domain does not imply execution;
49. verification is a separate exact authorization;
50. surplus peer conferring root remains structurally invalid rather than selecting an aggregation quantifier.

### RC2-specific identity obligations

At minimum the core matrix must additionally prove:

51. valid state: claimed and recomputed identities are both non-null and equal;
52. invalid supplied-but-well-formed state ID: denial preserves the supplied claimed ID and separately preserves the recomputed canonical ID;
53. `NEG-SUPPORT-CANNOT-CONFER` equivalent: empty/invalid standing state plus supporting artifacts denies while preserving both distinct identity facts;
54. malformed/non-SHA claimed state identity: denial has `claimed_authority_state_id=null` while recomputed identity is preserved when canonicalization succeeds;
55. non-object/non-canonicalizable AuthorityState: recomputed identity is null rather than invented;
56. request binding to the claimed ID cannot override a claimed/recomputed mismatch;
57. authorized receipt invariant: both state identity fields exist and are exactly equal;
58. denial receipt semantic identity changes if claimed identity changes while all other semantic fields remain fixed;
59. denial receipt semantic identity changes if recomputed identity changes while all other semantic fields remain fixed;
60. diagnostic vocabulary/content mutation does not change receipt semantic identity;
61. receipt cannot use one field as a fallback alias for the other;
62. an RC1 receipt/schema token fails closed under RC2 exact schema validation.

## Phase B — D→E trusted-origin profile

Re-run the previous D→E attack surface with the new external trust anchors. At minimum cover:

### Contract D applicability and origin

- exact trusted Decision digest + exact released D + exact requested operation/effect/target can produce `candidate_for_authorization`;
- HOLD and evaluation.failed cannot;
- operation, effect type/version/params, target id/kind/content, policy, upstream authority substitution fail applicability;
- fabricated internally valid CLEAR Decision with a self-consistent new hash is rejected when it does not equal the externally trusted Decision digest;
- a deliberately weak consumer that derives its expected Decision digest from the candidate Decision must be caught.

### AuthorityState origin

- valid AuthorityState whose recomputed identity equals the external trusted AuthorityState binding may proceed to E evaluation;
- self-consistent fabricated root grant/policy may be core-E-valid but must fail the trusted-origin profile when absent from the external trust binding;
- changing any root/delegation bound field changes identity and invalidates the external binding;
- a deliberately weak consumer that derives its trusted state binding from the candidate AuthorityState must be caught.

### Human consumption

- exact human subject succeeds only after fresh point-of-use E evaluation;
- changed human subject, target, operation, scope, currentness, blocker state, or trusted state fails under the prior binding;
- handoff package is non-conferring and cannot be used as AuthorityState.

### Machine consumption

- exact machine subject + exact immutable ExecutionIntent succeeds only after fresh point-of-use E evaluation;
- mutate independently: executable/script digest, entry point, args, input artifacts, environment restrictions, declared side-effect target, operation, subject, scope, and current AuthorityState;
- every execution-critical mutation must change the exact target/binding or otherwise fail the gate;
- stale previously authorized receipt after revocation must not permit execution.

### Receipt-origin attack

- fabricate a denied receipt into `authorized=true`, recompute a valid deterministic receipt ID, and verify that a receipt-only weak consumer can be fooled;
- verify the actual profile ignores that forged permit and obtains the decision from fresh E evaluation against the current externally trusted state;
- both claimed and recomputed AuthorityState identity fields must be checked/preserved by the point-of-use path.

## Phase C — metamorphic invariants

The experiment must test properties rather than only named fixtures:

- adding/removing/reordering diagnostic strings cannot change semantic receipt identity;
- changing any authority-conferring bound field changes AuthorityState recomputed identity;
- changing only request/supporting-artifact order/content changes request/receipt binding but cannot manufacture standing authority;
- changing only supporting artifacts cannot turn invalid standing authority into valid authority;
- subject mutation never preserves authorization unless a separately valid exact AuthorityState authorizes the new subject;
- valid delegation may change subject only, never jurisdiction;
- point-of-use currentness/revocation is evaluated from current state, not historical receipt status;
- Decision content identity, AuthorityState identity, and receipt identity are integrity bindings, never origin authentication by themselves.

## Phase D — evaluator qualification before independent implementation

Before any fresh RC2 implementation exists, create and qualify a sealed evaluator against the frozen RC2 public SPEC/schema and reference implementation.

Qualification must establish:

- reference normative exact match on every hidden case;
- diagnostic-content invariance;
- preservation checks for references/supporting artifacts/conflicts/residues and both receipt state identity facts;
- no hidden expected output derived from a future independent implementation;
- seeded weak controls caught, including at least:
  1. claimed-only receipt identity;
  2. recomputed-only receipt identity;
  3. supporting-artifact conferral;
  4. Decision digest derived from candidate bytes;
  5. AuthorityState trust anchor derived from candidate bytes;
  6. receipt-only execution/handoff permit;
  7. no point-of-use revocation re-evaluation;
  8. ExecutionIntent target substitution.

The evaluator must be sealed before a fresh independent RC2 implementation exists.

## Phase E — fresh independent reproduction

Only after Phase D seal, prepare a clean-room aperture containing the frozen RC2 public SPEC, schema, and implementation task. The fresh implementer must not see the reference implementation, candidate tests, hidden cases, evaluator, expected outputs, RC1 implementation, D→E harness, prior reader outputs, or this conversation.

The fresh implementation and prereveal tests must be frozen before evaluator reveal. No post-reveal repair may count as the same reproduction.

Terminal independent state:

- `SUPPORTED` only with zero normative mismatches, false permits/rejects, exceptions, preservation failures, and diagnostic-shape failures;
- `FALSIFIED` for any normative disagreement;
- `INCONCLUSIVE` only for contamination/apparatus failure that prevents a valid comparison.

## Promotion falsifier

Contract E remains unsupported for production promotion if RC2 core or the trusted-origin profile fails any preregistered safety case, if the evaluator cannot discriminate seeded weak controls, or if fresh independent reproduction is not exact.

## Explicit nonclaims

This experiment does not authorize production merge/release, choose signatures/PKI/attestation, establish root legitimacy, solve Qualification, solve surplus-conferring aggregation, define wildcard/group authorization, authorize execution, establish execution occurrence, or establish verification.