# Contract E Authority Basis Binding RC3B — Results

## Classification

Research / apparatus-contract architecture falsification.

## Primary disposition

**SUPPORTED FOR PROMOTION**

Promotion is bounded to the next research gate only:

> Freeze the demonstrated Contract E authority/warrant research specification and test whether a fresh implementation can independently recover the same authority boundaries and outcomes from the specification alone.

This is not production promotion and does not define Contract E 1.0.0.

## Parent failure preserved

RC3A was **FALSIFIED** at result commit `d6561975ef395bc7cfe96d599d118bc901feb5f6`.

Its decisive counterexample showed that a bare authority reference carrying only `type`, `id`, and `current` could be laundered across domains. A CAL assessment policy reference survived an envelope relabel to citation authority because the authority-conferring policy itself was not bound to its subject/domain/operation/scope/target.

RC3B did not repair the RC3A freeze in place.

## RC3B frozen candidate

- RC3B branch base / RC3A terminal result: `d6561975ef395bc7cfe96d599d118bc901feb5f6`
- RC3B preregistration: `5f6a8dc5c65f75adb7707bca4bfcbd675d8a9355`
- RC3B candidate freeze: `e16dc38b4b99ce854280bacb6a953506007a4a26`
- RC3B freeze tree: `eb65e1f3a1c3b9dd82fd5d0cd0add742f796333e`
- freeze receipt: `b7456c0edb963d57f2baa5e5630c296e166928e6`

Frozen RC3B blobs:

- `PREREGISTRATION.md`: `3d106af0f0e6b569452270fe1cd83673a88f95ef`
- `BASIS-BINDING-SPEC.json`: `63c952c9c28f1be2173e69c79976c7dfe5880c10`
- `AUTHORITY-BASIS-REGISTRY.json`: `76ea333ee0460d9614e9899edb69e6865e48eccb`
- `FROZEN-BASIS-ATTACKS.json`: `c726fb0ef914a850620e545131a70d427f4027bd`

Inherited RC3A specification/case blobs remained exact:

- `SPEC-CANDIDATE.json`: `9c1090335d87eb5e4885a755542923b453c45317`
- `SPEC-SHAPES.json`: `c3f293430ae6ddb87523d83ea6e5380b8b832136`
- `SPEC-PARTICIPANT-BOUNDARY.json`: `8b1d292a240300388949d502e7b656e7a23a0b8e`
- `FROZEN-CASES.json`: `85bc7805d02a04c5a10b48b43a5f5a89f4e2f32a`

## Smallest repair tested

RC3B changed only the authority-conferring basis interpretation.

A reference to a `grant`, `policy`, or `delegation` has no operative authority merely because the identifier exists and is current. The reference must resolve to an authority-basis record whose declared bounds cover the request:

- subject/principal;
- authority domain;
- typed operation;
- jurisdiction scope;
- target class;
- exact target identity when the basis is target-specific;
- currentness;
- validity interval.

Supporting artifacts may remain part of a basis chain but do not satisfy the authority requirement by themselves.

The frozen registry is only a research resolver representation. This result does not establish that production Contract E requires a centralized registry. Embedded signed grants, capabilities, policy queries, or other representations remain live alternatives if they preserve the demonstrated bindings.

## OBSERVED — first hosted RC3B pass

First hosted implementation head: `10839714d649ad17745a8b7f4733e6193dda29fc`.

Push run `33330518898`, job `99308141627`: **SUCCESS**.

Artifact:

- id `9737498711`;
- ZIP SHA-256 `ee62ab2950c89b5a5ba8d9fe1eb43302e075dc543df5e2bb7c553a9c179754e6`.

Observed:

- inherited envelope cases: 31;
- direct basis attacks: 13;
- propagation cases: 4;
- delegation cases: 4;
- historical cases: 2;
- semantic-result invariance cases: 27;
- scientific failures: 0;
- negative controls failed in the intended unsafe direction: true;
- semantic result/verdict/confidence/execution-report token hits in the common validator: 0;
- RC3A `N13 supported-does-not-cite`: rejected as `authority_basis_domain_mismatch`;
- RC3A `N14 decision-does-not-execute`: rejected as `authority_basis_domain_mismatch`;
- terminal signal: `CANDIDATE_SURVIVED_RC3B`.

## OBSERVED — preregistered compatibility-matrix hardening

After the first pass, a separate hardening pass was preregistered before its implementation. The RC3B candidate specification, registry, inherited cases, and direct attack set remained unchanged.

Hardening preregistration blob: `1d85e2036d410b3af08d4b2b8926586da8fe6088`.

Accepted hardening head: `1411b3b9ea6baae37b45a0bb3b38c3b13d3dc582`.

Push run `33330612503`: **SUCCESS**.

PR run `33330614847`: **SUCCESS**.

Push-run artifact:

- id `9737525580`;
- ZIP SHA-256 `9b49255cdc15d9a523d4d667cc692aba5adbef05023845f8d8850196f269172b`.

PR-run artifact:

- id `9737525100`;
- digest `sha256:7566995f6a794c8d87b573e3066cf072f0b717b1ecb2a4deb1d00b58ddb09f91`.

Compatibility hardening:

- authority-conferring registry records tested: 15;
- positive baseline requests tested: 9;
- basis-to-request compatibility cases: 135;
- intended canonical accepts: 9/9;
- false accepts: 0;
- false rejects: 0;
- reference-type mutations: 18;
- type-mutation failures: 0;
- hardening scientific failures: 0;
- terminal signal: `RC3B_HARDENING_PASS`.

The original RC3B suite reran unchanged in the same hosted hardening run and again reported zero scientific failures.

## What the challenge established

### 1. Authority basis is itself scoped authority-bearing state

A policy/grant/delegation identifier cannot be treated as a generic trust token.

The authority-conferring object must itself say, or resolve to a record that says, what authority it grants and where that authority stops.

### 2. Warrant and mandate remain distinct

A correct semantic warrant does not repair the wrong organizational/operational mandate.

A correct mandate does not repair an inapplicable/wrong semantic warrant where the domain requires one.

### 3. Competence and mandate remain distinct

A current qualification without an applicable authority basis was rejected.

A valid mandate without the required domain qualification was rejected where the frozen domain required competence.

### 4. Provenance may propagate without authority propagation

Identity/provenance propagation remained allowed under the frozen rules while semantic validity, Decision mandate, citation, task dispatch, and verification authority required re-establishment.

### 5. Historical validity is separable from current permission

Later revocation blocked a new exercise without rewriting a frozen `authority_was_valid_at_time=true` record for an earlier act.

### 6. Semantic strength does not create jurisdiction

Changing semantic result payloads across supported/contradicted/unknown-like shapes did not alter the common authority result.

Positive verdicts, confidence, generic `authorized`, or executor success remained insufficient to manufacture authority.

## Strongest alternative explanations / limits

### The registry may be doing hidden work

The RC3B frozen registry makes basis bounds explicit. This demonstrates the necessary information, not the required deployment topology. A central registry is not established.

### The tested authority vocabulary may still be overfit

The stage/domain set is derived from current CAL Pipeline research. Independent recoverability from the specification has not been established.

### Warrant representation remains provisional

RC3B shows that bounded warrants and bounded mandates can be kept separate. It does not establish that warrants should be durable Contract E objects rather than references to producer policy/method receipts.

### Participant identity vs principal identity is not yet generalized

The tested fixtures mostly use simple subject identities. Acting-on-behalf-of, multi-principal, organizational, and nested delegation cases remain outside this RC.

### No production cryptographic trust model is established

The research uses exact identifiers and frozen records, not signatures, PKI, verifiable credentials, or production revocation infrastructure.

## INFERENCE

The best-supported Contract E research model now has a stronger boundary:

`authority request -> participant responsibility check -> resolve authority-conferring basis -> exact jurisdiction match -> competence/warrant checks where domain requires -> local domain evaluation/enforcement`

The common layer need not determine what CAL evidence means or what Decision policy should conclude. It determines whether the participant, authority basis, domain, operation, scope, and target relation are legitimate enough for the local domain machinery to exercise its own authority.

## Primary falsifier still outstanding

**Independent recoverability.**

This execution designed both candidate and evaluator with full knowledge of prior authority research. It cannot establish that the specification is sufficiently explicit for a competent fresh implementation.

The next experiment must be Context-Free and must freeze the independent implementation before revealing the RC3A/RC3B test vectors or reference outcomes.

## Explicit non-claims

RC3B does not establish:

- Contract E 1.0.0;
- a production schema;
- a centralized production authority registry;
- a universal authority evaluator;
- universal authority domains;
- correct production roles/delegations;
- cryptographic trust roots;
- production CAL/EB/Decision Engine changes;
- automatic execution authorization;
- production promotion.

## Next state

**NEW EXPERIMENT REQUIRED: Context-Free Contract E Authority/Warrant Specification Reproduction.**

Use the separately frozen launch packet. Do not use this thread or the RC3A/RC3B reference validators as implementation guidance.
