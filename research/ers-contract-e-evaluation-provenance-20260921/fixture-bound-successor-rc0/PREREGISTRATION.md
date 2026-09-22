# Fixture-bound Contract E evaluation-time provenance successor — preregistration

## Experiment

`ERS-EVAL-TIME-PROV-20260922-05`

## Classification

Scientific successor preregistration only.

This successor preserves the scientific question and decisive controls from apparatus PR #130. It changes the fixture authority boundary exposed by qualified recovery PR #138.

No Contract E evaluation, supervisor launch, ERS shadow execution, executor action, pending-review write, or MainFrame mutation is authorized by this preregistration commit.

## Predecessor evidence

The frozen PR #134 apparatus remains blocked before scientific runner launch because it required a fixture root whose authority was not established.

Fixture-recovery PR #138 subsequently qualified the complete required layout with disposition:

`QUALIFIED_FIXTURE_RECOVERY_RC2`

Exact recovery subject:

- recovery candidate: `510e9a586a015ad5b825318d0908601baf98d55a`
- tree: `5373e38b744ec100cc61d6188ed83ca4522070aa`
- hosted run: `35779664920`
- hosted artifact: `10717946190`
- artifact digest: `sha256:a0aae7095994051cdc8fb229701541a55ae7798d00ffa5104a6019c4afc95790`
- manifest: `sha256:43dd34ef801b8b4f8aafcf13f482a1107033c04d40760e44e13307f2d6c779c2`
- verification JSON: `sha256:999a1c2aa8c10dd768d02a2233d557a102d2e578b6ff5602b55da1c912f26c85`
- composition result: `sha256:2ef133c504cd33bf5b9912acb06e154b43d7060b967dd4230081d4a8ad4f9753`

Local and hosted fixture bytes matched exactly.

## Authority change

The recovered bundle is a mixed-authority fixture.

For every PIPE case:

- `cal/contract-c.json` is byte-matched to the surviving historical PR #123 artifact.
- `contract-d.json` is byte-matched to the surviving historical PR #123 artifact.
- `consumer-inputs.json` is deterministically reconstructed without a preserved historical reference.
- `decision-target.json` is deterministically reconstructed without a preserved historical reference.

The successor therefore does **not** reinterpret the reconstructed files as historical bytes.

Instead, this experiment explicitly freezes those reconstructed bytes as part of the new scientific subject.

The complete machine-readable authority is:

`fixture-bound-successor-rc0/FIXTURE_AUTHORITY.json`

## Frozen scientific question

Unchanged from PR #130:

Can the frozen Contract E → ERS shadow composition bind an independently sourced evaluation time to the exact Contract E invocation and exact Contract E result, so that changing the result time after evaluation is rejected before `shadow_ready`?

## Frozen scientific machinery

This preregistration does not authorize changes to the PR #134 scientific runner.

Required runner blob:

`35bf0e98d7575b9db7ffe2f6906aff757e865e72`

Required receipt-preflight blob:

`e7e94523bff84792d355ef2a6da805a91919e076`

The PR #130 decisive controls remain unchanged, including:

- authentic PIPE01 path;
- +1 second result-time mutation without rerunning Contract E;
- cross-paired authentic result/transcript attempts;
- one-byte result mutation;
- wrong execution intent;
- wrong authority state;
- wrong issuer;
- stale transcript;
- replayed challenge;
- caller-supplied time/result injection attempt;
- PIPE02 expected HOLD;
- PIPE03 expected HOLD.

Any prohibited mutation reaching `shadow_ready=true` remains a falsification.

## Required pre-execution fixture gate

Before any scientific runner launch, an independent non-evaluating gate must establish all of the following against the actual fixture root supplied to the runner:

1. the root contains exactly the required four fixture files per PIPE case;
2. all twelve fixture files match the exact byte identities in `FIXTURE_AUTHORITY.json`;
3. the manifest and verification-receipt bytes match their frozen digests;
4. each file's provenance classification matches the frozen authority record;
5. the scientific runner blob remains exactly `35bf0e98d7575b9db7ffe2f6906aff757e865e72`;
6. no Contract E evaluation, supervisor launch, candidate runtime import, network recovery, or fixture regeneration occurs during this gate.

The gate must fail closed on any mismatch.

## Freeze rule

Implementation of the fixture gate must occur only after this preregistration is frozen as an ancestor.

The executable successor must then be frozen before decisive execution.

A qualification receipt must demonstrate that the fixture gate itself is non-evaluating and that the scientific runner bytes are unchanged.

## Stop conditions

Stop before scientific execution if:

- any fixture byte differs;
- provenance classification differs;
- manifest or verification receipt differs;
- the runner or existing scientific dependency identity moves;
- the gate imports or executes scientific candidate code;
- the gate itself changes fixture bytes;
- the recovered artifact cannot be established independently.

Preserve the first failure. Do not repair around it in the same frozen candidate.

## Nonclaims

This preregistration does not claim that reconstructed `consumer-inputs.json` or `decision-target.json` files are historical artifacts.

It does not strengthen the production-shaped A→D evidence.

It does not authorize production promotion, Contract D effect registration, an executor, ERS write behavior, or MainFrame mutation.

It does not itself provide a scientific result about evaluation-time provenance.
