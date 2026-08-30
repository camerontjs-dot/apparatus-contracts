from __future__ import annotations
import copy
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any

CONTRACT_D_VERSION = "0.3.0-rc3"
REGISTRY_PATH = Path(__file__).with_name("effect-registry.json")
_SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")

class ContractDError(ValueError):
    def __init__(self, code: str, path: str = "$", detail: str | None = None):
        self.code = code
        self.path = path
        self.detail = detail
        msg = f"{code} at {path}"
        if detail:
            msg += f": {detail}"
        super().__init__(msg)

def _load_registry() -> dict[str, Any]:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

REGISTRY = _load_registry()

def _finite_json(value: Any, path: str = "$") -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise ContractDError("non_finite_number", path)
    if isinstance(value, dict):
        for key, child in value.items():
            _finite_json(child, f"{path}.{key}")
    elif isinstance(value, list):
        for i, child in enumerate(value):
            _finite_json(child, f"{path}[{i}]")

def _object(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractDError("expected_object", path)
    return value

def _exact_keys(value: dict[str, Any], required: set[str], optional: set[str], path: str) -> None:
    missing = required - value.keys()
    if missing:
        raise ContractDError("missing_field", path, ",".join(sorted(missing)))
    extra = value.keys() - required - optional
    if extra:
        raise ContractDError("unknown_field", path, ",".join(sorted(extra)))

def _nonempty_string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value:
        raise ContractDError("expected_nonempty_string", path)
    return value

def validate_effect(effect: Any) -> dict[str, Any]:
    effect = _object(effect, "$.effect")
    _exact_keys(effect, {"type", "version"}, {"params"}, "$.effect")
    etype = _nonempty_string(effect["type"], "$.effect.type")
    version = _nonempty_string(effect["version"], "$.effect.version")
    params = effect.get("params", {})
    if not isinstance(params, dict):
        raise ContractDError("expected_object", "$.effect.params")
    effects = REGISTRY.get("effects", {})
    type_entry = effects.get(etype)
    if type_entry is None:
        raise ContractDError("unknown_effect_type", "$.effect.type", etype)
    version_entry = type_entry.get(version)
    if version_entry is None:
        raise ContractDError("unknown_effect_version", "$.effect.version", f"{etype}@{version}")
    param_spec = version_entry.get("params", {})
    unknown = set(params) - set(param_spec)
    if unknown:
        raise ContractDError("unknown_effect_parameter", "$.effect.params", ",".join(sorted(unknown)))
    normalized: dict[str, Any] = {}
    for name, spec in param_spec.items():
        if name in params:
            value = params[name]
        elif spec.get("required"):
            raise ContractDError("missing_effect_parameter", "$.effect.params", name)
        elif "default" in spec:
            value = copy.deepcopy(spec["default"])
        else:
            continue
        if spec.get("type") == "string" and not isinstance(value, str):
            raise ContractDError("invalid_effect_parameter_type", f"$.effect.params.{name}")
        if "enum" in spec and value not in spec["enum"]:
            raise ContractDError("invalid_effect_parameter_value", f"$.effect.params.{name}", repr(value))
        normalized[name] = value
    return {"type": etype, "version": version, "params": normalized}

def validate_decision(decision: Any) -> dict[str, Any]:
    decision = _object(decision, "$")
    _finite_json(decision)
    _exact_keys(decision,{"contract_d_version", "input_authority", "policy", "target", "evaluation"},{"effect", "metadata"},"$")
    if decision["contract_d_version"] != CONTRACT_D_VERSION:
        raise ContractDError("unknown_contract_version", "$.contract_d_version", repr(decision["contract_d_version"]))
    upstream = _object(decision["input_authority"], "$.input_authority")
    _exact_keys(upstream, {"kind", "id", "immutable_id"}, set(), "$.input_authority")
    for key in ("kind", "id", "immutable_id"):
        _nonempty_string(upstream[key], f"$.input_authority.{key}")
    policy = _object(decision["policy"], "$.policy")
    _exact_keys(policy, {"id", "version"}, set(), "$.policy")
    _nonempty_string(policy["id"], "$.policy.id")
    _nonempty_string(policy["version"], "$.policy.version")
    target = _object(decision["target"], "$.target")
    _exact_keys(target, {"kind", "id", "content_sha256"}, set(), "$.target")
    _nonempty_string(target["kind"], "$.target.kind")
    _nonempty_string(target["id"], "$.target.id")
    content = _nonempty_string(target["content_sha256"], "$.target.content_sha256")
    if not _SHA256.fullmatch(content):
        raise ContractDError("invalid_target_content_sha256", "$.target.content_sha256")
    evaluation = _object(decision["evaluation"], "$.evaluation")
    state = evaluation.get("state")
    if state == "completed":
        _exact_keys(evaluation, {"state", "disposition"}, set(), "$.evaluation")
        if evaluation["disposition"] not in {"clear", "hold"}:
            raise ContractDError("unknown_disposition", "$.evaluation.disposition", repr(evaluation["disposition"]))
        if "effect" not in decision:
            raise ContractDError("missing_field", "$", "effect")
        validate_effect(decision["effect"])
    elif state == "failed":
        _exact_keys(evaluation, {"state"}, set(), "$.evaluation")
        if "effect" in decision:
            raise ContractDError("effect_on_failed_evaluation", "$.effect")
    else:
        raise ContractDError("unknown_evaluation_state", "$.evaluation.state", repr(state))
    if "metadata" in decision:
        metadata = _object(decision["metadata"], "$.metadata")
        _exact_keys(metadata, set(), {"reason_codes", "explanation", "diagnostics"}, "$.metadata")
        if "reason_codes" in metadata:
            reasons = metadata["reason_codes"]
            if not isinstance(reasons, list):
                raise ContractDError("expected_array", "$.metadata.reason_codes")
            for i, reason in enumerate(reasons):
                _nonempty_string(reason, f"$.metadata.reason_codes[{i}]")
        if "explanation" in metadata:
            _nonempty_string(metadata["explanation"], "$.metadata.explanation")
        if "diagnostics" in metadata:
            _finite_json(metadata["diagnostics"], "$.metadata.diagnostics")
    return decision

def canonical_json_bytes(value: Any) -> bytes:
    _finite_json(value)
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")

def semantic_projection(decision: dict[str, Any]) -> dict[str, Any]:
    validate_decision(decision)
    projection = {"contract_d_version": decision["contract_d_version"],"input_authority": copy.deepcopy(decision["input_authority"]),"policy": copy.deepcopy(decision["policy"]),"target": copy.deepcopy(decision["target"]),"evaluation": copy.deepcopy(decision["evaluation"])}
    if decision["evaluation"]["state"] == "completed":
        projection["effect"] = validate_effect(decision["effect"])
    return projection

def semantic_identity(decision: dict[str, Any]) -> str:
    digest = hashlib.sha256(canonical_json_bytes(semantic_projection(decision))).hexdigest()
    return f"decision:sha256:{digest}"

def semantic_sha256(decision: dict[str, Any]) -> str:
    return semantic_identity(decision).removeprefix("decision:sha256:")

def whole_object_sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()
