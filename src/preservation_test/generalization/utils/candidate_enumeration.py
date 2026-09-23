"""Mechanical candidate enumeration over the fixed sampling frame.

Every blob at the fixed revision whose path ends in the declared suffix is a
candidate. Nothing is skipped by judgment; the screening step records a
reason for every candidate it excludes.
"""

from dataclasses import dataclass
from pathlib import Path

from preservation_test.generalization.utils.git_blobs import (
    GitError,
    list_tree_blobs,
    remote_url,
    verify_commit,
)
from preservation_test.generalization.utils.git_clone import normalize_remote_url
from preservation_test.generalization.utils.sampling_config import RepositorySpec


@dataclass(frozen=True)
class BlobCandidate:
    """One enumerated candidate blob."""

    repository: str
    revision: str
    path: str
    blob_id: str
    mode: str


def clone_dir(clone_root: Path, repository: str) -> Path:
    """Return the expected local clone directory for 'owner/name'."""
    owner, _, name = repository.partition("/")
    if not owner or not name:
        raise ValueError(f"repository must be 'owner/name': {repository!r}")
    return clone_root / name


def verify_clone(repo_dir: Path, spec: RepositorySpec) -> None:
    """Require that the clone is the declared repository and holds the revision."""
    if not repo_dir.is_dir():
        raise GitError(f"clone not found for {spec.name}: {repo_dir}")

    observed = remote_url(repo_dir)
    if normalize_remote_url(observed) != normalize_remote_url(spec.url):
        raise GitError(f"{repo_dir} origin {observed!r} is not {spec.url!r}")

    verify_commit(repo_dir, spec.revision)


def enumerate_candidates(
    clone_root: Path,
    spec: RepositorySpec,
    path_suffix: str,
) -> tuple[Path, list[BlobCandidate]]:
    """Enumerate every blob at the fixed revision whose path ends in path_suffix."""
    repo_dir = clone_dir(clone_root, spec.name)
    verify_clone(repo_dir, spec)

    candidates = [
        BlobCandidate(
            repository=spec.name,
            revision=spec.revision,
            path=entry.path,
            blob_id=entry.object_id,
            mode=entry.mode,
        )
        for entry in list_tree_blobs(repo_dir, spec.revision)
        if entry.path.endswith(path_suffix)
    ]
    return repo_dir, candidates
