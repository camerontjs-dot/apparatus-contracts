"""Three fixed controller operations; fake transport only, no runtime launcher.

Caller owns no command, endpoint, mount, evaluator, case selector or receipt
channel. A future runtime binding needs separate authority and qualification.
Profile/adapter/witness objects stay with the trusted controller.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re
from types import MappingProxyType
import uuid

from completion_check import EvidenceFailure, check_execution

VERSION = "cal-s1-lines-v1"
MAX_ENVELOPE = 262144
MAX_WRITE = 32768
MAX_READ = 65536
SHA = re.compile(r"[a-f0-9]{64}\Z")
LINE_BREAKS = frozenset("\n\r\v\f\x1c\x1d\x1e\x85\u2028\u2029")


class Refusal(ValueError):
    def __init__(self, reason):
        self.reason = reason
        super().__init__(reason)


def require(condition, reason):
    if not condition:
        raise Refusal(reason)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("utf-8")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def unique(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "MALFORMED_DUPLICATE_KEY")
        result[key] = value
    return result


def decode(raw):
    require(type(raw) is bytes and len(raw) <= MAX_ENVELOPE, "MALFORMED_ENVELOPE_SIZE")
    try:
        def constant(_):
            raise Refusal("MALFORMED_JSON_CONSTANT")
        return json.loads(raw.decode("utf-8"), object_pairs_hook=unique,
                          parse_constant=constant)
    except Refusal:
        raise
    except (UnicodeError, ValueError, RecursionError) as error:
        raise Refusal("MALFORMED_JSON") from error


@dataclass(frozen=True)
class Entry:
    data: bytes
    kind: str = "file"
    nlink: int = 1
    ancestors_clean: bool = True


@dataclass(frozen=True)
class Profile:
    reads: dict
    evaluator_sha256: str
    cases: tuple
    observer_sha256: str

    def __post_init__(self):
        require(type(self.reads) is dict and len(self.reads) == 7, "PROFILE_SEVEN_FILES_REQUIRED")
        paths = list(self.reads)
        require(all(type(p) is str for p in paths), "PROFILE_PATH")
        require(paths == sorted(paths), "PROFILE_PATH_ORDER")
        prefixes = {}
        for path, digest in self.reads.items():
            parts = path.split("/")
            require(len(path) <= 500 and re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_./-]*", path)
                    and all(p not in {"", ".", ".."} and not p.startswith(".") for p in parts)
                    and path.endswith((".py", ".md", ".json", ".txt")), "PROFILE_PATH")
            for n in range(1, len(parts) + 1):
                prefix = "/".join(parts[:n])
                folded = prefix.casefold()
                require(folded not in prefixes or prefixes[folded] == prefix, "PROFILE_CASE_ALIAS")
                prefixes[folded] = prefix
            require(type(digest) is str and SHA.fullmatch(digest), "PROFILE_DIGEST")
        require(type(self.evaluator_sha256) is str and SHA.fullmatch(self.evaluator_sha256), "PROFILE_EVALUATOR")
        require(type(self.observer_sha256) is str and SHA.fullmatch(self.observer_sha256), "PROFILE_OBSERVER")
        require(type(self.cases) is tuple and 1 <= len(self.cases) <= 32 and
                all(type(x) is str and re.fullmatch(r"[A-Za-z0-9_-]{1,64}", x) for x in self.cases)
                and len(set(self.cases)) == len(self.cases), "PROFILE_CASES")
        object.__setattr__(self, "reads", MappingProxyType(dict(self.reads)))

    @property
    def digest(self):
        return sha(canonical({"version": VERSION, "reads": dict(self.reads),
                              "evaluator_sha256": self.evaluator_sha256,
                              "observer_sha256": self.observer_sha256,
                              "cases": list(self.cases)}))


class Witness:
    """Separate controller observer, inaccessible through the runtime API.

    This version accepts synthetic observer fixtures only. It checks the evidence
    contract, not actual execution. No observer callback goes to the executor.
    """
    def __init__(self, provider=None):
        self.provider = provider
        self._events = []
        self._runs = {}

    @property
    def events(self):
        return json.loads(canonical(self._events))

    def begin(self, request):
        run_id = request["run_id"]
        require(run_id not in self._runs and len(self._runs) < 32, "WITNESS_REPLAY_OR_RUN_LIMIT")
        require(self.provider is not None and
                callable(getattr(self.provider, "begin", None)) and
                callable(getattr(self.provider, "finish", None)), "INDEPENDENT_OBSERVER_MISSING")
        require(getattr(self.provider, "identity_sha256", None) == request["observer_sha256"], "OBSERVER_IDENTITY_MISMATCH")
        require(getattr(self.provider, "evidence_layer", None) == "SYNTHETIC_FAKE_RUNTIME", "LIVE_OBSERVER_NOT_IMPLEMENTED")
        self._runs[run_id] = {"closed": False}
        try:
            self.provider.begin(decode(canonical(request)))
        except Exception as error:
            self._runs[run_id]["closed"] = True
            raise Refusal("OBSERVER_BEGIN_FAILED") from error

    def finish(self, run_id):
        state = self._runs[run_id]
        require(not state["closed"], "WITNESS_CLOSED")
        state["closed"] = True
        try:
            events = self.provider.finish(run_id)
            require(type(events) is tuple and len(events) <= 128, "WITNESS_EVENT_BOUND")
            copies = []
            for event in events:
                require(type(event) is dict, "WITNESS_EVENT_MALFORMED")
                raw = canonical(event)
                require(len(raw) <= 4096, "WITNESS_EVENT_SIZE")
                copies.append(decode(raw))
            self._events.extend(copies)
            return tuple(copies)
        except Refusal:
            raise
        except Exception as error:
            raise Refusal("OBSERVER_MISSING_OR_FAILED") from error


class Adapter:
    def __init__(self, profile, runtime, witness):
        require(type(profile) is Profile and type(witness) is Witness, "CONTROLLER_STATE_MISSING")
        require(witness.provider is not runtime, "EXECUTOR_OBSERVER_ALIAS")
        for name in ("read_packet", "list_candidates", "read_candidate", "write_candidate", "run_development_tests"):
            require(callable(getattr(runtime, name, None)), "RUNTIME_INTERFACE_MISSING")
        self.profile, self.runtime, self.witness = profile, runtime, witness
        self.candidate_sha256 = None
        self.last_pass = None
        self.decisions = []
        require(self._call("list_candidates") == (), "STALE_SCRATCH")

    def _call(self, method, *args):
        try:
            return getattr(self.runtime, method)(*args)
        except Refusal:
            raise
        except Exception as error:
            raise Refusal("RUNTIME_MISSING_OR_FAILED") from error

    def _entry(self, entry, maximum):
        require(type(entry) is Entry and entry.kind == "file" and type(entry.nlink) is int
                and entry.nlink == 1 and entry.ancestors_clean is True, "NONREGULAR_OR_LINK")
        require(type(entry.data) is bytes and len(entry.data) <= maximum, "BYTES_LIMIT")
        return entry.data

    def _candidate(self):
        require(self.candidate_sha256 is not None, "CANDIDATE_MISSING")
        require(self._call("list_candidates") == ("candidate.py",), "SCRATCH_DRIFT")
        data = self._entry(self._call("read_candidate", "candidate.py"), MAX_WRITE)
        require(sha(data) == self.candidate_sha256, "CANDIDATE_DRIFT")
        return data

    def dispatch(self, raw):
        require(len(self.decisions) < 256, "DISPATCH_BUDGET_EXHAUSTED")
        try:
            value = self._dispatch(raw)
            self.decisions.append({"request_sha256": sha(raw), "status": "ACCEPTED"})
            return value
        except Refusal as error:
            self.decisions.append({"request_sha256": sha(raw) if type(raw) is bytes else None,
                                   "status": "REFUSED", "reason": error.reason})
            raise

    def _dispatch(self, raw):
        obj = decode(raw)
        require(type(obj) is dict and set(obj) == {"version", "name", "arguments"}, "MALFORMED_ENVELOPE")
        require(obj["version"] == VERSION, "VERSION_DENIED")
        name, args = obj["name"], obj["arguments"]
        require(type(name) is str and name in {"read_packet_file", "write_candidate_lines", "run_development_tests"}, "TOOL_DENIED")
        require(type(args) is dict, "MALFORMED_ARGUMENTS")
        if name == "read_packet_file":
            require(set(args) == {"path"} and type(args["path"]) is str, "MALFORMED_ARGUMENTS")
            path = args["path"]
            require(path in self.profile.reads, "PATH_DENIED")
            data = self._entry(self._call("read_packet", path), MAX_READ)
            require(sha(data) == self.profile.reads[path], "PACKET_BYTES_DRIFT")
            try:
                content = data.decode("utf-8")
            except UnicodeError as error:
                raise Refusal("MALFORMED_UTF8") from error
            return {"path": path, "content": content, "bytes": len(data), "sha256": sha(data)}
        if name == "write_candidate_lines":
            require(set(args) == {"path", "lines"} and args["path"] == "candidate.py", "WRITE_PATH_OR_KEYS_DENIED")
            lines = args["lines"]
            require(type(lines) is list and len(lines) <= MAX_WRITE and
                    all(type(line) is str and not any(c in LINE_BREAKS for c in line) for line in lines), "MALFORMED_LINES")
            try:
                data = (("\n".join(lines) + "\n") if lines else "").encode("utf-8")
            except UnicodeError as error:
                raise Refusal("MALFORMED_UTF8") from error
            require(len(data) <= MAX_WRITE, "OUTPUT_BYTES_LIMIT")
            if self.candidate_sha256 is None:
                require(self._call("list_candidates") == (), "STALE_SCRATCH")
            else:
                self._candidate()
            self._call("write_candidate", "candidate.py", data)
            self.last_pass = None
            observed = self._entry(self._call("read_candidate", "candidate.py"), MAX_WRITE)
            require(self._call("list_candidates") == ("candidate.py",) and observed == data, "WRITE_BYTES_DRIFT")
            self.candidate_sha256 = sha(observed)
            return {"path": "candidate.py", "bytes": len(observed), "sha256": self.candidate_sha256}
        require(args == {}, "MALFORMED_ARGUMENTS")
        snapshot = self._candidate()
        request = {"schema": "cal-s1-dev-request/v1", "run_id": uuid.uuid4().hex,
                   "profile_sha256": self.profile.digest, "candidate_sha256": self.candidate_sha256,
                   "candidate_hex": snapshot.hex(), "observer_sha256": self.profile.observer_sha256,
                   "evaluator_sha256": self.profile.evaluator_sha256, "cases": list(self.profile.cases)}
        self.last_pass = None
        self.witness.begin(request)
        try:
            # A copy prevents transport mutation of the checker's expectations.
            report = self._call("run_development_tests", decode(canonical(request)))
        finally:
            events = self.witness.finish(request["run_id"])
        self._candidate()
        require(type(report) is dict and {"exit_code", "stdout"} <= set(report) <= {"exit_code", "stdout", "receipt"}, "FEEDBACK_SHAPE")
        try:
            require(len(canonical(report)) <= 16384, "FEEDBACK_LIMIT")
        except Refusal:
            raise
        except (ValueError, TypeError, RecursionError) as error:
            raise Refusal("FEEDBACK_MALFORMED") from error
        require(type(report["exit_code"]) is int and report["exit_code"] == 0, "DEVELOPMENT_EXIT_FAILED")
        require(type(report["stdout"]) is str, "FEEDBACK_SHAPE")
        try:
            require(len(report["stdout"].encode("utf-8")) <= 8192, "FEEDBACK_LIMIT")
        except UnicodeError as error:
            raise Refusal("FEEDBACK_UTF8") from error
        try:
            verdict = check_execution(request, events)
            self.last_pass = decode(canonical(verdict))
            return verdict
        except EvidenceFailure as error:
            raise Refusal(str(error)) from error

    def finalize(self, verdict):
        """Controller-only final hash binding; never a model-selected operation."""
        self._candidate()
        require(self.last_pass is not None and verdict == self.last_pass and
                verdict["candidate_sha256"] == self.candidate_sha256, "FINAL_EVIDENCE_STALE_OR_MISSING")
        return decode(canonical(self.last_pass))
