# Verification Summary

last_updated: 2026-05-22

Purpose: record the current public release verification for the apparatus-contracts asset.

## Release Candidate

Apparatus Contracts `0.1.0` is verified as a deterministic verifier-suite portfolio asset for the canonical handoff contracts at `handoff-contract-v1.0.0.md` and the v1.1.0 vocabulary addendum.

This verification does not claim that the verifier performs methodological validation, calibrates real-research measurement, or qualifies any regulated process. It claims that the verifier enforces structural and vocabulary integrity for C-A and C-B artifacts produced by the consumer assets (Evidence Bundler, Claim Audit Lab, future Research Scaffold Harness).

The v1 validation package is complete for the engineering scope. Real-corpus calibration and human-review qualification for the deferred-population e-signature surface are recorded as future-use gates in `../validation/deviation-log.md`.

## Commands Run

All commands executed from `live-asset/apparatus-contracts/` on 2026-05-22.

### IQ: install and import

```bash
make install
.venv/bin/python -m validators --help
.venv/bin/python -c "from validators import _models, _hashing, _vocabulary; print('ok')"
```

Result: clean venv created; editable install completed with runtime deps `PyYAML-6.0.3`, `pydantic-2.13.4`, `pydantic-core-2.46.4` and dev deps `pytest-9.0.3`, `ruff-0.15.14`, `types-PyYAML-6.0.12.20260518`. Subcommands `verify-vocabulary`, `verify-spec-vocabulary`, `verify-integrity`, `all` recognized. Private module imports clean.

### OQ: pytest suite, ruff, CLI smoke

```bash
make test
.venv/bin/ruff check .
```

Results:

- pytest: `20 passed in 0.15s` (9 integrity, 5 spec-vocabulary, 6 vocabulary).
- ruff: `All checks passed!`

CLI smoke for OQ-006 (tampered C-A):

```bash
TMPCOPY=$(mktemp -d)
cp -r ../evidence-bundler/examples/handoff-demo/scaffold-run-bm25-handoff-demo "$TMPCOPY/"
echo "# tampered" >> "$TMPCOPY/scaffold-run-bm25-handoff-demo/claims.yaml"
.venv/bin/python -m validators verify-integrity "$TMPCOPY/scaffold-run-bm25-handoff-demo"
```

Result:

```
C-A artifact: …/scaffold-run-bm25-handoff-demo
  files checked: 8
  result: FAIL (1 error)
    - claims.yaml: hash mismatch (expected eb5ff57ddfa4f5254fc9cd8acc48268c4d9d36e12bd9a6dfb25133ab9b10cc81, got 9c252978be8aa8f0d74b3b94e520a9011836c630b41374aaf5245f93078cc8a4)
exit=1
```

### PQ: real artifacts

```bash
# PQ-001 + PQ-002
make verify

# PQ-003: real C-A handoff-demo
.venv/bin/python -m validators verify-integrity \
  ../evidence-bundler/examples/handoff-demo/scaffold-run-bm25-handoff-demo

# PQ-004: committed CAL C-B test fixture
.venv/bin/python -m validators verify-integrity \
  ../claim-audit-lab/tests/fixtures/cb/evidence-bundle-minimal

# PQ-005: EB-generated minimal bundle
.venv/bin/python -m validators verify-integrity \
  ../evidence-bundler/build/unit7-roundtrip/evidence-bundle-minimal

# PQ-006: EB phase-2a retrieval bundle (larger, multi-source)
.venv/bin/python -m validators verify-integrity \
  ../evidence-bundler/build/phase-2a-retrieval-smoke.5xSa7J/evidence-bundle-retrieval

# PQ-007: CAL audited bundle with populated audit.* block
.venv/bin/python -m validators verify-integrity \
  ../claim-audit-lab/build/unit7-roundtrip/evidence-bundle-minimal-audited
```

Results:

- PQ-001 (`verify-vocabulary`):
  ```
  canonical: contract_version=1.1.0 hash=30e2ac74144185c8009d8224ecb67dd628b0b74244647c9051104334d05526bb
    [OK]        claim-audit-lab
    [OK]        evidence-bundler
    [OK]        research-scaffold-harness
  vocabulary verification passed.
  ```
- PQ-002 (`verify-spec-vocabulary`): `spec/canonical vocabulary parity: OK (8 vocabularies)`
- PQ-003: `result: OK` (8 files checked).
- PQ-004: `result: OK` (4 files checked).
- PQ-005: `result: OK` (4 files checked).
- PQ-006: `result: OK` (8 files checked).
- PQ-007: `result: OK` (4 files checked); the verifier accepted a fully populated `AuditBlock` with `audit_support_verdict: supported`, `audit_confidence: 1.0`, both flags set, and non-empty audit and deviation notes.

### v1.1.0 acceptance addendum (OQ-008, OQ-009, PQ-008)

```bash
TMPCOPY=$(mktemp -d)
cp -r ../evidence-bundler/examples/handoff-demo/scaffold-run-bm25-handoff-demo \
  "$TMPCOPY/scaffold-run-v110-test"
echo "1.1.0" > "$TMPCOPY/scaffold-run-v110-test/CONTRACT_VERSION"
# Regenerate the SHA256SUMS entry for CONTRACT_VERSION
( cd "$TMPCOPY/scaffold-run-v110-test" && \
  shasum -a 256 CONTRACT_VERSION | awk '{print $1, "CONTRACT_VERSION"}' > SHA256SUMS.new && \
  grep -v "  CONTRACT_VERSION$" SHA256SUMS >> SHA256SUMS.new && \
  mv SHA256SUMS.new SHA256SUMS )

.venv/bin/python -m validators verify-integrity "$TMPCOPY/scaffold-run-v110-test"
.venv/bin/python -m validators verify-integrity "$TMPCOPY/scaffold-run-v110-test" --against-pin 1.1.0
.venv/bin/python -m validators verify-integrity "$TMPCOPY/scaffold-run-v110-test" --against-pin 1.0.0
```

Results:

- Default acceptance (OQ-008 / PQ-008): `result: OK` (8 files checked); v1.1.0 accepted under the dual-acceptance pattern.
- `--against-pin 1.1.0`: `result: OK`.
- `--against-pin 1.0.0`: `result: FAIL (1 error)` with `CONTRACT_VERSION is '1.1.0' but --against-pin requires '1.0.0'`; exit code 1.

## Coverage Summary

- All eight Pydantic models in `validators/_models.py` exercised against real consumer data: `ScaffoldRun`, `ClaimsRegistry`, `SourceMetadata`, `PassagesFile` (via PQ-003); `BundleManifest`, `ClaimAuditUnit`, `PassageRecord`, `AuditConfig` (via PQ-004 through PQ-007).
- Both supported contract versions exercised: v1.0.0 via the committed fixtures; v1.1.0 via the tmp-copy bump (OQ-008, PQ-008).
- All three verifiers exercised on both positive and negative paths through the pytest suite and CLI smoke runs.
- ruff style compliance: clean.

## Known Limits

Recorded in `../validation/deviation-log.md`:

- AL-001: Harness has no executable surface yet (drift verifier sees it as a present, in-sync consumer; no Harness-produced C-A available to validate).
- AL-002: PQ uses fictional fixture data; calibration against real research corpora is a future-use gate (FUG-001).
- FUG-002: Human-review qualification for the deferred-population e-signature block opens before any regulated-customer-facing deployment.
