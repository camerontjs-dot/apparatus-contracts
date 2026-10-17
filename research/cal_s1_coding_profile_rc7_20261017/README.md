# CAL #173: S1 coding-profile RC7 preflight stop

**Status: BLOCKED_PREFLIGHT_TOOL_SAFETY_DENIAL. Q13: NOT_ADMITTED.**

This is an additive owner/controller preparation record, not an implemented or frozen actor profile. The operator explicitly approved an attempt to qualify #173 and requested a local-agent prompt. Live GitHub and the local source worktree were inspected before the attempted runtime preflight.

The branch starts from Apparatus Contracts Draft #182, commit `5f33a824ee5c92331ec3824aa2a8b71c18bf9683`. RC4's exact scientific subject remains `e53fc412a0db007ba87c4d1720cee66b781fc89c`; RC5 and RC6's first model-output failures are unchanged. The dependent CAL S1 packet remains at Draft #214 commit `a10e61f0d4be26ebb93a2b798d1a5f46470cc42c`, with seven-file staging manifest SHA-256 `de1df6d7da410ea3e58607d4ff967024bdf2cf6e28123961e1ad84e1c4aa62b4`.

## Observed stop

The remote terminal tool blocked a read-only pre-freeze identity request before execution. The request would have observed installed executable identities, Docker/image metadata and loopback Ollama version/model metadata, writing controller-private receipts. It requested no model inference or container creation.

The exact returned message is preserved in `QUALIFICATION_STOP.json`. No reason or platform case ID was supplied. The task-specific receipt directory subsequently listed no entries. No runtime pins, frozen candidate, model request, worker, new Q01-Q12 result or Q13 admission was produced. No alternate route was attempted.

This event is distinct from the earlier CAL ordinary `project-env` command denial. Neither denial was retried or bypassed in this task.

## Existing evidence and transfer limits

- Draft #175 establishes bounded packet construction and a code-isolated checker. Keep their established implementation; do not build another packet framework.
- RC4 establishes specified zero-model controls for its fixed two-file/two-function world. The immutable tool profile is Git blob `9c8fdc261d6ec87c955662097460aabf5e76741b`. Its read enum and single 4096-byte answer output do not provide a coding/test interface for the seven-file S1 task.
- Draft #182 records model-generated terminal-LF loss. The dispatcher preserved the supplied argument bytes; a prompt or successful scripted test did not cure the model-bearing failure. No layer-specific cause was established.
- Ollama's official tool-calling API describes model-requested functions and caller-provided tool results. Docker describes existing non-root/read-only/network-none mechanisms. These supply mechanisms, not conformance or admission evidence for a new profile.

Primary mechanism references, reviewed for the proposed interface only:

- https://docs.ollama.com/capabilities/tool-calling
- https://docs.ollama.com/api/chat
- https://docs.docker.com/engine/containers/run/
- https://docs.docker.com/engine/network/drivers/none/

## Next source-only work

`LOCAL_AGENT_PROMPT.md` is for a trusted local qualification lead, not the blinded CAL implementer. It allows the missing adapter and evaluator prerequisites to be developed with synthetic fixtures and fake runtime boundaries. It explicitly does not direct another agent to reproduce the blocked live preflight.

The smallest candidate interface must distinguish immutable packet reads, bounded code writes, fixed exposed-test invocation, and externally verified completion. If a line-array code transport is selected, its LF construction must be explicit, versioned and tested. Never normalize the original RC5/RC6 bytes or hide their failure.

Any future runtime step requires resolution of the platform boundary and a separately reviewed exact profile, input world, evaluator, environment and attempt authority. Required failure, unknown or not-run blocks admission. No unconditional CAL builder prompt is issued from this record.

## Publication boundary

Only the new research directory changes. Production contracts, validators, release metadata, old experiment code and raw evidence remain unchanged. Local absolute paths, runtime secrets and private source bodies are not published. This Draft is a preflight stop record; unrelated CI cannot qualify it.
