"""Verify that all artifacts recorded in Freeze 01 remain byte-identical.

This module reads the SHA-256 hashes recorded in
contracts/FREEZE_01_COMMITMENT_EVALUATOR.md and compares them with the
current repository files.

The verifier does not require the current Git commit to equal the commit
recorded when Freeze 01 was created. Subsequent validation work and other
non-frozen repository changes are permitted. Freeze integrity depends on
the recorded frozen artifacts remaining byte-identical.

This verifier performs no writes.
"""

import hashlib
from pathlib import Path
import re

FREEZE_FILE = Path("contracts/FREEZE_01_COMMITMENT_EVALUATOR.md")

HASH_LINE_PATTERN = re.compile(r"^- `(?P<sha256>[0-9a-fA-F]{64})`\s+`(?P<path>[^`]+)`$")


def find_repository_root(start: Path) -> Path:
    """Return the nearest ancestor containing the repository .git entry."""
    current = start.resolve()

    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return candidate

    raise RuntimeError(f"Could not find repository root from: {start}")


def calculate_sha256(path: Path) -> str:
    """Return the lowercase SHA-256 digest of a file's exact bytes."""
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def read_frozen_hashes(freeze_path: Path) -> dict[Path, str]:
    """Read frozen artifact paths and SHA-256 hashes from a freeze record."""
    if not freeze_path.is_file():
        raise FileNotFoundError(f"Freeze record not found: {freeze_path}")

    frozen_hashes: dict[Path, str] = {}

    for line in freeze_path.read_text(encoding="utf-8").splitlines():
        match = HASH_LINE_PATTERN.fullmatch(line.strip())

        if match is None:
            continue

        relative_path = Path(match.group("path"))
        expected_sha256 = match.group("sha256").lower()

        if relative_path in frozen_hashes:
            raise ValueError(
                f"Duplicate frozen artifact in freeze record: {relative_path}"
            )

        frozen_hashes[relative_path] = expected_sha256

    if not frozen_hashes:
        raise ValueError(
            f"No frozen content hashes found in freeze record: {freeze_path}"
        )

    return frozen_hashes


def verify_frozen_artifact(
    repository_root: Path,
    relative_path: Path,
    expected_sha256: str,
) -> None:
    """Verify one frozen artifact against its recorded SHA-256 hash."""
    artifact_path = repository_root / relative_path

    if not artifact_path.is_file():
        raise FileNotFoundError(f"Frozen artifact not found: {relative_path}")

    observed_sha256 = calculate_sha256(artifact_path)

    if observed_sha256 != expected_sha256:
        raise RuntimeError(
            "\n".join(
                [
                    f"Freeze 01 integrity failure: {relative_path}",
                    f"expected: {expected_sha256}",
                    f"observed: {observed_sha256}",
                ]
            )
        )


def verify_freeze_01(repository_root: Path) -> tuple[Path, ...]:
    """Verify every artifact recorded in the Freeze 01 content-hash section."""
    freeze_path = repository_root / FREEZE_FILE
    frozen_hashes = read_frozen_hashes(freeze_path)

    for relative_path, expected_sha256 in frozen_hashes.items():
        verify_frozen_artifact(
            repository_root=repository_root,
            relative_path=relative_path,
            expected_sha256=expected_sha256,
        )

    return tuple(frozen_hashes)


def main() -> None:
    """Verify Freeze 01 from the current repository."""
    repository_root = find_repository_root(Path.cwd())
    verified_files = verify_freeze_01(repository_root)

    print("Freeze 01 verified.")
    print(f"Frozen artifacts verified: {len(verified_files)}")

    for relative_path in verified_files:
        print(f"  {relative_path}")


if __name__ == "__main__":
    main()
