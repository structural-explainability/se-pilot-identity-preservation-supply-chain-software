"""Create and verify the complete Freeze 02 inventory without running converters."""

import argparse
from datetime import UTC, datetime
from pathlib import Path, PureWindowsPath
import re
import subprocess
import tomllib

from preservation_test.generalization.utils.hashing import sha256_file
from preservation_test.generalization.verification.verify_01_freeze_01 import (
    read_frozen_hashes,
    verify_01_freeze_01,
)
from preservation_test.generalization.verification.verify_05_freeze_02 import (
    verify_05_freeze_02,
)
from preservation_test.generalization.verification.verify_hashes import verify_file_hash

RECORD = "contracts/FREEZE_02_GENERALIZATION.md"
PLAN = "generalization/05-transformations.toml"
SMOKE = "validation/executor-smoke/results/run.json"
ROOT = Path(__file__).resolve().parents[3]

REQUIRED_CODE = {
    "src/preservation_test/generalization/freeze_02.py",
    "src/preservation_test/generalization/execute_generalization.py",
    "src/preservation_test/generalization/smoke_generalization.py",
    "src/preservation_test/generalization/verification/verify_01_freeze_01.py",
    "src/preservation_test/generalization/verification/verify_05_freeze_02.py",
    "src/preservation_test/generalization/verification/verify_06_freeze_02.py",
}


def contained(root: Path, relative: str) -> Path:
    """Resolve a repository-relative path, refusing traversal and symlinks."""
    p = Path(relative)

    if (
        not relative
        or p.is_absolute()
        or PureWindowsPath(relative).drive
        or ".." in p.parts
    ):
        raise ValueError(f"not a repository-relative path: {relative}")

    path = root / p

    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"path escapes repository: {relative}")

    current = path
    while current != root:
        if current.is_symlink():
            raise ValueError(f"symlinks are not frozen artifacts: {relative}")
        current = current.parent

    return path


def inventory(root: Path) -> set[str]:
    """Return the mandatory inventory, including every file in the Java runtime."""
    paths = {
        "contracts/FREEZE_01_COMMITMENT_EVALUATOR.md",
        "contracts/schema.md",
        "contracts/sources.toml",
        "contracts/commitments.toml",
        "docs/en/run.md",
        "uv.lock",
        "pyproject.toml",
        ".python-version",
        "freeze_02.ps1",
        "known/known_violations.toml",
        "generalization/PREDICTIONS.md",
        SMOKE,
        "generalization/01-sampling.toml",
        "generalization/02-candidates.toml",
        "generalization/03-corpus.toml",
        "generalization/04-sources.toml",
        PLAN,
        "validation/executor-smoke/plan.toml",
    }

    paths.update(REQUIRED_CODE)

    paths.update(
        p.relative_to(root).as_posix()
        for p in (root / "validation/executor-smoke").rglob("*")
        if p.is_file()
    )

    for path in (root / "src/preservation_test").rglob("*.py"):
        if path.name != "_version.py":
            paths.add(path.relative_to(root).as_posix())

    with contained(root, "generalization/04-sources.toml").open("rb") as handle:
        paths.update(r["preserved_path"] for r in tomllib.load(handle)["source"])

    with contained(root, PLAN).open("rb") as handle:
        plan = tomllib.load(handle)

    paths.add(plan["target_validator"]["artifact_path"])

    for converter in plan["converter"]:
        paths.add(converter["artifact_path"])

        if runtime := converter.get("runtime_artifact_path"):
            launcher = contained(root, runtime)
            runtime_root = launcher.parent.parent

            if launcher.parent.name != "bin" or runtime_root == root:
                raise ValueError("runtime must be a repository-local JDK/bin launcher")

            for required in ("release", "lib/modules"):
                if not (runtime_root / required).is_file():
                    raise ValueError(f"incomplete JDK: {runtime_root / required}")

            paths.update(
                p.relative_to(root).as_posix()
                for p in runtime_root.rglob("*")
                if p.is_file()
            )

    for relative in paths:
        if not contained(root, relative).is_file():
            raise ValueError(f"required freeze artifact missing: {relative}")

    return paths


def verify_06_freeze_02(root: Path) -> str:
    """Verify Freeze 01 and the exact complete Freeze 02 set, with results present."""
    root = root.resolve()
    verify_01_freeze_01(root)

    record = contained(root, RECORD)

    if "**Status:** FROZEN" not in record.read_text(encoding="utf-8"):
        raise ValueError("Freeze 02 has not been established")

    hashes = read_frozen_hashes(record)
    expected = inventory(root)
    recorded = {p.as_posix() for p in hashes}

    if recorded != expected:
        raise ValueError(
            "Freeze 02 inventory differs: "
            f"missing={sorted(expected - recorded)}, "
            f"extra={sorted(recorded - expected)}"
        )

    for path, digest in hashes.items():
        contained(root, path.as_posix())
        verify_file_hash(root, path.as_posix(), digest, label="Freeze 02")

    return sha256_file(record)


def establish(root: Path) -> None:
    """Write an explicit freeze from a clean commit; never commit automatically."""
    root = root.resolve()
    record = contained(root, RECORD)
    text = record.read_text(encoding="utf-8")

    if "**Status:** FROZEN" in text:
        raise ValueError("Freeze 02 is already established")

    status = subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=root,
        text=True,
    )

    if status.strip():
        raise ValueError(
            "commit the complete pre-freeze state before establishing Freeze 02"
        )

    verify_05_freeze_02(root)

    from preservation_test.generalization.smoke_generalization import verify_smoke

    verify_smoke(root)
    paths = inventory(root)

    head = subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        text=True,
    ).strip()

    lines = [f"- `{sha256_file(contained(root, p))}`  `{p}`" for p in sorted(paths)]

    stamp = datetime.now(UTC).isoformat()

    text = re.sub(
        r"\n## Frozen Content Hashes\n.*\Z",
        "",
        text,
        flags=re.DOTALL,
    )

    text += (
        "\n## Frozen Content Hashes\n\n"
        "**Status:** FROZEN\n\n"
        f"**Frozen (UTC):** {stamp}\n\n"
        f"**Frozen content commit:** `{head}`\n\n" + "\n".join(lines) + "\n"
    )

    temporary = record.with_suffix(".pending")

    with temporary.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(text)

    temporary.replace(record)
    verify_06_freeze_02(root)

    print(
        "Freeze 02 written and verified. "
        "Review and commit the freeze record before formal execution."
    )


def main() -> None:
    """Create the freeze only when explicitly requested."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--establish", action="store_true", required=True)
    parser.parse_args()
    establish(ROOT)


if __name__ == "__main__":
    main()
