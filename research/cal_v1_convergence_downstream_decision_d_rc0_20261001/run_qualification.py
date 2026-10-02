"""Issue 158 frozen operational runner; executes real installed/external engines.

Owns apparatus only. PR123's source remains byte-exact. The wrapper adds the
author/conform gate and byte discriminators; it never adapts semantic results.
No Authorization, Contract E, pending-review dispatch, or execution surface exists.
"""

from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import traceback
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
APPARATUS = HERE.parent.parent
SEMANTIC = "847cc970642bb648dc994b929c2053b5c9d4648c"
SUPPORTED = "SUPPORTED_EXACT_CAL_CONVERGENCE_DOWNSTREAM_EQUIVALENCE"
FALSIFIED = "FALSIFIED_EXACT_CAL_CONVERGENCE_DOWNSTREAM_EQUIVALENCE"
INVALID = "INCONCLUSIVE_APPARATUS_INVALID"
BLOCKED = "BLOCKED_EXACT_SUBJECT_UNAVAILABLE"


class SubjectUnavailable(RuntimeError):
    pass


class EquivalenceFailure(RuntimeError):
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
    path.write_bytes(canonical(value))


def compare_files(left: Path, right: Path, label: str) -> dict[str, Any]:
    a, b = left.read_bytes(), right.read_bytes()
    row = {
        "label": label,
        "a_sha256": digest(a),
        "b_sha256": digest(b),
        "a_bytes": len(a),
        "b_bytes": len(b),
        "byte_equal": a == b,
    }
    if a != b:
        raise EquivalenceFailure(json.dumps(row, sort_keys=True))
    return row


def compare_sets(left: Path, right: Path, label: str) -> dict[str, Any]:
    a = {p.relative_to(left).as_posix(): p for p in left.rglob("*") if p.is_file()}
    b = {p.relative_to(right).as_posix(): p for p in right.rglob("*") if p.is_file()}
    if not a or a.keys() != b.keys():
        raise EquivalenceFailure(
            f"{label}: artifact-set mismatch: {sorted(a)} / {sorted(b)}"
        )
    return {
        "label": label,
        "file_count": len(a),
        "byte_equal": True,
        "files": [compare_files(a[k], b[k], k) for k in sorted(a)],
    }


class Runner:
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.root = args.run_root.resolve()
        self.subject_root = args.subjects_root.resolve()
        self.subjects = json.loads((HERE / "SUBJECTS.json").read_bytes())
        self.env = os.environ.copy()
        self.env.pop("PYTHONPATH", None)
        self.env.update(
            PYTHONNOUSERSITE="1",
            PYTHONHASHSEED="0",
            TZ="UTC",
            UV_CACHE_DIR=str(self.root.parent / "uv-cache"),
        )
        self.phase = "preflight"
        self.arm = "A"
        self.negative = False
        self.current_root: Path | None = None
        if args.worker:
            self.receipt = json.loads((self.root / "receipt.json").read_bytes())
            if self.receipt["status"] != "runtime_prepared":
                raise RuntimeError("worker cannot resume an exposed or incomplete run")
        else:
            self.root.mkdir(parents=True, exist_ok=False)
            (self.root / "commands").mkdir()
            self.receipt = {
                "schema": "cal-convergence-downstream-receipt-v1",
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
            "stdin_sha256": digest(input_text.encode())
            if input_text is not None
            else None,
        }
        self.receipt["commands"].append(row)
        self.checkpoint()
        p = subprocess.run(
            args,
            cwd=cwd,
            env=env or self.env,
            input=input_text.encode() if input_text is not None else None,
            capture_output=True,
            check=False,
        )
        log.with_suffix(".stdout").write_bytes(p.stdout)
        log.with_suffix(".stderr").write_bytes(p.stderr)
        row.update(
            actual_exit=p.returncode,
            stdout_sha256=digest(p.stdout),
            stderr_sha256=digest(p.stderr),
            stdout_bytes=len(p.stdout),
            stderr_bytes=len(p.stderr),
            log_stem=f"commands/{stem}",
        )
        self.checkpoint()
        if p.returncode != expected:
            raise RuntimeError(
                f"{self.phase}/{label}: exit {p.returncode}, expected {expected}; "
                f"{p.stderr.decode(errors='replace')}"
            )
        return subprocess.CompletedProcess(
            args, p.returncode, p.stdout.decode(), p.stderr.decode()
        )

    def git(self, root: Path, *args: str) -> str:
        return self.command(
            ["git", "-C", str(root), *args], label="identity"
        ).stdout.strip()

    def verify(self) -> None:
        self.phase = "identity"
        freeze = json.loads((HERE / "EXPERIMENT.json").read_bytes())
        for name, expected in freeze["frozen_files"].items():
            if digest((HERE / name).read_bytes()) != expected:
                raise SubjectUnavailable(f"frozen apparatus file changed: {name}")
        base = self.subjects["apparatus_base"]
        self.git(APPARATUS, "merge-base", "--is-ancestor", base, "HEAD")
        self.git(
            APPARATUS, "merge-base", "--is-ancestor", freeze["source_commit"], "HEAD"
        )
        if (
            self.git(APPARATUS, "rev-parse", f"{freeze['source_commit']}^{{tree}}")
            != freeze["source_tree"]
        ):
            raise SubjectUnavailable("frozen apparatus source tree mismatch")
        changed = self.git(APPARATUS, "diff", "--name-only", base, "HEAD").splitlines()
        if any(
            not (
                p.startswith(
                    "research/cal_v1_convergence_downstream_decision_d_rc0_20261001/"
                )
                or p
                == ".github/workflows/cal-v1-convergence-downstream-decision-d-rc0.yml"
            )
            for p in changed
        ):
            raise SubjectUnavailable(
                "apparatus delta changes a component or historical experiment"
            )
        if self.git(APPARATUS, "status", "--porcelain", "--untracked-files=no"):
            raise SubjectUnavailable("apparatus tracked tree is dirty")
        head = self.git(APPARATUS, "rev-parse", "HEAD")
        tree = self.git(APPARATUS, "rev-parse", "HEAD^{tree}")
        self.receipt.setdefault(
            "apparatus",
            {
                "head": head,
                "tree": tree,
                "base": base,
                "frozen_source": freeze["source_commit"],
                "frozen_source_tree": freeze["source_tree"],
                "frozen_files": freeze["frozen_files"],
                "harness_blob": self.git(
                    APPARATUS, "hash-object", str(HERE / "run_qualification.py")
                ),
            },
        )
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
                raise SubjectUnavailable(
                    f"subject identity/clean-tree mismatch: {name}"
                )
            for rel, expected in authority["blobs"].items():
                if blob((path / rel).read_bytes()) != expected:
                    raise SubjectUnavailable(
                        f"protected working blob mismatch: {name}/{rel}"
                    )
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
                or self.git(path, "rev-parse", f"refs/tags/{tag['name']}^{{}}")
                != self.subjects["subjects"][name]["commit"]
            ):
                raise SubjectUnavailable(f"released tag mismatch: {name}")
        for rel, expected in self.subjects["trusted_targets"].items():
            if digest((HERE / rel).read_bytes()) != expected:
                raise SubjectUnavailable(f"trusted target bytes changed: {rel}")
        self.receipt["subjects"] = observed
        self.checkpoint()

    def prepare(self) -> None:
        self.phase = "build-and-clean-install"
        version = self.command(
            [self.args.python, "--version"], label="python-version"
        ).stdout
        if not version.startswith("Python 3.11."):
            raise RuntimeError(
                "apparatus requires the PR123 Python 3.11 runtime pattern"
            )
        node = self.command([self.args.node, "--version"], label="node-version").stdout
        if not node.startswith("v22."):
            raise RuntimeError("apparatus requires the PR123 Node 22 runtime pattern")
        self.receipt["runtime"] = {"python": version.strip(), "node": node.strip()}
        builder = self.root / "build-env"
        self.command(
            ["uv", "venv", "--python", self.args.python, str(builder)],
            label="builder-venv",
        )
        build_py = str(builder / "bin/python")
        self.command(
            ["uv", "pip", "install", "--python", build_py, "build==1.3.0"],
            label="build-dependency",
        )
        for arm in ("A", "B"):
            subject = self.subject_root / f"cal-{arm.lower()}"
            dist = self.root / f"dist-{arm}"
            self.command(
                [
                    build_py,
                    "-m",
                    "build",
                    "--wheel",
                    "--outdir",
                    str(dist),
                    str(subject),
                ],
                label=f"wheel-{arm}",
            )
            wheels = list(dist.glob("*.whl"))
            if len(wheels) != 1:
                raise RuntimeError("expected one exact CAL wheel")
            wheel = wheels[0]
            checked = 0
            with zipfile.ZipFile(wheel) as z:
                for rel, expected in self.subjects["subjects"][f"cal-{arm.lower()}"][
                    "blobs"
                ].items():
                    if rel.startswith("src/claim_audit_lab/"):
                        if blob(z.read(rel[4:])) != expected:
                            raise SubjectUnavailable(
                                f"packaged source bytes differ: {arm}/{rel}"
                            )
                        checked += 1
            env_path = self.root / f"env-{arm}"
            py = str(env_path / "bin/python")
            self.command(
                ["uv", "venv", "--python", self.args.python, str(env_path)],
                label=f"clean-venv-{arm}",
            )
            # PR123 uses the pinned EB source. Its deterministic v1 import path needs
            # rank-bm25; unused embedding/PDF execution is outside this three-case path.
            self.command(
                [
                    "uv",
                    "pip",
                    "install",
                    "--python",
                    py,
                    str(wheel),
                    "rfc8785==0.1.4",
                    "rank-bm25==0.2.2",
                ],
                label=f"clean-install-{arm}",
            )
            footprint = self.command(
                ["uv", "pip", "freeze", "--python", py],
                label=f"dependency-footprint-{arm}",
            ).stdout
            (self.root / f"dependencies-{arm}.txt").write_text(footprint)
            versions = self.command(
                ["uv", "pip", "list", "--python", py, "--format", "json"],
                label=f"dependency-versions-{arm}",
            ).stdout
            save(self.root / f"dependency-versions-{arm}.json", json.loads(versions))
            inspection = self.command(
                [str(env_path / "bin/claim-audit-v1"), "inspect", "--json"],
                label=f"installed-inspect-{arm}",
            )
            inspect_value = json.loads(inspection.stdout)
            if inspect_value["semantic_implementation_sha"] != SEMANTIC:
                raise SubjectUnavailable(f"installed semantic identity mismatch: {arm}")
            save(self.root / f"installed-inspect-{arm}.json", inspect_value)
            program = "import json,claim_audit_lab; from pathlib import Path; p=Path(claim_audit_lab.__file__).resolve(); print(json.dumps({'module':str(p),'prefix':str(Path(__import__('sys').prefix).resolve())}))"
            provenance = json.loads(
                self.command(
                    [py, "-c", program], label=f"installed-provenance-{arm}"
                ).stdout
            )
            if not Path(provenance["module"]).is_relative_to(env_path.resolve()):
                raise SubjectUnavailable(
                    f"CAL import is not from clean wheel environment: {arm}"
                )
            self.receipt.setdefault("builds", {})[arm] = {
                "wheel": str(wheel.relative_to(self.root)),
                "sha256": digest(wheel.read_bytes()),
                "source_blobs_checked": checked,
                "clean_installed": True,
                "module_provenance": provenance,
            }
        compare_files(
            self.root / "dependency-versions-A.json",
            self.root / "dependency-versions-B.json",
            "dependency-versions",
        )
        self.receipt["status"] = "runtime_prepared"
        self.checkpoint()

    def load_source(self) -> None:
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
            CAL_PARENT_CLI=str(self.root / "env-A/bin/claim-audit-v1-parent"),
            PYTHON=str(self.root / "env-A/bin/python"),
            NODE=self.args.node,
            COMPOSITION_ROOT=str(self.root / "worlds"),
        )
        spec = importlib.util.spec_from_file_location(
            "preserved_pr123", HERE / "source_pr123.py"
        )
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        self.source = module
        expected = self.subjects["cases"]
        observed = [
            {
                "case_id": c.case_id,
                "c1_source": c.c1_source,
                "admit_c2": c.admit_c2,
                "parent": c.expected_parent,
                "decision": c.expected_decision,
                "consumer": c.expected_consumer,
            }
            for c in module.CASES
        ]
        if expected != observed:
            raise SubjectUnavailable(
                "PR123 case definitions disagree with frozen expectations"
            )
        for child in ("C1", "C2"):
            if (
                module.canonical_json_bytes(module.target(child))
                != (HERE / "trusted-targets" / f"{child}.target.json").read_bytes()
            ):
                raise SubjectUnavailable(
                    "preserved PR123 targets differ from frozen trusted inputs"
                )
        module.run_checked = self.run_checked

    def gate_children(self, args: list[str]) -> list[str]:
        bundle = args[3]
        root = Path(args[args.index("--out-dir") + 1]).parent
        env_path = self.root / f"env-{self.arm}"
        selected: dict[str, Path] = {}
        new_args = list(args)
        for i, value in enumerate(args):
            if value != "--target":
                continue
            child, old = args[i + 1].split("=", 1)
            trusted = Path(old)
            compare_files(
                HERE / "trusted-targets" / f"{child}.target.json",
                trusted,
                f"{child}-trusted",
            )
            target = trusted
            if self.arm == "B":
                py = str(env_path / "bin/python")
                prefix = [py, "-m", "claim_audit_lab.production_v1.target_cli"]
                authored = self.command(
                    [*prefix, "author", bundle, child], label="target-author"
                )
                target = root / f"{child}.authored.target.json"
                target.write_bytes(authored.stdout.encode())
                compare_files(trusted, target, f"{child}-authored-trusted")
                if self.negative and child == "C1":
                    mutated = json.loads(target.read_bytes())
                    mutated["proposition"]["fields"]["comparison_direction"] = (
                        "LESS_THAN"
                    )
                    target = root / "C1.drift.target.json"
                    target.write_bytes(self.source.canonical_json_bytes(mutated))
                    self.command(
                        [
                            str(env_path / "bin/claim-audit-v1"),
                            "validate-bundle",
                            bundle,
                            str(target),
                        ],
                        label="structural-weak",
                    )
                conform = self.command(
                    [*prefix, "conform", bundle, str(target)],
                    label="target-conformance",
                    expected=2 if self.negative else 0,
                )
                if self.negative:
                    if conform.stdout or "conform rejected:" not in conform.stderr:
                        raise RuntimeError(
                            "negative conformance did not reach the intended semantic rejection"
                        )
                    save(
                        root / "conformance-stop.json",
                        {
                            "structural_accepted": True,
                            "conformance_rejected": True,
                            "mutation": "strict_direction_disagrees_with_claim",
                        },
                    )
                    raise ConformanceStop(
                        "candidate conformance stopped the orchestrated arm"
                    )
                save(root / f"{child}.conformance.json", json.loads(conform.stdout))
                new_args[i + 1] = f"{child}={target}"
            selected[child] = target
        if set(selected) != {"C1", "C2"}:
            raise RuntimeError(
                "complete target gate required before any child execution"
            )
        for child, target in selected.items():
            out = root / "explicit-children" / child
            self.command(
                [
                    str(env_path / "bin/claim-audit-v1"),
                    "run-bundle",
                    bundle,
                    str(target),
                    "--out-dir",
                    str(out),
                ],
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
        elif len(args) > 1 and args[1].endswith(
            "decision-engine-parent-bound-evaluate.mjs"
        ):
            label = "decision"
        elif len(args) > 2 and "validators.contract_d_consume" in args[2]:
            label = "contract-d-consumer"
        result = self.command(
            args, label=label, cwd=cwd, env=env, input_text=input_text
        )
        if label == "contract-d-consumer":
            assert self.current_root is not None
            (self.current_root / "contract-d-consumer.json").write_bytes(
                result.stdout.encode()
            )
        return result

    def case(self, case: Any, arm: str, suffix: str = "") -> dict[str, Any]:
        self.arm = arm
        self.phase = f"{arm}/{case.case_id}{suffix}"
        self.receipt["decisive_exposure"] = True
        self.checkpoint()
        self.current_root = self.root / "worlds" / arm / f"{case.case_id}{suffix}"
        self.source.CAL_CLI = self.root / f"env-{arm}/bin/claim-audit-v1-parent"
        start = len(self.receipt["commands"])
        try:
            execution = self.source.execute_case(case, self.current_root)
        except RuntimeError as exc:
            if (
                ": expected parent " in str(exc)
                or ": expected Decision " in str(exc)
                or ": expected Contract D consumer " in str(exc)
            ):
                raise EquivalenceFailure(str(exc)) from exc
            raise
        execution["root"] = self.current_root
        save(self.current_root / "eb-native-package.json", execution["package"])
        for child in ("C1", "C2"):
            compare_sets(
                self.current_root / "explicit-children" / child,
                execution["cal_out"] / "children" / child,
                f"{arm}-{child}-explicit-parent",
            )
        # Require preserved canonical materialized file bytes to equal actual CLI stdout.
        decision_rows = [
            r for r in self.receipt["commands"][start:] if r["label"] == "decision"
        ]
        if len(decision_rows) != 1:
            raise RuntimeError("one maintained Decision invocation required per case")
        cli_stdout = self.root / (decision_rows[0]["log_stem"] + ".stdout")
        compare_files(cli_stdout, execution["d_path"], "canonical-Decision-D-stdout")
        d = json.loads(execution["d_bytes"])
        if "epistemic_audit.stage_pending_review@1" in json.dumps(d):
            raise EquivalenceFailure(
                "prohibited pending-review effect reached Contract D"
            )
        for child in ("C1", "C2"):
            native = json.loads(
                (execution["cal_out"] / "children" / child / "result.json").read_bytes()
            )
            if native["semantic_implementation_sha"] != SEMANTIC:
                raise SubjectUnavailable("native semantic identity mismatch")
        self.receipt["cases"][f"{arm}/{case.case_id}{suffix}"] = execution["record"]
        self.checkpoint()
        print(f"completed {arm}/{case.case_id}{suffix}", flush=True)
        return execution

    def paired(self, a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
        ar, br = a["root"], b["root"]
        row = {"targets": {}, "native_children": {}, "explicit_children": {}}
        for child in ("C1", "C2"):
            row["targets"][child] = compare_files(
                ar / f"{child}.target.json", br / f"{child}.authored.target.json", child
            )
            row["native_children"][child] = compare_sets(
                a["cal_out"] / "children" / child,
                b["cal_out"] / "children" / child,
                child,
            )
            row["explicit_children"][child] = compare_sets(
                ar / "explicit-children" / child,
                br / "explicit-children" / child,
                child,
            )
        row["contract_a"] = compare_files(
            ar / "contract-a.json", br / "contract-a.json", "same-Contract-A"
        )
        row["eb_native"] = compare_files(
            ar / "eb-native-package.json",
            br / "eb-native-package.json",
            "same-EB-world",
        )
        row["contract_b"] = compare_sets(
            ar / "eb/contract_b", br / "eb/contract_b", "same-Contract-B-world"
        )
        for name, rel_a, rel_b in (
            (
                "parent",
                a["cal_out"] / "parent-result.json",
                b["cal_out"] / "parent-result.json",
            ),
            (
                "contract_c",
                a["cal_out"] / "contract-c.json",
                b["cal_out"] / "contract-c.json",
            ),
            ("decision_contract_d", a["d_path"], b["d_path"]),
            (
                "contract_d_consumer",
                ar / "contract-d-consumer.json",
                br / "contract-d-consumer.json",
            ),
        ):
            row[name] = compare_files(rel_a, rel_b, name)
        row["contract_c_whole_object_identity"] = a["record"]["contract_c_sha256"]
        if a["record"] != b["record"]:
            raise EquivalenceFailure("paired identity/outcome records differ")
        row["outcomes"] = a["record"]
        row["byte_equal"] = True
        return row

    def attack(self, executions: dict[str, Any], arm: str) -> dict[str, Any]:
        self.phase = f"{arm}/cross-run-replay"
        pipe01, pipe03 = executions["PIPE01"], executions["PIPE03"]
        inputs = copy.deepcopy(pipe01["consumer_inputs"])
        common = next(
            (
                k
                for k in inputs["native_child_results_b64"]
                if k in pipe03["consumer_inputs"]["native_child_results_b64"]
            ),
            None,
        )
        if common is None:
            raise RuntimeError(
                "preserved PR123 replay substitution has no common child"
            )
        inputs["native_child_results_b64"][common] = pipe03["consumer_inputs"][
            "native_child_results_b64"
        ][common]
        if base64.b64decode(
            inputs["native_child_results_b64"][common]
        ) == base64.b64decode(
            pipe01["consumer_inputs"]["native_child_results_b64"][common]
        ):
            raise RuntimeError("cross-run replay control has identical source bytes")
        root = self.root / "negative-controls" / f"replay-{arm}"
        root.mkdir(parents=True)
        path = root / "consumer-inputs.json"
        path.write_bytes(self.source.canonical_json_bytes(inputs))
        args = [
            self.args.node,
            str(
                self.subject_root
                / "decision/scripts/decision-engine-parent-bound-evaluate.mjs"
            ),
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
            str(self.root / "env-A/bin/python"),
        ]
        p = self.command(args, label="decision-replay", expected=1)
        error = json.loads(p.stderr)
        if (
            p.stdout
            or error.get("code") != "contract_c_validation_failed"
            or "NATIVE_RESULT_HASH_MISMATCH" not in error.get("message", "")
        ):
            raise EquivalenceFailure(
                "replay did not reject at the frozen native-byte binding before D output"
            )
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
        self.arm = "B"
        self.negative = True
        self.phase = "B/conformance-stop"
        self.current_root = self.root / "negative-controls/conformance-stop"
        self.source.CAL_CLI = self.root / "env-B/bin/claim-audit-v1-parent"
        start = len(self.receipt["commands"])
        try:
            self.source.execute_case(self.source.CASES[0], self.current_root)
        except ConformanceStop:
            pass
        else:
            raise EquivalenceFailure(
                "conformance drift control reached downstream execution"
            )
        finally:
            self.negative = False
        rows = self.receipt["commands"][start:]
        forbidden = {"cal-child", "cal-parent", "decision", "contract-d-consumer"}
        if any(r["label"] in forbidden for r in rows):
            raise EquivalenceFailure(
                "orchestration invoked a forbidden stage after conformance stop"
            )
        if (
            (self.current_root / "explicit-children").exists()
            or (self.current_root / "cal").exists()
            or list(self.current_root.rglob("contract-c.json"))
            or list(self.current_root.rglob("contract-d.json"))
        ):
            raise EquivalenceFailure("conformance-stop emitted native/C/D bytes")
        row = {
            "structural_accepted": True,
            "conformance_rejected": True,
            "conformance_exit": 2,
            "child_invocations": 0,
            "parent_invocations": 0,
            "decision_invocations": 0,
            "contract_c_emitted": False,
            "contract_d_emitted": False,
            "observed_stage_labels": [r["label"] for r in rows],
            "false_accepts": 0,
            "raw_run_bundle_claim": False,
        }
        save(self.current_root / "control-result.json", row)
        return row

    def execute(self) -> None:
        self.load_source()
        self.receipt["status"] = "active"
        executions: dict[str, dict[str, Any]] = {"A": {}, "B": {}}
        comparisons = {}
        for case in self.source.CASES:
            for arm in ("A", "B"):
                executions[arm][case.case_id] = self.case(case, arm)
            comparisons[case.case_id] = self.paired(
                executions["A"][case.case_id], executions["B"][case.case_id]
            )
            save(self.root / "paired-comparisons.json", comparisons)
        replay = self.case(self.source.CASES[0], "B", "-REPEAT")
        base = executions["B"]["PIPE01"]
        deterministic = {
            "native_children": compare_sets(
                base["cal_out"] / "children",
                replay["cal_out"] / "children",
                "B-PIPE01-native-repeat",
            ),
            "parent": compare_files(
                base["cal_out"] / "parent-result.json",
                replay["cal_out"] / "parent-result.json",
                "B-PIPE01-parent-repeat",
            ),
            "contract_c": compare_files(
                base["cal_out"] / "contract-c.json",
                replay["cal_out"] / "contract-c.json",
                "B-PIPE01-C-repeat",
            ),
            "contract_d": compare_files(
                base["d_path"], replay["d_path"], "B-PIPE01-D-repeat"
            ),
            "passed": True,
        }
        self.receipt["determinism"] = deterministic
        controls = {
            f"replay-{arm}": self.attack(executions[arm], arm) for arm in ("A", "B")
        }
        controls["replay_attack_input_equivalence"] = compare_files(
            self.root / "negative-controls/replay-A/consumer-inputs.json",
            self.root / "negative-controls/replay-B/consumer-inputs.json",
            "paired-replay-attack",
        )
        controls["conformance_stop"] = self.conformance_stop()
        self.receipt["negative_controls"] = controls
        self.verify()
        result = {
            "schema": "cal-convergence-downstream-result-v1",
            "disposition": SUPPORTED,
            "apparatus": self.receipt["apparatus"],
            "subjects": self.receipt["subjects"],
            "comparisons": comparisons,
            "determinism": deterministic,
            "negative_controls": controls,
            "cal_semantic_implementation": SEMANTIC,
            "component_implementations_changed": False,
            "authorization_performed": False,
            "execution_performed": False,
            "pending_review_dispatch_tested": False,
            "fresh_blind_accuracy_claim": False,
        }
        save(self.root / "result.json", result)
        self.receipt.update(
            status="completed",
            disposition=SUPPORTED,
            completed_at=datetime.now(UTC).isoformat(),
            result_sha256=digest((self.root / "result.json").read_bytes()),
        )
        self.checkpoint()
        print(
            json.dumps(
                {
                    "disposition": SUPPORTED,
                    "result_sha256": self.receipt["result_sha256"],
                    "commands": len(self.receipt["commands"]),
                }
            ),
            flush=True,
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--subjects-root", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--python", default="python3.11")
    parser.add_argument("--node", default="node")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    runner = Runner(args)
    try:
        runner.verify()
        if not args.worker:
            runner.prepare()
            command = [
                str(runner.root / "env-A/bin/python"),
                str(Path(__file__).resolve()),
                "--subjects-root",
                str(args.subjects_root.resolve()),
                "--run-root",
                str(args.run_root.resolve()),
                "--python",
                args.python,
                "--node",
                args.node,
                "--worker",
            ]
            os.execve(command[0], command, runner.env)
        runner.execute()
        return 0
    except Exception as exc:
        disposition = (
            BLOCKED
            if isinstance(exc, SubjectUnavailable)
            else FALSIFIED
            if isinstance(exc, EquivalenceFailure)
            else INVALID
        )
        runner.receipt.update(
            status="aborted",
            disposition=disposition,
            first_failure={
                "phase": runner.phase,
                "type": type(exc).__name__,
                "error": str(exc),
            },
            downstream_of_first_failure="NOT_RUN",
            completed_at=datetime.now(UTC).isoformat(),
        )
        (runner.root / "first-failure.txt").write_text(traceback.format_exc())
        runner.checkpoint()
        print(
            json.dumps(
                {"disposition": disposition, "phase": runner.phase, "error": str(exc)}
            ),
            file=sys.stderr,
        )
        return 1 if disposition == FALSIFIED else 2


if __name__ == "__main__":
    raise SystemExit(main())
