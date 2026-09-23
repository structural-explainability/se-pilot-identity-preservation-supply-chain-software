"""Verify the generated generalization corpus and its recorded provenance.

This verifier checks that 03-corpus.toml exists and still refers to the
current 01-sampling.toml and 02-candidates.toml bytes.

Additional corpus invariants can be added as Freeze 02 preparation
continues.
"""

from pathlib import Path
import tomllib

from preservation_test.generalization.utils.hashing import sha256_file

CORPUS_FILE = Path("generalization/03-corpus.toml")
SAMPLING_FILE = Path("generalization/01-sampling.toml")
CANDIDATES_FILE = Path("generalization/02-candidates.toml")


class CorpusVerificationError(RuntimeError):
    """Raised when the generated corpus fails integrity verification."""


def verify_corpus(repository_root: Path) -> Path:
    """Verify 03-corpus.toml against its recorded upstream inputs."""
    corpus_path = repository_root / CORPUS_FILE
    sampling_path = repository_root / SAMPLING_FILE
    candidates_path = repository_root / CANDIDATES_FILE

    for path in (corpus_path, sampling_path, candidates_path):
        if not path.is_file():
            raise CorpusVerificationError(f"required file not found: {path}")

    with corpus_path.open("rb") as handle:
        data = tomllib.load(handle)

    corpus = data.get("corpus")
    if not isinstance(corpus, dict):
        raise CorpusVerificationError("03-corpus.toml is missing [corpus]")

    expected_sampling = corpus.get("sampling_config_sha256")
    observed_sampling = sha256_file(sampling_path)

    if expected_sampling != observed_sampling:
        raise CorpusVerificationError(
            "01-sampling.toml does not match the hash recorded in 03-corpus.toml"
        )

    expected_candidates = corpus.get("candidates_record_sha256")
    observed_candidates = sha256_file(candidates_path)

    if expected_candidates != observed_candidates:
        raise CorpusVerificationError(
            "02-candidates.toml does not match the hash recorded in 03-corpus.toml"
        )

    members = data.get("member")
    if not isinstance(members, list) or not members:
        raise CorpusVerificationError("03-corpus.toml contains no corpus members")

    recorded_members = corpus.get("members")
    if recorded_members != len(members):
        raise CorpusVerificationError(
            "03-corpus.toml member count does not match [corpus].members"
        )

    return corpus_path
