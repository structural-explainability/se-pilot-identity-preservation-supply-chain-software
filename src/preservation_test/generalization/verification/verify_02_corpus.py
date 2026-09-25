"""Verification stage 02: verify the selected generalization corpus.

Purpose
-------
03-corpus.toml is the generated record of which source artifacts were selected
for the held-out generalization corpus.

This verifier establishes that the corpus still derives from the exact
predeclared sampling specification and candidate-screening record from which it
was generated.

The verified provenance chain is:

    Freeze 01
        |
        v
    01-sampling.toml
        |
        v
    02-candidates.toml
        |
        v
    03-corpus.toml

This stage verifies:

1. 01-sampling.toml, 02-candidates.toml, and 03-corpus.toml exist;
2. 02-candidates.toml records the current 01-sampling.toml SHA-256;
3. 03-corpus.toml records the current 01-sampling.toml SHA-256;
4. 03-corpus.toml records the current 02-candidates.toml SHA-256;
5. 02-candidates.toml still identifies the declared Freeze 01 record;
6. the recorded Freeze 01 record SHA-256 still matches that file;
7. the recorded candidate-screening code hashes still match the current files;
8. the recorded corpus-construction code hashes still match the current files;
9. the declared corpus-member count matches the generated member records; and
10. corpus study IDs are present and unique.

This stage does not repeat candidate screening or corpus selection.

It verifies provenance and integrity only. If an upstream authored or generated
artifact has changed, the appropriate downstream artifacts must be regenerated
rather than silently accepted.

The required hash relationships include:

    current 01-sampling.toml SHA-256
        ==
    SHA-256 recorded by 02-candidates.toml
        ==
    SHA-256 recorded by 03-corpus.toml

and:

    current 02-candidates.toml SHA-256
        ==
    SHA-256 recorded by 03-corpus.toml

This verifier performs no writes.
"""

from pathlib import Path
import tomllib
from typing import Any

from preservation_test.generalization.utils.hashing import sha256_file
from preservation_test.generalization.verification.verify_01_freeze_01 import (
    FREEZE_FILE,
)
from preservation_test.generalization.verification.verify_hashes import (
    HashVerificationError,
    verify_file_hash,
    verify_hash_table,
)

CORPUS_FILE = Path("generalization/03-corpus.toml")
SAMPLING_FILE = Path("generalization/01-sampling.toml")
CANDIDATES_FILE = Path("generalization/02-candidates.toml")


class CorpusVerificationError(RuntimeError):
    """Raised when the generated corpus fails integrity verification."""


def _required_table(
    data: dict[str, Any],
    key: str,
) -> dict[str, Any]:
    """Return one required TOML table."""
    value = data.get(key)

    if not isinstance(value, dict):
        raise CorpusVerificationError(f"03-corpus.toml is missing [{key}]")

    return value


def verify_02_corpus(repository_root: Path) -> Path:
    """Verify 01 -> 02 -> 03 provenance, hashes, code hashes, and member count."""
    corpus_path = repository_root / CORPUS_FILE
    sampling_path = repository_root / SAMPLING_FILE
    candidates_path = repository_root / CANDIDATES_FILE

    for path in (corpus_path, sampling_path, candidates_path):
        if not path.is_file():
            raise CorpusVerificationError(f"required file not found: {path}")

    try:
        with corpus_path.open("rb") as handle:
            corpus_data = tomllib.load(handle)

        with candidates_path.open("rb") as handle:
            candidates_data = tomllib.load(handle)

    except (OSError, tomllib.TOMLDecodeError) as error:
        raise CorpusVerificationError(str(error)) from error

    corpus = _required_table(corpus_data, "corpus")

    screening = candidates_data.get("screening")

    if not isinstance(screening, dict):
        raise CorpusVerificationError("02-candidates.toml is missing [screening]")

    observed_sampling = sha256_file(sampling_path)

    if screening.get("sampling_config_sha256") != observed_sampling:
        raise CorpusVerificationError(
            "02-candidates.toml does not match the current 01-sampling.toml"
        )

    if corpus.get("sampling_config_sha256") != observed_sampling:
        raise CorpusVerificationError(
            "03-corpus.toml does not match the current 01-sampling.toml"
        )

    observed_candidates = sha256_file(candidates_path)

    if corpus.get("candidates_record_sha256") != observed_candidates:
        raise CorpusVerificationError(
            "03-corpus.toml does not match the current 02-candidates.toml"
        )

    freeze_record = screening.get("freeze_01_record")
    freeze_record_sha256 = screening.get("freeze_01_record_sha256")

    if freeze_record != FREEZE_FILE.as_posix():
        raise CorpusVerificationError(
            "02-candidates.toml records an unexpected Freeze 01 path"
        )

    try:
        verify_file_hash(
            repository_root,
            freeze_record,
            freeze_record_sha256,
            label="02-candidates.toml Freeze 01 record",
        )

        verify_hash_table(
            repository_root,
            candidates_data.get("screening_code_sha256"),
            table_name="screening_code_sha256",
        )

        verify_hash_table(
            repository_root,
            corpus_data.get("corpus_code_sha256"),
            table_name="corpus_code_sha256",
        )

    except HashVerificationError as error:
        raise CorpusVerificationError(str(error)) from error

    members = corpus_data.get("member")

    if not isinstance(members, list) or not members:
        raise CorpusVerificationError("03-corpus.toml contains no corpus members")

    if corpus.get("members") != len(members):
        raise CorpusVerificationError(
            "03-corpus.toml member count does not match [corpus].members"
        )

    study_ids = [
        member.get("study_id") for member in members if isinstance(member, dict)
    ]

    if len(study_ids) != len(members) or any(
        not isinstance(study_id, str) or not study_id for study_id in study_ids
    ):
        raise CorpusVerificationError(
            "every [[member]] must contain a non-empty study_id"
        )

    if len(set(study_ids)) != len(study_ids):
        raise CorpusVerificationError(
            "03-corpus.toml contains duplicate study_id values"
        )

    return corpus_path
