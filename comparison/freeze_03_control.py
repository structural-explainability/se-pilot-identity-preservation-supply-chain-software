"""Check, establish, or verify Freeze 03 for the kernel missing-value study.

From the repository root:

    uv run --frozen python comparison/freeze_03_control.py --check
    uv run --frozen python comparison/freeze_03_control.py --establish
    uv run --frozen python comparison/freeze_03_control.py --verify

The PowerShell wrapper also runs the preparation and L4 self-tests.

Preparation counts were examined before this freeze. The frozen design
records that chronology. Establishment requires a clean committed tree
and absent comparison output directories. Verification permits later output.
"""

import argparse
from datetime import UTC, datetime
import os
from pathlib import Path
import re
import subprocess

from preservation_test.generalization.freeze_02 import contained, verify_06_freeze_02
from preservation_test.generalization.utils.hashing import sha256_file

ROOT = Path(__file__).resolve().parents[1]

RECORD = "contracts/FREEZE_03_KERNEL_MISSING_VALUES.md"
FREEZE_02_RECORD = "contracts/FREEZE_02_GENERALIZATION.md"
DESIGN = "comparison/freeze_03_design.md"
PREPARE = "comparison/freeze_03_prepare.py"
RUN_L4 = "comparison/freeze_03_run_l4.py"
SELF = "comparison/freeze_03_control.py"
WRAPPER = "freeze_03.ps1"

EVIDENCE_COMMIT = "e1befa159faff965b32a47975ac355bb6a9ccb18"
KERNEL_COMMIT = "e895ace0129e321eaf6912718c341ce3eb1644eb"

INVENTORY = (DESIGN, PREPARE, RUN_L4, SELF, WRAPPER, FREEZE_02_RECORD)
OUTPUT_DIRECTORIES = ("comparison/prepared", "comparison/results")

HASH_LINE = re.compile(
    r"^- `([0-9a-f]{64})`  `([^`]+)`[ \t]*$",
    re.MULTILINE,
)
COMMIT_LINE = re.compile(
    r"^\*\*Frozen content commit:\*\* `([0-9a-f]{40})`[ \t]*$",
    re.MULTILINE,
)


def git(root: Path, *args: str) -> str:
    """Run Git in the repository and return its stripped text output."""
    return subprocess.check_output(["git", *args], cwd=root, text=True).strip()


def require_ancestor(root: Path, commit: str) -> None:
    """Require the supplied commit to exist and be an ancestor of HEAD."""
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", commit, "HEAD"],
        cwd=root,
        check=False,
    )
    if result.returncode != 0:
        raise ValueError(
            f"Commit is unavailable or is not an ancestor of HEAD: {commit}"
        )


def pin(text: str, name: str) -> str:
    """Read one literal 40-character Git commit assignment."""
    pattern = rf'^{name} = "([0-9a-f]{{40}})"[ \t]*\r?$'
    found = re.findall(pattern, text, flags=re.MULTILINE)
    if len(found) != 1:
        raise ValueError(f"Expected exactly one {name} assignment, found {len(found)}")
    return found[0]


def check_pins(root: Path) -> None:
    """Check the evidence and kernel pins across the frozen apparatus."""
    prepare = contained(root, PREPARE).read_text(encoding="utf-8")
    runner = contained(root, RUN_L4).read_text(encoding="utf-8")
    design = contained(root, DESIGN).read_text(encoding="utf-8")

    if pin(prepare, "EVIDENCE_COMMIT") != EVIDENCE_COMMIT:
        raise ValueError(f"{PREPARE}: evidence commit mismatch")
    if pin(runner, "EVIDENCE_COMMIT") != EVIDENCE_COMMIT:
        raise ValueError(f"{RUN_L4}: evidence commit mismatch")
    if pin(runner, "KERNEL_COMMIT") != KERNEL_COMMIT:
        raise ValueError(f"{RUN_L4}: kernel commit mismatch")

    dependency_pin = f"se-interpretive-kernel.git@{KERNEL_COMMIT}"
    if runner.count(dependency_pin) != 1:
        raise ValueError(f"{RUN_L4}: expected one pinned kernel dependency")

    for commit in (EVIDENCE_COMMIT, KERNEL_COMMIT):
        if commit not in design:
            raise ValueError(f"{DESIGN}: required commit is missing: {commit}")

    if RECORD not in design:
        raise ValueError(f"{DESIGN}: required Freeze 03 record path is missing")


def check_inputs(root: Path) -> None:
    """Check establishing prerequisites apart from the clean-tree requirement."""
    verify_06_freeze_02(root)

    for relative in INVENTORY:
        if not contained(root, relative).is_file():
            raise ValueError(f"Required artifact missing: {relative}")

    check_pins(root)
    require_ancestor(root, EVIDENCE_COMMIT)

    for relative in OUTPUT_DIRECTORIES:
        if contained(root, relative).exists():
            raise ValueError(f"Comparison output directory already exists: {relative}")


def check_clean(root: Path) -> None:
    """Require a clean tree, including untracked files."""
    if git(root, "status", "--porcelain", "--untracked-files=all"):
        raise ValueError("Commit the complete preparation state before Freeze 03")


def render(root: Path) -> str:
    """Create the record text and current artifact digests."""
    head = git(root, "rev-parse", "HEAD")
    timestamp = datetime.now(UTC).isoformat()
    hashes = "\n".join(
        f"- `{sha256_file(contained(root, path))}`  `{path}`"
        for path in sorted(INVENTORY)
    )

    return f"""# Freeze 03 — Kernel Missing-Value Comparison

## Scope

This record freezes the L4 execution procedure using the interpretive kernel.

The design specifies the canonical-PURL probe, eligible occurrences,
source–target pairs, hash-authorized frame regime, both missing-value
policies, and reporting rules.

See [Kernel Missing-Value Comparison Design](../comparison/freeze_03_design.md).

## Chronology

The original L4 hypothesis predates the Freeze 02 baseline execution.

The operational design was completed after baseline inspection.
Real-evidence preparation counts were examined before this freeze.
Those counts and their implications are recorded in the frozen design.

At establishment, `comparison/prepared/` and `comparison/results/`
were absent. The frozen commands create the formal prepared artifact
and result file.

## Pinned Evidence and Kernel

- Baseline evidence commit: `{EVIDENCE_COMMIT}`
- Interpretive kernel commit: `{KERNEL_COMMIT}`

## Outputs and Report

- Prepared input: `comparison/prepared/freeze_02.json`
- Kernel result: `comparison/results/l4/run.json`
- Subsequent report: `comparison/REPORT_L4.md`

The inventory below covers the execution apparatus.
The generated outputs and subsequent report are preserved after execution.

## Verification

Verification checks every listed digest, the declared pins,
commit ancestry, and Freeze 02 integrity.
It permits comparison output directories after establishment.

```powershell
.\\freeze_03.ps1 -Verify
```

The pre-execution content commit identifies the preparation state.
The protocol requires separate review and commitment of this record
before formal execution.
Record generation does not perform that commitment.

## Frozen Content Hashes

**Status:** FROZEN

**Frozen (UTC):** {timestamp}

**Frozen content commit:** `{head}`

{hashes}
"""


def verify(root: Path) -> str:
    """Verify the established apparatus and return the record digest."""
    root = root.resolve()
    record = contained(root, RECORD)
    if not record.is_file():
        raise ValueError("Freeze 03 has not been established")

    text = record.read_text(encoding="utf-8")
    if "**Status:** FROZEN" not in text:
        raise ValueError("Freeze 03 record is missing its frozen status")

    commits = COMMIT_LINE.findall(text)
    if len(commits) != 1:
        raise ValueError("Freeze 03 must state exactly one content commit")

    entries = HASH_LINE.findall(text)
    hashes = {path: digest for digest, path in entries}
    if len(hashes) != len(entries):
        raise ValueError("Freeze 03 contains duplicate artifact paths")

    if set(hashes) != set(INVENTORY):
        raise ValueError(
            "Freeze 03 inventory mismatch: "
            f"missing={sorted(set(INVENTORY) - set(hashes))}, "
            f"extra={sorted(set(hashes) - set(INVENTORY))}"
        )

    for path, expected in hashes.items():
        actual = sha256_file(contained(root, path))
        if actual != expected:
            raise ValueError(f"Freeze 03 hash mismatch: {path}")

    verify_06_freeze_02(root)
    check_pins(root)
    require_ancestor(root, EVIDENCE_COMMIT)
    require_ancestor(root, commits[0])

    return sha256_file(record)


def establish(root: Path) -> None:
    """Establish the freeze once from a clean committed preparation state."""
    root = root.resolve()
    record = contained(root, RECORD)
    if record.exists():
        raise ValueError("Freeze 03 already exists")

    check_clean(root)
    check_inputs(root)

    pending = record.with_suffix(".pending")
    with pending.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(render(root))

    try:
        os.link(pending, record)
    finally:
        pending.unlink()

    verify(root)
    print(
        "Freeze 03 written and verified. "
        "Review and commit the record before formal execution."
    )


def main() -> None:
    """Dispatch the explicitly requested freeze operation."""
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--establish", action="store_true")
    mode.add_argument("--verify", action="store_true")
    args = parser.parse_args()

    if args.check:
        if contained(ROOT, RECORD).exists():
            raise ValueError("Freeze 03 already exists")
        check_inputs(ROOT)
        print("Freeze 03 checks passed. No comparison artifacts were written.")
    elif args.establish:
        establish(ROOT)
    else:
        print(f"Freeze 03 verified: {verify(ROOT)}")


if __name__ == "__main__":
    main()
