# Pre-freeze runtime construction attempts

These are preserved setup attempts, not frozen-successor qualification results.

## Attempt 1: resolver lock reconstruction

Command:
    uv pip compile requirements.in --python /Users/admin/.local/bin/python3.11 --python-version 3.11.15 --python-platform aarch64-apple-darwin --generate-hashes --only-binary :all: --no-annotate --no-header --no-cache --no-progress --default-index https://pypi.org/simple --config-file /dev/null --output-file /private/tmp/cal-ers05-runner-runtime-successor-20260924/runtime-build/reconstructed.lock

Result: resolved 10 packages; cmp against requirements.lock returned zero (byte-identical).

## Attempt 2: initial wheel download path error

Command from repository root:
    python3.11 -m pip download --isolated --disable-pip-version-check --no-input --no-deps --require-hashes --only-binary=:all: --no-cache-dir --index-url https://pypi.org/simple --dest /private/tmp/cal-ers05-runner-runtime-successor-20260924/runtime-build/wheelhouse-rebuild requirements.lock

Exact error: ERROR: Could not find a version that satisfies the requirement requirements.lock (from versions: none), followed by ERROR: No matching distribution found for requirements.lock. The lock filename was incorrectly given as a package requirement. No wheel was downloaded by this invocation.

Corrected command used the explicit lock path with -r:
    python3.11 -m pip download --isolated --disable-pip-version-check --no-input --no-deps --require-hashes --only-binary=:all: --no-cache-dir --index-url https://pypi.org/simple --dest /private/tmp/cal-ers05-runner-runtime-successor-20260924/runtime-build/wheelhouse-rebuild -r research/ers-contract-e-evaluation-provenance-20260924/runner-runtime-successor-rc0/runtime/requirements.lock

Result: all 10 target-platform wheels downloaded successfully with hash checking.

## Attempt 3: superseded ZIP timestamp

The first archive had SHA-256 26a67c91a5328fd35fe796df61541781e5054d1e0945ae556b6a9fefe22a7c24 and entries stamped 2026-09-24 12:00. Rebuilding from the same downloaded wheel bytes with fixed ZIP metadata produced SHA-256 68474c180d4e5d2b35df36354d68cc477a69061960cd26385661cad9a63a0214. All extracted wheel entries had matching names, byte counts, and CRCs; individual SHA-256 hashes are recorded in WHEELHOUSE.SHA256SUMS. The timestamped archive is retained as wheelhouse-original-current-timestamp.zip; the fixed-metadata archive is the successor input.

## Attempt 4: artifact checksum invocation from the wrong directory

The first `shasum -a 256 -c` invocation was issued from the repository root while ARTIFACTS.SHA256SUMS contains runtime-directory-relative names. It reported all seven listed files as unavailable. No files were changed. The checksum command is defined to run from the runtime directory, as the restore instructions state. A second wheel-check attempt extracted directly to a directory named wheelhouse-verification, although WHEELHOUSE.SHA256SUMS names wheelhouse/<filename>; it correctly rejected all 10 as absent. No archive or wheel bytes were modified. The corrected verification extracts under a parent directory with the required wheelhouse/ child.

## Attempt 5: path error while recording the checksum invocation

A logging command used a repository-relative path while already running from the runtime directory; the shell reported no such file or directory and did not append the note. The command then regenerated ARTIFACTS.SHA256SUMS from the correct runtime directory and its seven listed files verified OK. This note is the preserved record of that logging-path error.

## Pre-freeze construction smoke (not final qualification)

A disposable venv at /private/tmp/cal-ers05-runner-runtime-successor-20260924/runtime-build/construction-venv was created with CPython 3.11.15, include-system-site-packages=false, and no seed pip. uv pip sync used the then-extracted target wheel directory with --offline, --no-index, --find-links, --require-hashes, --strict, --no-cache, and the exact requirements.lock. It installed 10 locked packages. uv pip check reported: Checked 10 packages; All installed packages are compatible. No candidate package imports, runner imports, candidate source execution, or scientific execution occurred. The final post-freeze runtime check will recreate a fresh environment directly from the frozen wheelhouse.zip.
