"""Prepare/run Windows engineering smoke routes, without reading held-out outputs.

Prepares the smoke test using the two known validation sources,
exercises the converters, and checks the results.
"""

import argparse
import json
from pathlib import Path
import platform
import tomllib
from typing import Any

from preservation_test.generalization.freeze_02 import PLAN, ROOT, SMOKE, contained
from preservation_test.generalization.p04_build_transformations import (
    Converter,
    Source,
    TargetValidator,
    _route,
    _route_row,
)
from preservation_test.generalization.utils.hashing import sha256_file
from preservation_test.generalization.utils.toml_writer import render_document
from preservation_test.generalization.verification.verify_01_freeze_01 import (
    verify_01_freeze_01,
)

SMOKE_PLAN = "validation/executor-smoke/plan.toml"
RESULTS = "validation/executor-smoke/results"


def code_hashes(root: Path) -> dict[str, str]:
    """Identify the executor and integrity implementation used for smoke validation."""
    return {
        p.relative_to(root).as_posix(): sha256_file(p)
        for p in sorted((root / "src/preservation_test/generalization").rglob("*.py"))
    }


def prepare(root: Path) -> Path:
    """Build a separate plan using known validation sources and pinned tools."""
    verify_01_freeze_01(root)
    out = contained(root, SMOKE_PLAN)

    if out.exists():
        raise ValueError(
            "smoke plan exists; preserve it before preparing another attempt"
        )

    with contained(root, PLAN).open("rb") as handle:
        formal = tomllib.load(handle)

    converters = tuple(
        Converter(
            converter_id=c["id"],
            name=c["name"],
            version=c["version"],
            artifact_path=root / c["artifact_path"],
            artifact_sha256=c["artifact_sha256"],
            documentation=c.get("documentation", ""),
            runtime=c["runtime"],
            runtime_artifact_path=(
                root / c["runtime_artifact_path"]
                if c.get("runtime_artifact_path")
                else None
            ),
            runtime_version=c.get("runtime_version", ""),
            runtime_sha256=c.get("runtime_sha256", ""),
        )
        for c in formal["converter"]
    )

    v = formal["target_validator"]

    validator = TargetValidator(
        v["name"],
        v["version"],
        root / v["artifact_path"],
        v["artifact_sha256"],
        v.get("documentation", ""),
    )

    sources = []

    for study_id, path, standard in (
        (
            "validation-spdx",
            "validation/cyclonedx-cli-424/source.spdx.json",
            "spdx",
        ),
        (
            "validation-cdx",
            "validation/cyclonedx-cli-reverse-sweep/source.cdx.json",
            "cyclonedx",
        ),
    ):
        document = json.loads(contained(root, path).read_text(encoding="utf-8"))

        version = (
            document.get("spdxVersion")
            if standard == "spdx"
            else document["specVersion"]
        )

        sources.append(
            Source(
                study_id,
                path,
                sha256_file(root / path),
                standard,
                "json",
                version,
            )
        )

    rows = []

    for source in sources:
        for converter in converters:
            row = _route_row(_route(source, converter, validator))

            row = {
                key: (
                    value.replace("generalization/results", RESULTS)
                    if isinstance(value, str)
                    else [s.replace("generalization/results", RESULTS) for s in value]
                    if isinstance(value, list)
                    else value
                )
                for key, value in row.items()
            }

            rows.append(row)

    cfg = {
        "members": 2,
        "converters": len(converters),
        "matrix_rows": len(rows),
        "planned_routes": sum(r["status"] == "planned" for r in rows),
        "unsupported_routes": sum(r["status"] != "planned" for r in rows),
        "execution_state": "not_started",
        "transformation_outputs_examined": False,
        "results_directory": RESULTS,
        "run_manifest_path": f"{RESULTS}/run.json",
        "timeout_seconds": 300,
        "retry_directory_pattern": "retry-{n}",
    }

    text = render_document(
        header=["Engineering-only executor smoke plan."],
        tables={
            "transformations": cfg,
            "target_validator": v,
            "apparatus_sha256": code_hashes(root),
        },
        arrays={
            "converter": formal["converter"],
            "route": rows,
        },
    )

    out.parent.mkdir(parents=True, exist_ok=True)

    with out.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(text)

    return out


def refresh_plan(root: Path) -> None:
    """Refresh only the execution plan, preserving selection and pinned tool identities."""
    from preservation_test.generalization import p04_build_transformations as builder
    from preservation_test.generalization.execute_generalization import validate_plan
    from preservation_test.generalization.verification.verify_03_sources import (
        verify_03_sources,
    )
    from preservation_test.generalization.verification.verify_04_transformations_utils import (
        verify_converters,
        verify_target_validator,
    )

    if (
        "**Status:** FROZEN"
        in (root / "contracts/FREEZE_02_GENERALIZATION.md").read_text()
    ):
        raise ValueError("cannot refresh an established freeze")

    results = root / "generalization/results"

    if results.exists() and any(results.iterdir()):
        raise ValueError("formal results exist; refuse plan regeneration")

    verify_03_sources(root)

    plan_path = root / PLAN
    old = plan_path.read_bytes()
    plan = tomllib.loads(old.decode("utf-8"))

    verify_converters(root, plan)
    verify_target_validator(root, plan)

    converters = tuple(
        Converter(
            converter_id=c["id"],
            name=c["name"],
            version=c["version"],
            artifact_path=root / c["artifact_path"],
            artifact_sha256=c["artifact_sha256"],
            documentation=c.get("documentation", ""),
            runtime=c["runtime"],
            runtime_artifact_path=(
                root / c["runtime_artifact_path"]
                if c.get("runtime_artifact_path")
                else None
            ),
            runtime_version=c.get("runtime_version", ""),
            runtime_sha256=c.get("runtime_sha256", ""),
        )
        for c in plan["converter"]
    )

    v = plan["target_validator"]

    validator = TargetValidator(
        v["name"],
        v["version"],
        root / v["artifact_path"],
        v["artifact_sha256"],
        v.get("documentation", ""),
    )

    sources = builder._load_sources(root / "generalization/04-sources.toml")

    routes = tuple(
        builder._route(source, converter, validator)
        for source in sources
        for converter in converters
    )

    text = builder._render(
        sources,
        converters,
        validator,
        routes,
    )
    updated = tomllib.loads(text)

    old_pairs = {
        (r["route_id"], r["source_sha256"], r["status"]) for r in plan["route"]
    }
    new_pairs = {
        (r["route_id"], r["source_sha256"], r["status"]) for r in updated["route"]
    }

    if (
        old_pairs != new_pairs
        or updated["converter"] != plan["converter"]
        or updated["target_validator"] != plan["target_validator"]
    ):
        raise ValueError(
            "refresh would change sources, route population, or tool identities"
        )

    validate_plan(root, updated)
    temporary = plan_path.with_suffix(".pending")

    with temporary.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(text)

    temporary.replace(plan_path)

    print(
        "Execution plan refreshed; sampling, sources, routes, "
        "and tool identities retained."
    )


def verify_smoke(root: Path) -> dict[str, Any]:
    """Require real Windows smoke completion, preserved evidence, and timeout margin."""
    from preservation_test.generalization.execute_generalization import validate_plan

    with contained(root, SMOKE_PLAN).open("rb") as handle:
        plan = tomllib.load(handle)

    validate_plan(root, plan)

    if plan["apparatus_sha256"] != code_hashes(root):
        raise ValueError(
            "smoke apparatus changed; another engineering smoke attempt is required"
        )

    manifest = json.loads(contained(root, SMOKE).read_text(encoding="utf-8"))

    if (
        manifest.get("mode") != "engineering"
        or manifest.get("status") != "finished"
        or manifest.get("system") != "Windows"
        or manifest.get("architecture", "").lower() not in ("amd64", "x86_64")
    ):
        raise ValueError("a completed Windows x64 engineering smoke run is required")

    if manifest["plan_sha256"] != sha256_file(root / SMOKE_PLAN):
        raise ValueError("smoke plan changed after execution")

    with contained(root, PLAN).open("rb") as handle:
        formal = tomllib.load(handle)

    if (
        plan["converter"] != formal["converter"]
        or plan["target_validator"] != formal["target_validator"]
    ):
        raise ValueError("formal tools differ from smoke-tested tools")

    maximum = 0.0
    exercised = set()

    for route in plan["route"]:
        if route["status"] != "planned":
            continue

        record = json.loads(
            contained(root, route["execution_path"]).read_text(encoding="utf-8")
        )

        if (
            record.get("status") != "finished"
            or record.get("execution_outcome") != "completed"
            or record.get("evaluation_outcome") != "completed"
            or record.get("validation_outcome") not in ("valid", "invalid")
        ):
            raise ValueError(
                f"smoke route did not complete all steps: {route['route_id']}"
            )

        if record["target_sha256"] != sha256_file(
            contained(root, route["target_path"])
        ):
            raise ValueError("smoke target changed")

        for key in ("transformation", "validation", "evaluation"):
            maximum = max(
                maximum,
                record[key]["duration_seconds"],
            )

        exercised.add(route["converter_id"])

    if exercised != {c["id"] for c in formal["converter"]}:
        raise ValueError("smoke did not exercise all three converters")

    if formal["transformations"]["timeout_seconds"] < max(
        60,
        maximum * 4 + 30,
    ):
        raise ValueError(
            "formal timeout must allow four times maximum smoke duration "
            "plus 30 seconds, with a 60 second floor"
        )

    return {
        "maximum_step_seconds": maximum,
        "timeout_seconds": formal["transformations"]["timeout_seconds"],
    }


def main() -> None:
    """Prepare, execute, or verify engineering smoke evidence explicitly."""
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument("--refresh-plan", action="store_true")
    group.add_argument("--prepare", action="store_true")
    group.add_argument("--run", action="store_true")
    group.add_argument("--verify", action="store_true")

    args = parser.parse_args()

    if args.refresh_plan:
        refresh_plan(ROOT)

    elif args.prepare:
        print(prepare(ROOT))

    elif args.run:
        if platform.system() != "Windows":
            raise ValueError("real pinned tool smoke execution requires Windows")

        from preservation_test.generalization.execute_generalization import execute

        print(
            execute(
                ROOT,
                ROOT / SMOKE_PLAN,
                engineering=True,
            )
        )

    else:
        print(verify_smoke(ROOT))


if __name__ == "__main__":
    main()
