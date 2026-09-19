# ERS output-payload binding exploratory falsifier

Status: exploratory post-RC2 discriminator, not preregistered qualification.

## Exact subjects

- Contract E / ERS point-of-use RC2:
  `b153dcc4434cbe8a98616a9e410c6125378144c7`
  - Apparatus Draft PR #117
  - disposition: `SUPPORTED_FOR_BOUNDED_CROSS_REPOSITORY_POINT_OF_USE_RC2`
- exact ERS point-of-use consumer:
  `73a47dc0ce2e3ae6c7aa6e55c4183e223797724b`
  - epistemic-research-system Draft PR #2

## Question

Does the RC2 authorization/consumer seam bind the exact bytes that a future ERS
pending-review executor would write?

This question is intentionally narrower than RC2. RC2 established a bounded
write-free handoff:

`typed Contract D decision -> immutable ERS intent -> fresh Contract E authorization -> ERS point-of-use checks -> shadow-ready`

It did not claim that exact output bytes were authorized.

## Observed counterexample

The exact RC2 permit was constructed and accepted by the exact ERS consumer.
Two different candidate pending-review payloads were then considered:

- payload A and payload B have different SHA-256 identities;
- neither payload hash appears in the execution intent;
- neither payload hash appears in the Contract E shadow result;
- `consume_shadow_authorization` accepts no payload or payload-identity argument.

Therefore the same valid authorization is compatible with multiple distinct
candidate output byte streams.

Disposition:

`FALSIFIED_EXECUTION_PAYLOAD_UNBOUND`

This does not falsify RC2's bounded shadow-consumption claim. It falsifies the
stronger claim that RC2 is sufficient to authorize an executor to write exact
pending-review bytes.

## Additional implementation evidence

The current ERS promoter renders a larger markdown artifact than the source
claim alone. Its bytes depend on claim metadata, confidence, credibility,
evidence, contradictions, audit history, tags, source links, and the current
date.

Current evidence and contradiction DAO reads do not specify `ORDER BY`.
Revision history does specify `ORDER BY changed_at ASC`.

Consequently, binding only the claim-content SHA is insufficient to bind the
rendered pending-review artifact.

## Smallest justified successor

Before adding any executor, freeze a deterministic render packet containing the
complete ordered render snapshot plus an explicit render date/time input.

A successor should demonstrate:

1. the render packet is immutable and independently identifiable;
2. rendering the same packet produces byte-identical output;
3. mutation of any render-relevant field changes the payload SHA;
4. the exact output payload SHA is carried inside the execution intent;
5. Contract E authorization therefore binds target + pre-state + decision +
   exact output bytes;
6. the point-of-use consumer rejects a payload SHA that differs from the
   authorized intent.

Only after that should a disposable create-only executor be tested.

## Non-claims

This record does not justify:

- changing released Contract D effect semantics;
- a real ERS executor;
- real MainFrame mutation;
- merge, release, or production promotion;
- treating current DAO ordering as deterministic;
- treating the claim-content SHA as equivalent to rendered-output identity.
