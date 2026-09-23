"""Step p01: prepare local clones of the fixed sampling frame.

For each repository declared in 01-sampling.toml:

    if the clone does not exist:
        clone the declared URL
    verify the clone's origin corresponds to the declared URL
    if the clone has uncommitted changes (including untracked files):
        FAIL, and do not touch them
    if the pinned revision does not exist locally:
        fetch it
    verify the pinned revision is a commit
    check out the exact revision with a detached HEAD
        (also when a branch is already at the pinned commit)
    verify HEAD == the declared revision

Idempotent: a clone already at its pinned revision is verified and left
unchanged. Nothing is ever reset, cleaned, stashed, or deleted.

Screening reads git blobs at the pinned revision, not the working tree,
so a detached checkout here is for inspection convenience and for a
visible, verifiable frame state. New clones are made with
core.autocrlf=false so working-tree bytes match the blobs.

Usage (relative paths resolve against the repository root):

    uv run python -m preservation_test.generalization.p01_prepare_sampling_frame

    uv run python -m preservation_test.generalization.p01_prepare_sampling_frame `
        --config generalization/01-sampling.toml `
        --clone-root ../generalization-clones

Clones live at <clone-root>/<repository-name>, for example
../generalization-clones/bom-examples.
"""

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys

from preservation_test.generalization.utils.candidate_enumeration import clone_dir
from preservation_test.generalization.utils.git_blobs import GitError
from preservation_test.generalization.utils.git_clone import (
    checkout_detached,
    clone,
    fetch_revision,
    head_is_detached,
    head_revision,
    is_git_worktree,
    normalize_remote_url,
    object_type,
    origin_url,
    uncommitted_changes,
)
from preservation_test.generalization.utils.sampling_config import (
    RepositorySpec,
    SamplingConfigError,
    load_sampling_config,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]

DEFAULT_CONFIG = Path("generalization/01-sampling.toml")
DEFAULT_CLONE_ROOT = Path("../generalization-clones")

EXIT_OK = 0
EXIT_FAILED = 2


class FramePreparationError(RuntimeError):
    """Raised when a clone cannot be brought to its pinned revision safely."""


@dataclass(frozen=True)
class PreparedRepository:
    """Outcome for one repository in the sampling frame."""

    name: str
    path: Path
    revision: str
    actions: tuple[str, ...]


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else REPOSITORY_ROOT / path


def prepare_repository(spec: RepositorySpec, clone_root: Path) -> PreparedRepository:
    """Bring one clone to its pinned revision without discarding local work."""
    repo_dir = clone_dir(clone_root, spec.name)
    actions: list[str] = []

    if not repo_dir.exists():
        clone(spec.url, repo_dir)
        actions.append("cloned")
    elif not is_git_worktree(repo_dir):
        raise FramePreparationError(
            f"{repo_dir} exists but is not the top level of a git working tree; "
            "it will not be modified"
        )

    observed_url = origin_url(repo_dir)
    if normalize_remote_url(observed_url) != normalize_remote_url(spec.url):
        raise FramePreparationError(
            f"{repo_dir} origin is {observed_url!r}, not the declared {spec.url!r}"
        )

    changes = uncommitted_changes(repo_dir)
    if changes:
        listing = "\n    ".join(changes[:20])
        more = f"\n    ... and {len(changes) - 20} more" if len(changes) > 20 else ""
        raise FramePreparationError(
            f"{repo_dir} has uncommitted changes; nothing was modified:\n"
            f"    {listing}{more}"
        )

    if object_type(repo_dir, spec.revision) is None:
        fetch_revision(repo_dir, spec.revision)
        actions.append("fetched")

    kind = object_type(repo_dir, spec.revision)
    if kind is None:
        raise FramePreparationError(
            f"{spec.revision} is not available from {spec.url} after fetching"
        )
    if kind != "commit":
        raise FramePreparationError(f"{spec.revision} is a {kind}, not a commit")

    # Detach even when a branch currently points at the pinned commit so that
    # later branch movement cannot silently move the visible sampling frame.
    if head_revision(repo_dir) != spec.revision or not head_is_detached(repo_dir):
        checkout_detached(repo_dir, spec.revision)
        actions.append("checked out (detached)")

    head = head_revision(repo_dir)
    if head != spec.revision or not head_is_detached(repo_dir):
        raise FramePreparationError(
            f"{repo_dir} HEAD is {head}, expected detached at {spec.revision}"
        )

    if not actions:
        actions.append("already at pinned revision")

    return PreparedRepository(
        name=spec.name,
        path=repo_dir,
        revision=spec.revision,
        actions=tuple(actions),
    )


def prepare_sampling_frame(config_path: Path, clone_root: Path) -> int:
    """Prepare every repository in the sampling frame; stop at the first failure."""
    try:
        config = load_sampling_config(config_path)
    except (OSError, SamplingConfigError) as error:
        sys.stderr.write(
            f"SAMPLING FRAME NOT PREPARED.\nsampling specification: {error}\n"
        )
        return EXIT_FAILED

    for spec in config.repositories:
        try:
            prepared = prepare_repository(spec, clone_root)
        except (FramePreparationError, GitError) as error:
            sys.stderr.write(f"SAMPLING FRAME NOT PREPARED.\n{spec.name}: {error}\n")
            return EXIT_FAILED
        print(
            f"{prepared.name} @ {prepared.revision}: "
            f"{', '.join(prepared.actions)} ({prepared.path})"
        )

    print(f"sampling frame ready: {len(config.repositories)} repositories")
    return EXIT_OK


def main(argv: list[str] | None = None) -> int:
    """Parse arguments and run step p01."""
    parser = argparse.ArgumentParser(
        description="Step p01: prepare local clones of the fixed sampling frame."
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--clone-root", type=Path, default=DEFAULT_CLONE_ROOT)
    args = parser.parse_args(argv)
    return prepare_sampling_frame(_resolve(args.config), _resolve(args.clone_root))


if __name__ == "__main__":
    raise SystemExit(main())
