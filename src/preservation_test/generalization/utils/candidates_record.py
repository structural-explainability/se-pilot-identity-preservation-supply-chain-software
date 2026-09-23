"""Strictly load a 02-candidates.toml record back into Candidate objects.

Every field of Candidate and CandidateScreening must be present with the
recorded type, and no unknown fields are accepted. A hand-edited or
truncated record fails to load rather than being silently reinterpreted.
"""

from dataclasses import dataclass, fields
from pathlib import Path
import tomllib
from typing import Any

from preservation_test.generalization.models.candidate import Candidate
from preservation_test.generalization.models.candidate_screening import (
    CandidateScreening,
)
from preservation_test.generalization.utils.hashing import sha256_file


class CandidatesRecordError(ValueError):
    """Raised when 02-candidates.toml is malformed or incomplete."""


@dataclass(frozen=True)
class CandidatesRecord:
    """Parsed 02-candidates.toml."""

    path: Path
    sha256: str
    screening: dict[str, Any]
    screening_code_sha256: dict[str, str]
    candidates: tuple[Candidate, ...]


def _typed(value: Any, annotation: Any, where: str) -> Any:
    text = str(annotation)
    if annotation is bool:
        if not isinstance(value, bool):
            raise CandidatesRecordError(f"{where} must be a boolean")
        return value
    if annotation is int:
        if isinstance(value, bool) or not isinstance(value, int):
            raise CandidatesRecordError(f"{where} must be an integer")
        return value
    if annotation is str:
        if not isinstance(value, str):
            raise CandidatesRecordError(f"{where} must be a string")
        return value
    if text == "tuple[str, ...]":
        if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
            raise CandidatesRecordError(f"{where} must be a list of strings")
        return tuple(value)
    raise CandidatesRecordError(f"{where}: unsupported field type {text}")


def _build(cls: Any, data: Any, where: str, nested: dict[str, Any]) -> Any:
    if not isinstance(data, dict):
        raise CandidatesRecordError(f"{where} must be a table")
    names = [f.name for f in fields(cls)]
    missing = [name for name in names if name not in data]
    unknown = [key for key in data if key not in names]
    if missing or unknown:
        raise CandidatesRecordError(
            f"{where}: missing fields {missing}, unknown fields {unknown}"
        )
    values: dict[str, Any] = {}
    for field in fields(cls):
        location = f"{where}.{field.name}"
        if field.name in nested:
            values[field.name] = _build(
                nested[field.name], data[field.name], location, {}
            )
        else:
            values[field.name] = _typed(data[field.name], field.type, location)
    return cls(**values)


def load_candidates_record(path: Path) -> CandidatesRecord:
    """Load and structurally validate 02-candidates.toml."""
    with path.open("rb") as handle:
        data = tomllib.load(handle)

    screening = data.get("screening")
    code = data.get("screening_code_sha256")
    rows = data.get("candidate")
    if not isinstance(screening, dict):
        raise CandidatesRecordError("missing [screening] table")
    if not isinstance(code, dict) or not all(isinstance(v, str) for v in code.values()):
        raise CandidatesRecordError(
            "missing or malformed [screening_code_sha256] table"
        )
    if not isinstance(rows, list):
        raise CandidatesRecordError("missing [[candidate]] entries")

    candidates = tuple(
        _build(Candidate, row, f"candidate[{index}]", {"screening": CandidateScreening})
        for index, row in enumerate(rows)
    )
    return CandidatesRecord(
        path=path,
        sha256=sha256_file(path),
        screening=screening,
        screening_code_sha256=dict(code),
        candidates=candidates,
    )
