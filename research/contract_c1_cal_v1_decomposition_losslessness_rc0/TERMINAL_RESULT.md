# Contract C 1.0 × CAL V1 Decomposition Losslessness RC0 — Terminal Result

Date: 2026-09-18

Classification: Draft Research Infrastructure / terminal boundary-sufficiency evidence.

## Disposition

**C1_CANNOT_AUTHORITATIVELY_BIND_CAL_V1_DECOMPOSITION_RC0.**

This is a narrower claim than “Contract C 1.0 cannot carry bytes.” C1 can transport arbitrary opaque `state:` identifiers. The failure is that canonical C1 does not define an independently verifiable binding from those opaque identifiers to the exact CAL V1 child-result identities and decomposition receipt required by the qualified parent recomposition.

## Exact authority held fixed

- Contract C canonical/supported version: `1.0.0`
- spec blob: `8c15f2e5f4047ccd17e204fb23aee1168781b9d5`
- schema blob: `b0369de9b5c156322d6787261bbc7658a3b33781`
- validator blob: `9c75ccfbf2223578a8d1a7bf0c39673b394fbea4`

No released Contract C artifact changed.

## Exact CAL evidence

- Claim Audit Lab PR #178 terminal record: `47d7067476088e7b5b86944ec0df72ef949f5127`
- integrated code/test head: `b695a1ca16051fde1c204987895b672e73225168`
- decisive CAL integration run: `35368736767`

The source state requires exact recovery of:

- decomposition identity;
- `all_of` operator;
- ordered child proposition IDs/text hashes;
- immutable child CAL result identities;
- parent decomposition-receipt identity.

## Decisive execution

Exact research head: `1e8bff4eb3d7818e2c87ba02117730832bc73495`

Workflow run: `35370709834` — PASS.

Observed:
- frozen discriminator: **6 passed**;
- released Contract C regression: **16 passed**;
- static checks: PASS;
- canonical Contract C blob guards: PASS.

## Strongest C1 encoding tested

The experiment granted C1:

- child and parent proposition records;
- exact proposition IDs/text hashes;
- exact child and parent verdicts;
- parent `jointly_sufficient` causal form;
- a causal all-of rule role;
- opaque `state:` basis members for each child result and the decomposition receipt;
- exact C1 result-set identity;
- exact Contract B proposition/evidence binding.

That object is valid C1.

## Falsification

Two state-reference mutations were independently applied:

1. replace a child-result state ID with another well-formed opaque state ID;
2. replace the decomposition-receipt state ID with another well-formed opaque state ID.

After ordinary C1 reidentity, both mutated objects remained valid under the exact released C1 validator and exact Contract B index.

There is no C1 reference target against which either opaque state ID can be checked.

Therefore C1 can preserve the strings, but cannot independently establish that they actually refer to:

- the child CAL results;
- the Contract A decomposition;
- the parent DecompositionReceipt.

## Private-codec control

A control serialized the complete decomposition payload into one `state:private-codec:...` string.

The object validates structurally because C1 intentionally treats state IDs as opaque.

A producer-specific decoder could recover the hidden payload. A canonical C1 consumer cannot, because that codec is not Contract C semantics.

This discriminates transport capacity from shared contract authority.

## Smallest missing authority surface

The result does not justify a full C2 design.

The smallest demonstrated missing capability is a typed, reference-checked parent-recomposition binding that can name:

- decomposition/operator identity;
- ordered child proposition/result bindings;
- parent result/receipt identity.

Whether that belongs in a Contract C successor or another explicitly versioned handoff remains a separate design decision.

## Consequence for CAL V1

This is a downstream boundary defect, not a falsification of the CAL V1 architecture or PR #178 integration result.

CAL can freeze its native V1 result architecture while recording:

`Contract C 1.0 cannot losslessly authorize the new decomposition lineage without a successor boundary.`

No C1 downgrade, field overloading, or private codec should be used to erase that mismatch.
