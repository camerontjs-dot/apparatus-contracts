# Contract E v1 Pre-Promotion Candidate RC1 — Freeze Receipt

Freeze classification: **research-only pre-promotion candidate**

Frozen candidate commit: `8876b7bcc2afa1a4902400b0cc507cf2ef02e6e7`

The commit above is the immutable candidate freeze. Later evidence/metadata/apparatus commits on this branch MUST NOT be interpreted as changing the frozen candidate unless a successor candidate is explicitly named.

## Frozen public/normative candidate surface

| File | Git blob | SHA-256 |
|---|---|---|
| `candidate/SPEC.md` | `3041d31ed0905d50ff355e483fbb9422df994997` | `499b30f4d9d9f29b4c60a7e0d84465e3a09b13972a230b728117024da9d12841` |
| `candidate/schema.json` | `d934d055e39c81e6eb93830e7c6f6f43fc8a0870` | `eefe62ff98295f72457c4cc427c398f942afc81954c8d6afff2410652f56a07b` |
| `candidate/reference.py` | `378cdb7835df3959c82a0fe98068b1434b1b68ec` | `2b9ddbc5f6e51fffedcca1bcc33983113dbff995a476afe0608d7bf1dc58b643` |
| `candidate/test_candidate.py` | `39462a06c30aa312d3055d93d65a287688a89086` | `4f6dcc40cb27151f1b374a8fc847842685fc64ef8ac5a78bc8b93360cf2080e0` |

`PREREGISTRATION.md` and `OBLIGATION-MATRIX.md` were committed before implementation and remain part of the evidence lineage, but the four files above are the frozen candidate/apparatus bytes used by the accepted run.

## Accepted bounded candidate gate

- workflow: `.github/workflows/research-contract-e-v1-closure.yml`
- run: `33634217533`
- job: `100260885647`
- result: `success`
- artifact: `9848066163`
- artifact digest: `sha256:2ae3f8f4848e5993976adb14294137f63d2e520eac031e37f7c11e9900385a61`

Observed hosted gates:

- exact canonical A release commit verified: `529c92b49a34d5c610618551a8737f019f9fa332` (`contract-a-v2.0.0`);
- exact canonical B release commit verified: `c314e53bd91c0736aa4370a364673b069aceb43e` (`contract-b-v1.2.0`);
- exact canonical C release commit verified: `5fe55f9ed5d0ee9f026ca1b077e9d70ce0487ea1` (`contract-c-v1.0.0`);
- exact canonical D release commit verified: `298a1a0f7b7b6d7712e11200d04faec3e1ca169b` (`contract-d-v1.0.0`);
- candidate schema JSON parsed successfully;
- bounded adversarial/pipeline-boundary suite passed;
- seeded weak controls caught: `6/6`;
- released A-D immutable reference identities exercised: `4/4`.

## Frozen semantics

The candidate is intentionally smaller than the prior RC1 authority-chain research object.

It freezes:

- separately supplied immutable standing `AuthorityState`;
- exactly one complete linear `grant|policy -> delegation*` chain per state;
- exact scalar subject/domain/operation/scope/target binding;
- exact immutable target/reference identity;
- explicit currentness, validity interval, and revocation;
- non-amplifying delegation that changes subject only;
- separate non-conferring supporting artifacts;
- fail-closed relevant conflict/residue blockers;
- separate authorization of `resolution/resolve` without claiming resolution occurrence;
- AuthorizationReceipt as deterministic but explicitly non-conferring;
- strict missing/malformed/unknown/future Contract-E fail-closed behavior;
- opaque immutable A-D references without semantic rewriting;
- explicit Decision / Authorization / execution / verification separation;
- non-authoritative diagnostics excluded from receipt semantic identity.

It excludes Qualification semantics, competence as an authority predicate, peer/surplus conferring-record quantification, partial-record synthesis, delegation `any-of`/containment/inheritance, comparison truth promotion, composition/embedding semantics, bare resolution-ID discharge, automatic execution, and automatic verification.

## Known underdeterminations

No owner semantic decision is required for this freeze because the known unresolved predicates are absent by construction:

- Qualification subject/scope binding from #58 is not part of the v1 authority predicate;
- the #59 surplus-record quantifier is not evaluated because one AuthorityState contains exactly one linear chain;
- delegation domain/scope `any-of` is not representable.

These are bounded exclusions, not silently chosen defaults.

## Independence consequence

This frozen candidate is **materially different** from the authority-chain object independently implemented in RSH #9. RC1's fresh result therefore cannot establish independent recoverability of this candidate.

A new mechanically bounded context-free independent reproduction is required before a `SUPPORTED FOR BOUNDED E PROMOTION` claim can be made.

Do not expose `candidate/reference.py`, `candidate/test_candidate.py`, historical RC0/RC0B/RC1 implementations, evaluator cases, or expected outcomes to the fresh implementer before its independent implementation freeze.

No production promotion, canonical Contract E tag, release, execution authorization, or A-D semantic change is authorized by this receipt.
