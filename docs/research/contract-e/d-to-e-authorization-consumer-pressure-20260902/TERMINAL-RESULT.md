# Contract D → Contract E Authorization Consumer Pressure Test — Terminal Result

Primary disposition: **FALSIFIED**

This is a research disposition. The research branch remains unmerged and authorizes no production behavior, Contract E release, Authorization runtime, execution, or verification.

## Exact experimental lineage

- repository: `camerontjs-dot/apparatus-contracts`
- research branch: `research/contract-d-to-e-authorization-consumer-pressure-20260902`
- experiment base: `c3563cff66d2c85dcbf575c693056e2d8e4563d4`
- original preregistration: `fed51b9cfab1449c1d1ef92049d27e71a1f41eb7`
- original attack harness implementation: `3bc7c6910221c8cf20602305545470a12589cc2f`
- first hosted execution integration head: `79c0918af76c42e66c30831cd30a8d98d146c30c`
- authenticity/provenance extension preregistration: `8624cbf9b974cb6b50cba2a9c7625154a45ef0f0`
- authenticity/provenance extension implementation: `1e3f9a2076e1153db6875425c0550581200b6479`
- final dual-suite hosted head under test: `0c46b7c733b9ebc533b0c68ecd73662012301242`

Pinned authorities:

- Contract D `1.0.0` release commit: `298a1a0f7b7b6d7712e11200d04faec3e1ca169b`
- Contract D core validator blob: `564dcde5677df5ac8f86f21dc0ffd1692f44c9f0`
- Contract D consumer blob: `8b4ad5c9d6fc1145cf334d1416b5d52b9ed93c68`
- Contract D effect registry blob: `a40f4f4447470654bdc16d852f5927189ae30cc5`
- Contract D fixture blob: `66f59bc50e5062aa8550491defa2fee37e75fcc7`
- frozen Contract E RC1 candidate commit: `8876b7bcc2afa1a4902400b0cc507cf2ef02e6e7`
- Contract E RC1 SPEC blob: `3041d31ed0905d50ff355e483fbb9422df994997`
- Contract E RC1 schema blob: `d934d055e39c81e6eb93830e7c6f6f43fc8a0870`
- Contract E RC1 reference blob: `378cdb7835df3959c82a0fe98068b1434b1b68ec`
- Decision Engine live main observed before preregistration: `a4425f8eb47449ff6c683222921bbea9483742e2`

## Hosted result

Accepted final hosted run: `33670053673`.

All research jobs completed successfully on Python `3.11`, `3.12`, and `3.13`. Each job:

1. checked out and verified the exact pinned Contract D and Contract E identities/blobs;
2. compiled both frozen experiment harnesses;
3. executed the preregistered 101-case matrix;
4. executed the separately preregistered five-case authenticity/provenance extension;
5. verified the pinned Contract D and Contract E checkouts remained unmodified;
6. uploaded evidence.

The unrelated existing cross-repository production-acceptance job also completed successfully. That success is regression evidence only and is not the scientific disposition.

Final artifacts:

| Python | Artifact | ZIP digest |
|---|---:|---|
| 3.11 | `9862116687` | `sha256:9d602181af6a1f907177787c72c33ddbb303598aa9ec18e961ad70cd6fffadd2` |
| 3.12 | `9862120822` | `sha256:1ddb0e1f029d3d61100807183d1a2b894eb5b2d4863b405606dc58220d2f6362` |
| 3.13 | `9862117980` | `sha256:6d32083dd64aeb1db8227445d50226ac6af998b724086184b27eae993830f7bb` |

Across all three runtimes, the extracted result files were byte-identical:

- original `RESULTS.json`: SHA-256 `89aa1c562ad93348ace31650041a15a4eb509aafc019abe914e6316603d8095b`
- `AUTHENTICITY_RESULTS.json`: SHA-256 `df80042fc179622763fa3ca2e519426b27b49c710869818d07605c3d02b5cc20`

## Bounded result that survived

The original 101-case mutation/metamorphic matrix passed **101/101** on every runtime.

Supported only for the exact frozen reference/profile under test:

- exact released Contract D CLEAR plus exact applicability reaches only `candidate_for_authorization`;
- HOLD, failed evaluation, non-applicable, malformed Decision/expectation do not cross the adapter;
- target/policy/upstream/operation/effect-parameter substitution is rejected;
- Contract D metadata excluded from semantic identity does not create stronger downstream authority;
- the exact Contract D Decision can be preserved as non-conferring support while the adapter independently requires exact D applicability;
- D candidate/support and prior AuthorizationReceipt cannot replace standing AuthorityState;
- exact human and exact machine subject binding rejects cross-subject reuse;
- exact domain/operation/scope/target binding rejects substitution;
- currentness, inclusive validity boundaries, and revocation behave as expected;
- non-amplifying linear delegation works and delegation/lineage attacks reject;
- relevant unresolved/contested conflicts/residues block while irrelevant items remain preserved and non-blocking;
- malformed/unknown request fields, forged reference identity, duplicate IDs, missing target references, and bare resolved-ID claims reject;
- machine `ExecutionIntent` identity changes for every preregistered authority-relevant mutation: executable digest, entry point, arguments, input identities, environment, executor, requested operation, effect parameters, Decision identity, and Decision target;
- old receipt replay across subject/target/operation/AuthorityState changes rejects under exact request binding;
- a historical authorized machine receipt does not survive current revocation when the point-of-use gate re-evaluates current AuthorityState;
- all five deliberately weak strategies produced the intended false permits and were therefore discriminated by the evaluator.

These are useful bounded subclaims. They do not overcome the falsifier below.

## Decisive falsifier: integrity/binding is not origin authentication

The separately frozen authenticity/provenance extension passed its five expected observations on every runtime and produced finding:

`PROVENANCE_AUTHENTICITY_BOUNDARY_REQUIRED`

### F1 — forged-but-internally-valid Contract D CLEAR

A valid Contract D HOLD fixture was fabricated into a new internally valid CLEAR Decision. The exact released Contract D validator/consumer accepted the fabricated object as `candidate_for_authorization` when evaluated against expectations derived from those fabricated bytes.

This is not a Contract D defect under its current contract. Contract D validates semantics and deterministic identity; it does not authenticate that a trusted Decision Engine invocation produced the object.

**Required consequence:** the D→E integration profile must carry or enforce a trusted Decision-origin boundary. Contract D validity/semantic identity alone is insufficient.

### F2 — fabricated self-consistent root AuthorityState

A new attacker-selected root `grant` was fabricated and given its correctly recomputed AuthorityState content identity. Frozen Contract E RC1 authorized the matching request.

This is explicitly within RC1's stated external trust/configuration boundary rather than a surprise reference-implementation bug.

**Required consequence:** AuthorityState must enter from an explicitly trusted root/configuration/provenance channel. Its SHA-256 identity proves content binding, not entitlement to create the root grant/policy.

### F3 — forged `authorized=true` receipt

A denied AuthorizationReceipt was fabricated into `authorized=true` with a plausible `authority_basis_id`; its deterministic semantic receipt ID was then recomputed. A consumer checking only request binding + receipt self-hash accepted the forged receipt.

**Required consequence:** receipt self-hash does not authenticate which evaluator produced it. A receipt-only human or machine consumer is unsafe unless evaluator provenance is independently trusted.

### F4 — fresh point-of-use evaluation defeats forged receipt

Fresh Contract E evaluation of the actual denied AuthorityState/request remained denied despite the forged receipt.

**Supported successor constraint:** point-of-use re-evaluation is the smallest currently demonstrated way to avoid relying on unauthenticated receipt bytes, especially for machine execution.

### F5 — diagnostic text remains non-authoritative

Diagnostic-only mutation does not alter receipt semantic identity, as intended.

## Independent Contract E RC1 falsifier observed during this experiment

A separate context-free reproduction completed while this experiment was running:

- repository: `camerontjs-dot/research-scaffold-harness`
- PR: `#14`, closed unmerged
- frozen implementation: `75e22edf20c531fb50ed47cb1d199dfa15a5a6b8`
- terminal record: `d1e3c6998b20db845cdce8b4b39df90485c27e7d`
- sealed evaluator: `ee47670104776f627b7c337c6235dabafe03c874`
- result: `48/50` normative exact matches
- mismatches: `NEG-SUPPORT-CANNOT-CONFER`, `NEG-STATE-ID`
- false permits: `0`
- false rejects: `0`
- terminal state: **FALSIFIED**

The two mismatches are one denial-receipt identity semantic disagreement. Both implementations deny the attacks. For invalid/forged AuthorityState input, frozen RC1 emits the supplied/claimed `authority_state_id`, while the independent implementation emits the recomputed canonical AuthorityState identity. Because that field participates in receipt semantic identity, exact recovery fails.

The Contract E closure record PR #70 reconciles the public specification as underdetermined here: the spec says a denial receipt carries the AuthorityState identity but does not determine whether that means the claimed/supplied identity or recomputed content identity when validation fails.

This result independently blocks any claim that RC1 is stable enough to serve as production Authorization machinery.

## Why the primary disposition is FALSIFIED

The candidate integration profile was meant to be a safe downstream profile, not merely a demonstration that a particular reference implementation rejects common substitutions.

The original matrix established strong local binding behavior, but the authenticity extension identified an unmodeled trust assumption that can produce fabricated but self-consistent Decision, root-authority, and receipt artifacts. In addition, the Contract E substrate itself failed exact independent recoverability on denial-receipt identity semantics.

Therefore the tested profile, as originally specified, is not supported for promotion.

This does **not** falsify the architecture:

`Decision → exact action + exact subject → Authorization → human/machine point-of-use`

It falsifies the assumption that deterministic content/semantic identities alone close the trusted-origin boundaries needed to operate that architecture safely.

## Smallest successor supported by the evidence

A successor should change only the demonstrated gaps.

### 1. Contract E receipt identity clarification

For invalid AuthorityState input, preserve both facts rather than choosing one and discarding the other:

- claimed/supplied AuthorityState identity;
- recomputed canonical AuthorityState identity when recomputation succeeds.

This is a material normative/schema successor and requires a separately frozen candidate, new evaluator qualification/seal, and fresh independent reproduction. It must not repair RC1 in place.

### 2. Trusted-origin profile outside semantic content hashes

A D→E runtime must explicitly establish:

- trusted origin of the Contract D Decision, e.g. consumption directly from a trusted/pinned Decision Engine invocation or separately authenticated provenance channel;
- trusted origin/configuration of AuthorityState root authority;
- trusted Contract E evaluation at point of use, or independently authenticated evaluator provenance if stored receipts are consumed as authorization evidence.

No cryptographic scheme, signature format, PKI, attestation framework, or deployment topology is selected by this evidence.

### 3. Consumer posture

For the smallest successor, prefer fresh point-of-use Contract E evaluation for both human handoff creation and machine execution. For machine execution, continue binding exact immutable ExecutionIntent and re-evaluate current authority immediately before use.

A later reusable permit/lease/token design is not supported by this experiment.

## Preserved apparatus deviations

1. A new standalone workflow added only on the research branch did not immediately execute on initial PR creation because it was not yet registered on the base branch. No scientific case had run at that point.
2. To obtain hosted evidence without merging research infrastructure, the pressure job was additively attached on the research branch to an already base-registered PR workflow. The pre-existing production-acceptance job was retained unchanged and also passed.
3. Later pushes caused the standalone research workflow to become schedulable as GitHub registered it. Those executions are supplementary; the accepted dual-suite evidence is run `33670053673`.

These are Actions/control-plane deviations, not scientific passes or failures.

## Nonclaims

This result does not establish:

- Contract E production readiness or `1.0.0`;
- independently recoverable RC1 receipt semantics;
- trusted root grant legitimacy;
- trusted Decision producer identity from Contract D bytes alone;
- trusted evaluator identity from receipt bytes alone;
- a cryptographic authenticity mechanism;
- role/group/wildcard authorization;
- reusable permit/lease semantics;
- exactly-once execution or distributed locking;
- execution occurrence/correctness;
- verification occurrence/correctness;
- Qualification semantics;
- surplus peer authority-conferring aggregation;
- CAL or Decision policy correctness.

## Terminal state

**FALSIFIED.**

Close this research PR unmerged after the terminal record is committed. Any successor must be separately preregistered and must not rewrite this candidate's evidence into a pass.
