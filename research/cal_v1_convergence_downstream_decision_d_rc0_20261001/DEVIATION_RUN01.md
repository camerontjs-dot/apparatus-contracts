# Preserved first run and bounded apparatus successor

Classification: `APPARATUS_PACKAGED_FILE_SET_OVERREACH`.

The first frozen run at `e0b94f8f6ad37d6b78a28d880666c19b9035f94c`, tree
`b71768d5b494079548d91b960964dbdbe8da48bc`, terminated
`INCONCLUSIVE_APPARATUS_INVALID` before decisive exposure. Fifty real subprocess
commands were recorded. Exact subject and 594 blob checks passed, and Arm A's
wheel build succeeded. Clean installation, CAL child/parent execution, target
authoring/conformance, Contract C, Decision, D, paired comparisons, determinism,
and negative controls were `NOT_RUN`.

The command was the frozen `run_qualification.py` invocation with the exact
subject root and new `run-01` root described in `PREREGISTRATION.md`. The runner
raised:

```text
KeyError: There is no item named 'claim_audit_lab/ui/static/index.html' in the archive
```

It assumed every repository file below `src/claim_audit_lab/` was a wheel member.
The exact predecessor's packaging configuration does not declare that unrelated
UI HTML data file. This is a new apparatus assertion outside the supported
pipeline surface; the component wheel built as specified and no semantic result
was exposed. No component defect is inferred from this failure.

Preserved receipt SHA-256:
`sha256:fdee8636e284d7abf704443a93d9279fbf53fdc6e97c0c94523f2b08ef0effce`.
Preserved first-failure trace SHA-256:
`sha256:70d84403ce3f9b2113f76c2671d902f98c48bc54929d0cd20e8ec8d707469a82`.
The failed freeze and raw run remain immutable. Their branch is retained as
`research/cal-v1-convergence-downstream-decision-d-rc0-run01-20261001`.

The separately identified `apparatus-r1` successor changes only wheel-membership
checking. It checks the bytes of every tracked source file actually present in
the wheel, still requires every Python module and every production V1 file, and
records absent nonruntime data. It does not package the UI file or change CAL.

This correction removes the unintended requirement to ship undeclared UI data.
It cannot change the primary result: all component pins/trees/blobs, historical
source, trusted targets, cases, expected outcomes, conformance mutation, replay
substitution/rejection discriminator, and exact downstream byte checks remain
unchanged. Classification was recorded before correction. The successor receives
a new source/freeze identity and executes only into a new output root.

Two earlier setup observations are also preserved privately: Git's relative
worktree destination resolved under the ordinary checkout, so only the newly
created worktree was moved to the intended isolated path; and the sandbox could
not initialize the shared uv cache, so task-local caches were selected. Neither
exposed a decisive result or altered a subject. Node 22 was selected in isolated
tooling to match PR #123's runtime pattern instead of the installed Node 26.
