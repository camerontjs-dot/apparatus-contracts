# Offline restore: ERS 05 runner/runtime successor

This archive defines a new successor runtime. This is a newly frozen successor runtime chosen from available evidence. It is not claimed to reconstruct an unknown historical matrix environment.

Target: CPython 3.11.15, macOS 27.0 arm64. The dependency set is fixed by requirements.lock; install only into a newly created virtual environment with system site packages disabled. Do not reuse an existing environment.

## Verify and extract

From this directory:

    shasum -a 256 -c ARTIFACTS.SHA256SUMS
    mkdir -p wheelhouse
    python3.11 -m zipfile -e wheelhouse.zip wheelhouse
    shasum -a 256 -c WHEELHOUSE.SHA256SUMS

Confirm the lock and archive hashes match MANIFEST.json. The wheelhouse checksum file lists each of the 10 target wheels under the wheelhouse directory. The requirements lock pins every package version and includes accepted SHA-256 hashes.

## Create a clean environment and install offline

Use the qualified CPython 3.11.15 executable and the recorded uv 0.11.11 executable. Select a new, empty virtual-environment path.

    uv venv --python <python-3.11.15-executable> --no-project --no-python-downloads --no-cache --no-progress --config-file /dev/null <new-venv>
    uv pip sync --python <new-venv>/bin/python --offline --no-index --find-links <this-directory>/wheelhouse --require-hashes --strict --no-cache --no-progress --config-file /dev/null requirements.lock
    uv pip check --python <new-venv>/bin/python --offline --no-cache --config-file /dev/null

The sync uses only the local wheelhouse, disables package indexes, requires lock hashes, and fails if a wheel or dependency is absent. The fresh environment prevents ambient packages from satisfying requirements. uv pip check is the dependency-consistency check used instead of seeding pip into the environment.

## Verify imports and versions

Run the recorded qualification helper using the new interpreter and extracted wheelhouse:

    <new-venv>/bin/python qualification/dependency_smoke.py --manifest MANIFEST.json --lock requirements.lock --wheelhouse wheelhouse --output dependency-smoke.json

The helper verifies Python and virtual-environment identity, the exact locked package set, wheel and lock hashes, and harmless RFC 8785, JSON Schema, and ephemeral Ed25519 operations. It writes no signing key material. This helper does not import or execute the runner, ERS implementation, Contract E, a supervisor, or matrix code.

No package index or network fallback is part of restore. If any wheel/hash/version is absent or differs, stop and preserve the failure; do not resolve replacements.
