"""Classes, and utility functions for verify_04_transformations.py."""

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import tomllib
from typing import Any

from preservation_test.generalization.verification.verify_03_sources import (
    SourcesVerificationError,
    verify_03_sources,
)
from preservation_test.generalization.verification.verify_hashes import (
    HashVerificationError,
    verify_file_hash,
    verify_hash_table,
)

CORPUS_FILE = Path("generalization/03-corpus.toml")
SOURCES_RECORD = Path("generalization/04-sources.toml")
TRANSFORMATIONS_FILE = Path("generalization/05-transformations.toml")
PLANNED = "planned"
UNSUPPORTED = "unsupported_pre_execution"


class TransformationsVerificationError(RuntimeError):
    """Raised when transformation definitions fail Freeze 02 verification."""


@dataclass(frozen=True)
class ExecutionConfig:
    """Validated run-level execution configuration."""

    results_directory: str
    run_manifest_path: str
    timeout_seconds: int
    retry_directory_pattern: str


@dataclass(frozen=True)
class RouteSummary:
    """Route invariants collected while verifying the transformation matrix."""

    observed_pairs: frozenset[tuple[str, str]]
    status_counts: Counter[str]


def _required_string(
    row: dict[str, Any],
    key: str,
    where: str,
) -> str:
    """Return one required non-empty string."""
    value = row.get(key)

    if not isinstance(value, str) or not value:
        raise TransformationsVerificationError(
            f"{where}.{key} must be a non-empty string"
        )

    return value


def verify_source_provenance(repository_root: Path) -> Path:
    """Verify family A: preserved-source prerequisite."""
    try:
        return verify_03_sources(repository_root)

    except SourcesVerificationError as error:
        raise TransformationsVerificationError(str(error)) from error


def load_transformation_records(
    repository_root: Path,
    sources_path: Path,
) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    """Verify family B: input records."""
    path = repository_root / TRANSFORMATIONS_FILE

    if not path.is_file():
        raise TransformationsVerificationError(
            f"transformation matrix not found: {path}"
        )

    try:
        with path.open("rb") as handle:
            data = tomllib.load(handle)

        with sources_path.open("rb") as handle:
            sources_data = tomllib.load(handle)

    except (OSError, tomllib.TOMLDecodeError) as error:
        raise TransformationsVerificationError(str(error)) from error

    return path, data, sources_data


def verify_transformations_table(
    data: dict[str, Any],
) -> dict[str, Any]:
    """Verify family B: required transformations table."""
    transformations = data.get("transformations")

    if not isinstance(transformations, dict):
        raise TransformationsVerificationError(
            "05-transformations.toml is missing [transformations]"
        )

    return transformations


def verify_record_provenance(
    repository_root: Path,
    data: dict[str, Any],
    transformations: dict[str, Any],
) -> None:
    """Verify family C: record provenance."""
    if transformations.get("sources_record") != SOURCES_RECORD.as_posix():
        raise TransformationsVerificationError(
            "05-transformations.toml records an unexpected sources path"
        )

    if transformations.get("corpus_record") != CORPUS_FILE.as_posix():
        raise TransformationsVerificationError(
            "05-transformations.toml records an unexpected corpus path"
        )

    sources_record_sha256 = _required_string(
        transformations,
        "sources_record_sha256",
        "transformations",
    )
    corpus_record_sha256 = _required_string(
        transformations,
        "corpus_record_sha256",
        "transformations",
    )

    try:
        verify_file_hash(
            repository_root,
            SOURCES_RECORD.as_posix(),
            sources_record_sha256,
            label="05-transformations.toml sources record",
        )

        verify_file_hash(
            repository_root,
            CORPUS_FILE.as_posix(),
            corpus_record_sha256,
            label="05-transformations.toml corpus record",
        )

        verify_hash_table(
            repository_root,
            data.get("transformations_code_sha256"),
            table_name="transformations_code_sha256",
        )

    except HashVerificationError as error:
        raise TransformationsVerificationError(str(error)) from error


def load_verified_sources(
    sources_data: dict[str, Any],
) -> dict[str, tuple[str, str]]:
    """Verify family D: preserved-source registry."""
    source_rows = sources_data.get("source")

    if not isinstance(source_rows, list) or not source_rows:
        raise TransformationsVerificationError(
            "04-sources.toml contains no [[source]] entries"
        )

    sources_by_study_id: dict[str, tuple[str, str]] = {}

    for index, row in enumerate(source_rows):
        where = f"source[{index}]"

        if not isinstance(row, dict):
            raise TransformationsVerificationError(f"{where} must be a table")

        study_id = _required_string(
            row,
            "study_id",
            where,
        )
        preserved_path = _required_string(
            row,
            "preserved_path",
            where,
        )
        preserved_sha256 = _required_string(
            row,
            "preserved_sha256",
            where,
        )

        if study_id in sources_by_study_id:
            raise TransformationsVerificationError(
                f"duplicate study_id in 04-sources.toml: {study_id}"
            )

        sources_by_study_id[study_id] = (
            preserved_path,
            preserved_sha256,
        )

    return sources_by_study_id


def verify_converters(
    repository_root: Path,
    data: dict[str, Any],
) -> dict[str, tuple[str, str | None]]:
    """Verify checks 5-6 and return converter execution identities."""
    converters = data.get("converter")

    if not isinstance(converters, list) or not converters:
        raise TransformationsVerificationError(
            "05-transformations.toml contains no [[converter]] entries"
        )

    converter_execution: dict[str, tuple[str, str | None]] = {}

    for index, converter in enumerate(converters):
        where = f"converter[{index}]"

        if not isinstance(converter, dict):
            raise TransformationsVerificationError(f"{where} must be a table")

        converter_id = _required_string(
            converter,
            "id",
            where,
        )
        artifact_path = _required_string(
            converter,
            "artifact_path",
            where,
        )
        artifact_sha256 = _required_string(
            converter,
            "artifact_sha256",
            where,
        )

        if converter_id in converter_execution:
            raise TransformationsVerificationError(
                f"duplicate converter id: {converter_id}"
            )

        try:
            verify_file_hash(
                repository_root,
                artifact_path,
                artifact_sha256,
                label=f"converter {converter_id}",
            )

        except HashVerificationError as error:
            raise TransformationsVerificationError(str(error)) from error

        runtime_path = converter.get("runtime_artifact_path")
        runtime_sha256 = converter.get("runtime_sha256")
        runtime_version = converter.get("runtime_version")

        runtime_fields_present = any(
            value not in (None, "")
            for value in (
                runtime_path,
                runtime_sha256,
                runtime_version,
            )
        )

        runtime_executable: str | None = None

        if runtime_fields_present:
            if not all(
                isinstance(value, str) and value
                for value in (
                    runtime_path,
                    runtime_sha256,
                    runtime_version,
                )
            ):
                raise TransformationsVerificationError(
                    f"{where} runtime path, version, and SHA-256 "
                    "must be recorded together"
                )

            assert isinstance(runtime_path, str)
            assert isinstance(runtime_sha256, str)

            try:
                verify_file_hash(
                    repository_root,
                    runtime_path,
                    runtime_sha256,
                    label=f"converter {converter_id} runtime",
                )

            except HashVerificationError as error:
                raise TransformationsVerificationError(str(error)) from error

            runtime_executable = runtime_path

        converter_execution[converter_id] = (
            artifact_path,
            runtime_executable,
        )

    return converter_execution


def verify_target_validator(
    repository_root: Path,
    data: dict[str, Any],
) -> str:
    """Verify family F: target validator."""
    validator = data.get("target_validator")

    if not isinstance(validator, dict):
        raise TransformationsVerificationError(
            "05-transformations.toml is missing [target_validator]"
        )

    validator_path = _required_string(
        validator,
        "artifact_path",
        "target_validator",
    )
    validator_sha256 = _required_string(
        validator,
        "artifact_sha256",
        "target_validator",
    )

    try:
        verify_file_hash(
            repository_root,
            validator_path,
            validator_sha256,
            label="target validator",
        )

    except HashVerificationError as error:
        raise TransformationsVerificationError(str(error)) from error

    return validator_path


def verify_execution_config(
    transformations: dict[str, Any],
) -> ExecutionConfig:
    """Verify family G: execution configuration."""
    results_directory = _required_string(
        transformations,
        "results_directory",
        "transformations",
    )

    run_manifest_path = _required_string(
        transformations,
        "run_manifest_path",
        "transformations",
    )

    expected_run_manifest_path = (Path(results_directory) / "run.json").as_posix()

    if run_manifest_path != expected_run_manifest_path:
        raise TransformationsVerificationError(
            "[transformations].run_manifest_path must equal "
            f"{expected_run_manifest_path!r}"
        )

    timeout_seconds = transformations.get("timeout_seconds")

    if (
        isinstance(timeout_seconds, bool)
        or not isinstance(timeout_seconds, int)
        or timeout_seconds <= 0
    ):
        raise TransformationsVerificationError(
            "[transformations].timeout_seconds must be a positive integer"
        )

    retry_directory_pattern = _required_string(
        transformations,
        "retry_directory_pattern",
        "transformations",
    )

    if "{n}" not in retry_directory_pattern:
        raise TransformationsVerificationError(
            "[transformations].retry_directory_pattern must contain '{n}'"
        )

    return ExecutionConfig(
        results_directory=results_directory,
        run_manifest_path=run_manifest_path,
        timeout_seconds=timeout_seconds,
        retry_directory_pattern=retry_directory_pattern,
    )


def _verify_route_paths(
    repository_root: Path,
    route: dict[str, Any],
    where: str,
    route_id: str,
    results_directory: str,
    observed_paths: set[Path],
) -> None:
    """Verify checks 13-14 for one route's declared evidence paths."""
    route_paths = {
        "target_path": _required_string(
            route,
            "target_path",
            where,
        ),
        "validation_path": _required_string(
            route,
            "validation_path",
            where,
        ),
        "evaluation_path": _required_string(
            route,
            "evaluation_path",
            where,
        ),
        "log_path": _required_string(
            route,
            "log_path",
            where,
        ),
        "validation_log_path": _required_string(
            route,
            "validation_log_path",
            where,
        ),
        "evaluation_log_path": _required_string(
            route,
            "evaluation_log_path",
            where,
        ),
        "execution_path": _required_string(
            route,
            "execution_path",
            where,
        ),
    }

    results_root = (repository_root / results_directory).resolve()

    for field_name, route_path in route_paths.items():
        resolved_path = (repository_root / route_path).resolve()

        if not resolved_path.is_relative_to(results_root):
            raise TransformationsVerificationError(
                f"{route_id} {field_name} is outside {results_directory}"
            )

        if resolved_path in observed_paths:
            raise TransformationsVerificationError(
                f"duplicate route evidence path: {route_path}"
            )

        observed_paths.add(resolved_path)


def verify_routes(
    repository_root: Path,
    routes: Any,
    sources_by_study_id: dict[str, tuple[str, str]],
    converter_execution: dict[str, tuple[str, str | None]],
    validator_path: str,
    results_directory: str,
) -> RouteSummary:
    """Verify family H: route declarations."""
    if not isinstance(routes, list) or not routes:
        raise TransformationsVerificationError(
            "05-transformations.toml contains no [[route]] entries"
        )

    route_ids: set[str] = set()
    observed_pairs: set[tuple[str, str]] = set()
    observed_paths: set[Path] = set()
    status_counts: Counter[str] = Counter()

    for index, route in enumerate(routes):
        where = f"route[{index}]"

        if not isinstance(route, dict):
            raise TransformationsVerificationError(f"{where} must be a table")

        route_id = _required_string(
            route,
            "route_id",
            where,
        )
        study_id = _required_string(
            route,
            "study_id",
            where,
        )
        converter_id = _required_string(
            route,
            "converter_id",
            where,
        )
        source_path = _required_string(
            route,
            "source_path",
            where,
        )
        source_sha256 = _required_string(
            route,
            "source_sha256",
            where,
        )
        status = _required_string(
            route,
            "status",
            where,
        )

        if route_id in route_ids:
            raise TransformationsVerificationError(
                f"duplicate route_id in 05-transformations.toml: {route_id}"
            )

        route_ids.add(route_id)

        expected_source = sources_by_study_id.get(study_id)

        if expected_source is None:
            raise TransformationsVerificationError(
                f"{route_id} references unknown study_id {study_id!r}"
            )

        if converter_id not in converter_execution:
            raise TransformationsVerificationError(
                f"{route_id} references unknown converter_id {converter_id!r}"
            )

        if (source_path, source_sha256) != expected_source:
            raise TransformationsVerificationError(
                f"{route_id} source path/hash does not match 04-sources.toml"
            )

        _verify_route_paths(
            repository_root=repository_root,
            route=route,
            where=where,
            route_id=route_id,
            results_directory=results_directory,
            observed_paths=observed_paths,
        )

        expected_route_id = f"{study_id}--{converter_id}"

        if route_id != expected_route_id:
            raise TransformationsVerificationError(
                f"{route_id} does not equal expected route id {expected_route_id}"
            )

        pair = (
            study_id,
            converter_id,
        )

        if pair in observed_pairs:
            raise TransformationsVerificationError(
                f"duplicate source/converter matrix cell: {pair}"
            )

        observed_pairs.add(pair)

        if status not in {PLANNED, UNSUPPORTED}:
            raise TransformationsVerificationError(
                f"{route_id} has unknown status {status!r}"
            )

        status_counts[status] += 1

        command_argv = route.get("command_argv")
        validation_argv = route.get("validation_command_argv")
        validation_required = route.get("validation_required")

        if status == PLANNED:
            if not isinstance(command_argv, list) or not command_argv:
                raise TransformationsVerificationError(
                    f"{route_id} is planned but has no command_argv"
                )

            converter_artifact, runtime_executable = converter_execution[converter_id]

            if runtime_executable is None:
                if command_argv[0] != converter_artifact:
                    raise TransformationsVerificationError(
                        f"{route_id} command_argv does not invoke the "
                        "recorded converter artifact"
                    )

            else:
                if command_argv[0] != runtime_executable:
                    raise TransformationsVerificationError(
                        f"{route_id} command_argv does not invoke the "
                        "recorded converter runtime"
                    )

                if converter_artifact not in command_argv[1:]:
                    raise TransformationsVerificationError(
                        f"{route_id} command_argv does not reference the "
                        "recorded converter artifact"
                    )

            if validation_required is not True:
                raise TransformationsVerificationError(
                    f"{route_id} is planned but validation_required is not true"
                )

            if not isinstance(validation_argv, list) or not validation_argv:
                raise TransformationsVerificationError(
                    f"{route_id} is planned but has no validation_command_argv"
                )

            if validation_argv[0] != validator_path:
                raise TransformationsVerificationError(
                    f"{route_id} validation_command_argv does not invoke the "
                    "recorded target validator"
                )

        else:
            if command_argv not in (None, []):
                raise TransformationsVerificationError(
                    f"{route_id} is unsupported but has command_argv"
                )

            if validation_argv not in (None, []):
                raise TransformationsVerificationError(
                    f"{route_id} is unsupported but has validation_command_argv"
                )

            if validation_required is not False:
                raise TransformationsVerificationError(
                    f"{route_id} is unsupported but validation_required is not false"
                )

            _required_string(
                route,
                "unsupported_reason",
                where,
            )

    return RouteSummary(
        observed_pairs=frozenset(observed_pairs),
        status_counts=status_counts,
    )


def verify_matrix(
    transformations: dict[str, Any],
    sources_by_study_id: dict[str, tuple[str, str]],
    converter_ids: set[str],
    route_summary: RouteSummary,
) -> None:
    """Verify family I: matrix invariants."""
    expected_pairs = {
        (study_id, converter_id)
        for study_id in sources_by_study_id
        for converter_id in converter_ids
    }

    observed_pairs = set(route_summary.observed_pairs)

    if observed_pairs != expected_pairs:
        missing = sorted(expected_pairs - observed_pairs)
        extra = sorted(observed_pairs - expected_pairs)

        raise TransformationsVerificationError(
            "transformation matrix is not the complete cross-product; "
            f"missing={missing}, extra={extra}"
        )

    expected_rows = len(expected_pairs)

    if transformations.get("members") != len(sources_by_study_id):
        raise TransformationsVerificationError(
            "[transformations].members does not match 04-sources.toml"
        )

    if transformations.get("converters") != len(converter_ids):
        raise TransformationsVerificationError(
            "[transformations].converters does not match [[converter]] count"
        )

    if transformations.get("matrix_rows") != expected_rows:
        raise TransformationsVerificationError(
            "[transformations].matrix_rows does not match the complete matrix"
        )

    status_counts = route_summary.status_counts

    if transformations.get("planned_routes") != status_counts[PLANNED]:
        raise TransformationsVerificationError(
            "[transformations].planned_routes does not match [[route]] records"
        )

    if transformations.get("unsupported_routes") != status_counts[UNSUPPORTED]:
        raise TransformationsVerificationError(
            "[transformations].unsupported_routes does not match [[route]] records"
        )

    if status_counts[PLANNED] + status_counts[UNSUPPORTED] != expected_rows:
        raise TransformationsVerificationError(
            "planned + unsupported route counts do not equal matrix_rows"
        )


def verify_pre_execution_state(
    repository_root: Path,
    transformations: dict[str, Any],
    results_directory: str,
) -> None:
    """Verify checks 23-24: declared and observed pre-execution state."""
    if transformations.get("execution_state") != "not_started":
        raise TransformationsVerificationError(
            "[transformations].execution_state must be 'not_started' before Freeze 02"
        )

    if transformations.get("transformation_outputs_examined") is not False:
        raise TransformationsVerificationError(
            "[transformations].transformation_outputs_examined must be false"
        )

    results_root = repository_root / results_directory

    if results_root.exists() and any(results_root.iterdir()):
        raise TransformationsVerificationError(
            "generalization results directory is not empty before Freeze 02"
        )
