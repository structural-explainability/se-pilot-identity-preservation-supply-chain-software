"""Verification stage 04: verify the frozen transformation execution plan.

Purpose
-------
05-transformations.toml is the pre-outcome execution plan that crosses the
preserved held-out corpus with the independently selected transformation
implementations.

This verifier establishes that the plan still refers to the exact source
records, converter artifacts, runtime artifacts, target validator, and complete
source/converter matrix declared before generalization execution.

The verified provenance chain is:

    04-sources.toml
        |
        +----------------------+
        |                      |
        v                      v
preserved sources       frozen tool artifacts
        |                      |
        +----------+-----------+
                   |
                   v
        05-transformations.toml

This stage first invokes the preserved-source verifier and then verifies:

1. 05-transformations.toml exists and parses;
2. its recorded 04-sources.toml SHA-256 matches the current source record;
3. its recorded 03-corpus.toml SHA-256 matches the current corpus record;
4. its recorded transformation-definition code hashes match the current files;
5. every converter artifact exists and matches its recorded SHA-256;
6. every recorded converter runtime artifact exists and matches its SHA-256;
7. the target-validator artifact exists and matches its recorded SHA-256;
8. every route refers to a preserved source and declared converter;
9. every route carries the exact source path and SHA-256 recorded in
   04-sources.toml;
10. every route ID is uniquely determined by its study ID and converter ID;
11. every source/converter pair occurs exactly once;
12. the matrix is the complete cross-product of frozen sources and converters;
13. planned and unsupported route counts match the generated route records;
14. planned routes contain transformation and target-validation commands;
15. unsupported routes contain no executable command and record their
    pre-execution reason; and
16. the plan still declares that execution has not started and no
    generalization transformation outputs have been examined.

An unsupported route remains part of the matrix. It is verified as a declared
pre-execution capability boundary rather than treated as a transformation
failure.

The central matrix invariant is:

    number of preserved sources
        x
    number of frozen converters
        ==
    number of declared transformation routes

Every converter, runtime, validator, and source byte sequence required by the
plan must still be the exact artifact whose SHA-256 was recorded before
generalization execution.

This verifier runs no converter, validator, or evaluator and performs no
writes.
"""

from collections import Counter
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


def verify_04_transformations(repository_root: Path) -> Path:
    """Verify 04 -> 05 provenance, tool hashes, source hashes, and matrix invariants."""
    try:
        sources_path = verify_03_sources(repository_root)

    except SourcesVerificationError as error:
        raise TransformationsVerificationError(str(error)) from error

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

    transformations = data.get("transformations")

    if not isinstance(transformations, dict):
        raise TransformationsVerificationError(
            "05-transformations.toml is missing [transformations]"
        )

    if transformations.get("sources_record") != SOURCES_RECORD.as_posix():
        raise TransformationsVerificationError(
            "05-transformations.toml records an unexpected sources path"
        )

    if transformations.get("corpus_record") != CORPUS_FILE.as_posix():
        raise TransformationsVerificationError(
            "05-transformations.toml records an unexpected corpus path"
        )

    try:
        verify_file_hash(
            repository_root,
            SOURCES_RECORD.as_posix(),
            transformations.get("sources_record_sha256"),
            label="05-transformations.toml sources record",
        )

        verify_file_hash(
            repository_root,
            CORPUS_FILE.as_posix(),
            transformations.get("corpus_record_sha256"),
            label="05-transformations.toml corpus record",
        )

        verify_hash_table(
            repository_root,
            data.get("transformations_code_sha256"),
            table_name="transformations_code_sha256",
        )

    except HashVerificationError as error:
        raise TransformationsVerificationError(str(error)) from error

    source_rows = sources_data.get("source")
    converters = data.get("converter")
    routes = data.get("route")
    validator = data.get("target_validator")

    if not isinstance(source_rows, list) or not source_rows:
        raise TransformationsVerificationError(
            "04-sources.toml contains no [[source]] entries"
        )

    if not isinstance(converters, list) or not converters:
        raise TransformationsVerificationError(
            "05-transformations.toml contains no [[converter]] entries"
        )

    if not isinstance(routes, list) or not routes:
        raise TransformationsVerificationError(
            "05-transformations.toml contains no [[route]] entries"
        )

    if not isinstance(validator, dict):
        raise TransformationsVerificationError(
            "05-transformations.toml is missing [target_validator]"
        )

    sources_by_study_id: dict[str, tuple[str, str]] = {}

    for index, row in enumerate(source_rows):
        where = f"source[{index}]"

        if not isinstance(row, dict):
            raise TransformationsVerificationError(f"{where} must be a table")

        study_id = _required_string(row, "study_id", where)
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

    converter_ids: set[str] = set()

    for index, converter in enumerate(converters):
        where = f"converter[{index}]"

        if not isinstance(converter, dict):
            raise TransformationsVerificationError(f"{where} must be a table")

        converter_id = _required_string(converter, "id", where)
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

        if converter_id in converter_ids:
            raise TransformationsVerificationError(
                f"duplicate converter id: {converter_id}"
            )

        converter_ids.add(converter_id)

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

            try:
                verify_file_hash(
                    repository_root,
                    runtime_path,
                    runtime_sha256,
                    label=f"converter {converter_id} runtime",
                )

            except HashVerificationError as error:
                raise TransformationsVerificationError(str(error)) from error

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

    route_ids: set[str] = set()
    observed_pairs: set[tuple[str, str]] = set()
    status_counts: Counter[str] = Counter()

    for index, route in enumerate(routes):
        where = f"route[{index}]"

        if not isinstance(route, dict):
            raise TransformationsVerificationError(f"{where} must be a table")

        route_id = _required_string(route, "route_id", where)
        study_id = _required_string(route, "study_id", where)
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
        status = _required_string(route, "status", where)

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

        if converter_id not in converter_ids:
            raise TransformationsVerificationError(
                f"{route_id} references unknown converter_id {converter_id!r}"
            )

        if (source_path, source_sha256) != expected_source:
            raise TransformationsVerificationError(
                f"{route_id} source path/hash does not match 04-sources.toml"
            )

        expected_route_id = f"{study_id}--{converter_id}"

        if route_id != expected_route_id:
            raise TransformationsVerificationError(
                f"{route_id} does not equal expected route id {expected_route_id}"
            )

        pair = (study_id, converter_id)

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

            if validation_required is not True:
                raise TransformationsVerificationError(
                    f"{route_id} is planned but validation_required is not true"
                )

            if not isinstance(validation_argv, list) or not validation_argv:
                raise TransformationsVerificationError(
                    f"{route_id} is planned but has no validation_command_argv"
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

    expected_pairs = {
        (study_id, converter_id)
        for study_id in sources_by_study_id
        for converter_id in converter_ids
    }

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

    if transformations.get("execution_state") != "not_started":
        raise TransformationsVerificationError(
            "[transformations].execution_state must be 'not_started' before Freeze 02"
        )

    if transformations.get("transformation_outputs_examined") is not False:
        raise TransformationsVerificationError(
            "[transformations].transformation_outputs_examined must be false"
        )

    return path
