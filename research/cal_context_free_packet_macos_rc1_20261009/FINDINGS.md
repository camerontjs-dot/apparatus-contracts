# RC1 macOS packet-controls findings

## Observed

- The source RC0 head `7d9df68eff5d83d93aa6f07434d2f2e0d7fc2244` remains unchanged. Its original macOS result is `APPARATUS_INVALID_PLATFORM_CONTROL` (18 passes, one fixture setup error before verifier execution).
- Static review found that `test_world_symlink_rejected` removed a file while its parent `world/` remained mode `0555`, and that source path denylist matching was case-sensitive. This successor changes those research-only bytes in a separately frozen tree rather than silently repairing RC0.
- Frozen successor receipt: `FREEZE.json` SHA-256 `dd34b1da4923fc6a91a5cecd2152f2cb9154c5a8c355eb04bd999c3925f2018b`. Syntax compilation passed before freeze. No candidate or controller runner bytes changed afterward.
- First macOS run: 2026-10-09T12:52:48Z, Python 3.14.4, arm64, 34/34 unit controls, exit 0; stdout empty; stderr `sha256:c3307afb3aec3873dca949fb3f22c89eec4976b5db3ff8fbea3114179bd45957`. External receipt `sha256:c8dfa2d221de400e49d317aa63cb918df608e5bf1dd726c846399659ca466f25` remains controller-only with a sanitized public projection.
- All five candidate file SHA-256 values matched the freeze before and after the run.
- The **actual** weak copy-all control physically copied the entire public-synthetic source, including `private_gold.txt`, into a separate simulated world. The independent checker rejected the world for `EXTRA_FILE`, not for an incidental setup error.
- Positive exact-file staging passed. Negative controls exercised unknown world files/directories, mutated bytes, real symlink insertion, FIFO, hardlink, nonempty scratch, altered receipt, casefolded ambient paths/file and directory aliases, plus the existing 19 regression controls.
- The independent checker does not import the candidate verifier and compares paths, content hashes, source versus staged inodes, receipt identity, and world/scratch layout using stdlib filesystem observations. It was authored by this same controller, not a blind independent researcher.

## Bounded inference and limits

**`PASS_BOUNDED_OFFLINE_PACKET_CONTROLS`** on the named synthetic macOS fixture. This supports the narrow RC1 file-preparation/custody behavior exercised. It does **not** establish confidentiality from a model with ambient tools, host-MCP safety, microVM/container confinement, actual agent inventory, provider-side statelessness, or a scientifically blind CAL qualification.

Q01's staged-byte and independently implemented checker portions are exercised for this exact subject; Q02's executed weak copier is observed. The full launch protocol's Q03-Q13 have **no execution qualification**. No authorization, execution, model actor, Docker container, canonical contract, frozen CAL study, G89 retry, merge, or release followed from this packet test.

## Next blocker

At review, the authorized Mac had Docker Desktop installed but its selected engine endpoint had no server/socket. The launcher still lacks a selected image digest, exact complete adapter/provider request and effective tool inventory. Those are separate prerequisites under #173. The launcher proposal remains a proposal, not permission to admit a model or claim a complete Q01-Q13 pass.

## Research disposition

Research-infrastructure evidence only, **not a scientific support-for-promotion disposition**. Preserve the old failed control record and this exact successor independently. Next admission gate must be a new frozen launcher profile with externally witnessed Q03-Q13 controls; required missing/unknown/not-run keeps actor admission `BLOCKED`.
