# Candidate A RC0 post-qualification falsifier

**Classification:** Draft Research / Research Infrastructure.

This is an explicit successor record. It does not rewrite or delete the frozen Candidate A RC0 bytes, its preregistration, its executed qualification evidence, or its now-superseded qualification freeze.

## Trigger

A post-qualification independent audit compared RC0 directly against the frozen Phase 1 and Phase 2 semantic authorities rather than relying on the qualification evaluator's copied oracle table.

Frozen authorities:

- Phase 1 semantic-corpus commit: `175246ae16932f2f34a399560d7f76013213bf97`;
- Phase 1 `SEMANTIC_SPECIMEN_CORPUS.md` blob: `0ff4f66bca00924755d42ed7f944c4dae8d10f66`;
- Phase 2 representation freeze: `f5337dedaad045aa290e80f69dc83ac1a0f73436`;
- Phase 2 `phase2_bakeoff.py` blob: `9f00cd332ad366b878f60d13440af639360928de`.

Both frozen authorities preserve the mixed-result public terminal reason as the exact stable identity:

`MIXED_RELATIONS`

Phase 1 uses that identity for SP-09, SP-10, and SP-11. The frozen Phase 2 oracle uses it for SP-09 through SP-12.

## RC0 mismatch

Candidate A RC0 frozen at `9f1808c47503c884887dbf862e9cd8162b21b583` instead declares and accepts:

`mixed_relations`

in all three frozen candidate artifacts:

- `CANDIDATE_A_RC0.md` blob `4fae55b156b0caea5a4815c2c665a816f39667d9`;
- `candidate_a_rc0.schema.json` blob `ee89f25bfcef008c95cbb35adf696fb1b3e2dc20`;
- `candidate_a_rc0.py` blob `fb0a05ca929fbcf8284799306e9861d992839aaa`.

This is not a cosmetic spelling difference. The programme requires a **stable public terminal reason**, and the exact frozen semantic oracle is the authority for that public identity. A candidate that silently normalizes the reason changes the public semantic object.

## Why the executed RC0 qualification missed it

The RC0 qualification evaluator at `d06c1affdf5fb65cc1df235cb1a1ebb7af174adc` copied the semantic oracle into a local table instead of importing or otherwise verifying the exact frozen Phase 2 oracle source. That copied table repeated the same lowercase `mixed_relations` value as RC0.

Therefore the reported `19/19` positive reconstruction result established internal agreement between RC0 and its duplicated evaluator table, but did **not** establish exact agreement with the frozen programme oracle for the mixed terminal reason.

The executed run, artifact, and prior terminal record remain valid evidence of this apparatus weakness:

- run `34764954521`;
- job `103744166486`;
- artifact `10319849604`;
- artifact ZIP SHA-256 `871a0d2325a92a8415e46c61cf617ea649bee0b2ef6dadb3779eb0475c34c615`;
- preserved prior qualification freeze `f5f4f4069b6c9831710c022249bcc26399938d47`.

They are not deleted or relabeled as though the false-green run never happened.

## Classification of the falsifier

This falsifies the **exact RC0 candidate** and the independence of its qualification harness. It does **not** falsify the Phase 2 Candidate A architecture of canonical minimal sufficient basis groups over exact public participants.

No causal representation obligation changed. No ablated C1 surface needs to return. The smallest successor repair is exact public-reason preservation plus qualification anchored directly to the frozen Phase 1/2 oracle artifacts.

The architecture therefore remains closed for the successor attempt unless new evidence independently falsifies it.

## Superseding RC0 disposition

The prior RC0 disposition `QUALIFIED_FOR_CAL_PRODUCER_CONFORMANCE_RESEARCH` is superseded for RC0 by:

**`FALSIFIED_REQUIRES_SUCCESSOR_CANDIDATE`**

The no-patch rule applies. RC0 must not be repaired in place and the same cohort must not simply be recounted after editing its frozen bytes.

A successor candidate may reuse the Phase 2-selected architecture, but it must receive a new research profile, new freeze, new preregistration, and a qualification harness that verifies the exact frozen oracle blobs before execution and consumes the frozen Phase 2 oracle rather than duplicating its terminal semantics.

## Nonclaims

This falsifier does not reopen production Contract C, assign SemVer, change CAL or Decision Engine production behavior, touch Contract E / Authorization, authorize execution, or imply that Candidate B should replace Candidate A. It is a bounded research falsifier of RC0 and its evaluator anchoring.