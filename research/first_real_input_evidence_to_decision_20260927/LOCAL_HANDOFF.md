# First real-input evidence-to-decision local handoff — exact single-item successor

Status: **PREPARATION ONLY / PRIVATE INPUT NOT ADMITTED**.

This successor replaces the PR #151 local intake command only. PR #151 and frozen ERS #4 remain preserved evidence. The first-input run authority is the separately identified ERS single-item RC1 subject in `SUBJECTS.json`.

## Exact controlled path

```text
ERS single-item RC1 / PR #15
  -> deterministic ERS-to-Gate byte/identity adapter
  -> Gate #54
  -> released Contract A 2.0 validation
  -> current EB #120
  -> Contract B 1.2
  -> independently reviewed trusted CAL targets
  -> CAL #183
  -> parent-bound Contract C #121
  -> frozen independent Contract C consumer
  -> Decision #86
  -> released Contract D 1.0.0
```

No expected semantic disposition is preregistered. `not_checkable/HOLD` is a legitimate observation.

A missing/ambiguous provenance stop or non-`all_of` Gate result is also a legitimate first-case terminal observation. **Do not choose another item/claim after observing one merely to obtain a runnable shape.**

## Hard stops

Stop and preserve the observation when:

1. an exact checkout/blob verification fails;
2. ERS/Ollama health check fails before private input admission;
3. the exact single-item allowlist rejects cardinality/path/hash admission;
4. explicit source provenance escapes the root, mismatches recorded bytes, or reaches no resolved raw-local provenance;
5. the selected claim has no recoverable raw local source bytes;
6. Gate emits no Contract A;
7. the first admitted Contract A is not declared `all_of`: preserve `STOPPED.json`; **reroll is not authorized**;
8. any child target lacks separate authoring plus independent semantic-fidelity review;
9. current EB rejects the Contract A or a replay/substitution control fails;
10. continuation would require Contract E, an ERS write, target compilation, evidence auto-admission, release/promotion, or an invented semantic default.

## 1. Reuse existing verified checkouts; add only the new ERS subject

The previous local preflight already verified all unchanged downstream subjects. Keep those clean detached checkouts.

Create one additional clean detached ERS checkout/worktree at:

```text
camerontjs-dot/epistemic-research-system
3cf04f2defa07513ec2be4418d41698ca7aeebab
```

Then point:

```bash
export PREP_ROOT=/path/to/apparatus-contracts/research/first_real_input_evidence_to_decision_20260927
export ERS_ROOT=/clean/ers-single-3cf04f2d
export GATE_ROOT=/existing/verified/gate-89ca88c7
export A_ROOT=/existing/verified/apparatus-a-529c92b4
export EB_ROOT=/existing/verified/eb-08ca896d
export CAL_ROOT=/existing/verified/cal-ddaf9455
export C_ROOT=/existing/verified/apparatus-c-c5b1d757
export C_RC2_ROOT=/existing/verified/apparatus-c-b42c827a
export C_RESOLVER_ROOT=/existing/verified/apparatus-c-1d33e061
export C_CONSUMER_ROOT=/existing/verified/research-scaffold-12e7e640
export DE_ROOT=/existing/verified/decision-6cdb59c2
export D_ROOT=/existing/verified/apparatus-d-298a1a0f
```

Verify the complete subject set offline. This reuses the old clean checkouts and changes only the ERS role:

```bash
python3 "$PREP_ROOT/scripts/verify_subjects.py" \
  --subjects "$PREP_ROOT/SUBJECTS.json" \
  --root ers_intake="$ERS_ROOT" \
  --root gate="$GATE_ROOT" \
  --root contract_a="$A_ROOT" \
  --root evidence_bundler="$EB_ROOT" \
  --root cal="$CAL_ROOT" \
  --root contract_c_parent_bound="$C_ROOT" \
  --root contract_c_rc2="$C_RC2_ROOT" \
  --root contract_c_resolver="$C_RESOLVER_ROOT" \
  --root contract_c_consumer="$C_CONSUMER_ROOT" \
  --root decision="$DE_ROOT" \
  --root contract_d="$D_ROOT"
```

## 2. First executable continuation: runtime health only, no private input

The prior local attempt observed `OllamaAdapter.health_check("qwen3.5:9b") == false` with localhost:11434 connection refused. Disk presence did not establish serving/model suitability.

Do not select or read a private MainFrame item while that remains unresolved.

Using the exact ERS RC1 checkout and the existing local ERS Python environment:

```bash
export ERS_MODEL=qwen3.5:9b
export ERS_PYTHON=/path/to/python-with-existing-ERS-adapter-dependencies

PYTHONPATH="$ERS_ROOT" "$ERS_PYTHON" - <<'PY'
import os
from adapters.ollama import OllamaAdapter
model = os.environ["ERS_MODEL"]
adapter = OllamaAdapter(model)
ok = adapter.health_check()
print({"model": model, "health_check": ok})
raise SystemExit(0 if ok else 2)
PY
```

If this returns false, stop `BLOCKED_BEFORE_PRIVATE_INPUT`. This handoff does not authorize starting/downloading/changing a model service.

## 3. Admit exactly one private knowledge path

Only after runtime health passes, choose the first real synthesized knowledge item. Do not scan the directory to find a convenient case.

Set:

```bash
export RUN=/fresh/output/cal-first-real-input
export MAINFRAME_ROOT=/path/to/MainFrame
export KNOWLEDGE_REL='10_knowledge/<exact/private/path>.md'
mkdir -p "$RUN"
cp "$PREP_ROOT/ERS_ALLOWLIST.template.json" "$RUN/ERS-ALLOWLIST.json"
```

Compute the exact selected document identity directly from that one operator-chosen path:

```bash
export DOC_SHA="$("$ERS_PYTHON" - <<'PY'
import hashlib, os
from pathlib import Path
root = Path(os.environ["MAINFRAME_ROOT"]).resolve(strict=True)
raw = os.environ["KNOWLEDGE_REL"]
path = (root / raw).resolve(strict=True)
print("sha256:" + hashlib.sha256(path.read_bytes()).hexdigest())
PY
)"
```

Fill `$RUN/ERS-ALLOWLIST.json` with exactly:

```json
{
  "schema": "ers.mainframe_single_item_allowlist.rc1",
  "items": [
    {
      "knowledge_path": "THE EXACT $KNOWLEDGE_REL VALUE",
      "document_identity": "THE EXACT $DOC_SHA VALUE"
    }
  ]
}
```

RC1 itself independently rechecks cardinality, traversal, lexical/resolved equality, file existence, document hash, explicit provenance confinement and resolved-local source bytes before any model generation. It never calls the RC0 tree scanner.

Run:

```bash
PYTHONPATH="$ERS_ROOT" "$ERS_PYTHON" "$ERS_ROOT/harness/backlog_single_item_intake.py" \
  --mainframe-root "$MAINFRAME_ROOT" \
  --allowlist "$RUN/ERS-ALLOWLIST.json" \
  --output-dir "$RUN/ers" \
  --model "$ERS_MODEL"
```

If `$RUN/ers/STOPPED.json` exists, preserve it and stop. Do not broaden provenance discovery or select another item.

## 4. Select one claim from that one admitted inventory

Inspect only `$RUN/ers/inventory.json`. It must identify schema `ers.mainframe_single_item_intake.rc1`, mode `exact_single_item`, and exactly one document.

Copy `SELECTION.template.json` to `$RUN/SELECTION.json` and fill one existing claim from that document whose `resolved_raw_source_ref_ids` is non-empty.

This selects a claim **within the already admitted document**. It does not authorize selecting a different knowledge document if downstream shape is inconvenient.

## 5. Prepare the public runtime and ERS -> Gate packet

```bash
python3.11 -m venv "$RUN/venv"
export PY="$RUN/venv/bin/python"
"$PY" -m pip install --upgrade pip
"$PY" -m pip install build rfc8785==0.1.4 -e "$GATE_ROOT" -e "$EB_ROOT"
mkdir -p "$RUN/dist"
"$PY" -m build --wheel --outdir "$RUN/dist" "$CAL_ROOT"
"$PY" -m pip install "$RUN"/dist/*.whl
```

Adapt identity/text/bytes only:

```bash
"$PY" "$PREP_ROOT/scripts/ers_to_gate.py" \
  --intake-dir "$RUN/ers" \
  --selection "$RUN/SELECTION.json" \
  --gate-packet "$RUN/GATE-PACKET.json" \
  --receipt "$RUN/ERS-TO-GATE-RECEIPT.json"
```

Run current Gate #54:

```bash
"$PY" "$GATE_ROOT/scripts/run_gate_production_slice_v1.py" \
  "$RUN/GATE-PACKET.json" \
  --out-dir "$RUN/gate" \
  --implementation-identity "first-real-input@89ca88c7f0a661601f7eb798b6759667fa20ab3f"
```

If Gate does not emit `CONTRACT-A.json`, preserve that as the first-case stop.

Validate any emitted Contract A against released A2:

```bash
PYTHONPATH="$A_ROOT" "$PY" -c \
'import json,sys; from validators.contract_a import validate_candidate; validate_candidate(json.load(open(sys.argv[1], encoding="utf-8")))' \
"$RUN/gate/CONTRACT-A.json"
```

Then bind it back to ERS and classify the CAL #183 shape:

```bash
"$PY" "$PREP_ROOT/scripts/check_gate_output.py" \
  --contract-a "$RUN/gate/CONTRACT-A.json" \
  --adapter-receipt "$RUN/ERS-TO-GATE-RECEIPT.json" \
  --out-target-review "$RUN/TARGET-REVIEW.json" \
  --stop-receipt "$RUN/STOPPED.json"
```

Exit code 3 plus `STOPPED.json` means the **first case stops**. It explicitly records `reroll_authorized=false`.

## 6. Mandatory target-review stop

Only if `TARGET-REVIEW.json` was produced, stop before CAL.

Each exact child target must be authored and then independently reviewed against the exact Contract A child text. Fill target paths/hashes, distinct author/reviewer context identities, `independent_review=true`, and `semantic_fidelity_attested=true`.

Verify:

```bash
"$PY" "$PREP_ROOT/scripts/verify_target_review.py" \
  --review "$RUN/TARGET-REVIEW.json" \
  --contract-a "$RUN/gate/CONTRACT-A.json"
```

This mechanical verifier does not replace semantic review.

## 7. Optional explicit EB admission

Current EB #120 defaults retained candidates to `needs-review`. Nothing in this handoff auto-accepts evidence.

Omitting admission is allowed and may correctly lead to `not_checkable/HOLD`.

If explicit admission is separately authorized, it must bind exact retained `proposition_id/passage_id` pairs in an `evidence-bundler-admission-v1` file. Do not change admissions after seeing the CAL/Decision result.

## 8. Execute the admitted A -> D path

Only after trusted target review:

```bash
"$PY" "$PREP_ROOT/scripts/run_current_subject.py" \
  --contract-a "$RUN/gate/CONTRACT-A.json" \
  --target-review "$RUN/TARGET-REVIEW.json" \
  --out-root "$RUN/a-to-d" \
  --contract-a-root "$A_ROOT" \
  --eb-root "$EB_ROOT" \
  --cal-cli "$RUN/venv/bin/claim-audit-v1-parent" \
  --contract-c-root "$C_ROOT" \
  --rc2-root "$C_RC2_ROOT" \
  --resolver-root "$C_RESOLVER_ROOT" \
  --consumer-root "$C_CONSUMER_ROOT" \
  --decision-root "$DE_ROOT" \
  --contract-d-root "$D_ROOT" \
  --python "$PY" \
  --node node
```

Add `--eb-admission /exact/admission.json` only for an independently prepared admission.

The runner repeats the exact A->D inputs twice, requires byte-equivalent key artifacts, and performs the preregistered unresealed Contract-A source-byte substitution. Current EB must reject it before artifact emission.

Expected local record:

```text
$RUN/a-to-d/RUN-RECEIPT.json
```

No Contract E or ERS write belongs in this milestone.
