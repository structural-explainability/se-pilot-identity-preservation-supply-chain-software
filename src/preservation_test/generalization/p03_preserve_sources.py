"""Step p03: preserve the exact held-out source bytes and write 04-sources.toml.

Purpose
-------
03-corpus.toml has already decided which artifacts belong in the held-out
generalization corpus.
This step does not revisit eligibility, identity, selection, PURLs, ecosystems,
or any other scientific decision made in 01-sampling.toml through 03-corpus.toml.

Instead, p03 crosses the boundary from a selected corpus to preserved
experimental inputs.

For every member of 03-corpus.toml, this step:

1. locates the declared repository at the recorded pinned revision,
2. reads the exact Git blob identified by the recorded repository path,
3. verifies that the blob's SHA-256 equals the SHA-256 recorded in
   03-corpus.toml,
4. writes those exact bytes into generalization/sources/,
5. hashes the preserved bytes again, and
6. records their provenance and integrity in 04-sources.toml.

The required invariant is:

    Git blob SHA-256
        ==
    03-corpus.toml member SHA-256
        ==
    preserved source SHA-256

No converter is run. No evaluator is called. No source is re-screened.
No corpus member may be added, removed, substituted, or preferred here.

This step is mechanical: its purpose is to ensure that the
formal experiment later operates on exactly
the source bytes selected before
transformation outcomes were visible.

The operation is write-once.
Existing preserved evidence is never overwritten.

Usage from the repository root:

    uv run python -m preservation_test.generalization.p03_preserve_sources

An alternate clone root may be supplied when needed:

    uv run python -m preservation_test.generalization.p03_preserve_sources `
        --clone-root ../generalization-clones
"""

import argparse
from dataclasses import dataclass
from pathlib import Path
import subprocess
import sys
import tomllib
from typing import Any

from preservation_test.generalization.utils.hashing import (
    sha256_bytes,
    sha256_file,
)
from preservation_test.generalization.utils.screening import (
    relative_to_root,
    screening_code_hashes,
)
from preservation_test.generalization.utils.toml_writer import (
    render_document,
    write_new_file,
)
from preservation_test.generalization.verification.verify_corpus import (
    CorpusVerificationError,
    verify_corpus,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
THIS_STEP = Path(__file__).resolve()
STEP_MODULE = f"preservation_test.generalization.{THIS_STEP.stem}"

CORPUS_FILE = Path("generalization/03-corpus.toml")
SOURCES_DIR = Path("generalization/sources")
SOURCES_RECORD = Path("generalization/04-sources.toml")

DEFAULT_CLONE_ROOT = Path("../generalization-clones")

EXIT_OK = 0
EXIT_REFUSED = 2


class SourcePreservationError(RuntimeError):
    """Raised when selected source bytes cannot be preserved exactly."""


@dataclass(frozen=True)
class CorpusMember:
    """Source provenance required to preserve one selected corpus member."""

    study_id: str
    candidate_id: str
    repository: str
    repository_revision: str
    repository_relative_path: str
    sha256: str
    source_standard: str


@dataclass(frozen=True)
class MaterializedSource:
    """One verified Git blob ready to be preserved."""

    member: CorpusMember
    git_blob_id: str
    data: bytes
    preserved_path: Path


def _required_string(data: dict[str, Any], key: str, where: str) -> str:
    """Return one required non-empty string."""
    value = data.get(key)
    if not isinstance(value, str) or not value:
        raise SourcePreservationError(f"{where}.{key} must be a non-empty string")
    return value


def _load_corpus_members(path: Path) -> tuple[CorpusMember, ...]:
    """Load the already-selected members from 03-corpus.toml."""
    with path.open("rb") as handle:
        data = tomllib.load(handle)

    rows = data.get("member")
    if not isinstance(rows, list) or not rows:
        raise SourcePreservationError("03-corpus.toml contains no [[member]] entries")

    members: list[CorpusMember] = []

    for index, row in enumerate(rows):
        where = f"member[{index}]"

        if not isinstance(row, dict):
            raise SourcePreservationError(f"{where} must be a table")

        members.append(
            CorpusMember(
                study_id=_required_string(row, "study_id", where),
                candidate_id=_required_string(row, "candidate_id", where),
                repository=_required_string(row, "repository", where),
                repository_revision=_required_string(
                    row,
                    "repository_revision",
                    where,
                ),
                repository_relative_path=_required_string(
                    row,
                    "repository_relative_path",
                    where,
                ),
                sha256=_required_string(row, "sha256", where),
                source_standard=_required_string(
                    row,
                    "source_standard",
                    where,
                ),
            )
        )

    study_ids = [member.study_id for member in members]
    if len(set(study_ids)) != len(study_ids):
        raise SourcePreservationError(
            "03-corpus.toml contains duplicate study_id values"
        )

    return tuple(members)


def _clone_path(clone_root: Path, repository: str) -> Path:
    """Return the prepared clone directory for one declared repository."""
    name = repository.rsplit("/", 1)[-1]

    if not name:
        raise SourcePreservationError(
            f"cannot determine clone directory for repository {repository!r}"
        )

    return clone_root / name


def _run_git(repo_dir: Path, *args: str) -> bytes:
    """Run Git and return stdout bytes."""
    if not repo_dir.is_dir():
        raise SourcePreservationError(f"prepared repository not found: {repo_dir}")

    result = subprocess.run(
        ["git", *args],
        cwd=repo_dir,
        check=False,
        capture_output=True,
    )

    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        command = "git " + " ".join(args)
        raise SourcePreservationError(f"{command} failed in {repo_dir}: {detail}")

    return result.stdout


def _git_blob_id(
    repo_dir: Path,
    revision: str,
    repository_relative_path: str,
) -> str:
    """Return the Git object ID for a source path at the pinned revision."""
    object_spec = f"{revision}:{repository_relative_path}"

    return (
        _run_git(
            repo_dir,
            "rev-parse",
            object_spec,
        )
        .decode("ascii")
        .strip()
    )


def _git_blob_bytes(
    repo_dir: Path,
    revision: str,
    repository_relative_path: str,
) -> bytes:
    """Read exact blob bytes from Git rather than from the working tree."""
    object_spec = f"{revision}:{repository_relative_path}"

    return _run_git(
        repo_dir,
        "show",
        object_spec,
    )


def _source_suffix(source_standard: str) -> str:
    """Return the stable preserved-file suffix for one source standard."""
    if source_standard == "cyclonedx":
        return "cdx.json"

    if source_standard == "spdx":
        return "spdx.json"

    raise SourcePreservationError(
        f"unsupported source_standard in corpus: {source_standard!r}"
    )


def _preserved_path(member: CorpusMember, sources_dir: Path) -> Path:
    """Return the deterministic preserved path for one corpus member."""
    if "/" in member.study_id or "\\" in member.study_id:
        raise SourcePreservationError(
            f"study_id cannot be used as a filename: {member.study_id!r}"
        )

    return sources_dir / f"{member.study_id}.{_source_suffix(member.source_standard)}"


def _materialize(
    members: tuple[CorpusMember, ...],
    clone_root: Path,
    sources_dir: Path,
) -> tuple[MaterializedSource, ...]:
    """Read and verify every selected Git blob before writing any evidence."""
    materialized: list[MaterializedSource] = []

    for member in members:
        repo_dir = _clone_path(clone_root, member.repository)

        blob_id = _git_blob_id(
            repo_dir,
            member.repository_revision,
            member.repository_relative_path,
        )

        data = _git_blob_bytes(
            repo_dir,
            member.repository_revision,
            member.repository_relative_path,
        )

        observed = sha256_bytes(data)

        if observed != member.sha256:
            raise SourcePreservationError(
                "selected source bytes do not match 03-corpus.toml:\n"
                f"  study_id: {member.study_id}\n"
                f"  repository: {member.repository}\n"
                f"  path: {member.repository_relative_path}\n"
                f"  recorded: {member.sha256}\n"
                f"  observed: {observed}"
            )

        materialized.append(
            MaterializedSource(
                member=member,
                git_blob_id=blob_id,
                data=data,
                preserved_path=_preserved_path(member, sources_dir),
            )
        )

    paths = [item.preserved_path for item in materialized]
    if len(set(paths)) != len(paths):
        raise SourcePreservationError("preserved source filenames are not unique")

    return tuple(materialized)


def _require_clean_destination(
    sources_dir: Path,
    sources_record: Path,
) -> None:
    """Refuse to overwrite or mix previously preserved source evidence."""
    if sources_record.exists():
        raise SourcePreservationError(f"refusing to overwrite {sources_record}")

    if not sources_dir.exists():
        return

    existing = sorted(sources_dir.iterdir())

    if existing:
        shown = "\n  ".join(str(path) for path in existing)
        raise SourcePreservationError(
            f"sources directory is not empty; refusing to mix evidence:\n  {shown}"
        )


def _source_row(
    item: MaterializedSource,
    preserved_sha256: str,
) -> dict[str, Any]:
    """Return one preserved-source provenance row."""
    member = item.member

    return {
        "study_id": member.study_id,
        "candidate_id": member.candidate_id,
        "repository": member.repository,
        "repository_revision": member.repository_revision,
        "repository_relative_path": member.repository_relative_path,
        "git_blob_id": item.git_blob_id,
        "source_standard": member.source_standard,
        "corpus_sha256": member.sha256,
        "preserved_path": relative_to_root(
            item.preserved_path,
            REPOSITORY_ROOT,
        ),
        "preserved_sha256": preserved_sha256,
        "size_bytes": len(item.data),
    }


def _render_sources_record(
    corpus_path: Path,
    materialized: tuple[MaterializedSource, ...],
    rows: list[dict[str, Any]],
) -> str:
    """Render 04-sources.toml."""
    return render_document(
        header=[
            "04-sources.toml",
            f"Generated by {STEP_MODULE}.",
            "Provenance and integrity record for the exact preserved corpus bytes.",
            "Do not edit by hand.",
        ],
        tables={
            "sources": {
                "corpus_record": relative_to_root(
                    corpus_path,
                    REPOSITORY_ROOT,
                ),
                "corpus_record_sha256": sha256_file(corpus_path),
                "preserved_directory": relative_to_root(
                    SOURCES_DIR,
                    REPOSITORY_ROOT,
                ),
                "preservation_method": (
                    "exact Git blob bytes at recorded repository revision and path"
                ),
                "members": len(materialized),
            },
            "sources_code_sha256": screening_code_hashes(
                REPOSITORY_ROOT,
                extra=(THIS_STEP,),
            ),
        },
        arrays={"source": rows},
    )


def preserve_sources(clone_root: Path) -> int:
    """Run p03 and preserve the exact selected source bytes."""
    corpus_path = REPOSITORY_ROOT / CORPUS_FILE
    sources_dir = REPOSITORY_ROOT / SOURCES_DIR
    sources_record = REPOSITORY_ROOT / SOURCES_RECORD

    try:
        _require_clean_destination(sources_dir, sources_record)

        verify_corpus(REPOSITORY_ROOT)

        members = _load_corpus_members(corpus_path)

        materialized = _materialize(
            members,
            clone_root,
            sources_dir,
        )

    except (
        OSError,
        CorpusVerificationError,
        SourcePreservationError,
    ) as error:
        sys.stderr.write(f"SOURCES NOT PRESERVED.\n{error}\n")
        return EXIT_REFUSED

    created: list[Path] = []

    try:
        sources_dir.mkdir(parents=True, exist_ok=True)

        rows: list[dict[str, Any]] = []

        for item in materialized:
            item.preserved_path.write_bytes(item.data)
            created.append(item.preserved_path)

            preserved_sha256 = sha256_file(item.preserved_path)

            if preserved_sha256 != item.member.sha256:
                raise SourcePreservationError(
                    "preserved bytes failed post-write verification:\n"
                    f"  study_id: {item.member.study_id}\n"
                    f"  expected: {item.member.sha256}\n"
                    f"  observed: {preserved_sha256}"
                )

            rows.append(
                _source_row(
                    item,
                    preserved_sha256,
                )
            )

        text = _render_sources_record(
            corpus_path,
            materialized,
            rows,
        )

        write_new_file(sources_record, text)

    except (OSError, SourcePreservationError) as error:
        for path in reversed(created):
            path.unlink(missing_ok=True)

        sys.stderr.write(f"SOURCES NOT PRESERVED.\n{error}\n")
        return EXIT_REFUSED

    print(
        "wrote "
        f"{relative_to_root(sources_record, REPOSITORY_ROOT)} "
        f"(sha256 {sha256_file(sources_record)})"
    )
    print(f"preserved sources: {len(materialized)}")

    for item in materialized:
        print(
            "  "
            + relative_to_root(
                item.preserved_path,
                REPOSITORY_ROOT,
            )
        )

    return EXIT_OK


def main(argv: list[str] | None = None) -> int:
    """Parse arguments and run step p03."""
    parser = argparse.ArgumentParser(
        description=(
            "Step p03: preserve the exact held-out source bytes "
            "and write 04-sources.toml."
        )
    )
    parser.add_argument(
        "--clone-root",
        type=Path,
        default=DEFAULT_CLONE_ROOT,
        help="Directory containing the prepared sampling-frame clones.",
    )

    args = parser.parse_args(argv)

    clone_root = args.clone_root
    if not clone_root.is_absolute():
        clone_root = (REPOSITORY_ROOT / clone_root).resolve()

    return preserve_sources(clone_root)


if __name__ == "__main__":
    raise SystemExit(main())
