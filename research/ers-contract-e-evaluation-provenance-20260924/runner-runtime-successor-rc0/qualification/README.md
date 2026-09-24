# ERS 05 successor qualification protocol

This qualification is non-scientific and stops before the PR #130 matrix. It uses fresh detached checkouts of the exact frozen apparatus source, the PR #146 preflight source, and ERS PR #14. The existing preflight script at blob 3314048d5904fa59fdb00e67a1ee108c167097aa is executed unchanged against its qualified receipt inputs.

The candidate runner is imported only once, in its frozen detached checkout, with the sole argument --help. It receives none of the matrix execution arguments, scientific sandbox path, key path, supervisor socket, or output directory. argparse exits before the candidate's matrix function is entered. sitecustomize.py is loaded before the runner and records and blocks process, network, filesystem mutation, dynamic source load, and forbidden scientific import attempts.

The final process uses an external macOS Seatbelt profile with deny-default policy. It allows reads, writes only to the dedicated guard-log directory, and process execution only of the exact resolved CPython 3.11.15 binary. The command sets __PYVENV_LAUNCHER__ to the fresh venv's Python entrypoint, so CPython reports and uses that venv while the profile permits only the resolved base executable. Network, other process execution, and all other writes remain denied. The profile text and SHA-256 are copied into the final qualification trace. The earlier failed direct venv-symlink profile attempts are retained in attempts/STARTUP_GUARD_PREP.md.

The frozen-runtime installation uses a newly created venv with include-system-site-packages=false and no seeded pip. The wheelhouse ZIP is extracted and checked, and uv pip sync runs with offline mode, no package index, find-links only to the extracted wheelhouse, hashes required, strict dependency resolution, and no cache. uv pip check verifies compatibility. dependency_smoke.py checks every locked package/version, wheel hash, lock hash, runtime interpreter identity, and the harmless RFC 8785, JSON Schema, and in-memory Ed25519 operations.

The static gate records distinct expected rejection codes for all negative controls. These controls exercise the non-scientific receipt/source/runtime identity gate; they do not invoke the runner's scientific matrix function. A control counts as PASS only if its actual error code equals the preregistered boundary in NEGATIVE_CONTROLS.json.

No patch is allowed after frozen qualification begins. Preserve an exact failure and stop BLOCKED or INCONCLUSIVE as justified.
