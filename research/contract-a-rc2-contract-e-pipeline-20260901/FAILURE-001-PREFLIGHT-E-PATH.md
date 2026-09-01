# Failure 001 — Contract E preflight path doubled

Status: **PRESERVED HARNESS FAILURE / NO SCIENTIFIC TARGET RESULT**

## Frozen failing cut

- experiment commit: `acd0dad3e61dd6b41124b1fa4f6b5c6cac4b3e2c`
- hosted workflow: `Contract A RC2 to Contract E pre-promotion gate`
- run: `33514354077`
- job: `99877508977`
- conclusion: `failure`

## Observed failure

The job reached `Verify frozen identities and research-only aperture` after successfully checking out the exact pinned Contract A, Research Scaffold Harness, Evidence Bundler, Claim Audit Lab, Decision Engine, Contract C release, Contract D release, and Contract E held-out freeze.

The failing command used:

```bash
EDIR=_external/e/docs/research/contract-e/epistemic-authority-propagation-rc0b
git -C _external/e hash-object "$EDIR/AUTHORITY-CHAIN-CANDIDATE.json"
```

Because `git -C _external/e` changes Git's working tree root to `_external/e`, the path argument incorrectly repeated `_external/e`. Git therefore attempted to open a non-existent doubled path and exited before evaluator self-test or target execution.

Observed error:

```text
fatal: could not open '_external/e/docs/research/contract-e/epistemic-authority-propagation-rc0b/AUTHORITY-CHAIN-CANDIDATE.json' for reading: No such file or directory
```

## Classification

`PIPELINE_ADAPTER_DEFECT` / research harness pathing.

This is **not** evidence of:

- `CONTRACT_A_DEFECT`;
- `CONTRACT_E_DEFECT`;
- `CONTRACT_E_UNDERDETERMINED`;
- a pipeline-stage semantic failure;
- evaluator disagreement.

No A→B→CAL→C→D→E target result was exposed. The target steps were skipped.

## Smallest repair

Keep the checkout root fixed and make paths passed to `git -C _external/e` relative to that root:

```bash
EDIR=docs/research/contract-e/epistemic-authority-propagation-rc0b
```

No frozen Contract A bytes, Contract E evaluator bytes, repository pins, or original scientific interpretation are changed by this repair.

## Successor rule

Any successor execution must preserve this failure record. It may not rewrite run `33514354077` as evidence that the scientific gate passed or failed.
