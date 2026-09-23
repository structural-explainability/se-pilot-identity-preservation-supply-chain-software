"""Stable identifiers for candidates, selection units, and corpus members."""

UNIT_SEPARATOR = " | "


def candidate_id(repository: str, path: str) -> str:
    """Identify a screened candidate by repository and repository-relative path.

    Each repository has exactly one fixed revision in the sampling frame, so
    repository plus path is unique within one screening run.
    """
    return f"{repository}:{path}"


def unit_key(source_standard: str, subject: str) -> str:
    """Identify a selection unit (source standard plus subject)."""
    return f"{source_standard}{UNIT_SEPARATOR}{subject}"


def study_id(source_standard: str, sha256: str) -> str:
    """Identify a selected corpus member by standard and content digest."""
    return f"gen-{source_standard}-{sha256[:12]}"
