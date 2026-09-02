# Contract E RC2 successor — freeze receipt

Status: **FROZEN NORMAL-CONTEXT CANDIDATE**

This receipt freezes the candidate that survived the preregistered normal-context successor tests. It does not establish independent recoverability, production promotion, Authorization, execution, or verification.

## Candidate freeze

Repository: `camerontjs-dot/apparatus-contracts`

Branch at freeze: `research/contract-e-v1-successor-rc2-20260902`

Frozen commit:

`44c919ea7f571b9a01ccf420ac710822c29476e4`

Frozen tree:

`95e54858616fd0bc10c07762f571367255e48140`

All subsequent evaluator, seal, and clean-room work must treat the files below at this exact commit as immutable. A later repair requires a separately named successor and new freeze.

## Frozen public/core candidate

- `candidate/SPEC.md`
  - Git blob: `90bfa10fda928796f9b14c6a430ee12e412d9e3e`
- `candidate/schema.json`
  - Git blob: `ababc25a6dc9fc938251df57bea3ddcc3dd78850`
- `candidate/reference.py`
  - Git blob: `fda14bb18c66c51747b7b506abb8df8a55a8d166`
- `candidate/test_candidate.py`
  - Git blob: `7b51b8ad8e7523d29b45a153a6427934cb5661f5`

Public clean-room aperture, if later authorized, must include the frozen `SPEC.md` and `schema.json`, plus separately frozen task instructions. It must not expose `reference.py`, tests, evaluator, hidden cases, prior expected outputs, or this normal-context reasoning.

## Frozen downstream integration profile under test

- `integration_profile.py`
  - Git blob: `6f19875d4f21765e02d51fef50ca53fae3daf177`
- `test_integration_profile.py`
  - Git blob: `7c84806033a80b93c08d51492dce265a29dc2b40`
- `run_integration_superset.py`
  - Git blob: `8cd53b679f39f6b08a5184eb3133f3c7d610eb2c`
- `canonicalization_probe.py`
  - Git blob: `7f045533f7837835ef59d59ebbcf90a01c2ccded`
- `PREREGISTRATION.md`
  - Git blob: `212c65df29a46f238ac61153f6447fc7a4140ac0`
- `APPARATUS-DEVIATIONS.md`
  - Git blob: `167d3541803df4197e23c3957029d3a255ab4068`

## Exact external authority

Contract D 1.0.0:

- release commit: `298a1a0f7b7b6d7712e11200d04faec3e1ca169b`
- core validator blob: `564dcde5677df5ac8f86f21dc0ffd1692f44c9f0`
- consumer blob: `8b4ad5c9d6fc1145cf334d1416b5d52b9ed93c68`
- effect registry blob: `a40f4f4447470654bdc16d852f5927189ae30cc5`
- valid-fixture collection blob: `66f59bc50e5062aa8550491defa2fee37e75fcc7`

## Accepted normal-context successor run

Run: `33674531115`

Exact head: `44c919ea7f571b9a01ccf420ac710822c29476e4`

Results:

- Python 3.11: success
- Python 3.12: success
- Python 3.13: success
- RC2 core controls: `57`
- integration/pressure controls: `121`
- frozen Contract D identity checks: pass
- tracked source mutation check: pass

Artifacts:

- Python 3.11: `9863816819`, digest `sha256:4d9397e71362b9d008ac4c45c128a492e7d9b73eadd1e1fa9c7c72f424c412c5`
- Python 3.12: `9863816019`, digest `sha256:d7a74171aa7411c6692f3cf675217c4ef4cbdc4e0ee3b998ddd0284b303fb51d`
- Python 3.13: `9863817081`, digest `sha256:a5a09fbbb43b90c3c533ac71bc486f6d778bdf2da384fb896d28176a9820a92b`

The pressure surface includes exact Contract D applicability and mutation combinations; trusted Decision and AuthorityState bindings; human/machine subject and jurisdiction separation; blocker preservation; currentness/revocation and point-of-use re-evaluation; forged Decision/root/receipt attacks; operation-inflation rejection; and immutable ExecutionIntent mutation sensitivity.

## Accepted canonicalization discriminator

Run: `33674531214`

Exact head: `44c919ea7f571b9a01ccf420ac710822c29476e4`

Artifact: `9863818096`

Artifact digest: `sha256:2d142b1cd61a6d51866434001e1c56c53d9e1c42aa936c55900a1916c392d1bc`

Result:

- valid-state candidate bytes vs RFC 8785 + LF: agree;
- malformed numeric probes `1.0`, `-0.0`, `1e-6`, `1e20`: all agree after the RFC 8785 correction;
- divergent case IDs: none;
- probe status: `NO_DIVERGENCE_OBSERVED`;
- pipefail enabled, so semantic probe failure would fail the job.

## Preserved pre-freeze deviations/counterexamples

The frozen record includes, rather than erases:

1. initial integration run `33673708516`, where 112 substantive assertions passed before an erroneous arbitrary `>=120` count sentinel failed; repaired by adding eight real malformed-ExecutionIntent controls without removing or weakening original assertions;
2. canonicalization probe run `33674136989`, which found four real serializer divergences under the initial RC2 wording;
3. that initial probe workflow omitted pipefail and therefore displayed green despite the probe's `AMBIGUITY_DETECTED` exit; the payload was treated as the evidence and the gate was repaired;
4. RC2 then adopted RFC 8785 + exactly one LF, followed by the full successor rerun and repaired discriminator above.

## Frozen semantic claims supported for evaluator qualification

The normal-context evidence supports advancing these exact claims to a sealed evaluator:

1. RC2 preserves both claimed and recomputed AuthorityState identities and removes the RC1 single-field denial ambiguity in the reference behavior.
2. RC2 authorization predicate remains bounded to standing AuthorityState + exact request and does not infer root legitimacy from hashes.
3. The downstream profile can require explicit caller/configuration trusted bindings for exact D Decision identity and exact AuthorityState recomputed identity without making those hashes themselves proof of origin.
4. Contract D requested operation is exactly bound to the Contract E operation, preventing generic authority inflation.
5. Fresh point-of-use Contract E evaluation prevents prior or forged receipts from independently authorizing current human handoff or machine execution.
6. Machine execution is bound to a recomputed immutable ExecutionIntent identity; authorization is not execution occurrence.
7. RC2 canonical identity is RFC 8785 JCS bytes plus exactly one LF.

## Next gate

This candidate may now enter evaluator qualification. The evaluator and hidden cases must be frozen and sealed before any fresh independent implementation exists.

The maximum current disposition is **NORMAL-CONTEXT CANDIDATE FROZEN FOR EVALUATOR QUALIFICATION**. It is not yet `SUPPORTED_FOR_FRESH_REPRODUCTION` because evaluator qualification/sealing has not yet occurred.
