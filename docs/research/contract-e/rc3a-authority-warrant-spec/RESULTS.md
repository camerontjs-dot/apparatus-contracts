# Contract E Authority / Warrant Specification RC3A — Results

## Classification

Research / apparatus-contract architecture falsification.

## Primary disposition

**FALSIFIED**

The frozen RC3A specification did not adequately bind an `authority_basis` object to the exact authority domain / operation / jurisdiction it was supposed to authorize.

This falsifies the frozen candidate specification, not the broader hypothesis that a shared authority/warrant interface is possible.

## Frozen candidate

- preregistration: `94b69329c93b91337a293f9b8ce0e6890f561b01`
- candidate/fixture freeze commit: `c21454ad474a3beefa4bd7bd5baaf29f75188419`
- freeze tree: `23a7afec0a40d9a4acffb66065a3185841f34090`
- freeze receipt commit: `f640294b69f91508b3b300ce6a9bca5a762c1549`

## Hosted execution

PR workflow run: `33330202618`

Job: `99307302138`

Research step conclusion: failure, as scientifically expected for the observed counterexamples.

Artifact:

- id: `9737409060`
- ZIP SHA-256: `00b949c72fc4a54e8ca3d70be0c046ff5df14ce822c885988a8a309050eb28b7`

The frozen spec/case hashes and mutation-surface guard passed before the scientific validator executed.

## Observed results

Summary:

- envelope cases: 31;
- propagation cases: 4;
- delegation cases: 4;
- historical cases: 2;
- semantic-payload invariance cases: 27;
- negative controls failed in the intended unsafe direction: yes;
- scientific failures: 2;
- terminal signal: `CANDIDATE_FAILED_RC3A`.

### Failure 1 — policy basis laundering into citation authority

Frozen case `N13-supported-does-not-cite` expected rejection.

The case began from a CAL assessment envelope, then changed the participant/domain/operation to:

- participant: `citation-agent`;
- domain: `citation_use`;
- operation: `citation.use`.

The original CAL policy basis remained:

`policy:cal-assessment`.

Because the frozen common basis shape required only `type`, `id`, and `current`, the validator had no specification-level fact establishing that this policy was scoped only to `assessment_mandate` / `assessment.issue` / its original jurisdiction.

Observed result: **accepted**.

This is a genuine authority-laundering counterexample.

### Failure 2 — task substitution rejected for incidental reason

Frozen case `N14-decision-does-not-execute` expected rejection because a Decision mandate is not an execution grant.

Observed rejection reason was `warrant_not_allowed_for_domain`, because the mutated object still carried the Decision policy warrant while the task-dispatch domain forbids warrants.

The candidate therefore rejected the case, but **not because the retained Decision policy basis was proven inapplicable as execution authority**.

This is evidence that the same authority-basis binding hole remains even where another field happens to stop the attack.

## What survived the challenge

The following frozen distinctions survived the encoded tests:

- competence did not substitute for mandate in `N01`;
- mandate did not substitute for required competence in `N02`;
- cross-domain / stale / wrong-target warrants were rejected;
- participant-domain substitution was rejected;
- unknown domains failed closed;
- generic `authorized: true` did not recover missing authority;
- identity/provenance propagation could occur without semantic/action authority propagation;
- delegation amplification by operation, scope, or expiry was rejected;
- later revocation invalidated a new exercise without rewriting an earlier valid-at-time historical record;
- 27 result-payload mutations left common authority decisions unchanged;
- collapsed-authority, transitive-inheritance, and credential-only negative controls all produced unsafe permits in the intended direction.

These are retained observations, but they do not rescue the frozen specification from the authority-basis counterexample.

## Smallest missing authority

An authority basis cannot be a bare current credential/policy/grant identifier.

At minimum, the next candidate must bind the basis itself to enough of the following to prevent repurposing:

- authority domain;
- authorized operation/effect set;
- subject/principal/delegate;
- jurisdiction scope;
- target class and, where required, exact target identity/currentness;
- validity interval/currentness;
- parent/delegation identity where applicable.

The common validator should compare the requested envelope against those declared basis bounds without interpreting the semantic result payload.

## Non-claims

RC3A does not falsify:

- the broader cross-cutting authority-interface hypothesis;
- typed semantic authority;
- warrant as a distinct inference relation;
- explicit non-transitive propagation;
- a future Contract E research specification.

It does falsify the **specific frozen RC3A basis shape** as sufficient.

## Next discriminating test

Create a new freeze, RC3B, that changes only the authority-basis representation/binding required by this failure, then rerun the same attack family plus direct basis substitutions.

Do not repair the RC3A frozen files in place.
