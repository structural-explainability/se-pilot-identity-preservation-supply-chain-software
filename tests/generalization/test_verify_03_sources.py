"""Tests for preserved-source Freeze 02 verification."""

from hashlib import sha256
from pathlib import Path

import pytest

import preservation_test.generalization.verification.verify_03_sources as verify_module


def _sha256(data: bytes) -> str:
    """Return the SHA-256 digest for test bytes."""
    return sha256(data).hexdigest()


def _write_corpus(
    repository_root: Path,
    members: list[tuple[str, str]],
) -> Path:
    """Write a minimal 03-corpus.toml for verifier tests."""
    path = repository_root / "generalization" / "03-corpus.toml"
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# test corpus",
        "",
    ]

    for study_id, digest in members:
        lines.extend(
            [
                "[[member]]",
                f'study_id = "{study_id}"',
                f'sha256 = "{digest}"',
                "",
            ]
        )

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _write_code_file(repository_root: Path) -> tuple[str, str]:
    """Write one repository file used by sources_code_sha256."""
    relative_path = "src/test_source_preservation_code.py"
    path = repository_root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)

    data = b'"""Test provenance file."""\n'
    path.write_bytes(data)

    return relative_path, _sha256(data)


def _write_preserved_source(
    repository_root: Path,
    study_id: str,
    data: bytes,
) -> tuple[str, str]:
    """Write one preserved source and return its path and digest."""
    relative_path = f"generalization/sources/{study_id}.spdx.json"
    path = repository_root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)

    return relative_path, _sha256(data)


def _source_row(
    *,
    study_id: str,
    preserved_path: str,
    corpus_sha256: str,
    preserved_sha256: str,
    size_bytes: int,
) -> str:
    """Render one minimal [[source]] row."""
    return "\n".join(
        [
            "[[source]]",
            f'study_id = "{study_id}"',
            f'preserved_path = "{preserved_path}"',
            f'corpus_sha256 = "{corpus_sha256}"',
            f'preserved_sha256 = "{preserved_sha256}"',
            f"size_bytes = {size_bytes}",
            "",
        ]
    )


def _write_sources_record(
    repository_root: Path,
    *,
    corpus_sha256: str,
    member_count: int,
    rows: list[str],
) -> Path:
    """Write a minimal 04-sources.toml for verifier tests."""
    code_path, code_sha256 = _write_code_file(repository_root)

    path = repository_root / "generalization" / "04-sources.toml"
    path.parent.mkdir(parents=True, exist_ok=True)

    text = "\n".join(
        [
            "[sources]",
            'corpus_record = "generalization/03-corpus.toml"',
            f'corpus_record_sha256 = "{corpus_sha256}"',
            f"members = {member_count}",
            "",
            "[sources_code_sha256]",
            f'"{code_path}" = "{code_sha256}"',
            "",
            *rows,
        ]
    )

    path.write_text(text, encoding="utf-8")
    return path


def _prepare_valid_repository(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[Path, Path, bytes, str]:
    """Create one internally consistent 03 -> 04 -> source chain."""
    source_data = b'{"name": "example"}\n'
    source_digest = _sha256(source_data)

    corpus_path = _write_corpus(
        tmp_path,
        [("source-a", source_digest)],
    )

    preserved_path, _ = _write_preserved_source(
        tmp_path,
        "source-a",
        source_data,
    )

    sources_path = _write_sources_record(
        tmp_path,
        corpus_sha256=_sha256(corpus_path.read_bytes()),
        member_count=1,
        rows=[
            _source_row(
                study_id="source-a",
                preserved_path=preserved_path,
                corpus_sha256=source_digest,
                preserved_sha256=source_digest,
                size_bytes=len(source_data),
            )
        ],
    )

    monkeypatch.setattr(
        verify_module,
        "verify_02_corpus",
        lambda repository_root: corpus_path,
    )

    return corpus_path, sources_path, source_data, source_digest


def test_verify_03_sources_accepts_valid_preserved_source_chain(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A consistent corpus, source record, and preserved file passes."""
    _, sources_path, _, _ = _prepare_valid_repository(
        tmp_path,
        monkeypatch,
    )

    result = verify_module.verify_03_sources(tmp_path)

    assert result == sources_path


def test_verify_03_sources_propagates_corpus_verification_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Failure of the preceding corpus verifier blocks source verification."""

    def fail_corpus_verification(repository_root: Path) -> Path:
        raise verify_module.CorpusVerificationError("corpus verification failed")

    monkeypatch.setattr(
        verify_module,
        "verify_02_corpus",
        fail_corpus_verification,
    )

    with pytest.raises(
        verify_module.SourcesVerificationError,
        match="corpus verification failed",
    ):
        verify_module.verify_03_sources(tmp_path)


def test_verify_03_sources_rejects_missing_sources_record(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """04-sources.toml must exist."""
    corpus_path = _write_corpus(
        tmp_path,
        [("source-a", "0" * 64)],
    )

    monkeypatch.setattr(
        verify_module,
        "verify_02_corpus",
        lambda repository_root: corpus_path,
    )

    with pytest.raises(
        verify_module.SourcesVerificationError,
        match="source record not found",
    ):
        verify_module.verify_03_sources(tmp_path)


def test_verify_03_sources_rejects_corpus_record_hash_mismatch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """04 must identify the current exact 03-corpus.toml bytes."""
    source_data = b"source\n"
    source_digest = _sha256(source_data)

    corpus_path = _write_corpus(
        tmp_path,
        [("source-a", source_digest)],
    )

    preserved_path, _ = _write_preserved_source(
        tmp_path,
        "source-a",
        source_data,
    )

    _write_sources_record(
        tmp_path,
        corpus_sha256="0" * 64,
        member_count=1,
        rows=[
            _source_row(
                study_id="source-a",
                preserved_path=preserved_path,
                corpus_sha256=source_digest,
                preserved_sha256=source_digest,
                size_bytes=len(source_data),
            )
        ],
    )

    monkeypatch.setattr(
        verify_module,
        "verify_02_corpus",
        lambda repository_root: corpus_path,
    )

    with pytest.raises(
        verify_module.SourcesVerificationError,
        match="corpus record hash mismatch",
    ):
        verify_module.verify_03_sources(tmp_path)


def test_verify_03_sources_rejects_missing_preserved_source(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Every source record must resolve to an existing preserved file."""
    source_data = b"source\n"
    source_digest = _sha256(source_data)

    corpus_path = _write_corpus(
        tmp_path,
        [("source-a", source_digest)],
    )

    _write_sources_record(
        tmp_path,
        corpus_sha256=_sha256(corpus_path.read_bytes()),
        member_count=1,
        rows=[
            _source_row(
                study_id="source-a",
                preserved_path=("generalization/sources/source-a.spdx.json"),
                corpus_sha256=source_digest,
                preserved_sha256=source_digest,
                size_bytes=len(source_data),
            )
        ],
    )

    monkeypatch.setattr(
        verify_module,
        "verify_02_corpus",
        lambda repository_root: corpus_path,
    )

    with pytest.raises(
        verify_module.SourcesVerificationError,
        match="preserved source source-a file not found",
    ):
        verify_module.verify_03_sources(tmp_path)


def test_verify_03_sources_rejects_tampered_preserved_bytes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Current preserved bytes must still match the frozen source digest."""
    _, _, _, _ = _prepare_valid_repository(
        tmp_path,
        monkeypatch,
    )

    preserved = tmp_path / "generalization" / "sources" / "source-a.spdx.json"
    preserved.write_bytes(b'{"name": "tampered"}\n')

    with pytest.raises(
        verify_module.SourcesVerificationError,
        match="preserved source source-a hash mismatch",
    ):
        verify_module.verify_03_sources(tmp_path)


def test_verify_03_sources_rejects_corpus_sha_difference_between_03_and_04(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A source row cannot change the SHA-256 selected by 03."""
    source_data = b"source\n"
    source_digest = _sha256(source_data)
    other_digest = _sha256(b"other\n")

    corpus_path = _write_corpus(
        tmp_path,
        [("source-a", source_digest)],
    )

    preserved_path, _ = _write_preserved_source(
        tmp_path,
        "source-a",
        source_data,
    )

    _write_sources_record(
        tmp_path,
        corpus_sha256=_sha256(corpus_path.read_bytes()),
        member_count=1,
        rows=[
            _source_row(
                study_id="source-a",
                preserved_path=preserved_path,
                corpus_sha256=other_digest,
                preserved_sha256=other_digest,
                size_bytes=len(source_data),
            )
        ],
    )

    monkeypatch.setattr(
        verify_module,
        "verify_02_corpus",
        lambda repository_root: corpus_path,
    )

    with pytest.raises(
        verify_module.SourcesVerificationError,
        match="corpus SHA-256 differs between 03 and 04",
    ):
        verify_module.verify_03_sources(tmp_path)


def test_verify_03_sources_rejects_preserved_sha_difference_from_corpus(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The preserved digest recorded in 04 must equal the corpus digest."""
    source_data = b"source\n"
    source_digest = _sha256(source_data)
    other_digest = _sha256(b"other\n")

    corpus_path = _write_corpus(
        tmp_path,
        [("source-a", source_digest)],
    )

    preserved_path, _ = _write_preserved_source(
        tmp_path,
        "source-a",
        source_data,
    )

    _write_sources_record(
        tmp_path,
        corpus_sha256=_sha256(corpus_path.read_bytes()),
        member_count=1,
        rows=[
            _source_row(
                study_id="source-a",
                preserved_path=preserved_path,
                corpus_sha256=source_digest,
                preserved_sha256=other_digest,
                size_bytes=len(source_data),
            )
        ],
    )

    monkeypatch.setattr(
        verify_module,
        "verify_02_corpus",
        lambda repository_root: corpus_path,
    )

    with pytest.raises(
        verify_module.SourcesVerificationError,
        match="preserved SHA-256 differs from its corpus SHA-256",
    ):
        verify_module.verify_03_sources(tmp_path)


def test_verify_03_sources_rejects_recorded_size_mismatch(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Recorded source size must equal the current preserved byte length."""
    source_data = b"source\n"
    source_digest = _sha256(source_data)

    corpus_path = _write_corpus(
        tmp_path,
        [("source-a", source_digest)],
    )

    preserved_path, _ = _write_preserved_source(
        tmp_path,
        "source-a",
        source_data,
    )

    _write_sources_record(
        tmp_path,
        corpus_sha256=_sha256(corpus_path.read_bytes()),
        member_count=1,
        rows=[
            _source_row(
                study_id="source-a",
                preserved_path=preserved_path,
                corpus_sha256=source_digest,
                preserved_sha256=source_digest,
                size_bytes=len(source_data) + 1,
            )
        ],
    )

    monkeypatch.setattr(
        verify_module,
        "verify_02_corpus",
        lambda repository_root: corpus_path,
    )

    with pytest.raises(
        verify_module.SourcesVerificationError,
        match="preserved size differs from recorded size_bytes",
    ):
        verify_module.verify_03_sources(tmp_path)


def test_verify_03_sources_rejects_missing_corpus_member(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Every corpus study ID must appear exactly once in 04."""
    source_a = b"source-a\n"
    source_b = b"source-b\n"
    digest_a = _sha256(source_a)
    digest_b = _sha256(source_b)

    corpus_path = _write_corpus(
        tmp_path,
        [
            ("source-a", digest_a),
            ("source-b", digest_b),
        ],
    )

    preserved_path, _ = _write_preserved_source(
        tmp_path,
        "source-a",
        source_a,
    )

    _write_sources_record(
        tmp_path,
        corpus_sha256=_sha256(corpus_path.read_bytes()),
        member_count=1,
        rows=[
            _source_row(
                study_id="source-a",
                preserved_path=preserved_path,
                corpus_sha256=digest_a,
                preserved_sha256=digest_a,
                size_bytes=len(source_a),
            )
        ],
    )

    monkeypatch.setattr(
        verify_module,
        "verify_02_corpus",
        lambda repository_root: corpus_path,
    )

    with pytest.raises(
        verify_module.SourcesVerificationError,
        match="03/04 study_id sets differ",
    ):
        verify_module.verify_03_sources(tmp_path)


def test_verify_03_sources_rejects_unexpected_source_record(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """04 cannot introduce a study ID that was not selected in 03."""
    source_a = b"source-a\n"
    source_b = b"source-b\n"
    digest_a = _sha256(source_a)
    digest_b = _sha256(source_b)

    corpus_path = _write_corpus(
        tmp_path,
        [("source-a", digest_a)],
    )

    path_a, _ = _write_preserved_source(
        tmp_path,
        "source-a",
        source_a,
    )
    path_b, _ = _write_preserved_source(
        tmp_path,
        "source-b",
        source_b,
    )

    _write_sources_record(
        tmp_path,
        corpus_sha256=_sha256(corpus_path.read_bytes()),
        member_count=2,
        rows=[
            _source_row(
                study_id="source-a",
                preserved_path=path_a,
                corpus_sha256=digest_a,
                preserved_sha256=digest_a,
                size_bytes=len(source_a),
            ),
            _source_row(
                study_id="source-b",
                preserved_path=path_b,
                corpus_sha256=digest_b,
                preserved_sha256=digest_b,
                size_bytes=len(source_b),
            ),
        ],
    )

    monkeypatch.setattr(
        verify_module,
        "verify_02_corpus",
        lambda repository_root: corpus_path,
    )

    with pytest.raises(
        verify_module.SourcesVerificationError,
        match="exists in 04-sources.toml but not 03-corpus.toml",
    ):
        verify_module.verify_03_sources(tmp_path)


def test_verify_03_sources_rejects_duplicate_preserved_path(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Two selected sources cannot resolve to the same preserved path."""
    source_data = b"source\n"
    source_digest = _sha256(source_data)

    corpus_path = _write_corpus(
        tmp_path,
        [
            ("source-a", source_digest),
            ("source-b", source_digest),
        ],
    )

    preserved_path, _ = _write_preserved_source(
        tmp_path,
        "shared",
        source_data,
    )

    _write_sources_record(
        tmp_path,
        corpus_sha256=_sha256(corpus_path.read_bytes()),
        member_count=2,
        rows=[
            _source_row(
                study_id="source-a",
                preserved_path=preserved_path,
                corpus_sha256=source_digest,
                preserved_sha256=source_digest,
                size_bytes=len(source_data),
            ),
            _source_row(
                study_id="source-b",
                preserved_path=preserved_path,
                corpus_sha256=source_digest,
                preserved_sha256=source_digest,
                size_bytes=len(source_data),
            ),
        ],
    )

    monkeypatch.setattr(
        verify_module,
        "verify_02_corpus",
        lambda repository_root: corpus_path,
    )

    with pytest.raises(
        verify_module.SourcesVerificationError,
        match="duplicate preserved_path in 04-sources.toml",
    ):
        verify_module.verify_03_sources(tmp_path)
