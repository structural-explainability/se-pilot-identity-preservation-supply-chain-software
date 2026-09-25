"""Candidate record for one source artifact in the sampling frame.

A ``Candidate`` is the source-only inspection and screening result for one
mechanically enumerated file at a pinned repository revision.

It is built in step 01 using only source-side information:
the exact Git blob bytes plus the fixed sampling-frame and
provenance information needed to identify and screen that blob.
No generalization transformation is executed,
and no transformation or evaluator outcome is inspected.

The record is written to 02-candidates.toml.
Later steps read the frozen candidate inventory and may
copy selected fields into downstream records;
they do not modify the candidate record.
"""

from dataclasses import dataclass

from preservation_test.generalization.models.candidate_screening import (
    CandidateScreening,
)


@dataclass(frozen=True)
class Candidate:
    """Source-only inspection and screening result for one candidate file.

    Attributes:
        id: Deterministic identifier for the candidate.
        repository: Repository name declared in the sampling frame.
        repository_revision: Pinned revision from which the file was read.
        repository_relative_path: Path of the file within the repository.
        sha256: SHA-256 of the exact source bytes.
        size_bytes: Size of the exact source bytes.
        source_standard: Detected source standard (``cyclonedx`` or ``spdx``).
        source_format: Serialization of the source document; ``json`` in the
            frozen sampling frame.
        source_spec_version: Specification version declared by the source
            document.
        subject: Resolved subject used with ``source_standard`` to form the
            selection unit. The primary described component is used when
            available; otherwise the repository-relative parent directory is
            used as the fallback.
        subject_method: Method used to resolve the subject.
        package_ecosystem: Reporting ecosystem derived from the observed
            source PURL types under the predeclared reporting rule.
        purl_count: Number of PURLs found in the source document.
        eligible_purl_count: Number of those PURLs satisfying the predeclared
            source-side eligibility conditions.
        purl_types: PURL types observed in the source document.
        screening: Source-only screening flags, eligibility outcome, and
            exclusion reasons.
    """

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
