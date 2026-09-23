"""Local clone management for the fixed sampling frame.

These helpers never discard local work. Any operation that could overwrite
uncommitted changes is refused before it runs.
"""

from pathlib import Path
import re
import subprocess

from preservation_test.generalization.utils.git_blobs import GitError

_SCP_LIKE = re.compile(r"^(?:[^@/]+@)?([^:/]+):(?!//)(.+)$")


def run_git(repo_dir: Path | None, *args: str) -> str:
    """Run git, returning stripped stdout, or raise GitError."""
    command = ["git"]
    if repo_dir is not None:
        command += ["-C", str(repo_dir)]
    completed = subprocess.run(
        [*command, *args],
        capture_output=True,
        check=False,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode != 0:
        where = f" in {repo_dir}" if repo_dir is not None else ""
        raise GitError(
            f"git {' '.join(args)} failed{where}: {completed.stderr.strip()}"
        )
    return completed.stdout.strip()


def normalize_remote_url(url: str) -> str:
    """Normalize a remote URL for comparison.

    https://github.com/Owner/Repo.git, https://github.com/owner/repo/, and
    git@github.com:owner/repo.git all normalize to github.com/owner/repo.
    Local paths are resolved to an absolute POSIX path.
    """
    text = url.strip()
    if "://" in text:
        text = text.split("://", 1)[1]
        text = text.split("@", 1)[-1] if "@" in text.split("/", 1)[0] else text
    elif match := _SCP_LIKE.match(text):
        if len(match.group(1)) > 1:  # not a Windows drive letter such as C:
            text = f"{match.group(1)}/{match.group(2)}"
        else:
            text = Path(text).resolve().as_posix()
    else:
        text = Path(text).resolve().as_posix()
    return text.rstrip("/").removesuffix(".git").rstrip("/").casefold()


def is_git_worktree(repo_dir: Path) -> bool:
    """Return whether a directory is the top level of a git working tree."""
    if not repo_dir.is_dir():
        return False
    try:
        top = run_git(repo_dir, "rev-parse", "--show-toplevel")
    except GitError:
        return False
    return Path(top).resolve() == repo_dir.resolve()


def origin_url(repo_dir: Path) -> str:
    """Return the configured origin URL."""
    return run_git(repo_dir, "config", "--get", "remote.origin.url")


def uncommitted_changes(repo_dir: Path) -> list[str]:
    """Return porcelain status lines, including untracked files."""
    status = run_git(repo_dir, "status", "--porcelain", "--untracked-files=all")
    return [line for line in status.splitlines() if line.strip()]


def object_type(repo_dir: Path, revision: str) -> str | None:
    """Return the git object type of revision, or None if it is absent."""
    try:
        return run_git(repo_dir, "cat-file", "-t", revision)
    except GitError:
        return None


def head_revision(repo_dir: Path) -> str | None:
    """Return the full HEAD commit, or None if HEAD is unborn."""
    try:
        return run_git(repo_dir, "rev-parse", "--verify", "HEAD^{commit}")
    except GitError:
        return None


def head_is_detached(repo_dir: Path) -> bool:
    """Return whether HEAD is detached (not a symbolic ref to a branch)."""
    try:
        run_git(repo_dir, "symbolic-ref", "-q", "HEAD")
    except GitError:
        return True
    return False


def clone(url: str, repo_dir: Path) -> None:
    """Clone url into repo_dir, keeping working-tree bytes equal to blobs."""
    repo_dir.parent.mkdir(parents=True, exist_ok=True)
    run_git(None, "clone", "-c", "core.autocrlf=false", url, str(repo_dir))


def fetch_revision(repo_dir: Path, revision: str) -> None:
    """Fetch one revision from origin, falling back to fetching all refs."""
    try:
        run_git(repo_dir, "fetch", "origin", revision)
    except GitError:
        run_git(repo_dir, "fetch", "origin")


def checkout_detached(repo_dir: Path, revision: str) -> None:
    """Check out revision with a detached HEAD."""
    run_git(
        repo_dir, "-c", "advice.detachedHead=false", "checkout", "--detach", revision
    )
