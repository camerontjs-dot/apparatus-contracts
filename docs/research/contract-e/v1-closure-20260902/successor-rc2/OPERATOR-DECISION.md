# Contract E RC2 Successor Operator Decision

Date: 2026-09-02

Status: **ACCEPTED FOR A NEW RESEARCH CANDIDATE AND EXPERIMENT ONLY**

## Accepted normative choice

The successor to falsified Contract E candidate RC1 will preserve both AuthorityState identity facts in every AuthorizationReceipt when they can be established:

1. `claimed_authority_state_id` — the `authority_state_id` value supplied in the AuthorityState, when it is a syntactically valid `sha256:` identity; otherwise `null`.
2. `recomputed_authority_state_id` — the deterministic canonical identity recomputed from the supplied AuthorityState object excluding `authority_state_id`, whenever that canonicalization can be performed; otherwise `null`.

The successor MUST NOT collapse those two facts into one ambiguous field.

For valid AuthorityState input, the two identities must be equal before authorization can succeed. For invalid or forged input they may differ, and both facts must remain visible in the denial receipt.

Both fields participate in AuthorizationReceipt semantic identity. Diagnostic strings remain non-authoritative.

## Reason

Fresh independent reproduction RC1 terminated `FALSIFIED` with 48/50 normative exact matches and zero false permits/false rejects. Both mismatches were one ambiguity: the public RC1 receipt language did not determine whether a denial receipt's single AuthorityState identity field meant the supplied/claimed identity or the recomputed canonical identity.

Preserving both is the smallest change that retains both audit facts and removes the underdetermination without changing the authorization predicate.

## Separate trusted-origin boundary

The D→E integration successor will also test explicit external trusted-origin bindings exposed by the terminal D→E pressure experiment:

- a structurally valid Contract D object and its content hash do not authenticate Decision Engine origin;
- a self-consistent AuthorityState and its content hash do not authenticate root-grant legitimacy;
- a self-consistent AuthorizationReceipt hash does not authenticate evaluator origin.

The successor experiment therefore requires external trust anchors for the exact Decision object and AuthorityState source/state, and fresh point-of-use Contract E evaluation. It does **not** select signatures, PKI, attestations, reusable permits, leases, wildcard roles, or a universal trust ontology.

## Non-authorization

This decision authorizes creation and testing of a new research candidate only. It does not promote Contract E, create Contract E `1.0.0`, authorize execution, or authorize merging a production contract.