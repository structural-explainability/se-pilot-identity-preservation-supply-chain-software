"""Shared repository-file SHA-256 verification for generalization provenance.

Purpose
-------
Generated generalization artifacts record SHA-256 digests for upstream
artifacts, implementation files, preserved sources, converter binaries,
runtime artifacts, and other files whose exact bytes matter to the experiment.

This module provides the common mechanism used by the ordered verification
stages to check those declarations.

The helpers in this module:

1. require recorded paths to remain repository-relative;
2. reject absolute paths and parent-directory traversal;
3. require the referenced repository file to exist;
4. require recorded SHA-256 values to contain exactly 64 hexadecimal
   characters;
5. calculate SHA-256 from the file's current exact bytes;
6. compare the observed digest with the recorded digest; and
7. verify complete TOML path-to-SHA-256 tables when requested.

The fundamental invariant is:

    recorded SHA-256
        ==
    SHA-256 of current exact file bytes

This module does not decide which artifacts belong to an experimental stage.
The stage-specific verifiers define those relationships and use these helpers
to enforce their recorded byte identities.

This module performs no writes.
"""

from pathlib import Path
import re
from typing import Any

from preservation_test.generalization.utils.hashing import sha256_file

SHA256_PATTERN = re.compile(r"^[0-9a-fA-F]{64}$")


class HashVerificationError(RuntimeError):
    """Raised when a recorded SHA-256 provenance check fails."""


def _repository_file(
    repository_root: Path,
    relative_path: str,
    label: str,
) -> Path:
    """Return a repository-contained file path from one recorded relative path."""
    if not relative_path:
        raise HashVerificationError(f"{label} path must be a non-empty string")

    recorded = Path(relative_path)

    if recorded.is_absolute() or ".." in recorded.parts:
        raise HashVerificationError(
            f"{label} path must stay within the repository: {relative_path!r}"
        )

    root = repository_root.resolve()
    path = (root / recorded).resolve()

    if not path.is_relative_to(root):
        raise HashVerificationError(
            f"{label} path resolves outside the repository: {relative_path!r}"
        )

    if not path.is_file():
        raise HashVerificationError(f"{label} file not found: {relative_path}")

    return path


def verify_file_hash(
    repository_root: Path,
    relative_path: str,
    expected_sha256: str,
    *,
    label: str,
) -> Path:
    """Verify one repository file against one recorded SHA-256 digest."""
    if not isinstance(expected_sha256, str) or not SHA256_PATTERN.fullmatch(
        expected_sha256
    ):
        raise HashVerificationError(
            f"{label} SHA-256 must be exactly 64 hexadecimal characters"
        )

    path = _repository_file(repository_root, relative_path, label)
    observed_sha256 = sha256_file(path)

    if observed_sha256.lower() != expected_sha256.lower():
        raise HashVerificationError(
            "\n".join(
                [
                    f"{label} hash mismatch: {relative_path}",
                    f"expected: {expected_sha256.lower()}",
                    f"observed: {observed_sha256.lower()}",
                ]
            )
        )

    return path


def verify_hash_table(
    repository_root: Path,
    table: Any,
    *,
    table_name: str,
) -> tuple[Path, ...]:
    """Verify every path-to-SHA-256 entry in one generated TOML hash table."""
    if not isinstance(table, dict) or not table:
        raise HashVerificationError(
            f"{table_name} must be a non-empty path-to-SHA-256 table"
        )

    verified: list[Path] = []

    for relative_path, expected_sha256 in sorted(table.items()):
        if not isinstance(relative_path, str):
            raise HashVerificationError(f"{table_name} contains a non-string path key")

        verified.append(
            verify_file_hash(
                repository_root,
                relative_path,
                expected_sha256,
                label=f"{table_name}[{relative_path}]",
            )
        )

    return tuple(verified)
