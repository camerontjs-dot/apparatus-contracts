# First real-input evidence-to-decision local handoff

Status: **PREPARATION ONLY**. This package does not contain private MainFrame input, an approved target, a real pipeline result, a Contract E run, or an ERS write.

## Objective

Run exactly one admitted real MainFrame-derived claim through:

```text
ERS #4 read-only intake
  -> deterministic ERS-to-Gate byte/identity adapter
  -> Gate #54
  -> released Contract A 2.0 validation
  -> EB #120
  -> Contract B 1.2
  -> independently reviewed trusted CAL targets
  -> CAL #183
  -> parent-bound Contract C #121
  -> independent Contract C consumer
  -> Decision #86
  -> released Contract D 1.0.0
```

No expected semantic disposition is preregistered. A deterministic `not_checkable/HOLD` is a legitimate observation.

## Hard stops

Stop without widening or repairing frozen subjects when any of these occurs:

1. an exact checkout/blob check fails;
2. ERS produces no recoverable raw local source bytes for the selected claim;
3. the ERS source bytes do not match their recorded content identities;
4. Gate emits no Contract A, or Contract A is not a declared `all_of` decomposition usable by CAL #183;
5. any Contract A child lacks an independently reviewed frozen target in one of CAL #183's two active families;
6. current EB rejects the real Contract A or produces a boundary failure;
7. deterministic replay differs at any required A->D artifact;
8. the Contract A source-substitution control is accepted or emits EB artifacts;
9. the next step would require Contract E, an ERS write, a target compiler, a release, or a semantic default.

## 1. Prepare clean exact checkouts

Use detached checkouts/worktrees so active branches are not moved. Exact commits and executable blobs are in `SUBJECTS.json`.

Define:

```bash
export PREP_ROOT=/path/to/apparatus-contracts/research/first_real_input_evidence_to_decision_20260927
export ERS_ROOT=/clean/ers-5c22d846
export GATE_ROOT=/clean/gate-89ca88c7
export A_ROOT=/clean/apparatus-a-529c92b4
export EB_ROOT=/clean/eb-08ca896d
export CAL_ROOT=/clean/cal-ddaf9455
export C_ROOT=/clean/apparatus-c-c5b1d757
export C_RC2_ROOT=/clean/apparatus-c-b42c827a
export C_RESOLVER_ROOT=/clean/apparatus-c-1d33e061
export C_CONSUMER_ROOT=/clean/research-scaffold-12e7e640
export DE_ROOT=/clean/decision-6cdb59c2
export D_ROOT=/clean/apparatus-d-298a1a0f
```

Verify every executable subject before private input is read:

```bash
python3 "$PREP_ROOT/scripts/verify_subjects.py"   --subjects "$PREP_ROOT/SUBJECTS.json"   --root ers_intake="$ERS_ROOT"   --root gate="$GATE_ROOT"   --root contract_a="$A_ROOT"   --root evidence_bundler="$EB_ROOT"   --root cal="$CAL_ROOT"   --root contract_c_parent_bound="$C_ROOT"   --root contract_c_rc2="$C_RC2_ROOT"   --root contract_c_resolver="$C_RESOLVER_ROOT"   --root contract_c_consumer="$C_CONSUMER_ROOT"   --root decision="$DE_ROOT"   --root contract_d="$D_ROOT"
```

This check is intentionally offline. It also requires clean working trees.

## 2. First private/local requirement: one real read-only intake

Choose a **single MainFrame project/tag containing a synthesized knowledge item that has explicit recoverable local provenance**. Do not fabricate or copy a public fixture in place of the private item.

Set a fresh run directory and an ERS Python environment that can import the exact #4 checkout plus its Ollama adapter:

```bash
export RUN=/fresh/output/cal-first-real-input
export MAINFRAME_ROOT=/path/to/MainFrame
export PROJECT_TAG=<real 10_knowledge project/tag>
export ERS_MODEL=<locally available model>
export ERS_PYTHON=/path/to/python-with-ERS-adapter-dependencies

PYTHONPATH="$ERS_ROOT" "$ERS_PYTHON" "$ERS_ROOT/harness/backlog_intake.py"   --mainframe-root "$MAINFRAME_ROOT"   --project-tag "$PROJECT_TAG"   --output-dir "$RUN/ers"   --model "$ERS_MODEL"
```

This is the first capability-dependent local step. The GitHub preparation cannot choose the private item or supply its bytes.

Inspect `$RUN/ers/inventory.json`. Copy `SELECTION.template.json` to `$RUN/SELECTION.json` and fill exactly one existing `knowledge_path`, `document_identity`, and `claim_id` that has non-empty `resolved_raw_source_ref_ids`.

## 3. Freeze the deterministic ERS -> Gate packet

Create a runtime for the public components. The CAL install mirrors the successful #123 composition setup:

```bash
python3.11 -m venv "$RUN/venv"
export PY="$RUN/venv/bin/python"
"$PY" -m pip install --upgrade pip
"$PY" -m pip install build rfc8785==0.1.4 -e "$GATE_ROOT" -e "$EB_ROOT"
mkdir -p "$RUN/dist"
"$PY" -m build --wheel --outdir "$RUN/dist" "$CAL_ROOT"
"$PY" -m pip install "$RUN"/dist/*.whl
```

Adapt only identity/text/bytes:

```bash
"$PY" "$PREP_ROOT/scripts/ers_to_gate.py"   --intake-dir "$RUN/ers"   --selection "$RUN/SELECTION.json"   --gate-packet "$RUN/GATE-PACKET.json"   --receipt "$RUN/ERS-TO-GATE-RECEIPT.json"
```

Run current Gate #54:

```bash
"$PY" "$GATE_ROOT/scripts/run_gate_production_slice_v1.py"   "$RUN/GATE-PACKET.json"   --out-dir "$RUN/gate"   --implementation-identity "first-real-input@89ca88c7f0a661601f7eb798b6759667fa20ab3f"
```

Validate the emitted Contract A with released A2:

```bash
PYTHONPATH="$A_ROOT" "$PY" -c 'import json,sys; from validators.contract_a import validate_candidate; validate_candidate(json.load(open(sys.argv[1], encoding="utf-8")))' "$RUN/gate/CONTRACT-A.json"
```

Bind it back to the exact ERS claim/source bytes and generate the **unfilled** target-review packet:

```bash
"$PY" "$PREP_ROOT/scripts/check_gate_output.py"   --contract-a "$RUN/gate/CONTRACT-A.json"   --adapter-receipt "$RUN/ERS-TO-GATE-RECEIPT.json"   --out-target-review "$RUN/TARGET-REVIEW.json"
```

### STOP HERE

Do not execute CAL until each child target is authored and then independently reviewed against the exact child text. Fill `TARGET-REVIEW.json` with target paths/hashes, distinct author/reviewer context identities, `independent_review=true`, and `semantic_fidelity_attested=true`.

Then verify:

```bash
"$PY" "$PREP_ROOT/scripts/verify_target_review.py"   --review "$RUN/TARGET-REVIEW.json"   --contract-a "$RUN/gate/CONTRACT-A.json"
```

The verifier checks identities, bytes, text binding, and active-family membership. It does **not** replace the semantic review.

## 4. Optional explicit EB admission

Current EB #120 defaults retained candidates to `needs-review`; only explicit `accepted` decisions become CAL-admitted evidence. Auto-acceptance is forbidden.

You may omit admission entirely. That is still a valid bounded run and may correctly produce `not_checkable/HOLD`.

If an explicit admission is desired, first run a preview in a disposable directory, inspect only retained candidates, and create an `evidence-bundler-admission-v1` file whose decisions bind exact `proposition_id/passsage_id` pairs. The final runner accepts it through `--eb-admission`.

## 5. Execute the admitted A -> D path

After target review, run:

```bash
"$PY" "$PREP_ROOT/scripts/run_current_subject.py"   --contract-a "$RUN/gate/CONTRACT-A.json"   --target-review "$RUN/TARGET-REVIEW.json"   --out-root "$RUN/a-to-d"   --contract-a-root "$A_ROOT"   --eb-root "$EB_ROOT"   --cal-cli "$RUN/venv/bin/claim-audit-v1-parent"   --contract-c-root "$C_ROOT"   --rc2-root "$C_RC2_ROOT"   --resolver-root "$C_RESOLVER_ROOT"   --consumer-root "$C_CONSUMER_ROOT"   --decision-root "$DE_ROOT"   --contract-d-root "$D_ROOT"   --python "$PY"   --node node
```

Add `--eb-admission /exact/admission.json` only if that separate admission was explicitly prepared.

The runner executes the same frozen inputs twice, requires byte-equivalent key artifacts through D1, and then mutates one Contract A source byte **without resealing its hashes**. Current EB must reject the substitution before artifact emission.

Expected output record:

```text
$RUN/a-to-d/RUN-RECEIPT.json
```

The receipt records the observed CAL conclusion, Decision disposition and D1 consumer outcome without converting any particular outcome into a success criterion.

## 6. Scope of the local result

A completed admitted run may support only a bounded statement about this exact real input and exact frozen/current subjects. It does not authorize merge, release, Contract E, ERS execution, MainFrame mutation, unattended target authoring, or general semantic accuracy.

Update Apparatus #137 with the exact run receipt and subject identities after execution. Preserve any failure as the result; do not change the target, evidence admission, frozen subject, or acceptance rule after observing an inconvenient decision.
