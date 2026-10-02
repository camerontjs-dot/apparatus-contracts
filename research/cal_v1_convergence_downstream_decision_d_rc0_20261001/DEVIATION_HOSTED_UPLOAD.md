# Preserved hosted transport failure and bounded successor

Classification: `APPARATUS_HOSTED_ARTIFACT_FILENAME_TRANSPORT`.

At head `6655ed11e2218fb0244a60bc10ec98ce48456cd1`, tree
`d6967e225cba92f62ef7d4ddfbb6c83dd2c788a3`, push run
[36960792497](https://github.com/camerontjs-dot/apparatus-contracts/actions/runs/36960792497)
and PR run
[36960818148](https://github.com/camerontjs-dot/apparatus-contracts/actions/runs/36960818148)
completed exact-subject execution and maintained regression successfully. Both
then failed at `actions/upload-artifact@v4`. No artifact was created.

The upload found 932 files but rejected a native Contract B path containing
`passage:c3f537a18a59571579cd9b72442ae9d0.yaml`. Its cross-platform filename
policy prohibits `:`. That native path is part of the fixed component output;
it must not be renamed to satisfy a transport rule.

Preserved push log archive SHA-256:
`f83731e2edd0432df6d2824ea9d1c346dd4c02b3d9ecfafa5cbcca4698d7aadc`.
Preserved PR log archive SHA-256:
`1d0446fcb455e09bd9b9aaf8a4e88bf6eb0055b6da6689801880b6a76455a8fe`.
The failed transport is not a hosted artifact-custody pass. The valid local
apparatus-r1 terminal result and all its raw files remain preserved.

Classification was recorded before correction. A separately frozen apparatus-r2
adds only a transport helper and changes the workflow's upload envelope. The
helper archives the same selected evidence types and proves every internal
member name, size, and SHA-256 matches the original file. Upload receives that
archive and its manifest; native filenames and file bytes remain untouched.
The existing 932-file selection excludes installed environments and caches.

The scientific harness blob, exact subjects, trusted targets, cases, expected
outcomes, conformance mutation, replay substitution/discriminator, target
grammar, and primary byte checks are unchanged. No component is modified.
This correction cannot change the scientific result; it restores evidence
transport and makes its custody independently checkable. A new hosted execution
is identified separately rather than relabeling either failed upload as success.
