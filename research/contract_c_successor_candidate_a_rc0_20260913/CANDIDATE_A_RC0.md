# Contract C successor Candidate A RC0 research contract

**Classification:** Draft Research / Research Infrastructure. This is not a production Contract C, release, SemVer assignment, CAL production change, Decision Engine production change, Contract E / Authorization surface, execution authority, or independent-consumer reproduction.

**Candidate parent:** Phase 2 representation freeze `f5337dedaad045aa290e80f69dc83ac1a0f73436` with disposition `PREFER_CANDIDATE_A_FOR_CURRENT_SUCCESSOR_SCOPE`.

This record concretizes only the Phase 2-preferred architecture: **canonical minimal sufficient basis groups over exact public evidence participants**. It does not reopen the Phase 0, Phase 1, Phase 1.5, or Phase 2 architecture unless this exact candidate is falsified.

## Frozen research profile

The exact research discriminator is:

`contract-c-successor-candidate-a-rc0-research`

This string is a research-profile identity only. It is deliberately not a successor SemVer.

The candidate consists normatively of this contract record, `candidate_a_rc0.schema.json` for the closed structural shape, and `candidate_a_rc0.py` for cross-field semantic, canonicalization, local-identity, exact-B-reference, immutable-policy-resolution, and external-authority checks that JSON Schema alone cannot express.

## Wire object

```json
{
  "profile": "contract-c-successor-candidate-a-rc0-research",
  "result_set_id": "sha256:<canonical-unsealed-object>",
  "contract_b": {
    "contract_version": "<exact Contract-B authority>",
    "bundle_id": "<exact bundle id>",
    "bundle_hash": "sha256:<exact bundle bytes>"
  },
  "producer": {
    "semantic_implementation_sha": "<exact CAL semantic implementation git sha>",
    "policy_sha256": "<exact behaviorally relevant canonical policy sha256>",
    "policy_resolver_commit_sha": "<exact immutable deterministic resolver commit>"
  },
  "execution": {"state": "completed|failed|incomplete"},
  "propositions": [
    {
      "proposition": {
        "proposition_id": "<public id>",
        "content_sha256": "sha256:<canonical proposition semantic content>"
      },
      "execution": {
        "state": "completed|failed|incomplete",
        "completion": "assessed|not_checkable|null"
      },
      "terminal": {
        "verdict": "supported|contradicted|not_checkable",
        "reason": "<stable public reason>"
      },
      "participants": [
        {
          "evidence_ref": {"source_id": "...", "passage_id": "..."},
          "relation": "supports|refutes|non_polarized",
          "role": "causal|residual"
        }
      ],
      "basis_groups": [[{"source_id": "...", "passage_id": "..."}]]
    }
  ]
}
```

For failed/incomplete proposition execution, `completion` and `terminal` are `null`, and the proposition carries no participants or basis groups. For completed proposition execution, `completion` and `terminal` are present. For failed/incomplete result-set execution, `propositions` is empty.

## Exact binding semantics

### Contract B

`contract_b` binds the entire result set to one exact upstream evidence world by `(contract_version, bundle_id, bundle_hash)`. Participant references are only `(source_id, passage_id)` inside that exact world. The candidate deliberately does **not** repeat Contract-B evidence payloads or `passage_sha256`.

Conformance requires the verifier to resolve each participant against the independently selected exact Contract-B world. A reference absent from that exact world fails closed. Because there is one top-level exact B binding, participants from two worlds cannot be truthfully composed into one candidate object.

### Producer and policy

`producer.semantic_implementation_sha` is the exact CAL semantic implementation identity. `producer.policy_sha256` is the exact behaviorally relevant policy digest. `producer.policy_resolver_commit_sha` binds the immutable deterministic resolution mechanism needed to recover and verify the policy without a mutable `latest`, human configuration-name interpretation, or repeated in-band policy payload.

For the current frozen research lineage the demonstrated values are:

- semantic implementation `a902621e8baea3063dddd7f92ba975aade305464`;
- policy digest `44ecc33519fa8911079595d322f5f0decbf0389af42e153ac32214931798e42c`;
- Phase 1.5 immutable resolver fixture commit `43b571464734325277374ee81098553fb7c1b944`.

Those values are research evidence, not a production registry. Production release authority is explicitly unresolved until a later promotion decision.

### Proposition

`proposition_id` is not sufficient alone. `content_sha256` binds the exact authoritative canonical proposition semantic content. That canonical content must include every proposition semantic dimension that can change CAL interpretation, not merely a display string. Same-ID replacement under a different content digest is a different object and cannot satisfy the old external handoff authority.

## Execution and terminal epistemic state

Result-set and proposition execution each distinguish `completed`, `failed`, and `incomplete`. Proposition execution additionally carries `assessed` for a completed subject-matter assessment producing `supported` or `contradicted`, or `not_checkable` for a completed epistemic abstention producing terminal verdict `not_checkable`.

This makes completed epistemic abstention structurally different from failed or incomplete execution. Failed/incomplete execution cannot carry an invented terminal subject-matter verdict.

The bounded public terminal reasons in RC0 are `categorical_support`, `categorical_refutation`, `mixed_relations`, `unresolved_categorical_relation`, `joint_public_cause`, and `no_deciding_relation`. These are public semantic reason identities for the frozen corpus. Producer-private control-flow branch names are not exported merely because historical C1 did so.

## Participants

A participant is identified directly by its exact Contract-B evidence reference inside the object/proposition binding context. There is no separate `contribution_id`.

`relation` has exactly three RC0 values: `supports`, `refutes`, and `non_polarized`. `non_polarized` is not support, counterevidence, a score, Decision CLEAR, Authorization, or execution. `role` is independently `causal` or `residual`. Every retained participant appears exactly once and has exactly one relation and role.

RC0 terminal coherence is intentionally bounded to the frozen corpus: supported causal basis groups are support-only; contradicted groups are refute-only; `mixed_relations` groups contain both support and refutation; unresolved/joint-public-cause groups are non-polarized; `no_deciding_relation` has no causal basis and retains only residual non-polarized participants.

## Causal semantics

`basis_groups` is the canonical family of minimal sufficient causal participant sets for the proposition terminal result.

```text
single:                    {{S1}}
independent alternatives:  {{S1},{S2}}
joint:                     {{S1,S2}}
mixed:                     {{S1,R1}}
alternative-joint:         {{S1,R1},{S2,R1}}
```

Normative structural rules:

1. every group is non-empty;
2. group members are unique exact participant references;
3. every group member names a participant whose role is `causal`;
4. equivalent groups are unique;
5. no represented group may be a strict superset of another represented group;
6. the union of all groups is exactly the set of causal participants;
7. residual participants never appear in a basis group.

Rule 5 establishes antichain/minimal-normal-form consistency **inside the claimed family**. Contract bytes cannot prove the producer's empirical/semantic claim that an apparently joint group is truly minimal. That is a producer-conformance obligation: adversarial qualification compares claimed groups with the already frozen semantic oracle, and later CAL producer conformance must derive them from legitimate CAL ablation/authority state without a new epistemic judgment.

## Canonicalization and identity

The following collections are semantic sets and therefore unordered on input: proposition records, participants, basis groups, and members within each basis group. Canonicalization sorts them deterministically by their exact public identities. Arbitrary insertion order never becomes semantic identity.

Canonical JSON is UTF-8 JSON with lexicographically sorted object keys, no insignificant whitespace, no ASCII-forcing transformation, and one terminal LF.

Two identity layers are mandatory:

1. `result_set_id` is `sha256:` plus SHA-256 of the canonical object **with `result_set_id` omitted**. It detects stale local identity and gives deterministic self-consistency.
2. the handoff verifier receives an **independently established expected SHA-256 of the complete canonical object including `result_set_id`**. That digest is not selected from the object itself. A semantically changed object that an attacker coherently reseals can be locally self-consistent but cannot satisfy the old independent authority binding.

An attacker-provided replacement expected digest is not authority.

## Closed-world profile

Unknown fields are rejected at every candidate-owned object layer. The profile is an exact literal and cannot self-select a new version or extension. Destination thresholds/routing, Decision policy, actors, delegation, approval, Authorization, execution occurrence, generic C1 assessment slots, rule/state causal namespaces, repeated policy payload, repeated passage hashes, separate contribution IDs, measurements/scores, and private CAL control-flow state are outside this profile.

## Frozen-scope nonclaims

This candidate does not claim that Contract C proves causal truth from bytes alone, that SP-12 is observed current-CAL output, that the Phase 1.5 policy resolver is production release infrastructure, that Candidate B was semantically falsified, or that any candidate is ready for production/consumer promotion. Surviving adversarial qualification only makes this exact frozen RC0 eligible for a separate CAL producer-conformance experiment.
