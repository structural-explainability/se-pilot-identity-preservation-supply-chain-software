"""Step p04: define the frozen transformation matrix in 05-transformations.toml.

Purpose
-------
04-sources.toml has already fixed the exact held-out source bytes that will
participate in the formal generalization experiment.

This step defines what will be done to those sources before any generalization
transformation output is examined.

For every preserved source and every declared converter family, p04 records:

1. the converter identity and version,
2. the exact converter artifact and its SHA-256,
3. the transformation direction,
4. the intended target format and version where known,
5. the exact command arguments that will be used,
6. the target, evaluator-output, and log paths,
7. whether the route is planned or known to be unsupported before execution,
   and
8. the pre-execution capability basis for that decision.

This step does not run a converter.
It does not create target SBOMs, call the evaluator, inspect transformation
behavior, or alter corpus membership.

Unsupported routes remain in the matrix.
A source is never replaced merely because a converter
does not support its format or specification version.

The resulting 05-transformations.toml is
the pre-outcome execution plan for Freeze 02.

Usage from the repository root:

uv run python -m preservation_test.generalization.p04_build_transformations `
    --syft bin/generalization/syft.exe `
    --syft-version "1.52.0" `
    --sbom-convert bin/generalization/sbom-convert.exe `
    --sbom-convert-version "0.0.7" `
    --cdx2spdx-jar bin/generalization/cdx2spdx.jar `
    --cdx2spdx-version "0.1.5" `
    --java "bin/generalization/jdk-21.0.12.1+1/bin/java.exe" `
    --java-version "21.0.12.1+1"

Pre-freeze converter capability basis
-------------------------------------
Syft documents SPDX-to-CycloneDX and CycloneDX-to-SPDX conversion and supports
versioned output through SPDX 2.3 and CycloneDX 1.6.
Its applicable routes are included as planned transformations.

Protobom documents JSON input support for SPDX 2.3 and CycloneDX 1.4 through 1.6.
The selected SPDX 2.3 sources are eligible for its declared
SPDX-to-CycloneDX route.
The selected CycloneDX sources are version 1.2 or 1.3
and are recorded as unsupported pre-execution routes rather than
being replaced by different source artifacts.

cdx2spdx documents CycloneDX JSON-to-SPDX conversion but does not publish a
comparable CycloneDX source-version support matrix.
Its CycloneDX routes are frozen as planned attempts
without pretesting the held-out sources.

cdxgen/cdx-convert is not included in this matrix.
Its documented direct conversion inputs begin with
newer CycloneDX versions than the selected
CycloneDX 1.2/1.3 corpus members,
and its SPDX output is SPDX 3.x rather than the SPDX 2.x representation
supported by the frozen evaluator.
It does not provide an evaluable transformation route
for this corpus and frozen commitment/evaluator.

Exact converter versions, executable hashes, route status, and capability
basis used for Freeze 02 are recorded in 05-transformations.toml.
"""

import argparse
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import sys
import tomllib
from typing import Any

from preservation_test.generalization.utils.hashing import sha256_file
from preservation_test.generalization.utils.screening import (
    relative_to_root,
    screening_code_hashes,
)
from preservation_test.generalization.utils.toml_writer import (
    render_document,
    write_new_file,
)
from preservation_test.generalization.verification.verify_sources import (
    SourcesVerificationError,
    verify_sources,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
THIS_STEP = Path(__file__).resolve()
STEP_MODULE = f"preservation_test.generalization.{THIS_STEP.stem}"

CORPUS_FILE = Path("generalization/03-corpus.toml")
SOURCES_RECORD = Path("generalization/04-sources.toml")
OUT_FILE = Path("generalization/05-transformations.toml")
RESULTS_DIR = Path("generalization/results")

EXIT_OK = 0
EXIT_REFUSED = 2

PLANNED = "planned"
UNSUPPORTED = "unsupported_pre_execution"


class TransformationPlanError(RuntimeError):
    """Raised when the transformation matrix cannot be defined safely."""


@dataclass(frozen=True)
class Source:
    """One preserved held-out source with its selected source format."""

    study_id: str
    preserved_path: str
    preserved_sha256: str
    source_standard: str
    source_spec_version: str


@dataclass(frozen=True)
class Converter:
    """One exact converter artifact declared for the generalization run."""

    converter_id: str
    name: str
    version: str
    artifact_path: Path
    artifact_sha256: str
    documentation: str
    runtime: str


@dataclass(frozen=True)
class RoutePlan:
    """One source/converter transformation decision."""

    route_id: str
    study_id: str
    converter_id: str
    source_path: str
    source_sha256: str
    source_standard: str
    source_spec_version: str
    direction: str
    status: str
    target_standard: str
    target_spec_version: str
    target_path: str
    evaluation_path: str
    log_path: str
    capability_basis: str
    unsupported_reason: str
    command_argv: tuple[str, ...]


def _required_string(data: dict[str, Any], key: str, where: str) -> str:
    """Return one required non-empty string."""
    value = data.get(key)
    if not isinstance(value, str) or not value:
        raise TransformationPlanError(f"{where}.{key} must be a non-empty string")
    return value


def _load_corpus_versions(path: Path) -> dict[str, str]:
    """Return source specification versions keyed by study_id."""
    with path.open("rb") as handle:
        data = tomllib.load(handle)

    rows = data.get("member")
    if not isinstance(rows, list) or not rows:
        raise TransformationPlanError("03-corpus.toml contains no [[member]] entries")

    versions: dict[str, str] = {}

    for index, row in enumerate(rows):
        where = f"member[{index}]"

        if not isinstance(row, dict):
            raise TransformationPlanError(f"{where} must be a table")

        study_id = _required_string(row, "study_id", where)
        spec_version = _required_string(row, "source_spec_version", where)

        if study_id in versions:
            raise TransformationPlanError(f"duplicate corpus study_id: {study_id}")

        versions[study_id] = spec_version

    return versions


def _load_sources(
    sources_path: Path,
    corpus_path: Path,
) -> tuple[Source, ...]:
    """Load preserved sources and join them to their selected spec versions."""
    versions = _load_corpus_versions(corpus_path)

    with sources_path.open("rb") as handle:
        data = tomllib.load(handle)

    rows = data.get("source")
    if not isinstance(rows, list) or not rows:
        raise TransformationPlanError("04-sources.toml contains no [[source]] entries")

    sources: list[Source] = []
    seen: set[str] = set()

    for index, row in enumerate(rows):
        where = f"source[{index}]"

        if not isinstance(row, dict):
            raise TransformationPlanError(f"{where} must be a table")

        study_id = _required_string(row, "study_id", where)

        if study_id in seen:
            raise TransformationPlanError(f"duplicate source study_id: {study_id}")

        if study_id not in versions:
            raise TransformationPlanError(
                f"{study_id} exists in 04-sources.toml but not 03-corpus.toml"
            )

        source = Source(
            study_id=study_id,
            preserved_path=_required_string(row, "preserved_path", where),
            preserved_sha256=_required_string(
                row,
                "preserved_sha256",
                where,
            ),
            source_standard=_required_string(
                row,
                "source_standard",
                where,
            ),
            source_spec_version=versions[study_id],
        )

        preserved = REPOSITORY_ROOT / source.preserved_path

        if not preserved.is_file():
            raise TransformationPlanError(
                f"preserved source not found: {source.preserved_path}"
            )

        observed = sha256_file(preserved)

        if observed != source.preserved_sha256:
            raise TransformationPlanError(
                "preserved source hash mismatch:\n"
                f"  study_id: {source.study_id}\n"
                f"  recorded: {source.preserved_sha256}\n"
                f"  observed: {observed}"
            )

        sources.append(source)
        seen.add(study_id)

    if set(versions) != seen:
        missing = sorted(set(versions) - seen)
        raise TransformationPlanError(
            f"corpus members missing from 04-sources.toml: {missing}"
        )

    return tuple(sources)


def _resolve_tool(path: Path) -> Path:
    """Resolve one converter artifact relative to the repository root."""
    absolute = path if path.is_absolute() else REPOSITORY_ROOT / path

    if not absolute.is_file():
        raise TransformationPlanError(f"converter artifact not found: {path}")

    return absolute.resolve()


def _converter(
    converter_id: str,
    name: str,
    version: str,
    artifact_path: Path,
    documentation: str,
    runtime: str,
) -> Converter:
    """Create one converter record from an exact local artifact."""
    if not version.strip():
        raise TransformationPlanError(
            f"{converter_id} version must be a non-empty string"
        )

    resolved = _resolve_tool(artifact_path)

    return Converter(
        converter_id=converter_id,
        name=name,
        version=version.strip(),
        artifact_path=resolved,
        artifact_sha256=sha256_file(resolved),
        documentation=documentation,
        runtime=runtime,
    )


def _target_paths(
    source: Source,
    converter_id: str,
    target_standard: str,
) -> tuple[str, str, str]:
    """Return predeclared target, evaluation, and log paths."""
    directory = RESULTS_DIR / source.study_id / converter_id

    suffix = "spdx.json" if target_standard == "spdx" else "cdx.json"

    return (
        (directory / f"target.{suffix}").as_posix(),
        (directory / "evaluation.json").as_posix(),
        (directory / "transform.log").as_posix(),
    )


def _unsupported(
    source: Source,
    converter: Converter,
    direction: str,
    target_standard: str,
    target_spec_version: str,
    capability_basis: str,
    reason: str,
) -> RoutePlan:
    """Return one explicitly unsupported pre-execution route."""
    target_path, evaluation_path, log_path = _target_paths(
        source,
        converter.converter_id,
        target_standard,
    )

    return RoutePlan(
        route_id=f"{source.study_id}--{converter.converter_id}",
        study_id=source.study_id,
        converter_id=converter.converter_id,
        source_path=source.preserved_path,
        source_sha256=source.preserved_sha256,
        source_standard=source.source_standard,
        source_spec_version=source.source_spec_version,
        direction=direction,
        status=UNSUPPORTED,
        target_standard=target_standard,
        target_spec_version=target_spec_version,
        target_path=target_path,
        evaluation_path=evaluation_path,
        log_path=log_path,
        capability_basis=capability_basis,
        unsupported_reason=reason,
        command_argv=(),
    )


def _planned(
    source: Source,
    converter: Converter,
    direction: str,
    target_standard: str,
    target_spec_version: str,
    capability_basis: str,
    command_argv: tuple[str, ...],
) -> RoutePlan:
    """Return one predeclared transformation route."""
    target_path, evaluation_path, log_path = _target_paths(
        source,
        converter.converter_id,
        target_standard,
    )

    expanded = tuple(
        argument.replace("{source}", source.preserved_path).replace(
            "{target}",
            target_path,
        )
        for argument in command_argv
    )

    return RoutePlan(
        route_id=f"{source.study_id}--{converter.converter_id}",
        study_id=source.study_id,
        converter_id=converter.converter_id,
        source_path=source.preserved_path,
        source_sha256=source.preserved_sha256,
        source_standard=source.source_standard,
        source_spec_version=source.source_spec_version,
        direction=direction,
        status=PLANNED,
        target_standard=target_standard,
        target_spec_version=target_spec_version,
        target_path=target_path,
        evaluation_path=evaluation_path,
        log_path=log_path,
        capability_basis=capability_basis,
        unsupported_reason="",
        command_argv=expanded,
    )


def _syft_route(source: Source, converter: Converter) -> RoutePlan:
    """Define one Syft route without executing it."""
    executable = relative_to_root(
        converter.artifact_path,
        REPOSITORY_ROOT,
    )

    basis = (
        "Syft format-conversion documentation declares SPDX and CycloneDX "
        "conversion; target schema version is fixed explicitly in command"
    )

    if source.source_standard == "cyclonedx":
        target_path, _, _ = _target_paths(
            source,
            converter.converter_id,
            "spdx",
        )

        return _planned(
            source=source,
            converter=converter,
            direction="cyclonedx_to_spdx",
            target_standard="spdx",
            target_spec_version="SPDX-2.3",
            capability_basis=basis,
            command_argv=(
                executable,
                "convert",
                "{source}",
                "-o",
                f"spdx-json@2.3={target_path}",
            ),
        )

    if source.source_standard == "spdx":
        target_path, _, _ = _target_paths(
            source,
            converter.converter_id,
            "cyclonedx",
        )

        return _planned(
            source=source,
            converter=converter,
            direction="spdx_to_cyclonedx",
            target_standard="cyclonedx",
            target_spec_version="1.6",
            capability_basis=basis,
            command_argv=(
                executable,
                "convert",
                "{source}",
                "-o",
                f"cyclonedx-json@1.6={target_path}",
            ),
        )

    raise TransformationPlanError(
        f"unsupported source standard: {source.source_standard}"
    )


def _protobom_route(
    source: Source,
    converter: Converter,
) -> RoutePlan:
    """Define one protobom/sbom-convert route from documented read support."""
    executable = relative_to_root(
        converter.artifact_path,
        REPOSITORY_ROOT,
    )

    basis = (
        "Protobom documentation declares JSON read support for SPDX 2.3 "
        "and CycloneDX 1.4, 1.5, and 1.6"
    )

    if source.source_standard == "spdx":
        if source.source_spec_version != "SPDX-2.3":
            return _unsupported(
                source=source,
                converter=converter,
                direction="spdx_to_cyclonedx",
                target_standard="cyclonedx",
                target_spec_version="1.4",
                capability_basis=basis,
                reason=(
                    "source SPDX version is outside documented protobom "
                    "JSON read support"
                ),
            )

        return _planned(
            source=source,
            converter=converter,
            direction="spdx_to_cyclonedx",
            target_standard="cyclonedx",
            target_spec_version="1.4",
            capability_basis=basis,
            command_argv=(
                executable,
                "convert",
                "{source}",
                "-f",
                "cyclonedx-1.4",
                "-o",
                "{target}",
            ),
        )

    if source.source_standard == "cyclonedx":
        if source.source_spec_version not in {"1.4", "1.5", "1.6"}:
            return _unsupported(
                source=source,
                converter=converter,
                direction="cyclonedx_to_spdx",
                target_standard="spdx",
                target_spec_version="SPDX-2.3",
                capability_basis=basis,
                reason=(
                    "source CycloneDX version is outside documented "
                    "protobom JSON read support"
                ),
            )

        return _planned(
            source=source,
            converter=converter,
            direction="cyclonedx_to_spdx",
            target_standard="spdx",
            target_spec_version="SPDX-2.3",
            capability_basis=basis,
            command_argv=(
                executable,
                "convert",
                "{source}",
                "-f",
                "spdx-2.3",
                "-o",
                "{target}",
            ),
        )

    raise TransformationPlanError(
        f"unsupported source standard: {source.source_standard}"
    )


def _cdx2spdx_route(
    source: Source,
    converter: Converter,
) -> RoutePlan:
    """Define one cdx2spdx route without pretesting held-out inputs."""
    jar = relative_to_root(
        converter.artifact_path,
        REPOSITORY_ROOT,
    )

    basis = (
        "spdx/cdx2spdx documentation declares CycloneDX JSON to SPDX "
        "conversion but does not publish an explicit CycloneDX source-version "
        "support matrix; selected source versions are not pretested"
    )

    if source.source_standard == "spdx":
        return _unsupported(
            source=source,
            converter=converter,
            direction="spdx_to_cyclonedx",
            target_standard="cyclonedx",
            target_spec_version="not_applicable",
            capability_basis=basis,
            reason="cdx2spdx implements CycloneDX-to-SPDX conversion only",
        )

    if source.source_standard != "cyclonedx":
        raise TransformationPlanError(
            f"unsupported source standard: {source.source_standard}"
        )

    return _planned(
        source=source,
        converter=converter,
        direction="cyclonedx_to_spdx",
        target_standard="spdx",
        target_spec_version="converter-defined",
        capability_basis=basis,
        command_argv=(
            "java",
            "-jar",
            jar,
            "{source}",
            "{target}",
        ),
    )


def _route(
    source: Source,
    converter: Converter,
) -> RoutePlan:
    """Dispatch one source/converter pair to its declared route rule."""
    if converter.converter_id == "syft":
        return _syft_route(source, converter)

    if converter.converter_id == "protobom":
        return _protobom_route(source, converter)

    if converter.converter_id == "cdx2spdx":
        return _cdx2spdx_route(source, converter)

    raise TransformationPlanError(f"unknown converter_id: {converter.converter_id}")


def _converter_row(converter: Converter) -> dict[str, Any]:
    """Return one exact converter artifact as a TOML-ready row."""
    return {
        "id": converter.converter_id,
        "name": converter.name,
        "version": converter.version,
        "artifact_path": relative_to_root(
            converter.artifact_path,
            REPOSITORY_ROOT,
        ),
        "artifact_sha256": converter.artifact_sha256,
        "runtime": converter.runtime,
        "documentation": converter.documentation,
    }


def _route_row(route: RoutePlan) -> dict[str, Any]:
    """Return one transformation route as a TOML-ready row."""
    row: dict[str, Any] = {
        "route_id": route.route_id,
        "study_id": route.study_id,
        "converter_id": route.converter_id,
        "source_path": route.source_path,
        "source_sha256": route.source_sha256,
        "source_standard": route.source_standard,
        "source_spec_version": route.source_spec_version,
        "direction": route.direction,
        "status": route.status,
        "target_standard": route.target_standard,
        "target_spec_version": route.target_spec_version,
        "target_path": route.target_path,
        "evaluation_path": route.evaluation_path,
        "log_path": route.log_path,
        "capability_basis": route.capability_basis,
    }

    if route.unsupported_reason:
        row["unsupported_reason"] = route.unsupported_reason

    if route.command_argv:
        row["command_argv"] = list(route.command_argv)

    return row


def _render(
    sources: tuple[Source, ...],
    converters: tuple[Converter, ...],
    routes: tuple[RoutePlan, ...],
) -> str:
    """Render 05-transformations.toml."""
    status_counts = Counter(route.status for route in routes)

    return render_document(
        header=[
            "05-transformations.toml",
            f"Generated by {STEP_MODULE}.",
            "Pre-outcome transformation matrix for the held-out generalization corpus.",
            "No formal generalization transformation has been executed by this step.",
            "Do not edit by hand.",
        ],
        tables={
            "transformations": {
                "sources_record": SOURCES_RECORD.as_posix(),
                "sources_record_sha256": sha256_file(REPOSITORY_ROOT / SOURCES_RECORD),
                "corpus_record": CORPUS_FILE.as_posix(),
                "corpus_record_sha256": sha256_file(REPOSITORY_ROOT / CORPUS_FILE),
                "members": len(sources),
                "converters": len(converters),
                "matrix_rows": len(routes),
                "planned_routes": status_counts[PLANNED],
                "unsupported_routes": status_counts[UNSUPPORTED],
                "execution_state": "not_started",
                "transformation_outputs_examined": False,
                "results_directory": RESULTS_DIR.as_posix(),
            },
            "transformations_code_sha256": screening_code_hashes(
                REPOSITORY_ROOT,
                extra=(THIS_STEP,),
            ),
        },
        arrays={
            "converter": [_converter_row(converter) for converter in converters],
            "route": [_route_row(route) for route in routes],
        },
    )


def build_transformations(
    syft_path: Path,
    syft_version: str,
    sbom_convert_path: Path,
    sbom_convert_version: str,
    cdx2spdx_jar: Path,
    cdx2spdx_version: str,
) -> int:
    """Build the complete pre-execution transformation matrix."""
    out = REPOSITORY_ROOT / OUT_FILE

    if out.exists():
        sys.stderr.write(
            f"TRANSFORMATIONS NOT BUILT.\nrefusing to overwrite {OUT_FILE.as_posix()}\n"
        )
        return EXIT_REFUSED

    try:
        verify_sources(REPOSITORY_ROOT)

        sources = _load_sources(
            REPOSITORY_ROOT / SOURCES_RECORD,
            REPOSITORY_ROOT / CORPUS_FILE,
        )

        converters = (
            _converter(
                converter_id="syft",
                name="Anchore Syft",
                version=syft_version,
                artifact_path=syft_path,
                documentation=("https://oss.anchore.com/docs/guides/sbom/conversion/"),
                runtime="native executable",
            ),
            _converter(
                converter_id="protobom",
                name="Protobom sbom-convert",
                version=sbom_convert_version,
                artifact_path=sbom_convert_path,
                documentation=("https://github.com/protobom/sbom-convert"),
                runtime="native executable",
            ),
            _converter(
                converter_id="cdx2spdx",
                name="SPDX cdx2spdx",
                version=cdx2spdx_version,
                artifact_path=cdx2spdx_jar,
                documentation=("https://github.com/spdx/cdx2spdx"),
                runtime="Java",
            ),
        )

        routes = tuple(
            _route(source, converter) for source in sources for converter in converters
        )

        route_ids = [route.route_id for route in routes]

        if len(set(route_ids)) != len(route_ids):
            raise TransformationPlanError("transformation route IDs are not unique")

        text = _render(
            sources,
            converters,
            routes,
        )

        write_new_file(out, text)

    except (
        OSError,
        SourcesVerificationError,
        TransformationPlanError,
    ) as error:
        sys.stderr.write(f"TRANSFORMATIONS NOT BUILT.\n{error}\n")
        return EXIT_REFUSED

    print(f"wrote {OUT_FILE.as_posix()} (sha256 {sha256_file(out)})")
    print(f"sources: {len(sources)}")
    print(f"converters: {len(converters)}")
    print(f"matrix rows: {len(routes)}")
    print(f"planned: {sum(route.status == PLANNED for route in routes)}")
    print(
        "unsupported pre-execution: "
        f"{sum(route.status == UNSUPPORTED for route in routes)}"
    )

    return EXIT_OK


def main(argv: list[str] | None = None) -> int:
    """Parse arguments and run p04."""
    parser = argparse.ArgumentParser(
        description=(
            "Step p04: define the pre-outcome transformation matrix "
            "and write 05-transformations.toml."
        )
    )

    parser.add_argument(
        "--syft",
        type=Path,
        required=True,
        help="Exact Syft executable to freeze.",
    )
    parser.add_argument(
        "--syft-version",
        required=True,
        help="Version label for the supplied Syft executable.",
    )

    parser.add_argument(
        "--sbom-convert",
        type=Path,
        required=True,
        help="Exact protobom sbom-convert executable to freeze.",
    )
    parser.add_argument(
        "--sbom-convert-version",
        required=True,
        help="Version label for the supplied sbom-convert executable.",
    )

    parser.add_argument(
        "--cdx2spdx-jar",
        type=Path,
        required=True,
        help="Exact cdx2spdx JAR to freeze.",
    )
    parser.add_argument(
        "--cdx2spdx-version",
        required=True,
        help="Version label for the supplied cdx2spdx JAR.",
    )

    parser.add_argument(
        "--java",
        type=Path,
        required=True,
        help="Exact Java executable used to run cdx2spdx.",
    )
    parser.add_argument(
        "--java-version",
        required=True,
        help="Version label for the supplied Java runtime.",
    )

    args = parser.parse_args(argv)

    return build_transformations(
        syft_path=args.syft,
        syft_version=args.syft_version,
        sbom_convert_path=args.sbom_convert,
        sbom_convert_version=args.sbom_convert_version,
        cdx2spdx_jar=args.cdx2spdx_jar,
        cdx2spdx_version=args.cdx2spdx_version,
    )


if __name__ == "__main__":
    raise SystemExit(main())
