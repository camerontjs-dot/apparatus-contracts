# Contract C RC2 Consumer B Clean-Room Interface Notes

This directory is a frozen **handoff input**, not a Contract-C production specification and not a Consumer B result.

## Consumer-visible meaning

Treat `contract-c-rc2-producer-candidate.json` as a CAL-attributable epistemic result bound to the immutable Contract-B input packaged here. The consumer may use only the information explicitly present in the handoff.

The following durable CAL Pipeline invariants apply:

- preserve exact input/result/proposition/evidence identities and hashes rather than reconstructing them from filenames, order, or hidden implementation state;
- keep CAL epistemic state separate from downstream decision policy or operational authorization;
- preserve `not_performed` as distinct from a completed adverse, negative, or failed assessment;
- preserve retained/residual/non-deciding contribution state rather than silently deleting it;
- do not manufacture missing assessments, causal state, provenance, or defaults;
- changing downstream policy must not mutate this frozen candidate;
- the bundled Contract-B artifact is evidence-world input, not a source of downstream policy.

## Isolation boundary

A Consumer B experiment that uses this handoff must not inspect the producer implementation, producer tests, producer-side research reasoning, expected outputs, or the producer-gate evaluator. If any such information is exposed, record the contamination and do not describe the run as clean-room independent reproduction.

## Integrity

Verify `MANIFEST.json` identities before use. The candidate bytes must hash to `e142f4aab119751dc201bca7994c0f97636c65647489f7edbee823a7f8aee3b4`. Reassemble the Contract-B base64 parts exactly as specified in the manifest, decode the ZIP, verify its SHA-256, extract it, then validate the embedded `SHA256SUMS`, bundle identity, and bundle hash.

## Scope

The handoff deliberately excludes producer-side field justifications, ablation results, weak-candidate controls, implementation traces, and evaluator logic. Those are evidence for the producer gate, not legitimate clean-room consumer inputs.
