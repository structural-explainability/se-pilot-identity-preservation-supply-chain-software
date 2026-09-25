"""Verification stage 03: verify preserved held-out source artifacts.

Purpose
-------
04-sources.toml records the exact source bytes on which the formal
generalization experiment will operate.

This verifier establishes that those preserved bytes remain identical to the
corpus members selected in 03-corpus.toml and that the provenance record still
derives from the current corpus artifact.

The verified provenance chain is:

    03-corpus.toml
        |
        v
    04-sources.toml
        |
        v
    generalization/sources/<preserved source bytes>

This stage first invokes the corpus verifier and then verifies:

1. 04-sources.toml exists and parses;
2. its recorded 03-corpus.toml SHA-256 matches the current corpus record;
3. its recorded source-preservation code hashes match the current files;
4. every corpus member has exactly one preserved-source record;
5. no unexpected preserved-source record has been introduced;
6. study IDs and preserved paths are unique;
7. each source record carries the same source SHA-256 selected in the corpus;
8. each recorded preserved SHA-256 equals that corpus SHA-256;
9. each preserved file's current exact bytes hash to the recorded SHA-256; and
10. each preserved file's current byte length matches its recorded size.

The central invariant is:

    03-corpus.toml member SHA-256
        ==
    04-sources.toml corpus SHA-256
        ==
    04-sources.toml preserved SHA-256
        ==
    current preserved-file SHA-256

This verifier does not return to the upstream repositories, re-screen source
documents, rerun selection, or replace corpus members.

Its purpose is to prove that the formal experiment will consume exactly the
source bytes selected before transformation outcomes were available.

This verifier performs no writes.
"""

from pathlib import Path
import tomllib
from typing import Any

from preservation_test.generalization.verification.verify_02_corpus import (
    CorpusVerificationError,
    verify_02_corpus,
)
from preservation_test.generalization.verification.verify_hashes import (
    HashVerificationError,
    verify_file_hash,
    verify_hash_table,
)

CORPUS_FILE = Path("generalization/03-corpus.toml")
SOURCES_RECORD = Path("generalization/04-sources.toml")


class SourcesVerificationError(RuntimeError):
    """Raised when preserved sources fail Freeze 02 integrity verification."""


def _required_string(
    row: dict[str, Any],
    key: str,
    where: str,
) -> str:
    """Return one required non-empty string."""
    value = row.get(key)

    if not isinstance(value, str) or not value:
        raise SourcesVerificationError(f"{where}.{key} must be a non-empty string")

    return value


def verify_03_sources(repository_root: Path) -> Path:
    """Verify 03 -> 04 provenance and every preserved source byte-for-byte."""
    try:
        corpus_path = verify_02_corpus(repository_root)

    except CorpusVerificationError as error:
        raise SourcesVerificationError(str(error)) from error

    path = repository_root / SOURCES_RECORD

    if not path.is_file():
        raise SourcesVerificationError(f"source record not found: {path}")

    try:
        with path.open("rb") as handle:
            data = tomllib.load(handle)

        with corpus_path.open("rb") as handle:
            corpus_data = tomllib.load(handle)

    except (OSError, tomllib.TOMLDecodeError) as error:
        raise SourcesVerificationError(str(error)) from error

    sources = data.get("sources")

    if not isinstance(sources, dict):
        raise SourcesVerificationError("04-sources.toml is missing [sources]")

    if sources.get("corpus_record") != CORPUS_FILE.as_posix():
        raise SourcesVerificationError(
            "04-sources.toml records an unexpected corpus path"
        )

    try:
        verify_file_hash(
            repository_root,
            CORPUS_FILE.as_posix(),
            sources.get("corpus_record_sha256"),
            label="04-sources.toml corpus record",
        )

        verify_hash_table(
            repository_root,
            data.get("sources_code_sha256"),
            table_name="sources_code_sha256",
        )

    except HashVerificationError as error:
        raise SourcesVerificationError(str(error)) from error

    members = corpus_data.get("member")
    rows = data.get("source")

    if not isinstance(members, list) or not members:
        raise SourcesVerificationError("03-corpus.toml contains no [[member]] entries")

    if not isinstance(rows, list) or not rows:
        raise SourcesVerificationError("04-sources.toml contains no [[source]] entries")

    if sources.get("members") != len(rows):
        raise SourcesVerificationError(
            "04-sources.toml source count does not match [sources].members"
        )

    corpus_by_study_id: dict[str, str] = {}

    for index, member in enumerate(members):
        where = f"member[{index}]"

        if not isinstance(member, dict):
            raise SourcesVerificationError(f"{where} must be a table")

        study_id = _required_string(member, "study_id", where)
        sha256 = _required_string(member, "sha256", where)

        if study_id in corpus_by_study_id:
            raise SourcesVerificationError(
                f"duplicate study_id in 03-corpus.toml: {study_id}"
            )

        corpus_by_study_id[study_id] = sha256

    seen_study_ids: set[str] = set()
    seen_paths: set[str] = set()

    for index, row in enumerate(rows):
        where = f"source[{index}]"

        if not isinstance(row, dict):
            raise SourcesVerificationError(f"{where} must be a table")

        study_id = _required_string(row, "study_id", where)
        preserved_path = _required_string(row, "preserved_path", where)
        corpus_sha256 = _required_string(row, "corpus_sha256", where)
        preserved_sha256 = _required_string(
            row,
            "preserved_sha256",
            where,
        )

        if study_id in seen_study_ids:
            raise SourcesVerificationError(
                f"duplicate study_id in 04-sources.toml: {study_id}"
            )

        seen_study_ids.add(study_id)

        if preserved_path in seen_paths:
            raise SourcesVerificationError(
                f"duplicate preserved_path in 04-sources.toml: {preserved_path}"
            )

        seen_paths.add(preserved_path)

        expected_corpus_sha256 = corpus_by_study_id.get(study_id)

        if expected_corpus_sha256 is None:
            raise SourcesVerificationError(
                f"{study_id} exists in 04-sources.toml but not 03-corpus.toml"
            )

        if corpus_sha256 != expected_corpus_sha256:
            raise SourcesVerificationError(
                f"{study_id} corpus SHA-256 differs between 03 and 04"
            )

        if preserved_sha256 != corpus_sha256:
            raise SourcesVerificationError(
                f"{study_id} preserved SHA-256 differs from its corpus SHA-256"
            )

        try:
            preserved_file = verify_file_hash(
                repository_root,
                preserved_path,
                preserved_sha256,
                label=f"preserved source {study_id}",
            )

        except HashVerificationError as error:
            raise SourcesVerificationError(str(error)) from error

        size_bytes = row.get("size_bytes")

        if not isinstance(size_bytes, int) or size_bytes < 0:
            raise SourcesVerificationError(
                f"{where}.size_bytes must be a non-negative integer"
            )

        if preserved_file.stat().st_size != size_bytes:
            raise SourcesVerificationError(
                f"{study_id} preserved size differs from recorded size_bytes"
            )

    if seen_study_ids != set(corpus_by_study_id):
        missing = sorted(set(corpus_by_study_id) - seen_study_ids)
        extra = sorted(seen_study_ids - set(corpus_by_study_id))

        raise SourcesVerificationError(
            f"03/04 study_id sets differ; missing={missing}, extra={extra}"
        )

    return path
