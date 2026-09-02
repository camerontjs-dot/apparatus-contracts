# Contract E v1 Fresh Independent Reproduction RC1 — Reconciliation

Status: **terminal fresh reproduction result = FALSIFIED**

This record reconciles the sealed fresh independent reproduction of the frozen Contract E Authority Evaluation Candidate RC1. It does not alter the frozen candidate at `8876b7bcc2afa1a4902400b0cc507cf2ef02e6e7`, the sealed evaluator at `ee47670104776f627b7c337c6235dabafe03c874`, or the frozen fresh implementation at `75e22edf20c531fb50ed47cb1d199dfa15a5a6b8`.

## 1. Preserved fresh result

Repository: `camerontjs-dot/research-scaffold-harness`

Execution branch: `research/contract-e-v1-fresh-independent-reproduction-rc1-20260902`

Frozen implementation:

- commit: `75e22edf20c531fb50ed47cb1d199dfa15a5a6b8`
- blob: `42d2f43ec9222f2409d6066fd599327ce9ba5765`
- SHA-256: `7f2c2359a4553edb8adcf9ef9cee6ce624a5e5a1cbd3f67f5ade71be53338ad7`

Freeze receipt: `32b81adc82384a437289c8b034000cbe31951d86`

Post-freeze evidence:

- `RESULTS.json` preserving commit: `a5f616fc34cf70785ee047c3538c327868eb2287`
- `TERMINAL_RECORD.md` preserving commit: `d1e3c6998b20db845cdce8b4b39df90485c27e7d`
- preserved RESULTS SHA-256: `5ca842b1b9f2e58bcf23081f93dbeae7161efda3dc0c88f74e99cd23ff8dbc7e`

Sealed comparison:

- cases: 50
- normative exact matches: 48/50
- normative mismatch IDs: `NEG-SUPPORT-CANNOT-CONFER`, `NEG-STATE-ID`
- false permits: 0
- false rejects: 0
- exceptions: 0
- preservation failures: 0
- diagnostic-shape failures: 0
- terminal scientific state: `FALSIFIED`

Post-freeze contamination: none observed.

The post-freeze host could not perform a full network-backed Apparatus checkout. The fresh runner instead used the minimum evaluator layout authorized by the reveal packet, with evaluator, hidden cases, candidate reference, and frozen implementation each byte-verified against their sealed Git blob and SHA-256 identities. The sealed evaluator completed all 50 cases. No adapter, translation, repair, coercion, or frozen-file modification was introduced. This is an apparatus deviation, not evidence that the comparison failed to occur.

## 2. Common cause of both mismatches

The two mismatch IDs are one semantic disagreement expressed in two cases.

For an invalid or forged `AuthorityState`:

- the frozen candidate reference writes the **supplied/claimed** `authority_state_id` field from the input state into the denial receipt;
- the fresh implementation writes the **recomputed canonical AuthorityState identity** into the denial receipt.

The fresh implementation and reference agree that the request is denied in both cases.

Because `authority_state_id` is included in the receipt semantic projection, the differing identity also produces a differing deterministic `receipt_id`.

No authorization-direction disagreement was observed.

### `NEG-SUPPORT-CANNOT-CONFER`

The supplied state is structurally invalid (`records=[]`) and carries a zero-valued claimed `authority_state_id`. Supporting artifacts cannot confer authority. Both implementations deny. The reference receipt preserves the zero-valued claimed state ID; the fresh implementation reports the recomputed identity of the supplied state object.

### `NEG-STATE-ID`

The state content is otherwise valid but its supplied `authority_state_id` is forged. Both implementations deny. The reference receipt reports the forged claimed ID; the fresh implementation reports the recomputed canonical identity of the state content.

## 3. Public-spec determinacy finding

The frozen public specification defines AuthorityState canonical identity and requires the supplied `authority_state_id` to equal the recomputed identity. It also says the AuthorizationReceipt contains “request and AuthorityState identities.” It does **not** define what the receipt's single `authority_state_id` field means when the supplied state identity is invalid or mismatched.

Therefore the fresh disagreement is not evidence that either implementation permitted unsupported authority. It is evidence that the frozen public candidate did not make one receipt semantic recoverable from the normative aperture.

The sealed evaluator remains valid evidence for the frozen candidate because its gate was frozen before the fresh implementation existed and it faithfully tested the frozen reference surface. Its `FALSIFIED` result must not be relabelled as a pass.

## 4. Scientific classification

Observed evidence:

- authority decision behavior: agreement on 50/50 cases;
- safety direction: 0 false permits, 0 false rejects;
- preservation: 50/50;
- normative receipt projection: 48/50;
- fresh recoverability gate: `FALSIFIED`.

Inference:

- the bounded authority architecture remains strongly supported by adversarial and decision-direction evidence;
- Candidate RC1 is **not promotion-ready** because its public receipt semantics are not fully recoverable;
- the failure is narrower than a failure of standing-authority, exact-jurisdiction, delegation, currentness, conflict/residue, nonconferring-support, A-D identity, execution, or verification boundaries.

Unknown until a successor is specified and independently reproduced:

- whether a clarified receipt identity model eliminates the disagreement without exposing another latent ambiguity.

## 5. Genuine normative decision now exposed

A successor must explicitly distinguish or choose between two facts when an AuthorityState identity claim is invalid:

1. the **claimed/supplied identity** carried in the input field; and
2. the **computed canonical identity** of the supplied AuthorityState content, when canonicalization succeeds.

Three coherent successor designs exist:

### A. Claimed identity only

Keep one receipt field and explicitly define it as the syntactically supplied `authority_state_id`, even when validation fails.

Advantage: smallest change and matches the frozen RC1 reference.

Cost: a denial receipt does not canonically identify the actual invalid state bytes when the claim is forged.

### B. Computed identity only

Keep one receipt field and explicitly define it as the recomputed canonical state identity when possible, otherwise null.

Advantage: receipt identifies the actual supplied state content and matches the independent implementation's interpretation.

Cost: the original claimed identity is lost from the normative receipt surface unless separately preserved.

### C. Preserve both claimed and computed identities

Replace the ambiguous single semantic with two explicitly named receipt fields, for example `authority_state_claimed_id` and `authority_state_computed_id`.

Advantage: preserves the source claim and the independently recomputed observation without conflating them. This is the strongest audit/provenance model and makes identity mismatch directly inspectable.

Cost: larger schema change and therefore unquestionably requires a new frozen candidate and fresh independent reproduction.

## 6. Recommendation

**Recommend C: preserve both claimed and computed identities.**

Reason: Contract E is an authority/audit boundary. When integrity validation fails, collapsing “what was claimed” and “what was computed” into one field destroys information precisely where the audit trail is most important. The fresh reproduction demonstrated that the single-field model admits two reasonable interpretations. Carrying both facts removes that ambiguity instead of merely selecting one side of it.

This recommendation is not yet a successor candidate. It is a genuine normative architecture choice requiring operator acceptance before the receipt schema is changed.

## 7. Current programme disposition

For frozen Candidate RC1:

**FALSIFIED** for fresh independent recoverability.

For Contract E as a programme:

**INCONCLUSIVE / not yet supported for bounded promotion** pending resolution of the receipt identity semantic and a fresh reproduction of the resulting successor.

No production promotion, tag, release, or `1.0.0` authorization is supported by this record.
