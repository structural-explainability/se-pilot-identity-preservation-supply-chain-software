"""Inspect one candidate from its source bytes only.

Inspection gathers source facts. The eligibility decision is made in
exclusions.screen_facts, and the two are combined into a Candidate by
build_candidate, so the decision rule lives in exactly one place.
"""

from dataclasses import dataclass, field

from preservation_test.generalization.models.candidate import Candidate
from preservation_test.generalization.models.candidate_screening import (
    CandidateScreening,
)
from preservation_test.generalization.utils.candidate_enumeration import BlobCandidate
from preservation_test.generalization.utils.candidate_ids import candidate_id
from preservation_test.generalization.utils.hashing import sha256_bytes
from preservation_test.generalization.utils.purl_inspection import (
    AdapterLoadError,
    assign_ecosystem,
    inspect_source,
)
from preservation_test.generalization.utils.sampling_config import FormatsSpec
from preservation_test.generalization.utils.source_detection import (
    EXPECTED_ADAPTER_FORMAT,
    SBOM_STANDARDS,
    STANDARD_UNKNOWN,
    detect_source_format,
    format_in_scope,
    parse_json_object,
    serialization_of,
)
from preservation_test.generalization.utils.subject_resolution import resolve_subject

UNKNOWN_VERSION = "unknown"


@dataclass(frozen=True)
class SourceFacts:
    """Source-only facts about one candidate, before any eligibility decision."""

    blob: BlobCandidate
    sha256: str
    size_bytes: int
    parse_error: str | None
    source_standard: str
    source_format: str
    source_spec_version: str
    software_sbom: bool
    format_in_scope: bool
    adapter_error: str | None
    purl_count: int
    eligible_purl_count: int
    purl_type_counts: dict[str, int] = field(default_factory=dict)
    subject: str = ""
    subject_method: str = ""


def inspect_facts(
    blob: BlobCandidate, data: bytes, formats_spec: FormatsSpec
) -> SourceFacts:
    """Gather source-only facts about one candidate."""
    parsed = parse_json_object(data)

    standard = STANDARD_UNKNOWN
    spec_version = UNKNOWN_VERSION
    in_scope = False
    adapter_error: str | None = None
    purl_count = 0
    eligible_purl_count = 0
    type_counts: dict[str, int] = {}

    if parsed.document is not None:
        source_format = detect_source_format(parsed.document)
        standard = source_format.standard
        spec_version = source_format.spec_version or UNKNOWN_VERSION
        in_scope = format_in_scope(source_format, formats_spec)

        # The frozen adapter is applied only to in-scope sources, so that the
        # SPDX 2.x-to-2.3 routing in detect_format never governs eligibility.
        if in_scope:
            try:
                inspection = inspect_source(parsed.document)
            except AdapterLoadError as error:
                adapter_error = str(error)
            else:
                if inspection.adapter_format != EXPECTED_ADAPTER_FORMAT.get(standard):
                    adapter_error = (
                        f"adapter format {inspection.adapter_format!r} does not "
                        f"match declared standard {standard!r}"
                    )
                purl_count = inspection.purl_count
                eligible_purl_count = inspection.eligible_purl_count
                type_counts = inspection.purl_type_counts

    subject = resolve_subject(parsed.document, standard, blob.repository, blob.path)

    return SourceFacts(
        blob=blob,
        sha256=sha256_bytes(data),
        size_bytes=len(data),
        parse_error=parsed.error,
        source_standard=standard,
        source_format=serialization_of(parsed),
        source_spec_version=spec_version,
        software_sbom=standard in SBOM_STANDARDS,
        format_in_scope=in_scope,
        adapter_error=adapter_error,
        purl_count=purl_count,
        eligible_purl_count=eligible_purl_count,
        purl_type_counts=type_counts,
        subject=subject.key,
        subject_method=subject.method,
    )


def build_candidate(facts: SourceFacts, screening: CandidateScreening) -> Candidate:
    """Combine source facts and the screening decision into a Candidate."""
    return Candidate(
        id=candidate_id(facts.blob.repository, facts.blob.path),
        repository=facts.blob.repository,
        repository_revision=facts.blob.revision,
        repository_relative_path=facts.blob.path,
        sha256=facts.sha256,
        size_bytes=facts.size_bytes,
        source_standard=facts.source_standard,
        source_format=facts.source_format,
        source_spec_version=facts.source_spec_version,
        purl_count=facts.purl_count,
        eligible_purl_count=facts.eligible_purl_count,
        purl_types=tuple(facts.purl_type_counts),
        subject=facts.subject,
        subject_method=facts.subject_method,
        package_ecosystem=assign_ecosystem(facts.purl_type_counts),
        screening=screening,
    )
