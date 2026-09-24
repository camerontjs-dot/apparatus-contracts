# ERS-EVAL-TIME-PROV-20260922-05 repository-root successor preregistration

Status: preregistered after a mechanical diagnosis of the frozen PR #148 runner and before any runner edit. This commit does not change the runner, the runtime, PR #130, fixtures, or scientific controls.

## Predecessor

Apparatus PR #148 remains an open Draft at head `b673b2b06804e94042ad35d4621f4a4ca5ee4851`, tree `97e832138b7f9c955bc1eb1a940dbb937a230142`, base `c054d2fb0822e61833cb9e8a5acb7072dbce6531`. Its runner blob stays `79a347c9698610a1c743074e426a79590cb32ba4`. I am not amending, force-pushing, or rewriting that candidate.

Preserved sequence:

1. Earlier receipt-preflight attempt, 85/86, `INCONCLUSIVE`, retained at `/tmp/cal-ers05-runner-runtime-successor-20260924/final-qualification/preflight.json`.
2. PR #148 non-scientific qualification PASS. `--help` and the frozen runtime gate did not execute the scientific matrix.
3. First scientific matrix attempt `INCONCLUSIVE` before any matrix case. Receipt `/private/tmp/ers-eval-matrix-20260924/outputs/matrix-run/FAILURE.json`, SHA-256 `d169327a4958e203e087489a71a000460de5b36ad33583559d86619f2057f3d0`. `matrix_progress` is empty. Contract E, the supervisor, PIPE cases, sandbox mutation, and provenance sidecars did not run.

The scientific disposition of that attempt is `INCONCLUSIVE`. The cause is a frozen evaluator repository-root/path-resolution defect. No scientific result was observed.

## Diagnosis

`diagnosis/reproduce_root_resolution.py` evaluated the frozen runner file in place. It did not import the runner.

`HERE` is the directory containing `reproduce_rc6_fixture_bound.py`. The frozen assignment is `ROOT = HERE.parents[1]`.

| Expression | Directory | Contains `.git` | Equals `git rev-parse --show-toplevel` |
| --- | --- | --- | --- |
| `HERE` | `fixture-bound-identity-successor-rc0` | no | no |
| `HERE.parents[0]` | `ers-contract-e-evaluation-provenance-20260921` | no | no |
| `HERE.parents[1]` | `research` | no | no |
| `HERE.parents[2]` | repository root | yes | yes |
| `HERE.parents[3]` | parent of the repository | no | no |

`git -C research rev-parse --show-toplevel` still prints the repository root, because Git walks upward. That is why ancestry and `hash-object` checks can succeed with the wrong `ROOT`. `HEAD:<path>` cannot: the path is repository-relative, and `Path.relative_to(ROOT)` has already removed `research/`.

Against the committed apparatus freeze receipt, `parents[1]` produces:

`HEAD:ers-contract-e-evaluation-provenance-20260921/fixture-bound-receipt-contract-successor-rc0/FREEZE_RECEIPT.json`

Git exits 128. Its hint names the path that does exist:

`HEAD:research/ers-contract-e-evaluation-provenance-20260921/fixture-bound-receipt-contract-successor-rc0/FREEZE_RECEIPT.json`

That failing spec is the command in the preserved scientific `FAILURE.json`. `parents[2]` resolves the same file to blob `bc7d3938be9146dd6455ab5f9fda896f22a70274`.

The same wrong root changes a later join. `ROOT / "research/ers-render-bound-shadow-composition-20260921/reproduce.py"` is absent under `parents[1]` and present under `parents[2]`. The observed attempt stopped before that line. Sixteen `ROOT` names exist. The two string uses of `"ROOT"` as a claim id are not the path variable. No other assignment is required to make both the `relative_to` conversion and the `research/...` join address the repository.

## Authorized correction

I authorize exactly one runner change:

`ROOT = HERE.parents[2]`

PR #148's two earlier authorized changes stay in place: the ERS PR #14 receipt path, and `apparatus.scientific_preregistration.commit`.

No other runner semantic change is authorized. If the strengthened bootstrap cannot pass with this one change, stop and record the failure. Do not widen the runner after that observation.

## Unchanged scientific authority

The hypothesis is unchanged. PR #130 head `dcdd10355e2f885273d843eef6e345bafca95faa` remains the scientific authority.

Question: can the Contract E to ERS shadow composition bind an independently sourced evaluation time to the exact Contract E invocation and exact Contract E result such that post-evaluation substitution is rejected before `shadow_ready`?

All PR #130 matrix cases and expected outcomes remain frozen. This successor does not add or remove controls.

Bound identities, reconfirmed on 2026-09-24 before this preregistration:

| Role | Identity |
| --- | --- |
| PR #146 | open Draft, head `cd465d798220daa3f45261d3e6f385cf67224a46` |
| PR #147 | open Draft, head `c054d2fb0822e61833cb9e8a5acb7072dbce6531`, base `cd465d798220daa3f45261d3e6f385cf67224a46` |
| PR #130 | open Draft, head `dcdd10355e2f885273d843eef6e345bafca95faa` |
| PR #131 | closed Draft, head `077ccf6d386526bda258b3e90bd43e153c4c04c5`; this immutable contract object remains the bound receipt-contract authority |
| ERS PR #14 | open Draft, head `aa214666c9a68871c0d878a70b7f3833d49dbe9b` |
| ERS implementation | `65f47d029fb734be1d5d506a135cbeba813f6be8` |
| Transcript schema blob | `b85b38ce95263e348d2ebd1293f76ffc87adcf6d` |
| Issuer public identity | `sha256:e7f4581c2d58eecd0279f895cf3dd49df3098d092fa1e083731d802fcd1db259` |
| Runtime lock | SHA-256 `4d0bd11eadca52c292cb883afc062fd95de6b03e8304dedf4820a027898a419f` |
| Wheelhouse | SHA-256 `68474c180d4e5d2b35df36354d68cc477a69061960cd26385661cad9a63a0214` |

The runtime is reused. It is not rebuilt unless this root correction is shown to require a package change. Qualification must prove the lock, wheelhouse, and interpreter identities rather than assume them.

## Qualification boundary

`--help` is not sufficient for this successor.

The new gate invokes the runner with the complete scientific argument shape and stops at an explicit boundary immediately before the first scientific operation. That operation is the frozen hold-case `shadow_gate` loop, which is followed by supervisor launch. The gate must reach the repository-relative `HEAD:<path>` checks, fixture and issuer checks, and the module loads required before that boundary.

During the gate, supervisor launch, Contract E evaluation, scientific PIPE execution, sandbox creation, scientific substitution, authentic transcript generation, provenance-sidecar capture, unauthorized network calls, and MainFrame writes are forbidden. Expected counters: Contract E `0`, supervisor `0`, scientific PIPE cases `0`, scientific mutations `0`, scientific sandbox creations `0`.

Required discrimination, using the real frozen inputs:

- predecessor blob `79a347c9698610a1c743074e426a79590cb32ba4` fails at the repository-root `HEAD:<path>` boundary;
- the corrected successor reaches the pre-scientific stop;
- a wrong root expression, and a receipt path outside the repository, are rejected at the path boundary rather than by an incidental parser or environment error.

The frozen decision-byte comparisons and profile import that the runner already performs before the hold loop are bootstrap. They are not the PR #130 mutation matrix.

No PR #130 scientific result may be observed before freeze. After freeze, do not repair this successor. Run the unchanged PR #130 matrix only if the strengthened gate passes.
