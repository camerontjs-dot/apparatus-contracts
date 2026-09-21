# CAL Pipeline v3 to ERS RC3 shadow composition boundary

Date: 2026-09-21

Disposition: `BLOCKED_FROZEN_DECISION_BOUNDARY_CANNOT_EXPRESS_ERS_OPERATION`

## Question

Can the frozen CAL Pipeline v3 artifacts through Contract C, under an ERS-specific downstream Decision context or policy, natively produce a typed Contract D decision for `epistemic_audit.stage_pending_review@1`, then pass that decision unchanged through the existing research-local Contract D effect profile, Contract E, and ERS RC3 slice `319e325cdf678673fae645a70e3e34afb7dddef0`?

## Result

No. I stopped at the frozen Decision boundary and did not force the composition.

The parent-bound Decision candidate `6cdb59c2ba41779ac954af56dd077574ba090013` has no context or policy input that selects `epistemic_audit.stage_pending_review@1`. Its CLI rejects an unknown `--policy` argument and emits no Contract D bytes. Its library function reads only `decisionContext.target`. An added ERS policy object and an added requested-operation field are ignored. The function still emits `knowledge.add_verified_tag@1` under `decision-engine.contract-c.supported-claim-verification@1.0.0`.

The two maintained Contract C policy contexts also cannot express the ERS operation. Each accepts only its own policy id. An ERS policy id raises `unsupported_policy` and emits no decision. An extra requested-operation field raises `invalid_context` and emits no decision. Those policies emit `knowledge.add_verified_tag@1` and `knowledge.cite_as_evidence@1`.

No native typed Contract D decision for `epistemic_audit.stage_pending_review@1` was produced. I did not adapt the pipeline decision, register the effect in released Contract D, or add an executor.

`shadow_ready=true` was not reached.

## Path actually exercised

Unchanged frozen upstream, reproduced locally:

`Contract A 2.0.0 -> Evidence Bundler 4e1f6fe -> Contract B 1.2.0 -> CAL ddaf945 -> parent-bound Contract C c5b1d757 -> independent consumer 12e7e640 -> Decision 6cdb59c2 -> released Contract D 298a1a0`

The reproduction used the existing composition runner at `e68e5ab387e9779b0be62d92766b76e475964790` without modification. Its result bytes match the PR #123 qualification artifact.

Digest: `sha256:2ef133c504cd33bf5b9912acb06e154b43d7060b967dd4230081d4a8ad4f9753`

Artifact: `10594929710`, digest `sha256:bab1e7522a69e404208d9e65d9edae89d860827ef08fd3da1ad01813554b0841`

Observed again:

- PIPE01 supported -> clear -> `candidate_for_authorization`, effect `knowledge.add_verified_tag@1`
- PIPE02 contradicted -> hold -> `hold`, same effect
- PIPE03 not_checkable -> hold -> `hold`, same effect
- PIPE01 replay byte-identical
- cross-run native-child replay rejected before Contract D output
- authorization performed: false
- execution performed: false

The ERS context probe then called the same parent-bound function on the reproduced PIPE01 Contract C bytes and consumer inputs. Contract E and the ERS slice were used only for the negative controls below.

## Controls

Released Contract D 1.0.0, effect-registry blob `a40f4f4447470654bdc16d852f5927189ae30cc5`, still rejects `epistemic_audit.stage_pending_review@1` as `unknown_effect_type`. That probe copied each pipeline decision and changed only the effect field so the registry could be asked the question. Those copies were not sent to Contract E or ERS. The on-disk registry hash was unchanged.

The research-local Contract D extension from the PR #117 profile can add the effect to an in-memory registry. After that in-memory add, the native PIPE01 decision still validates as `knowledge.add_verified_tag`. The extension does not rewrite it. The on-disk registry remains unchanged. I did not use the extension as an adapter.

Unadapted pipeline decisions against the existing Contract E path, with that path's ERS jurisdiction:

- PIPE01: `decision_operation_authorization_mismatch`, `execution_permitted=false`, `execution_occurred=false`
- PIPE02 and PIPE03: `decision_not_candidate:hold` before Contract E `evaluate`
- PIPE01 with a mismatched trusted decision identity: `untrusted_decision_identity`
- Contract E `evaluate` call count across these controls: 0

Exact ERS slice `319e325cdf678673fae645a70e3e34afb7dddef0`, tree `f99276c67f7eb470a50e0872f36e1acdd5731033`, entry `harness.contract_e_shadow:stage_pending_review`:

- unadapted PIPE01 decision: `execution_occurred_not_false`, `shadow_ready=false`
- permitted-shaped result whose decision identity does not match the intent: `decision_identity_binding_mismatch`, `shadow_ready=false`
- PR #117 execution-intent shape against this slice: `wrong_execution_entry_point`, `shadow_ready=false`
- disposable sandbox entries before and after: empty
- no MainFrame write

## Frozen semantic bytes

Unchanged. Reconfirmed blobs:

- Decision parent-bound ingress `83ab34bce30f874111500ed91f2c01421be9f9a0`
- Decision parent-bound CLI `4e5a85aa1179e815b5e23e6524e2b2a314aab7d0`
- supported-claim policy `2225f73eb6eefd83609f0ba19e4786d1267dd527`
- Decision materializer `1562fb29da6679a0cf894e478cbdd4ae16e21a18`
- Decision tree `d4b75b63462451b5c258a13abf9ce2beb9e78098`
- released Contract D validators `564dcde5677df5ac8f86f21dc0ffd1692f44c9f0`, `c03ef6c6f059cd03addf5e69b01025bb9a6af8d2`, `8b4ad5c9d6fc1145cf334d1416b5d52b9ed93c68`
- CAL composer `268d0dc4dd22ddde3848141d62b7d719e48d374d`
- CAL parent-bound runtime `b6d281590d372729b968ae75fec470c7186d6bd6`
- CAL parent CLI `774178a12acce0ad7a453eb0ba85ec5e5b14fa1c`
- ERS slice consumer `ba3ae85223516d8141de560d647206431fb6686a`
- ERS focused tests `b1a67046c850ca1c3c0a7649ccccda324276a9f9`
- ERS pressure harness `33746363913b9198bed294eba30088091722fcfa`
- frozen v3 subject `ffc43d4e89f5b1f7748e9cde0fa1efc7db47b463` was not edited

## What this does not change

This disposition does not weaken apparatus-contracts PR #120. `FALSIFIED_EXECUTION_PAYLOAD_UNBOUND` remains a live blocker to any real executor.

It does not weaken PR #117. Trusted point-of-use authority-state provenance, evaluation-time provenance, released Contract D registration, and Contract E production authorization remain unresolved. The RC2 intent builder is also not a valid input to the RC3 slice.

It does not establish Contract E production readiness, a released effect registration, a real executor, or a MainFrame write.

## Smallest justified next experiment

Preregister a new Decision candidate. Do not edit `6cdb59c2ba41779ac954af56dd077574ba090013`.

The candidate needs an explicit parent-bound context field for the requested operation, must fail closed on an unknown policy or extra context instead of ignoring it, and must emit a native `epistemic_audit.stage_pending_review@1` decision only for the supported parent conclusion. Released Contract D stays unchanged. The research-local effect extension is eligible only after that native decision exists.

The same experiment should then feed that unadapted decision through Contract E using an execution intent the RC3 slice actually accepts. The current PR #117 intent builder is rejected by slice `319e325cdf678673fae645a70e3e34afb7dddef0` with `wrong_execution_entry_point`. The positive stop remains `shadow_ready=true` and `execution_occurred=false`.

HOLD cases must still stop before Contract E. Payload binding and point-of-use provenance remain out of scope.
