# Contract C minimal in-band successor promotion qualification RC0 terminal record

## Terminal disposition

**`INCONCLUSIVE`**

Version class if promoted: **`MAJOR`**

This is a terminal research qualification result, not promotion authorization, official version assignment, release, tag, merge, CAL production mutation, Decision production mutation, or operational authorization.

## Exact lineage

- protected production base: `c3563cff66d2c85dcbf575c693056e2d8e4563d4`
- frozen successor candidate PR #91 head: `242351af7214c23dce76edd06299f55c038cd3f0`
- qualification decisive head: `4421d8533febe3b790d09b8bd6928189fd304571`
- preregistration committed before evaluator execution
- qualification run: `34726412642`
- job: `103641190718`
- artifact: `10307064789`
- artifact digest: `sha256:7c773abd7f2f5af6cc39795e6969eb01a758e37939f3876ede57888eb7573d86`

## Candidate observations

The exact parent candidate remained unchanged during qualification.

Observed:

- candidate tests replayed: `15 passed`;
- released Contract C regression replayed: `17 passed, 8 skipped`;
- candidate semantic delta remained exactly:
  - `$defs.contribution.properties.channel.enum`;
  - `properties.contract_c_version.const`;
- exact frozen handoff validated directly under the successor candidate;
- retained channels remained `[non_deciding, non_deciding]` without semantic relabelling;
- candidate retained valid `support` and `counterevidence` behavior;
- released Contract C 1.0 rejected the exact successor unchanged;
- released Contract C 1.0 contribution channel remains exactly `[support, counterevidence]` and the contribution object remains strict.

## Compatibility and version result

All three tested 1.0 downgrade paths could be made structurally valid only by changing or removing demonstrated semantic state:

1. `non_deciding -> support` validates under 1.0 but changes neutral evidence into support;
2. `non_deciding -> counterevidence` validates under 1.0 but changes neutral evidence into counterevidence;
3. dropping both neutral contributions and repairing the basis validates under 1.0 but removes exact retained contribution identities, evidence provenance and demonstrated causal participation.

No safe automatic Contract C 1.0 downgrade is established.

Under the project post-1.0 Semantic Versioning rule, the observed successor class is therefore **MAJOR if promoted**.

No official numeric successor version was assigned by this qualification.

## Consumer conformance

The workflow checked out the exact fresh Consumer B final commit:

`07e60447fae17369be5676f013c187b9fd0bfd98`

It verified the frozen consumer/test/receipt blob identities, replayed all `21/21` prereveal tests, and directly consumed the exact Apparatus candidate handoff.

Observed cross-repository result:

- exact neutral causal channels preserved;
- causal form `independent_sufficient_alternatives` preserved;
- destination policy remained `hold`.

Bounded independent consumer conformance is therefore established for this exact handoff/profile.

## Sole promotion blocker

Required producer conformance for the exact successor is **not established**.

Current inspected CAL evidence does not satisfy that release predicate:

- CAL PR #100 is research-only representation-comparison evidence and explicitly does not establish a canonical Contract C revision;
- CAL RC1 PR #104 is supported for its bounded semantic-engine claim but explicitly states that canonical downstream Contract C authority and production support remain unresolved.

The existing evidence demonstrates why `non_deciding` is needed and that the successor can be consumed independently. It does not yet demonstrate a maintained or promotion-ready CAL producer/exporter that deterministically emits the exact successor representation from legitimate producer-boundary state without adding a new epistemic judgment.

Because producer conformance is a required Apparatus-contract release gate, this missing evidence cannot be laundered into `SUPPORTED FOR PROMOTION`.

## Next discriminating test

The smallest justified successor is a bounded CAL producer/exporter conformance experiment against exact Apparatus candidate head `242351af7214c23dce76edd06299f55c038cd3f0`.

It should establish or falsify that legitimate CAL RC1 producer-boundary state can deterministically project the exact `non_deciding` Contract C successor semantics while preserving:

- exact contribution/evidence identity;
- causal versus residual role;
- causal multiplicity;
- Contract-B binding;
- CAL/policy identity;
- result identity;
- no new semantic judgment in the exporter.

If that producer conformance is supported, do not rewrite this RC0 result. Run a successor promotion qualification with the new producer evidence added.
