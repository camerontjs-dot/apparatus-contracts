# POST-FREEZE REVEAL PACKET — Contract A RC2 Fresh Independent Consumer Reproduction

**SEALED. DO NOT EXPOSE BEFORE THE INDEPENDENT PREREVEAL FREEZE.**

This packet is authorized only after the owner has independently verified a durable prereveal freeze receipt for the fresh implementation.

## Scientific rule

The independent implementation and its prereveal tests are immutable evidence after reveal. Do not modify them after observing reference behavior and then count the modified result as independent agreement.

A disagreement, ambiguity, or evaluator defect is a valid terminal result and must be preserved.

## Frozen reference authorities

Candidate authority tree:

`54e5cfc659c574a1520ebc119d66e93d4f71ce34`

Reference implementation / normal-context experiment tree:

`18b9cec2bc3063ecad17d12d55e49ea4dcb61ff8`

Evaluator tree:

`5d7eb3e3a9a98ba1626118a5e06a018c02fa81ec`

Freeze receipt commit:

`6cf9019b9672075af674929455bef78c950dddc6`

Frozen evaluator path:

`research/contract-a-minimality-rc2-20260901/evaluator/test_candidate.py`

Frozen reference validator path:

`research/contract-a-minimality-rc2-20260901/candidate/validate.py`

Frozen public/reference fixture directory:

`research/contract-a-minimality-rc2-20260901/candidate/fixtures/`

The reference evaluator and fixtures may be read only after the prereveal freeze has been verified.

## Reveal sequence

1. Verify the fresh implementation's prereveal freeze receipt commit, implementation subtree, prereveal test identities, and prereveal test result.
2. Record the fresh implementation identities before opening any reference material.
3. Verify the three frozen reference tree SHAs above at the named freeze receipt commit.
4. Copy or check out the fresh implementation at its exact prereveal frozen commit into an isolated comparison workspace. Do not modify that checkout.
5. Reveal the frozen reference validator, reference evaluator, and frozen fixtures.
6. Run the frozen reference evaluator against the frozen reference candidate and record its result. A reference-evaluator failure is an evaluator defect, not an independent-implementation failure.
7. Run the frozen independent implementation against every revealed valid and invalid fixture using its prereveal API. If a call-shape adapter is necessary, create it outside the frozen implementation tree and restrict it to mechanical invocation/serialization only. It must not add validation, defaults, normalization, hashing, or semantic behavior.
8. For every valid fixture, compare at minimum:
   - accept/reject outcome;
   - computed whole-object integrity result;
   - retrieval proposition IDs, texts, hashes, and order;
   - decomposition state preserved;
   - supplied-source identity/content/hash preservation;
   - source-contract proposition projection: root/parent identity, operator, atom IDs/text/hashes/order, and provenance binding.
9. For every invalid fixture, compare accept/reject outcome and the invariant category that caused rejection. Exact error-message wording is not required unless both implementations claim a stable public error vocabulary.
10. Apply the evaluator's mutation/metamorphic controls to the frozen independent implementation without changing its bytes. Record every divergence.
11. Re-run the fresh implementer's own prereveal tests unchanged after reveal. Any changed result is evidence and must be preserved.
12. Classify each disagreement before any post-reveal repair.

## Disagreement classes

Use one of:

- `INDEPENDENT_AGREEMENT`
- `PUBLIC_SPEC_AMBIGUITY`
- `INDEPENDENT_IMPLEMENTATION_ERROR`
- `REFERENCE_IMPLEMENTATION_ERROR`
- `EVALUATOR_DEFECT`
- `REPRESENTATION_ADAPTER_DEFECT`
- `OUT_OF_SCOPE_DIFFERENCE`
- `UNRESOLVED_DISAGREEMENT`

A single reproduction may contain multiple disagreement classes. Do not collapse them into one pass/fail label.

## Required comparison controls

At minimum preserve explicit comparison records for:

- undecomposed `single` behavior;
- `failed` decomposition behavior;
- `unknown` decomposition behavior;
- declared `all_of` behavior and child order;
- missing required proposition identity;
- forbidden/unknown semantic-looking field;
- proposition text-hash mismatch or mutation;
- source content-hash mismatch or mutation;
- parent/root identity substitution;
- child identity substitution;
- source identity substitution;
- work identity substitution;
- unsupported composition relation;
- one-child `all_of`;
- noncontiguous child sequence;
- omitted `sources` versus explicit empty `sources: []`;
- duplicate child ID and duplicate child text;
- duplicate source ID;
- whole-object resealing after a legitimate bound-field change versus stale binding rejection.

If the fresh implementer froze a different interpretation of an underspecified point before reveal, preserve that interpretation and classify the difference rather than retrofitting the reference behavior.

## Reference nonclaims that must remain nonclaims

Do not score the independent implementation on:

- Evidence Bundler retrieval completeness or rank quality;
- CAL NLI accuracy;
- proposition truth/support/refutation;
- source trustworthiness;
- decomposition semantic correctness;
- Contract B production internals beyond the public Contract A consumer behavior being compared;
- Contract E authorization/jurisdiction/delegation/execution;
- a canonical Contract A release version.

## Post-reveal repair boundary

If a disagreement is understood and a repair is scientifically useful, place any repaired implementation in a new post-reveal successor subtree/commit. Never amend or overwrite the prereveal frozen implementation or tests. The repaired version cannot be counted as independent agreement for the original run.

## Terminal reproduction record

Create a durable terminal record containing:

- exact fresh aperture branch/head and normative blobs;
- prereveal implementation commit/tree/test identities;
- prereveal freeze receipt identity;
- frozen candidate/reference/evaluator tree identities;
- exact revealed fixtures/evaluator identities;
- unchanged prereveal test result before and after reveal;
- per-case comparison results;
- all disagreement classifications;
- evaluator/reference defects;
- any post-reveal successor identity, explicitly excluded from independent-agreement scoring;
- one bounded terminal reproduction disposition:
  - `INDEPENDENTLY_RECOVERED`
  - `FALSIFIED`
  - `INCONCLUSIVE`.

This post-freeze reproduction disposition is research evidence only. It does not itself authorize Contract A production promotion.
