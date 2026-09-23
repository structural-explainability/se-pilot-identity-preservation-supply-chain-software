"""Source-only screening of the fixed sampling frame.

Library functions used by the numbered generalization steps. This module
never runs a converter and never calls the evaluator's comparison logic.
"""

from dataclasses import asdict
from pathlib import Path
from typing import Any

from preservation_test.generalization.models.candidate import Candidate
from preservation_test.generalization.utils.candidate_enumeration import (
    enumerate_candidates,
)
from preservation_test.generalization.utils.candidate_ids import study_id
from preservation_test.generalization.utils.candidate_inspection import (
    build_candidate,
    inspect_facts,
)
from preservation_test.generalization.utils.candidate_sorting import (
    SelectedUnit,
    inventory_order,
)
from preservation_test.generalization.utils.exclusions import screen_facts
from preservation_test.generalization.utils.git_blobs import read_blob
from preservation_test.generalization.utils.hashing import sha256_file
from preservation_test.generalization.utils.sampling_config import SamplingConfig

SCREENING_CODE_DIRS = (
    Path("src/preservation_test/generalization/models"),
    Path("src/preservation_test/generalization/utils"),
)
SCREENING_CODE_FILES = (
    Path("src/preservation_test/evaluator/formats.py"),
    Path("src/preservation_test/evaluator/purl_canonical.py"),
)


def relative_to_root(path: Path, repository_root: Path) -> str:
    """Return a repository-relative POSIX path when possible."""
    try:
        return path.resolve().relative_to(repository_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def screening_code_hashes(
    repository_root: Path,
    extra: tuple[Path, ...] = (),
) -> dict[str, str]:
    """Return SHA-256 of the frozen adapters and all screening code."""
    files = list(SCREENING_CODE_FILES) + list(extra)
    for directory in SCREENING_CODE_DIRS:
        files += sorted((repository_root / directory).glob("*.py"))
    hashes: dict[str, str] = {}
    for path in files:
        absolute = path if path.is_absolute() else repository_root / path
        hashes[relative_to_root(absolute, repository_root)] = sha256_file(absolute)
    return dict(sorted(hashes.items()))


def provenance_fields(config: SamplingConfig, repository_root: Path) -> dict[str, Any]:
    """Return the sampling provenance recorded in every screening output."""
    return {
        "sampling_id": config.sampling_id,
        "sampling_config": relative_to_root(config.path, repository_root),
        "sampling_config_sha256": config.sha256,
        "repositories": [f"{r.name}@{r.revision}" for r in config.repositories],
    }


def screen(config: SamplingConfig, clone_root: Path) -> list[Candidate]:
    """Enumerate, inspect, and screen every candidate in the sampling frame."""
    candidates: list[Candidate] = []
    for spec in config.repositories:
        repo_dir, blobs = enumerate_candidates(clone_root, spec, config.path_suffix)
        for blob in blobs:
            data = read_blob(repo_dir, blob.blob_id)
            facts = inspect_facts(blob, data, config.formats)
            candidates.append(build_candidate(facts, screen_facts(facts, config)))
    return inventory_order(candidates)


def candidate_row(candidate: Candidate) -> dict[str, Any]:
    """Return a candidate as a TOML-ready row (screening as a sub-table)."""
    return asdict(candidate)


def corpus_row(selected: SelectedUnit) -> dict[str, Any]:
    """Return a selected unit as a TOML-ready corpus member row."""
    member = selected.member
    return {
        "study_id": study_id(member.source_standard, member.sha256),
        "unit": selected.unit,
        "candidate_id": member.id,
        "repository": member.repository,
        "repository_revision": member.repository_revision,
        "repository_relative_path": member.repository_relative_path,
        "sha256": member.sha256,
        "source_standard": member.source_standard,
        "source_spec_version": member.source_spec_version,
        "subject": member.subject,
        "subject_method": member.subject_method,
        "package_ecosystem": member.package_ecosystem,
        "collapsed_candidate_ids": [item.id for item in selected.collapsed],
    }
