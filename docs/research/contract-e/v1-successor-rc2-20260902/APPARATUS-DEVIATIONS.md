# RC2 successor apparatus deviations

## Initial hosted run — matrix-count sentinel mismatch

Run: `33673708516`

Head: `52fefe8fea3cbdb3b308033752bbf89bd6f40909`

Observed on Python 3.11 and 3.12 before the branch advanced:

- exact Contract D authority checks: pass;
- RC2 schema parse/compile: pass;
- RC2 core regression/adversarial suite: `CONTRACT_E_RC2_CORE_PASS=57`;
- all 112 substantive integration assertions preceding the final size sentinel completed;
- final assertion failed only because the harness required `COUNT >= 120` while the authored matrix contained 112 cases before that sentinel.

This was a test-apparatus cardinality defect. The preregistration required a replay/superset of the prior 101-case pressure surface; it did not require the arbitrary value 120.

Repair posture: do not lower or delete any semantic assertion. Add eight real malformed ExecutionIntent controls in a separate driver so the matrix reaches the intended larger surface while leaving the original 112 assertions unchanged. Re-run all runtimes from a new exact head.

No scientific disposition is inferred from run `33673708516`.

## Pre-freeze canonicalization discriminator — semantic ambiguity detected

Probe run: `33674136989`

Probe head: `0540e8cb0baed681bc08b0e4bbdc590a6c72f882`

Artifact: `9863669436`

Artifact digest: `sha256:826682fc5067072c93a5d6a9b4058484ece7790064e8d37512a9d36390c00c76`

Observed:

- a schema-valid AuthorityState value using only the valid RC2 value domain produced identical bytes under the candidate serializer and RFC 8785 + LF;
- four malformed-but-finite JSON AuthorityState inputs containing a numeric unknown field diverged under all four tested number shapes: `1.0`, `-0.0`, `1e-6`, and `1e20`;
- the RC2 public wording at that head required `recomputed_authority_state_id` whenever the supplied AuthorityState was canonicalizable finite JSON, but did not uniquely specify JSON-number serialization;
- therefore an independent implementation could legitimately recompute a different denial-receipt identity for malformed numeric input.

This is a valid pre-freeze semantic falsifier of the initial RC2 canonicalization wording, not a production failure and not evidence against the dual-identity architecture itself.

### Probe workflow exit-propagation defect

The probe program returned exit code `1` on `AMBIGUITY_DETECTED`, but the workflow command used `python ... | tee ...` without `set -o pipefail`. GitHub therefore reported the probe job as `success` even though the semantic payload explicitly reported `AMBIGUITY_DETECTED`.

This green check is not accepted as a passing scientific result. The probe payload/log is the evidence. The workflow must be repaired with pipefail before it is reused as a gate.

## Evidence-supported successor repair

The smallest supported correction is to define Contract E RC2 canonical JSON as **RFC 8785 JSON Canonicalization Scheme bytes plus exactly one LF**. Contract D 1.0.0 already uses this canonicalization family, so this removes an observed recoverability ambiguity without inventing a project-local number grammar.

The preregistration explicitly allowed RC1 semantics to change only when a test exposed an unavoidable contradiction. This probe is that evidence. The correction must be followed by a full RC2 core/integration rerun and a repaired canonicalization discriminator before any candidate freeze.
