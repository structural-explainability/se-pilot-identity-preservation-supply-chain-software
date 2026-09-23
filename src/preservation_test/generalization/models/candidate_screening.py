from dataclasses import dataclass


@dataclass(frozen=True)
class CandidateScreening:
    software_sbom: bool
    supported_source_representation: bool
    source_parseable: bool
    contains_eligible_purl: bool
    stable_provenance: bool
    used_in_engineering_validation: bool
    known_preservation_defect: bool
    eligible: bool
    exclusion_reasons: tuple[str, ...]
