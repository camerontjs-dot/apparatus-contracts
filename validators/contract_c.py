"""Reference validator and canonicalization for Apparatus Contract C 1.0.0."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import re
import sys
from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, StrictFloat, ValidationError, model_validator

CONTRACT_C_VERSION = "1.0.0"
CONTRACT_C_SUPPORTED_VERSIONS: tuple[str, ...] = (CONTRACT_C_VERSION,)

_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_CONTRIBUTION_ID = re.compile(r"^contribution:[0-9a-f]{64}$")

class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class ContractBBinding(_StrictModel):
    contract_version: str = Field(min_length=1)
    bundle_id: str = Field(min_length=1)
    bundle_hash: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")


class InputBinding(_StrictModel):
    contract_b: ContractBBinding


class PolicyBinding(_StrictModel):
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    canonical: dict[str, Any]


class ProducerBinding(_StrictModel):
    semantic_implementation_sha: str = Field(pattern=r"^[0-9a-f]{40}$")
    policy: PolicyBinding


class ResultSetExecution(_StrictModel):
    state: Literal["completed", "failed", "incomplete"]


class PropositionCompletedExecution(_StrictModel):
    state: Literal["completed"]
    completion: Literal["assessed", "not_checkable"]


class PropositionFailedExecution(_StrictModel):
    state: Literal["failed"]


class PropositionIncompleteExecution(_StrictModel):
    state: Literal["incomplete"]


PropositionExecution = Annotated[
    PropositionCompletedExecution | PropositionFailedExecution | PropositionIncompleteExecution,
    Field(discriminator="state"),
]


class AssessmentNotPerformed(_StrictModel):
    state: Literal["not_performed"]


class AssessmentPerformed(_StrictModel):
    state: Literal["performed"]
    value: Literal["unknown", "adverse"]


class AssessmentFailed(_StrictModel):
    state: Literal["failed"]


class AssessmentNotApplicable(_StrictModel):
    state: Literal["not_applicable"]


AssessmentState = Annotated[
    AssessmentNotPerformed | AssessmentPerformed | AssessmentFailed | AssessmentNotApplicable,
    Field(discriminator="state"),
]


class AssessmentStages(_StrictModel):
    eligibility: AssessmentState
    semantic_validity: AssessmentState
    aperture_completeness: AssessmentState
    temporal_applicability: AssessmentState


class PropositionBinding(_StrictModel):
    proposition_id: str = Field(min_length=1)
    text_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


class EvidenceReference(_StrictModel):
    source_id: str = Field(min_length=1)
    passage_id: str = Field(min_length=1)
    passage_sha256: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")


class Contribution(_StrictModel):
    contribution_id: str = Field(pattern=r"^contribution:[0-9a-f]{64}$")
    channel: Literal["support", "counterevidence"]
    evidence_ref: EvidenceReference


class Measurement(_StrictModel):
    kind: str = Field(min_length=1)
    value: StrictFloat | None
    basis_contribution_ids: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_measurement(self) -> "Measurement":
        if self.value is not None and not math.isfinite(self.value):
            raise ValueError("measurement value must be finite")
        if len(set(self.basis_contribution_ids)) != len(self.basis_contribution_ids):
            raise ValueError("measurement basis contribution ids must be unique")
        for value in self.basis_contribution_ids:
            if not _CONTRIBUTION_ID.fullmatch(value):
                raise ValueError("invalid measurement basis contribution id")
        return self


class BasisMember(_StrictModel):
    namespace: Literal["contribution", "rule", "state"]
    id: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_namespace_prefix(self) -> "BasisMember":
        if self.namespace == "contribution" and not _CONTRIBUTION_ID.fullmatch(self.id):
            raise ValueError("contribution basis member must use contribution:<sha256>")
        if self.namespace == "rule" and not self.id.startswith("rule-role:"):
            raise ValueError("rule basis member must use rule-role: namespace")
        if self.namespace == "state" and not self.id.startswith("state:"):
            raise ValueError("state basis member must use state: namespace")
        return self


class RuleRole(_StrictModel):
    rule_id: str = Field(pattern=r"^rule-role:.+")
    code: str = Field(min_length=1)
    terminal_role: Literal["causal", "residual"]


class Conclusion(_StrictModel):
    reported_verdict: str = Field(min_length=1)
    terminal_branch: str = Field(min_length=1)
    causal_form: Literal[
        "single_necessary",
        "independent_sufficient_alternatives",
        "jointly_sufficient",
        "redundant_non_deciding",
    ]
    basis_members: list[BasisMember]
    residual_contribution_ids: list[str]
    rule_roles: list[RuleRole]

    @model_validator(mode="after")
    def validate_conclusion(self) -> "Conclusion":
        basis_pairs = [(item.namespace, item.id) for item in self.basis_members]
        if len(set(basis_pairs)) != len(basis_pairs):
            raise ValueError("basis members must be unique")
        if len(set(self.residual_contribution_ids)) != len(self.residual_contribution_ids):
            raise ValueError("residual contribution ids must be unique")
        for value in self.residual_contribution_ids:
            if not _CONTRIBUTION_ID.fullmatch(value):
                raise ValueError("invalid residual contribution id")
        rule_ids = [item.rule_id for item in self.rule_roles]
        if len(set(rule_ids)) != len(rule_ids):
            raise ValueError("rule ids must be unique")
        if self.causal_form == "single_necessary" and len(self.basis_members) != 1:
            raise ValueError("single_necessary requires exactly one basis member")
        if self.causal_form in {"independent_sufficient_alternatives", "jointly_sufficient"} and len(
            self.basis_members
        ) < 2:
            raise ValueError(f"{self.causal_form} requires at least two basis members")
        if self.causal_form == "redundant_non_deciding" and self.basis_members:
            raise ValueError("redundant_non_deciding cannot declare causal basis members")
        return self


class PropositionResult(_StrictModel):
    proposition: PropositionBinding
    execution: PropositionExecution
    assessments: AssessmentStages
    contributions: list[Contribution]
    measurement: Measurement | None
    conclusion: Conclusion | None

    @model_validator(mode="after")
    def validate_result(self) -> "PropositionResult":
        contribution_ids = [item.contribution_id for item in self.contributions]
        if len(set(contribution_ids)) != len(contribution_ids):
            raise ValueError("contribution ids must be unique within a proposition")
        contribution_set = set(contribution_ids)

        if self.measurement is not None:
            unknown_measurement_refs = set(self.measurement.basis_contribution_ids) - contribution_set
            if unknown_measurement_refs:
                raise ValueError(
                    "measurement basis references unknown contributions: "
                    + ",".join(sorted(unknown_measurement_refs))
                )

        if self.execution.state in {"failed", "incomplete"}:
            if self.conclusion is not None:
                raise ValueError("failed/incomplete proposition execution cannot carry a conclusion")
            return self

        if self.conclusion is None:
            raise ValueError("completed proposition execution requires a conclusion")
        if self.execution.completion == "not_checkable" and self.conclusion.reported_verdict != "not_checkable":
            raise ValueError("not_checkable completion requires reported_verdict=not_checkable")
        if self.execution.completion == "assessed" and self.conclusion.reported_verdict == "not_checkable":
            raise ValueError("assessed completion cannot report not_checkable")

        basis_contributions = {
            member.id for member in self.conclusion.basis_members if member.namespace == "contribution"
        }
        unknown_basis = basis_contributions - contribution_set
        if unknown_basis:
            raise ValueError("causal basis references unknown contributions: " + ",".join(sorted(unknown_basis)))

        residual = set(self.conclusion.residual_contribution_ids)
        unknown_residual = residual - contribution_set
        if unknown_residual:
            raise ValueError("residual set references unknown contributions: " + ",".join(sorted(unknown_residual)))
        overlap = basis_contributions & residual
        if overlap:
            raise ValueError("contribution cannot be both causal basis and residual: " + ",".join(sorted(overlap)))
        if basis_contributions | residual != contribution_set:
            missing = contribution_set - (basis_contributions | residual)
            raise ValueError("every retained contribution must be classified as causal basis or residual: " + ",".join(sorted(missing)))

        declared_rules = {item.rule_id: item for item in self.conclusion.rule_roles}
        for member in self.conclusion.basis_members:
            if member.namespace == "rule":
                role = declared_rules.get(member.id)
                if role is None:
                    raise ValueError(f"causal rule basis member has no rule role: {member.id}")
                if role.terminal_role != "causal":
                    raise ValueError(f"causal rule basis member is not marked causal: {member.id}")
        for rule in self.conclusion.rule_roles:
            in_basis = ("rule", rule.rule_id) in {
                (member.namespace, member.id) for member in self.conclusion.basis_members
            }
            if rule.terminal_role == "residual" and in_basis:
                raise ValueError(f"residual rule role cannot appear in causal basis: {rule.rule_id}")
        return self


class ContractCResultSet(_StrictModel):
    contract_c_version: Literal["1.0.0"]
    input: InputBinding
    producer: ProducerBinding
    execution: ResultSetExecution
    propositions: list[PropositionResult]
    result_set_id: str = Field(pattern=r"^result-set:[0-9a-f]{64}$")

    @model_validator(mode="after")
    def validate_result_set(self) -> "ContractCResultSet":
        proposition_ids = [item.proposition.proposition_id for item in self.propositions]
        if len(set(proposition_ids)) != len(proposition_ids):
            raise ValueError("proposition ids must be unique")
        if self.execution.state == "completed" and not self.propositions:
            raise ValueError("completed result set requires at least one proposition")
        return self


class ContractBIndexPassage(_StrictModel):
    source_id: str = Field(min_length=1)
    passage_sha256: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")


class ContractBIndex(_StrictModel):
    contract_version: str = Field(min_length=1)
    bundle_id: str = Field(min_length=1)
    bundle_hash: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    propositions: dict[str, str]
    passages: dict[str, ContractBIndexPassage]

    @model_validator(mode="after")
    def validate_index(self) -> "ContractBIndex":
        for digest in self.propositions.values():
            if not _HEX64.fullmatch(digest):
                raise ValueError("invalid proposition text hash in Contract-B index")
        return self


def _no_duplicate_object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON number is not permitted: {value}")


def parse_json_bytes(raw: bytes) -> dict[str, Any]:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("Contract C must be UTF-8 JSON") from exc
    try:
        value = json.loads(
            text,
            object_pairs_hook=_no_duplicate_object_pairs,
            parse_constant=_reject_constant,
        )
    except (json.JSONDecodeError, ValueError) as exc:
        raise ValueError(f"invalid Contract-C JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError("Contract C top level must be an object")
    return value


def _validate_json_numbers(value: Any) -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("non-finite number is not permitted")
    if isinstance(value, dict):
        for child in value.values():
            _validate_json_numbers(child)
    elif isinstance(value, list):
        for child in value:
            _validate_json_numbers(child)


def canonical_bytes(value: dict[str, Any]) -> bytes:
    _validate_json_numbers(value)
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def sha256_hex(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def result_set_identity(value: dict[str, Any]) -> str:
    payload = copy.deepcopy(value)
    payload.pop("result_set_id", None)
    return "result-set:" + sha256_hex(canonical_bytes(payload))


def with_result_set_identity(value: dict[str, Any]) -> dict[str, Any]:
    payload = copy.deepcopy(value)
    payload["result_set_id"] = result_set_identity(payload)
    return payload


def validate_whole_object_hash(raw: bytes, expected_sha256: str) -> list[str]:
    expected = expected_sha256.removeprefix("sha256:")
    if not _HEX64.fullmatch(expected):
        return ["expected whole-object SHA-256 must be 64 lowercase hex characters"]
    actual = sha256_hex(raw)
    if actual != expected:
        return [f"whole-object SHA-256 mismatch: expected {expected}, got {actual}"]
    return []


def _validate_policy_hash(value: ContractCResultSet) -> list[str]:
    actual = sha256_hex(canonical_bytes(value.producer.policy.canonical))
    if actual != value.producer.policy.sha256:
        return [
            "CAL policy hash mismatch: "
            f"expected {value.producer.policy.sha256}, computed {actual}"
        ]
    return []


def validate_internal_structure(value: dict[str, Any], contract_b_index: dict[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    try:
        model = ContractCResultSet.model_validate(value)
    except ValidationError as exc:
        return [f"schema/semantic validation failed: {item['loc']}: {item['msg']}" for item in exc.errors()]

    expected_result_id = result_set_identity(value)
    if model.result_set_id != expected_result_id:
        errors.append(
            "result_set_id mismatch: "
            f"expected {expected_result_id}, got {model.result_set_id}"
        )
    errors.extend(_validate_policy_hash(model))

    if contract_b_index is not None:
        try:
            index = ContractBIndex.model_validate(contract_b_index)
        except ValidationError as exc:
            errors.extend(
                f"Contract-B index invalid: {item['loc']}: {item['msg']}" for item in exc.errors()
            )
            return errors
        binding = model.input.contract_b
        if (
            binding.contract_version != index.contract_version
            or binding.bundle_id != index.bundle_id
            or binding.bundle_hash != index.bundle_hash
        ):
            errors.append("exact Contract-B binding does not match supplied Contract-B index")
        for proposition in model.propositions:
            pid = proposition.proposition.proposition_id
            expected_text_hash = index.propositions.get(pid)
            if expected_text_hash is None:
                errors.append(f"proposition is absent from Contract-B index: {pid}")
            elif proposition.proposition.text_sha256 != expected_text_hash:
                errors.append(f"proposition text hash mismatch for {pid}")
            for contribution in proposition.contributions:
                ref = contribution.evidence_ref
                indexed = index.passages.get(ref.passage_id)
                if indexed is None:
                    errors.append(f"passage is absent from Contract-B index: {ref.passage_id}")
                    continue
                if ref.source_id != indexed.source_id or ref.passage_sha256 != indexed.passage_sha256:
                    errors.append(f"evidence reference mismatch for passage {ref.passage_id}")
    return errors


def validate_contract_c_bytes(
    raw: bytes,
    *,
    expected_sha256: str | None = None,
    contract_b_index: dict[str, Any] | None = None,
) -> list[str]:
    errors: list[str] = []
    if expected_sha256 is not None:
        errors.extend(validate_whole_object_hash(raw, expected_sha256))
    try:
        value = parse_json_bytes(raw)
    except ValueError as exc:
        errors.append(str(exc))
        return errors
    try:
        expected_canonical = canonical_bytes(value)
    except (TypeError, ValueError) as exc:
        errors.append(f"canonicalization failed: {exc}")
        return errors
    if raw != expected_canonical:
        errors.append(
            "non-canonical Contract-C bytes: require sorted object keys, compact separators, "
            "UTF-8 Unicode, finite numbers, and exactly one trailing newline"
        )
    errors.extend(validate_internal_structure(value, contract_b_index=contract_b_index))
    return errors


def _load_json(path: Path) -> dict[str, Any]:
    value = parse_json_bytes(path.read_bytes())
    return value


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate Apparatus Contract C 1.0.0")
    parser.add_argument("artifact", type=Path)
    parser.add_argument("--expected-sha256")
    parser.add_argument("--contract-b-index", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    index = _load_json(args.contract_b_index) if args.contract_b_index else None
    errors = validate_contract_c_bytes(
        args.artifact.read_bytes(),
        expected_sha256=args.expected_sha256,
        contract_b_index=index,
    )
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(
        f"PASS: Contract C {CONTRACT_C_VERSION} canonical structure, references, "
        "content identity, and requested whole-object binding"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
