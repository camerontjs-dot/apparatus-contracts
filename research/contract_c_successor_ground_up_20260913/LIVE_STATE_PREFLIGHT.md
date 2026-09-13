# Contract C successor ground-up programme: live-state preflight

**Classification:** Draft Research / Research Infrastructure. This record is not an independent-consumer reproduction, production contract authority, version assignment, release, tag, promotion, Decision policy change, Contract E change, Authorization, or execution.

**Coordination issue:** `camerontjs-dot/apparatus-contracts#93`.

**Inspection date:** 2026-09-13.

The programme starts from live repository evidence. Historical records below are evidence inputs, including negative and superseded results. They are not inherited design decisions unless separately justified in the obligation matrix.

## Production and release anchors actually inspected

| Repository / authority | Exact identity inspected | Observed status |
| --- | --- | --- |
| Apparatus Contracts `main` | `c3563cff66d2c85dcbf575c693056e2d8e4563d4` | Protected current `main`. |
| Contract C 1.0.0 release | annotated tag object `6bd135a948e407212b2e77ec18ac5c402f93565e` -> release commit `5fe55f9ed5d0ee9f026ca1b077e9d70ce0487ea1` | Immutable historical authority for its released bounded producer. Released schema blob `b0369de9b5c156322d6787261bbc7658a3b33781`; validator blob `9c75ccfbf2223578a8d1a7bf0c39673b394fbea4`. |
| EDR-002 / Apparatus issue #17 | issue plus 2026-09-13 reconsideration comment | Original bounded promotion remains valid. Reconsideration trigger is recorded as fired for the successor programme because later legitimate CAL states exceed the 1.0 public causal grammar. |
| Claim Audit Lab `main` | `32275a239b68af383a56bca843e28cbc1e343976` | Protected production `main`; current CAL V1 RC1 work remains Draft research, not production `main`. |
| Decision Engine `main` | `7be709b2141c767c5da89b8b94cf90233c4238fe` | Protected maintained V1 `main`. |
| Decision Engine v1.0.0 | annotated tag object `7835f2f53267843113212abfa0cac6e726242409` -> commit `7be709b2141c767c5da89b8b94cf90233c4238fe` | Published bounded release. It deliberately accepts exact released Contract C 1.0 only; Contract C successor research is outside its compatibility promise. |

## Apparatus Contract C successor research inspected

| Record | Exact identity / decisive evidence | Preserved result and present use |
| --- | --- | --- |
| #85 non-deciding shadow RC0 | PR head/receipt `ad1ffbd7906a7cf34cce5afa906a5797cd4a14ff`; run `34529151133`; artifact `10172768614`; handoff SHA-256 `325962ebcdbf6af836bb6193a451524ccd40b4d10f2394ff9f703fbfce1ec1e3` | `SUPPORTED_BOUNDED_TWO_LEAF_SHADOW_DELTA`. Shows neutral/non-deciding participation can cross the Apparatus boundary without weakening unrelated 1.0 checks. Does not establish general causal sufficiency. |
| #86 compatibility/downgrade RC0 | PR head `194a84ec11fc19dbdfd1db5c5747951ae6364324`; tested implementation `a8ee05e758a7be97c567cdc95ff70db75814946d`; run `34530811489`; artifact `10173394540` | `SUPPORTED_PARALLEL_VERSIONING_AND_BREAKING_CHANGE_SIGNAL`. Strict 1.0 consumers reject successor bytes; three validator-valid downgrade mappings caused semantic loss. MAJOR is a compatibility signal if an incompatible successor is eventually promoted, not an assigned successor version. |
| #87 richer attribution sidecar RC1 | PR head `f58f531abf6f2c8ab264db41346592b1498514d0`; decisive tested head `132a11587af3cfc7d0e05122390babe630cf26f4`; run `34532374495`; artifact `10174010034` | `SUPPORTED_RICHER_SIDECAR_TECHNICALLY_SUFFICIENT`. Preserved negative apparatus run `34532296461`. Sidecar can carry unresolved evidence provenance and multiplicity, but makes Contract C alone insufficient and creates a second authority object. Technical sufficiency is not architectural preference. |
| #89 surface necessity / sidecar ablation RC0 | terminal commit `c5fa9be39e6d521fdad8fd4c9cbb1d3cd10cc53b`; decisive head `afacb59149a06379616798893d3909d6fa1cbe11`; run `34695273270`; artifact `10298184921` | `SUPPORTED_MINIMAL_IN_BAND_INVARIANTS_WITH_SIDECAR_RESEARCH_VESSEL`. Exact evidence member set, causal form, causal/residual role and proposition identity were required in tested reconstruction. A second sidecar member ID was preregistered as required and falsified. |
| #91 minimal in-band candidate RC0 | candidate head `242351af7214c23dce76edd06299f55c038cd3f0`; validator blob `bbab0e94d56f2983ed6d5cc510bf26efa4a55e21`; schema-delta blob `bdd511aac6a26fd0bdaa07c353a29757b478b283` | Research candidate only. It reused Contract C 1.0 structure and added `non_deciding`; it is now preserved as a falsified/superseded design input after CAL #106 producer conformance. |
| #92 promotion qualification RC0 | parent candidate `242351af7214c23dce76edd06299f55c038cd3f0`; qualification head `4421d8533febe3b790d09b8bd6928189fd304571`; terminal commit `c6603dd35e81cba7382326abd76ff6c97588b7d9`; run `34726412642`; artifact `10307064789` | `INCONCLUSIVE`; producer conformance was the sole blocker at that point. The later CAL #106 result resolves that blocker negatively for this candidate. |

## Claim Audit Lab evidence inspected

| Record | Exact identity / decisive evidence | Preserved result and present use |
| --- | --- | --- |
| #95 Measurement Envelope RC0 | final candidate `6cb12e81698b21d3bed82f0f31d592ab6e5f1500`; decisive run `34431468666`; artifact `10134635566`; final-head run `34431577136` | `SUPPORTED_WITH_BOUNDS`. A family-neutral measurement envelope can preserve full audit context and exact consumed subsets. Measurement is explicitly not warrant or verdict. |
| #96 event-order authority RC0 | candidate freeze `634837fe368accbd9add2c9483dfff6722f5dfc7`; final head `3a4b5f24f813843eae3857ed3444fb12b1cb8182`; decisive run `34432288514`; artifact `10134908181` | `SUPPORTED_WITH_BOUNDS`. Preserves a weak-control result where caller-stipulated semantic fields were warrantable without independent source completion, then demonstrates a source-grounded completion boundary that closes the tested seam. |
| #97 event-order proposition relation RC0 | decisive freeze `94ea0c7531aeb852520f34bd56393b63a4b5ac75`; terminal Phase-3 head `ba5ac7a6f3438b054803ea50fee0d62d2b3fb3ca`; later falsifier run `34434431645`; artifact `10135645747` | Initial bounded relation result survives only for its original aperture. Multi-relation composition was later `FALSIFIED_COMMON_EVIDENCE_WORLD_BINDING` after support and refute from different Contract-B worlds were accepted together. |
| #98 temporal Contract C / Decision conformance RC0 | terminal record head `fc8e374b603ba375cd9047c1051bb1bc82c7d1fd`; evidence-world-bound freeze `10ce0894a56f265434b24963bf0543765c453996`; run `34434782626`; artifact `10135769621`; corrected Decision run `34504243114`; artifact `10163138696` | Bound-world successor refuses cross-bundle composition/projection. Unchanged Contract C 1.0 remains `VALID_WITH_PROVENANCE_COMPRESSION` for unresolved/irrelevant temporal relations because it has no neutral evidence contribution. Preserved first projector cross-bundle falsification and an apparatus-only Decision dependency failure/correction. |
| #99 unresolved-evidence provenance RC0 | tested head `34c92a5098389c3b691750baf9c3ab85fff5d20c`; run `34505136997`; artifact `10163485923`; digest `ab84eda20d93a3a6dec9600d16f35a96e8cebcd94bb27754f3362dbfda4cbd8d` | `SUPPORTED_BOUNDED_CONTRACT_C_UNRESOLVED_PROVENANCE_GAP`. Two legitimate unresolved executions over the same world and proposition used different passages, but Contract C 1.0 plus bound B could not reconstruct which passage participated because opaque `state:` basis IDs have no normative evidence edge. |
| #100 unresolved-provenance repair comparison | multiplicity head `aa5f0f1313e65e6d31493095214c76d743ca6d89`; run `34506201889`; artifact `10163899726`; digest `23ba4cb13870f0b2c5f213d3279faede9d17f19e638dea49444249328a0efb19` | Among four frozen repairs, neutral/non-deciding contributions uniquely preserved exact unresolved evidence refs plus independently-sufficient multiplicity. This was bounded repair-selection evidence, not proof that the inherited flat Contract C causal grammar was complete. |
| #104 CAL V1 RC1 authority-integrity successor | frozen RC1 `a902621e8baea3063dddd7f92ba975aade305464`; tree `0ad4434e4a897b39cda062917a3c1eb0968d11aa` | Draft successor candidate, not production. Adds relation-boundary source/world/identity revalidation after the parent Q12 authority-integrity failure. |
| #105 fresh RC1 qualification | terminal commit `3552fc83676304e3948b1e8db60da77b26877bc0`; decisive run `34675244077`; job `103503854205`; fresh cohort `19/19`; unsafe count `0` | `SUPPORTED_BOUNDED_RC1_QUALIFICATION`, with programme recommendation `BLOCKED ON SPECIFIC CONTRACT OR CONSUMER DECISION`. Does not establish canonical Contract C successor authority. |
| #106 successor producer conformance RC0 | CAL base `a902621e8baea3063dddd7f92ba975aade305464`; current research head inspected `9331aff4ee5715c2ab7b82ddb38eea2c34c7da57`; run `34726677711`; job `103641897133`; artifact `10307489383`; digest `c5189ac571ca6217bdd62ad30e8b3b72357f032491feda47bb1e8520c7779637` | Terminal `FALSIFIED`. `(S1 OR S2) AND R` was projected as one flat three-member `jointly_sufficient` basis even though ablating either support preserved the mixed terminal state. Structural validation passed, demonstrating that schema validity did not establish semantic causal sufficiency. A 2026-09-13 comment explicitly preserves #106 and directs the successor programme to issue #93 rather than patching the exporter. |

## Decision Engine evidence inspected

| Record | Exact identity / decisive evidence | Preserved result and present use |
| --- | --- | --- |
| Production V1 qualification/release #70 | exact qualified release-candidate `8d20a0a5c689797c77ae9e1a5629ff1be9f41cc9`; merge/release commit `7be709b2141c767c5da89b8b94cf90233c4238fe`; qualification run `34608924102`; artifact `10266414909` | Production authority is the bounded Decision Engine v1.0.0 release at `7be709b...`. Its public release explicitly excludes Contract C research `non_deciding`. |
| #67 non-deciding consumer RC0 | PR terminal head `9a0d8f78a76f74135eca60f51993f7cf5cfca6bc`; tested implementation `cd591c08c56a0336c8c2052c005a935de6ab1140`; run `34530232915`; artifact `10173178817` | `SUPPORTED_BOUNDED_CROSS_REPO_CONSUMER`. Preserved neutral evidence and multiplicity while HOLDing `not_checkable`. It explicitly states it is not a clean-room/context-free reproduction. |
| #72 current-main minimal in-band conformance RC1 | terminal head `3227726e8aee0eefa637fc65a756ca90edd6c844`; decisive scientific head `3ad518b9315d4767eae3d2a46f14e09975949479`; run `34695724968`; artifact `10297559181` | `SUPPORTED_CURRENT_MAIN_MINIMAL_IN_BAND_CONFORMANCE`, programme gate `BLOCKED_CONTEXT_FREE_REPRODUCTION_REQUIRED`. Preserved first-run wrong-error-class deviation. Maintained released-1.0 path stayed unchanged and rejected research successor bytes. |
| #73 context-free Consumer B evaluator freeze | evaluator head `97cb968ac8793adb575640404730399a8798ad98`; sparse aperture commit `cb1d27ff00ae030093c5e97d78477cec7f20c6f4`; self-check run `34710510423` | Supervisor-only evaluator freeze for the earlier minimal candidate. This programme has inspected it, so this context is not eligible to claim independence. A later independent-consumer test must be performed in a separate restricted context after a new candidate is frozen. |

## Authority boundary reconstructed from evidence

**Production authority:** released Contract C 1.0.0 at `5fe55f9...` remains immutable for its bounded released producer, and Decision Engine v1.0.0 at `7be709b...` remains the maintained downstream production authority.

**Observed research facts:** exact common Contract-B world binding, exact proposition binding, exact evidence participation, support/refutation/non-polarized semantics, causal versus residual role, and causal multiplicity are all capable of affecting faithful reconstruction. Contract C 1.0 loses unresolved evidence provenance in #99. The two-leaf successor preserves neutral participation but its inherited flat causal grammar is falsified by #106.

**Inference carried into Phase 0:** the successor must be derived from semantic obligations, not by widening Contract C 1.0. No representation has yet been selected.

**Unresolved choices:** exact causal representation, whether a separate contribution ID remains necessary, whether repeated passage hashes are necessary when exact Contract B is bound, whether generic assessment slots remain public obligations, whether rule/state basis concepts remain public, whether the full producer policy payload must remain in-band, and the final canonicalization/profile/version strategy.

**Excluded authority:** Contract C does not own the Contract-B evidence world, CAL private reasoning traces, arbitrary confidence/scalar semantics, Decision thresholds/routing, actor/delegation/approval state, Contract E Authorization, or execution occurrence.
