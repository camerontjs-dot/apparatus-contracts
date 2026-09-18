# CAL Provenance Canonical JSON Bounded 1

**Profile ID:** `cal-provenance-canonical-json-bounded-1`

**Status:** research candidate for discriminating digest portability only.

This profile closes one exact ambiguity exposed by Fresh Full-Chain RC0. It does not change the `ApparatusAttestation v1 Candidate` or `RunManifest v1 Candidate` data model, repair any run package, normalize logical-link aliases, or authorize schema release.

## 1. Scope

This profile defines digest preimages and identity derivation for JSON objects already valid under the candidate attestation and run-manifest schemas at provenance authority `1a5929295e735e351320cbd8c966dc43afed2859`.

The current schemas use objects, arrays, strings, booleans, and null. Numeric JSON values are outside this bounded profile. Duplicate object keys are invalid input.

## 2. Canonical JSON bytes

For an in-scope JSON value:

1. preserve array order exactly;
2. sort every object's member names in ascending Unicode code-point order;
3. emit strings without ASCII-only escaping: non-ASCII characters remain UTF-8, JSON-required escapes remain required, and no Unicode normalization is applied;
4. emit `true`, `false`, and `null` exactly as lowercase JSON tokens;
5. emit no insignificant whitespace: member separator `,`, name/value separator `:`, no spaces or indentation;
6. encode as UTF-8;
7. append exactly one LF byte (`0x0A`) after the closing JSON token.

The terminal LF is part of the digest preimage.

For the bounded domain, Python's explanatory equivalent is:

`(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")`

The seven rules above are normative.

## 3. ApparatusAttestation identity

For a schema-valid candidate attestation:

1. copy the object;
2. remove `attestation_id` if present;
3. remove `attestation_sha256` if present;
4. canonicalize under Section 2;
5. SHA-256 those bytes, lowercase hex as `<h>`;
6. derive:
   - `attestation_id = "attestation:sha256:" + <h>`
   - `attestation_sha256 = "sha256:" + <h>`

Both fields bind the same preimage.

This research profile explicitly corrects the architecture sentence saying the ID excludes only `attestation_id`; that sentence cannot reproduce the qualified RC0/RC1 producer convention.

## 4. RunManifest identity

For a schema-valid candidate manifest:

1. copy the object;
2. remove `manifest_id` if present;
3. remove `manifest_sha256` if present;
4. canonicalize under Section 2;
5. SHA-256 those bytes, lowercase hex as `<h>`;
6. derive:
   - `manifest_id = "run-manifest:sha256:" + <h>`
   - `manifest_sha256 = "sha256:" + <h>`

Both fields bind the same preimage.

## 5. Distinct byte commitments

The object digest above is not the SHA-256 of the serialized sealed JSON file. If a sealed attestation/manifest is retained as an artifact with `sha256-bytes`, that exact-file commitment is separate.

## 6. Portable vectors

A conforming consumer MUST pass every vector in `DIGEST-VECTORS.json` without importing producer/helper code.

It must also reject these mutations:

1. omit the terminal LF;
2. retain self identity/digest fields in their own preimage;
3. ASCII-escape non-ASCII vector text;
4. change any bound field without changing the digest.

## 7. Nonclaims

Passing this profile establishes only bounded digest/identity portability. It does not establish cross-object logical-link semantics, alias normalization, retention completeness, authority correctness, provenance non-interference, component semantic correctness, released-schema status, production readiness, or Authorization.

## 8. Decisive successor

Keep the four Fresh Full-Chain RC0 packages and externally frozen roots unchanged.

Freeze a fresh consumer from the candidate schemas plus this profile/vectors before package/root reveal. If it reproduces the unchanged roots and attestation digests, the earlier negative remains valid evidence that the prior specification was insufficient while this profile gains bounded support. If not, preserve the mismatch; do not reseal packages or move roots.
