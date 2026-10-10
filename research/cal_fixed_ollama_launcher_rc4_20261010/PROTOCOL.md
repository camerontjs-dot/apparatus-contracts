# CAL fixed launcher RC4: actual link-state network discriminator

Owner: [apparatus-contracts #173](https://github.com/camerontjs-dot/apparatus-contracts/issues/173).
Previous frozen [RC3 / Draft #180](https://github.com/camerontjs-dot/apparatus-contracts/pull/180)
stopped at Q08 when `socket.if_nameindex()` returned ten Linux kernel interface
names, not just `lo`. The first failure and all **317** verified raw receipt
objects remain preserved at retrospective head
`d9ac7505531369221fe89ea239645b09f886f6a3`. The existing
numeric `connect_ex` egress refusal and positive local socket had behaved
as frozen, but no interface flags or operstate were measured. **RC3 Q08 did
not pass.** RC4 is a new candidate and will exercise its own controls.

## Inherited contract, exact change and tested basis

The full Q01–Q13 protocol and earlier safety/evaluator boundaries are retained
verbatim in `PARENT-PROTOCOL.md`, SHA-256 `bbe02c0b8842d348c687894b5284889bec5a81a04e3dcd2b69afcf117f825cc1`. This new document
tightens the Q08 observation/acceptance rule; it does not change initial
Ollama request/render expectations, packet custody, the fixed two-function
adapter, actual docker privileges, Q05–Q07 controls or Q09–Q12 requirements.
No model inference/actor is authorized.

The Linux kernel documents `/sys/class/net/<iface>/flags` as the actual
IFF_* bitmask and `/sys/class/net/<iface>/operstate` as RFC2863 operational
state: https://github.com/torvalds/linux/blob/master/Documentation/ABI/testing/sysfs-class-net ;
`IFF_UP`, `IFF_LOOPBACK`, `IFF_RUNNING`, `IFF_LOWER_UP` are defined in
https://github.com/torvalds/linux/blob/master/include/uapi/linux/if.h .
Docker's maintained `--network none` contract exposes no Docker-managed
external network attachment, but its loopback-only documentation is not
a substitute for inspection of kernel-reported tunnel names:
https://docs.docker.com/engine/network/drivers/none/ .

RC4's same-worker `worker_control.py` reports for **each actually enumerated**
interface the Linux sysfs flags, ifindex and operstate, plus original IPv4/IPv6
routes and `/proc/net/if_inet6` IPv6 address affiliations. The pure
`network_state_validator.py` requires `lo` to be administratively UP and
LOOPBACK, and every non-loopback name to be administratively DOWN, not RUNNING,
not LOWER_UP, with recognized non-operational state and no non-loopback IPv4
route, IPv6 route or IPv6 assigned address. Unknown fields, missing flags,
unrecognized operational states, malformed/extra routing, and unexpectedly
usable non-loopback devices fail closed. It may accept *named* inert tunnel
interfaces only with affirmative state observations.

Critically, RC4 **retains the full Q08 direct socket checks**: a successfully
accepted synthetic local socket with verified content, actual
`ENETUNREACH/101` from `192.0.2.1:9`, actual `ECONNREFUSED/111` for
worker-local `127.0.0.1:11434`, immutable worker-owned mount/socket
absence and exact no-network Docker effective configuration. Link and route
acceptance is necessary but not alone sufficient. No silent `nc` exit,
no missing instrumented syscall, no unchecked extra interface, and no
generic assertion that all traffic is impossible may count as passing.

## Pre-freeze checker sensitivity

The pure validator's `test_network_state_validator.py` contains **17**
public synthetic mutation/negative cases; development run exit 0, 17/17,
raw stderr SHA-256 `0517e6fa720811890fef9fd60aac55d5010f0c8dc69a94f71048031b46762ac7`.
A route-only weak checker accepts a mutant administratively UP tunnel link,
but the RC4 validator rejects it. Other mutations exercise RUNNING,
LOWER_UP, operstate UP/UNKNOWN, non-loopback v4/v6 routes, IPv6 addresses,
identity mismatch, incomplete observations and bad loopback flags.
This is **same-controller, synthetic development control**, not observed Q08
confinement or a blind independent evaluation. The exact check hashes are
in `PRE-FREEZE-NETWORK-VALIDATION.json`.

The existing installed Ollama 0.40.0 service is still restricted to
literal `127.0.0.1:11434`, with identical installed binary/model manifest
hashes, under controller-only pre-freeze receipt
`f23565bbb9722f813a95b73871e9fb3301f4c6c2ec10b4376f01e455a51a431a`.
An initial pre-freeze diagnostic had a *parser setup error* because `lsof`
appends `(LISTEN)`; that error is retained under controller-only hash
`3cad06da18bfb1b218fa6598c813f905a448001aa555c733d82feb388320445b`.
The corrected pre-freeze service check passed. Neither was a frozen trial,
Q03 conformance, security permission, or model inference.

## Exact Q01–Q13 required acceptance and freeze

- Q03 must render the **complete frozen prompt and exactly two functions**
  in the actual Ollama provider, with no model inference.
- Q01–Q02 must actually stage two allowed synthetic files and reject
  physically copied outside-world material using the retained checker.
- Q04 must inspect the actual pinned worker identity, mounts, UID/capability,
  resource ceilings, no-network configuration, runtime environment and
  startup scratch. The SHA-bound private `PINS.json` remains external.
- Q05–Q07 exercise actual controller-mediated allowed/forbidden reads and
  writes, including kernel-level read-only refusals and unchanged sentinels.
- Q08 requires the full direct positive/negative connection controls **and**
  the new actual sysfs/proc state check. Only then is `Q08.link-validation.json`
  produced and required by formal Q11 receipt acceptance.
- Q09 exercises the hidden/native/MCP/hosted/generated and malformed name
  paths with no host command before refusal, including a weak decoder control.
- Q10 creates a separately fresh worker ID with empty scratch, absent first
  result, exact input/initial context. Provider internal erasure is unproven.
- Q11 checks actual external raw command/HTTP/tool receipts and their byte,
  time, input, authorization and checksum relationships, including mutation.
- Q12 verifies only exact owned worker cleanup and full-ID absence; fresh reset
  is not inferred from cleanup-only after an earlier failure.
- Q13 **PENDING_EXPLICIT_OWNER_ADMISSION_REVIEW** only if every required
  bounded zero-model control passes. Any failed/unknown/not-run gate stays
  BLOCKED. A zero-model pass is not model tool-use fitness or a CAL pilot.

Commit an exact preparation, then create an explicit separately reviewed
`FREEZE.json` with the exact new experiment ID, all source/expected-control
hashes, the external controller-only private pins SHA and timestamp **before
any decisive RC4 execution**. Commit the freeze separately and execute its
Q01–Q13 runner **once**, with an external one-shot attempt ledger and receipt
directory. Retain first failures. Publish result only in a separate retrospective
sibling subtree; never repair or rerun this frozen candidate.

No model actor, hidden CAL memory, scientific gold, credential, host socket,
G89 reroute, global permission change, canonical Contract A–E change,
consumer pin, release, merge, or pipeline integration is authorized.
