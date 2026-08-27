# Claim Decomposition Boundary Notes

**Status:** OPEN DESIGN NOTE  
**Relationship to Contract B:** upstream dependency, not defined by the CAL consumer profile  
**Primary discussion:** to be continued with Evidence Bundler / upstream claim-formation work

## Current conclusion

Claim decomposition is a separate epistemic transformation upstream of CAL's Contract-B consumer seam.

CAL should receive a supplied audit proposition or explicitly declared proposition graph. It should not silently invent claim decomposition while auditing evidence.

Evidence Bundler should not silently own the meaning of the claim merely because it retrieves evidence for it.

The original claim must remain preserved even when decomposition produces derived audit units.

## Why this matters

Consider the supplied claim:

> System X is validated, GMP-compliant, and safe for pharmaceutical manufacturing.

Possible decomposition A:

```text
P0 parent
├─ P1 System X is validated.
├─ P2 System X is GMP-compliant.
└─ P3 System X is safe for pharmaceutical manufacturing.
```

Possible decomposition B:

```text
P0 parent
├─ P1a validation was performed
├─ P1b validation covers intended use
├─ P1c validation covers the current deployed version
├─ P2 GMP requirements applicable to the claimed use are satisfied
└─ P3 safety is established for the claimed use
```

Those are not equivalent measurement objects.

Changing only the decomposition can change:

- retrieval targets;
- evidence aperture;
- semantic relations;
- missing-evidence diagnosis;
- composition logic;
- final parent conclusion.

Therefore decomposition must not be treated as invisible preprocessing.

## Preservation rule

The claim-side analogue of CAL's evidence-preservation rule is:

> **Decomposed does not mean replaced.**

The apparatus should retain:

```text
original claim
    ↓
derived proposition graph / audit units
    ↓
evidence audits for those units
    ↓
parent-level synthesis
```

The original linguistic assertion remains reconstructable.

## Minimum information CAL would eventually need

If upstream decomposition is used, CAL may need a stable representation of:

- original claim ID;
- original claim text;
- derived proposition IDs;
- exact derived proposition text or structured representation;
- parent-child lineage;
- decomposition method / version;
- decomposition receipt or provenance;
- decomposition status / uncertainty;
- declared composition relationship where required for parent synthesis;
- explicit indication when the supplied unit is already atomic and no decomposition occurred.

This is a **consumer need**, not a decision that these fields belong in Contract B.

The EB/upstream design discussion should determine the correct artifact and handoff location.

## Composition and decomposition are paired

A decomposition is incomplete if the apparatus cannot later explain how child results relate back to the parent.

For simple conjunction:

```text
Parent: A AND B
children: A, B
composition: all_of
```

For other claims, the relationship may be materially different:

- disjunction;
- conditional;
- comparison;
- quantifier;
- temporal scope;
- causal relation;
- requirement/dependency;
- population or jurisdiction scope.

Do not freeze a complete operator ontology yet. The immediate requirement is to avoid flattening the claim into an unordered list that cannot reconstruct the parent meaning.

## CAL-side boundary

The Contract-B CAL Consumer Profile RC0 assumes:

1. CAL receives the exact audit proposition supplied to it.
2. If a proposition graph/composition rule is supplied, CAL may audit those supplied units and use the declared composition.
3. CAL does not invent missing child propositions or parent-child relationships inside the audit decision stage.
4. If required composition information is missing, CAL should expose that limitation rather than infer a convenient structure.
5. Any future automatic decomposition machinery should be evaluated separately from downstream evidence measurement.

## Smallest useful decomposition experiment

Before locking a decomposition contract, take a small set of genuinely composite real claims and have multiple independent decomposition methods produce audit-unit graphs while holding the evidence world fixed.

Measure:

- agreement on proposition boundaries;
- agreement on parent-child relationships;
- number and type of obligations generated;
- retrieval/evidence changes caused solely by decomposition;
- final audit-outcome changes caused solely by decomposition;
- cases where one decomposition hides a critical dependency another exposes;
- reviewer preference / correction burden.

### Discriminating interpretation

If downstream audit outcomes are highly sensitive to reasonable decomposition alternatives, decomposition is a major measurement variable and requires strong receipts, uncertainty representation, and possibly human review.

If outcomes are largely invariant for a well-defined class of claims, a simpler decomposition contract may be sufficient for that class.

## Questions to resolve with the EB/upstream thread

1. Which component owns decomposition execution?
2. Is the decomposition artifact part of Contract A, a pre-EB claim artifact, an extension to Contract B, or its own typed object?
3. How are original claims and derived audit units linked without duplicating or rewriting history?
4. Who assigns and versions composition operators?
5. How is decomposition uncertainty represented?
6. Can EB retrieve against derived propositions while remaining semantically agnostic about whether the decomposition is correct?
7. Which fields must reach CAL versus remain upstream provenance only?
8. What happens when a later decomposition supersedes an earlier one?

## Current disposition

- **ADOPT:** decomposition is upstream of CAL's semantic audit stage.
- **ADOPT:** preserve original claim plus derived units; never destructively replace the parent claim.
- **ADOPT:** decomposition must be explicit and attributable if used.
- **ADOPT:** CAL does not silently invent decomposition.
- **EXPERIMENT REQUIRED:** exact ownership, artifact shape, composition vocabulary, and contract placement.
- **DO NOT LOCK YET:** run decomposition sensitivity tests before freezing a schema or operator ontology.
