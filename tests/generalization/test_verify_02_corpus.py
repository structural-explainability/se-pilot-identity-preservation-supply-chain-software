"""Tests for verification stage 02: 01 -> 02 -> 03 corpus provenance."""

from dataclasses import dataclass, field
import hashlib
from pathlib import Path

import pytest

from preservation_test.generalization.verification.verify_01_freeze_01 import (
    FREEZE_FILE,
)
from preservation_test.generalization.verification.verify_02_corpus import (
    CANDIDATES_FILE,
    CORPUS_FILE,
    SAMPLING_FILE,
    CorpusVerificationError,
    verify_02_corpus,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

SCREENING_CODE = "src/generalization/screening.py"
CORPUS_CODE = "src/generalization/p02_build_corpus.py"


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write(path: Path, data: bytes) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def _quote(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"

    if isinstance(value, int):
        return str(value)

    return f'"{value}"'


@dataclass
class Chain:
    """Controls for building a synthetic 01 -> 02 -> 03 provenance chain.

    Each field defaults to the value that produces a valid chain. A test changes
    exactly the field whose failure it verifies.
    """

    candidates_sampling_sha256: str | None = None
    corpus_sampling_sha256: str | None = None
    corpus_candidates_sha256: str | None = None
    freeze_record: str | None = FREEZE_FILE.as_posix()
    freeze_record_sha256: str | None = None
    screening_code: dict[str, str] | None = None
    corpus_code: dict[str, str] | None = None
    members_declared: int | None = None
    study_ids: list[object] = field(
        default_factory=lambda: ["gen-cyclonedx-aaa", "gen-spdx-bbb"]
    )
    include_screening_table: bool = True
    include_corpus_table: bool = True


def _build(root: Path, chain: Chain) -> Path:
    """Write a synthetic repository for one provenance chain."""
    (root / ".git").mkdir(parents=True, exist_ok=True)

    freeze_bytes = b"# Freeze 01\n"
    _write(root / FREEZE_FILE, freeze_bytes)

    screening_code_bytes = b"def screen(): ...\n"
    corpus_code_bytes = b"def build(): ...\n"
    _write(root / SCREENING_CODE, screening_code_bytes)
    _write(root / CORPUS_CODE, corpus_code_bytes)

    sampling_bytes = b"[sampling]\nframe = 'fixed'\n"
    _write(root / SAMPLING_FILE, sampling_bytes)
    sampling_sha256 = _sha256(sampling_bytes)

    screening_code = chain.screening_code
    if screening_code is None:
        screening_code = {SCREENING_CODE: _sha256(screening_code_bytes)}

    corpus_code = chain.corpus_code
    if corpus_code is None:
        corpus_code = {CORPUS_CODE: _sha256(corpus_code_bytes)}

    candidates_lines: list[str] = []

    if chain.include_screening_table:
        candidates_lines.append("[screening]")

        candidates_sampling = chain.candidates_sampling_sha256 or sampling_sha256
        candidates_lines.append(
            f"sampling_config_sha256 = {_quote(candidates_sampling)}"
        )

        if chain.freeze_record is not None:
            candidates_lines.append(f"freeze_01_record = {_quote(chain.freeze_record)}")

        freeze_sha256 = chain.freeze_record_sha256
        if freeze_sha256 is None:
            freeze_sha256 = _sha256(freeze_bytes)

        if freeze_sha256 != "":
            candidates_lines.append(
                f"freeze_01_record_sha256 = {_quote(freeze_sha256)}"
            )

        candidates_lines.append("")

    candidates_lines.append("[screening_code_sha256]")
    candidates_lines.extend(
        f"{_quote(path)} = {_quote(sha)}" for path, sha in screening_code.items()
    )
    candidates_lines.append("")

    candidates_bytes = "\n".join(candidates_lines).encode("utf-8")
    _write(root / CANDIDATES_FILE, candidates_bytes)
    candidates_sha256 = _sha256(candidates_bytes)

    members_declared = chain.members_declared
    if members_declared is None:
        members_declared = len(chain.study_ids)

    corpus_lines: list[str] = []

    if chain.include_corpus_table:
        corpus_lines.extend(
            [
                "[corpus]",
                "sampling_config_sha256 = "
                + _quote(chain.corpus_sampling_sha256 or sampling_sha256),
                "candidates_record_sha256 = "
                + _quote(chain.corpus_candidates_sha256 or candidates_sha256),
                f"members = {members_declared}",
                "",
            ]
        )

    corpus_lines.append("[corpus_code_sha256]")
    corpus_lines.extend(
        f"{_quote(path)} = {_quote(sha)}" for path, sha in corpus_code.items()
    )
    corpus_lines.append("")

    for study_id in chain.study_ids:
        corpus_lines.append("[[member]]")

        if study_id is not None:
            corpus_lines.append(f"study_id = {_quote(study_id)}")

        corpus_lines.append("standard = 'cyclonedx'")
        corpus_lines.append("")

    _write(root / CORPUS_FILE, "\n".join(corpus_lines).encode("utf-8"))
    return root


@pytest.fixture
def root(tmp_path: Path) -> Path:
    return tmp_path / "repo"


# ------------------------------------------------------------
# Valid chain
# ------------------------------------------------------------


def test_valid_chain_passes(root: Path) -> None:
    _build(root, Chain())

    assert verify_02_corpus(root) == root / CORPUS_FILE


def test_valid_chain_accepts_uppercase_recorded_hashes(root: Path) -> None:
    code_bytes = b"def screen(): ...\n"
    _build(
        root,
        Chain(screening_code={SCREENING_CODE: _sha256(code_bytes).upper()}),
    )

    assert verify_02_corpus(root) == root / CORPUS_FILE


def test_verifier_does_not_write(root: Path) -> None:
    _build(root, Chain())
    before = {path: path.read_bytes() for path in root.rglob("*") if path.is_file()}

    verify_02_corpus(root)

    after = {path: path.read_bytes() for path in root.rglob("*") if path.is_file()}
    assert after == before


# ------------------------------------------------------------
# Required files and tables
# ------------------------------------------------------------


@pytest.mark.parametrize("missing", [CORPUS_FILE, SAMPLING_FILE, CANDIDATES_FILE])
def test_missing_required_file_fails(root: Path, missing: Path) -> None:
    _build(root, Chain())
    (root / missing).unlink()

    with pytest.raises(CorpusVerificationError, match="required file not found"):
        verify_02_corpus(root)


def test_malformed_corpus_toml_fails(root: Path) -> None:
    _build(root, Chain())
    _write(root / CORPUS_FILE, b"[corpus\nnot toml")

    with pytest.raises(CorpusVerificationError):
        verify_02_corpus(root)


def test_malformed_candidates_toml_fails(root: Path) -> None:
    _build(root, Chain())
    _write(root / CANDIDATES_FILE, b"= broken")

    with pytest.raises(CorpusVerificationError):
        verify_02_corpus(root)


def test_missing_corpus_table_fails(root: Path) -> None:
    _build(root, Chain(include_corpus_table=False))

    with pytest.raises(CorpusVerificationError, match=r"missing \[corpus\]"):
        verify_02_corpus(root)


def test_missing_screening_table_fails(root: Path) -> None:
    _build(root, Chain(include_screening_table=False))

    with pytest.raises(CorpusVerificationError, match=r"missing \[screening\]"):
        verify_02_corpus(root)


# ------------------------------------------------------------
# 01 -> 02 -> 03 hash chain
# ------------------------------------------------------------


def test_edited_sampling_file_fails_at_candidates(root: Path) -> None:
    _build(root, Chain())
    _write(root / SAMPLING_FILE, b"[sampling]\nframe = 'edited'\n")

    with pytest.raises(
        CorpusVerificationError,
        match="02-candidates.toml does not match the current 01-sampling.toml",
    ):
        verify_02_corpus(root)


def test_candidates_recording_wrong_sampling_hash_fails(root: Path) -> None:
    _build(root, Chain(candidates_sampling_sha256=_sha256(b"other")))

    with pytest.raises(
        CorpusVerificationError,
        match="02-candidates.toml does not match the current 01-sampling.toml",
    ):
        verify_02_corpus(root)


def test_corpus_recording_wrong_sampling_hash_fails(root: Path) -> None:
    _build(root, Chain(corpus_sampling_sha256=_sha256(b"other")))

    with pytest.raises(
        CorpusVerificationError,
        match="03-corpus.toml does not match the current 01-sampling.toml",
    ):
        verify_02_corpus(root)


def test_corpus_recording_wrong_candidates_hash_fails(root: Path) -> None:
    _build(root, Chain(corpus_candidates_sha256=_sha256(b"other")))

    with pytest.raises(
        CorpusVerificationError,
        match="03-corpus.toml does not match the current 02-candidates.toml",
    ):
        verify_02_corpus(root)


def test_edited_candidates_file_fails_at_corpus(root: Path) -> None:
    _build(root, Chain())
    candidates = root / CANDIDATES_FILE
    candidates.write_bytes(candidates.read_bytes() + b"# trailing edit\n")

    with pytest.raises(
        CorpusVerificationError,
        match="03-corpus.toml does not match the current 02-candidates.toml",
    ):
        verify_02_corpus(root)


def test_candidates_line_ending_change_fails(root: Path) -> None:
    _build(root, Chain())
    candidates = root / CANDIDATES_FILE
    candidates.write_bytes(candidates.read_bytes().replace(b"\n", b"\r\n"))

    with pytest.raises(CorpusVerificationError, match="02-candidates.toml"):
        verify_02_corpus(root)


# ------------------------------------------------------------
# Freeze 01 record
# ------------------------------------------------------------


def test_unexpected_freeze_record_path_fails(root: Path) -> None:
    _build(root, Chain(freeze_record="contracts/OTHER_FREEZE.md"))

    with pytest.raises(
        CorpusVerificationError,
        match="unexpected Freeze 01 path",
    ):
        verify_02_corpus(root)


def test_missing_freeze_record_path_fails(root: Path) -> None:
    _build(root, Chain(freeze_record=None))

    with pytest.raises(
        CorpusVerificationError,
        match="unexpected Freeze 01 path",
    ):
        verify_02_corpus(root)


def test_edited_freeze_record_fails(root: Path) -> None:
    _build(root, Chain())
    _write(root / FREEZE_FILE, b"# Freeze 01, edited\n")

    with pytest.raises(CorpusVerificationError, match="hash mismatch"):
        verify_02_corpus(root)


def test_deleted_freeze_record_fails(root: Path) -> None:
    _build(root, Chain())
    (root / FREEZE_FILE).unlink()

    with pytest.raises(CorpusVerificationError, match="file not found"):
        verify_02_corpus(root)


def test_missing_freeze_record_sha256_fails(root: Path) -> None:
    _build(root, Chain(freeze_record_sha256=""))

    with pytest.raises(CorpusVerificationError, match="64 hexadecimal"):
        verify_02_corpus(root)


def test_malformed_freeze_record_sha256_fails(root: Path) -> None:
    _build(root, Chain(freeze_record_sha256="not-a-digest"))

    with pytest.raises(CorpusVerificationError, match="64 hexadecimal"):
        verify_02_corpus(root)


# ------------------------------------------------------------
# Code hash tables
# ------------------------------------------------------------


def test_edited_screening_code_fails(root: Path) -> None:
    _build(root, Chain())
    _write(root / SCREENING_CODE, b"def screen(): return 'edited'\n")

    with pytest.raises(CorpusVerificationError, match="screening_code_sha256"):
        verify_02_corpus(root)


def test_edited_corpus_code_fails(root: Path) -> None:
    _build(root, Chain())
    _write(root / CORPUS_CODE, b"def build(): return 'edited'\n")

    with pytest.raises(CorpusVerificationError, match="corpus_code_sha256"):
        verify_02_corpus(root)


def test_deleted_corpus_code_fails(root: Path) -> None:
    _build(root, Chain())
    (root / CORPUS_CODE).unlink()

    with pytest.raises(CorpusVerificationError, match="file not found"):
        verify_02_corpus(root)


def test_empty_screening_code_table_fails(root: Path) -> None:
    _build(root, Chain(screening_code={}))

    with pytest.raises(CorpusVerificationError, match="non-empty"):
        verify_02_corpus(root)


def test_empty_corpus_code_table_fails(root: Path) -> None:
    _build(root, Chain(corpus_code={}))

    with pytest.raises(CorpusVerificationError, match="non-empty"):
        verify_02_corpus(root)


@pytest.mark.parametrize(
    "unsafe_path",
    ["../outside.py", "src/../../outside.py"],
)
def test_code_hash_path_escaping_repository_fails(
    root: Path,
    unsafe_path: str,
) -> None:
    _build(root, Chain(corpus_code={unsafe_path: _sha256(b"x")}))

    with pytest.raises(CorpusVerificationError, match="within the repository"):
        verify_02_corpus(root)


# ------------------------------------------------------------
# Corpus members
# ------------------------------------------------------------


def test_corpus_without_members_fails(root: Path) -> None:
    _build(root, Chain(study_ids=[], members_declared=0))

    with pytest.raises(CorpusVerificationError, match="contains no corpus members"):
        verify_02_corpus(root)


@pytest.mark.parametrize("declared", [1, 3])
def test_declared_member_count_mismatch_fails(root: Path, declared: int) -> None:
    _build(root, Chain(members_declared=declared))

    with pytest.raises(CorpusVerificationError, match="member count"):
        verify_02_corpus(root)


def test_member_without_study_id_fails(root: Path) -> None:
    _build(root, Chain(study_ids=["gen-cyclonedx-aaa", None]))

    with pytest.raises(CorpusVerificationError, match="non-empty study_id"):
        verify_02_corpus(root)


def test_member_with_empty_study_id_fails(root: Path) -> None:
    _build(root, Chain(study_ids=["gen-cyclonedx-aaa", ""]))

    with pytest.raises(CorpusVerificationError, match="non-empty study_id"):
        verify_02_corpus(root)


def test_member_with_non_string_study_id_fails(root: Path) -> None:
    _build(root, Chain(study_ids=["gen-cyclonedx-aaa", 42]))

    with pytest.raises(CorpusVerificationError, match="non-empty study_id"):
        verify_02_corpus(root)


def test_duplicate_study_id_fails(root: Path) -> None:
    _build(root, Chain(study_ids=["gen-cyclonedx-aaa", "gen-cyclonedx-aaa"]))

    with pytest.raises(CorpusVerificationError, match="duplicate study_id"):
        verify_02_corpus(root)


# ------------------------------------------------------------
# Actual repository
# ------------------------------------------------------------


def test_actual_repository_corpus_chain_verifies() -> None:
    assert verify_02_corpus(REPOSITORY_ROOT) == REPOSITORY_ROOT / CORPUS_FILE
