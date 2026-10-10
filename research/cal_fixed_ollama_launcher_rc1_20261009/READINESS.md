# RC1 preparation: not frozen, not run

Only this new directory was added. No freeze, worker, Ollama call, network probe,
acceptance test, commit, push or PR update was performed. Static Python compilation
and JSON parsing are the permitted verification; they establish no gate pass.

The successor includes the runner, two-function adapter, same-worker socket
probe, exact dispatcher controls, external receipt checker, inherited request/
provider expectations, RC1 synthetic manifest and an offline freeze generator.
Read PROTOCOL.md for frozen outcomes, ownership, first-stop rules and limits.

Missing prerequisites for a later operator:

1. Complete the external controller-only `PINS.json` from `PINS.template.json`: immutable Official Python image digest and local image ID,
   linux/arm64 metadata, image/resulting-worker Config.Env, metadata-derived
   PYTHON_VERSION; controller platform/Python version, executable paths/hashes,
   HOME, Docker's exact Unix endpoint, model manifest/blob paths. Existing provider
   and model hashes are inherited exact requirements. No image substitution or
   installation occurs automatically. Obtain pins/provisioning evidence without
   running these qualification controls; do not use worker results to set them.
2. Review every candidate byte and command, then separately commit the completed
   preparation on this branch. No old file may differ from base
   `e0bffd2722b0781acba11fa03e1bf51f8fba3fa0`. Record that preparation commit.
3. At that clean preparation commit, explicitly generate the freeze **before any
   exposure**, with a real UTC timestamp. From this directory:

   ```sh
   python3 -E -s -B prepare_freeze.py --pins-path /EXTERNAL/CONTROLLER/PINS.json --prepared-commit PREPARATION_COMMIT --frozen-at UTC_ISO_TIMESTAMP
   ```

   Review FREEZE.json, then make a separate candidate commit adding only that
   file. Record its final commit ID and the SHA-256 of FREEZE.json externally.
   The generator is provided, not executed; FREEZE.json does not yet exist.
4. Separately review/admit that exact candidate for **one zero-model qualification**.
   Fill a copy of `OPERATOR-REVIEW.template.json` outside the repo with operator
   identity/time, final commit, freeze hash, fresh absolute external receipt path
   and existing external ledger path. Preserve/reuse that same ledger forever;
   never remove its per-freeze attempt reservation. This is an explicit operator
   record, not a cryptographic signature or automatic permission grant.

Only after those steps and separate authority, the exact runner command from
this directory is (replace uppercase identity/path placeholders):

```sh
python3 -E -s -B qualify_once.py /ABSOLUTE/FRESH/EXTERNAL/RECEIPTS --candidate-commit FINAL_CANDIDATE_COMMIT --freeze-sha256 FREEZE_SHA256 --operator-review /ABSOLUTE/EXTERNAL/OPERATOR-REVIEW.json --pins-path /EXTERNAL/CONTROLLER/PINS.json
```

Use the exact controller Python binary whose identity is in the external PINS.json. The receipt
parent and ledger must already exist. Keep the repository clean and use `-B` to
avoid changing the frozen inventory. No dry-run mode executes subsets of gates.
After any first stop, preserve everything; corrections require a newly named
successor. Never edit expectations, image pins or request/control bytes to fit
observations. Do not commit/push as part of this preparation task.

Known blind spots: image availability and Docker/Python configuration are
unverified; #175's historical Git object is absent locally (module hashes match
its recorded freeze); copied OBSERVED metadata is historical only. Runtime checks
cannot attest a running provider binary from an on-disk hash, erase provider
memory, establish independent authorship, defeat a hostile controller, or qualify
model behavior. Larger Python image/runtime surface is an explicit cost of
observable socket errno. A zero-model completion leaves Q13
`PENDING_EXPLICIT_OWNER_ADMISSION_REVIEW`; no actor launch is authorized.

**Private-path rule:** actual absolute controller HOME, model paths and Docker Unix socket are never committed; `PINS.template.json` is public-safe, `FREEZE.json` binds the SHA-256 of the controller-only exact `PINS.json` and publishes a safe digest-only summary. Preserve the unredacted raw pins outside the actor and repository.

## Pre-freeze local model manifest identity change

The local qwen3.5:9b manifest observed before this successor freeze differs in wire identity from RC0: current SHA-256 `9cda952e5d8f43bd4ddd3954c82e404e6cc286e04ceb77fa536f9f7113d7b28d`, previous `6488c96fa5faab64bb65cbd30d4289e20e6130ef535a93ef9a49f42eda893ea7`. Original three layers are identical, with three additional OCI index/manifest layers now present and their published digests independently verified locally. This is an explicit **new subject identity**, not a relabeling of PR #176. Extra layers may affect provider selection; Q03 must still match the frozen complete prior prompt or stop. The cause of the manifest update (mtime 2026-10-09T14:07:14Z) is not established; no model inference was used to investigate it. The original manifest and failure remain preserved.

**Docker image-store resolution:** The official image was pulled with `--platform linux/arm64` and its repo descriptor observed at `python@sha256:48b13b003dda20b16f9442b8475aa05fe21bf6579a8c881db92ffb4d8fd20f83`. On the observed Docker Desktop engine, `docker image inspect python@sha256:…` returned no such image, while the **immutable image ID** `sha256:48b13b003dda20b16f9442b8475aa05fe21bf6579a8c881db92ffb4d8fd20f83` resolved and matched the local image. RC1 therefore pins/uses that exact image ID with `--pull never`, not a mutable tag or an unresolvable alias. This is a prefreeze provisioning choice; actual worker configuration remains a Q04 observation.
