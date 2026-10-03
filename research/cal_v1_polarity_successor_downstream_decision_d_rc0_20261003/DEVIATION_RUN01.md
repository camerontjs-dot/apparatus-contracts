# Deviation: run 01 blocked before decisive exposure

Preserved freeze: `1d07193b743070f0eb4daa5db2d5d2ca65bb37a3`
Preserved harness blob: `b506bc4155caf8a8d697470e6d051bee538f6448`
Preserved harness sha256: `sha256:9d8220899d9408d0fef1df389fccd74bbc0212c8293bd26962202503678f4e51`

Run 01 disposition: `BLOCKED_EXACT_SUBJECT_UNAVAILABLE`
Error type: `ModuleNotFoundError`
Error: `No module named 'yaml'`
Phase: `build-and-clean-install`
`decisive_exposure`: false

Identity verification passed for every exact subject. The wheel build, clean
install, installed inspect identity `caa0048f8f511ec3c4aa1ce713766f2219a04bc1`,
and clean-environment provenance check passed. No PIPE case, polarity case,
Decision invocation, or Contract D consumer ran.

The preserved constructor imports Evidence Bundler in the orchestrator process.
That interpreter did not have PyYAML. The clean CAL environment did, at
`pyyaml==6.0.3`, because the exact product declares `PyYAML>=6.0`.

This file records that failure. The successor harness imports the constructor
only after the clean environment's site-packages are on the orchestrator path.
The exposed evaluator bytes are unchanged at the preserved freeze. The
scientific subjects and expected outcomes are unchanged.
