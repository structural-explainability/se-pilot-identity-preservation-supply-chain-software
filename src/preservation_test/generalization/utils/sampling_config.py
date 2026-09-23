"""Load and validate the predeclared sampling specification (01-sampling.toml).

Loading is strict. Anything this code cannot apply mechanically, or any
unfilled placeholder, is an error rather than a silently skipped rule.
"""

from dataclasses import dataclass
from pathlib import Path
import re
import tomllib
from typing import Any

from preservation_test.generalization.utils.hashing import (
    normalize_sha256,
    sha256_file,
)

SUPPORTED_SCHEMA_VERSION = 1
SUPPORTED_SELECTION_METHOD = "census-of-eligible-units"
SUPPORTED_SELECTION_UNIT = "source_standard + subject"
SUPPORTED_ONE_DOCUMENT_PER_UNIT = (
    "lowest source SHA-256 among eligible documents "
    "for the same source_standard and subject"
)
SUPPORTED_SERIALIZATION = "json"
EXCLUSION_KINDS = frozenset({"sha256", "subject"})
PLACEHOLDER = "..."

_REVISION = re.compile(r"^[0-9a-f]{40}$")
_SUFFIX_FILTER = re.compile(r"^\*(\.[A-Za-z0-9]+)$")


class SamplingConfigError(ValueError):
    """Raised when the sampling specification cannot be applied mechanically."""


@dataclass(frozen=True)
class RepositorySpec:
    """One repository in the fixed sampling frame."""

    name: str
    url: str
    revision: str


@dataclass(frozen=True)
class FormatsSpec:
    """In-scope source standards, specification versions, and serialization."""

    spdx_versions: tuple[str, ...]
    cyclonedx_spec_versions: tuple[str, ...]
    serialization: str


@dataclass(frozen=True)
class ValidationExclusion:
    """One predeclared engineering-validation exclusion."""

    kind: str
    value: str
    reason: str
    provenance: str


@dataclass(frozen=True)
class SamplingConfig:
    """Validated sampling specification."""

    path: Path
    sha256: str
    sampling_id: str
    repositories: tuple[RepositorySpec, ...]
    path_suffix: str
    formats: FormatsSpec
    validation_exclusions: tuple[ValidationExclusion, ...]
    selection_method: str
    selection_unit: str
    one_document_per_unit: str

    def excluded_sha256(self) -> frozenset[str]:
        """Return SHA-256 digests excluded as engineering-validation artifacts."""
        return frozenset(
            item.value for item in self.validation_exclusions if item.kind == "sha256"
        )

    def excluded_subjects(self) -> frozenset[str]:
        """Return subject keys excluded as engineering-validation subjects."""
        return frozenset(
            item.value for item in self.validation_exclusions if item.kind == "subject"
        )


def _table(data: dict[str, Any], key: str) -> dict[str, Any]:
    value = data.get(key)
    if not isinstance(value, dict):
        raise SamplingConfigError(f"missing table [{key}]")
    return value


def _string(data: dict[str, Any], key: str, where: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise SamplingConfigError(f"{where}.{key} must be a non-empty string")
    if PLACEHOLDER in value:
        raise SamplingConfigError(f"{where}.{key} still contains a placeholder")
    return value.strip()


def _strings(data: dict[str, Any], key: str, where: str) -> tuple[str, ...]:
    value = data.get(key)
    if not isinstance(value, list) or not value:
        raise SamplingConfigError(f"{where}.{key} must be a non-empty list")
    if not all(isinstance(item, str) and item for item in value):
        raise SamplingConfigError(f"{where}.{key} must contain only strings")
    return tuple(value)


def _repositories(frame: dict[str, Any]) -> tuple[RepositorySpec, ...]:
    entries = frame.get("repository")
    if not isinstance(entries, list) or not entries:
        raise SamplingConfigError("[[sampling_frame.repository]] is required")

    repositories: list[RepositorySpec] = []
    for index, entry in enumerate(entries):
        where = f"sampling_frame.repository[{index}]"
        if not isinstance(entry, dict):
            raise SamplingConfigError(f"{where} must be a table")
        name = _string(entry, "name", where)
        url = _string(entry, "url", where)
        revision = _string(entry, "revision", where)
        if not _REVISION.match(revision):
            raise SamplingConfigError(f"{where}.revision must be a full 40-hex commit")
        repositories.append(RepositorySpec(name=name, url=url, revision=revision))

    names = [repository.name for repository in repositories]
    if len(set(names)) != len(names):
        raise SamplingConfigError("sampling frame repositories must be unique")
    return tuple(repositories)


def _path_suffix(frame: dict[str, Any]) -> str:
    enumeration = _table(frame, "enumeration")
    path_filter = _string(enumeration, "path_filter", "sampling_frame.enumeration")
    match = _SUFFIX_FILTER.match(path_filter)
    if not match:
        raise SamplingConfigError(
            f"unsupported path_filter {path_filter!r}; expected '*.<ext>'"
        )
    content_source = _string(
        enumeration, "content_source", "sampling_frame.enumeration"
    )
    if content_source != "git blob at fixed revision":
        raise SamplingConfigError(f"unsupported content_source {content_source!r}")
    return match.group(1)


def _formats(data: dict[str, Any]) -> FormatsSpec:
    table = _table(data, "formats")
    serialization = _string(table, "serialization", "formats")
    if serialization != SUPPORTED_SERIALIZATION:
        raise SamplingConfigError(f"unsupported serialization {serialization!r}")
    return FormatsSpec(
        spdx_versions=_strings(table, "spdx_versions", "formats"),
        cyclonedx_spec_versions=_strings(table, "cyclonedx_spec_versions", "formats"),
        serialization=serialization,
    )


def _validation_exclusions(data: dict[str, Any]) -> tuple[ValidationExclusion, ...]:
    entries = data.get("validation_exclusion")
    if not isinstance(entries, list) or not entries:
        raise SamplingConfigError("[[validation_exclusion]] entries are required")

    exclusions: list[ValidationExclusion] = []
    for index, entry in enumerate(entries):
        where = f"validation_exclusion[{index}]"
        if not isinstance(entry, dict):
            raise SamplingConfigError(f"{where} must be a table")
        kind = _string(entry, "kind", where)
        if kind not in EXCLUSION_KINDS:
            raise SamplingConfigError(
                f"{where}.kind must be one of {sorted(EXCLUSION_KINDS)}"
            )
        value = _string(entry, "value", where)
        if kind == "sha256":
            try:
                value = normalize_sha256(value)
            except ValueError as error:
                raise SamplingConfigError(f"{where}.value: {error}") from error
        exclusions.append(
            ValidationExclusion(
                kind=kind,
                value=value,
                reason=_string(entry, "reason", where),
                provenance=_string(entry, "provenance", where),
            )
        )
    return tuple(exclusions)


def _selection_boundary(data: dict[str, Any]) -> None:
    boundary = _table(data, "selection_boundary")
    for key, value in boundary.items():
        if value is not False:
            raise SamplingConfigError(f"selection_boundary.{key} must be false")


def load_sampling_config(path: Path) -> SamplingConfig:
    """Load 01-sampling.toml and validate every rule screening depends on."""
    with path.open("rb") as handle:
        data = tomllib.load(handle)

    if data.get("schema_version") != SUPPORTED_SCHEMA_VERSION:
        raise SamplingConfigError(f"schema_version must be {SUPPORTED_SCHEMA_VERSION}")

    frame = _table(data, "sampling_frame")
    selection = _table(data, "selection")
    unit = _table(data, "unit")

    selection_method = _string(selection, "method", "selection")
    if selection_method != SUPPORTED_SELECTION_METHOD:
        raise SamplingConfigError(f"unsupported selection.method {selection_method!r}")

    selection_unit = _string(unit, "selection_unit", "unit")
    if selection_unit != SUPPORTED_SELECTION_UNIT:
        raise SamplingConfigError(f"unsupported unit.selection_unit {selection_unit!r}")
    one_document_per_unit = _string(
        unit,
        "one_document_per_unit",
        "unit",
    )
    if one_document_per_unit != SUPPORTED_ONE_DOCUMENT_PER_UNIT:
        raise SamplingConfigError(
            f"unsupported unit.one_document_per_unit {one_document_per_unit!r}"
        )
    _selection_boundary(data)

    return SamplingConfig(
        path=path,
        sha256=sha256_file(path),
        sampling_id=_string(data, "sampling_id", "root"),
        repositories=_repositories(frame),
        path_suffix=_path_suffix(frame),
        formats=_formats(data),
        validation_exclusions=_validation_exclusions(data),
        selection_method=selection_method,
        selection_unit=selection_unit,
        one_document_per_unit=one_document_per_unit,
    )
