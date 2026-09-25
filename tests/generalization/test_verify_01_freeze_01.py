"""Tests for verification stage 01: Freeze 01 byte integrity."""

import hashlib
from pathlib import Path

import pytest

from preservation_test.generalization.verification.verify_01_freeze_01 import (
    FREEZE_FILE,
    calculate_sha256,
    find_repository_root,
    main,
    read_frozen_hashes,
    verify_01_freeze_01,
    verify_frozen_artifact,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write(path: Path, data: bytes) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def _freeze_record(entries: dict[str, str]) -> str:
    lines = [
        "# First Commitment/Evaluator Freeze",
        "",
        "## Frozen Content Hashes",
        "",
    ]
    lines.extend(f"- `{sha256}`  `{path}`" for path, sha256 in entries.items())
    lines.append("")
    return "\n".join(lines)


def _make_repository(
    tmp_path: Path,
    artifacts: dict[str, bytes],
) -> Path:
    """Create a minimal repository whose freeze record matches its artifacts."""
    root = tmp_path / "repo"
    (root / ".git").mkdir(parents=True)

    entries: dict[str, str] = {}

    for relative_path, data in artifacts.items():
        _write(root / relative_path, data)
        entries[relative_path] = _sha256(data)

    _write(root / FREEZE_FILE, _freeze_record(entries).encode("utf-8"))
    return root


ARTIFACTS = {
    "contracts/schema.md": b"# schema\n",
    "contracts/commitments.toml": b"[[commitment]]\nid = 'x'\n",
    "src/evaluator/evaluate.py": b"print('frozen')\n",
}


# ------------------------------------------------------------
# find_repository_root
# ------------------------------------------------------------


def test_find_repository_root_from_root(tmp_path: Path) -> None:
    root = _make_repository(tmp_path, ARTIFACTS)

    assert find_repository_root(root) == root.resolve()


def test_find_repository_root_from_nested_directory(tmp_path: Path) -> None:
    root = _make_repository(tmp_path, ARTIFACTS)
    nested = root / "src" / "evaluator"

    assert find_repository_root(nested) == root.resolve()


def test_find_repository_root_accepts_git_file(tmp_path: Path) -> None:
    root = tmp_path / "worktree"
    root.mkdir()
    (root / ".git").write_text("gitdir: elsewhere\n", encoding="utf-8")

    assert find_repository_root(root) == root.resolve()


def test_find_repository_root_raises_without_git(tmp_path: Path) -> None:
    orphan = tmp_path / "no-repo" / "deeper"
    orphan.mkdir(parents=True)

    if any((p / ".git").exists() for p in (orphan, *orphan.parents)):
        pytest.skip("temporary directory is inside a Git repository")

    with pytest.raises(RuntimeError, match="Could not find repository root"):
        find_repository_root(orphan)


# ------------------------------------------------------------
# calculate_sha256
# ------------------------------------------------------------


def test_calculate_sha256_matches_hashlib(tmp_path: Path) -> None:
    data = b"exact bytes\r\nincluding CRLF\n"
    path = _write(tmp_path / "file.bin", data)

    assert calculate_sha256(path) == _sha256(data)


def test_calculate_sha256_empty_file(tmp_path: Path) -> None:
    path = _write(tmp_path / "empty", b"")

    assert calculate_sha256(path) == _sha256(b"")


def test_calculate_sha256_spans_multiple_chunks(tmp_path: Path) -> None:
    data = b"a" * (1024 * 1024 * 2 + 17)
    path = _write(tmp_path / "large.bin", data)

    assert calculate_sha256(path) == _sha256(data)


def test_calculate_sha256_is_lowercase(tmp_path: Path) -> None:
    path = _write(tmp_path / "file", b"x")

    digest = calculate_sha256(path)

    assert digest == digest.lower()
    assert len(digest) == 64


# ------------------------------------------------------------
# read_frozen_hashes
# ------------------------------------------------------------


def test_read_frozen_hashes_parses_recorded_entries(tmp_path: Path) -> None:
    root = _make_repository(tmp_path, ARTIFACTS)

    frozen = read_frozen_hashes(root / FREEZE_FILE)

    assert frozen == {Path(path): _sha256(data) for path, data in ARTIFACTS.items()}


def test_read_frozen_hashes_preserves_record_order(tmp_path: Path) -> None:
    root = _make_repository(tmp_path, ARTIFACTS)

    frozen = read_frozen_hashes(root / FREEZE_FILE)

    assert list(frozen) == [Path(path) for path in ARTIFACTS]


def test_read_frozen_hashes_lowercases_uppercase_digest(tmp_path: Path) -> None:
    digest = _sha256(b"x")
    record = _write(
        tmp_path / "freeze.md",
        f"- `{digest.upper()}`  `a.txt`\n".encode(),
    )

    assert read_frozen_hashes(record) == {Path("a.txt"): digest}


def test_read_frozen_hashes_ignores_non_hash_lines(tmp_path: Path) -> None:
    digest = _sha256(b"x")
    text = "\n".join(
        [
            "**Frozen content commit:** `ef3a5dacdf1a483f41d87ee955d365376e63a220`",
            "- `contracts/schema.md`",
            f"- `{digest[:63]}`  `short.txt`",
            f"- `{digest}` `a.txt`",
            f"* `{digest}`  `bullet-star.txt`",
            "Plain prose mentioning a.txt.",
            "",
        ]
    )
    record = _write(tmp_path / "freeze.md", text.encode("utf-8"))

    assert read_frozen_hashes(record) == {Path("a.txt"): digest}


def test_read_frozen_hashes_accepts_surrounding_whitespace(tmp_path: Path) -> None:
    digest = _sha256(b"x")
    record = _write(
        tmp_path / "freeze.md",
        f"   - `{digest}`  `a.txt`   \n".encode(),
    )

    assert read_frozen_hashes(record) == {Path("a.txt"): digest}


def test_read_frozen_hashes_accepts_crlf_record(tmp_path: Path) -> None:
    digest = _sha256(b"x")
    record = _write(
        tmp_path / "freeze.md",
        f"# Freeze\r\n\r\n- `{digest}`  `a.txt`\r\n".encode(),
    )

    assert read_frozen_hashes(record) == {Path("a.txt"): digest}


def test_read_frozen_hashes_rejects_missing_record(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Freeze record not found"):
        read_frozen_hashes(tmp_path / "missing.md")


def test_read_frozen_hashes_rejects_record_without_hashes(tmp_path: Path) -> None:
    record = _write(tmp_path / "freeze.md", b"# Freeze\n\nNo hashes here.\n")

    with pytest.raises(ValueError, match="No frozen content hashes"):
        read_frozen_hashes(record)


def test_read_frozen_hashes_rejects_duplicate_path(tmp_path: Path) -> None:
    first = _sha256(b"one")
    second = _sha256(b"two")
    record = _write(
        tmp_path / "freeze.md",
        f"- `{first}`  `a.txt`\n- `{second}`  `a.txt`\n".encode(),
    )

    with pytest.raises(ValueError, match="Duplicate frozen artifact"):
        read_frozen_hashes(record)


# ------------------------------------------------------------
# verify_frozen_artifact
# ------------------------------------------------------------


def test_verify_frozen_artifact_accepts_matching_bytes(tmp_path: Path) -> None:
    _write(tmp_path / "a.txt", b"frozen\n")

    verify_frozen_artifact(tmp_path, Path("a.txt"), _sha256(b"frozen\n"))


def test_verify_frozen_artifact_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Frozen artifact not found"):
        verify_frozen_artifact(tmp_path, Path("a.txt"), _sha256(b"x"))


def test_verify_frozen_artifact_rejects_directory(tmp_path: Path) -> None:
    (tmp_path / "a.txt").mkdir()

    with pytest.raises(FileNotFoundError, match="Frozen artifact not found"):
        verify_frozen_artifact(tmp_path, Path("a.txt"), _sha256(b"x"))


def test_verify_frozen_artifact_reports_expected_and_observed(
    tmp_path: Path,
) -> None:
    _write(tmp_path / "a.txt", b"changed\n")
    expected = _sha256(b"frozen\n")
    observed = _sha256(b"changed\n")

    with pytest.raises(RuntimeError) as caught:
        verify_frozen_artifact(tmp_path, Path("a.txt"), expected)

    message = str(caught.value)
    assert "Freeze 01 integrity failure: a.txt" in message
    assert f"expected: {expected}" in message
    assert f"observed: {observed}" in message


def test_verify_frozen_artifact_detects_line_ending_change(tmp_path: Path) -> None:
    _write(tmp_path / "a.txt", b"line\r\n")

    with pytest.raises(RuntimeError, match="integrity failure"):
        verify_frozen_artifact(tmp_path, Path("a.txt"), _sha256(b"line\n"))


# ------------------------------------------------------------
# verify_01_freeze_01
# ------------------------------------------------------------


def test_verify_01_freeze_01_accepts_intact_repository(tmp_path: Path) -> None:
    root = _make_repository(tmp_path, ARTIFACTS)

    verified = verify_01_freeze_01(root)

    assert verified == tuple(Path(path) for path in ARTIFACTS)


def test_verify_01_freeze_01_rejects_modified_artifact(tmp_path: Path) -> None:
    root = _make_repository(tmp_path, ARTIFACTS)
    _write(root / "src/evaluator/evaluate.py", b"print('edited')\n")

    with pytest.raises(
        RuntimeError,
        match=r"src[\\/]evaluator[\\/]evaluate\.py",
    ):
        verify_01_freeze_01(root)


def test_verify_01_freeze_01_rejects_deleted_artifact(tmp_path: Path) -> None:
    root = _make_repository(tmp_path, ARTIFACTS)
    (root / "contracts/schema.md").unlink()

    with pytest.raises(
        FileNotFoundError,
        match=r"contracts[\\/]schema\.md",
    ):
        verify_01_freeze_01(root)


def test_verify_01_freeze_01_rejects_missing_freeze_record(tmp_path: Path) -> None:
    root = _make_repository(tmp_path, ARTIFACTS)
    (root / FREEZE_FILE).unlink()

    with pytest.raises(FileNotFoundError, match="Freeze record not found"):
        verify_01_freeze_01(root)


def test_verify_01_freeze_01_ignores_unfrozen_files(tmp_path: Path) -> None:
    root = _make_repository(tmp_path, ARTIFACTS)
    _write(root / "docs/en/new-page.md", b"# Later documentation\n")
    _write(root / "src/evaluator/__init__.py", b'"""Edited docstring."""\n')

    assert len(verify_01_freeze_01(root)) == len(ARTIFACTS)


def test_verify_01_freeze_01_does_not_write(tmp_path: Path) -> None:
    root = _make_repository(tmp_path, ARTIFACTS)
    before = {path: path.read_bytes() for path in root.rglob("*") if path.is_file()}

    verify_01_freeze_01(root)

    after = {path: path.read_bytes() for path in root.rglob("*") if path.is_file()}
    assert after == before


# ------------------------------------------------------------
# main
# ------------------------------------------------------------


def test_main_reports_verified_artifacts(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = _make_repository(tmp_path, ARTIFACTS)
    monkeypatch.chdir(root / "src")

    main()

    output = capsys.readouterr().out
    assert "Freeze 01 verified." in output
    assert f"Frozen artifacts verified: {len(ARTIFACTS)}" in output

    for relative_path in ARTIFACTS:
        assert str(Path(relative_path)) in output


def test_main_propagates_integrity_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _make_repository(tmp_path, ARTIFACTS)
    _write(root / "contracts/schema.md", b"# edited\n")
    monkeypatch.chdir(root)

    with pytest.raises(RuntimeError, match="integrity failure"):
        main()


# ------------------------------------------------------------
# Actual repository
# ------------------------------------------------------------


def test_actual_freeze_01_record_lists_seven_artifacts() -> None:
    frozen = read_frozen_hashes(REPOSITORY_ROOT / FREEZE_FILE)

    assert set(frozen) == {
        Path("contracts/schema.md"),
        Path("contracts/sources.toml"),
        Path("contracts/commitments.toml"),
        Path("src/preservation_test/evaluator/purl_canonical.py"),
        Path("src/preservation_test/evaluator/formats.py"),
        Path("src/preservation_test/evaluator/evaluate.py"),
        Path("docs/en/run.md"),
    }


def test_actual_repository_passes_freeze_01() -> None:
    verified = verify_01_freeze_01(REPOSITORY_ROOT)

    assert len(verified) == 7
