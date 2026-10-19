# Support request: unexplained controller-only preflight refusal

**Submission state: NOT_SUBMITTED. No support case ID or platform determination.**
**Current execution state: blocked; no denied operation was retried or rerouted.**

Official channel verified October 18, 2026:
https://help.openai.com/en/articles/6614161-how-can-i-contact-support
The support chat is on the OpenAI Help Center. Include the account email and app
version privately when submitting. Do not publish account details or raw host
paths in the repository. The connected Browser tool in this session returned:
"Browser access requires the originating browser context. Open ChatGPT in the
browser with the connected extension and try again." No support conversation was
opened or submitted by the assistant.

## Message to submit

Subject: Please clarify a tool-level safety refusal for a read-only local runtime preflight

On October 17, 2026, in the America/Toronto timezone, ChatGPT attempted a
controller-only read-only preflight through Remote Desktop Commander on my
authorized Mac. The request would have read installed executable identities,
Docker/image metadata, and loopback Ollama version/model metadata, then saved
controller-private receipts. It did not request model inference, container
creation, credential export, security-setting changes, or access to third-party
systems.

The tool returned this exact error before execution:

"This tool call was blocked by OpenAI's safety checks. Please double check what you are sending."

No cause or request/case ID was supplied. We preserved the denial and stopped the
live attempt. A prior, separately recorded October 9 retry was accepted, but we
do not treat that as clearance for this event. We have not changed tools, syntax,
providers or hosts to bypass the October 17 refusal.

Could you clarify whether this was a policy restriction, tool behavior or an
erroneous refusal, and identify any supported method and conditions for this
specific bounded metadata operation? We are asking for an attributable scoped
response, not for security safeguards to be disabled or for general execution
permission. We can supply the original request and sensitive environment details
privately if a reviewer requests them.

Public sanitized stop record:
https://github.com/camerontjs-dot/apparatus-contracts/blob/beb4477dc3e87b03cec9eaa186a17042b4cac765/research/cal_s1_coding_profile_rc7_20261017/QUALIFICATION_STOP.json

Current research is ordinary testing of a fixed Python evaluation adapter. The
source code and simulated controls do not themselves establish runtime or model
qualification. Live testing remains stopped pending clarification of the specific
refusal.

## What to record after a response

Keep the actual reply private and preserve its bytes. Record its case/reference,
date, scope, supported interface, conditions and SHA-256 with the controller.
Post only a public-safe outcome under apparatus-contracts #177. A generic help
article, response-shaped JSON, user approval, successful source test, or silence
is not a favorable platform determination. Do not invent a case number or change
APPROVAL.template.json to make readiness green without the actual reviewed basis.
