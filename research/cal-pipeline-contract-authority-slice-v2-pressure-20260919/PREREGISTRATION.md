# CAL Pipeline contract-authority slice v2 pressure test

Date: 2026-09-19

Classification: Research Infrastructure / integration assurance. This branch may add only pressure-test apparatus and evidence. It may not modify the frozen slice, released contracts, Contract C successor subjects, Decision Engine, Contract E, or any production runtime.

## Exact subject

Frozen slice PR #116 head:

`79aa0527b52deaa748947514202c9a415b5f0e23`

The subject is the v2 handoff added at that head, including the preserved v1 authority freeze and the newly pinned Contract C successor lane.

## Question

Can a consumer distinguish the released authority lane from the C2 research-successor lane under identity substitution, semantic-status mutation, canonical-discovery mutation, and clean-room-aperture contamination, while all pinned Git identities remain exact?

## Preserved predecessor deviations

Apparatus PR #119 pressure run `35445510257` failed before its intended discriminators:

1. Gate CLI invocation ran from a working directory where its frozen predecessor vendor path was absent, despite the exact predecessor-fetch script having populated the Gate checkout.
2. Decision CLI's exact Contract C checkout was shallow and did not contain immutable tag `contract-c-v1.0.0`, so its authority identity check failed closed.

Those failures remain evidence. They are not contract falsifiers and are not rewritten as passes here.

This successor does not depend on either setup shape for its primary v2 authority discriminator.

## Frozen invariants

The test must establish all of the following without changing the subject:

- original `FREEZE_RECORD.md` and `SLICE_MANIFEST.json` Git blobs remain exactly `01fafba3b4924bcd0394bfc5530c2d525eb6ba1e` and `b66702df8a1f0f272ef113d14897aa01778af0a2`;
- all 22 v1 normative pins still match both their exact release commits and the consolidated carrier `c3563cff66d2c85dcbf575c693056e2d8e4563d4`;
- the C2 production-shaped candidate is exactly `b42c827acb0a9fe65353354d709add0e27bab307`;
- every C2 file blob pinned by `SLICE_MANIFEST_V2.json` matches that exact checkout;
- C2 global discovery still says canonical `1.0.0`, supported only `1.0.0`;
- C2 `promotion-version.json` still has `canonical_registry_switch_authorized=false`;
- PR #118 terminal record stays `SUPPORTED_FOR_INDEPENDENT_CONSUMER_APERTURE`, with exact candidate/evaluator/preregistration/workflow blob identities;
- RSH aperture `52869e08f98ebaaf4acd31dd5955874f7fdaec81` contains only the five frozen aperture files and no candidate/result/evaluator output;
- the v2 manifest accepts the honest state and rejects all preregistered authority-laundering mutations;
- a deliberately weak JSON-only consumer accepts those same mutations, proving the mutation cohort is semantically discriminating rather than syntactically invalid.

## Preregistered mutations

The strong handoff verifier must reject:

1. authority lane changed from C1 to C2;
2. C2 successor marked admitted to the authority lane;
3. C2 canonical discovery changed to 2.0.0;
4. independent-consumer blocking flag cleared;
5. independent-consumer state relabelled as completed/pass;
6. PR #118 disposition upgraded to `SUPPORTED_FOR_PROMOTION`;
7. exact C2 candidate head substituted;
8. Contract E marked included;
9. preserved v1 manifest blob substituted;
10. successor hard stop removed;
11. successor lane removed;
12. released Contract C entry silently changed from 1.0.0 to 2.0.0.

## Falsifiers

The pressure test fails if any exact pin does not resolve, any historical freeze blob changed, C2 is already advertised as canonical, the clean-room aperture contains post-freeze/candidate contamination, the honest v2 manifest is rejected, any preregistered mutation is accepted by the strong verifier, or the weak consumer does not accept all syntactically valid mutants.

## Interpretation ceiling

A green result establishes only that the frozen v2 handoff is internally and externally pinned strongly enough to preserve the current authority/research distinction under this mutation cohort.

It does **not** establish the missing fresh independent consumer, C2 promotion/release, Decision support for the parent-binding successor, Contract E, Authorization, execution, or end-to-end production readiness.
