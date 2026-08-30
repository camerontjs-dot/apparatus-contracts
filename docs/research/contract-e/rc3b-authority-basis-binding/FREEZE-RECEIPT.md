# Contract E Authority Basis Binding RC3B — Freeze Receipt

## Freeze point

RC3B basis-binding specification, registry, and direct basis attacks were frozen before the RC3B executable validator was written.

- freeze commit: `e16dc38b4b99ce854280bacb6a953506007a4a26`
- freeze tree: `eb65e1f3a1c3b9dd82fd5d0cd0add742f796333e`
- parent before final attack freeze: `08140503c8cc01d8d57c2a4e71207ee52598fb04`

## Frozen RC3B blobs

- `PREREGISTRATION.md`: `3d106af0f0e6b569452270fe1cd83673a88f95ef`
- `BASIS-BINDING-SPEC.json`: `63c952c9c28f1be2173e69c79976c7dfe5880c10`
- `AUTHORITY-BASIS-REGISTRY.json`: `76ea333ee0460d9614e9899edb69e6865e48eccb`
- `FROZEN-BASIS-ATTACKS.json`: `c726fb0ef914a850620e545131a70d427f4027bd`

## Frozen inherited RC3A authority

RC3B reuses the exact RC3A specification/cases without modifying them:

- `SPEC-CANDIDATE.json`: `9c1090335d87eb5e4885a755542923b453c45317`
- `SPEC-SHAPES.json`: `c3f293430ae6ddb87523d83ea6e5380b8b832136`
- `SPEC-PARTICIPANT-BOUNDARY.json`: `8b1d292a240300388949d502e7b656e7a23a0b8e`
- `FROZEN-CASES.json`: `85bc7805d02a04c5a10b48b43a5f5a89f4e2f32a`

## Scientific constraint

The only intended semantic repair relative to RC3A is the interpretation of authority-conferring basis references through exact bound records. Existing warrant, competence, participant, propagation, delegation, historical, and opaque-result behavior remains under the prior frozen expectations.

If RC3B fails scientifically, do not repair these frozen objects in place.
