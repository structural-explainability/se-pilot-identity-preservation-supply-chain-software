"""Verify a hash-based freeze record against the current file bytes.

Freeze records list frozen artifacts as lines of the form:

    - `<sha256>`  `<repository-relative path>`
"""

from pathlib import Path
import re

from preservation_test.generalization.utils.hashing import sha256_file

FREEZE_01_RECORD = Path("contracts/FREEZE_01_COMMITMENT_EVALUATOR.md")

_HASH_LINE = re.compile(r"^- `([0-9a-fA-F]{64})`\s+`([^`]+)`\s*$")


class FreezeIntegrityError(RuntimeError):
    """Raised when a freeze record is missing, empty, or does not match."""


def frozen_hashes(record: Path) -> dict[str, str]:
    """Return {relative path: sha256} listed in a freeze record."""
    if not record.is_file():
        raise FreezeIntegrityError(f"freeze record not found: {record}")
    hashes: dict[str, str] = {}
    for line in record.read_text(encoding="utf-8").splitlines():
        match = _HASH_LINE.match(line.strip())
        if match:
            hashes[match.group(2)] = match.group(1).lower()
    if not hashes:
        raise FreezeIntegrityError(f"no frozen content hashes found in {record}")
    return hashes


def verify_freeze(repository_root: Path, record: Path = FREEZE_01_RECORD) -> str:
    """Verify every frozen artifact; return the SHA-256 of the record itself."""
    record_path = repository_root / record
    problems: list[str] = []
    for relative, expected in frozen_hashes(record_path).items():
        path = repository_root / relative
        if not path.is_file():
            problems.append(f"missing: {relative}")
        elif (observed := sha256_file(path)) != expected:
            problems.append(
                f"changed: {relative} expected {expected} observed {observed}"
            )
    if problems:
        raise FreezeIntegrityError(
            f"{record} does not match the working tree:\n  " + "\n  ".join(problems)
        )
    return sha256_file(record_path)
