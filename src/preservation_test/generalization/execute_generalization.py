"""Execute declared routes once, preserving evidence and refusing mixed runs."""

import argparse
from datetime import UTC, datetime
import json
import os
from pathlib import Path
import platform
import signal
import subprocess
import sys
import time
import tomllib
from typing import Any

from preservation_test.generalization.freeze_02 import (
    PLAN,
    RECORD,
    ROOT,
    contained,
    verify_06_freeze_02,
)
from preservation_test.generalization.utils.hashing import sha256_file
from preservation_test.generalization.verification.verify_04_transformations_utils import (
    verify_converters,
    verify_execution_config,
    verify_matrix,
    verify_routes,
    verify_target_validator,
)
from preservation_test.generalization.verification.verify_hashes import verify_file_hash

PATH_FIELDS = (
    "target_path",
    "validation_path",
    "evaluation_path",
    "log_path",
    "validation_log_path",
    "evaluation_log_path",
    "execution_path",
)


def utc() -> str:
    """Return a timezone-qualified UTC timestamp."""
    return datetime.now(UTC).isoformat()


def write_json(path: Path, data: Any, *, exclusive: bool = False) -> None:
    """Write UTF-8 evidence atomically; initial records use exclusive creation."""
    path.parent.mkdir(parents=True, exist_ok=True)

    if exclusive:
        with path.open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(data, handle, indent=2)
            handle.write("\n")
        return

    temporary = path.with_suffix(path.suffix + ".pending")

    with temporary.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(data, handle, indent=2)
        handle.write("\n")

    temporary.replace(path)


def environment(root: Path, plan: dict[str, Any]) -> dict[str, str]:
    """Build a small environment without inheriting converter or Java options."""
    env = {
        key: os.environ[key]
        for key in (
            "SystemRoot",
            "WINDIR",
            "TEMP",
            "TMP",
            "TMPDIR",
            "HOME",
            "USERPROFILE",
            "APPDATA",
            "LOCALAPPDATA",
            "XDG_CONFIG_HOME",
            "XDG_CONFIG_DIRS",
        )
        if key in os.environ
    }

    system = os.environ.get("SystemRoot", r"C:\Windows")
    env["PATH"] = str(Path(system) / "System32") if os.name == "nt" else "/usr/bin:/bin"
    env["SYFT_CHECK_FOR_APP_UPDATE"] = "false"

    for converter in plan["converter"]:
        if runtime := converter.get("runtime_artifact_path"):
            env["JAVA_HOME"] = str(contained(root, runtime).parent.parent)

    return env


def check_syft_config(root: Path, env: dict[str, str]) -> dict[str, Any]:
    """Refuse local and standard user/XDG Syft configuration files."""
    directories = {root}
    home = Path(env.get("USERPROFILE") or env.get("HOME") or Path.home())

    directories.update((home, Path(env.get("XDG_CONFIG_HOME", str(home / ".config")))))

    for key in ("APPDATA", "LOCALAPPDATA"):
        if key in env:
            directories.add(Path(env[key]))

    directories.update(
        Path(p)
        for p in env.get(
            "XDG_CONFIG_DIRS",
            "/etc/xdg" if os.name != "nt" else "",
        ).split(os.pathsep)
        if p
    )

    checked: list[str] = []
    found: list[str] = []

    for directory in sorted(directories):
        for pattern in (".syft.*", ".syft/config.*", "syft/config.*"):
            checked.append(str(directory / pattern))
            found.extend(str(p) for p in directory.glob(pattern) if p.is_file())

    if found:
        raise ValueError(
            "external Syft configuration must be removed "
            f"from execution context: {found}"
        )

    return {"checked": checked, "found": found}


def invoke(
    argv: list[str],
    root: Path,
    env: dict[str, str],
    timeout: int,
    log: Path,
    stdout_file: Path | None = None,
) -> dict[str, Any]:
    """Capture both streams, including failures/timeouts, and terminate descendants."""
    start = time.monotonic()

    result: dict[str, Any] = {
        "argv": argv,
        "started_utc": utc(),
        "exit_code": None,
        "timeout": False,
        "launch_error": None,
    }

    stdout = stderr = b""

    try:
        process: subprocess.Popen[bytes] = subprocess.Popen(
            argv,
            cwd=root,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False,
            start_new_session=os.name != "nt",
            creationflags=(
                subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
            ),
        )

        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            result["timeout"] = True

            if os.name == "nt":
                subprocess.run(
                    [
                        str(Path(env["SystemRoot"]) / "System32/taskkill.exe"),
                        "/PID",
                        str(process.pid),
                        "/T",
                        "/F",
                    ],
                    capture_output=True,
                    check=False,
                )
            else:
                os.killpg(process.pid, signal.SIGKILL)

            stdout, stderr = process.communicate()

        result["exit_code"] = process.returncode

    except OSError as error:
        result["launch_error"] = str(error)

    log.parent.mkdir(parents=True, exist_ok=True)

    with log.open("xb") as handle:
        handle.write(b"[stdout]\n" + stdout + b"\n[stderr]\n" + stderr)

    if stdout_file is not None:
        with stdout_file.open("xb") as handle:
            handle.write(stdout)

    result.update(
        ended_utc=utc(),
        duration_seconds=time.monotonic() - start,
    )

    return result


def successful(step: dict[str, Any]) -> bool:
    """Return whether a subprocess completed successfully."""
    return (
        step["exit_code"] == 0 and not step["timeout"] and step["launch_error"] is None
    )


def validate_plan(root: Path, plan: dict[str, Any]) -> None:
    """Validate paths, artifact identities, matrix, and evidence uniqueness."""
    cfg = verify_execution_config(plan["transformations"])
    results = contained(root, cfg.results_directory)
    contained(root, cfg.run_manifest_path)

    sources: dict[str, tuple[str, str]] = {}

    for route in plan["route"]:
        source = (route["source_path"], route["source_sha256"])
        previous = sources.setdefault(route["study_id"], source)

        if previous != source:
            raise ValueError("inconsistent route source identity")

        verify_file_hash(root, *source, label="source")

        for field in PATH_FIELDS:
            path = contained(root, route[field])

            if not path.resolve().is_relative_to(results.resolve()):
                raise ValueError("route evidence escapes results root")

    converters = verify_converters(root, plan)

    for converter in plan["converter"]:
        contained(root, converter["artifact_path"])

        if runtime := converter.get("runtime_artifact_path"):
            contained(root, runtime)

    contained(root, plan["target_validator"]["artifact_path"])
    validator = verify_target_validator(root, plan)

    summary = verify_routes(
        root,
        plan["route"],
        sources,
        converters,
        validator,
        cfg.results_directory,
    )

    verify_matrix(
        plan["transformations"],
        sources,
        set(converters),
        summary,
    )

    evidence = {
        contained(root, r[field]).resolve()
        for r in plan["route"]
        for field in PATH_FIELDS
    }

    if contained(root, cfg.run_manifest_path).resolve() in evidence:
        raise ValueError("run manifest collides with route evidence")


def run_route(
    root: Path,
    plan: dict[str, Any],
    route: dict[str, Any],
    env: dict[str, str],
    *,
    attempt: int = 1,
) -> dict[str, Any]:
    """Run one planned route; retain independent validation and evaluation results."""
    verify_file_hash(
        root,
        route["source_path"],
        route["source_sha256"],
        label="route source",
    )
    verify_converters(root, plan)
    verify_target_validator(root, plan)

    paths = {k: contained(root, route[k]) for k in PATH_FIELDS}

    if any(p.exists() for p in paths.values()):
        raise ValueError(f"refusing existing route evidence: {route['route_id']}")

    for path in paths.values():
        path.parent.mkdir(parents=True, exist_ok=True)

    record: dict[str, Any] = {
        "route_id": route["route_id"],
        "attempt": attempt,
        "status": "started",
        "started_utc": utc(),
        "source_sha256": route["source_sha256"],
        "converter": next(
            c for c in plan["converter"] if c["id"] == route["converter_id"]
        ),
        "cwd": str(root),
        "environment": env,
        "evidence_paths": {k: route[k] for k in PATH_FIELDS},
        "validation_outcome": "not_attempted",
        "evaluation_outcome": "not_attempted",
    }

    write_json(paths["execution_path"], record, exclusive=True)
    timeout = plan["transformations"]["timeout_seconds"]

    record["transformation"] = invoke(
        route["command_argv"],
        root,
        env,
        timeout,
        paths["log_path"],
    )

    if paths["target_path"].is_file():
        record["target_sha256"] = sha256_file(paths["target_path"])

    record["execution_outcome"] = (
        "completed"
        if successful(record["transformation"]) and paths["target_path"].is_file()
        else "execution_failure"
    )

    write_json(paths["execution_path"], record)

    if record["execution_outcome"] == "completed":
        step = invoke(
            route["validation_command_argv"],
            root,
            env,
            timeout,
            paths["validation_log_path"],
        )

        record["validation"] = step

        valid_exit = (
            step["exit_code"] in (0, 2)
            and not step["timeout"]
            and step["launch_error"] is None
            and paths["validation_path"].is_file()
        )

        record["validation_outcome"] = (
            ("valid" if step["exit_code"] == 0 else "invalid")
            if valid_exit
            else "validation_error"
        )

        write_json(paths["execution_path"], record)

        argv = [
            sys.executable,
            "-m",
            "preservation_test.evaluator.evaluate",
            route["source_path"],
            route["target_path"],
            "--json",
            "--commitment-file",
            "contracts/commitments.toml",
            "--commitment-id",
            "purl_preservation_v1",
        ]

        step = invoke(
            argv,
            root,
            env,
            timeout,
            paths["evaluation_log_path"],
            paths["evaluation_path"],
        )

        record["evaluation"] = step
        record["evaluation_outcome"] = (
            "completed" if successful(step) else "evaluation_error"
        )

        if successful(step):
            try:
                report = json.loads(
                    paths["evaluation_path"].read_text(encoding="utf-8")
                )

                if not isinstance(report.get("results"), list):
                    raise TypeError("evaluator returned no results array")

            except (ValueError, AttributeError, TypeError) as error:
                record["evaluation_outcome"] = "evaluation_error"
                record["evaluation_error"] = str(error)

    record.update(status="finished", ended_utc=utc())
    write_json(paths["execution_path"], record)

    return record


def execute(root: Path, plan_path: Path, *, engineering: bool = False) -> Path:
    """Execute an empty declared results tree, refusing formal inputs in engineering mode."""
    root = root.resolve()
    plan_path = plan_path.resolve()

    if not plan_path.is_relative_to(root):
        raise ValueError("plan must be inside repository")

    with plan_path.open("rb") as handle:
        plan = tomllib.load(handle)

    cfg = plan["transformations"]
    results = contained(root, cfg["results_directory"])
    formal_results = root / "generalization/results"

    if engineering:
        if (
            plan_path == root / PLAN
            or results.resolve().is_relative_to(formal_results.resolve())
            or formal_results.resolve().is_relative_to(results.resolve())
        ):
            raise ValueError("engineering mode refuses the formal plan/results")

        for route in plan["route"]:
            if not contained(root, route["source_path"]).is_relative_to(
                root / "validation"
            ):
                raise ValueError("engineering sources must be under validation/")

        freeze_digest = None

    else:
        if plan_path != root / PLAN or results != formal_results:
            raise ValueError("formal mode requires the real plan/results")

        if platform.system() != "Windows" or platform.machine().lower() not in (
            "amd64",
            "x86_64",
        ):
            raise ValueError(
                "formal execution requires the declared Windows x64 platform"
            )

        freeze_digest = verify_06_freeze_02(root)

        subprocess.run(
            ["git", "diff", "--exit-code", "HEAD", "--", RECORD],
            cwd=root,
            check=True,
            capture_output=True,
        )

        pinned = (root / ".python-version").read_text().strip()

        if not platform.python_version().startswith(pinned + "."):
            raise ValueError("interpreter does not match .python-version")

    validate_plan(root, plan)

    if (
        cfg.get("execution_state") != "not_started"
        or cfg.get("transformation_outputs_examined") is not False
    ):
        raise ValueError("plan is not pre-execution")

    if results.exists() and any(results.iterdir()):
        raise ValueError(
            "results already exist; interrupted or completed runs are not resumed"
        )

    env = environment(root, plan)
    config_check = check_syft_config(root, env)
    manifest_path = contained(root, cfg["run_manifest_path"])

    manifest: dict[str, Any] = {
        "mode": "engineering" if engineering else "formal",
        "status": "started",
        "started_utc": utc(),
        "plan_sha256": sha256_file(plan_path),
        "freeze_02_sha256": freeze_digest,
        "python": platform.python_version(),
        "interpreter": sys.executable,
        "platform": platform.platform(),
        "system": platform.system(),
        "architecture": platform.machine(),
        "syft_config_check": config_check,
        "environment": env,
        "routes": [],
        "repository_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            text=True,
        ).strip(),
    }

    write_json(manifest_path, manifest, exclusive=True)

    try:
        if any(c["id"] == "syft" for c in plan["converter"]):
            converter = next(c for c in plan["converter"] if c["id"] == "syft")

            step = invoke(
                [converter["artifact_path"], "config", "--load"],
                root,
                env,
                cfg["timeout_seconds"],
                results / "syft-config.log",
            )

            manifest["syft_effective_config"] = step

            if not successful(step):
                raise ValueError("Syft effective configuration could not be captured")

        for route in plan["route"]:
            if route["status"] == "unsupported_pre_execution":
                manifest["routes"].append(
                    {
                        "route_id": route["route_id"],
                        "outcome": "unsupported_pre_execution",
                    }
                )
            else:
                if not engineering:
                    verify_06_freeze_02(root)

                record = run_route(root, plan, route, env)

                manifest["routes"].append(
                    {
                        "route_id": route["route_id"],
                        "execution_path": route["execution_path"],
                        "execution_outcome": record["execution_outcome"],
                    }
                )

            write_json(manifest_path, manifest)

        manifest["status"] = "finished"

    except BaseException as error:
        manifest.update(
            status="interrupted",
            error=f"{type(error).__name__}: {error}",
        )
        raise

    finally:
        manifest["ended_utc"] = utc()
        write_json(manifest_path, manifest)

    return manifest_path


def main() -> None:
    """Run a frozen formal plan or explicitly separate engineering plan."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engineering", action="store_true")
    parser.add_argument("--plan", type=Path, default=Path(PLAN))
    args = parser.parse_args()

    print(
        execute(
            ROOT,
            ROOT / args.plan,
            engineering=args.engineering,
        )
    )


if __name__ == "__main__":
    main()
