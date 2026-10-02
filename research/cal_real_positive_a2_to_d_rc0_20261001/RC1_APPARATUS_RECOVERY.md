# RC1 apparatus-recovery deviation

Predecessor scientific subject: branch `research/cal-real-positive-a2-to-d-rc0-20261001` at `0d1725253c0b5b37d978ad9d3d92559300ecad4f`.

Hosted run `36940574690` failed before any Evidence Bundler execution or downstream scientific outcome.

Observed apparatus failures:

1. The runner changed `cwd` to the released Contract A checkout and then attempted to launch the relative executable `.venv-positive/bin/python`, producing `FileNotFoundError`.
2. The evidence-upload step rejected pre-EB target filenames containing `:`, which came from proposition IDs.

State reached before failure:

- exact external authorities verified;
- frozen A2 validated under released Contract A 2.0;
- both child targets authored as the preregistered `strict_comparison` family;
- exact target bytes/hashes were frozen before EB;
- EB execution: zero;
- CAL execution: zero;
- Contract C / Decision / D execution: zero.

Authorized RC1 changes only:

- pass the already-created virtualenv Python by absolute path;
- store the same target bytes under filesystem-safe ordinal filenames for packaging.

Protected scientific state is unchanged:

- source representation and provenance;
- Contract A object and handoff identity;
- child proposition IDs/text/hashes;
- target authoring authority and target canonical bytes;
- EB default admission;
- CAL semantics;
- Contract C authority;
- Decision policy/materializer;
- D1;
- acceptance criteria and terminal dispositions.

The predecessor failure remains preserved. RC1 is a clean apparatus-recovery successor, not a repair of an exposed scientific result.
