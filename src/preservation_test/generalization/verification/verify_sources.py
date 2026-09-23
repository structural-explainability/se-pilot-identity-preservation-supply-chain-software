"""Verify the preserved-source stage required for Freeze 02.

This module intentionally refuses verification until 04-sources.toml has
been populated. Source-byte and hash checks will be expanded when p03 is
implemented.
"""

from pathlib import Path

SOURCES_RECORD = Path("generalization/04-sources.toml")


class SourcesVerificationError(RuntimeError):
    """Raised when preserved sources are not ready for Freeze 02."""


def verify_sources(repository_root: Path) -> Path:
    """Require a populated 04-sources.toml before Freeze 02 can proceed."""
    path = repository_root / SOURCES_RECORD

    if not path.is_file():
        raise SourcesVerificationError(f"source record not found: {path}")

    if path.stat().st_size == 0:
        raise SourcesVerificationError(
            "generalization/04-sources.toml is not populated"
        )

    return path
