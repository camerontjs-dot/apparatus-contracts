from __future__ import annotations

import copy
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any

import rfc8785

CONTRACT_D_VERSION = "0.3.0-rc5"
REGISTRY_PATH = Path(__file__).with_name("effect-registry.json")
MAX_JSON_CONTAINER_DEPTH = 128
SAFE_INTEGER_MAX = 9007199254740991
SAFE_INTEGER_MIN = -SAFE_INTEGER_MAX
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


REGISTRY = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def _valid_unicode_string(value: str, path: str) -> None:
    try:
        value.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ContractDError("invalid_unicode_scalar", path) from exc


def _json_value(
    value: Any,
    path: str = "$",
    active: set[int] | None = None,
    container_depth: int = 1,
) -> None:
    if value is None or isinstance(value, bool):
        return
    if isinstance(value, str):
        _valid_unicode_string(value, path)
        return
    if isinstance(value, int):
        if value < SAFE_INTEGER_MIN or value > SAFE_INTEGER_MAX:
            raise ContractDError("non_interoperable_integer", path)
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ContractDError("non_finite_number", path)
        return

    if active is None:
        active = set()

    if isinstance(value, list):
        if container_depth > MAX_JSON_CONTAINER_DEPTH:
            raise ContractDError(
                "json_depth_exceeded",
                path,
                f"max_container_depth={MAX_JSON_CONTAINER_DEPTH}",
            )
        marker = id(value)
        if marker in active:
            raise ContractDError("non_json_value", path, "cyclic_container")
        active.add(marker)
        try:
            for i, child in enumerate(value):
                _json_value(child, f"{path}[{i}]", active, container_depth + 1)
        finally:
            active.remove(marker)
        return

    if isinstance(value, dict):
        if container_depth > MAX_JSON_CONTAINER_DEPTH:
            raise ContractDError(
                "json_depth_exceeded",
                path,
                f"max_container_depth={MAX_JSON_CONTAINER_DEPTH}",
            )
        marker = id(value)
        if marker in active:
            raise ContractDError("non_json_value", path, "cyclic_container")
        active.add(marker)
        try:
            for key, child in value.items():
                if not isinstance(key, str):
                    raise ContractDError("non_json_object_key", path)
                _valid_unicode_string(key, path)
                _json_value(child, f"{path}.{key}", active, container_depth + 1)
        finally:
            active.remove(marker)
        return

    raise ContractDError("non_json_value", path, type(value).__name__)


def validate_json_value(value: Any, path: str = "$") -> None:
    """Validate one RC5 interoperable finite-JSON value using the normative bounds."""
    try:
        _json_value(value, path)
    except RecursionError as exc:
        raise ContractDError("resource_limit", path, "recursion") from exc


def is_sha256_value(value: Any) -> bool:
    return isinstance(value, str) and _SHA256.fullmatch(value) is not None


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
        raise ContractDError("unknown_field", path, ",".join(sorted(str(x) for x in extra)))


def _nonempty_string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value:
        raise ContractDError("expected_nonempty_string", path)
    _valid_unicode_string(value, path)
    return value


def validate_effect(effect: Any) -> dict[str, Any]:
    validate_json_value(effect, "$.effect")
    effect = _object(effect, "$.effect")
    _exact_keys(effect, {"type", "version"}, {"params"}, "$.effect")
    etype = _nonempty_string(effect["type"], "$.effect.type")
    version = _nonempty_string(effect["version"], "$.effect.version")
    params = effect.get("params", {})
    if not isinstance(params, dict):
        raise ContractDError("expected_object", "$.effect.params")
    type_entry = REGISTRY.get("effects", {}).get(etype)
    if type_entry is None:
        raise ContractDError("unknown_effect_type", "$.effect.type", etype)
    version_entry = type_entry.get(version)
    if version_entry is None:
        raise ContractDError("unknown_effect_version", "$.effect.version", f"{etype}@{version}")
    param_spec = version_entry.get("params", {})
    unknown = set(params) - set(param_spec)
    if unknown:
        raise ContractDError(
            "unknown_effect_parameter",
            "$.effect.params",
            ",".join(sorted(unknown)),
        )
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
        if isinstance(value, str):
            _valid_unicode_string(value, f"$.effect.params.{name}")
        if "enum" in spec and value not in spec["enum"]:
            raise ContractDError(
                "invalid_effect_parameter_value",
                f"$.effect.params.{name}",
                repr(value),
            )
        normalized[name] = value
    return {"type": etype, "version": version, "params": normalized}


def validate_decision(decision: Any) -> dict[str, Any]:
    validate_json_value(decision)

    decision = _object(decision, "$")
    _exact_keys(
        decision,
        {"contract_d_version", "input_authority", "policy", "target", "evaluation"},
        {"effect", "metadata"},
        "$",
    )
    if decision["contract_d_version"] != CONTRACT_D_VERSION:
        raise ContractDError(
            "unknown_contract_version",
            "$.contract_d_version",
            repr(decision["contract_d_version"]),
        )

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
    if not is_sha256_value(content):
        raise ContractDError("invalid_target_content_sha256", "$.target.content_sha256")

    evaluation = _object(decision["evaluation"], "$.evaluation")
    state = evaluation.get("state")
    if state == "completed":
        _exact_keys(evaluation, {"state", "disposition"}, set(), "$.evaluation")
        if evaluation["disposition"] not in {"clear", "hold"}:
            raise ContractDError(
                "unknown_disposition",
                "$.evaluation.disposition",
                repr(evaluation["disposition"]),
            )
        if "effect" not in decision:
            raise ContractDError("missing_field", "$", "effect")
        validate_effect(decision["effect"])
    elif state == "failed":
        _exact_keys(evaluation, {"state"}, set(), "$.evaluation")
        if "effect" in decision:
            raise ContractDError("effect_on_failed_evaluation", "$.effect")
    else:
        raise ContractDError(
            "unknown_evaluation_state",
            "$.evaluation.state",
            repr(state),
        )

    if "metadata" in decision:
        metadata = _object(decision["metadata"], "$.metadata")
        _exact_keys(
            metadata,
            set(),
            {"reason_codes", "explanation", "diagnostics"},
            "$.metadata",
        )
        if "reason_codes" in metadata:
            reasons = metadata["reason_codes"]
            if not isinstance(reasons, list):
                raise ContractDError("expected_array", "$.metadata.reason_codes")
            for i, reason in enumerate(reasons):
                _nonempty_string(reason, f"$.metadata.reason_codes[{i}]")
        if "explanation" in metadata:
            _nonempty_string(metadata["explanation"], "$.metadata.explanation")
    return decision


def canonical_json_bytes(value: Any) -> bytes:
    try:
        validate_json_value(value)
        return rfc8785.dumps(value) + b"\n"
    except ContractDError:
        raise
    except (rfc8785.CanonicalizationError, UnicodeError) as exc:
        raise ContractDError("canonicalization_failure", "$", type(exc).__name__) from exc
    except RecursionError as exc:
        raise ContractDError("resource_limit", "$", "recursion") from exc


def semantic_projection(decision: dict[str, Any]) -> dict[str, Any]:
    validate_decision(decision)
    try:
        projection = {
            "contract_d_version": decision["contract_d_version"],
            "input_authority": copy.deepcopy(decision["input_authority"]),
            "policy": copy.deepcopy(decision["policy"]),
            "target": copy.deepcopy(decision["target"]),
            "evaluation": copy.deepcopy(decision["evaluation"]),
        }
    except RecursionError as exc:
        raise ContractDError("resource_limit", "$", "recursion") from exc
    if decision["evaluation"]["state"] == "completed":
        projection["effect"] = validate_effect(decision["effect"])
    return projection


def semantic_identity(decision: dict[str, Any]) -> str:
    try:
        digest = hashlib.sha256(canonical_json_bytes(semantic_projection(decision))).hexdigest()
    except RecursionError as exc:
        raise ContractDError("resource_limit", "$", "recursion") from exc
    return f"decision:sha256:{digest}"
