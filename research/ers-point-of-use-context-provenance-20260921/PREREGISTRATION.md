# ERS point-of-use context provenance composition

Experiment: `ERS-POU-CTX-20260921-01`
ERS preregistration: [PR #8](https://github.com/camerontjs-dot/epistemic-research-system/pull/8), exact commit `907a10dae0d3d1fc78acbfda3c26a164f3a4693b`
Frozen ERS candidate: `099f84700f28e118734f1ca74feb977da1c4cf17`

This cross-repository reproduction inherits the ERS preregistration and the exact render-bound composition from apparatus-contracts PR #128 (`5fefe7ac3725ccf3a68ff1fa5991ebc14add6856`). It changes no frozen upstream source. It runs the actual PIPE01 Decision and frozen Contract E profile, then requires the RC5 local-supervisor receipt before the write-free ERS point-of-use consumer can return `shadow_ready=true`.

The additional provenance falsifier is deliberately narrow: after the frozen Contract E gate returns its result, alter only the `evaluation_time` field in that result's authorization request to a different timestamp still within the preregistered 30-second freshness window. Ask the pinned observer for the receipt through the normal RC5 consumer path. If the observer signs that caller-selected value and the consumer reaches `shadow_ready`, then the receipt has authenticated the observer's signature and currentness check but has not established provenance of the evaluation time actually used by Contract E.

The qualification uses the exact frozen PIPE01–03 fixtures identified by the PR #128 composition receipt and checked by byte hash at run time, the clean pinned Contract C consumer, and a disposable authority-state fixture. It performs no pending-review write, executor action, MainFrame mutation, effect registration, release, or promotion. The context private key remains outside all repositories.
