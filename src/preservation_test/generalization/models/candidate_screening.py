"""Source-side screening outcome for one candidate in the sampling frame.

A ``CandidateScreening`` records the source-side screening flags used while
constructing the candidate inventory, together with the overall eligibility
decision and all recorded exclusion reasons.

One record is written to 02-candidates.toml for every mechanically enumerated
candidate, including excluded candidates, so the complete screening history is
preserved.

Screening uses only information permitted by the frozen sampling specification.
No generalization transformation is executed, and no transformation or
source-target evaluator outcome is inspected.
"""

from dataclasses import dataclass


class CandidateScreeningError(Exception):
    """Base class for errors related to candidate screening."""


@dataclass(frozen=True)
class CandidateScreening:
    """Source-side screening flags and eligibility outcome for one candidate.

    The overall eligibility decision follows the predeclared inclusion and
    exclusion rules in the frozen sampling specification. Some fields also
    record screening invariants used by the implementation and should not be
    interpreted as additional outcome-aware selection criteria.

    Attributes:
        software_sbom: Source-side classification flag recorded by the
            screening implementation.
        supported_source_representation: The source uses an in-scope standard,
            specification version, and serialization.
        source_parseable: The source bytes parse as JSON.
        contains_eligible_purl: The frozen source adapter yields at least one
            component having both a canonical PURL and a content-hash anchor.
        stable_provenance: The candidate is identified by repository, pinned
            revision, and repository-relative path from the fixed sampling
            frame.
        used_in_engineering_validation: The candidate's SHA-256 or resolved
            subject matches a predeclared engineering-validation exclusion.
        known_preservation_defect: Screening implementation flag retained in
            the candidate record; it is not an independent selection criterion
            under the frozen sampling specification.
        eligible: Overall eligibility decision under the frozen inclusion and
            exclusion rules.
        exclusion_reasons: All recorded reasons the candidate failed
            eligibility; empty when the candidate is eligible.
    """

    software_sbom: bool
    supported_source_representation: bool
    source_parseable: bool
    contains_eligible_purl: bool
    stable_provenance: bool
    used_in_engineering_validation: bool
    known_preservation_defect: bool
    eligible: bool
    exclusion_reasons: tuple[str, ...]
