"""Read candidate content directly from git objects at a fixed revision.

Blob bytes come from `git cat-file blob <object-id>`, so they are the exact
stored bytes. No working tree, checkout filter, or line-ending conversion is
involved.
"""

from dataclasses import dataclass
from pathlib import Path
import subprocess


class GitError(RuntimeError):
    """Raised when a git command fails or returns unexpected output."""


@dataclass(frozen=True)
class TreeEntry:
    """One blob entry from a recursive tree listing."""

    mode: str
    object_id: str
    path: str


def _git(repo_dir: Path, *args: str) -> bytes:
    completed = subprocess.run(
        ["git", "-C", str(repo_dir), *args],
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        stderr = completed.stderr.decode("utf-8", errors="replace").strip()
        raise GitError(f"git {' '.join(args)} failed in {repo_dir}: {stderr}")
    return completed.stdout


def remote_url(repo_dir: Path, remote: str = "origin") -> str:
    """Return the configured URL of a remote."""
    return _git(repo_dir, "config", "--get", f"remote.{remote}.url").decode().strip()


def verify_commit(repo_dir: Path, revision: str) -> None:
    """Require that the full revision exists locally as a commit."""
    resolved = _git(repo_dir, "rev-parse", "--verify", f"{revision}^{{commit}}")
    if resolved.decode().strip() != revision:
        raise GitError(f"{revision} did not resolve to itself in {repo_dir}")


def list_tree_blobs(repo_dir: Path, revision: str) -> list[TreeEntry]:
    """List every blob in the tree at revision, sorted by path.

    Submodule entries (type commit) are not blobs and are not listed.
    Symlinks are blobs (mode 120000) and are listed with their mode.
    """
    raw = _git(repo_dir, "ls-tree", "-r", "-z", "--full-tree", revision)
    entries: list[TreeEntry] = []
    for record in raw.split(b"\0"):
        if not record:
            continue
        header, _, path_bytes = record.partition(b"\t")
        fields = header.decode().split()
        if len(fields) != 3 or not path_bytes:
            raise GitError(f"unexpected ls-tree record: {record!r}")
        mode, object_type, object_id = fields
        if object_type != "blob":
            continue
        entries.append(
            TreeEntry(mode=mode, object_id=object_id, path=path_bytes.decode("utf-8"))
        )
    return sorted(entries, key=lambda entry: entry.path)


def read_blob(repo_dir: Path, object_id: str) -> bytes:
    """Return the exact stored bytes of a blob."""
    return _git(repo_dir, "cat-file", "blob", object_id)
