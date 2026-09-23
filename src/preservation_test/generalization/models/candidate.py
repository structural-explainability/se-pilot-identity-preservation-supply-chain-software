from dataclasses import dataclass

from preservation_test.generalization.models.candidate_screening import (
    CandidateScreening,
)


@dataclass(frozen=True)
class Candidate:
    id: str
    repository: str
    repository_revision: str
    repository_relative_path: str
    sha256: str
    size_bytes: int
    source_standard: str
    source_format: str
    source_spec_version: str
    subject: str
    subject_method: str
    package_ecosystem: str
    purl_count: int
    eligible_purl_count: int
    purl_types: tuple[str, ...]
    screening: CandidateScreening
