"""Verify the complete repository state required before creating Freeze 02.

Freeze 02 verification composes the independent verifiers for:
- Freeze 01 integrity,
- the selected corpus,
- preserved source artifacts, and
- the transformation matrix.

This module performs no writes.
"""

from pathlib import Path

from preservation_test.generalization.verification.verify_corpus import (
    verify_corpus,
)
from preservation_test.generalization.verification.verify_freeze_01 import (
    verify_freeze_01,
)
from preservation_test.generalization.verification.verify_sources import (
    verify_sources,
)
from preservation_test.generalization.verification.verify_transformations import (
    verify_transformations,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[4]


def verify_freeze_02(repository_root: Path) -> None:
    """Verify all currently defined Freeze 02 prerequisites."""
    verify_freeze_01(repository_root)
    verify_corpus(repository_root)
    verify_sources(repository_root)
    verify_transformations(repository_root)


def main() -> None:
    """Verify Freeze 02 prerequisites from the current repository."""
    verify_freeze_02(REPOSITORY_ROOT)
    print("Freeze 02 prerequisites verified.")


if __name__ == "__main__":
    main()
