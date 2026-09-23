"""Verify the transformation-matrix stage required for Freeze 02.

This module intentionally refuses verification until
05-transformations.toml has been populated. Converter, route, version,
and executable-hash checks will be added when p04 is implemented.
"""

from pathlib import Path

TRANSFORMATIONS_FILE = Path("generalization/05-transformations.toml")


class TransformationsVerificationError(RuntimeError):
    """Raised when transformation definitions are not ready for Freeze 02."""


def verify_transformations(repository_root: Path) -> Path:
    """Require a populated transformation matrix before Freeze 02 can proceed."""
    path = repository_root / TRANSFORMATIONS_FILE

    if not path.is_file():
        raise TransformationsVerificationError(
            f"transformation matrix not found: {path}"
        )

    if path.stat().st_size == 0:
        raise TransformationsVerificationError(
            "generalization/05-transformations.toml is not populated"
        )

    return path
