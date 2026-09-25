"""Verification stage 05: verify all prerequisites for creating Freeze 02.

Purpose
-------
Freeze 02 establishes the final pre-outcome boundary for the held-out
generalization experiment.

This verifier is the top-level integrity gate.
It does not independently reimplement the lower-level checks.
Instead, it composes the ordered verification stages
that establish the complete provenance chain from the
frozen commitment/evaluator through the predeclared transformation plan.

The verification sequence is:

    verify_01_freeze_01
        |
        v
    verify_02_corpus
        |
        v
    verify_03_sources
        |
        v
    verify_04_transformations
        |
        v
    Freeze 02 prerequisites verified

Together those stages establish:

    Freeze 01 frozen artifacts
        |
        v
    01-sampling.toml
        |
        v
    02-candidates.toml
        |
        v
    03-corpus.toml
        |
        v
    04-sources.toml
        |
        v
    preserved held-out source bytes
        |
        +
        |
        +-- frozen converter artifacts
        +-- frozen runtime artifacts
        +-- frozen target validator
        |
        v
    05-transformations.toml

Successful completion means that the currently defined machine-verifiable
prerequisites for Freeze 02 are internally consistent and byte-identical to
their recorded provenance.

It does not itself create Freeze 02.

It does not run any formal generalization transformation, inspect generated
generalization output, invoke the evaluator on held-out results, or modify any
experimental artifact.

This verifier performs no writes.
"""

from pathlib import Path

from preservation_test.generalization.verification.verify_01_freeze_01 import (
    verify_01_freeze_01,
)
from preservation_test.generalization.verification.verify_02_corpus import (
    verify_02_corpus,
)
from preservation_test.generalization.verification.verify_03_sources import (
    verify_03_sources,
)
from preservation_test.generalization.verification.verify_04_transformations import (
    verify_04_transformations,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[4]


def verify_05_freeze_02(repository_root: Path) -> None:
    """Verify all currently defined Freeze 02 prerequisites."""
    verify_01_freeze_01(repository_root)
    verify_02_corpus(repository_root)
    verify_03_sources(repository_root)
    verify_04_transformations(repository_root)


def main() -> None:
    """Verify Freeze 02 prerequisites from the current repository."""
    verify_05_freeze_02(REPOSITORY_ROOT)
    print("Freeze 02 prerequisites verified.")


if __name__ == "__main__":
    main()
