"""Apply the predeclared eligibility and exclusion rules to one candidate.

Every applicable reason is recorded, in a fixed order, so the audit trail
shows each rule a candidate failed rather than only the first one.

known_preservation_defect is always False and is never an exclusion reason.
Excluding candidates for known failure behavior is prohibited information
under 01-sampling.toml. Known violations are classified as Rediscovered
under the run protocol instead.
"""

from preservation_test.generalization.models.candidate_screening import (
    CandidateScreening,
)
from preservation_test.generalization.utils.candidate_inspection import SourceFacts
from preservation_test.generalization.utils.sampling_config import SamplingConfig

REASON_PARSE = "json_parse_failure"
REASON_NOT_OBJECT = "not_json_object"
REASON_NOT_SBOM = "not_software_sbom"
REASON_FORMAT = "format_not_in_scope"
REASON_ADAPTER = "adapter_load_failure"
REASON_NO_ELIGIBLE_PURL = "no_component_with_canonical_purl_and_anchor"
REASON_VALIDATION_SHA256 = "validation_sha256"
REASON_VALIDATION_SUBJECT = "validation_subject"

REASON_ORDER = (
    REASON_PARSE,
    REASON_NOT_OBJECT,
    REASON_NOT_SBOM,
    REASON_FORMAT,
    REASON_ADAPTER,
    REASON_NO_ELIGIBLE_PURL,
    REASON_VALIDATION_SHA256,
    REASON_VALIDATION_SUBJECT,
)


def screen_facts(facts: SourceFacts, config: SamplingConfig) -> CandidateScreening:
    """Return the screening decision for one candidate."""
    reasons: set[str] = set()

    parseable = facts.parse_error is None
    supported = facts.format_in_scope and facts.adapter_error is None
    contains_eligible_purl = supported and facts.eligible_purl_count > 0

    if facts.parse_error is not None:
        reasons.add(facts.parse_error)
    elif not facts.software_sbom:
        reasons.add(REASON_NOT_SBOM)
    elif not facts.format_in_scope:
        reasons.add(REASON_FORMAT)
    elif facts.adapter_error is not None:
        reasons.add(REASON_ADAPTER)
    elif not contains_eligible_purl:
        reasons.add(REASON_NO_ELIGIBLE_PURL)

    sha256_match = facts.sha256 in config.excluded_sha256()
    subject_match = facts.subject in config.excluded_subjects()
    if sha256_match:
        reasons.add(REASON_VALIDATION_SHA256)
    if subject_match:
        reasons.add(REASON_VALIDATION_SUBJECT)

    ordered = tuple(reason for reason in REASON_ORDER if reason in reasons)

    return CandidateScreening(
        software_sbom=facts.software_sbom,
        supported_source_representation=supported,
        source_parseable=parseable,
        contains_eligible_purl=contains_eligible_purl,
        # Content is read from a git blob at a pinned full revision and hashed.
        stable_provenance=True,
        used_in_engineering_validation=sha256_match or subject_match,
        known_preservation_defect=False,
        eligible=not ordered,
        exclusion_reasons=ordered,
    )
