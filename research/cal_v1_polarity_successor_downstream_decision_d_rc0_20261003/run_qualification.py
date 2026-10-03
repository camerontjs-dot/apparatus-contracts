"""Issue 166 frozen operational runner.

Owns apparatus only. The preserved #123/#158 constructor stays byte-exact.
Runtime rebinds its producer pins to the polarity successor authority.
It does not rewrite CAL conclusion or polarity, and it does not require
old/new Contract C byte identity.

No Authorization, Contract E, pending-review dispatch, or execution surface exists.
"""

from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import importlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
APPARATUS = HERE.parent.parent
SEMANTIC = "caa0048f8f511ec3c4aa1ce713766f2219a04bc1"
RESOLVER = "292168222f83c67a24190b4846eebe84392e3d04"
CANDIDATE = "c183d2d12306ee30c509169a58db55e7430fe8c5"
CANDIDATE_BLOB = "aeb50dee8d24bda5f62eb879654e80437a50912d"
PREDECESSOR_SEMANTIC = "847cc970642bb648dc994b929c2053b5c9d4648c"
PREDECESSOR_RESOLVER = "1d33e0612befcf8016816197c90c062373796df9"
STRICT_INSTRUMENT = "strict-comparison-polarity-rc0"
PRIOR_STRICT_INSTRUMENT = "rc7fb1-comparator-1"
NEGATION = "Alpha did not have a higher rate than Beta."
SUPPORTED = "SUPPORTED_POLARITY_SUCCESSOR_DOWNSTREAM_DECISION_D_CONFORMANCE"
FALSIFIED = "FALSIFIED_POLARITY_SUCCESSOR_DOWNSTREAM_CONFORMANCE"
INVALID = "INCONCLUSIVE_APPARATUS_INVALID"
BLOCKED = "BLOCKED_EXACT_SUBJECT_UNAVAILABLE"
HASH_RE = re.compile(r"^(?:sha256:)?(?:[0-9a-f]{40}|[0-9a-f]{64})$")
ID_PREFIXES = (
    "cal-child-result:",
    "measurement:",
    "semantic-atom:",
    "semantic-authority:",
    "bound-relation:",
    "passage:",
    "query:",
    "retrieval:",
)


class SubjectUnavailable(RuntimeError):
    pass


class ScientificFailure(RuntimeError):
    pass


class ApparatusInvalid(RuntimeError):
    pass


class ConformanceStop(RuntimeError):
    pass


def canonical(value: Any) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n"
    ).encode()


def digest(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def blob(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def save(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical(value))


def load_module(path: Path, name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise SubjectUnavailable(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_validator(root: Path, module_name: str) -> Any:
    """Load a subject validator package so its relative imports resolve."""
    inserted = str(root)
    sys.path.insert(0, inserted)
    stale = [
        name
        for name in sys.modules
        if name == "validators" or name.startswith("validators.")
    ]
    for name in stale:
        del sys.modules[name]
    try:
        return importlib.import_module(module_name)
    finally:
        if sys.path and sys.path[0] == inserted:
            sys.path.pop(0)


def residue(value: Any) -> Any:
    """Drop producer identity, content hashes, and the added polarity field."""
    if isinstance(value, str):
        if value == STRICT_INSTRUMENT:
            return PRIOR_STRICT_INSTRUMENT
        if HASH_RE.fullmatch(value) or value.startswith(ID_PREFIXES):
            return "<id>"
        return value
    if isinstance(value, list):
        return [residue(item) for item in value]
    if isinstance(value, dict):
        return {
            key: residue(item)
            for key, item in value.items()
            if key not in {"assertion_polarity", "freeze_commit", "candidate_blob"}
        }
    return value


def residue_diff(left: Any, right: Any, prefix: str = "") -> list[str]:
    if type(left) is not type(right):
        return [f"{prefix}: {type(left).__name__} != {type(right).__name__}"]
    if isinstance(left, dict):
        keys = sorted(set(left) | set(right))
        rows: list[str] = []
        for key in keys:
            path = f"{prefix}.{key}" if prefix else key
            if key not in left or key not in right:
                rows.append(f"{path}: presence {key in left} != {key in right}")
            else:
                rows.extend(residue_diff(left[key], right[key], path))
        return rows
    if isinstance(left, list):
        if len(left) != len(right):
            return [f"{prefix}: len {len(left)} != {len(right)}"]
        rows = []
        for index, (a, b) in enumerate(zip(left, right, strict=True)):
            rows.extend(residue_diff(a, b, f"{prefix}[{index}]"))
        return rows
    if left != right:
        return [f"{prefix}: {left!r} != {right!r}"]
    return []


class Runner:
    def __init__(self, args: argparse.Namespace) -> None:
        self.args = args
        self.root = args.run_root.resolve()
        self.subject_root = args.subjects_root.resolve()
        self.subjects = json.loads((HERE / "SUBJECTS.json").read_bytes())
        self.baseline = json.loads((HERE / "HISTORICAL_BASELINE.json").read_bytes())
        self.env = os.environ.copy()
        self.env.pop("PYTHONPATH", None)
        self.env.update(
            PYTHONNOUSERSITE="1",
            PYTHONHASHSEED="0",
            TZ="UTC",
            UV_CACHE_DIR=str(self.root.parent / "uv-cache"),
        )
        self.phase = "preflight"
        self.arm = "S"
        self.negative = False
        self.current_root: Path | None = None
        self.root.mkdir(parents=True, exist_ok=False)
        (self.root / "commands").mkdir()
        self.receipt: dict[str, Any] = {
            "schema": "cal-polarity-successor-downstream-receipt-v1",
            "started_at": datetime.now(UTC).isoformat(),
            "status": "active",
            "phase": self.phase,
            "commands": [],
            "cases": {},
            "negative_controls": {},
            "determinism": "NOT_RUN",
            "decisive_exposure": False,
            "authorization_performed": False,
            "execution_performed": False,
        }
        self.checkpoint()

    def checkpoint(self) -> None:
        self.receipt["phase"] = self.phase
        save(self.root / "receipt.json", self.receipt)

    def command(
        self,
        args: list[str],
        *,
        label: str,
        cwd: Path | None = None,
        env: dict[str, str] | None = None,
        input_text: str | None = None,
        expected: int = 0,
    ) -> subprocess.CompletedProcess[str]:
        n = len(self.receipt["commands"]) + 1
        stem = f"{n:03d}-{label}"
        log = self.root / "commands" / stem
        row: dict[str, Any] = {
            "n": n,
            "phase": self.phase,
            "label": label,
            "argv": args,
            "cwd": str(cwd or Path.cwd()),
            "expected_exit": expected,
            "stdin_sha256": digest(input_text.encode()) if input_text is not None else None,
        }
        self.receipt["commands"].append(row)
        self.checkpoint()
        completed = subprocess.run(
            args,
            cwd=cwd,
            env=env or self.env,
            input=input_text.encode() if input_text is not None else None,
            capture_output=True,
            check=False,
        )
        log.with_suffix(".stdout").write_bytes(completed.stdout)
        log.with_suffix(".stderr").write_bytes(completed.stderr)
        row.update(
            actual_exit=completed.returncode,
            stdout_sha256=digest(completed.stdout),
            stderr_sha256=digest(completed.stderr),
            stdout_bytes=len(completed.stdout),
            stderr_bytes=len(completed.stderr),
            log_stem=f"commands/{stem}",
        )
        self.checkpoint()
        if completed.returncode != expected:
            raise RuntimeError(
                f"{self.phase}/{label}: exit {completed.returncode}, expected {expected}; "
                f"{completed.stderr.decode(errors='replace')[-2000:]}"
            )
        return subprocess.CompletedProcess(
            args, completed.returncode, completed.stdout.decode(), completed.stderr.decode()
        )

    def git(self, root: Path, *args: str) -> str:
        return self.command(["git", "-C", str(root), *args], label="identity").stdout.strip()

    def verify(self) -> None:
        self.phase = "identity"
        freeze = json.loads((HERE / "EXPERIMENT.json").read_bytes())
        for name, expected in freeze["frozen_files"].items():
            if digest((HERE / name).read_bytes()) != expected:
                raise SubjectUnavailable(f"frozen apparatus file changed: {name}")
        base = self.subjects["apparatus_base"]
        self.git(APPARATUS, "merge-base", "--is-ancestor", base, "HEAD")
        self.git(APPARATUS, "merge-base", "--is-ancestor", freeze["source_commit"], "HEAD")
        if self.git(APPARATUS, "rev-parse", f"{freeze['source_commit']}^{{tree}}") != freeze["source_tree"]:
            raise SubjectUnavailable("frozen apparatus source tree mismatch")
        changed = self.git(APPARATUS, "diff", "--name-only", base, "HEAD").splitlines()
        allowed_prefix = "research/cal_v1_polarity_successor_downstream_decision_d_rc0_20261003/"
        allowed_workflow = ".github/workflows/cal-v1-polarity-successor-downstream-decision-d-rc0.yml"
        if any(not (path.startswith(allowed_prefix) or path == allowed_workflow) for path in changed):
            raise SubjectUnavailable("apparatus delta changes a component or historical experiment")
        if self.git(APPARATUS, "status", "--porcelain", "--untracked-files=no"):
            raise SubjectUnavailable("apparatus tracked tree is dirty")
        self.receipt["apparatus"] = {
            "head": self.git(APPARATUS, "rev-parse", "HEAD"),
            "tree": self.git(APPARATUS, "rev-parse", "HEAD^{tree}"),
            "base": base,
            "frozen_source": freeze["source_commit"],
            "frozen_source_tree": freeze["source_tree"],
            "frozen_files": freeze["frozen_files"],
            "harness_blob": self.git(APPARATUS, "hash-object", str(HERE / "run_qualification.py")),
        }
        if self.receipt["apparatus"]["harness_blob"] != freeze["harness_blob"]:
            raise SubjectUnavailable("frozen harness blob mismatch")
        observed = {}
        for name, authority in self.subjects["subjects"].items():
            path = self.subject_root / name
            if not (path / ".git").exists():
                raise SubjectUnavailable(f"missing exact subject: {name}")
            if (
                self.git(path, "rev-parse", "HEAD") != authority["commit"]
                or self.git(path, "rev-parse", "HEAD^{tree}") != authority["tree"]
                or self.git(path, "status", "--porcelain")
            ):
                raise SubjectUnavailable(f"subject identity/clean-tree mismatch: {name}")
            for rel, expected in authority["blobs"].items():
                if blob((path / rel).read_bytes()) != expected:
                    raise SubjectUnavailable(f"protected working blob mismatch: {name}/{rel}")
            observed[name] = {
                "commit": authority["commit"],
                "tree": authority["tree"],
                "checked_blobs": len(authority["blobs"]),
                "clean": True,
            }
        for name, tag in self.subjects["release_tags"].items():
            path = self.subject_root / name
            if (
                self.git(path, "rev-parse", f"refs/tags/{tag['name']}") != tag["object"]
                or self.git(path, "rev-parse", f"refs/tags/{tag['name']}^{{}}") != self.subjects["subjects"][name]["commit"]
            ):
                raise SubjectUnavailable(f"released tag mismatch: {name}")
        protected = self.subjects["protected_identities"]
        decision = self.subject_root / "decision"
        for rel, expected in protected["decision_blobs"].items():
            if blob((decision / rel).read_bytes()) != expected:
                raise SubjectUnavailable(f"decision protected blob mismatch: {rel}")
        if blob((self.subject_root / "contract-c" / protected["candidate_path"]).read_bytes()) != CANDIDATE_BLOB:
            raise SubjectUnavailable("successor candidate blob mismatch")
        if blob((self.subject_root / "contract-c-resolver" / protected["resolver_path"]).read_bytes()) != protected["resolver_blob"]:
            raise SubjectUnavailable("successor resolver blob mismatch")
        self.receipt["subjects"] = observed
        self.checkpoint()

    def prepare(self) -> None:
        self.phase = "build-and-clean-install"
        version = self.command([self.args.python, "--version"], label="python-version").stdout
        if not version.startswith("Python 3.11."):
            raise RuntimeError("apparatus requires the Python 3.11 runtime pattern")
        node = self.command([self.args.node, "--version"], label="node-version").stdout
        if not node.startswith("v22."):
            raise RuntimeError("apparatus requires the Node 22 runtime pattern")
        self.receipt["runtime"] = {"python": version.strip(), "node": node.strip()}
        builder = self.root / "build-env"
        self.command(["uv", "venv", "--python", self.args.python, str(builder)], label="builder-venv")
        build_py = str(builder / "bin/python")
        self.command(["uv", "pip", "install", "--python", build_py, "build==1.3.0"], label="build-dependency")
        subject = self.subject_root / "cal"
        dist = self.root / "dist-S"
        self.command(
            [build_py, "-m", "build", "--wheel", "--outdir", str(dist), str(subject)],
            label="wheel-S",
        )
        wheels = list(dist.glob("*.whl"))
        if len(wheels) != 1:
            raise RuntimeError("expected one exact CAL wheel")
        wheel = wheels[0]
        checked = 0
        absent_nonruntime_data = []
        with zipfile.ZipFile(wheel) as zipped:
            members = set(zipped.namelist())
            for rel, expected in self.subjects["subjects"]["cal"]["blobs"].items():
                if not rel.startswith("src/claim_audit_lab/"):
                    continue
                if rel[4:] not in members:
                    if rel.endswith(".py") or rel.startswith("src/claim_audit_lab/production_v1/"):
                        raise SubjectUnavailable(f"required runtime file missing: {rel}")
                    absent_nonruntime_data.append(rel)
                    continue
                if blob(zipped.read(rel[4:])) != expected:
                    raise SubjectUnavailable(f"packaged source bytes differ: {rel}")
                checked += 1
        env_path = self.root / "env-S"
        py = str(env_path / "bin/python")
        self.command(["uv", "venv", "--python", self.args.python, str(env_path)], label="clean-venv-S")
        self.command(
            ["uv", "pip", "install", "--python", py, str(wheel), "rfc8785==0.1.4", "rank-bm25==0.2.2"],
            label="clean-install-S",
        )
        footprint = self.command(["uv", "pip", "freeze", "--python", py], label="dependency-footprint-S").stdout
        (self.root / "dependencies-S.txt").write_text(footprint)
        versions = self.command(
            ["uv", "pip", "list", "--python", py, "--format", "json"],
            label="dependency-versions-S",
        ).stdout
        save(self.root / "dependency-versions-S.json", json.loads(versions))
        inspection = self.command(
            [str(env_path / "bin/claim-audit-v1"), "inspect", "--json"],
            label="installed-inspect-S",
        )
        inspect_value = json.loads(inspection.stdout)
        if inspect_value["semantic_implementation_sha"] != SEMANTIC:
            raise SubjectUnavailable("installed semantic identity mismatch")
        save(self.root / "installed-inspect-S.json", inspect_value)
        program = (
            "import json,claim_audit_lab; from pathlib import Path; "
            "p=Path(claim_audit_lab.__file__).resolve(); "
            "print(json.dumps({'module':str(p),'prefix':str(Path(__import__('sys').prefix).resolve())}))"
        )
        provenance = json.loads(self.command([py, "-c", program], label="installed-provenance-S").stdout)
        if not Path(provenance["module"]).is_relative_to(env_path.resolve()):
            raise SubjectUnavailable("CAL import is not from the clean wheel environment")
        self.receipt["builds"] = {
            "S": {
                "wheel": str(wheel.relative_to(self.root)),
                "sha256": digest(wheel.read_bytes()),
                "source_blobs_checked": checked,
                "absent_nonruntime_data": absent_nonruntime_data,
                "clean_installed": True,
                "module_provenance": provenance,
            }
        }
        self.receipt["status"] = "runtime_prepared"
        self.checkpoint()

    def load_source(self) -> None:
        self.phase = "constructor-import"
        # Run 01 blocked here: the orchestrator interpreter could not import
        # the preserved constructor. The clean environment already has that
        # dependency set. EB source still comes from the exact subject tree.
        site_packages = self.root / "env-S" / "lib" / "python3.11" / "site-packages"
        if not site_packages.is_dir():
            raise SubjectUnavailable("clean environment does not provide the constructor imports")
        sys.path.insert(0, str(site_packages))
        self.receipt["orchestrator_imports"] = "clean-env-S-site-packages"
        roots = {
            "CONTRACT_A_ROOT": "contract-a",
            "EB_ROOT": "eb",
            "CONTRACT_C_ROOT": "contract-c",
            "CONTRACT_C_RC2_ROOT": "contract-c-rc2",
            "CONTRACT_C_RESOLVER_ROOT": "contract-c-resolver",
            "CONSUMER_ROOT": "contract-c-consumer",
            "DECISION_ROOT": "decision",
            "CONTRACT_D_ROOT": "contract-d",
        }
        for key, name in roots.items():
            os.environ[key] = str(self.subject_root / name)
        os.environ.update(
            CAL_PARENT_CLI=str(self.root / "env-S/bin/claim-audit-v1-parent"),
            PYTHON=str(self.root / "env-S/bin/python"),
            NODE=self.args.node,
            COMPOSITION_ROOT=str(self.root / "worlds"),
        )
        saved_argv = sys.argv
        sys.argv = ["source_pr123.py", str(self.root / "unused-constructor-result.json")]
        try:
            module = load_module(HERE / "source_pr123.py", "preserved_pr123")
        finally:
            sys.argv = saved_argv
        module.CAL_SEMANTIC_IMPLEMENTATION = SEMANTIC
        module.C_FREEZE = CANDIDATE
        module.RESOLVER_COMMIT = RESOLVER
        self.source = module
        expected = self.subjects["cases"]
        observed = [
            {
                "case_id": case.case_id,
                "c1_source": case.c1_source,
                "admit_c2": case.admit_c2,
                "parent": case.expected_parent,
                "decision": case.expected_decision,
                "consumer": case.expected_consumer,
            }
            for case in module.CASES
        ]
        if expected != observed:
            raise SubjectUnavailable("preserved case definitions disagree with frozen expectations")
        for child in ("C1", "C2"):
            if module.canonical_json_bytes(module.target(child)) != (HERE / "trusted-targets" / f"{child}.target.json").read_bytes():
                raise SubjectUnavailable("preserved targets differ from frozen trusted inputs")
        if digest((HERE / "source_pr123.py").read_bytes()) != self.subjects["constructor_sha256"]:
            raise SubjectUnavailable("preserved constructor bytes changed")
        module.run_checked = self.run_checked

    def gate_children(self, args: list[str]) -> list[str]:
        bundle = args[3]
        root = Path(args[args.index("--out-dir") + 1]).parent
        env_path = self.root / "env-S"
        selected: dict[str, Path] = {}
        new_args = list(args)
        for index, value in enumerate(args):
            if value != "--target":
                continue
            child, old = args[index + 1].split("=", 1)
            trusted = Path(old)
            trusted_bytes = (HERE / "trusted-targets" / f"{child}.target.json").read_bytes()
            if trusted.read_bytes() != trusted_bytes:
                raise ApparatusInvalid(f"{child} target is not the frozen trusted input")
            target = trusted
            py = str(env_path / "bin/python")
            prefix = [py, "-m", "claim_audit_lab.production_v1.target_cli"]
            authored = self.command([*prefix, "author", bundle, child], label="target-author")
            target = root / f"{child}.authored.target.json"
            target.write_bytes(authored.stdout.encode())
            if target.read_bytes() != trusted_bytes:
                raise ScientificFailure(f"{child} authored target drifted from the trusted target")
            if self.negative and child == "C1":
                mutated = json.loads(target.read_bytes())
                mutated["proposition"]["fields"]["comparison_direction"] = "LESS_THAN"
                target = root / "C1.drift.target.json"
                target.write_bytes(self.source.canonical_json_bytes(mutated))
                self.command(
                    [str(env_path / "bin/claim-audit-v1"), "validate-bundle", bundle, str(target)],
                    label="structural-weak",
                )
            conform = self.command(
                [*prefix, "conform", bundle, str(target)],
                label="target-conformance",
                expected=2 if self.negative else 0,
            )
            if self.negative:
                if conform.stdout or "conform rejected:" not in conform.stderr:
                    raise ApparatusInvalid("negative conformance did not reach the intended semantic rejection")
                save(
                    root / "conformance-stop.json",
                    {
                        "structural_accepted": True,
                        "conformance_rejected": True,
                        "mutation": "strict_direction_disagrees_with_claim",
                    },
                )
                raise ConformanceStop("candidate conformance stopped the orchestrated arm")
            save(root / f"{child}.conformance.json", json.loads(conform.stdout))
            new_args[index + 1] = f"{child}={target}"
            selected[child] = target
        if set(selected) != {"C1", "C2"}:
            raise RuntimeError("complete target gate required before any child execution")
        for child, target in selected.items():
            out = root / "explicit-children" / child
            self.command(
                [str(env_path / "bin/claim-audit-v1"), "run-bundle", bundle, str(target), "--out-dir", str(out)],
                label="cal-child",
            )
        return new_args

    def run_checked(
        self,
        args: list[str],
        *,
        cwd: Path | None = None,
        env: dict[str, str] | None = None,
        input_text: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        label = "contract-a-validator"
        if Path(args[0]).name == "claim-audit-v1-parent":
            args = self.gate_children(args)
            label = "cal-parent"
        elif len(args) > 1 and args[1].endswith("decision-engine-parent-bound-evaluate.mjs"):
            label = "decision"
        elif len(args) > 2 and "validators.contract_d_consume" in args[2]:
            label = "contract-d-consumer"
        result = self.command(args, label=label, cwd=cwd, env=env, input_text=input_text)
        if label == "contract-d-consumer" and self.current_root is not None:
            (self.current_root / "contract-d-consumer.json").write_bytes(result.stdout.encode())
        return result

    def bind_chain(self, execution: dict[str, Any]) -> None:
        parent = json.loads(execution["parent_bytes"])
        contract_c = json.loads(execution["c_bytes"])
        decision = json.loads(execution["d_bytes"])
        if "epistemic_audit.stage_pending_review@1" in json.dumps(decision):
            raise ScientificFailure("prohibited pending-review effect reached Contract D")
        producer = contract_c["rc2_result"]["producer"]
        if producer["semantic_implementation_sha"] != SEMANTIC:
            raise ScientificFailure("Contract C producer semantic identity drifted")
        if producer["policy_resolver_commit_sha"] != RESOLVER:
            raise ScientificFailure("Contract C producer resolver drifted")
        if producer["policy_sha256"] != self.baseline["unchanged_authority"]["policy_sha256"]:
            raise ScientificFailure("Contract C policy digest drifted")
        if parent["contract_c"]["candidate_blob"] != CANDIDATE_BLOB:
            raise ScientificFailure("parent candidate blob is not the successor authority")
        if parent["contract_c"]["freeze_commit"] != CANDIDATE:
            raise ScientificFailure("parent freeze commit is not the successor authority")
        if parent["semantic_implementation_sha"] != SEMANTIC:
            raise ScientificFailure("parent semantic identity drifted")
        if parent["authorization"]["automatic_action_allowed"] is not False:
            raise ScientificFailure("CAL authorized an action")
        by_id = {row["proposition_id"]: row for row in contract_c["recomposition"]["ordered_children"]}
        for child in parent["children"]:
            native_path = execution["cal_out"] / "children" / child["proposition_id"] / "result.json"
            native_bytes = native_path.read_bytes()
            native = json.loads(native_bytes)
            if digest(native_bytes) != child["native_result_sha256"]:
                raise ScientificFailure("parent does not bind the native result bytes")
            if by_id[child["proposition_id"]]["conclusion"] != native["result"]["conclusion"]:
                raise ScientificFailure("Contract C conclusion rewrote the CAL conclusion")
            if child["conclusion"] != native["result"]["conclusion"]:
                raise ScientificFailure("parent conclusion rewrote the CAL conclusion")
            if native["semantic_implementation_sha"] != SEMANTIC:
                raise ScientificFailure("native semantic identity drifted")
        if decision["input_authority"]["immutable_id"] != execution["record"]["contract_c_sha256"]:
            raise ScientificFailure("Decision is not bound to the emitted Contract C bytes")
        if decision["input_authority"]["id"] != contract_c["result_set_id"]:
            raise ScientificFailure("Decision is not bound to the Contract C result set")
        if decision["policy"]["id"] != self.baseline["unchanged_authority"]["policy_id"]:
            raise ScientificFailure("Decision policy changed")
        if decision["effect"]["type"] != self.baseline["unchanged_authority"]["effect_type"]:
            raise ScientificFailure("Contract D effect changed")
        recomposition = contract_c["recomposition"]
        unchanged = self.baseline["unchanged_authority"]
        if recomposition["cal_freeze_commit"] != unchanged["cal_freeze_commit"]:
            raise ScientificFailure("Contract C recomposition freeze commit drifted")
        if recomposition["cal_semantic_source_commit"] != unchanged["cal_semantic_source_commit"]:
            raise ScientificFailure("Contract C recomposition semantic source drifted")

    def attribute_case(self, case_id: str, execution: dict[str, Any]) -> dict[str, Any]:
        expected = self.baseline["cases"][case_id]
        record = execution["record"]
        if record["contract_a_handoff_sha256"] != self.baseline["contract_a_handoff_sha256"]:
            raise ApparatusInvalid(f"{case_id} Contract A world changed")
        if record["eb_native_package_sha256"] != expected["eb_native_package_sha256"]:
            raise ApparatusInvalid(f"{case_id} EB package changed")
        if record["contract_b_bundle_hash"] != expected["contract_b_bundle_hash"]:
            raise ApparatusInvalid(f"{case_id} Contract B bundle changed")
        if record["contract_c_sha256"] == expected["historical_contract_c_sha256"]:
            raise ScientificFailure(f"{case_id} Contract C bytes did not carry the new producer identity")
        parent = json.loads(execution["parent_bytes"])
        decision = json.loads(execution["d_bytes"])
        if parent["parent_conclusion"] != expected["parent"]:
            raise ScientificFailure(f"{case_id} parent {parent['parent_conclusion']}")
        if decision["evaluation"]["disposition"] != expected["decision"]:
            raise ScientificFailure(f"{case_id} decision {decision['evaluation']['disposition']}")
        if record["contract_d_consumer"] != expected["consumer"]:
            raise ScientificFailure(f"{case_id} consumer {record['contract_d_consumer']}")
        if decision["metadata"]["reason_codes"] != expected["reason_codes"]:
            raise ScientificFailure(f"{case_id} reason codes changed")
        if decision["metadata"]["diagnostics"]["parent_conclusion"] != expected["parent"]:
            raise ScientificFailure(f"{case_id} decision diagnostic parent changed")
        if decision["target"]["content_sha256"] != self.baseline["unchanged_authority"]["target_content_sha256"]:
            raise ScientificFailure(f"{case_id} decision target changed")
        historical = HERE / "historical" / case_id
        changed = {}
        for label, new_path, old_name in (
            ("parent", execution["cal_out"] / "parent-result.json", "parent-result.json"),
            ("contract_c", execution["cal_out"] / "contract-c.json", "contract-c.json"),
            ("contract_d", execution["d_path"], "contract-d.json"),
            ("C1", execution["cal_out"] / "children/C1/result.json", "C1-result.json"),
            ("C2", execution["cal_out"] / "children/C2/result.json", "C2-result.json"),
        ):
            new = json.loads(new_path.read_bytes())
            old = json.loads((historical / old_name).read_bytes())
            diff = residue_diff(residue(old), residue(new))
            if diff:
                raise ScientificFailure(f"{case_id} {label} semantic residue changed: {diff[:8]}")
            changed[label] = {
                "historical_sha256": digest((historical / old_name).read_bytes()),
                "successor_sha256": digest(new_path.read_bytes()),
                "byte_equal": new_path.read_bytes() == (historical / old_name).read_bytes(),
            }
        self._assert_child_semantics(case_id, execution, expected)
        return {"upstream_world_byte_equal": True, "changed_bytes": changed}

    def _assert_child_semantics(self, case_id: str, execution: dict[str, Any], expected: dict[str, Any]) -> None:
        for child, spec in expected["children"].items():
            native = json.loads((execution["cal_out"] / "children" / child / "result.json").read_bytes())
            if native["result"]["conclusion"] != spec["conclusion"]:
                raise ScientificFailure(f"{case_id} {child} conclusion changed")
            if child == "C2" and spec["conclusion"] == "not_checkable":
                continue
            if child == "C2":
                measurement = native["measurements"][0]
                if measurement["instrument_id"] != spec["instrument_id"] or measurement["instrument_version"] != spec["instrument_version"]:
                    raise ScientificFailure(f"{case_id} C2 instrument changed")
                continue
            proposal = native["measurements"][0]["raw_measurement"]["proposals"][0]
            if proposal["relation"] != spec["relation"]:
                raise ScientificFailure(f"{case_id} C1 relation changed")
            if proposal.get("assertion_polarity") != spec["assertion_polarity"]:
                raise ScientificFailure(f"{case_id} C1 polarity was not preserved")
            atom = native["authorities"][0]["atom"]["fields"]
            if atom.get("assertion_polarity") != proposal["assertion_polarity"] or atom.get("relation") != proposal["relation"]:
                raise ScientificFailure(f"{case_id} polarity or relation was rewritten inside CAL")
            if native["relations"][0]["categorical_relation"] != spec["categorical_relation"]:
                raise ScientificFailure(f"{case_id} categorical relation changed")
            if native["measurements"][0]["instrument_version"] != STRICT_INSTRUMENT:
                raise ScientificFailure(f"{case_id} strict instrument version is not the polarity successor")

    def case(self, case: Any, suffix: str = "") -> dict[str, Any]:
        self.arm = "S"
        self.phase = f"S/{case.case_id}{suffix}"
        self.receipt["decisive_exposure"] = True
        self.checkpoint()
        self.current_root = self.root / "worlds" / "S" / f"{case.case_id}{suffix}"
        self.source.CAL_CLI = self.root / "env-S/bin/claim-audit-v1-parent"
        start = len(self.receipt["commands"])
        try:
            execution = self.source.execute_case(case, self.current_root)
        except RuntimeError as exc:
            if ": expected parent " in str(exc) or ": expected Decision " in str(exc) or ": expected Contract D consumer " in str(exc):
                raise ScientificFailure(str(exc)) from exc
            raise
        execution["root"] = self.current_root
        save(self.current_root / "eb-native-package.json", execution["package"])
        for child in ("C1", "C2"):
            explicit = self.current_root / "explicit-children" / child
            parent_child = execution["cal_out"] / "children" / child
            explicit_files = {path.relative_to(explicit).as_posix() for path in explicit.rglob("*") if path.is_file()}
            parent_files = {path.relative_to(parent_child).as_posix() for path in parent_child.rglob("*") if path.is_file()}
            if explicit_files != parent_files:
                raise ScientificFailure(f"{child} explicit and parent artifact sets differ")
            for name in explicit_files:
                if (explicit / name).read_bytes() != (parent_child / name).read_bytes():
                    raise ScientificFailure(f"{child} explicit bytes differ from parent bytes: {name}")
        decision_rows = [row for row in self.receipt["commands"][start:] if row["label"] == "decision"]
        if len(decision_rows) != 1:
            raise RuntimeError("one maintained Decision invocation required per case")
        cli_stdout = self.root / (decision_rows[0]["log_stem"] + ".stdout")
        if cli_stdout.read_bytes() != execution["d_path"].read_bytes():
            raise ScientificFailure("Decision stdout bytes differ from the materialized Contract D file")
        self.bind_chain(execution)
        if suffix == "":
            execution["attribution"] = self.attribute_case(case.case_id, execution)
        self.receipt["cases"][f"S/{case.case_id}{suffix}"] = execution["record"]
        self.checkpoint()
        print(f"completed S/{case.case_id}{suffix}", flush=True)
        return execution

    def polarity_case(self) -> dict[str, Any]:
        """Execute the negation specimen through the same gated parent entry."""
        self.phase = "S/POLARITY"
        self.receipt["decisive_exposure"] = True
        self.checkpoint()
        source = self.source
        root = self.root / "worlds" / "S" / "POLARITY"
        if root.exists():
            raise ApparatusInvalid("polarity output already exists")
        self.current_root = root
        source.CAL_CLI = self.root / "env-S/bin/claim-audit-v1-parent"
        original_contract_a = source.contract_a
        original_execute = source.execute_case

        def polarity_contract_a() -> dict[str, Any]:
            value = original_contract_a()
            value["sources"].append(
                {
                    "source_id": "S-C1-NEGATE",
                    "media_type": "text/plain; charset=utf-8",
                    "content": NEGATION,
                    "content_sha256": source.tagged_text(NEGATION),
                }
            )
            value["handoff_sha256"] = "sha256:" + ("0" * 64)
            value["handoff_sha256"] = source.compute_handoff_sha256(value)
            return value

        source.contract_a = polarity_contract_a
        case = source.Case(
            "POLARITY",
            "S-C1-NEGATE",
            True,
            "contradicted",
            "hold",
            "hold",
        )
        try:
            execution = original_execute(case, root)
        except RuntimeError as exc:
            message = str(exc)
            if "was not uniquely retained" in message:
                raise ApparatusInvalid(message) from exc
            if ": expected parent " in message or ": expected Decision " in message or ": expected Contract D consumer " in message:
                raise ScientificFailure(message) from exc
            raise
        finally:
            source.contract_a = original_contract_a
        execution["root"] = root
        self.bind_chain(execution)
        native = json.loads((execution["cal_out"] / "children" / "C1" / "result.json").read_bytes())
        proposal = native["measurements"][0]["raw_measurement"]["proposals"][0]
        spec = self.baseline["polarity_case"]
        if native["original_claim"] != spec["claim"]:
            raise ScientificFailure("polarity claim text changed")
        if proposal["relation"] != spec["relation"] or proposal.get("assertion_polarity") != spec["assertion_polarity"]:
            raise ScientificFailure("polarity successor did not preserve negative MORE_THAN")
        atom = native["authorities"][0]["atom"]["fields"]
        if atom.get("relation") != proposal["relation"] or atom.get("assertion_polarity") != proposal["assertion_polarity"]:
            raise ScientificFailure("an adapter rewrote polarity between measurement and authority")
        if native["relations"][0]["categorical_relation"] != spec["categorical_relation"]:
            raise ScientificFailure("negative MORE_THAN did not refute")
        if native["result"]["conclusion"] != spec["child_conclusion"]:
            raise ScientificFailure("polarity child conclusion was not contradicted")
        passage_source = native["authorities"][0]["atom"].get("source_id")
        if passage_source != "S-C1-NEGATE":
            raise ScientificFailure(f"polarity deciding source was {passage_source}")
        self.receipt["cases"]["S/POLARITY"] = execution["record"]
        self.checkpoint()
        print("completed S/POLARITY", flush=True)
        return execution

    def attack(self, pipe01: dict[str, Any], pipe03: dict[str, Any]) -> dict[str, Any]:
        self.phase = "S/cross-run-replay"
        inputs = copy.deepcopy(pipe01["consumer_inputs"])
        common = next(
            (key for key in inputs["native_child_results_b64"] if key in pipe03["consumer_inputs"]["native_child_results_b64"]),
            None,
        )
        if common is None:
            raise ApparatusInvalid("cross-run replay has no common child")
        inputs["native_child_results_b64"][common] = pipe03["consumer_inputs"]["native_child_results_b64"][common]
        if base64.b64decode(inputs["native_child_results_b64"][common]) == base64.b64decode(
            pipe01["consumer_inputs"]["native_child_results_b64"][common]
        ):
            raise ApparatusInvalid("cross-run replay control has identical source bytes")
        root = self.root / "negative-controls" / "replay-S"
        root.mkdir(parents=True)
        path = root / "consumer-inputs.json"
        path.write_bytes(self.source.canonical_json_bytes(inputs))
        completed = self.command(
            [
                self.args.node,
                str(self.subject_root / "decision/scripts/decision-engine-parent-bound-evaluate.mjs"),
                "--contract-c",
                str(pipe01["cal_out"] / "contract-c.json"),
                "--contract-c-sha256",
                pipe01["record"]["contract_c_sha256"],
                "--consumer-authority",
                str(self.subject_root / "contract-c-consumer"),
                "--consumer-inputs",
                str(path),
                "--contract-d-authority",
                str(self.subject_root / "contract-d"),
                "--target",
                str(pipe01["target_path"]),
                "--python",
                str(self.root / "env-S/bin/python"),
            ],
            label="decision-replay",
            expected=1,
        )
        error = json.loads(completed.stderr)
        if completed.stdout or error.get("code") != "contract_c_validation_failed" or "NATIVE_RESULT_HASH_MISMATCH" not in error.get("message", ""):
            raise ScientificFailure("replay did not reject at the native-byte binding before D output")
        row = {
            "substituted_child": common,
            "rejected_before_contract_d": True,
            "false_accepts": 0,
            "stdout_bytes": 0,
            "error": error,
            "attack_inputs_sha256": digest(path.read_bytes()),
        }
        save(root / "result.json", row)
        return row

    def conformance_stop(self) -> dict[str, Any]:
        self.negative = True
        self.phase = "S/conformance-stop"
        self.current_root = self.root / "negative-controls/conformance-stop"
        self.source.CAL_CLI = self.root / "env-S/bin/claim-audit-v1-parent"
        start = len(self.receipt["commands"])
        try:
            self.source.execute_case(self.source.CASES[0], self.current_root)
        except ConformanceStop:
            pass
        else:
            raise ScientificFailure("conformance drift control reached downstream execution")
        finally:
            self.negative = False
        rows = self.receipt["commands"][start:]
        forbidden = {"cal-child", "cal-parent", "decision", "contract-d-consumer"}
        if any(row["label"] in forbidden for row in rows):
            raise ScientificFailure("orchestration invoked a forbidden stage after conformance stop")
        if (self.current_root / "explicit-children").exists() or (self.current_root / "cal").exists() or list(self.current_root.rglob("contract-c.json")) or list(self.current_root.rglob("contract-d.json")):
            raise ScientificFailure("conformance-stop emitted native/C/D bytes")
        row = {
            "structural_accepted": True,
            "conformance_rejected": True,
            "conformance_exit": 2,
            "observed_stage_labels": [item["label"] for item in rows],
            "false_accepts": 0,
            "raw_run_bundle_claim": False,
        }
        save(self.current_root / "control-result.json", row)
        return row

    def reseal(self, rc2: Any, candidate: Any, outer: dict[str, Any], **producer_updates: str) -> tuple[dict[str, Any], dict[str, Any]]:
        inner = copy.deepcopy(outer["rc2_result"])
        inner.pop("result_set_id", None)
        inner["producer"].update(producer_updates)
        sealed_inner = rc2.seal(inner)
        body = copy.deepcopy(outer)
        body.pop("result_set_id", None)
        body["rc2_result"] = sealed_inner
        return candidate.seal(body), sealed_inner

    def authority_controls(self, execution: dict[str, Any]) -> dict[str, Any]:
        self.phase = "S/authority-controls"
        outer = json.loads(execution["c_bytes"])
        rc2 = load_validator(self.subject_root / "contract-c-rc2", "validators.contract_c_rc2")
        successor = load_module(
            self.subject_root / "contract-c/research/contract_c_cal_v1_polarity_authority_successor_rc0_20261003/candidate_rc0.py",
            "polarity_successor_candidate",
        )
        predecessor = load_module(
            self.subject_root / "contract-c-predecessor/research/contract_c_cal_v1_parent_recomposition_rc0_20260919/candidate_rc0.py",
            "polarity_predecessor_candidate",
        )
        successor_resolver = json.loads(
            (self.subject_root / "contract-c-resolver/research/contract_c_cal_v1_polarity_authority_successor_rc0_20261003/RESOLVER.json").read_bytes()
        )
        predecessor_resolver = json.loads(
            (self.subject_root / "contract-c-resolver-predecessor/research/contract_c2_current_cal_resolver_successor_rc0/RESOLVER.json").read_bytes()
        )
        successor_ids = {entry["semantic_implementation_sha"] for entry in successor_resolver["entries"]}
        predecessor_ids = {entry["semantic_implementation_sha"] for entry in predecessor_resolver["entries"]}
        if SEMANTIC not in successor_ids or PREDECESSOR_SEMANTIC not in successor_ids:
            raise ApparatusInvalid("successor resolver does not list both producer identities")
        if SEMANTIC in predecessor_ids or PREDECESSOR_SEMANTIC not in predecessor_ids:
            raise ApparatusInvalid("predecessor resolver listing is not the historical producer set")

        def expect_reject(label: str, function: Any, message_part: str) -> str:
            try:
                function()
            except Exception as exc:
                text = str(exc)
                if message_part not in text:
                    raise ScientificFailure(f"{label} rejected for {text!r}, not {message_part}") from exc
                return text
            raise ScientificFailure(f"{label} fail-open accepted")

        predecessor_reason = expect_reject(
            "predecessor-candidate",
            lambda: predecessor.validate_object(outer, rc2_validator=rc2),
            "not frozen CAL V1",
        )
        wrong_resolver_outer, _inner = self.reseal(rc2, successor, outer, policy_resolver_commit_sha=PREDECESSOR_RESOLVER)
        successor_resolver_reason = expect_reject(
            "successor-candidate-wrong-resolver",
            lambda: successor.validate_object(wrong_resolver_outer, rc2_validator=rc2),
            "resolver mismatch",
        )
        weak_outer, weak_inner = self.reseal(rc2, successor, outer, semantic_implementation_sha=PREDECESSOR_SEMANTIC)
        rc2.verify_policy_resolution(
            weak_inner,
            independently_selected_resolver_commit_sha=RESOLVER,
            resolver_entries=successor_resolver["entries"],
        )
        weak_reason = expect_reject(
            "successor-candidate-predecessor-producer",
            lambda: successor.validate_object(weak_outer, rc2_validator=rc2),
            "not frozen CAL V1",
        )
        predecessor_listed_outer, predecessor_listed_inner = self.reseal(
            rc2,
            predecessor,
            outer,
            policy_resolver_commit_sha=PREDECESSOR_RESOLVER,
        )
        del predecessor_listed_outer
        predecessor_list_reason = expect_reject(
            "predecessor-resolver-list",
            lambda: rc2.verify_policy_resolution(
                predecessor_listed_inner,
                independently_selected_resolver_commit_sha=PREDECESSOR_RESOLVER,
                resolver_entries=predecessor_resolver["entries"],
            ),
            "unknown or ambiguous implementation",
        )
        row = {
            "predecessor_candidate_rejects_new_producer": True,
            "predecessor_reason": predecessor_reason,
            "successor_candidate_rejects_predecessor_resolver": True,
            "successor_resolver_reason": successor_resolver_reason,
            "resolver_membership_accepts_predecessor_producer": True,
            "candidate_pin_rejects_predecessor_producer": True,
            "weak_path_reason": weak_reason,
            "predecessor_resolver_rejects_new_producer": True,
            "predecessor_list_reason": predecessor_list_reason,
            "false_accepts": 0,
        }
        save(self.root / "negative-controls/authority-controls.json", row)
        return row

    def execute(self) -> None:
        self.load_source()
        executions = {}
        attributions = {}
        for case in self.source.CASES:
            executions[case.case_id] = self.case(case)
            attributions[case.case_id] = executions[case.case_id]["attribution"]
        repeat = self.case(self.source.CASES[0], "-REPEAT")
        base = executions["PIPE01"]
        for label, left, right in (
            ("parent", base["cal_out"] / "parent-result.json", repeat["cal_out"] / "parent-result.json"),
            ("contract_c", base["cal_out"] / "contract-c.json", repeat["cal_out"] / "contract-c.json"),
            ("contract_d", base["d_path"], repeat["d_path"]),
        ):
            if left.read_bytes() != right.read_bytes():
                raise ScientificFailure(f"PIPE01 repeat {label} bytes differ")
        polarity = self.polarity_case()
        controls = {
            "replay": self.attack(executions["PIPE01"], executions["PIPE03"]),
            "conformance_stop": self.conformance_stop(),
            "authority": self.authority_controls(executions["PIPE01"]),
        }
        self.receipt["negative_controls"] = controls
        self.receipt["determinism"] = {"PIPE01_repeat_byte_equal": True}
        self.verify()
        result = {
            "schema": "cal-polarity-successor-downstream-result-v1",
            "disposition": SUPPORTED,
            "apparatus": self.receipt["apparatus"],
            "subjects": self.receipt["subjects"],
            "attributions": attributions,
            "polarity": polarity["record"],
            "determinism": self.receipt["determinism"],
            "negative_controls": controls,
            "cal_semantic_implementation": SEMANTIC,
            "component_implementations_changed": False,
            "authorization_performed": False,
            "execution_performed": False,
            "pending_review_dispatch_tested": False,
            "fresh_blind_accuracy_claim": False,
            "old_new_contract_c_byte_identity_required": False,
        }
        save(self.root / "result.json", result)
        self.receipt.update(
            status="completed",
            disposition=SUPPORTED,
            completed_at=datetime.now(UTC).isoformat(),
            result_sha256=digest((self.root / "result.json").read_bytes()),
        )
        self.checkpoint()

    def fail(self, exc: BaseException) -> int:
        kind = type(exc).__name__
        if isinstance(exc, SubjectUnavailable):
            disposition = BLOCKED
        elif isinstance(exc, ApparatusInvalid):
            disposition = INVALID
        elif isinstance(exc, ScientificFailure):
            disposition = FALSIFIED
        else:
            disposition = INVALID if self.receipt.get("decisive_exposure") else BLOCKED
        self.receipt.update(
            status="failed",
            disposition=disposition,
            error_type=kind,
            error=str(exc),
            failed_at=datetime.now(UTC).isoformat(),
        )
        self.checkpoint()
        (self.root / "first-failure.txt").write_text(f"{disposition}\n{kind}: {exc}\n", encoding="utf-8")
        print(f"{disposition}: {exc}", file=sys.stderr)
        return 2 if disposition == FALSIFIED else 3


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--subjects-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--python", required=True)
    parser.add_argument("--node", required=True)
    args = parser.parse_args()
    runner = Runner(args)
    try:
        runner.verify()
        runner.prepare()
        runner.execute()
    except Exception as exc:
        return runner.fail(exc)
    print(runner.receipt["disposition"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
