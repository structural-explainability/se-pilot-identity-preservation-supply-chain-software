"""Tests for p02 deterministic corpus construction."""

from pathlib import Path
from types import SimpleNamespace
from typing import cast

import pytest

from preservation_test.generalization.models.candidate import Candidate
from preservation_test.generalization.p02_build_corpus import (
    EXIT_REFUSED,
    CorpusRefusal,
    build_corpus,
    refuse_undetermined_units,
)


def _candidate(
    candidate_id: str,
    sha256: str,
) -> Candidate:
    value = SimpleNamespace(
        id=candidate_id,
        source_standard="cyclonedx",
        subject="example@1.0",
        sha256=sha256,
        screening=SimpleNamespace(eligible=True),
    )
    return cast(Candidate, value)


def test_refuses_shared_lowest_sha256_within_unit() -> None:
    digest = "a" * 64

    candidates = (
        _candidate("candidate-a", digest),
        _candidate("candidate-b", digest),
    )

    with pytest.raises(
        CorpusRefusal,
        match="lowest SHA-256 is shared",
    ):
        refuse_undetermined_units(candidates)


def test_accepts_unique_lowest_sha256_within_unit() -> None:
    candidates = (
        _candidate("candidate-a", "a" * 64),
        _candidate("candidate-b", "b" * 64),
    )

    refuse_undetermined_units(candidates)


def test_build_corpus_refuses_to_overwrite_existing_output(
    tmp_path: Path,
) -> None:
    config = tmp_path / "01-sampling.toml"
    candidates = tmp_path / "02-candidates.toml"
    out = tmp_path / "03-corpus.toml"

    out.write_text("existing", encoding="utf-8")

    result = build_corpus(
        config_path=config,
        candidates_path=candidates,
        out=out,
    )

    assert result == EXIT_REFUSED
    assert out.read_text(encoding="utf-8") == "existing"
