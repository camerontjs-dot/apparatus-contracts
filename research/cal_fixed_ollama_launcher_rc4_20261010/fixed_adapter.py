#!/usr/bin/env python3
"""Two fixed CAL public-synthetic functions; controller-only, no sandbox framework.

The external controller supplies an actual command runner that preserves receipts.
The model cannot select a command, container, endpoint, mount, or environment.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
import urllib.error
import urllib.request

HERE = Path(__file__).resolve().parent
ENDPOINT = "http://127.0.0.1:11434/api/chat"
READS = {
    "data/marker.txt": "04d7c29ff732dcb8c993138ab73cfc3195ffd6e52a7cb26254bb3c2c9ba099c7",
    "instructions/request.txt": "fe139a5eee24ab24be7eb05af759de8f0f1705ebfd35b2d3958a304a7aa98987",
}
PYTHON = "/usr/local/bin/python3"
CLEAN_ENV = ["/usr/bin/env", "-i", "PATH=/usr/local/bin:/usr/bin:/bin", "HOME=/"]
WRITE_COMMAND = """import errno,json,os,sys
os.umask(0o077)
try:
    with open('/scratch/answer.txt','xb') as stream:
        stream.write(sys.stdin.buffer.read())
except OSError as error:
    print(json.dumps({'errno':error.errno,'errname':errno.errorcode.get(error.errno)}),file=sys.stderr)
    sys.exit(1)
"""
READ_COMMAND = "import pathlib,sys; sys.stdout.buffer.write(pathlib.Path(sys.argv[1]).read_bytes())"


class Refusal(Exception):
    def __init__(self, reason):
        self.reason = reason
        super().__init__(reason)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise Refusal("MALFORMED_DUPLICATE_KEY")
        result[key] = value
    return result


def reject_constant(value):
    raise Refusal("MALFORMED_JSON")


def decode(raw):
    if not isinstance(raw, bytes) or len(raw) > 16384:
        raise Refusal("MALFORMED_ENVELOPE_SIZE")
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object, parse_constant=reject_constant)
    except (UnicodeError, ValueError, RecursionError):
        raise Refusal("MALFORMED_JSON") from None


class FixedAdapter:
    def __init__(self, container_id, execute):
        if not isinstance(container_id, str) or not re.fullmatch(r"[a-f0-9]{64}", container_id):
            raise Refusal("INVALID_CONTAINER_ID")
        self.container_id = container_id
        self.execute = execute

    def dispatch(self, raw):
        envelope = decode(raw)
        if not isinstance(envelope, dict) or set(envelope) != {"name", "arguments"}:
            raise Refusal("MALFORMED_ENVELOPE")
        name, arguments = envelope["name"], envelope["arguments"]
        if not isinstance(name, str) or name not in ("read_packet_file", "write_result"):
            raise Refusal("AUTHORIZATION_TOOL_DENIED")
        if not isinstance(arguments, dict):
            raise Refusal("MALFORMED_ARGUMENTS")
        if name == "read_packet_file":
            return self.read_packet_file(arguments)
        return self.write_result(arguments)

    def dispatch_model_call(self, raw):
        """Bind Ollama's ToolCall.Function to the same strict dispatcher."""
        call = decode(raw)
        if not isinstance(call, dict) or not {"function"} <= set(call) <= {"function", "id"}:
            raise Refusal("MALFORMED_MODEL_CALL")
        if "id" in call and not isinstance(call["id"], str):
            raise Refusal("MALFORMED_MODEL_CALL")
        function = call["function"]
        if not isinstance(function, dict) or not {"name", "arguments"} <= set(function) <= {"name", "arguments", "index"}:
            raise Refusal("MALFORMED_MODEL_CALL")
        if "index" in function and (type(function["index"]) is not int or function["index"] < 0):
            raise Refusal("MALFORMED_MODEL_CALL")
        envelope = {"name": function["name"], "arguments": function["arguments"]}
        return self.dispatch(json.dumps(envelope, ensure_ascii=True).encode("utf-8"))

    def _exec(self, command, data=b""):
        argv = ["docker", "--context", "desktop-linux", "exec", "-i", self.container_id, *CLEAN_ENV, *command]
        result = self.execute(argv, data)
        if result.returncode != 0:
            raise Refusal("WORKER_EXEC_FAILED")
        return result.stdout

    def read_packet_file(self, arguments):
        if set(arguments) != {"path"} or not isinstance(arguments["path"], str):
            raise Refusal("MALFORMED_ARGUMENTS")
        path = arguments["path"]
        if path not in READS:
            raise Refusal("AUTHORIZATION_PATH_DENIED")
        content = self._exec([PYTHON, "-I", "-B", "-c", READ_COMMAND, "/packet/" + path])
        digest = hashlib.sha256(content).hexdigest()
        if digest != READS[path]:
            raise Refusal("READ_BYTES_DRIFT")
        return {"path": path, "content": content.decode("utf-8"), "bytes": len(content), "sha256": digest}

    def write_result(self, arguments):
        if set(arguments) != {"path", "content"} or not all(isinstance(v, str) for v in arguments.values()):
            raise Refusal("MALFORMED_ARGUMENTS")
        if arguments["path"] != "answer.txt":
            raise Refusal("AUTHORIZATION_PATH_DENIED")
        try:
            content = arguments["content"].encode("utf-8")
        except UnicodeError:
            raise Refusal("MALFORMED_UTF8") from None
        if len(content) > 4096:
            raise Refusal("OUTPUT_BYTES_LIMIT")
        self._exec([PYTHON, "-I", "-B", "-c", WRITE_COMMAND], content)
        return {"path": "answer.txt", "bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # HTTPError is returned as a captured non-200 response below


def model_request_bytes():
    """The complete initial request; no runtime/project history is loaded."""
    return (HERE / "MODEL-REQUEST.json").read_bytes()


def render_request_bytes():
    return (HERE / "Q03-RENDER-REQUEST.json").read_bytes()


def observe_render_only():
    """Maintained provider debug rendering. No generation/actor loop is invoked."""
    request = urllib.request.Request(ENDPOINT, data=render_request_bytes(), headers={"Content-Type": "application/json"})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    try:
        response = opener.open(request, timeout=45)
    except urllib.error.HTTPError as error:
        response = error  # capture rejected status/headers/body; never follow redirect
    with response:
        return response.status, dict(response.headers), response.read(1024 * 1024 + 1)
