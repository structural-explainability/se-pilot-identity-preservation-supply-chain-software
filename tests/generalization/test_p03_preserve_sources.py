"""Tests for p03 exact source-byte preservation."""

from pathlib import Path
import subprocess

import pytest

from preservation_test.generalization.p03_preserve_sources import (
    CorpusMember,
    SourcePreservationError,
    _materialize,
    _require_clean_destination,
    _source_suffix,
)
from preservation_test.generalization.utils.hashing import sha256_bytes


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def test_source_suffix_is_standard_specific() -> None:
    assert _source_suffix("cyclonedx") == "cdx.json"
    assert _source_suffix("spdx") == "spdx.json"

    with pytest.raises(SourcePreservationError):
        _source_suffix("unknown")


def test_clean_destination_rejects_existing_record(
    tmp_path: Path,
) -> None:
    sources_dir = tmp_path / "sources"
    record = tmp_path / "04-sources.toml"

    record.write_text("existing", encoding="utf-8")

    with pytest.raises(
        SourcePreservationError,
        match="refusing to overwrite",
    ):
        _require_clean_destination(sources_dir, record)


def test_clean_destination_rejects_existing_source_evidence(
    tmp_path: Path,
) -> None:
    sources_dir = tmp_path / "sources"
    sources_dir.mkdir()

    (sources_dir / "existing.json").write_bytes(b"evidence")

    record = tmp_path / "04-sources.toml"

    with pytest.raises(
        SourcePreservationError,
        match="sources directory is not empty",
    ):
        _require_clean_destination(sources_dir, record)


def test_materialize_reads_exact_git_blob_bytes(
    tmp_path: Path,
) -> None:
    clone_root = tmp_path / "clones"
    repo = clone_root / "examples"
    repo.mkdir(parents=True)

    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "test@example.org")
    _git(repo, "config", "user.name", "test")
    _git(repo, "config", "core.autocrlf", "false")

    data = b'{"bomFormat":"CycloneDX"}'

    source = repo / "bom.json"
    source.write_bytes(data)

    _git(repo, "add", "bom.json")
    _git(repo, "commit", "-q", "-m", "fixture")

    revision = _git(repo, "rev-parse", "HEAD")

    member = CorpusMember(
        study_id="gen-cyclonedx-test",
        candidate_id="Example/examples:bom.json",
        repository="Example/examples",
        repository_revision=revision,
        repository_relative_path="bom.json",
        sha256=sha256_bytes(data),
        source_standard="cyclonedx",
    )

    sources_dir = tmp_path / "sources"

    materialized = _materialize(
        members=(member,),
        clone_root=clone_root,
        sources_dir=sources_dir,
    )

    assert len(materialized) == 1
    assert materialized[0].data == data
    assert materialized[0].member == member
    assert materialized[0].preserved_path == (
        sources_dir / "gen-cyclonedx-test.cdx.json"
    )


def test_materialize_refuses_blob_hash_mismatch(
    tmp_path: Path,
) -> None:
    clone_root = tmp_path / "clones"
    repo = clone_root / "examples"
    repo.mkdir(parents=True)

    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "test@example.org")
    _git(repo, "config", "user.name", "test")

    (repo / "bom.json").write_bytes(b'{"bomFormat":"CycloneDX"}')

    _git(repo, "add", "bom.json")
    _git(repo, "commit", "-q", "-m", "fixture")

    revision = _git(repo, "rev-parse", "HEAD")

    member = CorpusMember(
        study_id="gen-cyclonedx-test",
        candidate_id="Example/examples:bom.json",
        repository="Example/examples",
        repository_revision=revision,
        repository_relative_path="bom.json",
        sha256="0" * 64,
        source_standard="cyclonedx",
    )

    with pytest.raises(
        SourcePreservationError,
        match="selected source bytes do not match",
    ):
        _materialize(
            members=(member,),
            clone_root=clone_root,
            sources_dir=tmp_path / "sources",
        )
