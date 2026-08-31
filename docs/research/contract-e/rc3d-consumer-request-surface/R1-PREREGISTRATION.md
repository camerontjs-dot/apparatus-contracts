# Contract E RC3D R1 — Apparatus-Only Successor Preregistration

Status: **RESEARCH ONLY / successor to inconclusive RC3D hosted execution**

## Why R1 exists

The first frozen RC3D hosted execution at `5f424b29b27c0af1a2b821ae8dd85e4843baba51` did not reach a scientific result.

Inherited RC3B and RC3C regressions passed, but the RC3D validator terminated before comparison because one RC3D hidden case referenced a nonexistent inherited historical case id:

`HIST-N01-new-action-after-revocation`

The frozen inherited RC3A corpus actually names that case:

`HIST-N01-revoked-new-exercise`

This is an evaluator-apparatus fixture-reference error. It is not evidence for or against the RC3D public interface candidate.

The original RC3D run must remain preserved as **INCONCLUSIVE**. Do not count R1 as a rerun of an unchanged valid apparatus.

## Allowed R1 mutation surface

Exactly two functional changes are allowed:

1. replace the nonexistent hidden-case source id with the exact frozen RC3A case id `HIST-N01-revoked-new-exercise`;
2. update workflow branch/hash guards necessary to execute the corrected frozen apparatus.

No change is allowed to:

- RC3D public interface semantics;
- the RC3D interface spec blob `61f46b09d391e7da4aed2491e428ec2ed226fe93`;
- vector materialization semantics/blob `5c75e46a8eb4d7346128d84e21c25bdcea454ec4`;
- reference validator semantics/blob `824916c40c863fd1e6e7f4d35943fd6e1077590b`;
- inherited RC3A/RC3B/RC3C authority;
- any expected outcome or reason other than correcting the source fixture identifier.

## R1 falsifier

If hosted execution reaches the corrected RC3D suite and any scientific case fails, preserve that result. Do not make another in-place repair and count it as RC3D R1 agreement.

## Promotion bound

A full R1 pass supports only a fresh different-model-family reproduction. It does not establish Contract E 1.0.0 or production authority behavior.