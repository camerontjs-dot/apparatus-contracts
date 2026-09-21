# Parent-bound ERS shadow composition

Date: 2026-09-21

Disposition: `SUPPORTED_FOR_CONTROLLED_LOCAL_ERS_SHADOW_COMPOSITION`

This is a controlled local shadow result for one frozen composition. It does not authorize a write, a release, Contract D effect registration, Contract E production use, or an executor.

## Question

Can a successor of frozen Decision candidate `6cdb59c2ba41779ac954af56dd077574ba090013` natively emit `epistemic_audit.stage_pending_review@1` for the frozen CAL Pipeline v3 parent-bound Contract C fixtures, then reach ERS slice `319e325cdf678673fae645a70e3e34afb7dddef0` at `shadow_ready=true` and `execution_occurred=false`?

The caller selects a maintained policy. The policy owns the effect. The caller does not supply an effect or a requested operation.

## Phase A candidate

Decision Engine successor:

- commit `816374379ba7eb23f5bfdadaf203b7e287c052db`
- tree `08a34359d4a177bc17c8de1521d60255bf6ebf82`
- parent `6cdb59c2ba41779ac954af56dd077574ba090013`
- dispatch blob `9948b0dba9f77d2ad7c71d74b27d2684985ecc70`

Phase A disposition: `SUPPORTED_NATIVE_ERS_OPERATION_DECISION_CANDIDATE`

That commit was frozen before this composition ran. The composition imported that commit and did not amend it.

Maintained policies:

- `decision-engine.contract-c.supported-claim-verification` `1.0.0` owns `knowledge.add_verified_tag@1` with params `{ "scope": "claim" }`
- `decision-engine.contract-c.epistemic-audit-stage-pending-review` `1.0.0` owns `epistemic_audit.stage_pending_review@1` with params `{}`

The second policy means: stage an epistemically supported claim for ERS pending review.

## Path exercised

Frozen v3 Contract C bytes, unchanged, for PIPE01, PIPE02, and PIPE03.

Successor Decision policy dispatch.

Released Contract D `298a1a0f7b7b6d7712e11200d04faec3e1ca169b` as the negative authority control.

Research-local in-memory effect extension from apparatus-contracts `b153dcc4434cbe8a98616a9e410c6125378144c7`. The extension did not rewrite the Decision object. The registry file stayed `sha256:4f6bcac7a9aa191cf03d500f1cfc46bbfad0d073c09a7564aa7b4b3eabaea61c`.

Existing Contract E point-of-use gate from that same commit.

ERS RC3 `build_execution_intent` and `stage_pending_review` at slice `319e325cdf678673fae645a70e3e34afb7dddef0`, tree `f99276c67f7eb470a50e0872f36e1acdd5731033`, consumer blob `ba3ae85223516d8141de560d647206431fb6686a`.

The executable identity is the frozen consumer file hash `sha256:16e3e1dff86aff4d6f8508360a4681cca839ba15b8613c94e05ecf909c67a106`.

The positive intent uses entry point `harness.contract_e_shadow:stage_pending_review`, shadow mode, claim id `ROOT`, relative target `20_live/epistemic-audit/pending-review/claim-review-PIPE01-root.md`, the native Decision semantic identity, the claim content hash, the observed absent pre-state, and environment constraints mutation forbidden, network disabled, workspace `mainframe`.

The sandbox was an empty disposable directory. It was empty after the positive call and after the negative calls.

## Results

Supported-claim policy on the successor matched the frozen ingress and the frozen v3 Contract D bytes:

- PIPE01 clear, `sha256:509862ec4b28ba211406eb21d9398f1fab7e153e0c7e12595d6ab8476d053e24`
- PIPE02 hold, `sha256:8c7b28718691d6a84ecda4172051172e1c9ecf1d106cbc7e4a9132fda5ff9230`
- PIPE03 hold, `sha256:12d9619bb4afc449ab5d8b01089940a9917ec28670fd4ed5e6602dd283abe55e`

ERS policy, native Decision objects:

- PIPE01 completed, clear, semantic identity `decision:sha256:3427c5cb6692bf7358c13e47628ef7a91a0c53e78affc58f2ae60173daffcc15`, canonical `sha256:7ddea63c77b2cf1223489129b64aef6ecc71ed31238b805689abb2f68f7a03eb`
- PIPE02 completed, hold, semantic identity `decision:sha256:e5e9197601b4f6fedd625c9f577cbdb0465b1d177b8df46faa4d5822f12aa1d4`
- PIPE03 completed, hold, semantic identity `decision:sha256:7ab331f7bf2f9a65b1b2677db63f80f224e01387ac6ae9614d7a359794eac160`

Released Contract D rejected the ERS decision with `unknown_effect_type` before the research profile was installed.

PIPE02 and PIPE03 stopped at `decision_not_candidate:hold` with zero Contract E `evaluate` calls.

PIPE01 reached Contract E outcome `candidate_for_authorization`, execution permitted, `execution_occurred=false`, result identity `sha256:a9ca429190620e48a3d0a2a4ffdf436f199e11af29b03b298030d8d334674cc8`. The Contract E and ERS execution-intent identities were the same: `sha256:f30952c81a147c6077936203db508aea52caee6e3dfbd740fd2110ceef934bc5`.

The ERS consumer returned `shadow_ready=true`, `execution_occurred=false`, operation `epistemic_audit.stage_pending_review@1`. Shadow result identity `sha256:bdb54311312d5661bafb55c449d016eda07746eb33db2c4123d2ea6518f856f2`.

Fail-closed controls returned no Decision, or rejected the composed object:

- unknown policy and wrong policy version: `unsupported_policy`
- extra context, caller `requested_operation`, and caller `effect`: `invalid_context`
- mutated target hash: `target_binding_mismatch`
- raw Contract C mutation: `contract_c_whole_object_mismatch`
- cross-run native-child replay: `contract_c_validation_failed`
- substituted consumer checkout: `consumer_authority_mismatch`
- CLI `--requested-operation` and `--effect`: `invalid_cli_arguments`, empty stdout
- wrong Decision identity at the consumer: `decision_identity_binding_mismatch`
- wrong executable identity: `unexpected_executable_identity`
- wrong pre-state: `point_of_use_pre_state_mismatch`
- stale authority state: `stale_authority_state`
- altered entry point: `wrong_execution_entry_point`
- untrusted Decision identity inside Contract E: `untrusted_decision_identity`, and `evaluate` was not called
- the supported-claim Decision against the ERS jurisdiction: `decision_operation_authorization_mismatch`, and `evaluate` was not called

## Unchanged bytes

The frozen ingress blob `83ab34bce30f874111500ed91f2c01421be9f9a0`, materializer `1562fb29da6679a0cf894e478cbdd4ae16e21a18`, supported-claim policy module `2225f73eb6eefd83609f0ba19e4786d1267dd527`, parent-bound CLI `4e5a85aa1179e815b5e23e6524e2b2a314aab7d0`, and Contract D canonical output `0ea61767b9ae61b3b80c0c2f26de4292f213b7fb` are the same bytes as `6cdb59c2`. Released Contract D and the ERS slice were not edited.

## Still blocked

PR #120 `FALSIFIED_EXECUTION_PAYLOAD_UNBOUND` remains. This intent names a relative path. It does not bind a rendered pending-review body to the claim content hash.

Trusted point-of-use authority-state provenance and evaluation-time provenance remain open. This run supplied both from the harness.

Released Contract D still does not register the ERS effect. Contract E is not a production authorization. No executor ran.

## Next falsifier

Bind an exact rendered pending-review payload to claim content `sha256:fe9a393b0c31f7e2f200cbefc08d9293e364f8a0810865a73003ec3502c387d0` and show whether this shadow intent still fails closed when that body is absent or different. Do not add an executor for that test.
